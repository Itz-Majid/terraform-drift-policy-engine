SECURITY_RULES = {
    "instance_type": "LOW",
    "tags": "LOW",
    "monitoring": "MEDIUM",
    "iam_instance_profile": "CRITICAL",
    "user_data": "CRITICAL",
    "security_group_ids": "CRITICAL",
}


def classify_change(attribute):
    return SECURITY_RULES.get(attribute, "MEDIUM")
