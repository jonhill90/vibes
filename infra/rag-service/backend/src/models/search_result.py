"""Search result and embedding Pydantic models."""

from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SearchResultResponse(BaseModel):
    """Response model for search results."""

    chunk_id: UUID
    document_id: UUID
    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0-1.0)")
    metadata: dict = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Validate that text is not empty."""
        if not v.strip():
            raise ValueError("Search result text cannot be empty")
        return v


@dataclass
class EmbeddingBatchResult:
    """Result of batch embedding operation.

    CRITICAL: Prevents null embedding corruption (Gotcha #1)

    This dataclass separates successful embeddings from failed items to prevent
    storing null or zero embeddings during quota exhaustion scenarios. Storing
    null embeddings corrupts search because all null embeddings match equally,
    rendering search results meaningless.

    Usage:
        result = await embedding_service.batch_embed_safe(texts)

        # Process successful embeddings
        for i, embedding in enumerate(result.embeddings):
            await vector_service.upsert_vector(ids[i], embedding)

        # Handle failures (retry later, log, alert, etc.)
        if result.failure_count > 0:
            logger.warning(f"Failed to embed {result.failure_count} items")
            for failed in result.failed_items:
                logger.debug(f"Failed item {failed['index']}: {failed['reason']}")

    Attributes:
        embeddings: List of successful embeddings (never null/zero)
        failed_items: List of dicts with 'index', 'text', 'reason' keys
        success_count: Number of successful embeddings
        failure_count: Number of failed embeddings
    """

    embeddings: list[list[float]]
    failed_items: list[dict]
    success_count: int
    failure_count: int

    def __post_init__(self):
        """Validate EmbeddingBatchResult integrity."""
        if self.success_count != len(self.embeddings):
            raise ValueError(
                f"Mismatch: success_count={self.success_count} but "
                f"len(embeddings)={len(self.embeddings)}"
            )
        if self.failure_count != len(self.failed_items):
            raise ValueError(
                f"Mismatch: failure_count={self.failure_count} but "
                f"len(failed_items)={len(self.failed_items)}"
            )

        # CRITICAL: Validate no null/zero embeddings
        for i, embedding in enumerate(self.embeddings):
            if not embedding:
                raise ValueError(f"Embedding at index {i} is empty")
            if all(v == 0.0 for v in embedding):
                raise ValueError(
                    f"Embedding at index {i} is all zeros - this would corrupt search! "
                    f"Use failed_items instead."
                )
