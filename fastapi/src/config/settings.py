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
    )

    # Application
    APP_NAME: str = Field(default="Product Management Service")
    APP_VERSION: str = Field(default="1.0.0")
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])
    ALLOWED_HOSTS: List[str] = Field(default=["*"])

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
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"])

    # Observability
    ENABLE_TRACING: bool = Field(default=True)
    ENABLE_METRICS: bool = Field(default=True)
    OTEL_SERVICE_NAME: str = Field(default="product-service")
    OTEL_EXPORTER_JAEGER_ENDPOINT: str = Field(default="http://localhost:14268/api/traces")
    PROMETHEUS_PORT: int = Field(default=9090)

    # Health Check
    HEALTH_CHECK_DB_TIMEOUT: int = Field(default=5)
    HEALTH_CHECK_REDIS_TIMEOUT: int = Field(default=3)

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parse comma-separated origins string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_hosts(cls, v):
        """Parse comma-separated hosts string to list"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [host.strip() for host in v.split(",")]
        return v

    @field_validator("CORS_ALLOW_METHODS", mode="before")
    @classmethod
    def parse_methods(cls, v):
        """Parse comma-separated methods string to list"""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_headers(cls, v):
        """Parse comma-separated headers string to list"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [header.strip() for header in v.split(",")]
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
