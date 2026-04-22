import unittest

from app.analysis.risk_engine import build_risk_output


class TestRiskEngine(unittest.TestCase):
    def setUp(self):
        self.silver_tables = {
            "players": [
                {"player_name": "Stable Player", "position": "Forward", "date_of_birth": "2003-01-01", "current_club": "Independiente del Valle"},
                {"player_name": "Volatile Player", "position": "Forward", "date_of_birth": "1992-05-05", "current_club": "Club Example"},
                {"player_name": "Tiny Sample", "position": "Midfielder", "date_of_birth": "2006-02-01", "current_club": "Club Example"},
            ],
            "player_match_stats": [
                {"player_name": "Stable Player", "match_date": "2026-01-01", "minutes": 90, "goals": 1, "assists": 0, "shots": 2, "yellow_cards": 0, "red_cards": 0},
                {"player_name": "Stable Player", "match_date": "2026-01-08", "minutes": 88, "goals": 1, "assists": 0, "shots": 2, "yellow_cards": 0, "red_cards": 0},
                {"player_name": "Stable Player", "match_date": "2026-01-15", "minutes": 90, "goals": 1, "assists": 1, "shots": 3, "yellow_cards": 0, "red_cards": 0},
                {"player_name": "Stable Player", "match_date": "2026-01-22", "minutes": 90, "goals": 1, "assists": 0, "shots": 2, "yellow_cards": 0, "red_cards": 0},
                {"player_name": "Volatile Player", "match_date": "2026-01-01", "minutes": 90, "goals": 2, "assists": 0, "shots": 5, "yellow_cards": 1, "red_cards": 0},
                {"player_name": "Volatile Player", "match_date": "2026-01-28", "minutes": 12, "goals": 0, "assists": 0, "shots": 0, "yellow_cards": 1, "red_cards": 0},
                {"player_name": "Volatile Player", "match_date": "2026-02-25", "minutes": 0, "goals": 0, "assists": 0, "shots": 0, "yellow_cards": 0, "red_cards": 0},
                {"player_name": "Volatile Player", "match_date": "2026-03-20", "minutes": 75, "goals": 0, "assists": 2, "shots": 1, "yellow_cards": 0, "red_cards": 1},
                {"player_name": "Tiny Sample", "match_date": "2026-03-01", "minutes": 18, "goals": 0, "assists": 0, "shots": 1, "yellow_cards": 0, "red_cards": 0},
            ],
        }
        self.gold_tables = {
            "player_features": [
                {"player_name": "Stable Player", "matches": 4, "minutes": 358, "discipline_risk_score": 0},
                {"player_name": "Volatile Player", "matches": 4, "minutes": 177, "discipline_risk_score": 4},
                {"player_name": "Tiny Sample", "matches": 1, "minutes": 18, "discipline_risk_score": 0},
            ]
        }
        self.kpi_rows = [
            {"player_name": "Stable Player", "age": 23, "consistency_score": 82.0},
            {"player_name": "Volatile Player", "age": 33, "consistency_score": 38.0},
            {"player_name": "Tiny Sample", "age": 20, "consistency_score": None},
        ]

    def test_build_risk_output(self):
        result = build_risk_output(self.silver_tables, self.gold_tables, self.kpi_rows)
        self.assertTrue(result["path"].endswith("player_risk.json"))
        self.assertEqual(len(result["rows"]), 3)

        rows = {row["player_name"]: row for row in result["rows"]}
        self.assertIn("components", rows["Stable Player"])
        self.assertIn("inputs", rows["Stable Player"])
        self.assertEqual(rows["Stable Player"]["model_version"], "risk_mvp_v1")
        self.assertGreater(rows["Volatile Player"]["risk_score"], rows["Stable Player"]["risk_score"])
        self.assertGreater(rows["Tiny Sample"]["components"]["small_sample_penalty"], 0.0)


if __name__ == "__main__":
    unittest.main()
