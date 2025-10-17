"""Pydantic response models for RAG Service API endpoints.

This module defines all response models with:
- Consistent structure across all endpoints
- OpenAPI documentation for automatic schema generation
- Type safety for API responses
- Error response patterns

Pattern: Example 05 (FastAPI route pattern)
Reference: infra/task-manager/backend/src/api/routes/
"""

from typing import Optional, Any
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Response model for single document operations.

    Used for GET /api/documents/{id} and document creation responses.
    """

    id: str = Field(..., description="Document UUID")
    source_id: str = Field(..., description="Parent source UUID")
    title: str = Field(..., description="Document title")
    document_type: Optional[str] = Field(None, description="Document type (pdf, markdown, etc.)")
    url: Optional[str] = Field(None, description="Document URL if available")
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")
    chunk_count: Optional[int] = Field(None, description="Number of chunks extracted")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "source_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Machine Learning Best Practices",
                "document_type": "pdf",
                "url": "https://example.com/ml-guide.pdf",
                "created_at": "2025-10-14T10:30:00Z",
                "updated_at": "2025-10-14T10:30:00Z",
                "chunk_count": 42
            }
        }
    }


class DocumentListResponse(BaseModel):
    """Response model for paginated document list.

    Used for GET /api/documents with pagination support.
    """

    documents: list[DocumentResponse] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents matching filters")
    page: int = Field(..., description="Current page number (1-indexed)")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="True if there are more pages")
    has_prev: bool = Field(..., description="True if there are previous pages")

    model_config = {
        "json_schema_extra": {
            "example": {
                "documents": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "source_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "ML Best Practices",
                        "document_type": "pdf",
                        "url": None,
                        "created_at": "2025-10-14T10:30:00Z",
                        "updated_at": "2025-10-14T10:30:00Z",
                        "chunk_count": 42
                    }
                ],
                "total_count": 156,
                "page": 1,
                "per_page": 10,
                "has_next": True,
                "has_prev": False
            }
        }
    }


class SearchResultItem(BaseModel):
    """Single search result item.

    Contains chunk text, relevance score, and metadata.
    """

    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Relevance score (0-1, higher is better)", ge=0.0, le=1.0)
    match_type: Optional[str] = Field(None, description="Match type: 'vector', 'text', or 'both'")
    source_id: Optional[str] = Field(None, description="Source UUID this result came from")
    collection_type: Optional[str] = Field(None, description="Collection type: 'documents', 'code', or 'media'")
    metadata: dict[str, Any] = Field(..., description="Chunk metadata (document_id, source_id, etc.)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "chunk_id": "chunk-123-456",
                "text": "Machine learning is a subset of artificial intelligence...",
                "score": 0.87,
                "match_type": "both",
                "source_id": "123e4567-e89b-12d3-a456-426614174000",
                "collection_type": "documents",
                "metadata": {
                    "document_id": "550e8400-e29b-41d4-a716-446655440000",
                    "source_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "ML Best Practices",
                    "chunk_index": 5
                }
            }
        }
    }


class SearchResponse(BaseModel):
    """Response model for search operations.

    Used for POST /api/search with performance metrics.
    """

    results: list[SearchResultItem] = Field(..., description="Ranked search results")
    query: str = Field(..., description="Original search query")
    search_type: str = Field(..., description="Search strategy used: 'vector', 'hybrid', or 'auto'")
    count: int = Field(..., description="Number of results returned")
    latency_ms: float = Field(..., description="Search latency in milliseconds")

    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "chunk_id": "chunk-123-456",
                        "text": "Machine learning best practices include...",
                        "score": 0.87,
                        "match_type": "both",
                        "metadata": {
                            "document_id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "ML Guide"
                        }
                    }
                ],
                "query": "machine learning best practices",
                "search_type": "hybrid",
                "count": 1,
                "latency_ms": 42.3
            }
        }
    }


class SourceResponse(BaseModel):
    """Response model for single source operations.

    Used for GET /api/sources/{id} and source creation responses.
    """

    id: str = Field(..., description="Source UUID")
    source_type: str = Field(..., description="Source type: 'upload', 'crawl', or 'api'")
    enabled_collections: list[str] = Field(
        default=["documents"],
        description="Collections enabled for this source: 'documents', 'code', 'media'"
    )
    collection_names: Optional[dict[str, str]] = Field(
        None,
        description="Mapping of collection_type to Qdrant collection name (e.g., {'documents': 'AI_Knowledge_documents'})"
    )
    url: Optional[str] = Field(None, description="Source URL")
    title: Optional[str] = Field(None, description="Human-readable title (from metadata)")
    status: str = Field(..., description="Status: 'pending', 'processing', 'completed', or 'failed'")
    metadata: Optional[dict] = Field(None, description="Source metadata as JSON")
    error_message: Optional[str] = Field(None, description="Error message if status is 'failed'")
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "source_type": "upload",
                "enabled_collections": ["documents", "code"],
                "collection_names": {
                    "documents": "AI_Knowledge_documents",
                    "code": "AI_Knowledge_code"
                },
                "url": None,
                "status": "completed",
                "metadata": {"uploaded_by": "user-123"},
                "error_message": None,
                "created_at": "2025-10-14T10:00:00Z",
                "updated_at": "2025-10-14T10:30:00Z"
            }
        }
    }


class SourceListResponse(BaseModel):
    """Response model for paginated source list.

    Used for GET /api/sources with pagination support.
    """

    sources: list[SourceResponse] = Field(..., description="List of sources")
    total_count: int = Field(..., description="Total number of sources matching filters")
    limit: int = Field(..., description="Maximum items returned")
    offset: int = Field(..., description="Number of items skipped")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sources": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "source_type": "upload",
                        "url": None,
                        "status": "completed",
                        "metadata": {},
                        "error_message": None,
                        "created_at": "2025-10-14T10:00:00Z",
                        "updated_at": "2025-10-14T10:30:00Z"
                    }
                ],
                "total_count": 25,
                "limit": 50,
                "offset": 0
            }
        }
    }


class ErrorResponse(BaseModel):
    """Structured error response for all API errors.

    Provides consistent error format across all endpoints.
    """

    success: bool = Field(default=False, description="Always False for errors")
    error: str = Field(..., description="High-level error message")
    detail: Optional[str] = Field(None, description="Detailed error explanation")
    suggestion: Optional[str] = Field(None, description="Suggestion for fixing the error")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": "Invalid file type",
                "detail": "File extension .exe is not allowed",
                "suggestion": "Upload one of: .pdf, .docx, .txt, .md, .html"
            }
        }
    }


class MessageResponse(BaseModel):
    """Generic success message response.

    Used for operations that don't return specific data (e.g., deletions).
    """

    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Human-readable success message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Document deleted successfully"
            }
        }
    }
