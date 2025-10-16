"""Pydantic request models for RAG Service API endpoints.

This module defines all request validation models with:
- Field-level validation with Pydantic validators
- Type hints for automatic validation
- Custom validators for complex business logic
- Structured error messages for validation failures

Pattern: Example 05 (FastAPI route pattern)
Reference: infra/task-manager/backend/src/api/routes/
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class DocumentUploadRequest(BaseModel):
    """Request model for document upload (metadata only, file separate).

    Note: File upload uses multipart/form-data with UploadFile,
    this model handles metadata fields.
    """

    source_id: str = Field(
        ...,
        description="UUID of the source this document belongs to",
        min_length=1
    )

    title: Optional[str] = Field(
        default=None,
        description="Document title (auto-generated from filename if not provided)",
        max_length=500
    )

    tags: Optional[list[str]] = Field(
        default=None,
        description="Optional tags for document categorization"
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        """Validate tags list has reasonable length."""
        if v is not None and len(v) > 20:
            raise ValueError("Maximum 20 tags allowed")
        return v


class SearchRequest(BaseModel):
    """Request model for semantic search operations.

    Supports both vector-only and hybrid search with optional filters.
    """

    query: str = Field(
        ...,
        description="Search query text",
        min_length=1,
        max_length=2000
    )

    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=100
    )

    source_id: Optional[str] = Field(
        default=None,
        description="Optional source UUID filter"
    )

    search_type: str = Field(
        default="vector",
        description="Search strategy: 'vector', 'hybrid', or 'auto'"
    )

    @field_validator("search_type")
    @classmethod
    def validate_search_type(cls, v):
        """Validate search_type is one of allowed values."""
        allowed_types = ["vector", "hybrid", "auto"]
        if v not in allowed_types:
            raise ValueError(
                f"search_type must be one of: {', '.join(allowed_types)}. Got: {v}"
            )
        return v


class SourceCreateRequest(BaseModel):
    """Request model for creating a new source.

    Sources represent ingestion origins (upload, crawl, api).
    """

    source_type: str = Field(
        ...,
        description="Source type: 'upload', 'crawl', or 'api'"
    )

    url: Optional[str] = Field(
        default=None,
        description="Source URL (required for 'crawl' and 'api' types)",
        max_length=2000
    )

    title: Optional[str] = Field(
        default=None,
        description="Optional human-readable title for the source",
        max_length=500
    )

    metadata: Optional[dict] = Field(
        default=None,
        description="Optional metadata as JSON object"
    )

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        """Validate source_type is one of allowed values."""
        allowed_types = ["upload", "crawl", "api"]
        if v not in allowed_types:
            raise ValueError(
                f"source_type must be one of: {', '.join(allowed_types)}. Got: {v}"
            )
        return v

    @field_validator("url")
    @classmethod
    def validate_url_required_for_crawl(cls, v, info):
        """Validate that URL is provided for crawl and api sources."""
        # Access source_type from info.data
        source_type = info.data.get("source_type")

        if source_type in ["crawl", "api"] and not v:
            raise ValueError(
                f"url is required for source_type '{source_type}'"
            )

        return v


class SourceUpdateRequest(BaseModel):
    """Request model for updating an existing source.

    All fields optional for partial updates.
    """

    source_type: Optional[str] = Field(
        default=None,
        description="Source type: 'upload', 'crawl', or 'api'"
    )

    url: Optional[str] = Field(
        default=None,
        description="Source URL",
        max_length=2000
    )

    title: Optional[str] = Field(
        default=None,
        description="Optional human-readable title for the source",
        max_length=500
    )

    status: Optional[str] = Field(
        default=None,
        description="Source status: 'pending', 'processing', 'completed', 'failed'"
    )

    metadata: Optional[dict] = Field(
        default=None,
        description="Optional metadata as JSON object"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error message for failed sources"
    )

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        """Validate source_type if provided."""
        if v is not None:
            allowed_types = ["upload", "crawl", "api"]
            if v not in allowed_types:
                raise ValueError(
                    f"source_type must be one of: {', '.join(allowed_types)}. Got: {v}"
                )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status if provided."""
        if v is not None:
            allowed_statuses = ["pending", "processing", "completed", "failed"]
            if v not in allowed_statuses:
                raise ValueError(
                    f"status must be one of: {', '.join(allowed_statuses)}. Got: {v}"
                )
        return v
