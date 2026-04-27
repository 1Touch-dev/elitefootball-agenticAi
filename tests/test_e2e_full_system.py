from __future__ import annotations

import unittest

from tests.e2e_full_pipeline_support import render_validation_report, run_full_system_validation


class TestE2EFullSystem(unittest.TestCase):
    def test_full_pipeline_validation_workflow(self):
        result = run_full_system_validation()
        report = render_validation_report(result)
        self.assertTrue(result.ok, msg=report)
        self.assertIn(result.readiness, {"READY", "READY_WITH_LIMITATIONS"}, msg=report)
        self.assertGreaterEqual(result.counts.get("silver_players", 0), 2, msg=report)
        self.assertGreaterEqual(result.counts.get("silver_matches", 0), 2, msg=report)
        self.assertGreaterEqual(result.counts.get("gold_kpi_rows", 0), 2, msg=report)
        self.assertGreaterEqual(result.counts.get("gold_valuation_rows", 0), 2, msg=report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
