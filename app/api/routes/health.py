"""Health check route."""

from fastapi import APIRouter, Depends

from app.api.deps import get_app_settings, get_supabase_service
from app.api.responses import success_response
from app.core.config import Settings
from app.schemas.common import HealthData, SuccessResponse
from app.services.database.supabase_service import SupabaseService
from app.utils.datetime_utils import utcnow

router = APIRouter(tags=["system"])


@router.get("/health", response_model=SuccessResponse)
def health(
    settings: Settings = Depends(get_app_settings),
    supabase_service: SupabaseService = Depends(get_supabase_service),
):
    """Application health endpoint for probes."""
    data = {
        **HealthData(status="ok", environment=settings.app_env, timestamp=utcnow()).model_dump(mode="json"),
        "services": {
            "minio_endpoint": settings.minio_endpoint,
            "supabase_configured": supabase_service.is_configured,
        },
    }
    return success_response(data=data, message="Service is healthy.")
