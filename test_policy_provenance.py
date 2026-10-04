import unittest

from provenance import (
    ProvenanceEvidence,
    ProvenanceState,
    classify_provenance,
)
from policy_engine_v2 import evaluate_policy


class TestPolicyProvenance(unittest.TestCase):

    def test_authorized_low_becomes_codify_candidate(self):
        evidence = ProvenanceEvidence(
            actor="authorized",
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=True,
        )

        provenance = classify_provenance(evidence)
        result = evaluate_policy("LOW", provenance.value)

        self.assertEqual(provenance, ProvenanceState.AUTHORIZED)
        self.assertEqual(result["decision"], "CODIFY-CANDIDATE")

    def test_unknown_low_requires_review(self):
        evidence = ProvenanceEvidence(
            actor="authorized",
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=False,
        )

        provenance = classify_provenance(evidence)
        result = evaluate_policy("LOW", provenance.value)

        self.assertEqual(provenance, ProvenanceState.UNKNOWN)
        self.assertEqual(result["decision"], "REVIEW")

    def test_unexpected_low_requires_review(self):
        evidence = ProvenanceEvidence(
            actor="unknown-user",
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=True,
        )

        provenance = classify_provenance(evidence)
        result = evaluate_policy("LOW", provenance.value)

        self.assertEqual(provenance, ProvenanceState.UNEXPECTED)
        self.assertEqual(result["decision"], "REVIEW")

    def test_critical_blocks_codification_regardless_of_provenance(self):
        for actor, evidence_match in [
            ("authorized", True),
            ("unknown-user", True),
            ("authorized", False),
        ]:
            evidence = ProvenanceEvidence(
                actor=actor,
                action="modify_instance_type",
                timestamp="2026-10-04T10:00:00Z",
                evidence_match=evidence_match,
            )

            provenance = classify_provenance(evidence)
            result = evaluate_policy("CRITICAL", provenance.value)

            self.assertFalse(result["codify_allowed"])
            self.assertEqual(
                result["decision"],
                "REVERT-RECOMMENDED",
            )


if __name__ == "__main__":
    unittest.main()
