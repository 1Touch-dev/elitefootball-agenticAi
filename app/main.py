from fastapi import FastAPI

from app.api.routes import router
from app.api.safety_routes import router as safety_router
from app.config import settings
from app.api.task_routes import router as task_router
from app.services.memory_service import memory_workflow_rule, required_memory_paths

app = FastAPI(title=settings.app_name)
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
