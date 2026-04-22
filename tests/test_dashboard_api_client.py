import unittest
from unittest.mock import Mock, patch

import requests

from dashboard.api_client import DashboardAPIClient, DashboardAPIError


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


if __name__ == "__main__":
    unittest.main()
