import unittest
from unittest.mock import patch, MagicMock

from src.tools.website_inspector import fetch_website


def make_stream_response(status_code, headers=None, body_chunks=None, encoding="utf-8"):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = headers or {}
    mock_resp.encoding = encoding
    mock_resp.iter_bytes.return_value = iter(body_chunks or [])
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False
    return mock_resp


class TestWebsiteInspectorUnit(unittest.TestCase):

    @patch("src.tools.website_inspector._resolve_ips")
    @patch("src.tools.website_inspector.httpx.Client")
    def test_successful_fetch_with_login_form(self, mock_client_class, mock_resolve):
        mock_resolve.return_value = {"93.184.216.34"}
        html = b"""
        <html><head><title>Secure Login</title></head>
        <body><form><input type="password" name="pw"></form></body></html>
        """
        mock_stream_resp = make_stream_response(
            200, headers={"content-type": "text/html"}, body_chunks=[html]
        )
        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_resp
        mock_client_class.return_value.__enter__.return_value = mock_client

        evidence = fetch_website("https://example.com/login")

        self.assertTrue(evidence.fetch_successful)
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(evidence.title, "Secure Login")
        self.assertTrue(evidence.has_password_field)
        self.assertTrue(evidence.has_login_form)
        self.assertIsNone(evidence.blocked_reason)

    @patch("src.tools.website_inspector._resolve_ips")
    @patch("src.tools.website_inspector.httpx.Client")
    def test_blocked_private_ip_immediately(self, mock_client_class, mock_resolve):
        mock_resolve.return_value = {"192.168.1.1"}
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        evidence = fetch_website("http://internal-service.local/")

        self.assertFalse(evidence.fetch_successful)
        self.assertIsNotNone(evidence.blocked_reason)
        self.assertIn("private or internal", evidence.blocked_reason)
        mock_client.stream.assert_not_called()

    @patch("src.tools.website_inspector._resolve_ips")
    @patch("src.tools.website_inspector.httpx.Client")
    def test_blocked_via_redirect_to_private_ip(self, mock_client_class, mock_resolve):
        mock_resolve.side_effect = [{"93.184.216.34"}, {"127.0.0.1"}]

        redirect_resp = make_stream_response(
            302, headers={"location": "http://internal-only.example/secret"}
        )
        mock_client = MagicMock()
        mock_client.stream.return_value = redirect_resp
        mock_client_class.return_value.__enter__.return_value = mock_client

        evidence = fetch_website("https://example.com/redirect-me")

        self.assertFalse(evidence.fetch_successful)
        self.assertIsNotNone(evidence.blocked_reason)
        self.assertEqual(evidence.redirect_count, 1)

    @patch("src.tools.website_inspector._resolve_ips")
    def test_dns_resolution_failure(self, mock_resolve):
        mock_resolve.return_value = None

        evidence = fetch_website("https://this-should-not-exist.example/")

        self.assertFalse(evidence.fetch_successful)
        self.assertIsNone(evidence.blocked_reason)
        self.assertIn("DNS resolution failed", evidence.error_message)

    @patch("src.tools.website_inspector._resolve_ips")
    @patch("src.tools.website_inspector.httpx.Client")
    def test_too_many_redirects(self, mock_client_class, mock_resolve):
        mock_resolve.return_value = {"93.184.216.34"}
        redirect_resp = make_stream_response(
            302, headers={"location": "https://example.com/loop"}
        )
        mock_client = MagicMock()
        mock_client.stream.return_value = redirect_resp
        mock_client_class.return_value.__enter__.return_value = mock_client

        evidence = fetch_website("https://example.com/start")

        self.assertFalse(evidence.fetch_successful)
        self.assertIn("Too many redirects", evidence.error_message)

    @patch("src.tools.website_inspector._resolve_ips")
    @patch("src.tools.website_inspector.httpx.Client")
    def test_non_html_content_not_parsed(self, mock_client_class, mock_resolve):
        mock_resolve.return_value = {"93.184.216.34"}
        mock_stream_resp = make_stream_response(
            200, headers={"content-type": "image/png"}, body_chunks=[b"\x89PNG..."]
        )
        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream_resp
        mock_client_class.return_value.__enter__.return_value = mock_client

        evidence = fetch_website("https://example.com/logo.png")

        self.assertTrue(evidence.fetch_successful)
        self.assertIsNone(evidence.title)
        self.assertIsNone(evidence.has_password_field)
        self.assertIsNone(evidence.has_login_form)


if __name__ == "__main__":
    unittest.main()
