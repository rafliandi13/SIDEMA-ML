"""Shared test fixtures and dependency overrides."""

from __future__ import annotations

import io
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.api import deps
from app.core.config import Settings
from app.core.exceptions import NotFoundException
from app.main import app
from app.schemas.prediction import (
    InferenceResult,
    ModelSummary,
    PredictionCreate,
    PredictionMethod,
    PredictionRecord,
    QualityStatus,
    ResultLabel,
)
from app.services.image.validation import ImageValidationService
from app.services.storage.minio_service import UploadResult


class FakeStorageService:
    """In-memory stub for MinIO uploads."""

    def build_object_key(self, user_id: str, method: str, extension: str) -> str:
        return f"raw/{user_id}/{method}/2026/03/{uuid4()}.{extension}"

    def upload_bytes(self, file_bytes: bytes, object_key: str, content_type: str) -> UploadResult:
        _ = file_bytes, content_type
        return UploadResult(object_key=object_key, image_url=f"http://example.local/{object_key}")


class FakePredictionRepository:
    """In-memory repository to test API behavior."""

    def __init__(self) -> None:
        self.records: list[PredictionRecord] = []

    def create_prediction(self, payload: PredictionCreate) -> PredictionRecord:
        record = PredictionRecord(
            id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            **payload.model_dump(),
        )
        self.records.append(record)
        return record

    def list_by_user(self, user_id: str, limit: int = 20, cursor: str | None = None) -> list[PredictionRecord]:
        rows = [record for record in self.records if record.user_id == user_id]
        rows.sort(key=lambda item: item.created_at, reverse=True)
        if cursor:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            rows = [record for record in rows if record.created_at < cursor_dt]
        return rows[:limit]

    def get_by_user_and_id(self, user_id: str, prediction_id: str) -> PredictionRecord:
        for record in self.records:
            if record.user_id == user_id and record.id == prediction_id:
                return record
        raise NotFoundException("Prediction history item not found.", code="PREDICTION_NOT_FOUND")


class FakeNailInferenceService:
    """Stub nail inference service."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def model_summary(self) -> ModelSummary:
        return ModelSummary(
            method=PredictionMethod.NAIL,
            model_version=self.settings.nail_model_version,
            threshold=self.settings.nail_threshold,
            ready=True,
            artifact_path="fake/nail",
        )

    def predict(self, image_bytes: bytes, threshold_override: float | None = None) -> InferenceResult:
        _ = image_bytes
        threshold = threshold_override if threshold_override is not None else self.settings.nail_threshold
        confidence = 0.9
        label = ResultLabel.ANEMIA_SUSPECTED if confidence >= threshold else ResultLabel.NON_ANEMIA
        return InferenceResult(
            method=PredictionMethod.NAIL,
            result_label=label,
            confidence=confidence,
            threshold=threshold,
            model_version=self.settings.nail_model_version,
        )


class FakeConjunctivaInferenceService:
    """Stub conjunctiva inference service."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def model_summary(self) -> ModelSummary:
        return ModelSummary(
            method=PredictionMethod.CONJUNCTIVA,
            model_version=self.settings.conjunctiva_model_version,
            threshold=self.settings.conjunctiva_threshold,
            ready=True,
            artifact_path="fake/conjunctiva",
        )

    def predict(self, image_bytes: bytes, threshold_override: float | None = None) -> InferenceResult:
        _ = image_bytes
        threshold = threshold_override if threshold_override is not None else self.settings.conjunctiva_threshold
        confidence = 0.2
        label = ResultLabel.ANEMIA_SUSPECTED if confidence >= threshold else ResultLabel.NON_ANEMIA
        return InferenceResult(
            method=PredictionMethod.CONJUNCTIVA,
            result_label=label,
            confidence=confidence,
            threshold=threshold,
            model_version=self.settings.conjunctiva_model_version,
        )


@pytest.fixture
def settings() -> Settings:
    """Return deterministic test settings."""
    return Settings(
        app_env="test",
        minio_auto_create_bucket=False,
        max_upload_size_bytes=2 * 1024 * 1024,
        nail_threshold=0.255,
        conjunctiva_threshold=0.5,
        allow_threshold_override=True,
    )


@pytest.fixture
def fake_repo() -> FakePredictionRepository:
    return FakePredictionRepository()


@pytest.fixture
def client(settings: Settings, fake_repo: FakePredictionRepository) -> TestClient:
    """Return FastAPI test client with mocked dependencies."""
    image_service = ImageValidationService(settings)
    storage = FakeStorageService()
    nail = FakeNailInferenceService(settings)
    conjunctiva = FakeConjunctivaInferenceService(settings)

    app.dependency_overrides[deps.get_app_settings] = lambda: settings
    app.dependency_overrides[deps.get_image_validation_service] = lambda: image_service
    app.dependency_overrides[deps.get_storage_service] = lambda: storage
    app.dependency_overrides[deps.get_prediction_repository] = lambda: fake_repo
    app.dependency_overrides[deps.get_nail_inference_service] = lambda: nail
    app.dependency_overrides[deps.get_conjunctiva_inference_service] = lambda: conjunctiva

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def valid_image_bytes() -> bytes:
    """Build an in-memory RGB image for upload tests."""
    img = Image.new("RGB", (256, 256), color=(200, 120, 120))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def sample_quality_status() -> QualityStatus:
    return QualityStatus.PASS
