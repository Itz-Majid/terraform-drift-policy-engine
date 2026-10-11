import hashlib
import json
import sys
from pathlib import Path

from reconciliation_gate import canonical_hash

PLAN = Path("reconcile.tfplan")
PROPOSAL = Path("reconcile-proposal.json")
APPROVAL = Path("reconcile-approval.json")

if not PLAN.is_file() or not PROPOSAL.is_file():
    sys.exit("BLOCKED: saved plan or proposal missing.")

if APPROVAL.exists():
    sys.exit("BLOCKED: approval record already exists.")

proposal = json.loads(PROPOSAL.read_text())

record = {
    "approved": False,
    "approver": "",
    "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
    "proposal_hash": canonical_hash(proposal),
}

APPROVAL.write_text(json.dumps(record, indent=2) + "\n")
print("Approval request created.")
print("Status: PENDING — no infrastructure changes applied.")
