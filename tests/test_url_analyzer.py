import unittest
from src.tools.url_analyzer import analyze_url

class TestURLAnalyzer(unittest.TestCase):

    def test_analyze_standard_url(self):
        url = "https://www.example.com/path/to/page?q=search#section"
        result = analyze_url(url)
        
        self.assertEqual(result.original_url, url)
        self.assertEqual(result.scheme, "https")
        self.assertEqual(result.hostname, "www.example.com")
        self.assertEqual(result.path, "/path/to/page")
        self.assertEqual(result.query, "q=search")
        self.assertEqual(result.fragment, "section")
        self.assertIsNone(result.port)

    def test_analyze_url_with_port(self):
        url = "http://localhost:8080/api/v1/health"
        result = analyze_url(url)
        
        self.assertEqual(result.scheme, "http")
        self.assertEqual(result.hostname, "localhost")
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.path, "/api/v1/health")

    def test_analyze_suspicious_url(self):
        url = "http://sbi-secure-login.xyz"
        result = analyze_url(url)
        
        self.assertEqual(result.scheme, "http")
        self.assertEqual(result.hostname, "sbi-secure-login.xyz")
        self.assertTrue(result.path is None or result.path == "")

    def test_analyze_invalid_port(self):
        url = "http://localhost:invalidport/test"
        result = analyze_url(url)
        
        self.assertEqual(result.original_url, url)

if __name__ == "__main__":
    unittest.main()
