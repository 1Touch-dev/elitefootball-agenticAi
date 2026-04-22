try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - depends on optional runtime dependency
    Celery = None


if Celery is None:
    celery_app = None
else:
    celery_app = Celery(
        "tasks",
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/0",
    )

    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )
