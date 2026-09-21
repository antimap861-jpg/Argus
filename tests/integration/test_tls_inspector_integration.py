import unittest
from src.tools.tls_inspector import inspect_tls


class TestTLSInspectorIntegration(unittest.TestCase):
    """
    Integration tests. Require live internet access. Run manually with:
    python -m unittest discover tests/integration
    """

    def test_known_valid_certificate(self):
        evidence = inspect_tls("google.com")
        self.assertTrue(evidence.connection_successful)
        self.assertTrue(evidence.certificate_valid)
        self.assertIsNotNone(evidence.issuer)

    def test_nonexistent_host(self):
        evidence = inspect_tls("this-host-should-not-exist-argus-test.com")
        self.assertFalse(evidence.connection_successful)
        self.assertIsNotNone(evidence.error_message)


if __name__ == "__main__":
    unittest.main()
