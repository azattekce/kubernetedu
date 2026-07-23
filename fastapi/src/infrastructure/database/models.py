"""
SQLAlchemy database models
"""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship

from src.infrastructure.database.session import Base


class ProductModel(Base):
    """Product database model"""

    __tablename__ = "products"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True)
    barcode = Column(String(50), nullable=True)
    unit_price = Column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True)
    updated_by = Column(UNIQUEIDENTIFIER, ForeignKey("users.id"), nullable=True)

    def __repr__(self) -> str:
        return f"<ProductModel(id={self.id}, code={self.product_code}, name={self.name})>"


class UserModel(Base):
    """User database model"""

    __tablename__ = "users"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    role = Column(String(50), nullable=False, default="user", index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    refresh_tokens = relationship("RefreshTokenModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username={self.username}, role={self.role})>"


class RefreshTokenModel(Base):
    """Refresh token database model"""

    __tablename__ = "refresh_tokens"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_revoked = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("UserModel", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshTokenModel(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"
