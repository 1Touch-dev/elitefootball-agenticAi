from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

import app.agents.analyst_agent as analyst_agent
import app.agents.data_cleaner_agent as data_cleaner_agent
import app.agents.report_generator_agent as report_generator_agent
import app.agents.scraper_agent as scraper_agent
from app.agents.types import AgentRunResult, AgentStepResult, AgentTask
from app.safety.service import assert_allowed
from app.safety.types import ActionKind, PolicyDecision, SafetyCheckRequest


@dataclass(frozen=True)
class AgentRole:
    name: str
    responsibility: str
    supported_task_kinds: list[str]


AGENT_ROLES = [
    AgentRole("coordinator", "Routes work across scraping, cleaning, analysis, and report generation.", ["scrape_players", "clean_data", "run_analysis", "generate_report", "full_refresh"]),
    AgentRole("scraper", "Collects and normalizes IDV player data from configured sources.", sorted(scraper_agent.SUPPORTED_TASK_KINDS)),
    AgentRole("data_cleaner", "Builds Bronze, Silver, and Gold artifacts from parsed source data.", sorted(data_cleaner_agent.SUPPORTED_TASK_KINDS)),
    AgentRole("analyst", "Generates KPI, risk, similarity, valuation, and related analysis artifacts.", sorted(analyst_agent.SUPPORTED_TASK_KINDS)),
    AgentRole("report_generator", "Builds operator-facing summaries from available artifacts and analysis outputs.", sorted(report_generator_agent.SUPPORTED_TASK_KINDS)),
]


AGENT_HANDLERS: dict[str, Callable[[AgentTask], AgentStepResult]] = {
    "scraper": scraper_agent.run,
    "data_cleaner": data_cleaner_agent.run,
    "analyst": analyst_agent.run,
    "report_generator": report_generator_agent.run,
}

ROUTE_MAP = {
    "scrape_players": ["scraper"],
    "clean_data": ["data_cleaner"],
    "run_analysis": ["analyst"],
    "generate_report": ["report_generator"],
    "full_refresh": ["scraper", "data_cleaner", "analyst", "report_generator"],
}


def build_agent_summary() -> list[dict[str, object]]:
    return [asdict(role) for role in AGENT_ROLES]


def supported_task_kinds() -> list[str]:
    return sorted(ROUTE_MAP.keys())


def route_task(task: AgentTask | str) -> list[str]:
    task_kind = task.kind if isinstance(task, AgentTask) else str(task)
    if task_kind not in ROUTE_MAP:
        raise ValueError(f"Unsupported task kind: {task_kind}")
    return list(ROUTE_MAP[task_kind])


def run_task(task: AgentTask | str, payload: dict | None = None) -> AgentRunResult:
    task_obj = task if isinstance(task, AgentTask) else AgentTask.from_input(kind=str(task), payload=payload)
    safety_request = SafetyCheckRequest(
        action_kind=ActionKind.AGENT_TASK,
        action_name=task_obj.kind,
        requested_by=task_obj.requested_by,
        metadata=dict(task_obj.metadata),
    )
    assert_allowed(safety_request)
    route = route_task(task_obj)
    context_metadata = dict(task_obj.metadata)
    step_results: list[AgentStepResult] = []

    for agent_name in route:
        handler = AGENT_HANDLERS[agent_name]
        step_task = AgentTask.from_input(
            kind=task_obj.kind,
            payload=task_obj.payload,
            requested_by=task_obj.requested_by,
            metadata=context_metadata,
        )
        step_result = handler(step_task)
        step_results.append(step_result)

        if agent_name == "data_cleaner":
            silver = step_result.artifacts.get("silver") or {}
            gold = step_result.artifacts.get("gold") or {}
            context_metadata["silver_tables"] = silver.get("tables") if isinstance(silver, dict) else None
            context_metadata["gold_tables"] = gold.get("tables") if isinstance(gold, dict) else None

        if agent_name == "analyst":
            context_metadata["analysis_outputs"] = step_result.artifacts

    summary = " -> ".join(step.summary for step in step_results)
    return AgentRunResult(
        task_kind=task_obj.kind,
        status="ok",
        route=route,
        steps=step_results,
        summary=summary,
        metadata={
            "supported_task_kinds": supported_task_kinds(),
            "safety_decision": PolicyDecision.ALLOW.value,
        },
    )


def run_task_dict(task_payload: dict) -> dict:
    task = AgentTask.from_input(
        kind=str(task_payload.get("task_kind") or task_payload.get("kind") or "").strip(),
        payload=task_payload.get("payload"),
        requested_by=task_payload.get("requested_by"),
        metadata=task_payload.get("metadata"),
    )
    return run_task(task).to_dict()
