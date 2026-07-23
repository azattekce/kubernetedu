"""
Custom exception classes
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception"""

    def __init__(
        self,
        message: str,
        error_code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Validation error exception"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code="VALIDATION_ERROR", status_code=400, details=details
        )


class NotFoundException(AppException):
    """Resource not found exception"""

    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message, error_code="NOT_FOUND", status_code=404, details=details
        )


class UnauthorizedException(AppException):
    """Unauthorized access exception"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, error_code="UNAUTHORIZED", status_code=401)


class ForbiddenException(AppException):
    """Forbidden access exception"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, error_code="FORBIDDEN", status_code=403)


class ConflictException(AppException):
    """Resource conflict exception"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="CONFLICT", status_code=409, details=details)


class DatabaseException(AppException):
    """Database operation exception"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code="DATABASE_ERROR", status_code=500, details=details
        )


class CacheException(AppException):
    """Cache operation exception"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, error_code="CACHE_ERROR", status_code=500, details=details
        )
