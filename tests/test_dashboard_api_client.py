import unittest
from unittest.mock import Mock, patch

import requests

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import build_dashboard_state, dashboard_status_message, enrich_similarity_rows, format_sync_time, placeholder_message_lines


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

    def test_build_dashboard_state_formats_sync_metadata(self):
        state = build_dashboard_state(
            {
                "status": "artifact_invalid",
                "sync": {
                    "last_successful_sync_at": "2026-04-27T10:00:00Z",
                    "last_failure_stage": "similarity",
                    "last_failure_message": "Artifact payload must be a list of rows.",
                    "recommended_action": "Check pipeline outputs and refresh.",
                },
                "diagnostics": {"recommended_action": "Check pipeline outputs and refresh."},
            }
        )

        self.assertEqual(state["category"], "upstream_failure")
        self.assertEqual(state["last_sync"], "2026-04-27 10:00 UTC") # Check that last sync is formatted correctly
        self.assertIn("similarity", state["failure"])
        self.assertIn("Check pipeline outputs", state["action"])

    def test_build_dashboard_state_defaults_when_no_sync(self):
        state = build_dashboard_state({})
        self.assertEqual(state["last_sync"], "No successful sync yet.")
        self.assertIsNone(state["failure"])

    def test_build_dashboard_state_handles_backend_error(self):
        state = build_dashboard_state(None, backend_error="connection refused")

        self.assertEqual(state["category"], "backend_error")
        self.assertEqual(state["level"], "error")
        self.assertIn("connection refused", state["message"])

    def test_placeholder_message_lines_include_sync_details(self):
        lines = placeholder_message_lines(
            {
                "message": "No dashboard data yet.",
                "last_sync": "2026-04-27 10:00 UTC",
                "failure": "players: missing artifact",
                "action": "Run the pipeline and refresh.",
            }
        )

        self.assertEqual(lines[0], "No dashboard data yet.")
        self.assertTrue(any("Last successful sync" in line for line in lines))
        self.assertTrue(any("Latest failure" in line for line in lines))
        self.assertTrue(any("Next step" in line for line in lines))

    def test_format_sync_time_returns_original_string_for_unparseable_values(self):
        self.assertEqual(format_sync_time("not-a-timestamp"), "not-a-timestamp")

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
