"""Nail prediction inference service."""

from __future__ import annotations

import io
import logging
from pathlib import Path

import numpy as np
from PIL import Image

from app.core.config import Settings
from app.schemas.prediction import InferenceResult, ModelSummary, PredictionMethod, ResultLabel

logger = logging.getLogger(__name__)


class NailInferenceService:
    """Inference service for nail-based anemia screening."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model = None
        self._scaler = None
        self._load_error: str | None = None
        self._ready = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        model_path = Path(self.settings.nail_mlp_model_path)
        scaler_path = Path(self.settings.nail_scaler_model_path)

        if not model_path.exists() or not scaler_path.exists():
            self._load_error = "Nail model artifacts are missing."
            logger.warning(self._load_error)
            return

        try:
            import joblib

            self._model = joblib.load(model_path)
            self._scaler = joblib.load(scaler_path)
            self._ready = True
        except Exception as exc:  # pragma: no cover - defensive for optional runtime dependency
            self._load_error = f"Failed to load nail model artifacts: {exc}"
            logger.warning(self._load_error)

    def model_summary(self) -> ModelSummary:
        return ModelSummary(
            method=PredictionMethod.NAIL,
            model_version=self.settings.nail_model_version,
            threshold=self.settings.nail_threshold,
            ready=self._ready,
            artifact_path=f"{self.settings.nail_mlp_model_path}, {self.settings.nail_scaler_model_path}",
        )

    def predict(self, image_bytes: bytes, threshold_override: float | None = None) -> InferenceResult:
        threshold = threshold_override if threshold_override is not None else self.settings.nail_threshold

        if self._ready and self._model is not None and self._scaler is not None:
            confidence = self._predict_real(image_bytes)
            notes = None
        else:
            confidence = self._predict_placeholder(image_bytes)
            notes = self._load_error or "Placeholder fallback used for nail inference."

        label = ResultLabel.ANEMIA_SUSPECTED if confidence >= threshold else ResultLabel.NON_ANEMIA

        return InferenceResult(
            method=PredictionMethod.NAIL,
            result_label=label,
            confidence=confidence,
            threshold=threshold,
            model_version=self.settings.nail_model_version,
            notes=notes,
        )

    def _predict_real(self, image_bytes: bytes) -> float:
        features = self._extract_features(image_bytes)
        scaled = self._scaler.transform([features])

        if hasattr(self._model, "predict_proba"):
            probabilities = self._model.predict_proba(scaled)
            confidence = float(probabilities[0][1])
        else:
            prediction = self._model.predict(scaled)
            confidence = float(prediction[0])

        return float(np.clip(confidence, 0.0, 1.0))

    def _predict_placeholder(self, image_bytes: bytes) -> float:
        features = self._extract_features(image_bytes)
        redness = features[8]
        pallor = features[9]
        baseline = 0.45 + (pallor - redness) * 0.35
        return float(np.clip(baseline, 0.0, 1.0))

    def _extract_features(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
        arr = np.asarray(image, dtype=np.float32) / 255.0
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        gray = 0.299 * r + 0.587 * g + 0.114 * b

        features = np.array(
            [
                float(np.mean(r)),
                float(np.mean(g)),
                float(np.mean(b)),
                float(np.std(r)),
                float(np.std(g)),
                float(np.std(b)),
                float(np.mean(gray)),
                float(np.std(gray)),
                float(np.mean(r - g)),
                float(np.mean((g + b) / 2.0 - r)),
                float(np.percentile(gray, 10)),
                float(np.percentile(gray, 90)),
            ],
            dtype=np.float32,
        )
        return features
