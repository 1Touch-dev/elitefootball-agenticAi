from app.tasks.celery_app import celery_app
from app.agents.orchestrator import run_task_dict


@celery_app.task(name='tasks.run_orchestrated_task')
def run_orchestrated_task(task_payload: dict) -> dict:
    """
    Execute the orchestrated task.

    :param task_payload: serialized task input
    :return: serialized task result
    """
    return run_task_dict(task_payload)
