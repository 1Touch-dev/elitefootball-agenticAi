from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.api.data_access import ArtifactInvalidError, ArtifactUnavailableError, inspect_artifact, inspect_dashboard_artifacts, load_players


class TestDataAccess(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.players_path = root / "players.json"
        self.stats_path = root / "player_match_stats.json"
        self.features_path = root / "player_features.json"
        self.kpi_path = root / "kpi.json"
        self.similarity_path = root / "player_similarity.json"
        self.valuation_path = root / "player_valuation.json"
        self.path_patch = patch(
            "app.api.data_access.ARTIFACT_PATHS",
            {
                "players": self.players_path,
                "player_match_stats": self.stats_path,
                "player_features": self.features_path,
                "kpi": self.kpi_path,
                "similarity": self.similarity_path,
                "valuation": self.valuation_path,
            },
        )
        self.path_patch.start()

    def tearDown(self) -> None:
        self.path_patch.stop()
        self.temp_dir.cleanup()

    def test_inspect_artifact_reports_empty_valid_list(self):
        self.players_path.write_text("[]", encoding="utf-8")

        artifact = inspect_artifact("players")

        self.assertEqual(artifact["state"], "empty")
        self.assertTrue(artifact["valid"])
        self.assertEqual(artifact["row_count"], 0)

    def test_load_players_raises_for_invalid_payload(self):
        self.players_path.write_text(json.dumps({"unexpected": True}), encoding="utf-8")

        with self.assertRaises(ArtifactInvalidError):
            load_players(required=True)

    def test_inspect_dashboard_artifacts_reports_missing_vs_ready(self):
        self.players_path.write_text(json.dumps([{"player_name": "Patrik Mercado"}]), encoding="utf-8")
        self.stats_path.write_text("[]", encoding="utf-8")
        self.features_path.write_text("[]", encoding="utf-8")
        self.kpi_path.write_text("[]", encoding="utf-8")
        self.similarity_path.write_text("[]", encoding="utf-8")
        self.valuation_path.write_text("[]", encoding="utf-8")

        status = inspect_dashboard_artifacts(sample_limit=1)

        self.assertEqual(status["status"], "partial")
        self.assertEqual(status["diagnostics"]["upstream_status"], "partially_available")
        self.assertIn("recommended_action", status["sync"])
        self.assertIsNotNone(status["sync"]["last_successful_sync_at"])
        self.assertEqual(status["artifacts"]["players"]["state"], "ready")
        self.assertEqual(status["artifacts"]["player_match_stats"]["state"], "empty")
        self.assertEqual(status["samples"]["players"][0]["player_name"], "Patrik Mercado")

    def test_inspect_dashboard_artifacts_reports_failure_metadata_for_missing_required_artifact(self):
        self.players_path.write_text(json.dumps([{"player_name": "Patrik Mercado"}]), encoding="utf-8")
        self.features_path.write_text("[]", encoding="utf-8")
        self.kpi_path.write_text("[]", encoding="utf-8")

        status = inspect_dashboard_artifacts(sample_limit=1)

        self.assertEqual(status["status"], "artifact_missing")
        self.assertEqual(status["sync"]["last_failure_stage"], "player_match_stats")
        self.assertIsNotNone(status["sync"]["last_failure_message"])
        self.assertEqual(status["diagnostics"]["upstream_status"], "pipeline_output_missing")

    def test_load_players_raises_for_missing_required_artifact(self):
        with self.assertRaises(ArtifactUnavailableError):
            load_players(required=True)


if __name__ == "__main__":
    unittest.main()
