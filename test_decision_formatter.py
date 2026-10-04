import unittest

from decision_formatter import format_decision


class TestDecisionFormatter(unittest.TestCase):

    def test_formats_policy_decision(self):
        policy_result = {
            "decision": "CODIFY-CANDIDATE",
            "codify_allowed": True,
            "reason": "LOW-risk drift with authorized provenance.",
        }

        result = format_decision(
            resource="aws_instance.web",
            attribute="instance_type",
            before="t3.small",
            after="t3.large",
            security_class="LOW",
            provenance_state="AUTHORIZED",
            policy_result=policy_result,
        )

        self.assertEqual(result["resource"], "aws_instance.web")
        self.assertEqual(result["change"]["attribute"], "instance_type")
        self.assertEqual(result["change"]["before"], "t3.small")
        self.assertEqual(result["change"]["after"], "t3.large")
        self.assertEqual(result["security_class"], "LOW")
        self.assertEqual(result["provenance"], "AUTHORIZED")
        self.assertEqual(result["decision"], "CODIFY-CANDIDATE")
        self.assertTrue(result["codify_allowed"])


if __name__ == "__main__":
    unittest.main()
