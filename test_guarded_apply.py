import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import subprocess

import guarded_apply
from reconciliation_gate import canonical_hash


class TestGuardedApply(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

        self.plan_file = Path("reconcile.tfplan")
        self.proposal_file = Path("reconcile-proposal.json")
        self.approval_file = Path("reconcile-approval.json")

        self.plan_file.write_bytes(b"mock-saved-terraform-plan")

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
        self.proposal_file.write_text(
            json.dumps(self.proposal, indent=2) + "\n"
        )

        self.plan = {
            "resource_changes": [
                {
                    "address": "aws_instance.web",
                    "change": {
                        "actions": ["update"],
                        "before": {"instance_type": "t3.large"},
                        "after": {"instance_type": "t3.small"},
                    },
                }
            ]
        }

        self.show_result = subprocess.CompletedProcess(
            args=["terraform", "show", "-json", str(self.plan_file)],
            returncode=0,
            stdout=json.dumps(self.plan),
            stderr="",
        )

        self.approval = {
            "approved": True,
            "approver": "test-reviewer",
            "plan_sha256": hashlib.sha256(
                self.plan_file.read_bytes()
            ).hexdigest(),
            "proposal_hash": canonical_hash(self.proposal),
        }

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp_dir.cleanup()

    def write_approval(self, approval=None):
        if approval is not None:
            self.approval_file.write_text(json.dumps(approval))

    def assert_apply_not_called(self, mocked_run):
        self.assertFalse(
            any(
                call.args[0][:2] == ["terraform", "apply"]
                for call in mocked_run.call_args_list
            ),
            "terraform apply must not run when approval is invalid",
        )

    def test_missing_approval_is_blocked(self):
        with patch("guarded_apply.subprocess.run") as mocked_run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()

        mocked_run.assert_not_called()

    def test_unapproved_record_is_blocked(self):
        approval = dict(self.approval)
        approval["approved"] = False
        self.write_approval(approval)

        with patch(
            "guarded_apply.subprocess.run",
            return_value=self.show_result,
        ) as mocked_run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()

        self.assert_apply_not_called(mocked_run)

    def test_missing_approver_is_blocked(self):
        approval = dict(self.approval)
        approval["approver"] = ""
        self.write_approval(approval)

        with patch(
            "guarded_apply.subprocess.run",
            return_value=self.show_result,
        ) as mocked_run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()

        self.assert_apply_not_called(mocked_run)

    def test_plan_hash_mismatch_is_blocked(self):
        approval = dict(self.approval)
        approval["plan_sha256"] = "incorrect-hash"
        self.write_approval(approval)

        with patch(
            "guarded_apply.subprocess.run",
            return_value=self.show_result,
        ) as mocked_run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()

        self.assert_apply_not_called(mocked_run)

    def test_valid_approval_invokes_apply_without_real_execution(self):
        self.write_approval(self.approval)

        with patch(
            "guarded_apply.subprocess.run",
            side_effect=[
                self.show_result,
                subprocess.CompletedProcess(
                    args=["terraform", "apply", str(self.plan_file)],
                    returncode=0,
                    stdout="",
                    stderr="",
                ),
            ],
        ) as mocked_run, patch(
            "builtins.input", return_value="APPLY"
        ):
            guarded_apply.main()

        apply_calls = [
            call for call in mocked_run.call_args_list
            if call.args[0][:2] == ["terraform", "apply"]
        ]
        self.assertEqual(len(apply_calls), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
