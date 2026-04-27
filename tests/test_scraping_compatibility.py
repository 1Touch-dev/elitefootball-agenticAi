import unittest
from unittest.mock import Mock

import requests

from app.scraping.compatibility import CompatibilityProbeResult, StaticProbeError, probe_static_request


class TestScrapingCompatibility(unittest.TestCase):
    def _response(self, *, status_code=200, text="", url="https://example.com", headers=None, cookies=None):
        response = Mock(spec=requests.Response)
        response.status_code = status_code
        response.text = text
        response.url = url
        response.headers = headers or {"Content-Type": "text/html"}
        response.cookies = requests.cookies.cookiejar_from_dict(cookies or {})
        return response

    def test_transfermarkt_static_html_classifies_ok(self):
        session = Mock(spec=requests.Session)
        session.get.return_value = self._response(
            status_code=200,
            text="<html><title>Independiente del Valle - Detailed squad 2026 | Transfermarkt</title><body>Market value Júnior Sornoza</body></html>",
            headers={"Content-Type": "text/html", "Server": "nginx"},
        )

        result = probe_static_request(
            "transfermarkt",
            "https://www.transfermarkt.com/independiente-del-valle/kader/verein/19309",
            session=session,
        )

        self.assertIsInstance(result, CompatibilityProbeResult)
        self.assertEqual(result.classification, "ok_static_html")
        self.assertFalse(result.challenge_detected)
        self.assertFalse(result.anti_bot_mitigation_required)
        self.assertGreaterEqual(result.selector_like_markers_found, 2)

    def test_fbref_challenge_classifies_challenge_page(self):
        session = Mock(spec=requests.Session)
        session.get.return_value = self._response(
            status_code=403,
            text="<html><title>Just a moment...</title><body>challenges.cloudflare.com</body></html>",
            headers={"Content-Type": "text/html", "cf-mitigated": "challenge", "Server": "cloudflare"},
            cookies={"__cf_bm": "abc"},
        )

        result = probe_static_request(
            "fbref",
            "https://fbref.com/en/squads/990519b8/Independiente-del-Valle-Stats",
            session=session,
        )

        self.assertEqual(result.classification, "challenge_page")
        self.assertTrue(result.challenge_detected)
        self.assertTrue(result.anti_bot_mitigation_required)
        self.assertIn("__cf_bm", result.cookies_seen)

    def test_request_exception_raises_static_probe_error(self):
        session = Mock(spec=requests.Session)
        session.get.side_effect = requests.RequestException("network broke")

        with self.assertRaises(StaticProbeError):
            probe_static_request("fbref", "https://fbref.com/en/test", session=session)


if __name__ == "__main__":
    unittest.main()
