# Integration Tests

Integration tests for the RAG service that validate end-to-end functionality.

## Test Files

### `test_source_creation_api.sh`
**Type**: API Integration Test
**Description**: Tests source creation via HTTP API calls
**Tests**:
- Create source with title (upload type)
- Verify title is returned in response
- Reject invalid source_type enum (validation)
- Create source without title (backwards compatibility)
- List sources and verify title extraction

**Run**:
```bash
./tests/integration/test_source_creation_api.sh
```

**Requirements**:
- Backend running on `localhost:8003`
- `curl` and `python3` installed

### `test_source_creation_browser.py`
**Type**: Browser Integration Test
**Description**: Tests source creation using Playwright browser automation
**Tests**:
- Navigate to frontend UI
- Fill source creation form
- Submit and verify source appears
- Verify via backend API as fallback

**Run**:
```bash
python3 tests/integration/test_source_creation_browser.py
```

**Requirements**:
- Frontend running on `localhost:5173`
- Backend running on `localhost:8003`
- Playwright installed: `pip install playwright && playwright install chromium`

## Test Coverage

These tests validate the fixes for:
- **Bug #1**: Frontend health (connection issues)
- **Bug #2**: Source creation validation (422 errors)
- **Bug #3**: Document upload source ID (400 errors)

## Running All Tests

```bash
# API tests (fast)
./tests/integration/test_source_creation_api.sh

# Browser tests (slower, requires Playwright)
python3 tests/integration/test_source_creation_browser.py
```

## Test Levels

- **Level 1**: Unit tests (in `tests/unit/`)
- **Level 2**: API integration tests (bash scripts in this folder)
- **Level 3**: Browser integration tests (Python/Playwright in this folder)
