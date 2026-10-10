import hashlib
import json
import sys
from pathlib import Path

PLAN = Path("reconcile.tfplan")
APPROVAL = Path("reconcile-approval.json")

if not PLAN.is_file():
    sys.exit("BLOCKED: saved Terraform plan not found.")

if APPROVAL.exists():
    sys.exit("BLOCKED: approval record already exists; refusing to overwrite.")

plan_hash = hashlib.sha256(PLAN.read_bytes()).hexdigest()

record = {
    "approved": False,
    "approver": "",
    "plan_sha256": plan_hash,
}

APPROVAL.write_text(json.dumps(record, indent=2) + "\n")
print("Approval request created.")
print("Plan SHA-256:", plan_hash)
print("Status: PENDING — no infrastructure changes applied.")
