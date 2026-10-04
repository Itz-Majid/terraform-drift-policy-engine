import json
import unittest

from pipeline import analyze_drift
from provenance import ProvenanceEvidence


def make_plan(attribute, before, after):
    return {
        "resource_drift": [
            {
                "address": "aws_instance.web",
                "change": {
                    "actions": ["update"],
                    "before": {attribute: before},
                    "after": {attribute: after},
                },
            }
        ]
    }


class TestPipelineSecurity(unittest.TestCase):

    def run_pipeline(self, attribute, before, after, evidence_match=True):
        filename = "test-plan.json"

        with open(filename, "w") as f:
            json.dump(make_plan(attribute, before, after), f)

        evidence = ProvenanceEvidence(
            actor="authorized",
            action=f"modify_{attribute}",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=evidence_match,
        )

        return analyze_drift(filename, evidence)[0]

    def test_low_authorized_can_codify(self):
        result = self.run_pipeline(
            "instance_type",
            "t3.small",
            "t3.large",
            True,
        )

        self.assertEqual(result["security_class"], "LOW")
        self.assertEqual(result["provenance"], "AUTHORIZED")
        self.assertEqual(result["decision"], "CODIFY-CANDIDATE")
        self.assertTrue(result["codify_allowed"])

    def test_low_unknown_requires_review(self):
        result = self.run_pipeline(
            "instance_type",
            "t3.small",
            "t3.large",
            False,
        )

        self.assertEqual(result["security_class"], "LOW")
        self.assertEqual(result["provenance"], "UNKNOWN")
        self.assertEqual(result["decision"], "REVIEW")

    def test_critical_authorized_cannot_codify(self):
        result = self.run_pipeline(
            "iam_instance_profile",
            "old-profile",
            "new-profile",
            True,
        )

        self.assertEqual(result["security_class"], "CRITICAL")
        self.assertEqual(result["provenance"], "AUTHORIZED")
        self.assertEqual(result["decision"], "REVERT-RECOMMENDED")
        self.assertFalse(result["codify_allowed"])


if __name__ == "__main__":
    unittest.main()
