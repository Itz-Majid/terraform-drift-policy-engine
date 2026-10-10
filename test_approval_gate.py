import hashlib
import json
import unittest

from approval_gate import validate_approval


def make_proposal():
    return {
        "resource": "aws_instance.web",
        "change": {
            "attribute": "instance_type",
            "before": "t3.small",
            "after": "t3.large",
        },
        "security_class": "LOW",
        "decision": "CODIFY-CANDIDATE",
        "codify_allowed": True,
    }


def make_approval(proposal, approver="reviewer@example.com"):
    canonical = json.dumps(
        proposal, sort_keys=True, separators=(",", ":")
    )
    return {
        "approved": True,
        "approver": approver,
        "proposal_hash": hashlib.sha256(
            canonical.encode()
        ).hexdigest(),
    }


class TestApprovalGate(unittest.TestCase):

    def test_missing_approval_is_blocked(self):
        self.assertEqual(
            validate_approval(make_proposal(), None)["status"],
            "BLOCKED",
        )

    def test_empty_approver_is_blocked(self):
        proposal = make_proposal()
        approval = make_approval(proposal, approver=" ")
        self.assertEqual(
            validate_approval(proposal, approval)["status"],
            "BLOCKED",
        )

    def test_changed_proposal_is_blocked(self):
        proposal = make_proposal()
        approval = make_approval(proposal)
        proposal["change"]["after"] = "t3.xlarge"
        self.assertEqual(
            validate_approval(proposal, approval)["status"],
            "BLOCKED",
        )

    def test_valid_approval_is_eligible_not_executed(self):
        proposal = make_proposal()
        approval = make_approval(proposal)
        result = validate_approval(proposal, approval)
        self.assertEqual(result["status"], "ELIGIBLE")
        self.assertNotIn("applied", result)

    def test_critical_change_cannot_be_codified(self):
        proposal = make_proposal()
        proposal["security_class"] = "CRITICAL"
        proposal["decision"] = "REVERT-RECOMMENDED"
        proposal["codify_allowed"] = False
        approval = make_approval(proposal)
        self.assertEqual(
            validate_approval(proposal, approval)["status"],
            "BLOCKED",
        )


if __name__ == "__main__":
    unittest.main()
