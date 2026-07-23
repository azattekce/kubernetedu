"""
Product repository interface
"""
from abc import abstractmethod
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.domain.entities.product import Product
from src.domain.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Product repository interface"""

    @abstractmethod
    async def get_by_product_code(self, product_code: str) -> Optional[Product]:
        """Get product by product code"""
        pass

    @abstractmethod
    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get product by barcode"""
        pass

    @abstractmethod
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
        """
        Search products with filters
        Returns: (list of products, total count)
        """
        pass

    @abstractmethod
    async def soft_delete(self, id: UUID, user_id: UUID) -> bool:
        """Soft delete product"""
        pass

    @abstractmethod
    async def restore(self, id: UUID, user_id: UUID) -> bool:
        """Restore soft deleted product"""
        pass

    @abstractmethod
    async def update_stock(self, id: UUID, quantity: int, user_id: UUID) -> Optional[Product]:
        """Update product stock quantity"""
        pass

    @abstractmethod
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get products by category"""
        pass

    @abstractmethod
    async def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        """Get products with stock below threshold"""
        pass
