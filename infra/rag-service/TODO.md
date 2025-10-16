# RAG Service Status

## Fixed
- Backend crawl endpoint metadata (json.dumps in POST, json.loads in GET)
- Frontend API baseURL changed to http://localhost:8003 (works for Mac browser)
- All React null safety

## Current Status
- Backend accessible at localhost:8003 ✓ (returns 5 sources)
- Frontend accessible at localhost:5173
- API client using localhost:8003
- Ready for user to test in Mac browser
