import unittest

from reconciliation_gate import canonical_hash, validate_reconciliation


class TestReconciliationGate(unittest.TestCase):
    def setUp(self):
        self.plan = {
            "resource_changes": [{
                "address": "aws_instance.web",
                "change": {
                    "actions": ["update"],
                    "before": {"instance_type": "t3.large"},
                    "after": {"instance_type": "t3.small"},
                },
            }]
        }
        self.proposal = {
            "resource": "aws_instance.web",
            "mode": "REVERT",
            "decision": "REVERT-RECOMMENDED",
            "change": {
                "attribute": "instance_type",
                "before": "t3.large",
                "after": "t3.small",
            },
        }
        self.plan_hash = "test-plan-hash"
        self.approval = {
            "approved": True,
            "approver": "test-reviewer",
            "plan_sha256": self.plan_hash,
            "proposal_hash": canonical_hash(self.proposal),
        }

    def check(self, plan=None, proposal=None, approval=None):
        return validate_reconciliation(
            plan or self.plan,
            proposal or self.proposal,
            approval or self.approval,
            self.plan_hash,
        )["status"]

    def test_matching_revert_is_eligible(self):
        self.assertEqual(self.check(), "ELIGIBLE")

    def test_missing_approval_is_blocked(self):
        approval = dict(self.approval, approved=False)
        self.assertEqual(self.check(approval=approval), "BLOCKED")

    def test_changed_proposal_is_blocked(self):
        proposal = dict(self.proposal)
        proposal["change"] = dict(self.proposal["change"], after="t3.xlarge")
        self.assertEqual(self.check(proposal=proposal), "BLOCKED")

    def test_plan_hash_mismatch_is_blocked(self):
        approval = dict(self.approval, plan_sha256="wrong-hash")
        self.assertEqual(self.check(approval=approval), "BLOCKED")

    def test_codify_mode_is_blocked(self):
        proposal = dict(self.proposal, mode="CODIFY")
        self.assertEqual(self.check(proposal=proposal), "BLOCKED")


if __name__ == "__main__":
    unittest.main()
