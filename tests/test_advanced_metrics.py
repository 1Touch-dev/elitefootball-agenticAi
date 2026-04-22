import unittest
from app.analysis.advanced_metrics import per_90, progression_score, safe_sum

class TestAdvancedMetrics(unittest.TestCase):
    def test_per_90(self):
        self.assertEqual(per_90(10, 100), 9.0)
        self.assertEqual(per_90(10, None), None)
        self.assertEqual(per_90(None, 100), None)
        self.assertEqual(per_90(0, 0), None)

    def test_safe_sum(self):
        self.assertEqual(safe_sum(1, 2, None, 3), 6.0)
        self.assertEqual(safe_sum(None, None, None), 0.0)

    def test_progression_score(self):
        self.assertEqual(progression_score(3.0, 2.0, 1.0), 2.3)
        self.assertEqual(progression_score(None, None, None), 0.0)

if __name__ == "__main__":
    unittest.main()
