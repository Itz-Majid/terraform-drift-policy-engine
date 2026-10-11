
import unittest

from plan_policy_validator import validate_plan_against_proposal


def make_plan():
    return {
        "resource_changes": [{
            "address": "aws_instance.web",
            "change": {
                "actions": ["update"],
                "before": {"instance_type": "t3.large"},
                "after": {"instance_type": "t3.small"},
            },
        }]
    }


def make_proposal():
    return {
        "resource": "aws_instance.web",
        "change": {
            "attribute": "instance_type",
            "before": "t3.large",
            "after": "t3.small",
        },
        "security_class": "LOW",
        "decision": "CODIFY-CANDIDATE",
        "codify_allowed": True,
    }


class TestPlanPolicyValidator(unittest.TestCase):

    def test_matching_plan_is_accepted(self):
        result = validate_plan_against_proposal(
            make_plan(), make_proposal()
        )
        self.assertEqual(result["status"], "MATCHED")

    def test_wrong_after_value_is_blocked(self):
        proposal = make_proposal()
        proposal["change"]["after"] = "t3.xlarge"
        result = validate_plan_against_proposal(make_plan(), proposal)
        self.assertEqual(result["status"], "BLOCKED")

    def test_wrong_before_value_is_blocked(self):
        proposal = make_proposal()
        proposal["change"]["before"] = "t3.medium"
        result = validate_plan_against_proposal(make_plan(), proposal)
        self.assertEqual(result["status"], "BLOCKED")

    def test_critical_proposal_is_blocked(self):
        proposal = make_proposal()
        proposal["security_class"] = "CRITICAL"
        result = validate_plan_against_proposal(make_plan(), proposal)
        self.assertEqual(result["status"], "BLOCKED")

    def test_unexpected_action_is_blocked(self):
        plan = make_plan()
        plan["resource_changes"][0]["change"]["actions"] = [
            "delete", "create"
        ]
        result = validate_plan_against_proposal(plan, make_proposal())
        self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
