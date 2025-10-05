# PRP: Initial Factory Removal

**Generated**: 2025-10-05
**Based On**: prps/INITIAL_initial_factory_removal.md
**Archon Project**: 41b007e8-54fc-43af-bd8d-114c6814fb5a

---

## Goal

Remove the INITIAL.md Factory workflow system (6 subagents + 1 command + documentation) that automated INITIAL.md creation through a multi-agent process. This cleanup task will:
- Delete 7 files (~2,500 lines total)
- Remove ~193 lines from CLAUDE.md
- Reduce agent count from 12+ to 10 specialized agents
- Return to the proven workflow: Manual INITIAL.md (10-20 min) → /generate-prp → /execute-prp

**End State**:
- All `prp-initial-*` agent files removed (6 files)
- `/create-initial` command file removed (1 file)
- INITIAL.md Factory section removed from CLAUDE.md (193 lines)
- All `prp-gen-*` and `prp-exec-*` agents preserved (10 files)
- Clean git commit with descriptive message
- Documentation updated to reflect simplified workflow
- Zero references to deleted files in codebase

## Why

**Current Pain Points**:
- **Over-automation of creative work**: The factory automated requirements gathering, a task that requires human judgment and benefits from thinking time
- **Unnecessary complexity**: 6 additional agents and 200+ lines of documentation for a 10-20 minute manual task
- **Maintenance burden**: 50% more agents to maintain, update, and test
- **Confusion**: Two ways to start PRP workflow creates decision paralysis

**Business Value**:
- **Simplification**: 50% reduction in agent count (12+ → 10)
- **Clearer workflow**: Single entry point (manual INITIAL.md) eliminates confusion
- **Better requirements**: Manual INITIAL.md creation produces better, more thoughtful requirements than automation
- **Reduced maintenance**: Fewer agents to keep in sync with evolving PRP methodology
- **Faster onboarding**: New users learn one workflow instead of two

**Pattern Recognition**: This is a textbook example of identifying over-engineering. The factory was built to optimize a task that doesn't benefit from optimization. Requirements gathering requires human creativity, context understanding, and judgment - exactly what AI shouldn't automate.

## What

### Core Features

This is a **cleanup/removal task** with the following scope:

**Files to Delete** (7 total):
1. `.claude/agents/prp-initial-feature-clarifier.md` (~300 lines)
2. `.claude/agents/prp-initial-codebase-researcher.md` (~300 lines)
3. `.claude/agents/prp-initial-documentation-hunter.md` (~300 lines)
4. `.claude/agents/prp-initial-example-curator.md` (~300 lines)
5. `.claude/agents/prp-initial-gotcha-detective.md` (~300 lines)
6. `.claude/agents/prp-initial-assembler.md` (~300 lines)
7. `.claude/commands/create-initial.md` (~531 lines)

**Documentation to Update**:
- Remove CLAUDE.md lines 185-378 (193 lines) - entire "INITIAL.md Factory Workflow" section
- Update agent count references from "12+ agents" to "10 agents"
- Update workflow descriptions to show only: Manual INITIAL → /generate-prp → /execute-prp

**Files to Preserve** (10 agents + 2 commands):
- All `prp-gen-*` agents (6 files) - used by /generate-prp
- All `prp-exec-*` agents (4 files) - used by /execute-prp
- `/generate-prp` command
- `/execute-prp` command
- INITIAL_EXAMPLE.md template
- Historical examples in examples/ directory

### Success Criteria

- [ ] All 6 prp-initial-* agent files deleted from .claude/agents/
- [ ] create-initial.md command file deleted from .claude/commands/
- [ ] Lines 185-378 removed from CLAUDE.md (193 lines)
- [ ] Zero grep matches for "prp-initial-" in .claude/ directory
- [ ] Zero grep matches for "create-initial" in CLAUDE.md
- [ ] Zero grep matches for "INITIAL.md Factory" in CLAUDE.md
- [ ] All 6 prp-gen-* agents still exist
- [ ] All 4 prp-exec-* agents still exist
- [ ] /generate-prp command still exists and works
- [ ] /execute-prp command still exists and works
- [ ] CLAUDE.md renders cleanly without gaps or orphaned content
- [ ] Agent count references updated throughout documentation
- [ ] Git commit completed with descriptive message
- [ ] No uncommitted changes remaining

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Git & Cleanup Best Practices
- url: https://git-scm.com/docs/git-rm
  sections:
    - "SYNOPSIS" - Basic usage patterns
    - "DESCRIPTION" - When to use git rm vs rm
    - "OPTIONS" - Force deletion and caching options
  why: Official reference for safe file deletion with git
  critical_gotchas:
    - Using `rm` requires separate `git add` to stage deletion
    - `git rm` removes file AND stages deletion in one step
    - Wildcards may not expand as expected - use explicit paths

- url: https://www.conventionalcommits.org/en/v1.0.0/
  sections:
    - "Summary" - Commit message structure
    - "Specification" - Type prefixes (chore, refactor, remove)
    - "Why Use Conventional Commits" - Benefits for changelog
  why: Standard format for cleanup commit messages
  critical_gotchas:
    - Use `chore:` for maintenance tasks like this
    - Add `BREAKING CHANGE:` footer if removing user-facing command
    - Keep subject line under 50 characters

- url: https://docs.claude.com/en/docs/claude-code/sub-agents/
  sections:
    - "Creating and Managing Subagents" - Lifecycle management
    - "File Structure and Storage" - Project vs user-level agents
    - "Best Practices" - When to delete subagents
  why: Understanding Claude Code agent system and safe deletion
  critical_gotchas:
    - Project-level agents (.claude/agents/) take precedence over global
    - No database dependencies - filesystem deletion is safe
    - Must ensure no commands reference deleted agents

- url: https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown
  sections:
    - "Markdown Best Practices" - Documentation maintenance
    - "Structure and Formatting" - Section boundaries
  why: Guidance for cleanly removing large documentation sections
  critical_gotchas:
    - "Delete cruft frequently and in small batches"
    - Preserve section separators (---) for visual structure
    - Verify heading hierarchy remains consistent after removal

- url: https://www.dolthub.com/blog/2025-06-30-claude-code-gotchas/
  sections:
    - "Git Command Management" - Claude Code's git patterns
    - "Common Pitfalls" - What goes wrong in automation
  why: Real-world gotchas from production Claude Code usage
  critical_gotchas:
    - Claude Code may use "weird Git commands"
    - Can commit unintended files (large binaries, artifacts)
    - Human oversight required for git operations

# ESSENTIAL LOCAL FILES
- file: examples/initial_factory_removal/example_1_agent_structure.md
  why: Shows structure of agent files being deleted
  pattern: YAML frontmatter + structured markdown sections
  critical: Each agent is ~300 lines with consistent structure

- file: examples/initial_factory_removal/example_2_command_structure.md
  why: Shows structure of command file being deleted
  pattern: Multi-phase workflow with subagent orchestration
  critical: 531 lines orchestrating 6 subagents, entry point to factory

- file: examples/initial_factory_removal/example_3_documentation_section.md
  why: Shows exact CLAUDE.md lines to remove (185-378)
  pattern: Large markdown section with clear boundaries
  critical: Line 179 (---) preserved, line 380 is next section

- file: examples/initial_factory_removal/example_4_cleanup_commit_pattern.md
  why: Shows proven cleanup commit patterns from this repository
  pattern: Simple messages, complete deletion, trust git history
  critical: Commits 2b91ff6 and 0a92e5c demonstrate confidence in deletion

- file: prps/research/gotchas.md
  why: Comprehensive gotcha analysis with solutions
  pattern: 15 gotchas with detection and fix code
  critical: Git corruption prevention, orphaned references, wildcard dangers

- file: prps/research/codebase-patterns.md
  why: Shows git safety patterns and deletion workflows
  pattern: Explicit staging, verification, commit best practices
  critical: Anti-patterns to avoid (wildcards, uncommitted changes, no review)
```

### Current Codebase Tree

```
.claude/
├── agents/
│   ├── documentation-manager.md        # KEEP - general purpose
│   ├── validation-gates.md             # KEEP - general purpose
│   ├── prp-gen-feature-analyzer.md    # KEEP - PRP generation
│   ├── prp-gen-codebase-researcher.md # KEEP - PRP generation
│   ├── prp-gen-documentation-hunter.md # KEEP - PRP generation
│   ├── prp-gen-example-curator.md     # KEEP - PRP generation
│   ├── prp-gen-gotcha-detective.md    # KEEP - PRP generation
│   ├── prp-gen-assembler.md           # KEEP - PRP generation
│   ├── prp-exec-task-analyzer.md      # KEEP - PRP execution
│   ├── prp-exec-implementer.md        # KEEP - PRP execution
│   ├── prp-exec-test-generator.md     # KEEP - PRP execution
│   ├── prp-exec-validator.md          # KEEP - PRP execution
│   ├── prp-initial-feature-clarifier.md    # DELETE
│   ├── prp-initial-codebase-researcher.md  # DELETE
│   ├── prp-initial-documentation-hunter.md # DELETE
│   ├── prp-initial-example-curator.md      # DELETE
│   ├── prp-initial-gotcha-detective.md     # DELETE
│   └── prp-initial-assembler.md            # DELETE
└── commands/
    ├── generate-prp.md         # KEEP - core workflow
    ├── execute-prp.md          # KEEP - core workflow
    ├── create-initial.md       # DELETE - deprecated workflow
    ├── prep-parallel.md        # KEEP - supporting command
    ├── execute-parallel.md     # KEEP - supporting command
    └── list-prps.md            # KEEP - supporting command

CLAUDE.md
  - Lines 1-184: Keep (existing content)
  - Lines 185-378: DELETE (INITIAL.md Factory Workflow section)
  - Line 179: Keep (section separator ---)
  - Lines 380+: Keep (Development Patterns section onwards)

examples/
└── initial_factory_removal/
    ├── README.md                           # Created by example curator
    ├── example_1_agent_structure.md        # Created by example curator
    ├── example_2_command_structure.md      # Created by example curator
    ├── example_3_documentation_section.md  # Created by example curator
    └── example_4_cleanup_commit_pattern.md # Created by example curator
```

### Desired Codebase Tree

```
.claude/
├── agents/
│   ├── documentation-manager.md        # 2 general purpose agents
│   ├── validation-gates.md
│   ├── prp-gen-feature-analyzer.md    # 6 PRP generation agents
│   ├── prp-gen-codebase-researcher.md
│   ├── prp-gen-documentation-hunter.md
│   ├── prp-gen-example-curator.md
│   ├── prp-gen-gotcha-detective.md
│   ├── prp-gen-assembler.md
│   ├── prp-exec-task-analyzer.md      # 4 PRP execution agents
│   ├── prp-exec-implementer.md
│   ├── prp-exec-test-generator.md
│   └── prp-exec-validator.md
└── commands/
    ├── generate-prp.md         # Core PRP workflows
    ├── execute-prp.md
    ├── prep-parallel.md        # Supporting commands
    ├── execute-parallel.md
    └── list-prps.md

CLAUDE.md
  - Lines 1-184: Unchanged
  - Lines 185+: Development Patterns section (was line 380)
  - Total: ~193 lines shorter
  - Agent count references updated: "12+ agents" → "10 agents"
  - Workflow simplified: Manual INITIAL → /generate-prp → /execute-prp

**Deleted Files** (7 total):
- 6 prp-initial-* agent files
- 1 create-initial.md command file

**Preserved Files** (12 agents + 5 commands):
- 10 specialized PRP agents (prp-gen-* and prp-exec-*)
- 2 general purpose agents
- 2 core PRP commands
- 3 supporting commands
- All historical examples
```

### Known Gotchas & Library Quirks

```bash
# CRITICAL 1: Git Reference Corruption During Deletion
# When git operations are interrupted (CTRL-C, crash), reference files in
# .git/refs/ can become corrupted with NULL characters
# Source: https://stackoverflow.com/questions/2998832/git-pull-fails-unable-to-resolve-reference

# ❌ WRONG - Interrupting git operations
git rm .claude/agents/prp-initial-*.md
# [User hits CTRL-C or system crashes]
# Result: Repository becomes unusable until corruption fixed

# ✅ RIGHT - Safe deletion with verification
# 1. Check repository health first
git fsck --full

# 2. Ensure clean git state
git status  # Should show "nothing to commit, working tree clean"

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
git commit -m "chore: remove INITIAL factory workflow system"


# CRITICAL 2: Orphaned Command References After Deletion
# Other commands or files may reference deleted agents, causing runtime errors
# Source: Claude Code subagent documentation + codebase analysis

# ❌ WRONG - Delete files without checking references
rm .claude/agents/prp-initial-*.md
# [Commands now reference non-existent agents]

# ✅ RIGHT - Comprehensive reference check before deletion
# Find ALL references to agents being deleted
grep -r "prp-initial-feature-clarifier" .claude/
grep -r "prp-initial-codebase-researcher" .claude/
grep -r "prp-initial-documentation-hunter" .claude/
grep -r "prp-initial-example-curator" .claude/
grep -r "prp-initial-gotcha-detective" .claude/
grep -r "prp-initial-assembler" .claude/
grep -r "create-initial" .claude/

# Expected: Only matches in files being deleted or CLAUDE.md (updating)
# If unexpected matches: Update those files first before deletion

# After deletion, verify no dangling references
grep -r "prp-initial-" .claude/
grep -r "create-initial" .claude/
# Expected: Zero matches


# CRITICAL 3: Claude Code Git Command Mismanagement
# Claude Code may commit unintended files or use confusing branch management
# Source: https://www.dolthub.com/blog/2025-06-30-claude-code-gotchas/

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

# 5. Manually commit with descriptive message
git commit -m "chore: remove INITIAL.md factory workflow system

- Delete 6 prp-initial-* subagent files
- Delete create-initial command
- Remove factory documentation from CLAUDE.md (~193 lines)
- Preserve all prp-gen-* and prp-exec-* agents

Reduces agent count from 12+ to 10, returns to manual
INITIAL.md → /generate-prp → /execute-prp workflow"


# CRITICAL 4: Documentation Section Removal Creating Orphaned Content
# Removing 193 lines without verifying boundaries can leave orphaned subsections
# Source: Markdown best practices + local analysis

# ❌ WRONG - Delete lines without checking boundaries
sed -i '' '185,378d' CLAUDE.md
# [May delete partial sections, leave orphaned references]

# ✅ RIGHT - Careful boundary verification and removal
# 1. Read context BEFORE deleted section
sed -n '180,187p' CLAUDE.md
# Expected: Line 183: ---
#           Line 185: ## INITIAL.md Factory Workflow

# 2. Read context AFTER deleted section
sed -n '375,382p' CLAUDE.md
# Expected: Line 378: [last line of factory section]
#           Line 379: ---
#           Line 380: ## Development Patterns

# 3. Verify exact line range
grep -n "## INITIAL.md Factory Workflow" CLAUDE.md  # Line 185
grep -n "## Development Patterns" CLAUDE.md         # Line 380

# 4. Delete section cleanly (preserve separator)
# Remove lines 185-378, keep line 179 (separator)
sed -i '' '185,378d' CLAUDE.md

# 5. Check for orphaned references
grep -i "factory" CLAUDE.md
grep -i "create-initial" CLAUDE.md
grep -i "prp-initial-" CLAUDE.md
# Expected: Zero matches


# CRITICAL 5: Agent File Duplication Confusion
# Some agents exist in both prp-gen-* and prp-initial-* versions
# Deleting the wrong version or assuming they're identical loses functionality
# Source: Codebase analysis + agent architecture patterns

# ❌ WRONG - Assume prp-gen-* and prp-initial-* are identical
rm .claude/agents/prp-initial-codebase-researcher.md
# [Deletes without verifying prp-gen version has all functionality]

# ✅ RIGHT - Compare agent versions before deletion
# 1. Compare frontmatter and tools
diff <(head -20 .claude/agents/prp-gen-codebase-researcher.md) \
     <(head -20 .claude/agents/prp-initial-codebase-researcher.md)

# 2. Check tool permissions specifically
grep "^tools:" .claude/agents/prp-gen-codebase-researcher.md
grep "^tools:" .claude/agents/prp-initial-codebase-researcher.md

# 3. Verify which commands use which version
grep "prp-gen-codebase-researcher" .claude/commands/generate-prp.md
grep "prp-initial-codebase-researcher" .claude/commands/create-initial.md

# 4. Only delete prp-initial-* after confirming:
#    - prp-gen-* has all functionality
#    - No commands reference prp-initial-* (except create-initial being deleted)
#    - create-initial.md command is being deleted anyway


# HIGH PRIORITY: Wildcard Deletion Without Verification
# Using rm .claude/agents/prp-*.md matches prp-gen-* and prp-exec-* too!
# Source: Common shell pitfall

# ❌ WRONG - Wildcard deletion
rm .claude/agents/prp-*.md
# Deletes ALL agents including active prp-gen-* and prp-exec-*!

# ✅ RIGHT - Explicit deletion with verification
# List first, verify, then delete explicitly
ls .claude/agents/prp-initial-*.md
# Verify output shows ONLY prp-initial-* files
# Then delete each explicitly (see CRITICAL 1)


# HIGH PRIORITY: Uncommitted Changes Conflict
# Starting deletion with uncommitted changes mixes cleanup with other work
# Source: Git best practices

# ❌ WRONG - Start deletion with dirty git state
git status
# Changes not staged for commit:
#   modified: some_other_file.py
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

# 3. Verify clean state
git status  # Expected: "nothing to commit, working tree clean"

# 4. Now perform deletions in clean state


# MEDIUM PRIORITY: Agent Count References Scattered
# Documentation references "12+ agents" in multiple locations with various phrasings
# Source: Documentation analysis

# ❌ WRONG - Update only obvious references
sed -i '' 's/12+ agents/10 agents/g' CLAUDE.md
# [Misses "12 agents", "6 prp-initial agents", "6 factory agents"]

# ✅ RIGHT - Comprehensive agent count update
# Find ALL agent count references
grep -n "12 agents\|12+ agents" CLAUDE.md
grep -n "6 prp-initial\|6 factory\|6 INITIAL" CLAUDE.md
grep -n "agent count" CLAUDE.md

# Update each reference individually based on context:
# "12+ agents" → "10 agents" (6 prp-gen + 4 prp-exec)
# "6 prp-initial-* agents" → [DELETE - no longer exists]
# "6 factory agents" → [DELETE - no longer exists]


# MEDIUM PRIORITY: Example Files with Deprecated References
# Example files in examples/prp_workflow_improvements/ reference /create-initial
# Source: Codebase analysis

# ❌ WRONG - Delete example files to remove references
rm -rf examples/prp_workflow_improvements/
# [Loses valuable historical context of pattern evolution]

# ✅ RIGHT - Keep examples but add deprecation notice
# Add deprecation notice to example README:
cat >> examples/prp_workflow_improvements/README.md << 'EOF'

---

## ⚠️ Deprecation Notice

The INITIAL.md factory workflow documented in these examples has been
deprecated and removed as of 2025-10-05.

**Reason**: Factory automated creative thinking that requires human judgment.

**Current workflow**: Manual INITIAL.md → /generate-prp → /execute-prp

**Historical value**: These examples document pattern evolution and serve
as a case study in identifying over-automation.
EOF


# LOW PRIORITY: Git History Contains Deleted Files
# Deleted files remain in git history, increasing repository size
# Source: Git documentation

# For this task: DO NOTHING
# Files are small (markdown, <50KB total)
# History preservation is valuable for understanding evolution
# No need to rewrite history for minor cleanup

# If history rewrite was needed (NOT recommended here):
# git filter-branch --force --index-filter \
#   'git rm --cached --ignore-unmatch .claude/agents/prp-initial-*.md' \
#   --prune-empty --tag-name-filter cat -- --all
# WARNING: History rewriting breaks all forks and clones
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting deletion, complete these steps:**

1. **Study extracted examples** (10 minutes):
   - Read `examples/initial_factory_removal/README.md`
   - Review example 1 (agent structure)
   - Review example 2 (command structure)
   - Review example 3 (documentation boundaries)
   - Review example 4 (cleanup commit patterns)

2. **Verify git state** (2 minutes):
   ```bash
   # Check repository is healthy
   git fsck --full

   # Ensure clean working tree
   git status  # Should show "nothing to commit, working tree clean"

   # If uncommitted changes exist, stash or commit them separately
   git stash push -m "WIP: other work"
   ```

3. **Verify file existence** (1 minute):
   ```bash
   # Confirm all 6 agent files exist
   ls .claude/agents/prp-initial-*.md | wc -l  # Should be 6

   # Confirm command file exists
   ls .claude/commands/create-initial.md  # Should exist

   # List exact files to delete
   ls .claude/agents/prp-initial-*.md
   ```

4. **Pre-deletion reference check** (3 minutes):
   ```bash
   # Find references to agents being deleted
   grep -r "prp-initial-" .claude/ | tee /tmp/prp-initial-refs.txt

   # Find references to command being deleted
   grep -r "create-initial" . | tee /tmp/create-initial-refs.txt

   # Expected: Only matches in files being deleted or CLAUDE.md
   # Review output files to ensure no unexpected references
   ```

### Task List (Execute in Order)

```yaml
Task 1: Delete Agent Files
RESPONSIBILITY: Remove 6 prp-initial-* agent definition files from .claude/agents/
FILES TO DELETE:
  - .claude/agents/prp-initial-feature-clarifier.md
  - .claude/agents/prp-initial-codebase-researcher.md
  - .claude/agents/prp-initial-documentation-hunter.md
  - .claude/agents/prp-initial-example-curator.md
  - .claude/agents/prp-initial-gotcha-detective.md
  - .claude/agents/prp-initial-assembler.md

PATTERN TO FOLLOW: Explicit deletion from example_4_cleanup_commit_pattern.md

SPECIFIC STEPS:
  1. Delete files one by one (no wildcards)
     git rm .claude/agents/prp-initial-feature-clarifier.md
     git rm .claude/agents/prp-initial-codebase-researcher.md
     git rm .claude/agents/prp-initial-documentation-hunter.md
     git rm .claude/agents/prp-initial-example-curator.md
     git rm .claude/agents/prp-initial-gotcha-detective.md
     git rm .claude/agents/prp-initial-assembler.md

  2. Verify staged deletions
     git status
     # Expected: 6 files deleted

  3. Do NOT commit yet (will commit all changes together)

VALIDATION:
  - git status shows 6 deleted files
  - All deletions are staged (green "deleted:" lines)
  - No untracked files created
  - No wildcards were used

---

Task 2: Delete Command File
RESPONSIBILITY: Remove create-initial.md command file from .claude/commands/
FILES TO DELETE:
  - .claude/commands/create-initial.md

PATTERN TO FOLLOW: Same explicit deletion pattern from Task 1

SPECIFIC STEPS:
  1. Delete command file
     git rm .claude/commands/create-initial.md

  2. Verify staged deletions
     git status
     # Expected: 7 files deleted total (6 agents + 1 command)

  3. Do NOT commit yet

VALIDATION:
  - git status shows 7 total deleted files
  - create-initial.md is staged for deletion
  - No backup files created

---

Task 3: Remove CLAUDE.md Factory Section
RESPONSIBILITY: Remove lines 185-378 (193 lines) from CLAUDE.md
FILES TO MODIFY:
  - CLAUDE.md

PATTERN TO FOLLOW: Surgical section removal from example_3_documentation_section.md

SPECIFIC STEPS:
  1. Read CLAUDE.md and verify section boundaries
     sed -n '180,187p' CLAUDE.md  # Before section
     sed -n '375,382p' CLAUDE.md  # After section
     # Expected: Line 185 starts "## INITIAL.md Factory Workflow"
     #           Line 379 is "---"
     #           Line 380 is "## Development Patterns"

  2. Backup CLAUDE.md (optional but safe)
     cp CLAUDE.md CLAUDE.md.backup

  3. Remove lines 185-378 (preserve line 179 separator)
     # Use text editor or sed:
     sed -i '' '185,378d' CLAUDE.md

  4. Verify next section starts correctly
     sed -n '185,188p' CLAUDE.md
     # Expected: Line 185 is "---"
     #           Line 186 or 187 is "## Development Patterns"

  5. Stage CLAUDE.md changes
     git add CLAUDE.md

  6. Verify git diff shows correct line removal
     git diff --staged CLAUDE.md | head -50
     # Should show 193 lines removed

VALIDATION:
  - CLAUDE.md is ~193 lines shorter
  - Section transition is clean (no orphaned content)
  - Next section ("Development Patterns") starts properly
  - git diff shows expected line removal

---

Task 4: Update Agent Count References
RESPONSIBILITY: Update all references to agent counts throughout CLAUDE.md
FILES TO MODIFY:
  - CLAUDE.md

PATTERN TO FOLLOW: Comprehensive search and replace

SPECIFIC STEPS:
  1. Find all agent count references
     grep -n "12 agent\|12+ agent" CLAUDE.md
     grep -n "6 prp-initial\|6 factory" CLAUDE.md

  2. Update each reference based on context:
     - "12+ agents" → "10 agents" (6 prp-gen + 4 prp-exec)
     - "6 prp-initial-* agents" → [DELETE or rephrase]
     - "6 factory agents" → [DELETE or rephrase]
     # Use text editor for context-aware replacements

  3. Stage CLAUDE.md changes
     git add CLAUDE.md

  4. Verify changes
     git diff --staged CLAUDE.md

VALIDATION:
  - No references to "12 agents" or "12+ agents" remain
  - No references to "6 prp-initial" or "6 factory" remain
  - References to "10 agents" are accurate
  - Context flows naturally after updates

---

Task 5: Verification and Reference Check
RESPONSIBILITY: Ensure no broken references to deleted files remain
FILES TO CHECK:
  - All files in .claude/ directory
  - CLAUDE.md
  - Example files

PATTERN TO FOLLOW: Comprehensive grep verification

SPECIFIC STEPS:
  1. Search for orphaned agent references
     grep -r "prp-initial-" .claude/
     # Expected: Zero matches

  2. Search for orphaned command references
     grep -r "create-initial" CLAUDE.md
     # Expected: Zero matches

  3. Search for factory workflow references
     grep -i "INITIAL.md Factory" CLAUDE.md
     # Expected: Zero matches

  4. Verify preserved agents still exist
     ls .claude/agents/prp-gen-*.md | wc -l   # Should be 6
     ls .claude/agents/prp-exec-*.md | wc -l  # Should be 4
     ls .claude/agents/prp-*.md | wc -l       # Should be 10

  5. Verify preserved commands still exist
     ls .claude/commands/generate-prp.md  # Should exist
     ls .claude/commands/execute-prp.md   # Should exist

VALIDATION:
  - Zero grep matches for "prp-initial-" in .claude/
  - Zero grep matches for "create-initial" in CLAUDE.md
  - Zero grep matches for "INITIAL.md Factory" in CLAUDE.md
  - All prp-gen-* agents present (6 files)
  - All prp-exec-* agents present (4 files)
  - Core commands still exist

---

Task 6: Add Deprecation Notice to Examples
RESPONSIBILITY: Update examples/prp_workflow_improvements/README.md with deprecation notice
FILES TO MODIFY:
  - examples/prp_workflow_improvements/README.md

PATTERN TO FOLLOW: Deprecation notice pattern from gotchas.md

SPECIFIC STEPS:
  1. Append deprecation notice to example README
     cat >> examples/prp_workflow_improvements/README.md << 'EOF'

---

## ⚠️ Deprecation Notice

**Note**: The INITIAL.md factory workflow documented in these examples has been deprecated and removed as of 2025-10-05.

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

  2. Stage changes
     git add examples/prp_workflow_improvements/README.md

  3. Verify changes
     git diff --staged examples/prp_workflow_improvements/README.md

VALIDATION:
  - Deprecation notice added to example README
  - Notice explains what was removed and why
  - Notice documents current workflow
  - Examples preserved for historical context

---

Task 7: Git Commit
RESPONSIBILITY: Commit all changes with descriptive message
FILES TO COMMIT:
  - 6 deleted agent files (staged in Task 1)
  - 1 deleted command file (staged in Task 2)
  - CLAUDE.md (modified in Tasks 3 and 4)
  - examples/prp_workflow_improvements/README.md (modified in Task 6)

PATTERN TO FOLLOW: Cleanup commit pattern from example_4_cleanup_commit_pattern.md

SPECIFIC STEPS:
  1. Review all staged changes
     git status
     git diff --staged --stat
     # Expected: 7 files deleted, 2 files modified

  2. Review detailed diff
     git diff --staged
     # Verify all changes are intentional

  3. Commit with descriptive message following Conventional Commits
     git commit -m "chore: remove INITIAL.md factory workflow system

- Delete 6 prp-initial-* subagent files
- Delete create-initial command
- Remove factory documentation from CLAUDE.md (~193 lines)
- Update agent count references from 12+ to 10
- Add deprecation notice to historical examples
- Preserve all prp-gen-* and prp-exec-* agents

Reduces agent count by 50% and returns to simplified workflow:
Manual INITIAL.md (10-20 min) → /generate-prp → /execute-prp

The factory automated creative thinking that requires human judgment.
This cleanup eliminates unnecessary complexity while preserving core
PRP generation and execution capabilities."

  4. Verify commit
     git log -1 --stat
     # Review commit message and changed files

  5. Clean up backup if created
     rm -f CLAUDE.md.backup

VALIDATION:
  - Commit includes all intended changes
  - Commit message is descriptive and follows Conventional Commits
  - No uncommitted changes remain (git status clean)
  - Backup file removed

---

Task 8: Final Verification
RESPONSIBILITY: Verify complete cleanup and system functionality
FILES TO CHECK:
  - All .claude/ files
  - CLAUDE.md
  - Git repository state

PATTERN TO FOLLOW: Final validation checklist

SPECIFIC STEPS:
  1. Verify file deletions complete
     # Should fail (files don't exist):
     ls .claude/agents/prp-initial-*.md 2>&1 | grep "No such file"
     ls .claude/commands/create-initial.md 2>&1 | grep "No such file"

  2. Verify preserved files intact
     ls .claude/agents/prp-gen-*.md | wc -l   # Should be 6
     ls .claude/agents/prp-exec-*.md | wc -l  # Should be 4
     ls .claude/commands/generate-prp.md      # Should exist
     ls .claude/commands/execute-prp.md       # Should exist

  3. Verify no orphaned references
     grep -r "prp-initial-" .claude/ 2>&1 | grep -v "Binary file"
     # Expected: No matches

     grep "create-initial\|INITIAL.md Factory" CLAUDE.md
     # Expected: No matches

  4. Verify CLAUDE.md structure
     grep "^##" CLAUDE.md | head -20
     # Should show clean heading hierarchy

  5. Verify git state
     git status  # Should show "nothing to commit, working tree clean"

  6. Verify repository health
     git fsck --quiet
     # Expected: No errors

VALIDATION:
  - All prp-initial-* files deleted
  - create-initial.md deleted
  - All prp-gen-* and prp-exec-* agents preserved
  - Core commands preserved
  - No orphaned references in codebase
  - CLAUDE.md has consistent structure
  - Git repository is healthy
  - Working tree is clean
```

---

## Validation Loop

### Level 1: File Deletion Verification

```bash
# Verify files are deleted
ls .claude/agents/prp-initial-*.md
# Expected: "No such file or directory"

ls .claude/commands/create-initial.md
# Expected: "No such file or directory"

# Count remaining agents
ls .claude/agents/prp-*.md | wc -l
# Expected: 10 (6 prp-gen + 4 prp-exec)

# Verify git shows deletions
git status
# Expected: Shows deleted files if not yet committed
# Or "nothing to commit" if already committed

# Verify commit exists
git log -1 --oneline
# Expected: Shows commit message about factory removal
```

### Level 2: Reference Verification

```bash
# Search for orphaned references
grep -r "prp-initial-" .claude/
# Expected: No matches (or only in git history)

grep "create-initial" CLAUDE.md
# Expected: No matches

grep "INITIAL.md Factory" CLAUDE.md
# Expected: No matches

# Verify agent count references updated
grep "10 agents" CLAUDE.md
# Expected: One or more matches

grep "12 agent\|12+ agent" CLAUDE.md
# Expected: No matches
```

### Level 3: Documentation Structure Check

```bash
# Verify CLAUDE.md heading hierarchy
grep "^##" CLAUDE.md

# Expected output should show:
# ## Directory Structure (or similar)
# ...
# ## Development Patterns (previously line 380)
# ...

# No "## INITIAL.md Factory Workflow" should appear

# Verify section separators intact
grep -n "^---$" CLAUDE.md | head -10
# Should show separator lines with reasonable spacing

# Check for orphaned subsections
grep "^###" CLAUDE.md | head -20
# Verify all subsections have parent sections
```

### Level 4: Functional Test

```bash
# Test that /generate-prp command still works
# (Manual test - requires user interaction)
# 1. Open Claude Code
# 2. Type: /generate-prp
# 3. Verify command is recognized
# 4. Cancel or test with sample INITIAL.md

# Test that /execute-prp command still works
# (Manual test - requires user interaction)
# 1. Type: /execute-prp
# 2. Verify command is recognized
# 3. Cancel test

# Verify /create-initial command is gone
# 1. Type: /create-initial
# 2. Expected: Command not recognized or error message
```

### Level 5: Repository Health Check

```bash
# Check repository integrity
git fsck --full
# Expected: No errors or warnings

# Verify no corrupted references
ls -la .git/refs/heads/
ls -la .git/refs/remotes/
# Expected: Normal file sizes (no zero-byte files)

# Check for orphaned objects (optional)
git count-objects -v
# Should show reasonable counts

# Verify branch is clean
git status
# Expected: "nothing to commit, working tree clean"
```

---

## Final Validation Checklist

Before marking this task complete, verify:

**File Deletions**:
- [ ] All 6 prp-initial-* agent files deleted
- [ ] create-initial.md command file deleted
- [ ] Zero references to deleted files in .claude/ directory
- [ ] No backup files remaining (.backup, .old, etc.)

**Documentation Updates**:
- [ ] ~193 lines removed from CLAUDE.md (lines 185-378)
- [ ] INITIAL.md Factory section completely removed
- [ ] Section transition is clean (no gaps or orphans)
- [ ] Agent count updated from "12+ agents" to "10 agents"
- [ ] Workflow documentation shows: Manual INITIAL → /generate-prp → /execute-prp
- [ ] Deprecation notice added to examples README

**Preserved Functionality**:
- [ ] All prp-gen-* agents still exist (6 files)
- [ ] All prp-exec-* agents still exist (4 files)
- [ ] /generate-prp command intact and functional
- [ ] /execute-prp command intact and functional
- [ ] INITIAL_EXAMPLE.md template intact
- [ ] Historical examples preserved in examples/ directory

**Quality Checks**:
- [ ] CLAUDE.md renders cleanly without orphaned sections
- [ ] Heading hierarchy is consistent (no level jumps)
- [ ] No broken internal links or references
- [ ] Git repository health check passes (git fsck)
- [ ] Working tree is clean (nothing to commit)

**Git Commit**:
- [ ] All changes committed with descriptive message
- [ ] Commit follows Conventional Commits format (chore:)
- [ ] Commit message explains what and why
- [ ] No uncommitted changes remaining

**Verification Tests**:
- [ ] grep -r "prp-initial-" .claude/ returns zero matches
- [ ] grep "create-initial" CLAUDE.md returns zero matches
- [ ] grep "INITIAL.md Factory" CLAUDE.md returns zero matches
- [ ] ls .claude/agents/prp-gen-*.md shows 6 files
- [ ] ls .claude/agents/prp-exec-*.md shows 4 files
- [ ] git log shows cleanup commit

---

## Anti-Patterns to Avoid

### 1. Wildcard Deletion Without Verification
**What**: Using `rm .claude/agents/prp-*.md` thinking it only matches prp-initial-*
**Why Bad**: Deletes ALL agents including active prp-gen-* and prp-exec-*
**Impact**: Breaks PRP generation and execution, difficult to recover
**Instead**: List files first, verify output, then delete explicitly (one by one)

### 2. Removing Section Without Boundary Verification
**What**: Using `sed '185,378d'` without verifying exact boundaries
**Why Bad**: May delete partial sentences from surrounding sections
**Impact**: Breaks document flow, creates orphaned content
**Instead**: Read lines before/after, verify boundaries match expectations exactly

### 3. Committing Without Review
**What**: Running `git commit -a -m "cleanup"` without reviewing diff
**Why Bad**: May commit unintended deletions or include artifacts
**Impact**: Messy git history, difficult rollback, unclear changes
**Instead**: Always `git diff --staged` before commit, review every changed file

### 4. Assuming Commands Auto-Update
**What**: Believing /generate-prp will automatically use prp-gen-* after deleting prp-initial-*
**Why Bad**: Commands have hardcoded agent references that don't auto-update
**Impact**: Command breaks with "agent not found" error
**Instead**: Verify command references before deletion (grep for agent names)

### 5. No Rollback Plan
**What**: Deleting files without a clear rollback strategy
**Why Bad**: If deletion breaks workflows, difficult to recover quickly
**Impact**: Extended downtime, unclear how to restore
**Instead**: Create rollback tag before deletion: `git tag -a factory-removal-checkpoint`

### 6. Skipping Pre-Deletion Reference Check
**What**: Deleting files without checking if other files reference them
**Why Bad**: Creates orphaned references that cause runtime errors
**Impact**: Broken workflows, confusing error messages
**Instead**: Comprehensive grep for all agent and command names before deletion

### 7. Ignoring Git State
**What**: Starting deletion when git has uncommitted changes
**Why Bad**: Mixes cleanup with other work, difficult to isolate or rollback
**Impact**: Unclear git history, hard to review changes
**Instead**: Ensure clean working tree first (git status shows clean)

---

## Success Metrics

**Quantitative Metrics**:
- Files deleted: 7 (6 agents + 1 command)
- Lines removed: ~2,524 total
  - Agent files: ~1,800 lines
  - Command file: ~531 lines
  - Documentation: ~193 lines
- Agent count reduction: 50% (12 → 10 specialized agents)
- Documentation reduction: ~193 lines from CLAUDE.md
- Git commits: 1 clean commit with descriptive message

**Qualitative Metrics**:
- Workflow simplified: Manual INITIAL → /generate-prp → /execute-prp (no /create-initial)
- Documentation clarity: Single workflow path, no decision paralysis
- Maintenance burden: 50% fewer agents to maintain
- Pattern recognition: Demonstrates over-engineering identification

**Validation Metrics**:
- Zero grep matches for "prp-initial-" in .claude/
- Zero grep matches for "create-initial" in CLAUDE.md
- Zero grep matches for "INITIAL.md Factory" in CLAUDE.md
- All preserved agents functional (10 files)
- All preserved commands functional (2 core + 3 supporting)
- Git repository health: No errors from `git fsck`

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research documents synthesized (feature analysis, codebase patterns, documentation, examples, gotchas)
- ✅ **Clear task breakdown**: 8 sequential tasks with explicit commands and validation steps
- ✅ **Proven patterns**: 4 extracted code examples showing exact deletion patterns
- ✅ **Validation strategy**: 5-level validation loop with specific commands and expected outputs
- ✅ **Error handling**: 15 gotchas documented with detection and solutions
- ✅ **Documentation**: 5+ official sources + 7 local file references
- ✅ **Examples extracted**: 4 complete code examples with 620-line README
- ✅ **Anti-patterns**: 7 documented with explanations and better alternatives

**Deduction reasoning** (-1 point):
- **Manual verification required**: Some checks require human judgment (CLAUDE.md rendering, command functionality tests)
- **Context-dependent updates**: Agent count references need context-aware replacement (not simple search-replace)
- **No automated validation**: No script provided to validate CLAUDE.md structure after section removal

**Strengths**:
1. **Complete deletion scope**: All 7 files identified with exact paths
2. **Line-precise documentation update**: Exact line numbers (185-378) for CLAUDE.md removal
3. **Comprehensive gotcha coverage**: 15 gotchas with code solutions
4. **Real examples extracted**: 4 actual code files showing deletion patterns
5. **Git safety emphasized**: Multiple gotchas about git corruption and safety
6. **Verification at every step**: Each task has explicit validation criteria

**Mitigations for deductions**:
- **Manual checks**: Provide specific commands for verification (grep patterns, heading checks)
- **Context-aware updates**: List exact search patterns and what to look for
- **Validation checklist**: Comprehensive final checklist with 30+ items

**Implementation confidence**:
- Time estimate: 15-20 minutes for experienced developer
- Risk level: Low (clear boundaries, explicit commands, comprehensive verification)
- Rollback ease: High (git tag checkpoint, small change scope)
- Success probability: 95%+ (very clear instructions, proven patterns)

**What makes this PRP production-ready**:
1. Every command is executable (no pseudocode in task steps)
2. Every validation has expected output documented
3. Every gotcha has both detection and solution code
4. Examples show actual files being deleted (not abstract patterns)
5. Git safety is emphasized throughout (prevent corruption)
6. Comprehensive reference check prevents orphaned references
