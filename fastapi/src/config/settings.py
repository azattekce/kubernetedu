"""
Application Configuration Management
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Disable JSON parsing for complex types from env
        env_parse_none_str="null",
    )

    # Application
    APP_NAME: str = Field(default="Product Management Service")
    APP_VERSION: str = Field(default="1.0.0")
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1")
    allowed_origins_str: str = Field(default="*", alias="ALLOWED_ORIGINS")
    allowed_hosts_str: str = Field(default="*", alias="ALLOWED_HOSTS")

    # Database Configuration
    DATABASE_DRIVER: str = Field(default="mssql+aioodbc")
    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=1433)
    DATABASE_NAME: str = Field(default="ProductManagementDB")
    DATABASE_USER: str = Field(default="sa")
    DATABASE_PASSWORD: str = Field(default="")
    DATABASE_ECHO: bool = Field(default=False)
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)
    DATABASE_POOL_TIMEOUT: int = Field(default=30)
    DATABASE_POOL_RECYCLE: int = Field(default=3600)

    # Redis Configuration
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: str = Field(default="")
    REDIS_DECODE_RESPONSES: bool = Field(default=True)
    REDIS_SOCKET_TIMEOUT: int = Field(default=5)
    REDIS_MAX_CONNECTIONS: int = Field(default=50)

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="change-this-secret-key-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Security
    PASSWORD_MIN_LENGTH: int = Field(default=8)
    BCRYPT_ROUNDS: int = Field(default=12)

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_PER_MINUTE: int = Field(default=100)

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    MAX_PAGE_SIZE: int = Field(default=100)

    # CORS
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    cors_allow_methods_str: str = Field(default="*", alias="CORS_ALLOW_METHODS")
    cors_allow_headers_str: str = Field(default="*", alias="CORS_ALLOW_HEADERS")

    # Observability
    ENABLE_TRACING: bool = Field(default=True)
    ENABLE_METRICS: bool = Field(default=True)
    OTEL_SERVICE_NAME: str = Field(default="product-service")
    OTEL_EXPORTER_JAEGER_ENDPOINT: str = Field(default="http://localhost:14268/api/traces")
    PROMETHEUS_PORT: int = Field(default=9090)

    # Health Check
    HEALTH_CHECK_DB_TIMEOUT: int = Field(default=5)
    HEALTH_CHECK_REDIS_TIMEOUT: int = Field(default=3)

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string"""
        if self.allowed_origins_str == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_str.split(",")]

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Parse ALLOWED_HOSTS from comma-separated string"""
        if self.allowed_hosts_str == "*":
            return ["*"]
        return [host.strip() for host in self.allowed_hosts_str.split(",")]

    @property
    def CORS_ALLOW_METHODS(self) -> List[str]:
        """Parse CORS_ALLOW_METHODS from comma-separated string"""
        if self.cors_allow_methods_str == "*":
            return ["*"]
        return [method.strip() for method in self.cors_allow_methods_str.split(",")]

    @property
    def CORS_ALLOW_HEADERS(self) -> List[str]:
        """Parse CORS_ALLOW_HEADERS from comma-separated string"""
        if self.cors_allow_headers_str == "*":
            return ["*"]
        return [header.strip() for header in self.cors_allow_headers_str.split(",")]

    @field_validator("allowed_origins_str", "allowed_hosts_str", "cors_allow_methods_str", "cors_allow_headers_str", mode="before")
    @classmethod
    def validate_string_list(cls, v):
        """Ensure value is string"""
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def DATABASE_URL(self) -> str:
        """Construct database connection URL"""
        if self.DATABASE_DRIVER.startswith("mssql"):
            # For MSSQL with aioodbc
            return (
                f"{self.DATABASE_DRIVER}://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
                f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
            )
        else:
            # Generic format
            return (
                f"{self.DATABASE_DRIVER}://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis connection URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Returns:
        Settings: Application settings
    """
    return Settings()
