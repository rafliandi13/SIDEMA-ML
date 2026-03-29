"""Unit tests for image validation service."""

import io

import pytest
from starlette.datastructures import Headers, UploadFile

from app.core.config import Settings
from app.core.exceptions import ValidationException
from app.services.image.validation import ImageValidationService


@pytest.mark.asyncio
async def test_read_and_validate_success(valid_image_bytes):
    settings = Settings(max_upload_size_bytes=2 * 1024 * 1024)
    service = ImageValidationService(settings)

    upload = UploadFile(
        file=io.BytesIO(valid_image_bytes),
        filename="sample.jpg",
        headers=Headers({"content-type": "image/jpeg"}),
    )

    file_bytes, meta = await service.read_and_validate(upload)
    assert len(file_bytes) > 0
    assert meta.mime_type == "image/jpeg"
    assert meta.extension == "jpg"


@pytest.mark.asyncio
async def test_invalid_mime_raises(valid_image_bytes):
    settings = Settings()
    service = ImageValidationService(settings)

    upload = UploadFile(
        file=io.BytesIO(valid_image_bytes),
        filename="sample.jpg",
        headers=Headers({"content-type": "text/plain"}),
    )

    with pytest.raises(ValidationException) as exc:
        await service.read_and_validate(upload)

    assert exc.value.code == "INVALID_MIME_TYPE"


@pytest.mark.asyncio
async def test_file_too_large_raises(valid_image_bytes):
    settings = Settings(max_upload_size_bytes=10)
    service = ImageValidationService(settings)

    upload = UploadFile(
        file=io.BytesIO(valid_image_bytes),
        filename="sample.jpg",
        headers=Headers({"content-type": "image/jpeg"}),
    )

    with pytest.raises(ValidationException) as exc:
        await service.read_and_validate(upload)

    assert exc.value.code == "FILE_TOO_LARGE"
