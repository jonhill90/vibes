# Codebase Patterns: cleanup_execution_reliability_artifacts

## Overview

Analyzed split directory structure (`prps/prp_execution_reliability/` vs `prps/execution_reliability/`), found 16 files containing "prp_execution_reliability" references requiring updates, identified orphaned test script in root directory, and documented two template location systems needing clarification. This cleanup consolidates 11 files from split directory, renames 1 PRP file to remove redundant prefix, updates 10+ documentation files, and establishes precedent for "no redundant prefixes" convention going forward.

## Architectural Patterns

### Pattern 1: Git-Preserved File Operations (History Retention)
**Source**: `.claude/commands/prp-cleanup.md` lines 180-193 + Git best practices
**Relevance**: 10/10 (critical for preserving file history during consolidation)

**What it does**: Uses `git mv` instead of shell `mv` to preserve git blame, history, and commit context when moving or renaming files.

**Key Techniques**:
```bash
# WRONG: Shell move (loses git history)
mv prps/prp_execution_reliability/examples prps/execution_reliability/
# Result: Git sees this as delete + create (history lost)

# CORRECT: Git move (preserves history)
git mv prps/prp_execution_reliability/examples prps/execution_reliability/
# Result: Git tracks file movement (history preserved)

# For individual files
git mv prps/prp_execution_reliability.md prps/execution_reliability.md

# For nested files
git mv prps/prp_execution_reliability/execution/TASK8_TEST_RESULTS.md \
       prps/execution_reliability/execution/TASK8_TEST_RESULTS.md
```

**When to use**:
- All directory moves during consolidation
- PRP file renames (prp_execution_reliability.md → execution_reliability.md)
- Test script relocation (root → prps/test_validation_gates/)
- ANY file operation in a git repository

**How to adapt**:
- Always use `git mv` for file/directory operations
- Verify source exists before move: `if [ -d "source" ]; then git mv ...; fi`
- Commit file operations separately from content updates (easier rollback)
- Use descriptive commit message: "Consolidate execution_reliability directories"

**Why this pattern**:
- Preserves git blame (track who wrote which lines)
- Maintains file history (all commits visible in git log --follow)
- Enables easier debugging (trace when bugs were introduced)
- Better code review (see full context of changes)

### Pattern 2: Safe Directory Cleanup (Validation Before Deletion)
**Source**: Feature analysis lines 161-164, prp-cleanup.md lines 67-91
**Relevance**: 10/10 (prevents accidental data loss)

**What it does**: Validates directory is completely empty before deletion, using multiple safety checks to prevent accidental deletion of files.

**Key Techniques**:
```python
from pathlib import Path

# Method 1: Check directory is empty (Python)
source_dir = Path("prps/prp_execution_reliability")

# After moving all contents
if source_dir.exists():
    # List all remaining items
    remaining = list(source_dir.iterdir())

    if len(remaining) == 0:
        # Safe to delete
        source_dir.rmdir()  # Only removes empty directories
        print(f"✅ Deleted empty directory: {source_dir}")
    else:
        # NOT SAFE - files still present
        print(f"⚠️ Directory not empty: {remaining}")
        print("   Manual review required before deletion")

# Method 2: Bash validation
# Check directory is empty before deletion
if [ -d "prps/prp_execution_reliability" ]; then
    if [ -z "$(ls -A prps/prp_execution_reliability)" ]; then
        rmdir prps/prp_execution_reliability
        echo "✅ Deleted empty directory"
    else
        echo "⚠️ Directory not empty:"
        ls -la prps/prp_execution_reliability
    fi
fi
```

**When to use**:
- After consolidating split directories
- After moving all files from a directory
- Before any directory deletion operation
- When cleaning up after refactoring

**How to adapt**:
- Use `Path.iterdir()` to list contents (not just `exists()`)
- Use `rmdir()` not `shutil.rmtree()` (safer - fails if not empty)
- Log remaining files if validation fails
- Never use `rm -rf` without multiple checks

**Why this pattern**:
- Prevents accidental data loss (files still in directory)
- Catches incomplete consolidation (missed files)
- Provides clear feedback (lists remaining files)
- Fail-safe behavior (refuses to delete non-empty dirs)

### Pattern 3: Multi-File Find/Replace (Documentation Consistency)
**Source**: Feature analysis lines 171-178, prp_context_refactor validation approach
**Relevance**: 10/10 (core pattern for updating 10+ documentation files)

**What it does**: Systematically updates all references to old naming across multiple files, with validation before and after to ensure completeness.

**Key Techniques**:
```python
from pathlib import Path

# Step 1: FIND ALL instances first (critical)
import subprocess
result = subprocess.run(
    ["grep", "-r", "prp_execution_reliability", "prps/"],
    capture_output=True, text=True
)
files_to_update = result.stdout.strip().split('\n')
print(f"Found {len(files_to_update)} files to update")

# Step 2: Update each file with simple string replacement
for file_path in files_to_update:
    if not file_path:  # Skip empty lines
        continue

    # Parse grep output: "filepath:line:content"
    filepath = file_path.split(':')[0]

    # Read file
    path = Path(filepath)
    content = path.read_text()

    # Replace all instances
    updated = content.replace("prp_execution_reliability", "execution_reliability")

    # Write back only if changed
    if updated != content:
        path.write_text(updated)
        print(f"✅ Updated: {filepath}")

# Step 3: VERIFY no instances remain
verify = subprocess.run(
    ["grep", "-r", "prp_execution_reliability", "prps/"],
    capture_output=True
)
if verify.returncode == 1:  # grep returns 1 when no matches
    print("✅ All instances replaced (0 remaining)")
else:
    print(f"⚠️ Still found instances:\n{verify.stdout.decode()}")
```

**Bash alternative** (simpler for this use case):
```bash
# Find all files containing old name
FILES=$(grep -rl "prp_execution_reliability" prps/)

# Update each file (in-place with backup)
for file in $FILES; do
    sed -i.bak 's/prp_execution_reliability/execution_reliability/g' "$file"
    echo "✅ Updated: $file"
done

# Verify replacement (should return 0 results)
grep -r "prp_execution_reliability" prps/ || echo "✅ All instances replaced"

# Clean up backups
find prps/ -name "*.bak" -delete
```

**When to use**:
- Renaming features across documentation
- Updating file paths after moves
- Changing API names consistently
- Any refactoring affecting multiple files

**How to adapt**:
- Always search FIRST (grep -r) to get complete list
- Use case-sensitive replacement (this is a unique identifier)
- Verify 0 instances remain after replacement (grep returns non-zero)
- Consider using sed -i for in-place editing (create .bak files first)
- Test on one file first, then batch process

**Why this pattern**:
- Catches ALL references (not just obvious ones)
- Prevents partial updates (completeness validation)
- Provides clear audit trail (list of updated files)
- Reversible with .bak files (safety net)

### Pattern 4: Scoped Directory Creation (Prevent Pollution)
**Source**: `.claude/commands/generate-prp.md` lines 67-69, prp_context_refactor pattern 5
**Relevance**: 9/10 (applicable to test script relocation)

**What it does**: Creates feature-scoped directories to prevent global namespace pollution and enable easy cleanup.

**Key Techniques**:
```bash
# WRONG: Global directory (namespace pollution)
mkdir -p prps/test_scripts/
mv test_validation_gates_script.py prps/test_scripts/
# Problem: All test scripts in one directory, no feature association

# CORRECT: Feature-scoped directory
mkdir -p prps/test_validation_gates/
git mv test_validation_gates_script.py prps/test_validation_gates/test_script.py
# Benefit: Test script tied to feature, easy to find and clean up

# Pattern for execution artifacts
mkdir -p prps/{feature_name}/execution/
mkdir -p prps/{feature_name}/planning/
mkdir -p prps/{feature_name}/examples/
```

**Real application in this cleanup**:
```bash
# Create feature-scoped directory for test script
mkdir -p prps/test_validation_gates

# Move with git to preserve history
git mv test_validation_gates_script.py prps/test_validation_gates/test_script.py

# Update reference in TASK8_COMPLETION.md
sed -i 's|test_validation_gates_script.py|prps/test_validation_gates/test_script.py|g' \
    prps/execution_reliability/execution/TASK8_COMPLETION.md
```

**When to use**:
- Relocating orphaned files from root directory
- Creating directories for feature artifacts
- Organizing test scripts by feature
- ANY new directory creation for PRP-related files

**How to adapt**:
- Use feature name as directory prefix: `prps/{feature_name}/`
- Rename generic files to standard names: `test_validation_gates_script.py` → `test_script.py`
- Update all references after relocation (grep for old path)
- Document location in README if shared across features

**Why this pattern**:
- Prevents root directory clutter (files in wrong place)
- Enables parallel PRP execution (no file conflicts)
- Simplifies cleanup (delete one directory)
- Clear ownership (which feature owns which files)

### Pattern 5: Path Validation Before Operations (EAFP Pattern)
**Source**: `prps/prp_execution_reliability/examples/validation_gate_pattern.py` lines 41-65
**Relevance**: 10/10 (critical for preventing errors in file operations)

**What it does**: Uses Python's "Easier to Ask for Forgiveness than Permission" (EAFP) pattern with try/except instead of check-then-use (TOCTOU vulnerability).

**Key Techniques**:
```python
from pathlib import Path

# ANTI-PATTERN: Check-Then-Use (TOCTOU race condition)
if Path("prps/prp_execution_reliability/examples").exists():
    # Between check and use, file could be deleted by another process
    shutil.move("prps/prp_execution_reliability/examples", "prps/execution_reliability/")

# CORRECT: Try-Except (EAFP - atomic operation)
try:
    # Attempt operation directly
    source = Path("prps/prp_execution_reliability/examples")
    dest = Path("prps/execution_reliability/examples")

    # Validate source exists
    if not source.exists():
        print(f"ℹ️ Source already moved or doesn't exist: {source}")
        return

    # Validate destination doesn't exist (prevent overwrite)
    if dest.exists():
        raise ValueError(f"Destination already exists: {dest}")

    # Use git mv (safer than shutil.move)
    import subprocess
    subprocess.run(["git", "mv", str(source), str(dest)], check=True)
    print(f"✅ Moved: {source} → {dest}")

except subprocess.CalledProcessError as e:
    print(f"❌ Git move failed: {e}")
    print(f"   Source: {source}")
    print(f"   Dest: {dest}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

**Validation pattern for this cleanup**:
```python
# Pre-flight validation (check everything exists BEFORE starting)
validation_checks = [
    ("prps/prp_execution_reliability/examples", "Source examples directory"),
    ("prps/prp_execution_reliability/planning", "Source planning directory"),
    ("prps/prp_execution_reliability/execution/TASK8_TEST_RESULTS.md", "TASK8 results"),
    ("prps/prp_execution_reliability.md", "PRP file"),
    ("test_validation_gates_script.py", "Test script")
]

missing = []
for path_str, description in validation_checks:
    if not Path(path_str).exists():
        missing.append(f"  ❌ {description}: {path_str}")

if missing:
    print("⚠️ Pre-flight validation failed. Missing files/directories:")
    print('\n'.join(missing))
    print("\nCannot proceed with cleanup.")
    exit(1)

print("✅ Pre-flight validation passed. All sources exist.")
```

**When to use**:
- Before ANY file operation (move, rename, delete)
- When user input determines file paths
- Before batch operations on multiple files
- As pre-flight check before multi-step operations

**How to adapt**:
- Run pre-flight validation FIRST (all sources exist)
- Check destinations DON'T exist (prevent overwrites)
- Use try/except for actual operations (not if/else)
- Provide clear error messages with paths

**Why this pattern**:
- Prevents TOCTOU race conditions (file changes between check and use)
- Atomic operations (all-or-nothing)
- Clear error reporting (exactly what failed)
- Fail-fast behavior (stop at first error)

## Naming Conventions

### File Naming

**PRP files** (from feature analysis assumptions):
- Pattern: `{feature_name}.md` (NOT `prp_{feature_name}.md`)
- Current: `prp_execution_reliability.md` ❌ (redundant prefix)
- Correct: `execution_reliability.md` ✅ (no redundancy)
- Location: `prps/` directory
- Reasoning: Directory already indicates "PRP", prefix is redundant

**Input files**:
- Pattern: `INITIAL_{feature_name}.md`
- Example: `INITIAL_cleanup_execution_reliability_artifacts.md`
- Location: `prps/` directory
- Purpose: Distinguishes input (INITIAL) from output (generated PRP)

**Completion reports** (from EXECUTION_SUMMARY.md):
- Pattern: `TASK{n}_COMPLETION.md` (standardized naming)
- Examples: `TASK1_COMPLETION.md`, `TASK2_COMPLETION.md`, `TASK8_COMPLETION.md`
- Location: `prps/{feature_name}/execution/`
- NOT: `task_1_completion.md`, `Task-1.md`, `completion_task1.md` (6 anti-patterns avoided)

**Test results**:
- Pattern: `TASK{n}_TEST_RESULTS.md`
- Example: `TASK8_TEST_RESULTS.md`
- Location: `prps/{feature_name}/execution/`
- Purpose: Distinguished from completion report (separate concerns)

**Test scripts** (relocated files):
- Pattern: `test_script.py` (generic name in scoped directory)
- Current: `test_validation_gates_script.py` ❌ (long, redundant)
- After: `prps/test_validation_gates/test_script.py` ✅ (directory provides context)
- Reasoning: Directory name contains feature, script name can be generic

### Directory Naming

**Feature directories**:
- Pattern: `prps/{feature_name}/`
- Example: `prps/execution_reliability/` (NOT `prps/prp_execution_reliability/`)
- Subdirectories: `planning/`, `examples/`, `execution/`
- Reasoning: No redundant prefixes (prps/ already indicates PRP)

**Template directories** (from feature analysis):
- **Execution templates**: `.claude/templates/` (4 files)
  - `task-completion-report.md` - Used during PRP execution
  - `test-generation-report.md` - Generated by test subagent
  - `validation-report.md` - Generated by validator
  - `completion-report.md` - Legacy template

- **Generation templates**: `prps/templates/` (4 files)
  - `prp_base.md` - Base PRP structure
  - `feature_template.md` - Feature PRP template
  - `tool_template.md` - Tool integration template
  - `documentation_template.md` - Documentation PRP template

**Archive directories** (from prp-cleanup.md):
- Pattern: `prps/archive/{feature_name}_{timestamp}/`
- Example: `prps/archive/execution_reliability_20251007_143022/`
- Purpose: Preserve artifacts without cluttering main directory

### Convention Examples

**BEFORE cleanup** (redundant prefixes):
```
prps/
├── prp_execution_reliability.md           # ❌ Redundant "prp_" prefix
├── prp_execution_reliability/             # ❌ Redundant prefix + split location
│   ├── examples/
│   ├── planning/
│   └── execution/TASK8_TEST_RESULTS.md
└── execution_reliability/                 # ⚠️ Split location (no prefix)
    └── execution/TASK{1-8}_COMPLETION.md

test_validation_gates_script.py            # ❌ Orphaned in root
```

**AFTER cleanup** (consistent conventions):
```
prps/
├── execution_reliability.md               # ✅ No redundant prefix
└── execution_reliability/                 # ✅ Single consolidated location
    ├── examples/                          # ✅ Moved from split directory
    ├── planning/                          # ✅ Moved from split directory
    └── execution/
        ├── TASK{1-8}_COMPLETION.md        # ✅ Standardized naming
        ├── TASK8_TEST_RESULTS.md          # ✅ Moved from split directory
        └── EXECUTION_SUMMARY.md

prps/test_validation_gates/
└── test_script.py                         # ✅ Feature-scoped location
```

**Precedent for future PRPs**:
- ✅ DO: `prps/user_auth.md` and `prps/user_auth/`
- ❌ DON'T: `prps/prp_user_auth.md` (redundant prefix)
- ✅ DO: Single directory per feature
- ❌ DON'T: Split directories (prp_feature vs feature)

## File Organization

### Current State (Before Cleanup)

```
prps/
├── prp_execution_reliability.md (PRP file - redundant prefix)
├── prp_execution_reliability/    (SPLIT DIRECTORY #1)
│   ├── examples/
│   │   ├── README.md
│   │   ├── error_message_pattern.py
│   │   ├── example_task_completion_report.md
│   │   ├── template_completion_report.md
│   │   ├── template_validation_report.md
│   │   └── validation_gate_pattern.py
│   ├── planning/
│   │   ├── feature-analysis.md
│   │   ├── codebase-patterns.md
│   │   ├── documentation-links.md
│   │   ├── examples-to-include.md
│   │   └── gotchas.md
│   └── execution/
│       └── TASK8_TEST_RESULTS.md (orphaned file)
├── execution_reliability/         (SPLIT DIRECTORY #2)
│   └── execution/
│       ├── TASK1_COMPLETION.md
│       ├── TASK2_COMPLETION.md
│       ├── TASK3_COMPLETION.md
│       ├── TASK4_COMPLETION.md
│       ├── TASK5_COMPLETION.md
│       ├── TASK6_COMPLETION.md
│       ├── TASK7_COMPLETION.md
│       ├── TASK8_COMPLETION.md
│       ├── EXECUTION_SUMMARY.md
│       └── execution-plan.md
└── INITIAL_cleanup_execution_reliability_artifacts.md

test_validation_gates_script.py (ORPHANED in root directory)

.claude/templates/ (EXECUTION templates)
├── task-completion-report.md
├── test-generation-report.md
├── validation-report.md
└── completion-report.md

prps/templates/ (GENERATION templates)
├── prp_base.md
├── feature_template.md
├── tool_template.md
└── documentation_template.md
```

**Problems with current state**:
1. **Split directories**: Content scattered across `prp_execution_reliability/` and `execution_reliability/`
2. **Redundant prefix**: `prp_execution_reliability.md` has unnecessary `prp_` prefix
3. **Orphaned file**: `TASK8_TEST_RESULTS.md` in wrong subdirectory
4. **Root clutter**: `test_validation_gates_script.py` doesn't belong in root
5. **Template confusion**: Two locations (`.claude/` vs `prps/`) without documentation

### Target State (After Cleanup)

```
prps/
├── execution_reliability.md (RENAMED - no redundant prefix)
├── execution_reliability/    (CONSOLIDATED - single source of truth)
│   ├── examples/             (MOVED from prp_execution_reliability/)
│   │   ├── README.md
│   │   ├── error_message_pattern.py
│   │   ├── example_task_completion_report.md
│   │   ├── template_completion_report.md
│   │   ├── template_validation_report.md
│   │   └── validation_gate_pattern.py
│   ├── planning/             (MOVED from prp_execution_reliability/)
│   │   ├── feature-analysis.md
│   │   ├── codebase-patterns.md
│   │   ├── documentation-links.md
│   │   ├── examples-to-include.md
│   │   └── gotchas.md
│   └── execution/
│       ├── TASK1_COMPLETION.md
│       ├── TASK2_COMPLETION.md
│       ├── TASK3_COMPLETION.md
│       ├── TASK4_COMPLETION.md
│       ├── TASK5_COMPLETION.md
│       ├── TASK6_COMPLETION.md
│       ├── TASK7_COMPLETION.md
│       ├── TASK8_COMPLETION.md
│       ├── TASK8_TEST_RESULTS.md (MOVED from prp_execution_reliability/execution/)
│       ├── EXECUTION_SUMMARY.md (UPDATED references)
│       └── execution-plan.md
├── test_validation_gates/    (NEW feature-scoped directory)
│   └── test_script.py        (MOVED and RENAMED from root)
└── INITIAL_cleanup_execution_reliability_artifacts.md

.claude/templates/ (EXECUTION templates - DOCUMENTED)
├── task-completion-report.md
├── test-generation-report.md
├── validation-report.md
├── completion-report.md
└── README.md (NEW - explains template usage)

prps/templates/ (GENERATION templates - unchanged)
├── prp_base.md
├── feature_template.md
├── tool_template.md
└── documentation_template.md
```

**Improvements in target state**:
1. ✅ **Single directory**: All execution_reliability content in one place
2. ✅ **No redundant prefix**: `execution_reliability.md` (not `prp_execution_reliability.md`)
3. ✅ **Proper location**: `TASK8_TEST_RESULTS.md` in execution/ subdirectory
4. ✅ **Feature-scoped**: Test script in `prps/test_validation_gates/test_script.py`
5. ✅ **Template clarity**: README.md documents `.claude/` vs `prps/` distinction

### Justification

**Why consolidate to `execution_reliability/` (not `prp_execution_reliability/`)**:
- Removes redundant `prp_` prefix (directory is already in `prps/`)
- Matches existing location with most files (9 files vs 3 files)
- Aligns with future naming convention standardization PRP
- Sets precedent: "no prp_ prefix when in prps/ directory"

**Why move test script to `prps/test_validation_gates/`**:
- Feature-scoped directory (not global `test_scripts/`)
- Enables parallel development (no conflicts with other features)
- Easy cleanup (delete entire directory when obsolete)
- Clear ownership (test script belongs to test_validation_gates feature)

**Why create `.claude/templates/README.md`**:
- Clarifies two template locations (`.claude/` for execution, `prps/` for generation)
- Prevents future confusion (documented in INITIAL.md as pain point)
- Helps future developers choose correct location
- Referenced in CLAUDE.md for visibility

## Common Utilities to Leverage

### 1. Git Operations (Bash)
**Location**: Standard git commands
**Purpose**: Preserve file history during moves/renames

**Usage Example**:
```bash
# Move directory with history preservation
git mv prps/prp_execution_reliability/examples prps/execution_reliability/

# Move individual file
git mv prps/prp_execution_reliability.md prps/execution_reliability.md

# Move file to different subdirectory
git mv prps/prp_execution_reliability/execution/TASK8_TEST_RESULTS.md \
       prps/execution_reliability/execution/TASK8_TEST_RESULTS.md

# Verify move was tracked (not delete+create)
git status  # Should show "renamed: old_path -> new_path"
```

**When to use**: All file operations in this cleanup (100% of moves)

### 2. Path Validation (Python pathlib)
**Location**: Standard library `pathlib.Path`
**Purpose**: Check file/directory existence, validate before operations

**Usage Example**:
```python
from pathlib import Path

# Pre-flight validation
sources = [
    Path("prps/prp_execution_reliability/examples"),
    Path("prps/prp_execution_reliability/planning"),
    Path("prps/prp_execution_reliability.md")
]

for source in sources:
    if not source.exists():
        print(f"❌ Missing: {source}")
        exit(1)

print("✅ All sources exist")

# Check directory is empty before deletion
old_dir = Path("prps/prp_execution_reliability")
if old_dir.exists() and len(list(old_dir.iterdir())) == 0:
    old_dir.rmdir()
    print(f"✅ Deleted empty directory: {old_dir}")
```

**When to use**: Pre-flight validation, post-move verification, safe deletion

### 3. Multi-File Find/Replace (grep + sed)
**Location**: Standard Unix utilities
**Purpose**: Update all references to old naming across documentation

**Usage Example**:
```bash
# Step 1: Find all files containing old reference
FILES=$(grep -rl "prp_execution_reliability" prps/)
echo "Found $(echo $FILES | wc -w) files to update"

# Step 2: Preview changes (dry run)
for file in $FILES; do
    echo "=== $file ==="
    grep -n "prp_execution_reliability" "$file"
done

# Step 3: Apply changes (with backup)
for file in $FILES; do
    sed -i.bak 's/prp_execution_reliability/execution_reliability/g' "$file"
    echo "✅ Updated: $file"
done

# Step 4: Verify no instances remain
if grep -r "prp_execution_reliability" prps/ > /dev/null; then
    echo "⚠️ Still found instances:"
    grep -rn "prp_execution_reliability" prps/
else
    echo "✅ All instances replaced (0 remaining)"
fi

# Step 5: Clean up backups after verification
find prps/ -name "*.bak" -delete
```

**When to use**: Updating 10+ documentation files with consistent naming change

### 4. Directory Size Calculation (prp-cleanup.md utility)
**Location**: `.claude/commands/prp-cleanup.md` lines 69-90
**Purpose**: Calculate impact metrics before cleanup operations

**Usage Example**:
```python
import os

def get_dir_size_mb(path):
    """Calculate directory size in megabytes."""
    if not os.path.exists(path):
        return 0.0
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total += os.path.getsize(filepath)
            except:
                pass
    return total / (1024 * 1024)

def count_files(path):
    """Count files in directory."""
    if not os.path.exists(path):
        return 0
    count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        count += len(filenames)
    return count

# Calculate impact of consolidation
old_dir = "prps/prp_execution_reliability"
size = get_dir_size_mb(old_dir)
files = count_files(old_dir)
print(f"Consolidating: {files} files, {size:.1f} MB")
```

**When to use**: Before major file operations (provides metrics for validation)

### 5. Template README Generator (New Utility)
**Location**: Create `.claude/templates/README.md` (new file)
**Purpose**: Document template location distinction

**Template Content**:
```markdown
# Template Locations Guide

This repository has TWO template locations with different purposes:

## `.claude/templates/` - PRP Execution Templates

**Purpose**: Templates used DURING PRP execution by subagents

**Files**:
- `task-completion-report.md` - Task completion documentation
- `test-generation-report.md` - Test coverage reports
- `validation-report.md` - Validation gate results
- `completion-report.md` - Legacy completion template

**When to use**:
- Creating completion reports during `/execute-prp`
- Generating test reports in validation phase
- Documenting task implementation

**Example**:
```python
template = Path(".claude/templates/task-completion-report.md").read_text()
report = template.format(
    task_number=1,
    task_name="Implement authentication",
    feature_name="user_auth"
)
```

## `prps/templates/` - PRP Generation Templates

**Purpose**: Templates used DURING PRP generation by `/generate-prp`

**Files**:
- `prp_base.md` - Base PRP structure
- `feature_template.md` - Feature implementation PRPs
- `tool_template.md` - Tool integration PRPs
- `documentation_template.md` - Documentation PRPs

**When to use**:
- Generating new PRPs with `/generate-prp`
- Creating consistent PRP structure
- Assembling PRP from research artifacts

**Example**: Used by prp-gen-assembler.md to create final PRP

## Quick Reference

**Need to...** | **Use Template From**
---|---
Document task completion | `.claude/templates/task-completion-report.md`
Generate test report | `.claude/templates/test-generation-report.md`
Create new PRP | `prps/templates/prp_base.md`
Validate implementation | `.claude/templates/validation-report.md`

---

**See also**: CLAUDE.md section on template usage
```

**When to use**: Part of this cleanup (Task 6 in feature analysis)

## Testing Patterns

### Validation Script Pattern
**Pattern**: Bash validation loops with exit codes
**Example**: From feature analysis validation requirements

**Comprehensive validation**:
```bash
#!/bin/bash
# validation_cleanup.sh - Validate cleanup completion

echo "🔍 Validating cleanup_execution_reliability_artifacts..."
echo ""

# Validation 1: Single consolidated directory
echo "1. Checking directory consolidation..."
if [ -d "prps/execution_reliability/examples" ] && \
   [ -d "prps/execution_reliability/planning" ] && \
   [ -d "prps/execution_reliability/execution" ]; then
    echo "✅ All subdirectories consolidated"
else
    echo "❌ Missing subdirectories"
    exit 1
fi

# Validation 2: Old directory removed
echo "2. Checking old directory deleted..."
if [ -d "prps/prp_execution_reliability" ]; then
    echo "❌ Old directory still exists"
    exit 1
else
    echo "✅ Old directory removed"
fi

# Validation 3: PRP file renamed
echo "3. Checking PRP file renamed..."
if [ -f "prps/execution_reliability.md" ]; then
    echo "✅ PRP file renamed correctly"
else
    echo "❌ PRP file not found at new location"
    exit 1
fi

# Validation 4: No instances of old naming
echo "4. Checking documentation updated..."
INSTANCES=$(grep -r "prp_execution_reliability" prps/ 2>/dev/null | wc -l)
if [ "$INSTANCES" -eq 0 ]; then
    echo "✅ No instances of old naming found (0 results)"
else
    echo "❌ Found $INSTANCES instances of old naming:"
    grep -rn "prp_execution_reliability" prps/
    exit 1
fi

# Validation 5: Test script relocated
echo "5. Checking test script relocated..."
if [ -f "prps/test_validation_gates/test_script.py" ]; then
    echo "✅ Test script relocated"
else
    echo "❌ Test script not found at new location"
    exit 1
fi

# Validation 6: Root directory clean
echo "6. Checking root directory cleaned..."
if [ -f "test_validation_gates_script.py" ]; then
    echo "❌ Test script still in root directory"
    exit 1
else
    echo "✅ Root directory cleaned"
fi

# Validation 7: Template README created
echo "7. Checking template documentation..."
if [ -f ".claude/templates/README.md" ]; then
    echo "✅ Template README created"
else
    echo "❌ Template README not found"
    exit 1
fi

# Validation 8: File path validation (spot check)
echo "8. Validating file paths in documentation..."
SPOT_CHECKS=(
    "prps/execution_reliability/examples/README.md"
    "prps/execution_reliability/planning/feature-analysis.md"
    "prps/execution_reliability/execution/TASK8_TEST_RESULTS.md"
    "prps/execution_reliability/execution/EXECUTION_SUMMARY.md"
    "prps/execution_reliability/execution/TASK1_COMPLETION.md"
)

for file in "${SPOT_CHECKS[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing file: $file"
        exit 1
    fi
done
echo "✅ All spot-checked files exist"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL VALIDATIONS PASSED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary:"
echo "  - Directory consolidated: ✅"
echo "  - PRP file renamed: ✅"
echo "  - Documentation updated: ✅"
echo "  - Test script relocated: ✅"
echo "  - Template locations documented: ✅"
echo "  - 0 instances of old naming: ✅"
echo "  - All file paths validated: ✅"
echo ""
```

**When to use**: After each phase of cleanup to ensure correctness

### Manual Validation Checklist
**Pattern**: Human verification of automated changes

```markdown
## Manual Validation Checklist

After running cleanup script:

- [ ] Open `prps/execution_reliability.md` - verify content intact
- [ ] Check `prps/execution_reliability/examples/` - 6 files present
- [ ] Check `prps/execution_reliability/planning/` - 5 files present
- [ ] Check `prps/execution_reliability/execution/` - 10 files present (including TASK8_TEST_RESULTS.md)
- [ ] Run test script: `python prps/test_validation_gates/test_script.py`
- [ ] Git status shows "renamed:" not "deleted:" + "created:"
- [ ] Open EXECUTION_SUMMARY.md - all paths use "execution_reliability"
- [ ] Open `.claude/templates/README.md` - clear template distinction
- [ ] Run automated validation: `bash validation_cleanup.sh`
```

## Anti-Patterns to Avoid

### 1. Shell Move Instead of Git Move (Loses History)
**What it is**: Using `mv` or `shutil.move()` instead of `git mv` for file operations
**Why to avoid**: Breaks git history tracking - file appears as delete+create, not rename
**Found in**: Potential mistake in manual operations
**Better approach**: Always use `git mv` in git repositories

**Example**:
```bash
# ANTI-PATTERN (loses git history)
mv prps/prp_execution_reliability/examples prps/execution_reliability/
# Git sees: deleted examples/ + created examples/ (separate files)

# CORRECT (preserves git history)
git mv prps/prp_execution_reliability/examples prps/execution_reliability/
# Git sees: renamed examples/ (tracks history)

# Verification
git log --follow prps/execution_reliability/examples/README.md
# Should show full commit history, not just "created"
```

**Detection**: `git status` shows "deleted" + "new file" instead of "renamed"

### 2. Deleting Non-Empty Directories (Data Loss Risk)
**What it is**: Using `rm -rf` or `shutil.rmtree()` without verifying directory is empty
**Why to avoid**: Accidentally deletes files that weren't moved (data loss)
**Found in**: Potential mistake if consolidation is incomplete
**Better approach**: Use `rmdir` (fails if not empty) + verify empty with `iterdir()`

**Example**:
```bash
# ANTI-PATTERN (deletes everything, even unmoved files)
rm -rf prps/prp_execution_reliability/
# Danger: If you forgot to move a file, it's gone forever

# CORRECT (fails if directory not empty)
rmdir prps/prp_execution_reliability/
# Error: "Directory not empty" - forces you to investigate

# Even better: Verify first
if [ -z "$(ls -A prps/prp_execution_reliability)" ]; then
    rmdir prps/prp_execution_reliability
    echo "✅ Deleted empty directory"
else
    echo "⚠️ Directory not empty:"
    ls -la prps/prp_execution_reliability
    echo "Manual review required"
fi
```

**Detection**: `ls -la prps/prp_execution_reliability` shows files remaining

### 3. Partial Find/Replace (Missed References)
**What it is**: Updating only obvious files, missing references in unexpected places
**Why to avoid**: Broken links, inconsistent documentation, confusion
**Found in**: Risk if only updating known files without comprehensive grep
**Better approach**: Grep FIRST to find ALL instances, then update ALL files

**Example**:
```bash
# ANTI-PATTERN (misses files)
# Only update known files
sed -i 's/prp_execution_reliability/execution_reliability/g' prps/execution_reliability.md
sed -i 's/prp_execution_reliability/execution_reliability/g' prps/execution_reliability/execution/EXECUTION_SUMMARY.md
# Problem: What about TASK*_COMPLETION.md files? Other references?

# CORRECT (comprehensive grep first)
# Find ALL files
FILES=$(grep -rl "prp_execution_reliability" prps/)
echo "Files to update: $(echo $FILES | tr ' ' '\n')"

# Update ALL files
for file in $FILES; do
    sed -i.bak 's/prp_execution_reliability/execution_reliability/g' "$file"
done

# Verify 0 instances remain
grep -r "prp_execution_reliability" prps/ || echo "✅ All instances replaced"
```

**Detection**: `grep -r "prp_execution_reliability" prps/` returns results after "complete" update

### 4. Forgetting to Update References After Move (Broken Links)
**What it is**: Moving files without updating references in documentation
**Why to avoid**: Broken links, 404 errors, confusion about file locations
**Found in**: `TASK8_COMPLETION.md` references `test_validation_gates_script.py` in root
**Better approach**: Grep for old path, update all references after move

**Example**:
```bash
# ANTI-PATTERN (move file but forget references)
git mv test_validation_gates_script.py prps/test_validation_gates/test_script.py
# Problem: TASK8_COMPLETION.md still references old path

# CORRECT (update references after move)
# 1. Move file
git mv test_validation_gates_script.py prps/test_validation_gates/test_script.py

# 2. Find all references to old path
grep -r "test_validation_gates_script.py" prps/

# 3. Update references
sed -i 's|test_validation_gates_script.py|prps/test_validation_gates/test_script.py|g' \
    prps/execution_reliability/execution/TASK8_COMPLETION.md

# 4. Verify no old references remain
grep -r "test_validation_gates_script.py" prps/ || echo "✅ All references updated"
```

**Detection**: Documentation references paths that don't exist

### 5. Skipping Pre-Flight Validation (Blind Operations)
**What it is**: Running file operations without checking sources exist first
**Why to avoid**: Cryptic errors, partial completion, hard to debug
**Found in**: Risk if script runs without validation checks
**Better approach**: Validate ALL sources exist BEFORE starting operations

**Example**:
```python
# ANTI-PATTERN (blindly attempt operations)
shutil.move("prps/prp_execution_reliability/examples", "prps/execution_reliability/")
# Error: "FileNotFoundError: prps/prp_execution_reliability/examples"
# Why? Already moved? Never existed? Typo?

# CORRECT (validate first, then operate)
from pathlib import Path

# Pre-flight validation
sources = {
    "examples": Path("prps/prp_execution_reliability/examples"),
    "planning": Path("prps/prp_execution_reliability/planning"),
    "PRP file": Path("prps/prp_execution_reliability.md")
}

missing = [name for name, path in sources.items() if not path.exists()]

if missing:
    print(f"❌ Pre-flight failed. Missing: {', '.join(missing)}")
    for name, path in sources.items():
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {name}: {path}")
    exit(1)

print("✅ Pre-flight passed. Proceeding with operations...")

# Now run operations with confidence
for name, source in sources.items():
    # Operations here
    pass
```

**Detection**: Operations fail with "file not found" errors

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. PRP Context Refactor (Similar Cleanup/Consolidation)
**Location**: `prps/prp_context_refactor/`
**Similarity**: 8/10 - Consolidation and DRY violation fixes
**Lessons**:
- Reference card compression pattern (reduce verbose tutorials)
- 5-level validation approach (file size, duplication, pattern loading, functionality, metrics)
- Security function extraction (DRY for repeated code)
- Progressive disclosure principle (two-level maximum)

**Key difference**:
- Context refactor: Compressing pattern files and removing duplication
- This cleanup: Moving/renaming files and updating references

**Applicable patterns**:
- Multi-file find/replace for documentation updates
- Validation gates at each phase
- Metrics calculation (before/after comparison)

#### 2. Standardize PRP Naming Convention (Related Future Work)
**Location**: `prps/INITIAL_standardize_prp_naming_convention.md`
**Similarity**: 10/10 - This cleanup is "Option A" referenced in that PRP
**Lessons**:
- This cleanup sets precedent for "no prp_ redundancy" rule
- Demonstrates proper cleanup workflow after PRP execution
- Shows how to handle split directories
- Establishes naming convention standards

**Key quote from that PRP**:
> "Option A: prp_execution_reliability → execution_reliability (precedent-setting cleanup)"

**Applicable patterns**:
- Naming convention enforcement
- Redundant prefix detection and removal
- Developer guide creation (template README)

#### 3. PRP Cleanup Command (Existing Cleanup Infrastructure)
**Location**: `.claude/commands/prp-cleanup.md`
**Similarity**: 7/10 - Directory operations and validation
**Lessons**:
- Directory size calculation for impact metrics
- File counting for before/after comparison
- Safe deletion with confirmation
- Archive option (preserve instead of delete)

**Reusable utilities**:
```python
# From prp-cleanup.md lines 69-90
def get_dir_size_mb(path): ...  # Calculate directory size
def count_files(path): ...      # Count files in directory
```

**Not applicable**: This cleanup moves/renames (doesn't delete artifacts)

#### 4. Test Validation Gates Script (File Being Relocated)
**Location**: `test_validation_gates_script.py` (root directory)
**Similarity**: 10/10 - This file is being relocated in this cleanup
**Lessons**:
- Validation gate patterns (from validation_gate_pattern.py)
- Report coverage calculation
- Error message formatting (5 sections: Problem, Path, Impact, Troubleshooting, Resolution)

**After relocation**:
- New path: `prps/test_validation_gates/test_script.py`
- Update reference in `TASK8_COMPLETION.md`
- Feature-scoped directory (not global test_scripts/)

## Recommendations for PRP

Based on pattern analysis:

1. **Follow git mv pattern** for ALL file operations
   - Preserves file history (git log --follow works)
   - Enables git blame (track who wrote which lines)
   - Shows as "renamed" not "deleted + created"
   - Use for: directories (examples, planning), files (PRP, test script)

2. **Use comprehensive grep** before find/replace
   - Find ALL 16 files containing "prp_execution_reliability"
   - Update all simultaneously (not one-by-one)
   - Verify 0 instances remain after replacement
   - Creates .bak files for safety (can rollback)

3. **Validate before deletion** of prp_execution_reliability directory
   - Check directory is empty: `len(list(Path.iterdir())) == 0`
   - Use `rmdir()` not `shutil.rmtree()` (safer)
   - List remaining files if validation fails
   - Document why directory can be deleted safely

4. **Create feature-scoped directory** for test script
   - Use `prps/test_validation_gates/` (not global `test_scripts/`)
   - Rename to generic `test_script.py` (directory provides context)
   - Update reference in TASK8_COMPLETION.md
   - Demonstrates scoped directory pattern for future PRPs

5. **Document template distinction** clearly
   - Create `.claude/templates/README.md`
   - Explain execution templates vs generation templates
   - Provide quick reference table (need X → use Y)
   - Reference from CLAUDE.md for visibility

6. **Run validation script** after each phase
   - Validate directory consolidation (all 3 subdirectories present)
   - Verify old directory deleted (prp_execution_reliability gone)
   - Check PRP file renamed (execution_reliability.md exists)
   - Confirm 0 instances of old naming (grep returns empty)
   - Validate file paths (spot check 5 random files)

7. **Use phased approach** (not all-at-once)
   - Phase 1: Pre-flight validation (all sources exist)
   - Phase 2: Directory consolidation (git mv 3 items)
   - Phase 3: PRP file rename (git mv 1 file)
   - Phase 4: Documentation updates (grep + sed on 10+ files)
   - Phase 5: Test script relocation (git mv + update reference)
   - Phase 6: Template documentation (create README.md)
   - Phase 7: Old directory cleanup (validate + rmdir)
   - Phase 8: Final validation (run comprehensive validation script)

8. **Preserve functionality** (no code changes)
   - This is file organization only (no logic changes)
   - Test script should work at new location
   - Documentation should reference correct paths
   - All links should resolve correctly

## Source References

### From Archon

**No directly relevant patterns found** in Archon knowledge base:
- Searched "git mv file consolidation" → 0 relevant results (directory setup examples only)
- Searched "directory reorganization pathlib" → 3 results (basic pathlib usage, not reorganization)
- Searched "file operations refactoring cleanup" → 5 results (agent loops and privacy policies, not file operations)

**Key insight**: File consolidation and naming standardization are codebase-specific patterns, not general programming patterns. No similar PRPs exist in Archon.

### From Local Codebase

**Files containing "prp_execution_reliability"** (grep results):
1. `/Users/jon/source/vibes/prps/cleanup_execution_reliability_artifacts/planning/feature-analysis.md` ← This planning artifact
2. `/Users/jon/source/vibes/.git/logs/refs/heads/main` ← Git history (won't change)
3. `/Users/jon/source/vibes/.git/logs/HEAD` ← Git history (won't change)
4. `/Users/jon/source/vibes/prps/INITIAL_standardize_prp_naming_convention.md` ← Related future PRP
5. `/Users/jon/source/vibes/prps/INITIAL_cleanup_execution_reliability_artifacts.md` ← Input file
6. `/Users/jon/source/vibes/prps/execution_reliability/execution/EXECUTION_SUMMARY.md` ← **UPDATE**
7. `/Users/jon/source/vibes/test_validation_gates_script.py` ← **UPDATE** (reference to prp_execution_reliability)
8. `/Users/jon/source/vibes/prps/test_validation_gates.md` ← **UPDATE** (PRP file reference)
9. `/Users/jon/source/vibes/.claude/commands/execute-prp.md` ← **UPDATE** (example reference)
10. `/Users/jon/source/vibes/prps/execution_reliability/execution/TASK5_COMPLETION.md` ← **UPDATE**
11. `/Users/jon/source/vibes/prps/execution_reliability/execution/TASK1_COMPLETION.md` ← **UPDATE**
12. `/Users/jon/source/vibes/prps/execution_reliability/execution/execution-plan.md` ← **UPDATE**
13. `/Users/jon/source/vibes/prps/prp_execution_reliability.md` ← **RENAME** (the PRP file itself)
14. `/Users/jon/source/vibes/prps/prp_execution_reliability/planning/examples-to-include.md` ← **MOVE** (in directory to consolidate)
15. `/Users/jon/source/vibes/prps/prp_execution_reliability/examples/README.md` ← **MOVE** (in directory to consolidate)
16. `/Users/jon/source/vibes/prps/prp_execution_reliability/planning/codebase-patterns.md` ← **MOVE** (in directory to consolidate)

**Summary**: 10+ files need content updates, 11 files need to be moved, 1 file needs rename

**Directory structure analysis**:
- `prps/prp_execution_reliability/examples/` → 6 files
- `prps/prp_execution_reliability/planning/` → 5 files
- `prps/prp_execution_reliability/execution/` → 1 file (TASK8_TEST_RESULTS.md)
- **Total to move**: 12 files in 3 directories

**Test script location**:
- Current: `/Users/jon/source/vibes/test_validation_gates_script.py` (root directory)
- Target: `prps/test_validation_gates/test_script.py`
- References: 2 files (TASK8_COMPLETION.md, prp_execution_reliability/execution/TASK8_TEST_RESULTS.md)

**Template locations** (verified by glob):
- `.claude/templates/`: 4 files (task-completion-report.md, test-generation-report.md, validation-report.md, completion-report.md)
- `prps/templates/`: 4 files (prp_base.md, feature_template.md, tool_template.md, documentation_template.md)
- **Distinction**: Execution templates vs generation templates (needs README.md)

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Implementation Blueprint" section**:
   - Pattern 1: Git mv for all operations (examples, planning, PRP file, test script)
   - Pattern 2: Safe directory cleanup (validate empty before rmdir)
   - Pattern 3: Multi-file find/replace (16 files with "prp_execution_reliability")
   - Pattern 4: Feature-scoped directory (test_validation_gates/)
   - Pattern 5: Pre-flight validation (check all sources exist)

2. **Include exact file operations in task breakdown**:
   ```bash
   # Task 1: Directory consolidation
   git mv prps/prp_execution_reliability/examples prps/execution_reliability/
   git mv prps/prp_execution_reliability/planning prps/execution_reliability/
   git mv prps/prp_execution_reliability/execution/TASK8_TEST_RESULTS.md \
          prps/execution_reliability/execution/

   # Task 2: PRP file rename
   git mv prps/prp_execution_reliability.md prps/execution_reliability.md

   # Task 4: Test script relocation
   mkdir -p prps/test_validation_gates
   git mv test_validation_gates_script.py prps/test_validation_gates/test_script.py
   ```

3. **Add validation gates to "Success Criteria"**:
   - ✅ Directory consolidated (3 subdirectories present)
   - ✅ PRP file renamed (no redundant prefix)
   - ✅ 0 instances of "prp_execution_reliability" in docs (except git history)
   - ✅ Test script relocated (root directory clean)
   - ✅ Template locations documented (README.md created)
   - ✅ Git history preserved (all operations use git mv)

4. **Document anti-patterns in "Known Gotchas" section**:
   - Anti-Pattern 1: Shell mv instead of git mv (loses history)
   - Anti-Pattern 2: Deleting non-empty directories (data loss)
   - Anti-Pattern 3: Partial find/replace (missed references)
   - Anti-Pattern 4: Forgetting to update references (broken links)
   - Anti-Pattern 5: Skipping pre-flight validation (blind operations)

5. **Use file organization for "Current Codebase Tree"**:
   - Show split directory structure (before state)
   - Show 16 files containing "prp_execution_reliability"
   - Show orphaned test script in root
   - Show 2 template locations without documentation

6. **Use file organization for "Desired Codebase Tree"**:
   - Show consolidated structure (after state)
   - Show renamed PRP file (no redundant prefix)
   - Show test script in feature-scoped directory
   - Show template README.md created

7. **Provide comprehensive validation script** (from Testing Patterns section):
   - 8 validation checks (directory, rename, references, test script, templates, paths)
   - Exit codes for pass/fail (automated CI/CD integration)
   - Clear success/failure messages

8. **Include impact metrics**:
   - Files to move: 12 (in 3 directories)
   - Files to rename: 1 (PRP file)
   - Files to update: 10+ (documentation references)
   - Files to create: 1 (template README.md)
   - Directories to delete: 1 (after validation)

**Critical success factors**:
1. Use git mv for ALL file operations (100% of moves/renames)
2. Comprehensive grep before AND after updates (verify 0 instances remain)
3. Pre-flight validation (all sources exist before operations)
4. Phased approach (8 phases, validate after each)
5. Create validation script (automated verification)

**Ready for PRP assembly**: ✅

This analysis provides complete context for assembling a surgical cleanup PRP with clear patterns, anti-patterns, validation gates, and step-by-step implementation guidance.
