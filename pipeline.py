import json

from extract_drift import extract_drift
from security_classifier import classify_change
from provenance import classify_provenance
from policy_engine_v2 import evaluate_policy
from decision_formatter import format_decision


def analyze_drift(plan_file, evidence):
    with open(plan_file) as f:
        plan = json.load(f)

    drift_items = extract_drift(plan)
    findings = []

    provenance = classify_provenance(evidence)

    for item in drift_items:
        for change in item["attributes"]:
            security_class = classify_change(change["attribute"])

            policy_result = evaluate_policy(
                security_class,
                provenance.value,
            )

            finding = format_decision(
                resource=item["resource"],
                attribute=change["attribute"],
                before=change["before"],
                after=change["after"],
                security_class=security_class,
                provenance_state=provenance.value,
                policy_result=policy_result,
            )

            findings.append(finding)

    return findings
