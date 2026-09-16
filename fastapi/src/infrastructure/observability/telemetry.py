"""
OpenTelemetry configuration for distributed tracing
"""
import structlog
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


def configure_telemetry() -> None:
    """Configure OpenTelemetry for distributed tracing"""
    try:
        # Create resource
        resource = Resource(
            attributes={
                "service.name": settings.OTEL_SERVICE_NAME,
                "service.version": settings.APP_VERSION,
                "deployment.environment": settings.APP_ENV,
            }
        )

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            collector_endpoint=settings.OTEL_EXPORTER_JAEGER_ENDPOINT
        )

        # Add span processor
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        logger.info(
            "OpenTelemetry configured",
            service_name=settings.OTEL_SERVICE_NAME,
            jaeger_endpoint=settings.OTEL_EXPORTER_JAEGER_ENDPOINT,
        )

    except Exception as e:
        logger.error("Failed to configure OpenTelemetry", error=str(e))


def instrument_app(app) -> None:
    """Attach OpenTelemetry auto-instrumentation to the FastAPI app so requests emit spans"""
    FastAPIInstrumentor.instrument_app(app)


def instrument_sqlalchemy(engine) -> None:
    """Attach OpenTelemetry instrumentation to the SQLAlchemy engine so DB queries emit spans"""
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


def instrument_redis() -> None:
    """Attach OpenTelemetry instrumentation to redis-py so cache calls emit spans"""
    RedisInstrumentor().instrument()


def shutdown_telemetry() -> None:
    """Flush buffered spans and shut down the tracer provider on app exit"""
    provider = trace.get_tracer_provider()
    force_flush = getattr(provider, "force_flush", None)
    if force_flush:
        force_flush()
    shutdown = getattr(provider, "shutdown", None)
    if shutdown:
        shutdown()


def get_tracer(name: str):
    """Get tracer instance"""
    return trace.get_tracer(name)
