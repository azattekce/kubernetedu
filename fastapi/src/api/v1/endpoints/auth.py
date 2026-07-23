"""
Authentication endpoints
"""
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, status

from src.api.v1.dependencies import get_auth_service, get_current_user_id
from src.application.schemas.common import MessageResponse
from src.application.schemas.user import (
    PasswordChangeRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from src.application.services.auth_service import AuthService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Register a new user account

    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **full_name**: Optional full name
    - **role**: User role (default: user)
    """
    user = await auth_service.register(data)
    logger.info("User registered via API", user_id=user.id, username=user.username)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
)
async def login(
    data: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    User login with username and password

    Returns JWT access token and refresh token

    - **username**: Username
    - **password**: Password
    """
    tokens = await auth_service.login(data)
    logger.info("User logged in via API", username=data.username)
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh_token(
    data: TokenRefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid refresh token
    """
    tokens = await auth_service.refresh_token(data.refresh_token)
    logger.info("Token refreshed via API")
    return tokens


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
)
async def logout(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    User logout (revoke refresh token)

    Requires authentication
    """
    # In production, you would pass the refresh token to revoke
    await auth_service.logout(user_id, "")
    logger.info("User logged out via API", user_id=user_id)
    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
)
async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Get current authenticated user information

    Requires authentication
    """
    user = await auth_service.get_current_user(user_id)
    return user


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
)
async def change_password(
    data: PasswordChangeRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Change user password

    Requires authentication

    - **current_password**: Current password
    - **new_password**: New password (strong password required)
    """
    success = await auth_service.change_password(
        user_id, data.current_password, data.new_password
    )

    if success:
        logger.info("Password changed via API", user_id=user_id)
        return MessageResponse(message="Password changed successfully")
    else:
        return MessageResponse(message="Failed to change password")
