from __future__ import annotations

from app.analysis.advanced_metrics_v2 import build_advanced_metrics_v2_output
from app.analysis.alert_system import build_alert_output
from app.analysis.club_benchmark import build_club_benchmark_output
from app.analysis.club_development import build_club_development_rankings
from app.analysis.club_fit import build_club_fit_output
from app.analysis.clustering_engine import build_clustering_output
from app.analysis.decision_engine import build_decision_engine_output
from app.analysis.feature_store import build_feature_store
from app.analysis.kpi_engine import build_kpi_engine_output
from app.analysis.market_value_model import build_market_value_output
from app.analysis.pathway_engine import build_pathway_output
from app.analysis.player_graph import build_player_graph_output
from app.analysis.player_simulation import build_player_simulation_output
from app.analysis.risk_engine import build_risk_output
from app.analysis.similarity_v2 import build_similarity_v2_output
from app.analysis.transfer_probability import build_transfer_probability_output
from app.analysis.valuation_v2 import build_valuation_v2_output
from app.db.persistence import ingest_silver_tables
from app.learning.pathway_learning_engine import build_pathway_learning_output
from app.pipeline.bronze import build_bronze_manifest
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables
from app.pipeline.transfers import run_transfer_pipeline
from app.reporting.scout_report import build_scout_report_output
from app.validation.cross_source_validator import build_confidence_index
from app.validation.drift_detector import build_drift_report


def _scrape_if_needed() -> dict[str, object]:
    """Run TM HTTP scraping for IDV players before the pipeline starts."""
    from pathlib import Path
    from app.config import settings
    from app.pipeline.io import list_files

    parsed_dir = Path(settings.parsed_data_dir)
    existing = list(list_files(parsed_dir, "*.json"))
    if existing:
        return {"skipped": True, "reason": "parsed data already present", "count": len(existing)}

    from app.scraping.tm_http_scraper import scrape_all_players
    results = scrape_all_players(force_refresh=False)
    ok = sum(1 for r in results if r.get("status") in ("ok", "cached"))
    return {"skipped": False, "results": results, "scraped": ok}


def _guard_real_data() -> None:
    """Raise if no parsed data exists (pipeline has no input)."""
    from pathlib import Path
    from app.config import settings
    from app.pipeline.io import list_files

    parsed_dir = Path(settings.parsed_data_dir)
    files = list(list_files(parsed_dir, "*.json"))
    if not files:
        raise RuntimeError(
            "No real scraped data found in data/parsed/transfermarkt/. "
            "Run scripts/run_real_scrape.py first to populate bronze/raw data."
        )


def run_pipeline() -> dict[str, object]:
    scrape_result = _scrape_if_needed()
    _guard_real_data()

    bronze = build_bronze_manifest()
    silver = build_silver_tables()

    # Pipeline strict mode: fail if silver tables are empty or invalid
    if not silver or not silver.get("tables") or not silver["tables"].get("players"):
        raise RuntimeError("Empty silver tables - pipeline stopped in strict mode.")

    persistence = ingest_silver_tables(silver["tables"])
    gold = build_gold_features(silver["tables"])

    # ── Validation layer ──────────────────────────────────────────────────────
    confidence_index = build_confidence_index(silver["tables"])
    drift_report = build_drift_report(silver["tables"])

    # ── Core analytics (confidence-weighted) ─────────────────────────────────
    kpi = build_kpi_engine_output(silver["tables"], confidence_index=confidence_index)

    advanced_metrics = build_advanced_metrics_v2_output(silver["tables"], gold["tables"])

    risk = build_risk_output(silver["tables"], gold["tables"], kpi["rows"])

    valuation = build_valuation_v2_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        risk_rows=risk["rows"],
        confidence_index=confidence_index,
    )

    pathway = build_pathway_output(silver["tables"], gold["tables"], kpi["rows"], valuation["rows"])

    similarity = build_similarity_v2_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        pathway_rows=pathway["rows"],
        valuation_rows=valuation["rows"],
    )

    club_benchmark = build_club_benchmark_output(
        silver["tables"],
        kpi["rows"],
        silver["tables"].get("transfers", []),
    )

    club_development = build_club_development_rankings(
        silver["tables"], gold["tables"], kpi["rows"], valuation["rows"]
    )

    transfers = run_transfer_pipeline(silver["tables"].get("transfers", []))

    # ── Intelligence layer ────────────────────────────────────────────────────
    transfer_probability = build_transfer_probability_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        valuation_rows=valuation["rows"],
        drift_report=drift_report,
    )

    club_fit = build_club_fit_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        valuation_rows=valuation["rows"],
    )

    market_value = build_market_value_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        valuation_rows=valuation["rows"],
        transfer_rows=transfer_probability["rows"],
        confidence_index=confidence_index,
        drift_report=drift_report,
    )

    clusters = build_clustering_output(
        kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
    )

    alerts = build_alert_output(
        kpi["rows"],
        valuation_rows=valuation["rows"],
        drift_report=drift_report,
        transfer_rows=transfer_probability["rows"],
        confidence_index=confidence_index,
    )

    # ── Feature store (consolidated) ─────────────────────────────────────────
    feature_store = build_feature_store(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        valuation_rows=valuation["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        risk_rows=risk["rows"],
        pathway_rows=pathway["rows"],
        similarity_rows=similarity["rows"],
        transfer_rows=transfer_probability["rows"],
        market_value_rows=market_value["rows"],
        cluster_rows=clusters.get("rows", []),
        confidence_index=confidence_index,
    )

    # ── Phase 7: Decision intelligence ───────────────────────────────────────
    pathway_learning = build_pathway_learning_output(
        silver["tables"],
        kpi["rows"],
        pathway_rows=pathway["rows"],
        drift_report=drift_report,
    )

    decision_engine = build_decision_engine_output(
        silver["tables"],
        kpi["rows"],
        valuation_rows=valuation["rows"],
        transfer_rows=transfer_probability["rows"],
        club_fit_rows=club_fit["rows"],
        market_value_rows=market_value["rows"],
        risk_rows=risk["rows"],
        confidence_index=confidence_index,
        drift_report=drift_report,
        pathway_learning_rows=pathway_learning["rows"],
    )

    player_simulation = build_player_simulation_output(
        silver["tables"],
        kpi["rows"],
        valuation_rows=valuation["rows"],
        club_fit_rows=club_fit["rows"],
        drift_report=drift_report,
    )

    player_graph = build_player_graph_output()

    scout_reports = build_scout_report_output(
        silver["tables"],
        kpi["rows"],
        decision_rows=decision_engine["rows"],
        valuation_rows=valuation["rows"],
        risk_rows=risk["rows"],
        market_value_rows=market_value["rows"],
        club_fit_rows=club_fit["rows"],
        pathway_rows=pathway_learning["rows"],
        simulation_rows=player_simulation["rows"],
        drift_report=drift_report,
    )

    return {
        "bronze": bronze,
        "silver": silver,
        "persistence": persistence,
        "gold": gold,
        "confidence_index": confidence_index,
        "drift_report": drift_report,
        "kpi": kpi,
        "advanced_metrics": advanced_metrics,
        "risk": risk,
        "valuation": valuation,
        "pathway": pathway,
        "similarity": similarity,
        "club_benchmark": club_benchmark,
        "club_development": club_development,
        "transfers": transfers,
        "transfer_probability": transfer_probability,
        "club_fit": club_fit,
        "market_value": market_value,
        "clusters": clusters,
        "alerts": alerts,
        "feature_store": feature_store,
        "pathway_learning": pathway_learning,
        "decision_engine": decision_engine,
        "player_simulation": player_simulation,
        "player_graph": player_graph,
        "scout_reports": scout_reports,
    }


def run_incremental_pipeline(player_slugs: list[str]) -> dict[str, object]:
    """
    Rebuild Silver + Gold only for the given player slugs.
    Used after targeted scrapes so we don't reprocess the entire dataset.
    """
    from app.pipeline.silver import build_silver_tables_for_players

    silver = build_silver_tables_for_players(player_slugs)
    confidence_index = build_confidence_index(silver["tables"])
    drift_report = build_drift_report(silver["tables"])

    persistence = ingest_silver_tables(silver["tables"])
    gold = build_gold_features(silver["tables"])
    kpi = build_kpi_engine_output(silver["tables"], confidence_index=confidence_index)
    advanced_metrics = build_advanced_metrics_v2_output(silver["tables"], gold["tables"])
    risk = build_risk_output(silver["tables"], gold["tables"], kpi["rows"])
    valuation = build_valuation_v2_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        risk_rows=risk["rows"],
        confidence_index=confidence_index,
    )
    pathway = build_pathway_output(silver["tables"], gold["tables"], kpi["rows"], valuation["rows"])
    similarity = build_similarity_v2_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        pathway_rows=pathway["rows"],
        valuation_rows=valuation["rows"],
    )
    transfer_probability = build_transfer_probability_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        valuation_rows=valuation["rows"],
        drift_report=drift_report,
    )
    return {
        "silver": silver,
        "persistence": persistence,
        "gold": gold,
        "kpi": kpi,
        "advanced_metrics": advanced_metrics,
        "risk": risk,
        "valuation": valuation,
        "pathway": pathway,
        "similarity": similarity,
        "transfer_probability": transfer_probability,
        "player_slugs": player_slugs,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(result)
