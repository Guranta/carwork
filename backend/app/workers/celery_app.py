from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "carwork",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_acks_late=True,
    worker_prefetch_multiplier=2,
)


@celery_app.task(name="celery.ping")
def ping() -> str:
    return "pong"
