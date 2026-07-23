"""
Pagination utilities
"""
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

from src.config.settings import get_settings

settings = get_settings()

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Items per page",
    )

    @property
    def skip(self) -> int:
        """Calculate number of items to skip"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit (same as page_size)"""
        return self.page_size


class PageResponse(BaseModel, Generic[T]):
    """Paginated response model"""

    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int) -> "PageResponse[T]":
        """
        Create paginated response
        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            page_size: Items per page
        Returns:
            PageResponse: Paginated response
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )


class SortParams(BaseModel):
    """Sorting parameters"""

    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", description="Sort order: asc or desc")

    def validate_sort_order(self) -> str:
        """Validate and normalize sort order"""
        return "asc" if self.sort_order.lower() == "asc" else "desc"
