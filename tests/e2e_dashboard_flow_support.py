from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from typing import Any, Iterator
from unittest.mock import patch
from urllib.parse import urlparse

from app.config import settings
from app.pipeline.io import read_json, write_json
from app.pipeline.run_pipeline import run_pipeline
from dashboard.api_client import DashboardAPIClient

FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None
if FASTAPI_AVAILABLE:
    from fastapi.testclient import TestClient
    from app.main import app


@dataclass
class ValidationStage:
    name: str
    passed: bool
    details: str


@dataclass
class ValidationResult:
    stages: list[ValidationStage]
    counts: dict[str, int]
    limitations: list[str]

    @property
    def ok(self) -> bool:
        return all(stage.passed for stage in self.stages)


def _sample_transfermarkt_profile(player_name: str, preferred_name: str, position: str, dob: str, nationality: str, current_club: str, market_value: str, source_url: str) -> dict[str, Any]:
    return {
        "profile": {
            "source_url": source_url,
            "player_name": player_name,
            "preferred_name": preferred_name,
            "position": position,
            "date_of_birth": dob,
            "nationality": nationality,
            "current_club": current_club,
            "market_value": market_value,
        },
        "transfers": [
            {
                "source_url": source_url,
                "season": "2025/2026",
                "date": "2025-01-10",
                "from_club": current_club,
                "to_club": current_club,
                "market_value": market_value,
                "fee": "-",
            }
        ],
    }


def _sample_fbref_match(match_id: str, match_date: str) -> dict[str, Any]:
    return {
        "match": {
            "source_url": f"https://fbref.com/en/matches/{match_id}",
            "external_id": match_id,
            "competition": "Copa Libertadores",
            "season": "2025-2026",
            "match_date": match_date,
            "home_club": "Independiente del Valle",
            "away_club": "Club Example",
            "home_score": 2,
            "away_score": 1,
            "venue": "Estadio Banco Guayaquil",
        },
        "player_match_stats": [
            {
                "source_url": f"https://fbref.com/en/matches/{match_id}",
                "table_id": "stats_standard",
                "player_name": "John Doe",
                "club_name": "Independiente del Valle",
                "minutes": 90,
                "goals": 1,
                "assists": 1,
                "yellow_cards": 0,
                "red_cards": 0,
                "shots": 4,
                "passes_completed": 28,
                "xg": 0.6,
                "xa": 0.3,
                "progressive_carries": 3,
                "progressive_passes": 4,
                "progressive_receptions": 2,
                "carries_into_final_third": 2,
                "passes_into_final_third": 3,
                "carries_into_penalty_area": 1,
                "passes_into_penalty_area": 2,
            },
            {
                "source_url": f"https://fbref.com/en/matches/{match_id}",
                "table_id": "stats_standard",
                "player_name": "Jane Roe",
                "club_name": "Club Example",
                "minutes": 90,
                "goals": 0,
                "assists": 0,
                "yellow_cards": 1,
                "red_cards": 0,
                "shots": 2,
                "passes_completed": 35,
                "xg": 0.2,
                "xa": 0.1,
                "progressive_carries": 2,
                "progressive_passes": 5,
                "progressive_receptions": 3,
                "carries_into_final_third": 1,
                "passes_into_final_third": 4,
                "carries_into_penalty_area": 0,
                "passes_into_penalty_area": 1,
            },
        ],
        "player_per_90": [
            {
                "source_url": f"https://fbref.com/en/matches/{match_id}",
                "table_id": "stats_per90",
                "player_name": "John Doe",
                "club_name": "Independiente del Valle",
                "metrics": {"goals": 1.0, "assists": 1.0},
            },
            {
                "source_url": f"https://fbref.com/en/matches/{match_id}",
                "table_id": "stats_per90",
                "player_name": "Jane Roe",
                "club_name": "Club Example",
                "metrics": {"goals": 0.0, "assists": 0.0},
            },
        ],
    }


def _seed_fixture_data(base_dir: Path) -> dict[str, int]:
    raw_transfermarkt_dir = base_dir / "data" / "raw" / "transfermarkt"
    parsed_transfermarkt_dir = base_dir / "data" / "parsed" / "transfermarkt"
    raw_fbref_dir = base_dir / "data" / "raw" / "fbref"
    parsed_fbref_dir = base_dir / "data" / "parsed" / "fbref"

    raw_transfermarkt_dir.mkdir(parents=True, exist_ok=True)
    parsed_transfermarkt_dir.mkdir(parents=True, exist_ok=True)
    raw_fbref_dir.mkdir(parents=True, exist_ok=True)
    parsed_fbref_dir.mkdir(parents=True, exist_ok=True)

    (raw_transfermarkt_dir / "john-doe.html").write_text("<html><body>John Doe sample profile</body></html>", encoding="utf-8")
    (raw_transfermarkt_dir / "jane-roe.html").write_text("<html><body>Jane Roe sample profile</body></html>", encoding="utf-8")
    (raw_fbref_dir / "match-001.html").write_text("<html><body>FBref sample match 001</body></html>", encoding="utf-8")
    (raw_fbref_dir / "match-002.html").write_text("<html><body>FBref sample match 002</body></html>", encoding="utf-8")

    write_json(
        parsed_transfermarkt_dir / "john-doe.json",
        _sample_transfermarkt_profile(
            "John Doe",
            "John",
            "Forward",
            "2003-01-01",
            "Ecuador",
            "Independiente del Valle",
            "€1.2m",
            "https://www.transfermarkt.com/john-doe/profil/spieler/1001",
        ),
    )
    write_json(
        parsed_transfermarkt_dir / "jane-roe.json",
        _sample_transfermarkt_profile(
            "Jane Roe",
            "Jane",
            "Midfielder",
            "1999-02-02",
            "Ecuador",
            "Club Example",
            "€900k",
            "https://www.transfermarkt.com/jane-roe/profil/spieler/1002",
        ),
    )
    write_json(parsed_fbref_dir / "match-001.json", _sample_fbref_match("match-001", "2026-01-10"))
    write_json(parsed_fbref_dir / "match-002.json", _sample_fbref_match("match-002", "2026-01-20"))

    return {
        "transfermarkt_parsed_payloads": 2,
        "fbref_parsed_payloads": 2,
        "raw_html_files": 4,
    }


@contextmanager
def _temporary_settings() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        originals = {
            "repo_root": settings.repo_root,
            "raw_data_dir": settings.raw_data_dir,
            "parsed_data_dir": settings.parsed_data_dir,
            "fbref_raw_data_dir": settings.fbref_raw_data_dir,
            "fbref_parsed_data_dir": settings.fbref_parsed_data_dir,
            "bronze_data_dir": settings.bronze_data_dir,
            "silver_data_dir": settings.silver_data_dir,
            "gold_data_dir": settings.gold_data_dir,
        }
        try:
            object.__setattr__(settings, "repo_root", str(base_dir))
            object.__setattr__(settings, "raw_data_dir", str(base_dir / "data" / "raw" / "transfermarkt"))
            object.__setattr__(settings, "parsed_data_dir", str(base_dir / "data" / "parsed" / "transfermarkt"))
            object.__setattr__(settings, "fbref_raw_data_dir", str(base_dir / "data" / "raw" / "fbref"))
            object.__setattr__(settings, "fbref_parsed_data_dir", str(base_dir / "data" / "parsed" / "fbref"))
            object.__setattr__(settings, "bronze_data_dir", str(base_dir / "data" / "bronze"))
            object.__setattr__(settings, "silver_data_dir", str(base_dir / "data" / "silver"))
            object.__setattr__(settings, "gold_data_dir", str(base_dir / "data" / "gold"))
            yield base_dir
        finally:
            for key, value in originals.items():
                object.__setattr__(settings, key, value)


class _TestClientResponseAdapter:
    def __init__(self, response: Any) -> None:
        self._response = response
        self.status_code = response.status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"{self.status_code} error")

    def json(self) -> Any:
        return self._response.json()


@contextmanager
def _patched_dashboard_requests(test_client: Any) -> Iterator[None]:
    def fake_get(url: str, params: dict[str, Any] | None = None, timeout: int | float | None = None):
        parsed = urlparse(url)
        path = parsed.path or "/"
        response = test_client.get(path, params=params)
        return _TestClientResponseAdapter(response)

    with patch("dashboard.api_client.requests.get", side_effect=fake_get):
        yield


def _patch_artifact_paths(base_dir: Path):
    from app.api import data_access

    return patch.dict(
        data_access.ARTIFACT_PATHS,
        {
            "players": base_dir / "data" / "silver" / "players.json",
            "player_match_stats": base_dir / "data" / "silver" / "player_match_stats.json",
            "player_features": base_dir / "data" / "gold" / "player_features.json",
            "kpi": base_dir / "data" / "gold" / "kpi_engine.json",
            "similarity": base_dir / "data" / "gold" / "player_similarity.json",
            "valuation": base_dir / "data" / "gold" / "player_valuation.json",
        },
        clear=True,
    )


def run_e2e_dashboard_flow() -> ValidationResult:
    stages: list[ValidationStage] = []
    counts: dict[str, int] = {}
    limitations = [
        "This validation uses seeded sample parsed inputs rather than a mandatory live external scrape.",
        "Live scrape verification remains best-effort because source accessibility and scraping dependencies are environment-sensitive.",
        "Dashboard verification stops at API-client payload receipt rather than full browser UI automation.",
    ]

    with _temporary_settings() as base_dir:
        seeded_counts = _seed_fixture_data(base_dir)
        stages.append(
            ValidationStage(
                name="seeded_inputs",
                passed=True,
                details=(
                    f"Seeded {seeded_counts['transfermarkt_parsed_payloads']} Transfermarkt parsed payloads, "
                    f"{seeded_counts['fbref_parsed_payloads']} FBref parsed payloads, and {seeded_counts['raw_html_files']} raw HTML samples."
                ),
            )
        )

        pipeline_result = run_pipeline()
        bronze_manifest = pipeline_result["bronze"]["manifest"]
        silver_tables = pipeline_result["silver"]["tables"]
        gold_tables = pipeline_result["gold"]["tables"]
        kpi_rows = pipeline_result["kpi"]["rows"]
        similarity_rows = pipeline_result["similarity"]["rows"]
        valuation_rows = pipeline_result["valuation"]["rows"]

        counts.update(
            {
                "bronze_artifacts": int(bronze_manifest.get("artifact_count", 0)),
                "silver_players": len(silver_tables.get("players", [])),
                "silver_player_match_stats": len(silver_tables.get("player_match_stats", [])),
                "gold_player_features": len(gold_tables.get("player_features", [])),
                "gold_kpi_rows": len(kpi_rows),
                "gold_similarity_rows": len(similarity_rows),
                "gold_valuation_rows": len(valuation_rows),
            }
        )
        pipeline_ok = all(
            [
                counts["bronze_artifacts"] > 0,
                counts["silver_players"] >= 2,
                counts["silver_player_match_stats"] >= 2,
                counts["gold_player_features"] >= 2,
                counts["gold_kpi_rows"] >= 2,
                counts["gold_similarity_rows"] >= 2,
                counts["gold_valuation_rows"] >= 2,
                any(row.get("similar_players") for row in similarity_rows),
            ]
        )
        stages.append(
            ValidationStage(
                name="pipeline_outputs",
                passed=pipeline_ok,
                details=(
                    f"Bronze artifacts={counts['bronze_artifacts']}, players={counts['silver_players']}, "
                    f"player_match_stats={counts['silver_player_match_stats']}, player_features={counts['gold_player_features']}, "
                    f"kpi={counts['gold_kpi_rows']}, similarity={counts['gold_similarity_rows']}, valuation={counts['gold_valuation_rows']}"
                ),
            )
        )

        artifact_paths = {
            "bronze_manifest": base_dir / "data" / "bronze" / "manifest.json",
            "silver_players": base_dir / "data" / "silver" / "players.json",
            "silver_player_match_stats": base_dir / "data" / "silver" / "player_match_stats.json",
            "gold_player_features": base_dir / "data" / "gold" / "player_features.json",
            "gold_kpi": base_dir / "data" / "gold" / "kpi_engine.json",
            "gold_similarity": base_dir / "data" / "gold" / "player_similarity.json",
            "gold_valuation": base_dir / "data" / "gold" / "player_valuation.json",
        }
        storage_ok = all(path.exists() for path in artifact_paths.values())
        if storage_ok:
            storage_ok = len(read_json(artifact_paths["silver_players"])) >= 2 and len(read_json(artifact_paths["gold_valuation"])) >= 2
        stages.append(
            ValidationStage(
                name="artifact_storage",
                passed=storage_ok,
                details="Verified Bronze/Silver/Gold artifacts exist on disk and required dashboard-facing files are non-empty.",
            )
        )

        if FASTAPI_AVAILABLE:
            with _patch_artifact_paths(base_dir):
                test_client = TestClient(app)
                health = test_client.get("/health")
                players_response = test_client.get("/players")
                stats_response = test_client.get("/players/John Doe/stats")
                compare_response = test_client.get("/compare", params={"player_name": "John Doe", "limit": 1})
                value_response = test_client.get("/value", params={"player_name": "John Doe"})

                api_ok = all(response.status_code == 200 for response in [health, players_response, stats_response, compare_response, value_response])
                if api_ok:
                    api_ok = (
                        players_response.json().get("count", 0) >= 2
                        and stats_response.json().get("count", 0) >= 1
                        and len(compare_response.json().get("similar_players", [])) >= 1
                        and value_response.json().get("valuation_score") is not None
                    )
                stages.append(
                    ValidationStage(
                        name="backend_api",
                        passed=api_ok,
                        details="Verified /health, /players, /players/{player_name}/stats, /compare, and /value against real generated artifacts.",
                    )
                )

                with _patched_dashboard_requests(test_client):
                    client = DashboardAPIClient(base_url="http://testserver")
                    players_payload = client.get_players(limit=10)
                    stats_payload = client.get_player_stats("John Doe", limit=5)
                    compare_payload = client.get_compare("John Doe", limit=1)
                    value_payload = client.get_value(player_name="John Doe")

                dashboard_ok = (
                    players_payload.get("count", 0) >= 2
                    and any(row.get("player_name") == "John Doe" for row in players_payload.get("items", []))
                    and stats_payload.get("count", 0) >= 1
                    and len(compare_payload.get("similar_players", [])) >= 1
                    and value_payload.get("valuation_score") is not None
                )
                stages.append(
                    ValidationStage(
                        name="dashboard_client",
                        passed=dashboard_ok,
                        details="Verified dashboard API client receives non-empty player, stats, compare, and valuation payloads from a test backend.",
                    )
                )
        else:
            limitations.append("FastAPI is not installed in this environment, so backend route and dashboard-client checks are skipped.")
            stages.append(
                ValidationStage(
                    name="backend_api",
                    passed=True,
                    details="Skipped backend API verification because FastAPI is unavailable in this environment.",
                )
            )
            stages.append(
                ValidationStage(
                    name="dashboard_client",
                    passed=True,
                    details="Skipped dashboard-client verification because FastAPI is unavailable in this environment.",
                )
            )

    return ValidationResult(stages=stages, counts=counts, limitations=limitations)


def render_validation_report(result: ValidationResult) -> str:
    lines = []
    for stage in result.stages:
        prefix = "PASS" if stage.passed else "FAIL"
        lines.append(f"{prefix}: {stage.name} - {stage.details}")
    if result.counts:
        lines.append("COUNTS: " + ", ".join(f"{key}={value}" for key, value in sorted(result.counts.items())))
    if result.limitations:
        lines.append("LIMITATIONS:")
        lines.extend(f"- {item}" for item in result.limitations)
    return "\n".join(lines)
