import unittest

from drift_normalizer import normalize_drift


class TestDriftNormalizer(unittest.TestCase):

    def test_empty_state_normalization_is_ignored(self):
        drift = [{
            "resource": "aws_instance.web",
            "actions": ["update"],
            "attributes": [{
                "attribute": "tags",
                "before": None,
                "after": {},
            }],
        }]

        self.assertEqual(normalize_drift(drift), [])

    def test_real_tag_change_is_kept(self):
        drift = [{
            "resource": "aws_instance.web",
            "actions": ["update"],
            "attributes": [{
                "attribute": "tags",
                "before": {"env": "dev"},
                "after": {"env": "prod"},
            }],
        }]

        result = normalize_drift(drift)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["attributes"][0]["attribute"],
            "tags",
        )

    def test_instance_type_change_is_kept(self):
        drift = [{
            "resource": "aws_instance.web",
            "actions": ["update"],
            "attributes": [{
                "attribute": "instance_type",
                "before": "t3.small",
                "after": "t3.large",
            }],
        }]

        result = normalize_drift(drift)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["attributes"][0]["after"],
            "t3.large",
        )


if __name__ == "__main__":
    unittest.main()
