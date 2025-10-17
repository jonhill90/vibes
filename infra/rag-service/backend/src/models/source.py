"""Source Pydantic models for request/response validation."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Type aliases for source enums
SourceType = Literal["upload", "crawl", "api"]
CollectionType = Literal["documents", "code", "media"]
SourceStatus = Literal["active", "processing", "failed", "archived"]


class SourceCreate(BaseModel):
    """Request model for creating a source."""

    source_type: SourceType
    enabled_collections: list[CollectionType] = Field(default=["documents"])
    url: str | None = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("enabled_collections")
    @classmethod
    def validate_collections(cls, v: list[CollectionType]) -> list[CollectionType]:
        """Ensure at least one collection enabled and no duplicates."""
        if not v or len(v) == 0:
            return ["documents"]  # Default to documents
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for item in v:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None, info) -> str | None:
        """Validate URL is provided for crawl and api source types."""
        # Access source_type from the data being validated
        if info.data.get("source_type") in ["crawl", "api"] and not v:
            raise ValueError("URL is required for crawl and api source types")
        return v


class SourceUpdate(BaseModel):
    """Request model for updating a source."""

    status: SourceStatus | None = None
    metadata: dict | None = None
    error_message: str | None = None


class SourceResponse(BaseModel):
    """Response model for source data."""

    id: UUID
    source_type: SourceType
    enabled_collections: list[CollectionType]
    url: str | None
    status: SourceStatus
    metadata: dict
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
