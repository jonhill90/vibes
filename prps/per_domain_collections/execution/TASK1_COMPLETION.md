# Task 1 Implementation Complete: Add collection_names column to sources table

## Task Information
- **Task ID**: N/A (PRP execution)
- **Task Name**: Task 1: Add collection_names column to sources table
- **Responsibility**: Create database migration to add JSONB column for storing collection name mappings per source, enabling domain-isolated vector collections
- **Status**: COMPLETE - Ready for Review

## Files Created/Modified

### Created Files:
1. **`/Users/jon/source/vibes/infra/rag-service/database/migrations/004_add_collection_names.sql`** (282 lines)
   - Database migration for adding collection_names JSONB column
   - Includes data population logic with title sanitization
   - GIN index for efficient JSON queries
   - Comprehensive validation and verification queries
   - Rollback instructions for emergency use

### Modified Files:
None - This task only creates the migration file

## Implementation Details

### Core Features Implemented

#### 1. JSONB Column for Collection Names
- Added `collection_names JSONB` column with default `'{}'::JSONB`
- Stores mapping: `collection_type → Qdrant collection name`
- Example: `{"documents": "AI_Knowledge_documents", "code": "AI_Knowledge_code"}`

#### 2. GIN Index for Performance
- Created `idx_sources_collection_names` GIN index
- Supports efficient JSON queries:
  - `WHERE collection_names ? 'documents'` (key existence)
  - `WHERE collection_names @> '{"documents": "AI_Knowledge_documents"}'` (containment)

#### 3. Data Migration with Sanitization
Implemented title sanitization logic per PRP (lines 119-130):
- Replace non-alphanumeric characters with underscores
- Collapse multiple underscores into one
- Strip leading/trailing underscores
- Limit to 64 characters total
- Append collection type suffix

Examples from production data:
- "Test Source" + "documents" → "Test_Source_documents"
- "Pydantic AI" + "documents" → "Pydantic_AI_documents"
- "Xerox" + "documents" → "Xerox_documents"

#### 4. Comprehensive Validation
- Column type verification (JSONB)
- Index existence check
- Data integrity validation (all sources populated)
- Collection_names keys match enabled_collections
- Migration statistics reporting

#### 5. Idempotent Migration
- Safe to run multiple times using DO blocks
- IF NOT EXISTS checks for column and index
- Only updates sources with empty collection_names

### Critical Gotchas Addressed

#### Gotcha #1: Set-Returning Functions in WHERE Clause
**Issue**: Initial validation query used `jsonb_object_keys()` in WHERE clause, causing SQL error
**Fix**: Rewrote query to use subqueries with `array_agg()` for proper comparison
```sql
-- BEFORE (broken):
WHERE jsonb_object_keys(collection_names) IS DISTINCT FROM (...)

-- AFTER (fixed):
WHERE (SELECT array_agg(key ORDER BY key) FROM jsonb_object_keys(...)) IS DISTINCT FROM (...)
```

#### Gotcha #2: Sanitization Edge Cases
**Handled**:
- Null titles fallback to `'Source_' || id::text`
- Special characters properly escaped in regex
- Multiple underscore collapse using `'_+'` pattern
- Leading/trailing underscore removal using `'^_+|_+$'` pattern

#### Gotcha #3: SUBSTRING vs LENGTH for Truncation
**Implementation**: Used `SUBSTRING(... FROM 1 FOR 64)` for clean truncation to 64 chars
- More reliable than `LEFT()` for multi-byte characters
- Ensures collection name fits Qdrant limits (255 chars, using 64 for safety)

## Dependencies Verified

### Completed Dependencies:
- None - This is Task 1 (first task in Phase 1)
- Can run independently with no blockers

### External Dependencies:
- PostgreSQL 15+ with JSONB support
- Existing `sources` table with `enabled_collections` column (from migration 003)
- Docker container `rag-postgres` running with `ragservice` database

## Testing Checklist

### Manual Testing (Completed):
- [x] Migration executes without errors
- [x] Column `collection_names` created with JSONB type
- [x] GIN index `idx_sources_collection_names` created
- [x] Existing sources populated with sanitized collection names
- [x] Validation queries pass (all ✓ checks)
- [x] Migration can be rolled back successfully
- [x] Re-running migration is idempotent (no errors)

### Validation Results:
```
✓ collection_names column exists with JSONB type
✓ GIN index created on collection_names
✓ All sources have valid collection_names
✓ All collection_names match enabled_collections
✓ 3 of 3 sources populated successfully

Production Data Verified:
- "Test Source" → {"documents": "Test_Source_documents"}
- "Xerox" → {"documents": "Xerox_documents"}
- "Pydantic AI" → {"documents": "Pydantic_AI_documents"}
```

### SQL Syntax Validation:
- Migration executed with `--single-transaction --set ON_ERROR_STOP=on`
- No SQL errors
- All DO blocks executed successfully
- ANALYZE completed without warnings

## Success Metrics

**All PRP Requirements Met**:
- [x] Create migration file `004_add_collection_names.sql`
- [x] Add JSONB column `collection_names` with default `'{}'::JSONB`
- [x] Create GIN index `idx_sources_collection_names`
- [x] Populate collection_names for existing sources
- [x] Implement title sanitization (alphanumeric + underscores)
- [x] Handle special characters correctly
- [x] Add rollback statements (DROP INDEX, DROP COLUMN)
- [x] Follow existing migration pattern (003_add_enabled_collections.sql)

**Code Quality**:
- Comprehensive inline documentation
- Clear section headers matching migration 003 pattern
- Idempotent implementation (safe re-runs)
- Detailed verification and validation logic
- Migration statistics for audit trail
- Example output for verification
- Emergency rollback instructions

**Database Integrity**:
- No data loss during migration
- All existing sources updated correctly
- Sanitization handles edge cases (null titles, special chars)
- Collection names match enabled_collections 1:1

## Completion Report

**Status**: COMPLETE - Ready for Review
**Implementation Time**: ~30 minutes
**Confidence Level**: HIGH
**Blockers**: None

### Files Created: 1
### Files Modified: 0
### Total Lines of Code: ~282 lines

**Migration Successfully Applied to Database**:
- Column: `collection_names JSONB` ✓
- Index: `idx_sources_collection_names (GIN)` ✓
- Data: 3/3 sources populated ✓
- Validation: All checks passed ✓

**Next Steps**:
- Task 2 (CollectionManager) can proceed independently (parallel execution)
- Migration 004 is production-ready
- Database schema supports per-domain collection architecture

**Ready for integration and next phase (Phase 2: Ingestion Pipeline).**
