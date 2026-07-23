"""
User and authentication schemas (DTOs)
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema"""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=200, description="Full name")


class UserCreate(UserBase):
    """User creation schema"""

    password: str = Field(..., min_length=8, description="Password")
    role: str = Field(default="user", description="User role")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """User update schema"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""

    id: UUID = Field(description="User ID")
    role: str = Field(description="User role")
    is_active: bool = Field(description="Active status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login request"""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response"""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration in seconds")


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""

    refresh_token: str = Field(..., description="Refresh token")


class PasswordChangeRequest(BaseModel):
    """Password change request"""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
