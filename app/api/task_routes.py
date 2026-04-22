from fastapi import APIRouter, HTTPException

from app.tasks.jobs import run_orchestrated_task
from app.tasks.service import submit_task, get_task_status, TaskQueueUnavailableError
from app.tasks.schemas import TaskSubmissionRequest, TaskSubmissionResponse, TaskStatusResponse

router = APIRouter()


@router.post("/tasks", response_model=TaskSubmissionResponse)
def create_task(request: TaskSubmissionRequest) -> TaskSubmissionResponse:
    try:
        return submit_task(request)
    except TaskQueueUnavailableError:
        raise HTTPException(status_code=503, detail="Task queue is unavailable. Make sure Celery and Redis are running.")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def read_task(task_id: str) -> TaskStatusResponse:
    return get_task_status(task_id)
