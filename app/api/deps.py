"""Dependency providers for routes."""

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.repositories.predictions import PredictionRepository
from app.services.database.supabase_service import SupabaseService
from app.services.image.validation import ImageValidationService
from app.services.inference.conjunctiva import ConjunctivaInferenceService
from app.services.inference.nail import NailInferenceService
from app.services.storage.minio_service import MinioStorageService


@lru_cache
def _storage_service() -> MinioStorageService:
    return MinioStorageService(get_settings())


@lru_cache
def _supabase_service() -> SupabaseService:
    return SupabaseService(get_settings())


@lru_cache
def _prediction_repository() -> PredictionRepository:
    return PredictionRepository(_supabase_service(), get_settings())


@lru_cache
def _image_validation_service() -> ImageValidationService:
    return ImageValidationService(get_settings())


@lru_cache
def _nail_inference_service() -> NailInferenceService:
    return NailInferenceService(get_settings())


@lru_cache
def _conjunctiva_inference_service() -> ConjunctivaInferenceService:
    return ConjunctivaInferenceService(get_settings())


def get_app_settings() -> Settings:
    return get_settings()


def get_storage_service() -> MinioStorageService:
    return _storage_service()


def get_supabase_service() -> SupabaseService:
    return _supabase_service()


def get_prediction_repository() -> PredictionRepository:
    return _prediction_repository()


def get_image_validation_service() -> ImageValidationService:
    return _image_validation_service()


def get_nail_inference_service() -> NailInferenceService:
    return _nail_inference_service()


def get_conjunctiva_inference_service() -> ConjunctivaInferenceService:
    return _conjunctiva_inference_service()
