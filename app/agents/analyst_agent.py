from __future__ import annotations

from app.agents.types import AgentStepResult, AgentTask
from app.analysis.advanced_metrics_v2 import build_advanced_metrics_v2_output
from app.analysis.club_benchmark import build_club_benchmark_output
from app.analysis.kpi_engine import build_kpi_engine_output
from app.analysis.pathway_engine import build_pathway_output
from app.analysis.risk_engine import build_risk_output as build_risk_engine_output
from app.analysis.similarity_v2 import build_similarity_v2_output
from app.analysis.valuation_v2 import build_valuation_v2_output
from app.pipeline.gold import build_gold_features
from app.pipeline.silver import build_silver_tables


AGENT_NAME = "analyst"
SUPPORTED_TASK_KINDS = {"run_analysis", "full_refresh"}


def run(task: AgentTask) -> AgentStepResult:
    if task.kind not in SUPPORTED_TASK_KINDS:
        raise ValueError(f"Unsupported analyst task kind: {task.kind}")

    silver_tables = task.metadata.get("silver_tables")
    gold_tables = task.metadata.get("gold_tables")
    if silver_tables is None:
        silver_tables = build_silver_tables()["tables"]
    if gold_tables is None:
        gold_tables = build_gold_features(silver_tables)["tables"]

    kpi = build_kpi_engine_output(silver_tables)
    advanced_metrics = build_advanced_metrics_v2_output(silver_tables, gold_tables)
    risk = build_risk_engine_output(silver_tables, gold_tables, kpi["rows"])
    valuation = build_valuation_v2_output(
        silver_tables, gold_tables, kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        risk_rows=risk["rows"],
    )
    pathway = build_pathway_output(silver_tables, gold_tables, kpi["rows"], valuation["rows"])
    similarity = build_similarity_v2_output(
        silver_tables, gold_tables, kpi["rows"],
        advanced_metric_rows=advanced_metrics["rows"],
        pathway_rows=pathway["rows"],
        valuation_rows=valuation["rows"],
    )
    benchmark = build_club_benchmark_output(silver_tables, gold_tables, kpi["rows"])

    return AgentStepResult(
        agent_name=AGENT_NAME,
        task_kind=task.kind,
        status="ok",
        summary="Built KPI, advanced metrics v2, risk, valuation v2, pathway, similarity v2, and benchmark outputs.",
        artifacts={
            "kpi": kpi,
            "advanced_metrics": advanced_metrics,
            "risk": risk,
            "valuation": valuation,
            "pathway": pathway,
            "similarity": similarity,
            "benchmark": benchmark,
        },
        metadata={
            "supported_task_kinds": sorted(SUPPORTED_TASK_KINDS),
            "silver_tables": silver_tables,
            "gold_tables": gold_tables,
        },
    )
