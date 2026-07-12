from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
import redis

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc),
    }


@router.get("/ready")
def readiness_check():
    checks = {
        "database": _check_database(),
        "redis": _check_redis(),
        "rabbitmq": _check_rabbitmq(),
    }

    all_healthy = all(checks.values())

    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={
            "status": "ok" if all_healthy else "unavailable",
            "checks": checks,
        },
    )


def _check_database() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        return bool(client.ping())
    except Exception:
        return False


def _check_rabbitmq() -> bool:
    try:
        with celery_app.connection() as connection:
            connection.ensure_connection(max_retries=1, timeout=2)
        return True
    except Exception:
        return False
