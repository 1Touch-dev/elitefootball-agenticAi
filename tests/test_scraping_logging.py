import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.pipeline.silver import build_silver_tables
from app.scraping.browser import BrowserConfig, PlaywrightUnavailableError, fetch_page_html
from app.scraping.transfermarkt import scrape_transfermarkt_player
from app.scraping.storage import save_parsed_payload, save_raw_html
from app.services import logging_service


class TestScrapingLogging(unittest.TestCase):
    def tearDown(self):
        root = logging.getLogger()
        for handler in list(root.handlers):
            try:
                handler.flush()
            except Exception:
                pass

    def test_fetch_page_html_logs_missing_playwright(self):
        with patch("app.scraping.browser.sync_playwright", None):
            with self.assertLogs("app.scraping.browser", level="ERROR") as captured:
                with self.assertRaises(PlaywrightUnavailableError):
                    fetch_page_html("https://example.com", BrowserConfig(), source="transfermarkt", slug="example")
        output = "\n".join(captured.output)
        self.assertIn("fetch.playwright_unavailable", output)
        self.assertIn("PlaywrightUnavailableError", output)

    def test_storage_logs_write_attempts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertLogs("app.scraping.storage", level="INFO") as captured:
                raw_path = save_raw_html("sample-player", "<html>ok</html>", directory=tmpdir)
                parsed_path = save_parsed_payload("sample-player", {"profile": {"player_name": "Sample"}}, directory=tmpdir)
            self.assertTrue(Path(raw_path).exists())
            self.assertTrue(Path(parsed_path).exists())
        output = "\n".join(captured.output)
        self.assertIn("storage.write_raw.start", output)
        self.assertIn("storage.write_raw.success", output)
        self.assertIn("storage.write_parsed.start", output)
        self.assertIn("storage.write_parsed.success", output)

    @patch("app.scraping.transfermarkt.fetch_page_html")
    @patch("app.scraping.transfermarkt.save_parsed_payload")
    @patch("app.scraping.transfermarkt.save_raw_html")
    def test_transfermarkt_empty_results_are_logged(self, mock_save_raw, mock_save_parsed, mock_fetch):
        mock_fetch.return_value = "<html><title>Example</title></html>"
        mock_save_raw.return_value = "data/raw/transfermarkt/example.html"
        mock_save_parsed.return_value = "data/parsed/transfermarkt/example.json"
        with self.assertLogs("app.scraping.transfermarkt", level="WARNING") as captured:
            result = scrape_transfermarkt_player("https://example.com/player")
        self.assertEqual(result["slug"], "player")
        output = "\n".join(captured.output)
        self.assertIn("scrape.empty_result", output)

    def test_silver_empty_output_is_logged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            previous_tm = logging_service.settings.parsed_data_dir
            previous_fb = logging_service.settings.fbref_parsed_data_dir
            previous_silver = logging_service.settings.silver_data_dir
            previous_bronze = logging_service.settings.bronze_data_dir
            object.__setattr__(logging_service.settings, "parsed_data_dir", tmpdir)
            object.__setattr__(logging_service.settings, "fbref_parsed_data_dir", tmpdir)
            object.__setattr__(logging_service.settings, "silver_data_dir", tmpdir)
            object.__setattr__(logging_service.settings, "bronze_data_dir", tmpdir)
            try:
                with self.assertLogs("app.pipeline.silver", level="WARNING") as captured:
                    result = build_silver_tables()
            finally:
                object.__setattr__(logging_service.settings, "parsed_data_dir", previous_tm)
                object.__setattr__(logging_service.settings, "fbref_parsed_data_dir", previous_fb)
                object.__setattr__(logging_service.settings, "silver_data_dir", previous_silver)
                object.__setattr__(logging_service.settings, "bronze_data_dir", previous_bronze)
        self.assertEqual(len(result["tables"]["players"]), 0)
        self.assertIn("silver.empty_output", "\n".join(captured.output))
