
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import guarded_apply


class TestGuardedApply(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_cwd = Path.cwd()
        import os
        os.chdir(self.temp_dir.name)

        self.plan = Path("reconcile.tfplan")
        self.approval = Path("reconcile-approval.json")
        self.plan.write_bytes(b"fake-plan-for-unit-test")

    def tearDown(self):
        import os
        os.chdir(self.old_cwd)
        self.temp_dir.cleanup()

    def write_approval(self, **overrides):
        record = {
            "approved": True,
            "approver": "test-reviewer",
            "plan_sha256": hashlib.sha256(
                self.plan.read_bytes()
            ).hexdigest(),
        }
        record.update(overrides)
        self.approval.write_text(json.dumps(record))

    def test_missing_approval_is_blocked(self):
        with patch("guarded_apply.subprocess.run") as run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()
            run.assert_not_called()

    def test_unapproved_record_is_blocked(self):
        self.write_approval(approved=False)
        with patch("guarded_apply.subprocess.run") as run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()
            run.assert_not_called()

    def test_missing_approver_is_blocked(self):
        self.write_approval(approver="")
        with patch("guarded_apply.subprocess.run") as run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()
            run.assert_not_called()

    def test_plan_hash_mismatch_is_blocked(self):
        self.write_approval(plan_sha256="incorrect-hash")
        with patch("guarded_apply.subprocess.run") as run:
            with self.assertRaises(SystemExit):
                guarded_apply.main()
            run.assert_not_called()

    def test_valid_approval_invokes_apply_without_real_execution(self):
        self.write_approval()
        with patch("builtins.input", return_value="APPLY"):
            with patch("guarded_apply.subprocess.run") as run:
                guarded_apply.main()
                run.assert_called_once_with(
                    ["terraform", "apply", "reconcile.tfplan"],
                    check=True,
                )


if __name__ == "__main__":
    unittest.main()
