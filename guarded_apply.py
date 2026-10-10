import hashlib
import json
import subprocess
import sys
from pathlib import Path

PLAN = Path("reconcile.tfplan")
APPROVAL = Path("reconcile-approval.json")


def main():
    if not PLAN.is_file():
        sys.exit("BLOCKED: saved plan not found.")

    if not APPROVAL.is_file():
        sys.exit("BLOCKED: approval record not found.")

    try:
        record = json.loads(APPROVAL.read_text())
    except (json.JSONDecodeError, OSError):
        sys.exit("BLOCKED: approval record is invalid.")

    if record.get("approved") is not True:
        sys.exit("BLOCKED: approval is not granted.")

    approver = record.get("approver")
    if not isinstance(approver, str) or not approver.strip():
        sys.exit("BLOCKED: approver identity is missing.")

    actual_hash = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    if record.get("plan_sha256") != actual_hash:
        sys.exit("BLOCKED: plan hash mismatch.")

    if input(f"Apply this saved plan? Approver: {approver}. Type APPLY to continue: ") != "APPLY":
        sys.exit("CANCELLED: no infrastructure changes applied.")

    subprocess.run(["terraform", "apply", str(PLAN)], check=True)


if __name__ == "__main__":
    main()
