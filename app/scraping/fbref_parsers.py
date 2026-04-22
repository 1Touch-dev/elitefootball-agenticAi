from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import urlparse

from app.scraping.parsers import extract_title, normalize_space, strip_tags


class _FBrefTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[dict[str, object]] = []
        self._current_table: dict[str, object] | None = None
        self._current_row: list[dict[str, str]] | None = None
        self._current_cell: dict[str, str] | None = None
        self._cell_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "table":
            self._current_table = {"id": attr_map.get("id", ""), "rows": []}
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = {
                "text": "",
                "data_stat": attr_map.get("data-stat", ""),
                "tag": tag,
            }
            self._cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            self._current_cell["text"] = normalize_space(unescape(" ".join(self._cell_parts)))
            self._current_row.append(self._current_cell)
            self._current_cell = None
            self._cell_parts = []
        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            if self._current_row:
                self._current_table["rows"].append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._current_table is not None:
            self.tables.append(self._current_table)
            self._current_table = None


def _prepare_html(html: str) -> str:
    return html.replace("<!--", "").replace("-->", "")


def _parse_tables(html: str) -> list[dict[str, object]]:
    parser = _FBrefTableParser()
    parser.feed(_prepare_html(html))
    return parser.tables


def _text_to_int(value: str | None) -> int | None:
    if not value:
        return None
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def _extract_match_score(title: str | None) -> tuple[int | None, int | None]:
    if not title:
        return None, None
    match = re.search(r"(\d+)\s*[–\-]\s*(\d+)", title)
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def _extract_match_date(html: str) -> str | None:
    match = re.search(r'<time[^>]+datetime=["\']([^"\']+)["\']', html, re.IGNORECASE)
    return match.group(1) if match else None


def _extract_venue(html: str) -> str | None:
    match = re.search(r"Venue\s*:?\s*([^<\n]+)", strip_tags(_prepare_html(html)), re.IGNORECASE)
    return normalize_space(match.group(1)) if match else None


def _derive_external_id(source_url: str) -> str | None:
    path = urlparse(source_url).path.strip("/")
    return path or None


def _extract_match_teams(title: str | None) -> tuple[str | None, str | None]:
    if not title:
        return None, None

    normalized_title = title.replace(" Match Report", "")
    versus_match = re.search(r"(.+?)\s+vs\.?\s+(.+)", normalized_title, re.IGNORECASE)
    if versus_match:
        return normalize_space(versus_match.group(1)), normalize_space(versus_match.group(2))

    score_match = re.search(r"(.+?)\s+\d+\s*[–\-]\s*\d+\s+(.+)", normalized_title)
    if score_match:
        return normalize_space(score_match.group(1)), normalize_space(score_match.group(2))

    return None, None


def _extract_competition(html: str) -> str | None:
    text = strip_tags(_prepare_html(html))
    match = re.search(r"Competition\s*:?\s*([^\n]+?)\s+(?:Season|Venue|Attendance|Referee)", text, re.IGNORECASE)
    if match:
        return normalize_space(match.group(1))
    return None


def _extract_season(source_url: str, html: str) -> str | None:
    url_match = re.search(r"/([0-9]{4}-[0-9]{4})/", source_url)
    if url_match:
        return url_match.group(1)

    text = strip_tags(_prepare_html(html))
    text_match = re.search(r"Season\s*:?\s*([0-9]{4}-[0-9]{4})", text, re.IGNORECASE)
    return text_match.group(1) if text_match else None


def _row_to_stat_map(row: list[dict[str, str]]) -> dict[str, str]:
    output: dict[str, str] = {}
    for index, cell in enumerate(row):
        key = cell.get("data_stat") or f"column_{index}"
        output[key] = cell.get("text", "")
    return output


def parse_fbref_match_payload(html: str, source_url: str) -> dict[str, object]:
    title = extract_title(html)
    home_score, away_score = _extract_match_score(title)
    home_club, away_club = _extract_match_teams(title)

    return {
        "source": "fbref",
        "source_url": source_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "external_id": _derive_external_id(source_url),
        "competition": _extract_competition(html),
        "season": _extract_season(source_url, html),
        "match_date": _extract_match_date(html),
        "home_club": home_club,
        "away_club": away_club,
        "home_score": home_score,
        "away_score": away_score,
        "venue": _extract_venue(html),
        "title": title,
    }


def parse_fbref_player_match_stats(html: str, source_url: str) -> list[dict[str, object]]:
    player_rows: list[dict[str, object]] = []

    for table in _parse_tables(html):
        table_id = str(table.get("id", ""))
        if "stats" not in table_id and "summary" not in table_id:
            continue

        rows = table.get("rows", [])
        for row in rows:
            stat_map = _row_to_stat_map(row)
            player_name = stat_map.get("player") or stat_map.get("column_0")
            if not player_name or player_name.lower() == "player":
                continue

            player_rows.append(
                {
                    "source": "fbref",
                    "source_url": source_url,
                    "table_id": table_id,
                    "player_name": player_name,
                    "club_name": stat_map.get("squad") or stat_map.get("team"),
                    "minutes": _text_to_int(stat_map.get("minutes") or stat_map.get("min")),
                    "goals": _text_to_int(stat_map.get("goals") or stat_map.get("gls")),
                    "assists": _text_to_int(stat_map.get("assists") or stat_map.get("ast")),
                    "yellow_cards": _text_to_int(stat_map.get("cards_yellow") or stat_map.get("crdy")),
                    "red_cards": _text_to_int(stat_map.get("cards_red") or stat_map.get("crdr")),
                    "shots": _text_to_int(stat_map.get("shots") or stat_map.get("sh")),
                    "passes_completed": _text_to_int(stat_map.get("passes_completed") or stat_map.get("cmp_passes")),
                }
            )

    return player_rows


def parse_fbref_player_per_90(html: str, source_url: str) -> list[dict[str, object]]:
    per_90_rows: list[dict[str, object]] = []

    for table in _parse_tables(html):
        table_id = str(table.get("id", ""))
        rows = table.get("rows", [])
        for row in rows:
            stat_map = _row_to_stat_map(row)
            player_name = stat_map.get("player") or stat_map.get("column_0")
            if not player_name or player_name.lower() == "player":
                continue

            per_90_keys = [key for key in stat_map if key.endswith("_per90") or key.endswith("per90")]
            if not per_90_keys and "per_90" not in table_id:
                continue

            metrics = {key: stat_map[key] for key in per_90_keys}
            if not metrics:
                continue

            per_90_rows.append(
                {
                    "source": "fbref",
                    "source_url": source_url,
                    "table_id": table_id,
                    "player_name": player_name,
                    "club_name": stat_map.get("squad") or stat_map.get("team"),
                    "metrics": metrics,
                }
            )

    return per_90_rows
