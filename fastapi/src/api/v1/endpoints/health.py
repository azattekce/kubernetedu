"""
Health check endpoints
"""
import asyncio

import structlog
from fastapi import APIRouter, Depends, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from src.api.v1.dependencies import get_database_session
from src.application.schemas.common import HealthCheckResponse
from src.config.settings import get_settings
from src.infrastructure.cache.redis_client import get_redis_client

logger = structlog.get_logger(__name__)
settings = get_settings()

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint
    Returns service status and version
    """
    return HealthCheckResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        checks={},
    )


@router.get(
    "/health/live",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint
    Checks if the application is running
    """
    return HealthCheckResponse(
        status="alive",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        checks={"application": "running"},
    )


@router.get(
    "/health/ready",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
)
async def readiness_probe(
    session: AsyncSession = Depends(get_database_session),
):
    """
    Kubernetes readiness probe endpoint
    Checks if the application is ready to serve traffic
    Validates database and Redis connections
    """
    checks = {}

    # Check database connection
    try:
        result = await asyncio.wait_for(
            session.execute(text("SELECT 1")),
            timeout=settings.HEALTH_CHECK_DB_TIMEOUT,
        )
        checks["database"] = "connected"
        logger.debug("Database health check passed")
    except asyncio.TimeoutError:
        checks["database"] = "timeout"
        logger.error("Database health check timeout")
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        logger.error("Database health check failed", error=str(e))

    # Check Redis connection
    redis_client = get_redis_client()
    try:
        ping_result = await asyncio.wait_for(
            redis_client.ping(),
            timeout=settings.HEALTH_CHECK_REDIS_TIMEOUT,
        )
        checks["redis"] = "connected" if ping_result else "disconnected"
        logger.debug("Redis health check passed")
    except asyncio.TimeoutError:
        checks["redis"] = "timeout"
        logger.warning("Redis health check timeout")
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
        logger.warning("Redis health check failed", error=str(e))

    # Determine overall status
    is_healthy = checks.get("database") == "connected"
    status_value = "ready" if is_healthy else "not_ready"

    response_status = (
        status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return HealthCheckResponse(
        status=status_value,
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        checks=checks,
    )


@router.get("/metrics", include_in_schema=False)
async def metrics():
    """
    Prometheus metrics endpoint
    Exposes application metrics in Prometheus format
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
