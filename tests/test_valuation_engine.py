import unittest

from app.analysis.valuation_engine import build_valuation_output


class TestValuationEngine(unittest.TestCase):
    def setUp(self):
        self.silver_tables = {
            "players": [
                {
                    "player_name": "John Doe",
                    "position": "Forward",
                    "date_of_birth": "2003-01-01",
                    "current_club": "Independiente del Valle",
                },
                {
                    "player_name": "Jane Roe",
                    "position": "Midfielder",
                    "date_of_birth": "1995-06-10",
                    "current_club": "Club Example",
                },
            ],
            "matches": [
                {"competition": "Copa Libertadores"},
            ],
            "player_match_stats": [
                {"player_name": "John Doe", "club_name": "Independiente del Valle"},
                {"player_name": "Jane Roe", "club_name": "Club Example"},
            ],
        }
        self.gold_tables = {
            "player_features": [
                {
                    "player_name": "John Doe",
                    "matches": 10,
                    "minutes": 1800,
                    "goal_contribution_per_90": 0.8,
                    "shots": 20,
                    "discipline_risk_score": 1,
                },
                {
                    "player_name": "Jane Roe",
                    "matches": 10,
                    "minutes": 900,
                    "goal_contribution_per_90": 0.3,
                    "shots": 8,
                    "discipline_risk_score": 4,
                },
            ]
        }
        self.kpi_rows = [
            {"player_name": "John Doe", "age": 23, "minutes_played": 1800, "base_kpi_score": 5.0, "consistency_score": 70.0},
            {"player_name": "Jane Roe", "age": 30, "minutes_played": 900, "base_kpi_score": 2.0, "consistency_score": 40.0},
        ]
        self.advanced_rows = [
            {"player_name": "John Doe", "progression_score": 10.0},
            {"player_name": "Jane Roe", "progression_score": 2.0},
        ]
        self.risk_rows = [
            {
                "player_name": "John Doe",
                "risk_score": 20.0,
                "components": {"injury_risk_score": 18.0, "volatility_risk_score": 24.0},
            },
            {
                "player_name": "Jane Roe",
                "risk_score": 80.0,
                "components": {"injury_risk_score": 70.0, "volatility_risk_score": 75.0},
            },
        ]

    def test_build_valuation_output(self):
        result = build_valuation_output(self.silver_tables, self.gold_tables, self.kpi_rows, self.advanced_rows, self.risk_rows)
        self.assertEqual(len(result["rows"]), 2)
        self.assertTrue(result["path"].endswith("player_valuation.json"))

        john_doe = result["rows"][0]
        self.assertEqual(john_doe["player_name"], "John Doe")
        self.assertEqual(john_doe["valuation_tier"], "strong_mvp")
        self.assertEqual(john_doe["components"]["club_factor"], 8.0)
        self.assertEqual(john_doe["components"]["league_adjustment"], 6.0)
        self.assertEqual(john_doe["inputs"]["player_risk_score"], 20.0)
        self.assertGreater(john_doe["valuation_score"], result["rows"][1]["valuation_score"])

    def test_build_valuation_output_without_optional_inputs(self):
        result = build_valuation_output(
            {"players": [], "matches": [], "player_match_stats": [{"player_name": "Fallback Player"}]},
            {"player_features": [{"player_name": "Fallback Player", "matches": 2, "minutes": 180, "goal_contribution_per_90": 0.5, "shots": 4, "discipline_risk_score": 0}]},
            [],
            [],
        )
        row = result["rows"][0]
        self.assertEqual(row["player_name"], "Fallback Player")
        self.assertEqual(row["components"]["club_factor"], 4.0)
        self.assertEqual(row["components"]["league_adjustment"], 4.0)
        self.assertEqual(row["model_version"], "mvp_v2_risk")

    def test_build_valuation_output_falls_back_without_risk_rows(self):
        without_risk = build_valuation_output(self.silver_tables, self.gold_tables, self.kpi_rows, self.advanced_rows, [])
        with_risk = build_valuation_output(self.silver_tables, self.gold_tables, self.kpi_rows, self.advanced_rows, self.risk_rows)
        john_without_risk = next(row for row in without_risk["rows"] if row["player_name"] == "John Doe")
        john_with_risk = next(row for row in with_risk["rows"] if row["player_name"] == "John Doe")
        jane_without_risk = next(row for row in without_risk["rows"] if row["player_name"] == "Jane Roe")
        jane_with_risk = next(row for row in with_risk["rows"] if row["player_name"] == "Jane Roe")
        self.assertGreater(john_without_risk["valuation_score"], john_with_risk["valuation_score"])
        self.assertGreater(jane_without_risk["valuation_score"], jane_with_risk["valuation_score"])


if __name__ == "__main__":
    unittest.main()
