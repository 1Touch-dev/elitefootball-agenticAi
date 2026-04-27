import importlib.util
import unittest
from unittest.mock import patch

FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None

if FASTAPI_AVAILABLE:
    from fastapi.testclient import TestClient
    from app.api.data_access import ArtifactInvalidError, ArtifactUnavailableError
    from app.main import app


@unittest.skipUnless(FASTAPI_AVAILABLE, "fastapi is not installed in this environment")
class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.players = [
            {
                "player_name": "John Doe",
                "preferred_name": "John",
                "position": "Forward",
                "current_club": "Independiente del Valle",
                "nationality": "Ecuador",
                "date_of_birth": "2003-01-01",
            },
            {
                "player_name": "Jane Roe",
                "preferred_name": "Jane",
                "position": "Midfielder",
                "current_club": "Club Example",
                "nationality": "Ecuador",
                "date_of_birth": "1998-02-02",
            },
        ]
        self.features = [{"player_name": "John Doe", "minutes": 1800, "matches": 20}]
        self.kpi = [{"player_name": "John Doe", "base_kpi_score": 5.0}]
        self.valuation = [
            {
                "player_name": "John Doe",
                "position": "Forward",
                "current_club": "Independiente del Valle",
                "competition": "Copa Libertadores",
                "valuation_score": 71.2,
                "valuation_tier": "strong_mvp",
                "components": {"performance_score": 10.0},
                "inputs": {"age": 23},
                "model_version": "mvp_v1",
            },
            {
                "player_name": "Jane Roe",
                "position": "Midfielder",
                "current_club": "Club Example",
                "competition": None,
                "valuation_score": 55.0,
                "valuation_tier": "solid_mvp",
                "components": {"performance_score": 7.0},
                "inputs": {"age": 28},
                "model_version": "mvp_v1",
            },
        ]
        self.stats = [
            {
                "player_name": "John Doe",
                "match_date": "2026-01-10",
                "club_name": "Independiente del Valle",
                "minutes": 90,
                "goals": 1,
                "assists": 0,
                "shots": 4,
                "passes_completed": 20,
                "yellow_cards": 0,
                "red_cards": 0,
                "source": "fbref",
            },
            {
                "player_name": "John Doe",
                "match_date": "2026-01-01",
                "club_name": "Independiente del Valle",
                "minutes": 45,
                "goals": 0,
                "assists": 1,
                "shots": 2,
                "passes_completed": 12,
                "yellow_cards": 1,
                "red_cards": 0,
                "source": "fbref",
            },
            {
                "player_name": "Jane Roe",
                "match_date": "2026-01-05",
                "club_name": "Club Example",
                "minutes": 90,
                "goals": 0,
                "assists": 0,
                "shots": 1,
                "passes_completed": 30,
                "yellow_cards": 0,
                "red_cards": 0,
                "source": "fbref",
            },
        ]
        self.similarity = [
            {
                "player_name": "John Doe",
                "position": "Forward",
                "comparison_features": {"goal_contribution_per_90": 0.8},
                "similar_players": [
                    {"player_name": "Jane Roe", "position": "Midfielder", "distance": 0.3, "similarity_score": 70.0},
                    {"player_name": "Alex Poe", "position": "Forward", "distance": 0.4, "similarity_score": 60.0},
                ],
            }
        ]

    def test_health_and_summary(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        response = self.client.get("/summary")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("agents", payload)
        self.assertIn("orchestration", payload)
        self.assertIn("supported_task_kinds", payload["orchestration"])

    @patch("app.api.routes.inspect_dashboard_artifacts")
    def test_dashboard_status_reports_artifact_state(self, mock_inspect):
        mock_inspect.return_value = {
            "status": "empty",
            "artifacts": {
                "players": {"path": "data/silver/players.json", "exists": True, "required": True, "valid": True, "state": "empty", "row_count": 0, "error": None}
            },
            "samples": {"players": []},
        }

        response = self.client.get("/dashboard/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "empty")
        self.assertEqual(payload["artifacts"]["players"]["state"], "empty")

    @patch("app.api.routes.load_players")
    @patch("app.api.routes.load_player_features")
    @patch("app.api.routes.load_kpi_rows")
    @patch("app.api.routes.load_valuation_rows")
    def test_players_list_and_filters(self, mock_valuation, mock_kpi, mock_features, mock_players):
        mock_players.return_value = self.players
        mock_features.return_value = self.features
        mock_kpi.return_value = self.kpi
        mock_valuation.return_value = self.valuation

        response = self.client.get("/players", params={"name": "john", "position": "forward", "club": "Independiente del Valle"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["player_name"], "John Doe")
        self.assertEqual(payload["items"][0]["valuation"]["valuation_tier"], "strong_mvp")

    @patch("app.api.routes.load_player_match_stats")
    def test_player_stats(self, mock_stats):
        mock_stats.return_value = self.stats

        response = self.client.get("/players/John Doe/stats")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["items"][0]["match_date"], "2026-01-10")

    @patch("app.api.routes.load_similarity_rows")
    def test_compare(self, mock_similarity):
        mock_similarity.return_value = self.similarity

        response = self.client.get("/compare", params={"player_name": "john doe", "limit": 1})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["player_name"], "John Doe")
        self.assertEqual(len(payload["similar_players"]), 1)

    @patch("app.api.routes.load_similarity_rows")
    def test_compare_not_found(self, mock_similarity):
        mock_similarity.return_value = self.similarity

        response = self.client.get("/compare", params={"player_name": "missing player"})
        self.assertEqual(response.status_code, 404)

    @patch("app.api.routes.load_valuation_rows")
    def test_value_list_and_lookup(self, mock_valuation):
        mock_valuation.return_value = self.valuation

        response = self.client.get("/value", params={"tier": "strong_mvp"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["player_name"], "John Doe")

        lookup = self.client.get("/value", params={"player_name": "jane roe"})
        self.assertEqual(lookup.status_code, 200)
        self.assertEqual(lookup.json()["player_name"], "Jane Roe")

    @patch("app.api.routes.load_similarity_rows")
    def test_missing_artifact_returns_503(self, mock_similarity):
        mock_similarity.side_effect = ArtifactUnavailableError("Required analysis artifact is not available. Run the pipeline first.")

        response = self.client.get("/compare", params={"player_name": "John Doe"})
        self.assertEqual(response.status_code, 503)

    @patch("app.api.routes.load_similarity_rows")
    def test_invalid_artifact_returns_500(self, mock_similarity):
        mock_similarity.side_effect = ArtifactInvalidError("Artifact payload must be a list of rows: player_similarity.json.")

        response = self.client.get("/compare", params={"player_name": "John Doe"})
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
