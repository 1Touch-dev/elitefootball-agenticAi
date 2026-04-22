from fastapi import FastAPI

from app.api.routes import router
from app.config import settings
from app.services.memory_service import memory_workflow_rule, required_memory_paths

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "message": "elitefootball-agenticAi backend scaffold is ready.",
        "memory_rule": memory_workflow_rule(),
        "memory_files": required_memory_paths(),
    }
