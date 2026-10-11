import json
import os
import tempfile
import unittest

from pipeline import analyze_drift
from provenance import ProvenanceEvidence


class TestCriticalProvenanceMatrix(unittest.TestCase):

    def test_critical_drift_never_allows_codification(self):
        plan = {
            "resource_drift": [{
                "address": "aws_instance.web",
                "change": {
                    "actions": ["update"],
                    "before": {"iam_instance_profile": "old"},
                    "after": {"iam_instance_profile": "new"},
                },
            }]
        }

        cases = [
            ProvenanceEvidence(
                actor="authorized",
                action="modify_iam_instance_profile",
                timestamp="2026-10-11T09:00:00Z",
                evidence_match=True,
            ),
            ProvenanceEvidence(
                actor="unknown-user",
                action="modify_iam_instance_profile",
                timestamp="2026-10-11T09:00:00Z",
                evidence_match=True,
            ),
            ProvenanceEvidence(
                actor=None,
                action=None,
                timestamp=None,
                evidence_match=False,
            ),
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(plan, f)
            filename = f.name

        try:
            for evidence in cases:
                findings = analyze_drift(filename, evidence)

                self.assertEqual(len(findings), 1)
                finding = findings[0]

                self.assertEqual(finding["security_class"], "CRITICAL")
                self.assertEqual(
                    finding["decision"], "REVERT-RECOMMENDED"
                )
                self.assertFalse(finding["codify_allowed"])
        finally:
            os.unlink(filename)


if __name__ == "__main__":
    unittest.main()
