from app.tasks.celery_app import celery_app
from app.agents.orchestrator import run_task_dict


TASK_NAME = "tasks.run_orchestrated_task"


def _run_task(task_payload: dict) -> dict:
    return run_task_dict(task_payload)


if celery_app is None:
    def run_orchestrated_task(task_payload: dict) -> dict:
        return _run_task(task_payload)
else:
    @celery_app.task(name=TASK_NAME)
    def run_orchestrated_task(task_payload: dict) -> dict:
        return _run_task(task_payload)
