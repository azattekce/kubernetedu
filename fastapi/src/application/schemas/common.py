"""
Common schemas for API requests/responses
"""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response"""

    success: bool = Field(default=True)
    message: str = Field(description="Response message")
    data: T = Field(description="Response data")


class ErrorResponse(BaseModel):
    """Error response"""

    success: bool = Field(default=False)
    error_code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: dict = Field(default_factory=dict, description="Additional error details")


class MessageResponse(BaseModel):
    """Simple message response"""

    message: str = Field(description="Response message")


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = Field(description="Health status")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")
    checks: dict = Field(default_factory=dict, description="Individual health checks")
