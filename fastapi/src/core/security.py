"""
Security utilities: JWT, password hashing, RBAC
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import structlog
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Password hashing context with explicit configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
    bcrypt__ident="2b"  # Use bcrypt version 2b (handles long passwords better)
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    Args:
        password: Plain text password
    Returns:
        str: Hashed password
    """
    # Ensure password is encoded as UTF-8 bytes and check length
    password_bytes = password.encode('utf-8')
    
    if len(password_bytes) > 72:
        logger.warning(
            "Password truncated to 72 bytes for bcrypt",
            original_length=len(password_bytes),
            original_chars=len(password)
        )
        # Truncate bytes, not characters
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully", password_length=len(password))
        return hashed
    except Exception as e:
        logger.error(
            "Password hashing failed",
            error=str(e),
            password_length=len(password),
            exc_info=True
        )
        raise ValueError(f"Password hashing failed: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token
    Args:
        data: Data to encode in the token
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token
    Args:
        token: JWT token string
    Returns:
        Dict: Decoded token payload
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.error("JWT decode error", error=str(e))
        raise


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength
    Args:
        password: Password to validate
    Returns:
        bool: True if password meets requirements
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    return has_upper and has_lower and has_digit
