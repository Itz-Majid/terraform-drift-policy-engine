from policy_engine_v2 import evaluate_policy


def test_critical_never_codifies():
    for provenance in ["AUTHORIZED", "UNEXPECTED", "UNKNOWN"]:
        result = evaluate_policy("CRITICAL", provenance)

        assert result["codify_allowed"] is False
        assert result["decision"] == "REVERT-RECOMMENDED"


def test_low_authorized_codify_candidate():
    result = evaluate_policy("LOW", "AUTHORIZED")

    assert result["codify_allowed"] is True
    assert result["decision"] == "CODIFY-CANDIDATE"


def test_low_unknown_review():
    result = evaluate_policy("LOW", "UNKNOWN")

    assert result["decision"] == "REVIEW"


def test_medium_authorized_review():
    result = evaluate_policy("MEDIUM", "AUTHORIZED")

    assert result["decision"] == "REVIEW"


print("Policy tests passed.")
