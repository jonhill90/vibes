# Testing Strategy

**Section**: 09_testing_strategy
**Research Date**: 2025-10-11
**Archon Task ID**: dc163359-11bf-4f9e-ae44-b6820379c638

---

## Overview

This section defines a comprehensive testing strategy for the RAG service covering unit tests, integration tests, MCP tool validation, performance benchmarking, and test data management. The strategy follows proven patterns from task-manager and pytest best practices.

**Coverage Target**: 80% code coverage minimum
**Testing Framework**: pytest + pytest-asyncio + pytest-cov
**Test Types**: Unit, Integration, MCP, Performance, Load

---

## 1. Unit Testing Approach

### 1.1 Service Layer Testing

**Pattern**: Mock asyncpg connection pool with AsyncMock, test service methods independently.

#### Test Structure
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncpg

from services.document_service import DocumentService
from services.source_service import SourceService
from services.rag_service import RAGService


@pytest.fixture
async def mock_db_pool():
    """Create mock asyncpg connection pool."""
    pool = AsyncMock(spec=asyncpg.Pool)

    # Mock connection acquisition
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    pool.acquire.return_value.__aenter__.return_value = mock_conn

    return pool, mock_conn


@pytest.fixture
def document_service(mock_db_pool):
    """Create DocumentService with mocked pool."""
    pool, _ = mock_db_pool
    return DocumentService(db_pool=pool)


@pytest.mark.asyncio
async def test_get_document_success(document_service, mock_db_pool):
    """Test successful document retrieval."""
    _, mock_conn = mock_db_pool

    # Setup mock response
    mock_conn.fetchrow.return_value = {
        "id": "doc-123",
        "title": "Test Document",
        "content": "Test content",
        "source_id": "src-456",
        "created_at": "2025-10-11T10:00:00Z"
    }

    # Execute
    success, result = await document_service.get_document("doc-123")

    # Assert
    assert success is True
    assert result["document"]["id"] == "doc-123"
    assert result["document"]["title"] == "Test Document"
    mock_conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_get_document_not_found(document_service, mock_db_pool):
    """Test document not found error handling."""
    _, mock_conn = mock_db_pool

    # Setup mock to return None
    mock_conn.fetchrow.return_value = None

    # Execute
    success, result = await document_service.get_document("nonexistent")

    # Assert
    assert success is False
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_get_document_database_error(document_service, mock_db_pool):
    """Test database error handling."""
    _, mock_conn = mock_db_pool

    # Setup mock to raise exception
    mock_conn.fetchrow.side_effect = asyncpg.PostgresError("Connection failed")

    # Execute
    success, result = await document_service.get_document("doc-123")

    # Assert
    assert success is False
    assert "error" in result
    assert "Connection failed" in result["error"]
```

#### tuple[bool, dict] Return Validation
```python
@pytest.mark.asyncio
async def test_all_methods_return_tuple_bool_dict(document_service):
    """Verify all service methods return tuple[bool, dict]."""
    # Test create
    result = await document_service.create_document({...})
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert isinstance(result[1], dict)

    # Test update
    result = await document_service.update_document("id", {...})
    assert isinstance(result, tuple)
    assert isinstance(result[0], bool)
    assert isinstance(result[1], dict)

    # Test delete
    result = await document_service.delete_document("id")
    assert isinstance(result, tuple)
    assert isinstance(result[0], bool)
    assert isinstance(result[1], dict)
```

#### Error Handling Path Coverage
```python
@pytest.mark.asyncio
@pytest.mark.parametrize("error_type,expected_message", [
    (asyncpg.UniqueViolationError, "already exists"),
    (asyncpg.ForeignKeyViolationError, "source not found"),
    (asyncpg.NotNullViolationError, "required field missing"),
    (asyncpg.CheckViolationError, "validation failed"),
])
async def test_create_document_error_paths(
    document_service, mock_db_pool, error_type, expected_message
):
    """Test all database error handling paths."""
    _, mock_conn = mock_db_pool
    mock_conn.fetchrow.side_effect = error_type(expected_message)

    success, result = await document_service.create_document({...})

    assert success is False
    assert expected_message in result["error"].lower()
```

### 1.2 Vector Service Testing

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint, PointStruct

from services.vector_service import VectorService


@pytest.fixture
def mock_qdrant_client():
    """Create mock Qdrant client."""
    client = MagicMock(spec=QdrantClient)
    return client


@pytest.fixture
def vector_service(mock_qdrant_client):
    """Create VectorService with mocked client."""
    return VectorService(
        client=mock_qdrant_client,
        collection_name="test_documents"
    )


@pytest.mark.asyncio
async def test_upsert_vectors(vector_service, mock_qdrant_client):
    """Test vector upsertion."""
    vectors = [
        {"id": "vec-1", "vector": [0.1] * 1536, "payload": {"text": "test"}},
        {"id": "vec-2", "vector": [0.2] * 1536, "payload": {"text": "test2"}},
    ]

    await vector_service.upsert_vectors(vectors)

    mock_qdrant_client.upsert.assert_called_once()
    call_args = mock_qdrant_client.upsert.call_args
    assert call_args.kwargs["collection_name"] == "test_documents"
    assert len(call_args.kwargs["points"]) == 2


@pytest.mark.asyncio
async def test_search_vectors(vector_service, mock_qdrant_client):
    """Test vector search."""
    # Setup mock search results
    mock_qdrant_client.search.return_value = [
        ScoredPoint(
            id="vec-1",
            score=0.95,
            payload={"text": "relevant content"}
        ),
        ScoredPoint(
            id="vec-2",
            score=0.85,
            payload={"text": "also relevant"}
        ),
    ]

    query_vector = [0.1] * 1536
    results = await vector_service.search_vectors(
        query_vector=query_vector,
        limit=10
    )

    assert len(results) == 2
    assert results[0]["score"] == 0.95
    assert results[0]["id"] == "vec-1"
```

### 1.3 Coverage Targets

**Minimum Coverage**: 80%
- Service layer: 85% (high coverage due to business logic)
- MCP tools: 75% (focused on happy path + key errors)
- Search strategies: 90% (critical path coverage)
- Utilities: 70% (helper functions)

**Coverage Measurement**:
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

**Excluded from Coverage**:
- Type stubs (`*.pyi`)
- Test files (`test_*.py`)
- Configuration files (`config.py`)
- Main entry points (`main.py`, `__main__.py`)

---

## 2. Integration Testing

### 2.1 FastAPI TestClient Pattern

```python
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import asyncio

from main import app
from config.database import get_pool


@pytest.fixture
async def test_app():
    """Create test FastAPI app with test database."""
    # Setup test database pool
    test_pool = await asyncpg.create_pool(
        dsn="postgresql://test:test@localhost:5433/rag_test"
    )

    # Override dependency
    async def override_get_pool():
        return test_pool

    app.dependency_overrides[get_pool] = override_get_pool

    yield app

    # Cleanup
    await test_pool.close()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_document_endpoint(test_app):
    """Test POST /api/documents endpoint."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        response = await client.post(
            "/api/documents",
            json={
                "title": "Integration Test Document",
                "content": "Test content for integration testing",
                "source_id": "src-test-123",
                "metadata": {"type": "test"}
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Integration Test Document"
        assert "id" in data

        # Verify document was created
        doc_id = data["id"]
        get_response = await client.get(f"/api/documents/{doc_id}")
        assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_list_documents_with_filters(test_app):
    """Test GET /api/documents with filters."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        # Create test documents
        await client.post("/api/documents", json={
            "title": "Doc 1", "source_id": "src-1", "content": "test"
        })
        await client.post("/api/documents", json={
            "title": "Doc 2", "source_id": "src-2", "content": "test"
        })

        # Test filter by source
        response = await client.get("/api/documents?source_id=src-1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 1
        assert data["documents"][0]["source_id"] == "src-1"
```

### 2.2 Request/Response Cycle Validation

```python
@pytest.mark.asyncio
async def test_full_document_lifecycle(test_app):
    """Test complete document CRUD cycle."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        # 1. Create
        create_response = await client.post(
            "/api/documents",
            json={"title": "Lifecycle Test", "content": "test", "source_id": "src-1"}
        )
        assert create_response.status_code == 201
        doc_id = create_response.json()["id"]

        # 2. Read
        get_response = await client.get(f"/api/documents/{doc_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Lifecycle Test"

        # 3. Update
        update_response = await client.put(
            f"/api/documents/{doc_id}",
            json={"title": "Updated Title"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Title"

        # 4. Delete
        delete_response = await client.delete(f"/api/documents/{doc_id}")
        assert delete_response.status_code == 204

        # 5. Verify deletion
        verify_response = await client.get(f"/api/documents/{doc_id}")
        assert verify_response.status_code == 404
```

### 2.3 Status Code Verification

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("method,endpoint,expected_status", [
    ("GET", "/api/documents", 200),
    ("POST", "/api/documents", 201),
    ("GET", "/api/documents/nonexistent", 404),
    ("PUT", "/api/documents/nonexistent", 404),
    ("DELETE", "/api/documents/nonexistent", 404),
    ("POST", "/api/documents", 400),  # Missing required fields
])
async def test_http_status_codes(test_app, method, endpoint, expected_status):
    """Verify correct HTTP status codes."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        if method == "GET":
            response = await client.get(endpoint)
        elif method == "POST":
            response = await client.post(endpoint, json={})
        elif method == "PUT":
            response = await client.put(endpoint, json={})
        elif method == "DELETE":
            response = await client.delete(endpoint)

        assert response.status_code == expected_status
```

---

## 3. MCP Tool Testing

### 3.1 Direct Tool Invocation Tests

```python
import pytest
import json
from mcp_server.features.documents.document_tools import find_documents, manage_document


@pytest.mark.asyncio
async def test_find_documents_returns_json_string():
    """Verify MCP tool returns JSON string, not dict."""
    result = await find_documents(page=1, per_page=10)

    # CRITICAL: Must be string
    assert isinstance(result, str), "MCP tools MUST return JSON strings"

    # Verify valid JSON
    data = json.loads(result)
    assert "success" in data
    assert "documents" in data


@pytest.mark.asyncio
async def test_find_documents_single_item_mode():
    """Test getting single document by ID."""
    # Create test document first
    create_result = await manage_document(
        action="create",
        title="Test Doc",
        content="Test content",
        source_id="src-1"
    )
    create_data = json.loads(create_result)
    doc_id = create_data["document"]["id"]

    # Get single document
    result = await find_documents(document_id=doc_id)
    data = json.loads(result)

    assert data["success"] is True
    assert data["document"]["id"] == doc_id
    assert data["document"]["title"] == "Test Doc"


@pytest.mark.asyncio
async def test_find_documents_list_mode():
    """Test listing documents with pagination."""
    result = await find_documents(page=1, per_page=5)
    data = json.loads(result)

    assert data["success"] is True
    assert "documents" in data
    assert "total_count" in data
    assert len(data["documents"]) <= 5
```

### 3.2 Truncation and Optimization Tests

```python
@pytest.mark.asyncio
async def test_mcp_response_truncation():
    """Verify large fields are truncated for MCP."""
    # Create document with large content
    large_content = "x" * 5000
    create_result = await manage_document(
        action="create",
        title="Large Doc",
        content=large_content,
        source_id="src-1"
    )
    create_data = json.loads(create_result)
    doc_id = create_data["document"]["id"]

    # Get via MCP tool (should truncate)
    result = await find_documents(document_id=doc_id)
    data = json.loads(result)

    # Verify truncation
    MAX_CONTENT_LENGTH = 1000
    assert len(data["document"]["content"]) <= MAX_CONTENT_LENGTH
    assert data["document"]["content"].endswith("...")


@pytest.mark.asyncio
async def test_mcp_pagination_limits():
    """Verify pagination limits are enforced."""
    # Try to request too many items
    result = await find_documents(page=1, per_page=100)
    data = json.loads(result)

    # Should be limited to MAX_PER_PAGE (20)
    MAX_PER_PAGE = 20
    assert len(data["documents"]) <= MAX_PER_PAGE
```

### 3.3 Action Mode Tests

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("action", ["create", "update", "delete"])
async def test_manage_document_all_actions(action):
    """Test all manage_document action modes."""
    if action == "create":
        result = await manage_document(
            action="create",
            title="Test",
            content="Test content",
            source_id="src-1"
        )
        data = json.loads(result)
        assert data["success"] is True
        assert "document" in data

    elif action == "update":
        # Create first
        create_result = await manage_document(
            action="create",
            title="Original",
            content="Original content",
            source_id="src-1"
        )
        doc_id = json.loads(create_result)["document"]["id"]

        # Update
        result = await manage_document(
            action="update",
            document_id=doc_id,
            title="Updated"
        )
        data = json.loads(result)
        assert data["success"] is True
        assert data["document"]["title"] == "Updated"

    elif action == "delete":
        # Create first
        create_result = await manage_document(
            action="create",
            title="To Delete",
            content="Will be deleted",
            source_id="src-1"
        )
        doc_id = json.loads(create_result)["document"]["id"]

        # Delete
        result = await manage_document(
            action="delete",
            document_id=doc_id
        )
        data = json.loads(result)
        assert data["success"] is True
```

### 3.4 Error Response Format Tests

```python
@pytest.mark.asyncio
async def test_mcp_error_response_format():
    """Verify MCP error responses include suggestion."""
    result = await find_documents(document_id="nonexistent-id")
    data = json.loads(result)

    assert data["success"] is False
    assert "error" in data
    assert "suggestion" in data
    assert "not found" in data["error"].lower()
    assert "list all" in data["suggestion"].lower()


@pytest.mark.asyncio
async def test_mcp_validation_error():
    """Test MCP tool validation error handling."""
    result = await manage_document(
        action="create",
        # Missing required fields
        title=""
    )
    data = json.loads(result)

    assert data["success"] is False
    assert "error" in data
    assert "required" in data["error"].lower()
```

---

## 4. Performance Testing

### 4.1 Load Testing

```python
import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor


@pytest.mark.asyncio
async def test_concurrent_search_requests():
    """Load test: 100 concurrent search requests."""
    async def search_request():
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.post(
                "/api/search",
                json={"query": "test query", "match_count": 5}
            )
            return response.status_code

    # Execute 100 concurrent requests
    tasks = [search_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)

    # Verify all succeeded
    assert all(status == 200 for status in results)


@pytest.mark.asyncio
async def test_database_connection_pool_under_load():
    """Test connection pool behavior under load."""
    pool = await asyncpg.create_pool(
        dsn=TEST_DATABASE_URL,
        min_size=5,
        max_size=10
    )

    async def query_task():
        async with pool.acquire() as conn:
            await conn.fetchrow("SELECT 1")
            await asyncio.sleep(0.1)  # Simulate work

    # 50 concurrent tasks, pool size 10
    tasks = [query_task() for _ in range(50)]
    start = asyncio.get_event_loop().time()
    await asyncio.gather(*tasks)
    duration = asyncio.get_event_loop().time() - start

    # Should complete without deadlock
    assert duration < 10.0  # 50 tasks * 0.1s / 10 pool = ~0.5s minimum

    await pool.close()
```

### 4.2 Latency Percentiles

```python
import pytest
import numpy as np
from time import time


@pytest.mark.asyncio
async def test_search_latency_percentiles():
    """Measure search latency p50, p95, p99."""
    latencies = []

    async with AsyncClient(app=test_app, base_url="http://test") as client:
        for i in range(100):
            start = time()
            response = await client.post(
                "/api/search",
                json={"query": f"test query {i}", "match_count": 10}
            )
            latency = (time() - start) * 1000  # Convert to ms
            latencies.append(latency)
            assert response.status_code == 200

    # Calculate percentiles
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    print(f"\nSearch Latency Percentiles:")
    print(f"  p50: {p50:.2f}ms")
    print(f"  p95: {p95:.2f}ms")
    print(f"  p99: {p99:.2f}ms")

    # Assert acceptable latency
    assert p50 < 100  # 50th percentile under 100ms
    assert p95 < 200  # 95th percentile under 200ms
    assert p99 < 500  # 99th percentile under 500ms
```

### 4.3 Memory Usage Benchmarks

```python
import pytest
import psutil
import os


@pytest.mark.asyncio
async def test_memory_usage_under_load():
    """Monitor memory usage during load test."""
    process = psutil.Process(os.getpid())

    # Baseline memory
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Execute load test
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        tasks = []
        for i in range(1000):
            tasks.append(
                client.post(
                    "/api/search",
                    json={"query": f"query {i}", "match_count": 50}
                )
            )
        await asyncio.gather(*tasks)

    # Peak memory
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = peak_memory - baseline_memory

    print(f"\nMemory Usage:")
    print(f"  Baseline: {baseline_memory:.2f} MB")
    print(f"  Peak: {peak_memory:.2f} MB")
    print(f"  Increase: {memory_increase:.2f} MB")

    # Assert memory increase is reasonable
    assert memory_increase < 500  # Less than 500MB increase
```

### 4.4 Performance Testing Tools

**pytest-benchmark**: For micro-benchmarks
```python
def test_embedding_generation_performance(benchmark):
    """Benchmark embedding generation."""
    embedding_service = EmbeddingService(provider="openai")

    def generate_embedding():
        return embedding_service.create_embedding("test text")

    result = benchmark(generate_embedding)
    assert len(result) == 1536
```

**locust**: For distributed load testing
```python
# locustfile.py
from locust import HttpUser, task, between


class RAGServiceUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def search_documents(self):
        self.client.post("/api/search", json={
            "query": "test query",
            "match_count": 10
        })

    @task(1)
    def list_documents(self):
        self.client.get("/api/documents?page=1&per_page=20")

    @task(1)
    def create_document(self):
        self.client.post("/api/documents", json={
            "title": "Load Test Doc",
            "content": "Content for load testing",
            "source_id": "src-load-test"
        })
```

**Usage**:
```bash
# Run locust load test
locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

---

## 5. Test Data Setup

### 5.1 Sample Documents with Known Embeddings

```python
import pytest
import hashlib
import numpy as np


@pytest.fixture
async def sample_documents():
    """Create sample documents with deterministic embeddings."""
    # Deterministic embedding generation
    def create_embedding(text: str) -> list[float]:
        # Use hash for deterministic vectors
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        np.random.seed(hash_val % (2**32))
        return np.random.rand(1536).tolist()

    documents = [
        {
            "id": "doc-sample-1",
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence...",
            "embedding": create_embedding("Machine learning is a subset of artificial intelligence..."),
            "source_id": "src-sample-1",
        },
        {
            "id": "doc-sample-2",
            "title": "Deep Learning Fundamentals",
            "content": "Deep learning uses neural networks with multiple layers...",
            "embedding": create_embedding("Deep learning uses neural networks with multiple layers..."),
            "source_id": "src-sample-1",
        },
        {
            "id": "doc-sample-3",
            "title": "Natural Language Processing",
            "content": "NLP enables computers to understand human language...",
            "embedding": create_embedding("NLP enables computers to understand human language..."),
            "source_id": "src-sample-2",
        },
    ]

    return documents


@pytest.fixture
async def populated_test_db(sample_documents, test_db_pool):
    """Populate test database with sample documents."""
    async with test_db_pool.acquire() as conn:
        for doc in sample_documents:
            await conn.execute(
                """
                INSERT INTO documents (id, title, content, source_id)
                VALUES ($1, $2, $3, $4)
                """,
                doc["id"], doc["title"], doc["content"], doc["source_id"]
            )

    yield test_db_pool

    # Cleanup
    async with test_db_pool.acquire() as conn:
        await conn.execute("DELETE FROM documents WHERE id LIKE 'doc-sample-%'")
```

### 5.2 Test Collections in Qdrant

```python
@pytest.fixture
async def test_qdrant_collection(mock_qdrant_client, sample_documents):
    """Create test collection in Qdrant with sample vectors."""
    collection_name = "test_documents"

    # Create collection
    await mock_qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "size": 1536,
            "distance": "Cosine"
        }
    )

    # Insert sample vectors
    points = [
        {
            "id": doc["id"],
            "vector": doc["embedding"],
            "payload": {
                "title": doc["title"],
                "content": doc["content"][:1000],
                "source_id": doc["source_id"]
            }
        }
        for doc in sample_documents
    ]

    await mock_qdrant_client.upsert(
        collection_name=collection_name,
        points=points
    )

    yield collection_name

    # Cleanup
    await mock_qdrant_client.delete_collection(collection_name)
```

### 5.3 Separate Test Database

**docker-compose.test.yml**:
```yaml
services:
  postgres-test:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: rag_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5433:5432"
    volumes:
      - ./tests/sql/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./tests/sql/test_data.sql:/docker-entrypoint-initdb.d/02-test-data.sql

  qdrant-test:
    image: qdrant/qdrant:latest
    ports:
      - "6334:6333"
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334
```

**pytest.ini**:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (require test database)
    performance: Performance benchmarks
    slow: Slow tests (skip by default)
```

### 5.4 Common Test Fixtures

```python
# conftest.py
import pytest
import asyncpg
from qdrant_client import QdrantClient


@pytest.fixture(scope="session")
async def test_db_pool():
    """Session-scoped database pool for tests."""
    pool = await asyncpg.create_pool(
        host="localhost",
        port=5433,
        database="rag_test",
        user="test",
        password="test",
        min_size=5,
        max_size=10
    )

    yield pool

    await pool.close()


@pytest.fixture
async def clean_db(test_db_pool):
    """Clean database before each test."""
    async with test_db_pool.acquire() as conn:
        await conn.execute("TRUNCATE documents, chunks, sources, crawl_jobs CASCADE")

    yield

    # Optional: cleanup after test
    async with test_db_pool.acquire() as conn:
        await conn.execute("TRUNCATE documents, chunks, sources, crawl_jobs CASCADE")


@pytest.fixture
def test_qdrant_client():
    """Create Qdrant client for testing."""
    client = QdrantClient(host="localhost", port=6334)
    yield client
    client.close()


@pytest.fixture
async def embedding_service_mock():
    """Mock embedding service."""
    class MockEmbeddingService:
        async def create_embedding(self, text: str) -> list[float]:
            # Return deterministic embedding
            hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
            np.random.seed(hash_val % (2**32))
            return np.random.rand(1536).tolist()

    return MockEmbeddingService()
```

### 5.5 Cleanup Strategies

```python
@pytest.fixture
async def auto_cleanup_documents(test_db_pool):
    """Track and auto-cleanup created documents."""
    created_ids = []

    async def create_and_track(doc_data):
        async with test_db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO documents (title, content, source_id)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                doc_data["title"],
                doc_data["content"],
                doc_data["source_id"]
            )
            created_ids.append(row["id"])
            return row["id"]

    yield create_and_track

    # Cleanup all created documents
    async with test_db_pool.acquire() as conn:
        for doc_id in created_ids:
            await conn.execute("DELETE FROM documents WHERE id = $1", doc_id)
```

---

## 6. Testing Tools & Frameworks

### 6.1 Core Testing Stack

**pytest + pytest-asyncio**:
```bash
pip install pytest pytest-asyncio pytest-mock
```

**Configuration** (pyproject.toml):
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--asyncio-mode=auto"
]
```

### 6.2 Coverage Tools

**pytest-cov**:
```bash
pip install pytest-cov
```

**Usage**:
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Generate XML for CI/CD
pytest --cov=src --cov-report=xml

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

**Coverage Configuration** (.coveragerc):
```ini
[run]
source = src
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */migrations/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

### 6.3 HTTP Testing

**httpx for async HTTP testing**:
```bash
pip install httpx
```

**Usage**:
```python
import httpx
from fastapi.testclient import TestClient

# Synchronous client
client = TestClient(app)
response = client.get("/api/documents")

# Async client (preferred for async apps)
async with httpx.AsyncClient(app=app, base_url="http://test") as client:
    response = await client.get("/api/documents")
```

### 6.4 Mocking Framework

**pytest-mock**:
```python
def test_with_mocker(mocker):
    # Mock function
    mock_func = mocker.patch("module.function")
    mock_func.return_value = "mocked"

    # Mock async function
    mock_async = mocker.patch("module.async_function")
    mock_async.return_value = asyncio.coroutine(lambda: "mocked")()

    # Spy on function (call original but track calls)
    spy = mocker.spy(module, "function")
```

---

## 7. CI/CD Integration

### 7.1 GitHub Actions Workflow

**.github/workflows/test.yml**:
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: rag_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5433:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6334:6333
        options: >-
          --health-cmd "curl -f http://localhost:6333/health || exit 1"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run unit tests
      run: |
        pytest tests/unit -v --cov=src --cov-report=xml

    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://test:test@localhost:5433/rag_test
        QDRANT_URL: http://localhost:6334
      run: |
        pytest tests/integration -v

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### 7.2 Coverage Reporting

**codecov.yml**:
```yaml
coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 2%
    patch:
      default:
        target: 70%
        threshold: 5%

comment:
  layout: "reach, diff, flags, files"
  behavior: default
  require_changes: false
```

### 7.3 Performance Benchmarking

**.github/workflows/benchmark.yml**:
```yaml
name: Performance Benchmarks

on:
  push:
    branches: [ main ]

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Run benchmarks
      run: |
        pytest tests/performance --benchmark-only --benchmark-json=benchmark.json

    - name: Store benchmark results
      uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'pytest'
        output-file-path: benchmark.json
        github-token: ${{ secrets.GITHUB_TOKEN }}
        auto-push: true
```

---

## 8. Test Execution Commands

### 8.1 Run All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### 8.2 Run Specific Test Types
```bash
# Unit tests only (fast)
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Performance tests
pytest tests/performance --benchmark-only

# Specific test file
pytest tests/unit/test_document_service.py -v

# Specific test function
pytest tests/unit/test_document_service.py::test_get_document_success -v
```

### 8.3 Run with Markers
```bash
# Run only unit tests (marked with @pytest.mark.unit)
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run integration and performance tests
pytest -m "integration or performance"
```

### 8.4 Debugging Tests
```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# Verbose output with full traceback
pytest -vv --tb=long
```

---

## 9. Example Test Suite Structure

### 9.1 Directory Organization

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_document_service.py
│   ├── test_source_service.py
│   ├── test_rag_service.py
│   ├── test_vector_service.py
│   └── test_embedding_service.py
├── integration/
│   ├── test_api_documents.py
│   ├── test_api_search.py
│   ├── test_api_sources.py
│   └── test_end_to_end.py
├── mcp/
│   ├── test_document_tools.py
│   ├── test_source_tools.py
│   └── test_search_tools.py
├── performance/
│   ├── test_search_latency.py
│   ├── test_concurrent_load.py
│   └── test_memory_usage.py
└── fixtures/
    ├── sample_documents.json
    ├── sample_embeddings.npy
    └── test_queries.txt
```

### 9.2 Sample Test File

**tests/unit/test_document_service.py**:
```python
"""Unit tests for DocumentService."""
import pytest
from unittest.mock import AsyncMock
import asyncpg

from services.document_service import DocumentService


class TestDocumentService:
    """Test suite for DocumentService."""

    @pytest.fixture
    async def mock_pool(self):
        """Mock database pool."""
        pool = AsyncMock(spec=asyncpg.Pool)
        conn = AsyncMock(spec=asyncpg.Connection)
        pool.acquire.return_value.__aenter__.return_value = conn
        return pool, conn

    @pytest.fixture
    def service(self, mock_pool):
        """Create service with mock pool."""
        pool, _ = mock_pool
        return DocumentService(db_pool=pool)

    @pytest.mark.asyncio
    async def test_get_document_success(self, service, mock_pool):
        """Test successful document retrieval."""
        _, conn = mock_pool
        conn.fetchrow.return_value = {
            "id": "doc-1",
            "title": "Test",
            "content": "Content"
        }

        success, result = await service.get_document("doc-1")

        assert success is True
        assert result["document"]["id"] == "doc-1"

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, service, mock_pool):
        """Test document not found error."""
        _, conn = mock_pool
        conn.fetchrow.return_value = None

        success, result = await service.get_document("nonexistent")

        assert success is False
        assert "error" in result
```

---

## 10. Success Metrics

### 10.1 Coverage Targets

| Component | Target Coverage | Rationale |
|-----------|----------------|-----------|
| Service Layer | 85% | Business logic critical |
| MCP Tools | 75% | Focus on happy path + errors |
| Search Strategies | 90% | Core functionality |
| API Endpoints | 80% | Integration coverage |
| Utilities | 70% | Helper functions |
| **Overall** | **80%** | **Minimum acceptable** |

### 10.2 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search Latency p50 | < 100ms | 100 concurrent requests |
| Search Latency p95 | < 200ms | 100 concurrent requests |
| Search Latency p99 | < 500ms | 100 concurrent requests |
| Concurrent Requests | 100 | Without errors |
| Memory Increase | < 500MB | Under load |

### 10.3 Test Quality Metrics

- **Test Reliability**: 0% flaky tests (deterministic)
- **Test Speed**: Unit tests < 5s, Integration tests < 30s
- **Test Maintenance**: Clear naming, good documentation
- **Test Coverage**: 80% minimum, tracked in CI/CD

---

## Summary

This testing strategy provides comprehensive coverage across all layers of the RAG service:

1. **Unit Testing**: Mock-based testing of service layer with 85% coverage target
2. **Integration Testing**: FastAPI TestClient for full request/response cycle validation
3. **MCP Tool Testing**: Direct invocation tests ensuring JSON string returns and truncation
4. **Performance Testing**: Load tests, latency percentiles, memory usage benchmarks
5. **Test Data**: Sample documents, Qdrant collections, separate test database
6. **CI/CD**: GitHub Actions workflows for automated testing and coverage reporting

**Key Testing Principles**:
- ✅ Mock external dependencies (asyncpg, Qdrant, OpenAI)
- ✅ Validate tuple[bool, dict] return pattern in all service methods
- ✅ Ensure MCP tools return JSON strings, not dicts
- ✅ Test all error handling paths
- ✅ Measure performance under load
- ✅ Maintain 80% code coverage minimum
- ✅ Use separate test database and Qdrant collection
- ✅ Integrate with CI/CD for continuous validation

**Tools**: pytest, pytest-asyncio, pytest-cov, httpx, pytest-mock, locust, pytest-benchmark
