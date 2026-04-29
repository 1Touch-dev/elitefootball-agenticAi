from __future__ import annotations

from app.analysis.advanced_metrics_engine import build_advanced_metrics_output
from app.analysis.advanced_metrics_v2 import build_advanced_metrics_v2_output
from app.analysis.club_benchmark import build_club_benchmark_output
from app.analysis.club_development import build_club_development_rankings
from app.analysis.kpi_engine import build_kpi_engine_output
from app.analysis.pathway_engine import build_pathway_output
from app.analysis.risk_engine import build_risk_output
from app.analysis.similarity_v2 import build_similarity_v2_output
from app.analysis.valuation_v2 import build_valuation_v2_output
from app.db.persistence import ingest_silver_tables
from app.pipeline.bronze import build_bronze_manifest
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables
from app.pipeline.transfers import run_transfer_pipeline


def run_pipeline() -> dict[str, object]:
    bronze = build_bronze_manifest()
    silver = build_silver_tables()
    persistence = ingest_silver_tables(silver["tables"])
    gold = build_gold_features(silver["tables"])
    kpi = build_kpi_engine_output(silver["tables"])

    # Advanced metrics v2 (xG, xA, xT, EPV, OBV)
    advanced_metrics = build_advanced_metrics_v2_output(silver["tables"], gold["tables"])

    # Risk engine
    risk = build_risk_output(silver["tables"], gold["tables"], kpi["rows"])

    # Valuation v2 (weighted model)
    valuation = build_valuation_v2_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        risk_rows=risk["rows"],
    )

    # Development pathway
    pathway = build_pathway_output(silver["tables"], gold["tables"], kpi["rows"], valuation["rows"])

    # Role-aware similarity v2
    similarity = build_similarity_v2_output(
        silver["tables"],
        gold["tables"],
        kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        pathway_rows=pathway["rows"],
        valuation_rows=valuation["rows"],
    )

    # Club benchmark (IDV vs Benfica vs Ajax vs Salzburg)
    club_benchmark = build_club_benchmark_output(
        silver["tables"],
        kpi["rows"],
        silver["tables"].get("transfers", []),
    )

    # Legacy club development (kept for backward compat)
    club_development = build_club_development_rankings(silver["tables"], gold["tables"], kpi["rows"], valuation["rows"])

    # Transfer pipeline
    transfers = run_transfer_pipeline(silver["tables"].get("transfers", []))

    return {
        "bronze": bronze,
        "silver": silver,
        "persistence": persistence,
        "gold": gold,
        "kpi": kpi,
        "advanced_metrics": advanced_metrics,
        "risk": risk,
        "valuation": valuation,
        "pathway": pathway,
        "similarity": similarity,
        "club_benchmark": club_benchmark,
        "club_development": club_development,
        "transfers": transfers,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(result)
