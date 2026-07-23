"""
User domain entity
"""
from datetime import datetime
from typing import Optional
from uuid import UUID


class User:
    """User domain entity"""

    def __init__(
        self,
        id: Optional[UUID] = None,
        username: str = "",
        email: str = "",
        hashed_password: str = "",
        full_name: Optional[str] = None,
        role: str = "user",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == "admin"

    def is_manager(self) -> bool:
        """Check if user is manager"""
        return self.role in ["admin", "manager"]

    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return self.role == role

    def deactivate(self) -> None:
        """Deactivate user"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate user"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
