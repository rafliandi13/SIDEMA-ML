"""Unit tests for MinIO object key generation."""

import re

from app.core.config import Settings
from app.services.storage.minio_service import MinioStorageService


def test_build_object_key_format():
    service = MinioStorageService(Settings())
    key = service.build_object_key(user_id="user-1", method="nail", extension="jpg")

    pattern = r"^raw/user-1/nail/\d{4}/\d{2}/[a-f0-9-]{36}\.jpg$"
    assert re.match(pattern, key)
