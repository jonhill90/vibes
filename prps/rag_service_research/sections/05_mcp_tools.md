# MCP Tools Specification

**Section**: 05 - MCP Tools
**Pattern**: Consolidated find/manage pattern from task-manager
**Status**: Complete

---

## Overview

The RAG service exposes 4 MCP tools following the consolidated find/manage pattern established in task-manager. All tools adhere to critical MCP protocol requirements:

- **JSON String Returns**: Tools MUST return JSON strings (not dicts) per MCP spec
- **Payload Optimization**: Large fields truncated to 1000 chars for AI context
- **Pagination Limits**: Maximum 20 items per page to prevent token overflow
- **Consistent Error Format**: All errors include suggestion field for recovery

---

## Tool Definitions

### 1. search_knowledge_base

**Purpose**: Search documents using vector similarity, hybrid search, or reranking strategies.

**Signature**:
```python
@mcp.tool()
async def search_knowledge_base(
    query: str,
    source_id: str | None = None,
    match_count: int = 10,
    search_type: str = "hybrid",  # "vector", "hybrid", "rerank"
    similarity_threshold: float = 0.05
) -> str:
    """Search documents with vector or hybrid search.

    Args:
        query: Natural language search query
        source_id: Optional filter to specific source/collection
        match_count: Number of results to return (max 50)
        search_type: Search strategy - "vector" (fast), "hybrid" (better recall), "rerank" (highest quality)
        similarity_threshold: Minimum cosine similarity (0.0-1.0, lower = more similar)

    Returns:
        JSON string with search results

    Examples:
        # Basic vector search
        search_knowledge_base(query="Python async patterns", match_count=5)

        # Hybrid search in specific source
        search_knowledge_base(
            query="database optimization",
            source_id="src_abc123",
            search_type="hybrid"
        )

        # High precision with reranking
        search_knowledge_base(
            query="authentication best practices",
            search_type="rerank",
            similarity_threshold=0.03
        )
    """
```

**Response Format**:
```json
{
  "success": true,
  "results": [
    {
      "chunk_id": "chunk_uuid",
      "document_id": "doc_uuid",
      "document_title": "Python Async Guide",
      "text": "Truncated to 1000 chars...",
      "score": 0.92,
      "match_type": "hybrid",
      "metadata": {
        "source_id": "src_abc123",
        "chunk_index": 3,
        "url": "https://docs.example.com/async"
      }
    }
  ],
  "count": 5,
  "search_type": "hybrid",
  "query": "Python async patterns"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Invalid source_id: src_abc123 not found",
  "suggestion": "Use manage_source(action='list') to see available sources"
}
```

**Implementation Strategy**:
```python
async def search_knowledge_base(...) -> str:
    try:
        # 1. Generate query embedding
        embedding = await embedding_service.create_embedding(query)

        # 2. Select search strategy
        if search_type == "vector":
            results = await rag_service.base_strategy.search(embedding, match_count)
        elif search_type == "hybrid":
            results = await rag_service.hybrid_strategy.search(query, embedding, match_count)
        elif search_type == "rerank":
            results = await rag_service.reranking_strategy.search(query, embedding, match_count)
        else:
            return json.dumps({
                "success": False,
                "error": f"Invalid search_type: {search_type}",
                "suggestion": "Use 'vector', 'hybrid', or 'rerank'"
            })

        # 3. Apply filters
        if source_id:
            results = [r for r in results if r.get("metadata", {}).get("source_id") == source_id]

        # 4. Apply similarity threshold
        results = [r for r in results if r["score"] >= (1 - similarity_threshold)]

        # 5. Optimize for MCP (truncate text)
        optimized_results = [optimize_result_for_mcp(r) for r in results]

        # 6. Return JSON string (CRITICAL)
        return json.dumps({
            "success": True,
            "results": optimized_results,
            "count": len(optimized_results),
            "search_type": search_type,
            "query": query
        })

    except Exception as e:
        logger.error(f"Error in search_knowledge_base: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check query format and try again"
        })
```

---

### 2. manage_document

**Purpose**: Consolidated tool for document lifecycle (create, update, delete, get).

**Signature**:
```python
@mcp.tool()
async def manage_document(
    action: str,  # "create", "update", "delete", "get", "list"
    document_id: str | None = None,
    file_path: str | None = None,
    source_id: str | None = None,
    title: str | None = None,
    url: str | None = None,
    metadata: dict | None = None,
    page: int = 1,
    per_page: int = 10
) -> str:
    """Manage documents (upload, update, delete, retrieve).

    Args:
        action: Operation - "create", "update", "delete", "get", "list"
        document_id: Document UUID for get/update/delete
        file_path: Local file path for create (PDF, HTML, TXT, etc.)
        source_id: Source UUID to associate with document
        title: Document title (optional, extracted from file if not provided)
        url: Original URL if document was fetched from web
        metadata: Additional metadata (tags, author, date, etc.)
        page: Page number for list operation (default 1)
        per_page: Items per page for list (max 20)

    Returns:
        JSON string with operation result

    Examples:
        # Upload a document
        manage_document(
            action="create",
            file_path="/path/to/research.pdf",
            source_id="src_abc123",
            title="Research Paper on RAG",
            metadata={"author": "John Doe", "year": 2024}
        )

        # Get document details
        manage_document(action="get", document_id="doc_xyz789")

        # Update document metadata
        manage_document(
            action="update",
            document_id="doc_xyz789",
            title="Updated Title",
            metadata={"reviewed": true}
        )

        # List documents in a source
        manage_document(action="list", source_id="src_abc123", per_page=20)

        # Delete document (also deletes chunks and vectors)
        manage_document(action="delete", document_id="doc_xyz789")
    """
```

**Response Format (create)**:
```json
{
  "success": true,
  "document": {
    "id": "doc_uuid",
    "title": "Research Paper on RAG",
    "source_id": "src_abc123",
    "document_type": "pdf",
    "url": null,
    "chunks_created": 47,
    "status": "completed",
    "created_at": "2024-10-11T18:00:00Z",
    "metadata": {
      "author": "John Doe",
      "year": 2024,
      "pages": 15
    }
  },
  "message": "Document ingested successfully with 47 chunks"
}
```

**Response Format (list)**:
```json
{
  "success": true,
  "documents": [
    {
      "id": "doc_uuid_1",
      "title": "Document 1",
      "source_id": "src_abc123",
      "document_type": "pdf",
      "chunks_count": 47,
      "created_at": "2024-10-11T18:00:00Z"
    }
  ],
  "total_count": 156,
  "count": 10,
  "page": 1,
  "per_page": 10
}
```

**Implementation Strategy**:
```python
async def manage_document(action: str, ...) -> str:
    try:
        db_pool = await get_pool()
        document_service = DocumentService(db_pool, vector_service)

        if action == "create":
            # Validation
            if not file_path:
                return json.dumps({
                    "success": False,
                    "error": "file_path required for create",
                    "suggestion": "Provide file_path to upload document"
                })

            # Ingest document
            success, result = await document_service.ingest_document(
                file_path=file_path,
                source_id=source_id,
                title=title,
                url=url,
                metadata=metadata or {}
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to ingest document"),
                    "suggestion": result.get("suggestion", "Check file format and try again")
                })

            # Optimize for MCP
            document = optimize_document_for_mcp(result.get("document"))

            return json.dumps({
                "success": True,
                "document": document,
                "message": result.get("message", "Document created successfully")
            })

        elif action == "get":
            if not document_id:
                return json.dumps({
                    "success": False,
                    "error": "document_id required for get",
                    "suggestion": "Provide document_id to retrieve"
                })

            success, result = await document_service.get_document(document_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Document not found"),
                    "suggestion": "Verify document_id or use manage_document(action='list')"
                })

            document = optimize_document_for_mcp(result.get("document"))

            return json.dumps({
                "success": True,
                "document": document
            })

        elif action == "list":
            # Limit per_page (Gotcha #7)
            per_page = min(per_page, MAX_DOCUMENTS_PER_PAGE)

            filters = {}
            if source_id:
                filters["source_id"] = source_id

            success, result = await document_service.list_documents(
                filters=filters,
                page=page,
                per_page=per_page,
                exclude_large_fields=True  # Critical for MCP
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to list documents"),
                    "suggestion": "Check error and try again"
                })

            documents = [optimize_document_for_mcp(d) for d in result.get("documents", [])]

            return json.dumps({
                "success": True,
                "documents": documents,
                "total_count": result.get("total_count", 0),
                "count": len(documents),
                "page": page,
                "per_page": per_page
            })

        elif action == "update":
            if not document_id:
                return json.dumps({
                    "success": False,
                    "error": "document_id required for update",
                    "suggestion": "Provide document_id to update"
                })

            success, result = await document_service.update_document(
                document_id=document_id,
                title=title,
                url=url,
                metadata=metadata
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to update document"),
                    "suggestion": "Verify document_id and field values"
                })

            document = optimize_document_for_mcp(result.get("document"))

            return json.dumps({
                "success": True,
                "document": document,
                "message": "Document updated successfully"
            })

        elif action == "delete":
            if not document_id:
                return json.dumps({
                    "success": False,
                    "error": "document_id required for delete",
                    "suggestion": "Provide document_id to delete"
                })

            # Delete cascades to chunks and vectors
            success, result = await document_service.delete_document(document_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to delete document"),
                    "suggestion": "Verify document_id exists"
                })

            return json.dumps({
                "success": True,
                "message": result.get("message", "Document and associated chunks deleted successfully")
            })

        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "suggestion": "Use 'create', 'get', 'list', 'update', or 'delete'"
            })

    except Exception as e:
        logger.error(f"Error in manage_document ({action}): {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and parameters"
        })
```

---

### 3. manage_source

**Purpose**: Manage ingestion sources (collections of documents).

**Signature**:
```python
@mcp.tool()
async def manage_source(
    action: str,  # "create", "update", "delete", "list", "get"
    source_id: str | None = None,
    title: str | None = None,
    url: str | None = None,
    source_type: str = "upload",  # "upload", "crawl", "api"
    page: int = 1,
    per_page: int = 10
) -> str:
    """Manage ingestion sources (document collections).

    Args:
        action: Operation - "create", "update", "delete", "list", "get"
        source_id: Source UUID for get/update/delete
        title: Human-readable source name
        url: Base URL if source_type is "crawl" or "api"
        source_type: "upload" (manual files), "crawl" (website), "api" (external API)
        page: Page number for list operation
        per_page: Items per page for list (max 20)

    Returns:
        JSON string with operation result

    Examples:
        # Create upload source
        manage_source(
            action="create",
            title="Research Papers",
            source_type="upload"
        )

        # Create crawl source
        manage_source(
            action="create",
            title="Python Docs",
            url="https://docs.python.org/3/",
            source_type="crawl"
        )

        # List all sources
        manage_source(action="list")

        # Get source details with document count
        manage_source(action="get", source_id="src_abc123")

        # Delete source (also deletes documents, chunks, vectors)
        manage_source(action="delete", source_id="src_abc123")
    """
```

**Response Format (create)**:
```json
{
  "success": true,
  "source": {
    "id": "src_uuid",
    "title": "Research Papers",
    "url": null,
    "source_type": "upload",
    "status": "active",
    "documents_count": 0,
    "created_at": "2024-10-11T18:00:00Z",
    "updated_at": "2024-10-11T18:00:00Z"
  },
  "message": "Source created successfully"
}
```

**Response Format (list)**:
```json
{
  "success": true,
  "sources": [
    {
      "id": "src_uuid_1",
      "title": "Research Papers",
      "source_type": "upload",
      "documents_count": 47,
      "status": "active",
      "created_at": "2024-10-11T18:00:00Z"
    }
  ],
  "total_count": 5,
  "count": 5,
  "page": 1,
  "per_page": 10
}
```

**Implementation Strategy**:
```python
async def manage_source(action: str, ...) -> str:
    try:
        db_pool = await get_pool()
        source_service = SourceService(db_pool)

        if action == "create":
            if not title:
                return json.dumps({
                    "success": False,
                    "error": "title required for create",
                    "suggestion": "Provide title for the source"
                })

            success, result = await source_service.create_source(
                title=title,
                url=url,
                source_type=source_type
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to create source"),
                    "suggestion": "Check parameters and try again"
                })

            return json.dumps({
                "success": True,
                "source": result.get("source"),
                "message": "Source created successfully"
            })

        elif action == "get":
            if not source_id:
                return json.dumps({
                    "success": False,
                    "error": "source_id required for get",
                    "suggestion": "Provide source_id to retrieve"
                })

            success, result = await source_service.get_source_with_stats(source_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Source not found"),
                    "suggestion": "Verify source_id or use manage_source(action='list')"
                })

            return json.dumps({
                "success": True,
                "source": result.get("source")
            })

        elif action == "list":
            per_page = min(per_page, MAX_SOURCES_PER_PAGE)

            success, result = await source_service.list_sources(
                page=page,
                per_page=per_page
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to list sources"),
                    "suggestion": "Check error and try again"
                })

            return json.dumps({
                "success": True,
                "sources": result.get("sources", []),
                "total_count": result.get("total_count", 0),
                "count": len(result.get("sources", [])),
                "page": page,
                "per_page": per_page
            })

        elif action == "update":
            if not source_id:
                return json.dumps({
                    "success": False,
                    "error": "source_id required for update",
                    "suggestion": "Provide source_id to update"
                })

            success, result = await source_service.update_source(
                source_id=source_id,
                title=title,
                url=url
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to update source"),
                    "suggestion": "Verify source_id and field values"
                })

            return json.dumps({
                "success": True,
                "source": result.get("source"),
                "message": "Source updated successfully"
            })

        elif action == "delete":
            if not source_id:
                return json.dumps({
                    "success": False,
                    "error": "source_id required for delete",
                    "suggestion": "Provide source_id to delete"
                })

            # CASCADE DELETE to documents, chunks, vectors
            success, result = await source_service.delete_source(source_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to delete source"),
                    "suggestion": "Verify source_id exists"
                })

            return json.dumps({
                "success": True,
                "message": result.get("message", "Source and all associated documents deleted successfully")
            })

        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "suggestion": "Use 'create', 'get', 'list', 'update', or 'delete'"
            })

    except Exception as e:
        logger.error(f"Error in manage_source ({action}): {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and parameters"
        })
```

---

### 4. crawl_website

**Purpose**: Crawl a website and ingest content into the knowledge base.

**Signature**:
```python
@mcp.tool()
async def crawl_website(
    url: str,
    recursive: bool = False,
    max_pages: int = 10,
    source_id: str | None = None,
    title: str | None = None,
    exclude_patterns: list[str] | None = None
) -> str:
    """Crawl a website and ingest content.

    Args:
        url: Starting URL to crawl
        recursive: Follow links to other pages (default False)
        max_pages: Maximum number of pages to crawl (max 100)
        source_id: Existing source to add to (creates new if not provided)
        title: Source title if creating new (defaults to website domain)
        exclude_patterns: URL patterns to skip (e.g., ["/archive/", "/tag/"])

    Returns:
        JSON string with crawl job status

    Examples:
        # Crawl single page
        crawl_website(url="https://docs.example.com/guide")

        # Recursive crawl with limit
        crawl_website(
            url="https://docs.example.com/",
            recursive=True,
            max_pages=50,
            title="Example Docs",
            exclude_patterns=["/archive/", "/tag/"]
        )

        # Add pages to existing source
        crawl_website(
            url="https://docs.example.com/new-section/",
            recursive=True,
            max_pages=20,
            source_id="src_abc123"
        )
    """
```

**Response Format (started)**:
```json
{
  "success": true,
  "crawl_job": {
    "id": "job_uuid",
    "source_id": "src_uuid",
    "url": "https://docs.example.com/",
    "status": "running",
    "pages_crawled": 0,
    "pages_pending": 1,
    "max_pages": 50,
    "recursive": true,
    "created_at": "2024-10-11T18:00:00Z"
  },
  "message": "Crawl job started, use manage_crawl_job to check progress"
}
```

**Response Format (completed)**:
```json
{
  "success": true,
  "crawl_job": {
    "id": "job_uuid",
    "source_id": "src_uuid",
    "url": "https://docs.example.com/",
    "status": "completed",
    "pages_crawled": 47,
    "pages_failed": 3,
    "documents_created": 44,
    "total_chunks": 1247,
    "started_at": "2024-10-11T18:00:00Z",
    "completed_at": "2024-10-11T18:15:23Z"
  },
  "message": "Crawl completed: 47 pages crawled, 44 documents created"
}
```

**Implementation Strategy**:
```python
async def crawl_website(url: str, recursive: bool, max_pages: int, ...) -> str:
    try:
        # 1. Validate URL
        if not url.startswith(("http://", "https://")):
            return json.dumps({
                "success": False,
                "error": "Invalid URL: must start with http:// or https://",
                "suggestion": "Provide fully qualified URL"
            })

        # 2. Limit max_pages
        max_pages = min(max_pages, MAX_CRAWL_PAGES)

        # 3. Create or get source
        db_pool = await get_pool()
        source_service = SourceService(db_pool)

        if not source_id:
            # Create new source
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            title = title or f"Crawled: {domain}"

            success, result = await source_service.create_source(
                title=title,
                url=url,
                source_type="crawl"
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": "Failed to create source",
                    "suggestion": result.get("error", "Check URL and try again")
                })

            source_id = result["source"]["id"]

        # 4. Create crawl job
        crawl_service = CrawlService(db_pool)

        success, result = await crawl_service.start_crawl_job(
            source_id=source_id,
            url=url,
            recursive=recursive,
            max_pages=max_pages,
            exclude_patterns=exclude_patterns or []
        )

        if not success:
            return json.dumps({
                "success": False,
                "error": result.get("error", "Failed to start crawl job"),
                "suggestion": "Check URL is accessible and try again"
            })

        # 5. Start crawling in background
        crawl_job_id = result["crawl_job"]["id"]

        # Background task (don't await)
        asyncio.create_task(
            _execute_crawl_job(crawl_job_id, url, recursive, max_pages, exclude_patterns)
        )

        return json.dumps({
            "success": True,
            "crawl_job": result["crawl_job"],
            "message": f"Crawl job started, use manage_crawl_job(action='get', job_id='{crawl_job_id}') to check progress"
        })

    except Exception as e:
        logger.error(f"Error in crawl_website: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check URL and parameters"
        })


async def _execute_crawl_job(
    job_id: str,
    url: str,
    recursive: bool,
    max_pages: int,
    exclude_patterns: list[str]
):
    """Background task to execute crawl job."""
    try:
        # 1. Initialize crawler
        from crawl4ai import AsyncWebCrawler

        async with AsyncWebCrawler() as crawler:
            pages_crawled = 0
            pages_to_crawl = [url]
            visited_urls = set()

            while pages_to_crawl and pages_crawled < max_pages:
                current_url = pages_to_crawl.pop(0)

                if current_url in visited_urls:
                    continue

                # Check exclude patterns
                if any(pattern in current_url for pattern in exclude_patterns):
                    continue

                # 2. Crawl page
                result = await crawler.arun(url=current_url)

                if result.success:
                    # 3. Create document from page
                    document_service = DocumentService(db_pool, vector_service)

                    await document_service.ingest_document(
                        file_path=None,  # Content provided directly
                        source_id=source_id,
                        title=result.title or current_url,
                        url=current_url,
                        content=result.markdown,  # LLM-optimized content
                        metadata={
                            "crawled_at": datetime.utcnow().isoformat(),
                            "links_found": len(result.links)
                        }
                    )

                    pages_crawled += 1
                    visited_urls.add(current_url)

                    # 4. Add links if recursive
                    if recursive:
                        for link in result.links:
                            if link not in visited_urls:
                                pages_to_crawl.append(link)

                    # 5. Update job progress
                    await crawl_service.update_crawl_job(
                        job_id=job_id,
                        pages_crawled=pages_crawled,
                        status="running"
                    )

                # Rate limiting
                await asyncio.sleep(1)

            # 6. Mark job complete
            await crawl_service.update_crawl_job(
                job_id=job_id,
                status="completed",
                pages_crawled=pages_crawled
            )

    except Exception as e:
        logger.error(f"Error executing crawl job {job_id}: {e}", exc_info=True)
        await crawl_service.update_crawl_job(
            job_id=job_id,
            status="failed",
            error_message=str(e)
        )
```

---

## Response Optimization Functions

**Critical for MCP payload management** (from Gotcha #7):

```python
# Constants
MAX_CONTENT_LENGTH = 1000
MAX_DOCUMENTS_PER_PAGE = 20
MAX_SOURCES_PER_PAGE = 20
MAX_CRAWL_PAGES = 100

def truncate_text(text: str | None, max_length: int = MAX_CONTENT_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis."""
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def optimize_result_for_mcp(result: dict) -> dict:
    """Optimize search result for MCP response.

    Truncates large fields to prevent token overflow.
    """
    result = result.copy()

    # Truncate text content
    if "text" in result:
        result["text"] = truncate_text(result["text"])

    # Truncate document title if very long
    if "document_title" in result:
        result["document_title"] = truncate_text(result["document_title"], 200)

    return result


def optimize_document_for_mcp(document: dict) -> dict:
    """Optimize document for MCP response.

    Removes or truncates large fields.
    """
    document = document.copy()

    # Remove full content (not needed in list views)
    if "content" in document:
        del document["content"]

    # Truncate title and description
    if "title" in document:
        document["title"] = truncate_text(document["title"], 200)

    if "description" in document:
        document["description"] = truncate_text(document["description"])

    return document
```

---

## Error Handling Standards

All tools follow consistent error response format:

```python
def create_error_response(error: str, suggestion: str) -> str:
    """Standard error response for MCP tools."""
    return json.dumps({
        "success": False,
        "error": error,
        "suggestion": suggestion
    })

# Common error scenarios:
ERROR_RESPONSES = {
    "missing_required_field": lambda field: create_error_response(
        f"{field} is required for this operation",
        f"Provide {field} parameter"
    ),
    "not_found": lambda resource, resource_id: create_error_response(
        f"{resource} not found: {resource_id}",
        f"Verify {resource}_id is correct or list available {resource}s"
    ),
    "invalid_action": lambda action, valid_actions: create_error_response(
        f"Unknown action: {action}",
        f"Use one of: {', '.join(valid_actions)}"
    ),
    "invalid_parameter": lambda param, valid_values: create_error_response(
        f"Invalid {param} value",
        f"Valid values: {', '.join(valid_values)}"
    )
}
```

---

## Usage Examples

### Example 1: Research Workflow

```python
# 1. Create a source for research papers
source_result = manage_source(
    action="create",
    title="AI Research Papers 2024",
    source_type="upload"
)
# Returns: {"success": true, "source": {"id": "src_abc123", ...}}

# 2. Upload multiple documents
for paper_path in research_papers:
    doc_result = manage_document(
        action="create",
        file_path=paper_path,
        source_id="src_abc123"
    )
    # Processing happens asynchronously

# 3. Search across all papers
search_result = search_knowledge_base(
    query="attention mechanisms in transformers",
    source_id="src_abc123",
    search_type="hybrid",
    match_count=10
)
# Returns relevant chunks from all papers
```

### Example 2: Documentation Crawling

```python
# 1. Crawl documentation site
crawl_result = crawl_website(
    url="https://docs.python.org/3/",
    recursive=True,
    max_pages=100,
    title="Python Official Docs",
    exclude_patterns=["/archives/", "/download/"]
)
# Returns: {"success": true, "crawl_job": {"id": "job_xyz", "status": "running"}}

# 2. Check crawl progress (would need additional tool)
# job_status = manage_crawl_job(action="get", job_id="job_xyz")

# 3. Search the crawled docs
search_result = search_knowledge_base(
    query="async context managers",
    search_type="hybrid",
    match_count=5
)
```

### Example 3: Multi-Source Search

```python
# 1. List all sources
sources = manage_source(action="list")
# Returns: {"success": true, "sources": [...], "total_count": 5}

# 2. Search across all sources (no source_id filter)
results = search_knowledge_base(
    query="database connection pooling best practices",
    search_type="rerank",
    match_count=20
)
# Returns results from all sources, ranked by relevance

# 3. Filter to specific source if needed
filtered_results = search_knowledge_base(
    query="database connection pooling best practices",
    source_id="src_abc123",
    search_type="hybrid"
)
```

---

## Testing Strategy

### Unit Tests for MCP Tools

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_search_knowledge_base_returns_json_string():
    """Verify tool returns JSON string, not dict (Gotcha #6)."""
    result = await search_knowledge_base(
        query="test query",
        match_count=5
    )

    # CRITICAL: Must be string
    assert isinstance(result, str)

    # Must be valid JSON
    parsed = json.loads(result)
    assert "success" in parsed
    assert isinstance(parsed["success"], bool)


@pytest.mark.asyncio
async def test_search_results_truncated():
    """Verify large text fields truncated (Gotcha #7)."""
    # Mock service to return large text
    with patch("search_service.search") as mock_search:
        mock_search.return_value = [{
            "text": "x" * 5000,  # Very large text
            "score": 0.95
        }]

        result = await search_knowledge_base(query="test", match_count=1)
        parsed = json.loads(result)

        # Text should be truncated
        result_text = parsed["results"][0]["text"]
        assert len(result_text) <= MAX_CONTENT_LENGTH
        assert result_text.endswith("...")


@pytest.mark.asyncio
async def test_manage_document_create_validation():
    """Verify required field validation."""
    result = await manage_document(action="create")
    parsed = json.loads(result)

    assert parsed["success"] is False
    assert "file_path" in parsed["error"]
    assert "suggestion" in parsed


@pytest.mark.asyncio
async def test_manage_document_list_pagination():
    """Verify pagination limits (Gotcha #7)."""
    result = await manage_document(
        action="list",
        per_page=1000  # Try to exceed limit
    )
    parsed = json.loads(result)

    # Should be limited to MAX_DOCUMENTS_PER_PAGE
    assert parsed["per_page"] <= MAX_DOCUMENTS_PER_PAGE


@pytest.mark.asyncio
async def test_error_response_format():
    """Verify all errors include suggestion field."""
    result = await manage_source(action="invalid_action")
    parsed = json.loads(result)

    assert parsed["success"] is False
    assert "error" in parsed
    assert "suggestion" in parsed
    assert isinstance(parsed["suggestion"], str)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_ingestion_search_workflow():
    """Test complete workflow: create source → upload doc → search."""
    # 1. Create source
    source_result = await manage_source(
        action="create",
        title="Test Source",
        source_type="upload"
    )
    source = json.loads(source_result)
    assert source["success"]
    source_id = source["source"]["id"]

    # 2. Upload document
    doc_result = await manage_document(
        action="create",
        file_path="/path/to/test.pdf",
        source_id=source_id
    )
    doc = json.loads(doc_result)
    assert doc["success"]

    # 3. Search for content
    search_result = await search_knowledge_base(
        query="test content from uploaded document",
        source_id=source_id
    )
    search = json.loads(search_result)
    assert search["success"]
    assert search["count"] > 0

    # 4. Cleanup
    delete_result = await manage_source(
        action="delete",
        source_id=source_id
    )
    assert json.loads(delete_result)["success"]
```

---

## Migration Notes from Archon

### What We Keep:
1. **JSON String Returns**: All MCP tools return JSON strings (not dicts)
2. **Payload Optimization**: Truncate large fields to prevent token overflow
3. **Consolidated Pattern**: find/manage pattern reduces tool count
4. **Error Format**: Consistent error responses with suggestions

### What We Change:
1. **Search Strategies**: Expose search_type parameter to let users choose strategy
2. **Document Management**: Consolidated manage_document replaces separate tools
3. **Source Management**: Add source concept for organizing document collections

### What We Add:
1. **Crawl Tool**: New crawl_website tool for web content ingestion
2. **Pagination Limits**: Explicit MAX_DOCUMENTS_PER_PAGE constant
3. **Metadata Support**: Rich metadata in documents and sources

---

## Success Criteria

- [x] All 4 MCP tools defined with complete signatures
- [x] Parameters and return types documented
- [x] Response format examples for success and error cases
- [x] Implementation strategies with code examples
- [x] Truncation and optimization functions (Gotcha #7)
- [x] Pagination limits specified (Gotcha #7)
- [x] JSON string return requirement documented (Gotcha #6)
- [x] Usage examples for common workflows
- [x] Testing strategy with unit and integration tests
- [x] Error handling standards with consistent format
- [x] Migration notes from Archon patterns

---

## Next Steps

This MCP tools specification provides:
1. Complete tool definitions ready for implementation
2. Response optimization to prevent token overflow
3. Consistent error handling across all tools
4. Testing strategy to validate MCP protocol compliance

**For Implementation PRP**: Use these specifications as contract for MCP server implementation. Follow task-manager patterns for service layer integration.
