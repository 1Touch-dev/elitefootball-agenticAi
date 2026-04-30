from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import tempfile
from typing import Any, Iterator
from unittest.mock import patch
from urllib.parse import urlparse

from app.analysis.legacy.advanced_metrics_engine import build_advanced_metrics_output
from app.analysis.club_development import build_club_development_rankings
from app.analysis.kpi_engine import build_kpi_engine_output
from app.analysis.risk_engine import build_risk_output
from app.analysis.legacy.similarity_engine import build_similarity_output
from app.analysis.legacy.valuation_engine import build_valuation_output
from app.config import settings
from app.pipeline.bronze import build_bronze_manifest
from app.pipeline.gold import build_gold_features
from app.pipeline.io import read_json, write_json
from app.pipeline.silver import build_silver_tables
from dashboard.api_client import DashboardAPIClient

SQLALCHEMY_AVAILABLE = importlib.util.find_spec("sqlalchemy") is not None
FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None
PLAYWRIGHT_AVAILABLE = importlib.util.find_spec("playwright") is not None

if FASTAPI_AVAILABLE:
    from fastapi.testclient import TestClient
    from app.main import app


@dataclass
class ValidationStage:
    name: str
    passed: bool
    details: str
    skipped: bool = False


@dataclass
class ValidationResult:
    stages: list[ValidationStage]
    counts: dict[str, int]
    limitations: list[str]
    environment: dict[str, bool]

    @property
    def ok(self) -> bool:
        return self.readiness != "NOT_READY"

    @property
    def readiness(self) -> str:
        if any(not stage.passed and not stage.skipped for stage in self.stages):
            return "NOT_READY"
        if any(stage.skipped for stage in self.stages):
            return "READY_WITH_LIMITATIONS"
        return "READY"


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
            "database_url": settings.database_url,
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
            object.__setattr__(settings, "database_url", f"sqlite:///{base_dir / 'full-system.sqlite'}")
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


def _run_persistence_if_available(silver_tables: dict[str, list[dict[str, Any]]]) -> tuple[ValidationStage, dict[str, int], list[str]]:
    if not SQLALCHEMY_AVAILABLE:
        return (
            ValidationStage(
                name="db_persistence",
                passed=True,
                skipped=True,
                details="Skipped DB ingestion because SQLAlchemy is unavailable in this environment.",
            ),
            {},
            ["SQLAlchemy is not installed in this environment, so the DB ingestion stage is skipped."],
        )

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.db import base as db_base
    from app.db.persistence import ingest_silver_tables

    db_path = Path(settings.repo_root) / "full-system.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    try:
        with patch.object(db_base, "engine", engine), patch.object(db_base, "SessionLocal", session_local), patch("app.db.persistence.settings", settings):
            report = ingest_silver_tables(silver_tables)
        counts = {
            "db_clubs": int(report["verification"]["counts"].get("clubs", 0)),
            "db_players": int(report["verification"]["counts"].get("players", 0)),
            "db_matches": int(report["verification"]["counts"].get("matches", 0)),
            "db_stats": int(report["verification"]["counts"].get("stats", 0)),
        }
        return (
            ValidationStage(
                name="db_persistence",
                passed=(
                    report.get("status") in {"success_complete", "success_partial"}
                    and counts["db_players"] >= 2
                    and counts["db_matches"] >= 2
                    and counts["db_stats"] >= 4
                ),
                details=(
                    f"Persistence status={report.get('status')}, clubs={counts['db_clubs']}, players={counts['db_players']}, "
                    f"matches={counts['db_matches']}, stats={counts['db_stats']}"
                ),
            ),
            counts,
            [],
        )
    finally:
        engine.dispose()


def run_full_system_validation() -> ValidationResult:
    stages: list[ValidationStage] = []
    counts: dict[str, int] = {}
    environment = {
        "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
        "fastapi_available": FASTAPI_AVAILABLE,
        "playwright_available": PLAYWRIGHT_AVAILABLE,
    }
    limitations = [
        "This validation uses deterministic seeded scrape-like fixture data instead of a mandatory live external scrape.",
        "Live scrape execution remains environment-sensitive because browser dependencies and source access are not guaranteed.",
    ]

    stages.append(
        ValidationStage(
            name="environment_preflight",
            passed=True,
            details=(
                f"sqlalchemy_available={environment['sqlalchemy_available']}, "
                f"fastapi_available={environment['fastapi_available']}, "
                f"playwright_available={environment['playwright_available']}"
            ),
        )
    )

    with _temporary_settings() as base_dir:
        seeded_counts = _seed_fixture_data(base_dir)
        stages.append(
            ValidationStage(
                name="seeded_scrape_inputs",
                passed=True,
                details=(
                    f"Seeded {seeded_counts['transfermarkt_parsed_payloads']} Transfermarkt payloads, "
                    f"{seeded_counts['fbref_parsed_payloads']} FBref payloads, and {seeded_counts['raw_html_files']} raw HTML samples."
                ),
            )
        )

        bronze = build_bronze_manifest()
        counts["bronze_artifacts"] = int(bronze["manifest"].get("artifact_count", 0))
        stages.append(
            ValidationStage(
                name="bronze_manifest",
                passed=counts["bronze_artifacts"] >= 8,
                details=f"Bronze manifest contains {counts['bronze_artifacts']} raw/parsed scrape artifacts.",
            )
        )

        silver = build_silver_tables()
        silver_tables = silver["tables"]
        counts.update(
            {
                "silver_players": len(silver_tables.get("players", [])),
                "silver_matches": len(silver_tables.get("matches", [])),
                "silver_player_match_stats": len(silver_tables.get("player_match_stats", [])),
                "silver_player_per90": len(silver_tables.get("player_per90", [])),
            }
        )
        stages.append(
            ValidationStage(
                name="silver_tables",
                passed=(
                    counts["silver_players"] >= 2
                    and counts["silver_matches"] >= 2
                    and counts["silver_player_match_stats"] >= 4
                    and counts["silver_player_per90"] >= 4
                ),
                details=(
                    f"players={counts['silver_players']}, matches={counts['silver_matches']}, "
                    f"player_match_stats={counts['silver_player_match_stats']}, player_per90={counts['silver_player_per90']}"
                ),
            )
        )

        persistence_stage, persistence_counts, persistence_limitations = _run_persistence_if_available(silver_tables)
        stages.append(persistence_stage)
        counts.update(persistence_counts)
        limitations.extend(persistence_limitations)

        gold = build_gold_features(silver_tables)
        kpi = build_kpi_engine_output(silver_tables)
        advanced_metrics = build_advanced_metrics_output(silver_tables)
        risk = build_risk_output(silver_tables, gold["tables"], kpi["rows"])
        similarity = build_similarity_output(silver_tables, gold["tables"], kpi["rows"])
        valuation = build_valuation_output(silver_tables, gold["tables"], kpi["rows"], advanced_metrics["rows"], risk["rows"])
        club_development = build_club_development_rankings(silver_tables, gold["tables"], kpi["rows"], valuation["rows"])

        counts.update(
            {
                "gold_player_features": len(gold["tables"].get("player_features", [])),
                "gold_kpi_rows": len(kpi["rows"]),
                "gold_advanced_metrics_rows": len(advanced_metrics["rows"]),
                "gold_risk_rows": len(risk["rows"]),
                "gold_similarity_rows": len(similarity["rows"]),
                "gold_valuation_rows": len(valuation["rows"]),
                "gold_club_development_rows": len(club_development["rankings"]),
            }
        )
        stages.append(
            ValidationStage(
                name="analysis_outputs",
                passed=(
                    counts["gold_player_features"] >= 2
                    and counts["gold_kpi_rows"] >= 2
                    and counts["gold_advanced_metrics_rows"] >= 2
                    and counts["gold_risk_rows"] >= 2
                    and counts["gold_similarity_rows"] >= 2
                    and counts["gold_valuation_rows"] >= 2
                    and counts["gold_club_development_rows"] >= 1
                    and any(row.get("similar_players") for row in similarity["rows"])
                ),
                details=(
                    f"player_features={counts['gold_player_features']}, kpi={counts['gold_kpi_rows']}, advanced_metrics={counts['gold_advanced_metrics_rows']}, "
                    f"risk={counts['gold_risk_rows']}, similarity={counts['gold_similarity_rows']}, valuation={counts['gold_valuation_rows']}, "
                    f"club_development={counts['gold_club_development_rows']}"
                ),
            )
        )

        artifact_paths = {
            "players": base_dir / "data" / "silver" / "players.json",
            "player_match_stats": base_dir / "data" / "silver" / "player_match_stats.json",
            "player_features": base_dir / "data" / "gold" / "player_features.json",
            "kpi": base_dir / "data" / "gold" / "kpi_engine.json",
            "advanced_metrics": base_dir / "data" / "gold" / "advanced_metrics.json",
            "risk": base_dir / "data" / "gold" / "player_risk.json",
            "similarity": base_dir / "data" / "gold" / "player_similarity.json",
            "valuation": base_dir / "data" / "gold" / "player_valuation.json",
            "club_development": base_dir / "data" / "gold" / "club_development_rankings.json",
        }
        storage_ok = all(path.exists() for path in artifact_paths.values())
        if storage_ok:
            storage_ok = len(read_json(artifact_paths["players"])) >= 2 and len(read_json(artifact_paths["valuation"])) >= 2
        stages.append(
            ValidationStage(
                name="artifact_storage",
                passed=storage_ok,
                details="Verified Silver/Gold artifacts exist on disk and required system outputs are non-empty.",
            )
        )

        if FASTAPI_AVAILABLE:
            with _patch_artifact_paths(base_dir):
                test_client = TestClient(app)
                responses = {
                    "health": test_client.get("/health"),
                    "status": test_client.get("/dashboard/status"),
                    "players": test_client.get("/players"),
                    "stats": test_client.get("/players/John Doe/stats"),
                    "compare": test_client.get("/compare", params={"player_name": "John Doe", "limit": 1}),
                    "value": test_client.get("/value", params={"player_name": "John Doe"}),
                }
                api_ok = all(response.status_code == 200 for response in responses.values())
                if api_ok:
                    api_ok = (
                        responses["players"].json().get("count", 0) >= 2
                        and responses["stats"].json().get("count", 0) >= 1
                        and len(responses["compare"].json().get("similar_players", [])) >= 1
                        and responses["value"].json().get("valuation_score") is not None
                    )
                stages.append(
                    ValidationStage(
                        name="backend_api",
                        passed=api_ok,
                        details="Verified /health, /dashboard/status, /players, /players/{player_name}/stats, /compare, and /value against generated artifacts.",
                    )
                )

                with _patched_dashboard_requests(test_client):
                    client = DashboardAPIClient(base_url="http://testserver")
                    dashboard_status = client.get_dashboard_status()
                    players_payload = client.get_players(limit=10)
                    stats_payload = client.get_player_stats("John Doe", limit=5)
                    compare_payload = client.get_compare("John Doe", limit=1)
                    value_payload = client.get_value(player_name="John Doe")
                dashboard_ok = (
                    dashboard_status.get("status") in {"ready", "partial"}
                    and players_payload.get("count", 0) >= 2
                    and stats_payload.get("count", 0) >= 1
                    and len(compare_payload.get("similar_players", [])) >= 1
                    and value_payload.get("valuation_score") is not None
                )
                stages.append(
                    ValidationStage(
                        name="dashboard_client",
                        passed=dashboard_ok,
                        details="Verified dashboard client receives status, players, stats, compare, and valuation payloads from a test backend.",
                    )
                )
        else:
            limitations.append("FastAPI is not installed in this environment, so backend-route and dashboard-client validation are skipped.")
            stages.append(
                ValidationStage(
                    name="backend_api",
                    passed=True,
                    skipped=True,
                    details="Skipped backend API verification because FastAPI is unavailable in this environment.",
                )
            )
            stages.append(
                ValidationStage(
                    name="dashboard_client",
                    passed=True,
                    skipped=True,
                    details="Skipped dashboard-client verification because FastAPI is unavailable in this environment.",
                )
            )

    return ValidationResult(stages=stages, counts=counts, limitations=limitations, environment=environment)


def render_validation_report(result: ValidationResult) -> str:
    lines: list[str] = []
    lines.append(f"READINESS: {result.readiness}")
    lines.append(
        "ENVIRONMENT: "
        + ", ".join(f"{key}={value}" for key, value in sorted(result.environment.items()))
    )
    for stage in result.stages:
        prefix = "SKIP" if stage.skipped else ("PASS" if stage.passed else "FAIL")
        lines.append(f"{prefix}: {stage.name} - {stage.details}")
    if result.counts:
        lines.append("COUNTS: " + ", ".join(f"{key}={value}" for key, value in sorted(result.counts.items())))
    if result.limitations:
        lines.append("LIMITATIONS:")
        lines.extend(f"- {item}" for item in result.limitations)
    lines.append(
        "SUMMARY: deterministic seeded full-pipeline validation covers scrape-like inputs -> Bronze -> Silver -> DB when available -> KPI/analysis -> backend/dashboard contract when available."
    )
    return "\n".join(lines)
