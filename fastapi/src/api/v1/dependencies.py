"""
API dependencies - dependency injection for FastAPI
"""
from typing import Annotated, List
from uuid import UUID

import structlog
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auth_service import AuthService
from src.application.services.cache_service import CacheService
from src.application.services.product_service import ProductService
from src.core.exceptions import UnauthorizedException
from src.core.security import decode_token
from src.infrastructure.cache.redis_client import get_redis_client
from src.infrastructure.database.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.database.session import get_db

logger = structlog.get_logger(__name__)

# Security
security = HTTPBearer()


# Database dependency
async def get_database_session() -> AsyncSession:
    """Get database session"""
    async for session in get_db():
        yield session


# Repository dependencies
def get_product_repository(
    session: Annotated[AsyncSession, Depends(get_database_session)]
) -> ProductRepositoryImpl:
    """Get product repository"""
    return ProductRepositoryImpl(session)


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_database_session)]
) -> UserRepositoryImpl:
    """Get user repository"""
    return UserRepositoryImpl(session)


# Service dependencies
def get_product_service(
    repository: Annotated[ProductRepositoryImpl, Depends(get_product_repository)]
) -> ProductService:
    """Get product service"""
    return ProductService(repository)


def get_cache_service() -> CacheService:
    """Get cache service"""
    redis_client = get_redis_client()
    return CacheService(redis_client)


def get_auth_service(
    repository: Annotated[UserRepositoryImpl, Depends(get_user_repository)]
) -> AuthService:
    """Get auth service"""
    redis_client = get_redis_client()
    return AuthService(repository, redis_client)


# Authentication dependencies
async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> UUID:
    """
    Get current user ID from JWT token
    Raises:
        HTTPException: If token is invalid
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        return UUID(user_id)

    except JWTError as e:
        logger.error("JWT validation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_role(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """Get current user role from JWT token"""
    try:
        token = credentials.credentials
        payload = decode_token(token)
        role = payload.get("role", "user")
        return role
    except Exception as e:
        logger.error("Role extraction error", error=str(e))
        return "user"


class RoleChecker:
    """Dependency for role-based access control"""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, role: Annotated[str, Depends(get_current_user_role)]) -> str:
        """Check if user has required role"""
        if role not in self.allowed_roles:
            logger.warning("Insufficient permissions", role=role, required=self.allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(self.allowed_roles)}",
            )
        return role


# Role-based dependencies
require_admin = RoleChecker(["admin"])
require_manager = RoleChecker(["admin", "manager"])


# Rate limiting dependency
async def rate_limit_check(
    x_forwarded_for: Annotated[str | None, Header()] = None,
    cache_service: Annotated[CacheService, Depends(get_cache_service)] = None,
) -> None:
    """
    Check rate limit
    Raises:
        HTTPException: If rate limit exceeded
    """
    from src.config.settings import get_settings

    settings = get_settings()

    if not settings.RATE_LIMIT_ENABLED:
        return

    # Get client identifier (IP address)
    identifier = x_forwarded_for or "unknown"

    # Check rate limit
    count = await cache_service.increment_rate_limit(identifier, window=60)

    if count > settings.RATE_LIMIT_PER_MINUTE:
        logger.warning("Rate limit exceeded", identifier=identifier, count=count)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"},
        )
