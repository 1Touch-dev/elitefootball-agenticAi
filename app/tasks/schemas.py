from pydantic import BaseModel
from typing import Optional, Any


class TaskSubmissionRequest(BaseModel):
    task_kind: str
    payload: dict[str, Any] = {}
    requested_by: Optional[str] = None
    schedule_at: Optional[str] = None
    countdown_seconds: Optional[int] = None


class TaskSubmissionResponse(BaseModel):
    task_id: str
    state: str
    task_kind: str
    route: list[str]
    scheduled_for: Optional[str] = None
    countdown_seconds: Optional[int] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    state: str
    task_kind: Optional[str] = None
    route: Optional[list[str]] = None
    result: Optional[Any] = None
    error: Optional[str] = None
