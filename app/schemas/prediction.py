"""Prediction domain schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PredictionMethod(str, Enum):
    """Supported inference pipelines."""

    NAIL = "nail"
    CONJUNCTIVA = "conjunctiva"


class ResultLabel(str, Enum):
    """Binary anemia screening labels."""

    ANEMIA_SUSPECTED = "anemia_suspected"
    NON_ANEMIA = "non_anemia"


class QualityStatus(str, Enum):
    """Image quality status after checks."""

    PASS = "pass"
    NEEDS_REVIEW = "needs_review"


class ModelSummary(BaseModel):
    """Metadata returned by /models/info."""

    method: PredictionMethod
    model_version: str
    threshold: float
    ready: bool
    artifact_path: str


class InferenceResult(BaseModel):
    """Raw inference result from model services."""

    method: PredictionMethod
    result_label: ResultLabel
    confidence: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(ge=0.0, le=1.0)
    model_version: str
    notes: str | None = None


class QualityResult(BaseModel):
    """Quality check output used in responses and persistence."""

    quality_status: QualityStatus
    quality_score: float = Field(ge=0.0, le=1.0)
    blur_score: float
    brightness_score: float


class PredictionResponseData(BaseModel):
    """Prediction endpoint response payload."""

    prediction_id: str
    user_id: str
    method: PredictionMethod
    result_label: ResultLabel
    confidence: float
    threshold: float
    model_version: str
    quality_status: QualityStatus
    quality_score: float
    image_url: str
    created_at: datetime


class PredictionCreate(BaseModel):
    """Record payload inserted into persistence layer."""

    user_id: str
    method: PredictionMethod
    result_label: ResultLabel
    confidence: float
    threshold: float
    model_version: str
    image_url: str
    file_key: str
    original_filename: str
    mime_type: str
    file_size: int
    quality_status: QualityStatus
    quality_score: float
    notes: str | None = None


class PredictionRecord(PredictionCreate):
    """Persisted prediction row schema."""

    id: str
    created_at: datetime
