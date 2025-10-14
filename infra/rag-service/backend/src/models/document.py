"""Document and Chunk Pydantic models for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DocumentCreate(BaseModel):
    """Request model for creating a document."""

    source_id: UUID
    title: str = Field(..., min_length=1, max_length=1000)
    document_type: str | None = None
    url: str | None = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate that title is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()


class DocumentUpdate(BaseModel):
    """Request model for updating a document."""

    title: str | None = None
    document_type: str | None = None
    url: str | None = None
    metadata: dict | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        """Validate that title is not empty or whitespace only if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v is not None else None


class DocumentResponse(BaseModel):
    """Response model for document data."""

    id: UUID
    source_id: UUID
    title: str
    document_type: str | None
    url: str | None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChunkCreate(BaseModel):
    """Request model for creating a chunk."""

    document_id: UUID
    chunk_index: int = Field(..., ge=0)
    text: str = Field(..., min_length=1)
    token_count: int | None = Field(None, ge=0)
    metadata: dict = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Validate that text is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Chunk text cannot be empty or whitespace")
        return v


class ChunkResponse(BaseModel):
    """Response model for chunk data."""

    id: UUID
    document_id: UUID
    chunk_index: int
    text: str
    token_count: int | None
    metadata: dict
    created_at: datetime

    model_config = {"from_attributes": True}
