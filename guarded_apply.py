import hashlib
import json
import subprocess
import sys
from pathlib import Path

from reconciliation_gate import validate_reconciliation

PLAN = Path("reconcile.tfplan")
PROPOSAL = Path("reconcile-proposal.json")
APPROVAL = Path("reconcile-approval.json")


def main():
    for path in (PLAN, PROPOSAL, APPROVAL):
        if not path.is_file():
            sys.exit(f"BLOCKED: required file missing: {path}")

    try:
        proposal = json.loads(PROPOSAL.read_text())
        approval = json.loads(APPROVAL.read_text())
        plan_hash = hashlib.sha256(PLAN.read_bytes()).hexdigest()

        result = subprocess.run(
            ["terraform", "show", "-json", str(PLAN)],
            capture_output=True,
            text=True,
            check=True,
        )
        plan = json.loads(result.stdout)
    except (OSError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        sys.exit(f"BLOCKED: could not verify saved plan: {exc}")

    decision = validate_reconciliation(
        plan, proposal, approval, plan_hash
    )
    if decision["status"] != "ELIGIBLE":
        sys.exit(f"BLOCKED: {decision['reason']}")

    approver = approval["approver"]
    if input(
        f"Plan validated. Approver: {approver}. "
        "Type APPLY to execute the saved plan: "
    ) != "APPLY":
        sys.exit("CANCELLED: no infrastructure changes applied.")

    subprocess.run(["terraform", "apply", str(PLAN)], check=True)


if __name__ == "__main__":
    main()
