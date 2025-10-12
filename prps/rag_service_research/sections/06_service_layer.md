# Service Layer Architecture

**Task 6 - Service Layer Design**
**Date**: 2025-10-11
**Pattern**: Service Layer with tuple[bool, dict] returns and async database operations
**References**:
- examples/01_service_layer_pattern.py
- infra/task-manager/backend/src/services/task_service.py

---

## Overview

The RAG service follows a **layered service architecture** with clear separation of concerns:

1. **CRUD Services** (DocumentService, SourceService): Handle database operations with tuple[bool, dict] returns
2. **Vector Services** (VectorService, EmbeddingService): Manage vector operations and embedding generation
3. **Coordinator Service** (RAGService): Orchestrates search strategies without direct database access

This architecture enables:
- Clear separation of concerns (database vs vector vs search logic)
- Consistent error handling with tuple[bool, dict] pattern
- Easy testing through dependency injection
- Scalable service composition

---

## 1. DocumentService

**Responsibility**: Manage document metadata and coordinate with vector storage.

### Class Definition

```python
from typing import Any
import asyncpg
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document CRUD operations with vector coordination.

    PATTERN: Service layer with asyncpg connection pooling
    - All methods return tuple[bool, dict]
    - Async context managers for connection management
    - Validation before database operations
    - Comprehensive error handling
    - Response optimization with exclude_large_fields

    CRITICAL GOTCHAS:
    - Gotcha #2: Pass db_pool, NOT connections (prevents deadlock)
    - Gotcha #3: Use $1, $2 placeholders (asyncpg syntax, not %s)
    - Gotcha #8: Always use async with for connection management
    """

    def __init__(self, db_pool: asyncpg.Pool, vector_service: 'VectorService'):
        """Initialize DocumentService with database pool and vector service.

        Args:
            db_pool: asyncpg connection pool for database operations
            vector_service: VectorService instance for vector operations
        """
        self.db_pool = db_pool
        self.vector_service = vector_service

    async def list_documents(
        self,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = 50,
        exclude_large_fields: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """List documents with filters, pagination, and optional field exclusion.

        PATTERN: Conditional field selection for performance
        - exclude_large_fields=True: Truncate content > 1000 chars (for MCP)
        - exclude_large_fields=False: Return full content

        Args:
            filters: Optional filters (source_id, document_type, status)
            page: Page number (1-indexed)
            per_page: Items per page (max 50)
            exclude_large_fields: If True, truncate large fields for MCP

        Returns:
            Tuple of (success, {documents, total_count, page, per_page})

        Example:
            >>> success, result = await service.list_documents(
            ...     filters={"source_id": "uuid-here"},
            ...     page=1,
            ...     per_page=20,
            ...     exclude_large_fields=True  # For MCP tools
            ... )
            >>> if success:
            ...     print(f"Found {result['total_count']} documents")
        """
        try:
            filters = filters or {}
            offset = (page - 1) * per_page

            # Limit per_page to prevent massive payloads (MCP Gotcha #7)
            per_page = min(per_page, 50)

            # Build base query with conditional field selection
            if exclude_large_fields:
                # Truncate content to 1000 chars for MCP (Gotcha #7)
                select_fields = """
                    id, title, source_id, document_type, url, status,
                    CASE
                        WHEN LENGTH(content) > 1000
                        THEN SUBSTRING(content FROM 1 FOR 1000) || '...'
                        ELSE content
                    END as content,
                    metadata, created_at, updated_at
                """
            else:
                select_fields = "*"

            where_clauses = []
            params = []
            param_idx = 1

            # Apply filters (CRITICAL: Use $1, $2 syntax - Gotcha #3)
            if "source_id" in filters:
                where_clauses.append(f"source_id = ${param_idx}::uuid")
                params.append(filters["source_id"])
                param_idx += 1

            if "document_type" in filters:
                where_clauses.append(f"document_type = ${param_idx}")
                params.append(filters["document_type"])
                param_idx += 1

            if "status" in filters:
                where_clauses.append(f"status = ${param_idx}")
                params.append(filters["status"])
                param_idx += 1

            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # CRITICAL: Always use async with for connection management (Gotcha #8)
            async with self.db_pool.acquire() as conn:
                # Get total count
                count_query = f"SELECT COUNT(*) FROM documents {where_clause}"
                total_count = await conn.fetchval(count_query, *params)

                # Get paginated documents
                query = f"""
                    SELECT {select_fields}
                    FROM documents
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """
                params.extend([per_page, offset])
                rows = await conn.fetch(query, *params)

            documents = [dict(row) for row in rows]

            return True, {
                "documents": documents,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing documents: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return False, {"error": f"Error listing documents: {str(e)}"}

    async def get_document(self, document_id: str) -> tuple[bool, dict[str, Any]]:
        """Get document by ID with full content.

        Args:
            document_id: UUID of the document

        Returns:
            Tuple of (success, {document: dict} or {error: str})

        Example:
            >>> success, result = await service.get_document("uuid-here")
            >>> if success:
            ...     print(result["document"]["title"])
        """
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM documents WHERE id = $1::uuid",
                    document_id
                )

            if not row:
                return False, {"error": f"Document {document_id} not found"}

            return True, {"document": dict(row)}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error getting document: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return False, {"error": f"Error getting document: {str(e)}"}

    async def create_document(
        self,
        title: str,
        content: str,
        source_id: str,
        document_type: str = "text",
        url: str | None = None,
        metadata: dict | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Create a new document with metadata.

        PATTERN: Validation before database insert

        Args:
            title: Document title
            content: Full document content
            source_id: UUID of source
            document_type: Type (text, pdf, html, etc.)
            url: Optional source URL
            metadata: Optional metadata dict

        Returns:
            Tuple of (success, {document_id: str} or {error: str})

        Example:
            >>> success, result = await service.create_document(
            ...     title="My Document",
            ...     content="Full text here...",
            ...     source_id="source-uuid",
            ...     metadata={"author": "John Doe"}
            ... )
            >>> if success:
            ...     doc_id = result["document_id"]
        """
        try:
            # Validation
            if not title or not title.strip():
                return False, {"error": "Title is required"}

            if not content or not content.strip():
                return False, {"error": "Content is required"}

            async with self.db_pool.acquire() as conn:
                # Insert document
                row = await conn.fetchrow(
                    """
                    INSERT INTO documents (
                        title, content, source_id, document_type, url, metadata, status
                    )
                    VALUES ($1, $2, $3::uuid, $4, $5, $6, 'pending')
                    RETURNING id, title, created_at
                    """,
                    title,
                    content,
                    source_id,
                    document_type,
                    url,
                    metadata or {}
                )

            return True, {
                "document_id": str(row["id"]),
                "title": row["title"],
                "created_at": row["created_at"].isoformat(),
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error creating document: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return False, {"error": f"Error creating document: {str(e)}"}

    async def update_document(
        self,
        document_id: str,
        title: str | None = None,
        content: str | None = None,
        metadata: dict | None = None,
        status: str | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Update document fields.

        Args:
            document_id: UUID of document
            title: Optional new title
            content: Optional new content
            metadata: Optional metadata update (replaces existing)
            status: Optional status update

        Returns:
            Tuple of (success, {document: dict} or {error: str})
        """
        try:
            # Build SET clause dynamically
            set_clauses = []
            params = [document_id]
            param_idx = 2

            if title is not None:
                set_clauses.append(f"title = ${param_idx}")
                params.append(title)
                param_idx += 1

            if content is not None:
                set_clauses.append(f"content = ${param_idx}")
                params.append(content)
                param_idx += 1

            if metadata is not None:
                set_clauses.append(f"metadata = ${param_idx}")
                params.append(metadata)
                param_idx += 1

            if status is not None:
                set_clauses.append(f"status = ${param_idx}")
                params.append(status)
                param_idx += 1

            if not set_clauses:
                return False, {"error": "No fields to update"}

            set_clauses.append("updated_at = NOW()")

            async with self.db_pool.acquire() as conn:
                query = f"""
                    UPDATE documents
                    SET {', '.join(set_clauses)}
                    WHERE id = $1::uuid
                    RETURNING *
                """
                row = await conn.fetchrow(query, *params)

            if not row:
                return False, {"error": f"Document {document_id} not found"}

            return True, {"document": dict(row)}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error updating document: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False, {"error": f"Error updating document: {str(e)}"}

    async def delete_document(self, document_id: str) -> tuple[bool, dict[str, Any]]:
        """Delete document and associated vectors.

        PATTERN: Coordinate database and vector deletion

        Args:
            document_id: UUID of document to delete

        Returns:
            Tuple of (success, {message: str} or {error: str})

        Example:
            >>> success, result = await service.delete_document("uuid-here")
            >>> if success:
            ...     print(result["message"])
        """
        try:
            # Step 1: Delete from vector store
            vector_success = await self.vector_service.delete_vectors(
                filter_condition={"document_id": document_id}
            )

            if not vector_success:
                logger.warning(f"Failed to delete vectors for document {document_id}")
                # Continue with database deletion anyway

            # Step 2: Delete from database (CASCADE deletes chunks)
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM documents WHERE id = $1::uuid",
                    document_id
                )

            # Parse result (e.g., "DELETE 1")
            deleted_count = int(result.split()[-1])

            if deleted_count == 0:
                return False, {"error": f"Document {document_id} not found"}

            return True, {
                "message": f"Document {document_id} deleted successfully",
                "vectors_deleted": vector_success,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error deleting document: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False, {"error": f"Error deleting document: {str(e)}"}
```

### Key Methods Summary

| Method | Purpose | Returns | Notes |
|--------|---------|---------|-------|
| `list_documents` | List with filters/pagination | `tuple[bool, dict]` | Use `exclude_large_fields=True` for MCP |
| `get_document` | Get single document by ID | `tuple[bool, dict]` | Returns full content |
| `create_document` | Create new document | `tuple[bool, dict]` | Validates inputs |
| `update_document` | Update document fields | `tuple[bool, dict]` | Dynamic SET clause |
| `delete_document` | Delete document + vectors | `tuple[bool, dict]` | Coordinates with VectorService |

---

## 2. SourceService

**Responsibility**: Manage ingestion sources and crawl jobs.

### Class Definition

```python
class SourceService:
    """Service for source management (uploads, crawls).

    PATTERN: Simple CRUD service for source tracking
    - Manages source lifecycle: pending → processing → completed/failed
    - Updates crawl job progress
    """

    VALID_SOURCE_TYPES = ["upload", "crawl", "api"]
    VALID_STATUSES = ["pending", "processing", "completed", "failed"]

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize SourceService with database pool.

        Args:
            db_pool: asyncpg connection pool
        """
        self.db_pool = db_pool

    def validate_source_type(self, source_type: str) -> tuple[bool, str]:
        """Validate source type against allowed values."""
        if source_type not in self.VALID_SOURCE_TYPES:
            return (
                False,
                f"Invalid source_type '{source_type}'. Must be one of: {', '.join(self.VALID_SOURCE_TYPES)}",
            )
        return True, ""

    def validate_status(self, status: str) -> tuple[bool, str]:
        """Validate status against allowed values."""
        if status not in self.VALID_STATUSES:
            return (
                False,
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}",
            )
        return True, ""

    async def list_sources(
        self,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[bool, dict[str, Any]]:
        """List sources with optional filters.

        Args:
            filters: Optional filters (source_type, status)
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Tuple of (success, {sources, total_count, page, per_page})
        """
        try:
            filters = filters or {}
            offset = (page - 1) * per_page
            per_page = min(per_page, 50)

            where_clauses = []
            params = []
            param_idx = 1

            if "source_type" in filters:
                source_type = filters["source_type"]
                is_valid, error_msg = self.validate_source_type(source_type)
                if not is_valid:
                    return False, {"error": error_msg}
                where_clauses.append(f"source_type = ${param_idx}")
                params.append(source_type)
                param_idx += 1

            if "status" in filters:
                status = filters["status"]
                is_valid, error_msg = self.validate_status(status)
                if not is_valid:
                    return False, {"error": error_msg}
                where_clauses.append(f"status = ${param_idx}")
                params.append(status)
                param_idx += 1

            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            async with self.db_pool.acquire() as conn:
                # Get total count
                count_query = f"SELECT COUNT(*) FROM sources {where_clause}"
                total_count = await conn.fetchval(count_query, *params)

                # Get paginated sources
                query = f"""
                    SELECT *
                    FROM sources
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """
                params.extend([per_page, offset])
                rows = await conn.fetch(query, *params)

            sources = [dict(row) for row in rows]

            return True, {
                "sources": sources,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing sources: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error listing sources: {e}")
            return False, {"error": f"Error listing sources: {str(e)}"}

    async def create_source(
        self,
        source_type: str,
        url: str | None = None,
        metadata: dict | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Create a new source for document ingestion.

        Args:
            source_type: Type of source (upload, crawl, api)
            url: Optional source URL
            metadata: Optional metadata

        Returns:
            Tuple of (success, {source_id: str} or {error: str})
        """
        try:
            # Validation
            is_valid, error_msg = self.validate_source_type(source_type)
            if not is_valid:
                return False, {"error": error_msg}

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO sources (source_type, url, metadata, status)
                    VALUES ($1, $2, $3, 'pending')
                    RETURNING id, source_type, status, created_at
                    """,
                    source_type,
                    url,
                    metadata or {}
                )

            return True, {
                "source_id": str(row["id"]),
                "source_type": row["source_type"],
                "status": row["status"],
                "created_at": row["created_at"].isoformat(),
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error creating source: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating source: {e}")
            return False, {"error": f"Error creating source: {str(e)}"}

    async def update_source_status(
        self,
        source_id: str,
        status: str,
        error_message: str | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Update source status and optional error message.

        PATTERN: Status lifecycle tracking
        - pending → processing (when ingestion starts)
        - processing → completed (when all documents processed)
        - processing → failed (when error occurs)

        Args:
            source_id: UUID of source
            status: New status
            error_message: Optional error message (for failed status)

        Returns:
            Tuple of (success, {source: dict} or {error: str})
        """
        try:
            # Validation
            is_valid, error_msg = self.validate_status(status)
            if not is_valid:
                return False, {"error": error_msg}

            async with self.db_pool.acquire() as conn:
                if error_message:
                    row = await conn.fetchrow(
                        """
                        UPDATE sources
                        SET status = $2, error_message = $3, updated_at = NOW()
                        WHERE id = $1::uuid
                        RETURNING *
                        """,
                        source_id,
                        status,
                        error_message
                    )
                else:
                    row = await conn.fetchrow(
                        """
                        UPDATE sources
                        SET status = $2, updated_at = NOW()
                        WHERE id = $1::uuid
                        RETURNING *
                        """,
                        source_id,
                        status
                    )

            if not row:
                return False, {"error": f"Source {source_id} not found"}

            return True, {"source": dict(row)}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error updating source status: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating source status: {e}")
            return False, {"error": f"Error updating source status: {str(e)}"}
```

### Key Methods Summary

| Method | Purpose | Returns | Notes |
|--------|---------|---------|-------|
| `list_sources` | List sources with filters | `tuple[bool, dict]` | Filter by type/status |
| `create_source` | Create new source | `tuple[bool, dict]` | Initial status: pending |
| `update_source_status` | Update lifecycle status | `tuple[bool, dict]` | Tracks processing progress |

---

## 3. RAGService (Coordinator)

**Responsibility**: Orchestrate search strategies without direct database access.

### Class Definition

```python
from qdrant_client import QdrantClient
from typing import Protocol


class SearchStrategy(Protocol):
    """Protocol for search strategy implementations."""

    async def search(
        self,
        query: str,
        match_count: int,
        filters: dict | None = None,
    ) -> list[dict]:
        """Execute search strategy."""
        ...


class RAGService:
    """Coordinator service for RAG search strategies.

    PATTERN: Strategy coordinator (extracted from Archon)
    - Thin coordinator that delegates to search strategies
    - No direct database access (strategies handle data)
    - Configuration-driven feature enablement
    - Strategies: base → hybrid → reranking (optional)

    CRITICAL: This is a COORDINATOR, not a database service
    - Does NOT return tuple[bool, dict]
    - Returns list[dict] directly
    - Raises exceptions for errors (caught by routes)
    """

    def __init__(
        self,
        qdrant_client: QdrantClient,
        base_strategy: 'BaseSearchStrategy',
        hybrid_strategy: 'HybridSearchStrategy | None' = None,
        reranking_strategy: 'RerankingStrategy | None' = None,
    ):
        """Initialize RAGService with search strategies.

        Args:
            qdrant_client: QdrantClient for vector operations
            base_strategy: Base vector search strategy (always available)
            hybrid_strategy: Optional hybrid search (vector + full-text)
            reranking_strategy: Optional reranking with CrossEncoder
        """
        self.qdrant_client = qdrant_client
        self.base_strategy = base_strategy
        self.hybrid_strategy = hybrid_strategy
        self.reranking_strategy = reranking_strategy

    async def search_documents(
        self,
        query: str,
        match_count: int = 10,
        search_type: str = "hybrid",
        filters: dict | None = None,
    ) -> list[dict]:
        """Search documents using specified strategy.

        PATTERN: Strategy selection based on search_type
        - "vector": Base vector similarity search
        - "hybrid": Vector + full-text combined (better recall)
        - "rerank": Hybrid + CrossEncoder reranking (best accuracy)

        Args:
            query: Search query text
            match_count: Number of results to return
            search_type: Strategy to use (vector, hybrid, rerank)
            filters: Optional metadata filters (source_id, document_id)

        Returns:
            List of result dicts with:
            - id: chunk ID
            - document_id: parent document ID
            - content: chunk text
            - score: relevance score (0-1)
            - match_type: "vector", "both", "text"

        Raises:
            ValueError: If search_type invalid or strategy not configured

        Example:
            >>> results = await rag_service.search_documents(
            ...     query="What is RAG?",
            ...     match_count=5,
            ...     search_type="hybrid",
            ...     filters={"source_id": "uuid-here"}
            ... )
            >>> for result in results:
            ...     print(f"{result['score']:.2f}: {result['content'][:100]}")
        """
        # Validate search_type
        if search_type not in ["vector", "hybrid", "rerank"]:
            raise ValueError(
                f"Invalid search_type '{search_type}'. Must be: vector, hybrid, or rerank"
            )

        # Select strategy
        if search_type == "vector":
            strategy = self.base_strategy

        elif search_type == "hybrid":
            if not self.hybrid_strategy:
                raise ValueError("Hybrid search not configured")
            strategy = self.hybrid_strategy

        elif search_type == "rerank":
            if not self.reranking_strategy:
                raise ValueError("Reranking not configured")
            strategy = self.reranking_strategy

        # Execute search
        results = await strategy.search(
            query=query,
            match_count=match_count,
            filters=filters or {}
        )

        return results

    async def get_collection_stats(self) -> dict:
        """Get vector collection statistics.

        Returns:
            Dict with:
            - total_vectors: Total number of vectors
            - indexed_vectors: Number of indexed vectors
            - collection_name: Name of collection
        """
        collection_info = await self.qdrant_client.get_collection(
            collection_name="documents"
        )

        return {
            "total_vectors": collection_info.vectors_count,
            "indexed_vectors": collection_info.indexed_vectors_count,
            "collection_name": "documents",
        }
```

### Key Methods Summary

| Method | Purpose | Returns | Notes |
|--------|---------|---------|-------|
| `search_documents` | Execute search strategy | `list[dict]` | Strategy selection based on search_type |
| `get_collection_stats` | Get vector stats | `dict` | Useful for monitoring |

**IMPORTANT**: RAGService does NOT use tuple[bool, dict] pattern because it's a coordinator, not a database service. It delegates to strategies and raises exceptions on errors.

---

## 4. EmbeddingService

**Responsibility**: Generate embeddings using OpenAI or local models.

### Class Definition

```python
from dataclasses import dataclass, field
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingBatchResult:
    """Result of batch embedding operation.

    PATTERN: Track successes and failures separately (Gotcha #1)
    - NEVER store null/zero embeddings (corrupts search)
    - Track failed items for retry
    - Separate success/failure counts
    """
    embeddings: list[list[float]] = field(default_factory=list)
    failed_items: list[dict] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0

    def add_success(self, embedding: list[float], text: str):
        """Add successful embedding."""
        self.embeddings.append(embedding)
        self.success_count += 1

    def add_failure(self, text: str, error: Exception):
        """Add failed item for retry."""
        self.failed_items.append({
            "text": text[:100],  # Truncate for logging
            "error": str(error),
        })
        self.failure_count += 1


class EmbeddingService:
    """Service for generating text embeddings.

    PATTERN: Multi-provider design with OpenAI as MVP
    - OpenAI text-embedding-3-small for MVP (1536 dimensions)
    - Future: Sentence-BERT for local embeddings
    - Batch processing for efficiency (up to 100 texts)
    - Rate limit handling with quota exhaustion detection

    CRITICAL GOTCHA #1: Never store null embeddings on quota exhaustion
    """

    EMBEDDING_MODELS = {
        "openai": {
            "model": "text-embedding-3-small",
            "dimension": 1536,
            "max_batch_size": 100,
        },
        "local": {
            "model": "all-MiniLM-L6-v2",
            "dimension": 384,
            "max_batch_size": 32,
        },
    }

    def __init__(self, provider: str = "openai", api_key: str | None = None):
        """Initialize EmbeddingService with provider.

        Args:
            provider: Provider to use (openai, local)
            api_key: Optional OpenAI API key (uses env var if not provided)
        """
        self.provider = provider
        self.config = self.EMBEDDING_MODELS.get(provider)

        if not self.config:
            raise ValueError(f"Invalid provider '{provider}'. Must be: openai or local")

        if provider == "openai":
            self.client = AsyncOpenAI(api_key=api_key)
        elif provider == "local":
            # Future: Initialize sentence-transformers model
            raise NotImplementedError("Local embeddings not yet implemented")

    async def create_embedding(self, text: str) -> list[float]:
        """Create embedding for single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats

        Raises:
            Exception: If embedding fails
        """
        if self.provider == "openai":
            try:
                response = await self.client.embeddings.create(
                    model=self.config["model"],
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Error creating embedding: {e}")
                raise

    async def create_embeddings_batch(
        self,
        texts: list[str],
        stop_on_quota_exhaustion: bool = True,
    ) -> EmbeddingBatchResult:
        """Create embeddings for batch of texts.

        PATTERN: Safe batch processing with quota handling (Gotcha #1)
        - Process in batches of max_batch_size
        - Track successes and failures separately
        - STOP on quota exhaustion (don't corrupt data)

        Args:
            texts: List of texts to embed
            stop_on_quota_exhaustion: If True, stop on quota error

        Returns:
            EmbeddingBatchResult with embeddings and failures

        Example:
            >>> result = await service.create_embeddings_batch(texts)
            >>> if result.failure_count > 0:
            ...     print(f"Failed: {result.failure_count}, retry later")
            >>> for embedding in result.embeddings:
            ...     await store_embedding(embedding)  # Only store successes
        """
        result = EmbeddingBatchResult()
        max_batch = self.config["max_batch_size"]

        if self.provider == "openai":
            # Process in batches
            for i in range(0, len(texts), max_batch):
                batch = texts[i:i + max_batch]

                try:
                    response = await self.client.embeddings.create(
                        model=self.config["model"],
                        input=batch
                    )

                    # Add all successful embeddings
                    for text, emb_data in zip(batch, response.data):
                        result.add_success(emb_data.embedding, text)

                except Exception as e:
                    error_str = str(e).lower()

                    # Check for quota exhaustion (Gotcha #1)
                    if "insufficient_quota" in error_str and stop_on_quota_exhaustion:
                        logger.error(f"Quota exhausted after {result.success_count} embeddings")
                        # Mark all remaining texts as failed
                        for remaining_text in texts[result.success_count:]:
                            result.add_failure(remaining_text, e)
                        break  # STOP - don't corrupt data

                    # Other errors: log and continue
                    logger.error(f"Batch embedding error: {e}")
                    for text in batch:
                        result.add_failure(text, e)

        return result
```

### Key Methods Summary

| Method | Purpose | Returns | Notes |
|--------|---------|---------|-------|
| `create_embedding` | Single text embedding | `list[float]` | Raises on error |
| `create_embeddings_batch` | Batch embedding | `EmbeddingBatchResult` | Tracks successes/failures |

**CRITICAL**: EmbeddingService uses `EmbeddingBatchResult` dataclass to avoid storing null embeddings (Gotcha #1).

---

## 5. VectorService

**Responsibility**: Manage vector operations in Qdrant.

### Class Definition

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class VectorService:
    """Service for vector operations in Qdrant.

    PATTERN: Vector database abstraction
    - Manages Qdrant collection operations
    - Handles vector upsert, search, delete
    - Metadata filtering support

    CRITICAL GOTCHA #5: Dimension must match embedding model
    """

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = "documents",
        dimension: int = 1536,
    ):
        """Initialize VectorService.

        Args:
            client: QdrantClient instance
            collection_name: Name of collection
            dimension: Vector dimension (must match embedding model)
        """
        self.client = client
        self.collection_name = collection_name
        self.dimension = dimension

    async def ensure_collection(self):
        """Ensure collection exists with correct configuration.

        PATTERN: Idempotent collection creation
        - Creates collection if not exists
        - Validates dimension if exists
        """
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)

            if not exists:
                # Create collection
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection '{self.collection_name}' with dimension {self.dimension}")
            else:
                # Validate dimension
                info = await self.client.get_collection(self.collection_name)
                if info.config.params.vectors.size != self.dimension:
                    raise ValueError(
                        f"Collection dimension mismatch: expected {self.dimension}, "
                        f"got {info.config.params.vectors.size}"
                    )

        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
            raise

    async def upsert_vectors(
        self,
        vectors: list[list[float]],
        payloads: list[dict],
        ids: list[str] | None = None,
    ) -> None:
        """Upsert vectors with payloads into collection.

        PATTERN: Batch upsert with validation (Gotcha #5)

        Args:
            vectors: List of embedding vectors
            payloads: List of metadata dicts (document_id, chunk_index, text)
            ids: Optional list of IDs (generates UUIDs if not provided)

        Raises:
            ValueError: If dimension mismatch or length mismatch

        Example:
            >>> await service.upsert_vectors(
            ...     vectors=[embedding1, embedding2],
            ...     payloads=[
            ...         {"document_id": "doc1", "text": "chunk1"},
            ...         {"document_id": "doc1", "text": "chunk2"},
            ...     ]
            ... )
        """
        # Validation
        if len(vectors) != len(payloads):
            raise ValueError(f"Vectors ({len(vectors)}) and payloads ({len(payloads)}) length mismatch")

        # Validate dimensions (Gotcha #5)
        for i, vector in enumerate(vectors):
            if len(vector) != self.dimension:
                raise ValueError(
                    f"Vector {i} dimension mismatch: expected {self.dimension}, got {len(vector)}"
                )

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(vectors))]

        # Create points
        points = [
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            for point_id, vector, payload in zip(ids, vectors, payloads)
        ]

        # Upsert
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        logger.info(f"Upserted {len(points)} vectors to '{self.collection_name}'")

    async def search_vectors(
        self,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: float = 0.05,
        filter_condition: dict | None = None,
    ) -> list[dict]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding
            limit: Number of results
            score_threshold: Minimum similarity score (0-1)
            filter_condition: Optional metadata filters

        Returns:
            List of result dicts with id, score, payload

        Example:
            >>> results = await service.search_vectors(
            ...     query_vector=embedding,
            ...     limit=5,
            ...     filter_condition={"document_id": "doc-uuid"}
            ... )
        """
        # Validate dimension (Gotcha #5)
        if len(query_vector) != self.dimension:
            raise ValueError(
                f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}"
            )

        # Build filter
        qdrant_filter = None
        if filter_condition:
            conditions = []
            for key, value in filter_condition.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            qdrant_filter = Filter(must=conditions)

        # Search
        search_result = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=qdrant_filter
        )

        # Format results
        results = [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in search_result
        ]

        return results

    async def delete_vectors(
        self,
        filter_condition: dict | None = None,
        ids: list[str] | None = None,
    ) -> bool:
        """Delete vectors by filter or IDs.

        Args:
            filter_condition: Delete by metadata (e.g., {"document_id": "uuid"})
            ids: Delete by specific IDs

        Returns:
            True if deletion successful

        Example:
            >>> # Delete all vectors for a document
            >>> await service.delete_vectors(
            ...     filter_condition={"document_id": "doc-uuid"}
            ... )
        """
        try:
            if ids:
                # Delete by IDs
                await self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=ids
                )
            elif filter_condition:
                # Delete by filter
                conditions = []
                for key, value in filter_condition.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                qdrant_filter = Filter(must=conditions)

                await self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qdrant_filter
                )
            else:
                raise ValueError("Must provide either filter_condition or ids")

            logger.info(f"Deleted vectors from '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
```

### Key Methods Summary

| Method | Purpose | Returns | Notes |
|--------|---------|---------|-------|
| `ensure_collection` | Create/validate collection | `None` | Idempotent |
| `upsert_vectors` | Insert/update vectors | `None` | Validates dimensions |
| `search_vectors` | Similarity search | `list[dict]` | Supports metadata filters |
| `delete_vectors` | Delete by filter/IDs | `bool` | Useful for cleanup |

---

## 6. Connection Pool Setup (Avoiding Gotcha #2)

**CRITICAL**: FastAPI connection pool setup to avoid deadlock.

### FastAPI Lifespan Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
import asyncpg
from qdrant_client import QdrantClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with connection pools.

    PATTERN: Connection pools in lifespan (Gotcha #2)
    - Create pools at startup
    - Store in app.state
    - Close pools at shutdown
    - NEVER create pools in dependency functions
    """
    # Startup: Create connection pools
    app.state.db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        database="rag_service",
        user="postgres",
        password="password",
        min_size=10,
        max_size=20,
    )

    app.state.qdrant_client = QdrantClient(
        host="localhost",
        port=6333,
    )

    logger.info("Connection pools created")

    yield  # Application runs

    # Shutdown: Close connection pools
    await app.state.db_pool.close()
    await app.state.qdrant_client.close()

    logger.info("Connection pools closed")


# Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)


# Dependency functions (CORRECT: Return pool, not connection)
async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Get database pool from app state.

    CRITICAL: Return POOL, not connection (Gotcha #2)
    - Services acquire connections as needed
    - Connections released immediately after query
    - Prevents pool exhaustion
    """
    return request.app.state.db_pool


async def get_qdrant_client(request: Request) -> QdrantClient:
    """Get Qdrant client from app state."""
    return request.app.state.qdrant_client


# Service initialization in routes
@app.get("/documents")
async def list_documents(
    pool: asyncpg.Pool = Depends(get_db_pool),
    qdrant: QdrantClient = Depends(get_qdrant_client),
):
    """Route example with service initialization.

    PATTERN: Initialize services per-request
    - Pass pool to service (not connection)
    - Service acquires connection when needed
    """
    vector_service = VectorService(qdrant, "documents")
    doc_service = DocumentService(pool, vector_service)

    success, result = await doc_service.list_documents()

    if not success:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
```

### Why This Pattern Prevents Deadlock

**WRONG Pattern** (causes deadlock):
```python
# ❌ Each dependency acquires connection
async def get_db_connection(pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        yield conn  # Held until request completes

@app.get("/route")
async def route(
    conn1=Depends(get_db_connection),  # Connection 1
    conn2=Depends(get_db_connection),  # Connection 2
):
    # With pool size 10, only 5 concurrent requests possible!
    pass
```

**CORRECT Pattern** (no deadlock):
```python
# ✅ Share pool, acquire connections as needed
async def get_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool

@app.get("/route")
async def route(pool: asyncpg.Pool = Depends(get_pool)):
    service = DocumentService(pool)
    # Service acquires connection only during query
    # Connection released immediately
    return await service.list_documents()
```

---

## 7. Service Layer Class Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Routes                        │
│                                                              │
│  GET  /documents     → DocumentService.list_documents()     │
│  POST /documents     → DocumentService.create_document()    │
│  GET  /search        → RAGService.search_documents()        │
│  POST /sources       → SourceService.create_source()        │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        ↓                                           ↓
┌───────────────────┐                    ┌──────────────────┐
│  DocumentService  │                    │  SourceService   │
│                   │                    │                  │
│ - db_pool         │                    │ - db_pool        │
│ - vector_service  │                    │                  │
│                   │                    │ Methods:         │
│ Methods:          │                    │ - list_sources   │
│ - list_documents  │                    │ - create_source  │
│ - get_document    │                    │ - update_status  │
│ - create_document │                    │                  │
│ - update_document │                    │ Returns:         │
│ - delete_document │                    │ tuple[bool,dict] │
│                   │                    └──────────────────┘
│ Returns:          │
│ tuple[bool, dict] │
└─────────┬─────────┘
          │
          │ uses
          ↓
┌───────────────────┐
│  VectorService    │
│                   │
│ - qdrant_client   │
│ - collection_name │
│ - dimension       │
│                   │
│ Methods:          │
│ - upsert_vectors  │
│ - search_vectors  │
│ - delete_vectors  │
│                   │
│ Returns:          │
│ None / list[dict] │
└─────────┬─────────┘
          │
          │ uses
          ↓
┌───────────────────┐
│  QdrantClient     │
│  (external lib)   │
└───────────────────┘


┌───────────────────┐
│   RAGService      │
│   (coordinator)   │
│                   │
│ - qdrant_client   │
│ - base_strategy   │
│ - hybrid_strategy │
│ - reranking_strat │
│                   │
│ Methods:          │
│ - search_documents│
│                   │
│ Returns:          │
│ list[dict]        │
└─────────┬─────────┘
          │
          │ delegates to
          ↓
┌───────────────────────────────────────┐
│         Search Strategies             │
│                                       │
│  ┌─────────────────────┐             │
│  │ BaseSearchStrategy  │             │
│  │ - vector search     │             │
│  └─────────────────────┘             │
│                                       │
│  ┌─────────────────────┐             │
│  │ HybridSearchStrat   │             │
│  │ - vector + ts_vector│             │
│  └─────────────────────┘             │
│                                       │
│  ┌─────────────────────┐             │
│  │ RerankingStrategy   │             │
│  │ - CrossEncoder      │             │
│  └─────────────────────┘             │
└───────────────────────────────────────┘


┌───────────────────┐
│ EmbeddingService  │
│                   │
│ - openai_client   │
│ - provider        │
│                   │
│ Methods:          │
│ - create_embedding│
│ - create_batch    │
│                   │
│ Returns:          │
│ list[float]       │
│ EmbeddingBatchRes │
└───────────────────┘


Connection Pool Flow (Gotcha #2):
═══════════════════════════════════
FastAPI Lifespan
    ↓
app.state.db_pool (asyncpg.Pool)
    ↓
Dependency: get_db_pool() → returns Pool
    ↓
Service.__init__(pool)
    ↓
Service.method():
    async with pool.acquire() as conn:
        # Connection acquired only during query
        await conn.fetch(...)
    # Connection released immediately
```

---

## 8. Service Dependencies Matrix

| Service | Depends On | Returns | Use Case |
|---------|-----------|---------|----------|
| **DocumentService** | db_pool, VectorService | `tuple[bool, dict]` | Document CRUD |
| **SourceService** | db_pool | `tuple[bool, dict]` | Source management |
| **RAGService** | QdrantClient, Strategies | `list[dict]` | Search coordination |
| **EmbeddingService** | OpenAI client | `list[float]` / `EmbeddingBatchResult` | Embedding generation |
| **VectorService** | QdrantClient | `None` / `list[dict]` / `bool` | Vector operations |

---

## 9. Service Initialization Example

```python
# In main.py or route initialization

from services.document_service import DocumentService
from services.source_service import SourceService
from services.rag_service import RAGService
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService

# From app.state (lifespan)
db_pool = app.state.db_pool
qdrant_client = app.state.qdrant_client

# Initialize vector and embedding services
vector_service = VectorService(
    client=qdrant_client,
    collection_name="documents",
    dimension=1536
)

embedding_service = EmbeddingService(
    provider="openai",
    api_key=settings.OPENAI_API_KEY
)

# Initialize CRUD services
document_service = DocumentService(
    db_pool=db_pool,
    vector_service=vector_service
)

source_service = SourceService(
    db_pool=db_pool
)

# Initialize RAG service with strategies
from services.search.base_search_strategy import BaseSearchStrategy
from services.search.hybrid_search_strategy import HybridSearchStrategy

base_strategy = BaseSearchStrategy(
    qdrant_client=qdrant_client,
    embedding_service=embedding_service
)

hybrid_strategy = HybridSearchStrategy(
    qdrant_client=qdrant_client,
    db_pool=db_pool,
    embedding_service=embedding_service
)

rag_service = RAGService(
    qdrant_client=qdrant_client,
    base_strategy=base_strategy,
    hybrid_strategy=hybrid_strategy,
    reranking_strategy=None  # Optional
)
```

---

## 10. Key Patterns Summary

### Pattern 1: tuple[bool, dict] for Database Services

**All database services (DocumentService, SourceService) use this pattern:**

```python
async def method(...) -> tuple[bool, dict]:
    try:
        # Database operation
        return True, {"data": result}
    except Exception as e:
        logger.error(f"Error: {e}")
        return False, {"error": str(e)}
```

**Why**:
- Consistent error handling across all services
- No exceptions propagated to routes
- Easy to check success before using result

### Pattern 2: Coordinator Without Database Access

**RAGService is a coordinator, NOT a database service:**

```python
async def search_documents(...) -> list[dict]:
    # Delegates to strategies
    # Raises exceptions (caught by routes)
    # Returns data directly
```

**Why**:
- Thin coordinator layer
- Strategies handle data access
- Clear separation of concerns

### Pattern 3: Connection Pool in Lifespan

**Critical pattern to avoid deadlock (Gotcha #2):**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(...)
    yield
    await app.state.db_pool.close()

async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool
```

**Why**:
- Pool shared across all requests
- Connections acquired only when needed
- Prevents pool exhaustion

### Pattern 4: Batch Result with Failure Tracking

**EmbeddingBatchResult tracks successes and failures separately (Gotcha #1):**

```python
result = await embedding_service.create_embeddings_batch(texts)
# Only store successful embeddings
for embedding in result.embeddings:
    await store_embedding(embedding)
# Retry failures later
for failure in result.failed_items:
    await queue_for_retry(failure)
```

**Why**:
- NEVER stores null embeddings (corrupts search)
- Clear tracking for retry logic
- Quota exhaustion handling

---

## 11. Validation Checklist

### Service Layer Completeness

- [x] **DocumentService** defined with 5 methods (list, get, create, update, delete)
- [x] **SourceService** defined with 3 methods (list, create, update_status)
- [x] **RAGService** defined as coordinator with search_documents()
- [x] **EmbeddingService** defined with batch processing
- [x] **VectorService** defined with Qdrant operations
- [x] All database services return `tuple[bool, dict]`
- [x] RAGService returns `list[dict]` (coordinator pattern)
- [x] Connection pool setup documented (Gotcha #2)
- [x] EmbeddingBatchResult dataclass defined (Gotcha #1)
- [x] Class diagram showing dependencies
- [x] Service initialization example provided
- [x] All critical gotchas addressed

### Gotcha Coverage

- [x] **Gotcha #1**: EmbeddingBatchResult prevents null embeddings
- [x] **Gotcha #2**: Connection pool in lifespan, not per-request
- [x] **Gotcha #3**: asyncpg $1, $2 syntax used throughout
- [x] **Gotcha #5**: Dimension validation in VectorService
- [x] **Gotcha #7**: exclude_large_fields for MCP optimization
- [x] **Gotcha #8**: async with for all connection management

---

## 12. Next Steps

**After Service Layer Design**:

1. **Task 7**: Docker Compose Configuration
   - Define PostgreSQL, Qdrant, FastAPI services
   - Health checks and volume mounting
   - Environment variable template

2. **Task 8**: Cost & Performance Analysis
   - Embedding costs calculation
   - Infrastructure monthly costs
   - Performance benchmarks

3. **Task 9**: Testing Strategy
   - Unit tests for all service methods
   - Integration tests for API routes
   - MCP tool testing patterns

---

## Completion Summary

**Task 6 - Service Layer Architecture: COMPLETE**

**Deliverables**:
- ✅ 5 service classes fully defined with methods
- ✅ All methods documented with docstrings
- ✅ tuple[bool, dict] pattern applied consistently
- ✅ Connection pool setup to avoid Gotcha #2
- ✅ EmbeddingBatchResult to avoid Gotcha #1
- ✅ Class diagram showing dependencies
- ✅ Service initialization example
- ✅ All critical gotchas addressed

**Files Created**:
- prps/rag_service_research/sections/06_service_layer.md

**Patterns Applied**:
- Service layer with asyncpg (examples/01_service_layer_pattern.py)
- tuple[bool, dict] returns (task-manager pattern)
- Strategy coordinator (Archon RAG pattern)
- Connection pool in lifespan (FastAPI best practice)
- Batch result with failure tracking (Gotcha #1 solution)

**Ready for Integration**: This service layer design can now be used in Task 11 (Final Assembly) to complete the ARCHITECTURE.md document.
