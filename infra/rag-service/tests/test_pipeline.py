"""Quick test of RAG service pipeline: ingest → search.

Tests:
1. Database connection
2. Document ingestion (create source + document)
3. Embedding generation
4. Vector storage
5. Search functionality
"""

import asyncio
import asyncpg
from qdrant_client import AsyncQdrantClient

from src.config.settings import settings
from src.services.document_service import DocumentService
from src.services.source_service import SourceService
from src.services.vector_service import VectorService
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.document_parser import DocumentParser
from src.services.chunker import TextChunker
from src.services.ingestion_service import IngestionService
from src.services.search.base_search_strategy import BaseSearchStrategy
from src.services.search.rag_service import RAGService


async def test_pipeline():
    """Test the complete RAG pipeline."""

    print("🚀 Starting RAG Service Pipeline Test")
    print("=" * 70)

    # Step 1: Initialize connections
    print("\n📦 Step 1: Initializing connections...")
    db_pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60,
    )
    print(f"✅ Database pool created")

    qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)
    print(f"✅ Qdrant client initialized")

    try:
        # Step 2: Initialize services
        print("\n📦 Step 2: Initializing services...")

        source_service = SourceService(db_pool=db_pool)
        document_service = DocumentService(db_pool=db_pool)
        vector_service = VectorService(
            qdrant_client=qdrant_client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
        )
        embedding_service = EmbeddingService(
            db_pool=db_pool,
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            model=settings.OPENAI_EMBEDDING_MODEL,
            dimensions=settings.OPENAI_EMBEDDING_DIMENSION,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
        )

        document_parser = DocumentParser()
        text_chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        ingestion_service = IngestionService(
            db_pool=db_pool,
            document_parser=document_parser,
            text_chunker=text_chunker,
            embedding_service=embedding_service,
            vector_service=vector_service,
            document_service=document_service,
        )

        base_search_strategy = BaseSearchStrategy(
            vector_service=vector_service,
            embedding_service=embedding_service,
            db_pool=db_pool,
        )

        rag_service = RAGService(
            base_strategy=base_search_strategy,
            hybrid_strategy=None,
            use_hybrid=False,
        )

        print("✅ All services initialized")

        # Step 3: Create a source
        print("\n📦 Step 3: Creating test source...")
        success, source_result = await source_service.create_source(
            source_type="upload",
            url=None,
            metadata={"test": "pipeline", "description": "Test data for RAG pipeline"},
        )

        if not success:
            print(f"❌ Failed to create source: {source_result}")
            return

        source_id = source_result["source"]["id"]
        print(f"✅ Source created: {source_id}")

        # Step 4: Create test document with simple text
        print("\n📦 Step 4: Ingesting test document...")

        # Simple markdown content for testing
        test_content = """# RAG Service Test Document

This is a test document for the RAG (Retrieval Augmented Generation) service.

## What is RAG?

RAG combines retrieval-based and generation-based approaches for AI systems.
It retrieves relevant documents from a knowledge base and uses them to generate accurate responses.

## Key Components

1. **Document Ingestion**: Parse and chunk documents
2. **Embedding Generation**: Convert text to vector embeddings using OpenAI
3. **Vector Storage**: Store embeddings in Qdrant vector database
4. **Semantic Search**: Find relevant documents using vector similarity
5. **Response Generation**: Use retrieved context for accurate answers

## Benefits

- Improved accuracy with up-to-date information
- Reduced hallucinations
- Traceable sources
- Scalable to large knowledge bases
"""

        # Write test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        print(f"   Created temp file: {temp_file}")

        success, ingest_result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path=temp_file,
            filename="test_rag_document.md",
            metadata={"category": "test", "topic": "RAG systems"},
        )

        # Clean up temp file
        import os
        os.unlink(temp_file)

        if not success:
            print(f"❌ Failed to ingest document: {ingest_result}")
            return

        document_id = ingest_result["document"]["id"]
        chunk_count = ingest_result["chunks_stored"]
        print(f"✅ Document ingested: {document_id}")
        print(f"   Chunks created: {chunk_count}")
        print(f"   Embeddings generated: {chunk_count}")

        # Step 5: Test search
        print("\n📦 Step 5: Testing vector search...")

        test_queries = [
            "What is RAG?",
            "How does semantic search work?",
            "What are the benefits of RAG systems?",
        ]

        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")

            success, search_result = await rag_service.search(
                query=query,
                limit=3,
                source_id=source_id,
            )

            if not success:
                print(f"   ❌ Search failed: {search_result}")
                continue

            results = search_result.get("results", [])
            print(f"   ✅ Found {len(results)} results")

            for i, result in enumerate(results, 1):
                score = result.get("score", 0)
                content = result.get("content", "")[:100]
                print(f"   {i}. Score: {score:.3f} | Content: {content}...")

        # Step 6: Verify data in database
        print("\n📦 Step 6: Verifying database state...")

        async with db_pool.acquire() as conn:
            source_count = await conn.fetchval("SELECT COUNT(*) FROM sources")
            doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
            chunk_count = await conn.fetchval("SELECT COUNT(*) FROM chunks")

            print(f"   Sources: {source_count}")
            print(f"   Documents: {doc_count}")
            print(f"   Chunks: {chunk_count}")

        # Step 7: Verify vectors in Qdrant
        print("\n📦 Step 7: Verifying Qdrant collection...")

        collection_info = await qdrant_client.get_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME
        )
        vector_count = collection_info.points_count
        print(f"   Vectors in Qdrant: {vector_count}")

        print("\n" + "=" * 70)
        print("✅ Pipeline test completed successfully!")
        print("\nSummary:")
        print(f"  - Created 1 source")
        print(f"  - Ingested 1 document")
        print(f"  - Generated {chunk_count} chunks with embeddings")
        print(f"  - Stored {vector_count} vectors in Qdrant")
        print(f"  - Tested {len(test_queries)} search queries")

    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await qdrant_client.close()
        await db_pool.close()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(test_pipeline())
