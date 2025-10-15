"""Shared pytest fixtures for RAG service tests.

This module provides reusable fixtures for unit and integration tests:
- Database fixtures (pool, connection, test transaction)
- Service mocks (OpenAI, Qdrant, services)
- Test data factories (documents, sources, embeddings)

Pattern: pytest fixtures with async support
Reference: https://docs.pytest.org/en/stable/fixture.html
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import asyncpg
from openai import AsyncOpenAI

# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def mock_db_pool():
    """Mock asyncpg connection pool for unit tests.

    Returns:
        MagicMock: Mocked connection pool with acquire() context manager

    Example:
        async def test_something(mock_db_pool):
            async with mock_db_pool.acquire() as conn:
                result = await conn.fetchrow("SELECT 1")
    """
    pool = MagicMock()
    conn = MagicMock()

    # Mock connection methods
    conn.fetchrow = AsyncMock()
    conn.fetchval = AsyncMock()
    conn.fetch = AsyncMock()
    conn.execute = AsyncMock()

    # Mock acquire() as async context manager
    async def mock_acquire():
        yield conn

    pool.acquire = MagicMock(return_value=mock_acquire())
    pool.close = AsyncMock()

    return pool


@pytest.fixture
async def test_db_pool():
    """Real database connection pool for integration tests.

    Creates a connection pool to the test database with automatic cleanup.

    Yields:
        asyncpg.Pool: Real connection pool

    Example:
        async def test_integration(test_db_pool):
            async with test_db_pool.acquire() as conn:
                result = await conn.fetchrow("SELECT 1")
    """
    from src.config.settings import settings

    pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=5,
    )

    yield pool

    await pool.close()


# =============================================================================
# Service Mocks
# =============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI AsyncClient for unit tests.

    Returns:
        AsyncMock: Mocked OpenAI client with embeddings.create() method

    Example:
        async def test_embedding(mock_openai_client):
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_openai_client.embeddings.create.return_value = mock_response
    """
    client = AsyncMock(spec=AsyncOpenAI)
    client.embeddings = AsyncMock()
    client.embeddings.create = AsyncMock()

    return client


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant AsyncClient for unit tests.

    Returns:
        AsyncMock: Mocked Qdrant client with search/upsert methods

    Example:
        async def test_vector_search(mock_qdrant_client):
            mock_qdrant_client.search.return_value = [
                MagicMock(id="chunk-1", score=0.95)
            ]
    """
    from qdrant_client import AsyncQdrantClient

    client = AsyncMock(spec=AsyncQdrantClient)
    client.search = AsyncMock()
    client.upsert = AsyncMock()
    client.get_collections = AsyncMock()
    client.create_collection = AsyncMock()
    client.update_collection = AsyncMock()
    client.close = AsyncMock()

    return client


# =============================================================================
# Service Fixtures
# =============================================================================

@pytest.fixture
def embedding_service(mock_db_pool, mock_openai_client):
    """EmbeddingService with mocked dependencies.

    Returns:
        EmbeddingService: Service instance with mocked pool and client

    Example:
        async def test_embed(embedding_service):
            result = await embedding_service.embed_text("test")
    """
    from src.services.embeddings.embedding_service import EmbeddingService

    service = EmbeddingService(
        db_pool=mock_db_pool,
        openai_client=mock_openai_client,
    )

    return service


@pytest.fixture
def vector_service(mock_qdrant_client):
    """VectorService with mocked Qdrant client.

    Returns:
        VectorService: Service instance with mocked client

    Example:
        async def test_search(vector_service):
            results = await vector_service.search(embedding, limit=10)
    """
    from src.services.vector_service import VectorService

    service = VectorService(
        qdrant_client=mock_qdrant_client,
        collection_name="documents",
    )

    return service


# =============================================================================
# Test Data Factories
# =============================================================================

@pytest.fixture
def sample_embedding():
    """Sample embedding vector (1536 dimensions).

    Returns:
        list[float]: Valid embedding vector for text-embedding-3-small

    Example:
        def test_something(sample_embedding):
            assert len(sample_embedding) == 1536
    """
    return [0.1] * 1536


@pytest.fixture
def sample_source_id():
    """Sample source UUID.

    Returns:
        UUID: Random source ID

    Example:
        def test_something(sample_source_id):
            doc = {"source_id": sample_source_id}
    """
    return uuid4()


@pytest.fixture
def sample_document_id():
    """Sample document UUID.

    Returns:
        UUID: Random document ID

    Example:
        def test_something(sample_document_id):
            result = await service.get_document(sample_document_id)
    """
    return uuid4()


@pytest.fixture
def sample_chunk():
    """Sample chunk dictionary.

    Returns:
        dict: Chunk data structure with all required fields

    Example:
        def test_chunk(sample_chunk):
            assert sample_chunk["chunk_id"] is not None
    """
    return {
        "chunk_id": str(uuid4()),
        "document_id": str(uuid4()),
        "source_id": str(uuid4()),
        "text": "This is a test chunk of text for testing purposes.",
        "chunk_index": 0,
        "score": 0.95,
        "metadata": {
            "title": "Test Document",
            "created": "2025-10-14T10:00:00",
        }
    }


# =============================================================================
# Async Test Support
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session.

    This fixture is required for pytest-asyncio to work correctly.
    It ensures all async tests use the same event loop.

    Yields:
        asyncio.AbstractEventLoop: Event loop for async tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# MCP Context Mocks
# =============================================================================

@pytest.fixture
def mock_mcp_context(mock_db_pool, mock_openai_client, mock_qdrant_client):
    """Mock MCP Context for tool testing.

    Returns:
        MagicMock: Mocked Context with app.state containing all services

    Example:
        async def test_tool(mock_mcp_context):
            # Tool can access services via ctx.request_context.app.state
            rag_service = mock_mcp_context.request_context.app.state.rag_service
    """
    from src.services.embeddings.embedding_service import EmbeddingService
    from src.services.vector_service import VectorService
    from src.services.search.base_search_strategy import BaseSearchStrategy
    from src.services.search.rag_service import RAGService

    # Create services
    embedding_service = EmbeddingService(
        db_pool=mock_db_pool,
        openai_client=mock_openai_client,
    )

    vector_service = VectorService(
        qdrant_client=mock_qdrant_client,
        collection_name="documents",
    )

    base_strategy = BaseSearchStrategy(
        vector_service=vector_service,
        embedding_service=embedding_service,
        db_pool=mock_db_pool,
    )

    rag_service = RAGService(
        base_strategy=base_strategy,
        hybrid_strategy=None,  # Disable hybrid for most tests
        use_hybrid=False,
    )

    # Create mock context
    ctx = MagicMock()
    ctx.request_context = MagicMock()
    ctx.request_context.app = MagicMock()
    ctx.request_context.app.state = MagicMock()

    # Attach services to state
    ctx.request_context.app.state.db_pool = mock_db_pool
    ctx.request_context.app.state.openai_client = mock_openai_client
    ctx.request_context.app.state.qdrant_client = mock_qdrant_client
    ctx.request_context.app.state.embedding_service = embedding_service
    ctx.request_context.app.state.vector_service = vector_service
    ctx.request_context.app.state.rag_service = rag_service
    ctx.request_context.app.state.document_service = MagicMock()
    ctx.request_context.app.state.source_service = MagicMock()
    ctx.request_context.app.state.ingestion_service = MagicMock()

    # Add shortcuts for common access patterns
    ctx.app = ctx.request_context.app

    return ctx
