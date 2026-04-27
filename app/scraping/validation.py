from __future__ import annotations

from typing import Any


TRANSFERMARKT_PROFILE_REQUIRED = ("player_name", "position")
TRANSFERMARKT_PROFILE_OPTIONAL = ("current_club", "nationality", "market_value")
FBREF_MATCH_REQUIRED = ("home_club", "away_club")
FBREF_PLAYER_STAT_FIELDS = (
    "minutes",
    "goals",
    "assists",
    "shots",
    "passes_completed",
    "xg",
    "xa",
    "progressive_carries",
    "progressive_passes",
    "progressive_receptions",
)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def _missing_fields(payload: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if not _present(payload.get(field))]


def _row_has_values(row: dict[str, Any], fields: tuple[str, ...]) -> bool:
    return any(_present(row.get(field)) for field in fields)


def validate_transfermarkt_payload(profile: dict[str, Any], transfers: list[dict[str, Any]]) -> dict[str, Any]:
    missing_required_fields = _missing_fields(profile, TRANSFERMARKT_PROFILE_REQUIRED)
    optional_hits = sum(1 for field in TRANSFERMARKT_PROFILE_OPTIONAL if _present(profile.get(field)))
    valid_transfer_rows = [
        row for row in transfers
        if _present(row.get("season")) and (_present(row.get("from_club")) or _present(row.get("to_club")))
    ]
    if not missing_required_fields and optional_hits > 0:
        status = "success_complete"
    elif not missing_required_fields:
        status = "success_partial"
    else:
        status = "schema_invalid"

    return {
        "source": "transfermarkt",
        "extraction_status": status,
        "missing_required_fields": missing_required_fields,
        "record_counts": {
            "profile_fields_present": sum(1 for key, value in profile.items() if key not in {"source", "source_url", "scraped_at"} and _present(value)),
            "transfer_rows": len(valid_transfer_rows),
            "transfer_rows_seen": len(transfers),
        },
        "sample_records": {
            "profile": profile,
            "transfer": valid_transfer_rows[0] if valid_transfer_rows else None,
        },
    }


def validate_fbref_payload(
    match_payload: dict[str, Any],
    player_match_stats: list[dict[str, Any]],
    player_per_90: list[dict[str, Any]],
    *,
    challenge_detected: bool = False,
) -> dict[str, Any]:
    missing_required_fields = _missing_fields(match_payload, FBREF_MATCH_REQUIRED)
    has_match_identity = _present(match_payload.get("external_id")) or _present(match_payload.get("title"))
    valid_player_rows = [
        row for row in player_match_stats
        if _present(row.get("player_name")) and _row_has_values(row, FBREF_PLAYER_STAT_FIELDS)
    ]
    valid_per90_rows = [
        row for row in player_per_90
        if _present(row.get("player_name")) and _present(row.get("metrics"))
    ]

    if challenge_detected:
        status = "challenge_page"
    elif has_match_identity and not missing_required_fields and (valid_player_rows or valid_per90_rows):
        status = "success_complete"
    elif has_match_identity and (valid_player_rows or valid_per90_rows):
        status = "success_partial"
    elif has_match_identity:
        status = "selector_missing"
    else:
        status = "schema_invalid"

    return {
        "source": "fbref",
        "extraction_status": status,
        "missing_required_fields": ([] if has_match_identity else ["external_id_or_title"]) + missing_required_fields,
        "record_counts": {
            "player_match_stats": len(valid_player_rows),
            "player_match_stats_seen": len(player_match_stats),
            "player_per_90": len(valid_per90_rows),
            "player_per_90_seen": len(player_per_90),
        },
        "sample_records": {
            "match": match_payload,
            "player_match_stat": valid_player_rows[0] if valid_player_rows else None,
            "player_per_90": valid_per90_rows[0] if valid_per90_rows else None,
        },
    }
