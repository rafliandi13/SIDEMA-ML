"""Global exception handlers that enforce API response envelope."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from app.core.exceptions import AppException
from app.schemas.common import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def _error_payload(code: str, message: str) -> dict:
    return ErrorResponse(error=ErrorDetail(code=code, message=message)).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    """Register all application-wide exception handlers."""

    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException: %s - %s", exc.code, exc.message)
        return JSONResponse(status_code=exc.status_code, content=_error_payload(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("RequestValidationError: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload("REQUEST_VALIDATION_ERROR", "Request validation failed."),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("INTERNAL_SERVER_ERROR", "An unexpected error occurred."),
        )
