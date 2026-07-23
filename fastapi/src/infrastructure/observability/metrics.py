"""
Prometheus metrics configuration
"""
from prometheus_client import Counter, Histogram, Gauge
from src.config.settings import get_settings

settings = get_settings()

# HTTP Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# Database metrics
db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
)

db_connection_pool_size = Gauge(
    "db_connection_pool_size",
    "Current database connection pool size",
)

db_connection_pool_active = Gauge(
    "db_connection_pool_active",
    "Number of active database connections",
)

# Cache metrics
cache_hits_total = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["cache_key"],
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["cache_key"],
)

# Business metrics
products_created_total = Counter(
    "products_created_total",
    "Total number of products created",
)

products_updated_total = Counter(
    "products_updated_total",
    "Total number of products updated",
)

products_deleted_total = Counter(
    "products_deleted_total",
    "Total number of products deleted",
)

# Application metrics
active_users_gauge = Gauge(
    "active_users",
    "Number of currently active users",
)

failed_login_attempts_total = Counter(
    "failed_login_attempts_total",
    "Total number of failed login attempts",
)
