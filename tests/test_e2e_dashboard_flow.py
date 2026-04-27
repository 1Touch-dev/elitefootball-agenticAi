from __future__ import annotations

import unittest

from tests.e2e_dashboard_flow_support import render_validation_report, run_e2e_dashboard_flow


class TestE2EDashboardFlow(unittest.TestCase):
    def test_seeded_scrape_to_dashboard_flow(self):
        result = run_e2e_dashboard_flow()
        report = render_validation_report(result)
        self.assertTrue(result.ok, msg=report)
        self.assertGreaterEqual(result.counts.get("silver_players", 0), 2, msg=report)
        self.assertGreaterEqual(result.counts.get("gold_similarity_rows", 0), 2, msg=report)
        self.assertGreaterEqual(result.counts.get("gold_valuation_rows", 0), 2, msg=report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
