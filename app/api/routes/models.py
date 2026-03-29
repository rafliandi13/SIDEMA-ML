"""Model metadata route."""

from fastapi import APIRouter, Depends

from app.api.deps import get_conjunctiva_inference_service, get_nail_inference_service
from app.api.responses import success_response
from app.schemas.common import SuccessResponse
from app.services.inference.conjunctiva import ConjunctivaInferenceService
from app.services.inference.nail import NailInferenceService

router = APIRouter(tags=["models"])


@router.get("/models/info", response_model=SuccessResponse)
def model_info(
    nail_service: NailInferenceService = Depends(get_nail_inference_service),
    conjunctiva_service: ConjunctivaInferenceService = Depends(get_conjunctiva_inference_service),
):
    """Return readiness and metadata for all configured models."""
    data = {
        "models": [
            nail_service.model_summary().model_dump(mode="json"),
            conjunctiva_service.model_summary().model_dump(mode="json"),
        ]
    }
    return success_response(data=data, message="Model metadata fetched.")
