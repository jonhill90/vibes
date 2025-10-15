"""MCP Server Entry Point for RAG Service.

This module provides the MCP server implementation using FastMCP with HTTP transport.
It registers all MCP tools (search, document, source) and initializes all required services.

Pattern: FastMCP server with Streamable HTTP transport
References:
- Example 01: prps/rag_service_completion/examples/01_mcp_http_server_setup.py
- Example 02: prps/rag_service_completion/examples/02_openai_client_initialization.py
- infra/task-manager/backend/src/mcp_server.py (JSON string returns, consolidated tools)

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #2: AsyncOpenAI client initialized and injected into EmbeddingService
- Gotcha #3: MCP tools MUST return JSON strings (not dicts)
- Gotcha #2: Store POOL in app state, not connections
- Gotcha #8: Use async with pool.acquire() for connection management
- Gotcha #9: HNSW disabled during bulk upload (m=0) for 60-90x speedup

Architecture:
- FastMCP server with HTTP transport on port 8002
- Service initialization before server run
- Services stored in mcp.app.state for tool access
- Graceful shutdown with resource cleanup
"""

import asyncio
import logging
import sys

import asyncpg
from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI
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
    stream=sys.stderr  # CRITICAL: Log to stderr for HTTP transport
)
logger = logging.getLogger(__name__)

# Create FastMCP server with HTTP transport configuration
# PATTERN FROM: Example 01 (01_mcp_http_server_setup.py)
# CRITICAL: Use port 8002 to avoid conflicts (8000=task-manager, 8001=api)
mcp = FastMCP(
    "RAG Service",
    host="0.0.0.0",  # Listen on all interfaces (required for Docker)
    port=8002  # HTTP port for MCP server
)


async def initialize_services():
    """Initialize all services and store in MCP context.

    This function initializes the complete service dependency tree:
    1. Database connection pool (asyncpg)
    2. OpenAI AsyncClient (CRITICAL: Gotcha #2 fix)
    3. Qdrant vector database client
    4. Base services (Vector, Source, Document, Embedding)
    5. Composite services (DocumentParser, TextChunker)
    6. High-level services (IngestionService, RAGService)

    Services are stored in mcp.app.state for tool access.

    CRITICAL PATTERNS:
    - Initialize AsyncOpenAI BEFORE EmbeddingService (Gotcha #2)
    - Store POOL in context, not connections (Gotcha #2)
    - HNSW disabled (m=0) during bulk upload for 60-90x speedup (Gotcha #9)
    - Use async with pool.acquire() in services (Gotcha #8)

    Returns:
        Tuple of (db_pool, openai_client, qdrant_client) for cleanup

    Raises:
        Exception: If service initialization fails
    """
    logger.info("🚀 Initializing RAG Service MCP server...")

    try:
        # Initialize database connection pool
        # CRITICAL: Store POOL, not connections (Gotcha #2)
        logger.info("Step 1/10: Creating database connection pool...")
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
        # CRITICAL: Initialize OpenAI client BEFORE EmbeddingService (Gotcha #2)
        # PATTERN FROM: Example 02 (02_openai_client_initialization.py)
        logger.info("Step 2/10: Initializing OpenAI AsyncClient...")
        openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            max_retries=3,
            timeout=30.0
        )
        logger.info(f"✅ OpenAI client initialized (model={settings.OPENAI_EMBEDDING_MODEL})")
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        await db_pool.close()
        raise

    try:
        # Initialize Qdrant vector database client
        logger.info("Step 3/10: Initializing Qdrant client...")
        qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)
        logger.info(f"✅ Qdrant client initialized (url={settings.QDRANT_URL})")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        await db_pool.close()
        raise

    try:
        # CRITICAL: Initialize Qdrant collection with HNSW disabled for bulk upload (Gotcha #9)
        logger.info("Step 4/10: Ensuring Qdrant collection exists...")
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
        logger.info("Step 5/10: Initializing VectorService...")
        vector_service = VectorService(
            qdrant_client=qdrant_client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
        )
        logger.info("✅ VectorService initialized")

        logger.info("Step 6/10: Initializing SourceService and DocumentService...")
        source_service = SourceService(db_pool=db_pool)
        document_service = DocumentService(db_pool=db_pool)
        logger.info("✅ SourceService and DocumentService initialized")

        # CRITICAL: Initialize EmbeddingService with openai_client parameter (Gotcha #2 fix)
        # PATTERN FROM: Example 02 (02_openai_client_initialization.py)
        logger.info("Step 7/10: Initializing EmbeddingService with OpenAI client...")
        embedding_service = EmbeddingService(
            db_pool=db_pool,
            openai_client=openai_client,  # FIX: Inject the client
        )
        logger.info("✅ EmbeddingService initialized with OpenAI client")

        # Initialize composite services
        logger.info("Step 8/10: Initializing DocumentParser and TextChunker...")
        document_parser = DocumentParser()
        text_chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        logger.info("✅ Composite services initialized")

        # Initialize IngestionService
        logger.info("Step 9/10: Initializing IngestionService...")
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
        logger.info("Step 10/10: Initializing search strategies and RAGService...")
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
        rag_service = RAGService(
            base_strategy=base_search_strategy,
            hybrid_strategy=hybrid_search_strategy,
            use_hybrid=settings.USE_HYBRID_SEARCH,
        )
        logger.info("✅ RAGService initialized")

        # Store all services in MCP context for tool access
        # PATTERN: Store services in mcp.app.state (similar to FastAPI app.state)
        # Tools will access via mcp.app.state
        mcp.app.state = type('State', (), {})()  # Create state namespace
        mcp.app.state.db_pool = db_pool
        mcp.app.state.openai_client = openai_client
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

        return db_pool, openai_client, qdrant_client

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        await qdrant_client.close()
        await db_pool.close()
        raise


# Register all MCP tools
# PATTERN: Import tools modules to trigger @mcp.tool() decorators
# Tools are defined in src/tools/ and return JSON strings (Gotcha #3)
logger.info("Registering MCP tools...")

try:
    # Import tool modules to register via decorators
    # These imports will execute @mcp.tool() decorators and register the tools
    from src.tools import search_tools  # noqa: F401
    from src.tools import document_tools  # noqa: F401
    from src.tools import source_tools  # noqa: F401

    logger.info("✅ All MCP tools registered successfully")
    logger.info("   - search_knowledge_base (query, limit, source_id)")
    logger.info("   - manage_document (action: create/get/update/delete/list)")
    logger.info("   - rag_manage_source (action: create/get/update/delete/list)")

except ImportError as e:
    logger.error(f"❌ Failed to import MCP tools: {e}")
    raise
except Exception as e:
    logger.error(f"❌ Failed to register MCP tools: {e}")
    raise


async def main():
    """Main entry point for MCP server.

    Initializes services, runs MCP server with HTTP transport,
    and handles graceful shutdown.

    CRITICAL PATTERNS:
    - HTTP transport on port 8002 (not STDIO)
    - Graceful shutdown with resource cleanup
    - Exception handling for initialization failures
    """
    db_pool = None
    openai_client = None
    qdrant_client = None

    try:
        # Initialize all services
        db_pool, openai_client, qdrant_client = await initialize_services()

        # Run MCP server with HTTP transport
        # PATTERN FROM: Example 01 (01_mcp_http_server_setup.py)
        logger.info("=" * 70)
        logger.info("🚀 Starting RAG Service MCP server...")
        logger.info("   Transport: Streamable HTTP")
        logger.info("   URL: http://0.0.0.0:8002/mcp")
        logger.info("   Tools: search_knowledge_base, manage_document, rag_manage_source")
        logger.info("=" * 70)

        # Run server - this blocks until shutdown
        # CRITICAL: Use transport="streamable-http" for HTTP mode (not "stdio")
        await mcp.run(transport="streamable-http")

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

        # Note: AsyncOpenAI client doesn't need explicit close

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
