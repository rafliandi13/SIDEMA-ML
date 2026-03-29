"""Inference interfaces and base protocol."""

from __future__ import annotations

from typing import Protocol

from app.schemas.prediction import InferenceResult, ModelSummary


class InferenceService(Protocol):
    """Protocol for method-specific inference service implementations."""

    def model_summary(self) -> ModelSummary:
        """Return model metadata and readiness."""

    def predict(self, image_bytes: bytes, threshold_override: float | None = None) -> InferenceResult:
        """Run inference on image bytes and return prediction result."""
