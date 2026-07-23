# 🚀 Product Management Service - Enterprise FastAPI Microservice

[![CI](https://github.com/yourusername/product-service/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/product-service/actions/workflows/ci.yml)
[![CD](https://github.com/yourusername/product-service/actions/workflows/cd.yml/badge.svg)](https://github.com/yourusername/product-service/actions/workflows/cd.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready, enterprise-grade Product Management microservice built with **FastAPI**, **SQLAlchemy 2.x async**, and designed for **Kubernetes** deployment.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Observability](#-observability)
- [Security](#-security)
- [Contributing](#-contributing)

## ✨ Features

### Core Functionality
- ✅ **CRUD Operations**: Create, Read, Update, Delete products
- ✅ **Soft Delete**: Products can be soft-deleted and restored
- ✅ **Advanced Search**: Full-text search, filtering, sorting, pagination
- ✅ **Stock Management**: Track and update product inventory
- ✅ **Category & Brand**: Organize products by category and brand

### Authentication & Authorization
- ✅ **JWT Authentication**: Stateless token-based auth
- ✅ **Refresh Tokens**: Secure token refresh mechanism
- ✅ **RBAC**: Role-Based Access Control (Admin, Manager, User)
- ✅ **Password Security**: Bcrypt hashing with salt

### API Features
- ✅ **API Versioning**: RESTful API with version support
- ✅ **OpenAPI/Swagger**: Auto-generated API documentation
- ✅ **Request Validation**: Pydantic v2 schemas
- ✅ **Error Handling**: Centralized exception handling
- ✅ **Rate Limiting**: Redis-based rate limiting

### Observability
- ✅ **Structured Logging**: JSON logging with structlog
- ✅ **Distributed Tracing**: OpenTelemetry + Jaeger
- ✅ **Metrics**: Prometheus metrics export
- ✅ **Health Checks**: Liveness and readiness probes

### Cloud-Native
- ✅ **Kubernetes Ready**: Full K8s manifests included
- ✅ **Horizontal Scaling**: HPA with CPU/memory metrics
- ✅ **Graceful Shutdown**: Proper connection cleanup
- ✅ **Configuration Management**: ConfigMaps and Secrets
- ✅ **CI/CD**: GitHub Actions workflows

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│           (FastAPI Routes, Dependencies)                 │
├─────────────────────────────────────────────────────────┤
│                   Application Layer                      │
│        (Services, DTOs, Business Logic)                  │
├─────────────────────────────────────────────────────────┤
│                     Domain Layer                         │
│         (Entities, Value Objects, Interfaces)            │
├─────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                     │
│    (Database, External Services, Cache, Observability)   │
└─────────────────────────────────────────────────────────┘
```

### Design Principles
- **Clean Architecture**: Separation of concerns, dependency inversion
- **Domain-Driven Design**: Rich domain models, repository pattern
- **SOLID Principles**: Maintainable, testable, extensible code
- **Async First**: Async/await throughout the stack
- **12-Factor App**: Configuration, logging, disposability

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.110+ |
| **Language** | Python 3.12+ |
| **Database** | Microsoft SQL Server |
| **ORM** | SQLAlchemy 2.x (async) |
| **Migration** | Alembic |
| **Cache** | Redis |
| **Validation** | Pydantic v2 |
| **Auth** | JWT (python-jose) |
| **Security** | Passlib (bcrypt) |
| **Logging** | Structlog |
| **Tracing** | OpenTelemetry |
| **Metrics** | Prometheus |
| **Container** | Docker |
| **Orchestration** | Kubernetes |
| **CI/CD** | GitHub Actions |
| **Testing** | Pytest, Pytest-asyncio |
| **Code Quality** | Black, Ruff, MyPy, Pre-commit |

## 📁 Project Structure

```
fastapi/
├── src/
│   ├── api/                    # API layer
│   │   └── v1/
│   │       ├── endpoints/      # API endpoints
│   │       ├── dependencies.py # Dependency injection
│   │       └── router.py       # Route aggregation
│   ├── application/            # Application layer
│   │   ├── schemas/            # Pydantic DTOs
│   │   └── services/           # Business logic
│   ├── core/                   # Core utilities
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── middleware.py       # Middleware
│   │   ├── pagination.py       # Pagination utils
│   │   └── security.py         # Auth & security
│   ├── domain/                 # Domain layer
│   │   ├── entities/           # Domain entities
│   │   └── repositories/       # Repository interfaces
│   ├── infrastructure/         # Infrastructure layer
│   │   ├── database/           # Database config & repos
│   │   ├── cache/              # Redis client
│   │   └── observability/      # Telemetry & metrics
│   ├── config/                 # Configuration
│   ├── tests/                  # Tests
│   └── main.py                 # Application entry point
├── k8s/                        # Kubernetes manifests
│   ├── base/                   # Base manifests
│   └── hpa.yaml                # Autoscaling
├── alembic/                    # Database migrations
├── .github/workflows/          # CI/CD pipelines
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Local development
├── pyproject.toml              # Project config
└── requirements.txt            # Dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Microsoft SQL Server (or Docker)
- Redis (or Docker)
- kubectl (for Kubernetes deployment)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/product-service.git
cd product-service/fastapi
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using Poetry
poetry install
```

### 4. Run with Docker Compose

```bash
docker-compose up -d
```

This starts:
- FastAPI application (port 8000)
- MSSQL Server (port 1433)
- Redis (port 6379)
- Jaeger (port 16686)
- Prometheus (port 9090)
- Grafana (port 3000)

### 5. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Create initial admin user (optional)
python scripts/create_admin.py
```

### 6. Access the Application

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **Jaeger UI**: http://localhost:16686
- **Grafana**: http://localhost:3000 (admin/admin)

## 📚 API Documentation

### Authentication

```bash
# Register new user
POST /api/v1/auth/register
{
  "username": "user1",
  "email": "user@example.com",
  "password": "Password123",
  "full_name": "John Doe"
}

# Login
POST /api/v1/auth/login
{
  "username": "user1",
  "password": "Password123"
}

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Product Management

```bash
# List products (with filters)
GET /api/v1/products?page=1&page_size=20&category=Electronics

# Get product by ID
GET /api/v1/products/{product_id}

# Create product (Admin only)
POST /api/v1/products
Authorization: Bearer {access_token}
{
  "product_code": "PROD001",
  "name": "Laptop",
  "description": "High-performance laptop",
  "category": "Electronics",
  "brand": "TechBrand",
  "unit_price": 999.99,
  "stock_quantity": 50
}

# Update product (Admin only)
PUT /api/v1/products/{product_id}
Authorization: Bearer {access_token}
{
  "name": "Updated Laptop",
  "unit_price": 899.99
}

# Delete product (Admin only)
DELETE /api/v1/products/{product_id}
Authorization: Bearer {access_token}

# Restore deleted product (Admin only)
POST /api/v1/products/{product_id}/restore
Authorization: Bearer {access_token}
```

### Complete API documentation available at `/api/v1/docs` (Swagger UI)

## 🛠️ Development

### Set Up Development Environment

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/ --fix

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest src/tests/unit/test_product_service.py

# Run integration tests only
pytest src/tests/integration/

# Run with verbose output
pytest -v
```

### Test Coverage

- Unit Tests: Business logic and services
- Integration Tests: API endpoints
- Target Coverage: >80%

## 🚢 Deployment

### Kubernetes Deployment

```bash
# Apply ConfigMap
kubectl apply -f k8s/base/configmap.yaml

# Apply Secrets (use sealed secrets in production!)
kubectl apply -f k8s/base/secret.yaml

# Apply Deployment
kubectl apply -f k8s/base/deployment.yaml

# Apply Service
kubectl apply -f k8s/base/service.yaml

# Apply Ingress
kubectl apply -f k8s/base/ingress.yaml

# Apply HPA
kubectl apply -f k8s/hpa.yaml

# Check deployment
kubectl get pods
kubectl get services
kubectl logs -f deployment/product-service
```

### Environment-Specific Deployments

```bash
# Development
kubectl apply -k k8s/overlays/dev/

# Production
kubectl apply -k k8s/overlays/prod/
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment product-service --replicas=5

# Check HPA status
kubectl get hpa
kubectl describe hpa product-service-hpa
```

## 📊 Observability

### Logging

Structured JSON logging with correlation IDs:

```json
{
  "timestamp": "2026-07-21T10:30:00.123Z",
  "level": "INFO",
  "service": "product-service",
  "trace_id": "abc123...",
  "user_id": "uuid",
  "method": "POST",
  "path": "/api/v1/products",
  "status_code": 201,
  "duration_ms": 45
}
```

### Metrics (Prometheus)

- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request latency
- `db_query_duration_seconds`: Database query time
- `products_created_total`: Products created counter
- `cache_hits_total` / `cache_misses_total`: Cache metrics

### Tracing (Jaeger)

Distributed tracing for request flow visualization.

## 🔒 Security

### Best Practices Implemented

- ✅ JWT with short-lived access tokens
- ✅ Refresh token rotation
- ✅ Password hashing with bcrypt
- ✅ RBAC authorization
- ✅ SQL injection prevention (parameterized queries)
- ✅ Input validation (Pydantic)
- ✅ CORS configuration
- ✅ Security headers
- ✅ Rate limiting
- ✅ Secrets management (K8s secrets)
- ✅ HTTPS/TLS (via Ingress)

### Production Recommendations

- Use external secret management (Azure Key Vault, AWS Secrets Manager)
- Implement API gateway (rate limiting, throttling)
- Enable WAF (Web Application Firewall)
- Regular security audits
- Dependency scanning
- Container image scanning

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- FastAPI community
- SQLAlchemy team
- Kubernetes ecosystem

---

**Happy Coding!** 🎉

For questions or support, please open an issue or contact the maintainers.
