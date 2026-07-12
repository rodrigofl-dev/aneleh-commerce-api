import os

from celery import Celery

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "aneleh_commerce",
    broker=RABBITMQ_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
