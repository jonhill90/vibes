# Task 3 Implementation Complete: Fix Critical Bug in generate-prp.md

## Task Information
- **Task ID**: N/A (Standalone PRP task)
- **Task Name**: Task 3 - Fix Critical Bug in generate-prp.md
- **Responsibility**: Fix same replace() bug in generate-prp command that affects prefix stripping logic
- **Status**: COMPLETE - Ready for Review

## Files Created/Modified

### Created Files:
None (modification only)

### Modified Files:
1. **`/Users/jon/source/vibes/.claude/commands/generate-prp.md`** (lines 24-38)
   - Fixed critical bug: Changed `feature.replace(strip_prefix, "")` to `feature.removeprefix(strip_prefix)`
   - Added comprehensive 4-line comment explaining the rationale
   - Comment references PEP 616 for official documentation

## Implementation Details

### Core Features Implemented

#### 1. Critical Bug Fix
- **Issue**: Line 28 used `.replace()` which removes ALL occurrences of the prefix string
- **Solution**: Changed to `.removeprefix()` which only removes from the start
- **Impact**: Prevents incorrect behavior when feature names coincidentally contain the prefix string

#### 2. Documentation
- Added 4-line comment block explaining:
  - What the bug was (replace removes ALL occurrences)
  - What the fix does (removeprefix only strips leading prefix)
  - Example edge case: "INITIAL_INITIAL_test" -> "INITIAL_test" (correct) vs "test" (bug)
  - Reference to PEP 616 for official rationale

### Critical Gotchas Addressed

#### Gotcha #1: String replace() vs removeprefix()
**From PRP Section**: Known Gotchas, lines 260-289

**Implementation**:
```python
# OLD (line 28): feature = feature.replace(strip_prefix, "")
# NEW (line 32): feature = feature.removeprefix(strip_prefix)
```

**Why This Matters**:
- `replace()` replaces ALL occurrences: "INITIAL_INITIAL_test" -> "test" (WRONG)
- `removeprefix()` only removes leading prefix: "INITIAL_INITIAL_test" -> "INITIAL_test" (CORRECT)
- Edge case example from PRP: if feature name contains prefix string multiple times, ALL would be removed

#### Gotcha #2: lstrip() is NOT prefix removal
**From PRP Section**: Known Gotchas, lines 313-330

**Avoided**: Did NOT use `lstrip()` which removes CHARACTERS (not substring)
- `lstrip("INITIAL_")` would remove any combo of I, N, T, A, L, _ characters
- Example: "LLLLL_test".lstrip("INITIAL_") -> "test" (removes all L's)
- Used `removeprefix()` instead which treats prefix as complete substring

## Dependencies Verified

### Completed Dependencies:
- Task 2 (Fix execute-prp.md): Used same pattern and solution approach
- Pattern file: `prps/standardize_prp_naming_convention/examples/filename_extraction_logic.py` (Solution 1, lines 60-90)
- PEP 616 documentation: Confirmed `removeprefix()` is the correct Python 3.9+ solution

### External Dependencies:
- Python 3.9+: Required for `str.removeprefix()` method
- No additional libraries needed (built-in string method)

## Testing Checklist

### Validation Results:

**1. grep verification - No more replace(strip_prefix)**
```bash
grep -n "\.replace(strip_prefix" .claude/commands/generate-prp.md
# Output: (empty) - No matches found ✓
```

**2. grep verification - removeprefix now used**
```bash
grep -n "removeprefix(strip_prefix)" .claude/commands/generate-prp.md
# Output: 32:    if strip_prefix: feature = feature.removeprefix(strip_prefix) ✓
```

**3. Call site verification**
```bash
grep -n "extract_feature_name(initial_md_path" .claude/commands/generate-prp.md
# Output: 40:feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_") ✓
```

**All validation checks passed successfully.**

## Success Metrics

**All PRP Requirements Met**:
- [x] Located extract_feature_name() function (line 24)
- [x] Found the problematic line: `feature = feature.replace(strip_prefix, "")`
- [x] Replaced with: `feature = feature.removeprefix(strip_prefix)`
- [x] Added comment explaining why removeprefix is correct
- [x] Verified call site uses: `extract_feature_name(initial_md_path, strip_prefix="INITIAL_")`
- [x] Confirmed no auto-detection needed here (always strips INITIAL_)

**Code Quality**:
- Comprehensive 4-line comment explaining rationale
- Reference to PEP 616 for official documentation
- Inline examples showing edge case behavior
- Follows pattern from Task 2 (consistency across commands)
- No syntax errors introduced

## Completion Report

**Status**: COMPLETE - Ready for Review

**Implementation Time**: ~8 minutes

**Confidence Level**: HIGH

**Blockers**: None

### Files Created: 0
### Files Modified: 1
### Total Lines Changed: ~9 lines (5 lines added for comment + 1 line changed)

---

## Technical Details

### Before (Line 28):
```python
if strip_prefix: feature = feature.replace(strip_prefix, "")
```

### After (Lines 28-32):
```python
# CRITICAL: Use removeprefix() instead of replace() to only strip leading prefix
# replace() removes ALL occurrences (e.g., "INITIAL_INITIAL_test" -> "test")
# removeprefix() only removes from start (e.g., "INITIAL_INITIAL_test" -> "INITIAL_test")
# See: PEP 616 (https://peps.python.org/pep-0616/) for rationale
if strip_prefix: feature = feature.removeprefix(strip_prefix)
```

### Why This Fix Matters:

1. **Correctness**: Only removes prefix from start, not all occurrences
2. **Edge Case Safety**: Handles feature names like "INITIAL_INITIAL_test" correctly
3. **Predictability**: Behavior matches developer expectations (prefix stripping, not global replacement)
4. **Security**: More predictable behavior reduces potential for unexpected file path manipulations
5. **PEP Compliance**: Uses the officially recommended Python 3.9+ method for prefix removal

### Comparison with Task 2:

Task 2 (execute-prp.md) required:
- Same bug fix (replace -> removeprefix)
- PLUS auto-detection logic (detect INITIAL_ prefix before calling function)

Task 3 (generate-prp.md) required:
- Same bug fix (replace -> removeprefix)
- NO auto-detection needed (always strips INITIAL_ because we control the file creation)

Both tasks now use the same safe pattern for prefix stripping.

---

**Ready for validation and next steps.**

**Next Task**: Task 4 - Add 6th Validation Level (Redundant Prefix Check) to security-validation.md
