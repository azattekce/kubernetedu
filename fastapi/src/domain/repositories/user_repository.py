"""
User repository interface
"""
from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.user import User
from src.domain.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository interface"""

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        pass

    @abstractmethod
    async def update_password(self, user_id: UUID, hashed_password: str) -> bool:
        """Update user password"""
        pass

    @abstractmethod
    async def deactivate(self, user_id: UUID) -> bool:
        """Deactivate user"""
        pass

    @abstractmethod
    async def activate(self, user_id: UUID) -> bool:
        """Activate user"""
        pass
