# Feature Analysis: RAG Service Testing & Validation

## INITIAL.md Summary
The goal is to implement comprehensive testing and validation for recently completed RAG service features (document upload, search source filtering, delete functionality) using a multi-level testing strategy that includes backend unit/integration tests and frontend browser testing with Playwright. The feature also requires creating a missing "Documents Management" page component with browser validation.

## Core Requirements

### Explicit Requirements
- **Backend Testing**: Unit and integration tests for document upload, search filtering, and delete operations
- **Frontend Browser Testing**: Playwright-based browser automation for UI validation (using MCP browser tools)
- **End-to-End Workflow Validation**: Complete user journey testing from source creation to deletion
- **Quality Gates Implementation**: 4-level validation (Syntax → Unit → API Integration → Browser Integration)
- **Documents Management Page**: New React component for document CRUD operations with browser tests
- **Known Issues Investigation**: Crawl4AI content truncation problem (50 chunks instead of expected 300-400)
- **Test Coverage**: >80% code coverage requirement

### Implicit Requirements
- **Test Infrastructure Setup**: pytest configuration, fixtures, test data factories
- **CI/CD Integration**: Tests must be automated and run on every PR
- **Performance Benchmarks**: Each test level has target execution time (5s, 30s, 60s, 120s)
- **Error Handling Tests**: Validation for edge cases, invalid inputs, network failures
- **Data Cleanup**: Test isolation with proper teardown/rollback
- **Documentation**: Test results, screenshots, validation reports
- **Regression Prevention**: Tests prevent breaking existing features

## Technical Components

### Data Models
**Test Fixtures Needed**:
- `sample_document`: Full document record with metadata, chunks, embeddings
- `sample_source`: Source with various types (upload, crawl, manual)
- `sample_crawl_job`: Crawl job with different statuses (pending, running, completed, failed)
- `sample_chunks`: Text chunks with embeddings for search testing
- `mock_uploaded_file`: File upload test data (PDF, TXT, MD formats)
- `test_database`: Isolated test database with transaction rollback

**Database Schema Coverage**:
- `sources` table CRUD operations
- `documents` table with cascade deletes
- `chunks` table with embeddings
- `crawl_jobs` table with status tracking
- Foreign key constraints validation

### External Integrations
**Services to Mock**:
- **OpenAI API**: Embedding generation (mock with fixed vectors)
- **Qdrant Vector DB**: Vector storage/search (mock client)
- **Crawl4AI Library**: Web crawling (mock responses)
- **File System**: Temporary file storage (use tempfile)

**Browser Automation**:
- **Playwright MCP Tools**: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_fill_form`, `browser_wait_for`, `browser_take_screenshot`
- **Frontend Services**: RAG service at `localhost:5173`, ensure running before tests
- **Browser Binaries**: Pre-flight check and auto-install if missing

### Core Logic

**Backend Test Categories**:
1. **Document Upload Pipeline**:
   - File validation (type, size, magic bytes)
   - Parsing (PDF, DOCX, TXT, MD, HTML)
   - Chunking (text splitting with overlap)
   - Embedding generation (OpenAI API)
   - Vector storage (Qdrant upsert)
   - Database persistence (PostgreSQL)

2. **Search Source Filtering**:
   - Vector search without filter
   - Vector search with source_id filter
   - Invalid source_id handling
   - Empty results handling

3. **Delete Functionality**:
   - Cascade delete (document → chunks)
   - Crawl job deletion
   - Source deletion with cascade
   - 404 handling for non-existent IDs

**Frontend Test Workflows**:
1. **Document Upload Flow**:
   - Navigate to upload page
   - Fill form (file, title, source)
   - Submit and wait for completion
   - Verify document in list with chunk count
   - Capture proof screenshot

2. **Search Filtering Flow**:
   - Navigate to search page
   - Enter query and select source filter
   - Verify filtered results
   - Change filter and verify update
   - Capture proof screenshots

3. **Delete Flow**:
   - Navigate to management page
   - Click delete button
   - Confirm in modal
   - Verify removal from list
   - Capture proof screenshot

### UI/CLI Requirements
**New Component Needed**:
- `DocumentsManagement.tsx`: Similar to `CrawlManagement.tsx` and `SourceManagement.tsx`
  - List all documents with metadata (title, type, chunk count, created date)
  - Delete button per document with confirmation modal
  - Pagination support (10/25/50 per page)
  - Source filter dropdown
  - Success/error toast notifications

**Browser Test Requirements**:
- Use accessibility tree (`browser_snapshot()`) for validation, NOT screenshots
- Use semantic queries (`"button containing 'Upload'"`) NOT element refs (`ref="e5"`)
- Pre-flight checks: Verify services running and browser installed
- Auto-wait for elements (`browser_wait_for()`) NOT manual `sleep()`
- One screenshot at end for human proof only

## Similar Implementations Found in Archon

### 1. RAG Service Crawl API Testing
- **Relevance**: 9/10
- **Archon ID**: `/Users/jon/source/vibes/infra/rag-service/backend/tests/integration/test_crawl_api.py`
- **Key Patterns**:
  - FastAPI TestClient with mocked dependencies
  - Async test fixtures using pytest-asyncio
  - Mock database pool with `AsyncMock` for connection/cursor operations
  - Validation tests for UUID formats, required fields, limits
  - Error handling tests (404, 400, 422, 500)
- **Gotchas**:
  - Must override `get_db_pool` dependency in FastAPI app
  - Mock both `fetchval` and `fetchrow` with side effects for multi-step operations
  - Use `side_effect` list for sequential mock returns

### 2. Existing Test Infrastructure (conftest.py)
- **Relevance**: 10/10
- **Archon ID**: `/Users/jon/source/vibes/infra/rag-service/backend/tests/conftest.py`
- **Key Patterns**:
  - Comprehensive fixture library (mock services, test data factories)
  - `mock_db_pool`, `mock_openai_client`, `mock_qdrant_client` fixtures
  - `sample_embedding`, `sample_chunk`, `sample_document_id` test data
  - `mock_mcp_context` for tool testing with all services injected
  - Async event loop fixture for pytest-asyncio
- **Gotchas**:
  - Connection pool `acquire()` must return async context manager
  - Mock both `__aenter__` and `__aexit__` for context managers
  - Services expect `app.state` object with all dependencies

### 3. Browser Validation Pattern
- **Relevance**: 10/10
- **Archon ID**: `.claude/patterns/browser-validation.md`
- **Key Patterns**:
  - Navigation → Interaction → Validation workflow
  - Pre-flight checks (browser installed, services running)
  - Accessibility tree for validation (`browser_snapshot()`)
  - Semantic element queries for stability
  - Retry pattern for flaky operations (max 3 attempts)
- **Gotchas**:
  - Element refs change every render (use semantic queries)
  - Timeout errors (set appropriate timeouts: 5s UI, 30s uploads)
  - Token budget exhaustion (screenshots ~2000 tokens, snapshots ~500 tokens)
  - Thread safety violations (Playwright sync API NOT thread-safe)
  - Frontend service not running (check `docker-compose ps` first)

## Recommended Technology Stack

### Backend Testing
- **Framework**: pytest 8.x with pytest-asyncio
- **Mocking**: unittest.mock (AsyncMock, MagicMock, patch)
- **Test Client**: FastAPI TestClient for API tests
- **Database**: asyncpg with test transaction rollback
- **Coverage**: pytest-cov with 80% minimum threshold
- **Linting**: ruff, mypy (type checking)

### Frontend Testing
- **Browser Automation**: Playwright via MCP_DOCKER tools
- **API**: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_fill_form`, `browser_wait_for`, `browser_take_screenshot`
- **Validation**: Accessibility tree parsing (NOT screenshot analysis)
- **Pre-flight**: `docker-compose ps`, browser installation check
- **Service URLs**:
  - RAG Service: `http://localhost:5173`
  - Backend API: `http://localhost:8002`

### Quality Gates
**Level 1: Syntax & Style (~5s)**
```bash
cd infra/rag-service/backend
ruff check src/ tests/
mypy src/
```

**Level 2: Unit Tests (~30s)**
```bash
pytest tests/unit/ -v --cov=src --cov-report=term-missing
```

**Level 3a: API Integration (~60s)**
```bash
pytest tests/integration/ -v
```

**Level 3b: Browser Integration (~120s)**
```bash
pytest tests/browser/ -v
# Or agent-driven: claude --agent validation-gates "Validate frontend"
```

## Assumptions Made

### 1. **Test Database Configuration**
- **Assumption**: Use existing DATABASE_URL from settings with transaction rollback for isolation
- **Reasoning**: INITIAL.md doesn't specify separate test DB, existing pattern uses main DB with rollback
- **Source**: Existing `test_db_pool` fixture in conftest.py uses `settings.DATABASE_URL`

### 2. **Browser Testing Approach**
- **Assumption**: Use MCP browser tools (not direct Playwright library) for consistency with existing patterns
- **Reasoning**: CLAUDE.md explicitly states "Browser Testing for Agents" uses MCP_DOCKER tools, maintains agent compatibility
- **Source**: `.claude/patterns/browser-validation.md` and CLAUDE.md Browser Testing section

### 3. **Documents Management Page Implementation**
- **Assumption**: Clone structure from `CrawlManagement.tsx` (list, delete, modal, filters)
- **Reasoning**: INITIAL.md states "Similar structure to SourceManagement/CrawlManagement"
- **Source**: Pattern analysis of existing frontend components

### 4. **Test Organization Structure**
- **Assumption**: Organize tests by layer: `tests/unit/`, `tests/integration/`, `tests/browser/`
- **Reasoning**: Aligns with quality-gates pattern (Level 1-3) and existing test structure
- **Source**: Existing test directory structure and quality-gates.md

### 5. **Crawl4AI Investigation Scope**
- **Assumption**: Document truncation issue is a separate investigation task, not blocking main testing work
- **Reasoning**: INITIAL.md lists it under "Known Issues to Address", suggests investigation not immediate fix
- **Source**: INITIAL.md section "Known Issues to Address"

### 6. **Coverage Threshold**
- **Assumption**: 80% code coverage minimum based on INITIAL.md requirement
- **Reasoning**: Explicitly stated in "Backend Validation" checklist
- **Source**: INITIAL.md "Validation Gates" section

### 7. **Test Data Management**
- **Assumption**: Use factories from conftest.py, extend as needed for new test scenarios
- **Reasoning**: DRY principle, existing fixtures cover most use cases
- **Source**: Existing `sample_*` fixtures in conftest.py

### 8. **Error Handling Priority**
- **Assumption**: Test happy path + common errors (404, 400, 422, 500), defer edge cases to Phase 2
- **Reasoning**: INITIAL.md focuses on "proper validation", suggests comprehensive but not exhaustive
- **Source**: Existing test patterns in test_crawl_api.py

### 9. **Screenshot Strategy**
- **Assumption**: One screenshot per test case at completion for human proof, not for agent validation
- **Reasoning**: Browser-validation.md emphasizes accessibility tree for validation, screenshots for proof only
- **Source**: `.claude/patterns/browser-validation.md` Gotcha #6

### 10. **Service Startup Order**
- **Assumption**: Backend starts before frontend, both required for browser tests
- **Reasoning**: Frontend depends on backend API, browser tests need both
- **Source**: docker-compose.yaml service dependencies

## Success Criteria

### Backend Validation
✅ All unit tests pass with >80% coverage
✅ All integration tests pass (API endpoints validated)
✅ Type checking passes (mypy zero errors)
✅ Linting passes (ruff zero violations)
✅ Tests run in <30s (unit) and <60s (integration)

### Frontend Validation (Playwright)
✅ Browser binaries installed (pre-flight check passes)
✅ Services running (docker-compose up -d verified)
✅ All browser tests pass (document upload, search filter, delete)
✅ Screenshots captured for proof (one per test case)
✅ No console errors in browser (checked via accessibility tree)
✅ Tests run in <120s total

### End-to-End Validation
✅ Complete workflow test passes (create source → crawl → upload → search → delete)
✅ Data persists correctly across operations
✅ UI reflects backend state accurately
✅ Error states handled gracefully (network failures, invalid inputs)

### Documentation
✅ Test results documented with pass/fail status
✅ Screenshots prove functionality
✅ Known issues documented (Crawl4AI truncation)
✅ Test coverage report generated

### Regression Prevention
✅ No existing tests broken
✅ All features work as before
✅ CI/CD pipeline includes new tests

## Next Steps for Downstream Agents

### Codebase Researcher
Focus on:
- Document upload ingestion pipeline implementation (`infra/rag-service/backend/src/api/routes/documents.py:174-283`)
- Search source filtering logic (`SearchInterface.tsx`, `backend/src/services/search/`)
- Delete functionality (`CrawlManagement.tsx`, `client.ts`, `backend/src/api/routes/`)
- Existing test patterns (`tests/integration/test_crawl_api.py`, `tests/conftest.py`)
- Frontend component structure (`CrawlManagement.tsx` as template for DocumentsManagement)

### Documentation Hunter
Find docs for:
- **pytest-asyncio**: Async test fixtures and event loop configuration
- **FastAPI TestClient**: Mocking dependencies, overriding DI
- **Playwright Python**: Accessibility tree API, semantic locators, auto-waiting
- **MCP Browser Tools**: Tool signatures, parameters, return types
- **asyncpg**: Test transaction rollback, connection pool testing
- **unittest.mock**: AsyncMock patterns, side_effect lists, patch decorators

### Example Curator
Extract examples showing:
- **Document upload testing**: File validation, multipart/form-data handling
- **Browser automation**: Navigation → Interaction → Validation pattern
- **Async test fixtures**: Database pool, service mocking
- **Error handling tests**: 400, 404, 422, 500 status codes
- **Cascade delete testing**: Foreign key constraint validation
- **Search filtering**: Source_id parameter, result validation

### Gotcha Detective
Investigate:
1. **Browser binary installation**: Auto-install flow, version compatibility
2. **Frontend service startup**: Health check endpoints, retry logic
3. **Element ref instability**: Semantic query alternatives
4. **Timeout configuration**: Per-operation timeouts (UI vs upload)
5. **Mock side effects**: Sequential return values for multi-step operations
6. **Async context managers**: `__aenter__`/`__aexit__` mocking
7. **Test isolation**: Transaction rollback, data cleanup
8. **Crawl4AI truncation**: Configuration options, chunk size limits
9. **Token budget**: Accessibility tree vs screenshot costs
10. **Thread safety**: Playwright sync API limitations
11. **Port conflicts**: Service identity verification
12. **File upload security**: Magic byte validation, MIME type checks
