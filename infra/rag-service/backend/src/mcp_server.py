"""MCP Server Entry Point for RAG Service.

This module provides the MCP server implementation using FastMCP with STDIO transport.
It registers all MCP tools (search, document, source) and initializes all required services.

Pattern: FastMCP server with STDIO transport
References:
- infra/vibesbox/src/mcp_server.py (FastMCP pattern)
- infra/task-manager/backend/src/mcp_server.py (Service initialization pattern)
- prps/rag_service_implementation/examples/02_mcp_consolidated_tools.py

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #2: Store POOL in app state, not connections
- Gotcha #6: MCP tools MUST return JSON strings (not dicts)
- Gotcha #8: Use async with pool.acquire() for connection management
- Gotcha #9: HNSW disabled during bulk upload (m=0) for 60-90x speedup

Architecture:
- FastMCP server with tool registration pattern
- Service initialization in main() before server run
- Services stored in mcp.context for tool access
- STDIO transport for Claude Desktop integration
- Graceful shutdown with resource cleanup
"""

import asyncio
import logging
import sys

import asyncpg
from mcp.server.fastmcp import FastMCP
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

from src.config.settings import settings
from src.services.vector_service import VectorService
from src.services.source_service import SourceService
from src.services.document_service import DocumentService
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.document_parser import DocumentParser
from src.services.chunker import TextChunker
from src.services.ingestion_service import IngestionService
from src.services.search.base_search_strategy import BaseSearchStrategy
from src.services.search.hybrid_search_strategy import HybridSearchStrategy
from src.services.search.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # CRITICAL: Log to stderr for STDIO transport
)
logger = logging.getLogger(__name__)

# Create FastMCP server with STDIO transport
# PATTERN FROM: vibesbox/src/mcp_server.py
mcp = FastMCP(
    "RAG Service",
    # No host/port for STDIO transport - Claude Desktop communicates via stdin/stdout
)


async def initialize_services():
    """Initialize all services and store in MCP context.

    This function initializes the complete service dependency tree:
    1. Database connection pool (asyncpg)
    2. Qdrant vector database client
    3. Base services (Vector, Source, Document, Embedding)
    4. Composite services (DocumentParser, TextChunker)
    5. High-level services (IngestionService, RAGService)

    Services are stored in mcp context for tool access.

    CRITICAL PATTERNS:
    - Store POOL in context, not connections (Gotcha #2)
    - HNSW disabled (m=0) during bulk upload for 60-90x speedup (Gotcha #9)
    - Use async with pool.acquire() in services (Gotcha #8)

    Returns:
        Tuple of (db_pool, qdrant_client) for cleanup

    Raises:
        Exception: If service initialization fails
    """
    logger.info("🚀 Initializing RAG Service MCP server...")

    try:
        # Initialize database connection pool
        # CRITICAL: Store POOL, not connections (Gotcha #2)
        logger.info("Step 1/9: Creating database connection pool...")
        db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DATABASE_POOL_MIN_SIZE,
            max_size=settings.DATABASE_POOL_MAX_SIZE,
            command_timeout=60,
        )
        logger.info(
            f"✅ Database pool created "
            f"(min={settings.DATABASE_POOL_MIN_SIZE}, max={settings.DATABASE_POOL_MAX_SIZE})"
        )
    except Exception as e:
        logger.error(f"❌ Failed to create database pool: {e}")
        raise

    try:
        # Initialize Qdrant vector database client
        logger.info("Step 2/9: Initializing Qdrant client...")
        qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)
        logger.info(f"✅ Qdrant client initialized (url={settings.QDRANT_URL})")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        await db_pool.close()
        raise

    try:
        # CRITICAL: Initialize Qdrant collection with HNSW disabled for bulk upload (Gotcha #9)
        logger.info("Step 3/9: Ensuring Qdrant collection exists...")
        collections = await qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if settings.QDRANT_COLLECTION_NAME not in collection_names:
            await qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.OPENAI_EMBEDDING_DIMENSION,  # 1536 for text-embedding-3-small
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(m=0),  # Disable HNSW for bulk upload (Gotcha #9)
                ),
            )
            logger.info(
                f"✅ Qdrant collection created: {settings.QDRANT_COLLECTION_NAME} "
                f"(dims={settings.OPENAI_EMBEDDING_DIMENSION}, HNSW disabled)"
            )
        else:
            logger.info(f"✅ Qdrant collection exists: {settings.QDRANT_COLLECTION_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant collection: {e}")
        await qdrant_client.close()
        await db_pool.close()
        raise

    try:
        # Initialize base services
        logger.info("Step 4/9: Initializing VectorService...")
        vector_service = VectorService(
            qdrant_client=qdrant_client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
        )
        logger.info("✅ VectorService initialized")

        logger.info("Step 5/9: Initializing SourceService, DocumentService, EmbeddingService...")
        source_service = SourceService(db_pool=db_pool)
        document_service = DocumentService(db_pool=db_pool)
        embedding_service = EmbeddingService(
            db_pool=db_pool,
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            model=settings.OPENAI_EMBEDDING_MODEL,
            dimensions=settings.OPENAI_EMBEDDING_DIMENSION,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
        )
        logger.info("✅ Base services initialized")

        # Initialize composite services
        logger.info("Step 6/9: Initializing DocumentParser and TextChunker...")
        document_parser = DocumentParser()
        text_chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        logger.info("✅ Composite services initialized")

        # Initialize IngestionService
        logger.info("Step 7/9: Initializing IngestionService...")
        ingestion_service = IngestionService(
            db_pool=db_pool,
            document_parser=document_parser,
            text_chunker=text_chunker,
            embedding_service=embedding_service,
            vector_service=vector_service,
            document_service=document_service,
        )
        logger.info("✅ IngestionService initialized")

        # Initialize search strategies
        logger.info("Step 8/9: Initializing search strategies...")
        base_search_strategy = BaseSearchStrategy(
            vector_service=vector_service,
            embedding_service=embedding_service,
            db_pool=db_pool,
        )

        # Initialize HybridSearchStrategy if enabled
        hybrid_search_strategy = None
        if settings.USE_HYBRID_SEARCH:
            hybrid_search_strategy = HybridSearchStrategy(
                vector_service=vector_service,
                embedding_service=embedding_service,
                db_pool=db_pool,
            )
            logger.info("✅ Hybrid search strategy initialized")
        else:
            logger.info("ℹ️  Hybrid search disabled (USE_HYBRID_SEARCH=False)")

        # Initialize RAGService
        logger.info("Step 9/9: Initializing RAGService...")
        rag_service = RAGService(
            base_strategy=base_search_strategy,
            hybrid_strategy=hybrid_search_strategy,
            use_hybrid=settings.USE_HYBRID_SEARCH,
        )
        logger.info("✅ RAGService initialized")

        # Store all services in MCP context for tool access
        # PATTERN: Store services in mcp context (similar to FastAPI app.state)
        # Tools will access via ctx.app (FastMCP context object)
        mcp.app.state = type('State', (), {})()  # Create state namespace
        mcp.app.state.db_pool = db_pool
        mcp.app.state.qdrant_client = qdrant_client
        mcp.app.state.vector_service = vector_service
        mcp.app.state.source_service = source_service
        mcp.app.state.document_service = document_service
        mcp.app.state.embedding_service = embedding_service
        mcp.app.state.document_parser = document_parser
        mcp.app.state.text_chunker = text_chunker
        mcp.app.state.ingestion_service = ingestion_service
        mcp.app.state.rag_service = rag_service

        logger.info("✅ All services initialized and stored in MCP context")

        return db_pool, qdrant_client

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        await qdrant_client.close()
        await db_pool.close()
        raise


# Register all MCP tools
# PATTERN: Import register functions and call them
# Tools are registered via @mcp.tool() decorators in respective modules
logger.info("Registering MCP tools...")

try:
    from src.tools.search_tools import register_search_tools
    from src.tools.document_tools import register_document_tools

    # Register search tools (search_knowledge_base)
    register_search_tools(mcp)
    logger.info("✓ Search tools registered")

    # Register document tools (manage_document)
    register_document_tools(mcp)
    logger.info("✓ Document tools registered")

    # Note: source_tools uses async function pattern, not register function
    # Import the tool function directly to register via decorator
    from src.tools.source_tools import manage_source

    # Register source tool by making it available to MCP
    @mcp.tool()
    async def rag_manage_source(
        action: str,
        source_id: str | None = None,
        source_type: str | None = None,
        url: str | None = None,
        status: str | None = None,
        metadata: dict | None = None,
        error_message: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> str:
        """Manage RAG sources (consolidated: create/update/delete/get/list).

        Wrapper for manage_source tool to integrate with FastMCP.
        See source_tools.manage_source for full documentation.
        """
        return await manage_source(
            action=action,
            source_id=source_id,
            source_type=source_type,
            url=url,
            status=status,
            metadata=metadata,
            error_message=error_message,
            limit=limit,
            offset=offset,
        )

    logger.info("✓ Source tools registered")
    logger.info("✅ All MCP tools registered successfully")

except ImportError as e:
    logger.error(f"❌ Failed to import MCP tools: {e}")
    raise
except Exception as e:
    logger.error(f"❌ Failed to register MCP tools: {e}")
    raise


async def main():
    """Main entry point for MCP server.

    Initializes services, runs MCP server with STDIO transport,
    and handles graceful shutdown.

    CRITICAL PATTERNS:
    - STDIO transport for Claude Desktop integration
    - Graceful shutdown with resource cleanup
    - Exception handling for initialization failures
    """
    db_pool = None
    qdrant_client = None

    try:
        # Initialize all services
        db_pool, qdrant_client = await initialize_services()

        # Run MCP server with STDIO transport
        # PATTERN FROM: vibesbox/src/mcp_server.py
        logger.info("🚀 Starting RAG Service MCP server...")
        logger.info("   Transport: STDIO (for Claude Desktop)")
        logger.info("   Tools: search_knowledge_base, manage_document, rag_manage_source")
        logger.info("=" * 70)

        # Run server - this blocks until shutdown
        await mcp.run(transport="stdio")

    except KeyboardInterrupt:
        logger.info("⚠️  RAG Service MCP server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error in MCP server: {e}", exc_info=True)
        raise
    finally:
        # Graceful shutdown - close all resources
        logger.info("🛑 Shutting down RAG Service MCP server...")

        try:
            if qdrant_client:
                await qdrant_client.close()
                logger.info("✅ Qdrant client closed")
        except Exception as e:
            logger.error(f"❌ Error closing Qdrant client: {e}", exc_info=True)

        try:
            if db_pool:
                await db_pool.close()
                logger.info("✅ Database pool closed")
        except Exception as e:
            logger.error(f"❌ Error closing database pool: {e}", exc_info=True)

        logger.info("✅ RAG Service MCP server shutdown complete")


# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Already handled in main()
        pass
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
