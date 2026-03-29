"""MinIO object storage service."""

from __future__ import annotations

import io
from dataclasses import dataclass
from uuid import uuid4

from minio import Minio
from minio.error import S3Error

from app.core.config import Settings
from app.core.exceptions import ServiceUnavailableException
from app.utils.datetime_utils import utcnow


@dataclass
class UploadResult:
    """Result of a MinIO upload operation."""

    object_key: str
    image_url: str


class MinioStorageService:
    """Service wrapping MinIO upload and URL generation logic."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.bucket = settings.minio_bucket_name
        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def ensure_bucket_exists(self) -> None:
        """Create bucket if configured and missing."""
        try:
            if not self._client.bucket_exists(self.bucket):
                self._client.make_bucket(self.bucket)
        except S3Error as exc:
            raise ServiceUnavailableException("Failed to verify or create MinIO bucket.") from exc

    def build_object_key(self, user_id: str, method: str, extension: str) -> str:
        """Build object key using required partitioned format."""
        now = utcnow()
        timestamp_uuid = uuid4()
        return f"raw/{user_id}/{method}/{now:%Y}/{now:%m}/{timestamp_uuid}.{extension}"

    def upload_bytes(self, file_bytes: bytes, object_key: str, content_type: str) -> UploadResult:
        """Upload image bytes to MinIO and return object metadata."""
        try:
            stream = io.BytesIO(file_bytes)
            self._client.put_object(
                bucket_name=self.bucket,
                object_name=object_key,
                data=stream,
                length=len(file_bytes),
                content_type=content_type,
            )
        except S3Error as exc:
            raise ServiceUnavailableException("Failed to upload image to MinIO.") from exc

        return UploadResult(object_key=object_key, image_url=self._build_public_url(object_key))

    def _build_public_url(self, object_key: str) -> str:
        if self.settings.minio_public_base_url:
            base = self.settings.minio_public_base_url.rstrip("/")
            return f"{base}/{self.bucket}/{object_key}"
        scheme = "https" if self.settings.minio_secure else "http"
        return f"{scheme}://{self.settings.minio_endpoint}/{self.bucket}/{object_key}"
