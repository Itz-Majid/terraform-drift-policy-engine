import unittest

from policy_engine_v2 import evaluate_policy


class TestPolicyEngine(unittest.TestCase):

    def test_critical_never_codifies(self):
        for provenance in ["AUTHORIZED", "UNEXPECTED", "UNKNOWN"]:
            result = evaluate_policy("CRITICAL", provenance)

            self.assertFalse(result["codify_allowed"])
            self.assertEqual(
                result["decision"],
                "REVERT-RECOMMENDED",
            )

    def test_low_authorized_codify_candidate(self):
        result = evaluate_policy("LOW", "AUTHORIZED")

        self.assertTrue(result["codify_allowed"])
        self.assertEqual(
            result["decision"],
            "CODIFY-CANDIDATE",
        )

    def test_low_unknown_review(self):
        result = evaluate_policy("LOW", "UNKNOWN")

        self.assertEqual(
            result["decision"],
            "REVIEW",
        )

    def test_medium_authorized_review(self):
        result = evaluate_policy("MEDIUM", "AUTHORIZED")

        self.assertEqual(
            result["decision"],
            "REVIEW",
        )


if __name__ == "__main__":
    unittest.main()
