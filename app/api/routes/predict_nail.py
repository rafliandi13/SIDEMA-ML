"""Nail prediction route."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import (
    get_app_settings,
    get_image_validation_service,
    get_nail_inference_service,
    get_prediction_repository,
    get_storage_service,
)
from app.api.responses import success_response
from app.core.config import Settings
from app.core.exceptions import ValidationException
from app.repositories.predictions import PredictionRepository
from app.schemas.common import SuccessResponse
from app.schemas.prediction import PredictionCreate, PredictionMethod, PredictionResponseData
from app.services.image.validation import ImageValidationService
from app.services.inference.nail import NailInferenceService
from app.services.storage.minio_service import MinioStorageService

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/nail", response_model=SuccessResponse)
async def predict_nail(
    user_id: str = Form(...),
    image: UploadFile = File(...),
    threshold: float | None = Form(default=None),
    settings: Settings = Depends(get_app_settings),
    image_service: ImageValidationService = Depends(get_image_validation_service),
    storage_service: MinioStorageService = Depends(get_storage_service),
    inference_service: NailInferenceService = Depends(get_nail_inference_service),
    repository: PredictionRepository = Depends(get_prediction_repository),
):
    """Run nail prediction pipeline and persist metadata."""
    if threshold is not None:
        if not settings.allow_threshold_override:
            raise ValidationException("Threshold override is disabled.", code="THRESHOLD_OVERRIDE_DISABLED")
        if not 0.0 <= threshold <= 1.0:
            raise ValidationException("Threshold must be between 0 and 1.", code="INVALID_THRESHOLD")

    image_bytes, meta = await image_service.read_and_validate(image)
    quality = image_service.run_quality_checks(image_bytes)

    file_key = storage_service.build_object_key(user_id=user_id, method=PredictionMethod.NAIL.value, extension=meta.extension)
    upload_result = storage_service.upload_bytes(image_bytes, file_key, meta.mime_type)

    inference = inference_service.predict(image_bytes=image_bytes, threshold_override=threshold)
    notes = _join_notes(inference.notes, f"blur_score={quality.blur_score:.2f};brightness={quality.brightness_score:.2f}")

    saved = repository.create_prediction(
        PredictionCreate(
            user_id=user_id,
            method=PredictionMethod.NAIL,
            result_label=inference.result_label,
            confidence=inference.confidence,
            threshold=inference.threshold,
            model_version=inference.model_version,
            image_url=upload_result.image_url,
            file_key=upload_result.object_key,
            original_filename=meta.filename,
            mime_type=meta.mime_type,
            file_size=meta.file_size,
            quality_status=quality.quality_status,
            quality_score=quality.quality_score,
            notes=notes,
        )
    )

    payload = PredictionResponseData(
        prediction_id=saved.id,
        user_id=saved.user_id,
        method=saved.method,
        result_label=saved.result_label,
        confidence=saved.confidence,
        threshold=saved.threshold,
        model_version=saved.model_version,
        quality_status=saved.quality_status,
        quality_score=saved.quality_score,
        image_url=saved.image_url,
        created_at=saved.created_at,
    )

    return success_response(data=payload.model_dump(mode="json"), message="Nail prediction completed.")


def _join_notes(first: str | None, second: str | None) -> str | None:
    notes = [part for part in [first, second] if part]
    return " | ".join(notes) if notes else None
