from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.agents.orchestrator import build_agent_summary, supported_task_kinds
from app.api.data_access import (
    ArtifactInvalidError,
    ArtifactUnavailableError,
    index_by_player_name,
    inspect_dashboard_artifacts,
    load_advanced_metric_rows,
    load_club_benchmark_rows,
    load_kpi_rows,
    load_pathway_rows,
    load_player_features,
    load_player_match_stats,
    load_players,
    load_risk_rows,
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


@router.get("/pathway/{player_name}")
def pathway(player_name: str) -> dict[str, object]:
    try:
        rows = load_pathway_rows(required=False)
    except (ArtifactUnavailableError, ArtifactInvalidError):
        rows = []
    target_key = normalize_name(player_name)
    for row in rows:
        if normalize_name(row.get("player_name")) == target_key:
            return row
    raise _player_not_found(player_name)


@router.get("/pathway")
def pathway_list(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    try:
        rows = load_pathway_rows(required=False)
    except (ArtifactUnavailableError, ArtifactInvalidError):
        rows = []
    paged = paginate(rows, offset=offset, limit=limit)
    return {"count": len(rows), "items": paged}


@router.get("/undervalued")
def undervalued_players(
    min_gap_pct: float = Query(default=25.0, ge=0.0, le=500.0),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    """
    Returns players where the computed valuation exceeds market value by min_gap_pct%.
    Also includes players with no market value data who have high valuation scores (≥60).
    """
    try:
        valuation_rows = load_valuation_rows(required=True)
    except ArtifactUnavailableError as exc:
        raise _artifact_unavailable(str(exc)) from exc
    except ArtifactInvalidError as exc:
        raise _artifact_invalid(str(exc)) from exc

    results = []
    for row in valuation_rows:
        market_val = row.get("market_value_eur")
        computed_val = row.get("computed_value_eur")
        val_score = float(row.get("valuation_score") or 0)

        if market_val and computed_val and market_val > 0:
            gap_pct = ((computed_val - market_val) / market_val) * 100.0
            if gap_pct >= min_gap_pct:
                results.append({**row, "value_gap_pct": round(gap_pct, 1), "gap_type": "market_vs_computed"})
        elif not market_val and val_score >= 60:
            # No market value data — flag high-scorers as potentially undervalued
            results.append({**row, "value_gap_pct": None, "gap_type": "no_market_data_high_score"})

    results.sort(key=lambda r: (r.get("value_gap_pct") or r.get("valuation_score") or 0), reverse=True)
    paged = paginate(results, offset=offset, limit=limit)
    return {"count": len(results), "items": paged}


@router.get("/benchmark")
def club_benchmark() -> dict[str, object]:
    try:
        rows = load_club_benchmark_rows(required=False)
    except (ArtifactUnavailableError, ArtifactInvalidError):
        rows = []
    return {"count": len(rows), "items": rows}


@router.get("/advanced-metrics")
def advanced_metrics(
    player_name: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    try:
        rows = load_advanced_metric_rows(required=False)
    except (ArtifactUnavailableError, ArtifactInvalidError):
        rows = []
    if player_name:
        target_key = normalize_name(player_name)
        rows = [r for r in rows if normalize_name(r.get("player_name")) == target_key]
    paged = paginate(rows, offset=offset, limit=limit)
    return {"count": len(rows), "items": paged}


@router.post("/admin/pipeline/run")
def admin_run_pipeline() -> dict[str, object]:
    """Trigger a full pipeline run."""
    try:
        from app.pipeline.run_pipeline import run_pipeline
        result = run_pipeline()
        return {
            "status": "ok",
            "stages": {k: (len(v.get("rows", [])) if isinstance(v, dict) else "done") for k, v in result.items()},
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@router.get("/transfer-probability")
def transfer_probability(
    player_name: str | None = Query(None),
    min_prob: float = Query(0.0),
    limit: int = Query(20),
    offset: int = Query(0),
) -> dict[str, object]:
    """Transfer probability — 1-year and 2-year estimates per player."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/transfer_probability.json")
    if not path.exists():
        raise _artifact_unavailable("transfer_probability.json not found — run pipeline first")
    rows = read_json(path) or []
    if not isinstance(rows, list):
        raise _artifact_invalid("transfer_probability.json has unexpected format")
    if player_name:
        key = player_name.strip().lower()
        rows = [r for r in rows if key in str(r.get("player_name") or "").lower()]
    if min_prob > 0:
        rows = [r for r in rows if float(r.get("transfer_probability_1y") or 0) >= min_prob]
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.get("/club-fit/{player_name}")
def club_fit_for_player(player_name: str) -> dict[str, object]:
    """Top 5 club fit recommendations for a specific player."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/club_fit.json")
    if not path.exists():
        raise _artifact_unavailable("club_fit.json not found — run pipeline first")
    rows = read_json(path) or []
    key = player_name.strip().lower()
    match = next((r for r in rows if key in str(r.get("player_name") or "").lower()), None)
    if not match:
        raise _player_not_found(player_name)
    return match


@router.get("/club-fit")
def club_fit_list(limit: int = Query(20), offset: int = Query(0)) -> dict[str, object]:
    """Club fit rankings for all players."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/club_fit.json")
    if not path.exists():
        raise _artifact_unavailable("club_fit.json not found — run pipeline first")
    rows = read_json(path) or []
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.get("/market-value")
def market_value(
    player_name: str | None = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
) -> dict[str, object]:
    """€ market value predictions with confidence scores."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/market_value.json")
    if not path.exists():
        raise _artifact_unavailable("market_value.json not found — run pipeline first")
    rows = read_json(path) or []
    if player_name:
        key = player_name.strip().lower()
        rows = [r for r in rows if key in str(r.get("player_name") or "").lower()]
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.get("/clusters")
def player_clusters() -> dict[str, object]:
    """Player performance clusters (k-means by style profile)."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/player_clusters.json")
    if not path.exists():
        raise _artifact_unavailable("player_clusters.json not found — run pipeline first")
    data = read_json(path)
    if isinstance(data, list):
        return {"players": data, "centroids": []}
    return data or {}


@router.get("/alerts")
def player_alerts(
    alert_type: str | None = Query(None, description="UNDERVALUED | BREAKOUT | DECLINE"),
    severity: str | None = Query(None, description="critical | high | medium | low"),
    limit: int = Query(50),
    offset: int = Query(0),
) -> dict[str, object]:
    """Active player alerts: undervalued, breakout, and decline signals."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/alerts.json")
    if not path.exists():
        raise _artifact_unavailable("alerts.json not found — run pipeline first")
    data = read_json(path) or {}
    alerts = data.get("alerts", []) if isinstance(data, dict) else data
    if alert_type:
        alerts = [a for a in alerts if a.get("alert_type") == alert_type.upper()]
    if severity:
        alerts = [a for a in alerts if a.get("severity") == severity.lower()]
    summary = data.get("summary", {}) if isinstance(data, dict) else {}
    return {
        "summary": summary,
        "count": len(alerts),
        "items": paginate(alerts, offset=offset, limit=limit),
    }


@router.get("/feature-store")
def feature_store(
    player_name: str | None = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
) -> dict[str, object]:
    """Consolidated feature store — all player features in one normalized record."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/feature_store.json")
    if not path.exists():
        raise _artifact_unavailable("feature_store.json not found — run pipeline first")
    rows = read_json(path) or []
    if player_name:
        key = player_name.strip().lower()
        rows = [r for r in rows if key in str(r.get("player_name") or "").lower()]
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.post("/admin/discover")
def admin_discover(league_keys: list[str] | None = None) -> dict[str, object]:
    """Trigger player discovery crawl across league pages."""
    try:
        from app.scraping.discovery_engine import run_discovery_cycle
        result = run_discovery_cycle(league_keys=league_keys)
        return {"status": "ok", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@router.get("/decision")
def decisions(
    player_name: str | None = Query(None),
    decision_type: str | None = Query(None, description="BUY | SELL | HOLD"),
    min_confidence: float = Query(0.0),
    limit: int = Query(20),
    offset: int = Query(0),
) -> dict[str, object]:
    """BUY/SELL/HOLD decisions for all players with full reasoning breakdown."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/player_decisions.json")
    if not path.exists():
        raise _artifact_unavailable("player_decisions.json not found — run pipeline first")
    rows = read_json(path) or []
    if player_name:
        key = player_name.strip().lower()
        rows = [r for r in rows if key in str(r.get("player_name") or "").lower()]
    if decision_type:
        rows = [r for r in rows if r.get("decision") == decision_type.upper()]
    if min_confidence > 0:
        rows = [r for r in rows if float(r.get("decision_confidence") or 0) >= min_confidence]
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.get("/decision/{player_name}")
def decision_for_player(player_name: str) -> dict[str, object]:
    """Full BUY/SELL/HOLD decision with reasoning for a specific player."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/player_decisions.json")
    if not path.exists():
        raise _artifact_unavailable("player_decisions.json not found — run pipeline first")
    rows = read_json(path) or []
    key = player_name.strip().lower()
    match = next((r for r in rows if key in str(r.get("player_name") or "").lower()), None)
    if not match:
        raise _player_not_found(player_name)
    return match


@router.get("/simulation/{player_name}")
def simulation_for_player(player_name: str) -> dict[str, object]:
    """Projected performance simulation for a player in different leagues."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/player_simulations.json")
    if not path.exists():
        raise _artifact_unavailable("player_simulations.json not found — run pipeline first")
    rows = read_json(path) or []
    key = player_name.strip().lower()
    match = next((r for r in rows if key in str(r.get("player_name") or "").lower()), None)
    if not match:
        raise _player_not_found(player_name)
    return match


@router.get("/simulation")
def simulations(
    player_name: str | None = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
) -> dict[str, object]:
    """League simulation projections for all players."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/player_simulations.json")
    if not path.exists():
        raise _artifact_unavailable("player_simulations.json not found — run pipeline first")
    rows = read_json(path) or []
    if player_name:
        key = player_name.strip().lower()
        rows = [r for r in rows if key in str(r.get("player_name") or "").lower()]
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.get("/scout-report/{player_name}")
def scout_report(player_name: str) -> dict[str, object]:
    """Full scout report (LLM or template) for a specific player."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/scout_reports.json")
    if not path.exists():
        raise _artifact_unavailable("scout_reports.json not found — run pipeline first")
    rows = read_json(path) or []
    key = player_name.strip().lower()
    match = next((r for r in rows if key in str(r.get("player_name") or "").lower()), None)
    if not match:
        # Generate on-demand if not in cache
        try:
            from app.reporting.scout_report import generate_scout_report
            return generate_scout_report(player_name=player_name)
        except Exception as exc:
            raise _artifact_unavailable(f"Scout report unavailable: {exc}") from exc
    return match


@router.get("/scout-report")
def scout_reports_list(
    decision: str | None = Query(None, description="BUY | SELL | HOLD"),
    limit: int = Query(20),
    offset: int = Query(0),
) -> dict[str, object]:
    """List all scout reports."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/scout_reports.json")
    if not path.exists():
        raise _artifact_unavailable("scout_reports.json not found — run pipeline first")
    rows = read_json(path) or []
    if decision:
        rows = [r for r in rows if r.get("decision") == decision.upper()]
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.get("/player-graph")
def player_graph() -> dict[str, object]:
    """Transfer network graph with PageRank — springboard clubs and career routes."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/player_graph.json")
    if not path.exists():
        raise _artifact_unavailable("player_graph.json not found — run pipeline first")
    return read_json(path) or {}


@router.get("/pathway-learning")
def pathway_learning(
    player_name: str | None = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
) -> dict[str, object]:
    """GBM-based pathway success probabilities per player."""
    from pathlib import Path
    from app.pipeline.io import read_json
    path = Path("data/gold/pathway_learning.json")
    if not path.exists():
        raise _artifact_unavailable("pathway_learning.json not found — run pipeline first")
    rows = read_json(path) or []
    if player_name:
        key = player_name.strip().lower()
        rows = [r for r in rows if key in str(r.get("player_name") or "").lower()]
    return {"count": len(rows), "items": paginate(rows, offset=offset, limit=limit)}


@router.get("/admin/status")
def admin_status() -> dict[str, object]:
    """Admin overview: artifact readiness."""
    from pathlib import Path
    artifact_map = {
        "players": Path("data/silver/players.json"),
        "player_match_stats": Path("data/silver/player_match_stats.json"),
        "player_features": Path("data/gold/player_features.json"),
        "kpi": Path("data/gold/kpi_engine.json"),
        "valuation": Path("data/gold/player_valuation.json"),
        "pathway": Path("data/gold/player_pathway.json"),
        "advanced_metrics": Path("data/gold/advanced_metrics.json"),
        "club_benchmark": Path("data/gold/club_development_rankings.json"),
        "risk": Path("data/gold/player_risk.json"),
        "similarity": Path("data/gold/player_similarity.json"),
        "transfer_probability": Path("data/gold/transfer_probability.json"),
        "club_fit": Path("data/gold/club_fit.json"),
        "market_value": Path("data/gold/market_value.json"),
        "clusters": Path("data/gold/player_clusters.json"),
        "alerts": Path("data/gold/alerts.json"),
        "feature_store": Path("data/gold/feature_store.json"),
        "pathway_learning": Path("data/gold/pathway_learning.json"),
        "player_decisions": Path("data/gold/player_decisions.json"),
        "player_simulations": Path("data/gold/player_simulations.json"),
        "player_graph": Path("data/gold/player_graph.json"),
        "scout_reports": Path("data/gold/scout_reports.json"),
    }
    from app.scraping.job_queue import PersistentJobQueue
    from app.orchestration.scheduler import get_scheduler_status
    queue = PersistentJobQueue()
    return {
        "dashboard": inspect_dashboard_artifacts(),
        "artifacts": {
            name: {"exists": path.exists(), "path": str(path)}
            for name, path in artifact_map.items()
        },
        "job_queue": queue.stats(),
        "scheduler": get_scheduler_status(),
    }
