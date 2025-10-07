# Known Gotchas: cleanup_execution_reliability_artifacts

## Overview

This cleanup operation consolidates split directories, removes redundant naming, and updates documentation references. While conceptually simple, file operations present **critical risks**: data loss from TOCTOU race conditions, broken git history, partial find/replace updates, and silent failures. This document identifies 12 comprehensive gotchas across security, performance, git operations, and reference integrity - each with concrete detection methods and mitigation strategies. Key insight: **git doesn't track renames, it guesses them** - combining content changes with moves breaks history detection.

## Critical Gotchas

### 1. Git History Loss from Content Changes During Rename

**Severity**: Critical
**Category**: Git History / Data Loss
**Affects**: Git rename detection (all versions)
**Source**: https://stackoverflow.com/questions/2314652/is-it-possible-to-move-rename-files-in-git-and-maintain-their-history

**What it is**:
Git uses heuristic-based similarity detection to track file renames. When you combine a file move with content changes in the same commit, Git's rename detection fails if content similarity drops below ~50%. The file appears as "deleted" + "added" instead of "renamed", losing all git blame and history continuity.

**Why it's a problem**:
- **Lost attribution**: git blame shows wrong author for all lines (the person who moved it, not who wrote it)
- **Broken history**: `git log --follow` doesn't work across the rename
- **Debugging nightmare**: Can't trace when bugs were introduced
- **Code review confusion**: Diff shows entire file as new, not just changes
- **GitHub breaks**: File view shows "new file" not full commit history

**How to detect it**:
```bash
# After rename, check if Git detected it as rename or delete+add
git status
# Should show: "renamed: old_path -> new_path"
# NOT: "deleted: old_path" and "new file: new_path"

# Verify history follows across rename
git log --follow --oneline prps/execution_reliability.md
# Should show commits from BEFORE the rename
# If only shows commits AFTER, history is broken

# Check rename detection similarity
git log --follow -M50% prps/execution_reliability.md
# -M50% = 50% similarity threshold (default)
```

**How to avoid/fix**:

```bash
# ❌ WRONG - Combines rename + content change (breaks detection)
git mv prps/execution_reliability.md prps/execution_reliability.md
sed -i 's/execution_reliability/execution_reliability/g' prps/execution_reliability.md
git add prps/execution_reliability.md
git commit -m "Rename and update PRP file"
# Result: Git sees "deleted + added", not "renamed"

# ✅ RIGHT - Separate commits: rename first, then content changes
# Commit 1: Pure rename (no content changes)
git mv prps/execution_reliability.md prps/execution_reliability.md
git commit -m "Rename: execution_reliability.md → execution_reliability.md"

# Commit 2: Content updates (after rename is committed)
sed -i 's/execution_reliability/execution_reliability/g' prps/execution_reliability.md
git commit -am "Update internal references to new name"

# Verification: Check rename was detected
git log --follow --oneline prps/execution_reliability.md
# Should show full history including pre-rename commits
```

**Additional context**:
- Git doesn't track renames explicitly - it guesses them post-hoc
- Similarity threshold is configurable but defaults to 50%
- `--find-copies-harder` flag often doesn't help, even with zero content changes
- Attribution issues: Moving a file attributes all code to you (the mover) unless rename is detected

**Additional Resources**:
- https://git-scm.com/docs/git-mv
- https://medium.com/@nairmilind3/why-you-should-never-rename-or-move-files-17bdebfcdf7a

---

### 2. TOCTOU Race Condition in File Operations

**Severity**: Critical
**Category**: Security / Data Loss
**Affects**: All file operations using check-then-use pattern
**Source**: https://cwe.mitre.org/data/definitions/367.html

**What it is**:
Time-of-check to time-of-use (TOCTOU) race condition: file state changes between verification check and actual operation. An attacker or concurrent process can modify, delete, or replace files in the gap between `if file.exists()` and `file.move()`. This is a CWE-367 vulnerability.

**Why it's a problem**:
- **Security**: Privilege escalation attacks (used to compromise Tesla Model 3 at Pwn2Own 2023)
- **Data loss**: File deleted between check and use causes unexpected behavior
- **Symbolic link attacks**: Attacker replaces file with symlink to sensitive file
- **Race condition**: Multiple processes operating on shared filesystem
- **Real-world impact**: Docker had TOCTOU vulnerability allowing root filesystem access (2019)

**How to detect it**:
```bash
# Symptom: Intermittent failures, especially under high concurrency
FileNotFoundError: [Errno 2] No such file or directory: 'file.txt'
# File existed during check but gone during use

# Look for check-then-use pattern in code
if Path("source").exists():
    # GAP: File could be deleted/modified here by another process
    shutil.move("source", "dest")
```

**How to avoid/fix**:

```python
# ❌ VULNERABLE - Check-then-use pattern (TOCTOU vulnerability)
from pathlib import Path
import shutil

source = Path("prps/execution_reliability/examples")
dest = Path("prps/execution_reliability/examples")

# Check 1: Source exists?
if source.exists():
    # **VULNERABILITY**: Between check and use, another process could:
    # - Delete the source
    # - Replace with symlink to /etc/passwd
    # - Modify permissions

    # Check 2: Destination doesn't exist?
    if not dest.exists():
        # **VULNERABILITY**: Another process could create dest here
        shutil.move(str(source), str(dest))

# ✅ SECURE - Try-except pattern (atomic operation, EAFP)
import subprocess

def safe_git_move(source, dest):
    """
    Atomic git mv operation with proper error handling.
    No TOCTOU vulnerability - git mv is atomic.
    """
    try:
        # Single atomic operation - no gap between check and use
        result = subprocess.run(
            ["git", "mv", str(source), str(dest)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Moved: {source} → {dest}")
        return True

    except subprocess.CalledProcessError as e:
        # Handle specific errors
        if "does not exist" in e.stderr:
            print(f"ℹ️ Source doesn't exist (already moved?): {source}")
        elif "already exists" in e.stderr:
            print(f"❌ Destination already exists: {dest}")
        else:
            print(f"❌ Git move failed: {e.stderr}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Usage: Attempt operation directly, handle errors
safe_git_move(
    Path("prps/execution_reliability/examples"),
    Path("prps/execution_reliability/examples")
)
```

**Better approach - Pre-flight validation, then atomic operation**:
```python
# Pre-flight validation (ALL checks upfront, fail fast)
def validate_consolidation_preconditions():
    """
    Validate ALL conditions before starting operations.
    Still has TOCTOU gap, but minimizes risk by checking everything first.
    """
    errors = []

    sources = [
        Path("prps/execution_reliability/examples"),
        Path("prps/execution_reliability/planning"),
        Path("prps/execution_reliability.md")
    ]

    for source in sources:
        if not source.exists():
            errors.append(f"Source missing: {source}")

    if errors:
        print("❌ Pre-flight validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("✅ Pre-flight validation passed")
    return True

# Run all operations with try-except (atomic)
if validate_consolidation_preconditions():
    # Each operation is atomic (no check-then-use)
    safe_git_move(source1, dest1)
    safe_git_move(source2, dest2)
```

**Mitigation hierarchy** (best to worst):
1. **Atomic operations** (git mv, file handles) - eliminates TOCTOU
2. **File handles** (openat, statat) - operate on handles not paths
3. **Try-except** (EAFP) - attempt operation, handle errors
4. **Pre-flight + try-except** - validate upfront, but still use try-except
5. **Check-then-use** (NEVER use) - vulnerable to TOCTOU

**Additional Resources**:
- https://wiki.sei.cmu.edu/confluence/display/c/FIO45-C.+Avoid+TOCTOU+race+conditions+while+accessing+files
- https://www.sonarsource.com/blog/winning-the-race-against-toctou-vulnerabilities/

---

### 3. Accidental Data Loss from Non-Empty Directory Deletion

**Severity**: Critical
**Category**: Data Loss
**Affects**: Directory cleanup operations
**Source**: Feature analysis + web search (common Unix pitfall)

**What it is**:
Using `rm -rf` or `shutil.rmtree()` to delete directories without verifying they're empty first. Hidden files (`.DS_Store`, `.gitkeep`), concurrent file creation, or incomplete consolidation can result in unintended deletion of important files.

**Why it's a problem**:
- **Irreversible data loss**: Deleted files can't be recovered (no trash/recycle bin)
- **Hidden files**: `.DS_Store`, `.git`, `__pycache__` not visible with `ls`
- **Concurrent operations**: Another process might add files during deletion
- **Network filesystems**: CIFS/SMB may have hidden files only visible from server
- **Incomplete moves**: If consolidation fails partway, source dir still has files

**How to detect it**:
```bash
# Symptom: Directory deletion succeeds when you expected failure
rm -rf prps/execution_reliability/
# No error even though directory wasn't empty!

# Check if directory truly empty (catches hidden files)
find prps/execution_reliability -mindepth 1 -maxdepth 1 | wc -l
# Returns: 3 (not empty!)

# ls misses hidden files
ls -la prps/execution_reliability
# Shows: .DS_Store, .gitkeep (hidden files)
```

**How to avoid/fix**:

```bash
# ❌ DANGEROUS - Deletes everything without verification
rm -rf prps/execution_reliability/
# Problem: No error if directory has files. SILENT DATA LOSS.

# ❌ DANGEROUS - Python equivalent
import shutil
shutil.rmtree("prps/execution_reliability")
# Problem: Deletes non-empty directories without warning

# ✅ SAFE - Use rmdir (fails if not empty)
rmdir prps/execution_reliability/
# Output: "rmdir: prps/execution_reliability/: Directory not empty"
# Forces you to investigate before deleting

# ✅ SAFER - Verify empty before deletion (bash)
#!/bin/bash
delete_empty_directory() {
    local dir_path="$1"

    if [ ! -d "${dir_path}" ]; then
        echo "ℹ️ Directory doesn't exist (already deleted?): ${dir_path}"
        return 0
    fi

    # Use find to catch hidden files (ls misses them)
    local file_count=$(find "${dir_path}" -mindepth 1 -maxdepth 1 | wc -l)

    if [ "${file_count}" -ne "0" ]; then
        echo "❌ Directory not empty (${file_count} items remain):"
        ls -la "${dir_path}"
        echo ""
        echo "Remaining files:"
        find "${dir_path}" -mindepth 1 -maxdepth 1
        return 1
    fi

    # Use rmdir not rm -rf (fail-safe)
    rmdir "${dir_path}"
    if [ $? -eq 0 ]; then
        echo "✅ Deleted empty directory: ${dir_path}"
        return 0
    else
        echo "❌ Failed to delete directory: ${dir_path}"
        return 1
    fi
}

# Usage
delete_empty_directory "prps/execution_reliability"
```

**Python safe deletion**:
```python
from pathlib import Path

def delete_empty_directory(dir_path: Path) -> bool:
    """
    Safely delete directory only if truly empty.
    Uses rmdir() which fails on non-empty directories.
    """
    if not dir_path.exists():
        print(f"ℹ️ Directory doesn't exist: {dir_path}")
        return True

    if not dir_path.is_dir():
        print(f"❌ Not a directory: {dir_path}")
        return False

    # Check for any contents (including hidden files)
    contents = list(dir_path.iterdir())

    if len(contents) > 0:
        print(f"❌ Directory not empty ({len(contents)} items):")
        for item in contents:
            print(f"  - {item.name}")
        return False

    try:
        # rmdir only works on empty directories (fail-safe)
        dir_path.rmdir()
        print(f"✅ Deleted empty directory: {dir_path}")
        return True
    except OSError as e:
        print(f"❌ Failed to delete: {e}")
        return False

# Usage
delete_empty_directory(Path("prps/execution_reliability"))
```

**Why rmdir is safer than rm -rf**:
- `rmdir`: Fails if directory not empty (forces investigation)
- `rm -rf`: Deletes everything silently (data loss)
- `rmdir`: Single directory only (no recursion)
- `rm -rf`: Recursive deletion (catastrophic if path wrong)

**Additional context**:
- On btrfs filesystems, empty directories can have non-zero i_size (edge case)
- Network filesystems (CIFS/SMB) may hide files from client-side listing
- Concurrent operations: one process adds files while another deletes

---

## High Priority Gotchas

### 4. Partial Find/Replace from Incomplete File Discovery

**Severity**: High
**Category**: Reference Integrity / Documentation Consistency
**Affects**: Documentation updates across multiple files
**Source**: Feature analysis + codebase patterns

**What it is**:
Updating only known or obvious files without comprehensive grep to find ALL instances. Results in broken references, inconsistent naming, and documentation pointing to non-existent paths. Happens when manually specifying files instead of discovering them programmatically.

**Why it's a problem**:
- **Broken links**: Documentation references old paths that no longer exist
- **Inconsistent naming**: Mix of old and new names confuses developers
- **Silent failures**: grep finds references but they're not in the update list
- **Maintenance debt**: Future developers don't know which naming to use
- **CI/CD breakage**: Automated tools fail on broken references

**How to detect it**:
```bash
# After "completing" find/replace
grep -r "execution_reliability" prps/

# Output shows missed files:
prps/execution_reliability/execution/TASK3_COMPLETION.md:45: in execution_reliability
prps/test_validation_gates.md:12: See prps/execution_reliability.md
.claude/commands/execute-prp.md:89: Example: execution_reliability

# Symptom: Files you forgot to update still reference old naming
```

**How to avoid/fix**:

```bash
# ❌ WRONG - Manual file list (misses files)
sed -i 's/execution_reliability/execution_reliability/g' prps/execution_reliability.md
sed -i 's/execution_reliability/execution_reliability/g' prps/execution_reliability/execution/EXECUTION_SUMMARY.md
# Problem: What about TASK*_COMPLETION.md? .claude/commands/execute-prp.md?

# ✅ RIGHT - Comprehensive grep first, then update ALL files
#!/bin/bash

OLD_TEXT="execution_reliability"
NEW_TEXT="execution_reliability"
SEARCH_DIR="prps/"

echo "=== Step 1: Find ALL files containing '${OLD_TEXT}' ==="
FILES=$(grep -rl "${OLD_TEXT}" "${SEARCH_DIR}" 2>/dev/null)

if [ -z "${FILES}" ]; then
    echo "✅ No instances found (already updated?)"
    exit 0
fi

# Count files and occurrences
FILE_COUNT=$(echo "${FILES}" | wc -l | xargs)
OCCURRENCE_COUNT=$(grep -r "${OLD_TEXT}" "${SEARCH_DIR}" 2>/dev/null | wc -l | xargs)

echo "Found:"
echo "  - Files: ${FILE_COUNT}"
echo "  - Total occurrences: ${OCCURRENCE_COUNT}"
echo ""
echo "Files to update:"
echo "${FILES}" | sed 's/^/  - /'
echo ""

# Step 2: Preview changes
echo "=== Step 2: Preview changes (first 3 files) ==="
echo "${FILES}" | head -3 | while read file; do
    echo "--- ${file} ---"
    grep -n "${OLD_TEXT}" "${file}" | head -5
    echo ""
done

# Step 3: Confirm before executing
read -p "Proceed with replacement? (yes/no): " confirm
if [ "${confirm}" != "yes" ]; then
    echo "❌ Cancelled by user"
    exit 0
fi

# Step 4: Create backups
echo "=== Step 3: Creating backups ==="
echo "${FILES}" | while read file; do
    cp "${file}" "${file}.bak"
done
echo "✅ Backups created (.bak files)"

# Step 5: Execute replacement
echo "=== Step 4: Executing replacement ==="
echo "${FILES}" | while read file; do
    sed -i '' "s/${OLD_TEXT}/${NEW_TEXT}/g" "${file}"  # macOS
    # sed -i "s/${OLD_TEXT}/${NEW_TEXT}/g" "${file}"   # Linux
    echo "  ✅ Updated: ${file}"
done

# Step 6: Verify no instances remain
echo ""
echo "=== Step 5: Verification ==="
REMAINING=$(grep -r "${OLD_TEXT}" "${SEARCH_DIR}" 2>/dev/null)

if [ -z "${REMAINING}" ]; then
    echo "✅ All instances replaced (0 remaining)"
    echo ""
    echo "Cleaning up backups..."
    find "${SEARCH_DIR}" -name "*.bak" -delete
    echo "✅ Backups deleted"
else
    echo "⚠️ Found remaining instances:"
    echo "${REMAINING}"
    echo ""
    echo "Backups preserved in .bak files"
    echo "Run: find ${SEARCH_DIR} -name '*.bak' -delete  # to remove backups"
fi
```

**Python alternative**:
```python
import re
from pathlib import Path
import subprocess

def comprehensive_find_replace(
    directory: Path,
    old_text: str,
    new_text: str,
    dry_run: bool = True
) -> dict:
    """
    Find and replace across ALL files in directory.
    Uses grep to find files, then sed to replace.
    """
    # Step 1: Find ALL files containing old_text
    result = subprocess.run(
        ["grep", "-rl", old_text, str(directory)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {"files": [], "occurrences": 0}

    files = [f for f in result.stdout.strip().split('\n') if f]

    # Step 2: Count total occurrences
    count_result = subprocess.run(
        ["grep", "-r", old_text, str(directory)],
        capture_output=True,
        text=True
    )
    occurrences = len(count_result.stdout.strip().split('\n'))

    print(f"Found: {len(files)} files, {occurrences} occurrences")

    if dry_run:
        print("\nDRY RUN - Files that would be updated:")
        for f in files:
            print(f"  - {f}")
        return {"files": files, "occurrences": occurrences}

    # Step 3: Update all files
    for file_path in files:
        # Use sed for replacement
        subprocess.run(
            ["sed", "-i.bak", f"s/{old_text}/{new_text}/g", file_path]
        )
        print(f"  ✅ Updated: {file_path}")

    # Step 4: Verify
    verify = subprocess.run(
        ["grep", "-r", old_text, str(directory)],
        capture_output=True
    )

    if verify.returncode == 1:  # grep returns 1 when no matches
        print("\n✅ All instances replaced")
        # Clean up backups
        for f in files:
            Path(f"{f}.bak").unlink(missing_ok=True)
    else:
        print(f"\n⚠️ Still found instances:\n{verify.stdout.decode()}")

    return {"files": files, "occurrences": occurrences}

# Usage
comprehensive_find_replace(
    directory=Path("prps/"),
    old_text="execution_reliability",
    new_text="execution_reliability",
    dry_run=True  # Preview first
)

# After review, run with dry_run=False
```

**Why comprehensive grep matters**:
- Finds files in unexpected locations (`.claude/commands/`, other PRPs)
- Catches references in comments, examples, templates
- Ensures atomic update (all or nothing)
- Provides clear audit trail (list of updated files)

---

### 5. Sed Path Delimiter Collision

**Severity**: High
**Category**: Text Processing / Find-Replace Errors
**Affects**: sed commands on file paths
**Source**: https://stackoverflow.com/questions/28402181/replace-many-arbitrary-markdown-links-with-grep-sed

**What it is**:
Using forward slash `/` as sed delimiter when replacing file paths causes syntax errors because paths contain `/`. Requires excessive escaping (`\/home\/user\/path`) making commands unreadable and error-prone.

**Why it's a problem**:
- **Syntax errors**: sed fails with "unterminated s command"
- **Escaping hell**: Every `/` in path must be escaped: `prps\/execution_reliability\/examples`
- **Unreadable**: `sed 's/prps\/execution_reliability/prps\/execution_reliability/g'`
- **Error-prone**: Easy to miss one slash, breaking the command
- **Debugging nightmare**: Complex escaping obscures actual replacement

**How to detect it**:
```bash
# Symptom: sed command fails with cryptic error
sed 's/prps/execution_reliability/prps/execution_reliability/g' file.md
# Error: sed: 1: "s/prps/prp_execution_rel ...": bad flag in substitute command: 'p'

# Or escaping errors
sed 's/prps\/execution_reliability/prps\/execution_reliability/g' file.md
# Works but unreadable and fragile
```

**How to avoid/fix**:

```bash
# ❌ WRONG - Forward slash delimiter (requires escaping)
sed 's/prps\/execution_reliability\/examples/prps\/execution_reliability\/examples/g' file.md
# Unreadable, error-prone

# ❌ WORSE - Forgot to escape one slash (breaks)
sed 's/prps/execution_reliability/examples/prps/execution_reliability/examples/g' file.md
# Error: bad flag in substitute command

# ✅ RIGHT - Use alternative delimiter (| : # @)
# No escaping needed!
sed 's|prps/execution_reliability/examples|prps/execution_reliability/examples|g' file.md

# ✅ ALSO GOOD - Colon delimiter
sed 's:prps/execution_reliability/examples:prps/execution_reliability/examples:g' file.md

# ✅ ALSO GOOD - Hash delimiter
sed 's#prps/execution_reliability/examples#prps/execution_reliability/examples#g' file.md

# All three are equivalent and readable
```

**Complete example for this cleanup**:
```bash
# Replace directory paths in markdown files
OLD_PATH="prps/execution_reliability"
NEW_PATH="prps/execution_reliability"

# ❌ WRONG
sed "s/${OLD_PATH}/${NEW_PATH}/g" file.md
# Fails because OLD_PATH contains slashes

# ❌ WRONG - Manual escaping
sed "s/prps\/execution_reliability/prps\/execution_reliability/g" file.md
# Works but fragile

# ✅ RIGHT - Use | delimiter (clean and readable)
sed "s|${OLD_PATH}|${NEW_PATH}|g" file.md

# Works with variables too
find prps/execution_reliability -name "*.md" -exec sed -i '' "s|${OLD_PATH}|${NEW_PATH}|g" {} \;
```

**Handle multiple path variations**:
```bash
#!/bin/bash
OLD_BASE="execution_reliability"
NEW_BASE="execution_reliability"

# Update all path variations in one pass
find prps/ -name "*.md" -exec sed -i '' \
    -e "s|prps/${OLD_BASE}/|prps/${NEW_BASE}/|g" \
    -e "s|prps/${OLD_BASE}|prps/${NEW_BASE}|g" \
    -e "s|\`${OLD_BASE}\`|\`${NEW_BASE}\`|g" \
    -e "s|${OLD_BASE}|${NEW_BASE}|g" \
    {} \;

# Explanation:
# -e 1: With trailing slash: prps/execution_reliability/
# -e 2: Without trailing slash: prps/execution_reliability
# -e 3: In inline code: `execution_reliability`
# -e 4: Standalone name: execution_reliability
```

**Delimiter choice guide**:
- **`|` pipe**: Best for file paths (rarely used in paths)
- **`:` colon**: Good for URLs (but colons appear in http://)
- **`#` hash**: Good for markdown (but used in headers)
- **`@` at**: Good for emails (but @ appears in email addresses)
- **Choose based on what you're replacing**

---

### 6. BSD vs GNU Sed Incompatibility

**Severity**: High
**Category**: Cross-Platform Compatibility
**Affects**: macOS (BSD sed) vs Linux (GNU sed)
**Source**: https://stackoverflow.com/questions/159367/using-sed-to-find-and-replace

**What it is**:
macOS uses BSD sed, Linux uses GNU sed. The `-i` (in-place edit) flag works differently: BSD requires an argument (backup extension), GNU makes it optional. Using `-ie` creates unwanted files ending in 'e'. Scripts that work on Linux fail on macOS and vice-versa.

**Why it's a problem**:
- **Script portability**: Same command fails on different platforms
- **Unwanted files**: `-ie` creates `file.mde` backup files
- **Subtle bugs**: Script appears to work but creates wrong backups
- **Team friction**: Different team members on Mac/Linux get different results
- **CI/CD issues**: Pipeline works locally but fails on different OS

**How to detect it**:
```bash
# On macOS (BSD sed)
sed -i 's/old/new/g' file.md
# Error: sed: 1: "file.md": invalid command code f

# Using -ie flag (creates unwanted backup)
sed -ie 's/old/new/g' file.md
# Creates: file.md (modified) and file.mde (backup with 'e' appended!)

# After running -ie
ls -la
# file.md
# file.mde  <-- Unwanted backup file
```

**How to avoid/fix**:

```bash
# ❌ WRONG - Works on Linux, fails on macOS
sed -i 's/execution_reliability/execution_reliability/g' file.md
# macOS error: "invalid command code"

# ❌ WRONG - Creates file.mde backup (not file.md.bak)
sed -ie 's/execution_reliability/execution_reliability/g' file.md
# Result: file.md (modified), file.mde (backup) - confusing!

# ✅ RIGHT - Portable across macOS and Linux
# Option 1: Explicit backup with extension (works on both)
sed -i.bak 's/execution_reliability/execution_reliability/g' file.md
# Creates: file.md.bak (both macOS and Linux)

# Option 2: Empty string for no backup (macOS)
sed -i '' 's/execution_reliability/execution_reliability/g' file.md
# Works on macOS, needs adjustment for Linux

# ✅ BEST - Platform detection for full portability
#!/bin/bash
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS (BSD sed)
    SED_BACKUP=(-i '')
else
    # Linux (GNU sed)
    SED_BACKUP=(-i)
fi

# Use detected flags
sed "${SED_BACKUP[@]}" 's/execution_reliability/execution_reliability/g' file.md

# For backups:
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_CMD=(sed -i '.bak')
else
    SED_CMD=(sed -i'.bak')  # Note: no space on Linux
fi

"${SED_CMD[@]}" 's/old/new/g' file.md
```

**Cross-platform wrapper function**:
```bash
#!/bin/bash

portable_sed_replace() {
    local old_text="$1"
    local new_text="$2"
    local file="$3"
    local create_backup="${4:-true}"  # Default: create backup

    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - BSD sed requires backup extension
        if [ "$create_backup" = "true" ]; then
            sed -i '.bak' "s|${old_text}|${new_text}|g" "${file}"
        else
            sed -i '' "s|${old_text}|${new_text}|g" "${file}"
        fi
    else
        # Linux - GNU sed
        if [ "$create_backup" = "true" ]; then
            sed -i'.bak' "s|${old_text}|${new_text}|g" "${file}"
        else
            sed -i "s|${old_text}|${new_text}|g" "${file}"
        fi
    fi

    echo "✅ Updated: ${file}"
}

# Usage
portable_sed_replace \
    "execution_reliability" \
    "execution_reliability" \
    "prps/execution_reliability.md" \
    true  # Create backup

# Or use in loop
find prps/ -name "*.md" | while read file; do
    portable_sed_replace "old" "new" "${file}" false  # No backup
done
```

**Using Perl instead (fully portable)**:
```bash
# Perl is available on both macOS and Linux with consistent syntax
perl -i.bak -pe 's/execution_reliability/execution_reliability/g' file.md
# Works identically on macOS and Linux
# Creates file.md.bak backup

# No backup version
perl -i -pe 's/execution_reliability/execution_reliability/g' file.md

# In find command
find prps/ -name "*.md" -exec perl -i.bak -pe 's|old|new|g' {} \;
```

**Key differences**:
- **macOS**: `-i` requires argument (extension), use `-i ''` for no backup
- **Linux**: `-i` argument optional, use `-i` alone for no backup
- **macOS**: `-ie` creates `file.mde` (e appended to filename)
- **Linux**: `-ie` creates `file.mde` (same issue on Linux too!)
- **Safe pattern**: Always use `-i.bak` with explicit extension (portable)

---

### 7. Markdown Link Variations Breaking References

**Severity**: High
**Category**: Reference Integrity / Documentation
**Affects**: Markdown files with internal links
**Source**: https://www.docstomarkdown.pro/relative-links-in-markdown/

**What it is**:
Markdown supports multiple link syntax variations: `[text](path)`, `[text](path/)`, `path` (bare), `./path`, `../path`. Simple find/replace only catches one variation, leaving other references broken. Relative links break when files move unless all variations are updated.

**Why it's a problem**:
- **Broken links**: Some link variations not updated, result in 404s
- **Inconsistent docs**: Mix of old and new paths confuses readers
- **CI/CD failures**: Broken link checkers fail builds
- **Navigation breaks**: GitHub/GitLab markdown rendering shows dead links
- **SEO impact**: Broken internal links hurt documentation discoverability

**How to detect it**:
```bash
# Search reveals multiple path variations in markdown
grep -r "execution_reliability" prps/*.md

# Output shows different formats:
# [docs](prps/execution_reliability/planning/feature-analysis.md)
# [docs](prps/execution_reliability/planning/)
# See prps/execution_reliability.md
# `prps/execution_reliability/`
# ../execution_reliability/examples/

# Simple find/replace misses variations with/without trailing slashes
```

**How to avoid/fix**:

```bash
# ❌ WRONG - Only catches one variation
sed 's/execution_reliability/execution_reliability/g' file.md
# Misses: trailing slashes, relative paths, inline code

# ✅ RIGHT - Update all variations
#!/bin/bash

OLD_NAME="execution_reliability"
NEW_NAME="execution_reliability"

# Multiple sed expressions to catch all variations
find prps/ -name "*.md" -exec sed -i '' \
    -e "s|prps/${OLD_NAME}/|prps/${NEW_NAME}/|g" \
    -e "s|prps/${OLD_NAME})|prps/${NEW_NAME})|g" \
    -e "s|prps/${OLD_NAME}|prps/${NEW_NAME}|g" \
    -e "s|\.\./${OLD_NAME}/|\.\\./${NEW_NAME}/|g" \
    -e "s|\./${OLD_NAME}/|\.\/${NEW_NAME}/|g" \
    -e "s|\`${OLD_NAME}\`|\`${NEW_NAME}\`|g" \
    -e "s|${OLD_NAME}\.md|${NEW_NAME}.md|g" \
    -e "s|${OLD_NAME}|${NEW_NAME}|g" \
    {} \;

# Explanation of each pattern:
# 1. With trailing slash: prps/execution_reliability/
# 2. Before closing paren: prps/execution_reliability)
# 3. Without trailing slash: prps/execution_reliability
# 4. Relative parent: ../execution_reliability/
# 5. Relative current: ./execution_reliability/
# 6. In inline code: `execution_reliability`
# 7. Filename references: execution_reliability.md
# 8. Standalone (last, most general): execution_reliability
```

**Python approach with regex**:
```python
import re
from pathlib import Path

def update_markdown_references(file_path: Path, old_name: str, new_name: str):
    """
    Update all markdown reference variations in a file.
    """
    content = file_path.read_text()
    original = content

    # Pattern 1: Markdown links [text](path)
    content = re.sub(
        rf'\[(.*?)\]\(([^)]*){old_name}([^)]*)\)',
        rf'[\1](\2{new_name}\3)',
        content
    )

    # Pattern 2: Relative paths with slashes
    content = content.replace(f"prps/{old_name}/", f"prps/{new_name}/")
    content = content.replace(f"../{old_name}/", f"../{new_name}/")
    content = content.replace(f"./{old_name}/", f"./{new_name}/")

    # Pattern 3: Without trailing slash
    content = content.replace(f"prps/{old_name}", f"prps/{new_name}")

    # Pattern 4: Inline code
    content = content.replace(f"`{old_name}`", f"`{new_name}`")

    # Pattern 5: File extensions
    content = content.replace(f"{old_name}.md", f"{new_name}.md")
    content = content.replace(f"{old_name}.py", f"{new_name}.py")

    # Pattern 6: Standalone (most general, do last)
    content = content.replace(old_name, new_name)

    # Only write if changed
    if content != original:
        file_path.write_text(content)
        print(f"✅ Updated: {file_path}")
        return True
    else:
        print(f"ℹ️ No changes: {file_path}")
        return False

# Usage
for md_file in Path("prps/").rglob("*.md"):
    update_markdown_references(
        md_file,
        "execution_reliability",
        "execution_reliability"
    )
```

**Validation - Check all links after update**:
```bash
#!/bin/bash
# Extract all file paths from markdown and verify they exist

check_markdown_links() {
    local md_file="$1"

    # Extract markdown links: [text](path)
    grep -oE '\[.*\]\([^)]+\)' "${md_file}" | \
        grep -oE '\([^)]+\)' | \
        tr -d '()' | \
        while read link; do
            # Skip URLs
            if [[ "${link}" =~ ^https?:// ]]; then
                continue
            fi

            # Resolve relative path
            local base_dir=$(dirname "${md_file}")
            local full_path="${base_dir}/${link}"

            if [ ! -e "${full_path}" ]; then
                echo "❌ Broken link in ${md_file}: ${link}"
            fi
        done
}

# Check all markdown files
find prps/ -name "*.md" | while read file; do
    check_markdown_links "${file}"
done
```

**Use automated link checker**:
```bash
# Install markdown-link-check (Node.js)
npm install -g markdown-link-check

# Check all markdown files
find prps/ -name "*.md" -exec markdown-link-check {} \;

# Output shows broken links with 404 errors
```

---

### 8. Shell mv Instead of git mv (History Loss)

**Severity**: High
**Category**: Git History Loss
**Affects**: File move operations in git repositories
**Source**: Feature analysis + git best practices

**What it is**:
Using shell `mv` or Python `shutil.move()` instead of `git mv` for file operations in a git repository. Git sees the operation as "file deleted" + "new file added" instead of "file renamed", breaking git history tracking even if rename detection eventually works.

**Why it's a problem**:
- **Lost git blame**: Can't see who wrote which lines historically
- **Broken git log --follow**: File history stops at the move
- **Attribution errors**: Mover appears as author of entire file
- **Harder code review**: Diff shows entire file as new, not just changes
- **Debugging impact**: Can't trace when bugs were introduced
- **Rollback harder**: Can't revert to pre-rename versions easily

**How to detect it**:
```bash
# After using shell mv instead of git mv
git status

# ❌ BAD - Shows as delete + add (not rename)
# Changes not staged for commit:
#   deleted:    prps/execution_reliability.md
#
# Untracked files:
#   prps/execution_reliability.md

# ✅ GOOD - Shows as rename
# Changes to be committed:
#   renamed:    prps/execution_reliability.md -> prps/execution_reliability.md

# Check if history follows across rename
git log --follow prps/execution_reliability.md
# If history stops at move, rename detection failed
```

**How to avoid/fix**:

```bash
# ❌ WRONG - Shell mv (loses history tracking)
mv prps/execution_reliability.md prps/execution_reliability.md
git add prps/execution_reliability.md
git rm prps/execution_reliability.md
# Result: Git sees "deleted + added", not "renamed"

# ❌ WRONG - Python shutil (same problem)
import shutil
shutil.move("prps/execution_reliability.md", "prps/execution_reliability.md")
# Then: git add/rm (breaks history)

# ✅ RIGHT - Use git mv
git mv prps/execution_reliability.md prps/execution_reliability.md
# Git immediately records this as a rename in the index

# ✅ RIGHT - Directory moves
git mv prps/execution_reliability/examples prps/execution_reliability/
# Note: Destination should be parent directory, not full path

# ✅ RIGHT - Python subprocess calling git mv
import subprocess
from pathlib import Path

def git_move(source: Path, dest: Path) -> bool:
    """Use git mv to preserve history."""
    try:
        subprocess.run(
            ["git", "mv", str(source), str(dest)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Git moved: {source} → {dest}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git mv failed: {e.stderr}")
        return False

# Usage
git_move(
    Path("prps/execution_reliability.md"),
    Path("prps/execution_reliability.md")
)
```

**If you already used shell mv, fix it**:
```bash
# Situation: You used mv instead of git mv and committed
# The damage is done, but you can improve detection

# Option 1: Recommit with git mv (if not yet pushed)
git reset HEAD~1  # Undo last commit
git restore --staged .  # Unstage all
git restore prps/  # Restore files to before move

# Now use git mv correctly
git mv prps/execution_reliability.md prps/execution_reliability.md
git commit -m "Rename: execution_reliability.md → execution_reliability.md"

# Option 2: If already pushed, lower similarity threshold
# Helps git detect rename with less stringent requirements
git log --follow -M40% prps/execution_reliability.md
# -M40% = 40% similarity threshold (default is 50%)
```

**Verification checklist**:
```bash
# 1. Check git status shows "renamed" not "deleted + added"
git status
# Should show: renamed: old_path -> new_path

# 2. Verify history follows across rename
git log --follow --oneline prps/execution_reliability.md
# Should show commits from before rename

# 3. Check git blame works
git blame prps/execution_reliability.md
# Should show original authors, not all "person who moved it"

# 4. Verify rename in commit
git show HEAD
# Should show: rename from/to, not delete/create
```

**Why git mv is non-negotiable**:
- Updates git index immediately (recorded as rename)
- Helps rename detection (though git still uses heuristics)
- Best practice in all git documentation
- Required for maintaining git blame continuity
- Essential for code archaeology and debugging

---

## Medium Priority Gotchas

### 9. Case-Sensitive Filesystems Breaking Cross-Platform

**Severity**: Medium
**Category**: Cross-Platform Compatibility
**Affects**: macOS (case-insensitive) vs Linux (case-sensitive)
**Source**: Git documentation + common Unix pitfall

**What it is**:
macOS and Windows have case-insensitive filesystems by default, while Linux is case-sensitive. Renaming `file.txt` to `File.txt` works on macOS but creates issues: git sees both files on Linux, file conflicts in version control, and confusion about canonical naming.

**Why it's confusing**:
- **Platform-specific behavior**: Works on dev machine (macOS), fails in production (Linux)
- **Git confusion**: `git mv file.txt File.txt` sometimes creates weird states
- **CI/CD differences**: Tests pass locally, fail in Docker/Linux CI
- **Team friction**: Some developers see one file, others see two
- **Hard to debug**: "Works on my machine" syndrome

**How to handle it**:

```bash
# ❌ PROBLEMATIC - Case-only rename on macOS
git mv prps/execution_reliability.md prps/Execution_Reliability.md
# macOS: Works fine
# Linux: May see both files or git confusion

# ✅ BETTER - Two-step rename for case-only changes
git mv prps/execution_reliability.md prps/temp_execution_reliability.md
git mv prps/temp_execution_reliability.md prps/Execution_Reliability.md
# Works consistently on both macOS and Linux

# ✅ BEST - Avoid case-only renames altogether
# Use consistent naming (lowercase with underscores or hyphens)
# Good: execution_reliability.md, user-auth.md
# Avoid: ExecutionReliability.md, User_Auth.md
```

**For this cleanup**: No case-only renames, so not applicable. But good to know if naming standards involve capitalization.

---

### 10. Forgetting to Update Test Script Reference

**Severity**: Medium
**Category**: Reference Integrity
**Affects**: TASK8_COMPLETION.md referencing relocated test script
**Source**: Feature analysis

**What it is**:
Moving `test_validation_gates_script.py` from root to `prps/test_validation_gates/test_script.py` without updating the reference in `TASK8_COMPLETION.md`. Results in broken reference when someone tries to run the test script from documentation.

**Why it's a problem**:
- **Broken instructions**: Documentation says "run test_validation_gates_script.py" but file doesn't exist
- **User confusion**: "File not found" errors when following docs
- **Diminished trust**: Broken documentation undermines confidence in project
- **Maintenance debt**: Future developers don't know where to find the script

**How to detect it**:
```bash
# After moving test script
grep -r "test_validation_gates_script.py" prps/

# Output shows stale reference:
prps/execution_reliability/execution/TASK8_COMPLETION.md:89: Run: python test_validation_gates_script.py
# But file no longer exists at root
```

**How to handle**:
```bash
# Update reference after moving file
sed -i '' 's|test_validation_gates_script\.py|prps/test_validation_gates/test_script.py|g' \
    prps/execution_reliability/execution/TASK8_COMPLETION.md

# Verify no old references remain
grep -r "test_validation_gates_script" prps/
# Should return 0 results

# Test the new path works
python prps/test_validation_gates/test_script.py
# Should run successfully
```

---

### 11. Git Status Clutter from Backup Files

**Severity**: Medium
**Category**: Repository Cleanliness
**Affects**: All backup file operations
**Source**: Feature analysis + best practices

**What it is**:
Creating `.bak` backup files during find/replace operations and forgetting to clean them up or add to `.gitignore`. Results in untracked files cluttering `git status`, potential accidental commits of backup files, and repository bloat.

**Why it's annoying**:
- **Git status pollution**: Dozens of `.bak` files show as untracked
- **Accidental commits**: `git add .` includes backups unintentionally
- **Repository bloat**: Backup files committed to history
- **Confusion**: Are `.bak` files important or safe to delete?

**How to handle**:
```bash
# ✅ Add to .gitignore BEFORE creating backups
echo "*.bak" >> .gitignore
git add .gitignore
git commit -m "Ignore backup files"

# Clean up backups after successful validation
find prps/ -name "*.bak" -delete

# Or if you want to review backups first
find prps/ -name "*.bak" -exec ls -lh {} \;
# Then delete after review
find prps/ -name "*.bak" -delete
```

**Better: Use temporary directory for backups**:
```bash
#!/bin/bash
BACKUP_DIR=$(mktemp -d)
echo "Backups in: ${BACKUP_DIR}"

# Create backups in temp directory
find prps/ -name "*.md" | while read file; do
    cp "${file}" "${BACKUP_DIR}/$(basename ${file}).bak"
done

# Perform replacements
# ...

# If successful, remove temp directory
rm -rf "${BACKUP_DIR}"

# If failed, restore from temp directory
# cp "${BACKUP_DIR}"/*.bak prps/execution_reliability/
```

---

### 12. Network Filesystem Hidden Files

**Severity**: Medium
**Category**: Directory Operations
**Affects**: CIFS/SMB/NFS mounted filesystems
**Source**: Web search (directory deletion pitfalls)

**What it is**:
On network filesystems (CIFS, SMB, NFS), hidden files may exist that are only visible from the fileserver, not from client-side listings. Directory appears empty on client but deletion fails because server sees files.

**Why it's confusing**:
- **Appears empty**: `ls -la` shows no files
- **Deletion fails**: `rmdir` says "directory not empty"
- **Client-server mismatch**: Client and server have different views
- **Hard to debug**: Files invisible to standard tools

**How to handle**:
```bash
# ✅ More robust empty check
# Use find instead of ls (catches more cases)
find dir/ -mindepth 1 -maxdepth 1 | wc -l

# If still shows 0 but deletion fails, might be network FS issue
# Access from server side to check for hidden files

# Workaround: Use rm -rf if directory is on network FS
# (Not recommended for local filesystems)
```

**For this cleanup**: Unlikely to affect local git repository, but worth knowing for production deployments.

---

## Gotcha Checklist for Implementation

Before marking cleanup complete, verify these gotchas are addressed:

- [ ] **Git history**: Used `git mv` for all file operations (not shell `mv`)
- [ ] **Separate commits**: Renamed files in separate commit from content changes
- [ ] **TOCTOU safety**: Used try-except pattern, not check-then-use
- [ ] **Comprehensive find/replace**: Grepped for ALL instances before updating
- [ ] **Path delimiters**: Used `|` or `:` delimiter in sed (not `/`)
- [ ] **Cross-platform sed**: Used portable sed syntax (`.bak` extension)
- [ ] **Link variations**: Updated all markdown link formats (trailing slash, relative, inline code)
- [ ] **Empty verification**: Checked directory empty with `find` before deletion
- [ ] **Reference updates**: Updated test script reference in TASK8_COMPLETION.md
- [ ] **Backup cleanup**: Removed `.bak` files after validation
- [ ] **Validation**: Ran comprehensive validation (0 old references remain)
- [ ] **Git status**: Clean git status (renamed, not deleted+added)

---

## Testing Checklist

**Pre-flight validation**:
```bash
# All sources exist
[ -d "prps/execution_reliability/examples" ] && echo "✅" || echo "❌"
[ -d "prps/execution_reliability/planning" ] && echo "✅" || echo "❌"
[ -f "prps/execution_reliability.md" ] && echo "✅" || echo "❌"
[ -f "test_validation_gates_script.py" ] && echo "✅" || echo "❌"
```

**Post-operation validation**:
```bash
# Old directories/files removed
[ ! -d "prps/execution_reliability" ] && echo "✅ Old dir removed" || echo "❌ Still exists"
[ ! -f "test_validation_gates_script.py" ] && echo "✅ Test script moved" || echo "❌ Still in root"

# New structure exists
[ -d "prps/execution_reliability/examples" ] && echo "✅" || echo "❌"
[ -d "prps/execution_reliability/planning" ] && echo "✅" || echo "❌"
[ -f "prps/execution_reliability.md" ] && echo "✅" || echo "❌"

# No old references
REFS=$(grep -r "execution_reliability" prps/ 2>/dev/null | wc -l)
[ "${REFS}" -eq "0" ] && echo "✅ 0 old references" || echo "❌ Found ${REFS} references"

# Git status shows renames
git status | grep -q "renamed:" && echo "✅ Git tracked renames" || echo "❌ Not tracked as renames"
```

---

## Sources Referenced

### From Web Research
- **Git rename detection**: https://stackoverflow.com/questions/2314652/is-it-possible-to-move-rename-files-in-git-and-maintain-their-history
- **TOCTOU vulnerabilities**: https://cwe.mitre.org/data/definitions/367.html
- **TOCTOU mitigation**: https://wiki.sei.cmu.edu/confluence/display/c/FIO45-C.+Avoid+TOCTOU+race+conditions+while+accessing+files
- **Sed path delimiters**: https://stackoverflow.com/questions/28402181/replace-many-arbitrary-markdown-links-with-grep-sed
- **Directory deletion safety**: https://askubuntu.com/questions/566474/why-do-i-get-directory-not-empty-when-i-try-to-remove-an-empty-directory
- **Markdown link integrity**: https://www.docstomarkdown.pro/relative-links-in-markdown/
- **Git mv documentation**: https://git-scm.com/docs/git-mv

### From Codebase Analysis
- **Feature analysis**: `prps/cleanup_execution_reliability_artifacts/planning/feature-analysis.md`
- **Codebase patterns**: `prps/cleanup_execution_reliability_artifacts/planning/codebase-patterns.md`
- **Documentation links**: `prps/cleanup_execution_reliability_artifacts/planning/documentation-links.md`
- **Code examples**: `prps/cleanup_execution_reliability_artifacts/examples/`

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include critical gotchas** in "Known Gotchas & Library Quirks" section:
   - Gotcha #1 (git history loss) is the most critical
   - Gotcha #2 (TOCTOU) affects security-conscious implementations
   - Gotcha #4 (partial find/replace) is most likely to occur

2. **Reference solutions** in "Implementation Blueprint":
   - Use separate commits for renames vs content changes
   - Use comprehensive grep before find/replace
   - Use alternative sed delimiters for paths
   - Validate with `find` before directory deletion

3. **Add detection tests** to validation gates:
   - Verify `git status` shows "renamed" not "deleted+added"
   - Run `git log --follow` to confirm history preservation
   - Grep for 0 instances of old naming
   - Test all markdown links resolve

4. **Warn about platform differences**:
   - BSD vs GNU sed incompatibility
   - Case-sensitive filesystem differences
   - Network filesystem hidden file issues

5. **Provide validation script** incorporating gotcha checks:
   - Check git rename detection worked
   - Verify no TOCTOU check-then-use patterns
   - Confirm all reference variations updated
   - Validate directory truly empty before deletion

## Confidence Assessment

**Gotcha Coverage**: 9/10
- **Security**: Comprehensive (TOCTOU, file operations, git safety)
- **Git History**: Comprehensive (rename detection, attribution, history loss)
- **Find/Replace**: Comprehensive (partial updates, delimiter issues, link variations)
- **Common Mistakes**: Comprehensive (directory deletion, backup files, platform differences)

**Gaps**:
- Template location confusion (covered in other docs, not file-operation specific)
- Archive vs delete workflows (out of scope for this cleanup)
- Some edge cases specific to exotic filesystems (btrfs, network FS)

**Sources**:
- 7 web search results with authoritative sources (Stack Overflow, CWE, Git docs)
- 4 codebase analysis documents
- Comprehensive coverage of git, sed, file operations, and markdown gotchas

**Confidence**: HIGH - All major gotchas identified with concrete solutions and detection methods. Each gotcha includes anti-patterns, proper patterns, and validation steps.
