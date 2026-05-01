from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.api.safety_routes import router as safety_router
from app.config import settings
from app.api.task_routes import router as task_router
from app.services.logging_service import configure_logging
from app.services.memory_service import memory_workflow_rule, required_memory_paths

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.pipeline.scheduler import start_scheduler, stop_scheduler
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)
app.include_router(task_router, prefix="/api")
app.include_router(safety_router)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "message": "elitefootball-agenticAi backend scaffold is ready.",
        "memory_rule": memory_workflow_rule(),
        "memory_files": required_memory_paths(),
    }


@app.get("/api/scheduler/status")
def scheduler_status() -> dict:
    from app.pipeline.scheduler import get_scheduler_status
    return get_scheduler_status()


@app.post("/api/scheduler/trigger")
def scheduler_trigger(force_refresh: bool = False) -> dict:
    from app.pipeline.scheduler import trigger_now
    return trigger_now(force_refresh=force_refresh)
