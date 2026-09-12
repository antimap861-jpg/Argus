import unittest
import socket
from unittest.mock import patch
from src.tools.dns_resolver import resolve_hostname


class TestDNSResolverUnit(unittest.TestCase):

    @patch("src.tools.dns_resolver.socket.getaddrinfo")
    def test_resolve_hostname_success(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (2, 1, 6, '', ('93.184.216.34', 0)),
            (2, 1, 6, '', ('93.184.216.34', 0)),
        ]
        evidence = resolve_hostname("example.com")
        self.assertTrue(evidence.resolved)
        self.assertEqual(evidence.hostname, "example.com")
        self.assertEqual(evidence.ip_addresses, ["93.184.216.34"])
        self.assertIsNone(evidence.error_message)

    @patch("src.tools.dns_resolver.socket.getaddrinfo")
    def test_resolve_hostname_gaierror(self, mock_getaddrinfo):
        mock_getaddrinfo.side_effect = socket.gaierror("Name or service not known")
        evidence = resolve_hostname("this-domain-should-not-exist.test")
        self.assertFalse(evidence.resolved)
        self.assertEqual(evidence.ip_addresses, [])
        self.assertIsNotNone(evidence.error_message)

    @patch("src.tools.dns_resolver.socket.getaddrinfo")
    def test_resolve_hostname_unicode_error(self, mock_getaddrinfo):
        mock_getaddrinfo.side_effect = UnicodeError("label too long")
        evidence = resolve_hostname("a" * 100 + ".com")
        self.assertFalse(evidence.resolved)
        self.assertIsNotNone(evidence.error_message)
        self.assertIn("Invalid hostname encoding", evidence.error_message)


if __name__ == "__main__":
    unittest.main()
