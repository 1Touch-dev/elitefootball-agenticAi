import unittest
from unittest.mock import patch

from app.scraping.fbref import scrape_fbref_page
from app.scraping.fbref_parsers import parse_fbref_match_payload, parse_fbref_player_match_stats, parse_fbref_player_per_90
from app.scraping.parsers import parse_player_profile, parse_transfer_history
from app.scraping.transfermarkt import scrape_transfermarkt_player
from app.scraping.validation import validate_fbref_payload, validate_transfermarkt_payload


TRANSFERMARKT_HTML = """
<html>
  <head>
    <title>Patrik Mercado - Independiente del Valle | Transfermarkt</title>
    <meta property="og:title" content="Patrik Mercado - Independiente del Valle | Transfermarkt" />
  </head>
  <body>
    <div>Name in home country: Patrik David Mercado</div>
    <div>Position: Attacking Midfield</div>
    <div>Date of birth: Jan 1, 2003</div>
    <div>Citizenship: Ecuador</div>
    <div>Current club: Independiente del Valle</div>
    <div>Market value: €5.50m</div>
    <table>
      <tr><th>Season</th><th>Date</th><th>Left</th><th>Joined</th><th>MV</th><th>Fee</th></tr>
      <tr><td>2023</td><td>Jan 1, 2023</td><td>IDV U20</td><td>Independiente del Valle</td><td>€1.00m</td><td>-</td></tr>
    </table>
  </body>
</html>
"""

FBREF_HTML = """
<html>
  <head><title>Independiente del Valle 2–1 Barcelona SC Match Report</title></head>
  <body>
    <div>Competition: Liga Pro Season 2025-2026 Venue Banco Guayaquil</div>
    <time datetime="2026-04-20"></time>
    <!--
    <table id="stats_standard">
      <tr>
        <th data-stat="player">Player</th>
        <th data-stat="team">Team</th>
        <th data-stat="minutes">Min</th>
        <th data-stat="goals">Gls</th>
        <th data-stat="assists">Ast</th>
        <th data-stat="shots">Sh</th>
        <th data-stat="passes_completed">Cmp</th>
        <th data-stat="xg">xG</th>
        <th data-stat="xa">xA</th>
        <th data-stat="prgc">PrgC</th>
        <th data-stat="prgp">PrgP</th>
        <th data-stat="prgr">PrgR</th>
      </tr>
      <tr>
        <td data-stat="player">Patrik Mercado</td>
        <td data-stat="team">Independiente del Valle</td>
        <td data-stat="minutes">90</td>
        <td data-stat="goals">1</td>
        <td data-stat="assists">0</td>
        <td data-stat="shots">3</td>
        <td data-stat="passes_completed">24</td>
        <td data-stat="xg">0.42</td>
        <td data-stat="xa">0.05</td>
        <td data-stat="prgc">5</td>
        <td data-stat="prgp">4</td>
        <td data-stat="prgr">7</td>
      </tr>
    </table>
    <table id="stats_standard_per_90">
      <tr><th data-stat="player">Player</th><th data-stat="team">Team</th><th data-stat="goals_per90">Gls/90</th><th data-stat="assists_per90">Ast/90</th></tr>
      <tr><td data-stat="player">Patrik Mercado</td><td data-stat="team">Independiente del Valle</td><td data-stat="goals_per90">1.00</td><td data-stat="assists_per90">0.00</td></tr>
    </table>
    -->
  </body>
</html>
"""

FBREF_CHALLENGE_HTML = "<html><head><title>Just a moment...</title></head><body>challenge</body></html>"


class TestScrapingExtraction(unittest.TestCase):
    def test_transfermarkt_parser_extracts_profile_and_transfer(self):
        profile = parse_player_profile(TRANSFERMARKT_HTML, "https://example.com/player")
        transfers = parse_transfer_history(TRANSFERMARKT_HTML, "https://example.com/player")
        diagnostics = validate_transfermarkt_payload(profile, transfers)

        self.assertEqual(profile["player_name"], "Patrik Mercado")
        self.assertEqual(profile["position"], "Attacking Midfield")
        self.assertEqual(profile["current_club"], "Independiente del Valle")
        self.assertEqual(len(transfers), 1)
        self.assertEqual(transfers[0]["to_club"], "Independiente del Valle")
        self.assertEqual(diagnostics["extraction_status"], "success_complete")

    def test_fbref_parser_extracts_match_stats_and_per90(self):
        match_payload = parse_fbref_match_payload(FBREF_HTML, "https://fbref.com/en/matches/abc/2025-2026/Match")
        player_rows = parse_fbref_player_match_stats(FBREF_HTML, "https://fbref.com/en/matches/abc/2025-2026/Match")
        per90_rows = parse_fbref_player_per_90(FBREF_HTML, "https://fbref.com/en/matches/abc/2025-2026/Match")
        diagnostics = validate_fbref_payload(match_payload, player_rows, per90_rows)

        self.assertEqual(match_payload["home_club"], "Independiente del Valle")
        self.assertEqual(match_payload["away_club"], "Barcelona SC")
        self.assertEqual(len(player_rows), 1)
        self.assertEqual(player_rows[0]["player_name"], "Patrik Mercado")
        self.assertEqual(player_rows[0]["minutes"], 90)
        self.assertEqual(len(per90_rows), 1)
        self.assertEqual(per90_rows[0]["metrics"]["goals_per90"], "1.00")
        self.assertEqual(diagnostics["extraction_status"], "success_complete")

    @patch("app.scraping.transfermarkt.fetch_page_html", return_value=TRANSFERMARKT_HTML)
    @patch("app.scraping.transfermarkt.save_raw_html", return_value="data/raw/transfermarkt/patrik.html")
    @patch("app.scraping.transfermarkt.save_parsed_payload", return_value="data/parsed/transfermarkt/patrik.json")
    def test_transfermarkt_scrape_returns_diagnostics(self, _save_parsed, _save_raw, _fetch):
        result = scrape_transfermarkt_player("https://www.transfermarkt.com/player")
        self.assertEqual(result["payload"]["diagnostics"]["extraction_status"], "success_complete")
        self.assertEqual(result["payload"]["diagnostics"]["sample_records"]["profile"]["player_name"], "Patrik Mercado")

    @patch("app.scraping.fbref.fetch_page_html", return_value=FBREF_CHALLENGE_HTML)
    @patch("app.scraping.fbref.save_raw_html", return_value="data/raw/fbref/challenge.html")
    @patch("app.scraping.fbref.save_parsed_payload", return_value="data/parsed/fbref/challenge.json")
    def test_fbref_scrape_classifies_challenge_without_silent_success(self, _save_parsed, _save_raw, _fetch):
        result = scrape_fbref_page("https://fbref.com/en/squads/abc/Stats")
        diagnostics = result["payload"]["diagnostics"]
        self.assertEqual(diagnostics["extraction_status"], "challenge_page")
        self.assertEqual(diagnostics["sample_records"]["player_match_stat"], None)


if __name__ == "__main__":
    unittest.main()
