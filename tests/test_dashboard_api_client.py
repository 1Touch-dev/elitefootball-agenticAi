import unittest
from unittest.mock import Mock, patch

import requests

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import dashboard_status_message, enrich_similarity_rows


class TestDashboardApiClient(unittest.TestCase):
    @patch("dashboard.api_client.requests.get")
    def test_get_players_success(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"count": 1, "items": [{"player_name": "John Doe"}]}
        mock_get.return_value = response

        client = DashboardAPIClient(base_url="http://example.com")
        payload = client.get_players(name="john")

        self.assertEqual(payload["count"], 1)
        mock_get.assert_called_once()

    @patch("dashboard.api_client.requests.get")
    def test_get_dashboard_status_success(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"status": "empty", "artifacts": {}, "samples": {}}
        mock_get.return_value = response

        client = DashboardAPIClient(base_url="http://example.com")
        payload = client.get_dashboard_status()

        self.assertEqual(payload["status"], "empty")

    @patch("dashboard.api_client.requests.get")
    def test_backend_unavailable_raises_dashboard_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("connection refused")

        client = DashboardAPIClient(base_url="http://example.com")
        with self.assertRaises(DashboardAPIError):
            client.get_compare("John Doe")

    @patch("dashboard.api_client.requests.get")
    def test_invalid_json_raises_dashboard_error(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("bad json")
        mock_get.return_value = response

        client = DashboardAPIClient(base_url="http://example.com")
        with self.assertRaises(DashboardAPIError):
            client.get_value(player_name="John Doe")

    @patch("dashboard.api_client.requests.get")
    def test_unexpected_payload_type_raises_dashboard_error(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = [{"player_name": "John Doe"}]
        mock_get.return_value = response

        client = DashboardAPIClient(base_url="http://example.com")
        with self.assertRaises(DashboardAPIError):
            client.get_health()

    def test_dashboard_status_message_distinguishes_empty_from_ready(self):
        self.assertEqual(dashboard_status_message({"status": "empty"})[0], "warning")
        self.assertEqual(dashboard_status_message({"status": "ready"})[0], "success")

    def test_enrich_similarity_rows_preserves_similarity_fields(self):
        rows = [{"player_name": "Jane Roe", "distance": 0.3, "similarity_score": 70.0, "position": "Midfielder"}]
        lookup = {"Jane Roe": {"player_name": "Jane Roe", "valuation_score": 55.0, "valuation_tier": "solid_mvp", "model_version": "mvp_v1"}}

        enriched = enrich_similarity_rows(rows, lookup)

        self.assertEqual(enriched[0]["distance"], 0.3)
        self.assertEqual(enriched[0]["similarity_score"], 70.0)
        self.assertEqual(enriched[0]["valuation_score"], 55.0)
        self.assertEqual(enriched[0]["valuation_tier"], "solid_mvp")


if __name__ == "__main__":
    unittest.main()
