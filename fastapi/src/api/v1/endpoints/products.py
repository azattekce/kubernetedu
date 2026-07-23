"""
Product endpoints
"""
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query, status

from src.api.v1.dependencies import (
    get_current_user_id,
    get_product_service,
    require_admin,
)
from src.application.schemas.common import MessageResponse
from src.application.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductSearchParams,
    ProductUpdate,
    StockUpdateRequest,
)
from src.application.services.product_service import ProductService
from src.core.pagination import PageResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=PageResponse[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="List products",
)
async def list_products(
    query: str | None = Query(None, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    brand: str | None = Query(None, description="Filter by brand"),
    min_price: float | None = Query(None, ge=0, description="Minimum price"),
    max_price: float | None = Query(None, ge=0, description="Maximum price"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    include_deleted: bool = Query(False, description="Include deleted products"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    product_service: Annotated[ProductService, Depends(get_product_service)] = None,
):
    """
    List products with filtering, sorting, and pagination

    **Filters:**
    - query: Search in name, description, and product code
    - category: Filter by category
    - brand: Filter by brand
    - min_price: Minimum price
    - max_price: Maximum price
    - is_active: Filter by active status
    - include_deleted: Include soft deleted products

    **Sorting:**
    - sort_by: Field to sort by (created_at, name, unit_price, etc.)
    - sort_order: asc or desc

    **Pagination:**
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)
    """
    search_params = ProductSearchParams(
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        include_deleted=include_deleted,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    result = await product_service.search_products(search_params)
    logger.debug("Products listed", page=page, total=result.total)
    return result


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by ID",
)
async def get_product(
    product_id: UUID,
    product_service: Annotated[ProductService, Depends(get_product_service)],
):
    """
    Get product details by ID

    - **product_id**: Product UUID
    """
    product = await product_service.get_product(product_id)
    logger.debug("Product retrieved", product_id=product_id)
    return product


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    dependencies=[Depends(require_admin)],
)
async def create_product(
    data: ProductCreate,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
):
    """
    Create a new product

    **Requires admin role**

    - **product_code**: Unique product code
    - **name**: Product name
    - **description**: Product description (optional)
    - **category**: Product category (optional)
    - **brand**: Product brand (optional)
    - **barcode**: Product barcode (optional)
    - **unit_price**: Unit price (must be >= 0)
    - **stock_quantity**: Stock quantity (must be >= 0)
    - **is_active**: Active status (default: true)
    """
    product = await product_service.create_product(data, user_id)
    logger.info(
        "Product created via API",
        product_id=product.id,
        product_code=product.product_code,
        user_id=user_id,
    )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product",
    dependencies=[Depends(require_admin)],
)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
):
    """
    Update product

    **Requires admin role**

    All fields are optional. Only provided fields will be updated.

    - **product_id**: Product UUID
    """
    product = await product_service.update_product(product_id, data, user_id)
    logger.info(
        "Product updated via API",
        product_id=product_id,
        user_id=user_id,
    )
    return product


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Partial update product",
    dependencies=[Depends(require_admin)],
)
async def partial_update_product(
    product_id: UUID,
    data: ProductUpdate,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
):
    """
    Partial update product (same as PUT, for REST compliance)

    **Requires admin role**

    - **product_id**: Product UUID
    """
    product = await product_service.update_product(product_id, data, user_id)
    logger.info(
        "Product partially updated via API",
        product_id=product_id,
        user_id=user_id,
    )
    return product


@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete product (soft delete)",
    dependencies=[Depends(require_admin)],
)
async def delete_product(
    product_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
):
    """
    Soft delete product

    **Requires admin role**

    Product is marked as deleted but not removed from database.
    Can be restored later.

    - **product_id**: Product UUID
    """
    success = await product_service.delete_product(product_id, user_id)

    if success:
        logger.info("Product soft deleted via API", product_id=product_id, user_id=user_id)
        return MessageResponse(message="Product deleted successfully")
    else:
        return MessageResponse(message="Failed to delete product")


@router.post(
    "/{product_id}/restore",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Restore deleted product",
    dependencies=[Depends(require_admin)],
)
async def restore_product(
    product_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
):
    """
    Restore soft deleted product

    **Requires admin role**

    - **product_id**: Product UUID
    """
    product = await product_service.restore_product(product_id, user_id)
    logger.info("Product restored via API", product_id=product_id, user_id=user_id)
    return product


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product stock",
    dependencies=[Depends(require_admin)],
)
async def update_stock(
    product_id: UUID,
    data: StockUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
):
    """
    Update product stock quantity

    **Requires admin role**

    - **product_id**: Product UUID
    - **stock_quantity**: New stock quantity
    """
    product = await product_service.update_stock(product_id, data.stock_quantity, user_id)
    logger.info(
        "Product stock updated via API",
        product_id=product_id,
        quantity=data.stock_quantity,
        user_id=user_id,
    )
    return product


@router.get(
    "/low-stock/alert",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Get low stock products",
    dependencies=[Depends(require_admin)],
)
async def get_low_stock_products(
    threshold: int = Query(10, ge=0, description="Stock quantity threshold"),
    product_service: Annotated[ProductService, Depends(get_product_service)] = None,
):
    """
    Get products with stock below threshold

    **Requires admin role**

    - **threshold**: Stock quantity threshold (default: 10)
    """
    products = await product_service.get_low_stock_products(threshold)
    logger.debug("Low stock products retrieved", count=len(products), threshold=threshold)
    return products
