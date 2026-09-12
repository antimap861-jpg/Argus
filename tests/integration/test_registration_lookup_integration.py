import unittest
from src.tools.registration_lookup import lookup_registration


class TestRegistrationLookupIntegration(unittest.TestCase):
    """
    Integration tests. Require live internet access to IANA and
    registry RDAP servers. Run manually with:
    python -m unittest discover tests/integration
    """

    def test_lookup_known_domain(self):
        evidence = lookup_registration("google.com")
        self.assertTrue(evidence.lookup_successful)
        self.assertIsNotNone(evidence.creation_date)
        self.assertGreater(len(evidence.nameservers), 0)

    def test_lookup_nonexistent_domain(self):
        evidence = lookup_registration("this-domain-should-definitely-not-exist-argus-test.com")
        self.assertFalse(evidence.lookup_successful)
        self.assertIsNotNone(evidence.error_message)


if __name__ == "__main__":
    unittest.main()
