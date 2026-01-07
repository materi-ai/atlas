# API Service Setup

<Info>
**SDD Classification:** L4-Operational
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

This document provides instructions for setting up the API Service development environment, including prerequisites, configuration, and common workflows.

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Go | 1.25+ | Runtime and build |
| PostgreSQL | 15+ | Primary database |
| Redis | 7+ | Caching and events |
| Docker | 24+ | Container runtime |
| Make | 4+ | Build automation |

### Optional Software

| Software | Version | Purpose |
|----------|---------|---------|
| golangci-lint | 1.55+ | Code linting |
| air | 1.49+ | Hot reload |
| sqlc | 1.24+ | SQL code generation |
| protoc | 3.21+ | Protocol buffers |

---

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/materi/materi.git
cd materi/api

# Install Go dependencies
go mod download

# Copy environment configuration
cp .env.example .env.development
```

### 2. Start Dependencies

```bash
# Using Docker Compose (recommended)
docker-compose up -d postgres redis

# Or using Make from repository root
cd ..
make start-deps
```

### 3. Run Migrations

```bash
# Create database
make db-create ENV=development

# Apply migrations
make migrate-up ENV=development
```

### 4. Start Development Server

```bash
# With hot reload
make dev

# Or without hot reload
make run
```

The API is now available at `http://localhost:8080`.

---

## Project Structure

```
api/
├── cmd/
│   ├── api/
│   │   └── main.go          # Application entry point
│   └── migrate/
│       └── main.go          # Migration tool
├── internal/
│   ├── config/              # Configuration loading
│   ├── controller/          # HTTP handlers
│   ├── middleware/          # HTTP middleware
│   ├── model/               # Domain models
│   ├── repository/          # Data access layer
│   ├── service/             # Business logic
│   ├── infra/               # Infrastructure (DB, Redis)
│   └── wire/                # Dependency injection
├── migrations/              # SQL migration files
├── pkg/                     # Shared utilities
├── test/                    # Test utilities and fixtures
├── .env.example             # Environment template
├── Makefile                 # Build commands
├── go.mod                   # Go dependencies
└── Dockerfile               # Container definition
```

---

## Environment Configuration

### Environment Files

| File | Purpose |
|------|---------|
| `.env.development` | Local development |
| `.env.test` | Test environment |
| `.env.staging` | Staging deployment |
| `.env.production` | Production deployment |

### Required Variables

```bash
# Core Configuration
ENVIRONMENT=development
API_PORT=8080
LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/materi_dev
DATABASE_POOL_SIZE=20
DATABASE_TIMEOUT=30s

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=50

# Authentication
JWT_PUBLIC_KEY_PATH=./certs/jwt.pub
SHIELD_URL=http://localhost:8000
SHIELD_INTERNAL_SECRET=dev-secret

# AI Services (optional for development)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Feature Flags
ENABLE_AI_FEATURES=true
ENABLE_COLLABORATION=true
```

### Secret Management

For production, use environment variables or secret management:

```bash
# Using Kubernetes secrets
kubectl create secret generic api-secrets \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=REDIS_URL='redis://...'

# Using AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id materi/api/prod
```

---

## Database Setup

### Create Development Database

```bash
# Using Make
make db-create ENV=development

# Manually
createdb -h localhost -U postgres materi_dev
```

### Run Migrations

```bash
# Apply all pending migrations
make migrate-up ENV=development

# Rollback last migration
make migrate-down ENV=development

# Check migration status
make migrate-status ENV=development
```

### Create New Migration

```bash
# Create migration files
make migrate-create NAME=add_users_table

# This creates:
# migrations/YYYYMMDDHHMMSS_add_users_table.up.sql
# migrations/YYYYMMDDHHMMSS_add_users_table.down.sql
```

### Seed Test Data

```bash
# Apply seed data
make db-seed ENV=development

# Or run specific seed file
psql -d materi_dev -f seeds/development.sql
```

---

## Development Workflow

### Running the Server

```bash
# Development with hot reload (recommended)
make dev

# Development without hot reload
make run

# Build and run optimized binary
make build && ./bin/api
```

### Code Generation

```bash
# Generate dependency injection code (Wire)
make generate

# Generate SQL query types (sqlc)
make sqlc-generate

# Generate Protocol Buffer types
make proto-generate
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific package tests
go test -v ./internal/service/...

# Run single test
go test -v -run TestDocumentService_Create ./internal/service/
```

### Code Quality

```bash
# Run linter
make lint

# Format code
make format

# Run security scanner
make security
```

---

## IDE Setup

### VS Code

Recommended extensions:
- Go (golang.go)
- Go Test Explorer
- Error Lens

Settings (`.vscode/settings.json`):

```json
{
  "go.useLanguageServer": true,
  "go.lintTool": "golangci-lint",
  "go.lintFlags": ["--fast"],
  "go.formatTool": "goimports",
  "editor.formatOnSave": true,
  "[go]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "go.testFlags": ["-v"],
  "go.coverOnSave": true,
  "go.coverageDecorator": {
    "type": "highlight"
  }
}
```

### GoLand / IntelliJ

1. Enable Go modules: Preferences > Go > Go Modules
2. Configure linter: Preferences > Tools > File Watchers
3. Set test runner: Run > Edit Configurations

---

## Docker Development

### Build Container

```bash
# Build development image
docker build -t materi-api:dev .

# Build with build args
docker build \
  --build-arg VERSION=1.2.3 \
  --build-arg GIT_COMMIT=$(git rev-parse HEAD) \
  -t materi-api:1.2.3 .
```

### Run Container

```bash
# Run with environment file
docker run -p 8080:8080 --env-file .env.development materi-api:dev

# Run with Docker Compose
docker-compose up api
```

### Docker Compose Services

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/materi
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: materi
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## Common Tasks

### Adding a New Endpoint

1. **Define route** in `internal/controller/routes.go`
2. **Create handler** in `internal/controller/`
3. **Add service method** in `internal/service/`
4. **Add repository method** if database access needed
5. **Write tests** for all layers
6. **Update OpenAPI spec** if public endpoint

### Adding a Database Migration

```bash
# Create migration
make migrate-create NAME=add_documents_index

# Edit the generated files
vim migrations/YYYYMMDDHHMMSS_add_documents_index.up.sql
vim migrations/YYYYMMDDHHMMSS_add_documents_index.down.sql

# Test migration
make migrate-up ENV=development
make migrate-down ENV=development
make migrate-up ENV=development
```

### Adding a New Service Dependency

1. Add to `internal/infra/` or `pkg/`
2. Update Wire providers in `internal/wire/`
3. Run `make generate`
4. Update health checks if needed

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U postgres -d materi_dev -c "SELECT 1"

# Check connection pool
make db-pool-status
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping

# Check connection info
redis-cli INFO clients
```

### Build Failures

```bash
# Clean build cache
go clean -cache

# Update dependencies
go mod tidy
go mod download

# Regenerate code
make clean
make generate
```

### Test Failures

```bash
# Run with verbose output
go test -v ./...

# Check test database
make db-test-reset

# Run single test with debug
go test -v -run TestName ./internal/service/ 2>&1 | tee test.log
```

---

## Make Targets Reference

| Target | Description |
|--------|-------------|
| `make build` | Build API binary |
| `make run` | Run API server |
| `make dev` | Run with hot reload |
| `make test` | Run all tests |
| `make test-coverage` | Run tests with coverage |
| `make lint` | Run linter |
| `make format` | Format code |
| `make generate` | Generate code (Wire, sqlc) |
| `make migrate-up` | Apply migrations |
| `make migrate-down` | Rollback migration |
| `make migrate-create` | Create migration files |
| `make db-create` | Create database |
| `make db-reset` | Drop and recreate database |
| `make clean` | Clean build artifacts |
| `make docker-build` | Build Docker image |
| `make security` | Run security scanner |

---

## Related Documentation

- [Overview](overview) - Service overview
- [Architecture](architecture) - System design
- [Testing](testing) - Test strategies
- [Deployment](deployment) - Production deployment

---

**Document Status:** Complete
**Version:** 2.0
