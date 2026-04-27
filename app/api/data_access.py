from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from app.pipeline.io import read_json


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data"


class ArtifactUnavailableError(FileNotFoundError):
    """Raised when a required generated artifact is not available yet."""


class ArtifactInvalidError(ValueError):
    """Raised when an artifact exists but does not match the expected payload contract."""


ARTIFACT_PATHS = {
    "players": DATA_ROOT / "silver" / "players.json",
    "player_match_stats": DATA_ROOT / "silver" / "player_match_stats.json",
    "player_features": DATA_ROOT / "gold" / "player_features.json",
    "kpi": DATA_ROOT / "gold" / "kpi_engine.json",
    "similarity": DATA_ROOT / "gold" / "player_similarity.json",
    "valuation": DATA_ROOT / "gold" / "player_valuation.json",
}
REQUIRED_DASHBOARD_ARTIFACTS = {"players", "player_match_stats", "similarity", "valuation"}


def normalize_name(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def inspect_artifact(name: str, *, required: bool = True, sample_limit: int = 3) -> dict[str, Any]:
    path = ARTIFACT_PATHS[name]
    result: dict[str, Any] = {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
        "required": required,
        "valid": False,
        "state": "missing",
        "row_count": 0,
        "rows": [],
        "sample_rows": [],
        "error": None,
    }

    if not path.exists():
        if required:
            result["error"] = f"Required analysis artifact is not available: {path.name}. Run the pipeline first."
        else:
            result["state"] = "missing_optional"
        return result

    try:
        payload = read_json(path)
    except Exception as exc:
        result["state"] = "invalid"
        result["error"] = f"Artifact could not be read: {path.name} ({type(exc).__name__}: {exc})"
        return result

    if not isinstance(payload, list):
        result["state"] = "invalid"
        result["error"] = f"Artifact payload must be a list of rows: {path.name}."
        return result

    rows = [row for row in payload if isinstance(row, dict)]
    if len(rows) != len(payload):
        result["state"] = "invalid"
        result["error"] = f"Artifact contains non-object rows: {path.name}."
        result["row_count"] = len(rows)
        result["rows"] = rows
        result["sample_rows"] = rows[: max(sample_limit, 0)]
        return result

    result["valid"] = True
    result["rows"] = rows
    result["row_count"] = len(rows)
    result["sample_rows"] = rows[: max(sample_limit, 0)]
    result["state"] = "ready" if rows else "empty"
    return result


def _isoformat_utc(timestamp: float | None) -> str | None:
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")


def _artifact_mtime(path: str | Path) -> float | None:
    artifact_path = Path(path)
    if not artifact_path.exists():
        return None
    return artifact_path.stat().st_mtime


def _recommended_action_for_status(status: str) -> str:
    if status == "ready":
        return "Refresh the dashboard if you expect newer data."
    if status == "partial":
        return "Some data is available, but parts of the scrape or pipeline output are still empty. Re-run the pipeline and refresh."
    if status == "empty":
        return "No dashboard-ready records exist yet. Run the scrape + pipeline workflow, then refresh the dashboard."
    if status == "artifact_missing":
        return "Required dashboard artifacts are missing. Run the pipeline first and confirm Silver/Gold outputs were written."
    if status == "artifact_invalid":
        return "Dashboard artifacts exist but are invalid. Check pipeline outputs and backend logs before retrying."
    return "Refresh the dashboard after checking backend health and pipeline outputs."


def inspect_dashboard_artifacts(sample_limit: int = 3) -> dict[str, Any]:
    artifacts = {
        name: inspect_artifact(name, required=(name in REQUIRED_DASHBOARD_ARTIFACTS), sample_limit=sample_limit)
        for name in ARTIFACT_PATHS
    }
    states = {artifact["state"] for artifact in artifacts.values()}
    required_artifacts = {name: artifact for name, artifact in artifacts.items() if artifact["required"]}

    if any(artifact["state"] == "invalid" for artifact in required_artifacts.values()):
        status = "artifact_invalid"
        upstream_status = "pipeline_output_invalid"
    elif any(artifact["state"] == "missing" for artifact in required_artifacts.values()):
        status = "artifact_missing"
        upstream_status = "pipeline_output_missing"
    elif all(artifact["row_count"] == 0 for artifact in artifacts.values()):
        status = "empty"
        upstream_status = "no_dashboard_data"
    elif any(artifact["state"] == "empty" for artifact in required_artifacts.values()):
        status = "partial"
        upstream_status = "partially_available"
    else:
        status = "ready"
        upstream_status = "healthy"

    existing_valid_artifacts = [artifact for artifact in artifacts.values() if artifact["exists"] and artifact["valid"]]
    success_timestamps = [_artifact_mtime(artifact["path"]) for artifact in existing_valid_artifacts]
    success_timestamps = [timestamp for timestamp in success_timestamps if timestamp is not None]
    last_successful_sync_at = _isoformat_utc(max(success_timestamps)) if success_timestamps else None

    failure_candidates = [artifact for artifact in required_artifacts.values() if artifact["state"] in {"missing", "invalid"}]
    last_failure_stage = None
    last_failure_message = None
    last_failed_sync_at = None
    if failure_candidates:
        failure_artifact = failure_candidates[0]
        last_failure_stage = failure_artifact["name"]
        last_failure_message = failure_artifact["error"]
        last_failed_sync_at = _isoformat_utc(_artifact_mtime(failure_artifact["path"]))

    return {
        "status": status,
        "diagnostics": {
            "upstream_status": upstream_status,
            "recommended_action": _recommended_action_for_status(status),
        },
        "sync": {
            "last_successful_sync_at": last_successful_sync_at,
            "last_failed_sync_at": last_failed_sync_at,
            "last_failure_stage": last_failure_stage,
            "last_failure_message": last_failure_message,
            "recommended_action": _recommended_action_for_status(status),
        },
        "artifacts": {
            name: {
                "path": artifact["path"],
                "exists": artifact["exists"],
                "required": artifact["required"],
                "valid": artifact["valid"],
                "state": artifact["state"],
                "row_count": artifact["row_count"],
                "error": artifact["error"],
            }
            for name, artifact in artifacts.items()
        },
        "samples": {name: artifact["sample_rows"] for name, artifact in artifacts.items()},
    }


def _load_artifact(name: str, required: bool = True) -> list[dict[str, Any]]:
    artifact = inspect_artifact(name, required=required)
    if artifact["state"] == "missing" and required:
        raise ArtifactUnavailableError(str(artifact["error"]))
    if artifact["state"] == "invalid":
        raise ArtifactInvalidError(str(artifact["error"]))
    return list(artifact["rows"])


def load_players(required: bool = True) -> list[dict[str, Any]]:
    return _load_artifact("players", required=required)


def load_player_match_stats(required: bool = True) -> list[dict[str, Any]]:
    return _load_artifact("player_match_stats", required=required)


def load_player_features(required: bool = False) -> list[dict[str, Any]]:
    return _load_artifact("player_features", required=required)


def load_kpi_rows(required: bool = False) -> list[dict[str, Any]]:
    return _load_artifact("kpi", required=required)


def load_similarity_rows(required: bool = True) -> list[dict[str, Any]]:
    return _load_artifact("similarity", required=required)


def load_valuation_rows(required: bool = True) -> list[dict[str, Any]]:
    return _load_artifact("valuation", required=required)


def index_by_player_name(rows: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = normalize_name(row.get("player_name"))
        if key:
            indexed[key] = row
    return indexed


def paginate(rows: list[dict[str, Any]], offset: int = 0, limit: int = 20) -> list[dict[str, Any]]:
    start = max(offset, 0)
    end = start + max(limit, 0)
    return rows[start:end]
