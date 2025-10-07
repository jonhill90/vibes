# INITIAL: Cleanup execution_reliability Artifacts & Update References

**Created**: 2025-10-07
**Type**: Post-Execution Cleanup
**Priority**: HIGH (blocks clean slate for future PRPs)
**Estimated Time**: 30-45 minutes

---

## Goal

Clean up naming inconsistencies and misplaced files from the `prp_execution_reliability` PRP execution. Consolidate all artifacts under `prps/execution_reliability/`, update all references in documentation to reflect the correct (non-redundant) naming convention, and establish clear template location guidelines.

**End State**:
- Single directory: `prps/execution_reliability/` (consolidated)
- All documentation references updated to `execution_reliability`
- Test script moved to proper location
- Clear template location documentation (`.claude/templates/` vs `prps/templates/`)
- No orphaned files in root directory

---

## Why

**Current Pain Points**:
1. **Split directories**: `prps/prp_execution_reliability/` and `prps/execution_reliability/` cause confusion
2. **Redundant naming**: `prp_execution_reliability` has redundant `prp_` prefix (already in `prps/` directory)
3. **Misplaced test script**: `test_validation_gates_script.py` in root (should be in tests/ or with test PRP)
4. **Template confusion**: Two template locations (`.claude/templates/` vs `prps/templates/`) without clear documentation
5. **Inconsistent references**: PRP documentation uses old `prp_execution_reliability` naming

**Business Value**:
- Clean directory structure for future PRPs
- Consistent naming convention (no `prp_` redundancy)
- Clear template location guidelines
- Easier to find artifacts (single location)
- Better context for iterating on this feature

---

## What

### Core Tasks

1. **Consolidate Directories**
   - Move `prps/prp_execution_reliability/examples/` → `prps/execution_reliability/examples/`
   - Move `prps/prp_execution_reliability/planning/` → `prps/execution_reliability/planning/`
   - Move `prps/prp_execution_reliability/execution/TASK8_TEST_RESULTS.md` → `prps/execution_reliability/execution/`
   - Delete empty `prps/prp_execution_reliability/` directory
   - Verify no broken references

2. **Rename PRP File**
   - Rename `prps/prp_execution_reliability.md` → `prps/execution_reliability.md`
   - Update Archon project reference (if needed)
   - Update any git history references (optional)

3. **Update All Documentation References**
   - Update `prps/execution_reliability.md` (the PRP itself):
     - Replace all `prp_execution_reliability` → `execution_reliability`
     - Update file paths in "All Needed Context"
     - Update example paths in "Implementation Blueprint"
   - Update all TASK*_COMPLETION.md reports:
     - Fix any references to `prp_execution_reliability`
   - Update EXECUTION_SUMMARY.md:
     - Fix feature name references
     - Update file paths

4. **Move Test Script to Proper Location**
   - Move `test_validation_gates_script.py` → `prps/test_validation_gates/test_script.py`
   - OR move to `tests/validation/test_validation_gates.py` (if tests/ directory exists)
   - Update any references in TASK8_COMPLETION.md

5. **Document Template Locations**
   - Create `.claude/templates/README.md` explaining:
     - `.claude/templates/` = PRP execution report templates (task-completion, test-generation, validation)
     - `prps/templates/` = PRP generation templates (prp_base.md, feature_template.md, etc.)
     - When to use which location
   - Update CLAUDE.md to reference template locations

### Success Criteria

- [ ] All artifacts under single directory: `prps/execution_reliability/`
- [ ] PRP file renamed: `prps/execution_reliability.md` (no `prp_` prefix)
- [ ] All documentation uses `execution_reliability` (not `prp_execution_reliability`)
- [ ] Test script moved to appropriate location (not in root)
- [ ] Template locations documented in `.claude/templates/README.md`
- [ ] No broken references (all file paths work)
- [ ] `find . -name "*prp_execution_reliability*"` returns only historical git commits

---

## Tasks

```yaml
Task 1: Consolidate Directory Structure
RESPONSIBILITY: Move all prp_execution_reliability/ contents to execution_reliability/
FILES TO MODIFY:
  - Directory: prps/prp_execution_reliability/ (delete after move)
  - Directory: prps/execution_reliability/ (consolidate into)
SPECIFIC STEPS:
  1. Verify prps/execution_reliability/execution/ has TASK1-8 completion reports
  2. Move prps/prp_execution_reliability/examples/ → prps/execution_reliability/examples/
  3. Move prps/prp_execution_reliability/planning/ → prps/execution_reliability/planning/
  4. Move prps/prp_execution_reliability/execution/TASK8_TEST_RESULTS.md → prps/execution_reliability/execution/
  5. Verify prps/prp_execution_reliability/ is empty
  6. Delete prps/prp_execution_reliability/ directory
  7. Verify all files accessible at new locations
VALIDATION:
  - prps/execution_reliability/ contains: examples/, planning/, execution/
  - prps/prp_execution_reliability/ does not exist
  - All files readable at new paths

Task 2: Rename PRP File
RESPONSIBILITY: Rename PRP to match non-redundant naming convention
FILES TO MODIFY:
  - prps/prp_execution_reliability.md → prps/execution_reliability.md
SPECIFIC STEPS:
  1. mv prps/prp_execution_reliability.md prps/execution_reliability.md
  2. Update PRP header "Generated Based On" if it references old name
  3. Check if Archon project reference needs updating (optional)
VALIDATION:
  - prps/execution_reliability.md exists
  - prps/prp_execution_reliability.md does not exist
  - File content intact (no corruption)

Task 3: Update PRP Documentation References
RESPONSIBILITY: Update all feature name references in PRP file
FILES TO MODIFY:
  - prps/execution_reliability.md
SPECIFIC STEPS:
  1. Read prps/execution_reliability.md
  2. Find all instances of "prp_execution_reliability"
  3. Replace with "execution_reliability" (preserve formatting)
  4. Update file paths in "All Needed Context" section:
     - /Users/jon/source/vibes/prps/prp_execution_reliability/examples/README.md
     - /Users/jon/source/vibes/prps/prp_execution_reliability/examples/*.md
     - /Users/jon/source/vibes/prps/prp_execution_reliability/examples/*.py
  5. Update paths in "Implementation Blueprint" task steps
  6. Verify markdown formatting preserved
VALIDATION:
  - No instances of "prp_execution_reliability" in PRP (except git references)
  - All file paths use execution_reliability
  - Markdown renders correctly

Task 4: Update Completion Report References
RESPONSIBILITY: Fix feature name in all TASK*_COMPLETION.md reports
FILES TO MODIFY:
  - prps/execution_reliability/execution/TASK1_COMPLETION.md
  - prps/execution_reliability/execution/TASK2_COMPLETION.md
  - prps/execution_reliability/execution/TASK3_COMPLETION.md
  - prps/execution_reliability/execution/TASK4_COMPLETION.md
  - prps/execution_reliability/execution/TASK5_COMPLETION.md
  - prps/execution_reliability/execution/TASK6_COMPLETION.md
  - prps/execution_reliability/execution/TASK7_COMPLETION.md
  - prps/execution_reliability/execution/TASK8_COMPLETION.md
SPECIFIC STEPS:
  1. For each TASK*_COMPLETION.md:
     - Find all "prp_execution_reliability" references
     - Replace with "execution_reliability"
     - Update file paths in examples/references
  2. Verify no broken links
VALIDATION:
  - All completion reports use "execution_reliability"
  - All file path references valid
  - No broken links or references

Task 5: Update Execution Summary
RESPONSIBILITY: Fix feature name and paths in EXECUTION_SUMMARY.md
FILES TO MODIFY:
  - prps/execution_reliability/execution/EXECUTION_SUMMARY.md
SPECIFIC STEPS:
  1. Read EXECUTION_SUMMARY.md
  2. Replace all "prp_execution_reliability" → "execution_reliability"
  3. Update file paths throughout document
  4. Update directory references in "Files Summary" section
VALIDATION:
  - Feature name is "execution_reliability" throughout
  - All paths reference execution_reliability/
  - Directory structure section accurate

Task 6: Move Test Script to Proper Location
RESPONSIBILITY: Relocate test script from root to appropriate directory
FILES TO MODIFY:
  - test_validation_gates_script.py (move from root)
  - prps/execution_reliability/execution/TASK8_COMPLETION.md (update reference)
SPECIFIC STEPS:
  1. Check if tests/ directory exists in project root
  2. If tests/ exists:
     - mv test_validation_gates_script.py tests/validation/test_validation_gates.py
     - Create tests/validation/ if needed
  3. If tests/ doesn't exist:
     - mv test_validation_gates_script.py prps/test_validation_gates/test_script.py
     - Create prps/test_validation_gates/ if needed
  4. Update reference in TASK8_COMPLETION.md to new path
VALIDATION:
  - test_validation_gates_script.py not in root
  - Script accessible at new location
  - TASK8_COMPLETION.md references correct path

Task 7: Document Template Locations
RESPONSIBILITY: Create clear documentation for template usage
FILES TO CREATE:
  - .claude/templates/README.md
FILES TO MODIFY:
  - CLAUDE.md (add template location reference)
SPECIFIC STEPS:
  1. Create .claude/templates/README.md:
     - Explain purpose of .claude/templates/ (execution report templates)
     - List templates: task-completion-report.md, test-generation-report.md, validation-report.md
     - Usage instructions (how to use in execute-prp.md)
     - When to add new templates here
  2. Explain prps/templates/ distinction:
     - Purpose: PRP generation templates (for /generate-prp)
     - List templates: prp_base.md, feature_template.md, documentation_template.md, tool_template.md
     - Usage: Only for /generate-prp workflow
  3. Update CLAUDE.md with template location section:
     - Add under "## Repository Overview" or new "## Template Locations" section
     - Link to .claude/templates/README.md
VALIDATION:
  - .claude/templates/README.md exists with clear distinction
  - CLAUDE.md references template locations
  - Documentation explains when to use each location

Task 8: Verify No Broken References
RESPONSIBILITY: Final validation that all moves/renames didn't break anything
FILES TO TEST:
  - All documentation files
  - All code references
SPECIFIC STEPS:
  1. grep -r "prp_execution_reliability" . --exclude-dir=.git
     - Should return 0 results (except git history)
  2. Test file paths from documentation:
     - Pick 5 random file paths from PRP/completion reports
     - Verify files exist at those paths
  3. Verify directory structure:
     - ls prps/execution_reliability/
     - Should show: examples/, planning/, execution/
  4. Verify test script accessible:
     - Check new location (tests/validation/ or prps/test_validation_gates/)
     - Run basic validation (python test_script.py --help or similar)
VALIDATION:
  - No instances of "prp_execution_reliability" in codebase (except git)
  - All file paths from docs resolve correctly
  - Directory structure matches expected layout
  - Test script runs from new location
```

---

## Validation Loop

### Level 1: File Operations
```bash
# Verify consolidation
ls prps/execution_reliability/
# Should show: examples/ planning/ execution/

# Verify no old directory
ls prps/prp_execution_reliability/ 2>&1
# Should error: No such file or directory

# Verify PRP renamed
ls prps/execution_reliability.md
# Should exist

# Verify test script moved
ls test_validation_gates_script.py 2>&1
# Should error: No such file or directory
```

### Level 2: Content Updates
```bash
# Check for old references in PRP
grep -c "prp_execution_reliability" prps/execution_reliability.md
# Should be: 0 (or very few, like in git references)

# Check for old references in completion reports
grep -r "prp_execution_reliability" prps/execution_reliability/execution/
# Should be: empty or minimal

# Verify paths in documentation
grep -r "/prps/execution_reliability/" prps/execution_reliability/
# Should find updated paths
```

### Level 3: Template Documentation
```bash
# Verify template README exists
cat .claude/templates/README.md
# Should explain .claude/templates/ vs prps/templates/

# Verify CLAUDE.md updated
grep -A 5 "Template Locations" CLAUDE.md
# Should reference template structure
```

---

## Success Metrics

### Quantitative
- 0 instances of "prp_execution_reliability" in docs (except git history)
- 1 directory: prps/execution_reliability/ (not 2)
- 0 files in root matching test_validation_gates_script.py
- 100% of file paths in docs resolve correctly

### Qualitative
- Clear understanding of which templates are where
- Easy to find all execution_reliability artifacts
- No confusion about naming conventions
- Clean slate for future PRPs

---

## Notes

**Why This Matters**:
- Sets precedent for future PRP naming (no redundant prefixes)
- Demonstrates proper cleanup after PRP execution
- Establishes clear template location conventions
- Improves developer experience (less confusion)

**Scope Boundaries**:
- Does NOT change execute-prp.md logic (that's Option B)
- Does NOT retroactively rename other PRPs
- Does NOT change /generate-prp behavior
- ONLY cleans up this specific PRP's artifacts

**Follow-up Work** (not in this PRP):
- Option B: Standardize naming convention across all PRPs
- Update /generate-prp to avoid "prp_" prefix
- Create linter to catch redundant prefixes

---

**Estimated Effort**: 30-45 minutes
**Risk Level**: LOW (mostly file moves and find/replace)
**Dependencies**: None (standalone cleanup)
