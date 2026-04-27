from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import logging
import re
from urllib.parse import urlparse

from app.scraping.parsers import extract_title, normalize_space, strip_tags
from app.services.logging_service import get_logger, is_debug_enabled, log_event


logger = get_logger(__name__)
PLAYER_STATS_TABLE_HINTS = ("stats_standard", "stats_summary", "stats_keeper", "stats_passing", "stats_misc")
PER90_TABLE_HINTS = ("per_90", "stats_standard", "stats_misc")
CHALLENGE_MARKERS = ("just a moment", "challenge", "captcha", "access denied")


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


def _text_to_float(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
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
    prepared = _prepare_html(html)
    text = strip_tags(prepared)
    match = re.search(r"Venue\s*:?\s*(.+?)(?=\s+(?:Attendance|Referee|Player|Season)\b|$)", text, re.IGNORECASE)
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


def _table_matches(table_id: str, hints: tuple[str, ...]) -> bool:
    return any(hint in table_id for hint in hints)


def _row_has_stat_values(stat_map: dict[str, str]) -> bool:
    keys = (
        "minutes", "min", "goals", "gls", "assists", "ast", "shots", "sh",
        "passes_completed", "cmp_passes", "xg", "xa", "prgc", "prgp", "prgr",
    )
    return any(stat_map.get(key) not in {None, "", "0", "0.0"} for key in keys)


def parse_fbref_match_payload(html: str, source_url: str) -> dict[str, object]:
    log_event(logger, logging.INFO, "parse.fbref.match.start", source="fbref", source_url=source_url)
    title = extract_title(html)
    home_score, away_score = _extract_match_score(title)
    home_club, away_club = _extract_match_teams(title)

    payload = {
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
        "challenge_detected": any(marker in (title or "").lower() for marker in CHALLENGE_MARKERS),
    }
    fields_found = sum(1 for value in payload.values() if value)
    log_event(logger, logging.INFO, "parse.fbref.match.complete", source="fbref", source_url=source_url, fields_found=fields_found)
    if not payload.get("external_id") and not payload.get("title"):
        log_event(logger, logging.WARNING, "parse.partial_result", source="fbref", source_url=source_url, section="match")
    return payload


def parse_fbref_player_match_stats(html: str, source_url: str) -> list[dict[str, object]]:
    log_event(logger, logging.INFO, "parse.fbref.player_stats.start", source="fbref", source_url=source_url)
    player_rows: list[dict[str, object]] = []
    tables = _parse_tables(html)
    candidate_table_ids: list[str] = []

    for table in tables:
        table_id = str(table.get("id", ""))
        if not _table_matches(table_id, PLAYER_STATS_TABLE_HINTS) or "per_90" in table_id:
            continue
        candidate_table_ids.append(table_id)

        rows = table.get("rows", [])
        for row in rows:
            stat_map = _row_to_stat_map(row)
            player_name = stat_map.get("player") or stat_map.get("column_0")
            if not player_name or player_name.lower() == "player":
                continue
            if not _row_has_stat_values(stat_map):
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
                    "xg": _text_to_float(stat_map.get("xg") or stat_map.get("expected_goals")),
                    "xa": _text_to_float(stat_map.get("xa") or stat_map.get("expected_assists")),
                    "progressive_carries": _text_to_int(stat_map.get("progressive_carries") or stat_map.get("prgc")),
                    "progressive_passes": _text_to_int(stat_map.get("progressive_passes") or stat_map.get("prgp")),
                    "progressive_receptions": _text_to_int(stat_map.get("progressive_passes_received") or stat_map.get("prgr")),
                    "carries_into_final_third": _text_to_int(stat_map.get("carries_into_final_third") or stat_map.get("carries_1_3")),
                    "passes_into_final_third": _text_to_int(stat_map.get("passes_into_final_third") or stat_map.get("passes_into_final_third_att")),
                    "carries_into_penalty_area": _text_to_int(stat_map.get("carries_into_penalty_area") or stat_map.get("carries_pen_area")),
                    "passes_into_penalty_area": _text_to_int(stat_map.get("passes_into_penalty_area") or stat_map.get("passes_pen_area")),
                }
            )

    log_fields = {"source": "fbref", "source_url": source_url, "tables_discovered": len(tables), "candidate_tables": len(candidate_table_ids), "records_extracted": len(player_rows)}
    if is_debug_enabled():
        log_fields["candidate_table_ids"] = candidate_table_ids
    log_event(logger, logging.INFO, "parse.fbref.player_stats.complete", **log_fields)
    if not player_rows:
        log_event(logger, logging.WARNING, "parse.empty_player_stats", source="fbref", source_url=source_url)
        log_event(logger, logging.WARNING, "parse.partial_result", source="fbref", source_url=source_url, section="player_match_stats", records_extracted=0)
    return player_rows


def parse_fbref_player_per_90(html: str, source_url: str) -> list[dict[str, object]]:
    log_event(logger, logging.INFO, "parse.fbref.per90.start", source="fbref", source_url=source_url)
    per_90_rows: list[dict[str, object]] = []
    tables = _parse_tables(html)
    candidate_table_ids: list[str] = []

    for table in tables:
        table_id = str(table.get("id", ""))
        if not _table_matches(table_id, PER90_TABLE_HINTS):
            continue
        rows = table.get("rows", [])
        for row in rows:
            stat_map = _row_to_stat_map(row)
            player_name = stat_map.get("player") or stat_map.get("column_0")
            if not player_name or player_name.lower() == "player":
                continue

            per_90_keys = [key for key in stat_map if key.endswith("_per90") or key.endswith("per90")]
            if not per_90_keys and "per_90" not in table_id:
                continue
            if table_id and table_id not in candidate_table_ids:
                candidate_table_ids.append(table_id)

            metrics = {key: stat_map[key] for key in per_90_keys if stat_map.get(key)}
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

    log_fields = {"source": "fbref", "source_url": source_url, "tables_discovered": len(tables), "candidate_tables": len(candidate_table_ids), "records_extracted": len(per_90_rows)}
    if is_debug_enabled():
        log_fields["candidate_table_ids"] = candidate_table_ids
    log_event(logger, logging.INFO, "parse.fbref.per90.complete", **log_fields)
    if not per_90_rows:
        log_event(logger, logging.WARNING, "parse.partial_result", source="fbref", source_url=source_url, section="player_per90", records_extracted=0)
    return per_90_rows
