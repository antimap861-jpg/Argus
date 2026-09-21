import unittest
from src.tools.website_inspector import fetch_website


class TestWebsiteInspectorIntegration(unittest.TestCase):
    """
    Integration tests. Require live internet access. Run manually with:
    python -m unittest discover tests/integration
    """

    def test_fetch_known_site(self):
        evidence = fetch_website("https://example.com")
        self.assertTrue(evidence.fetch_successful)
        self.assertEqual(evidence.status_code, 200)

    def test_blocked_localhost(self):
        evidence = fetch_website("http://127.0.0.1/")
        self.assertFalse(evidence.fetch_successful)
        self.assertIsNotNone(evidence.blocked_reason)


if __name__ == "__main__":
    unittest.main()
