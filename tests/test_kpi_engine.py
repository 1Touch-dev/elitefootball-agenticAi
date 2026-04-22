import unittest
from collections import defaultdict
from app.analysis.kpi_engine import build_kpi_engine_output

class TestKPIEngine(unittest.TestCase):
    def setUp(self):
        self.silver_tables = {
            "players": [
                {"player_name": "John Doe", "date_of_birth": "2001-01-01"}
            ],
            "player_match_stats": [
                {"player_name": "John Doe", "minutes": 90, "goals": 1, "assists": 1, "shots": 3, "passes_completed": 30},
                {"player_name": "John Doe", "minutes": 0, "goals": 0, "assists": 0, "shots": 0, "passes_completed": 0},
                {"player_name": "John Doe", "minutes": 90, "goals": 1, "assists": 0, "shots": 2, "passes_completed": 20},
                {"player_name": "Jane Roe", "minutes": 90, "goals": 1, "assists": 2, "shots": 4, "passes_completed": 40}
            ]
        }

    def test_build_kpi_engine_output(self):
        result = build_kpi_engine_output(self.silver_tables)
        self.assertGreater(len(result['rows']), 0)
        john_doe_row = next((r for r in result['rows'] if r['player_name'] == "John Doe"), None)
        self.assertIsNotNone(john_doe_row)
        self.assertAlmostEqual(john_doe_row['goals_per_90'], 1.0)
        self.assertAlmostEqual(john_doe_row['age_adjusted_kpi_score'], round(john_doe_row['base_kpi_score'] * 1.1, 3))

if __name__ == "__main__":
    unittest.main()
