# Feature Analysis: Codex Directory Reorganization

## INITIAL.md Summary

This feature reorganizes Codex-related files from scattered root directories (`scripts/codex/`, `tests/codex/`) into a unified `.codex/` structure. The goal is to consolidate all Codex files into one logical location for better organization, cleaner root directories, and easier maintenance. This involves moving 10 files (7 scripts, 3 tests, 1 fixtures directory) while preserving git history, updating path references, and maintaining full functionality.

---

## Core Requirements

### Explicit Requirements

1. **File Moves** (10 files total):
   - Move 7 files from `scripts/codex/` to `.codex/scripts/`
   - Move 3 files from `tests/codex/` to `.codex/tests/`
   - Move `tests/codex/fixtures/` directory to `.codex/tests/fixtures/`

2. **Git History Preservation**:
   - Use `git mv` commands (not `rm` + `add`)
   - Preserve all commit history for moved files
   - Maintain file permissions (executable bits)

3. **Path Reference Updates**:
   - Update script sourcing paths (scripts that source other scripts)
   - Update test file references (tests that call scripts)
   - Update documentation examples (README files)

4. **Documentation Updates**:
   - Update `.codex/README.md` with new paths
   - Update `.codex/scripts/README.md` with new structure
   - Ensure all examples reflect new locations

5. **Validation Requirements**:
   - All scripts must pass `bash -n` syntax check
   - All tests must run successfully after moves
   - No broken references to old paths
   - Functionality preserved 100%

### Implicit Requirements

1. **Directory Structure**:
   - Create `.codex/scripts/` directory if not exists
   - Create `.codex/tests/` directory if not exists
   - Remove empty `scripts/codex/` and `tests/codex/` after moves

2. **Atomic Operation**:
   - All moves should succeed or fail together
   - Rollback strategy if any validation fails
   - Maintain working state throughout migration

3. **Testing Strategy**:
   - Run tests before migration (baseline)
   - Run tests after migration (validation)
   - Compare results to ensure no regressions

4. **Path Resolution**:
   - Scripts using `$(dirname "${BASH_SOURCE[0]}")` need review
   - Tests using `${REPO_ROOT}` pattern need updates
   - Relative vs absolute path considerations

---

## Technical Components

### Data Models

**File Mapping Structure**:
```bash
# Source → Destination mapping
declare -A FILE_MOVES=(
    ["scripts/codex/security-validation.sh"]=".codex/scripts/security-validation.sh"
    ["scripts/codex/parallel-exec.sh"]=".codex/scripts/parallel-exec.sh"
    ["scripts/codex/codex-generate-prp.sh"]=".codex/scripts/codex-generate-prp.sh"
    ["scripts/codex/codex-execute-prp.sh"]=".codex/scripts/codex-execute-prp.sh"
    ["scripts/codex/quality-gate.sh"]=".codex/scripts/quality-gate.sh"
    ["scripts/codex/log-phase.sh"]=".codex/scripts/log-phase.sh"
    ["scripts/codex/README.md"]=".codex/scripts/README.md"
    ["scripts/codex/validate-config.sh"]=".codex/scripts/validate-config.sh"
    ["scripts/codex/validate-bootstrap.sh"]=".codex/scripts/validate-bootstrap.sh"
    ["tests/codex/test_generate_prp.sh"]=".codex/tests/test_generate_prp.sh"
    ["tests/codex/test_parallel_timing.sh"]=".codex/tests/test_parallel_timing.sh"
    ["tests/codex/test_execute_prp.sh"]=".codex/tests/test_execute_prp.sh"
    ["tests/codex/fixtures"]=".codex/tests/fixtures"
)
```

**Path Update Patterns**:
```bash
# Test files: Update REPO_ROOT-based paths
OLD_PATTERN: "${REPO_ROOT}/scripts/codex/codex-generate-prp.sh"
NEW_PATTERN: "${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

# Script files: Sourcing pattern (stays the same within same dir)
CURRENT: source "${script_dir}/log-phase.sh"
AFTER_MOVE: source "${script_dir}/log-phase.sh"  # No change (same dir)
```

### External Integrations

**Git Operations**:
- `git mv` for each file/directory move
- `git status` to verify staged changes
- `git commit` with descriptive message
- No external git APIs needed

**Bash Validation**:
- `bash -n <script>` for syntax validation
- Test harness execution for functional validation
- No external validation tools needed

**File System Operations**:
- Directory creation (`mkdir -p`)
- Path resolution (`realpath`, `dirname`)
- File permission preservation (automatic with `git mv`)

### Core Logic

**Migration Algorithm**:
```bash
1. Pre-migration validation:
   - Verify all source files exist
   - Run baseline tests (capture results)
   - Check git working tree is clean

2. Directory setup:
   - Create .codex/scripts/ (if not exists)
   - Create .codex/tests/ (if not exists)

3. File moves (in order):
   - Move scripts first (preserve dependencies)
   - Move tests second (they depend on scripts)
   - Move fixtures last (data only)

4. Path updates:
   - Update test files (search/replace scripts/codex → .codex/scripts)
   - Update test files (search/replace tests/codex → .codex/tests)
   - Verify no lingering old paths

5. Documentation updates:
   - Update .codex/README.md examples
   - Update .codex/scripts/README.md paths
   - Search for any other references

6. Post-migration validation:
   - Run bash -n on all moved scripts
   - Run all tests (compare to baseline)
   - Verify no broken references

7. Cleanup:
   - Remove empty scripts/codex/ directory
   - Remove empty tests/codex/ directory
   - Commit all changes with descriptive message
```

**Path Reference Detection**:
```bash
# Patterns to search for:
1. "scripts/codex/" in any file
2. "tests/codex/" in any file
3. "${REPO_ROOT}/scripts/codex/"
4. "${script_dir}/../" (relative navigation)
5. Documentation examples with old paths
```

**Rollback Strategy**:
```bash
# If validation fails after moves:
1. git reset --hard HEAD  # Undo all changes
2. Report which validation failed
3. Exit with error code
```

### UI/CLI Requirements

**Terminal Output**:
- Progress indicators for each move
- Color-coded success/failure messages
- Summary report at end
- Clear error messages with context

**Interactive Elements** (optional):
- Confirmation prompt before starting
- Pause/review after path updates
- Manual verification option

**Logging**:
- Log all operations to migration log file
- Record all path changes
- Capture validation results

---

## Similar Implementations Found in Archon

### 1. Git Configuration Updates
- **Relevance**: 4/10
- **Archon ID**: e9eb05e2bf38f125
- **Key Patterns**:
  - Git operations for configuration changes
  - Commit message patterns for infrastructure changes
- **Gotchas**:
  - Not directly about file moves, but shows git workflow patterns

### 2. Context Engineering PRP Patterns
- **Relevance**: 6/10
- **Archon ID**: b8565aff9938938b
- **Key Patterns**:
  - Documentation structure for feature requirements
  - Path reference patterns in configuration files
- **Gotchas**:
  - Emphasized importance of updating all references
  - Showed file path documentation patterns

### 3. Pydantic AI Examples
- **Relevance**: 3/10
- **Archon ID**: c0e629a894699314
- **Key Patterns**:
  - Path resolution in Python (analogous to bash)
  - File persistence patterns
- **Gotchas**:
  - Different language but similar path resolution concerns

**Note**: Archon search yielded limited directly relevant results for bash script reorganization. Most patterns are general git/path management principles. This indicates we should rely heavily on:
1. Git best practices for `git mv` operations
2. Bash scripting patterns already in codebase
3. Test-driven validation approach

---

## Recommended Technology Stack

**Core Technologies** (already in use):
- **Shell**: Bash 4.0+ (for associative arrays in migration script)
- **Version Control**: Git (for history-preserving moves)
- **Validation**: bash -n (syntax), existing test suite (functional)

**Migration Script Structure**:
- Single migration script: `scripts/migrate_codex_to_dotcodex.sh`
- Use existing patterns from `scripts/codex/` scripts
- Leverage existing validation functions

**No New Dependencies**:
- Everything needed is already in codebase
- Reuse existing validation patterns
- Standard bash utilities only

---

## Assumptions Made

### 1. **Directory Creation Safety**
   - **Assumption**: `.codex/scripts/` and `.codex/tests/` directories either don't exist or are empty
   - **Reasoning**: INITIAL.md shows these as new directories to create
   - **Source**: INITIAL.md desired end state structure
   - **Validation**: Migration script will check and create only if needed

### 2. **Script Sourcing Pattern Stability**
   - **Assumption**: Scripts using `$(dirname "${BASH_SOURCE[0]}")` pattern will work unchanged within same directory
   - **Reasoning**: Pattern is directory-relative, moves keep scripts in same dir relative to each other
   - **Source**: Analysis of `parallel-exec.sh` (lines 118, 303) showing this pattern
   - **Evidence**: After move, all scripts still in same directory (`.codex/scripts/`)

### 3. **Test Path Update Pattern**
   - **Assumption**: All test files use `${REPO_ROOT}/scripts/codex/` pattern consistently
   - **Reasoning**: Grep results show this pattern used in all test files
   - **Source**: Grep search showing 20+ instances of this exact pattern
   - **Validation**: Search/replace on this pattern will catch all references

### 4. **Git Working Tree State**
   - **Assumption**: Working tree is clean before migration (no uncommitted changes)
   - **Reasoning**: Best practice for structural changes, prevents merge conflicts
   - **Source**: Standard git workflow practices
   - **Validation**: Migration script will check `git status` first

### 5. **File Permissions**
   - **Assumption**: `git mv` preserves executable bits on .sh files
   - **Reasoning**: This is standard git behavior
   - **Source**: Git documentation
   - **Validation**: Post-migration check will verify executability

### 6. **Test Baseline Availability**
   - **Assumption**: All tests currently pass (or we know their current state)
   - **Reasoning**: Need baseline to compare post-migration results
   - **Source**: INITIAL.md mentions "All tests run successfully with new paths"
   - **Validation**: Run tests before migration to capture baseline

### 7. **Documentation Completeness**
   - **Assumption**: Only `.codex/README.md` and `.codex/scripts/README.md` contain path examples
   - **Reasoning**: These are the main user-facing docs mentioned in INITIAL.md
   - **Source**: INITIAL.md section "Documentation Updates"
   - **Validation**: Grep search for `scripts/codex` pattern will reveal all references

### 8. **Rollback Simplicity**
   - **Assumption**: `git reset --hard` is acceptable rollback if migration fails
   - **Reasoning**: Structural change should be atomic (all or nothing)
   - **Source**: Best practice for infrastructure changes
   - **Validation**: User will be warned before migration starts

### 9. **No External References**
   - **Assumption**: No files outside the repo reference `scripts/codex/` paths
   - **Reasoning**: Codex system is self-contained within this repo
   - **Source**: INITIAL.md description of self-contained system
   - **Validation**: Only internal references need updating

### 10. **Parallel Execution Not Running**
   - **Assumption**: No PRP generation/execution is running during migration
   - **Reasoning**: Moving files while scripts are running would cause failures
   - **Source**: Common sense for file system operations
   - **Validation**: Migration script will warn user to ensure no processes running

---

## Success Criteria

**From INITIAL.md (verbatim)**:

1. **Organization**:
   - All Codex scripts in `.codex/scripts/` (9 files total including validate-*.sh)
   - All Codex tests in `.codex/tests/` (3 files + fixtures)
   - Root `scripts/codex/` and `tests/codex/` directories removed
   - `.codex/` directory is self-contained and complete

2. **Functionality**:
   - All script sourcing works (relative paths correct)
   - All tests run successfully with new paths
   - All documentation examples updated and accurate
   - Git history preserved for all moved files

3. **Validation**:
   - `bash -n .codex/scripts/*.sh` - All scripts have valid syntax
   - `.codex/tests/test_*.sh` - All tests pass
   - Examples in `.codex/README.md` work correctly
   - No broken references to old paths

**Additional Measurable Outcomes**:

4. **Git History Verification**:
   - `git log --follow .codex/scripts/parallel-exec.sh` shows full history
   - All files show proper "renamed from" in git log
   - No history loss for any moved file

5. **Path Reference Completeness**:
   - `grep -r "scripts/codex" .` returns only intended references (if any)
   - `grep -r "tests/codex" .` returns only intended references (if any)
   - Zero broken symlinks or references

6. **Documentation Accuracy**:
   - All command examples in `.codex/README.md` are executable
   - All path references in `.codex/scripts/README.md` are accurate
   - Dependency graphs updated to show new structure

**Validation Commands**:
```bash
# Syntax validation
for script in .codex/scripts/*.sh; do
    bash -n "$script" || echo "FAIL: $script"
done

# Functional validation
.codex/tests/test_generate_prp.sh
.codex/tests/test_parallel_timing.sh
.codex/tests/test_execute_prp.sh

# Path reference check
grep -r "scripts/codex" . --exclude-dir=.git
grep -r "tests/codex" . --exclude-dir=.git

# Git history verification
git log --follow .codex/scripts/codex-generate-prp.sh | head -20

# Directory cleanup verification
[ ! -d "scripts/codex" ] && echo "✅ scripts/codex removed"
[ ! -d "tests/codex" ] && echo "✅ tests/codex removed"
```

---

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus Areas**:
1. **Path Reference Patterns**:
   - Find all instances of `scripts/codex/` in codebase (expect: test files, docs)
   - Find all instances of `tests/codex/` in codebase (expect: minimal)
   - Identify any unexpected references (hidden in comments, configs)

2. **Sourcing Patterns**:
   - Analyze all `source` statements in `scripts/codex/*.sh`
   - Verify they use `${script_dir}/` pattern (directory-relative)
   - Check for any absolute path references

3. **Test Dependencies**:
   - Map which tests depend on which scripts
   - Identify test execution order requirements
   - Find any hardcoded paths in test fixtures

4. **Documentation References**:
   - Find all files mentioning `scripts/codex` or `tests/codex`
   - Identify which are user-facing vs internal
   - Prioritize docs that need updates

**Output Expected**: Complete list of files requiring updates, categorized by type (test, doc, config)

### Documentation Hunter
**Focus Areas**:
1. **User-Facing Documentation**:
   - `.codex/README.md` - main user guide (KNOWN - needs update)
   - `.codex/scripts/README.md` - technical docs (KNOWN - needs update)
   - Any other markdown files referencing old paths

2. **Code Comments**:
   - Comments in scripts referencing file locations
   - Header comments with path information
   - TODO/FIXME comments mentioning paths

3. **Example Code**:
   - Shell script examples in docs
   - Copy-paste command snippets
   - Troubleshooting sections with paths

**Output Expected**: Comprehensive list of documentation updates needed, with old → new path mappings

### Example Curator
**Focus Areas**:
1. **Migration Script Examples**:
   - Find bash migration scripts (file moves, git operations)
   - Extract patterns for safe file moves
   - Identify validation techniques used in similar scripts

2. **Path Update Patterns**:
   - Find sed/awk examples for bulk path updates
   - Extract safe search/replace patterns
   - Identify edge cases in path replacements

3. **Git History Preservation**:
   - Find examples of `git mv` usage
   - Extract patterns for moving directories
   - Identify verification techniques for history preservation

4. **Test Validation Patterns**:
   - Find before/after test comparison examples
   - Extract diff analysis patterns
   - Identify regression detection techniques

**Output Expected**: Code snippets demonstrating proven patterns for each migration step

### Gotcha Detective
**Focus Areas**:
1. **Git Operation Gotchas**:
   - `git mv` failures (locked files, permissions)
   - History loss scenarios (wrong commands)
   - Merge conflict potential (concurrent changes)
   - Staging area issues (partial commits)

2. **Path Resolution Gotchas**:
   - Relative vs absolute path confusion
   - `$(dirname)` behavior changes
   - Symlink issues (if any exist)
   - Path escaping in sed/awk

3. **Test Execution Gotchas**:
   - Working directory assumptions
   - Environment variable dependencies
   - Test isolation failures
   - Race conditions in parallel tests

4. **Bash Scripting Gotchas**:
   - Array handling in path lists
   - Quoting issues in path variables
   - Exit code handling in loops
   - Error propagation in sourced scripts

5. **Documentation Update Gotchas**:
   - Markdown link breakage
   - Code block path references
   - Hidden path references (collapsed sections)
   - Version-specific documentation

**Output Expected**: Comprehensive list of potential pitfalls with mitigation strategies

---

## Risk Assessment

**Low Risk Areas** (from INITIAL.md):
- Simple file moves with `git mv` ✅
- All files self-contained (no external dependencies beyond repo) ✅
- Comprehensive test suite to validate ✅

**Medium Risk Areas** (from INITIAL.md + analysis):
- Path references in scripts (mitigated by systematic search/replace) ⚠️
- Documentation accuracy (mitigated by verification of all examples) ⚠️
- **Additional**: Test file updates (20+ references to update) ⚠️
- **Additional**: Parallel script sourcing (must verify relative paths work) ⚠️

**Newly Identified Risks**:
1. **Concurrent Execution Risk** - If PRP generation running during migration:
   - Mitigation: Check for running processes, warn user
   - Validation: `ps aux | grep codex-generate-prp`

2. **Incomplete Path Updates** - Missing a reference:
   - Mitigation: Comprehensive grep search, test execution validation
   - Validation: Run all tests, check for import errors

3. **Git History Verification** - Silently losing history:
   - Mitigation: Post-migration git log check for each file
   - Validation: Automated check with `git log --follow`

4. **Documentation Drift** - Docs updated but examples broken:
   - Mitigation: Test all documented commands
   - Validation: Automated execution of example snippets

**Overall Risk Level**: LOW-MEDIUM
- Well-defined scope (10 files)
- Strong test coverage (3 integration tests)
- Reversible operation (git reset)
- No data loss risk (files moved, not deleted)

---

## Migration Strategy Summary

**Three-Phase Approach**:

**Phase 1: Preparation** (5 minutes)
- Verify git working tree clean
- Run baseline tests (capture results)
- Create target directories
- Backup current state (git tag or branch)

**Phase 2: Migration** (10 minutes)
- Execute file moves with `git mv`
- Update path references in test files
- Update path references in documentation
- Verify syntax with `bash -n`

**Phase 3: Validation** (10 minutes)
- Run all tests (compare to baseline)
- Verify git history with `git log --follow`
- Check for lingering old path references
- Cleanup empty directories
- Commit changes

**Total Estimated Time**: 25 minutes
**Rollback Time**: < 1 minute (git reset)

**Confidence Level**: HIGH
- Clear requirements ✅
- Comprehensive validation strategy ✅
- Known patterns from codebase ✅
- Reversible operations ✅
- No external dependencies ✅

---

## Implementation Notes

### File Move Order (Critical)
Move files in dependency order to avoid breaking mid-migration:
1. Scripts with no dependencies first (security-validation.sh, validate-*.sh)
2. Scripts that source others (parallel-exec.sh, quality-gate.sh, log-phase.sh)
3. Main orchestrators (codex-generate-prp.sh, codex-execute-prp.sh)
4. Tests last (they depend on all scripts)
5. Fixtures last (data only, no code dependencies)

### Path Update Strategy
**Test Files** (bulk update via sed):
```bash
# Pattern: ${REPO_ROOT}/scripts/codex/ → ${REPO_ROOT}/.codex/scripts/
# Pattern: ${REPO_ROOT}/tests/codex/ → ${REPO_ROOT}/.codex/tests/
find .codex/tests -name "*.sh" -exec sed -i '' \
    's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' {} \;
find .codex/tests -name "*.sh" -exec sed -i '' \
    's|${REPO_ROOT}/tests/codex/|${REPO_ROOT}/.codex/tests/|g' {} \;
```

**Documentation Files** (manual review + update):
- `.codex/README.md`: Update all example commands
- `.codex/scripts/README.md`: Update all path references, dependency graphs

### Critical Validations
1. **Before migration**: Capture test results, git status
2. **After file moves**: Verify all files present in new locations
3. **After path updates**: Run bash -n on all scripts
4. **After all changes**: Run complete test suite
5. **Before commit**: Final grep check for old paths

### Success Indicators
- ✅ All tests pass (same results as baseline)
- ✅ All scripts pass bash -n syntax check
- ✅ Zero grep results for "scripts/codex" or "tests/codex" (excluding docs/comments)
- ✅ Git log --follow shows full history for all moved files
- ✅ Empty source directories removed
- ✅ All documentation examples executable

**This analysis provides complete foundation for PRP generation. Downstream agents have clear direction on what to research, which patterns to extract, and which gotchas to investigate.**
