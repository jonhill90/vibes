# Codebase Patterns: codex_reorganization

## Overview

Analyzed existing cleanup/reorganization PRP (`cleanup_execution_reliability_artifacts`) which provides complete patterns for git-based file operations, path updates, and validation. Found 7 Codex bash scripts using `$(dirname "${BASH_SOURCE[0]}")` sourcing pattern, 3 test files using `${REPO_ROOT}` for absolute path references, and comprehensive validation patterns from previous cleanup operations. The reorganization will move 10 files while preserving git history and updating 20+ path references.

## Architectural Patterns

### Pattern 1: Git History-Preserving File Moves
**Source**: `prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh` lines 11-47
**Relevance**: 10/10 - Core pattern for all file operations in this reorganization

**What it does**: Uses `git mv` with pre-flight validation to move files/directories while preserving complete git history (blame, log, commit context).

**Key Techniques**:
```bash
# Function: Safe directory move with comprehensive pre-flight checks
move_directory_contents() {
    local source_dir="$1"
    local dest_parent="$2"
    local item_name="$3"

    echo "Moving: ${source_dir}/${item_name} → ${dest_parent}/${item_name}"

    # Pre-flight check 1: Source exists
    if [ ! -e "${source_dir}/${item_name}" ]; then
        echo "❌ ERROR: Source does not exist: ${source_dir}/${item_name}"
        return 1
    fi

    # Pre-flight check 2: Destination doesn't exist (avoid overwrite)
    if [ -e "${dest_parent}/${item_name}" ]; then
        echo "❌ ERROR: Destination already exists: ${dest_parent}/${item_name}"
        return 1
    fi

    # Pre-flight check 3: Destination parent exists
    if [ ! -d "${dest_parent}" ]; then
        echo "❌ ERROR: Destination parent does not exist: ${dest_parent}"
        return 1
    fi

    # Execute git mv (preserves history)
    git mv "${source_dir}/${item_name}" "${dest_parent}/${item_name}"

    echo "✅ Moved successfully"
}

# Application to codex reorganization
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
git mv scripts/codex/codex-generate-prp.sh .codex/scripts/codex-generate-prp.sh
git mv tests/codex/test_generate_prp.sh .codex/tests/test_generate_prp.sh

# Verify move was tracked (not delete+create)
git status  # Should show "renamed: old_path -> new_path"
```

**When to use**:
- All script moves from `scripts/codex/` to `.codex/scripts/` (7 files)
- All test moves from `tests/codex/` to `.codex/tests/` (3 files)
- Fixtures directory move from `tests/codex/fixtures/` to `.codex/tests/fixtures/`
- ANY file operation in a git repository

**How to adapt**:
- Create target directories first: `mkdir -p .codex/scripts .codex/tests`
- Move files in dependency order (sourced files before files that source them)
- Verify each move with `git status` (should show "renamed")
- Commit file moves separately from path updates (easier rollback)

**Why this pattern**:
- Preserves git blame (track original author of each line)
- Maintains file history (all commits visible with `git log --follow`)
- Enables bisecting (find when bugs were introduced)
- Better code review (see full context of changes)

### Pattern 2: Directory-Relative Script Sourcing
**Source**: `scripts/codex/parallel-exec.sh` line 118, `scripts/codex/codex-generate-prp.sh` lines 112-125
**Relevance**: 10/10 - Critical for maintaining script functionality after moves

**What it does**: Uses `$(dirname "${BASH_SOURCE[0]}")` pattern to locate and source sibling scripts, making sourcing paths resilient to directory moves.

**Key Techniques**:
```bash
# Pattern from parallel-exec.sh (line 118)
# Source dependencies using directory-relative path
local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/log-phase.sh"

# Pattern from codex-generate-prp.sh (lines 112-125)
# Script directory (for sourcing dependencies)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Import Dependencies
source "${SCRIPT_DIR}/log-phase.sh"
source "${SCRIPT_DIR}/security-validation.sh"
source "${SCRIPT_DIR}/parallel-exec.sh"

# Why this works after move:
# BEFORE: scripts/codex/parallel-exec.sh sources scripts/codex/log-phase.sh
# AFTER:  .codex/scripts/parallel-exec.sh sources .codex/scripts/log-phase.sh
# Result: Both scripts move together, relative path stays the same ✅
```

**When to use**:
- All scripts that source sibling scripts in same directory
- Identified in: `parallel-exec.sh`, `codex-generate-prp.sh`, `codex-execute-prp.sh`, `quality-gate.sh`
- Pattern found in 4 of 7 scripts being moved

**How to adapt**:
- **NO CHANGES NEEDED** - This pattern is move-resilient
- Scripts will continue sourcing correctly after move to `.codex/scripts/`
- Pattern uses `BASH_SOURCE[0]` which dynamically resolves to script's location
- All sourced files move together to same directory

**Why this pattern**:
- Move-resilient (works regardless of directory location)
- No path updates required after file moves
- Self-documenting (clear which files are in same directory)
- Standard bash best practice for multi-file scripts

### Pattern 3: Repository-Root-Based Test Paths
**Source**: `tests/codex/test_generate_prp.sh` lines 14-16
**Relevance**: 10/10 - All test files use this pattern and require updates

**What it does**: Uses `${REPO_ROOT}` variable to construct absolute paths to scripts, enabling tests to locate scripts regardless of working directory.

**Key Techniques**:
```bash
# Pattern from test_generate_prp.sh (lines 14-16)
# Calculate repository root from test location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Use REPO_ROOT to reference scripts (REQUIRES UPDATE after move)
# BEFORE move:
"${REPO_ROOT}/scripts/codex/codex-generate-prp.sh"

# AFTER move (MUST UPDATE):
"${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

# Search/replace pattern for migration
OLD_PATTERN: "${REPO_ROOT}/scripts/codex/"
NEW_PATTERN: "${REPO_ROOT}/.codex/scripts/"

OLD_PATTERN: "${REPO_ROOT}/tests/codex/"
NEW_PATTERN: "${REPO_ROOT}/.codex/tests/"
```

**When to use**:
- All test files that execute scripts
- Found in: `test_generate_prp.sh`, `test_execute_prp.sh`, `test_parallel_timing.sh`
- Any file that needs absolute path to scripts

**How to adapt**:
- Use `sed` for bulk update after moves:
  ```bash
  # Update test files with new script paths
  find .codex/tests -name "*.sh" -exec sed -i '' \
      's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' {} \;
  find .codex/tests -name "*.sh" -exec sed -i '' \
      's|${REPO_ROOT}/tests/codex/|${REPO_ROOT}/.codex/tests/|g' {} \;
  ```
- Update `REPO_ROOT` calculation itself (test files move from `tests/codex` to `.codex/tests`):
  ```bash
  # BEFORE: REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
  # AFTER:  REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
  # Note: Same calculation works! Both are 2 levels deep
  ```

**Why this pattern**:
- Enables running tests from any working directory
- Absolute paths avoid ambiguity
- Standard pattern across entire test suite
- Easy to update with bulk search/replace

### Pattern 4: Safe Directory Cleanup with Validation
**Source**: `prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh` lines 88-119
**Relevance**: 10/10 - Required for deleting empty `scripts/codex/` and `tests/codex/`

**What it does**: Validates directory is completely empty (including hidden files) before deletion, using `find` to catch all files and `rmdir` (not `rm -rf`) for safety.

**Key Techniques**:
```bash
# Safe directory deletion pattern
delete_empty_directory() {
    local dir_path="$1"

    echo "Checking if directory is empty: ${dir_path}"

    # Pre-flight check 1: Directory exists
    if [ ! -d "${dir_path}" ]; then
        echo "⚠️  Directory does not exist (already deleted?): ${dir_path}"
        return 0  # Not an error - goal achieved
    fi

    # Pre-flight check 2: Directory is truly empty (including hidden files)
    # CRITICAL: Use find to catch .gitkeep, .DS_Store, etc.
    local file_count=$(find "${dir_path}" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')

    if [ "${file_count}" -ne "0" ]; then
        echo "❌ ERROR: Directory is not empty (${file_count} items found)"
        echo "   Contents:"
        ls -la "${dir_path}"
        return 1
    fi

    # Safe to delete (use rmdir, not rm -rf, ensures truly empty)
    rmdir "${dir_path}"

    echo "✅ Empty directory deleted"
}

# Application to codex reorganization
delete_empty_directory "scripts/codex"
delete_empty_directory "tests/codex"
```

**When to use**:
- After moving all files from `scripts/codex/` to `.codex/scripts/`
- After moving all files from `tests/codex/` to `.codex/tests/`
- Before any directory deletion operation
- As final cleanup step in migration

**How to adapt**:
- Use `find` with `-mindepth 1 -maxdepth 1` to catch hidden files
- Use `rmdir` not `rm -rf` (fails safely if directory not empty)
- Log remaining files if validation fails
- Check parent directories too (`scripts/` and `tests/` may also be empty)

**Why this pattern**:
- Prevents accidental data loss (catches forgotten files)
- Detects incomplete migration (files still in old location)
- Fail-safe behavior (refuses to delete non-empty directories)
- Clear feedback (lists remaining files if validation fails)

### Pattern 5: Comprehensive Validation Suite
**Source**: `prps/cleanup_execution_reliability_artifacts/examples/validation_checks.sh` lines 239-324
**Relevance**: 10/10 - Essential for verifying reorganization completed correctly

**What it does**: Runs systematic validation checks across multiple dimensions (file existence, directory structure, path references, git status) with clear pass/fail reporting.

**Key Techniques**:
```bash
# Comprehensive validation pattern
run_comprehensive_validation() {
    local feature_name="$1"

    echo "========================================="
    echo "COMPREHENSIVE VALIDATION"
    echo "Feature: ${feature_name}"
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

    # Check 3: All scripts moved (7 expected)
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

    # Check 5: No old path references in test files
    echo ""
    echo "CHECK 5/6: Path References Updated"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    local old_refs=$(grep -r "scripts/codex/" .codex/tests 2>/dev/null | wc -l | tr -d ' ')
    if [ "${old_refs}" -eq 0 ]; then
        echo "✅ No old path references (0 found)"
        passed_checks=$((passed_checks + 1))
    else
        echo "❌ Found ${old_refs} old path references:"
        grep -rn "scripts/codex/" .codex/tests
    fi

    # Check 6: Scripts still source correctly
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
```

**When to use**:
- After all file moves complete
- After all path reference updates complete
- Before committing changes
- As automated CI/CD check

**How to adapt**:
- Add check for fixtures directory: `.codex/tests/fixtures/`
- Add check for README updates (if applicable)
- Add check for documentation examples
- Run `bash -n` on all moved scripts

**Why this pattern**:
- Systematic verification (no manual checking needed)
- Clear pass/fail reporting (exit codes for automation)
- Comprehensive coverage (file existence, references, syntax)
- Easy to extend (add new checks as needed)

## Naming Conventions

### File Naming

**Script files** (being moved, no renaming):
- Pattern: `{purpose}.sh` or `codex-{command}.sh`
- Examples:
  - `security-validation.sh` - Validation utility
  - `parallel-exec.sh` - Parallel execution helper
  - `codex-generate-prp.sh` - Main generation orchestrator
  - `codex-execute-prp.sh` - Main execution orchestrator
  - `quality-gate.sh` - Quality validation
  - `log-phase.sh` - Logging utility
  - `validate-config.sh` - Configuration validator
  - `validate-bootstrap.sh` - Bootstrap validator
  - `README.md` - Documentation
- Location change: `scripts/codex/` → `.codex/scripts/`
- **NO RENAMING** - Files keep same names, only directory changes

**Test files** (being moved, no renaming):
- Pattern: `test_{feature}.sh`
- Examples:
  - `test_generate_prp.sh` - PRP generation tests
  - `test_parallel_timing.sh` - Parallel execution tests
  - `test_execute_prp.sh` - PRP execution tests
- Location change: `tests/codex/` → `.codex/tests/`
- **NO RENAMING** - Files keep same names, only directory changes

**Fixtures directory** (being moved, no renaming):
- Pattern: `fixtures/` with subdirectories/files inside
- Location change: `tests/codex/fixtures/` → `.codex/tests/fixtures/`
- **NO RENAMING** - Directory and contents keep same structure

### Directory Naming

**Target directory structure**:
```
.codex/
├── scripts/          # All Codex scripts (9 files)
│   ├── security-validation.sh
│   ├── parallel-exec.sh
│   ├── codex-generate-prp.sh
│   ├── codex-execute-prp.sh
│   ├── quality-gate.sh
│   ├── log-phase.sh
│   ├── validate-config.sh
│   ├── validate-bootstrap.sh
│   └── README.md
└── tests/            # All Codex tests (3 files + fixtures)
    ├── test_generate_prp.sh
    ├── test_parallel_timing.sh
    ├── test_execute_prp.sh
    └── fixtures/     # Test fixtures directory
```

**Reasoning**:
- `.codex/` prefix indicates Codex-specific infrastructure
- Hidden directory (dotfile) keeps root clean
- `scripts/` and `tests/` subdirectories mirror old structure
- Self-contained (all Codex files in one location)

### Path Reference Patterns

**Test file references** (REQUIRES UPDATE):
```bash
# OLD PATTERN (20+ instances to update):
"${REPO_ROOT}/scripts/codex/codex-generate-prp.sh"
"${REPO_ROOT}/scripts/codex/parallel-exec.sh"
"${REPO_ROOT}/tests/codex/fixtures/"

# NEW PATTERN (after update):
"${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"
"${REPO_ROOT}/.codex/scripts/parallel-exec.sh"
"${REPO_ROOT}/.codex/tests/fixtures/"
```

**Script sourcing references** (NO UPDATE NEEDED):
```bash
# Directory-relative sourcing (works before and after move)
source "${script_dir}/log-phase.sh"
source "${SCRIPT_DIR}/security-validation.sh"
source "${SCRIPT_DIR}/parallel-exec.sh"

# Why no update needed: All sourced files move together to same directory
```

## File Organization

### Current State (Before Reorganization)

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

**Problems with current state**:
1. Root directories cluttered with feature-specific subdirectories
2. Codex files scattered across 2 root directories (`scripts/` and `tests/`)
3. `.codex/` directory exists but doesn't contain Codex scripts/tests
4. Inconsistent with other hidden tool directories (`.claude/`, `.github/`)

### Target State (After Reorganization)

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

**Improvements in target state**:
1. ✅ **Single location**: All Codex files in `.codex/` directory
2. ✅ **Clean root**: No Codex-specific subdirectories in `scripts/` and `tests/`
3. ✅ **Consistent structure**: Matches `.claude/`, `.github/` pattern
4. ✅ **Self-contained**: Easy to understand what's Codex-related
5. ✅ **Maintainable**: Clear separation of concerns

### Justification

**Why consolidate to `.codex/` (not keep in `scripts/codex/` and `tests/codex/`)**:
- `.codex/` directory already exists with related files (prompts, commands, patterns)
- Matches hidden directory pattern (`.claude/`, `.github/`, `.vscode/`)
- Consolidates all Codex infrastructure in one location
- Reduces root directory clutter (2 fewer subdirectories)
- Self-documenting (clear which files are Codex-specific)

**Why use `scripts/` and `tests/` subdirectories within `.codex/`**:
- Mirrors existing structure (scripts in scripts/, tests in tests/)
- Clear separation of concerns (code vs tests)
- Familiar to developers (matches old structure)
- Enables future expansion (can add `docs/`, `configs/`, etc.)

**Why delete empty `scripts/codex/` and `tests/codex/` directories**:
- No files remain after move (empty directories serve no purpose)
- Reduces confusion (clear single source of truth)
- Cleaner repository structure
- Standard practice after directory consolidation

## Common Utilities to Leverage

### 1. Git Move Operations (Bash)
**Location**: Standard `git mv` command + pattern from cleanup PRP
**Purpose**: Move files while preserving git history

**Usage Example**:
```bash
# Create target directories
mkdir -p .codex/scripts .codex/tests

# Move script files (one at a time for clear git history)
git mv scripts/codex/security-validation.sh .codex/scripts/security-validation.sh
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
git mv scripts/codex/codex-generate-prp.sh .codex/scripts/codex-generate-prp.sh
# ... (repeat for all 9 files)

# Move test files
git mv tests/codex/test_generate_prp.sh .codex/tests/test_generate_prp.sh
git mv tests/codex/test_parallel_timing.sh .codex/tests/test_parallel_timing.sh
git mv tests/codex/test_execute_prp.sh .codex/tests/test_execute_prp.sh

# Move fixtures directory
git mv tests/codex/fixtures .codex/tests/fixtures

# Verify moves were tracked
git status  # Should show "renamed: ..." for all files
```

**When to use**: All file operations in this reorganization (100% of moves)

### 2. Path Reference Bulk Update (sed)
**Location**: Standard Unix `sed` + `grep` utilities
**Purpose**: Update all path references in test files

**Usage Example**:
```bash
# Step 1: Find all files with old path references
grep -rl "scripts/codex/" .codex/tests/
grep -rl "tests/codex/" .codex/tests/

# Step 2: Update references (in-place with backup)
find .codex/tests -name "*.sh" -exec sed -i.bak \
    's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' {} \;
find .codex/tests -name "*.sh" -exec sed -i.bak \
    's|${REPO_ROOT}/tests/codex/|${REPO_ROOT}/.codex/tests/|g' {} \;
find .codex/tests -name "*.sh" -exec sed -i.bak \
    's|scripts/codex/|.codex/scripts/|g' {} \;
find .codex/tests -name "*.sh" -exec sed -i.bak \
    's|tests/codex/|.codex/tests/|g' {} \;

# Step 3: Verify no old references remain
grep -r "scripts/codex/" .codex/tests/ || echo "✅ All references updated"
grep -r "tests/codex/" .codex/tests/ || echo "✅ All references updated"

# Step 4: Clean up backup files after verification
find .codex/tests -name "*.bak" -delete
```

**When to use**: After all file moves complete, before validation

### 3. Bash Syntax Validation
**Location**: Standard `bash -n` command
**Purpose**: Verify all moved scripts have valid syntax

**Usage Example**:
```bash
# Validate all scripts in new location
echo "Validating script syntax..."
for script in .codex/scripts/*.sh; do
    if bash -n "$script" 2>&1; then
        echo "✅ $script"
    else
        echo "❌ $script - SYNTAX ERROR"
    fi
done

# Exit code variant (for automation)
all_valid=true
for script in .codex/scripts/*.sh; do
    if ! bash -n "$script" 2>/dev/null; then
        echo "❌ Syntax error: $script"
        all_valid=false
    fi
done

if [ "$all_valid" = true ]; then
    echo "✅ All scripts have valid syntax"
    exit 0
else
    echo "❌ Some scripts have syntax errors"
    exit 1
fi
```

**When to use**: After path updates complete, as part of validation suite

### 4. Directory Empty Validation
**Location**: `find` + `rmdir` commands
**Purpose**: Safely delete empty directories after moves

**Usage Example**:
```bash
# Safe directory deletion
delete_empty_directory() {
    local dir_path="$1"

    if [ ! -d "${dir_path}" ]; then
        echo "⚠️  Directory doesn't exist: ${dir_path}"
        return 0
    fi

    # Check if truly empty (including hidden files)
    local file_count=$(find "${dir_path}" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')

    if [ "${file_count}" -ne "0" ]; then
        echo "❌ Directory not empty: ${dir_path}"
        echo "   Contents:"
        ls -la "${dir_path}"
        return 1
    fi

    # Use rmdir (not rm -rf) for safety
    rmdir "${dir_path}"
    echo "✅ Deleted empty directory: ${dir_path}"
}

# Apply to codex reorganization
delete_empty_directory "scripts/codex"
delete_empty_directory "tests/codex"
```

**When to use**: Final cleanup step after all moves verified

### 5. Comprehensive Validation Script
**Location**: Based on `prps/cleanup_execution_reliability_artifacts/examples/validation_checks.sh`
**Purpose**: Automated verification of reorganization

**Usage Example**: See Pattern 5 above for full implementation

**When to use**: Before committing changes, as final verification step

## Testing Patterns

### Unit Test Pattern: Script Syntax Validation
**Pattern**: Bash syntax check on all moved scripts
**Example**: From validation patterns above

**Test structure**:
```bash
#!/bin/bash
# Validation: All scripts have valid bash syntax

echo "Testing: Script syntax validation"

syntax_errors=0
for script in .codex/scripts/*.sh; do
    if ! bash -n "$script" 2>&1; then
        echo "❌ Syntax error: $script"
        bash -n "$script"  # Show error
        syntax_errors=$((syntax_errors + 1))
    fi
done

if [ $syntax_errors -eq 0 ]; then
    echo "✅ All scripts valid (9 scripts checked)"
    exit 0
else
    echo "❌ $syntax_errors scripts have syntax errors"
    exit 1
fi
```

### Integration Test Pattern: Test Execution
**Pattern**: Run actual test suite with new paths
**Example**: Execute moved test files

**Test structure**:
```bash
#!/bin/bash
# Integration: Run test suite with new paths

echo "Testing: Codex test suite"

# Run all tests
.codex/tests/test_generate_prp.sh
test1_exit=$?

.codex/tests/test_parallel_timing.sh
test2_exit=$?

.codex/tests/test_execute_prp.sh
test3_exit=$?

# Check all passed
if [ $test1_exit -eq 0 ] && [ $test2_exit -eq 0 ] && [ $test3_exit -eq 0 ]; then
    echo "✅ All tests passed"
    exit 0
else
    echo "❌ Some tests failed"
    echo "   test_generate_prp: exit $test1_exit"
    echo "   test_parallel_timing: exit $test2_exit"
    echo "   test_execute_prp: exit $test3_exit"
    exit 1
fi
```

### Validation Test Pattern: Path References
**Pattern**: Grep-based verification no old paths remain
**Example**: From validation patterns above

**Test structure**:
```bash
#!/bin/bash
# Validation: No old path references remain

echo "Testing: Path reference cleanup"

# Search for old patterns
old_refs=$(grep -r "scripts/codex/" .codex/ 2>/dev/null | grep -v ".git" || true)

if [ -z "$old_refs" ]; then
    echo "✅ No old path references found"
    exit 0
else
    echo "❌ Found old path references:"
    echo "$old_refs"
    exit 1
fi
```

## Anti-Patterns to Avoid

### 1. Shell Move Instead of Git Move (Loses History)
**What it is**: Using `mv` or `cp` instead of `git mv` for file operations
**Why to avoid**: Breaks git history tracking - file appears as delete+create, not rename
**Found in**: Potential mistake if using shell commands instead of git
**Better approach**: Always use `git mv` for all file operations

**Example**:
```bash
# ANTI-PATTERN (loses git history)
mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
git add .codex/scripts/parallel-exec.sh
git rm scripts/codex/parallel-exec.sh
# Git sees: deleted old file + created new file (HISTORY LOST)

# CORRECT (preserves git history)
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
# Git sees: renamed file (HISTORY PRESERVED)

# Verification
git log --follow .codex/scripts/parallel-exec.sh
# Should show full commit history back to original creation
```

**Detection**: `git status` shows "deleted" + "new file" instead of "renamed"

### 2. Updating Paths Before Moving Files (Broken References)
**What it is**: Running sed path updates before executing git mv operations
**Why to avoid**: Creates intermediate state where paths point to files that don't exist yet
**Found in**: Incorrect task ordering
**Better approach**: Move files first, then update path references

**Example**:
```bash
# ANTI-PATTERN (wrong order)
# Step 1: Update test file references (files don't exist at new location yet)
sed -i '' 's|scripts/codex/|.codex/scripts/|g' tests/codex/test_generate_prp.sh
# Step 2: Move files (paths in tests were already updated but files weren't there)
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
# Result: Broken state between steps 1 and 2

# CORRECT (right order)
# Step 1: Move files first
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
git mv tests/codex/test_generate_prp.sh .codex/tests/test_generate_prp.sh
# Step 2: Then update path references
sed -i '' 's|scripts/codex/|.codex/scripts/|g' .codex/tests/test_generate_prp.sh
# Result: Consistent state at every step
```

**Detection**: Tests fail between migration steps

### 3. Forgetting to Update REPO_ROOT Calculation (Wrong Root Path)
**What it is**: Not updating relative path calculation when test depth changes
**Why to avoid**: Tests calculate wrong repository root, fail to find scripts
**Found in**: Potential issue if test files move to different depth
**Better approach**: Verify REPO_ROOT calculation after move

**Example**:
```bash
# Check test file depth:
# BEFORE: tests/codex/test_generate_prp.sh (depth 2: tests → codex → file)
# AFTER:  .codex/tests/test_generate_prp.sh (depth 2: .codex → tests → file)

# REPO_ROOT calculation (SAME for both):
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# NO UPDATE NEEDED - depth is same
# But VERIFY after move:
cd .codex/tests
SCRIPT_DIR="$(pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
echo "REPO_ROOT: $REPO_ROOT"  # Should print repository root
```

**Detection**: Tests fail with "file not found" errors

### 4. Deleting Directories Before Verifying Empty (Data Loss)
**What it is**: Using `rm -rf` without checking directory is empty first
**Why to avoid**: Accidentally deletes files that weren't moved (data loss)
**Found in**: Hasty cleanup without validation
**Better approach**: Use `find` to verify empty, then `rmdir` (not `rm -rf`)

**Example**:
```bash
# ANTI-PATTERN (dangerous)
rm -rf scripts/codex/
# Danger: If you forgot to move a file, it's permanently deleted

# CORRECT (safe)
# 1. Verify directory is empty
file_count=$(find scripts/codex -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')
if [ "$file_count" -ne 0 ]; then
    echo "❌ Directory not empty:"
    ls -la scripts/codex/
    exit 1
fi

# 2. Use rmdir (fails if not empty)
rmdir scripts/codex/
# If this succeeds, directory was definitely empty
```

**Detection**: Files missing after cleanup, no way to recover

### 5. Partial Path Updates (Inconsistent References)
**What it is**: Updating only some path references, missing others
**Why to avoid**: Some tests/scripts work, others fail (inconsistent state)
**Found in**: Not using comprehensive grep before update
**Better approach**: Grep first to find ALL instances, update ALL files

**Example**:
```bash
# ANTI-PATTERN (manual, incomplete)
# Only update known files
sed -i '' 's|scripts/codex/|.codex/scripts/|g' .codex/tests/test_generate_prp.sh
# Problem: What about test_execute_prp.sh? test_parallel_timing.sh?

# CORRECT (comprehensive)
# 1. Find ALL files with old references
grep -rl "scripts/codex/" .codex/tests/

# 2. Update ALL files in one operation
find .codex/tests -name "*.sh" -exec sed -i.bak \
    's|scripts/codex/|.codex/scripts/|g' {} \;

# 3. Verify 0 instances remain
grep -r "scripts/codex/" .codex/tests/ || echo "✅ All updated"
```

**Detection**: `grep -r "scripts/codex/"` returns results after "complete" update

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. cleanup_execution_reliability_artifacts PRP
**Location**: `prps/cleanup_execution_reliability_artifacts/`
**Similarity**: 10/10 - Direct precedent for file reorganization with git mv
**Lessons**:
- Use git mv for ALL file operations (preserves history)
- Validate directory empty before deletion (use find + rmdir)
- Comprehensive grep for path references (find ALL instances)
- Multi-phase validation (file existence, references, syntax)
- Separate file moves from path updates (clear git history)

**Reusable code**:
```bash
# From git_mv_operations.sh
move_directory_contents()     # Safe git mv with validation
rename_file_with_git()         # File rename with validation
delete_empty_directory()       # Safe directory cleanup
validate_consolidation()       # Automated verification

# From validation_checks.sh
validate_file_exists()         # File existence check
validate_no_old_references()   # Grep-based validation
validate_git_status()          # Git status verification
run_comprehensive_validation() # Full validation suite
```

**Key difference**: cleanup PRP consolidated split directories, this reorganizes to new location

#### 2. Codex Script Sourcing Pattern
**Location**: `scripts/codex/*.sh` (files being moved)
**Similarity**: 10/10 - Shows exact sourcing pattern used
**Lessons**:
- Directory-relative sourcing: `source "${script_dir}/log-phase.sh"`
- Pattern is move-resilient (no updates needed after move)
- All sourced files must move together to same directory
- BASH_SOURCE[0] dynamically resolves to script location

**Files using this pattern**:
- `parallel-exec.sh` (line 119): sources `log-phase.sh`
- `codex-generate-prp.sh` (lines 123-125): sources 3 dependencies
- `codex-execute-prp.sh`: likely uses same pattern
- `quality-gate.sh`: likely uses same pattern

**Applicable to reorganization**: NO CHANGES NEEDED to sourcing statements

#### 3. Test File Path Pattern
**Location**: `tests/codex/test_*.sh` (files being moved)
**Similarity**: 10/10 - Shows exact path pattern requiring updates
**Lessons**:
- All tests use `${REPO_ROOT}/scripts/codex/` pattern
- REPO_ROOT calculated from test location: `$(cd "${SCRIPT_DIR}/../.." && pwd)`
- Tests reference both scripts and fixtures
- All references require bulk update after move

**Files using this pattern**:
- `test_generate_prp.sh` (lines 14-16, plus 20+ references)
- `test_execute_prp.sh` (similar pattern)
- `test_parallel_timing.sh` (similar pattern)

**Update required**: Change all `scripts/codex/` → `.codex/scripts/` and `tests/codex/` → `.codex/tests/`

## Recommendations for PRP

Based on pattern analysis:

1. **Follow git mv pattern** for ALL file operations (10 files + 1 directory)
   - Use git mv for each file individually (clear git history per file)
   - Create target directories first: `mkdir -p .codex/scripts .codex/tests`
   - Verify each move with `git status` (should show "renamed")
   - Commit file moves separately from path updates

2. **Preserve directory-relative sourcing** (no changes needed)
   - Scripts using `${script_dir}/` pattern work automatically after move
   - All sourced files move together to `.codex/scripts/`
   - No updates needed to source statements
   - Verify with `bash -n` after move

3. **Update test path references** systematically (20+ references)
   - Use comprehensive grep first: `grep -r "scripts/codex/" .codex/tests/`
   - Bulk update with sed: `s|scripts/codex/|.codex/scripts/|g`
   - Update both patterns: `scripts/codex/` and `tests/codex/`
   - Verify 0 instances remain after update

4. **Validate empty before deletion** (2 directories)
   - Use `find -mindepth 1 -maxdepth 1` to check for hidden files
   - Use `rmdir` not `rm -rf` (fails safely if not empty)
   - Delete subdirectories first, then parents
   - Log contents if validation fails

5. **Run comprehensive validation** (6+ checks)
   - File existence: verify all files in new location
   - Directory cleanup: verify old directories deleted
   - Path references: verify no old paths remain
   - Syntax validation: run `bash -n` on all scripts
   - Integration test: run test suite
   - Git status: verify all moves tracked correctly

6. **Use phased approach** (not all-at-once)
   - Phase 1: Create directories (`.codex/scripts/`, `.codex/tests/`)
   - Phase 2: Move script files (9 files)
   - Phase 3: Move test files (3 files)
   - Phase 4: Move fixtures directory
   - Phase 5: Update path references (bulk sed)
   - Phase 6: Validate all changes
   - Phase 7: Delete empty directories
   - Phase 8: Commit with descriptive message

7. **Document in README** if applicable
   - Update `.codex/README.md` with new structure
   - Update any references to old paths in documentation
   - Add migration notes if needed

8. **Test before committing**
   - Run all syntax checks: `bash -n .codex/scripts/*.sh`
   - Run full test suite: `.codex/tests/test_*.sh`
   - Verify git history: `git log --follow .codex/scripts/parallel-exec.sh`
   - Check for old references: `grep -r "scripts/codex/"`

## Source References

### From Archon

**Limited relevant results** from Archon knowledge base:
- Bash sourcing examples from Claude docs (NVM configuration pattern)
- General CI/CD patterns (GitLab pipeline examples)
- Not directly applicable to file reorganization

**Key insight**: File reorganization is codebase-specific, best patterns from local examples

### From Local Codebase

**Highly relevant patterns** from cleanup PRP:
- `/Users/jon/source/vibes/prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh` (Relevance: 10/10)
  - Complete git mv pattern with validation
  - Directory move, file rename, and cleanup functions
  - Rollback and validation patterns

- `/Users/jon/source/vibes/prps/cleanup_execution_reliability_artifacts/examples/validation_checks.sh` (Relevance: 10/10)
  - Comprehensive validation suite
  - File existence, path reference, and syntax checks
  - Automated pass/fail reporting

- `/Users/jon/source/vibes/prps/cleanup_execution_reliability_artifacts/planning/codebase-patterns.md` (Relevance: 9/10)
  - Meta-patterns for cleanup operations
  - Anti-patterns to avoid
  - Validation strategies

**Script sourcing patterns** from files being moved:
- `/Users/jon/source/vibes/scripts/codex/parallel-exec.sh` (lines 118-119)
  - Directory-relative sourcing pattern
  - Move-resilient design

- `/Users/jon/source/vibes/scripts/codex/codex-generate-prp.sh` (lines 112-125)
  - Multiple dependency sourcing
  - SCRIPT_DIR pattern

**Test path patterns** from files being moved:
- `/Users/jon/source/vibes/tests/codex/test_generate_prp.sh` (lines 14-19)
  - REPO_ROOT calculation
  - Absolute path references requiring updates

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Implementation Blueprint" section**:
   - Pattern 1: Git mv with validation (all file moves)
   - Pattern 2: Directory-relative sourcing (no changes needed)
   - Pattern 3: REPO_ROOT path updates (bulk sed operation)
   - Pattern 4: Safe directory cleanup (validate empty before delete)
   - Pattern 5: Comprehensive validation suite (6+ checks)

2. **Include exact commands in task breakdown**:
   ```bash
   # Task 1: Create directories
   mkdir -p .codex/scripts .codex/tests

   # Task 2: Move scripts (9 files)
   git mv scripts/codex/security-validation.sh .codex/scripts/
   git mv scripts/codex/parallel-exec.sh .codex/scripts/
   # ... (repeat for all scripts)

   # Task 3: Move tests (3 files)
   git mv tests/codex/test_generate_prp.sh .codex/tests/
   # ... (repeat for all tests)

   # Task 4: Move fixtures
   git mv tests/codex/fixtures .codex/tests/

   # Task 5: Update path references
   find .codex/tests -name "*.sh" -exec sed -i.bak \
       's|scripts/codex/|.codex/scripts/|g' {} \;
   ```

3. **Add validation gates to "Success Criteria"**:
   - ✅ All 10 files moved to new location
   - ✅ All scripts have valid syntax (`bash -n`)
   - ✅ All tests pass with new paths
   - ✅ 0 old path references remain
   - ✅ Old directories deleted (empty)
   - ✅ Git history preserved (use `--follow`)

4. **Document anti-patterns in "Known Gotchas" section**:
   - Anti-Pattern 1: Shell mv instead of git mv (loses history)
   - Anti-Pattern 2: Wrong task order (update paths before moving)
   - Anti-Pattern 3: Incomplete path updates (missing references)
   - Anti-Pattern 4: Unsafe directory deletion (rm -rf without validation)
   - Anti-Pattern 5: Skipping syntax validation (broken scripts)

5. **Use file organization for "Current Codebase Tree"**:
   - Show current scattered structure (scripts/codex/, tests/codex/)
   - Highlight files to be moved
   - Note existing .codex/ directory

6. **Use file organization for "Desired Codebase Tree"**:
   - Show consolidated structure (.codex/scripts/, .codex/tests/)
   - Show clean root directories (scripts/, tests/ without codex/)
   - Highlight self-contained organization

7. **Provide validation script** (from Pattern 5):
   - Copy comprehensive validation suite
   - Adapt checks for codex reorganization
   - Include in task breakdown for execution

8. **Include git history verification**:
   ```bash
   # Verify history preserved for each file
   git log --follow .codex/scripts/parallel-exec.sh | head -20
   git log --follow .codex/tests/test_generate_prp.sh | head -20
   ```

**Critical success factors**:
1. Use git mv for ALL moves (100% - no exceptions)
2. Move files BEFORE updating path references (correct task order)
3. Use comprehensive grep + sed for path updates (catch all references)
4. Validate empty before deleting directories (prevent data loss)
5. Run bash -n and test suite before committing (ensure functionality)

**Ready for PRP assembly**: ✅

This analysis provides complete patterns from proven cleanup PRP, exact sourcing patterns from scripts being moved, and comprehensive validation strategies for ensuring successful reorganization with zero functionality loss.
