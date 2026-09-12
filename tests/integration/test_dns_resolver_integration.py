import unittest
from src.tools.dns_resolver import resolve_hostname


class TestDNSResolverIntegration(unittest.TestCase):
    """
    Integration tests. These require live internet/DNS access and are
    NOT run as part of the fast unit suite. Run manually with:
    python -m unittest discover tests/integration
    """

    def test_resolve_known_domain(self):
        evidence = resolve_hostname("google.com")
        self.assertTrue(evidence.resolved)
        self.assertGreater(len(evidence.ip_addresses), 0)
        self.assertIsNone(evidence.error_message)

    def test_resolve_nonexistent_domain(self):
        evidence = resolve_hostname("this-domain-should-definitely-not-exist.test")
        self.assertFalse(evidence.resolved)
        self.assertEqual(evidence.ip_addresses, [])
        self.assertIsNotNone(evidence.error_message)


if __name__ == "__main__":
    unittest.main()
