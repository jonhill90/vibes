# Docker Compose Configuration

**Task 7 - Docker Compose Setup**
**Date**: 2025-10-11
**Pattern**: Production-ready multi-service Docker Compose with health checks
**References**:
- Qdrant documentation: https://qdrant.tech/documentation/guides/installation/
- PostgreSQL Docker Hub: https://hub.docker.com/_/postgres
- Task 1: Qdrant vector database selection
- Task 2: PostgreSQL schema design
- Task 6: Service layer connection pooling

---

## Overview

The RAG service deployment uses **Docker Compose** to orchestrate four services:

1. **PostgreSQL** (15-alpine): Document metadata, chunks, sources
2. **Qdrant**: Vector storage and similarity search
3. **FastAPI Backend**: REST API and service layer
4. **Frontend** (Optional): React/Vue UI for document management

This configuration provides:
- **Local development** with hot reload and debug logging
- **Production deployment** with health checks and resource limits
- **Data persistence** with named volumes
- **Service dependencies** with health-based startup ordering
- **Environment-based configuration** with .env file

---

## 1. PostgreSQL Service

### Service Definition

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: rag_postgres
    restart: unless-stopped

    ports:
      - "5432:5432"

    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-rag_service}
      # Performance tuning
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=C"

    volumes:
      # Data persistence
      - postgres_data:/var/lib/postgresql/data
      # Optional: Schema initialization
      - ./backend/sql/init.sql:/docker-entrypoint-initdb.d/01_init.sql:ro
      # Optional: Sample data
      - ./backend/sql/seed.sql:/docker-entrypoint-initdb.d/02_seed.sql:ro

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

    networks:
      - rag_network
```

### Key Features

**Health Check**:
- `pg_isready`: Checks if PostgreSQL accepts connections
- `interval: 10s`: Check every 10 seconds
- `start_period: 10s`: Allow 10 seconds for initial startup
- Backend service waits for `healthy` status before starting

**Volume Mounting**:
- `postgres_data`: Persistent storage for database files
- `init.sql`: Runs on first container creation (schema setup)
- `seed.sql`: Optional sample data for development

**Performance Configuration**:
- `UTF8` encoding for full Unicode support
- `C` locale for faster text operations
- Alpine image for smaller size (40MB vs 130MB)

### PostgreSQL Configuration File (Optional)

For production tuning, mount custom `postgresql.conf`:

```yaml
volumes:
  - ./backend/config/postgresql.conf:/etc/postgresql/postgresql.conf:ro

command:
  - postgres
  - -c
  - config_file=/etc/postgresql/postgresql.conf
```

**Example postgresql.conf**:
```conf
# Connection settings
max_connections = 100
shared_buffers = 256MB

# Query performance
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB

# Logging
log_statement = 'all'  # Development only
log_duration = on

# Full-text search
default_text_search_config = 'pg_catalog.english'
```

---

## 2. Qdrant Service

### Service Definition

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: rag_qdrant
    restart: unless-stopped

    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC API

    environment:
      # Optional: API key for production
      QDRANT__SERVICE__API_KEY: ${QDRANT_API_KEY:-}
      # Performance settings
      QDRANT__SERVICE__MAX_REQUEST_SIZE_MB: 32
      QDRANT__SERVICE__GRPC_PORT: 6334
      QDRANT__SERVICE__HTTP_PORT: 6333

    volumes:
      # CRITICAL: :z flag for SELinux compatibility
      - qdrant_data:/qdrant/storage:z
      # Optional: Custom configuration
      - ./backend/config/qdrant.yaml:/qdrant/config/production.yaml:ro

    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:6333/healthz || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s

    networks:
      - rag_network
```

### Key Features

**Health Check**:
- `/healthz` endpoint: Qdrant health status
- `start_period: 15s`: Allow time for index loading
- Backend waits for `healthy` before connecting

**Volume Mounting**:
- `qdrant_data:/qdrant/storage:z`: Persistent vector storage
- `:z` flag: SELinux compatibility (required on RHEL/CentOS)

**API Configuration**:
- Port 6333: REST API (used by Python client)
- Port 6334: gRPC API (optional, faster but requires gRPC client)
- `QDRANT__SERVICE__API_KEY`: Optional authentication

**Memory Considerations**:
- 1M vectors (1536 dim) ≈ 6GB RAM
- 10M vectors ≈ 60GB RAM
- Adjust host resources accordingly

### Qdrant Configuration File (Optional)

**qdrant.yaml**:
```yaml
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334

  # Enable API key authentication
  api_key: ${QDRANT_API_KEY}

storage:
  # Storage configuration
  storage_path: /qdrant/storage

  # Performance tuning
  performance:
    max_search_threads: 0  # Auto-detect CPU cores

  # Indexing settings
  hnsw_index:
    m: 16              # Number of edges per node (higher = better recall)
    ef_construct: 100  # Construction quality (higher = slower insert, better search)

cluster:
  # Single-node configuration
  enabled: false
```

---

## 3. FastAPI Backend Service

### Service Definition

```yaml
services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: ${BUILD_TARGET:-development}
    container_name: rag_api
    restart: unless-stopped

    ports:
      - "8000:8000"

    environment:
      # Database connection
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@postgres:5432/${POSTGRES_DB:-rag_service}

      # Qdrant connection
      QDRANT_URL: http://qdrant:6333
      QDRANT_API_KEY: ${QDRANT_API_KEY:-}
      QDRANT_COLLECTION: ${QDRANT_COLLECTION:-documents}
      QDRANT_DIMENSION: ${QDRANT_DIMENSION:-1536}

      # OpenAI API
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_MODEL: ${OPENAI_MODEL:-text-embedding-3-small}

      # Application settings
      ENVIRONMENT: ${ENVIRONMENT:-development}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      DEBUG: ${DEBUG:-false}

      # Connection pool settings (from Task 6)
      DB_POOL_MIN_SIZE: ${DB_POOL_MIN_SIZE:-10}
      DB_POOL_MAX_SIZE: ${DB_POOL_MAX_SIZE:-20}

      # CORS settings
      CORS_ORIGINS: ${CORS_ORIGINS:-http://localhost:3000,http://localhost:8000}

    volumes:
      # Hot reload in development
      - ./backend/src:/app/src:ro
      # Logs
      - ./logs:/app/logs

    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy

    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

    networks:
      - rag_network

    command: >
      uvicorn main:app
      --host 0.0.0.0
      --port 8000
      --reload
      --log-level ${LOG_LEVEL:-info}
```

### Multi-Stage Dockerfile

**backend/Dockerfile**:
```dockerfile
# Stage 1: Base dependencies
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development
FROM base as development

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Development command (overridden by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]

# Stage 3: Production
FROM base as production

# Copy source code only (no dev tools)
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Production command (no reload)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "4"]
```

### Backend Requirements

**requirements.txt**:
```txt
# FastAPI
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
asyncpg==0.29.0
psycopg2-binary==2.9.9

# Vector database
qdrant-client==1.7.0

# Embeddings
openai==1.3.5

# Utilities
python-multipart==0.0.6
python-dotenv==1.0.0
httpx==0.25.2
```

**requirements-dev.txt**:
```txt
# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Code quality
ruff==0.1.6
mypy==1.7.1
black==23.11.0

# Debugging
ipython==8.18.1
```

### Key Features

**Depends On with Health Checks**:
```yaml
depends_on:
  postgres:
    condition: service_healthy  # Wait for pg_isready
  qdrant:
    condition: service_healthy  # Wait for /healthz
```

**Hot Reload in Development**:
```yaml
volumes:
  - ./backend/src:/app/src:ro  # Mount source code
command: uvicorn main:app --reload  # Auto-restart on changes
```

**Health Endpoint**:
Backend should expose `/health` endpoint:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {
        "status": "healthy",
        "services": {
            "postgres": await check_postgres_health(),
            "qdrant": await check_qdrant_health(),
        }
    }
```

---

## 4. Frontend Service (Optional)

### Service Definition

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: ${BUILD_TARGET:-development}
    container_name: rag_frontend
    restart: unless-stopped

    ports:
      - "3000:3000"

    environment:
      # API endpoint
      VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
      # Environment
      NODE_ENV: ${NODE_ENV:-development}

    volumes:
      # Hot reload in development
      - ./frontend/src:/app/src:ro
      - ./frontend/public:/app/public:ro
      # Exclude node_modules (use container's version)
      - /app/node_modules

    depends_on:
      - api

    networks:
      - rag_network

    command: npm run dev
```

### Frontend Dockerfile

**frontend/Dockerfile**:
```dockerfile
# Stage 1: Development
FROM node:20-alpine as development

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Development command (overridden by docker-compose)
CMD ["npm", "run", "dev"]

# Stage 2: Build
FROM node:20-alpine as build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Stage 3: Production
FROM nginx:alpine as production

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 5. Complete docker-compose.yml

### Development Configuration

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: rag_postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-rag_service}
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/sql/init.sql:/docker-entrypoint-initdb.d/01_init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - rag_network

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: rag_qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    environment:
      QDRANT__SERVICE__API_KEY: ${QDRANT_API_KEY:-}
      QDRANT__SERVICE__MAX_REQUEST_SIZE_MB: 32
    volumes:
      - qdrant_data:/qdrant/storage:z
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:6333/healthz || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    networks:
      - rag_network

  # FastAPI Backend
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    container_name: rag_api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      # Database
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@postgres:5432/${POSTGRES_DB:-rag_service}
      DB_POOL_MIN_SIZE: ${DB_POOL_MIN_SIZE:-10}
      DB_POOL_MAX_SIZE: ${DB_POOL_MAX_SIZE:-20}

      # Qdrant
      QDRANT_URL: http://qdrant:6333
      QDRANT_API_KEY: ${QDRANT_API_KEY:-}
      QDRANT_COLLECTION: ${QDRANT_COLLECTION:-documents}
      QDRANT_DIMENSION: ${QDRANT_DIMENSION:-1536}

      # OpenAI
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_MODEL: ${OPENAI_MODEL:-text-embedding-3-small}

      # Application
      ENVIRONMENT: development
      LOG_LEVEL: DEBUG
      DEBUG: true
      CORS_ORIGINS: http://localhost:3000,http://localhost:8000
    volumes:
      - ./backend/src:/app/src:ro
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - rag_network
    command: >
      uvicorn main:app
      --host 0.0.0.0
      --port 8000
      --reload
      --log-level debug

  # Frontend (Optional)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    container_name: rag_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
      NODE_ENV: development
    volumes:
      - ./frontend/src:/app/src:ro
      - ./frontend/public:/app/public:ro
      - /app/node_modules
    depends_on:
      - api
    networks:
      - rag_network
    command: npm run dev

# Persistent volumes
volumes:
  postgres_data:
    driver: local
  qdrant_data:
    driver: local

# Network
networks:
  rag_network:
    driver: bridge
```

---

## 6. Production Configuration

### Production Overrides

**docker-compose.prod.yml**:
```yaml
version: '3.8'

services:
  postgres:
    environment:
      # Production database name
      POSTGRES_DB: rag_service_prod
    # Remove port exposure (internal only)
    ports: []
    # Add resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  qdrant:
    # Require API key in production
    environment:
      QDRANT__SERVICE__API_KEY: ${QDRANT_API_KEY}
    # Remove port exposure (internal only)
    ports: []
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

  api:
    build:
      target: production
    environment:
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      DEBUG: false
      # Stricter CORS
      CORS_ORIGINS: https://yourdomain.com
    # Multiple workers in production
    command: >
      uvicorn main:app
      --host 0.0.0.0
      --port 8000
      --workers 4
      --log-level info
    # Remove source mounting
    volumes:
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  frontend:
    build:
      target: production
    ports:
      - "80:80"
    environment:
      NODE_ENV: production
    # No source mounting in production
    volumes: []
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Running in Production

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f api

# Stop services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

---

## 7. Environment Variables

### Complete .env.example

```bash
#############################################
# PostgreSQL Configuration
#############################################
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=rag_service

# Connection Pool (from Task 6 service layer)
DB_POOL_MIN_SIZE=10
DB_POOL_MAX_SIZE=20

#############################################
# Qdrant Configuration
#############################################
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=your_qdrant_api_key_here  # Optional, recommended for production
QDRANT_COLLECTION=documents
QDRANT_DIMENSION=1536  # text-embedding-3-small dimension

#############################################
# OpenAI Configuration
#############################################
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=text-embedding-3-small

#############################################
# Application Configuration
#############################################
ENVIRONMENT=development  # development, staging, production
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR
DEBUG=false

#############################################
# CORS Configuration
#############################################
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

#############################################
# Frontend Configuration
#############################################
VITE_API_URL=http://localhost:8000
NODE_ENV=development

#############################################
# Docker Build Configuration
#############################################
BUILD_TARGET=development  # development, production

#############################################
# Resource Limits (Production)
#############################################
# These are used in docker-compose.prod.yml
POSTGRES_MEMORY_LIMIT=2G
POSTGRES_CPU_LIMIT=2
QDRANT_MEMORY_LIMIT=8G
QDRANT_CPU_LIMIT=4
API_MEMORY_LIMIT=2G
API_CPU_LIMIT=2
```

### Environment Setup

```bash
# Copy example to .env
cp .env.example .env

# Edit with your values
nano .env

# IMPORTANT: Never commit .env to version control
echo ".env" >> .gitignore
```

---

## 8. Usage Guide

### Development Workflow

```bash
# 1. Initial setup
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 2. Start all services
docker-compose up -d

# 3. View logs
docker-compose logs -f api

# 4. Check service health
docker-compose ps

# 5. Initialize database (first time)
docker-compose exec api python scripts/init_db.py

# 6. Run database migrations
docker-compose exec api alembic upgrade head

# 7. Access services
# - Backend API: http://localhost:8000/docs
# - Frontend: http://localhost:3000
# - Qdrant Dashboard: http://localhost:6333/dashboard

# 8. Stop services
docker-compose down

# 9. Remove volumes (reset everything)
docker-compose down -v
```

### Testing Changes

```bash
# Rebuild specific service
docker-compose build api

# Restart specific service
docker-compose restart api

# View service logs
docker-compose logs -f api

# Execute commands in container
docker-compose exec api bash
docker-compose exec postgres psql -U postgres -d rag_service
```

### Database Management

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d rag_service

# Backup database
docker-compose exec postgres pg_dump -U postgres rag_service > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres -d rag_service < backup.sql

# Check database size
docker-compose exec postgres psql -U postgres -d rag_service -c "SELECT pg_size_pretty(pg_database_size('rag_service'));"
```

### Qdrant Management

```bash
# Access Qdrant CLI
docker-compose exec qdrant sh

# Check collection stats
curl http://localhost:6333/collections/documents

# Delete collection (careful!)
curl -X DELETE http://localhost:6333/collections/documents
```

---

## 9. Monitoring & Debugging

### Health Checks

```bash
# Check all service health
docker-compose ps

# Expected output:
# NAME           STATUS
# rag_postgres   Up (healthy)
# rag_qdrant     Up (healthy)
# rag_api        Up (healthy)
# rag_frontend   Up
```

### Service-Specific Health

```bash
# PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# Qdrant
curl http://localhost:6333/healthz

# Backend API
curl http://localhost:8000/health
```

### Log Aggregation

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api

# Filter by time
docker-compose logs --since 1h api
```

### Resource Usage

```bash
# Container resource usage
docker stats

# Example output:
# CONTAINER     CPU %   MEM USAGE / LIMIT     NET I/O
# rag_postgres  5%      200MiB / 2GiB         10MB / 5MB
# rag_qdrant    20%     4GiB / 8GiB           50MB / 30MB
# rag_api       10%     500MiB / 2GiB         5MB / 10MB
```

### Troubleshooting

**Service won't start**:
```bash
# Check logs
docker-compose logs service_name

# Rebuild image
docker-compose build service_name

# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

**Database connection issues**:
```bash
# Verify DATABASE_URL
docker-compose exec api env | grep DATABASE_URL

# Test connection from API container
docker-compose exec api python -c "import asyncpg; print('Test')"
```

**Qdrant connection issues**:
```bash
# Verify Qdrant is healthy
docker-compose ps qdrant

# Test from API container
docker-compose exec api curl http://qdrant:6333/healthz
```

---

## 10. Production Deployment Checklist

### Pre-Deployment

- [ ] **Environment Variables**:
  - [ ] Set strong `POSTGRES_PASSWORD`
  - [ ] Set `QDRANT_API_KEY` for authentication
  - [ ] Set `OPENAI_API_KEY` with sufficient quota
  - [ ] Set `ENVIRONMENT=production`
  - [ ] Set `DEBUG=false`
  - [ ] Configure production `CORS_ORIGINS`

- [ ] **Resource Limits**:
  - [ ] Define CPU/memory limits for all services
  - [ ] Size Qdrant memory based on vector count (6GB per 1M vectors)
  - [ ] Size PostgreSQL based on expected data volume

- [ ] **Security**:
  - [ ] Don't expose database ports externally
  - [ ] Use API key authentication for Qdrant
  - [ ] Use HTTPS for frontend (reverse proxy)
  - [ ] Restrict CORS to specific domains

- [ ] **Backups**:
  - [ ] Set up automated PostgreSQL backups
  - [ ] Set up automated Qdrant volume backups
  - [ ] Test restore procedures

- [ ] **Monitoring**:
  - [ ] Set up log aggregation (ELK, Grafana Loki)
  - [ ] Configure alerting for service health
  - [ ] Monitor resource usage trends

### Deployment Commands

```bash
# 1. Copy production environment
cp .env.example .env.production
# Edit with production values

# 2. Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Verify health
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# 5. Initialize database
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec api python scripts/init_db.py

# 6. Monitor logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

---

## 11. Scaling Considerations

### Horizontal Scaling (Multiple API Instances)

```yaml
services:
  api:
    deploy:
      replicas: 3  # Run 3 API containers
    # ... rest of config
```

**Load Balancer Required**:
- Use nginx, Traefik, or cloud load balancer
- Distribute requests across API replicas
- Health check endpoints for automatic failover

### Vertical Scaling (Resource Allocation)

**PostgreSQL**:
- 4GB RAM: ~10K documents, moderate traffic
- 8GB RAM: ~100K documents, high traffic
- 16GB RAM: ~1M documents, very high traffic

**Qdrant**:
- 2GB RAM: ~300K vectors (1536 dim)
- 8GB RAM: ~1.3M vectors
- 32GB RAM: ~5M vectors

**API Backend**:
- 1GB RAM: Development, light traffic
- 2GB RAM: Production, moderate traffic
- 4GB RAM: Production, high traffic

### Database Optimization

**PostgreSQL**:
```yaml
environment:
  # Increase connection limit
  POSTGRES_MAX_CONNECTIONS: 200
  # Tune shared buffers (25% of RAM)
  POSTGRES_SHARED_BUFFERS: 2GB
```

**Qdrant**:
```yaml
environment:
  # Enable quantization for memory savings
  QDRANT__SERVICE__ENABLE_QUANTIZATION: true
  # Adjust HNSW parameters
  QDRANT__SERVICE__HNSW_EF: 128
```

---

## 12. Integration with Task 2 (Schema)

### Schema Initialization

**backend/sql/init.sql** (from Task 2):
```sql
-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL DEFAULT 'text',
    url TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    metadata JSONB DEFAULT '{}'::jsonb,
    search_vector tsvector,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    text TEXT NOT NULL,
    token_count INT,
    search_vector tsvector,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT NOT NULL CHECK (source_type IN ('upload', 'crawl', 'api')),
    url TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Crawl jobs table
CREATE TABLE IF NOT EXISTS crawl_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    pages_crawled INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes (from Task 2)
CREATE INDEX IF NOT EXISTS idx_documents_source_id ON documents(source_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_search_vector ON documents USING GIN(search_vector);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_search_vector ON chunks USING GIN(search_vector);

CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(status);
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);

CREATE INDEX IF NOT EXISTS idx_crawl_jobs_source_id ON crawl_jobs(source_id);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status ON crawl_jobs(status);

-- Trigger for automatic search_vector updates
CREATE OR REPLACE FUNCTION documents_search_vector_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER documents_search_vector_update
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION documents_search_vector_trigger();

CREATE OR REPLACE FUNCTION chunks_search_vector_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.text, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER chunks_search_vector_update
    BEFORE INSERT OR UPDATE ON chunks
    FOR EACH ROW
    EXECUTE FUNCTION chunks_search_vector_trigger();
```

---

## 13. Integration with Task 6 (Service Layer)

### Connection Pool Configuration

Docker Compose environment variables match Task 6 service layer:

```yaml
# docker-compose.yml
environment:
  DB_POOL_MIN_SIZE: ${DB_POOL_MIN_SIZE:-10}
  DB_POOL_MAX_SIZE: ${DB_POOL_MAX_SIZE:-20}
```

**Backend usage** (from Task 6):
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Use environment variables from Docker Compose
    app.state.db_pool = await asyncpg.create_pool(
        os.getenv("DATABASE_URL"),
        min_size=int(os.getenv("DB_POOL_MIN_SIZE", 10)),
        max_size=int(os.getenv("DB_POOL_MAX_SIZE", 20)),
    )
    yield
    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)
```

---

## 14. Cost Estimates

### Development Environment (Local)

**Hardware Requirements**:
- CPU: 4 cores minimum
- RAM: 8GB minimum (16GB recommended)
- Disk: 20GB minimum

**Monthly Cost**: $0 (runs on local machine)

### Production Environment (Cloud)

**Small Deployment** (10K documents, 1M vectors):
- PostgreSQL: 4GB RAM, 50GB storage → $30/month (DigitalOcean)
- Qdrant: 8GB RAM, 20GB SSD → $40/month (DigitalOcean)
- API Backend: 2GB RAM → $20/month (DigitalOcean)
- **Total**: ~$90/month

**Medium Deployment** (100K documents, 10M vectors):
- PostgreSQL: 8GB RAM, 100GB storage → $60/month
- Qdrant: 32GB RAM, 50GB SSD → $160/month
- API Backend: 4GB RAM (2 instances) → $80/month
- Load Balancer → $10/month
- **Total**: ~$310/month

**Large Deployment** (1M documents, 100M vectors):
- PostgreSQL: 16GB RAM, 500GB storage → $150/month
- Qdrant: 64GB RAM, 200GB SSD → $320/month (or distributed cluster)
- API Backend: 4GB RAM (4 instances) → $160/month
- Load Balancer → $10/month
- **Total**: ~$640/month

---

## 15. Validation Checklist

### Docker Compose Completeness

- [x] **PostgreSQL service** defined with health check
- [x] **Qdrant service** defined with health check
- [x] **FastAPI backend** defined with dependencies on healthy services
- [x] **Frontend service** (optional) defined
- [x] **Volumes** defined for data persistence
- [x] **Network** defined for service communication
- [x] **Environment variables** documented in .env.example

### Production Readiness

- [x] **Resource limits** defined in docker-compose.prod.yml
- [x] **Multi-stage Dockerfiles** for development and production
- [x] **Health checks** for all critical services
- [x] **Restart policies** set to unless-stopped
- [x] **Security**: API keys, no exposed database ports in production
- [x] **Logging**: Log volume mounts configured

### Integration with Previous Tasks

- [x] **Task 1**: Qdrant selected and configured
- [x] **Task 2**: PostgreSQL schema initialized via init.sql
- [x] **Task 6**: Connection pool settings from service layer

---

## 16. Next Steps

**After Docker Compose Configuration**:

1. **Task 8**: Cost & Performance Analysis
   - Use resource limits from this task for cost calculations
   - Performance benchmarks with actual Docker services

2. **Task 9**: Testing Strategy
   - Docker Compose for test environment
   - Integration tests with real services

3. **Task 11**: Final Assembly
   - Integrate this section into ARCHITECTURE.md
   - Add deployment instructions

---

## Completion Summary

**Task 7 - Docker Compose Configuration: COMPLETE**

**Deliverables**:
- ✅ Complete docker-compose.yml with 4 services
- ✅ Production overrides in docker-compose.prod.yml
- ✅ Multi-stage Dockerfiles for backend and frontend
- ✅ Health checks for all critical services
- ✅ Persistent volumes for PostgreSQL and Qdrant
- ✅ Complete .env.example with all variables
- ✅ Usage guide with commands
- ✅ Monitoring and debugging instructions
- ✅ Production deployment checklist
- ✅ Cost estimates for different scales

**Files Documented**:
- docker-compose.yml (development)
- docker-compose.prod.yml (production)
- backend/Dockerfile (multi-stage)
- frontend/Dockerfile (multi-stage)
- .env.example (all variables)
- backend/sql/init.sql (schema from Task 2)

**Integration Points**:
- Task 1: Qdrant configuration and ports
- Task 2: PostgreSQL schema initialization
- Task 6: Connection pool environment variables

**Ready for Integration**: This Docker Compose configuration can now be used in Task 11 (Final Assembly) to complete the ARCHITECTURE.md document.
