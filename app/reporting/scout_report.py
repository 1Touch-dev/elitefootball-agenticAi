"""
Scout Report Generator.

Uses Claude claude-haiku-4-5 (cheapest model) via the Anthropic SDK to generate
a structured scouting report for each player. Falls back to a template-based
report when the API is unavailable or rate-limited.

Report sections:
  1. Executive Summary
  2. Performance Assessment
  3. Transfer Decision (BUY/SELL/HOLD) with reasoning
  4. Risk Factors
  5. Development Pathway + Target Clubs
  6. Scout Recommendation (1-2 sentences)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# ── Anthropic client (lazy init) ──────────────────────────────────────────────
_anthropic_client = None


def _get_client():
    global _anthropic_client
    if _anthropic_client is None:
        try:
            import anthropic
            _anthropic_client = anthropic.Anthropic()
        except Exception:
            _anthropic_client = False  # mark as unavailable
    return _anthropic_client if _anthropic_client is not False else None


# ── Template-based fallback report ───────────────────────────────────────────
def _template_report(player_data: dict[str, Any]) -> str:
    name = player_data.get("player_name", "Unknown")
    age = player_data.get("age", "?")
    decision = player_data.get("decision", "HOLD")
    decision_conf = player_data.get("decision_confidence", 0.5)
    buy_score = player_data.get("buy_score", 0.0)
    sell_score = player_data.get("sell_score", 0.0)
    reasoning = player_data.get("reasoning") or []
    val_score = player_data.get("valuation_score", 0)
    kpi = player_data.get("age_adjusted_kpi_score", 0)
    market_val = player_data.get("blended_value_eur", 0)
    best_fit = player_data.get("best_fit_club", "")
    pathway = player_data.get("best_pathway", "")
    sim_league = player_data.get("best_sim_league", "")
    sim_kpi = player_data.get("projected_kpi", "")
    risk_score = player_data.get("risk_score", 0)
    trajectory = player_data.get("trajectory", "stable")
    transfer_prob = player_data.get("transfer_probability_1y", 0)
    cluster = player_data.get("player_cluster", "")

    val_tier = "Elite" if val_score >= 80 else ("High" if val_score >= 65 else ("Medium" if val_score >= 50 else "Development"))
    risk_label = "Critical" if risk_score >= 0.7 else ("High" if risk_score >= 0.5 else ("Medium" if risk_score >= 0.3 else "Low"))

    decision_line = {
        "BUY": f"RECOMMENDATION: BUY — confidence {decision_conf:.0%}",
        "SELL": f"RECOMMENDATION: SELL — confidence {decision_conf:.0%}",
        "HOLD": f"RECOMMENDATION: HOLD — monitor for 3-6 months",
    }[decision]

    mv_str = f"€{market_val/1e6:.1f}M" if market_val >= 1_000_000 else (f"€{market_val/1e3:.0f}K" if market_val else "N/A")

    report_lines = [
        f"SCOUT REPORT — {name} (Age {age})",
        "=" * 50,
        "",
        "1. EXECUTIVE SUMMARY",
        f"   {name}, age {age}, is a {val_tier.lower()}-tier player currently assessed at {mv_str}.",
        f"   KPI score: {kpi:.1f}/14 | Valuation score: {val_score:.0f}/100 | Trajectory: {trajectory}",
        f"   Player archetype: {cluster or 'N/A'}",
        "",
        "2. PERFORMANCE ASSESSMENT",
        f"   Valuation score {val_score:.0f}/100 places this player in the {val_tier} tier.",
        f"   Age-adjusted KPI {kpi:.1f} reflects current match performance contribution.",
        f"   Transfer probability (1yr): {transfer_prob:.0%}" if transfer_prob else "   Transfer probability: insufficient data",
        "",
        "3. TRANSFER DECISION",
        f"   {decision_line}",
        f"   Buy score: {buy_score:.3f} | Sell score: {sell_score:.3f}",
    ]

    if reasoning:
        report_lines.append("   Key factors:")
        for r in reasoning[:4]:
            report_lines.append(f"   • {r}")

    report_lines += [
        "",
        "4. RISK ASSESSMENT",
        f"   Overall risk: {risk_label} ({risk_score:.2f}/1.00)",
        f"   Injury risk and performance volatility inform this assessment.",
        "",
        "5. DEVELOPMENT PATHWAY",
    ]

    if best_fit:
        report_lines.append(f"   Best club fit: {best_fit.title()}")
    if pathway:
        report_lines.append(f"   Recommended pathway: {pathway}")
    if sim_league and sim_kpi:
        report_lines.append(f"   Projected KPI in {sim_league}: {sim_kpi:.1f}")

    report_lines += [
        "",
        "6. SCOUT RECOMMENDATION",
    ]

    if decision == "BUY":
        report_lines.append(
            f"   Acquire {name} now — model signals undervaluation and strong trajectory. "
            f"Target {best_fit.title() if best_fit else 'a pathway club'} as likely destination."
        )
    elif decision == "SELL":
        report_lines.append(
            f"   Sell {name} in the current transfer window to maximise return at {mv_str}. "
            f"Age and trajectory indicators suggest value will plateau or decline."
        )
    else:
        report_lines.append(
            f"   Monitor {name} for one additional evaluation cycle. "
            f"Reassess following next 5 matches or when transfer window opens."
        )

    return "\n".join(report_lines)


# ── LLM-based report ─────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are an elite football scout at a South American development club.
Write a concise, professional scouting report based on the player data provided.
Format exactly as:
1. EXECUTIVE SUMMARY (2 sentences)
2. PERFORMANCE ASSESSMENT (3-4 bullet points, specific numbers)
3. TRANSFER DECISION: [BUY/SELL/HOLD] with 2-3 specific reasons
4. RISK FACTORS (2-3 bullets)
5. PATHWAY RECOMMENDATION (1-2 sentences, name a specific club)
6. SCOUT VERDICT (1 crisp sentence)
Be specific, data-driven, and concise. Never hallucinate stats not in the data."""


def _llm_report(player_data: dict[str, Any]) -> str | None:
    client = _get_client()
    if client is None:
        return None

    try:
        prompt = f"""Generate a scouting report for this player. Use only the data provided:

{json.dumps(player_data, indent=2, default=str)}

Write the report now:"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text if message.content else None
    except Exception:
        return None


# ── Main report generation ────────────────────────────────────────────────────
def generate_scout_report(
    player_name: str,
    decision_row: dict[str, Any] | None = None,
    kpi_row: dict[str, Any] | None = None,
    valuation_row: dict[str, Any] | None = None,
    risk_row: dict[str, Any] | None = None,
    market_value_row: dict[str, Any] | None = None,
    club_fit_row: dict[str, Any] | None = None,
    pathway_row: dict[str, Any] | None = None,
    simulation_row: dict[str, Any] | None = None,
    drift_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a full scout report for one player."""
    decision_row = decision_row or {}
    kpi_row = kpi_row or {}
    valuation_row = valuation_row or {}
    risk_row = risk_row or {}
    market_value_row = market_value_row or {}
    club_fit_row = club_fit_row or {}
    pathway_row = pathway_row or {}
    simulation_row = simulation_row or {}
    drift_row = drift_row or {}

    best_sim = simulation_row.get("best_projection") or {}

    player_data = {
        "player_name": player_name,
        "age": kpi_row.get("age") or valuation_row.get("age"),
        "decision": decision_row.get("decision", "HOLD"),
        "decision_confidence": decision_row.get("decision_confidence", 0.5),
        "buy_score": decision_row.get("buy_score", 0.0),
        "sell_score": decision_row.get("sell_score", 0.0),
        "reasoning": decision_row.get("reasoning", []),
        "valuation_score": valuation_row.get("valuation_score"),
        "computed_value_eur": valuation_row.get("computed_value_eur"),
        "market_value_eur_raw": valuation_row.get("market_value_eur"),
        "age_adjusted_kpi_score": kpi_row.get("age_adjusted_kpi_score"),
        "base_kpi_score": kpi_row.get("base_kpi_score"),
        "blended_value_eur": market_value_row.get("blended_value_eur"),
        "value_confidence": market_value_row.get("value_confidence"),
        "confidence_interval": market_value_row.get("confidence_interval"),
        "risk_score": risk_row.get("risk_score") or risk_row.get("injury_risk"),
        "trajectory": drift_row.get("overall_drift_direction"),
        "transfer_probability_1y": valuation_row.get("transfer_probability_1y")
            or decision_row.get("supporting_data", {}).get("transfer_probability_1y"),
        "best_fit_club": club_fit_row.get("best_fit_club"),
        "best_fit_score": club_fit_row.get("best_fit_score"),
        "best_pathway": pathway_row.get("best_destination"),
        "pathway_success_prob": pathway_row.get("best_success_probability"),
        "best_sim_league": best_sim.get("target_league"),
        "projected_kpi": best_sim.get("projected_kpi"),
        "projected_value_eur": best_sim.get("projected_value_eur"),
        "player_cluster": kpi_row.get("cluster_label"),
    }

    # Try LLM first, fallback to template
    report_text = _llm_report(player_data) or _template_report(player_data)
    report_source = "llm" if _llm_report.__name__ and _get_client() else "template"

    return {
        "player_name": player_name,
        "decision": player_data["decision"],
        "report_text": report_text,
        "report_source": report_source,
        "key_metrics": {
            "age": player_data["age"],
            "valuation_score": player_data["valuation_score"],
            "kpi_score": player_data["age_adjusted_kpi_score"],
            "blended_value_eur": player_data["blended_value_eur"],
            "risk_score": player_data["risk_score"],
            "trajectory": player_data["trajectory"],
            "best_fit_club": player_data["best_fit_club"],
        },
    }


def build_scout_report_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]] | None = None,
    valuation_rows: list[dict[str, Any]] | None = None,
    risk_rows: list[dict[str, Any]] | None = None,
    market_value_rows: list[dict[str, Any]] | None = None,
    club_fit_rows: list[dict[str, Any]] | None = None,
    pathway_rows: list[dict[str, Any]] | None = None,
    simulation_rows: list[dict[str, Any]] | None = None,
    drift_report: dict[str, Any] | None = None,
) -> dict[str, object]:
    decision_rows = decision_rows or []
    valuation_rows = valuation_rows or []
    risk_rows = risk_rows or []
    market_value_rows = market_value_rows or []
    club_fit_rows = club_fit_rows or []
    pathway_rows = pathway_rows or []
    simulation_rows = simulation_rows or []
    drift_report = drift_report or {}

    def _nk(name: Any) -> str:
        return str(name or "").strip().lower()

    kpi_by = {_nk(r.get("player_name")): r for r in kpi_rows}
    decision_by = {_nk(r.get("player_name")): r for r in decision_rows}
    val_by = {_nk(r.get("player_name")): r for r in valuation_rows}
    risk_by = {_nk(r.get("player_name")): r for r in risk_rows}
    mv_by = {_nk(r.get("player_name")): r for r in market_value_rows}
    fit_by = {_nk(r.get("player_name")): r for r in club_fit_rows}
    path_by = {_nk(r.get("player_name")): r for r in pathway_rows}
    sim_by = {_nk(r.get("player_name")): r for r in simulation_rows}
    players_by = {
        _nk(r.get("player_name")): r
        for r in silver_tables.get("players", [])
    }

    all_names = sorted(set(kpi_by) | set(decision_by) | set(players_by))
    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        pr = players_by.get(name, {})
        drift_row = drift_report.get("players", {}).get(name, {}).get("career_drift", {})
        canonical = pr.get("player_name") or kpi_by.get(name, {}).get("player_name") or name

        report = generate_scout_report(
            player_name=canonical,
            decision_row=decision_by.get(name),
            kpi_row=kpi_by.get(name),
            valuation_row=val_by.get(name),
            risk_row=risk_by.get(name),
            market_value_row=mv_by.get(name),
            club_fit_row=fit_by.get(name),
            pathway_row=path_by.get(name),
            simulation_row=sim_by.get(name),
            drift_row=drift_row,
        )
        output_rows.append(report)

    path = write_json(Path(settings.gold_data_dir) / "scout_reports.json", output_rows)
    return {"path": path, "rows": output_rows}
