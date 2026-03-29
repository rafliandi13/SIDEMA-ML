"""Image upload validation and quality checks."""

from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import Settings
from app.core.exceptions import ValidationException
from app.schemas.prediction import QualityResult, QualityStatus
from app.utils.file_utils import get_extension


@dataclass
class UploadedImageMeta:
    """Validated uploaded file metadata."""

    filename: str
    mime_type: str
    extension: str
    file_size: int
    width: int
    height: int


class ImageValidationService:
    """Service for file validation and lightweight image quality checks."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def read_and_validate(self, upload: UploadFile) -> tuple[bytes, UploadedImageMeta]:
        """Read upload bytes and validate MIME, size, readability, and dimensions."""
        filename = upload.filename or "uploaded_image"
        mime_type = (upload.content_type or "").lower()
        extension = get_extension(filename)

        if mime_type not in self.settings.allowed_image_mime_types:
            raise ValidationException("Unsupported image MIME type.", code="INVALID_MIME_TYPE")
        if extension not in self.settings.allowed_image_extensions:
            raise ValidationException("Unsupported file extension.", code="INVALID_FILE_EXTENSION")

        file_bytes = await upload.read()
        if not file_bytes:
            raise ValidationException("Uploaded file is empty.", code="EMPTY_FILE")

        file_size = len(file_bytes)
        if file_size > self.settings.max_upload_size_bytes:
            raise ValidationException("Uploaded file exceeds maximum size.", code="FILE_TOO_LARGE")

        width, height = self._validate_readable_and_dimensions(file_bytes)

        return (
            file_bytes,
            UploadedImageMeta(
                filename=filename,
                mime_type=mime_type,
                extension=extension,
                file_size=file_size,
                width=width,
                height=height,
            ),
        )

    def run_quality_checks(self, file_bytes: bytes) -> QualityResult:
        """Run blur and brightness placeholder checks and return quality summary."""
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        array = np.asarray(image, dtype=np.float32)
        grayscale = np.mean(array, axis=2)

        # Placeholder blur heuristic: use gradient std as a simple sharpness proxy.
        vertical_grad = np.diff(grayscale, axis=0)
        blur_score = float(np.std(vertical_grad))
        blur_ok = blur_score >= self.settings.blur_score_threshold

        brightness_score = float(np.mean(grayscale))
        brightness_ok = self.settings.brightness_min <= brightness_score <= self.settings.brightness_max

        quality_score = (float(blur_ok) + float(brightness_ok)) / 2.0
        quality_status = QualityStatus.PASS if quality_score >= 1.0 else QualityStatus.NEEDS_REVIEW

        return QualityResult(
            quality_status=quality_status,
            quality_score=quality_score,
            blur_score=blur_score,
            brightness_score=brightness_score,
        )

    def _validate_readable_and_dimensions(self, file_bytes: bytes) -> tuple[int, int]:
        try:
            with Image.open(io.BytesIO(file_bytes)) as image:
                width, height = image.size
        except UnidentifiedImageError as exc:
            raise ValidationException("Uploaded file is not a readable image.", code="UNREADABLE_IMAGE") from exc

        if width < self.settings.min_image_width or height < self.settings.min_image_height:
            raise ValidationException(
                "Image dimensions are smaller than minimum requirements.",
                code="IMAGE_TOO_SMALL",
            )

        return width, height
