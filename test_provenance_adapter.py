import unittest

from provenance import ProvenanceState, classify_provenance
from provenance_adapter import evidence_from_record


class TestProvenanceAdapter(unittest.TestCase):

    def test_authorized_record(self):
        record = {
            "actor": "authorized",
            "action": "modify_instance_type",
            "timestamp": "2026-10-04T10:00:00Z",
            "evidence_match": True,
        }

        evidence = evidence_from_record(record)

        self.assertEqual(
            classify_provenance(evidence),
            ProvenanceState.AUTHORIZED,
        )

    def test_missing_evidence_is_unknown(self):
        record = {
            "actor": "authorized",
            "action": "modify_instance_type",
            "timestamp": None,
            "evidence_match": False,
        }

        evidence = evidence_from_record(record)

        self.assertEqual(
            classify_provenance(evidence),
            ProvenanceState.UNKNOWN,
        )


if __name__ == "__main__":
    unittest.main()
