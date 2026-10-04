SECURITY_RULES = {
    "LOW": True,
    "MEDIUM": True,
    "CRITICAL": False,
}

TRUST_LEVELS = {
    "AUTHORIZED": 3,
    "UNEXPECTED": 2,
    "UNKNOWN": 1,
}


def evaluate_policy(security_class, provenance_state):
    codify_allowed = SECURITY_RULES[security_class]
    trust_level = TRUST_LEVELS[provenance_state]

    if not codify_allowed:
        return {
            "decision": "REVERT-RECOMMENDED",
            "codify_allowed": False,
            "reason": "CRITICAL security class blocks codification regardless of provenance.",
        }

    if security_class == "LOW" and provenance_state == "AUTHORIZED":
        return {
            "decision": "CODIFY-CANDIDATE",
            "codify_allowed": True,
            "reason": "LOW-risk drift with authorized provenance.",
        }

    return {
        "decision": "REVIEW",
        "codify_allowed": True,
        "reason": f"{security_class}-risk drift requires human review for {provenance_state.lower()} provenance.",
    }
