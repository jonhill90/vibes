# Known Gotchas: Codex Directory Reorganization

## Overview

This document identifies critical issues, common mistakes, security vulnerabilities, and performance concerns when reorganizing bash scripts and test files using git operations. All gotchas include **practical solutions** with code examples. This reorganization moves 10 files (7 scripts, 3 tests, 1 fixtures directory) from scattered locations to unified `.codex/` structure while preserving git history.

**Research Sources**: Web searches for git mv pitfalls, bash sed escaping issues, sourcing gotchas, command injection vulnerabilities, and migration script validation blind spots. Local codebase patterns from cleanup PRP and existing Codex scripts.

---

## Critical Gotchas

### 1. Git History Loss - Mixing Rename with Content Changes

**Severity**: Critical
**Category**: Data Loss / Git History
**Affects**: All git mv operations
**Source**: https://stackoverflow.com/questions/10828267/can-git-restructure-my-folders-without-losing-history

**What it is**:
Git doesn't store hard history of renames - it uses heuristics to detect renames by comparing deleted and added files. If you move a file AND modify its content in the same commit, git may fail to detect the rename, causing the file to appear as "deleted + newly created" instead of "renamed", breaking `git log --follow` and `git blame`.

**Why it's a problem**:
- Loses complete commit history (can't see who wrote each line)
- Breaks `git blame` (shows wrong author for all lines)
- Makes bisecting bugs impossible (history appears to start fresh)
- Prevents tracking down when bugs were introduced

**How to detect it**:
- `git status` shows "deleted: old/path" and "new file: new/path" instead of "renamed:"
- `git log --follow new/path` only shows commits after the move
- `git show --stat <commit>` shows large deletions and additions instead of rename

**How to avoid/fix**:

```bash
# ❌ WRONG - Move and modify in same commit (BREAKS HISTORY)
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
# Then immediately edit the file
sed -i 's/old_pattern/new_pattern/' .codex/scripts/parallel-exec.sh
git add .codex/scripts/parallel-exec.sh
git commit -m "Reorganize and update parallel-exec.sh"
# Result: Git sees this as delete + create, NOT rename

# ✅ RIGHT - Separate moves from content changes (PRESERVES HISTORY)
# Step 1: Move files ONLY (no content changes)
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh
git commit -m "Move: parallel-exec.sh to .codex/scripts/"

# Step 2: Verify history preserved
git log --follow --oneline .codex/scripts/parallel-exec.sh
# Should show commits before the move

# Step 3: Make content changes in SEPARATE commit (if needed)
sed -i 's/old_pattern/new_pattern/' .codex/scripts/parallel-exec.sh
git commit -am "Update: parallel-exec.sh path references"

# Why this works:
# Git compares file content hashes between commits. When you move without
# changing content, hashes match and rename is detected. Content changes
# in separate commit don't affect rename detection.
```

**Testing for this vulnerability**:
```bash
# After migration, verify each moved file retains history
for file in .codex/scripts/*.sh; do
    echo "Checking: $file"
    commit_count=$(git log --follow --oneline "$file" | wc -l)
    if [ "$commit_count" -lt 2 ]; then
        echo "❌ HISTORY LOST: $file only has $commit_count commits"
    else
        echo "✅ History preserved: $file has $commit_count commits"
    fi
done
```

**Additional Resources**:
- https://stackoverflow.com/questions/2314652/is-it-possible-to-move-rename-files-in-git-and-maintain-their-history
- https://linuxctl.com/p/git-preserve-history-when-moving-files/

---

### 2. Similarity Threshold Failure - Large Content Changes

**Severity**: Critical
**Category**: Git History
**Affects**: Files modified heavily during reorganization
**Source**: https://stackoverflow.com/questions/72165668/losing-history-when-moving-files-with-git

**What it is**:
Git's rename detection requires >50% similarity between old and new file content (default threshold). If you refactor a script significantly while moving it, git won't recognize it as the same file, even when using `git mv`.

**Why it's a problem**:
- History appears to start fresh after move
- Can't track evolution of complex functions
- Makes code review confusing (massive "changes")
- Prevents effective debugging with bisect

**How to detect it**:
- `git log --follow` shows fewer commits than expected
- `git show --stat <commit>` shows file as 100% new
- `git diff --summary <commit>` doesn't show "rename" line
- Running `git log --follow -M50% <file>` shows different results than default

**How to avoid/fix**:

```bash
# ❌ WRONG - Heavy refactoring during move
git mv scripts/codex/quality-gate.sh .codex/scripts/quality-gate.sh
# Then refactor 60% of the file
sed -i 's/old_api/new_api/g' .codex/scripts/quality-gate.sh
# Add new functions, remove old ones
# ... major changes ...
git commit -am "Move and refactor quality-gate.sh"
# Result: <50% similarity, rename not detected

# ✅ RIGHT - Staged approach for refactoring
# Phase 1: Move without ANY content changes
git mv scripts/codex/quality-gate.sh .codex/scripts/quality-gate.sh
git commit -m "Move: quality-gate.sh to .codex/scripts/ (no changes)"

# Phase 2: Small incremental changes across multiple commits
# Commit 2: Update one pattern
sed -i 's/old_api_v1/new_api_v1/g' .codex/scripts/quality-gate.sh
git commit -am "Update: quality-gate API v1 calls"

# Commit 3: Update another pattern
sed -i 's/old_api_v2/new_api_v2/g' .codex/scripts/quality-gate.sh
git commit -am "Update: quality-gate API v2 calls"

# Commit 4: Add new functionality
# ... incremental changes ...
git commit -am "Add: new quality checks"

# Why this works:
# Each commit has >50% similarity to previous, so full history preserved
```

**Adjusting similarity threshold** (if needed):
```bash
# Check history with different similarity thresholds
git log --follow -M40% .codex/scripts/quality-gate.sh  # More lenient (40%)
git log --follow -M70% .codex/scripts/quality-gate.sh  # More strict (70%)

# If history lost, you can rewrite commit to split it
git reset HEAD~1  # Undo last commit (keep changes staged)
# Then create separate commits as shown above
```

**Additional Resources**:
- https://git-scm.com/docs/git-log (`-M` option documentation)
- https://gist.github.com/ajaegers/2a8d8cbf51e49bcb17d5

---

### 3. Command Injection via Unvalidated Paths

**Severity**: Critical
**Category**: Security
**Affects**: Migration script using dynamic paths
**Source**: https://www.akamai.com/blog/security-research/kubernetes-gitsync-command-injection-defcon

**What it is**:
If migration script constructs `git mv` commands using unvalidated input (e.g., file paths from user input, environment variables, or external files), an attacker can inject shell commands via malicious path names containing special characters like `;`, `|`, `$()`, or backticks.

**Why it's a problem**:
- Arbitrary command execution on developer machine
- Potential data exfiltration or malware installation
- Could affect CI/CD systems running migration
- Difficult to detect after compromise

**How to detect it**:
- Migration script uses variables in commands without quotes
- Paths constructed from user input or env vars
- Use of `eval` or unquoted command substitution
- No input validation before git operations

**How to avoid/fix**:

```bash
# ❌ VULNERABLE - Unquoted path allows injection
# If SOURCE contains "; rm -rf /" this executes both commands
git mv $SOURCE $DEST
# Result: Command injection vulnerability

# ❌ VULNERABLE - Even with quotes, eval is dangerous
SOURCE="scripts/codex/file.sh"
eval "git mv $SOURCE .codex/scripts/file.sh"
# Attacker could set SOURCE="x.sh; malicious_command"

# ✅ SECURE - Always quote variables and validate input
move_file_securely() {
    local source="$1"
    local dest="$2"

    # Validation 1: No command substitution characters
    if [[ "$source" =~ [\$\`\;] ]] || [[ "$dest" =~ [\$\`\;] ]]; then
        echo "❌ ERROR: Invalid characters in path" >&2
        return 1
    fi

    # Validation 2: Path exists and is a regular file
    if [ ! -f "$source" ]; then
        echo "❌ ERROR: Source file does not exist: $source" >&2
        return 1
    fi

    # Validation 3: Destination parent directory exists
    local dest_dir="$(dirname "$dest")"
    if [ ! -d "$dest_dir" ]; then
        echo "❌ ERROR: Destination directory does not exist: $dest_dir" >&2
        return 1
    fi

    # Validation 4: Paths are within expected directories
    if [[ ! "$source" =~ ^scripts/codex/ ]] && [[ ! "$source" =~ ^tests/codex/ ]]; then
        echo "❌ ERROR: Source path outside allowed directories: $source" >&2
        return 1
    fi

    # Execute with properly quoted variables (prevents injection)
    git mv "$source" "$dest"

    # Additional safety: Verify operation succeeded
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: git mv failed for $source" >&2
        return 1
    fi

    echo "✅ Moved: $source → $dest"
}

# Use array instead of string for file list (prevents word splitting attacks)
declare -a FILE_MOVES=(
    "scripts/codex/parallel-exec.sh:.codex/scripts/parallel-exec.sh"
    "scripts/codex/codex-generate-prp.sh:.codex/scripts/codex-generate-prp.sh"
)

for move_pair in "${FILE_MOVES[@]}"; do
    IFS=':' read -r source dest <<< "$move_pair"
    move_file_securely "$source" "$dest" || exit 1
done

# Why this works:
# 1. Input validation rejects malicious characters
# 2. Quoting prevents variable expansion exploits
# 3. Array usage prevents word splitting attacks
# 4. Explicit error checking catches failures
```

**Security checklist**:
```bash
# Before running migration script, verify:
# 1. All variables quoted in git commands
grep -n 'git mv \$' migrate.sh  # Should return nothing

# 2. No eval usage
grep -n 'eval' migrate.sh  # Should return nothing

# 3. Input validation present
grep -n 'if.*\[\[.*=~' migrate.sh  # Should find validation checks

# 4. Paths are hardcoded or validated
grep -n 'FILE_MOVES' migrate.sh  # Should use declare -a
```

**Additional Resources**:
- https://github.com/payloadbox/command-injection-payload-list
- https://www.nodejs-security.com/blog/flawed-git-promises-library-on-npm-leads-to-command-injection-vulnerability

---

## High Priority Gotchas

### 1. sed -i Syntax Differs: macOS vs Linux

**Severity**: High
**Category**: Portability / Cross-Platform
**Affects**: Path update sed commands
**Source**: https://stackoverflow.com/questions/4247068/sed-command-with-i-option-failing-on-mac-but-works-on-linux

**What it is**:
macOS uses BSD sed, which requires a backup extension argument after `-i` (even if empty), while GNU sed (Linux) makes the extension optional. Scripts using `sed -i` without handling this difference will fail on one platform or the other.

**Why it's a problem**:
- Migration script fails on macOS or Linux depending on syntax used
- Can't run same script across development environments
- Creates confusion in team with mixed OS usage
- Breaks CI/CD if platform differs from dev environment

**How to detect it**:
- Error: `sed: 1: "file.sh": invalid command code f` (macOS)
- Error: `sed: -e expression #1, char X: unterminated 's' command` (varies)
- Script works on one developer's machine but fails on another's

**How to avoid/fix**:

```bash
# ❌ WRONG - Linux-only syntax (fails on macOS)
find .codex/tests -name "*.sh" -exec sed -i 's|scripts/codex/|.codex/scripts/|g' {} \;
# macOS error: sed: 1: "test_file.sh": invalid command code t

# ❌ WRONG - macOS-only syntax (fails on Linux with different behavior)
find .codex/tests -name "*.sh" -exec sed -i '' 's|scripts/codex/|.codex/scripts/|g' {} \;
# Linux: Creates backup files named '' (empty string filename issues)

# ✅ RIGHT - Cross-platform compatible approach
# Option 1: Detect OS and use appropriate syntax
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS (BSD sed)
    SED_INPLACE="sed -i ''"
else
    # Linux (GNU sed)
    SED_INPLACE="sed -i"
fi

find .codex/tests -name "*.sh" -exec $SED_INPLACE 's|scripts/codex/|.codex/scripts/|g' {} \;

# Option 2: Use backup extension on both platforms (safer)
# Create .bak files, then remove after verification
find .codex/tests -name "*.sh" -exec sed -i.bak 's|scripts/codex/|.codex/scripts/|g' {} \;

# Verify changes before removing backups
if grep -r "scripts/codex/" .codex/tests/*.sh 2>/dev/null; then
    echo "❌ ERROR: Old paths still exist, restoring backups"
    find .codex/tests -name "*.bak" -exec bash -c 'mv "$1" "${1%.bak}"' _ {} \;
    exit 1
else
    echo "✅ Path updates verified, removing backups"
    find .codex/tests -name "*.bak" -delete
fi

# Option 3: Use perl instead (identical syntax on both platforms)
find .codex/tests -name "*.sh" -exec perl -pi -e 's|scripts/codex/|.codex/scripts/|g' {} \;

# Why this works:
# - Option 1: Adapts to platform automatically
# - Option 2: Creates safety net with backups, works on both platforms
# - Option 3: Perl has consistent syntax across platforms
```

**Testing cross-platform compatibility**:
```bash
# Test script on both platforms
docker run --rm -v "$PWD:/work" -w /work ubuntu:latest bash migrate.sh  # Linux
# Then test on macOS directly
bash migrate.sh  # macOS

# Or use shellcheck for portability warnings
shellcheck migrate.sh
# Look for: "SC2039: In POSIX sh, sed -i is undefined"
```

**Additional Resources**:
- https://stackoverflow.com/questions/4247068/sed-command-with-i-option-failing-on-mac-but-works-on-linux
- https://superuser.com/questions/307165/newlines-in-sed-on-mac-os-x

---

### 2. Slash Delimiter Conflicts in sed Path Replacements

**Severity**: High
**Category**: Path Update Errors
**Affects**: sed commands replacing paths
**Source**: https://stackoverflow.com/questions/12061410/how-to-replace-a-path-with-another-path-in-sed

**What it is**:
When using `/` as sed's delimiter (e.g., `s/old/new/g`), paths containing `/` characters must be escaped with backslashes, creating unreadable commands like `s/scripts\/codex\//\.codex\/scripts\//g`. Missing even one escape breaks the command.

**Why it's a problem**:
- Commands become error-prone and hard to read
- Easy to miss escaping a single slash
- Difficult to debug when command fails
- Makes maintenance nightmarish

**How to detect it**:
- Error: `sed: -e expression #1, char X: unterminated 's' command`
- sed command fails silently (no replacements made)
- Command line becomes a backslash nightmare

**How to avoid/fix**:

```bash
# ❌ WRONG - Using / delimiter requires escaping every slash
sed -i 's/scripts\/codex\//\.codex\/scripts\//g' test_file.sh
sed -i 's/${REPO_ROOT}\/scripts\/codex\//${REPO_ROOT}\/\.codex\/scripts\//g' test_file.sh
# Hard to read, easy to make mistakes

# ❌ WRONG - Forgetting to escape one slash breaks everything
sed -i 's/scripts\/codex/.codex\/scripts/g' test_file.sh
# Error: unterminated 's' command (missing escape on .codex)

# ✅ RIGHT - Use alternative delimiter (pipe, hash, underscore, etc.)
# Pipe delimiter (most readable for paths)
sed -i 's|scripts/codex/|.codex/scripts/|g' test_file.sh
sed -i 's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' test_file.sh

# Hash delimiter (also works well)
sed -i 's#scripts/codex/#.codex/scripts/#g' test_file.sh

# Underscore delimiter (if paths contain | and #)
sed -i 's_scripts/codex/_.codex/scripts/_g' test_file.sh

# Why this works:
# Alternative delimiters don't appear in paths, so no escaping needed
# Commands are readable and maintainable
# Less error-prone during editing
```

**Complete path update pattern**:
```bash
# Update all test files with readable pipe delimiter
echo "Updating path references in test files..."

# Pattern 1: ${REPO_ROOT}/scripts/codex/ → ${REPO_ROOT}/.codex/scripts/
find .codex/tests -name "*.sh" -type f -exec sed -i.bak \
    's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' {} \;

# Pattern 2: ${REPO_ROOT}/tests/codex/ → ${REPO_ROOT}/.codex/tests/
find .codex/tests -name "*.sh" -type f -exec sed -i.bak \
    's|${REPO_ROOT}/tests/codex/|${REPO_ROOT}/.codex/tests/|g' {} \;

# Pattern 3: Unquoted paths (without ${REPO_ROOT})
find .codex/tests -name "*.sh" -type f -exec sed -i.bak \
    's|scripts/codex/|.codex/scripts/|g' {} \;
find .codex/tests -name "*.sh" -type f -exec sed -i.bak \
    's|tests/codex/|.codex/tests/|g' {} \;

# Verify no old paths remain
if grep -r "scripts/codex/" .codex/tests/ 2>/dev/null || \
   grep -r "tests/codex/" .codex/tests/ 2>/dev/null; then
    echo "❌ ERROR: Old paths still present"
    exit 1
else
    echo "✅ All path references updated"
    find .codex/tests -name "*.bak" -delete
fi
```

**Additional Resources**:
- https://unix.stackexchange.com/questions/379572/escaping-both-forward-slash-and-back-slash-with-sed
- https://phoenixnap.com/kb/sed-replace

---

### 3. Forgetting --follow Flag Breaks History Viewing

**Severity**: High
**Category**: Git History / Debugging
**Affects**: Post-migration verification and debugging
**Source**: https://stackoverflow.com/questions/2314652/is-it-possible-to-move-rename-files-in-git-and-maintain-their-history

**What it is**:
`git log` without `--follow` flag only shows commits affecting the current file path. After `git mv`, running `git log new/path` shows only post-move commits, making it appear that history was lost even though it's preserved.

**Why it's a problem**:
- Developers think history is lost when it's actually preserved
- Triggers unnecessary investigation and confusion
- Makes `git blame` show wrong authors
- Can't find who wrote specific lines of code
- Makes bisecting bugs difficult

**How to detect it**:
- `git log .codex/scripts/parallel-exec.sh` shows only recent commits
- File appears to have no history before the move
- `git blame` shows committer who did the move as author of all lines

**How to avoid/fix**:

```bash
# ❌ WRONG - Viewing history without --follow (appears to lose history)
git log .codex/scripts/parallel-exec.sh
# Shows only commits after the move, not before

git blame .codex/scripts/parallel-exec.sh
# Shows move commit author for all lines

# ✅ RIGHT - Always use --follow for moved files
git log --follow .codex/scripts/parallel-exec.sh
# Shows complete history including before move

git log --follow --oneline .codex/scripts/parallel-exec.sh
# Concise view of full history

git log --follow --stat .codex/scripts/parallel-exec.sh
# Shows files changed in each commit

git blame .codex/scripts/parallel-exec.sh
# Actually doesn't need --follow, works automatically

# Why this works:
# --follow tells git to continue tracking through renames
# Git's rename detection finds the old path and shows those commits too
```

**Post-migration verification script**:
```bash
#!/bin/bash
# Verify all moved files retain full history

echo "Verifying git history for moved files..."

declare -a MOVED_FILES=(
    ".codex/scripts/parallel-exec.sh"
    ".codex/scripts/codex-generate-prp.sh"
    ".codex/scripts/quality-gate.sh"
    ".codex/tests/test_generate_prp.sh"
    ".codex/tests/test_execute_prp.sh"
)

all_verified=true

for file in "${MOVED_FILES[@]}"; do
    # Count commits with --follow
    with_follow=$(git log --follow --oneline "$file" 2>/dev/null | wc -l | tr -d ' ')

    # Count commits without --follow (post-move only)
    without_follow=$(git log --oneline "$file" 2>/dev/null | wc -l | tr -d ' ')

    echo ""
    echo "File: $file"
    echo "  Commits with --follow: $with_follow"
    echo "  Commits without --follow: $without_follow"

    if [ "$with_follow" -gt "$without_follow" ]; then
        echo "  ✅ History preserved (rename detected)"
    elif [ "$with_follow" -eq "$without_follow" ] && [ "$with_follow" -gt 1 ]; then
        echo "  ⚠️  May be new file or no renames in history"
    else
        echo "  ❌ HISTORY LOST or file has minimal history"
        all_verified=false
    fi
done

if [ "$all_verified" = true ]; then
    echo ""
    echo "✅ All files verified with complete history"
    exit 0
else
    echo ""
    echo "❌ Some files may have lost history"
    exit 1
fi
```

**Important limitation**:
```bash
# --follow only works for SINGLE files, not directories
git log --follow .codex/scripts/  # Does NOT work
git log --follow .codex/scripts/*.sh  # Does NOT work

# Must check each file individually
for file in .codex/scripts/*.sh; do
    git log --follow "$file"
done
```

**Additional Resources**:
- https://git-scm.com/docs/git-log (--follow documentation)
- https://dev.to/gkampitakis/check-files-git-history-even-if-renamedmoved-13m0

---

### 4. BASH_SOURCE[0] vs $0 Confusion

**Severity**: High
**Category**: Script Sourcing Errors
**Affects**: Scripts that source other scripts
**Source**: https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script

**What it is**:
When a script is sourced (`. script.sh` or `source script.sh`), `$0` becomes "bash" instead of the script name, but `${BASH_SOURCE[0]}` correctly identifies the sourced script. Using `$0` to locate sibling scripts fails when sourcing is involved.

**Why it's a problem**:
- Scripts fail to find their dependencies after move
- Different behavior when executed vs sourced
- Hard to debug (works when run directly, fails when sourced)
- Breaks multi-script systems like Codex

**How to detect it**:
- Script works when executed: `./script.sh` ✅
- Same script fails when sourced: `source script.sh` ❌
- Error: "No such file or directory" for sourced dependencies
- `echo $0` when sourced shows "bash" not script name

**How to avoid/fix**:

```bash
# ❌ WRONG - Using $0 for sourced scripts
# In script: scripts/codex/parallel-exec.sh
script_dir="$(cd "$(dirname "$0")" && pwd)"
source "${script_dir}/log-phase.sh"

# When executed directly: $0 = "scripts/codex/parallel-exec.sh" ✅
# When sourced: $0 = "bash" ❌
# Result: Looks for bash/log-phase.sh (doesn't exist)

# ❌ WRONG - Using BASH_SOURCE without [0] index
script_dir="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
# This might work but is less explicit and could break

# ✅ RIGHT - Always use ${BASH_SOURCE[0]} for reliability
# In script: .codex/scripts/parallel-exec.sh
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/log-phase.sh"
source "${script_dir}/security-validation.sh"

# When executed: ${BASH_SOURCE[0]} = ".codex/scripts/parallel-exec.sh" ✅
# When sourced: ${BASH_SOURCE[0]} = ".codex/scripts/parallel-exec.sh" ✅
# Result: Always finds sibling scripts correctly

# Enhanced version with error handling
get_script_dir() {
    local source="${BASH_SOURCE[0]}"

    # Resolve symlinks
    while [ -h "$source" ]; do
        local dir="$(cd -P "$(dirname "$source")" && pwd)"
        source="$(readlink "$source")"
        [[ $source != /* ]] && source="$dir/$source"
    done

    echo "$(cd -P "$(dirname "$source")" && pwd)"
}

SCRIPT_DIR="$(get_script_dir)"
source "${SCRIPT_DIR}/log-phase.sh" || {
    echo "ERROR: Failed to source log-phase.sh" >&2
    exit 1
}

# Why this works:
# ${BASH_SOURCE[0]} always refers to the actual script file
# regardless of how it was invoked (executed or sourced)
# $0 changes based on invocation method
```

**Verification after move**:
```bash
# Test both execution modes for all scripts
echo "Testing script sourcing patterns..."

# Test 1: Direct execution
.codex/scripts/parallel-exec.sh --help
if [ $? -eq 0 ]; then
    echo "✅ Direct execution works"
else
    echo "❌ Direct execution failed"
fi

# Test 2: Sourcing
source .codex/scripts/parallel-exec.sh
if [ $? -eq 0 ]; then
    echo "✅ Sourcing works"
else
    echo "❌ Sourcing failed"
fi

# Test 3: Verify all scripts use BASH_SOURCE[0] not $0
grep -n 'dirname.*\$0' .codex/scripts/*.sh
if [ $? -eq 0 ]; then
    echo "⚠️  WARNING: Found scripts using \$0 instead of \${BASH_SOURCE[0]}"
    echo "These may fail when sourced"
fi
```

**Pattern in existing Codex scripts**:
```bash
# From parallel-exec.sh (line 118) - CORRECT PATTERN
local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/log-phase.sh"

# From codex-generate-prp.sh (lines 112-125) - CORRECT PATTERN
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/log-phase.sh"
source "${SCRIPT_DIR}/security-validation.sh"
source "${SCRIPT_DIR}/parallel-exec.sh"

# These patterns work correctly before AND after the move
# because they use directory-relative sourcing
```

**Additional Resources**:
- https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
- https://unix.stackexchange.com/questions/4650/how-to-determine-the-path-to-a-sourced-tcsh-or-bash-shell-script-from-within-the

---

### 5. Incomplete Path Updates - Missing References

**Severity**: High
**Category**: Broken References / Integration
**Affects**: Test files, documentation, hidden references
**Source**: http://www.pixelbeat.org/programming/shell_script_mistakes.html

**What it is**:
After moving files, some path references remain unchanged because they exist in unexpected locations: comments, documentation, test fixtures, error messages, or files that weren't searched. This creates partial breakage where some things work but others mysteriously fail.

**Why it's a problem**:
- Tests fail with confusing "file not found" errors
- Documentation examples don't work
- Error messages reference non-existent paths
- Intermittent failures hard to track down
- Creates technical debt (old paths linger)

**How to detect it**:
- Tests fail after migration with path errors
- `grep -r "scripts/codex"` returns results after update
- Documentation examples point to old locations
- Error logs reference non-existent files

**How to avoid/fix**:

```bash
# ❌ WRONG - Only updating obvious files
find .codex/tests -name "*.sh" -exec sed -i 's|scripts/codex/|.codex/scripts/|g' {} \;
# Misses: comments, documentation, fixtures, error messages

# ❌ WRONG - Not searching comprehensively
grep -r "scripts/codex/" .codex/tests/  # Only searches tests
# Misses: README files, markdown docs, configuration files

# ✅ RIGHT - Comprehensive search and replace strategy

# Step 1: Find ALL instances (excluding .git directory)
echo "Searching for old path references..."
OLD_REFS=$(grep -r "scripts/codex/" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude="*.log" \
    --exclude="*.bak" \
    2>/dev/null)

if [ -n "$OLD_REFS" ]; then
    echo "Found old path references:"
    echo "$OLD_REFS"
else
    echo "No old path references found"
fi

# Step 2: Update code files
echo "Updating code files..."
find . -type f \( -name "*.sh" -o -name "*.bash" \) \
    -not -path "./.git/*" \
    -exec sed -i.bak 's|scripts/codex/|.codex/scripts/|g' {} \;

find . -type f \( -name "*.sh" -o -name "*.bash" \) \
    -not -path "./.git/*" \
    -exec sed -i.bak 's|tests/codex/|.codex/tests/|g' {} \;

# Step 3: Update documentation files
echo "Updating documentation..."
find . -type f \( -name "*.md" -o -name "README*" \) \
    -not -path "./.git/*" \
    -exec sed -i.bak 's|scripts/codex/|.codex/scripts/|g' {} \;

find . -type f \( -name "*.md" -o -name "README*" \) \
    -not -path "./.git/*" \
    -exec sed -i.bak 's|tests/codex/|.codex/tests/|g' {} \;

# Step 4: Update configuration files
echo "Updating configuration files..."
find . -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.toml" \) \
    -not -path "./.git/*" \
    -not -path "./node_modules/*" \
    -exec sed -i.bak 's|scripts/codex/|.codex/scripts/|g' {} \;

# Step 5: Verify no references remain (thorough check)
echo "Verifying all references updated..."
REMAINING=$(grep -r "scripts/codex/" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude="*.log" \
    --exclude="*.bak" \
    --exclude="gotchas.md" \
    2>/dev/null | wc -l | tr -d ' ')

if [ "$REMAINING" -eq 0 ]; then
    echo "✅ All path references updated"
    # Remove backup files
    find . -name "*.bak" -type f -delete
    exit 0
else
    echo "❌ ERROR: $REMAINING old path references still exist:"
    grep -rn "scripts/codex/" . \
        --exclude-dir=.git \
        --exclude-dir=node_modules \
        --exclude="*.log" \
        --exclude="*.bak" \
        --exclude="gotchas.md"
    exit 1
fi

# Why this works:
# - Searches all file types (code, docs, configs)
# - Excludes irrelevant directories (.git, node_modules)
# - Creates backups for safety
# - Verifies completeness before cleanup
# - Excludes this gotchas.md file from verification (it contains old paths as examples)
```

**Known locations to check**:
```bash
# Checklist of files/locations that commonly contain path references
LOCATIONS_TO_CHECK=(
    ".codex/README.md"                    # Main documentation
    ".codex/scripts/README.md"            # Script documentation
    "README.md"                           # Root readme
    ".github/workflows/*.yml"             # CI/CD configs
    "tests/codex/fixtures/*.sh"           # Test fixtures
    "scripts/codex/*.sh"                  # Before move (comments)
    ".codex/tests/*.sh"                   # After move (actual paths)
)

for location in "${LOCATIONS_TO_CHECK[@]}"; do
    if ls $location 2>/dev/null; then
        echo "Checking: $location"
        grep -n "scripts/codex/" $location || echo "  ✅ Clean"
    fi
done
```

**Additional Resources**:
- http://www.pixelbeat.org/programming/shell_script_mistakes.html
- https://mywiki.wooledge.org/BashPitfalls

---

## Medium Priority Gotchas

### 1. Empty Directory Detection Misses Hidden Files

**Severity**: Medium
**Category**: Directory Cleanup
**Affects**: Deletion of scripts/codex/ and tests/codex/
**Source**: prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh

**What it is**:
Simple checks like `[ -z "$(ls -A dir)" ]` or `rmdir dir` can fail to detect hidden files like `.DS_Store` (macOS), `.gitkeep`, or `._*` (resource forks). Attempting to delete a "seemingly empty" directory that contains hidden files fails or leaves remnants.

**Why it's confusing**:
- Directory appears empty when listing: `ls scripts/codex/` shows nothing
- But `rmdir scripts/codex/` fails with "Directory not empty"
- Hidden files not visible without `ls -la`
- Causes migration script to fail unexpectedly

**How to handle it**:

```bash
# ❌ WRONG - Doesn't catch hidden files
if [ -z "$(ls scripts/codex)" ]; then
    rmdir scripts/codex
fi
# Fails if .DS_Store or other hidden files exist

# ❌ WRONG - Using -A flag but not counting properly
if [ -z "$(ls -A scripts/codex)" ]; then
    rmdir scripts/codex
fi
# Still fails to verify before deletion

# ✅ RIGHT - Use find with proper depth
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

    if [ $? -eq 0 ]; then
        echo "✅ Empty directory deleted: ${dir_path}"
        return 0
    else
        echo "❌ ERROR: Failed to delete directory: ${dir_path}"
        return 1
    fi
}

# Application to codex reorganization
delete_empty_directory "scripts/codex" || exit 1
delete_empty_directory "tests/codex" || exit 1

# Why this works:
# - find with -mindepth 1 catches ALL files (including hidden)
# - maxdepth 1 prevents searching subdirectories
# - rmdir (not rm -rf) fails safely if dir not truly empty
# - Lists contents if validation fails (helps debugging)
```

**Alternative: Force delete with verification**:
```bash
# If you're certain directory should be empty, force delete
force_delete_directory() {
    local dir_path="$1"

    if [ ! -d "${dir_path}" ]; then
        echo "⚠️  Directory does not exist: ${dir_path}"
        return 0
    fi

    # Show what will be deleted
    echo "Contents of ${dir_path} before deletion:"
    ls -la "${dir_path}"

    # Confirm deletion (comment out for non-interactive)
    read -p "Delete this directory? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deletion cancelled"
        return 1
    fi

    # Force delete (use cautiously)
    rm -rf "${dir_path}"
    echo "✅ Directory forcefully deleted: ${dir_path}"
}
```

**Additional Resources**:
- prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh lines 50-85
- https://unix.stackexchange.com/questions/107800/find-hidden-files-but-not-directories

---

### 2. REPO_ROOT Calculation Breaks with Different Depth

**Severity**: Medium
**Category**: Path Resolution
**Affects**: Test files after move
**Source**: tests/codex/test_generate_prp.sh lines 14-16

**What it is**:
Test files calculate repository root using relative navigation: `REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"`. If directory depth changes during reorganization (e.g., from `tests/codex/` to `.codex/tests/`), the calculation can break or point to wrong directory.

**Why it's confusing**:
- Tests suddenly can't find scripts
- Error messages are unclear ("file not found")
- Works if run from specific directory, fails from others
- Depth appears same but symlinks or mounts can affect it

**How to handle**:

```bash
# ❌ POTENTIALLY WRONG - Assuming depth stays same
# Before move: tests/codex/test_file.sh (depth 2: tests → codex → file)
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# After move: .codex/tests/test_file.sh (depth 2: .codex → tests → file)
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# Happens to work because depth is same, but fragile

# ❌ WRONG - Using wrong number of "../" after move
# If depth actually changed from 2 to 3 levels
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"  # Now points to wrong dir

# ✅ RIGHT - Verify REPO_ROOT after move
# In .codex/tests/test_generate_prp.sh

# Calculate REPO_ROOT
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Verify REPO_ROOT is actually repository root
if [ ! -f "${REPO_ROOT}/.git/config" ]; then
    echo "❌ ERROR: REPO_ROOT calculation is wrong: ${REPO_ROOT}" >&2
    echo "   Expected to find .git/config" >&2
    echo "   SCRIPT_DIR: ${SCRIPT_DIR}" >&2
    exit 1
fi

echo "✅ REPO_ROOT: ${REPO_ROOT}"

# ✅ BETTER - Use git to find repo root (most reliable)
REPO_ROOT="$(git rev-parse --show-toplevel)"

if [ -z "${REPO_ROOT}" ]; then
    echo "❌ ERROR: Not in a git repository" >&2
    exit 1
fi

echo "✅ REPO_ROOT: ${REPO_ROOT}"

# Why this works:
# - git rev-parse --show-toplevel always finds repo root
# - Doesn't depend on directory depth
# - Works from any subdirectory
# - Immune to symlinks and mount points
```

**Depth verification script**:
```bash
# Verify test file depths before and after move
echo "Checking directory depths..."

# Before move
echo "Before: tests/codex/test_generate_prp.sh"
echo "  Depth from root: 2 levels"

# After move
echo "After: .codex/tests/test_generate_prp.sh"
echo "  Depth from root: 2 levels"

# Verify REPO_ROOT calculation works
cd .codex/tests
SCRIPT_DIR="$(pwd)"
REPO_ROOT_RELATIVE="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ROOT_GIT="$(git rev-parse --show-toplevel)"

echo ""
echo "REPO_ROOT (relative): ${REPO_ROOT_RELATIVE}"
echo "REPO_ROOT (git):      ${REPO_ROOT_GIT}"

if [ "${REPO_ROOT_RELATIVE}" = "${REPO_ROOT_GIT}" ]; then
    echo "✅ REPO_ROOT calculation correct"
else
    echo "❌ REPO_ROOT calculation WRONG"
    exit 1
fi
```

**Pattern in test files** (NO CHANGES NEEDED):
```bash
# From test_generate_prp.sh (lines 14-16)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Depth check:
# Before: tests/codex/test_generate_prp.sh → up 2 levels → repo root ✅
# After:  .codex/tests/test_generate_prp.sh → up 2 levels → repo root ✅
# Result: NO CHANGE NEEDED (depth is same)
```

**Additional Resources**:
- https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
- https://git-scm.com/docs/git-rev-parse

---

### 3. Quoting Variables Prevents Word Splitting Attacks

**Severity**: Medium
**Category**: Security / Robustness
**Affects**: All file operations with variables
**Source**: http://www.pixelbeat.org/programming/shell_script_mistakes.html

**What it is**:
When variables containing paths are unquoted in bash, the shell performs word splitting on spaces, tabs, and newlines. A malicious or accidental filename like `my file.sh` or `file; rm -rf.sh` can cause commands to execute incorrectly or dangerously.

**Why it's a problem**:
- File names with spaces break commands
- Can enable command injection attacks
- Difficult to debug (works for some files, fails for others)
- Security vulnerability if paths come from user input

**How to handle**:

```bash
# ❌ VULNERABLE - Unquoted variables
SOURCE_FILE=scripts/codex/my file.sh  # File with space
git mv $SOURCE_FILE .codex/scripts/
# Expands to: git mv scripts/codex/my file.sh .codex/scripts/
# Git sees: git mv scripts/codex/my file.sh .codex/scripts/
# Error: "scripts/codex/my" not found

# ❌ VULNERABLE - Unquoted in loops
for file in $FILES; do  # Word splitting occurs
    git mv $file .codex/scripts/
done

# ✅ SECURE - Always quote variables
SOURCE_FILE="scripts/codex/my file.sh"
git mv "$SOURCE_FILE" .codex/scripts/
# Expands to: git mv "scripts/codex/my file.sh" ".codex/scripts/"
# Works correctly with spaces

# ✅ SECURE - Quote in loops
for file in "${FILES[@]}"; do  # Array prevents word splitting
    git mv "$file" ".codex/scripts/"
done

# ✅ BEST - Use arrays for file lists
declare -a FILE_MOVES=(
    "scripts/codex/parallel-exec.sh"
    "scripts/codex/codex-generate-prp.sh"
    "scripts/codex/quality-gate.sh"
)

for source_file in "${FILE_MOVES[@]}"; do
    filename="$(basename "$source_file")"
    dest_file=".codex/scripts/${filename}"
    git mv "$source_file" "$dest_file"
done

# Why this works:
# - Quotes prevent word splitting
# - Arrays preserve each element as single item
# - Safer against malicious filenames
```

**Complete safe move function**:
```bash
safe_git_mv() {
    local source="$1"
    local dest="$2"

    # Validation
    if [ ! -e "$source" ]; then
        echo "❌ ERROR: Source does not exist: $source" >&2
        return 1
    fi

    if [ -e "$dest" ]; then
        echo "❌ ERROR: Destination already exists: $dest" >&2
        return 1
    fi

    # Execute with quoted variables
    echo "Moving: $source → $dest"
    git mv "$source" "$dest"

    if [ $? -ne 0 ]; then
        echo "❌ ERROR: git mv failed" >&2
        return 1
    fi

    echo "✅ Moved successfully"
    return 0
}

# Use it
safe_git_mv "scripts/codex/parallel-exec.sh" ".codex/scripts/parallel-exec.sh"
```

**ShellCheck warnings**:
```bash
# Run shellcheck to detect unquoted variables
shellcheck migrate.sh

# Look for warnings like:
# SC2086: Double quote to prevent globbing and word splitting
# SC2068: Double quote array expansions to avoid re-splitting elements

# Fix all such warnings before running migration
```

**Additional Resources**:
- http://www.pixelbeat.org/programming/shell_script_mistakes.html
- https://mywiki.wooledge.org/BashPitfalls (Pitfall #1)
- https://www.shellcheck.net/

---

### 4. Concurrent Execution During Migration Causes Chaos

**Severity**: Medium
**Category**: Timing / Race Conditions
**Affects**: Migration if PRP generation/execution running
**Source**: Common sense + feature-analysis.md lines 306-309

**What it is**:
If PRP generation (`codex-generate-prp.sh`) or execution (`codex-execute-prp.sh`) is running when migration script moves files, the running processes will fail with "file not found" errors or attempt to execute files from non-existent paths.

**Why it's a problem**:
- Running processes crash mid-execution
- Partial PRP results or corrupted state
- Difficult to debug (intermittent failures)
- Can leave orphaned processes or temp files

**How to handle**:

```bash
# ❌ WRONG - No check for running processes
git mv scripts/codex/*.sh .codex/scripts/
# If codex-generate-prp.sh is running, it suddenly can't find dependencies

# ✅ RIGHT - Check for running Codex processes before migration

check_no_codex_processes() {
    echo "Checking for running Codex processes..."

    # Check for codex-generate-prp.sh
    if pgrep -f "codex-generate-prp.sh" > /dev/null; then
        echo "❌ ERROR: codex-generate-prp.sh is currently running"
        echo "   Please wait for it to complete or stop it before migration"
        return 1
    fi

    # Check for codex-execute-prp.sh
    if pgrep -f "codex-execute-prp.sh" > /dev/null; then
        echo "❌ ERROR: codex-execute-prp.sh is currently running"
        echo "   Please wait for it to complete or stop it before migration"
        return 1
    fi

    # Check for parallel-exec.sh
    if pgrep -f "parallel-exec.sh" > /dev/null; then
        echo "❌ ERROR: parallel-exec.sh is currently running"
        echo "   Please wait for parallel tasks to complete"
        return 1
    fi

    echo "✅ No Codex processes running"
    return 0
}

# Run check before migration
check_no_codex_processes || {
    echo ""
    echo "Migration aborted. Please stop Codex processes and try again."
    exit 1
}

# Proceed with migration...
```

**Interactive warning**:
```bash
# Warn user before starting
cat << 'EOF'
==============================================
CODEX DIRECTORY REORGANIZATION
==============================================

This script will move all Codex files to .codex/ directory.

⚠️  WARNING:
- Do NOT run this while PRP generation/execution is in progress
- Do NOT interrupt this script once started (use Ctrl+C only if necessary)
- All changes will be committed to git

EOF

read -p "Are you ready to proceed? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled"
    exit 0
fi

check_no_codex_processes || exit 1
```

**Additional Resources**:
- feature-analysis.md lines 306-309 (assumption #10)

---

## Low Priority Gotchas

### 1. Git Working Tree Dirty Check

**Severity**: Low
**Category**: Git State
**Affects**: Migration rollback capability

**What it is**:
Running migration with uncommitted changes makes rollback difficult and can cause merge conflicts.

**How to handle**:

```bash
# Check for clean working tree before migration
check_clean_working_tree() {
    echo "Checking git working tree status..."

    if ! git diff-index --quiet HEAD --; then
        echo "❌ ERROR: Git working tree has uncommitted changes"
        echo ""
        echo "Please commit or stash your changes before running migration:"
        echo "  git status"
        echo "  git add -A && git commit -m 'Your message'"
        echo "  # OR"
        echo "  git stash"
        exit 1
    fi

    echo "✅ Working tree is clean"
}

check_clean_working_tree
```

---

### 2. Backup Before Migration

**Severity**: Low
**Category**: Safety

**What it is**:
Creating rollback point before starting.

**How to handle**:

```bash
# Create git tag for easy rollback
echo "Creating backup tag..."
BACKUP_TAG="codex-reorganization-backup-$(date +%Y%m%d-%H%M%S)"
git tag "$BACKUP_TAG"
echo "✅ Created backup tag: $BACKUP_TAG"
echo "   To rollback: git reset --hard $BACKUP_TAG"
```

---

## Gotcha Checklist for Implementation

Before marking migration complete, verify these gotchas are addressed:

- [ ] **Git History**: All moves in separate commits from content changes
- [ ] **Similarity**: No heavy refactoring during file moves
- [ ] **Command Injection**: All paths validated and quoted
- [ ] **sed Portability**: Using alternative delimiters (pipe) and -i.bak
- [ ] **--follow Flag**: Documentation reminds users to use --follow
- [ ] **BASH_SOURCE**: All scripts use ${BASH_SOURCE[0]} not $0
- [ ] **Path References**: Comprehensive grep finds all old paths
- [ ] **Hidden Files**: Empty directory check uses find with mindepth/maxdepth
- [ ] **REPO_ROOT**: Test file calculations verified or use git rev-parse
- [ ] **Quoting**: All variables quoted in commands
- [ ] **Process Check**: No Codex processes running during migration
- [ ] **Clean Tree**: Working tree clean before migration
- [ ] **Backup**: Git tag created for rollback

---

## Confidence Assessment

**Gotcha Coverage**: 9/10

- **Security**: HIGH - Command injection, path validation covered
- **Performance**: MEDIUM - Covered concurrent execution, no major perf issues expected
- **Common Mistakes**: HIGH - Git history, sed escaping, path updates covered thoroughly

**Gaps**:
- Network filesystem behaviors (NFS, SMB) not covered (low priority for local dev)
- Disk space issues if backups accumulate (low risk, small files)
- Windows/WSL compatibility not covered (project appears Unix-only)

**Recommendation**: Proceed with migration. All critical and high-priority gotchas have proven solutions from successful cleanup PRP and web research.

---

## Sources Referenced

### From Web Research

**Git History & Operations**:
- https://stackoverflow.com/questions/10828267/can-git-restructure-my-folders-without-losing-history
- https://stackoverflow.com/questions/2314652/is-it-possible-to-move-rename-files-in-git-and-maintain-their-history
- https://stackoverflow.com/questions/72165668/losing-history-when-moving-files-with-git
- https://git-scm.com/docs/git-mv
- https://linuxctl.com/p/git-preserve-history-when-moving-files/

**sed & Path Operations**:
- https://stackoverflow.com/questions/4247068/sed-command-with-i-option-failing-on-mac-but-works-on-linux
- https://stackoverflow.com/questions/12061410/how-to-replace-a-path-with-another-path-in-sed
- https://unix.stackexchange.com/questions/379572/escaping-both-forward-slash-and-back-slash-with-sed
- https://askubuntu.com/questions/76785/how-to-escape-file-path-in-sed

**Bash Scripting**:
- https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
- http://www.pixelbeat.org/programming/shell_script_mistakes.html
- https://mywiki.wooledge.org/BashPitfalls

**Security**:
- https://www.akamai.com/blog/security-research/kubernetes-gitsync-command-injection-defcon
- https://github.com/payloadbox/command-injection-payload-list

### From Local Codebase

- `prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh` - Safe git mv patterns
- `prps/cleanup_execution_reliability_artifacts/examples/validation_checks.sh` - Validation patterns
- `scripts/codex/parallel-exec.sh` - BASH_SOURCE sourcing pattern
- `tests/codex/test_generate_prp.sh` - REPO_ROOT calculation pattern
- `prps/codex_reorganization/planning/feature-analysis.md` - Requirements and assumptions
- `prps/codex_reorganization/planning/codebase-patterns.md` - Existing patterns

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include critical gotchas** in "Known Gotchas & Library Quirks" section:
   - Git history loss (mixing moves with changes)
   - Command injection (path validation)
   - sed macOS vs Linux differences
   - BASH_SOURCE vs $0 confusion

2. **Reference solutions** in "Implementation Blueprint":
   - Separate commits for moves vs content changes
   - Use pipe delimiter in sed commands
   - Validate paths before git operations
   - Check for running processes before migration

3. **Add detection tests** to validation gates:
   - Verify git history with --follow for each file
   - Check for old path references with comprehensive grep
   - Validate bash syntax with bash -n
   - Run test suite to ensure functionality

4. **Warn about version issues** in documentation references:
   - Note macOS sed requires -i ''
   - Document --follow requirement for git log
   - Highlight BASH_SOURCE[0] pattern for sourcing

5. **Highlight anti-patterns** to avoid:
   - Never mix git mv with content changes in same commit
   - Never use / delimiter in sed with paths
   - Never use $0 for sourced scripts
   - Never run migration while Codex processes active
