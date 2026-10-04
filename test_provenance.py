import unittest

from provenance import (
    ProvenanceEvidence,
    ProvenanceState,
    classify_provenance,
)


class TestProvenance(unittest.TestCase):

    def test_authorized(self):
        evidence = ProvenanceEvidence(
            actor="authorized",
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=True,
        )

        self.assertEqual(
            classify_provenance(evidence),
            ProvenanceState.AUTHORIZED,
        )

    def test_unexpected(self):
        evidence = ProvenanceEvidence(
            actor="unknown-user",
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=True,
        )

        self.assertEqual(
            classify_provenance(evidence),
            ProvenanceState.UNEXPECTED,
        )

    def test_unknown_missing_evidence(self):
        evidence = ProvenanceEvidence(
            actor="authorized",
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=False,
        )

        self.assertEqual(
            classify_provenance(evidence),
            ProvenanceState.UNKNOWN,
        )

    def test_unknown_incomplete(self):
        evidence = ProvenanceEvidence(
            actor=None,
            action="modify_instance_type",
            timestamp="2026-10-04T10:00:00Z",
            evidence_match=True,
        )

        self.assertEqual(
            classify_provenance(evidence),
            ProvenanceState.UNKNOWN,
        )


if __name__ == "__main__":
    unittest.main()
