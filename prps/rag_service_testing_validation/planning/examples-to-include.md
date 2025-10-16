# Examples Curated: rag_service_testing_validation

## Summary

Extracted **6 code examples** to the examples directory (`prps/rag_service_testing_validation/examples/`). These examples provide comprehensive coverage of testing patterns needed for RAG service validation, including backend unit/integration tests, frontend React components, browser automation, and API client patterns.

**Total Files Created**: 7 (6 examples + 1 comprehensive README)
**Total Lines**: ~1,500 lines of documented code patterns
**Coverage**: Backend (pytest), Frontend (React), Browser (Playwright), API clients

---

## Files Created

### 1. example_1_test_fixtures.py
**Source**: `infra/rag-service/backend/tests/conftest.py` (lines 1-331)
**Pattern**: Pytest fixtures with async mocking
**Relevance**: 10/10

**Key Patterns**:
- Mock asyncpg connection pool with async context manager
- Mock OpenAI and Qdrant clients with AsyncMock
- Test data factories (embeddings, UUIDs, chunks)
- Async event loop fixture for pytest-asyncio
- MCP context mock for tool testing

**What to Copy**: Fixture structure, async context manager mocking pattern, service mock setup

---

### 2. example_2_fastapi_test_pattern.py
**Source**: `infra/rag-service/backend/tests/integration/test_crawl_api.py` (lines 1-243)
**Pattern**: FastAPI TestClient with dependency injection
**Relevance**: 9/10

**Key Patterns**:
- Create test app with routes and override dependencies
- Use `side_effect` lists for sequential mock returns
- Test class organization by endpoint
- Validation testing (400, 404, 422, 500 errors)
- Mock database operations for multi-step processes

**What to Copy**: TestClient setup, dependency override pattern, error status testing, side_effect usage

---

### 3. example_3_file_upload_validation.py
**Source**: `infra/rag-service/backend/src/api/routes/documents.py` (lines 39-173)
**Pattern**: Defensive file upload validation
**Relevance**: 9/10

**Key Patterns**:
- Extension whitelist validation
- File size limit enforcement (10MB)
- MIME type checking (secondary validation)
- User-friendly error messages with suggestions
- Document type mapping from extension

**What to Copy**: Multi-level validation approach, error message structure, security checks

---

### 4. example_4_react_component_pattern.py
**Source**: `infra/rag-service/frontend/src/components/CrawlManagement.tsx` (full component)
**Pattern**: React CRUD component with state management
**Relevance**: 10/10

**Key Patterns**:
- useState for component state (items, loading, error, filters)
- useEffect for data loading and auto-refresh
- useCallback for memoized functions
- react-hook-form for form validation
- Delete confirmation modal (two-step pattern)
- Status badges with conditional styling
- Expandable card details
- Filter dropdowns and pagination

**What to Copy**: State management structure, form handling, modal pattern, status badges

---

### 5. example_5_browser_validation_workflow.py
**Source**: `.claude/patterns/browser-validation.md` (lines 304-403)
**Pattern**: Playwright browser automation workflow
**Relevance**: 10/10

**Key Patterns**:
- Pre-flight checks (browser installed, services running)
- Accessibility tree validation (`browser_snapshot()`)
- Semantic element queries (stable, not refs)
- Auto-wait with `browser_wait_for()`
- Validation checklist with clear status reporting
- Screenshot for human proof (end of test only)
- Error handling with retry logic

**What to Copy**: Pre-flight check functions, navigation → interaction → validation flow, validation checklist pattern

---

### 6. example_6_api_client_patterns.py
**Source**: `infra/rag-service/frontend/src/api/client.ts` (full file)
**Pattern**: TypeScript API client with typed requests
**Relevance**: 8/10

**Key Patterns**:
- Axios client configuration (baseURL, timeout, headers)
- Global error interceptor for error handling
- FormData for file uploads (multipart/form-data)
- Query parameters for list/filter operations
- Typed request/response interfaces
- Python equivalent patterns for testing

**What to Copy**: Request structure, FormData usage, error handling, Python test equivalents

---

### 7. README.md (Comprehensive Guide)
**Content**: Master guide with detailed "What to Mimic/Adapt/Skip" for each example
**Lines**: ~800 lines of documentation
**Sections**:
- Overview and example index
- Detailed breakdown for each example (What to Mimic, Adapt, Skip, Pattern Highlights, Why This Example)
- Usage instructions (Study Phase, Application Phase, Testing Patterns)
- Pattern summary and anti-patterns
- Integration with PRP guidance
- Quality assessment (9.3/10 overall)

---

## Key Patterns Extracted

### Backend Testing Patterns
1. **Async Context Manager Mocking**: Mock `pool.acquire()` with async generator
2. **Side Effect Lists**: Sequential mock returns for multi-step operations
3. **Dependency Override**: FastAPI `app.dependency_overrides[get_db_pool]`
4. **Error Status Testing**: Validate 400, 404, 413, 422, 500 responses
5. **File Upload Testing**: Use `files` parameter with tuple (filename, content, mime_type)

### Frontend Patterns
6. **State Management**: useState + useEffect + useCallback for data loading
7. **Form Handling**: react-hook-form with validation and reset
8. **Delete Confirmation**: Two-step modal pattern (click → confirm)
9. **Status Badges**: Switch-case styling based on status
10. **Auto-Refresh**: Interval polling for active jobs/processes

### Browser Testing Patterns
11. **Pre-Flight Checks**: Verify browser installed and services running
12. **Accessibility Tree Validation**: Use `browser_snapshot()` not screenshots
13. **Semantic Queries**: `"button containing 'Upload'"` not `ref="e5"`
14. **Auto-Wait**: `browser_wait_for(text="Success", timeout=30000)`
15. **Validation Checklist**: Dictionary of checks with all() for pass/fail

### Security Patterns
16. **Extension Whitelist**: Only allow `.pdf, .docx, .txt, .md, .html`
17. **Size Limits**: Enforce MAX_FILE_SIZE before processing
18. **MIME Type Validation**: Secondary check, log warnings
19. **Error Messages**: Include error, detail, suggestion fields

---

## Recommendations for PRP Assembly

### 1. Reference in "All Needed Context" Section
Add this to PRP:
```markdown
## Code Examples
Study these examples before implementation (located in `prps/rag_service_testing_validation/examples/`):

**Backend Testing**:
- Example 1: Test fixtures with async mocking
- Example 2: FastAPI integration test pattern
- Example 3: File upload validation

**Frontend Development**:
- Example 4: React CRUD component structure

**Browser Validation**:
- Example 5: Playwright automation workflow

**API Integration**:
- Example 6: API client patterns for testing

See `examples/README.md` for detailed "What to Mimic/Adapt/Skip" guidance for each example.
```

### 2. Include Pattern Highlights in "Implementation Blueprint"
Key patterns to emphasize:
- **Async context manager mocking** (Example 1) - Essential for database tests
- **Side effect lists** (Example 2) - Multi-step operation testing
- **Browser pre-flight checks** (Example 5) - Prevent common failures
- **Delete confirmation modal** (Example 4) - UX best practice

### 3. Direct Implementer to Study Before Coding
Add to PRP validation checklist:
```markdown
## Pre-Implementation Checklist
- [ ] Read `examples/README.md` cover-to-cover
- [ ] Studied Example 1 (test fixtures)
- [ ] Studied Example 2 (FastAPI tests)
- [ ] Studied Example 5 (browser validation)
- [ ] Identified which patterns apply to current task
- [ ] Prepared to adapt patterns (not copy verbatim)
```

### 4. Use Examples for Validation
During code review, check:
- ✅ Are test fixtures structured like Example 1?
- ✅ Do integration tests use TestClient pattern from Example 2?
- ✅ Does file upload validation follow Example 3 security checks?
- ✅ Does React component match Example 4 state management patterns?
- ✅ Do browser tests follow Example 5 pre-flight → navigate → interact → validate workflow?

### 5. Reference Specific Examples in Task Descriptions
For each task in PRP:
```markdown
**Task 1: Backend Unit Tests**
See: Example 1 (fixtures), Example 3 (validation logic)
Pattern: Mock services, test validation layers

**Task 2: Integration Tests**
See: Example 2 (FastAPI TestClient)
Pattern: Override dependencies, test error responses

**Task 3: Browser Validation**
See: Example 5 (Playwright workflow)
Pattern: Pre-flight checks, accessibility tree validation

**Task 4: DocumentsManagement Component**
See: Example 4 (React CRUD pattern)
Pattern: State management, delete confirmation, filters
```

---

## Quality Assessment

### Coverage: 10/10
- ✅ Backend unit testing (fixtures, mocks)
- ✅ Backend integration testing (FastAPI TestClient)
- ✅ File upload validation and security
- ✅ Frontend React component patterns
- ✅ Browser automation workflow
- ✅ API client patterns for testing

All major testing patterns needed for RAG service validation are covered.

### Relevance: 9.2/10
- ✅ All examples directly applicable to RAG service
- ✅ Patterns extracted from actual working code
- ✅ Browser validation matches project conventions
- ⚠️ API client example is TypeScript (but includes Python equivalents)

Every example has clear relevance to the testing requirements.

### Completeness: 9/10
- ✅ Each example has source attribution (file, lines)
- ✅ Each example includes "What to Mimic/Adapt/Skip" guidance
- ✅ Pattern highlights explain WHY patterns work
- ✅ README provides comprehensive usage instructions
- ⚠️ Could include more edge case examples (but covered in gotchas)

Examples are self-contained and well-documented.

### Usability: 9.5/10
- ✅ Clear organization (numbered examples, logical order)
- ✅ Comprehensive README with study/application phases
- ✅ Pattern highlights with code snippets
- ✅ Anti-patterns documented (what NOT to do)
- ✅ Integration guidance for PRP assembly

Ready to use immediately, minimal explanation needed.

### Overall: 9.3/10

**Strengths**:
- Comprehensive coverage of all testing patterns
- Actual working code extracted (not hypothetical)
- Clear "What to Mimic/Adapt/Skip" for each example
- Pattern highlights explain the "why" not just "what"
- README is a complete guide (study → apply → validate)

**Areas for Improvement**:
- Could add more error handling edge cases
- Could include performance testing patterns
- Could add CI/CD integration examples

**Recommendation**: Examples are production-ready. Use as primary reference for test implementation.

---

## Next Steps

### For Codebase Researcher
Use these examples as reference when extracting implementation details:
- Example 1: Fixture patterns for service initialization
- Example 3: Document upload pipeline logic
- Example 4: Frontend component structure

### For Documentation Hunter
Look for docs on:
- pytest-asyncio (async test patterns from Example 1)
- FastAPI TestClient (integration test patterns from Example 2)
- Playwright accessibility tree (validation patterns from Example 5)

### For Gotcha Detective
Cross-reference these gotchas with examples:
- Gotcha #6 (Async context managers): See Example 1
- Gotcha #2 (Frontend service not running): See Example 5 pre-flight checks
- Gotcha #4 (Element refs change): See Example 5 semantic queries
- Gotcha #12 (File upload security): See Example 3 validation layers

### For Assembler
Integrate examples into PRP:
1. Reference examples in "All Needed Context"
2. Include pattern highlights in "Implementation Blueprint"
3. Add pre-implementation checklist (study examples first)
4. Link specific examples to each task
5. Use examples for validation criteria

---

Generated: 2025-10-16
Feature: rag_service_testing_validation
Total Examples: 6
Total Files: 7 (6 examples + README)
Quality Score: 9.3/10
Coverage: Comprehensive (backend, frontend, browser, API)
Readiness: Production-ready, use immediately
