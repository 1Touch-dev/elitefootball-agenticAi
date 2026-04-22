from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class AgentRole:
    name: str
    responsibility: str


AGENT_ROLES = [
    AgentRole("coordinator", "Routes work across scraping, storage, analysis, and memory updates."),
    AgentRole("scraper", "Collects and normalizes IDV player data from configured sources."),
    AgentRole("memory", "Reads memory before work and updates memory after work."),
    AgentRole("analysis", "Interprets collected player data for downstream workflows."),
]


def build_agent_summary() -> list[dict[str, str]]:
    return [asdict(role) for role in AGENT_ROLES]
