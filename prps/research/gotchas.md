# Known Gotchas: Initial Factory Removal

## Overview

This cleanup task involves removing 6 INITIAL factory subagent files, 1 command file, and ~193 lines from CLAUDE.md. The main categories of gotchas identified are: **Git reference handling** (preventing corruption during deletions), **documentation coherence** (avoiding broken links and orphaned sections), **hidden dependencies** (ensuring no code references deleted files), and **workflow validation** (confirming PRP generation still works after cleanup).

## Critical Gotchas

### 1. Git Reference Corruption During File Deletion
**Severity**: Critical
**Category**: Data Loss / Repository Corruption
**Affects**: Git repository integrity
**Source**: https://stackoverflow.com/questions/2998832/git-pull-fails-unable-to-resolve-reference

**What it is**:
When git operations are interrupted (system crash, force-close, CTRL-C during git rm), reference files in `.git/refs/` can become corrupted or contain NULL characters, leading to "unable to resolve reference" errors.

**Why it's a problem**:
- Repository becomes unusable until corruption is fixed
- Can lose track of branches and commits
- May require manual recovery steps
- Future pulls/pushes fail with cryptic errors

**How to detect it**:
- Error message: `error: cannot lock ref 'refs/remotes/origin/[branch]': unable to resolve reference`
- `git status` hangs or shows errors
- `.git/refs/` contains empty or corrupted files

**How to avoid/fix**:
```bash
# ❌ WRONG - Interrupting git operations
git rm .claude/agents/prp-initial-*.md
# [User hits CTRL-C or system crashes]

# ✅ RIGHT - Safe deletion with verification
# 1. Check repository health first
git fsck --full

# 2. Ensure clean git state before deletion
git status
# Should show "nothing to commit, working tree clean"

# 3. Delete files one by one (easier to recover if interrupted)
git rm .claude/agents/prp-initial-feature-clarifier.md
git rm .claude/agents/prp-initial-codebase-researcher.md
git rm .claude/agents/prp-initial-documentation-hunter.md
git rm .claude/agents/prp-initial-example-curator.md
git rm .claude/agents/prp-initial-gotcha-detective.md
git rm .claude/agents/prp-initial-assembler.md
git rm .claude/commands/create-initial.md

# 4. Verify staged deletions
git status

# 5. Commit immediately (don't leave staged deletions uncommitted)
git commit -m "chore: remove INITIAL factory subagent files"

# If corruption occurs, recover with:
git gc --prune=now
rm .git/refs/remotes/origin/[corrupted-branch]
git fetch
```

**Additional Resources**:
- Git fsck documentation: https://git-scm.com/docs/git-fsck
- Repository repair guide: https://www.mindfulchase.com/explore/troubleshooting-tips/troubleshooting-git-repository-corruption-fixing-broken-objects,-missing-commits,-and-index-inconsistencies.html

---

### 2. Orphaned Command References After Deletion
**Severity**: Critical
**Category**: Broken Workflow
**Affects**: `/generate-prp` and `/execute-prp` commands
**Source**: Research analysis + Claude Code subagent documentation

**What it is**:
Other commands or agent files may reference the deleted `prp-initial-*` agents or `/create-initial` command, causing runtime errors when invoked.

**Why it's a problem**:
- PRP generation workflow breaks if commands reference deleted agents
- Users see confusing errors about missing agent files
- Workflow documentation contradicts actual implementation
- No clear error message explaining the root cause

**How to detect it**:
- Command execution fails with "agent not found" error
- References to deleted files in command outputs
- Grep shows references in `.claude/commands/` or `.claude/agents/`

**How to avoid/fix**:
```bash
# ❌ WRONG - Delete files without checking references
rm .claude/agents/prp-initial-*.md
# [Commands now reference non-existent agents]

# ✅ RIGHT - Comprehensive reference check before deletion
# 1. Find ALL references to agents being deleted
grep -r "prp-initial-feature-clarifier" .claude/
grep -r "prp-initial-codebase-researcher" .claude/
grep -r "prp-initial-documentation-hunter" .claude/
grep -r "prp-initial-example-curator" .claude/
grep -r "prp-initial-gotcha-detective" .claude/
grep -r "prp-initial-assembler" .claude/

# 2. Find references to command being deleted
grep -r "create-initial" .claude/
grep -r "/create-initial" .

# 3. Expected results:
# - Only matches in files being deleted or CLAUDE.md (which we're updating)
# - No matches in generate-prp.md or execute-prp.md

# 4. If unexpected references found, update those files first
# Example: If generate-prp.md references prp-initial-* agents
# Update it to use prp-gen-* agents instead

# 5. After deletion, verify no dangling references
grep -r "prp-initial-" .claude/
grep -r "create-initial" .claude/
# Expected: Zero matches

# 6. Test commands still work
# Manually invoke /generate-prp with a test INITIAL.md
# Verify it invokes prp-gen-* agents, not prp-initial-*
```

**Testing for this vulnerability**:
```bash
# Verification script
#!/bin/bash

# Check for orphaned references after deletion
echo "Checking for orphaned references..."

# Should return 0 matches
PRPINITIAL_COUNT=$(grep -r "prp-initial-" .claude/ 2>/dev/null | wc -l)
CREATEINITIAL_COUNT=$(grep -r "create-initial" .claude/ 2>/dev/null | wc -l)

if [ "$PRPINITIAL_COUNT" -gt 0 ]; then
  echo "❌ FAIL: Found $PRPINITIAL_COUNT references to prp-initial-* agents"
  grep -r "prp-initial-" .claude/
  exit 1
fi

if [ "$CREATEINITIAL_COUNT" -gt 0 ]; then
  echo "❌ FAIL: Found $CREATEINITIAL_COUNT references to create-initial command"
  grep -r "create-initial" .claude/
  exit 1
fi

echo "✅ PASS: No orphaned references found"
```

---

### 3. Claude Code Git Command Mismanagement
**Severity**: Critical
**Category**: Repository State Corruption
**Affects**: Git history and working directory
**Source**: https://www.dolthub.com/blog/2025-06-30-claude-code-gotchas/

**What it is**:
Claude Code may use "weird Git commands" or leave artifacts in the working directory, potentially committing unintended files (like large binaries or test artifacts) or using confusing branch management.

**Why it's a problem**:
- Unintended files get committed (e.g., 100MB binaries)
- Git history becomes messy with unnecessary commits
- Working directory contains artifacts that break clean builds
- Difficult to rollback or clean up after automated Git operations

**How to detect it**:
- `git status` shows unexpected untracked or modified files
- Large files appear in git history unexpectedly
- Branch state doesn't match expectations
- Commit history has automated commits you didn't review

**How to avoid/fix**:
```bash
# ❌ WRONG - Let Claude Code handle git without oversight
# [Claude Code runs git commands automatically]
# [Commits artifacts, large files, or parallel implementations]

# ✅ RIGHT - Human-controlled Git workflow for deletions
# 1. Review current state BEFORE any changes
git status
git diff

# 2. Stash or commit unrelated changes first
git stash push -m "WIP: unrelated changes"

# 3. Manually perform deletions (don't let Claude Code auto-commit)
git rm .claude/agents/prp-initial-*.md
git rm .claude/commands/create-initial.md

# 4. Review EXACTLY what's being deleted
git status
git diff --staged

# Expected output:
# deleted: .claude/agents/prp-initial-feature-clarifier.md
# deleted: .claude/agents/prp-initial-codebase-researcher.md
# ... (6 total agent files)
# deleted: .claude/commands/create-initial.md

# 5. Update CLAUDE.md manually
# (Don't let Claude Code edit without review)

# 6. Review documentation changes
git diff CLAUDE.md
# Verify exactly 193 lines removed (lines 185-378)

# 7. Manually commit with descriptive message
git commit -m "chore: remove INITIAL.md factory workflow system

- Delete 6 prp-initial-* subagent files
- Delete create-initial command
- Remove factory documentation from CLAUDE.md (~193 lines)
- Preserve all prp-gen-* and prp-exec-* agents

Reduces agent count from 12+ to 10, returns to manual
INITIAL.md → /generate-prp → /execute-prp workflow"

# 8. Clean up working directory
git status
# Should show "nothing to commit, working tree clean"

# If artifacts remain:
git clean -fd -n  # Preview what would be deleted
git clean -fd     # Actually delete untracked files
```

**Prevention strategy**:
```bash
# Create .gitignore entries for common artifacts
echo "*.pyc" >> .gitignore
echo "*.pyo" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "*.swp" >> .gitignore
echo ".vibes/" >> .gitignore

# Use git hooks to prevent large file commits
# Create .git/hooks/pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Prevent commits of files larger than 10MB
MAX_SIZE=10485760  # 10MB in bytes

for file in $(git diff --cached --name-only); do
  if [ -f "$file" ]; then
    SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    if [ "$SIZE" -gt "$MAX_SIZE" ]; then
      echo "ERROR: File $file is too large ($SIZE bytes > 10MB)"
      echo "Large files should not be committed to the repository"
      exit 1
    fi
  fi
done
EOF
chmod +x .git/hooks/pre-commit
```

---

## High Priority Gotchas

### 1. Documentation Section Removal Creating Orphaned Content
**Severity**: High
**Category**: Documentation Coherence
**Affects**: CLAUDE.md structure and readability
**Source**: Markdown best practices research + local analysis

**What it is**:
Removing a large section (193 lines) from CLAUDE.md without verifying section boundaries can leave orphaned subsections, broken heading hierarchy, or disconnected content that references the removed section.

**Why it's a problem**:
- Table of contents links break (if auto-generated)
- Internal links to removed section return 404
- Heading hierarchy becomes inconsistent (skips from H2 to H4)
- Context flow is broken (section references content that no longer exists)

**How to detect it**:
- Broken internal links in rendered markdown
- Sections that start with "As mentioned above..." but "above" is deleted
- Heading level jumps (## → ####)
- References to "the factory workflow" without explanation

**How to avoid/fix**:
```bash
# ❌ WRONG - Delete lines without checking boundaries
sed -i '' '185,378d' CLAUDE.md
# [May delete partial sections, leave orphaned references]

# ✅ RIGHT - Careful boundary verification and removal
# 1. Read context BEFORE deleted section
sed -n '180,187p' CLAUDE.md

# Expected:
# Line 183: ---
# Line 185: ## INITIAL.md Factory Workflow
# Line 186: [content starts]

# 2. Read context AFTER deleted section
sed -n '375,382p' CLAUDE.md

# Expected:
# Line 378: [last line of factory section]
# Line 379: ---
# Line 380: ## Development Patterns

# 3. Verify exact line range
grep -n "## INITIAL.md Factory Workflow" CLAUDE.md  # Should be line 185
grep -n "## Development Patterns" CLAUDE.md          # Should be line 380

# 4. Extract section to review before deletion
sed -n '185,378p' CLAUDE.md > /tmp/factory_section_backup.md
wc -l /tmp/factory_section_backup.md  # Should show 194 lines

# 5. Delete section cleanly (preserve separator)
# Remove lines 185-378, keep line 379 (separator)
sed -i '' '185,378d' CLAUDE.md

# 6. Verify next section starts correctly
sed -n '185,188p' CLAUDE.md
# Expected:
# Line 185: ---
# Line 186: (blank or start of Development Patterns)
# Line 187: ## Development Patterns

# 7. Check for orphaned references to factory
grep -i "factory" CLAUDE.md
grep -i "create-initial" CLAUDE.md
grep -i "prp-initial-" CLAUDE.md
# Expected: Zero matches

# 8. Verify document structure
grep "^##" CLAUDE.md | head -20
# Should show clean heading hierarchy without gaps
```

**Markdown structure validation**:
```python
# Validation script to check heading hierarchy
import re

def validate_markdown_structure(file_path):
    with open(file_path) as f:
        lines = f.readlines()

    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
    prev_level = 0
    issues = []

    for i, line in enumerate(lines, 1):
        match = heading_pattern.match(line.strip())
        if match:
            level = len(match.group(1))
            heading = match.group(2)

            # Check for level jumps (e.g., ## → ####)
            if level > prev_level + 1 and prev_level > 0:
                issues.append(f"Line {i}: Heading level jump from {prev_level} to {level}: {heading}")

            prev_level = level

    return issues

# Run validation
issues = validate_markdown_structure('CLAUDE.md')
if issues:
    print("❌ Heading hierarchy issues found:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("✅ Heading hierarchy is valid")
```

---

### 2. Agent File Duplication Confusion
**Severity**: High
**Category**: Functionality Loss
**Affects**: PRP generation workflow
**Source**: Codebase analysis + agent architecture patterns

**What it is**:
Some agents exist in both `prp-gen-*` and `prp-initial-*` versions (e.g., `prp-gen-codebase-researcher.md` and `prp-initial-codebase-researcher.md`). Deleting the wrong version or assuming they're identical can lose functionality.

**Why it's a problem**:
- `prp-gen-*` and `prp-initial-*` versions may have different tools
- Implementation details may differ (e.g., output format, Archon integration)
- Deleting the active version breaks PRP generation
- No clear indication which version is canonical

**How to detect it**:
- Commands reference wrong agent version after deletion
- Agent invocation fails with "agent not found"
- Generated PRPs are missing sections or have wrong format

**How to avoid/fix**:
```bash
# ❌ WRONG - Assume prp-gen-* and prp-initial-* are identical
rm .claude/agents/prp-initial-codebase-researcher.md
# [Deletes without verifying prp-gen version has all functionality]

# ✅ RIGHT - Compare agent versions before deletion
# 1. List all potential duplicates
ls .claude/agents/prp-gen-*.md
ls .claude/agents/prp-initial-*.md

# 2. For each duplicate pair, compare frontmatter and tools
# Example: Compare codebase researcher agents
diff <(head -20 .claude/agents/prp-gen-codebase-researcher.md) \
     <(head -20 .claude/agents/prp-initial-codebase-researcher.md)

# 3. Check tool permissions specifically
grep "^tools:" .claude/agents/prp-gen-codebase-researcher.md
# Output: tools: Read, Write, Grep, Glob, mcp__archon__rag_search_code_examples

grep "^tools:" .claude/agents/prp-initial-codebase-researcher.md
# Output: tools: Read, Write, Grep, Glob, mcp__archon__rag_search_code_examples

# 4. Compare core responsibilities (lines 10-50)
diff <(sed -n '10,50p' .claude/agents/prp-gen-codebase-researcher.md) \
     <(sed -n '10,50p' .claude/agents/prp-initial-codebase-researcher.md)

# 5. If differences found, ensure prp-gen-* has ALL needed functionality
# If prp-initial-* has unique features, port them to prp-gen-* first

# 6. Verify which commands use which version
grep "prp-gen-codebase-researcher" .claude/commands/generate-prp.md
grep "prp-initial-codebase-researcher" .claude/commands/create-initial.md

# 7. Only delete prp-initial-* after confirming:
#    - prp-gen-* has all functionality
#    - No commands reference prp-initial-* version
#    - create-initial.md command is being deleted anyway

# 8. Safe deletion
git rm .claude/agents/prp-initial-codebase-researcher.md
```

**Comparison checklist**:
```markdown
## Agent Comparison Checklist (before deletion)

For each prp-initial-* agent:

### prp-initial-feature-clarifier
- [ ] Compared frontmatter (name, description, tools, model)
- [ ] Checked prp-gen-feature-analyzer has equivalent functionality
- [ ] Verified no unique tools or permissions
- [ ] Confirmed no commands reference prp-initial version

### prp-initial-codebase-researcher
- [ ] Compared frontmatter
- [ ] Checked prp-gen-codebase-researcher has equivalent functionality
- [ ] Verified no unique tools or permissions
- [ ] Confirmed no commands reference prp-initial version

### prp-initial-documentation-hunter
- [ ] Compared frontmatter
- [ ] Checked prp-gen-documentation-hunter has equivalent functionality
- [ ] Verified no unique tools or permissions
- [ ] Confirmed no commands reference prp-initial version

### prp-initial-example-curator
- [ ] Compared frontmatter
- [ ] Checked prp-gen-example-curator has equivalent functionality
- [ ] Verified no unique tools or permissions
- [ ] Confirmed no commands reference prp-initial version

### prp-initial-gotcha-detective
- [ ] Compared frontmatter
- [ ] Checked prp-gen-gotcha-detective has equivalent functionality
- [ ] Verified no unique tools or permissions
- [ ] Confirmed no commands reference prp-initial version

### prp-initial-assembler
- [ ] Compared frontmatter
- [ ] Checked prp-gen-assembler has equivalent functionality
- [ ] Verified no unique tools or permissions
- [ ] Confirmed no commands reference prp-initial version
```

---

### 3. Uncommitted Changes Conflict
**Severity**: High
**Category**: Git State Management
**Affects**: Clean deletion tracking
**Source**: Git best practices + DoltHub Claude Code gotchas

**What it is**:
Starting deletion task when git repository has uncommitted changes mixes the cleanup with other work, making it difficult to isolate, review, or rollback the deletion.

**Why it's a problem**:
- Can't cleanly rollback deletion without affecting other work
- `git diff` shows deletion mixed with unrelated changes
- Commit history is unclear about what changed
- Code review becomes difficult (too many changes in one commit)

**How to detect it**:
- `git status` shows modified or untracked files before starting
- `git diff --staged` shows changes unrelated to deletion
- Commit includes changes not mentioned in commit message

**How to avoid/fix**:
```bash
# ❌ WRONG - Start deletion with dirty git state
git status
# On branch main
# Changes not staged for commit:
#   modified:   some_other_file.py
#   modified:   another_file.md
# [Proceed with deletion anyway, mixing changes]

# ✅ RIGHT - Clean git state before deletion
# 1. Check git status first
git status

# 2. If uncommitted changes exist, handle them:

# Option A: Commit unrelated changes separately
git add some_other_file.py
git commit -m "fix: update some_other_file logic"

# Option B: Stash changes for later
git stash push -m "WIP: feature work in progress"

# Option C: Create separate branch for other work
git checkout -b feature/other-work
git add .
git commit -m "WIP: other feature work"
git checkout main

# 3. Verify clean state
git status
# Expected: "nothing to commit, working tree clean"

# 4. Now perform deletions in clean state
git rm .claude/agents/prp-initial-*.md
git rm .claude/commands/create-initial.md

# 5. Edit CLAUDE.md
# [Make changes]

# 6. Review ONLY deletion changes
git diff
git diff --staged

# 7. Commit ONLY deletion changes
git commit -m "chore: remove INITIAL factory workflow"

# 8. Restore previous work if stashed
git stash pop
# Or switch back to feature branch
git checkout feature/other-work
```

**Pre-deletion checklist**:
```bash
#!/bin/bash
# Pre-deletion validation script

echo "🔍 Pre-Deletion Validation"
echo "=========================="

# Check git status
echo -e "\n1. Checking git status..."
if [[ -z $(git status -s) ]]; then
  echo "✅ Working tree is clean"
else
  echo "❌ Working tree has uncommitted changes:"
  git status -s
  echo ""
  echo "Action required:"
  echo "  - Commit changes: git add -A && git commit -m 'message'"
  echo "  - Stash changes: git stash push -m 'WIP'"
  echo "  - Or review with: git diff"
  exit 1
fi

# Check repository health
echo -e "\n2. Checking repository health..."
if git fsck --quiet; then
  echo "✅ Repository is healthy"
else
  echo "❌ Repository has issues:"
  git fsck
  exit 1
fi

# Check branch is up to date
echo -e "\n3. Checking branch status..."
git fetch origin --quiet
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "no-upstream")
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "✅ Branch is up to date with remote"
elif [ "$REMOTE" = "no-upstream" ]; then
  echo "⚠️  No upstream branch configured"
else
  echo "❌ Branch is not up to date with remote"
  echo "Action required: git pull"
  exit 1
fi

echo -e "\n✅ All pre-deletion validations passed"
echo "Safe to proceed with file deletion"
```

---

## Medium Priority Gotchas

### 1. Example Files with Deprecated References
**Severity**: Medium
**Category**: Historical Documentation Confusion
**Affects**: `examples/prp_workflow_improvements/` directory
**Source**: Codebase analysis

**What it is**:
Example files in `examples/prp_workflow_improvements/` reference the `/create-initial` command and factory workflow, but these are intentionally kept as historical documentation showing pattern evolution.

**Why it's confusing**:
- New developers find examples that reference non-existent commands
- Unclear if examples are outdated or examples of what NOT to do
- Documentation seems contradictory (examples show factory, CLAUDE.md doesn't mention it)

**How to handle it**:
```bash
# ❌ WRONG - Delete example files to remove references
rm -rf examples/prp_workflow_improvements/
# [Loses valuable historical context of pattern evolution]

# ✅ RIGHT - Keep examples but add deprecation notice
# 1. Verify which example files reference factory
grep -r "create-initial" examples/
grep -r "prp-initial-" examples/

# 2. Add deprecation notice to example README
cat >> examples/prp_workflow_improvements/README.md << 'EOF'

---

## ⚠️ Deprecation Notice

**Note**: The INITIAL.md factory workflow documented in these examples has been deprecated and removed as of [DATE].

**What was removed**:
- 6 `prp-initial-*` subagent files
- `/create-initial` command
- Factory workflow documentation from CLAUDE.md

**Why it was removed**:
The factory automated a creative thinking task (requirements gathering) that benefits from human judgment. Manual INITIAL.md creation takes 10-20 minutes and produces better results.

**Current workflow**:
1. **Manual INITIAL.md creation** (10-20 minutes)
2. `/generate-prp INITIAL.md` (automated research & PRP creation)
3. `/execute-prp PRP.md` (automated implementation)

**Historical value**:
These examples are preserved to show the evolution of the PRP workflow and document why automation isn't always the answer. They serve as a case study in identifying over-engineering.

EOF

# 3. Add warning to specific example files
for file in examples/prp_workflow_improvements/*.md; do
  # Skip README (already updated)
  [[ "$file" == *"README.md" ]] && continue

  # Add deprecation warning at top of file
  sed -i '' '1i\
> **⚠️ DEPRECATED**: This example references the INITIAL.md factory workflow which has been removed. See README for current workflow.\
' "$file"
done

# 4. Commit documentation updates
git add examples/prp_workflow_improvements/
git commit -m "docs: add deprecation notices to factory workflow examples

Mark INITIAL factory workflow examples as deprecated with
explanation of why the pattern was removed. Examples are
preserved for historical context and as case study in
identifying over-engineering."
```

**Deprecation notice template**:
```markdown
> **⚠️ DEPRECATED**: This example references the INITIAL.md factory workflow which has been removed as of [DATE].
>
> **Reason for removal**: The factory automated creative thinking tasks that require human judgment.
>
> **Current workflow**: Manual INITIAL.md → `/generate-prp` → `/execute-prp`
>
> **Why this example is preserved**: Historical documentation of pattern evolution and case study in avoiding over-automation.
```

---

### 2. Agent Count References Scattered in Documentation
**Severity**: Medium
**Category**: Documentation Inconsistency
**Affects**: CLAUDE.md and README files
**Source**: Documentation analysis

**What it is**:
Documentation references "12+ agents" or "6 prp-initial agents" in multiple locations. After deletion, these numbers are wrong but easy to miss during search-and-replace.

**Why it's a problem**:
- Documentation claims different agent counts in different places
- Users are confused about how many agents exist
- Reduces trust in documentation accuracy
- Hard to find all references (various phrasings)

**How to detect it**:
- Grep for agent count references
- Manual documentation review
- Inconsistent numbers in different sections

**How to avoid/fix**:
```bash
# ❌ WRONG - Update only obvious references
sed -i '' 's/12+ agents/10 agents/g' CLAUDE.md
# [Misses variations like "12 agents", "6 prp-initial agents", "6 factory agents"]

# ✅ RIGHT - Comprehensive agent count update
# 1. Find ALL agent count references (various phrasings)
grep -n "12 agents\|12+ agents" CLAUDE.md
grep -n "6 prp-initial\|6 factory\|6 INITIAL" CLAUDE.md
grep -n "subagent" CLAUDE.md | grep -i "6\|12"

# 2. Check for count descriptions
grep -n "agent count" CLAUDE.md
grep -n "total.*agent" CLAUDE.md
grep -n "agent.*total" CLAUDE.md

# 3. Update each reference individually (context-aware)
# Example replacements:
# "12+ agents" → "10 agents" (6 prp-gen + 4 prp-exec)
# "6 prp-initial-* agents" → [DELETE - no longer exists]
# "6 factory agents" → [DELETE - no longer exists]

# 4. Verify final agent count
ls .claude/agents/prp-gen-*.md | wc -l   # Should be 6
ls .claude/agents/prp-exec-*.md | wc -l  # Should be 4
ls .claude/agents/prp-*.md | wc -l       # Should be 10

# 5. Create standardized agent count reference
cat > /tmp/agent_count.md << 'EOF'
## Agent Architecture

**Total Agents**: 10 specialized agents

**PRP Generation Agents** (6):
- prp-gen-feature-analyzer
- prp-gen-codebase-researcher
- prp-gen-documentation-hunter
- prp-gen-example-curator
- prp-gen-gotcha-detective
- prp-gen-assembler

**PRP Execution Agents** (4):
- prp-exec-task-analyzer
- prp-exec-implementer
- prp-exec-test-generator
- prp-exec-validator

**General Purpose Agents** (2):
- documentation-manager
- validation-gates
EOF

# 6. Add to CLAUDE.md if agent reference table doesn't exist
# Or update existing table to match

# 7. Verify consistency
grep -n "10 agents\|6.*prp-gen\|4.*prp-exec" CLAUDE.md
```

**Search patterns for agent count references**:
```bash
# Comprehensive search script
#!/bin/bash

echo "🔍 Finding all agent count references..."

# Pattern 1: Explicit numbers
grep -n "12\|6.*initial\|6.*factory" CLAUDE.md | grep -i agent

# Pattern 2: Descriptive phrases
grep -n "prp-initial-\*" CLAUDE.md
grep -n "factory.*agent" CLAUDE.md
grep -n "INITIAL.*agent" CLAUDE.md

# Pattern 3: Agent lists or tables
grep -n "subagent.*table\|agent.*list" CLAUDE.md

# Pattern 4: Workflow descriptions
grep -n "6.*subagent\|6.*specialized" CLAUDE.md

echo ""
echo "✅ Review each match and update to reflect 10 total agents"
echo "   (6 prp-gen + 4 prp-exec, excluding 2 general purpose)"
```

---

### 3. Workflow Description Inconsistency
**Severity**: Medium
**Category**: Documentation Clarity
**Affects**: CLAUDE.md workflow sections
**Source**: Documentation structure analysis

**What it is**:
After removing the factory section, workflow descriptions may still imply three entry points (manual INITIAL, /create-initial, /generate-prp) instead of the simplified two-step flow (manual INITIAL → /generate-prp).

**Why it's a problem**:
- Users are confused about correct workflow
- Documentation describes commands that don't exist
- Multiple "correct" workflows create decision paralysis
- Unclear which approach is recommended

**How to handle it**:
```markdown
# ❌ WRONG - Leave inconsistent workflow descriptions
## Workflows Available:
1. Manual INITIAL.md creation
2. `/create-initial` command (automated)
3. `/generate-prp` from INITIAL.md

# ✅ RIGHT - Unified workflow description
## PRP-Driven Development Workflow

**The streamlined workflow** (2 steps):

1. **Create INITIAL.md manually** (10-20 minutes)
   - Describe the feature or change
   - Include requirements, constraints, examples
   - Specify technology preferences
   - Outline success criteria
   - Template: `prps/templates/INITIAL_EXAMPLE.md`

2. **Generate comprehensive PRP** (<10 minutes, automated)
   ```bash
   /generate-prp prps/INITIAL_<feature-name>.md
   ```
   - Searches Archon knowledge base
   - Extracts codebase patterns
   - Finds official documentation
   - Identifies gotchas and pitfalls
   - Outputs: `prps/<feature-name>.md`

3. **Execute PRP** (30-50% faster with parallel execution)
   ```bash
   /execute-prp prps/<feature-name>.md
   ```
   - Analyzes task dependencies
   - Implements in parallel groups
   - Generates tests (70%+ coverage)
   - Validates all gates pass

**Why manual INITIAL.md?**
- Requires human judgment and creative thinking
- Only takes 10-20 minutes
- Produces better requirements than automation
- Context engineering is about augmenting humans, not replacing them

**What's automated?**
- Research (documentation, examples, gotchas)
- Implementation (code generation, testing)
- Validation (iterative fixes until passing)
```

**Update checklist**:
```bash
# Find all workflow descriptions
grep -n "workflow" CLAUDE.md -i -A 5

# Check for outdated patterns:
grep -n "create-initial\|factory.*workflow\|automated INITIAL" CLAUDE.md

# Verify simplified workflow is documented clearly
grep -n "Manual INITIAL" CLAUDE.md
grep -n "/generate-prp" CLAUDE.md
grep -n "/execute-prp" CLAUDE.md

# Ensure no references to "3 workflows" or "multiple approaches"
grep -n "three workflow\|3 workflow\|multiple.*workflow" CLAUDE.md
```

---

## Low Priority Gotchas

### 1. Git History Contains Deleted Files
**Severity**: Low
**Category**: Repository Size
**Affects**: Repository history and clone time

**What it is**:
Deleted files remain in git history, increasing repository size and clone time. Files are accessible via git history even after deletion.

**How to handle**:
```bash
# For this task: DO NOTHING
# Files are small (markdown files, <50KB total)
# History preservation is valuable for understanding evolution
# No need to rewrite history for minor cleanup

# If history rewrite was needed (NOT recommended here):
# git filter-branch --force --index-filter \
#   'git rm --cached --ignore-unmatch .claude/agents/prp-initial-*.md' \
#   --prune-empty --tag-name-filter cat -- --all
#
# WARNING: History rewriting breaks all forks and clones
```

---

### 2. Command File Naming Collision Risk
**Severity**: Low
**Category**: Namespace Confusion
**Affects**: Future command creation

**What it is**:
After deleting `/create-initial`, someone might create a new command with the same name but different functionality, causing confusion for users who remember the old command.

**How to handle**:
```bash
# Document in CHANGELOG or DEPRECATED.md
cat >> DEPRECATED.md << 'EOF'
## Removed Commands

### `/create-initial` (Removed: 2025-10)
**Reason**: Over-automation of creative thinking task
**Replacement**: Manual INITIAL.md creation (10-20 min)
**Do not reuse this name**: Preserve namespace to avoid confusion
EOF

# Add comment in commands directory README
cat >> .claude/commands/README.md << 'EOF'
## Reserved Names (Do Not Reuse)
- `create-initial.md` - Previously used for factory workflow (deprecated 2025-10)
EOF
```

---

## Library-Specific Quirks

### Git (Version Control)

**Common Mistakes**:
1. **Using `rm` instead of `git rm`**: Requires separate `git add` to stage deletion
   - **How to avoid**: Always use `git rm` for tracked files

2. **Wildcard expansion issues**: `git rm *.md` may not expand as expected
   - **How to avoid**: Use quotes: `git rm "*.md"` or explicit paths

3. **Deleting modified files**: `git rm` fails if file has unstaged changes
   - **How to avoid**: Use `git rm -f` (force) or stage changes first

**Best Practices**:
- Always run `git status` before and after deletions
- Use `git diff --staged` to review deletions before commit
- Commit deletions separately from other changes
- Write descriptive commit messages explaining what and why

---

### Markdown Documentation

**Common Mistakes**:
1. **Removing section without checking internal links**: Breaks `[link](#section-name)` references
   - **How to avoid**: Grep for `#initial-factory` or similar anchors

2. **Breaking heading hierarchy**: Removing H2 between H1 and H3
   - **How to avoid**: Verify heading levels before/after deletion

3. **Orphaned list items**: List item references deleted section
   - **How to avoid**: Search for "see INITIAL factory" or similar phrases

**Best Practices**:
- Preserve section separators (`---`) for visual structure
- Verify table of contents is updated (if auto-generated)
- Check that surrounding sections flow logically
- Use markdown linters to validate structure

---

### Claude Code Subagents

**Version-Specific Issues**:
- **v1.0.124+**: SlashCommand tool only recognizes commands with `description` frontmatter
- **Project-level agents**: Take precedence over global agents with same name

**Common Mistakes**:
1. **Deleting agent file while command references it**: Runtime error
   - **How to avoid**: Grep for agent name in all command files first

2. **Assuming frontmatter format doesn't matter**: Claude Code parses YAML strictly
   - **How to avoid**: Validate YAML before deleting agents

3. **Not checking tool dependencies**: Deleted agent may be only one with specific tool
   - **How to avoid**: Check tool permissions in remaining agents

**Best Practices**:
- Use `/agents` command to verify agents are recognized
- Test commands after agent deletion
- Keep agent naming conventions consistent
- Document agent architecture in CLAUDE.md

---

## Performance Gotchas

### 1. Grep Performance on Large Repositories
**Impact**: Search time for reference verification
**Affects**: Pre-deletion validation

**The problem**:
```bash
# ❌ SLOW - Search entire repository including node_modules, .git
grep -r "prp-initial-" .
# Time: 30+ seconds on large repos
```

**The solution**:
```bash
# ✅ FAST - Exclude irrelevant directories
grep -r "prp-initial-" . \
  --exclude-dir=node_modules \
  --exclude-dir=.git \
  --exclude-dir=__pycache__ \
  --exclude-dir=.vibes
# Time: <1 second

# Or use ripgrep (much faster)
rg "prp-initial-" --type md
# Automatically excludes .git, respects .gitignore
```

**Benchmarks**:
- `grep -r` (full repo): ~30 seconds
- `grep -r` (with excludes): ~1 second
- `rg` (ripgrep): <0.5 seconds
- Improvement: 60x faster

---

## Security Gotchas

### 1. Accidental Deletion of Active Configuration
**Severity**: High
**Type**: Configuration Loss
**Affects**: Claude Code agent system
**CVE**: N/A

**Vulnerability**:
```bash
# ❌ VULNERABLE - Wildcard deletion without verification
rm .claude/agents/prp-*.md
# Could delete prp-gen-* and prp-exec-* agents by mistake!
```

**Secure Implementation**:
```bash
# ✅ SECURE - Explicit deletion with verification
# 1. List files first
ls .claude/agents/prp-initial-*.md

# Expected output:
# .claude/agents/prp-initial-assembler.md
# .claude/agents/prp-initial-codebase-researcher.md
# .claude/agents/prp-initial-documentation-hunter.md
# .claude/agents/prp-initial-example-curator.md
# .claude/agents/prp-initial-feature-clarifier.md
# .claude/agents/prp-initial-gotcha-detective.md

# 2. Delete explicitly (no wildcards)
git rm .claude/agents/prp-initial-assembler.md
git rm .claude/agents/prp-initial-codebase-researcher.md
git rm .claude/agents/prp-initial-documentation-hunter.md
git rm .claude/agents/prp-initial-example-curator.md
git rm .claude/agents/prp-initial-feature-clarifier.md
git rm .claude/agents/prp-initial-gotcha-detective.md

# 3. Verify only intended files deleted
git status
# Should show exactly 6 deletions, all prp-initial-*

# Security measures applied:
# 1. Explicit file paths (no wildcards)
# 2. Pre-deletion verification (ls first)
# 3. Post-deletion verification (git status)
```

**Testing for this vulnerability**:
```bash
# Test: Verify active agents are preserved
#!/bin/bash

EXPECTED_AGENTS=(
  "prp-gen-feature-analyzer"
  "prp-gen-codebase-researcher"
  "prp-gen-documentation-hunter"
  "prp-gen-example-curator"
  "prp-gen-gotcha-detective"
  "prp-gen-assembler"
  "prp-exec-task-analyzer"
  "prp-exec-implementer"
  "prp-exec-test-generator"
  "prp-exec-validator"
)

echo "Verifying active agents are preserved..."
MISSING=0

for agent in "${EXPECTED_AGENTS[@]}"; do
  if [ ! -f ".claude/agents/${agent}.md" ]; then
    echo "❌ MISSING: ${agent}.md"
    MISSING=$((MISSING + 1))
  fi
done

if [ $MISSING -eq 0 ]; then
  echo "✅ All active agents preserved"
else
  echo "❌ FAIL: $MISSING active agents missing"
  exit 1
fi
```

---

## Integration Gotchas

### Archon MCP Server + File Deletion

**Known Issues**:
1. **Task references deleted files**: Archon tasks may link to files being deleted
   - **Solution**: Update task notes before deletion, document what was removed

2. **Knowledge base references**: Archon may have ingested deleted agent files
   - **Solution**: Not a problem - historical knowledge is valuable for context

**Configuration Gotchas**:
```bash
# ❌ WRONG - Delete files before updating Archon tasks
git rm .claude/agents/prp-initial-*.md
# [Archon tasks still reference deleted files]

# ✅ RIGHT - Update Archon first, then delete
# 1. Update relevant tasks with notes
mcp__archon__manage_task("update",
  task_id="gotcha-detective-task",
  status="done",
  notes="Deleted prp-initial-gotcha-detective.md as part of factory removal"
)

# 2. Document in project
mcp__archon__manage_project("update",
  project_id="41b007e8-54fc-43af-bd8d-114c6814fb5a",
  notes="Removed 6 prp-initial-* agents + create-initial command. See commit [hash]"
)

# 3. Then delete files
git rm .claude/agents/prp-initial-*.md
```

---

## Version Compatibility Matrix

| Component | Version | Compatible? | Known Issues |
|-----------|---------|-------------|--------------|
| Git | 2.30+ | ✅ | None |
| Claude Code | 1.0.124+ | ✅ | SlashCommand tool requires description frontmatter |
| Archon MCP | Current | ✅ | None |
| Markdown | CommonMark | ✅ | None |
| Ripgrep | 13.0+ | ✅ | Much faster than grep for large repos |

---

## Testing Gotchas

**Common Test Pitfalls**:
1. **Not testing commands after agent deletion**: Commands fail silently if agents missing
   ```bash
   # Better test pattern after deletion
   # Manually invoke /generate-prp with test INITIAL.md
   # Verify all prp-gen-* agents are invoked (not prp-initial-*)
   # Check for "agent not found" errors in output
   ```

2. **Assuming grep zero results means success**: Could mean grep failed or pattern wrong
   ```bash
   # Better verification pattern
   RESULT=$(grep -r "prp-initial-" .claude/ 2>&1)
   if [ $? -eq 0 ]; then
     echo "❌ FAIL: Found references to deleted agents"
     echo "$RESULT"
     exit 1
   elif echo "$RESULT" | grep -q "No such file"; then
     echo "✅ PASS: No references found (verified)"
   else
     echo "⚠️  WARNING: Grep may have failed"
     exit 1
   fi
   ```

---

## Deployment Gotchas

**Environment-Specific Issues**:
- **Development**: Tests may reference deleted agent files in test fixtures
- **Staging**: Documentation may be cached (restart Claude Code to reload)
- **Production**: User workflows may break if they reference `/create-initial`

**Configuration Issues**:
```bash
# ❌ WRONG - Deploy without clearing Claude Code cache
# [Claude Code still sees deleted agents in cache]

# ✅ RIGHT - Clear cache and restart
# 1. Exit Claude Code completely
# 2. Clear cache (if applicable)
rm -rf ~/.claude/cache  # (if exists)
# 3. Restart Claude Code
# 4. Verify agents are recognized correctly
claude --debug  # Shows which agents are loaded
```

---

## Anti-Patterns to Avoid

### 1. Wildcard Deletion Without Verification
**What it is**:
Using `rm .claude/agents/prp-*.md` thinking it will only match `prp-initial-*`, but it actually matches `prp-gen-*` and `prp-exec-*` as well.

**Why it's bad**:
- Deletes active agents used by core workflows
- Breaks PRP generation and execution
- Difficult to recover (must restore from git or rewrite)

**Better pattern**:
```bash
# List first, verify, then delete explicitly
ls .claude/agents/prp-initial-*.md
# Verify output shows ONLY prp-initial-* files
# Then delete each explicitly (shown in Security Gotchas section)
```

---

### 2. Removing Section Without Boundary Verification
**What it is**:
Using `sed '185,378d'` to remove lines without verifying those are exact section boundaries.

**Why it's bad**:
- May delete partial sentences from surrounding sections
- Could remove section separator leaving heading without context
- Breaks document flow if line numbers are off by even 1 line

**Better pattern**:
```bash
# Verify boundaries before deletion
sed -n '183,187p' CLAUDE.md  # Check start
sed -n '376,381p' CLAUDE.md  # Check end
# Only proceed if boundaries are exactly as expected
```

---

### 3. Committing Without Review
**What it is**:
Running `git commit -a -m "cleanup"` without reviewing `git diff` first.

**Why it's bad**:
- May commit unintended deletions
- Could include debug files or artifacts
- Doesn't document what or why in commit message

**Better pattern**:
```bash
# Always review before commit
git diff --staged
git status
# Read every file in the diff
# Write comprehensive commit message explaining what and why
```

---

### 4. Assuming Commands Auto-Update
**What it is**:
Believing that `/generate-prp` command will automatically update to use `prp-gen-*` agents after deleting `prp-initial-*` agents.

**Why it's bad**:
- Commands have hardcoded agent references
- Deletion doesn't trigger updates
- Command breaks with "agent not found" error

**Better pattern**:
```bash
# Verify command references before deletion
grep "prp-initial-" .claude/commands/*.md
# If matches found, update commands first OR
# Verify create-initial.md is being deleted (so references don't matter)
```

---

### 5. No Rollback Plan
**What it is**:
Deleting files without having a clear rollback strategy if something goes wrong.

**Why it's bad**:
- If deletion breaks workflows, difficult to recover quickly
- Git history can restore files, but what commit?
- May not remember exact configuration of deleted files

**Better pattern**:
```bash
# Create rollback tag before deletion
git tag -a factory-removal-checkpoint -m "Before INITIAL factory removal"

# Perform deletions
git rm .claude/agents/prp-initial-*.md
# ... etc

# If something goes wrong:
git reset --hard factory-removal-checkpoint

# After confirming deletion is successful:
git tag -d factory-removal-checkpoint  # Clean up tag
```

---

## Gotcha Checklist for Implementation

Before marking PRP complete, verify these gotchas are addressed:

- [ ] **Git State**: Repository is clean before starting (no uncommitted changes)
- [ ] **Repository Health**: `git fsck` passes, no corruption warnings
- [ ] **Reference Check**: No commands reference prp-initial-* agents (except create-initial.md being deleted)
- [ ] **Agent Comparison**: Verified prp-gen-* agents have all functionality of prp-initial-* versions
- [ ] **Explicit Deletion**: Files deleted one-by-one (no wildcards), verified with `ls` first
- [ ] **Documentation Boundaries**: Section boundaries verified (lines 185-378 exactly)
- [ ] **Orphaned References**: Zero grep matches for "prp-initial-", "create-initial", "INITIAL.md Factory"
- [ ] **Heading Hierarchy**: CLAUDE.md has consistent heading levels (no jumps)
- [ ] **Agent Count Updated**: All references to "12+ agents" changed to "10 agents"
- [ ] **Workflow Description**: Documentation shows simplified workflow (Manual INITIAL → /generate-prp)
- [ ] **Example Deprecation**: Historical examples marked as deprecated with explanation
- [ ] **Git Commit**: Staged changes reviewed with `git diff --staged`, descriptive commit message
- [ ] **Functional Test**: `/generate-prp` and `/execute-prp` commands work correctly
- [ ] **Rollback Tag**: Created checkpoint tag before deletion (optional but recommended)

---

## Sources Referenced

### From Archon
- **9a7d4217c64c9a0a**: Anthropic Documentation (Claude Code subagent system)
- **b8565aff9938938b**: Context Engineering Intro (PRP workflow patterns)
- **e9eb05e2bf38f125**: Kubechain examples (cleanup patterns)

### From Web
- **Git Reference Corruption**: https://stackoverflow.com/questions/2998832/git-pull-fails-unable-to-resolve-reference
- **Claude Code Gotchas**: https://www.dolthub.com/blog/2025-06-30-claude-code-gotchas/
- **Git Repository Corruption**: https://www.mindfulchase.com/explore/troubleshooting-tips/troubleshooting-git-repository-corruption-fixing-broken-objects,-missing-commits,-and-index-inconsistencies.html
- **Git Documentation**: https://git-scm.com/docs/git-rm
- **Conventional Commits**: https://www.conventionalcommits.org/en/v1.0.0/
- **Markdown Best Practices**: https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown
- **Hidden Dependencies**: https://learn.microsoft.com/en-us/power-platform/alm/removing-dependencies

---

## Recommendations for PRP Assembly

When generating the PRP:
1. **Include critical gotchas** in "Known Gotchas & Library Quirks" section
   - Git reference corruption prevention
   - Orphaned command reference detection
   - Claude Code git mismanagement oversight

2. **Reference solutions** in "Implementation Blueprint"
   - Pre-deletion validation script
   - Explicit deletion commands (no wildcards)
   - Documentation boundary verification
   - Post-deletion reference check

3. **Add detection tests** to validation gates
   - `grep -r "prp-initial-" .claude/` should return 0 matches
   - `ls .claude/agents/prp-gen-*.md | wc -l` should return 6
   - `ls .claude/agents/prp-exec-*.md | wc -l` should return 4
   - CLAUDE.md section transitions verified

4. **Warn about version issues** in documentation references
   - Claude Code v1.0.124+ required for SlashCommand tool
   - Git 2.30+ recommended for fsck features

5. **Highlight anti-patterns** to avoid
   - Wildcard deletion (delete explicitly)
   - Uncommitted changes (clean state first)
   - No review (always `git diff --staged`)
   - Assuming equivalence (compare agents first)

## Confidence Assessment

**Gotcha Coverage**: 9/10
- **Security**: High confidence we found major security issues (accidental deletion of active agents via wildcards)
- **Performance**: Good coverage of performance pitfalls (grep optimization, cache clearing)
- **Common Mistakes**: Excellent coverage of git, documentation, and workflow gotchas

**Gaps**:
- Limited documentation on Claude Code internal caching behavior (version-specific)
- No automated CLAUDE.md structure validator found (manual review required)
- Agent interaction patterns not fully documented (Anthropic docs are high-level)

**Strengths**:
- Comprehensive git safety patterns from multiple sources
- Real-world Claude Code gotchas from DoltHub production experience
- Practical solutions with code examples for every gotcha
- Testing and verification patterns for each issue

**Recommendations for Implementation**:
- Follow pre-deletion validation checklist strictly
- Use explicit file deletion (no wildcards)
- Verify git state before AND after deletion
- Test commands manually after cleanup
- Review all documentation boundaries carefully

This gotcha analysis provides comprehensive coverage of cleanup/removal risks with actionable solutions for each issue identified.