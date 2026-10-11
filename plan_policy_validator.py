
import json


def validate_plan_against_proposal(plan, proposal):
    if not isinstance(plan, dict) or not isinstance(proposal, dict):
        return {"status": "BLOCKED", "reason": "Invalid input."}

    if proposal.get("security_class") == "CRITICAL":
        return {"status": "BLOCKED", "reason": "CRITICAL changes are prohibited."}

    if proposal.get("codify_allowed") is not True:
        return {"status": "BLOCKED", "reason": "Policy prohibits codification."}

    if proposal.get("decision") != "CODIFY-CANDIDATE":
        return {"status": "BLOCKED", "reason": "Proposal is not eligible."}

    resource = proposal.get("resource")
    change = proposal.get("change")

    if not isinstance(resource, str) or not isinstance(change, dict):
        return {"status": "BLOCKED", "reason": "Invalid proposal structure."}

    matches = [
        item for item in plan.get("resource_changes", [])
        if item.get("address") == resource
    ]

    if len(matches) != 1:
        return {"status": "BLOCKED", "reason": "Resource missing or ambiguous."}

    actual = matches[0].get("change", {})
    before = actual.get("before") or {}
    after = actual.get("after") or {}
    attribute = change.get("attribute")

    if actual.get("actions") != ["update"]:
        return {"status": "BLOCKED", "reason": "Unexpected Terraform actions."}

    if before.get(attribute) != change.get("before"):
        return {"status": "BLOCKED", "reason": "Before value mismatch."}

    if after.get(attribute) != change.get("after"):
        return {"status": "BLOCKED", "reason": "After value mismatch."}

    return {"status": "MATCHED", "reason": "Plan matches the approved proposal."}


if __name__ == "__main__":
    with open("reconcile-plan.json") as f:
        plan = json.load(f)

    proposal = {
        "resource": "aws_instance.web",
        "change": {
            "attribute": "instance_type",
            "before": "t3.large",
            "after": "t3.small",
        },
        "security_class": "LOW",
        "decision": "CODIFY-CANDIDATE",
        "codify_allowed": True,
    }

    print(validate_plan_against_proposal(plan, proposal))
