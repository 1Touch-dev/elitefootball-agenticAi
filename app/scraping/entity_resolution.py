"""
Cross-source entity resolution: matches players from Transfermarkt, FBref, and Sofascore
using name similarity + age + club hints. Returns a canonical player_slug for each record.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

# Minimum similarity score to consider two names a match
_NAME_THRESHOLD = 0.80
# Minimum score for a confident cross-source match
_CONFIDENT_THRESHOLD = 0.88


def _normalize_name(name: str) -> str:
    """Lowercase, strip accents, collapse whitespace, remove punctuation."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_str = ascii_str.lower()
    ascii_str = re.sub(r"[^\w\s]", "", ascii_str)
    return re.sub(r"\s+", " ", ascii_str).strip()


def _name_similarity(a: str, b: str) -> float:
    na, nb = _normalize_name(a), _normalize_name(b)
    if na == nb:
        return 1.0
    # SequenceMatcher ratio
    ratio = SequenceMatcher(None, na, nb).ratio()
    # Bonus: one name is a substring of the other (handles "Ronaldo" vs "Cristiano Ronaldo")
    if na in nb or nb in na:
        ratio = max(ratio, 0.85)
    return ratio


def _age_matches(age_a: int | None, age_b: int | None, tolerance: int = 1) -> bool:
    if age_a is None or age_b is None:
        return True  # can't rule out
    return abs(age_a - age_b) <= tolerance


def _club_matches(club_a: str | None, club_b: str | None) -> bool:
    if not club_a or not club_b:
        return True  # can't rule out
    return _normalize_name(club_a) == _normalize_name(club_b)


def _position_matches(pos_a: str | None, pos_b: str | None) -> bool:
    if not pos_a or not pos_b:
        return True
    broad = {
        "fw": {"fw", "st", "cf", "lw", "rw", "ss", "forward", "striker", "winger"},
        "mf": {"mf", "cm", "am", "dm", "lm", "rm", "mid", "midfielder"},
        "df": {"df", "cb", "lb", "rb", "lwb", "rwb", "defender", "back"},
        "gk": {"gk", "goalkeeper", "keeper"},
    }
    def broad_pos(p: str) -> str | None:
        p = p.lower().strip()
        for key, variants in broad.items():
            if p in variants:
                return key
        return None

    return broad_pos(pos_a) == broad_pos(pos_b)


def compute_match_score(
    record_a: dict[str, Any],
    record_b: dict[str, Any],
) -> float:
    """
    Compute 0–1 match confidence between two player records from different sources.
    Fields consulted: player_name, age, current_club, position.
    """
    name_sim = _name_similarity(
        str(record_a.get("player_name") or ""),
        str(record_b.get("player_name") or ""),
    )
    if name_sim < _NAME_THRESHOLD:
        return name_sim * 0.5  # penalise hard mismatches

    score = name_sim * 0.60  # name is primary signal

    age_ok = _age_matches(record_a.get("age"), record_b.get("age"))
    score += 0.20 if age_ok else 0.0

    club_ok = _club_matches(record_a.get("current_club"), record_b.get("current_club"))
    score += 0.12 if club_ok else 0.0

    pos_ok = _position_matches(record_a.get("position"), record_b.get("position"))
    score += 0.08 if pos_ok else 0.0

    return round(min(score, 1.0), 4)


def resolve_player_slug(
    record: dict[str, Any],
    known_players: list[dict[str, Any]],
    source: str = "unknown",
) -> tuple[str | None, float]:
    """
    Find the best slug match for an incoming scrape record against known players.
    Returns (slug, confidence). Returns (None, 0.0) if no confident match found.
    """
    best_slug: str | None = None
    best_score = 0.0

    for known in known_players:
        score = compute_match_score(record, known)
        if score > best_score:
            best_score = score
            best_slug = known.get("slug") or known.get("player_slug")

    if best_score >= _CONFIDENT_THRESHOLD:
        log_event(logger, logging.DEBUG, "entity_resolution.matched",
                  name=record.get("player_name"), slug=best_slug, score=best_score, source=source)
        return best_slug, best_score

    if best_score >= _NAME_THRESHOLD:
        log_event(logger, logging.INFO, "entity_resolution.low_confidence",
                  name=record.get("player_name"), slug=best_slug, score=best_score, source=source)
        return best_slug, best_score

    log_event(logger, logging.WARNING, "entity_resolution.no_match",
              name=record.get("player_name"), best_score=best_score, source=source)
    return None, best_score


def merge_player_records(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Merge multiple source records (e.g. TM + FBref) for the same player into one.
    Later records take precedence for non-null values.
    """
    merged: dict[str, Any] = {}
    for rec in records:
        for k, v in rec.items():
            if v is not None and v != "" and v != []:
                merged[k] = v
    return merged


def deduplicate_player_list(
    players: list[dict[str, Any]],
    slug_field: str = "slug",
) -> list[dict[str, Any]]:
    """
    Collapse duplicate slug entries by merging their records.
    Used after cross-source ingestion to produce one canonical row per player.
    """
    by_slug: dict[str, list[dict[str, Any]]] = {}
    no_slug: list[dict[str, Any]] = []

    for p in players:
        slug = p.get(slug_field)
        if not slug:
            no_slug.append(p)
            continue
        by_slug.setdefault(slug, []).append(p)

    result = [merge_player_records(recs) for recs in by_slug.values()]
    result.extend(no_slug)
    return result


def build_resolution_index(
    silver_players: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build the known-players list used for resolution from Silver's players table.
    Adds a 'slug' field derived from normalized player_name if not already present.
    """
    index = []
    for p in silver_players:
        entry = dict(p)
        if not entry.get("slug"):
            name = str(p.get("player_name") or "")
            entry["slug"] = re.sub(r"\s+", "_", _normalize_name(name))
        index.append(entry)
    return index
