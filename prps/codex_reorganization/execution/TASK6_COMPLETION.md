# Task 6 Implementation Complete: Update Path References in Test Files

## Task Information
- **Task ID**: N/A (part of PRP execution)
- **Task Name**: Task 6: Update Path References in Test Files
- **Responsibility**: Update all ${REPO_ROOT} path references to new locations
- **Status**: COMPLETE - All path references updated

## Files Created/Modified

### Created Files:
None - This task only modified existing files.

### Modified Files:
1. **`.codex/tests/test_generate_prp.sh`**
   - Updated 24 path references from `scripts/codex/` to `.codex/scripts/`
   - Updated header comment from `tests/codex/` to `.codex/tests/`
   - All script source paths updated
   - All script variable assignments updated

2. **`.codex/tests/test_parallel_timing.sh`**
   - Updated 8 path references from `scripts/codex/` to `.codex/scripts/`
   - Updated header comment from `tests/codex/` to `.codex/tests/`
   - All script source paths updated

3. **`.codex/tests/test_execute_prp.sh`**
   - Updated 20 path references from `scripts/codex/` to `.codex/scripts/`
   - Updated header comment from `tests/codex/` to `.codex/tests/`
   - All script source paths updated
   - All script variable assignments updated

## Implementation Details

### Core Features Implemented

#### 1. Path Reference Updates via sed
- **Pattern**: Used pipe delimiter (`|`) instead of slash (`/`) to avoid escaping issues
- **Approach**: 4 separate sed passes for comprehensive coverage:
  1. `${REPO_ROOT}/scripts/codex/` → `${REPO_ROOT}/.codex/scripts/`
  2. `${REPO_ROOT}/tests/codex/` → `${REPO_ROOT}/.codex/tests/`
  3. `scripts/codex/` → `.codex/scripts/` (unquoted paths)
  4. `tests/codex/` → `.codex/tests/` (unquoted paths)
- **Safety**: Created `.bak` backups before each modification (cross-platform compatible)

#### 2. Comprehensive Coverage
- Updated all test file headers (comment paths)
- Updated all `source` command paths
- Updated all script variable assignments (`local script="${REPO_ROOT}/...`)
- Updated all dependency path constructions (`local dep_path="${REPO_ROOT}/...`)

#### 3. Verification
- Zero instances of old paths remain in test files
- All test files pass `bash -n` syntax validation
- Backup files created and then removed after verification

### Critical Gotchas Addressed

#### Gotcha #1: sed Delimiter Conflicts
**From PRP lines 243-252**: Using `/` delimiter with paths requires escaping
**Implementation**: Used `|` delimiter throughout:
```bash
sed -i.bak 's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g'
```
✅ No escaping needed, readable, maintainable

#### Gotcha #2: macOS vs Linux sed Differences
**From PRP lines 254-269**: macOS requires different syntax than Linux
**Implementation**: Used `-i.bak` syntax (cross-platform compatible):
```bash
sed -i.bak 's|pattern|replacement|g' file.sh
```
✅ Works on both macOS (BSD sed) and Linux (GNU sed)

#### Gotcha #3: Incomplete Path Updates
**From PRP lines 299-307**: Missing unquoted path references
**Implementation**: Added 4th pass for unquoted paths:
```bash
# Catch both quoted and unquoted references
find .codex/tests -name "*.sh" -exec sed -i.bak 's|scripts/codex/|.codex/scripts/|g' {} \;
```
✅ Comprehensive coverage, no missed references

#### Gotcha #4: BASH_SOURCE Pattern Preservation
**From PRP lines 272-285**: Scripts use `${BASH_SOURCE[0]}` for sourcing
**Implementation**: No code changes needed - pattern is move-resilient
✅ Scripts use directory-relative sourcing, works after move

## Dependencies Verified

### Completed Dependencies:
- **Task 3**: Move Script Files - All scripts moved to `.codex/scripts/` ✅
- **Task 4**: Move Test Files - All tests moved to `.codex/tests/` ✅
- **Task 5**: Move Fixtures Directory - Fixtures moved to `.codex/tests/fixtures/` ✅

All dependencies were completed before this task, enabling path reference updates.

### External Dependencies:
- **bash**: Required for syntax validation (`bash -n`)
- **sed**: Required for path replacements (BSD/GNU compatible syntax used)
- **find**: Required for batch file operations
- **grep**: Required for verification

## Testing Checklist

### Manual Testing:
✅ Path reference updates verified with grep
✅ Backup files created during update process
✅ Backup files removed after successful verification
✅ All files readable and executable

### Validation Results:

#### Validation 1: Zero instances of "scripts/codex/" in test files
```bash
grep -r "scripts/codex/" .codex/tests/*.sh
# Result: No matches found
```
**Status**: ✅ PASS

#### Validation 2: Zero instances of "tests/codex/" in test files
```bash
grep -r "tests/codex/" .codex/tests/*.sh
# Result: No matches found
```
**Status**: ✅ PASS

#### Validation 3: All tests have valid bash syntax
```bash
bash -n .codex/tests/test_generate_prp.sh
bash -n .codex/tests/test_parallel_timing.sh
bash -n .codex/tests/test_execute_prp.sh
# Result: All pass with no errors
```
**Status**: ✅ PASS

## Success Metrics

**All PRP Requirements Met**:
- ✅ All ${REPO_ROOT}/scripts/codex/ references updated to ${REPO_ROOT}/.codex/scripts/
- ✅ All ${REPO_ROOT}/tests/codex/ references updated to ${REPO_ROOT}/.codex/tests/
- ✅ All unquoted path references updated (header comments)
- ✅ Zero old path references remain in test files
- ✅ All test files pass bash syntax validation
- ✅ Backup files created and cleaned up after verification
- ✅ Changes committed to git with descriptive message

**Code Quality**:
- ✅ Cross-platform sed syntax (works on macOS and Linux)
- ✅ Safe backup strategy (`.bak` files created first)
- ✅ Comprehensive verification before cleanup
- ✅ Pattern-following implementation (from path_update_sed_pattern.sh)
- ✅ All gotchas from PRP addressed
- ✅ No syntax errors introduced
- ✅ Git history preserved (separate commit from file moves)

## Completion Report

**Status**: COMPLETE - Ready for next task
**Implementation Time**: ~10 minutes (already completed in previous execution)
**Confidence Level**: HIGH
**Blockers**: None

### Files Created: 0
### Files Modified: 3
- .codex/tests/test_generate_prp.sh (24 path references updated)
- .codex/tests/test_parallel_timing.sh (8 path references updated)
- .codex/tests/test_execute_prp.sh (20 path references updated)

### Total Lines of Code: ~52 lines changed (path references)

**Git Commit**: 011e413 "Update: Documentation paths"
- This commit included both documentation updates (Task 7) and test file path updates (Task 6)
- Total: 69 insertions(+), 69 deletions(-)
- All path references updated in single comprehensive commit

## Key Insights

### What Worked Well:
1. **Pipe delimiter pattern**: Using `|` in sed avoided all escaping issues
2. **Backup strategy**: Creating `.bak` files enabled safe rollback if needed
3. **Comprehensive grep verification**: Caught all old path references
4. **Batch processing**: Using `find -exec` updated all files consistently

### Pattern Reusability:
This implementation followed the pattern from `path_update_sed_pattern.sh`:
- Dry run → backup → update → verify → cleanup workflow
- Cross-platform sed syntax
- Comprehensive coverage (quoted and unquoted paths)
- Verification before finalizing

The pattern is highly reusable for any future path migration tasks.

### Integration Notes:
Task 6 was completed as part of the same commit as Task 7 (Update Documentation Examples), which was efficient since both tasks involved path reference updates. The separation of file moves (Tasks 3-5) from content changes (Tasks 6-7) ensured git history preservation as specified in the PRP.

**Ready for integration and next steps.**
