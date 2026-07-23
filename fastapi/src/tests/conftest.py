"""
Pytest configuration and fixtures
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.database.session import Base, get_db
from src.main import app


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency"""

    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """Create test client"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def sample_product_data():
    """Sample product data for tests"""
    return {
        "product_code": "TEST001",
        "name": "Test Product",
        "description": "Test Description",
        "category": "Electronics",
        "brand": "TestBrand",
        "barcode": "1234567890",
        "unit_price": "99.99",
        "stock_quantity": 100,
        "is_active": True,
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test1234",
        "full_name": "Test User",
        "role": "user",
    }
