"""
Unit tests for ProductService
"""
from decimal import Decimal
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.schemas.product import ProductCreate, ProductUpdate
from src.application.services.product_service import ProductService
from src.core.exceptions import ConflictException, NotFoundException
from src.domain.entities.product import Product


@pytest.fixture
def mock_product_repository():
    """Mock product repository"""
    return AsyncMock()


@pytest.fixture
def product_service(mock_product_repository):
    """Create product service with mocked repository"""
    return ProductService(mock_product_repository)


@pytest.fixture
def sample_product():
    """Sample product entity"""
    return Product(
        id=uuid4(),
        product_code="TEST001",
        name="Test Product",
        description="Test Description",
        category="Electronics",
        brand="TestBrand",
        unit_price=Decimal("99.99"),
        stock_quantity=100,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_create_product_success(product_service, mock_product_repository, sample_product):
    """Test successful product creation"""
    # Arrange
    mock_product_repository.get_by_product_code.return_value = None
    mock_product_repository.create.return_value = sample_product

    data = ProductCreate(
        product_code="TEST001",
        name="Test Product",
        unit_price=Decimal("99.99"),
        stock_quantity=100,
    )
    user_id = uuid4()

    # Act
    result = await product_service.create_product(data, user_id)

    # Assert
    assert result.product_code == "TEST001"
    assert result.name == "Test Product"
    mock_product_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_product_duplicate_code(product_service, mock_product_repository, sample_product):
    """Test product creation with duplicate code"""
    # Arrange
    mock_product_repository.get_by_product_code.return_value = sample_product

    data = ProductCreate(
        product_code="TEST001",
        name="Test Product",
        unit_price=Decimal("99.99"),
    )
    user_id = uuid4()

    # Act & Assert
    with pytest.raises(ConflictException):
        await product_service.create_product(data, user_id)


@pytest.mark.asyncio
async def test_get_product_success(product_service, mock_product_repository, sample_product):
    """Test successful product retrieval"""
    # Arrange
    product_id = sample_product.id
    mock_product_repository.get_by_id.return_value = sample_product

    # Act
    result = await product_service.get_product(product_id)

    # Assert
    assert result.id == product_id
    assert result.product_code == "TEST001"


@pytest.mark.asyncio
async def test_get_product_not_found(product_service, mock_product_repository):
    """Test product retrieval when not found"""
    # Arrange
    product_id = uuid4()
    mock_product_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundException):
        await product_service.get_product(product_id)


@pytest.mark.asyncio
async def test_update_product_success(product_service, mock_product_repository, sample_product):
    """Test successful product update"""
    # Arrange
    product_id = sample_product.id
    mock_product_repository.get_by_id.return_value = sample_product
    mock_product_repository.update.return_value = sample_product

    data = ProductUpdate(name="Updated Product")
    user_id = uuid4()

    # Act
    result = await product_service.update_product(product_id, data, user_id)

    # Assert
    mock_product_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_delete_product_success(product_service, mock_product_repository, sample_product):
    """Test successful product deletion"""
    # Arrange
    product_id = sample_product.id
    mock_product_repository.get_by_id.return_value = sample_product
    mock_product_repository.soft_delete.return_value = True

    user_id = uuid4()

    # Act
    result = await product_service.delete_product(product_id, user_id)

    # Assert
    assert result is True
    mock_product_repository.soft_delete.assert_called_once()
