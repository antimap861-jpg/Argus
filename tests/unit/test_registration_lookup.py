import unittest
from unittest.mock import patch, MagicMock
import httpx
from src.tools.registration_lookup import lookup_registration


def make_response(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


class TestRegistrationLookupUnit(unittest.TestCase):

    @patch("src.tools.registration_lookup.httpx.Client")
    def test_successful_lookup(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        bootstrap_response = make_response({
            "services": [[["com"], ["https://rdap.verisign.com/com/v1"]]]
        })
        rdap_response = make_response({
            "entities": [{
                "roles": ["registrar"],
                "vcardArray": ["vcard", [["fn", {}, "text", "Example Registrar Inc."]]]
            }],
            "events": [
                {"eventAction": "registration", "eventDate": "2020-01-01T00:00:00Z"},
                {"eventAction": "expiration", "eventDate": "2030-01-01T00:00:00Z"}
            ],
            "nameservers": [
                {"ldhName": "ns1.example.com"},
                {"ldhName": "ns2.example.com"}
            ]
        })
        mock_client.get.side_effect = [bootstrap_response, rdap_response]

        evidence = lookup_registration("example.com")

        self.assertTrue(evidence.lookup_successful)
        self.assertEqual(evidence.registrar, "Example Registrar Inc.")
        self.assertEqual(evidence.creation_date, "2020-01-01T00:00:00Z")
        self.assertEqual(evidence.expiration_date, "2030-01-01T00:00:00Z")
        self.assertEqual(evidence.nameservers, ["ns1.example.com", "ns2.example.com"])

    @patch("src.tools.registration_lookup.httpx.Client")
    def test_domain_not_found(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        bootstrap_response = make_response({
            "services": [[["com"], ["https://rdap.verisign.com/com/v1"]]]
        })
        not_found_response = make_response({}, status_code=404)
        mock_client.get.side_effect = [bootstrap_response, not_found_response]

        evidence = lookup_registration("this-domain-should-not-exist-xyz123.com")

        self.assertFalse(evidence.lookup_successful)
        self.assertIn("not found", evidence.error_message.lower())

    @patch("src.tools.registration_lookup.httpx.Client")
    def test_unsupported_tld(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        bootstrap_response = make_response({"services": []})
        mock_client.get.side_effect = [bootstrap_response]

        evidence = lookup_registration("example.zzz")

        self.assertFalse(evidence.lookup_successful)
        self.assertIn("no rdap server", evidence.error_message.lower())

    @patch("src.tools.registration_lookup.httpx.Client")
    def test_network_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client.get.side_effect = httpx.RequestError("Connection failed")

        evidence = lookup_registration("example.com")

        self.assertFalse(evidence.lookup_successful)
        self.assertIn("network error", evidence.error_message.lower())


if __name__ == "__main__":
    unittest.main()
