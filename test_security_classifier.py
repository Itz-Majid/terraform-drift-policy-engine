import unittest

from security_classifier import classify_change


class TestSecurityClassifier(unittest.TestCase):

    def test_instance_type_is_low(self):
        self.assertEqual(
            classify_change("instance_type"),
            "LOW",
        )

    def test_monitoring_is_medium(self):
        self.assertEqual(
            classify_change("monitoring"),
            "MEDIUM",
        )

    def test_iam_profile_is_critical(self):
        self.assertEqual(
            classify_change("iam_instance_profile"),
            "CRITICAL",
        )

    def test_unknown_attribute_defaults_to_medium(self):
        self.assertEqual(
            classify_change("unknown_attribute"),
            "MEDIUM",
        )


if __name__ == "__main__":
    unittest.main()
