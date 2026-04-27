from __future__ import annotations

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


def inspect_dashboard_artifacts(sample_limit: int = 3) -> dict[str, Any]:
    artifacts = {
        name: inspect_artifact(name, required=(name in {"players", "player_match_stats", "similarity", "valuation"}), sample_limit=sample_limit)
        for name in ARTIFACT_PATHS
    }
    states = {artifact["state"] for artifact in artifacts.values()}
    if any(state == "invalid" for state in states):
        status = "artifact_invalid"
    elif any(state == "missing" for state in states):
        status = "artifact_missing"
    elif all(artifact["row_count"] == 0 for artifact in artifacts.values()):
        status = "empty"
    elif any(state == "empty" for state in states):
        status = "partial"
    else:
        status = "ready"

    return {
        "status": status,
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
