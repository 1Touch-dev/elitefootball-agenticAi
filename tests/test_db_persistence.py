from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import base as db_base
from app.db.persistence import ensure_database_ready, ingest_silver_tables


class TestDbPersistence(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "pap243.sqlite"
        self.report_dir = Path(self.temp_dir.name) / "bronze"
        self.engine = create_engine(f"sqlite:///{self.db_path}", future=True)
        self.session_local = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

        self.base_engine_patch = patch.object(db_base, "engine", self.engine)
        self.base_session_patch = patch.object(db_base, "SessionLocal", self.session_local)
        self.base_engine_patch.start()
        self.base_session_patch.start()

        self.persistence_settings_patch = patch("app.db.persistence.settings")
        self.mock_settings = self.persistence_settings_patch.start()
        self.mock_settings.database_url = f"sqlite:///{self.db_path}"
        self.mock_settings.bronze_data_dir = str(self.report_dir)

    def tearDown(self) -> None:
        self.persistence_settings_patch.stop()
        self.base_session_patch.stop()
        self.base_engine_patch.stop()
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_ingest_silver_tables_persists_and_verifies_rows(self):
        silver_tables = {
            "players": [
                {
                    "source": "transfermarkt",
                    "player_name": "Patrik Mercado",
                    "preferred_name": "Patrik Mercado",
                    "position": "Attacking Midfield",
                    "date_of_birth": "2003-01-01",
                    "nationality": "Ecuador",
                    "current_club": "Independiente del Valle",
                }
            ],
            "transfers": [],
            "matches": [
                {
                    "source": "fbref",
                    "external_id": "en/matches/abc123",
                    "competition": "Liga Pro",
                    "season": "2025-2026",
                    "match_date": "2026-04-20",
                    "home_club": "Independiente del Valle",
                    "away_club": "Barcelona SC",
                    "home_score": 2,
                    "away_score": 1,
                    "venue": "Banco Guayaquil",
                }
            ],
            "player_match_stats": [
                {
                    "source": "fbref",
                    "player_name": "Patrik Mercado",
                    "club_name": "Independiente del Valle",
                    "match_date": "2026-04-20",
                    "match_external_id": "en/matches/abc123",
                    "minutes": 90,
                    "goals": 1,
                    "assists": 0,
                    "yellow_cards": 0,
                    "red_cards": 0,
                    "shots": 3,
                    "passes_completed": 24,
                }
            ],
            "player_per90": [],
        }

        ensure_database_ready()
        report = ingest_silver_tables(silver_tables)

        self.assertEqual(report["status"], "success_complete")
        self.assertEqual(report["entities"]["clubs"]["inserted"], 2)
        self.assertEqual(report["entities"]["matches"]["inserted"], 1)
        self.assertEqual(report["entities"]["stats"]["inserted"], 1)
        self.assertEqual(report["verification"]["counts"]["clubs"], 2)
        self.assertEqual(report["verification"]["counts"]["players"], 1)
        self.assertEqual(report["verification"]["counts"]["matches"], 1)
        self.assertEqual(report["verification"]["counts"]["stats"], 1)
        self.assertTrue(Path(report["report_path"]).exists())
        self.assertEqual(report["verification"]["samples"]["players"][0]["full_name"], "Patrik Mercado")

    def test_ingest_silver_tables_surfaces_validation_failures_without_silent_success(self):
        silver_tables = {
            "players": [],
            "transfers": [],
            "matches": [
                {
                    "source": "fbref",
                    "external_id": None,
                    "competition": "Liga Pro",
                    "season": "2025-2026",
                    "match_date": None,
                    "home_club": "Independiente del Valle",
                    "away_club": "Barcelona SC",
                    "home_score": 2,
                    "away_score": 1,
                    "venue": "Banco Guayaquil",
                }
            ],
            "player_match_stats": [
                {
                    "source": "fbref",
                    "player_name": None,
                    "club_name": "Independiente del Valle",
                    "match_date": "2026-04-20",
                    "match_external_id": "missing-match",
                    "minutes": 90,
                    "goals": 1,
                    "assists": 0,
                    "yellow_cards": 0,
                    "red_cards": 0,
                    "shots": 3,
                    "passes_completed": 24,
                }
            ],
            "player_per90": [],
        }

        report = ingest_silver_tables(silver_tables)

        self.assertEqual(report["status"], "validation_failed")
        self.assertGreaterEqual(len(report["errors"]), 2)
        self.assertEqual(report["entities"]["matches"]["failed"], 1)
        self.assertEqual(report["entities"]["stats"]["failed"], 1)
        self.assertEqual(report["verification"]["counts"]["matches"], 0)
        self.assertEqual(report["verification"]["counts"]["stats"], 0)


if __name__ == "__main__":
    unittest.main()
