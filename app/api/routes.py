from fastapi import APIRouter

from app.agents.orchestrator import build_agent_summary
from app.scraping.players import get_idv_player_scrape_plan

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/summary")
def summary() -> dict[str, object]:
    return {
        "project": "elitefootball-agenticAi",
        "mvp_scope": "IDV players",
        "agents": build_agent_summary(),
        "scraping": get_idv_player_scrape_plan(),
    }
