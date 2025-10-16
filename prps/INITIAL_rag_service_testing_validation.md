# RAG Service Testing & Validation

## Overview
Complete testing and validation of recently implemented RAG service features, with comprehensive Playwright browser testing for end-to-end user workflows.

## Context
Recent work completed:
- Document upload ingestion pipeline (backend/src/api/routes/documents.py:174-283)
- Search source filtering (SearchInterface.tsx, search.py)
- Frontend delete functionality (CrawlManagement.tsx, client.ts)

These features need proper validation with:
1. Backend unit/integration tests
2. Frontend browser tests using Playwright
3. End-to-end workflow validation

## Requirements

### 1. Document Upload Testing
**Backend Tests:**
- Upload succeeds and returns document metadata
- File is saved temporarily and cleaned up
- Document is parsed correctly (test with PDF, TXT, MD)
- Chunks are created and counted
- Embeddings are generated
- Data is stored in PostgreSQL + Qdrant
- Error handling for invalid files

**Frontend Browser Tests (Playwright):**
- Navigate to document upload page
- Fill upload form with test document
- Submit upload
- Wait for success message
- Verify document appears in list
- Verify chunk count displayed
- Take screenshot for proof

### 2. Search Source Filtering Testing
**Backend Tests:**
- Search without filter returns all results
- Search with source_id filters correctly
- Invalid source_id handled gracefully
- Empty results handled correctly

**Frontend Browser Tests (Playwright):**
- Navigate to search page
- Enter search query
- Select source from dropdown
- Submit search
- Verify filtered results
- Change source filter
- Verify results update
- Take screenshots for proof

### 3. Delete Functionality Testing
**Backend Tests:**
- Delete crawl job removes job from database
- Delete document removes document + chunks
- Delete source cascades to documents/chunks
- Non-existent IDs return 404

**Frontend Browser Tests (Playwright):**
- Navigate to crawl management page
- Click delete button on crawl job
- Confirm deletion in modal
- Verify job removed from list
- Repeat for documents (once page exists)
- Take screenshots for proof

### 4. Documents Management Page
**Requirements:**
- Create "Manage Documents" page component
- List all documents with metadata
- Delete button per document
- Confirmation modal
- Success/error feedback

**Frontend Browser Tests (Playwright):**
- Navigate to documents page
- Verify list displays
- Click delete button
- Confirm deletion
- Verify document removed
- Take screenshot for proof

### 5. End-to-End Workflow Validation
**Complete User Journey (Playwright):**
1. Create source
2. Start crawl job
3. Wait for completion
4. Upload document to source
5. Verify chunks created
6. Search for content
7. Apply source filter
8. Verify filtered results
9. Delete document
10. Delete crawl job
11. Delete source

## Testing Strategy

### Quality Gates (From .claude/patterns/quality-gates.md)
**Level 1: Syntax & Style (~5s)**
```bash
cd infra/rag-service/backend
ruff check src/ tests/
mypy src/
```

**Level 2: Unit Tests (~30s)**
```bash
pytest tests/unit/ -v
```

**Level 3a: API Integration (~60s)**
```bash
pytest tests/integration/ -v
```

**Level 3b: Browser Integration (~120s)**
```bash
pytest tests/browser/ -v
# Uses Playwright via MCP browser tools
```

### Browser Testing Guidelines
- Use `browser_snapshot()` for validation (structured data)
- Use `browser_take_screenshot()` only for human proof
- Use semantic queries for element selection
- Use `browser_wait_for()` for async operations
- Ensure services running before tests
- Install browser binaries if needed

## Validation Gates

### Backend Validation
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Code coverage >80%

### Frontend Validation (Playwright)
- [ ] Browser binaries installed
- [ ] Services running (docker-compose up)
- [ ] All browser tests pass
- [ ] Screenshots captured for proof
- [ ] No console errors in browser

### End-to-End Validation
- [ ] Complete workflow test passes
- [ ] Data persists correctly
- [ ] UI reflects backend state
- [ ] Error states handled gracefully

## Known Issues to Address

### 1. Crawl4AI Content Truncation
- Currently getting ~50 chunks from 2.7MB docs (expected 300-400)
- Root cause: Crawl4AI library returns truncated markdown
- Investigation needed on Crawl4AI configuration
- Test case: https://ai.pydantic.dev/llms-full.txt

### 2. Documents Management Page Missing
- Need to create page component
- Similar structure to SourceManagement/CrawlManagement
- Include list, delete, metadata display

## Success Criteria
- All backend tests pass (unit + integration)
- All frontend browser tests pass (Playwright)
- End-to-end workflow validated with browser automation
- Documentation updated with test results
- Screenshots captured proving functionality
- No regression in existing features

## Resources
- Browser testing: `.claude/patterns/browser-validation.md`
- Quality gates: `.claude/patterns/quality-gates.md`
- Validation agents: `.claude/agents/validation-gates.md`
- Test examples: `prps/playwright_agent_integration/examples/`
