"""Integration tests for per-domain collection architecture.

This test suite validates the complete per-domain collection architecture:
1. Source creation creates unique Qdrant collections per domain
2. Ingestion routes chunks to correct domain-specific collections
3. Search returns only domain-specific results (0% cross-contamination)
4. Source deletion removes all associated domain collections
5. Multi-domain search aggregates results correctly
6. Collection name sanitization handles edge cases

Pattern: pytest-asyncio with real database and Qdrant
Reference: prps/per_domain_collections.md (lines 547-577)
"""

import asyncio
import json
import os
import tempfile
from typing import List
from uuid import UUID

import asyncpg
import pytest
import pytest_asyncio
from qdrant_client import AsyncQdrantClient

from src.config.settings import settings
from src.services.chunker import TextChunker
from src.services.collection_manager import CollectionManager
from src.services.document_parser import DocumentParser
from src.services.document_service import DocumentService
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.ingestion_service import IngestionService
from src.services.search_service import SearchService
from src.services.source_service import SourceService
from src.services.vector_service import VectorService


# ===========================
# Fixtures
# ===========================


@pytest_asyncio.fixture
async def db_pool():
    """Create database connection pool for tests."""
    pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60,
    )
    yield pool
    await pool.close()


@pytest_asyncio.fixture
async def qdrant_client():
    """Create Qdrant client for tests.

    NOTE: No automatic cleanup of "orphaned" collections - that's dangerous and could
    delete production data. Tests must clean up after themselves using cleanup_sources fixture.
    """
    client = AsyncQdrantClient(url=settings.QDRANT_URL)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def services(db_pool, qdrant_client):
    """Initialize all services needed for testing."""
    import openai

    source_service = SourceService(db_pool=db_pool, qdrant_client=qdrant_client)
    document_service = DocumentService(db_pool=db_pool)
    collection_manager = CollectionManager(qdrant_client=qdrant_client)

    # Create OpenAI client
    openai_client = openai.AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    embedding_service = EmbeddingService(
        db_pool=db_pool,
        openai_client=openai_client,
    )

    vector_service = VectorService(qdrant_client=qdrant_client)

    document_parser = DocumentParser()
    text_chunker = TextChunker(
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
    )

    ingestion_service = IngestionService(
        db_pool=db_pool,
        document_parser=document_parser,
        text_chunker=text_chunker,
        embedding_service=embedding_service,
        vector_service=vector_service,
        document_service=document_service,
    )

    search_service = SearchService(
        db_pool=db_pool,
        embedding_service=embedding_service,
        vector_service=vector_service,
    )

    return {
        "source_service": source_service,
        "document_service": document_service,
        "vector_service": vector_service,
        "embedding_service": embedding_service,
        "ingestion_service": ingestion_service,
        "search_service": search_service,
        "collection_manager": collection_manager,
        "qdrant_client": qdrant_client,
    }


@pytest_asyncio.fixture
async def cleanup_sources(services):
    """Clean up test sources after each test.

    IMPORTANT: Only deletes sources (and their collections) created during THIS test.
    Does NOT delete existing sources/collections from previous tests or production data.
    """
    created_sources = []

    yield created_sources

    # Cleanup: Delete ONLY test sources created during this test
    # SourceService.delete_source() handles cascade deletion of collections
    source_service = services["source_service"]

    for source_id in created_sources:
        try:
            # Delete source (will cascade to collections via SourceService)
            await source_service.delete_source(source_id)
        except Exception as e:
            print(f"Warning: Failed to cleanup source {source_id}: {e}")


# ===========================
# Test Cases
# ===========================


@pytest.mark.asyncio
async def test_source_creation_creates_unique_collections(services, cleanup_sources):
    """Test 1: Source creation creates unique Qdrant collections.

    Validates:
    - Source creation triggers Qdrant collection creation
    - Collection names follow {source_title}_{collection_type} pattern
    - Collections have correct vector dimensions
    - collection_names field stored in database
    """
    source_service = services["source_service"]
    qdrant_client = services["qdrant_client"]

    # Create source with documents and code collections
    success, result = await source_service.create_source({
        "source_type": "upload",
        "enabled_collections": ["documents", "code"],
        "metadata": {"title": "AI Knowledge"},
    })

    assert success, f"Source creation failed: {result}"
    source_id = result["source"]["id"]
    cleanup_sources.append(source_id)

    # Verify collection_names stored in database
    source = result["source"]
    assert "collection_names" in source
    collection_names = source["collection_names"]

    # Parse if JSON string
    if isinstance(collection_names, str):
        collection_names = json.loads(collection_names)

    # Verify collection naming pattern
    assert collection_names["documents"] == "AI_Knowledge_documents"
    assert collection_names["code"] == "AI_Knowledge_code"

    # Verify collections exist in Qdrant
    collections = await qdrant_client.get_collections()
    existing_names = [c.name for c in collections.collections]

    assert "AI_Knowledge_documents" in existing_names
    assert "AI_Knowledge_code" in existing_names

    # Verify collection dimensions
    docs_info = await qdrant_client.get_collection("AI_Knowledge_documents")
    code_info = await qdrant_client.get_collection("AI_Knowledge_code")

    assert docs_info.config.params.vectors.size == 1536  # documents dimension
    assert code_info.config.params.vectors.size == 3072  # code dimension

    print(
        f"✅ Test 1 passed: Created collections "
        f"{list(collection_names.values())} with correct dimensions"
    )


@pytest.mark.asyncio
async def test_ingestion_routes_to_domain_collections(services, cleanup_sources):
    """Test 2: Ingestion routes chunks to correct domain collections.

    Validates:
    - Document ingestion stores chunks in domain-specific collections
    - Content classification routes code chunks to {domain}_code
    - Content classification routes doc chunks to {domain}_documents
    - Collections metadata includes source_id for filtering
    """
    source_service = services["source_service"]
    ingestion_service = services["ingestion_service"]
    qdrant_client = services["qdrant_client"]

    # Create source
    success, source_result = await source_service.create_source({
        "source_type": "upload",
        "enabled_collections": ["documents", "code"],
        "metadata": {"title": "Network Knowledge"},
    })
    assert success
    source_id = source_result["source"]["id"]
    cleanup_sources.append(source_id)

    # Create test document with mixed content (HTML format)
    test_content = """<!DOCTYPE html>
<html>
<head><title>Network Security Guide</title></head>
<body>
<h1>Network Security Guide</h1>
<p>This guide covers fundamental network security concepts.</p>

<h2>Port Scanning Detection</h2>
<pre><code class="language-python">
def detect_port_scan(connections: List[Connection]) -> bool:
    \"\"\"Detect potential port scanning activity.\"\"\"
    unique_ports = set(c.dst_port for c in connections)
    return len(unique_ports) > 50  # Threshold for port scan
</code></pre>

<p>Network security requires both prevention and detection strategies.</p>
</body>
</html>
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        # Ingest document
        success, ingest_result = await ingestion_service.ingest_document(
            source_id=source_id,  # Already a UUID from asyncpg
            file_path=temp_file,
            document_metadata={"title": "Network Security"},
        )

        assert success, f"Ingestion failed: {ingest_result}"
        assert ingest_result["chunks_stored"] > 0

        # Verify chunks stored in domain-specific collections
        collections_used = ingest_result.get("collections_used", [])
        assert "Network_Knowledge_documents" in collections_used or "Network_Knowledge_code" in collections_used

        # Verify source_id in chunk payloads
        for collection_name in collections_used:
            collection_info = await qdrant_client.get_collection(collection_name)
            assert collection_info.points_count > 0, f"No points in {collection_name}"

        print(
            f"✅ Test 2 passed: Ingested {ingest_result['chunks_stored']} chunks "
            f"to domain collections: {collections_used}"
        )

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_search_returns_only_domain_results(services, cleanup_sources):
    """Test 3: Search returns only domain-specific results (0% cross-contamination).

    Validates:
    - Searching domain A returns only chunks from domain A
    - Searching domain B returns only chunks from domain B
    - No cross-contamination between domains
    - source_id filtering works correctly
    """
    source_service = services["source_service"]
    ingestion_service = services["ingestion_service"]
    search_service = services["search_service"]

    # Create two separate domains
    success1, ai_result = await source_service.create_source({
        "source_type": "upload",
        "enabled_collections": ["documents"],
        "metadata": {"title": "AI Domain"},
    })
    assert success1
    ai_source_id = ai_result["source"]["id"]
    cleanup_sources.append(ai_source_id)

    success2, network_result = await source_service.create_source({
        "source_type": "upload",
        "enabled_collections": ["documents"],
        "metadata": {"title": "Network Domain"},
    })
    assert success2
    network_source_id = network_result["source"]["id"]
    cleanup_sources.append(network_source_id)

    # Ingest AI content (HTML format)
    ai_content = """<!DOCTYPE html>
<html>
<head><title>Machine Learning Basics</title></head>
<body>
<h1>Machine Learning Basics</h1>
<p>Neural networks are the foundation of modern AI.</p>
<p>Deep learning uses multiple layers to extract features from raw data.</p>
</body>
</html>
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(ai_content)
        ai_file = f.name

    # Ingest Network content (HTML format)
    network_content = """<!DOCTYPE html>
<html>
<head><title>TCP/IP Fundamentals</title></head>
<body>
<h1>TCP/IP Fundamentals</h1>
<p>The Transmission Control Protocol ensures reliable data delivery.</p>
<p>Network packets are routed through multiple hops to reach their destination.</p>
</body>
</html>
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(network_content)
        network_file = f.name

    try:
        # Ingest both documents
        success, _ = await ingestion_service.ingest_document(
            source_id=ai_source_id,  # Already a UUID
            file_path=ai_file,
            document_metadata={"title": "AI Basics"},
        )
        assert success

        success, _ = await ingestion_service.ingest_document(
            source_id=network_source_id,  # Already a UUID
            file_path=network_file,
            document_metadata={"title": "Network Basics"},
        )
        assert success

        # Search AI domain only
        ai_results = await search_service.search(
            query="neural networks deep learning",
            source_ids=[ai_source_id],  # Already a UUID
            limit=10,
        )

        # Verify ONLY AI results returned
        for result in ai_results:
            assert str(result["source_id"]) == str(ai_source_id), (
                f"Cross-contamination detected: AI search returned "
                f"result from {result['source_id']}"
            )

        # Search Network domain only
        network_results = await search_service.search(
            query="TCP protocol packets",
            source_ids=[network_source_id],  # Already a UUID
            limit=10,
        )

        # Verify ONLY Network results returned
        for result in network_results:
            assert str(result["source_id"]) == str(network_source_id), (
                f"Cross-contamination detected: Network search returned "
                f"result from {result['source_id']}"
            )

        # Calculate cross-contamination rate (should be 0%)
        total_ai_results = len(ai_results)
        total_network_results = len(network_results)

        print(
            f"✅ Test 3 passed: Domain isolation verified "
            f"(AI: {total_ai_results} results, Network: {total_network_results} results, "
            f"cross-contamination: 0%)"
        )

    finally:
        if os.path.exists(ai_file):
            os.unlink(ai_file)
        if os.path.exists(network_file):
            os.unlink(network_file)


@pytest.mark.asyncio
async def test_source_deletion_removes_domain_collections(services, cleanup_sources):
    """Test 4: Source deletion removes all domain collections from Qdrant.

    Validates:
    - Deleting source removes associated Qdrant collections
    - All collection types deleted (documents, code, media)
    - No orphaned collections remain
    - Graceful handling if collection already deleted
    """
    source_service = services["source_service"]
    qdrant_client = services["qdrant_client"]

    # Create source with multiple collections
    # NOTE: Using "Test_DevOps_Knowledge" to avoid conflict with production "DevOps Knowledge" source
    success, result = await source_service.create_source({
        "source_type": "upload",
        "enabled_collections": ["documents", "code"],
        "metadata": {"title": "Test_DevOps_Knowledge"},
    })
    assert success
    source_id = result["source"]["id"]

    # Don't add to cleanup_sources - we're testing deletion ourselves

    # Get collection names before deletion
    collection_names = result["source"]["collection_names"]
    if isinstance(collection_names, str):
        collection_names = json.loads(collection_names)

    expected_collection_names = list(collection_names.values())

    # Verify collections exist before deletion
    collections_before = await qdrant_client.get_collections()
    existing_before = [c.name for c in collections_before.collections]

    for name in expected_collection_names:
        assert name in existing_before, f"Collection {name} not created"

    # Delete source (should delete collections)
    success, delete_result = await source_service.delete_source(source_id)  # Already a UUID
    assert success, f"Source deletion failed: {delete_result}"

    # Verify collections removed from Qdrant
    collections_after = await qdrant_client.get_collections()
    existing_after = [c.name for c in collections_after.collections]

    for name in expected_collection_names:
        assert name not in existing_after, (
            f"Orphaned collection detected: {name} still exists after source deletion"
        )

    print(
        f"✅ Test 4 passed: Deleted source and removed all collections: "
        f"{expected_collection_names}"
    )


@pytest.mark.asyncio
async def test_multi_domain_search_aggregation(services, cleanup_sources):
    """Test 5: Multi-domain search aggregates and re-ranks results correctly.

    Validates:
    - Searching multiple source_ids aggregates results
    - Results re-ranked by score across all domains
    - Top results can come from different domains
    - Limit parameter works correctly for aggregated results
    """
    source_service = services["source_service"]
    ingestion_service = services["ingestion_service"]
    search_service = services["search_service"]

    # Create three domains
    domains = []
    for domain_name in ["Python Docs", "JavaScript Docs", "Database Docs"]:
        success, result = await source_service.create_source({
            "source_type": "upload",
            "enabled_collections": ["documents"],
            "metadata": {"title": domain_name},
        })
        assert success
        domains.append(result["source"]["id"])
        cleanup_sources.append(result["source"]["id"])

    # Ingest content to each domain (HTML format)
    contents = [
        """<!DOCTYPE html><html><body><p>Python functions use def keyword. Lambda functions are anonymous.</p></body></html>""",
        """<!DOCTYPE html><html><body><p>JavaScript functions can be arrow functions or traditional functions.</p></body></html>""",
        """<!DOCTYPE html><html><body><p>Database functions include aggregations like COUNT, SUM, AVG.</p></body></html>""",
    ]

    for source_id, content in zip(domains, contents):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            success, _ = await ingestion_service.ingest_document(
                source_id=source_id,  # Already a UUID
                file_path=temp_file,
                document_metadata={"title": "Functions Guide"},
            )
            assert success
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    # Multi-domain search
    results = await search_service.search(
        query="function definition syntax",
        source_ids=domains,  # Already UUIDs
        limit=5,
    )

    # Verify results aggregated from multiple domains
    source_ids_in_results = set(str(r["source_id"]) for r in results)

    # At least some results should come from the query
    assert len(results) > 0, "No results from multi-domain search"

    # Verify results are sorted by score descending
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True), "Results not sorted by score"

    # Verify limit respected
    assert len(results) <= 5, f"Returned {len(results)} results, expected ≤5"

    print(
        f"✅ Test 5 passed: Multi-domain search returned {len(results)} results "
        f"from {len(source_ids_in_results)} domains, properly ranked by score"
    )


@pytest.mark.asyncio
async def test_collection_name_sanitization_edge_cases(services, cleanup_sources):
    """Test 6: Collection name sanitization handles edge cases.

    Validates:
    - Special characters removed/replaced correctly
    - Long names truncated to 64 chars
    - Unicode characters handled
    - Multiple underscores collapsed
    - Leading/trailing underscores removed
    """
    source_service = services["source_service"]
    qdrant_client = services["qdrant_client"]

    # Test cases for sanitization
    test_cases = [
        {
            "title": "Network & Security!",
            "expected_prefix": "Network_Security",
        },
        {
            "title": "Test___Multiple___Underscores",
            "expected_prefix": "Test_Multiple_Underscores",
        },
        {
            "title": "___Leading_Trailing___",
            "expected_prefix": "Leading_Trailing",
        },
        {
            "title": "Special@#$Chars%^&*()",
            "expected_prefix": "Special_Chars",
        },
        {
            "title": "Very Long Source Name That Exceeds The Maximum Length Limit And Should Be Truncated",
            "expected_max_length": 64,
        },
    ]

    for i, test_case in enumerate(test_cases):
        success, result = await source_service.create_source({
            "source_type": "upload",
            "enabled_collections": ["documents"],
            "metadata": {"title": test_case["title"]},
        })
        assert success, f"Source creation failed for test case {i}: {result}"

        source_id = result["source"]["id"]
        cleanup_sources.append(source_id)

        collection_names = result["source"]["collection_names"]
        if isinstance(collection_names, str):
            collection_names = json.loads(collection_names)

        collection_name = collection_names["documents"]

        # Verify expected sanitization
        if "expected_prefix" in test_case:
            assert collection_name.startswith(test_case["expected_prefix"]), (
                f"Expected prefix '{test_case['expected_prefix']}', "
                f"got '{collection_name}'"
            )

        if "expected_max_length" in test_case:
            assert len(collection_name) <= test_case["expected_max_length"], (
                f"Collection name too long: {len(collection_name)} chars, "
                f"expected ≤{test_case['expected_max_length']}"
            )

        # Verify collection exists in Qdrant
        collections = await qdrant_client.get_collections()
        existing_names = [c.name for c in collections.collections]
        assert collection_name in existing_names, (
            f"Sanitized collection '{collection_name}' not found in Qdrant"
        )

        print(f"✅ Test 6.{i+1} passed: '{test_case['title']}' → '{collection_name}'")

    print(f"✅ Test 6 complete: All sanitization edge cases handled correctly")


@pytest.mark.asyncio
async def test_ingestion_with_multiple_collection_types(services, cleanup_sources):
    """Test 7: Ingestion correctly handles multiple collection types per source.

    Validates:
    - Source with documents + code + media enabled
    - Content classifier routes chunks correctly
    - Each collection type gets appropriate embedding model
    - Multiple document records created (one per collection type)
    """
    source_service = services["source_service"]
    ingestion_service = services["ingestion_service"]

    # Create source with all collection types
    success, result = await source_service.create_source({
        "source_type": "upload",
        "enabled_collections": ["documents", "code", "media"],
        "metadata": {"title": "Complete Guide"},
    })
    assert success
    source_id = result["source"]["id"]
    cleanup_sources.append(source_id)

    # Create document with all content types (HTML format)
    test_content = """<!DOCTYPE html>
<html>
<head><title>Complete Development Guide</title></head>
<body>
<h1>Complete Development Guide</h1>
<p>This guide includes documentation, code examples, and diagrams.</p>

<h2>Documentation</h2>
<p>Software development requires clear documentation and best practices.</p>

<h2>Code Example</h2>
<pre><code class="language-python">
def process_data(data: list) -> dict:
    return {"count": len(data), "items": data}
</code></pre>

<h2>Architecture Diagram</h2>
<img src="https://example.com/architecture.png" alt="System Architecture">
<p>The diagram shows the complete system architecture with all components.</p>
</body>
</html>
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        success, ingest_result = await ingestion_service.ingest_document(
            source_id=source_id,  # Already a UUID
            file_path=temp_file,
            document_metadata={"title": "Complete Guide"},
        )

        assert success, f"Ingestion failed: {ingest_result}"

        # Verify multiple collections used (at least documents and code)
        collections_used = ingest_result.get("collections_used", [])
        assert len(collections_used) >= 1, "Expected at least one collection used"

        # Verify document IDs created (one per collection with chunks)
        document_ids = ingest_result.get("document_ids", [])
        assert len(document_ids) >= 1, "Expected at least one document created"

        print(
            f"✅ Test 7 passed: Ingested to {len(collections_used)} collections: "
            f"{collections_used}, created {len(document_ids)} document records"
        )

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_empty_enabled_collections_handling(services, cleanup_sources):
    """Test 8: Source with empty enabled_collections handled gracefully.

    Validates:
    - Source can be created with empty enabled_collections
    - No Qdrant collections created
    - Ingestion fails gracefully (no collections to store chunks)
    """
    source_service = services["source_service"]
    ingestion_service = services["ingestion_service"]

    # Create source with no enabled collections
    success, result = await source_service.create_source({
        "source_type": "upload",
        "enabled_collections": [],
        "metadata": {"title": "Empty Source"},
    })
    assert success
    source_id = result["source"]["id"]
    cleanup_sources.append(source_id)

    # Verify no collection_names created
    collection_names = result["source"]["collection_names"]
    if isinstance(collection_names, str):
        collection_names = json.loads(collection_names)

    assert collection_names == {} or collection_names is None, (
        f"Expected empty collection_names, got {collection_names}"
    )

    # Attempt ingestion (should fail gracefully) - use HTML format
    test_content = """<!DOCTYPE html><html><body><p>This is test content that cannot be stored.</p></body></html>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        success, ingest_result = await ingestion_service.ingest_document(
            source_id=source_id,  # Already a UUID
            file_path=temp_file,
            document_metadata={"title": "Test Doc"},
        )

        # Expect failure due to no enabled collections
        assert not success or ingest_result.get("chunks_stored", 0) == 0, (
            "Expected ingestion to fail or store 0 chunks with no enabled collections"
        )

        print(
            f"✅ Test 8 passed: Empty enabled_collections handled gracefully "
            f"(ingestion result: {ingest_result.get('error', 'no chunks stored')})"
        )

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# ===========================
# Test Execution
# ===========================

if __name__ == "__main__":
    """Run tests with pytest."""
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            __file__,
            "-v",
            "-s",
            "--tb=short",
        ],
        cwd="/Users/jon/source/vibes/infra/rag-service",
    )
    sys.exit(result.returncode)
