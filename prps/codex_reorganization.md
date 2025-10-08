# PRP: Codex Directory Reorganization

**Generated**: 2025-10-08
**Based On**: prps/INITIAL_codex_reorganization.md
**Archon Project**: 5636b60c-60b8-4789-91c7-5ed51c3a46b6

---

## Goal

Reorganize all Codex-related files from scattered root directories (`scripts/codex/`, `tests/codex/`) into a unified `.codex/` structure. This consolidates 10 files (7 scripts, 3 tests, 1 fixtures directory) into a single self-contained location while preserving complete git history and maintaining 100% functionality.

**End State**:
- All Codex scripts in `.codex/scripts/` (9 files including validation scripts)
- All Codex tests in `.codex/tests/` (3 test files + fixtures directory)
- Root `scripts/codex/` and `tests/codex/` directories removed
- Git history fully preserved for all moved files
- All tests pass with new paths
- Zero broken references to old paths

## Why

**Current Pain Points**:
- Codex files scattered across multiple root directories creates organizational confusion
- Root directories (`scripts/`, `tests/`) cluttered with feature-specific subdirectories
- `.codex/` directory exists but doesn't contain the Codex scripts/tests it logically should
- Inconsistent with other hidden tool directories (`.claude/`, `.github/`)
- Makes it harder to understand which files are Codex-specific infrastructure

**Business Value**:
- Cleaner repository structure improves developer experience
- Self-contained `.codex/` directory makes system boundaries clear
- Easier maintenance and onboarding (all related files in one place)
- Aligns with industry best practices for tool-specific directories
- Reduces cognitive load when navigating the codebase

## What

### Core Features

1. **File Relocation**: Move 10 files while preserving git history
   - 7 scripts: security-validation.sh, parallel-exec.sh, codex-generate-prp.sh, codex-execute-prp.sh, quality-gate.sh, log-phase.sh, README.md
   - 2 validation scripts: validate-config.sh, validate-bootstrap.sh
   - 3 test files: test_generate_prp.sh, test_parallel_timing.sh, test_execute_prp.sh
   - 1 fixtures directory with contents

2. **Path Reference Updates**: Update all references to moved files
   - Test files: 20+ instances of `${REPO_ROOT}/scripts/codex/` → `${REPO_ROOT}/.codex/scripts/`
   - Test files: References to `${REPO_ROOT}/tests/codex/` → `${REPO_ROOT}/.codex/tests/`
   - Documentation: Update examples in `.codex/README.md` and `.codex/scripts/README.md`

3. **Directory Cleanup**: Remove empty source directories
   - Delete `scripts/codex/` after verifying empty
   - Delete `tests/codex/` after verifying empty

4. **Validation**: Ensure complete migration success
   - All scripts pass `bash -n` syntax check
   - All tests execute successfully
   - Git history verified with `git log --follow`
   - Zero old path references remain

### Success Criteria

- [ ] All 10 files moved to `.codex/scripts/` or `.codex/tests/`
- [ ] Git history preserved: `git log --follow` shows full commit history for each file
- [ ] All scripts have valid syntax: `bash -n .codex/scripts/*.sh` succeeds
- [ ] All tests pass: `.codex/tests/test_*.sh` execute successfully
- [ ] No broken references: `grep -r "scripts/codex/"` returns zero results (excluding documentation)
- [ ] Old directories removed: `scripts/codex/` and `tests/codex/` no longer exist
- [ ] Documentation updated: All examples in `.codex/README.md` use new paths

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Git History Preservation
- url: https://git-scm.com/docs/git-mv
  sections:
    - "git mv command syntax" - Only way to preserve history
    - "Rename detection" - Understanding git's heuristics
  why: Core operation for all file moves, preserves blame and log
  critical_gotchas:
    - Never mix file moves with content changes in same commit
    - Git uses >50% similarity threshold for rename detection
    - Verify with `git log --follow` for each moved file

- url: https://git-scm.com/docs/git-log
  sections:
    - "--follow flag" - Tracking files through renames
  why: Required for verifying history preservation post-migration
  critical_gotchas:
    - Without --follow, history appears lost even when preserved
    - Only works for single files, not directories
    - Must be used explicitly (not default behavior)

# MUST READ - Bash Scripting Patterns
- url: https://stackoverflow.com/questions/59895/
  sections:
    - "BASH_SOURCE[0] vs $0" - Directory resolution for sourced scripts
  why: Scripts use this pattern to source dependencies
  critical_gotchas:
    - $0 returns "bash" when sourcing, BASH_SOURCE[0] always correct
    - Scripts in .codex/scripts/ source each other (must use BASH_SOURCE)
    - Pattern is move-resilient (no code changes needed)

- url: https://stackoverflow.com/questions/64786/
  sections:
    - "Bash error handling" - set -euo pipefail pattern
    - "Trap for cleanup" - Rollback on migration failure
  why: Migration script needs robust error handling
  critical_gotchas:
    - Use trap to rollback on any failure
    - set -e exits on first error (prevents partial migration)
    - set -u catches undefined variables early

# MUST READ - Path Updates with sed
- url: https://stackoverflow.com/questions/12061410/
  sections:
    - "Alternative delimiters" - Using | or # instead of /
  why: Updating 20+ path references in test files
  critical_gotchas:
    - Never use / delimiter with paths (escaping nightmare)
    - macOS sed requires -i '' (BSD), Linux uses -i (GNU)
    - Always create .bak files first for safety

# ESSENTIAL LOCAL FILES
- file: /Users/jon/source/vibes/prps/codex_reorganization/examples/git_mv_pattern.sh
  why: Complete git mv pattern with pre-flight validation
  pattern: Safe file move with source exists, dest doesn't exist, parent exists checks
  critical: Use pre-flight checks to prevent 90% of common errors

- file: /Users/jon/source/vibes/prps/codex_reorganization/examples/dirname_sourcing_pattern.sh
  why: Understanding what changes vs what doesn't after move
  pattern: Directory-relative sourcing with ${BASH_SOURCE[0]}
  critical: Scripts sourcing sibling files need NO changes (move-resilient)

- file: /Users/jon/source/vibes/prps/codex_reorganization/examples/path_update_sed_pattern.sh
  why: Bulk path update workflow with safety checks
  pattern: Dry run → backup → update → verify → cleanup
  critical: Use pipe delimiter in sed, create backups, verify before cleanup

- file: /Users/jon/source/vibes/prps/codex_reorganization/examples/bash_validation_pattern.sh
  why: Post-migration validation framework
  pattern: Syntax check, path reference verification, git history verification
  critical: Validate all success criteria before marking complete

- file: /Users/jon/source/vibes/prps/codex_reorganization/examples/README.md
  why: Integration guide showing what to mimic, adapt, or skip
  pattern: Usage instructions for all 4 code examples
  critical: REQUIRED READING before implementation (saves 2-3 hours)
```

### Current Codebase Tree

```
scripts/
└── codex/                    # WILL BE DELETED after move
    ├── security-validation.sh
    ├── parallel-exec.sh
    ├── codex-generate-prp.sh
    ├── codex-execute-prp.sh
    ├── quality-gate.sh
    ├── log-phase.sh
    ├── validate-config.sh
    ├── validate-bootstrap.sh
    └── README.md

tests/
└── codex/                    # WILL BE DELETED after move
    ├── test_generate_prp.sh
    ├── test_parallel_timing.sh
    ├── test_execute_prp.sh
    └── fixtures/             # Directory with test data
        └── (various test fixtures)

.codex/                       # EXISTS (has other files)
├── prompts/                  # Existing, not affected
├── commands/                 # Existing, not affected
└── patterns/                 # Existing, not affected
```

### Desired Codebase Tree

```
.codex/                       # CONSOLIDATED (all Codex files here)
├── scripts/                  # NEW - moved from scripts/codex/
│   ├── security-validation.sh
│   ├── parallel-exec.sh
│   ├── codex-generate-prp.sh
│   ├── codex-execute-prp.sh
│   ├── quality-gate.sh
│   ├── log-phase.sh
│   ├── validate-config.sh
│   ├── validate-bootstrap.sh
│   └── README.md
├── tests/                    # NEW - moved from tests/codex/
│   ├── test_generate_prp.sh
│   ├── test_parallel_timing.sh
│   ├── test_execute_prp.sh
│   └── fixtures/             # Moved with test files
│       └── (various test fixtures)
├── prompts/                  # Existing, not affected
├── commands/                 # Existing, not affected
└── patterns/                 # Existing, not affected

scripts/                      # CLEANED UP
└── (codex/ directory deleted)

tests/                        # CLEANED UP
└── (codex/ directory deleted)
```

**New Files**: None (pure reorganization, no new files created)

### Known Gotchas & Library Quirks

```bash
# CRITICAL: Git History Loss - Mixing Rename with Content Changes
# Source: https://stackoverflow.com/questions/10828267/

# ❌ WRONG - Move and modify in same commit (BREAKS HISTORY)
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
sed -i 's/old/new/' .codex/scripts/parallel-exec.sh  # Edit in same commit
git commit -m "Move and update parallel-exec.sh"
# Result: Git sees delete+create, NOT rename. History lost.

# ✅ RIGHT - Separate commits (PRESERVES HISTORY)
# Commit 1: Move only (no edits)
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
git commit -m "Move: parallel-exec.sh to .codex/scripts/"

# Commit 2: Content changes (separate)
sed -i 's/old/new/' .codex/scripts/parallel-exec.sh
git commit -am "Update: parallel-exec.sh references"

# Explanation: Git uses content hash matching to detect renames. Same content
# = same hash = rename detected. Different content = different hash = looks
# like delete+create. Keep moves and edits in separate commits.

# CRITICAL: sed Delimiter Conflicts - Slash in Paths
# Source: https://stackoverflow.com/questions/12061410/

# ❌ WRONG - Using / delimiter requires escaping (error-prone)
sed -i 's/scripts\/codex\//\.codex\/scripts\//g' test.sh
# Hard to read, easy to miss an escape

# ✅ RIGHT - Use pipe delimiter (no escaping needed)
sed -i 's|scripts/codex/|.codex/scripts/|g' test.sh
# Readable, maintainable, no escaping

# CRITICAL: macOS vs Linux sed Differences
# Source: https://stackoverflow.com/questions/4247068/

# ❌ WRONG - Linux syntax fails on macOS
sed -i 's|old|new|g' file.sh
# macOS error: "sed: 1: "file.sh": invalid command code"

# ❌ WRONG - macOS syntax behaves differently on Linux
sed -i '' 's|old|new|g' file.sh
# Linux creates backup files named '' (empty string)

# ✅ RIGHT - Cross-platform: Use backup extension
sed -i.bak 's|old|new|g' file.sh
# Works on both, creates .bak files for safety
# Verify changes, then: find . -name "*.bak" -delete

# CRITICAL: BASH_SOURCE vs $0 Confusion
# Source: https://stackoverflow.com/questions/59895/
# Source: scripts/codex/parallel-exec.sh line 118

# ❌ WRONG - Using $0 for sourced scripts
script_dir="$(cd "$(dirname "$0")" && pwd)"
source "${script_dir}/log-phase.sh"
# When executed: $0 = script name ✅
# When sourced: $0 = "bash" ❌ (fails to find dependencies)

# ✅ RIGHT - Always use BASH_SOURCE[0]
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/log-phase.sh"
# Works for both execution and sourcing
# Pattern already used in parallel-exec.sh, codex-generate-prp.sh
# NO CHANGES NEEDED - scripts will work after move

# CRITICAL: Forgetting --follow Flag
# Source: https://git-scm.com/docs/git-log

# ❌ WRONG - Viewing history without --follow
git log .codex/scripts/parallel-exec.sh
# Shows only post-move commits (appears history lost)

# ✅ RIGHT - Always use --follow for moved files
git log --follow .codex/scripts/parallel-exec.sh
# Shows complete history including before move

# CRITICAL: Incomplete Path Updates - Missing References
# Source: http://www.pixelbeat.org/programming/shell_script_mistakes.html

# ❌ WRONG - Only updating obvious files
find .codex/tests -name "*.sh" -exec sed -i 's|scripts/codex/|.codex/scripts/|g' {} \;
# Misses: documentation, comments, configuration files

# ✅ RIGHT - Comprehensive search across all file types
grep -r "scripts/codex/" . --exclude-dir=.git --exclude-dir=node_modules
# Then update ALL files found: code, docs, configs

# CRITICAL: Empty Directory Detection Misses Hidden Files
# Source: prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh

# ❌ WRONG - Simple check misses .DS_Store, .gitkeep
if [ -z "$(ls scripts/codex)" ]; then
    rmdir scripts/codex
fi

# ✅ RIGHT - Use find to catch hidden files
file_count=$(find scripts/codex -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')
if [ "$file_count" -ne 0 ]; then
    echo "❌ Directory not empty:"
    ls -la scripts/codex/
    exit 1
fi
rmdir scripts/codex  # Fails safely if not truly empty

# CRITICAL: Command Injection via Unvalidated Paths
# Source: https://www.akamai.com/blog/security-research/kubernetes-gitsync-command-injection-defcon

# ❌ VULNERABLE - Unquoted variables
git mv $SOURCE $DEST
# If SOURCE contains "; rm -rf /" this executes both commands

# ✅ SECURE - Quote all variables
git mv "$SOURCE" "$DEST"
# Prevents word splitting and command injection

# CRITICAL: Concurrent Execution During Migration
# Source: feature-analysis.md assumption #10

# Check for running Codex processes before migration
if pgrep -f "codex-generate-prp.sh" > /dev/null; then
    echo "❌ ERROR: PRP generation running, abort migration"
    exit 1
fi
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Study Examples Directory**:
   - **REQUIRED**: Read `prps/codex_reorganization/examples/README.md` completely
   - Study time: 15-20 minutes
   - Focus on "What to Mimic" sections (these are copy/paste patterns)
   - Understand "What to Adapt" (customize for Codex paths)
   - Note "What to Skip" (saves time)

2. **Review Current Scripts**:
   - Verify which scripts use BASH_SOURCE pattern: `grep -r 'BASH_SOURCE' scripts/codex/`
   - Identify test files needing updates: `grep -r 'REPO_ROOT' tests/codex/`
   - Count path references to update: `grep -r "scripts/codex/" tests/`

3. **Understand Git Gotchas**:
   - Why separate commits matter (history preservation)
   - Why --follow flag is required (post-verification)
   - Why sed needs pipe delimiter (path escaping)

### Task List (Execute in Order)

```yaml
Task 1: Pre-Migration Validation
RESPONSIBILITY: Ensure clean state before starting migration
FILES TO CHECK:
  - Git working tree status
  - Running Codex processes
  - Baseline test results

SPECIFIC STEPS:
  1. Check git status is clean: git diff-index --quiet HEAD --
  2. Check no Codex processes running: pgrep -f "codex-.*\.sh"
  3. Run baseline tests and capture results: .codex/tests/test_*.sh
  4. Create backup tag: git tag "codex-reorg-backup-$(date +%Y%m%d-%H%M%S)"

VALIDATION:
  - Git working tree clean (no uncommitted changes)
  - No running processes found
  - Baseline test results documented
  - Backup tag created

---

Task 2: Create Target Directory Structure
RESPONSIBILITY: Prepare destination directories for file moves
FILES TO CREATE:
  - .codex/scripts/ (if not exists)
  - .codex/tests/ (if not exists)

PATTERN TO FOLLOW: From git_mv_pattern.sh lines 127-136 (idempotent directory creation)

SPECIFIC STEPS:
  1. Create .codex/scripts: mkdir -p .codex/scripts
  2. Create .codex/tests: mkdir -p .codex/tests
  3. Verify directories exist: [ -d .codex/scripts ] && [ -d .codex/tests ]

VALIDATION:
  - .codex/scripts/ directory exists
  - .codex/tests/ directory exists
  - No errors during creation

---

Task 3: Move Script Files with Git History Preservation
RESPONSIBILITY: Relocate all 9 script files to .codex/scripts/ using git mv
FILES TO MOVE:
  - scripts/codex/security-validation.sh → .codex/scripts/security-validation.sh
  - scripts/codex/parallel-exec.sh → .codex/scripts/parallel-exec.sh
  - scripts/codex/codex-generate-prp.sh → .codex/scripts/codex-generate-prp.sh
  - scripts/codex/codex-execute-prp.sh → .codex/scripts/codex-execute-prp.sh
  - scripts/codex/quality-gate.sh → .codex/scripts/quality-gate.sh
  - scripts/codex/log-phase.sh → .codex/scripts/log-phase.sh
  - scripts/codex/validate-config.sh → .codex/scripts/validate-config.sh
  - scripts/codex/validate-bootstrap.sh → .codex/scripts/validate-bootstrap.sh
  - scripts/codex/README.md → .codex/scripts/README.md

PATTERN TO FOLLOW: From git_mv_pattern.sh lines 18-47 (pre-flight checks + git mv)

SPECIFIC STEPS:
  1. For each file:
     a. Verify source exists: [ -e "scripts/codex/${file}" ]
     b. Verify dest doesn't exist: [ ! -e ".codex/scripts/${file}" ]
     c. Execute git mv: git mv "scripts/codex/${file}" ".codex/scripts/${file}"
     d. Verify git status shows "renamed": git status | grep renamed
  2. Commit moves: git commit -m "Move: Codex scripts to .codex/scripts/"

VALIDATION:
  - All 9 files present in .codex/scripts/
  - git status shows "renamed:" for each file (NOT "deleted" + "new file")
  - Commit created with descriptive message

---

Task 4: Move Test Files with Git History Preservation
RESPONSIBILITY: Relocate all 3 test files to .codex/tests/ using git mv
FILES TO MOVE:
  - tests/codex/test_generate_prp.sh → .codex/tests/test_generate_prp.sh
  - tests/codex/test_parallel_timing.sh → .codex/tests/test_parallel_timing.sh
  - tests/codex/test_execute_prp.sh → .codex/tests/test_execute_prp.sh

PATTERN TO FOLLOW: Same as Task 3 (git_mv_pattern.sh)

SPECIFIC STEPS:
  1. For each test file:
     a. Verify source exists
     b. Verify dest doesn't exist
     c. Execute git mv
     d. Verify git status shows "renamed"
  2. Commit moves: git commit -m "Move: Codex tests to .codex/tests/"

VALIDATION:
  - All 3 test files present in .codex/tests/
  - git status shows "renamed:" for each file
  - Commit created with descriptive message

---

Task 5: Move Fixtures Directory
RESPONSIBILITY: Relocate test fixtures directory with all contents
FILES TO MOVE:
  - tests/codex/fixtures/ → .codex/tests/fixtures/

PATTERN TO FOLLOW: git_mv_pattern.sh directory move pattern

SPECIFIC STEPS:
  1. Verify source directory exists: [ -d tests/codex/fixtures ]
  2. Verify dest doesn't exist: [ ! -e .codex/tests/fixtures ]
  3. Execute git mv: git mv tests/codex/fixtures .codex/tests/fixtures
  4. Verify all fixture files moved
  5. Commit move: git commit -m "Move: Codex test fixtures to .codex/tests/fixtures/"

VALIDATION:
  - .codex/tests/fixtures/ directory exists with all files
  - git status shows directory was moved (renamed)
  - Commit created

---

Task 6: Update Path References in Test Files
RESPONSIBILITY: Update all ${REPO_ROOT} path references to new locations
FILES TO MODIFY:
  - .codex/tests/test_generate_prp.sh
  - .codex/tests/test_parallel_timing.sh
  - .codex/tests/test_execute_prp.sh

PATTERN TO FOLLOW: From path_update_sed_pattern.sh (bulk update with backups)

SPECIFIC STEPS:
  1. Create backups: find .codex/tests -name "*.sh" -exec cp {} {}.bak \;
  2. Update script paths:
     find .codex/tests -name "*.sh" -exec sed -i.bak \
       's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' {} \;
  3. Update test paths:
     find .codex/tests -name "*.sh" -exec sed -i.bak \
       's|${REPO_ROOT}/tests/codex/|${REPO_ROOT}/.codex/tests/|g' {} \;
  4. Update unquoted paths:
     find .codex/tests -name "*.sh" -exec sed -i.bak \
       's|scripts/codex/|.codex/scripts/|g' {} \;
     find .codex/tests -name "*.sh" -exec sed -i.bak \
       's|tests/codex/|.codex/tests/|g' {} \;
  5. Verify no old paths remain:
     grep -r "scripts/codex/" .codex/tests/ || echo "✅ All updated"
     grep -r "tests/codex/" .codex/tests/ || echo "✅ All updated"
  6. If verification passes, remove backups: find .codex/tests -name "*.bak" -delete
  7. Commit changes: git commit -am "Update: Path references in test files"

VALIDATION:
  - Zero instances of "scripts/codex/" in .codex/tests/
  - Zero instances of "tests/codex/" in .codex/tests/
  - All tests still have valid syntax: bash -n .codex/tests/*.sh

---

Task 7: Update Documentation Examples
RESPONSIBILITY: Update path references in documentation files
FILES TO MODIFY:
  - .codex/README.md (if contains old paths)
  - .codex/scripts/README.md (if contains old paths)

PATTERN TO FOLLOW: Manual review + sed update

SPECIFIC STEPS:
  1. Search for old paths in docs:
     grep -n "scripts/codex/" .codex/README.md .codex/scripts/README.md
  2. Review each instance (some may be intentional examples)
  3. Update as needed:
     sed -i.bak 's|scripts/codex/|.codex/scripts/|g' .codex/README.md
     sed -i.bak 's|scripts/codex/|.codex/scripts/|g' .codex/scripts/README.md
  4. Verify examples are accurate
  5. Commit if changes made: git commit -am "Update: Documentation paths"

VALIDATION:
  - All command examples in docs are executable with new paths
  - No broken references in documentation

---

Task 8: Validate Script Syntax
RESPONSIBILITY: Ensure all moved scripts have valid bash syntax
FILES TO CHECK:
  - All .sh files in .codex/scripts/

PATTERN TO FOLLOW: From bash_validation_pattern.sh (batch syntax validation)

SPECIFIC STEPS:
  1. Run bash -n on all scripts:
     for script in .codex/scripts/*.sh; do
       bash -n "$script" || echo "❌ Syntax error: $script"
     done
  2. If any errors found, review and fix
  3. Re-run until all pass

VALIDATION:
  - All scripts pass bash -n syntax check
  - Zero syntax errors reported

---

Task 9: Run Integration Tests
RESPONSIBILITY: Verify all tests pass with new paths
FILES TO EXECUTE:
  - .codex/tests/test_generate_prp.sh
  - .codex/tests/test_parallel_timing.sh
  - .codex/tests/test_execute_prp.sh

PATTERN TO FOLLOW: From bash_validation_pattern.sh (test execution with pass/fail tracking)

SPECIFIC STEPS:
  1. Run each test and capture results:
     .codex/tests/test_generate_prp.sh
     .codex/tests/test_parallel_timing.sh
     .codex/tests/test_execute_prp.sh
  2. Compare to baseline results from Task 1
  3. If any failures, investigate and fix path references
  4. Re-run until all pass

VALIDATION:
  - All tests pass (same results as baseline)
  - No "file not found" errors
  - Tests execute successfully from any working directory

---

Task 10: Verify Git History Preservation
RESPONSIBILITY: Confirm complete git history for all moved files
FILES TO CHECK:
  - All files in .codex/scripts/
  - All files in .codex/tests/

PATTERN TO FOLLOW: From bash_validation_pattern.sh (git history verification loop)

SPECIFIC STEPS:
  1. For each moved file, verify history with --follow:
     git log --follow --oneline .codex/scripts/parallel-exec.sh | head -10
     git log --follow --oneline .codex/scripts/codex-generate-prp.sh | head -10
     # ... (repeat for all files)
  2. Count commits with and without --follow:
     with_follow=$(git log --follow --oneline "$file" | wc -l)
     without_follow=$(git log --oneline "$file" | wc -l)
  3. Verify with_follow > without_follow (proves rename detected)

VALIDATION:
  - All files show complete history with --follow
  - Commit count with --follow > without --follow (proves rename)
  - git blame works correctly for all files

---

Task 11: Clean Up Empty Directories
RESPONSIBILITY: Remove empty scripts/codex/ and tests/codex/ directories
FILES TO DELETE:
  - scripts/codex/
  - tests/codex/

PATTERN TO FOLLOW: From git_mv_pattern.sh lines 50-85 (safe directory deletion)

SPECIFIC STEPS:
  1. Verify scripts/codex/ is empty:
     file_count=$(find scripts/codex -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')
     if [ "$file_count" -ne 0 ]; then
       echo "❌ Directory not empty"
       ls -la scripts/codex/
       exit 1
     fi
  2. Delete scripts/codex/: rmdir scripts/codex
  3. Verify tests/codex/ is empty (same pattern)
  4. Delete tests/codex/: rmdir tests/codex
  5. Commit cleanup: git commit -m "Cleanup: Remove empty codex directories"

VALIDATION:
  - scripts/codex/ directory no longer exists
  - tests/codex/ directory no longer exists
  - rmdir succeeded (proves truly empty)

---

Task 12: Final Verification
RESPONSIBILITY: Run comprehensive validation suite
FILES TO VERIFY:
  - All files in .codex/scripts/
  - All files in .codex/tests/
  - Entire repository for lingering references

PATTERN TO FOLLOW: From bash_validation_pattern.sh (comprehensive validation suite)

SPECIFIC STEPS:
  1. Comprehensive path reference check:
     grep -r "scripts/codex/" . --exclude-dir=.git --exclude-dir=node_modules || echo "✅ Clean"
     grep -r "tests/codex/" . --exclude-dir=.git --exclude-dir=node_modules || echo "✅ Clean"
  2. Syntax validation: bash -n .codex/scripts/*.sh
  3. Test execution: .codex/tests/test_*.sh
  4. Git history verification: git log --follow for sample files
  5. File count verification:
     script_count=$(find .codex/scripts -name "*.sh" | wc -l)
     test_count=$(find .codex/tests -name "*.sh" | wc -l)
     # Expect: 9 scripts, 3 tests
  6. Directory structure verification:
     [ -d .codex/scripts ] && [ -d .codex/tests ] && \
     [ ! -d scripts/codex ] && [ ! -d tests/codex ]

VALIDATION:
  - Zero old path references found (excluding gotchas.md, this PRP)
  - All scripts valid syntax
  - All tests pass
  - Git history complete for all files
  - File counts correct: 9 scripts, 3 tests
  - Directory structure as expected

---

Task 13: Documentation & Completion
RESPONSIBILITY: Finalize migration and document
FILES TO UPDATE:
  - Git commit messages
  - Migration completion tag

SPECIFIC STEPS:
  1. Review all commits made during migration
  2. Create completion tag: git tag codex-reorganization-complete
  3. Push to remote (if applicable): git push && git push --tags
  4. Update any higher-level documentation if needed

VALIDATION:
  - All commits have descriptive messages
  - Completion tag created
  - Changes pushed to remote (if applicable)
```

### Implementation Pseudocode

```bash
#!/bin/bash
# Codex Directory Reorganization Migration Script
# Based on patterns from prps/codex_reorganization/examples/

set -euo pipefail

# ============================================================================
# PHASE 1: VALIDATION & SETUP
# ============================================================================

# Pattern from git_mv_pattern.sh lines 109-116
verify_clean_working_tree() {
    echo "Checking git working tree status..."
    if ! git diff-index --quiet HEAD --; then
        echo "❌ ERROR: Git working tree has uncommitted changes"
        exit 1
    fi
    echo "✅ Working tree is clean"
}

# Pattern from feature-analysis.md assumption #10
check_no_codex_processes() {
    echo "Checking for running Codex processes..."
    if pgrep -f "codex-.*\.sh" > /dev/null; then
        echo "❌ ERROR: Codex processes running, abort migration"
        exit 1
    fi
    echo "✅ No Codex processes running"
}

# Create backup tag for rollback
create_backup() {
    BACKUP_TAG="codex-reorg-backup-$(date +%Y%m%d-%H%M%S)"
    git tag "$BACKUP_TAG"
    echo "✅ Created backup tag: $BACKUP_TAG"
    echo "   To rollback: git reset --hard $BACKUP_TAG"
}

# ============================================================================
# PHASE 2: FILE MOVES
# ============================================================================

# Pattern from git_mv_pattern.sh lines 18-47
move_file_with_git() {
    local source="$1"
    local dest="$2"

    echo "Moving: ${source} → ${dest}"

    # Pre-flight check 1: Source exists
    if [ ! -e "$source" ]; then
        echo "❌ ERROR: Source does not exist: $source"
        return 1
    fi

    # Pre-flight check 2: Destination doesn't exist
    if [ -e "$dest" ]; then
        echo "❌ ERROR: Destination already exists: $dest"
        return 1
    fi

    # Pre-flight check 3: Destination parent exists
    if [ ! -d "$(dirname "$dest")" ]; then
        echo "❌ ERROR: Destination parent does not exist: $(dirname "$dest")"
        return 1
    fi

    # Execute git mv (preserves history)
    git mv "$source" "$dest"
    echo "✅ Moved successfully"
}

# Move all scripts
move_scripts() {
    echo "Moving script files..."
    mkdir -p .codex/scripts

    declare -a SCRIPT_FILES=(
        "security-validation.sh"
        "parallel-exec.sh"
        "codex-generate-prp.sh"
        "codex-execute-prp.sh"
        "quality-gate.sh"
        "log-phase.sh"
        "validate-config.sh"
        "validate-bootstrap.sh"
        "README.md"
    )

    for file in "${SCRIPT_FILES[@]}"; do
        move_file_with_git "scripts/codex/${file}" ".codex/scripts/${file}" || exit 1
    done

    git commit -m "Move: Codex scripts to .codex/scripts/"
    echo "✅ All scripts moved"
}

# Move all tests
move_tests() {
    echo "Moving test files..."
    mkdir -p .codex/tests

    declare -a TEST_FILES=(
        "test_generate_prp.sh"
        "test_parallel_timing.sh"
        "test_execute_prp.sh"
    )

    for file in "${TEST_FILES[@]}"; do
        move_file_with_git "tests/codex/${file}" ".codex/tests/${file}" || exit 1
    done

    # Move fixtures directory
    move_file_with_git "tests/codex/fixtures" ".codex/tests/fixtures" || exit 1

    git commit -m "Move: Codex tests to .codex/tests/"
    echo "✅ All tests moved"
}

# ============================================================================
# PHASE 3: PATH UPDATES
# ============================================================================

# Pattern from path_update_sed_pattern.sh lines 17-28
update_test_paths() {
    echo "Updating path references in test files..."

    # Pattern 1: ${REPO_ROOT}/scripts/codex/ → ${REPO_ROOT}/.codex/scripts/
    find .codex/tests -name "*.sh" -exec sed -i.bak \
        's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' {} \;

    # Pattern 2: ${REPO_ROOT}/tests/codex/ → ${REPO_ROOT}/.codex/tests/
    find .codex/tests -name "*.sh" -exec sed -i.bak \
        's|${REPO_ROOT}/tests/codex/|${REPO_ROOT}/.codex/tests/|g' {} \;

    # Pattern 3: Unquoted paths
    find .codex/tests -name "*.sh" -exec sed -i.bak \
        's|scripts/codex/|.codex/scripts/|g' {} \;
    find .codex/tests -name "*.sh" -exec sed -i.bak \
        's|tests/codex/|.codex/tests/|g' {} \;

    # Verify no old paths remain
    if grep -r "scripts/codex/" .codex/tests/ 2>/dev/null || \
       grep -r "tests/codex/" .codex/tests/ 2>/dev/null; then
        echo "❌ ERROR: Old paths still present"
        exit 1
    fi

    echo "✅ All path references updated"
    find .codex/tests -name "*.bak" -delete

    git commit -am "Update: Path references in test files"
}

# ============================================================================
# PHASE 4: VALIDATION
# ============================================================================

# Pattern from bash_validation_pattern.sh lines 190-265
validate_reorganization() {
    echo "========================================="
    echo "COMPREHENSIVE VALIDATION"
    echo "========================================="

    local total_checks=0
    local passed_checks=0

    # Check 1: New directories exist
    echo ""
    echo "CHECK 1/6: New Directory Structure"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    if [ -d ".codex/scripts" ] && [ -d ".codex/tests" ]; then
        echo "✅ New directories exist"
        passed_checks=$((passed_checks + 1))
    else
        echo "❌ New directories missing"
    fi

    # Check 2: Old directories removed
    echo ""
    echo "CHECK 2/6: Old Directories Removed"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    if [ ! -d "scripts/codex" ] && [ ! -d "tests/codex" ]; then
        echo "✅ Old directories removed"
        passed_checks=$((passed_checks + 1))
    else
        echo "❌ Old directories still exist"
    fi

    # Check 3: All scripts moved (9 expected)
    echo ""
    echo "CHECK 3/6: Script Files"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    local script_count=$(find .codex/scripts -name "*.sh" | wc -l | tr -d ' ')
    if [ "${script_count}" -eq 9 ]; then  # 7 codex + 2 validate scripts
        echo "✅ All scripts moved (9 files)"
        passed_checks=$((passed_checks + 1))
    else
        echo "❌ Script count mismatch: ${script_count}/9"
    fi

    # Check 4: All tests moved (3 expected)
    echo ""
    echo "CHECK 4/6: Test Files"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    local test_count=$(find .codex/tests -name "*.sh" | wc -l | tr -d ' ')
    if [ "${test_count}" -eq 3 ]; then
        echo "✅ All tests moved (3 files)"
        passed_checks=$((passed_checks + 1))
    else
        echo "❌ Test count mismatch: ${test_count}/3"
    fi

    # Check 5: No old path references
    echo ""
    echo "CHECK 5/6: Path References Updated"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    local old_refs=$(grep -r "scripts/codex/" .codex/tests 2>/dev/null | wc -l | tr -d ' ')
    if [ "${old_refs}" -eq 0 ]; then
        echo "✅ No old path references (0 found)"
        passed_checks=$((passed_checks + 1))
    else
        echo "❌ Found ${old_refs} old path references"
    fi

    # Check 6: Script syntax validation
    echo ""
    echo "CHECK 6/6: Script Syntax Validation"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    local syntax_errors=0
    for script in .codex/scripts/*.sh; do
        if ! bash -n "$script" 2>/dev/null; then
            echo "❌ Syntax error: $script"
            syntax_errors=$((syntax_errors + 1))
        fi
    done
    if [ "${syntax_errors}" -eq 0 ]; then
        echo "✅ All scripts have valid syntax"
        passed_checks=$((passed_checks + 1))
    else
        echo "❌ ${syntax_errors} scripts have syntax errors"
    fi

    # Summary
    echo ""
    echo "========================================="
    echo "VALIDATION SUMMARY"
    echo "========================================="
    echo "Checks passed: ${passed_checks}/${total_checks}"

    if [ ${passed_checks} -eq ${total_checks} ]; then
        echo ""
        echo "✅ ALL VALIDATIONS PASSED"
        return 0
    else
        echo ""
        echo "❌ SOME VALIDATIONS FAILED"
        return 1
    fi
}

# Pattern from git_mv_pattern.sh lines 50-85
delete_empty_directory() {
    local dir_path="$1"

    echo "Checking if directory is empty: ${dir_path}"

    if [ ! -d "${dir_path}" ]; then
        echo "⚠️  Directory does not exist (already deleted?): ${dir_path}"
        return 0
    fi

    # Use find to catch hidden files
    local file_count=$(find "${dir_path}" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')

    if [ "${file_count}" -ne "0" ]; then
        echo "❌ ERROR: Directory is not empty (${file_count} items found)"
        echo "   Contents:"
        ls -la "${dir_path}"
        return 1
    fi

    # Use rmdir (not rm -rf) for safety
    rmdir "${dir_path}"
    echo "✅ Empty directory deleted"
}

# ============================================================================
# MAIN WORKFLOW
# ============================================================================

main() {
    echo "========================================="
    echo "CODEX DIRECTORY REORGANIZATION"
    echo "========================================="
    echo ""

    # Phase 1: Validation & Setup
    verify_clean_working_tree || exit 1
    check_no_codex_processes || exit 1
    create_backup

    # Phase 2: File Moves
    move_scripts || exit 1
    move_tests || exit 1

    # Phase 3: Path Updates
    update_test_paths || exit 1

    # Phase 4: Validation
    validate_reorganization || exit 1

    # Phase 5: Cleanup
    delete_empty_directory "scripts/codex" || exit 1
    delete_empty_directory "tests/codex" || exit 1
    git commit -m "Cleanup: Remove empty codex directories" 2>/dev/null || true

    # Phase 6: Completion
    git tag codex-reorganization-complete
    echo ""
    echo "========================================="
    echo "✅ MIGRATION COMPLETE"
    echo "========================================="
    echo ""
    echo "Verify with:"
    echo "  git log --follow .codex/scripts/parallel-exec.sh"
    echo "  .codex/tests/test_generate_prp.sh"
    echo ""
}

main "$@"
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Validate all moved scripts have correct bash syntax
echo "Validating bash syntax..."
for script in .codex/scripts/*.sh; do
    bash -n "$script" || echo "❌ Syntax error: $script"
done
# Expected: No errors

# Validate no ShellCheck warnings
shellcheck .codex/scripts/*.sh
# Expected: No warnings or only style suggestions
```

### Level 2: Unit Tests

```bash
# Run all Codex tests with new paths
echo "Running Codex test suite..."

.codex/tests/test_generate_prp.sh
test1_exit=$?

.codex/tests/test_parallel_timing.sh
test2_exit=$?

.codex/tests/test_execute_prp.sh
test3_exit=$?

# Check all passed
if [ $test1_exit -eq 0 ] && [ $test2_exit -eq 0 ] && [ $test3_exit -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Some tests failed"
    exit 1
fi
```

### Level 3: Integration Tests

```bash
# Verify git history for sample files
echo "Verifying git history preservation..."

git log --follow --oneline .codex/scripts/parallel-exec.sh | head -10
git log --follow --oneline .codex/tests/test_generate_prp.sh | head -10

# Expected: Shows commits before the move

# Verify no old path references remain
echo "Checking for old path references..."
grep -r "scripts/codex/" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude="gotchas.md" \
    --exclude="codex_reorganization.md"

# Expected: Zero results (or only this PRP and gotchas.md as documentation)
```

---

## Final Validation Checklist

### File Organization
- [ ] All 9 script files in `.codex/scripts/`
- [ ] All 3 test files in `.codex/tests/`
- [ ] Fixtures directory in `.codex/tests/fixtures/`
- [ ] Old `scripts/codex/` directory deleted
- [ ] Old `tests/codex/` directory deleted

### Git History
- [ ] All files show "renamed:" in git commit (not "deleted" + "new file")
- [ ] `git log --follow .codex/scripts/parallel-exec.sh` shows complete history
- [ ] `git log --follow .codex/tests/test_generate_prp.sh` shows complete history
- [ ] All moved files have > 1 commit in history

### Path References
- [ ] Zero instances of `scripts/codex/` in `.codex/tests/` files
- [ ] Zero instances of `tests/codex/` in `.codex/tests/` files
- [ ] Documentation examples use new paths
- [ ] Comprehensive grep shows no broken references

### Functionality
- [ ] All scripts pass `bash -n` syntax check
- [ ] `test_generate_prp.sh` passes
- [ ] `test_parallel_timing.sh` passes
- [ ] `test_execute_prp.sh` passes
- [ ] Scripts source dependencies correctly (no "file not found" errors)

### Code Quality
- [ ] No ShellCheck warnings (or only minor style suggestions)
- [ ] All variables quoted in file operations
- [ ] Error handling present (set -euo pipefail)
- [ ] Rollback mechanism tested (git tag created)

---

## Anti-Patterns to Avoid

### 1. Mixing File Moves with Content Changes
**Issue**: Breaks git history detection
```bash
# ❌ WRONG
git mv scripts/codex/file.sh .codex/scripts/file.sh
sed -i 's/old/new/' .codex/scripts/file.sh
git commit -m "Move and update file.sh"

# ✅ RIGHT
git mv scripts/codex/file.sh .codex/scripts/file.sh
git commit -m "Move: file.sh to .codex/scripts/"
# Then in separate commit:
sed -i 's/old/new/' .codex/scripts/file.sh
git commit -m "Update: file.sh references"
```

### 2. Using Slash Delimiter in sed with Paths
**Issue**: Requires escaping, error-prone
```bash
# ❌ WRONG
sed -i 's/scripts\/codex\//\.codex\/scripts\//g' test.sh

# ✅ RIGHT
sed -i 's|scripts/codex/|.codex/scripts/|g' test.sh
```

### 3. Using $0 Instead of BASH_SOURCE for Sourced Scripts
**Issue**: Fails when script is sourced
```bash
# ❌ WRONG
script_dir="$(cd "$(dirname "$0")" && pwd)"

# ✅ RIGHT
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

### 4. Deleting Directories Without Validation
**Issue**: May delete files not yet moved
```bash
# ❌ WRONG
rm -rf scripts/codex/

# ✅ RIGHT
file_count=$(find scripts/codex -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')
if [ "$file_count" -ne 0 ]; then
    echo "❌ Directory not empty"
    exit 1
fi
rmdir scripts/codex  # Fails safely if not truly empty
```

### 5. Incomplete Path Reference Updates
**Issue**: Some tests work, others fail mysteriously
```bash
# ❌ WRONG - Only updates obvious files
find .codex/tests -name "*.sh" -exec sed -i 's|old|new|g' {} \;

# ✅ RIGHT - Comprehensive search then update
grep -r "scripts/codex/" . --exclude-dir=.git
# Review all results, then update ALL file types (code, docs, configs)
```

---

## Success Metrics

### Primary Metrics
- **File Count**: 9 scripts + 3 tests + 1 fixtures dir = 13 items successfully moved
- **Git History**: 100% of moved files show complete history with `git log --follow`
- **Test Success**: 3/3 tests pass with new paths
- **Path References**: 0 old path references remain (excluding documentation)

### Quality Metrics
- **Syntax Validation**: 100% of scripts pass `bash -n`
- **Source Detection**: `git status` shows "renamed:" for all moves (not "deleted" + "new")
- **Directory Cleanup**: Old directories completely removed
- **Rollback Ready**: Git tag created for instant rollback if needed

---

## PRP Quality Self-Assessment

**Score: 9.5/10** - Very high confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research docs (feature-analysis, codebase-patterns, documentation-links, examples-to-include, gotchas) thoroughly analyzed and synthesized
- ✅ **Clear task breakdown**: 13 tasks with specific steps, validation criteria, and patterns to follow
- ✅ **Proven patterns**: 4 working code examples extracted from successful cleanup PRP and existing Codex scripts
- ✅ **Validation strategy**: Multi-level validation (syntax, tests, git history, path references) with executable commands
- ✅ **Error handling**: All critical gotchas documented with solutions (git history loss, sed portability, command injection, path updates)

**Deduction reasoning** (-0.5 points):
- ⚠️ **Documentation updates**: Pattern provided but not full content guidance (assumes manual review)
- ⚠️ **Edge cases**: Network filesystems (NFS, SMB) and Windows/WSL not covered (low priority for local dev)

**Mitigations**:
- Documentation updates are manual review tasks (low risk, easy to verify)
- Edge cases are outside project scope (Unix-only environment)
- Comprehensive grep and validation catches most issues
- Examples directory provides 80%+ of migration script code (high reuse)

**Implementation readiness**: 95% - Migration script can be written by copying/adapting example functions. Only customization needed: file lists and specific paths.
