import socket
import ssl
import unittest
from unittest.mock import patch, MagicMock

from src.tools.tls_inspector import inspect_tls


class TestTLSInspectorUnit(unittest.TestCase):

    @patch("src.tools.tls_inspector.socket.create_connection")
    @patch("src.tools.tls_inspector.ssl.create_default_context")
    def test_valid_certificate(self, mock_context_factory, mock_create_conn):
        mock_ssock = MagicMock()
        mock_ssock.getpeercert.return_value = {
            "issuer": ((("organizationName", "Example CA"),),),
            "subject": ((("commonName", "example.com"),),),
            "notBefore": "Jan  1 00:00:00 2024 GMT",
            "notAfter": "Jan  1 00:00:00 2026 GMT",
        }
        mock_ssock.__enter__.return_value = mock_ssock

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value = mock_ssock
        mock_context_factory.return_value = mock_context

        mock_sock = MagicMock()
        mock_create_conn.return_value.__enter__.return_value = mock_sock

        evidence = inspect_tls("example.com")

        self.assertTrue(evidence.connection_successful)
        self.assertTrue(evidence.certificate_valid)
        self.assertFalse(evidence.is_self_signed)
        self.assertIn("Example CA", evidence.issuer)

    @patch("src.tools.tls_inspector.socket.create_connection")
    @patch("src.tools.tls_inspector.ssl.create_default_context")
    @patch("src.tools.tls_inspector.ssl._create_unverified_context")
    def test_self_signed_certificate(
        self, mock_unverified_factory, mock_verified_factory, mock_create_conn
    ):
        mock_verified_context = MagicMock()
        mock_verified_context.wrap_socket.side_effect = ssl.SSLCertVerificationError(
            "self-signed certificate"
        )
        mock_verified_factory.return_value = mock_verified_context

        mock_ssock = MagicMock()
        same_dn = ((("organizationName", "Fake Bank Co"),),)
        mock_ssock.getpeercert.return_value = {
            "issuer": same_dn,
            "subject": same_dn,
            "notBefore": "Jan  1 00:00:00 2026 GMT",
            "notAfter": "Jan  1 00:00:00 2027 GMT",
        }
        mock_ssock.__enter__.return_value = mock_ssock

        mock_unverified_context = MagicMock()
        mock_unverified_context.wrap_socket.return_value = mock_ssock
        mock_unverified_factory.return_value = mock_unverified_context

        mock_sock = MagicMock()
        mock_create_conn.return_value.__enter__.return_value = mock_sock

        evidence = inspect_tls("sbi-secure-login.xyz")

        self.assertTrue(evidence.connection_successful)
        self.assertFalse(evidence.certificate_valid)
        self.assertTrue(evidence.is_self_signed)
        self.assertIsNotNone(evidence.error_message)

    @patch("src.tools.tls_inspector.socket.create_connection")
    def test_connection_timeout(self, mock_create_conn):
        mock_create_conn.side_effect = socket.timeout()

        evidence = inspect_tls("unreachable-host.example")

        self.assertFalse(evidence.connection_successful)
        self.assertIn("timed out", evidence.error_message.lower())

    @patch("src.tools.tls_inspector.socket.create_connection")
    def test_connection_refused(self, mock_create_conn):
        mock_create_conn.side_effect = ConnectionRefusedError()

        evidence = inspect_tls("no-server-here.example")

        self.assertFalse(evidence.connection_successful)
        self.assertIsNotNone(evidence.error_message)


if __name__ == "__main__":
    unittest.main()
