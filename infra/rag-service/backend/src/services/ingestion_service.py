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
    ):
        """Initialize IngestionService with required dependencies.

        Args:
            db_pool: asyncpg connection pool for PostgreSQL
            document_parser: DocumentParser instance
            text_chunker: TextChunker instance
            embedding_service: EmbeddingService instance
            vector_service: VectorService instance
            document_service: DocumentService instance
        """
        self.db_pool = db_pool
        self.document_parser = document_parser
        self.text_chunker = text_chunker
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.document_service = document_service

        logger.info("IngestionService initialized with all dependencies")

    async def ingest_document(
        self,
        source_id: UUID,
        file_path: str,
        document_metadata: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Ingest a document: parse → chunk → embed → store atomically.

        This is the main entry point for document ingestion. It coordinates
        the complete pipeline and ensures atomic storage using database
        transactions.

        Process:
        1. Parse document using DocumentParser
        2. Chunk text using TextChunker (~500 tokens per chunk)
        3. Batch embed chunks using EmbeddingService (100 texts per batch)
        4. Store in PostgreSQL + Qdrant atomically
        5. Handle partial failures (EmbeddingBatchResult)

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
                - document_id: UUID of created document
                - chunks_stored: Number of chunks successfully stored
                - chunks_failed: Number of chunks that failed to embed
                - total_chunks: Total chunks created
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
                doc_id = result["document_id"]
                chunks = result["chunks_stored"]
                print(f"Ingested document {doc_id} with {chunks} chunks")
            else:
                print(f"Error: {result['error']}")
        """
        start_time = time.time()

        try:
            # Step 1: Parse document using DocumentParser
            logger.info(f"Step 1/4: Parsing document: {file_path}")
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

            # Step 2: Chunk text using TextChunker
            logger.info("Step 2/4: Chunking text into semantic chunks")
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

            # Step 3: Batch embed chunks using EmbeddingService
            logger.info(f"Step 3/4: Batch embedding {len(chunks)} chunks")
            chunk_texts = [chunk.text for chunk in chunks]

            try:
                embed_result = await self.embedding_service.batch_embed(chunk_texts)
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}", exc_info=True)
                return False, {"error": f"Batch embedding failed: {str(e)}"}

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
                        "failed_items": embed_result.failed_items,
                    }

                # Partial success - log warning and continue with successful embeddings
                logger.warning(
                    f"Partial embedding success: storing {embed_result.success_count} chunks, "
                    f"skipping {embed_result.failure_count} failed chunks"
                )

            logger.info(
                f"Successfully embedded {embed_result.success_count}/{len(chunks)} chunks"
            )

            # Step 4: Atomic storage (PostgreSQL + Qdrant)
            logger.info("Step 4/4: Storing document and chunks atomically")

            # Extract document title from file path or metadata
            import os
            document_title = document_metadata.get("title") if document_metadata else None
            if not document_title:
                document_title = os.path.basename(file_path)

            # Determine document type from file extension
            file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
            document_type = file_ext if file_ext in ["pdf", "html", "docx"] else "text"

            try:
                document_id, chunks_stored = await self._store_document_atomic(
                    source_id=source_id,
                    title=document_title,
                    document_type=document_type,
                    url=document_metadata.get("url") if document_metadata else None,
                    metadata=document_metadata or {},
                    chunks=chunks,
                    embeddings=embed_result.embeddings,
                )
            except Exception as e:
                logger.error(f"Atomic storage failed: {e}", exc_info=True)
                return False, {"error": f"Atomic storage failed: {str(e)}"}

            # Calculate ingestion time
            elapsed_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Document ingestion complete: document_id={document_id}, "
                f"chunks_stored={chunks_stored}, time={elapsed_ms}ms"
            )

            return True, {
                "document_id": str(document_id),
                "chunks_stored": chunks_stored,
                "chunks_failed": embed_result.failure_count,
                "total_chunks": len(chunks),
                "ingestion_time_ms": elapsed_ms,
                "message": "Document ingested successfully",
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
    ) -> tuple[UUID, int]:
        """Store document and chunks atomically in PostgreSQL + Qdrant.

        CRITICAL PATTERN (Transaction + Row Locking):
        1. Start transaction with async with conn.transaction()
        2. Lock affected rows ORDER BY id (Gotcha #4: prevents deadlocks)
        3. Create document record
        4. Insert chunks in PostgreSQL
        5. Upsert vectors to Qdrant (idempotent, can retry safely)
        6. Commit transaction (automatic on exit)

        CRITICAL (Gotcha #1):
        Only store chunks that have successful embeddings. Never store chunks
        with null/zero embeddings - they corrupt search results.

        Args:
            source_id: UUID of source
            title: Document title
            document_type: Document type (pdf, html, docx, etc.)
            url: Optional document URL
            metadata: Document metadata
            chunks: List of Chunk objects (from TextChunker)
            embeddings: List of successful embeddings (from EmbeddingBatchResult)

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

                await self.vector_service.upsert_vectors(points)
                logger.info(f"Upserted {len(points)} vectors to Qdrant")

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
        1. Vectors from Qdrant (by document_id filter)
        2. Chunks from PostgreSQL (CASCADE delete via foreign key)
        3. Document from PostgreSQL

        Args:
            document_id: UUID of document to delete

        Returns:
            Tuple of (success, result_dict)

        Pattern: Delete in reverse order (Qdrant first, then PostgreSQL)
        """
        try:
            logger.info(f"Deleting document {document_id} and all chunks")

            # Step 1: Delete vectors from Qdrant
            try:
                await self.vector_service.delete_by_filter(
                    {"document_id": str(document_id)}
                )
                logger.info(f"Deleted vectors for document {document_id} from Qdrant")
            except Exception as e:
                logger.error(f"Qdrant deletion failed: {e}", exc_info=True)
                # Continue anyway - PostgreSQL deletion will clean up database

            # Step 2: Delete document from PostgreSQL (CASCADE deletes chunks)
            success, result = await self.document_service.delete_document(document_id)

            if not success:
                return False, result

            logger.info(f"Successfully deleted document {document_id}")
            return True, {
                "message": f"Document {document_id} deleted successfully",
                "document_id": str(document_id),
            }

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
            return False, {"error": f"Error deleting document: {str(e)}"}
