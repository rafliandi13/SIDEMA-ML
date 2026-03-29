"""Shared response and error schema models."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error payload details."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standardized API error envelope."""

    success: Literal[False] = False
    error: ErrorDetail


class SuccessResponse(BaseModel):
    """Standardized API success envelope."""

    success: Literal[True] = True
    data: Any
    message: str = "OK"


class HealthData(BaseModel):
    """Health endpoint payload."""

    status: str
    environment: str
    timestamp: datetime


class PaginationMeta(BaseModel):
    """Pagination metadata for list endpoints."""

    limit: int
    next_cursor: str | None = None


class HistoryListData(BaseModel):
    """Paginated history payload."""

    items: list[dict[str, Any]] = Field(default_factory=list)
    pagination: PaginationMeta
