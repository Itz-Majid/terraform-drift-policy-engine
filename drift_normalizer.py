def is_empty(value):
    return value is None or value == {} or value == []


def is_meaningful_change(before, after):
    # Ignore provider normalization between empty representations.
    if is_empty(before) and is_empty(after):
        return False

    return before != after


def normalize_drift(drift_items):
    normalized = []

    for item in drift_items:
        attributes = []

        for change in item["attributes"]:
            if is_meaningful_change(
                change["before"],
                change["after"],
            ):
                attributes.append(change)

        if attributes:
            normalized.append({
                "resource": item["resource"],
                "actions": item["actions"],
                "attributes": attributes,
            })

    return normalized
