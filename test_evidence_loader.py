import unittest

from evidence_loader import load_evidence
from provenance import ProvenanceState, classify_provenance


class TestEvidenceLoader(unittest.TestCase):

    def test_load_authorized_evidence(self):
        evidence = load_evidence("evidence.json")

        self.assertEqual(
            classify_provenance(evidence),
            ProvenanceState.AUTHORIZED,
        )

        self.assertEqual(evidence.actor, "authorized")
        self.assertEqual(evidence.action, "modify_instance_type")
        self.assertTrue(evidence.evidence_match)


if __name__ == "__main__":
    unittest.main()
