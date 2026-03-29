"""Prediction history routes."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_prediction_repository
from app.api.responses import success_response
from app.repositories.predictions import PredictionRepository
from app.schemas.common import SuccessResponse
from app.schemas.history import HistoryItem

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{user_id}", response_model=SuccessResponse)
def get_history(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    repository: PredictionRepository = Depends(get_prediction_repository),
):
    """Return paginated prediction history for a user."""
    records = repository.list_by_user(user_id=user_id, limit=limit, cursor=cursor)
    items = [
        HistoryItem(
            id=record.id,
            user_id=record.user_id,
            method=record.method,
            result_label=record.result_label,
            confidence=record.confidence,
            threshold=record.threshold,
            model_version=record.model_version,
            image_url=record.image_url,
            quality_status=record.quality_status,
            quality_score=record.quality_score,
            created_at=record.created_at,
        ).model_dump(mode="json")
        for record in records
    ]

    next_cursor = items[-1]["created_at"] if len(items) == limit else None
    return success_response(
        data={"items": items, "pagination": {"limit": limit, "next_cursor": next_cursor}},
        message="Prediction history fetched.",
    )


@router.get("/{user_id}/{prediction_id}", response_model=SuccessResponse)
def get_history_detail(
    user_id: str,
    prediction_id: str,
    repository: PredictionRepository = Depends(get_prediction_repository),
):
    """Return a specific prediction history record."""
    record = repository.get_by_user_and_id(user_id=user_id, prediction_id=prediction_id)
    item = HistoryItem(
        id=record.id,
        user_id=record.user_id,
        method=record.method,
        result_label=record.result_label,
        confidence=record.confidence,
        threshold=record.threshold,
        model_version=record.model_version,
        image_url=record.image_url,
        quality_status=record.quality_status,
        quality_score=record.quality_score,
        created_at=record.created_at,
    )
    return success_response(data=item.model_dump(mode="json"), message="Prediction history detail fetched.")
