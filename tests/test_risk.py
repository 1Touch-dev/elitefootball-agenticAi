import unittest

from app.analysis.risk import (
    availability_gap_component,
    coefficient_of_variation,
    composite_risk_score,
    days_between_appearances,
    injury_risk_score,
    risk_tier,
    series_per_90,
    small_sample_penalty,
    volatility_risk_score,
)


class TestRiskHelpers(unittest.TestCase):
    def test_days_between_appearances(self):
        self.assertEqual(days_between_appearances(["2026-01-01", "2026-01-10", "2026-01-04"]), [3, 6])

    def test_coefficient_of_variation_handles_small_or_zero_means(self):
        self.assertEqual(coefficient_of_variation([1], minimum_mean=0.5), 0.0)
        self.assertGreater(coefficient_of_variation([0, 1, 0], minimum_mean=0.5), 0.0)

    def test_gap_component_increases_with_longer_absences(self):
        self.assertLess(availability_gap_component(12, 8), availability_gap_component(30, 20))

    def test_small_sample_penalty(self):
        self.assertEqual(small_sample_penalty(10), 0.0)
        self.assertEqual(small_sample_penalty(3), 6.0)
        self.assertEqual(small_sample_penalty(1), 14.0)

    def test_injury_risk_score_increases_with_gaps_and_instability(self):
        stable = injury_risk_score(23, [7, 7, 6], [90, 88, 87, 90], 4)
        unstable = injury_risk_score(32, [7, 21, 28], [90, 12, 0, 25], 4)
        self.assertGreater(unstable, stable)

    def test_volatility_risk_score_increases_with_variance(self):
        stable_minutes = [90, 90, 90, 90]
        stable_gc = series_per_90([1, 1, 1, 1], stable_minutes)
        stable_shots = series_per_90([2, 2, 2, 2], stable_minutes)

        volatile_minutes = [90, 15, 90, 10]
        volatile_gc = series_per_90([1, 0, 2, 0], volatile_minutes)
        volatile_shots = series_per_90([2, 0, 5, 0], volatile_minutes)

        self.assertGreater(
            volatility_risk_score(volatile_gc, volatile_shots, volatile_minutes, 40.0),
            volatility_risk_score(stable_gc, stable_shots, stable_minutes, 75.0),
        )

    def test_composite_score_and_tier(self):
        score = composite_risk_score(50, 50, 50)
        self.assertEqual(score, 50.0)
        self.assertEqual(risk_tier(10), "low")
        self.assertEqual(risk_tier(30), "moderate")
        self.assertEqual(risk_tier(55), "elevated")
        self.assertEqual(risk_tier(80), "high")


if __name__ == "__main__":
    unittest.main()
