"""Document Ingestion Pipeline for RAG Service.

This service implements the complete document ingestion pipeline:
1. Parse document (PDF, HTML, DOCX) using DocumentParser
2. Chunk text (~500 tokens, 50 token overlap) using TextChunker
3. Batch embed chunks (100 texts per batch) using EmbeddingService
4. Atomic storage in PostgreSQL + Qdrant using transaction pattern

Critical Gotchas Addressed:
- Gotcha #1: EmbeddingBatchResult pattern - NEVER store chunks with failed embeddings
- Gotcha #4: ORDER BY id with FOR UPDATE to prevent deadlocks in transactions
- Gotcha #8: Always use async with pool.acquire() for connection management
- Gotcha #3: Use $1, $2 placeholders (asyncpg style, NOT %s)

Pattern: examples/06_transaction_pattern.py + EmbeddingBatchResult
Reference: prps/rag_service_implementation.md (Phase 4, Task 4.3)
"""

import logging
import time
import json
from typing import Any
from uuid import UUID, uuid4

import asyncpg

from ..services.chunker import TextChunker, Chunk
from ..services.crawler.crawl_service import CrawlerService
from ..services.document_parser import DocumentParser
from ..services.document_service import DocumentService
from ..services.embeddings.embedding_service import EmbeddingService
from ..services.vector_service import VectorService

logger = logging.getLogger(__name__)


class IngestionService:
    """Document ingestion pipeline orchestrator.

    This service coordinates the complete ingestion pipeline:
    - Document parsing (Docling)
    - Text chunking (semantic boundaries)
    - Batch embedding (OpenAI with cache)
    - Atomic storage (PostgreSQL + Qdrant transaction)

    CRITICAL PATTERN (Gotcha #1):
    On quota exhaustion, EmbeddingBatchResult contains failed_items.
    NEVER store chunks that failed to embed - they would have null embeddings
    and corrupt search results (all null embeddings match equally).

    Usage:
        ingestion_service = IngestionService(
            db_pool=db_pool,
            document_parser=document_parser,
            text_chunker=text_chunker,
            embedding_service=embedding_service,
            vector_service=vector_service,
            document_service=document_service,
        )

        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/path/to/document.pdf",
        )

        if success:
            print(f"Ingested {result['chunks_stored']} chunks")
        else:
            print(f"Ingestion failed: {result['error']}")

    Attributes:
        db_pool: asyncpg connection pool for database operations
        document_parser: Service for parsing documents (PDF, HTML, DOCX)
        text_chunker: Service for semantic text chunking
        embedding_service: Service for generating embeddings with cache
        vector_service: Service for Qdrant vector operations
        document_service: Service for document CRUD operations
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        document_parser: DocumentParser,
        text_chunker: TextChunker,
        embedding_service: EmbeddingService,
        vector_service: VectorService,
        document_service: DocumentService,
        crawler_service: CrawlerService | None = None,
    ):
        """Initialize IngestionService with required dependencies.

        Args:
            db_pool: asyncpg connection pool for PostgreSQL
            document_parser: DocumentParser instance
            text_chunker: TextChunker instance
            embedding_service: EmbeddingService instance
            vector_service: VectorService instance
            document_service: DocumentService instance
            crawler_service: Optional CrawlerService for web crawling ingestion
        """
        self.db_pool = db_pool
        self.document_parser = document_parser
        self.text_chunker = text_chunker
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.document_service = document_service
        self.crawler_service = crawler_service

        logger.info("IngestionService initialized with all dependencies")

    async def ingest_document(
        self,
        source_id: UUID,
        file_path: str,
        document_metadata: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Ingest a document: parse → chunk → classify → embed → store (multi-collection).

        This is the main entry point for document ingestion. It coordinates
        the complete pipeline and ensures atomic storage using database
        transactions.

        Process (Multi-Collection Architecture):
        1. Get source configuration (enabled_collections from DB)
        2. Parse document using DocumentParser
        3. Chunk text using TextChunker (~500 tokens per chunk)
        4. Classify chunks by content type (code/documents/media)
        5. Filter chunks based on enabled_collections
        6. Group chunks by collection type
        7. For each collection: embed with appropriate model → store in collection
        8. Handle partial failures (EmbeddingBatchResult)

        CRITICAL (Gotcha #1):
        On quota exhaustion, embedding_service returns failed_items.
        These chunks are NOT stored - they would have null embeddings and
        corrupt search results.

        Args:
            source_id: UUID of the source this document belongs to
            file_path: Path to document file (PDF, HTML, DOCX)
            document_metadata: Optional metadata to attach to document

        Returns:
            Tuple of (success, result_dict) where result_dict contains:
                On success:
                - document_ids: List of UUIDs of created documents (one per collection)
                - chunks_stored: Number of chunks successfully stored
                - chunks_failed: Number of chunks that failed to embed
                - total_chunks: Total chunks created
                - collections_used: List of collections used
                - ingestion_time_ms: Total time in milliseconds
                On failure:
                - error: Error message

        Example:
            success, result = await ingestion_service.ingest_document(
                source_id=source_uuid,
                file_path="/tmp/doc.pdf",
                document_metadata={"author": "John Doe"}
            )

            if success:
                doc_ids = result["document_ids"]
                chunks = result["chunks_stored"]
                collections = result["collections_used"]
                print(f"Ingested {chunks} chunks across {len(collections)} collections")
            else:
                print(f"Error: {result['error']}")
        """
        start_time = time.time()

        try:
            # Step 1: Get source configuration (enabled_collections)
            logger.info(f"Step 1/7: Getting source configuration for {source_id}")
            async with self.db_pool.acquire() as conn:
                source_row = await conn.fetchrow(
                    "SELECT enabled_collections FROM sources WHERE id = $1",
                    source_id
                )

            if not source_row:
                return False, {"error": f"Source {source_id} not found"}

            enabled_collections = source_row["enabled_collections"]
            logger.info(f"Source {source_id} enabled collections: {enabled_collections}")

            # Step 2: Parse document using DocumentParser
            logger.info(f"Step 2/7: Parsing document: {file_path}")
            try:
                markdown_text = await self.document_parser.parse_document(file_path)
            except FileNotFoundError as e:
                return False, {"error": f"File not found: {str(e)}"}
            except ValueError as e:
                return False, {"error": f"Invalid file: {str(e)}"}
            except Exception as e:
                logger.error(f"Document parsing failed: {e}", exc_info=True)
                return False, {"error": f"Document parsing failed: {str(e)}"}

            if not markdown_text or not markdown_text.strip():
                return False, {"error": "Document parsing produced no text"}

            logger.info(
                f"Successfully parsed document: {len(markdown_text)} characters extracted"
            )

            # Step 3: Chunk text using TextChunker
            logger.info("Step 3/7: Chunking text into semantic chunks")
            try:
                chunks: list[Chunk] = await self.text_chunker.chunk_text(markdown_text)
            except Exception as e:
                logger.error(f"Text chunking failed: {e}", exc_info=True)
                return False, {"error": f"Text chunking failed: {str(e)}"}

            if not chunks:
                return False, {"error": "Text chunking produced no chunks"}

            logger.info(
                f"Successfully created {len(chunks)} chunks "
                f"(avg {sum(c.token_count for c in chunks) / len(chunks):.1f} tokens/chunk)"
            )

            # Step 4: Classify chunks by content type
            logger.info("Step 4/7: Classifying chunks by content type")
            from .content_classifier import ContentClassifier
            classifier = ContentClassifier()

            classified_chunks: dict[str, list[tuple[Chunk, int]]] = {
                "documents": [],
                "code": [],
                "media": [],
            }

            for i, chunk in enumerate(chunks):
                content_type = classifier.detect_content_type(chunk.text)

                # Only process if collection is enabled for this source
                if content_type in enabled_collections:
                    classified_chunks[content_type].append((chunk, i))
                else:
                    logger.debug(
                        f"Skipping chunk {i} (type={content_type}, not in enabled_collections)"
                    )

            # Log classification results
            for collection_type, chunk_tuples in classified_chunks.items():
                if chunk_tuples:
                    logger.info(
                        f"Classified {len(chunk_tuples)} chunks as '{collection_type}' "
                        f"(enabled={collection_type in enabled_collections})"
                    )

            # Step 5: Embed and store per collection
            logger.info("Step 5/7: Embedding and storing chunks per collection")

            # Import settings for collection configuration
            from ..config.settings import settings

            total_chunks_stored = 0
            total_chunks_failed = 0
            document_ids = []

            # Extract document metadata once (used for all collections)
            import os
            document_title = document_metadata.get("title") if document_metadata else None
            if not document_title:
                document_title = os.path.basename(file_path)

            file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
            document_type = file_ext if file_ext in ["pdf", "html", "docx"] else "text"
            url = document_metadata.get("url") if document_metadata else None

            # Process each collection type
            for collection_type, chunk_tuples in classified_chunks.items():
                if not chunk_tuples:
                    continue  # Skip empty collections

                chunks_only = [chunk for chunk, _ in chunk_tuples]
                chunk_texts = [chunk.text for chunk in chunks_only]

                # Get appropriate embedding model for this collection
                model_name = settings.COLLECTION_EMBEDDING_MODELS[collection_type]

                # Embed with collection-specific model
                logger.info(
                    f"Step 6/7 ({collection_type}): Embedding {len(chunk_texts)} chunks "
                    f"using {model_name}"
                )

                try:
                    embed_result = await self.embedding_service.batch_embed(
                        chunk_texts,
                        model_name=model_name
                    )
                except Exception as e:
                    logger.error(
                        f"Batch embedding failed for {collection_type} collection: {e}",
                        exc_info=True
                    )
                    total_chunks_failed += len(chunk_texts)
                    continue  # Skip this collection, continue with others

                # CRITICAL (Gotcha #1): Check for failed embeddings
                if embed_result.failure_count > 0:
                    logger.warning(
                        f"Embedding quota exhaustion detected for {collection_type}: "
                        f"{embed_result.success_count} success, "
                        f"{embed_result.failure_count} failed"
                    )

                if embed_result.success_count == 0:
                    logger.error(
                        f"All embeddings failed for {collection_type} collection - skipping"
                    )
                    total_chunks_failed += embed_result.failure_count
                    continue  # Skip this collection

                logger.info(
                    f"Successfully embedded {embed_result.success_count}/{len(chunk_texts)} "
                    f"chunks for {collection_type} collection"
                )

                # Store in collection-specific Qdrant collection
                collection_name = f"{settings.COLLECTION_NAME_PREFIX}{collection_type.upper()}"

                logger.info(
                    f"Step 7/7 ({collection_type}): Storing {embed_result.success_count} chunks "
                    f"in '{collection_name}' collection"
                )

                try:
                    document_id, chunks_stored = await self._store_document_atomic(
                        source_id=source_id,
                        title=document_title,
                        document_type=document_type,
                        url=url,
                        metadata={
                            **(document_metadata or {}),
                            "collection_type": collection_type
                        },
                        chunks=chunks_only[:len(embed_result.embeddings)],  # Only successful chunks
                        embeddings=embed_result.embeddings,
                        collection_name=collection_name,
                    )

                    total_chunks_stored += chunks_stored
                    total_chunks_failed += embed_result.failure_count
                    document_ids.append(str(document_id))

                    logger.info(
                        f"Stored {chunks_stored} chunks for {collection_type} "
                        f"(document_id={document_id})"
                    )

                except Exception as e:
                    logger.error(
                        f"Atomic storage failed for {collection_type} collection: {e}",
                        exc_info=True
                    )
                    total_chunks_failed += embed_result.success_count
                    continue  # Skip this collection

            # Calculate ingestion time
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Determine collections actually used (had chunks stored)
            collections_used = [
                ctype for ctype, chunk_tuples in classified_chunks.items()
                if chunk_tuples
            ]

            if total_chunks_stored == 0:
                return False, {
                    "error": "No chunks were successfully stored across any collection",
                    "chunks_failed": total_chunks_failed,
                    "collections_attempted": collections_used,
                }

            logger.info(
                f"Multi-collection ingestion complete: "
                f"document_ids={document_ids}, "
                f"chunks_stored={total_chunks_stored}, "
                f"collections={collections_used}, "
                f"time={elapsed_ms}ms"
            )

            return True, {
                "document_ids": document_ids,
                "chunks_stored": total_chunks_stored,
                "chunks_failed": total_chunks_failed,
                "total_chunks": len(chunks),
                "collections_used": collections_used,
                "ingestion_time_ms": elapsed_ms,
                "message": f"Document ingested across {len(document_ids)} collections",
            }

        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}", exc_info=True)
            return False, {"error": f"Ingestion pipeline failed: {str(e)}"}

    async def _store_document_atomic(
        self,
        source_id: UUID,
        title: str,
        document_type: str,
        url: str | None,
        metadata: dict[str, Any],
        chunks: list[Chunk],
        embeddings: list[list[float]],
        collection_name: str | None = None,
    ) -> tuple[UUID, int]:
        """Store document and chunks atomically in PostgreSQL + Qdrant (multi-collection).

        CRITICAL PATTERN (Transaction + Row Locking):
        1. Start transaction with async with conn.transaction()
        2. Lock affected rows ORDER BY id (Gotcha #4: prevents deadlocks)
        3. Create document record
        4. Insert chunks in PostgreSQL
        5. Upsert vectors to Qdrant in specified collection (idempotent, can retry safely)
        6. Commit transaction (automatic on exit)

        CRITICAL (Gotcha #1):
        Only store chunks that have successful embeddings. Never store chunks
        with null/zero embeddings - they corrupt search results.

        Multi-Collection Support:
        - If collection_name provided, stores in that specific collection
        - If None, uses default collection from VectorService

        Args:
            source_id: UUID of source
            title: Document title
            document_type: Document type (pdf, html, docx, etc.)
            url: Optional document URL
            metadata: Document metadata
            chunks: List of Chunk objects (from TextChunker)
            embeddings: List of successful embeddings (from EmbeddingBatchResult)
            collection_name: Optional Qdrant collection name (e.g., "AI_CODE", "AI_DOCUMENTS")

        Returns:
            Tuple of (document_id, chunks_stored)

        Raises:
            ValueError: If embeddings count doesn't match chunks count
            asyncpg.PostgresError: If database transaction fails
            Exception: If Qdrant upsert fails

        Pattern: examples/06_transaction_pattern.py (atomic multi-step operations)
        """
        # Validate embeddings count matches chunks count
        # (EmbeddingBatchResult may have failures, but we should only store successful ones)
        if len(embeddings) != len(chunks):
            # This can happen if some embeddings failed (Gotcha #1)
            # We only store chunks that have successful embeddings
            logger.warning(
                f"Embedding count mismatch: {len(embeddings)} embeddings "
                f"for {len(chunks)} chunks. Only storing successful embeddings."
            )

            # Take only the first N chunks that have embeddings
            chunks = chunks[: len(embeddings)]

        if len(embeddings) == 0:
            raise ValueError("No embeddings provided - cannot store document")

        # PATTERN: Atomic transaction with row locking (Gotcha #4)
        # Use async with for both connection AND transaction (Gotcha #8)
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Lock source row to prevent concurrent modifications (Gotcha #4)
                # CRITICAL: ORDER BY id prevents deadlocks
                await conn.execute(
                    """
                    SELECT id FROM sources
                    WHERE id = $1
                    ORDER BY id
                    FOR UPDATE
                    """,
                    source_id,
                )

                # Create document record
                # CRITICAL: Use $1, $2 placeholders (asyncpg style, Gotcha #3)
                # Convert metadata dict to JSON string for JSONB column
                metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata

                document_row = await conn.fetchrow(
                    """
                    INSERT INTO documents (
                        id, source_id, title, document_type, url, metadata,
                        created_at, updated_at
                    )
                    VALUES (
                        $1, $2, $3, $4, $5, $6::jsonb,
                        NOW(), NOW()
                    )
                    RETURNING id
                    """,
                    uuid4(),  # Generate new document UUID
                    source_id,
                    title,
                    document_type,
                    url,
                    metadata_json,
                )

                document_id = document_row["id"]
                logger.info(f"Created document record: {document_id}")

                # Insert chunks in PostgreSQL (batch insert for performance)
                chunk_records = []
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    chunk_id = str(uuid4())
                    chunk_records.append(
                        (
                            chunk_id,
                            document_id,
                            chunk.chunk_index,
                            chunk.text,
                            chunk.token_count,
                        )
                    )

                # Batch insert chunks (embeddings stored in Qdrant, not PostgreSQL)
                await conn.executemany(
                    """
                    INSERT INTO chunks (
                        id, document_id, chunk_index, text, token_count
                    )
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    chunk_records,
                )

                logger.info(f"Inserted {len(chunk_records)} chunks into PostgreSQL")

                # Commit transaction before Qdrant (PostgreSQL transaction ends here)

            # Upsert vectors to Qdrant (AFTER PostgreSQL transaction commits)
            # Qdrant upserts are idempotent - can retry safely
            try:
                points = []
                # Combine chunk_records with embeddings (they're parallel arrays)
                for (chunk_id, doc_id_val, chunk_index, text, token_count), embedding in zip(chunk_records, embeddings):
                    points.append({
                        "id": chunk_id,
                        "embedding": embedding,
                        "payload": {
                            "document_id": str(doc_id_val),
                            "chunk_index": chunk_index,
                            "text": text[:1000],  # Truncate for payload optimization
                            "token_count": token_count,
                            "source_id": str(source_id),
                        },
                    })

                # Multi-collection support: use specified collection or default
                if collection_name:
                    # Create collection-specific VectorService instance
                    from ..config.settings import settings

                    # Determine dimension from collection name
                    collection_type = collection_name.replace(settings.COLLECTION_NAME_PREFIX, "").lower()
                    expected_dimension = settings.COLLECTION_DIMENSIONS.get(
                        collection_type,
                        settings.OPENAI_EMBEDDING_DIMENSION  # Fallback to default
                    )

                    # Create VectorService for this specific collection
                    collection_vector_service = VectorService(
                        self.vector_service.client,
                        collection_name,
                        expected_dimension=expected_dimension
                    )

                    # Ensure collection exists before upserting
                    await collection_vector_service.ensure_collection_exists()

                    # Upsert to specific collection
                    await collection_vector_service.upsert_vectors(points)
                    logger.info(
                        f"Upserted {len(points)} vectors to collection '{collection_name}' "
                        f"(dimension={expected_dimension})"
                    )
                else:
                    # Use default VectorService (backward compatibility)
                    await self.vector_service.upsert_vectors(points)
                    logger.info(f"Upserted {len(points)} vectors to default collection")

            except Exception:
                # If Qdrant upsert fails, we have inconsistent state
                # PostgreSQL has chunks, but Qdrant doesn't
                # Log error and re-raise (caller should handle)
                logger.error(
                    f"Qdrant upsert failed after PostgreSQL commit. "
                    f"Database has {len(chunk_records)} chunks for document {document_id}, "
                    f"but vectors not in Qdrant. Manual reconciliation required.",
                    exc_info=True,
                )
                raise

        return document_id, len(chunk_records)

    async def delete_document(
        self,
        document_id: UUID,
    ) -> tuple[bool, dict[str, Any]]:
        """Delete document and all associated chunks from PostgreSQL + Qdrant.

        This is the inverse of ingest_document(). It removes:
        1. Chunk IDs from PostgreSQL
        2. Vectors from Qdrant (using chunk IDs)
        3. Document from PostgreSQL (CASCADE deletes chunks)

        The deletion is atomic - if Qdrant deletion fails, PostgreSQL deletion is aborted.

        Args:
            document_id: UUID of document to delete

        Returns:
            Tuple of (success, result_dict)

        Pattern: Delete in reverse order (Qdrant first, then PostgreSQL)
        """
        try:
            logger.info(f"Deleting document {document_id} and all chunks")

            # Use DocumentService.delete_document which handles Qdrant cleanup atomically
            success, result = await self.document_service.delete_document(
                document_id,
                vector_service=self.vector_service
            )

            if not success:
                return False, result

            chunks_deleted = result.get("chunks_deleted", 0)
            logger.info(
                f"Successfully deleted document {document_id} "
                f"with {chunks_deleted} chunks (Qdrant cleanup: {result.get('qdrant_cleanup', False)})"
            )

            return True, {
                "message": f"Document {document_id} deleted successfully",
                "document_id": str(document_id),
                "chunks_deleted": chunks_deleted,
                "qdrant_cleanup": result.get("qdrant_cleanup", False),
            }

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
            return False, {"error": f"Error deleting document: {str(e)}"}

    async def ingest_from_crawl(
        self,
        source_id: UUID,
        url: str,
        max_pages: int = 10,
        recursive: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """Crawl website and ingest content through full pipeline.

        This method orchestrates the complete crawl → parse → chunk → embed → store pipeline:
        1. Crawl URL using CrawlerService (with job tracking)
        2. Parse markdown content (already in markdown from Crawl4AI)
        3. Chunk text using TextChunker
        4. Batch embed chunks using EmbeddingService
        5. Store atomically in PostgreSQL + Qdrant

        Args:
            source_id: UUID of source this crawl belongs to
            url: Starting URL to crawl
            max_pages: Maximum pages to crawl (default 10)
            recursive: If True, follow links (not yet implemented in CrawlerService)

        Returns:
            Tuple of (success, result_dict) where result_dict contains:
                On success:
                - document_id: UUID of created document
                - crawl_job_id: UUID of crawl job
                - chunks_stored: Number of chunks successfully stored
                - pages_crawled: Number of pages crawled
                - crawl_time_ms: Time spent crawling
                - ingestion_time_ms: Total time including embedding/storage
                On failure:
                - error: Error message
                - crawl_job_id: UUID of crawl job (if created)

        Raises:
            ValueError: If crawler_service not provided during initialization

        Example:
            success, result = await ingestion_service.ingest_from_crawl(
                source_id=source_uuid,
                url="https://docs.example.com",
                max_pages=50,
                recursive=True,
            )

            if success:
                doc_id = result["document_id"]
                job_id = result["crawl_job_id"]
                print(f"Crawled and ingested {result['pages_crawled']} pages")
            else:
                print(f"Error: {result['error']}")
        """
        start_time = time.time()

        # Validate crawler_service is available
        if self.crawler_service is None:
            return False, {
                "error": "CrawlerService not initialized - crawl ingestion not available"
            }

        logger.info(f"Starting crawl ingestion for URL: {url}")

        # Step 1: Crawl website using CrawlerService
        try:
            crawl_success, crawl_result = await self.crawler_service.crawl_website(
                source_id=source_id,
                url=url,
                max_pages=max_pages,
                recursive=recursive,
            )
        except Exception as e:
            logger.error(f"Crawl failed: {e}", exc_info=True)
            return False, {"error": f"Crawl failed: {str(e)}"}

        if not crawl_success:
            return False, {
                "error": f"Crawl failed: {crawl_result.get('error')}",
                "crawl_job_id": crawl_result.get("job_id"),
            }

        # Extract crawl metadata
        crawl_job_id = crawl_result["job_id"]
        pages_crawled = crawl_result["pages_crawled"]
        markdown_content = crawl_result["content"]
        crawl_time_ms = crawl_result["crawl_time_ms"]

        logger.info(
            f"Crawl completed: job={crawl_job_id}, pages={pages_crawled}, "
            f"content_length={len(markdown_content)}, time={crawl_time_ms}ms"
        )

        # Step 2: Skip document parsing - Crawl4AI already provides markdown
        # Step 3: Chunk text using TextChunker
        logger.info("Chunking crawled markdown content")
        try:
            chunks: list[Chunk] = await self.text_chunker.chunk_text(markdown_content)
        except Exception as e:
            logger.error(f"Text chunking failed: {e}", exc_info=True)
            return False, {
                "error": f"Text chunking failed: {str(e)}",
                "crawl_job_id": crawl_job_id,
            }

        if not chunks:
            return False, {
                "error": "Text chunking produced no chunks",
                "crawl_job_id": crawl_job_id,
            }

        logger.info(
            f"Successfully created {len(chunks)} chunks "
            f"(avg {sum(c.token_count for c in chunks) / len(chunks):.1f} tokens/chunk)"
        )

        # Step 4: Batch embed chunks using EmbeddingService
        logger.info(f"Batch embedding {len(chunks)} chunks")
        chunk_texts = [chunk.text for chunk in chunks]

        try:
            embed_result = await self.embedding_service.batch_embed(chunk_texts)
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}", exc_info=True)
            return False, {
                "error": f"Batch embedding failed: {str(e)}",
                "crawl_job_id": crawl_job_id,
            }

        # CRITICAL (Gotcha #1): Check for failed embeddings
        if embed_result.failure_count > 0:
            logger.warning(
                f"Embedding quota exhaustion detected: "
                f"{embed_result.success_count} success, "
                f"{embed_result.failure_count} failed"
            )

            # If ALL embeddings failed, abort ingestion
            if embed_result.success_count == 0:
                return False, {
                    "error": "All embeddings failed - quota exhausted or API error",
                    "crawl_job_id": crawl_job_id,
                    "failed_items": embed_result.failed_items,
                }

            # Partial success - log warning and continue
            logger.warning(
                f"Partial embedding success: storing {embed_result.success_count} chunks, "
                f"skipping {embed_result.failure_count} failed chunks"
            )

        logger.info(
            f"Successfully embedded {embed_result.success_count}/{len(chunks)} chunks"
        )

        # Step 5: Atomic storage (PostgreSQL + Qdrant)
        logger.info("Storing crawled document and chunks atomically")

        # Extract document title from URL or metadata
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        document_title = parsed_url.netloc + parsed_url.path or url

        try:
            document_id, chunks_stored = await self._store_document_atomic(
                source_id=source_id,
                title=document_title,
                document_type="html",  # Crawled content is HTML
                url=url,
                metadata={
                    "crawl_job_id": crawl_job_id,
                    "pages_crawled": pages_crawled,
                    "crawl_time_ms": crawl_time_ms,
                    "recursive": recursive,
                },
                chunks=chunks,
                embeddings=embed_result.embeddings,
            )
        except Exception as e:
            logger.error(f"Atomic storage failed: {e}", exc_info=True)
            return False, {
                "error": f"Atomic storage failed: {str(e)}",
                "crawl_job_id": crawl_job_id,
            }

        # Calculate total ingestion time
        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Crawl ingestion complete: document_id={document_id}, "
            f"crawl_job_id={crawl_job_id}, chunks_stored={chunks_stored}, "
            f"total_time={elapsed_ms}ms (crawl={crawl_time_ms}ms)"
        )

        return True, {
            "document_id": str(document_id),
            "crawl_job_id": crawl_job_id,
            "chunks_stored": chunks_stored,
            "chunks_failed": embed_result.failure_count,
            "total_chunks": len(chunks),
            "pages_crawled": pages_crawled,
            "crawl_time_ms": crawl_time_ms,
            "ingestion_time_ms": elapsed_ms,
            "message": "Website crawled and ingested successfully",
        }
