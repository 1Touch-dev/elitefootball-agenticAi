from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.agents.orchestrator import build_agent_summary, supported_task_kinds
from app.api.data_access import (
    ArtifactInvalidError,
    ArtifactUnavailableError,
    index_by_player_name,
    inspect_dashboard_artifacts,
    load_kpi_rows,
    load_player_features,
    load_player_match_stats,
    load_players,
    load_similarity_rows,
    load_valuation_rows,
    normalize_name,
    paginate,
)
from app.api.schemas import CompareResponse, PlayerListResponse, PlayerStatsResponse, ValuationListResponse, ValuationRow
from app.scraping.players import get_idv_player_scrape_plan
from app.safety.types import PolicyDecision

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/summary")
def summary() -> dict[str, object]:
    return {
        "project": "elitefootball-agenticAi",
        "mvp_scope": "IDV players",
        "agents": build_agent_summary(),
        "orchestration": {"supported_task_kinds": supported_task_kinds()},
        "scraping": get_idv_player_scrape_plan(),
        "safety": {
            "decisions": [decision.value for decision in PolicyDecision],
            "approval_flow": True,
            "blocked_examples": ["delete_repo", "rm -rf .", "git clean -fdx", "curl ... | sh"],
        },
    }


@router.get("/dashboard/status")
def dashboard_status() -> dict[str, object]:
    return inspect_dashboard_artifacts()


def _artifact_unavailable(detail: str) -> HTTPException:
    return HTTPException(status_code=503, detail=detail)


def _artifact_invalid(detail: str) -> HTTPException:
    return HTTPException(status_code=500, detail=detail)


def _player_not_found(player_name: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Player not found: {player_name}")


def _load_optional_indexes() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    feature_index = index_by_player_name(load_player_features(required=False))
    kpi_index = index_by_player_name(load_kpi_rows(required=False))
    valuation_index = index_by_player_name(load_valuation_rows(required=False))
    return feature_index, kpi_index, valuation_index


@router.get("/players", response_model=PlayerListResponse)
def players(
    name: str | None = None,
    position: str | None = None,
    club: str | None = None,
    include: str = "features,kpi,valuation",
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    try:
        player_rows = load_players(required=True)
        feature_index, kpi_index, valuation_index = _load_optional_indexes()
    except ArtifactUnavailableError as exc:
        raise _artifact_unavailable(str(exc)) from exc
    except ArtifactInvalidError as exc:
        raise _artifact_invalid(str(exc)) from exc

    include_set = {item.strip().lower() for item in include.split(",") if item.strip()}
    filtered_rows = []
    name_filter = normalize_name(name)
    position_filter = normalize_name(position)
    club_filter = normalize_name(club)

    for row in player_rows:
        player_name = normalize_name(row.get("player_name"))
        row_position = normalize_name(row.get("position"))
        row_club = normalize_name(row.get("current_club"))

        if name_filter and name_filter not in player_name:
            continue
        if position_filter and position_filter != row_position:
            continue
        if club_filter and club_filter != row_club:
            continue

        item = {
            "player_name": row.get("player_name") or "unknown-player",
            "preferred_name": row.get("preferred_name"),
            "position": row.get("position"),
            "current_club": row.get("current_club"),
            "nationality": row.get("nationality"),
            "date_of_birth": row.get("date_of_birth"),
            "features": feature_index.get(player_name) if "features" in include_set else None,
            "kpi": kpi_index.get(player_name) if "kpi" in include_set else None,
            "valuation": valuation_index.get(player_name) if "valuation" in include_set else None,
        }
        filtered_rows.append(item)

    paged_rows = paginate(filtered_rows, offset=offset, limit=limit)
    return {"count": len(filtered_rows), "items": paged_rows}


@router.get("/players/{player_name}/stats", response_model=PlayerStatsResponse)
def player_stats(
    player_name: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="-match_date"),
) -> dict[str, object]:
    try:
        stat_rows = load_player_match_stats(required=True)
    except ArtifactUnavailableError as exc:
        raise _artifact_unavailable(str(exc)) from exc
    except ArtifactInvalidError as exc:
        raise _artifact_invalid(str(exc)) from exc

    normalized_target = normalize_name(player_name)
    matching_rows = [row for row in stat_rows if normalize_name(row.get("player_name")) == normalized_target]
    if not matching_rows:
        raise _player_not_found(player_name)

    reverse = sort.startswith("-")
    sort_key = sort[1:] if reverse else sort
    sorted_rows = sorted(matching_rows, key=lambda row: (row.get(sort_key) or ""), reverse=reverse)
    paged_rows = paginate(sorted_rows, offset=offset, limit=limit)

    return {
        "player_name": matching_rows[0].get("player_name") or player_name,
        "count": len(matching_rows),
        "items": [
            {
                "match_date": row.get("match_date"),
                "club_name": row.get("club_name"),
                "minutes": row.get("minutes"),
                "goals": row.get("goals", 0),
                "assists": row.get("assists", 0),
                "shots": row.get("shots", 0),
                "passes_completed": row.get("passes_completed", 0),
                "yellow_cards": row.get("yellow_cards", 0),
                "red_cards": row.get("red_cards", 0),
                "source": row.get("source"),
            }
            for row in paged_rows
        ],
    }


@router.get("/compare", response_model=CompareResponse)
def compare(
    player_name: str = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=20),
) -> dict[str, object]:
    try:
        similarity_rows = load_similarity_rows(required=True)
    except ArtifactUnavailableError as exc:
        raise _artifact_unavailable(str(exc)) from exc
    except ArtifactInvalidError as exc:
        raise _artifact_invalid(str(exc)) from exc

    target_key = normalize_name(player_name)
    for row in similarity_rows:
        if normalize_name(row.get("player_name")) != target_key:
            continue
        similar_players = list(row.get("similar_players") or [])[:limit]
        return {
            "player_name": row.get("player_name") or player_name,
            "position": row.get("position"),
            "comparison_features": row.get("comparison_features") or {},
            "similar_players": similar_players,
        }

    raise _player_not_found(player_name)


@router.get("/value", response_model=ValuationRow | ValuationListResponse)
def value(
    player_name: str | None = None,
    tier: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    try:
        valuation_rows = load_valuation_rows(required=True)
    except ArtifactUnavailableError as exc:
        raise _artifact_unavailable(str(exc)) from exc
    except ArtifactInvalidError as exc:
        raise _artifact_invalid(str(exc)) from exc

    if player_name:
        target_key = normalize_name(player_name)
        for row in valuation_rows:
            if normalize_name(row.get("player_name")) == target_key:
                return row
        raise _player_not_found(player_name)

    filtered_rows = valuation_rows
    if tier:
        filtered_rows = [row for row in valuation_rows if str(row.get("valuation_tier") or "").strip().lower() == tier.strip().lower()]

    paged_rows = paginate(filtered_rows, offset=offset, limit=limit)
    return {"count": len(filtered_rows), "items": paged_rows}
