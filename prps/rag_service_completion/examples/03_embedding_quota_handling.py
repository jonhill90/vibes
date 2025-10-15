# Source: infra/rag-service/backend/src/services/embeddings/embedding_service.py
# Lines: 130-278 (batch_embed method with EmbeddingBatchResult pattern)
# Pattern: Quota exhaustion handling with EmbeddingBatchResult
# Extracted: 2025-10-14
# Relevance: 9/10 - Critical gotcha #1 from feature-analysis.md

"""
WHAT THIS DEMONSTRATES:
- EmbeddingBatchResult pattern for quota protection
- Immediate STOP on quota exhaustion (never store null embeddings)
- Exponential backoff for rate limits
- Partial success handling
"""

import asyncio
import logging
import random
from dataclasses import dataclass
import openai

logger = logging.getLogger(__name__)


# ==============================================================================
# PATTERN 1: EmbeddingBatchResult Data Model
# ==============================================================================

@dataclass
class EmbeddingBatchResult:
    """Result of batch embedding operation with quota protection.

    CRITICAL: This pattern prevents null embedding corruption (Gotcha #1).
    On quota exhaustion, we mark items as failed rather than storing nulls.

    Attributes:
        embeddings: List of successful embeddings (same order as input)
        failed_items: List of failed items with reason
        success_count: Number of successful embeddings
        failure_count: Number of failed embeddings
    """
    embeddings: list[list[float]]
    failed_items: list[dict]
    success_count: int
    failure_count: int

    def __post_init__(self):
        """Validate counts match."""
        if self.success_count != len(self.embeddings):
            raise ValueError(
                f"success_count ({self.success_count}) doesn't match "
                f"embeddings length ({len(self.embeddings)})"
            )
        if self.failure_count != len(self.failed_items):
            raise ValueError(
                f"failure_count ({self.failure_count}) doesn't match "
                f"failed_items length ({len(self.failed_items)})"
            )


# ==============================================================================
# PATTERN 2: Batch Embed with Quota Protection
# ==============================================================================

async def batch_embed(
    texts: list[str],
    openai_client: openai.AsyncOpenAI,
    batch_size: int = 100
) -> EmbeddingBatchResult:
    """Batch embed texts with quota handling and EmbeddingBatchResult pattern.

    CRITICAL: This method implements Gotcha #1 protection.
    On quota exhaustion, it STOPS immediately and marks remaining items as failed.
    It NEVER adds null or zero embeddings to the result.

    Process:
    1. Process in batches of batch_size (default 100)
    2. Use exponential backoff on RateLimitError
    3. Track successful embeddings separately from failed items
    4. On quota exhaustion: STOP immediately, fail remaining items

    Args:
        texts: List of texts to embed
        openai_client: Initialized AsyncOpenAI client
        batch_size: Batch size for API calls (default: 100)

    Returns:
        EmbeddingBatchResult with successful embeddings and failed items
    """
    if not texts:
        return EmbeddingBatchResult(
            embeddings=[],
            failed_items=[],
            success_count=0,
            failure_count=0,
        )

    embeddings: list[list[float]] = []
    failed_items: list[dict] = []

    # Process in batches of batch_size (OpenAI limit)
    for batch_start in range(0, len(texts), batch_size):
        batch_end = min(batch_start + batch_size, len(texts))
        batch_texts = texts[batch_start:batch_end]

        logger.info(f"Processing batch {batch_start // batch_size + 1}: {len(batch_texts)} texts")

        try:
            # Generate embeddings with retry logic (exponential backoff)
            batch_embeddings = await _generate_batch_with_retry(
                openai_client,
                batch_texts,
                max_retries=3
            )

            # Add successful embeddings
            embeddings.extend(batch_embeddings)

        except openai.RateLimitError as e:
            # CRITICAL: Quota exhausted - STOP immediately (Gotcha #1)
            logger.error(
                f"Quota exhausted after processing {batch_start} items. "
                f"Marking remaining {len(texts) - batch_start} items as failed."
            )

            # Mark ALL remaining items as failed (current batch + future batches)
            for i in range(batch_start, len(texts)):
                failed_items.append({
                    "index": i,
                    "text": texts[i][:100],  # Truncate for logging
                    "reason": "quota_exhausted",
                    "error": str(e),
                })

            # STOP processing - do NOT continue to next batch
            # This prevents storing null/zero embeddings (corrupts vector search)
            break

        except Exception as e:
            # Other errors (network, timeout, etc.) - fail current batch
            logger.error(f"Batch embedding error: {e}", exc_info=True)

            for i in range(batch_start, batch_end):
                failed_items.append({
                    "index": i,
                    "text": texts[i][:100],
                    "reason": "api_error",
                    "error": str(e),
                })

            # Continue to next batch (transient errors may resolve)

    # Return EmbeddingBatchResult
    return EmbeddingBatchResult(
        embeddings=embeddings,
        failed_items=failed_items,
        success_count=len(embeddings),
        failure_count=len(failed_items),
    )


# ==============================================================================
# PATTERN 3: Exponential Backoff Retry Logic
# ==============================================================================

async def _generate_batch_with_retry(
    openai_client: openai.AsyncOpenAI,
    texts: list[str],
    max_retries: int = 3,
) -> list[list[float]]:
    """Generate batch embeddings with exponential backoff retry.

    CRITICAL: On quota exhaustion, this raises RateLimitError immediately
    to trigger Gotcha #1 protection in batch_embed().

    Retry strategy:
    - Retry 1: Wait 1s + jitter (2^0 + random)
    - Retry 2: Wait 2s + jitter (2^1 + random)
    - Retry 3: Wait 4s + jitter (2^2 + random)

    Args:
        openai_client: OpenAI client
        texts: List of texts to embed (up to batch_size)
        max_retries: Maximum number of retries (default: 3)

    Returns:
        List of embedding vectors

    Raises:
        openai.RateLimitError: On quota exhaustion (triggers Gotcha #1 protection)
        Exception: On other errors after max_retries
    """
    for attempt in range(max_retries):
        try:
            response = await openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts,
            )

            if not response.data:
                raise ValueError("OpenAI returned empty data")

            # Extract embeddings in order
            embeddings = [item.embedding for item in response.data]

            # Validate count matches
            if len(embeddings) != len(texts):
                raise ValueError(
                    f"Embedding count mismatch: expected {len(texts)}, "
                    f"got {len(embeddings)}"
                )

            # Validate no zero vectors (indicates quota exhaustion)
            for i, embedding in enumerate(embeddings):
                if all(v == 0.0 for v in embedding):
                    raise ValueError(f"Embedding at index {i} is all zeros - quota exhaustion?")

            return embeddings

        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt seconds + jitter
                delay = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
            else:
                # CRITICAL: Raise RateLimitError to trigger quota exhaustion handling
                logger.error(f"Rate limit exceeded after {max_retries} retries. Triggering quota protection.")
                raise  # Re-raise to batch_embed() for Gotcha #1 protection

        except Exception as e:
            logger.error(f"Batch embedding error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt >= max_retries - 1:
                raise  # Re-raise to batch_embed() for error handling
            await asyncio.sleep(1)  # Short delay for non-rate-limit errors

    raise Exception(f"Failed to generate batch embeddings after {max_retries} retries")


# ==============================================================================
# PATTERN 4: Usage Example in Ingestion Pipeline
# ==============================================================================

async def ingest_documents(documents: list[dict]):
    """Ingest documents with quota-aware embedding."""

    # Extract text chunks
    all_texts = []
    for doc in documents:
        chunks = chunk_document(doc["content"])
        all_texts.extend(chunks)

    # Batch embed with quota protection
    result = await batch_embed(all_texts, openai_client)

    # Log results
    logger.info(
        f"Embedding complete: {result.success_count} success, "
        f"{result.failure_count} failed"
    )

    # Process successful embeddings
    for i, embedding in enumerate(result.embeddings):
        # Store in vector database (only successful embeddings)
        await vector_service.upsert(
            id=f"chunk_{i}",
            vector=embedding,
            payload={"text": all_texts[i]}
        )

    # Handle failures
    if result.failure_count > 0:
        logger.error(f"Failed to embed {result.failure_count} chunks")

        # Check for quota exhaustion
        quota_failed = [
            item for item in result.failed_items
            if item["reason"] == "quota_exhausted"
        ]

        if quota_failed:
            # CRITICAL: Quota exhausted - stop ingestion
            logger.error(
                f"Quota exhausted: {len(quota_failed)} items failed. "
                f"STOPPING ingestion to prevent null embedding corruption."
            )
            raise Exception("Quota exhausted - ingestion stopped")

        # For other errors, log and optionally retry later
        for failed in result.failed_items:
            logger.warning(
                f"Failed chunk {failed['index']}: {failed['reason']} - {failed['error']}"
            )


# ==============================================================================
# KEY TAKEAWAYS
# ==============================================================================

# ✅ DO THIS:
# 1. Use EmbeddingBatchResult to track successes and failures separately
# 2. On quota exhaustion (RateLimitError), STOP immediately and mark remaining items as failed
# 3. NEVER store null or zero embeddings (corrupts vector search)
# 4. Use exponential backoff for transient rate limits
# 5. Validate embeddings before storing (check for zeros, correct dimensions)

# ❌ DON'T DO THIS:
# 1. Store null embeddings on quota failure (corrupts database)
# 2. Continue processing after quota exhaustion (wastes API calls)
# 3. Use fixed delays for retries (exponential backoff is better)
# 4. Skip validation of embedding dimensions and zero vectors
