"""
Authentication service - business logic for auth
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import structlog

from src.application.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from src.core.exceptions import ConflictException, UnauthorizedException
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.cache.redis_client import RedisClient
from src.infrastructure.observability.metrics import failed_login_attempts_total

logger = structlog.get_logger(__name__)


class AuthService:
    """Authentication service"""

    def __init__(self, user_repository: UserRepository, redis_client: RedisClient):
        self.user_repository = user_repository
        self.redis_client = redis_client

    def _entity_to_response(self, entity: User) -> UserResponse:
        """Convert entity to response DTO"""
        return UserResponse(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            full_name=entity.full_name,
            role=entity.role,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def register(self, data: UserCreate) -> UserResponse:
        """
        Register new user
        Args:
            data: User registration data
        Returns:
            UserResponse: Created user
        Raises:
            ConflictException: If username or email already exists
        """
        # Check if username exists
        if await self.user_repository.exists_by_username(data.username):
            raise ConflictException(f"Username '{data.username}' already exists")

        # Check if email exists
        if await self.user_repository.exists_by_email(data.email):
            raise ConflictException(f"Email '{data.email}' already exists")

        # Hash password
        hashed_password = hash_password(data.password)

        # Create user entity
        entity = User(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name,
            role=data.role,
        )

        # Save to database
        created = await self.user_repository.create(entity)

        logger.info("User registered", user_id=created.id, username=created.username)

        return self._entity_to_response(created)

    async def login(self, data: UserLogin) -> TokenResponse:
        """
        User login
        Args:
            data: Login credentials
        Returns:
            TokenResponse: Access and refresh tokens
        Raises:
            UnauthorizedException: If credentials are invalid
        """
        # Get user by username
        user = await self.user_repository.get_by_username(data.username)

        if not user or not verify_password(data.password, user.hashed_password):
            failed_login_attempts_total.inc()
            logger.warning("Failed login attempt", username=data.username)
            raise UnauthorizedException("Invalid username or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Store refresh token in Redis
        refresh_token_key = f"refresh_token:{user.id}:{uuid4()}"
        await self.redis_client.set(
            refresh_token_key, refresh_token, expire=7 * 24 * 60 * 60  # 7 days
        )

        logger.info("User logged in", user_id=user.id, username=user.username)

        from src.config.settings import get_settings

        settings = get_settings()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token
        Args:
            refresh_token: Refresh token
        Returns:
            TokenResponse: New access and refresh tokens
        Raises:
            UnauthorizedException: If token is invalid
        """
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")

            user_id = UUID(payload.get("sub"))

            # Get user
            user = await self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise UnauthorizedException("User not found or inactive")

            # Create new tokens
            access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

            # Store new refresh token
            refresh_token_key = f"refresh_token:{user.id}:{uuid4()}"
            await self.redis_client.set(
                refresh_token_key, new_refresh_token, expire=7 * 24 * 60 * 60
            )

            logger.info("Token refreshed", user_id=user.id)

            from src.config.settings import get_settings

            settings = get_settings()

            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except Exception as e:
            logger.error("Token refresh failed", error=str(e))
            raise UnauthorizedException("Invalid or expired refresh token")

    async def logout(self, user_id: UUID, refresh_token: str) -> bool:
        """
        Logout user (revoke refresh token)
        Args:
            user_id: User ID
            refresh_token: Refresh token to revoke
        Returns:
            bool: True if logout successful
        """
        # In a production system, you would maintain a blacklist of revoked tokens
        # For now, we just log the logout
        logger.info("User logged out", user_id=user_id)
        return True

    async def get_current_user(self, user_id: UUID) -> UserResponse:
        """
        Get current user by ID
        Args:
            user_id: User ID
        Returns:
            UserResponse: User details
        Raises:
            UnauthorizedException: If user not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        return self._entity_to_response(user)

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> bool:
        """
        Change user password
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        Returns:
            bool: True if password changed successfully
        Raises:
            UnauthorizedException: If current password is incorrect
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        # Hash new password
        new_hashed_password = hash_password(new_password)

        # Update password
        success = await self.user_repository.update_password(user_id, new_hashed_password)

        if success:
            logger.info("Password changed", user_id=user_id)

        return success
