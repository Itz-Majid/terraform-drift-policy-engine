import json


IGNORED_ATTRIBUTES = {
    "public_dns",
    "public_ip",
}


def extract_drift(plan):
    results = []

    for resource in plan.get("resource_drift", []):
        change = resource.get("change", {})
        actions = change.get("actions", [])

        if actions == ["no-op"]:
            continue

        before = change.get("before", {})
        after = change.get("after", {})

        attributes = []

        for key in before:
            if key in IGNORED_ATTRIBUTES:
                continue

            old = before.get(key)
            new = after.get(key)

            if old != new:
                attributes.append({
                    "attribute": key,
                    "before": old,
                    "after": new,
                })

        if attributes:
            results.append({
                "resource": resource["address"],
                "actions": actions,
                "attributes": attributes,
            })

    return results


if __name__ == "__main__":
    with open("drift.json") as f:
        plan = json.load(f)

    drift = extract_drift(plan)

    print("=== NORMALIZED DRIFT ===")

    for item in drift:
        print(f"\nResource: {item['resource']}")
        print(f"Actions: {item['actions']}")

        for change in item["attributes"]:
            print(f"Change: {change['attribute']}")
            print(f"Before: {change['before']}")
            print(f"After:  {change['after']}")
