from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProvenanceState(Enum):
    AUTHORIZED = "AUTHORIZED"
    UNEXPECTED = "UNEXPECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ProvenanceEvidence:
    actor: Optional[str]
    action: Optional[str]
    timestamp: Optional[str]
    evidence_match: bool


def classify_provenance(evidence: ProvenanceEvidence) -> ProvenanceState:
    """
    Classify provenance using WHO + WHAT + WHEN + evidence-match.

    AUTHORIZED:
        Actor, action and timestamp are present and evidence matches.

    UNEXPECTED:
        Evidence is available and matched, but the actor is not the
        expected/authorized actor.

    UNKNOWN:
        Evidence is incomplete or does not establish a trustworthy
        provenance chain.
    """

    if not evidence.evidence_match:
        return ProvenanceState.UNKNOWN

    if not evidence.actor or not evidence.action or not evidence.timestamp:
        return ProvenanceState.UNKNOWN

    if evidence.actor == "authorized":
        return ProvenanceState.AUTHORIZED

    return ProvenanceState.UNEXPECTED
