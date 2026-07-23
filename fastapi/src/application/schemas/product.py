"""
Product schemas (DTOs)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    """Base product schema"""

    product_code: str = Field(..., min_length=1, max_length=50, description="Unique product code")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    brand: Optional[str] = Field(None, max_length=100, description="Product brand")
    barcode: Optional[str] = Field(None, max_length=50, description="Product barcode")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    stock_quantity: int = Field(default=0, ge=0, description="Stock quantity")
    is_active: bool = Field(default=True, description="Active status")

    @field_validator("unit_price")
    @classmethod
    def validate_price(cls, v):
        """Validate price has max 2 decimal places"""
        if v.as_tuple().exponent < -2:
            raise ValueError("Price can have at most 2 decimal places")
        return v


class ProductCreate(ProductBase):
    """Product creation schema"""

    pass


class ProductUpdate(BaseModel):
    """Product update schema - all fields optional"""

    product_code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response schema"""

    id: UUID = Field(description="Product ID")
    is_deleted: bool = Field(description="Soft delete status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    created_by: Optional[UUID] = Field(None, description="Creator user ID")
    updated_by: Optional[UUID] = Field(None, description="Last updater user ID")

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Product list response with pagination"""

    items: list[ProductResponse] = Field(description="List of products")
    total: int = Field(description="Total number of products")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")


class ProductSearchParams(BaseModel):
    """Product search parameters"""

    query: Optional[str] = Field(None, description="Search query (name, description, code)")
    category: Optional[str] = Field(None, description="Filter by category")
    brand: Optional[str] = Field(None, description="Filter by brand")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    include_deleted: bool = Field(default=False, description="Include soft deleted products")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class StockUpdateRequest(BaseModel):
    """Stock update request"""

    stock_quantity: int = Field(..., ge=0, description="New stock quantity")
