# RAG Service

A containerized Retrieval-Augmented Generation (RAG) service with vector search capabilities, MCP server integration, and web UI for document management.

## Overview

This service provides semantic search over documents using OpenAI embeddings and PostgreSQL pgvector. External AI assistants like Claude Code can search the knowledge base via the Model Context Protocol (MCP) server while humans manage documents through the web interface.

**Architecture**:
- **Backend**: FastAPI + SQLAlchemy with async PostgreSQL support
- **Frontend**: React + TypeScript with document upload and search interface
- **Database**: PostgreSQL 16 with pgvector extension for vector similarity search
- **Deployment**: Docker Compose with health checks and hot reload support
- **MCP Server**: Knowledge base search tools for AI assistant integration

**Key Features**:
- Document ingestion with automatic chunking and embedding generation
- Vector similarity search with configurable thresholds
- Source attribution and metadata tracking
- MCP server for AI assistant knowledge base access
- Web UI for document management and search testing
- Data persistence across container restarts

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker**: Version 20.10 or higher ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0 or higher (included with Docker Desktop)
- **OpenAI API Key**: For embedding generation ([Get API Key](https://platform.openai.com/api-keys))

To verify your installation:
```bash
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Clone and Configure

```bash
# Navigate to the rag-service directory
cd infra/rag-service

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
# Set: OPENAI_API_KEY=your-api-key-here
```

### 2. Start Services

```bash
# Build and start all services (database, backend, frontend)
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d
```

**First-time startup takes 2-3 minutes**:
1. PostgreSQL initializes database with pgvector extension (10-15 seconds)
2. Backend waits for database health check, runs migrations (20-30 seconds)
3. Frontend builds and starts development server (60-90 seconds)

### 3. Access the Application

Once all health checks pass:

- **Web UI**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **MCP Server**: `http://localhost:8052/mcp` (via `npx mcp-remote`)

### 4. Verify MCP Integration

Test the MCP server from Claude Code or another AI assistant:

```bash
# Connect to MCP server
npx mcp-remote http://localhost:8052/mcp

# Example MCP commands (in Claude Code):
# - rag_get_available_sources()
# - rag_search_knowledge_base(query="authentication JWT", match_count=5)
# - rag_search_code_examples(query="React hooks", match_count=3)
```

---

## MCP Server Usage

The MCP server provides tools for AI assistants to search the knowledge base:

### 1. `rag_get_available_sources` - List all indexed sources

```python
# Get all available documentation sources
rag_get_available_sources()

# Returns: List of sources with id, title, url, document_count
```

### 2. `rag_search_knowledge_base` - Search across documents

```python
# Search all sources (keep queries SHORT - 2-5 keywords)
rag_search_knowledge_base(query="vector functions", match_count=5)

# Search specific source
rag_search_knowledge_base(
    query="authentication JWT",
    source_id="src_abc123",
    match_count=10
)
```

**Parameters**:
- `query` (str, required): Search query (2-5 keywords recommended)
- `source_id` (str, optional): Filter to specific source
- `match_count` (int, optional): Number of results (default: 5, max: 20)
- `similarity_threshold` (float, optional): Minimum similarity score (0.0-1.0, default: 0.7)

### 3. `rag_search_code_examples` - Search code snippets

```python
# Find code examples
rag_search_code_examples(query="async database query", match_count=3)
```

---

## Environment Configuration

The `.env` file controls all service configuration. Key variables:

### Database Configuration
- `POSTGRES_DB`: Database name (default: `ragservice`)
- `POSTGRES_USER`: Database username (default: `raguser`)
- `POSTGRES_PASSWORD`: Database password (**change in production!**)
- `DATABASE_URL`: Full connection string (use `db` as hostname in Docker)
- `DB_PORT`: Exposed database port (default: `5433`)

### Backend Configuration
- `API_PORT`: FastAPI server port (default: `8001`)
- `MCP_PORT`: MCP server port (default: `8052`)
- `CORS_ORIGINS`: Allowed frontend URLs (comma-separated)
- `LOG_LEVEL`: Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)

### Embedding Service Configuration
- `OPENAI_API_KEY`: OpenAI API key (**required!**)
- `EMBEDDING_MODEL`: Model to use (default: `text-embedding-3-small`)
- `EMBEDDING_DIMENSIONS`: Vector dimensions (default: `1536`)
- `EMBEDDING_BATCH_SIZE`: Batch size for processing (default: `100`)

### Vector Search Configuration
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: `0.7`)
- `MAX_SEARCH_RESULTS`: Maximum results to return (default: `10`)

### Frontend Configuration
- `FRONTEND_PORT`: React development server port (default: `5173`)
- `VITE_API_URL`: Backend API URL (use `http://localhost:8001` for browser access)

---

## Development Workflow

### Hot Reload

All services support hot reload during development:

- **Backend**: Changes to Python files trigger automatic reload (FastAPI `--reload`)
- **Frontend**: Vite detects file changes and hot-reloads the browser
- **Database**: Schema changes require manual migration (see below)

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Run Database Migrations

```bash
# Access backend container
docker exec -it ragservice-backend bash

# Generate migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Exit container
exit
```

### Run Tests

The RAG service includes comprehensive testing infrastructure with 4-level quality gates:

**Quick Test Commands**:
```bash
# All tests (all quality gates)
docker exec -it ragservice-backend pytest

# Unit tests only (fast, ~30s)
docker exec -it ragservice-backend pytest tests/unit/ -v

# Integration tests only (medium, ~60s)
docker exec -it ragservice-backend pytest tests/integration/ -v

# Browser tests only (slow, ~120s)
docker exec -it ragservice-backend pytest tests/browser/ -v
```

**Quality Gate Levels** (from fastest to slowest):

1. **Level 1: Syntax & Style** (~5s)
   ```bash
   docker exec -it ragservice-backend ruff check tests/ --fix
   docker exec -it ragservice-backend mypy tests/
   ```
   - Validates code style, import order, type annotations
   - Auto-fixes common issues with `--fix` flag

2. **Level 2: Unit Tests** (~30s)
   ```bash
   docker exec -it ragservice-backend pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-fail-under=80
   ```
   - Tests business logic in isolation (document validation, service layer)
   - Requires >80% code coverage to pass
   - Uses mocked dependencies (no database or external APIs)

3. **Level 3a: API Integration Tests** (~60s)
   ```bash
   docker exec -it ragservice-backend pytest tests/integration/ -v
   ```
   - Tests FastAPI endpoints with mocked database
   - Validates request/response formats, error handling
   - Tests all HTTP status codes (200, 400, 404, 413, 422, 500)

4. **Level 3b: Browser Integration Tests** (~120s)
   ```bash
   # Ensure services running first
   docker-compose up -d

   # Run browser tests
   docker exec -it ragservice-backend pytest tests/browser/ -v
   ```
   - Tests complete user workflows (upload, search, delete)
   - Uses Playwright browser automation
   - Validates frontend UI integration with backend
   - Generates screenshots in `tests/browser/screenshots/` for proof

**Test Coverage**:
- **Backend**: 80%+ code coverage for document/search/delete operations
- **Unit Tests**: File validation, document service, search filtering
- **Integration Tests**: Document API, search API, cascade deletes
- **Browser Tests**: Document upload, search filtering, delete operations

**Test Dependencies**:
All dependencies are included in the Docker image. If running tests locally outside Docker:
```bash
pip install pytest pytest-asyncio pytest-cov mypy ruff httpx playwright
playwright install  # Browser binaries for browser tests
```

**Troubleshooting Tests**:
- **Browser tests fail with "Executable doesn't exist"**: Run `playwright install` inside container
- **Services not accessible**: Verify `docker-compose ps` shows all services running
- **Timeout errors**: Increase timeouts in test files (default: 30s for uploads, 5s for UI)
- **Coverage below 80%**: Run with `--cov-report=html` to see detailed coverage report

---

## Architecture Details

### Database Schema

**Documents Table**:
- `id` (UUID, primary key)
- `source_id` (UUID, foreign key to sources)
- `title` (VARCHAR 500, required)
- `content` (TEXT, required)
- `chunk_index` (INTEGER, for document chunks)
- `embedding` (VECTOR(1536), for similarity search)
- `metadata` (JSONB, for additional attributes)
- `created_at` (TIMESTAMP, auto-generated)

**Sources Table**:
- `id` (UUID, primary key)
- `title` (VARCHAR 255, required)
- `url` (VARCHAR 1000, optional)
- `source_type` (ENUM: documentation, code, markdown, pdf)
- `created_at` (TIMESTAMP, auto-generated)

**Indexes**:
- HNSW index on `embedding` for vector similarity search
- Index on `source_id` for filtering by source
- Full-text search index on `content` for keyword matching

### API Endpoints

**Document Endpoints**:
- `POST /documents` - Upload and ingest document
- `GET /documents/{document_id}` - Get document details
- `DELETE /documents/{document_id}` - Delete document

**Search Endpoints**:
- `POST /search` - Vector similarity search
- `GET /search/sources` - List available sources

**Source Endpoints**:
- `GET /sources` - List all sources
- `POST /sources` - Create source
- `DELETE /sources/{source_id}` - Delete source and documents

**Health Endpoints**:
- `GET /health` - Backend health check
- `GET /health/db` - Database connectivity check

---

## Troubleshooting

### OpenAI API Errors

**Symptom**: Backend logs show "OpenAI API key not configured"

**Solutions**:
1. Verify `OPENAI_API_KEY` is set in `.env` file
2. Check API key is valid: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`
3. Restart backend: `docker-compose restart backend`

### Vector Search Returning No Results

**Symptom**: Search returns empty results even with valid documents

**Solutions**:
1. Check if documents have embeddings: `docker exec -it ragservice-db psql -U raguser -d ragservice -c "SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;"`
2. Lower similarity threshold in `.env`: `SIMILARITY_THRESHOLD=0.5`
3. Verify pgvector extension installed: `docker exec -it ragservice-db psql -U raguser -d ragservice -c "SELECT * FROM pg_extension WHERE extname='vector';"`

### Slow Embedding Generation

**Symptom**: Document upload takes > 30 seconds

**Solutions**:
1. Reduce batch size in `.env`: `EMBEDDING_BATCH_SIZE=50`
2. Use smaller embedding model: `EMBEDDING_MODEL=text-embedding-3-small`
3. Check OpenAI API rate limits in logs

---

## Production Deployment

**IMPORTANT**: Before deploying to production:

1. **Secure API keys**:
   ```env
   OPENAI_API_KEY=<use-secrets-management>
   POSTGRES_PASSWORD=<strong-random-password>
   ```

2. **Optimize vector search**:
   ```env
   EMBEDDING_BATCH_SIZE=100
   SIMILARITY_THRESHOLD=0.75
   MAX_SEARCH_RESULTS=10
   ```

3. **Configure monitoring**:
   - Track OpenAI API usage and costs
   - Monitor vector index performance
   - Set up log aggregation for search queries

4. **Database backups**:
   ```bash
   # Backup with vector data
   docker exec ragservice-db pg_dump -U raguser ragservice > backup.sql
   ```

---

## License

This project is part of the vibes ecosystem. See top-level LICENSE file for details.

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [vibes/issues](https://github.com/yourusername/vibes/issues)
- **Documentation**: See `/Users/jon/source/vibes/README.md` for overall architecture
- **MCP Specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
