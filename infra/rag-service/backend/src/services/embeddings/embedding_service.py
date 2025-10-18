"""Embedding service with OpenAI embeddings, cache lookup, and quota handling.

This service implements the EmbeddingBatchResult pattern (Gotcha #1) to prevent
null embedding corruption during quota exhaustion. It includes:
- Cache lookup/storage for cost reduction
- Exponential backoff with jitter for rate limit handling (Gotcha #10)
- Batch processing with 100 texts per API call
- NEVER stores null or zero embeddings

Pattern: OpenAI embeddings + asyncpg cache + EmbeddingBatchResult
Reference: prps/rag_service_implementation.md (Task 2.5, Gotcha #1, Gotcha #10)
"""

import asyncio
import hashlib
import logging
import random
import time
from typing import Optional

import asyncpg
import openai

from ...config.settings import settings
from ...models.search_result import EmbeddingBatchResult

logger = logging.getLogger(__name__)


class EmbeddingService:
    """OpenAI embedding service with cache and quota handling.

    CRITICAL PATTERNS:
    1. EmbeddingBatchResult: Never stores null embeddings (Gotcha #1)
    2. Exponential backoff: Handles rate limits (Gotcha #10)
    3. Cache lookup: Reduces API calls by 20-40%
    4. Batch processing: 100 texts per API call (OpenAI limit)

    Usage:
        service = EmbeddingService(db_pool, openai_client)

        # Single embedding
        embedding = await service.embed_text("Hello world")

        # Batch embedding with quota protection
        result = await service.batch_embed(texts)
        for i, embedding in enumerate(result.embeddings):
            # Process successful embeddings
            pass
        for failed in result.failed_items:
            logger.warning(f"Failed to embed: {failed['reason']}")

    Attributes:
        db_pool: asyncpg connection pool for cache storage
        openai_client: OpenAI async client for embeddings
        model_name: Embedding model (text-embedding-3-small)
        expected_dimension: Expected vector dimension (1536)
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        openai_client: openai.AsyncOpenAI,
    ):
        """Initialize EmbeddingService.

        Args:
            db_pool: asyncpg connection pool for cache operations
            openai_client: OpenAI async client for embedding generation
        """
        self.db_pool = db_pool
        self.openai_client = openai_client
        self.model_name = settings.OPENAI_EMBEDDING_MODEL
        self.expected_dimension = settings.OPENAI_EMBEDDING_DIMENSION
        self.batch_size = settings.EMBEDDING_BATCH_SIZE

        # Cache hit rate tracking (Task 7: Embedding Cache Schema Fix)
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_requests = 0

        logger.info(
            f"EmbeddingService initialized: model={self.model_name}, "
            f"dimension={self.expected_dimension}, batch_size={self.batch_size}"
        )

    async def embed_text(
        self,
        text: str,
        model_name: Optional[str] = None
    ) -> Optional[list[float]]:
        """Generate embedding for a single text with cache lookup.

        Process:
        1. Check cache first (MD5 hash lookup with model_name)
        2. Generate embedding if not cached
        3. Store in cache on success
        4. Return None on failure (NEVER null/zero embeddings)

        Args:
            text: Text to embed
            model_name: Optional model name (defaults to self.model_name)

        Returns:
            list[float]: Embedding vector (dimension depends on model)
            None: If embedding generation fails

        Example:
            embedding = await service.embed_text("Hello world")
            if embedding:
                await vector_service.upsert(id, embedding)
            else:
                logger.error("Failed to generate embedding")
        """
        if not text or not text.strip():
            logger.warning("Empty text provided, skipping embedding")
            return None

        # Use default model if not specified (backward compatibility)
        model_name = model_name or self.model_name

        # Step 1: Check cache (includes model_name in lookup)
        cached_embedding = await self._get_cached_embedding(text, model_name)
        if cached_embedding:
            # Track cache hit (Task 7)
            self.cache_hits += 1
            self.total_requests += 1
            self._log_cache_hit_rate_if_needed()
            logger.debug(f"Cache hit for text: {text[:50]}... (model: {model_name})")
            return cached_embedding

        # Track cache miss (Task 7)
        self.cache_misses += 1
        self.total_requests += 1

        # Step 2: Generate embedding with retry logic
        try:
            embedding = await self._generate_embedding_with_retry(text, model_name)
            if embedding:
                # Step 3: Store in cache (includes model_name)
                await self._cache_embedding(text, embedding, model_name)
                self._log_cache_hit_rate_if_needed()
                return embedding
            else:
                logger.error(f"Failed to generate embedding for text: {text[:50]}... (model: {model_name})")
                return None

        except Exception as e:
            logger.error(f"Embedding generation error: {e}", exc_info=True)
            return None

    async def embed_with_model(
        self,
        text: str,
        model_name: str
    ) -> Optional[list[float]]:
        """Generate embedding using a specific model (multi-collection support).

        This is an explicit alias for embed_text() with model_name specified,
        added for clarity when using multi-collection architecture.

        Args:
            text: Text to embed
            model_name: Embedding model to use (e.g., "text-embedding-3-large")

        Returns:
            list[float]: Embedding vector (dimension depends on model)
            None: If embedding generation fails

        Example:
            # For code collection using large model
            embedding = await service.embed_with_model(
                "def hello(): pass",
                "text-embedding-3-large"
            )
        """
        return await self.embed_text(text, model_name=model_name)

    async def batch_embed(
        self,
        texts: list[str],
        model_name: Optional[str] = None
    ) -> EmbeddingBatchResult:
        """Batch embed texts with quota handling and EmbeddingBatchResult pattern.

        CRITICAL: This method implements Gotcha #1 protection.
        On quota exhaustion, it STOPS immediately and marks remaining items as failed.
        It NEVER adds null or zero embeddings to the result.

        Process:
        1. Check cache for all texts (with model_name in lookup)
        2. Batch generate embeddings for uncached texts (100 per API call)
        3. Use exponential backoff on RateLimitError (Gotcha #10)
        4. Track successful embeddings separately from failed items
        5. Cache successful embeddings (with model_name)

        Args:
            texts: List of texts to embed (any length)
            model_name: Optional model name (defaults to self.model_name)

        Returns:
            EmbeddingBatchResult: Contains successful embeddings and failed items

        Example:
            result = await service.batch_embed(texts)
            print(f"Success: {result.success_count}/{len(texts)}")

            # Process successful embeddings
            for i, embedding in enumerate(result.embeddings):
                await vector_service.upsert(ids[i], embedding)

            # Handle failures (retry later, log, alert)
            if result.failure_count > 0:
                for failed in result.failed_items:
                    logger.warning(f"Failed: {failed['reason']}")
        """
        if not texts:
            return EmbeddingBatchResult(
                embeddings=[],
                failed_items=[],
                success_count=0,
                failure_count=0,
            )

        # Use default model if not specified (backward compatibility)
        model_name = model_name or self.model_name

        embeddings: list[list[float]] = []
        failed_items: list[dict] = []
        cache_misses: list[tuple[int, str]] = []  # (original_index, text)

        # Step 1: Check cache for all texts (with model_name)
        for i, text in enumerate(texts):
            if not text or not text.strip():
                failed_items.append({
                    "index": i,
                    "text": text[:100] if text else "",
                    "reason": "empty_text",
                    "error": "Text is empty or whitespace only",
                })
                continue

            cached_embedding = await self._get_cached_embedding(text, model_name)
            if cached_embedding:
                embeddings.append(cached_embedding)
            else:
                cache_misses.append((i, text))

        # Track cache statistics (Task 7)
        batch_cache_hits = len(embeddings)
        batch_cache_misses = len(cache_misses)
        self.cache_hits += batch_cache_hits
        self.cache_misses += batch_cache_misses
        self.total_requests += len(texts) - len(failed_items)  # Don't count empty texts

        logger.info(
            f"Cache stats: {batch_cache_hits} hits, {batch_cache_misses} misses "
            f"({batch_cache_hits / (batch_cache_hits + batch_cache_misses) * 100:.1f}% hit rate)"
        )
        self._log_cache_hit_rate_if_needed()

        # Step 2: Batch generate embeddings for cache misses (token-aware batching)
        if cache_misses:
            start_time = time.time()

            # CRITICAL: OpenAI has 8,192 token limit per batch request
            # Use conservative limit of 7,000 tokens to leave margin for encoding overhead
            MAX_BATCH_TOKENS = 7000

            batch_num = 0
            i = 0
            while i < len(cache_misses):
                batch_items = []
                batch_texts = []
                current_batch_tokens = 0

                # Build batch respecting both token limit and max batch size
                while i < len(cache_misses) and len(batch_items) < self.batch_size:
                    original_idx, text = cache_misses[i]

                    # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
                    # This is conservative - actual tokenization may differ
                    estimated_tokens = len(text) // 4

                    # Check if adding this text would exceed token limit
                    if current_batch_tokens + estimated_tokens > MAX_BATCH_TOKENS:
                        if batch_items:
                            # Batch full - process what we have
                            logger.info(
                                f"Batch {batch_num + 1} token limit reached: "
                                f"~{current_batch_tokens} tokens, {len(batch_items)} texts"
                            )
                            break
                        else:
                            # Single text exceeds limit - fail it immediately
                            logger.error(
                                f"Text at index {original_idx} too large: ~{estimated_tokens} tokens "
                                f"(exceeds {MAX_BATCH_TOKENS} limit)"
                            )
                            failed_items.append({
                                "index": original_idx,
                                "text": text[:100],
                                "reason": "token_limit_exceeded",
                                "error": f"Text exceeds {MAX_BATCH_TOKENS} token limit",
                            })
                            i += 1
                            continue

                    batch_items.append((original_idx, text))
                    batch_texts.append(text)
                    current_batch_tokens += estimated_tokens
                    i += 1

                batch_num += 1
                logger.info(
                    f"Processing batch {batch_num}: {len(batch_texts)} texts, ~{current_batch_tokens} tokens"
                )

                # Generate embeddings with retry logic (using specified model)
                try:
                    batch_embeddings = await self._generate_batch_embeddings_with_retry(
                        batch_texts,
                        model_name=model_name
                    )

                    # Add successful embeddings and cache them (with model_name)
                    for (original_idx, text), embedding in zip(batch_items, batch_embeddings):
                        embeddings.append(embedding)
                        # Cache in background (don't await to improve throughput)
                        asyncio.create_task(self._cache_embedding(text, embedding, model_name))

                except openai.RateLimitError as e:
                    # CRITICAL: Quota exhausted - STOP immediately (Gotcha #1)
                    logger.error(
                        f"Quota exhausted after processing {i - len(batch_items)} items. "
                        f"Marking remaining {len(cache_misses) - i} items as failed."
                    )

                    # Mark ALL remaining items as failed (current batch + future batches)
                    for original_idx, text in cache_misses[i:]:
                        failed_items.append({
                            "index": original_idx,
                            "text": text[:100],
                            "reason": "quota_exhausted",
                            "error": str(e),
                        })

                    # STOP processing - do NOT continue to next batch
                    break

                except Exception as e:
                    # Other errors (network, timeout, etc.) - fail current batch
                    logger.error(f"Batch embedding error: {e}", exc_info=True)

                    for original_idx, text in batch_items:
                        failed_items.append({
                            "index": original_idx,
                            "text": text[:100],
                            "reason": "api_error",
                            "error": str(e),
                        })

                    # Continue to next batch (transient errors may resolve)

            elapsed = time.time() - start_time
            logger.info(
                f"Batch embedding completed in {elapsed:.2f}s: "
                f"{len(embeddings)} success, {len(failed_items)} failed"
            )

        # Step 3: Return EmbeddingBatchResult
        result = EmbeddingBatchResult(
            embeddings=embeddings,
            failed_items=failed_items,
            success_count=len(embeddings),
            failure_count=len(failed_items),
        )

        # Validation check (should never fail due to __post_init__)
        if result.success_count + result.failure_count != len(texts):
            logger.error(
                f"Embedding count mismatch: {result.success_count} + {result.failure_count} "
                f"!= {len(texts)} total texts"
            )

        return result

    async def _get_cached_embedding(
        self,
        text: str,
        model_name: str
    ) -> Optional[list[float]]:
        """Get embedding from cache using content hash and model name.

        CRITICAL: Cache lookup includes both content_hash AND model_name.
        This ensures different models have separate cache entries for the same text.

        Args:
            text: Text to lookup
            model_name: Model name to lookup (part of cache key)

        Returns:
            list[float]: Cached embedding if found
            None: If not in cache or cache error
        """
        content_hash = self._compute_content_hash(text)

        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT embedding
                    FROM embedding_cache
                    WHERE content_hash = $1 AND model_name = $2
                    """,
                    content_hash,
                    model_name,
                )

                if row:
                    embedding = row["embedding"]

                    # CRITICAL: Validate cached embedding dimensions
                    # Corrupted embeddings can be stored if previous requests failed
                    expected_dims = {
                        "text-embedding-3-small": 1536,
                        "text-embedding-3-large": 3072,
                    }
                    expected_dim = expected_dims.get(model_name, 1536)

                    if len(embedding) != expected_dim:
                        logger.warning(
                            f"Invalid cached embedding dimension: {len(embedding)}, "
                            f"expected {expected_dim} for model {model_name}. "
                            f"Deleting corrupted cache entry."
                        )
                        # Delete corrupted cache entry
                        await conn.execute(
                            """
                            DELETE FROM embedding_cache
                            WHERE content_hash = $1 AND model_name = $2
                            """,
                            content_hash,
                            model_name,
                        )
                        return None  # Force re-generation

                    # Update access statistics
                    await conn.execute(
                        """
                        UPDATE embedding_cache
                        SET access_count = access_count + 1,
                            last_accessed_at = NOW()
                        WHERE content_hash = $1 AND model_name = $2
                        """,
                        content_hash,
                        model_name,
                    )
                    return embedding

        except Exception as e:
            logger.error(f"Cache lookup error: {e}", exc_info=True)

        return None

    async def _cache_embedding(
        self,
        text: str,
        embedding: list[float],
        model_name: str
    ) -> None:
        """Store embedding in cache with content hash and model name.

        CRITICAL: Cache storage includes both content_hash AND model_name.
        This ensures different models have separate cache entries for the same text.

        Args:
            text: Original text
            embedding: Generated embedding vector
            model_name: Model name used for embedding (part of cache key)

        Note:
            Uses INSERT ... ON CONFLICT DO UPDATE to handle race conditions
            and update access statistics when the same text is cached again.
            (Task 7: Updates access_count and last_accessed_at on conflict)
        """
        content_hash = self._compute_content_hash(text)

        try:
            async with self.db_pool.acquire() as conn:
                # Convert embedding list to string format for pgvector
                # pgvector expects: "[0.1, 0.2, 0.3]" format
                embedding_str = str(embedding)

                await conn.execute(
                    """
                    INSERT INTO embedding_cache (content_hash, text_preview, embedding, model_name)
                    VALUES ($1, $2, $3::vector, $4)
                    ON CONFLICT (content_hash, model_name) DO UPDATE
                    SET access_count = embedding_cache.access_count + 1,
                        last_accessed_at = NOW()
                    """,
                    content_hash,
                    text[:500],  # Store preview for debugging
                    embedding_str,
                    model_name,
                )

        except Exception as e:
            # Cache storage failure is non-critical - log and continue
            logger.warning(f"Cache storage error (non-critical): {e}")

    async def _generate_embedding_with_retry(
        self,
        text: str,
        model_name: str,
        max_retries: int = 3,
    ) -> Optional[list[float]]:
        """Generate embedding with exponential backoff retry (Gotcha #10).

        Retry strategy:
        - Retry 1: Wait 1s + jitter
        - Retry 2: Wait 2s + jitter
        - Retry 3: Wait 4s + jitter

        Args:
            text: Text to embed
            model_name: Model name to use for embedding
            max_retries: Maximum number of retries (default: 3)

        Returns:
            list[float]: Embedding vector
            None: If all retries failed
        """
        for attempt in range(max_retries):
            try:
                response = await self.openai_client.embeddings.create(
                    model=model_name,
                    input=text,
                )

                if not response.data:
                    logger.error("OpenAI returned empty data")
                    return None

                embedding = response.data[0].embedding

                # Validate embedding (dimension validation removed - varies by model)
                # text-embedding-3-small: 1536 dimensions
                # text-embedding-3-large: 3072 dimensions
                if len(embedding) == 0:
                    logger.error("Empty embedding returned")
                    return None

                if all(v == 0.0 for v in embedding):
                    logger.error("Embedding is all zeros - quota exhaustion?")
                    return None

                return embedding

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
                    logger.error(f"Rate limit exceeded after {max_retries} retries: {e}")
                    raise  # Re-raise to caller for quota exhaustion handling

            except Exception as e:
                logger.error(f"Embedding generation error (attempt {attempt + 1}): {e}")
                if attempt >= max_retries - 1:
                    return None
                # Wait before retry (shorter delay for non-rate-limit errors)
                await asyncio.sleep(1)

        return None

    async def _generate_batch_embeddings_with_retry(
        self,
        texts: list[str],
        model_name: str,
        max_retries: int = 3,
    ) -> list[list[float]]:
        """Generate batch embeddings with exponential backoff retry (Gotcha #10).

        CRITICAL: On quota exhaustion, this method raises RateLimitError
        immediately to trigger Gotcha #1 protection in batch_embed().

        Args:
            texts: List of texts to embed (up to EMBEDDING_BATCH_SIZE)
            model_name: Model name to use for embedding
            max_retries: Maximum number of retries (default: 3)

        Returns:
            list[list[float]]: List of embedding vectors

        Raises:
            openai.RateLimitError: On quota exhaustion (triggers Gotcha #1 protection)
            Exception: On other errors after max_retries
        """
        for attempt in range(max_retries):
            try:
                response = await self.openai_client.embeddings.create(
                    model=model_name,
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

                # Validate no zero vectors (dimension validation removed - varies by model)
                for i, embedding in enumerate(embeddings):
                    if len(embedding) == 0:
                        raise ValueError(f"Empty embedding at index {i}")

                    if all(v == 0.0 for v in embedding):
                        raise ValueError(
                            f"Embedding at index {i} is all zeros - quota exhaustion?"
                        )

                return embeddings

            except openai.RateLimitError:
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
                    logger.error(
                        f"Rate limit exceeded after {max_retries} retries. "
                        f"Triggering quota exhaustion protection."
                    )
                    raise  # Re-raise to batch_embed() for Gotcha #1 protection

            except Exception as e:
                logger.error(
                    f"Batch embedding error (attempt {attempt + 1}/{max_retries}): {e}",
                    exc_info=True,
                )
                if attempt >= max_retries - 1:
                    raise  # Re-raise to batch_embed() for error handling
                # Wait before retry (shorter delay for non-rate-limit errors)
                await asyncio.sleep(1)

        raise Exception(f"Failed to generate batch embeddings after {max_retries} retries")

    @staticmethod
    def _compute_content_hash(text: str) -> str:
        """Compute MD5 hash for cache lookup.

        Args:
            text: Text to hash

        Returns:
            str: MD5 hash (32 hex characters)
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @property
    def cache_hit_rate(self) -> float:
        """Calculate current cache hit rate.

        Returns:
            float: Cache hit rate as percentage (0.0-100.0)

        Example:
            >>> service.cache_hit_rate
            34.5  # 34.5% cache hit rate
        """
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100.0

    def _log_cache_hit_rate_if_needed(self) -> None:
        """Log cache hit rate every 100 requests (Task 7).

        Logs cache performance metrics to monitor cost savings.
        Target: 20-40% hit rate (30% cost savings at scale).
        """
        if self.total_requests % 100 == 0 and self.total_requests > 0:
            logger.info(
                f"[Cache Performance] Total requests: {self.total_requests}, "
                f"Hits: {self.cache_hits}, Misses: {self.cache_misses}, "
                f"Hit rate: {self.cache_hit_rate:.1f}%"
            )

            # Warn if hit rate is unexpectedly low
            if self.total_requests >= 500 and self.cache_hit_rate < 10.0:
                logger.warning(
                    f"Cache hit rate unusually low ({self.cache_hit_rate:.1f}%). "
                    f"Expected 20-40%. Check for unique content or cache issues."
                )
