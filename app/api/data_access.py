from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from app.pipeline.io import read_json


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data"


class ArtifactUnavailableError(FileNotFoundError):
    """Raised when a required generated artifact is not available yet."""


ARTIFACT_PATHS = {
    "players": DATA_ROOT / "silver" / "players.json",
    "player_match_stats": DATA_ROOT / "silver" / "player_match_stats.json",
    "player_features": DATA_ROOT / "gold" / "player_features.json",
    "kpi": DATA_ROOT / "gold" / "kpi_engine.json",
    "similarity": DATA_ROOT / "gold" / "player_similarity.json",
    "valuation": DATA_ROOT / "gold" / "player_valuation.json",
}


def normalize_name(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _load_artifact(name: str, required: bool = True) -> list[dict[str, Any]]:
    path = ARTIFACT_PATHS[name]
    if not path.exists():
        if required:
            raise ArtifactUnavailableError(f"Required analysis artifact is not available: {path.name}. Run the pipeline first.")
        return []

    payload = read_json(path)
    if not isinstance(payload, list):
        return []
    return [row for row in payload if isinstance(row, dict)]


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
