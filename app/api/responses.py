"""Response helper functions for standardized API envelopes."""

from typing import Any

from fastapi.responses import JSONResponse

from app.schemas.common import SuccessResponse


def success_response(data: Any, message: str = "OK", status_code: int = 200) -> JSONResponse:
    """Build a standardized success response envelope."""
    payload = SuccessResponse(data=data, message=message).model_dump(mode="json")
    return JSONResponse(status_code=status_code, content=payload)
