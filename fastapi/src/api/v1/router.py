"""
API v1 Router - aggregates all endpoint routers
"""
from fastapi import APIRouter

from src.api.v1.endpoints import auth, health, products

# Create main API router
api_router = APIRouter()

# Include health check routes (no prefix)
api_router.include_router(health.router)

# Include authentication routes
api_router.include_router(auth.router)

# Include product routes
api_router.include_router(products.router)
