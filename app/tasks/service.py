from __future__ import annotations

from datetime import datetime
from typing import Any

from app.agents.orchestrator import route_task
from app.tasks.celery_app import celery_app
from app.tasks.jobs import TASK_NAME
from app.tasks.schemas import TaskStatusResponse, TaskSubmissionRequest, TaskSubmissionResponse


class TaskQueueUnavailableError(RuntimeError):
    """Raised when Celery/Redis support is not available in the runtime."""


class TaskSubmissionValidationError(ValueError):
    """Raised when an async task request is invalid."""


def _ensure_queue_available() -> None:
    if celery_app is None:
        raise TaskQueueUnavailableError(
            "Celery is not installed or configured in this environment. Install queue dependencies and start Redis/Celery."
        )


def validate_task_submission(request: TaskSubmissionRequest) -> None:
    if request.schedule_at is not None and request.countdown_seconds is not None:
        raise TaskSubmissionValidationError("Provide either schedule_at or countdown_seconds, not both.")
    route_task(request.task_kind)


def submit_task(request: TaskSubmissionRequest) -> TaskSubmissionResponse:
    validate_task_submission(request)
    _ensure_queue_available()

    send_kwargs: dict[str, Any] = {
        "task_kind": request.task_kind,
        "payload": dict(request.payload),
        "requested_by": request.requested_by,
        "metadata": dict(request.metadata),
    }
    schedule_kwargs: dict[str, Any] = {}
    if request.countdown_seconds is not None:
        schedule_kwargs["countdown"] = request.countdown_seconds
    elif request.schedule_at is not None:
        schedule_kwargs["eta"] = request.schedule_at

    async_result = celery_app.send_task(TASK_NAME, kwargs=send_kwargs, **schedule_kwargs)
    return TaskSubmissionResponse(
        task_id=async_result.id,
        state="PENDING",
        task_kind=request.task_kind,
        route=route_task(request.task_kind),
        scheduled_for=request.schedule_at,
        countdown_seconds=request.countdown_seconds,
    )


def _normalize_success_result(task_id: str, result: dict[str, Any]) -> TaskStatusResponse:
    task_kind = result.get("task_kind") if isinstance(result, dict) else None
    route = result.get("route") if isinstance(result, dict) else None
    return TaskStatusResponse(
        task_id=task_id,
        state="SUCCESS",
        task_kind=task_kind,
        route=route,
        result=result if isinstance(result, dict) else {"value": result},
    )


def get_task_status(task_id: str) -> TaskStatusResponse:
    _ensure_queue_available()
    async_result = celery_app.AsyncResult(task_id)
    state = str(async_result.state or "PENDING")

    if state == "SUCCESS":
        return _normalize_success_result(task_id, async_result.result)

    if state == "FAILURE":
        return TaskStatusResponse(task_id=task_id, state=state, error=str(async_result.result))

    task_kind = None
    route = None
    info = getattr(async_result, "info", None)
    if isinstance(info, dict):
        task_kind = info.get("task_kind")
        if task_kind:
            route = route_task(task_kind)

    return TaskStatusResponse(task_id=task_id, state=state, task_kind=task_kind, route=route)
