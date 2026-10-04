import json
import unittest

from extract_drift import extract_drift
from security_classifier import classify_change
from provenance import ProvenanceEvidence, classify_provenance
from policy_engine_v2 import evaluate_policy


class TestEndToEnd(unittest.TestCase):

    def test_low_authorized_drift(self):
        with open("drift.json") as f:
            plan = json.load(f)

        drift = extract_drift(plan)

        change = drift[0]["attributes"][0]

        security_class = classify_change(change["attribute"])

        evidence = ProvenanceEvidence(
            actor="authorized",
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=True,
        )

        provenance = classify_provenance(evidence)

        result = evaluate_policy(
            security_class,
            provenance.value,
        )

        self.assertEqual(security_class, "LOW")
        self.assertEqual(provenance.value, "AUTHORIZED")
        self.assertEqual(result["decision"], "CODIFY-CANDIDATE")
        self.assertTrue(result["codify_allowed"])


if __name__ == "__main__":
    unittest.main()
