import unittest
from app.analysis.kpi_formulas import (
    per_90,
    rolling_average,
    bounded_consistency_score,
    age_multiplier,
    base_kpi_score,
    age_in_years,
    parse_birth_date
)

class TestKPIFormulas(unittest.TestCase):
    def test_per_90(self):
        self.assertEqual(per_90(10, 1000), 0.9)
        self.assertEqual(per_90(10, None), None)
        self.assertEqual(per_90(None, 1000), None)
        self.assertEqual(per_90(0, 0), None)

    def test_age(self):
        self.assertEqual(age_in_years("2001-01-01"), 22)
        self.assertEqual(age_in_years(None), None)
        self.assertEqual(parse_birth_date("01/01/1990"), "1990-01-01")
        self.assertEqual(parse_birth_date(None), None)

    def test_rolling_average(self):
        self.assertEqual(rolling_average([1, 2, 3, 4, 5], 3), 4.0)
        self.assertEqual(rolling_average([None, 2, None, 4, 5], 2), 4.5)
        self.assertEqual(rolling_average([], 2), None)

    def test_consistency_score(self):
        self.assertEqual(bounded_consistency_score([1, 1, 1, 1, 1]), 100.0)
        self.assertEqual(bounded_consistency_score([1, 2, 1, 2, 1]), bounded_consistency_score([1, 2, 2, 2, 1]))

    def test_base_kpi_score(self):
        self.assertEqual(base_kpi_score(1, 1, 1, 0), 0.8)
        self.assertEqual(base_kpi_score(None, 1, 1, 0), 0.5)
        self.assertEqual(base_kpi_score(1, None, 1, 0), 0.6)
        self.assertEqual(base_kpi_score(1, 1, None, 0), 0.65)

    def test_age_multiplier(self):
        self.assertEqual(age_multiplier(20), 1.1)
        self.assertEqual(age_multiplier(23), 1.05)
        self.assertEqual(age_multiplier(28), 1.0)

if __name__ == "__main__":
    unittest.main()
