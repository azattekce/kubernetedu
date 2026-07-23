"""
Product Management Service - FastAPI Application Entry Point
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.router import api_router
from src.config.logging_config import configure_logging
from src.config.settings import get_settings
from src.core.exceptions import AppException
from src.core.middleware import LoggingMiddleware, RequestIDMiddleware
from src.infrastructure.cache.redis_client import get_redis_client
from src.infrastructure.database.session import close_db, init_db
from src.infrastructure.observability.telemetry import configure_telemetry

# Configure structured logging
configure_logging()
logger = structlog.get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager - handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Product Management Service", version=settings.APP_VERSION)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize Redis
    redis = get_redis_client()
    try:
        await redis.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning("Redis connection failed", error=str(e))

    # Configure telemetry
    if settings.ENABLE_TRACING:
        configure_telemetry()
        logger.info("Telemetry configured")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Product Management Service")

    # Close database connections
    await close_db()
    logger.info("Database connections closed")

    # Close Redis connection
    await redis.close()
    logger.info("Redis connection closed")

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade Product Management Service with FastAPI",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Add custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)


# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """Handle custom application exceptions"""
    logger.error(
        "Application exception",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception("Unexpected exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.DEBUG else None,
        },
    )


# Include routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - service information"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
