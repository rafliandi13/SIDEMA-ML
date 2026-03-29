"""Conjunctiva prediction inference service."""

from __future__ import annotations

import io
import logging
from pathlib import Path

import numpy as np
from PIL import Image

from app.core.config import Settings
from app.schemas.prediction import InferenceResult, ModelSummary, PredictionMethod, ResultLabel

logger = logging.getLogger(__name__)


class ConjunctivaInferenceService:
    """Inference service for conjunctiva-based anemia screening."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model = None
        self._load_error: str | None = None
        self._ready = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        model_path = Path(self.settings.conjunctiva_model_path)
        if not model_path.exists():
            self._load_error = "Conjunctiva model artifact is missing."
            logger.warning(self._load_error)
            return

        try:
            import tensorflow as tf

            self._model = tf.keras.models.load_model(str(model_path))
            self._ready = True
        except Exception as exc:  # pragma: no cover - defensive for optional runtime dependency
            self._load_error = f"Failed to load conjunctiva model artifact: {exc}"
            logger.warning(self._load_error)

    def model_summary(self) -> ModelSummary:
        return ModelSummary(
            method=PredictionMethod.CONJUNCTIVA,
            model_version=self.settings.conjunctiva_model_version,
            threshold=self.settings.conjunctiva_threshold,
            ready=self._ready,
            artifact_path=self.settings.conjunctiva_model_path,
        )

    def predict(self, image_bytes: bytes, threshold_override: float | None = None) -> InferenceResult:
        threshold = threshold_override if threshold_override is not None else self.settings.conjunctiva_threshold

        if self._ready and self._model is not None:
            confidence = self._predict_real(image_bytes)
            notes = None
        else:
            confidence = self._predict_placeholder(image_bytes)
            notes = self._load_error or "Placeholder fallback used for conjunctiva inference."

        label = ResultLabel.ANEMIA_SUSPECTED if confidence >= threshold else ResultLabel.NON_ANEMIA

        return InferenceResult(
            method=PredictionMethod.CONJUNCTIVA,
            result_label=label,
            confidence=confidence,
            threshold=threshold,
            model_version=self.settings.conjunctiva_model_version,
            notes=notes,
        )

    def _predict_real(self, image_bytes: bytes) -> float:
        input_tensor = self._prepare_input(image_bytes)
        raw_output = self._model.predict(input_tensor, verbose=0)
        confidence = float(np.asarray(raw_output).reshape(-1)[0])
        return float(np.clip(confidence, 0.0, 1.0))

    def _predict_placeholder(self, image_bytes: bytes) -> float:
        input_tensor = self._prepare_input(image_bytes)
        image = input_tensor[0]
        redness = float(np.mean(image[:, :, 0]))
        brightness = float(np.mean(image))
        score = 0.35 + redness * 0.45 - brightness * 0.15
        return float(np.clip(score, 0.0, 1.0))

    def _prepare_input(self, image_bytes: bytes) -> np.ndarray:
        size = self.settings.conjunctiva_input_size
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((size, size))
        arr = np.asarray(image, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)
