# Language Field Workflow - Correct Implementation

## Summary

The `language` field in code chunks identifies the programming language (python, bash, json, typescript, etc.) for syntax highlighting and filtering.

**CRITICAL**: Use the **two-phase workflow** below. Do NOT try to extract language during crawl.

## Two-Phase Workflow

### Phase 1: Crawl Documents
```bash
# Start crawl via API or UI
POST /api/crawls
{
  "source_id": "<uuid>",
  "url": "https://example.com/docs",
  "max_pages": 100,
  "max_depth": 3
}
```

**What happens:**
- Crawls pages and creates chunks
- Stores in PostgreSQL `chunks` table
- Embeds and stores in `MCP_documents` collection (1536d)
- Documentation with embedded code examples → stored as "documents"

### Phase 2: Extract Code Blocks
```bash
# Run script AFTER crawl completes
docker exec -w /app rag-backend python3 src/scripts/extract_code_blocks.py \
  --source-id <uuid>
```

**What happens:**
- Reads all chunks from PostgreSQL
- Finds code fences: ` ```language\n...code...\n``` `
- Extracts pure code blocks with language tags
- Creates NEW points in `MCP_code` collection (3072d)
- Adds `language` field to Qdrant payload

## Results

From 387 documentation chunks:
- **244 code blocks extracted** (88.7% coverage)
- **Total MCP_code points**: 275 (244 with language field)
- **Languages**: json (106), bash (39), typescript (18), mermaid (18), powershell (14), python (12), kotlin (10), csharp (6), groovy (5), http (4), xml (3), java (3), env (2), javascript (1), yml (1), properties (1), yaml (1)

## Why This Approach?

**Problem with inline extraction during crawl:**
1. Chunks may not start with code fences (docs first, code embedded later)
2. Code fences may have no language tag (` ``` ` vs ` ```python`)
3. Mixed content (documentation + code) gets misclassified

**Script-based extraction solves this:**
- Reads FULL chunk text (not just start)
- Extracts ONLY pure code blocks
- Skips documentation prose
- Properly tags with language when available

## Data Integrity (Orphan Prevention)

**Critical**: Document deletion automatically cleans up code vectors.

**Implementation**: `document_service.py:380-453`
```python
# When deleting a document, also delete its code vectors
deleted_count = await vector_service.delete_vectors_by_filter(
    collection_name=code_collection,
    filter_conditions={
        "must": [{"key": "document_id", "match": {"value": str(document_id)}}]
    }
)
```

**Tested**: Deleting documents properly removes orphaned code points from Qdrant.

## Verification

Check language field coverage:
```bash
curl -s http://localhost:6333/collections/MCP_code/points/scroll \
  -H 'Content-Type: application/json' \
  -d '{"limit": 100, "with_payload": true, "with_vector": false}' | \
python3 -c "
import json, sys
data = json.load(sys.stdin)
points = data['result']['points']
with_lang = sum(1 for p in points if 'language' in p['payload'])
print(f'Coverage: {with_lang}/{len(points)} ({100*with_lang/len(points):.1f}%)')
"
```

## Future Work

- **UI**: Add language badges to search results
- **Filtering**: Enable search by programming language
- **Syntax Highlighting**: Use language field for code display

## References

- Script: `backend/src/scripts/extract_code_blocks.py`
- Orphan cleanup: `backend/src/services/document_service.py:380-453`
- Content classifier: `backend/src/services/content_classifier.py`
- TODO: Task 6 (lines 61-77)
