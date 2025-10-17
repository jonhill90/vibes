name: "Multi-Collection Architecture: Enable Per-Source Collection Selection"
description: |

## Purpose
Migrate RAG service from single-collection architecture to multi-collection architecture where users can enable multiple embedding collections (documents, code, media) per source. This enables optimal embeddings per content type while giving users explicit control over which collections to use.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance

---

## Goal
Transform the RAG service to support multiple Qdrant collections where:
- Users select which collections to enable per source (documents, code, media)
- Each collection uses optimized embedding models for content type
- Ingestion pipeline automatically classifies chunks and routes to appropriate collections
- Search aggregates results across enabled collections
- Sources show "completed" status immediately after creation (not "pending")

## Why
- **Better Embeddings**: Code content gets code-optimized embeddings, docs get doc-optimized
- **User Control**: Explicit opt-in prevents unexpected behavior and controls costs
- **Scalability**: Per-collection HNSW indices perform better than single massive index
- **Domain Isolation**: Different content types are physically separated in vector space
- **UX Improvement**: No "pending" status confusion - sources are ready immediately

## What
Add `enabled_collections` field to sources table and implement:
1. Database migration to add `enabled_collections` array column
2. Update Pydantic models to include collection selection
3. Content type detection (code vs documents vs media)
4. Multi-collection vector storage during ingestion
5. Multi-collection search aggregation
6. Frontend UI for collection selection checkboxes
7. Fix source status to show "completed" on creation

### Success Criteria
- [ ] Sources have `enabled_collections` array field (default: ["documents"])
- [ ] Content type detector classifies chunks as "code", "documents", or "media"
- [ ] Ingestion pipeline stores chunks in appropriate collections based on enabled_collections
- [ ] Three Qdrant collections exist: AI_DOCUMENTS, AI_CODE, AI_MEDIA
- [ ] Search queries multiple collections and aggregates results
- [ ] Frontend UI allows selecting collections during source creation
- [ ] Sources show "completed" status immediately after creation (not "pending")
- [ ] All tests pass with new architecture
- [ ] Migration script works on existing database

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- file: infra/rag-service/backend/src/models/source.py
  why: Current source model structure - need to add enabled_collections field

- file: infra/rag-service/backend/src/services/ingestion_service.py
  why: Ingestion pipeline that needs to route chunks to different collections

- file: infra/rag-service/backend/src/services/vector_service.py
  why: VectorService that needs to support multiple collections

- file: infra/rag-service/backend/src/services/embeddings/embedding_service.py
  why: EmbeddingService that needs to support multiple embedding models

- file: infra/rag-service/database/scripts/init.sql
  why: Schema definition - need to understand sources table structure

- file: infra/rag-service/TODO.md
  why: Context on current status and architecture decisions (lines 14-27, 92-96)

- url: https://qdrant.tech/documentation/concepts/collections/
  why: Qdrant collection management patterns

- url: https://platform.openai.com/docs/guides/embeddings/embedding-models
  why: Different embedding models and their use cases (text-embedding-3-small vs 3-large)
```

### Current Codebase Tree
```bash
infra/rag-service/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── source.py              # SourceCreate, SourceResponse (MODIFY)
│   │   │   ├── responses.py           # Response models
│   │   │   └── requests.py            # Request models
│   │   ├── services/
│   │   │   ├── ingestion_service.py   # Main ingestion pipeline (MODIFY)
│   │   │   ├── vector_service.py      # Qdrant operations (MODIFY)
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py  # OpenAI embeddings (MODIFY)
│   │   │   ├── source_service.py      # Source CRUD (MODIFY for status fix)
│   │   │   └── search_service.py      # Search across vectors (MODIFY)
│   │   └── api/
│   │       └── routes/
│   │           ├── sources.py         # Source API endpoints (MODIFY)
│   │           └── search.py          # Search API endpoints (MODIFY)
│   └── config/
│       └── settings.py                # Configuration (ADD collection settings)
├── database/
│   ├── scripts/
│   │   └── init.sql                   # Initial schema
│   └── migrations/
│       └── 003_add_enabled_collections.sql  # NEW MIGRATION
├── frontend/
│   └── src/
│       └── components/
│           └── SourceForm.tsx         # UI for source creation (MODIFY)
└── tests/
    └── integration/
        └── test_multi_collection.py   # NEW TEST FILE
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: VectorService currently hardcoded to single collection "documents"
# CRITICAL: embedding_cache table only supports 1536 dimensions (text-embedding-3-small)
# CRITICAL: source.status="pending" confuses users - should be "completed" for upload sources
# CRITICAL: Content type detection must be lenient (40% code threshold, not strict)
# CRITICAL: Qdrant collection names are case-sensitive: "AI_DOCUMENTS" != "ai_documents"
# CRITICAL: Search must handle sources with zero enabled collections gracefully
# CRITICAL: Migration must set default enabled_collections for existing sources
# CRITICAL: PostgreSQL array syntax: ARRAY['documents']::TEXT[]
# CRITICAL: Qdrant collections must be created before first upsert
# CRITICAL: Each collection needs its own VectorParams with correct dimension
```

### Current Architecture Issues
```python
# Issue 1: Hardcoded collection name
# File: vector_service.py:35
def __init__(self, qdrant_client: AsyncQdrantClient, collection_name: str):
    self.collection_name = collection_name  # Currently always "documents"

# Issue 2: Single embedding model
# File: embedding_service.py:73
self.model_name = settings.OPENAI_EMBEDDING_MODEL  # Always text-embedding-3-small

# Issue 3: Source status confusion
# File: source.py:12
SourceStatus = Literal["pending", "processing", "completed", "failed"]
# "pending" shows immediately after creation, confusing users

# Issue 4: No content type classification
# File: ingestion_service.py:205
chunk_texts = [chunk.text for chunk in chunks]
# All chunks embedded with same model, stored in single collection
```

## Implementation Blueprint

### Data Models and Structure

```python
# models/source.py - Updated source models
from typing import Literal
from pydantic import BaseModel, Field, field_validator

# Collection types available
CollectionType = Literal["documents", "code", "media"]

# Status types (remove "pending" confusion)
SourceStatus = Literal["active", "processing", "failed", "archived"]

class SourceCreate(BaseModel):
    """Request model for creating a source."""
    source_type: Literal["upload", "crawl", "api"]
    enabled_collections: list[CollectionType] = Field(default=["documents"])
    url: str | None = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("enabled_collections")
    @classmethod
    def validate_collections(cls, v: list[CollectionType]) -> list[CollectionType]:
        """Ensure at least one collection enabled and no duplicates."""
        if not v or len(v) == 0:
            return ["documents"]  # Default to documents
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for item in v:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None, info) -> str | None:
        """Validate URL is provided for crawl and api source types."""
        if info.data.get("source_type") in ["crawl", "api"] and not v:
            raise ValueError("URL is required for crawl and api source types")
        return v

class SourceResponse(BaseModel):
    """Response model for source data."""
    id: UUID
    source_type: Literal["upload", "crawl", "api"]
    enabled_collections: list[CollectionType]  # NEW FIELD
    url: str | None
    status: SourceStatus
    metadata: dict
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

```python
# config/settings.py - Collection configuration
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...

    # Collection-specific embedding models
    COLLECTION_EMBEDDING_MODELS: dict[str, str] = {
        "documents": "text-embedding-3-small",  # Fast, cheap for general text
        "code": "text-embedding-3-large",       # Better for technical content
        "media": "clip-vit-base-patch32",       # Multimodal (future)
    }

    # Collection-specific dimensions
    COLLECTION_DIMENSIONS: dict[str, int] = {
        "documents": 1536,   # text-embedding-3-small
        "code": 3072,        # text-embedding-3-large
        "media": 512,        # clip-vit (future)
    }

    # Collection name prefix
    COLLECTION_NAME_PREFIX: str = "AI_"

    # Content type detection thresholds
    CODE_DETECTION_THRESHOLD: float = 0.4  # 40% code blocks = code collection

settings = Settings()
```

### List of Tasks to be Completed

```yaml
Task 1: Database Migration - Add enabled_collections Column
CREATE database/migrations/003_add_enabled_collections.sql:
  - PATTERN: Follow migration pattern from 001_add_text_preview.sql
  - Add enabled_collections TEXT[] column with CHECK constraint
  - Set default value ARRAY['documents']::TEXT[]
  - Update existing rows to have default collection
  - Add GIN index for array queries

Task 2: Update Source Models
MODIFY backend/src/models/source.py:
  - PATTERN: Follow existing Pydantic model patterns
  - Add CollectionType literal
  - Update SourceCreate with enabled_collections field and validator
  - Update SourceResponse to include enabled_collections
  - Change SourceStatus to remove "pending" (use "active" instead)

Task 3: Fix Source Status Confusion
MODIFY backend/src/services/source_service.py:
  - PATTERN: Set appropriate default status based on source_type
  - upload sources: Default status="active" (ready immediately)
  - crawl/api sources: Default status="active" (will process when job runs)
  - Remove "pending" status from status flow

Task 4: Implement Content Type Detector
CREATE backend/src/services/content_classifier.py:
  - PATTERN: Pure function, no external dependencies
  - detect_content_type(text: str) -> CollectionType
  - Code detection: Check for code indicators (```, def, import, {})
  - Media detection: Check for image syntax (![, <img, data:image/)
  - Default to "documents" for general text
  - Use CODE_DETECTION_THRESHOLD from settings

Task 5: Update VectorService for Multi-Collection Support
MODIFY backend/src/services/vector_service.py:
  - PATTERN: Factory pattern to create collection-specific instances
  - Remove hardcoded collection_name from __init__
  - Add get_collection_name(collection_type: str) -> str helper
  - Update validate_embedding() to accept dimension parameter
  - Add ensure_collection_exists() for each collection type
  - Update upsert_vectors() to accept collection_name parameter

Task 6: Update EmbeddingService for Multiple Models
MODIFY backend/src/services/embeddings/embedding_service.py:
  - PATTERN: Model selection based on collection type
  - Add embed_with_model(text: str, model_name: str) method
  - Update embedding_cache to store model_name in lookup
  - Update batch_embed() to accept model_name parameter
  - Ensure cache lookup includes model_name in hash

Task 7: Update Ingestion Pipeline for Multi-Collection
MODIFY backend/src/services/ingestion_service.py:
  - PATTERN: Classify → Group → Embed per model → Store per collection
  - Import ContentClassifier
  - In ingest_document(): Get source.enabled_collections from DB
  - Classify each chunk using ContentClassifier.detect_content_type()
  - Filter chunks where content_type not in enabled_collections
  - Group chunks by content_type
  - For each group: embed with appropriate model, store in collection
  - Update _store_document_atomic() to handle multiple collections

Task 8: Implement Multi-Collection Search
MODIFY backend/src/services/search_service.py:
  - PATTERN: Query multiple collections, aggregate, re-rank by score
  - Get enabled_collections for each source_id in filter
  - Determine which collections to query (union of all enabled)
  - Embed query once (use "documents" model for general queries)
  - Search each collection with appropriate filters
  - Merge results and sort by score descending
  - Return top N results

Task 9: Update Source API Endpoints
MODIFY backend/src/api/routes/sources.py:
  - PATTERN: Follow existing route patterns
  - Update POST /sources to accept enabled_collections
  - Update GET /sources/{id} to return enabled_collections
  - Validate enabled_collections in request body

Task 10: Create Qdrant Collection Initialization
CREATE backend/src/services/qdrant_init.py:
  - PATTERN: Startup script to ensure collections exist
  - Check if AI_DOCUMENTS, AI_CODE, AI_MEDIA exist
  - Create collections with appropriate VectorParams
  - Use COLLECTION_DIMENSIONS from settings
  - Call during app startup in main.py

Task 11: Update Frontend Source Creation Form
MODIFY frontend/src/components/SourceForm.tsx:
  - PATTERN: Checkbox group for collection selection
  - Add enabled_collections state with default ["documents"]
  - Render checkboxes for each collection type with descriptions
  - Documents: "General text, articles, documentation"
  - Code: "Source code, snippets, technical examples"
  - Media: "Images, diagrams, visual content (future)"
  - Validate at least one collection selected
  - Send enabled_collections in POST /api/sources request

Task 12: Add Integration Tests
CREATE tests/integration/test_multi_collection.py:
  - PATTERN: Test end-to-end multi-collection flow
  - Test 1: Create source with multiple collections
  - Test 2: Ingest document with mixed content (code + docs)
  - Test 3: Verify chunks stored in correct collections
  - Test 4: Search returns results from multiple collections
  - Test 5: Migration script works on existing data
  - Test 6: Content classifier accuracy on sample texts

Task 13: Update Documentation
MODIFY infra/rag-service/TODO.md:
  - PATTERN: Document architecture decision
  - Update "Architecture Decision" section (lines 14-27)
  - Document multi-collection approach chosen
  - Add gotchas section for content classification
  - Update system health with collection info
```

### Per Task Pseudocode

```sql
-- Task 1: Database Migration
-- File: database/migrations/003_add_enabled_collections.sql

-- Add enabled_collections column with validation
ALTER TABLE sources
ADD COLUMN enabled_collections TEXT[] DEFAULT ARRAY['documents']::TEXT[]
CHECK (
    enabled_collections <@ ARRAY['documents', 'code', 'media']::TEXT[]
    AND array_length(enabled_collections, 1) > 0
);

-- Create GIN index for efficient array queries
CREATE INDEX idx_sources_enabled_collections
ON sources USING GIN(enabled_collections);

-- Update existing sources to have default collection
UPDATE sources
SET enabled_collections = ARRAY['documents']::TEXT[]
WHERE enabled_collections IS NULL;

-- Change status column to remove "pending" (add "active")
-- Note: existing "pending" → "active", "completed" → "active"
ALTER TABLE sources DROP CONSTRAINT sources_status_check;
ALTER TABLE sources ADD CONSTRAINT sources_status_check
CHECK (status IN ('active', 'processing', 'failed', 'archived'));

UPDATE sources SET status = 'active'
WHERE status IN ('pending', 'completed');
```

```python
-- Task 4: Content Type Classifier
-- File: backend/src/services/content_classifier.py

from typing import Literal
from ..config.settings import settings

CollectionType = Literal["documents", "code", "media"]

class ContentClassifier:
    """Classify text chunks into content types for collection routing."""

    @staticmethod
    def detect_content_type(text: str) -> CollectionType:
        """Detect if chunk is code, document, or media based on content.

        Algorithm:
        1. Check for media indicators (images) → "media"
        2. Count code indicators vs total lines → "code" if >threshold
        3. Default to "documents" for general text

        Args:
            text: Text content to classify

        Returns:
            CollectionType: "code", "media", or "documents"
        """
        # Check for media (highest priority - most specific)
        media_indicators = [
            "![" in text,           # Markdown image
            "<img" in text,         # HTML image
            "data:image/" in text,  # Base64 image
            "<svg" in text,         # SVG graphics
        ]

        if any(media_indicators):
            return "media"

        # Check for code patterns
        code_indicators = [
            text.strip().startswith("```"),         # Code fence
            text.strip().startswith("    "),       # Indented code block
            bool(re.search(r'\bdef\s+\w+\s*\(', text)),   # Python function
            bool(re.search(r'\bfunction\s+\w+\s*\(', text)),  # JS function
            bool(re.search(r'\bclass\s+\w+', text)),      # Class definition
            "import " in text or "from " in text,  # Python imports
            "{" in text and "}" in text and ";" in text,  # C-style syntax
            bool(re.search(r'\bconst\s+\w+\s*=', text)),  # Modern JS
            bool(re.search(r'\blet\s+\w+\s*=', text)),    # Modern JS
        ]

        # Calculate code density
        code_indicator_count = sum(code_indicators)
        total_lines = max(text.count("\n"), 1)

        # If multiple code indicators present, classify as code
        threshold = settings.CODE_DETECTION_THRESHOLD
        if code_indicator_count >= 3:  # Absolute minimum
            return "code"

        # Check code block percentage for markdown
        code_fence_count = text.count("```") // 2  # Pairs of fences
        if code_fence_count / total_lines > threshold:
            return "code"

        # Default to documents
        return "documents"
```

```python
-- Task 7: Multi-Collection Ingestion Pipeline
-- File: backend/src/services/ingestion_service.py (modify existing)

async def ingest_document(
    self,
    source_id: UUID,
    file_path: str,
    document_metadata: dict[str, Any] | None = None,
) -> tuple[bool, dict[str, Any]]:
    """Ingest document with multi-collection support."""

    # Step 1: Get source configuration
    async with self.db_pool.acquire() as conn:
        source_row = await conn.fetchrow(
            "SELECT enabled_collections FROM sources WHERE id = $1",
            source_id
        )
        enabled_collections = source_row["enabled_collections"]

    logger.info(f"Source {source_id} enabled collections: {enabled_collections}")

    # Step 2-3: Parse and chunk (existing code)
    markdown_text = await self.document_parser.parse_document(file_path)
    chunks: list[Chunk] = await self.text_chunker.chunk_text(markdown_text)

    # Step 4: Classify chunks by content type
    from .content_classifier import ContentClassifier
    classifier = ContentClassifier()

    classified_chunks: dict[str, list[tuple[Chunk, int]]] = {
        "documents": [],
        "code": [],
        "media": [],
    }

    for i, chunk in enumerate(chunks):
        content_type = classifier.detect_content_type(chunk.text)

        # Only process if collection is enabled
        if content_type in enabled_collections:
            classified_chunks[content_type].append((chunk, i))
        else:
            logger.debug(
                f"Skipping chunk {i} (type={content_type}, not in enabled_collections)"
            )

    # Step 5: Embed and store per collection
    total_chunks_stored = 0
    total_chunks_failed = 0
    document_ids = []

    for collection_type, chunk_tuples in classified_chunks.items():
        if not chunk_tuples:
            continue  # Skip empty collections

        chunks_only = [chunk for chunk, _ in chunk_tuples]
        chunk_texts = [chunk.text for chunk in chunks_only]

        # Get appropriate embedding model for this collection
        model_name = settings.COLLECTION_EMBEDDING_MODELS[collection_type]

        # Embed with collection-specific model
        logger.info(
            f"Embedding {len(chunk_texts)} chunks for {collection_type} "
            f"collection using {model_name}"
        )
        embed_result = await self.embedding_service.batch_embed(
            chunk_texts,
            model_name=model_name
        )

        if embed_result.success_count == 0:
            logger.error(f"All embeddings failed for {collection_type} collection")
            total_chunks_failed += embed_result.failure_count
            continue

        # Store in collection-specific Qdrant collection
        collection_name = f"{settings.COLLECTION_NAME_PREFIX}{collection_type.upper()}"

        document_id, chunks_stored = await self._store_document_atomic(
            source_id=source_id,
            title=document_title,
            document_type=document_type,
            url=url,
            metadata={**document_metadata, "collection_type": collection_type},
            chunks=chunks_only,
            embeddings=embed_result.embeddings,
            collection_name=collection_name,  # NEW PARAMETER
        )

        total_chunks_stored += chunks_stored
        total_chunks_failed += embed_result.failure_count
        document_ids.append(str(document_id))

    return True, {
        "document_ids": document_ids,
        "chunks_stored": total_chunks_stored,
        "chunks_failed": total_chunks_failed,
        "collections_used": list(classified_chunks.keys()),
        "message": f"Document ingested across {len(document_ids)} collections"
    }
```

```python
-- Task 8: Multi-Collection Search
-- File: backend/src/services/search_service.py (modify existing)

async def search(
    self,
    query: str,
    source_ids: list[UUID] | None = None,
    limit: int = 10,
    score_threshold: float = 0.05,
) -> list[SearchResult]:
    """Search across multiple collections based on source configurations."""

    # Step 1: Determine which collections to search
    if source_ids:
        # Get enabled collections for specified sources
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT unnest(enabled_collections) as collection_type
                FROM sources
                WHERE id = ANY($1)
                """,
                source_ids
            )
        collections_to_search = [row["collection_type"] for row in rows]
    else:
        # Search all collections
        collections_to_search = ["documents", "code", "media"]

    if not collections_to_search:
        logger.warning("No collections to search (sources have zero enabled collections)")
        return []

    # Step 2: Embed query (use "documents" model for general queries)
    query_embedding = await self.embedding_service.embed_text(
        query,
        model_name=settings.COLLECTION_EMBEDDING_MODELS["documents"]
    )

    if not query_embedding:
        return []

    # Step 3: Search each collection
    all_results = []

    for collection_type in collections_to_search:
        collection_name = f"{settings.COLLECTION_NAME_PREFIX}{collection_type.upper()}"

        # Build source_id filter if specified
        filter_conditions = None
        if source_ids:
            # Only search sources that have this collection enabled
            async with self.db_pool.acquire() as conn:
                filtered_sources = await conn.fetch(
                    """
                    SELECT id FROM sources
                    WHERE id = ANY($1)
                    AND $2 = ANY(enabled_collections)
                    """,
                    source_ids,
                    collection_type
                )

            source_ids_for_collection = [str(row["id"]) for row in filtered_sources]

            if not source_ids_for_collection:
                continue  # Skip this collection

            filter_conditions = {
                "must": [
                    {
                        "key": "source_id",
                        "match": {"any": source_ids_for_collection}
                    }
                ]
            }

        # Search this collection
        try:
            vector_service = VectorService(
                self.qdrant_client,
                collection_name
            )

            results = await vector_service.search_vectors(
                query_vector=query_embedding,
                limit=limit * 2,  # Get more results to re-rank later
                score_threshold=score_threshold,
                filter_conditions=filter_conditions,
            )

            # Add collection metadata to results
            for result in results:
                result["collection_type"] = collection_type

            all_results.extend(results)

        except Exception as e:
            logger.error(f"Error searching {collection_name}: {e}")
            continue  # Skip failed collections

    # Step 4: Merge and re-rank by score
    sorted_results = sorted(
        all_results,
        key=lambda r: r["score"],
        reverse=True
    )[:limit]

    logger.info(
        f"Multi-collection search: {len(all_results)} total results "
        f"from {len(collections_to_search)} collections, "
        f"returning top {len(sorted_results)}"
    )

    return sorted_results
```

```typescript
// Task 11: Frontend Collection Selection
// File: frontend/src/components/SourceForm.tsx (modify existing)

interface SourceFormData {
  source_type: "upload" | "crawl" | "api";
  enabled_collections: ("documents" | "code" | "media")[];
  url?: string;
  metadata: Record<string, any>;
}

const SourceForm: React.FC = () => {
  const [formData, setFormData] = useState<SourceFormData>({
    source_type: "upload",
    enabled_collections: ["documents"], // Default
    url: "",
    metadata: {},
  });

  const collectionOptions = [
    {
      value: "documents",
      label: "Documents",
      description: "General text, articles, documentation, blog posts",
      icon: "📄",
    },
    {
      value: "code",
      label: "Code",
      description: "Source code, snippets, technical examples, API docs",
      icon: "💻",
    },
    {
      value: "media",
      label: "Media",
      description: "Images, diagrams, visual content (coming soon)",
      icon: "🖼️",
      disabled: true, // Future feature
    },
  ];

  const handleCollectionToggle = (collectionType: string) => {
    setFormData((prev) => {
      const current = prev.enabled_collections;

      if (current.includes(collectionType)) {
        // Remove if already selected (but ensure at least one remains)
        if (current.length === 1) {
          return prev; // Don't allow removing last collection
        }
        return {
          ...prev,
          enabled_collections: current.filter((c) => c !== collectionType),
        };
      } else {
        // Add if not selected
        return {
          ...prev,
          enabled_collections: [...current, collectionType],
        };
      }
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Existing source_type and url fields... */}

      <div className="form-section">
        <label className="form-label">
          Enable Collections
          <span className="help-text">
            Select which embedding types to use for this source
          </span>
        </label>

        <div className="collection-checkboxes">
          {collectionOptions.map((option) => (
            <label
              key={option.value}
              className={`collection-option ${
                option.disabled ? "disabled" : ""
              } ${
                formData.enabled_collections.includes(option.value)
                  ? "selected"
                  : ""
              }`}
            >
              <input
                type="checkbox"
                checked={formData.enabled_collections.includes(option.value)}
                onChange={() => handleCollectionToggle(option.value)}
                disabled={option.disabled}
              />
              <div className="collection-info">
                <div className="collection-header">
                  <span className="collection-icon">{option.icon}</span>
                  <span className="collection-label">{option.label}</span>
                </div>
                <div className="collection-description">
                  {option.description}
                </div>
              </div>
            </label>
          ))}
        </div>

        {formData.enabled_collections.length === 0 && (
          <div className="error-message">
            At least one collection must be enabled
          </div>
        )}
      </div>

      {/* Submit button... */}
    </form>
  );
};
```

### Integration Points
```yaml
ENVIRONMENT:
  - add to: backend/.env
  - vars: |
      # Existing OpenAI settings...

      # Multi-collection settings (optional - has defaults)
      COLLECTION_NAME_PREFIX=AI_
      CODE_DETECTION_THRESHOLD=0.4

DATABASE:
  - Migration 003 must run before code deployment
  - Existing "pending"/"completed" sources → "active"
  - All existing sources get enabled_collections=["documents"]

QDRANT:
  - Three collections created on startup:
    - AI_DOCUMENTS (1536 dimensions, text-embedding-3-small)
    - AI_CODE (3072 dimensions, text-embedding-3-large)
    - AI_MEDIA (512 dimensions, clip-vit - future)
  - Existing vectors in "documents" collection remain (backward compatible)

FRONTEND:
  - API contract changes:
    - POST /api/sources: Add enabled_collections field (array)
    - GET /api/sources: Returns enabled_collections field
    - GET /api/sources/{id}: Returns enabled_collections field
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd infra/rag-service/backend

# Type checking
mypy src/ --strict

# Linting
ruff check src/ --fix

# Expected: No errors. If errors, READ and fix.
```

### Level 2: Unit Tests
```python
# tests/unit/test_content_classifier.py
def test_detect_code_content():
    """Test code detection with various code samples."""
    classifier = ContentClassifier()

    # Python code
    assert classifier.detect_content_type("def foo():\n    pass") == "code"

    # JavaScript code
    assert classifier.detect_content_type("function bar() { return 42; }") == "code"

    # Markdown with code fence
    code_md = "```python\ndef test():\n    pass\n```"
    assert classifier.detect_content_type(code_md) == "code"

    # Regular text
    assert classifier.detect_content_type("This is a blog post about cats.") == "documents"

def test_detect_media_content():
    """Test media detection with image syntax."""
    classifier = ContentClassifier()

    # Markdown image
    assert classifier.detect_content_type("![alt text](image.png)") == "media"

    # HTML image
    assert classifier.detect_content_type('<img src="test.jpg">') == "media"

    # Base64 image
    assert classifier.detect_content_type("data:image/png;base64,abc123") == "media"

def test_mixed_content_threshold():
    """Test code threshold with mixed content."""
    classifier = ContentClassifier()

    # 30% code (below threshold) → documents
    text = "Some text\n" * 7 + "```python\ncode\n```\n" * 3
    assert classifier.detect_content_type(text) == "documents"

    # 50% code (above threshold) → code
    text = "Some text\n" * 5 + "```python\ncode\n```\n" * 5
    assert classifier.detect_content_type(text) == "code"
```

```python
# tests/unit/test_source_model.py
def test_enabled_collections_validator():
    """Test enabled_collections validation."""
    # Valid: single collection
    source = SourceCreate(
        source_type="upload",
        enabled_collections=["documents"]
    )
    assert source.enabled_collections == ["documents"]

    # Valid: multiple collections
    source = SourceCreate(
        source_type="crawl",
        url="https://example.com",
        enabled_collections=["documents", "code"]
    )
    assert len(source.enabled_collections) == 2

    # Valid: empty list defaults to ["documents"]
    source = SourceCreate(
        source_type="upload",
        enabled_collections=[]
    )
    assert source.enabled_collections == ["documents"]

    # Valid: removes duplicates
    source = SourceCreate(
        source_type="upload",
        enabled_collections=["documents", "code", "documents"]
    )
    assert source.enabled_collections == ["documents", "code"]
```

```bash
# Run unit tests
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Expected: 90%+ coverage for new code
```

### Level 3: Integration Tests
```python
# tests/integration/test_multi_collection.py
import pytest

@pytest.mark.asyncio
async def test_multi_collection_ingestion(db_pool, qdrant_client):
    """Test document ingestion with multiple enabled collections."""
    # Create source with multiple collections
    source_id = await create_source(
        source_type="upload",
        enabled_collections=["documents", "code"]
    )

    # Create test file with mixed content
    test_content = """
    # Introduction
    This is a documentation article about Python.

    ## Code Example
    ```python
    def hello_world():
        print("Hello, World!")
    ```

    ## Conclusion
    That's how you write Python code.
    """

    # Ingest document
    success, result = await ingestion_service.ingest_document(
        source_id=source_id,
        file_path="test.md",
        document_metadata={"title": "Test Doc"}
    )

    assert success
    assert "collections_used" in result
    assert set(result["collections_used"]) == {"documents", "code"}

    # Verify chunks in correct collections
    docs_count = await count_vectors_in_collection("AI_DOCUMENTS", source_id)
    code_count = await count_vectors_in_collection("AI_CODE", source_id)

    assert docs_count > 0  # Text chunks
    assert code_count > 0  # Code chunks

@pytest.mark.asyncio
async def test_multi_collection_search(db_pool, qdrant_client):
    """Test search across multiple collections."""
    # Create source with both collections
    source_id = await create_source(
        enabled_collections=["documents", "code"]
    )

    # Ingest test data
    await ingest_test_documents(source_id)

    # Search across all collections
    results = await search_service.search(
        query="Python function example",
        source_ids=[source_id],
        limit=10
    )

    # Should return results from both collections
    collection_types = {r["collection_type"] for r in results}
    assert "documents" in collection_types or "code" in collection_types

    # Results should be sorted by score
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)

@pytest.mark.asyncio
async def test_collection_filtering_during_ingestion(db_pool):
    """Test that chunks are filtered based on enabled_collections."""
    # Create source with only "documents" enabled
    source_id = await create_source(
        enabled_collections=["documents"]
    )

    # Ingest file with code content
    test_code = """
    ```python
    def test():
        pass
    ```
    """

    success, result = await ingestion_service.ingest_document(
        source_id=source_id,
        file_path="test_code.md"
    )

    assert success

    # Code chunks should be skipped (not in enabled_collections)
    code_count = await count_vectors_in_collection("AI_CODE", source_id)
    assert code_count == 0

    # Only document chunks stored
    docs_count = await count_vectors_in_collection("AI_DOCUMENTS", source_id)
    assert docs_count > 0

@pytest.mark.asyncio
async def test_migration_script(db_pool):
    """Test that migration 003 works correctly."""
    # Migration should add enabled_collections column
    async with db_pool.acquire() as conn:
        # Check column exists
        result = await conn.fetchrow("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'sources'
            AND column_name = 'enabled_collections'
        """)

        assert result is not None
        assert result["data_type"] == "ARRAY"

        # Check existing sources have default value
        sources = await conn.fetch("SELECT enabled_collections FROM sources")
        for source in sources:
            assert source["enabled_collections"] is not None
            assert len(source["enabled_collections"]) > 0
```

```bash
# Run integration tests
cd infra/rag-service
docker-compose up -d
docker exec rag-backend python -m pytest tests/integration/test_multi_collection.py -v

# Expected: All tests pass
```

### Level 4: End-to-End UI Test
```bash
# Manual UI validation
# 1. Open frontend: http://localhost:5173
# 2. Click "Create Source"
# 3. Verify:
#    - Three collection checkboxes visible
#    - "Documents" checked by default
#    - Can select multiple collections
#    - Cannot uncheck last collection (at least one required)
# 4. Create source with "Documents" + "Code" enabled
# 5. Upload a file with mixed content (text + code)
# 6. Verify:
#    - Source shows "active" status (not "pending")
#    - Search returns results from both collections
# 7. Check Qdrant collections:
#    curl http://localhost:6333/collections
#    - Should see AI_DOCUMENTS, AI_CODE, AI_MEDIA
```

## Final Validation Checklist
- [ ] Migration 003 runs successfully on existing database
- [ ] All unit tests pass: `pytest tests/unit/ -v`
- [ ] All integration tests pass: `pytest tests/integration/test_multi_collection.py -v`
- [ ] No type errors: `mypy src/ --strict`
- [ ] No lint errors: `ruff check src/`
- [ ] Frontend displays collection checkboxes correctly
- [ ] Sources show "active" status on creation (not "pending")
- [ ] Content classifier correctly identifies code vs documents
- [ ] Ingestion stores chunks in appropriate collections
- [ ] Search aggregates results from multiple collections
- [ ] Qdrant has three collections: AI_DOCUMENTS, AI_CODE, AI_MEDIA
- [ ] Existing data migrated correctly (enabled_collections set)
- [ ] API endpoints accept and return enabled_collections field
- [ ] Documentation updated in TODO.md

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode collection names - use COLLECTION_NAME_PREFIX from settings
- ❌ Don't skip content type validation - could store in wrong collection
- ❌ Don't forget to check enabled_collections before storing chunks
- ❌ Don't use same embedding model for all collections - defeats the purpose
- ❌ Don't allow zero enabled_collections - must have at least one
- ❌ Don't forget to create Qdrant collections before first upsert
- ❌ Don't ignore migration rollback plan - have a way to revert
- ❌ Don't assume all sources have enabled_collections - handle null gracefully during migration
- ❌ Don't forget to re-rank multi-collection search results by score
- ❌ Don't use "pending" status anymore - switch to "active" for clarity

## Confidence Score: 8/10

High confidence due to:
- Clear existing codebase patterns to follow
- Well-documented Qdrant collection management
- Existing ingestion pipeline to extend
- Comprehensive test coverage planned

Minor uncertainty on:
- Content classifier accuracy (40% threshold may need tuning)
- Migration impact on large existing datasets (test thoroughly)
- Frontend UX for collection selection (may need user feedback)

---

## Rollback Plan

If migration fails or causes issues:

```sql
-- Rollback migration 003
ALTER TABLE sources DROP CONSTRAINT sources_status_check;
ALTER TABLE sources ADD CONSTRAINT sources_status_check
CHECK (status IN ('pending', 'processing', 'completed', 'failed'));

UPDATE sources SET status = 'pending' WHERE status = 'active';

DROP INDEX IF EXISTS idx_sources_enabled_collections;
ALTER TABLE sources DROP COLUMN IF EXISTS enabled_collections;
```

Then revert code changes and redeploy previous version.
