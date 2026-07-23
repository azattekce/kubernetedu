"""
User repository implementation
"""
from typing import List, Optional
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models import UserModel

logger = structlog.get_logger(__name__)


class UserRepositoryImpl(UserRepository):
    """User repository implementation with SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity"""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: User) -> UserModel:
        """Convert domain entity to database model"""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            role=entity.role,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        result = await self.session.execute(select(UserModel).offset(skip).limit(limit))
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.role == role).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        result = await self.session.execute(
            select(func.count(UserModel.id)).where(UserModel.username == username)
        )
        count = result.scalar_one()
        return count > 0

    async def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        result = await self.session.execute(
            select(func.count(UserModel.id)).where(UserModel.email == email)
        )
        count = result.scalar_one()
        return count > 0

    async def create(self, entity: User) -> User:
        """Create new user"""
        model = self._entity_to_model(entity)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        logger.info("User created", user_id=model.id, username=model.username)
        return self._model_to_entity(model)

    async def update(self, entity: User) -> User:
        """Update existing user"""
        model = await self.session.get(UserModel, entity.id)
        if not model:
            raise ValueError(f"User with ID {entity.id} not found")

        # Update fields
        model.username = entity.username
        model.email = entity.email
        model.hashed_password = entity.hashed_password
        model.full_name = entity.full_name
        model.role = entity.role
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        logger.info("User updated", user_id=model.id, username=model.username)
        return self._model_to_entity(model)

    async def update_password(self, user_id: UUID, hashed_password: str) -> bool:
        """Update user password"""
        model = await self.session.get(UserModel, user_id)
        if not model:
            return False

        model.hashed_password = hashed_password
        await self.session.flush()
        logger.info("User password updated", user_id=user_id)
        return True

    async def deactivate(self, user_id: UUID) -> bool:
        """Deactivate user"""
        model = await self.session.get(UserModel, user_id)
        if not model:
            return False

        model.is_active = False
        await self.session.flush()
        logger.info("User deactivated", user_id=user_id)
        return True

    async def activate(self, user_id: UUID) -> bool:
        """Activate user"""
        model = await self.session.get(UserModel, user_id)
        if not model:
            return False

        model.is_active = True
        await self.session.flush()
        logger.info("User activated", user_id=user_id)
        return True

    async def delete(self, id: UUID) -> bool:
        """Delete user"""
        model = await self.session.get(UserModel, id)
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        logger.info("User deleted", user_id=id)
        return True

    async def count(self) -> int:
        """Count total users"""
        result = await self.session.execute(select(func.count(UserModel.id)))
        return result.scalar_one()
