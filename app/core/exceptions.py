"""Custom domain exceptions for API error mapping."""


class AppException(Exception):
    """Base API exception with HTTP status mapping."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ValidationException(AppException):
    """Raised when a request payload is invalid."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(code=code, message=message, status_code=422)


class NotFoundException(AppException):
    """Raised when a requested resource cannot be found."""

    def __init__(self, message: str, code: str = "NOT_FOUND") -> None:
        super().__init__(code=code, message=message, status_code=404)


class ServiceUnavailableException(AppException):
    """Raised when an infrastructure dependency is unavailable."""

    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE") -> None:
        super().__init__(code=code, message=message, status_code=503)
