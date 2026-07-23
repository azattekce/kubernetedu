"""
Integration tests for product endpoints
"""
import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(async_client):
    """Test health check endpoint"""
    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_product_unauthorized(async_client, sample_product_data):
    """Test create product without authentication"""
    response = await async_client.post("/api/v1/products", json=sample_product_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_list_products(async_client):
    """Test list products endpoint"""
    response = await async_client.get("/api/v1/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
