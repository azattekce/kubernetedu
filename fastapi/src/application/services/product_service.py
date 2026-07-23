"""
Product service - business logic layer
"""
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

import structlog

from src.application.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductSearchParams,
    ProductUpdate,
)
from src.core.exceptions import ConflictException, NotFoundException
from src.core.pagination import PageResponse
from src.domain.entities.product import Product
from src.domain.repositories.product_repository import ProductRepository
from src.infrastructure.observability.metrics import (
    products_created_total,
    products_deleted_total,
    products_updated_total,
)

logger = structlog.get_logger(__name__)


class ProductService:
    """Product service for business logic"""

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def _entity_to_response(self, entity: Product) -> ProductResponse:
        """Convert entity to response DTO"""
        return ProductResponse(
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

    async def create_product(self, data: ProductCreate, user_id: UUID) -> ProductResponse:
        """
        Create new product
        Args:
            data: Product creation data
            user_id: ID of user creating the product
        Returns:
            ProductResponse: Created product
        Raises:
            ConflictException: If product code already exists
        """
        # Check if product code exists
        existing = await self.product_repository.get_by_product_code(data.product_code)
        if existing:
            raise ConflictException(f"Product with code '{data.product_code}' already exists")

        # Create entity
        entity = Product(
            product_code=data.product_code,
            name=data.name,
            description=data.description,
            category=data.category,
            brand=data.brand,
            barcode=data.barcode,
            unit_price=data.unit_price,
            stock_quantity=data.stock_quantity,
            is_active=data.is_active,
            created_by=user_id,
            updated_by=user_id,
        )

        # Save to database
        created = await self.product_repository.create(entity)

        # Update metrics
        products_created_total.inc()

        logger.info(
            "Product created",
            product_id=created.id,
            product_code=created.product_code,
            user_id=user_id,
        )

        return self._entity_to_response(created)

    async def get_product(self, product_id: UUID) -> ProductResponse:
        """
        Get product by ID
        Args:
            product_id: Product ID
        Returns:
            ProductResponse: Product details
        Raises:
            NotFoundException: If product not found
        """
        entity = await self.product_repository.get_by_id(product_id)
        if not entity:
            raise NotFoundException(f"Product with ID '{product_id}' not found")

        return self._entity_to_response(entity)

    async def update_product(
        self, product_id: UUID, data: ProductUpdate, user_id: UUID
    ) -> ProductResponse:
        """
        Update product
        Args:
            product_id: Product ID
            data: Update data
            user_id: ID of user updating the product
        Returns:
            ProductResponse: Updated product
        Raises:
            NotFoundException: If product not found
            ConflictException: If product code already exists
        """
        # Get existing product
        entity = await self.product_repository.get_by_id(product_id)
        if not entity:
            raise NotFoundException(f"Product with ID '{product_id}' not found")

        # Check product code uniqueness if being updated
        if data.product_code and data.product_code != entity.product_code:
            existing = await self.product_repository.get_by_product_code(data.product_code)
            if existing:
                raise ConflictException(f"Product with code '{data.product_code}' already exists")

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)

        entity.updated_by = user_id

        # Save changes
        updated = await self.product_repository.update(entity)

        # Update metrics
        products_updated_total.inc()

        logger.info(
            "Product updated",
            product_id=updated.id,
            product_code=updated.product_code,
            user_id=user_id,
        )

        return self._entity_to_response(updated)

    async def delete_product(self, product_id: UUID, user_id: UUID) -> bool:
        """
        Soft delete product
        Args:
            product_id: Product ID
            user_id: ID of user deleting the product
        Returns:
            bool: True if deleted successfully
        Raises:
            NotFoundException: If product not found
        """
        entity = await self.product_repository.get_by_id(product_id)
        if not entity:
            raise NotFoundException(f"Product with ID '{product_id}' not found")

        success = await self.product_repository.soft_delete(product_id, user_id)

        if success:
            products_deleted_total.inc()
            logger.info("Product soft deleted", product_id=product_id, user_id=user_id)

        return success

    async def restore_product(self, product_id: UUID, user_id: UUID) -> ProductResponse:
        """
        Restore soft deleted product
        Args:
            product_id: Product ID
            user_id: ID of user restoring the product
        Returns:
            ProductResponse: Restored product
        Raises:
            NotFoundException: If product not found
        """
        entity = await self.product_repository.get_by_id(product_id)
        if not entity:
            raise NotFoundException(f"Product with ID '{product_id}' not found")

        success = await self.product_repository.restore(product_id, user_id)
        if not success:
            raise NotFoundException(f"Failed to restore product '{product_id}'")

        # Get updated entity
        restored = await self.product_repository.get_by_id(product_id)
        logger.info("Product restored", product_id=product_id, user_id=user_id)

        return self._entity_to_response(restored)

    async def search_products(self, params: ProductSearchParams) -> PageResponse[ProductResponse]:
        """
        Search products with filters and pagination
        Args:
            params: Search parameters
        Returns:
            PageResponse: Paginated product list
        """
        skip = (params.page - 1) * params.page_size

        items, total = await self.product_repository.search(
            query=params.query,
            category=params.category,
            brand=params.brand,
            min_price=params.min_price,
            max_price=params.max_price,
            is_active=params.is_active,
            include_deleted=params.include_deleted,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            skip=skip,
            limit=params.page_size,
        )

        response_items = [self._entity_to_response(item) for item in items]

        return PageResponse.create(
            items=response_items, total=total, page=params.page, page_size=params.page_size
        )

    async def update_stock(
        self, product_id: UUID, quantity: int, user_id: UUID
    ) -> ProductResponse:
        """
        Update product stock
        Args:
            product_id: Product ID
            quantity: New stock quantity
            user_id: ID of user updating stock
        Returns:
            ProductResponse: Updated product
        Raises:
            NotFoundException: If product not found
        """
        updated = await self.product_repository.update_stock(product_id, quantity, user_id)
        if not updated:
            raise NotFoundException(f"Product with ID '{product_id}' not found")

        logger.info(
            "Product stock updated",
            product_id=product_id,
            quantity=quantity,
            user_id=user_id,
        )

        return self._entity_to_response(updated)

    async def get_low_stock_products(self, threshold: int = 10) -> List[ProductResponse]:
        """
        Get products with low stock
        Args:
            threshold: Stock quantity threshold
        Returns:
            List[ProductResponse]: Products below threshold
        """
        products = await self.product_repository.get_low_stock_products(threshold)
        return [self._entity_to_response(product) for product in products]
