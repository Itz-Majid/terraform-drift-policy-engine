from provenance import ProvenanceEvidence


def evidence_from_record(record):
    return ProvenanceEvidence(
        actor=record.get("actor"),
        action=record.get("action"),
        timestamp=record.get("timestamp"),
        evidence_match=record.get("evidence_match", False),
    )
