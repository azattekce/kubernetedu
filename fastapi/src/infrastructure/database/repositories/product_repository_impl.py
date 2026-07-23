"""
Product repository implementation
"""
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

import structlog
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.product import Product
from src.domain.repositories.product_repository import ProductRepository
from src.infrastructure.database.models import ProductModel

logger = structlog.get_logger(__name__)


class ProductRepositoryImpl(ProductRepository):
    """Product repository implementation with SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: ProductModel) -> Product:
        """Convert database model to domain entity"""
        return Product(
            id=model.id,
            product_code=model.product_code,
            name=model.name,
            description=model.description,
            category=model.category,
            brand=model.brand,
            barcode=model.barcode,
            unit_price=model.unit_price,
            stock_quantity=model.stock_quantity,
            is_active=model.is_active,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convert domain entity to database model"""
        return ProductModel(
            id=entity.id,
            product_code=entity.product_code,
            name=entity.name,
            description=entity.description,
            category=entity.category,
            brand=entity.brand,
            barcode=entity.barcode,
            unit_price=entity.unit_price,
            stock_quantity=entity.stock_quantity,
            is_active=entity.is_active,
            is_deleted=entity.is_deleted,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
        )

    async def get_by_id(self, id: UUID) -> Optional[Product]:
        """Get product by ID"""
        result = await self.session.execute(select(ProductModel).where(ProductModel.id == id))
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_product_code(self, product_code: str) -> Optional[Product]:
        """Get product by product code"""
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.product_code == product_code)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get product by barcode"""
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.barcode == barcode)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        result = await self.session.execute(
            select(ProductModel)
            .where(ProductModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_active: Optional[bool] = None,
        include_deleted: bool = False,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Product], int]:
        """Search products with filters"""
        # Build base query
        conditions = []

        if not include_deleted:
            conditions.append(ProductModel.is_deleted == False)

        if query:
            search_pattern = f"%{query}%"
            conditions.append(
                or_(
                    ProductModel.name.ilike(search_pattern),
                    ProductModel.description.ilike(search_pattern),
                    ProductModel.product_code.ilike(search_pattern),
                )
            )

        if category:
            conditions.append(ProductModel.category == category)

        if brand:
            conditions.append(ProductModel.brand == brand)

        if min_price is not None:
            conditions.append(ProductModel.unit_price >= min_price)

        if max_price is not None:
            conditions.append(ProductModel.unit_price <= max_price)

        if is_active is not None:
            conditions.append(ProductModel.is_active == is_active)

        # Count total
        count_query = select(func.count(ProductModel.id)).where(and_(*conditions))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Get items
        sort_column = getattr(ProductModel, sort_by, ProductModel.created_at)
        sort_func = desc if sort_order == "desc" else asc

        items_query = (
            select(ProductModel)
            .where(and_(*conditions))
            .order_by(sort_func(sort_column))
            .offset(skip)
            .limit(limit)
        )

        items_result = await self.session.execute(items_query)
        models = items_result.scalars().all()
        items = [self._model_to_entity(model) for model in models]

        return items, total

    async def create(self, entity: Product) -> Product:
        """Create new product"""
        model = self._entity_to_model(entity)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        logger.info("Product created", product_id=model.id, product_code=model.product_code)
        return self._model_to_entity(model)

    async def update(self, entity: Product) -> Product:
        """Update existing product"""
        model = await self.session.get(ProductModel, entity.id)
        if not model:
            raise ValueError(f"Product with ID {entity.id} not found")

        # Update fields
        model.product_code = entity.product_code
        model.name = entity.name
        model.description = entity.description
        model.category = entity.category
        model.brand = entity.brand
        model.barcode = entity.barcode
        model.unit_price = entity.unit_price
        model.stock_quantity = entity.stock_quantity
        model.is_active = entity.is_active
        model.is_deleted = entity.is_deleted
        model.updated_at = entity.updated_at
        model.updated_by = entity.updated_by

        await self.session.flush()
        await self.session.refresh(model)
        logger.info("Product updated", product_id=model.id, product_code=model.product_code)
        return self._model_to_entity(model)

    async def delete(self, id: UUID) -> bool:
        """Hard delete product"""
        model = await self.session.get(ProductModel, id)
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        logger.info("Product deleted", product_id=id)
        return True

    async def soft_delete(self, id: UUID, user_id: UUID) -> bool:
        """Soft delete product"""
        model = await self.session.get(ProductModel, id)
        if not model:
            return False

        model.is_deleted = True
        model.is_active = False
        model.updated_by = user_id
        await self.session.flush()
        logger.info("Product soft deleted", product_id=id)
        return True

    async def restore(self, id: UUID, user_id: UUID) -> bool:
        """Restore soft deleted product"""
        model = await self.session.get(ProductModel, id)
        if not model:
            return False

        model.is_deleted = False
        model.is_active = True
        model.updated_by = user_id
        await self.session.flush()
        logger.info("Product restored", product_id=id)
        return True

    async def update_stock(self, id: UUID, quantity: int, user_id: UUID) -> Optional[Product]:
        """Update product stock quantity"""
        model = await self.session.get(ProductModel, id)
        if not model:
            return None

        model.stock_quantity = quantity
        model.updated_by = user_id
        await self.session.flush()
        await self.session.refresh(model)
        logger.info("Product stock updated", product_id=id, quantity=quantity)
        return self._model_to_entity(model)

    async def get_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Get products by category"""
        result = await self.session.execute(
            select(ProductModel)
            .where(
                and_(
                    ProductModel.category == category,
                    ProductModel.is_deleted == False,
                )
            )
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        """Get products with stock below threshold"""
        result = await self.session.execute(
            select(ProductModel).where(
                and_(
                    ProductModel.stock_quantity <= threshold,
                    ProductModel.is_deleted == False,
                    ProductModel.is_active == True,
                )
            )
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def count(self) -> int:
        """Count total products (non-deleted)"""
        result = await self.session.execute(
            select(func.count(ProductModel.id)).where(ProductModel.is_deleted == False)
        )
        return result.scalar_one()
