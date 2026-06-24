from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut, tags=["system"])
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        app=settings.app_name,
        env=settings.app_env,
        version="0.1.0",
        timestamp=datetime.now(UTC),
    )
