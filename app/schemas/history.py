"""History endpoint schema models."""

from datetime import datetime

from pydantic import BaseModel

from app.schemas.prediction import PredictionMethod, QualityStatus, ResultLabel


class HistoryItem(BaseModel):
    """History entry payload for list/detail endpoints."""

    id: str
    user_id: str
    method: PredictionMethod
    result_label: ResultLabel
    confidence: float
    threshold: float
    model_version: str
    image_url: str
    quality_status: QualityStatus
    quality_score: float
    created_at: datetime
