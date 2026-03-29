"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "SIDEMA-ML API"
    app_env: str = "development"
    app_debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    max_upload_size_bytes: int = 5 * 1024 * 1024
    allowed_image_mime_types: list[str] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    )
    allowed_image_extensions: list[str] = Field(default_factory=lambda: ["jpg", "jpeg", "png", "webp"])
    min_image_width: int = 128
    min_image_height: int = 128

    blur_score_threshold: float = 35.0
    brightness_min: float = 30.0
    brightness_max: float = 230.0

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_name: str = "sidema-raw"
    minio_public_base_url: str | None = None
    minio_auto_create_bucket: bool = False

    supabase_url: str = ""
    supabase_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_KEY"),
    )
    predictions_table: str = "predictions"

    nail_model_version: str = "nail-mlp-v1"
    nail_threshold: float = 0.255
    nail_mlp_model_path: str = "models/nail/mlp_model.joblib"
    nail_scaler_model_path: str = "models/nail/feature_scaler.joblib"

    conjunctiva_model_version: str = "conjunctiva-mobilenet-v1"
    conjunctiva_threshold: float = 0.5
    conjunctiva_model_path: str = "models/conjunctiva/Model_MobileNet.h5"
    conjunctiva_input_size: int = 224

    allow_threshold_override: bool = True

    @property
    def nail_model_exists(self) -> bool:
        """Return True if nail model artifacts exist on disk."""
        return Path(self.nail_mlp_model_path).exists() and Path(self.nail_scaler_model_path).exists()

    @property
    def conjunctiva_model_exists(self) -> bool:
        """Return True if conjunctiva model artifact exists on disk."""
        return Path(self.conjunctiva_model_path).exists()


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
