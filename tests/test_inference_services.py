"""Unit tests for inference service fallback behavior."""

from app.core.config import Settings
from app.schemas.prediction import PredictionMethod
from app.services.inference.conjunctiva import ConjunctivaInferenceService
from app.services.inference.nail import NailInferenceService


def test_nail_inference_fallback(valid_image_bytes):
    settings = Settings(
        nail_mlp_model_path="/tmp/not-found-mlp.joblib",
        nail_scaler_model_path="/tmp/not-found-scaler.joblib",
    )
    service = NailInferenceService(settings)

    summary = service.model_summary()
    assert summary.ready is False

    result = service.predict(valid_image_bytes)
    assert result.method == PredictionMethod.NAIL
    assert 0.0 <= result.confidence <= 1.0


def test_conjunctiva_inference_fallback(valid_image_bytes):
    settings = Settings(conjunctiva_model_path="/tmp/not-found-conjunctiva.h5")
    service = ConjunctivaInferenceService(settings)

    summary = service.model_summary()
    assert summary.ready is False

    result = service.predict(valid_image_bytes)
    assert result.method == PredictionMethod.CONJUNCTIVA
    assert 0.0 <= result.confidence <= 1.0
