import hashlib
import json


def canonical_hash(data):
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def validate_reconciliation(plan, proposal, approval, plan_hash):
    if not all(isinstance(x, dict) for x in (plan, proposal, approval)):
        return {"status": "BLOCKED", "reason": "Invalid input."}

    if proposal.get("mode") != "REVERT":
        return {"status": "BLOCKED", "reason": "Expected REVERT mode."}

    if proposal.get("decision") != "REVERT-RECOMMENDED":
        return {"status": "BLOCKED", "reason": "Revert policy decision required."}

    if approval.get("approved") is not True:
        return {"status": "BLOCKED", "reason": "Approval missing."}

    approver = approval.get("approver")
    if not isinstance(approver, str) or not approver.strip():
        return {"status": "BLOCKED", "reason": "Approver missing."}

    if approval.get("plan_sha256") != plan_hash:
        return {"status": "BLOCKED", "reason": "Plan hash mismatch."}

    if approval.get("proposal_hash") != canonical_hash(proposal):
        return {"status": "BLOCKED", "reason": "Proposal hash mismatch."}

    resource = proposal.get("resource")
    change = proposal.get("change")
    if not isinstance(resource, str) or not isinstance(change, dict):
        return {"status": "BLOCKED", "reason": "Invalid proposal."}

    matches = [
        r for r in plan.get("resource_changes", [])
        if r.get("address") == resource
    ]

    if len(matches) != 1:
        return {"status": "BLOCKED", "reason": "Resource missing or ambiguous."}

    actual = matches[0].get("change", {})
    before = actual.get("before") or {}
    after = actual.get("after") or {}
    attribute = change.get("attribute")

    if actual.get("actions") != ["update"]:
        return {"status": "BLOCKED", "reason": "Unexpected Terraform action."}

    if before.get(attribute) != change.get("before"):
        return {"status": "BLOCKED", "reason": "Before value mismatch."}

    if after.get(attribute) != change.get("after"):
        return {"status": "BLOCKED", "reason": "After value mismatch."}

    return {"status": "ELIGIBLE", "reason": "Plan, proposal and approval match."}
