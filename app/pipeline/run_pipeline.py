from __future__ import annotations

from app.analysis.advanced_metrics_v2 import build_advanced_metrics_v2_output
from app.analysis.alert_system import build_alert_output
from app.analysis.club_benchmark import build_club_benchmark_output
from app.analysis.club_development import build_club_development_rankings
from app.analysis.club_fit import build_club_fit_output
from app.analysis.clustering_engine import build_clustering_output
from app.analysis.feature_store import build_feature_store
from app.analysis.kpi_engine import build_kpi_engine_output
from app.analysis.market_value_model import build_market_value_output
from app.analysis.pathway_engine import build_pathway_output
from app.analysis.risk_engine import build_risk_output
from app.analysis.similarity_v2 import build_similarity_v2_output
from app.analysis.transfer_probability import build_transfer_probability_output
from app.analysis.valuation_v2 import build_valuation_v2_output
from app.db.persistence import ingest_silver_tables
from app.pipeline.bronze import build_bronze_manifest
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables
from app.pipeline.transfers import run_transfer_pipeline
from app.validation.cross_source_validator import build_confidence_index
from app.validation.drift_detector import build_drift_report


def run_pipeline() -> dict[str, object]:
    bronze = build_bronze_manifest()
    silver = build_silver_tables()
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
