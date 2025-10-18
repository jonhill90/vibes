"""Extract code blocks from existing documentation chunks into MCP_code collection.

This script implements Phase 2, Task 1 from JON-12:
Extract code blocks from documentation into MCP_code collection

Problem:
- Code examples embedded in 500-token docs chunks (MCP_code has 0 points)
- Code queries score 0.41 (below 0.6 threshold)
- Agent rating: 7/10

Solution:
1. Read existing 916 chunks from PostgreSQL
2. Extract code blocks using regex (```python, ```typescript, etc.)
3. Create new code-only chunks (min 50 chars for viable snippets)
4. Embed using text-embedding-3-large (3072d, better for code)
5. Store in MCP_code collection (separate from documentation)

Expected Impact:
- Code search score: 0.41 → 0.65+ (above threshold)
- Agent rating: 7/10 → 9/10
- MCP_code collection: 0 → ~150 points (estimated)

Reference: infra/rag-service/TODO.md (lines 6-11, 166-213)
"""

import asyncio
import asyncpg
import json
import logging
import openai
import re
import sys
import os
from typing import List, Tuple
from uuid import UUID, uuid4
from qdrant_client import AsyncQdrantClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config.settings import settings
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.vector_service import VectorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CodeBlockExtractor:
    """Extract code blocks from markdown text chunks."""

    # Regex pattern to match markdown code fences with language specifier
    # Matches: ```python\ncode\n``` or ```bash code\n```
    # Note: Language can be followed by optional attributes and whitespace
    CODE_FENCE_PATTERN = re.compile(
        r'```([a-zA-Z0-9_+-]+)(?:\s+[^\n]*)?\n(.*?)```',
        re.DOTALL | re.MULTILINE
    )

    # Minimum characters for a viable code snippet
    MIN_CODE_LENGTH = 50

    @staticmethod
    def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
        """Extract code blocks from markdown text.

        Args:
            text: Markdown text containing code fences

        Returns:
            List of tuples: [(language, code_text), ...]

        Example:
            >>> text = "# Example\\n```python\\ndef hello():\\n    pass\\n```"
            >>> CodeBlockExtractor.extract_code_blocks(text)
            [('python', 'def hello():\\n    pass')]
        """
        matches = CodeBlockExtractor.CODE_FENCE_PATTERN.findall(text)

        # Filter out very short code blocks (likely not useful)
        code_blocks = [
            (lang, code.strip())
            for lang, code in matches
            if len(code.strip()) >= CodeBlockExtractor.MIN_CODE_LENGTH
        ]

        return code_blocks

    @staticmethod
    def create_code_chunk_text(language: str, code: str, original_chunk_text: str) -> str:
        """Create searchable text for code chunk with context.

        Includes language, code, and a snippet of surrounding documentation
        for better semantic search.

        Args:
            language: Programming language (e.g., 'python', 'typescript')
            code: Code block content
            original_chunk_text: Original chunk for context extraction

        Returns:
            Formatted text for embedding and search
        """
        # Extract surrounding context (first 200 chars before code block)
        context_match = re.search(
            r'(.{0,200})```' + re.escape(language),
            original_chunk_text,
            re.DOTALL
        )

        context = ""
        if context_match:
            context = context_match.group(1).strip()
            # Clean up context (remove markdown headers, excess whitespace)
            context = re.sub(r'#+\s*', '', context)
            context = re.sub(r'\s+', ' ', context)

        # Format: Language + Context + Code
        # This helps with semantic search (e.g., "MCP tool decorator" finds @mcp.tool())
        if context:
            return f"Language: {language}\nContext: {context}\n\n{code}"
        else:
            return f"Language: {language}\n\n{code}"


async def extract_and_store_code_blocks(
    db_pool: asyncpg.Pool,
    embedding_service: EmbeddingService,
    vector_service: VectorService,
    source_id: UUID,
    collection_name: str,
    dry_run: bool = False
) -> dict:
    """Extract code blocks from existing chunks and store in code collection.

    Args:
        db_pool: Database connection pool
        embedding_service: Service for generating embeddings
        vector_service: Service for Qdrant operations
        source_id: Source ID to process chunks from
        collection_name: Name of code collection (e.g., "MCP_code")
        dry_run: If True, don't actually store (just analyze)

    Returns:
        dict with statistics:
        - chunks_processed: Number of original chunks analyzed
        - code_blocks_found: Number of code blocks extracted
        - code_blocks_stored: Number successfully stored in vector DB
        - code_blocks_skipped: Number too small or failed
    """
    logger.info(f"Starting code extraction for source {source_id}")
    logger.info(f"Target collection: {collection_name}")
    logger.info(f"Dry run mode: {dry_run}")

    # Step 1: Fetch all chunks for this source
    async with db_pool.acquire() as conn:
        # Get document IDs for this source
        doc_rows = await conn.fetch(
            "SELECT id FROM documents WHERE source_id = $1",
            source_id
        )
        doc_ids = [row['id'] for row in doc_rows]

        if not doc_ids:
            logger.warning(f"No documents found for source {source_id}")
            return {
                "chunks_processed": 0,
                "code_blocks_found": 0,
                "code_blocks_stored": 0,
                "code_blocks_skipped": 0
            }

        logger.info(f"Found {len(doc_ids)} documents for source {source_id}")

        # Fetch all chunks for these documents
        chunk_rows = await conn.fetch(
            "SELECT id, document_id, chunk_index, text FROM chunks WHERE document_id = ANY($1::uuid[])",
            doc_ids
        )

    logger.info(f"Fetched {len(chunk_rows)} chunks to process")

    # Step 2: Extract code blocks from chunks
    extractor = CodeBlockExtractor()
    code_blocks_data = []  # (chunk_id, document_id, language, code, formatted_text)

    for chunk_row in chunk_rows:
        chunk_id = chunk_row['id']
        document_id = chunk_row['document_id']
        chunk_text = chunk_row['text']

        # Extract code blocks from this chunk
        code_blocks = extractor.extract_code_blocks(chunk_text)

        for language, code in code_blocks:
            # Create searchable text with context
            formatted_text = extractor.create_code_chunk_text(language, code, chunk_text)

            code_blocks_data.append({
                'original_chunk_id': chunk_id,
                'document_id': document_id,
                'language': language,
                'code': code,
                'formatted_text': formatted_text
            })

    logger.info(f"Extracted {len(code_blocks_data)} code blocks from {len(chunk_rows)} chunks")

    if not code_blocks_data:
        logger.info("No code blocks found - nothing to store")
        return {
            "chunks_processed": len(chunk_rows),
            "code_blocks_found": 0,
            "code_blocks_stored": 0,
            "code_blocks_skipped": 0
        }

    # Step 3: Embed code blocks (if not dry run)
    if dry_run:
        logger.info("DRY RUN: Would embed and store code blocks, but skipping")
        return {
            "chunks_processed": len(chunk_rows),
            "code_blocks_found": len(code_blocks_data),
            "code_blocks_stored": 0,
            "code_blocks_skipped": 0
        }

    # Prepare texts for embedding
    texts_to_embed = [block['formatted_text'] for block in code_blocks_data]

    logger.info(f"Embedding {len(texts_to_embed)} code blocks using text-embedding-3-large")

    # Embed in batches (text-embedding-3-large is better for code)
    batch_result = await embedding_service.batch_embed(
        texts=texts_to_embed,
        model_name="text-embedding-3-large"  # 3072d, better for code
    )

    if batch_result.failed_items:
        logger.warning(
            f"Failed to embed {len(batch_result.failed_items)} code blocks "
            f"(quota exhaustion or errors)"
        )

    logger.info(
        f"Successfully embedded {len(batch_result.embeddings)} / {len(texts_to_embed)} code blocks"
    )

    # Step 4: Store in Qdrant code collection
    points_to_upsert = []

    for i, embedding in enumerate(batch_result.embeddings):
        code_block = code_blocks_data[i]

        point_id = str(uuid4())
        payload = {
            "source_id": str(source_id),
            "document_id": str(code_block['document_id']),
            "original_chunk_id": str(code_block['original_chunk_id']),
            "text": code_block['code'],  # Store raw code for display
            "language": code_block['language'],
            "collection_type": "code",
            "formatted_text": code_block['formatted_text'],  # Store searchable version
        }

        points_to_upsert.append({
            "id": point_id,
            "embedding": embedding,  # VectorService expects 'embedding' field
            "payload": payload
        })

    if points_to_upsert:
        logger.info(f"Upserting {len(points_to_upsert)} code blocks to {collection_name}")

        await vector_service.upsert_vectors(
            collection_name=collection_name,
            points=points_to_upsert
        )

        logger.info(f"Successfully stored {len(points_to_upsert)} code blocks in {collection_name}")

    return {
        "chunks_processed": len(chunk_rows),
        "code_blocks_found": len(code_blocks_data),
        "code_blocks_stored": len(points_to_upsert),
        "code_blocks_skipped": len(batch_result.failed_items)
    }


async def main():
    """Main entry point for code extraction script."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Extract code blocks from documentation chunks into code collection"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze without storing (preview mode)"
    )
    parser.add_argument(
        "--source-id",
        type=str,
        help="Source UUID to process (default: MCP Documentation source)"
    )
    args = parser.parse_args()

    # Initialize database connection
    logger.info("Connecting to database...")
    db_pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=1,
        max_size=5
    )

    try:
        # Get source ID (default to MCP Documentation)
        if args.source_id:
            source_id = UUID(args.source_id)
        else:
            # Find MCP Documentation source
            async with db_pool.acquire() as conn:
                source_row = await conn.fetchrow(
                    """
                    SELECT id, collection_names
                    FROM sources
                    WHERE status = 'active'
                    AND source_type = 'upload'
                    LIMIT 1
                    """
                )

            if not source_row:
                logger.error("No active upload source found - please provide --source-id")
                return

            source_id = source_row['id']
            collection_names = source_row['collection_names']

            logger.info(f"Using source {source_id}")
            logger.info(f"Collection names: {collection_names}")

        # Get collection name from source
        async with db_pool.acquire() as conn:
            source_row = await conn.fetchrow(
                "SELECT collection_names FROM sources WHERE id = $1",
                source_id
            )

        if not source_row:
            logger.error(f"Source {source_id} not found")
            return

        collection_names_raw = source_row['collection_names']

        # Parse collection_names (could be string or dict)
        if isinstance(collection_names_raw, str):
            collection_names = json.loads(collection_names_raw)
        elif isinstance(collection_names_raw, dict):
            collection_names = collection_names_raw
        else:
            collection_names = {}

        code_collection_name = collection_names.get('code')

        if not code_collection_name:
            logger.error(f"Source {source_id} does not have a 'code' collection configured")
            logger.error(f"collection_names: {collection_names}")
            return

        logger.info(f"Using code collection: {code_collection_name}")

        # Initialize services
        logger.info("Initializing embedding and vector services...")

        # Create OpenAI client
        openai_client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value()
        )

        # Create Qdrant client
        qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)

        embedding_service = EmbeddingService(
            db_pool=db_pool,
            openai_client=openai_client
        )
        vector_service = VectorService(qdrant_client=qdrant_client)

        # Run extraction
        logger.info("=" * 80)
        logger.info("Starting code block extraction")
        logger.info("=" * 80)

        result = await extract_and_store_code_blocks(
            db_pool=db_pool,
            embedding_service=embedding_service,
            vector_service=vector_service,
            source_id=source_id,
            collection_name=code_collection_name,
            dry_run=args.dry_run
        )

        # Print summary
        logger.info("=" * 80)
        logger.info("Extraction Summary")
        logger.info("=" * 80)
        logger.info(f"Chunks processed: {result['chunks_processed']}")
        logger.info(f"Code blocks found: {result['code_blocks_found']}")
        logger.info(f"Code blocks stored: {result['code_blocks_stored']}")
        logger.info(f"Code blocks skipped: {result['code_blocks_skipped']}")

        if args.dry_run:
            logger.info("")
            logger.info("DRY RUN COMPLETE - No changes made")
            logger.info("Run without --dry-run to actually store code blocks")
        else:
            logger.info("")
            logger.info("✅ Code extraction complete!")
            logger.info(f"MCP_code collection now has {result['code_blocks_stored']} code blocks")

    finally:
        await db_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
