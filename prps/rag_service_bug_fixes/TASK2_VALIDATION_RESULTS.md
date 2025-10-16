# Task 2: Source Creation Validation - COMPLETED

## Problem Statement
Users could not create sources via the frontend. Backend was returning 422 Unprocessable Entity errors.

## Root Cause Analysis

### Issue 1: Schema Mismatch - Field Names
**Frontend sent**: `{ name: string, source_type: string }`
**Backend expected**: `{ source_type: string, url?: string, metadata?: dict }`

The frontend was sending a `name` field that didn't exist in the backend schema.

### Issue 2: Enum Value Mismatch
**Frontend source_type values**: `document`, `web`, `database`, `other`
**Backend accepted values**: `upload`, `crawl`, `api`

The frontend dropdown had completely different enum values than what the backend accepted.

### Issue 3: Missing Human-Readable Name Field
The database sources table has no `name` column, only metadata. The UI needs human-readable names for sources.

## Solution Implemented

### Backend Changes
1. **Added `title` field to SourceCreateRequest** (`backend/src/models/requests.py`)
   - Optional field, max 500 characters
   - Stored in metadata as `{"title": "..."}` for backwards compatibility

2. **Added `title` field to SourceResponse** (`backend/src/models/responses.py`)
   - Extracts title from metadata when returning sources
   - Returns `null` for sources without title (backwards compatible)

3. **Updated all source routes** (`backend/src/api/routes/sources.py`)
   - `create_source`: Stores title in metadata
   - `list_sources`: Extracts title from metadata
   - `get_source`: Extracts title from metadata
   - `update_source`: Handles title updates by merging with existing metadata

4. **Added `title` to SourceUpdateRequest** (`backend/src/models/requests.py`)
   - Allows updating source title after creation

### Frontend Changes
1. **Updated TypeScript interfaces** (`frontend/src/api/client.ts`)
   - Changed `name` to `title` in SourceRequest
   - Updated SourceResponse to include title, status, metadata fields
   - Aligned with backend schema

2. **Fixed source_type enum values** (`frontend/src/components/SourceManagement.tsx`)
   - Changed from: `document`, `web`, `database`, `other`
   - Changed to: `upload`, `crawl`, `api`
   - Now matches backend validation

3. **Updated UI component** (`frontend/src/components/SourceManagement.tsx`)
   - Changed form field from `name` to `title`
   - Made title optional (not required)
   - Added Status column to table
   - Display fallback for sources without title: `url || id.slice(0,8)`
   - Fixed edit mode to use `title` instead of `name`

## Validation Results

### Backend API Tests
```bash
# Test 1: Create source with title ✅
curl -X POST http://localhost:8003/api/sources \
  -H "Content-Type: application/json" \
  -d '{"source_type": "upload", "title": "My Test Source"}'
Response: 201 Created
{
  "id": "5cdc8271-bbed-4450-9038-2d4fd42061e9",
  "source_type": "upload",
  "title": "My Test Source",
  "status": "pending",
  "metadata": {"title": "My Test Source"}
}

# Test 2: Create source without title (backwards compatible) ✅
curl -X POST http://localhost:8003/api/sources \
  -H "Content-Type: application/json" \
  -d '{"source_type": "upload"}'
Response: 201 Created
{
  "id": "f27a6933-a051-4958-9dc1-58a2cffd1124",
  "source_type": "upload",
  "title": null,
  "status": "pending"
}

# Test 3: Reject invalid source_type ✅
curl -X POST http://localhost:8003/api/sources \
  -H "Content-Type: application/json" \
  -d '{"source_type": "document", "title": "Should Fail"}'
Response: 422 Unprocessable Entity
{
  "detail": [{
    "msg": "Value error, source_type must be one of: upload, crawl, api. Got: document"
  }]
}

# Test 4: List sources with title extraction ✅
curl http://localhost:8003/api/sources
Response: 200 OK
{
  "sources": [
    {"id": "...", "title": "My Test Source", ...},
    {"id": "...", "title": null, ...}
  ],
  "total_count": 4
}

# Test 5: Crawl source with URL ✅
curl -X POST http://localhost:8003/api/sources \
  -H "Content-Type: application/json" \
  -d '{"source_type": "crawl", "title": "Web Crawl", "url": "https://example.com"}'
Response: 201 Created
```

### Frontend Validation
- ✅ Frontend service healthy on port 5173
- ✅ Vite HMR picked up code changes automatically
- ✅ No TypeScript compilation errors
- ✅ Form now uses correct field names (title, not name)
- ✅ Dropdown uses correct enum values (upload, crawl, api)

### Backend Logs Analysis
**Before fix**: `POST /api/sources HTTP/1.1" 422 Unprocessable Entity`
**After fix**: `POST /api/sources HTTP/1.1" 201 Created`

Recent logs show consistent 201 Created responses, confirming the fix works.

## Files Modified

### Backend
1. `/Users/jon/source/vibes/infra/rag-service/backend/src/models/requests.py`
   - Added `title` field to SourceCreateRequest
   - Added `title` field to SourceUpdateRequest

2. `/Users/jon/source/vibes/infra/rag-service/backend/src/models/responses.py`
   - Added `title` field to SourceResponse

3. `/Users/jon/source/vibes/infra/rag-service/backend/src/api/routes/sources.py`
   - Updated create_source to store title in metadata
   - Updated list_sources to extract title from metadata
   - Updated get_source to extract title from metadata
   - Updated update_source to handle title updates

### Frontend
1. `/Users/jon/source/vibes/infra/rag-service/frontend/src/api/client.ts`
   - Updated SourceRequest interface (name → title)
   - Updated SourceResponse interface (added title, status, metadata)

2. `/Users/jon/source/vibes/infra/rag-service/frontend/src/components/SourceManagement.tsx`
   - Changed form field from name to title
   - Fixed source_type enum values
   - Added Status column
   - Updated edit mode to use title
   - Added fallback display for sources without title

## Backwards Compatibility
- ✅ Old sources without title display correctly (show url or id)
- ✅ Creating sources without title still works
- ✅ Metadata structure preserved (title stored as `{"title": "..."}`)
- ✅ No database migration required

## Known Gotchas Addressed
1. **Pydantic validation**: Used field validators to provide clear error messages
2. **Metadata handling**: Stored title in metadata for flexibility
3. **Frontend type safety**: Updated TypeScript interfaces to match backend
4. **Enum validation**: Clear validation messages for invalid source_type values

## Success Criteria
- ✅ Source creation form validates correctly
- ✅ Backend accepts title field
- ✅ Frontend sends correct source_type enum values
- ✅ No more 422 errors for valid source creation
- ✅ Title displayed in source list
- ✅ Backwards compatible with existing sources

## Next Steps
This fix unblocks:
- Task 3: Document Upload (needs valid source IDs)
- User ability to organize documents by source
- Web crawling functionality (crawl source type now works)
