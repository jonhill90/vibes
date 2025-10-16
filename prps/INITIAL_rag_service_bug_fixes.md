# RAG Service Bug Fixes - Critical UI Issues

## Problem Statement

The RAG service has three critical bugs preventing core functionality:

1. **Source Creation (422 Error)**: Users cannot create new sources - API returns validation error
2. **Document Upload (400 Error)**: Document upload fails with database error - frontend sending source title instead of UUID
3. **Frontend Unavailable**: Frontend unhealthy, connection refused on port 5173

**Evidence from logs**:
```
# Source creation validation error
INFO: 172.66.0.243:58682 - "POST /api/sources HTTP/1.1" 422 Unprocessable Entity

# Document upload database error
Database error creating document: invalid input for query argument $1: 'TEst'
(invalid UUID 'TEst': length must be between 32..36 characters, got 4)
INFO: 172.66.0.243:37956 - "POST /api/documents HTTP/1.1" 400 Bad Request

# Frontend status
rag-frontend   rag-service-frontend   Up 22 hours (unhealthy)
```

## Success Criteria

- [ ] Source creation form validates and creates sources successfully
- [ ] Document upload accepts files and stores with correct source_id (UUID)
- [ ] Frontend serves on port 5173 with healthy status
- [ ] All three operations testable via browser automation

## Technical Context

**Backend**: FastAPI (port 8003-8004) - healthy
**Frontend**: React + Vite (port 5173) - unhealthy
**Database**: PostgreSQL with pgvector - healthy

**Root Causes**:
1. Source creation: Validation schema mismatch or missing required fields
2. Document upload: Frontend sending source.title instead of source.id
3. Frontend: Vite dev server crash or misconfiguration

## Implementation Tasks

### Task 1: Diagnose Frontend Health
**Priority**: CRITICAL (blocking UI access)
**Assignee**: prp-exec-implementer
**Description**:
- Check frontend container logs for crash/error
- Verify Vite configuration and port binding
- Fix startup issues and validate healthy status
- Test browser access on localhost:5173

**Files to check**:
- `infra/rag-service/frontend/vite.config.ts`
- `infra/rag-service/docker-compose.yml` (frontend service)
- Frontend container logs

**Validation**:
```bash
docker-compose logs frontend --tail=100
curl -I http://localhost:5173
docker-compose ps | grep frontend  # Should show (healthy)
```

### Task 2: Fix Source Creation Validation
**Priority**: HIGH (blocks document uploads)
**Assignee**: prp-exec-implementer
**Description**:
- Examine backend source creation endpoint (`POST /api/sources`)
- Check Pydantic model validation requirements
- Compare frontend form payload with backend schema
- Fix validation mismatch (missing fields, wrong types)
- Test with browser automation

**Files to check**:
- `infra/rag-service/backend/app/api/endpoints/sources.py`
- `infra/rag-service/backend/app/models/source.py`
- `infra/rag-service/frontend/src/components/SourceForm.tsx`

**Validation**:
```python
# Browser test
browser_navigate("http://localhost:5173")
browser_click(element="Create Source button")
browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "value": "Test Source"},
    {"name": "url", "type": "textbox", "value": "https://example.com"}
])
browser_click(element="Submit")
browser_wait_for(text="Source created", timeout=5000)
```

### Task 3: Fix Document Upload Source ID
**Priority**: HIGH (core functionality broken)
**Assignee**: prp-exec-implementer
**Description**:
- Fix frontend to send source.id (UUID) instead of source.title
- Verify backend expects UUID in source_id field
- Update document upload form to use source dropdown with IDs
- Test end-to-end document upload flow

**Files to fix**:
- `infra/rag-service/frontend/src/components/DocumentUpload.tsx`
- `infra/rag-service/backend/app/api/endpoints/documents.py`

**Current bug**:
```
Database error: invalid UUID 'TEst': length must be between 32..36 characters, got 4
```

**Expected behavior**:
```javascript
// Frontend should send:
{
  source_id: "06216db3-ee22-4a33-a9ce-e638d07970d8",  // UUID
  file: <File>
}

// NOT:
{
  source_id: "TEst",  // source title
  file: <File>
}
```

**Validation**:
```python
# Browser test
browser_navigate("http://localhost:5173")
browser_click(element="Upload Document button")
browser_fill_form(fields=[
    {"name": "source", "type": "combobox", "value": "Test Source"},
    {"name": "file", "type": "file", "value": "/tmp/test.pdf"}
])
browser_click(element="Upload")
browser_wait_for(text="Upload successful", timeout=30000)
```

## Testing Strategy

### Level 1: Backend API Tests
```bash
# Test source creation
curl -X POST http://localhost:8003/api/sources \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "url": "https://example.com"}'

# Test document upload with valid UUID
curl -X POST http://localhost:8003/api/documents \
  -F "source_id=<valid-uuid>" \
  -F "file=@test.pdf"
```

### Level 2: Frontend Component Tests
- React component rendering tests
- Form validation tests
- API integration tests

### Level 3: Browser Integration Tests
- Full user flow: Create source → Upload document → Search
- Browser automation validation (see task validation blocks)

## Quality Gates

**Exit Criteria**:
1. ✅ Frontend serves on port 5173 (healthy status)
2. ✅ Source creation succeeds via UI (no 422 errors)
3. ✅ Document upload succeeds with valid source (no 400 errors)
4. ✅ Browser automation tests pass for all three operations
5. ✅ Backend logs show 200 OK responses for all endpoints

**Validation Commands**:
```bash
# Check all services healthy
docker-compose ps | grep -v "(healthy)"  # Should be empty

# Check recent errors
docker-compose logs backend --tail=50 | grep -E "(422|400|500)"

# Browser validation
# Run browser automation tests (see task validation blocks)
```

## Patterns Used

- **browser-validation**: Full-stack UI testing with Playwright
- **quality-gates**: Three-level validation (API → Component → Browser)
- **task-driven-development**: Archon task tracking throughout

## Resources

- Backend API docs: http://localhost:8003/docs
- Frontend: http://localhost:5173
- Database: postgresql://raguser@localhost:5433/ragservice
