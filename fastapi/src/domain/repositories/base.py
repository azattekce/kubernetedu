"""
Base repository interface
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository interface for CRUD operations"""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity"""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity"""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Count total entities"""
        pass
