import unittest
from collections import defaultdict
from app.analysis.advanced_metrics_engine import build_advanced_metrics_output

class TestAdvancedMetricsEngine(unittest.TestCase):
    def setUp(self):
        self.silver_tables = {
            "player_match_stats": [
                {"player_name": "John Doe", "minutes": 90, "goals": 1, "assists": 1, "xg": 0.5, "xa": 0.4, "progressive_carries": 5, "progressive_passes": 10, "progressive_receptions": 4, "carries_into_final_third": 2, "passes_into_final_third": 6, "carries_into_penalty_area": 0, "passes_into_penalty_area": 1},
                {"player_name": "John Doe", "minutes": 90, "goals": 0, "assists": 0, "xg": 0.3, "xa": 0.1, "progressive_carries": 8, "progressive_passes": 7, "progressive_receptions": 5, "carries_into_final_third": 1, "passes_into_final_third": 3, "carries_into_penalty_area": 1, "passes_into_penalty_area": 1}
            ]
        }

    def test_build_advanced_metrics_output(self):
        result = build_advanced_metrics_output(self.silver_tables)
        self.assertGreater(len(result['rows']), 0)
        john_doe_row = next((r for r in result['rows'] if r['player_name'] == "John Doe"), None)
        self.assertIsNotNone(john_doe_row)
        self.assertAlmostEqual(john_doe_row['xg_per_90'], 0.4)
        self.assertAlmostEqual(john_doe_row['xa_per_90'], 0.25)

if __name__ == "__main__":
    unittest.main()
