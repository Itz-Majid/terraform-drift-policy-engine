import json

from provenance_adapter import evidence_from_record


def load_evidence(filename):
    with open(filename) as f:
        record = json.load(f)

    return evidence_from_record(record)
