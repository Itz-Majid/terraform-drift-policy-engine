import hashlib
import json


def _proposal_hash(proposal):
    canonical = json.dumps(
        proposal,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def validate_approval(proposal, approval):
    if not isinstance(proposal, dict):
        return {"status": "BLOCKED", "reason": "Invalid proposal."}

    if proposal.get("security_class") == "CRITICAL":
        return {
            "status": "BLOCKED",
            "reason": "CRITICAL changes cannot be codified.",
        }

    if proposal.get("codify_allowed") is not True:
        return {
            "status": "BLOCKED",
            "reason": "Policy prohibits codification.",
        }

    if proposal.get("decision") != "CODIFY-CANDIDATE":
        return {
            "status": "BLOCKED",
            "reason": "Proposal is not eligible for codification.",
        }

    if not isinstance(approval, dict) or approval.get("approved") is not True:
        return {
            "status": "BLOCKED",
            "reason": "Explicit approval is required.",
        }

    approver = approval.get("approver")
    if not isinstance(approver, str) or not approver.strip():
        return {
            "status": "BLOCKED",
            "reason": "A valid approver identity is required.",
        }

    if approval.get("proposal_hash") != _proposal_hash(proposal):
        return {
            "status": "BLOCKED",
            "reason": "Approval does not match the exact proposal.",
        }

    return {
        "status": "ELIGIBLE",
        "reason": "Approval validated; no infrastructure action executed.",
    }
