"""FastAPI application bootstrap."""

import logging

from fastapi import FastAPI

from app.api.deps import get_app_settings, get_storage_service
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.models import router as models_router
from app.api.routes.predict_conjunctiva import router as predict_conjunctiva_router
from app.api.routes.predict_nail import router as predict_nail_router
from app.core.handlers import register_exception_handlers
from app.core.logging import configure_logging

settings = get_app_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, debug=settings.app_debug)
register_exception_handlers(app)

app.include_router(health_router)
app.include_router(models_router)
app.include_router(predict_nail_router)
app.include_router(predict_conjunctiva_router)
app.include_router(history_router)


@app.on_event("startup")
def startup_event() -> None:
    """Initialize infrastructure dependencies."""
    storage = get_storage_service()
    if settings.minio_auto_create_bucket:
        try:
            storage.ensure_bucket_exists()
            logger.info("MinIO bucket is ready: %s", settings.minio_bucket_name)
        except Exception as exc:  # pragma: no cover - startup resilience
            logger.warning("MinIO bucket check failed: %s", exc)


@app.get("/")
def root() -> dict:
    """Simple root endpoint for quick sanity checks."""
    return {"service": settings.app_name, "status": "running"}
