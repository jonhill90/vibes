# Documentation Resources: Codex Directory Reorganization

## Overview
Comprehensive official documentation and resources for safely reorganizing Codex files from scattered root directories (`scripts/codex/`, `tests/codex/`) into unified `.codex/` structure. Focus on git history preservation, bash script sourcing patterns, path updates, and migration validation. All resources include working examples and gotchas relevant to file reorganization.

## Primary Framework Documentation

### Git - Version Control & History Preservation
**Official Docs**: https://git-scm.com/docs/git-mv
**Version**: Git 2.x+
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:
1. **git mv Command Syntax**: https://git-scm.com/docs/git-mv
   - **Why**: Official syntax for moving files while preserving history
   - **Key Concepts**:
     - Updates index automatically after move
     - Handles directories and individual files
     - Force flag (-f) for overwriting
     - Dry-run option (-n) for testing

2. **git log --follow**: https://git-scm.com/docs/git-log
   - **Why**: Verify history preservation after moves
   - **Key Concepts**:
     - Continues file history beyond renames
     - Works only for single files
     - Essential for post-migration validation
     - Default 50% similarity index for rename detection

**Code Examples from Docs**:
```bash
# Example 1: Rename a single file
# Source: https://git-scm.com/docs/git-mv
git mv oldname.txt newname.txt

# Example 2: Move multiple files to directory
# Source: https://git-scm.com/docs/git-mv
git mv file1.txt file2.txt destination_folder/

# Example 3: Force move with verbose output
# Source: https://git-scm.com/docs/git-mv
git mv -fv important.txt backup/

# Example 4: Verify history preservation
# Source: https://git-scm.com/docs/git-log
git log --follow .codex/scripts/parallel-exec.sh
```

**Gotchas from Documentation**:
- Git doesn't explicitly track renames - uses heuristic-based detection
- `--follow` only works for single files, not directories
- Don't combine file moves with content changes in same commit
- Rename detection requires 50%+ content similarity between old/new files
- Submodule moves require manual `git submodule update` afterward

---

### Bash - Shell Scripting Foundation
**Official Docs**: https://www.gnu.org/software/bash/manual/
**Version**: Bash 4.0+
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:
1. **Script Directory Resolution**: https://stackoverflow.com/questions/59895/
   - **Why**: Essential for maintaining sourcing patterns after directory moves
   - **Key Concepts**:
     - `BASH_SOURCE[0]` vs `$0` differences
     - Using `dirname` for path extraction
     - Absolute path resolution with `cd && pwd`
     - Symlink handling considerations

2. **Syntax Validation**: https://stackoverflow.com/questions/171924/
   - **Why**: Pre-migration and post-migration script validation
   - **Key Concepts**:
     - `bash -n` for syntax checking without execution
     - ShellCheck for comprehensive static analysis
     - Limitations of noexec mode
     - Handling edge cases

**Code Examples from Docs**:
```bash
# Example 1: Get script directory (recommended approach)
# Source: https://www.ostricher.com/2014/10/the-right-way-to-get-the-directory-of-a-bash-script/
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Example 2: Handle symlinks (advanced)
# Source: https://stackoverflow.com/questions/59895/
get_script_dir() {
    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do
        DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
        SOURCE="$( readlink "$SOURCE" )"
        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    echo "$DIR"
}

# Example 3: Syntax validation without execution
# Source: https://stackoverflow.com/questions/171924/
bash -n script.sh

# Example 4: Batch syntax validation
# Source: https://stackoverflow.com/questions/171924/
find .codex/scripts -name "*.sh" -print0 | xargs -0 -P"$(nproc)" -I{} bash -n "{}"
```

**Gotchas from Documentation**:
- `$0` inconsistent when sourcing scripts - always use `${BASH_SOURCE[0]}`
- `bash -n` only checks syntax, not runtime errors (e.g., command availability)
- Relative paths break when working directory changes
- Symlinks require special handling with `-P` flag
- Quoting variables essential for paths with spaces

---

## Library Documentation

### 1. sed - Stream Editor for Path Updates
**Official Docs**: https://www.gnu.org/software/sed/manual/sed.html
**Purpose**: Bulk path reference updates in test files and documentation
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Pages**:
- **sed Substitute Command**: https://www.cyberciti.biz/faq/how-to-use-sed-to-find-and-replace-text-in-files-in-linux-unix-shell/
  - **Use Case**: Update all path references from `scripts/codex/` to `.codex/scripts/`
  - **Example**: Basic in-place replacement with alternative delimiters

- **Recursive Find/Replace**: https://stackoverflow.com/questions/1583219/
  - **Use Case**: Update paths across all test files simultaneously
  - **Example**: Combining find with sed for directory-wide updates

**API Reference**:
- **sed -i (in-place editing)**: https://askubuntu.com/questions/20414/
  - **Signature**: `sed -i 's/pattern/replacement/g' file`
  - **Returns**: Modified file (in-place)
  - **Example**:
  ```bash
  # Update test file paths with alternative delimiter
  sed -i 's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' test_file.sh

  # Recursive update across all test files
  find .codex/tests -name "*.sh" -type f -exec sed -i 's|scripts/codex/|.codex/scripts/|g' {} +

  # macOS version (requires empty extension)
  sed -i '' 's|scripts/codex/|.codex/scripts/|g' test_file.sh
  ```

**Gotchas**:
- Default `/` delimiter conflicts with paths - use `|` or `_` instead
- macOS requires `-i ''` syntax, Linux uses `-i` alone
- Test with backup files first (`sed -i.bak`)
- Avoid running in `.git` directories
- Quote patterns to handle shell variables

---

### 2. Git Filter-Repo - Advanced Repository Restructuring
**Official Docs**: https://github.com/newren/git-filter-repo
**Purpose**: Alternative for complex history rewriting (if needed)
**Archon Source**: Not in Archon
**Relevance**: 6/10

**Key Pages**:
- **Getting Started**: https://www.git-tower.com/learn/git/faq/git-filter-repo
  - **Use Case**: If simple `git mv` proves insufficient
  - **Note**: Overkill for this migration, but good to know

**Applicable patterns**:
- Repository-wide path restructuring while preserving history
- Faster than deprecated `git filter-branch`
- Not needed for simple file moves - `git mv` suffices

---

## Integration Guides

### Git + Bash: Safe File Migration Pattern
**Guide URL**: https://stackoverflow.com/questions/10828267/can-git-restructure-my-folders-without-losing-history
**Source Type**: Community Best Practice (Stack Overflow)
**Quality**: 9/10
**Archon Source**: Not in Archon

**What it covers**:
- Moving files without losing git history
- Importance of separating moves from content changes
- How git detects renames through heuristics
- Verification techniques for history preservation

**Code examples**:
```bash
# Pattern: Separate directory moves from content changes
# Source: https://stackoverflow.com/questions/10828267/

# Step 1: Move files only (no content changes)
git mv scripts/codex/parallel-exec.sh .codex/scripts/parallel-exec.sh

# Step 2: Commit move separately
git commit -m "Move: parallel-exec.sh to .codex/scripts/"

# Step 3: Verify history preservation
git log --follow --name-status .codex/scripts/parallel-exec.sh

# Step 4: Make content changes in separate commit (if needed)
# This ensures git recognizes the move via hash matching
```

**Applicable patterns**:
- One commit per concern: moves separate from edits
- Verify each move with `git log --follow`
- Use descriptive commit messages for tracking
- Test migration on branch before merging

---

### Bash Error Handling for Migration Scripts
**Resource**: https://stackoverflow.com/questions/64786/error-handling-in-bash
**Type**: Community Best Practice (Stack Overflow)
**Relevance**: 10/10

**Key Practices**:
1. **Trap for Cleanup**: Ensure rollback on failure
   - **Why**: Migration should be atomic - all or nothing
   - **Example**:
   ```bash
   # Source: https://stackoverflow.com/questions/64786/
   cleanup() {
       if [ $? -ne 0 ]; then
           echo "Migration failed, rolling back..."
           git reset --hard HEAD
       fi
   }
   trap cleanup EXIT
   ```

2. **Set Options for Safety**: Fail fast on errors
   - **Why**: Catch issues immediately during migration
   - **Example**:
   ```bash
   # Source: https://opensource.com/article/20/7/bash-error-handling
   set -euo pipefail
   # -e: exit on error
   # -u: error on undefined variables
   # -o pipefail: pipeline fails if any command fails
   ```

3. **Explicit Error Checking**: Verify each critical step
   - **Why**: Migration has multiple failure points
   - **Example**:
   ```bash
   # Source: https://stackoverflow.com/questions/64786/
   if ! git mv scripts/codex/file.sh .codex/scripts/file.sh; then
       echo "Failed to move file.sh" >&2
       exit 1
   fi
   ```

---

## Testing Documentation

### Bash Script Testing & Validation
**Official Docs**: https://www.baeldung.com/linux/validate-bash-script
**Archon Source**: Not in Archon

**Relevant Sections**:
- **Syntax Validation**: https://stackoverflow.com/questions/171924/
  - **How to use**: Run `bash -n script.sh` before and after migration
- **ShellCheck Linting**: https://www.shellcheck.net/
  - **Patterns**: Static analysis for script quality
- **Exit Code Validation**: https://stackoverflow.com/questions/30569408/
  - **Considerations**: Proper error propagation in migration script

**Test Examples**:
```bash
# Test Pattern 1: Pre-migration syntax validation
# Source: https://www.baeldung.com/linux/validate-bash-script
for script in scripts/codex/*.sh; do
    bash -n "$script" || { echo "Syntax error in $script"; exit 1; }
done

# Test Pattern 2: Post-migration validation
# Source: https://www.baeldung.com/linux/validate-bash-script
for script in .codex/scripts/*.sh; do
    bash -n "$script" || { echo "Syntax error in $script"; exit 1; }
done

# Test Pattern 3: Comprehensive validation with ShellCheck
# Source: https://www.shellcheck.net/
find .codex/scripts -name "*.sh" -exec shellcheck {} \;

# Test Pattern 4: Verify git history for each moved file
# Source: https://git-scm.com/docs/git-log
for file in .codex/scripts/*.sh; do
    filename=$(basename "$file")
    if ! git log --follow --oneline "$file" | head -5; then
        echo "History verification failed for $file"
        exit 1
    fi
done
```

---

## Best Practices Documentation

### Directory Restructuring Without History Loss
**Resource**: https://medium.com/code-factory-berlin/github-repository-structure-best-practices-248e6effc405
**Type**: Best Practice Guide
**Relevance**: 8/10

**Key Practices**:
1. **Separate Concerns**: Don't mix moves with content changes
   - **Why**: Allows git to detect renames via hash matching
   - **Example**:
   ```bash
   # DO: Move only, no edits
   git mv scripts/codex/ .codex/scripts/
   git commit -m "Restructure: Move codex scripts to .codex/"

   # DON'T: Move and edit in same commit
   # (This breaks rename detection)
   ```

2. **Small Focused Commits**: One logical change per commit
   - **Why**: Easier rollback and history tracking
   - **Example**:
   ```bash
   # Commit 1: Move scripts
   git mv scripts/codex/*.sh .codex/scripts/
   git commit -m "Move codex scripts to .codex/scripts/"

   # Commit 2: Move tests
   git mv tests/codex/*.sh .codex/tests/
   git commit -m "Move codex tests to .codex/tests/"

   # Commit 3: Update path references
   sed -i 's|scripts/codex/|.codex/scripts/|g' .codex/tests/*.sh
   git commit -m "Update path references in tests"
   ```

3. **Maintain .gitignore**: Keep repository clean
   - **Why**: Migration creates directories, ensure proper ignore patterns
   - **Example**: Verify `.codex/` patterns if needed

---

### Bash Script Path Resolution Best Practices
**Resource**: https://www.ostricher.com/2014/10/the-right-way-to-get-the-directory-of-a-bash-script/
**Type**: Technical Guide
**Relevance**: 10/10

**Key Practices**:
1. **Use BASH_SOURCE[0]**: Reliable across sourcing scenarios
   - **Why**: Scripts in `.codex/scripts/` source each other
   - **Pattern**:
   ```bash
   # Source: https://www.ostricher.com/2014/10/
   script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
   source "${script_dir}/log-phase.sh"
   ```

2. **Avoid $0 for Sourced Scripts**: Unreliable when sourcing
   - **Why**: Returns bash path, not script path when sourced
   - **Verification**: Review all `source` statements in codex scripts

3. **Test Both Execution Modes**: Direct run vs sourced
   - **Why**: Scripts may be executed or sourced
   - **Validation**:
   ```bash
   # Test direct execution
   .codex/scripts/parallel-exec.sh

   # Test sourcing
   source .codex/scripts/parallel-exec.sh
   ```

---

### Git Rollback Strategies for Failed Migrations
**Resource**: https://stackoverflow.com/questions/4114095/how-do-i-revert-a-git-repository-to-a-previous-commit
**Type**: Community Best Practice
**Relevance**: 10/10

**Key Strategies**:
1. **Hard Reset for Local Rollback**: Nuclear option for failed migration
   - **When**: Migration validation fails, need complete rollback
   - **Example**:
   ```bash
   # Source: https://stackoverflow.com/questions/4114095/
   # Reset to state before migration started
   git reset --hard HEAD~3  # If migration was 3 commits

   # Or reset to specific commit
   git reset --hard <commit-hash-before-migration>

   # Clean untracked files
   git clean -f -d
   ```

2. **Soft Reset for Partial Rollback**: Keep changes, redo commits
   - **When**: Commits made, but need to restructure
   - **Example**:
   ```bash
   # Source: https://opensource.com/article/18/6/git-reset-revert-rebase-commands
   # Reset commit history but keep changes staged
   git reset --soft HEAD~1
   ```

3. **Revert for Public History**: Safe for pushed commits
   - **When**: Migration already pushed (avoid if possible)
   - **Example**:
   ```bash
   # Source: https://www.atlassian.com/git/tutorials/undoing-changes/git-revert
   git revert <commit-hash>
   ```

**Migration-Specific Rollback Pattern**:
```bash
# Source: Multiple sources combined
#!/bin/bash
set -e

# Store initial commit for rollback
MIGRATION_START=$(git rev-parse HEAD)

# Trap for automatic rollback on failure
rollback() {
    if [ $? -ne 0 ]; then
        echo "ERROR: Migration failed, rolling back to $MIGRATION_START"
        git reset --hard "$MIGRATION_START"
        git clean -f -d
        exit 1
    fi
}
trap rollback EXIT

# Migration operations here...
# If any fail, rollback triggers automatically
```

---

## Additional Resources

### Tutorials with Code
1. **Bash Error Handling Tutorial**: https://www.redhat.com/en/blog/bash-error-handling
   - **Format**: Blog post with examples
   - **Quality**: 9/10
   - **What makes it useful**: Real-world error handling patterns for robust scripts

2. **Git History Preservation Guide**: https://dev.to/gkampitakis/check-files-git-history-even-if-renamedmoved-13m0
   - **Format**: Blog tutorial
   - **Quality**: 8/10
   - **What makes it useful**: Step-by-step verification of history after moves

3. **Sed Path Replacement Tutorial**: https://phoenixnap.com/kb/sed-replace
   - **Format**: Technical guide
   - **Quality**: 8/10
   - **What makes it useful**: Clear examples of sed with paths and special characters

### API References
1. **Git Command Reference**: https://git-scm.com/docs
   - **Coverage**: All git commands (mv, log, reset, commit)
   - **Examples**: Yes, comprehensive examples for each command

2. **Bash Manual**: https://www.gnu.org/software/bash/manual/
   - **Coverage**: Complete bash scripting reference
   - **Examples**: Yes, includes BASH_SOURCE, dirname, sourcing

3. **Sed Manual**: https://www.gnu.org/software/sed/manual/sed.html
   - **Coverage**: Complete sed stream editor documentation
   - **Examples**: Yes, comprehensive substitution patterns

### Community Resources
1. **Stack Overflow - Bash Tag**: https://stackoverflow.com/questions/tagged/bash
   - **Type**: Q&A forum with expert answers
   - **Why included**: Extensive real-world bash scripting solutions

2. **Stack Overflow - Git Tag**: https://stackoverflow.com/questions/tagged/git
   - **Type**: Q&A forum with expert answers
   - **Why included**: Deep git workflow and history questions answered

3. **ShellCheck Project**: https://github.com/koalaman/shellcheck
   - **Type**: Open source bash linter
   - **Why included**: Essential tool for bash script validation

---

## Documentation Gaps

**Not found in Archon or Web**:
- Specific documentation for bash script migration testing patterns
  - **Recommendation**: Adapt database migration testing patterns to file migrations
  - **Workaround**: Combine git validation + bash syntax checks + functional tests

- Automated git history verification tools
  - **Recommendation**: Write custom script using `git log --follow` in loop
  - **Workaround**: Manual verification with provided git commands

**Outdated or Incomplete**:
- Git filter-branch documentation (deprecated)
  - **Status**: Replaced by git-filter-repo
  - **Suggested alternative**: Use git mv for simple moves, git-filter-repo only for complex rewrites

- Some bash scripting guides use outdated $0 pattern
  - **Status**: Inconsistent recommendations across resources
  - **Suggested alternative**: Always use ${BASH_SOURCE[0]} for reliability

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Git Documentation:
  - git mv: https://git-scm.com/docs/git-mv
  - git log --follow: https://git-scm.com/docs/git-log
  - git reset: https://git-scm.com/docs/git-reset
  - git revert: https://git-scm.com/docs/git-revert

Bash Scripting:
  - Script directory resolution: https://stackoverflow.com/questions/59895/
  - Syntax validation: https://stackoverflow.com/questions/171924/
  - Error handling: https://stackoverflow.com/questions/64786/
  - Best practices: https://www.ostricher.com/2014/10/the-right-way-to-get-the-directory-of-a-bash-script/

Path Updates:
  - sed find/replace: https://stackoverflow.com/questions/1583219/
  - sed with paths: https://askubuntu.com/questions/20414/
  - Alternative delimiters: https://unix.stackexchange.com/questions/725426/

Testing & Validation:
  - bash -n syntax check: https://www.baeldung.com/linux/validate-bash-script
  - ShellCheck: https://www.shellcheck.net/
  - Migration testing: https://stackoverflow.com/questions/34887318/

Restructuring Guides:
  - Directory restructuring: https://medium.com/code-factory-berlin/github-repository-structure-best-practices-248e6effc405
  - History preservation: https://stackoverflow.com/questions/10828267/
  - Rollback strategies: https://stackoverflow.com/questions/4114095/
```

## Recommendations for PRP Assembly

When generating the PRP:
1. **Include these URLs** in "Documentation & References" section:
   - Official git-scm.com docs for mv and log commands
   - Stack Overflow threads for bash BASH_SOURCE patterns
   - sed tutorials for path replacement examples

2. **Extract code examples** shown above into PRP context:
   - Migration script with trap-based rollback
   - git mv + commit pattern for history preservation
   - sed one-liners for path updates with alternative delimiters
   - bash -n validation loops for pre/post checks
   - git log --follow verification for each moved file

3. **Highlight gotchas** from documentation in "Known Gotchas" section:
   - Git rename detection is heuristic (50% similarity)
   - Don't mix moves with content changes in same commit
   - ${BASH_SOURCE[0]} required for sourced scripts, not $0
   - sed -i syntax differs between Linux and macOS
   - bash -n only checks syntax, not runtime errors
   - git log --follow works only for single files

4. **Reference specific sections** in implementation tasks:
   - "See git mv docs: https://git-scm.com/docs/git-mv for syntax"
   - "Follow BASH_SOURCE pattern from: https://stackoverflow.com/questions/59895/"
   - "Use sed alternative delimiters: https://askubuntu.com/questions/20414/"
   - "Implement rollback from: https://stackoverflow.com/questions/4114095/"

5. **Note gaps** so implementation can compensate:
   - No automated git history verification - write custom loop
   - Limited bash migration testing docs - adapt from database patterns
   - Test on branch first, extensive validation before merge
   - Manual verification still needed for some edge cases

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:
- https://git-scm.com/docs - **Why**: Official git documentation is foundational for all git operations, essential for future PRPs
- https://www.gnu.org/software/bash/manual/ - **Why**: Bash is core to all shell scripting PRPs, comprehensive official reference
- https://stackoverflow.com/questions/59895/ (BASH_SOURCE dirname) - **Why**: This specific pattern is reusable across many bash script projects
- https://stackoverflow.com/questions/64786/ (bash error handling) - **Why**: Error handling patterns apply to all bash automation scripts
- https://www.shellcheck.net/ - **Why**: Shell script validation is critical for code quality in bash-based projects

[These resources would significantly improve Archon's bash and git knowledge for future PRPs involving shell scripts and version control operations]

---

## Migration-Specific Implementation Checklist

Based on documentation research, here's a recommended migration checklist:

### Pre-Migration Phase
- [ ] Verify git working tree is clean: `git status`
- [ ] Run baseline tests and capture results
- [ ] Syntax check all scripts: `for s in scripts/codex/*.sh; do bash -n "$s"; done`
- [ ] Create rollback point: `MIGRATION_START=$(git rev-parse HEAD)`
- [ ] Verify BASH_SOURCE patterns in scripts: `grep -r 'BASH_SOURCE' scripts/codex/`

### Migration Execution Phase
- [ ] Create target directories: `mkdir -p .codex/scripts .codex/tests`
- [ ] Move scripts with git mv: `git mv scripts/codex/*.sh .codex/scripts/`
- [ ] Move tests with git mv: `git mv tests/codex/*.sh .codex/tests/`
- [ ] Move fixtures: `git mv tests/codex/fixtures .codex/tests/`
- [ ] Commit moves separately: `git commit -m "Move codex files to .codex/"`

### Path Update Phase
- [ ] Update test file paths: `find .codex/tests -name "*.sh" -exec sed -i 's|scripts/codex/|.codex/scripts/|g' {} +`
- [ ] Update documentation: Edit `.codex/README.md` and `.codex/scripts/README.md`
- [ ] Verify no old paths remain: `grep -r "scripts/codex" . --exclude-dir=.git`
- [ ] Commit path updates: `git commit -m "Update path references for .codex/ structure"`

### Validation Phase
- [ ] Syntax check all scripts: `find .codex/scripts -name "*.sh" -exec bash -n {} \;`
- [ ] Run all tests: `.codex/tests/test_*.sh`
- [ ] Verify git history: `git log --follow .codex/scripts/parallel-exec.sh | head -20`
- [ ] Check for broken references: `grep -r "tests/codex" . --exclude-dir=.git`

### Cleanup Phase
- [ ] Remove empty directories: `rmdir scripts/codex tests/codex`
- [ ] Final commit: `git commit -m "Complete codex reorganization to .codex/"`
- [ ] Tag migration: `git tag codex-reorganization-complete`

### Rollback (if validation fails)
- [ ] Execute rollback: `git reset --hard $MIGRATION_START`
- [ ] Clean untracked: `git clean -f -d`
- [ ] Verify clean state: `git status`
