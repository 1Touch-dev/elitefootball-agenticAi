import unittest

from app.analysis.valuation import (
    age_score,
    clamp_score,
    club_factor,
    league_adjustment,
    minutes_score,
    performance_score,
    risk_score,
    valuation_tier,
)


class TestValuation(unittest.TestCase):
    def test_performance_score_prefers_kpi(self):
        self.assertEqual(performance_score(4.0, 10.0, 0.5, 4, 2), 33.2)

    def test_performance_score_fallback_without_kpi(self):
        self.assertEqual(performance_score(None, None, 1.0, 6, 3), 22.0)

    def test_age_score(self):
        self.assertEqual(age_score(20), 18.0)
        self.assertEqual(age_score(23), 16.0)
        self.assertEqual(age_score(26), 13.0)
        self.assertEqual(age_score(30), 9.0)
        self.assertEqual(age_score(31), 5.0)
        self.assertEqual(age_score(35), 5.0)
        self.assertEqual(age_score(None), 10.0)

    def test_minutes_score(self):
        self.assertEqual(minutes_score(900), 3.0)
        self.assertEqual(minutes_score(4500), 15.0)

    def test_club_factor(self):
        self.assertEqual(club_factor("Independiente del Valle"), 8.0)
        self.assertEqual(club_factor("IDV"), 8.0)
        self.assertEqual(club_factor("IDV U20"), 3.0)
        self.assertEqual(club_factor(None), 4.0)

    def test_league_adjustment(self):
        self.assertEqual(league_adjustment("Copa Libertadores", None), 6.0)
        self.assertEqual(league_adjustment("Youth League", None), 2.0)
        self.assertEqual(league_adjustment(None, None), 4.0)

    def test_risk_score(self):
        self.assertEqual(risk_score(2, 50), 3.8)
        self.assertEqual(risk_score(None, None), 0.0)

    def test_clamp_and_tier(self):
        self.assertEqual(clamp_score(120), 100.0)
        self.assertEqual(valuation_tier(86), "elite_mvp")
        self.assertEqual(valuation_tier(72), "strong_mvp")
        self.assertEqual(valuation_tier(60), "solid_mvp")
        self.assertEqual(valuation_tier(45), "rotation_mvp")
        self.assertEqual(valuation_tier(10), "development_mvp")


if __name__ == "__main__":
    unittest.main()
