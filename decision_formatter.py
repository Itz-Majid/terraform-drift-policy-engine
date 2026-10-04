def format_decision(
    resource,
    attribute,
    before,
    after,
    security_class,
    provenance_state,
    policy_result,
):
    return {
        "resource": resource,
        "change": {
            "attribute": attribute,
            "before": before,
            "after": after,
        },
        "security_class": security_class,
        "provenance": provenance_state,
        "decision": policy_result["decision"],
        "codify_allowed": policy_result["codify_allowed"],
        "reason": policy_result["reason"],
    }
