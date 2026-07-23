"""
Product domain entity
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class Product:
    """Product domain entity"""

    def __init__(
        self,
        id: Optional[UUID] = None,
        product_code: str = "",
        name: str = "",
        description: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        barcode: Optional[str] = None,
        unit_price: Decimal = Decimal("0.00"),
        stock_quantity: int = 0,
        is_active: bool = True,
        is_deleted: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
    ):
        self.id = id
        self.product_code = product_code
        self.name = name
        self.description = description
        self.category = category
        self.brand = brand
        self.barcode = barcode
        self.unit_price = unit_price
        self.stock_quantity = stock_quantity
        self.is_active = is_active
        self.is_deleted = is_deleted
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.created_by = created_by
        self.updated_by = updated_by

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, code={self.product_code}, name={self.name})>"

    def mark_as_deleted(self, user_id: UUID) -> None:
        """Soft delete the product"""
        self.is_deleted = True
        self.is_active = False
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()

    def restore(self, user_id: UUID) -> None:
        """Restore soft deleted product"""
        self.is_deleted = False
        self.is_active = True
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()

    def update_stock(self, quantity: int, user_id: UUID) -> None:
        """Update stock quantity"""
        self.stock_quantity = quantity
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()

    def deactivate(self, user_id: UUID) -> None:
        """Deactivate product"""
        self.is_active = False
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()

    def activate(self, user_id: UUID) -> None:
        """Activate product"""
        self.is_active = True
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()
