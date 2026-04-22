from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskSubmissionRequest(BaseModel):
    task_kind: str
    payload: dict[str, Any] = Field(default_factory=dict)
    requested_by: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    schedule_at: Optional[datetime] = None
    countdown_seconds: Optional[int] = None


class TaskSubmissionResponse(BaseModel):
    task_id: str
    state: str
    task_kind: str
    route: list[str]
    scheduled_for: Optional[datetime] = None
    countdown_seconds: Optional[int] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    state: str
    task_kind: Optional[str] = None
    route: Optional[list[str]] = None
    result: Optional[Any] = None
    error: Optional[str] = None
