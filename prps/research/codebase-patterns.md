# Codebase Patterns: Initial Factory Removal

## Overview

This document extracts patterns for safely removing the INITIAL.md factory workflow (6 agents + 1 command) while preserving the core PRP generation/execution system. The key insight: this is a **reversal pattern** - removing over-automation and returning to a simpler, more effective workflow where manual INITIAL.md creation (10-20 min) precedes automated PRP generation.

## Architectural Patterns

### Pattern 1: Agent File Organization
**Source**: `.claude/agents/` directory structure
**Relevance**: 10/10
**What it does**: Organizes agents by workflow phase with consistent naming conventions

**Key Techniques**:
```
.claude/agents/
├── documentation-manager.md       # General purpose
├── validation-gates.md            # General purpose
├── prp-gen-*.md                  # PRP Generation (6 agents) - PRESERVE
├── prp-exec-*.md                 # PRP Execution (4 agents) - PRESERVE
└── prp-initial-*.md              # INITIAL Factory (6 agents) - DELETE
```

**Agent Naming Convention**:
- `prp-gen-{phase}`: PRP generation subagents (from INITIAL.md)
- `prp-exec-{phase}`: PRP execution subagents (from PRP)
- `prp-initial-{phase}`: INITIAL factory subagents (DEPRECATED)

**When to use**:
- When organizing multi-phase workflows with subagents
- When creating parallel execution groups
- When maintaining clear separation between workflow stages

**How to adapt**:
- Delete all `prp-initial-*.md` files (6 files)
- Preserve all `prp-gen-*.md` files (6 files)
- Preserve all `prp-exec-*.md` files (4 files)
- Update CLAUDE.md to reflect 10 total agents (was 12+)

**Why this pattern**:
- Clear namespace prevents confusion between similar agents
- Prefix-based grouping makes batch operations easy
- Phase-based naming documents execution order

### Pattern 2: Agent Frontmatter Structure
**Source**: All agent files in `.claude/agents/`
**Relevance**: 9/10
**What it does**: Uses YAML frontmatter to define agent metadata and tool permissions

**Key Techniques**:
```yaml
---
name: prp-gen-codebase-researcher
description: USE PROACTIVELY for codebase pattern extraction...
tools: Read, Write, Grep, Glob, mcp__archon__rag_search_code_examples
color: green
---
```

**When to use**:
- Every agent definition file needs frontmatter
- Tool permissions must be explicitly listed
- Description should trigger proactive use

**How to adapt**:
- After deleting prp-initial-* agents, verify prp-gen-* agents have correct tools
- No changes needed to frontmatter format
- Ensure no tools reference deleted agents

**Why this pattern**:
- Claude Code uses frontmatter for agent discovery
- Tool restrictions enforce security boundaries
- Proactive triggers enable autonomous execution

### Pattern 3: Command File Structure
**Source**: `.claude/commands/create-initial.md` (to be deleted)
**Relevance**: 8/10
**What it does**: Defines slash commands that orchestrate multi-agent workflows

**Key Techniques**:
```markdown
# Command Name

## Trigger Patterns
- List of user phrases that activate this command

## The N-Phase Workflow
### Phase 0: Setup (YOU handle this)
### Phase 1: Subagent execution
### Phase N: Completion

## Archon Integration
- Health check → Create project → Create tasks → Execute
```

**When to use**:
- Creating orchestration commands for multi-agent workflows
- Defining clear phase boundaries with responsibilities
- Integrating with Archon for task tracking

**How to adapt**:
- Delete `.claude/commands/create-initial.md` entirely
- Preserve `/generate-prp` and `/execute-prp` commands
- Update CLAUDE.md to remove all references to `/create-initial`

**Why this pattern**:
- Phased execution enables parallel optimization
- Clear ownership (YOU vs subagent) prevents ambiguity
- Archon integration provides observability

### Pattern 4: Documentation Section Removal
**Source**: `CLAUDE.md` lines 185-378 (INITIAL.md Factory Workflow section)
**Relevance**: 10/10
**What it does**: Shows how to cleanly remove large documentation sections while maintaining coherence

**Key Techniques**:
```markdown
# BEFORE (lines 183-185)
---

## INITIAL.md Factory Workflow
[~193 lines of factory documentation]

---

## Development Patterns

# AFTER (lines 183-185)
---

## Development Patterns
```

**When to use**:
- Removing deprecated features from documentation
- Maintaining document flow after large deletions
- Preserving section separators and structure

**How to adapt**:
1. Read CLAUDE.md to identify exact line range (185-378)
2. Read lines before/after to verify boundaries
3. Delete section completely
4. Preserve separator lines (`---`) for document structure
5. Verify next section starts correctly

**Why this pattern**:
- Clean section boundaries prevent orphaned content
- Preserving separators maintains visual structure
- Verification prevents broken references

### Pattern 5: Duplicate Agent Consolidation
**Source**: Comparison of `prp-gen-*` vs `prp-initial-*` agents
**Relevance**: 9/10
**What it does**: Handles cases where similar agents exist with different prefixes

**Key Techniques**:
```bash
# Identify duplicates by comparing base names
prp-gen-codebase-researcher.md      # KEEP
prp-initial-codebase-researcher.md  # DELETE

prp-gen-documentation-hunter.md     # KEEP
prp-initial-documentation-hunter.md # DELETE

prp-gen-example-curator.md          # KEEP
prp-initial-example-curator.md      # DELETE
```

**When to use**:
- When removing redundant agent implementations
- When consolidating similar functionality
- When deprecating experimental features

**How to adapt**:
1. Compare agent purposes (read first 20 lines of each)
2. Verify prp-gen-* version has all needed functionality
3. Check that commands reference correct version
4. Delete prp-initial-* version safely

**Why this pattern**:
- Prevents accidental deletion of active agents
- Ensures functionality preservation during cleanup
- Documents which version is canonical

## Naming Conventions

### File Naming

**Agent Files**:
- Pattern: `{workflow}-{phase}-{role}.md`
- Examples:
  - `prp-gen-feature-analyzer.md` (PRP generation, phase 1)
  - `prp-exec-implementer.md` (PRP execution, implementation)
  - `documentation-manager.md` (general purpose, no prefix)

**Command Files**:
- Pattern: `{action}-{noun}.md` or `{workflow-name}.md`
- Examples:
  - `generate-prp.md` (workflow command)
  - `execute-prp.md` (workflow command)
  - `create-initial.md` (DELETE - deprecated workflow)

**Documentation Sections**:
- Pattern: `## {Feature Name} Workflow` or `## {Feature Name}`
- Mark deprecated sections with clear headers before removal

### Deletion Naming Pattern

**Files to Delete** (7 total):
1. `.claude/agents/prp-initial-feature-clarifier.md`
2. `.claude/agents/prp-initial-codebase-researcher.md`
3. `.claude/agents/prp-initial-documentation-hunter.md`
4. `.claude/agents/prp-initial-example-curator.md`
5. `.claude/agents/prp-initial-gotcha-detective.md`
6. `.claude/agents/prp-initial-assembler.md`
7. `.claude/commands/create-initial.md`

**Files to Preserve** (10 agents + 2 commands):
- All 6 `prp-gen-*.md` agents
- All 4 `prp-exec-*.md` agents
- `generate-prp.md` command
- `execute-prp.md` command

### Reference Update Pattern

**Strings to Remove from CLAUDE.md**:
- "INITIAL.md Factory" (section title)
- "prp-initial-*" (agent references)
- "/create-initial" (command reference)
- "12+ agents" or "12 agents" → "10 agents"
- "6 specialized subagents" (in factory context)

**Strings to Preserve**:
- "INITIAL.md" (as a file format)
- "Manual INITIAL.md creation" (recommended workflow)
- "prp-gen-*" (agent references)
- "prp-exec-*" (agent references)

## File Organization

### Directory Structure

**Current State**:
```
.claude/
├── agents/
│   ├── documentation-manager.md        # KEEP
│   ├── validation-gates.md             # KEEP
│   ├── prp-gen-*.md (6 files)         # KEEP
│   ├── prp-exec-*.md (4 files)        # KEEP
│   └── prp-initial-*.md (6 files)     # DELETE
└── commands/
    ├── generate-prp.md                 # KEEP
    ├── execute-prp.md                  # KEEP
    ├── create-initial.md               # DELETE
    ├── prep-parallel.md                # KEEP
    ├── execute-parallel.md             # KEEP
    └── list-prps.md                    # KEEP
```

**After Cleanup**:
```
.claude/
├── agents/
│   ├── documentation-manager.md        # 2 general purpose
│   ├── validation-gates.md
│   ├── prp-gen-*.md (6 files)         # 6 PRP generation
│   └── prp-exec-*.md (4 files)        # 4 PRP execution
└── commands/
    ├── generate-prp.md                 # Core workflows
    ├── execute-prp.md
    ├── prep-parallel.md                # Supporting commands
    ├── execute-parallel.md
    └── list-prps.md
```

**Justification**:
- Removes 6 redundant agents (50% reduction from 12 to 6 subagents)
- Simplifies workflow: Manual INITIAL → /generate-prp → /execute-prp
- Eliminates automation of creative thinking (INITIAL creation)
- Preserves automation of mechanical work (PRP research/implementation)

### Git Organization

**Safe Deletion Process**:
```bash
# 1. Check git status before deletion
git status

# 2. If uncommitted changes exist, understand them first
git diff

# 3. Stage deletions explicitly (not wildcards)
git rm .claude/agents/prp-initial-feature-clarifier.md
git rm .claude/agents/prp-initial-codebase-researcher.md
git rm .claude/agents/prp-initial-documentation-hunter.md
git rm .claude/agents/prp-initial-example-curator.md
git rm .claude/agents/prp-initial-gotcha-detective.md
git rm .claude/agents/prp-initial-assembler.md
git rm .claude/commands/create-initial.md

# 4. Stage documentation update
git add CLAUDE.md

# 5. Verify staged changes
git diff --staged

# 6. Commit with descriptive message
git commit -m "Remove INITIAL.md factory workflow

- Delete 6 prp-initial-* agent files
- Delete create-initial command
- Remove factory documentation section from CLAUDE.md
- Reduce agent count from 12+ to 10
- Return to manual INITIAL.md → /generate-prp → /execute-prp workflow"
```

**Git Best Practices for Deletions**:
- Use `git rm` instead of `rm` to stage deletions
- Review `git diff --staged` before committing
- Write commit messages explaining what and why
- Include impact summary (agent count, workflow changes)

## Common Utilities to Leverage

### 1. Git Safety Check
**Location**: Shell commands
**Purpose**: Verify repository state before major changes
**Usage Example**:
```bash
# Check for uncommitted changes
git status --short

# Check staged changes
git diff --staged

# Check recent commits for context
git log --oneline -5
```

### 2. Grep Reference Verification
**Location**: Grep tool
**Purpose**: Find all references to deleted items
**Usage Example**:
```bash
# Find all references to prp-initial agents
grep -r "prp-initial-" .claude/

# Find all references to create-initial command
grep -r "create-initial" CLAUDE.md

# Verify no orphaned references after deletion
grep -r "INITIAL.md Factory" .
```

### 3. File Comparison for Duplicates
**Location**: Read tool + manual comparison
**Purpose**: Verify functionality before deletion
**Usage Example**:
```python
# Read both versions
gen_agent = Read(".claude/agents/prp-gen-codebase-researcher.md")
initial_agent = Read(".claude/agents/prp-initial-codebase-researcher.md")

# Compare core responsibilities (lines 10-50)
# Verify prp-gen version has all needed features
# Then safely delete prp-initial version
```

### 4. Line Range Extraction
**Location**: Read tool with offset/limit
**Purpose**: Precisely identify documentation sections to remove
**Usage Example**:
```python
# Read around section boundaries
before = Read("CLAUDE.md", offset=180, limit=10)  # Lines 180-190
target = Read("CLAUDE.md", offset=185, limit=195) # Lines 185-380
after = Read("CLAUDE.md", offset=375, limit=10)   # Lines 375-385

# Verify clean boundaries before deletion
```

### 5. Archon Health Check Pattern
**Location**: Archon MCP server integration
**Purpose**: Check availability before operations
**Usage Example**:
```python
# Always check Archon availability first
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# If available, update project/task status
if archon_available:
    mcp__archon__manage_task("update",
        task_id=task_id,
        status="done",
        notes="Deleted 6 prp-initial agents, 1 command, updated docs"
    )
```

## Testing Patterns

### Unit Test Structure
**Pattern**: Verification via grep and file existence checks
**Example**: Post-deletion verification
**Key techniques**:
- **File deletion verification**: Check files no longer exist
- **Reference verification**: Grep for orphaned references
- **Preservation verification**: Confirm kept files still exist

```bash
# Verify deletions
test ! -f .claude/agents/prp-initial-feature-clarifier.md
test ! -f .claude/commands/create-initial.md

# Verify no references remain
! grep -r "prp-initial-" .claude/commands/
! grep -r "create-initial" CLAUDE.md
! grep "INITIAL.md Factory" CLAUDE.md

# Verify preservations
test -f .claude/agents/prp-gen-feature-analyzer.md
test -f .claude/commands/generate-prp.md

# Count agents (should be 10)
agent_count=$(ls .claude/agents/prp-*.md | wc -l)
test $agent_count -eq 10
```

### Documentation Quality Test
**Pattern**: Manual review of CLAUDE.md coherence
**Example**: Section transition verification
**Key techniques**:
- Read before/after deleted section
- Verify no orphaned headers
- Check section numbering/hierarchy
- Validate markdown rendering

```bash
# Check CLAUDE.md renders without errors
# Visual inspection for:
# - Clean section transitions
# - No broken links
# - No orphaned content
# - Proper heading hierarchy
```

### Command Execution Test
**Pattern**: Verify core workflows still function
**Example**: Test /generate-prp and /execute-prp commands
**Key techniques**:
- Execute commands with test INITIAL.md
- Verify subagent invocation works
- Check output file generation
- Validate no errors about missing agents

```bash
# Test workflow still works (after cleanup)
# 1. Create test INITIAL.md
# 2. Run: /generate-prp prps/INITIAL_test.md
# 3. Verify PRP generated successfully
# 4. Check all prp-gen-* agents invoked
# 5. Run: /execute-prp prps/test.md
# 6. Verify execution completes
```

## Anti-Patterns to Avoid

### 1. Wildcard Deletion
**What it is**: Using `rm .claude/agents/prp-initial-*` or `git rm` with wildcards
**Why to avoid**:
- Risk of deleting wrong files if glob expands unexpectedly
- Harder to review staged changes
- No explicit verification of each deletion
**Found in**: Common shell practices (antipattern)
**Better approach**:
```bash
# Delete explicitly, one by one
git rm .claude/agents/prp-initial-feature-clarifier.md
git rm .claude/agents/prp-initial-codebase-researcher.md
# ... etc
```

### 2. Documentation Without Verification
**What it is**: Removing CLAUDE.md section without checking references
**Why to avoid**:
- May leave broken links to deleted agents
- Can create orphaned subsections
- Might remove too much or too little
**Found in**: Rushed documentation updates
**Better approach**:
```python
# 1. Grep for all references first
grep -n "prp-initial-" CLAUDE.md
grep -n "create-initial" CLAUDE.md
grep -n "INITIAL.md Factory" CLAUDE.md

# 2. Read section boundaries
Read("CLAUDE.md", offset=180, limit=210)

# 3. Delete precise line range
# 4. Verify with grep again (should be zero matches)
```

### 3. Assuming Agent Equivalence
**What it is**: Deleting prp-initial-* agents without comparing to prp-gen-*
**Why to avoid**:
- Agents may have different tools or capabilities
- Implementation details might differ
- Risk of losing functionality
**Found in**: Quick cleanup attempts
**Better approach**:
```python
# Compare agents before deletion
gen_tools = grep("^tools:", ".claude/agents/prp-gen-codebase-researcher.md")
init_tools = grep("^tools:", ".claude/agents/prp-initial-codebase-researcher.md")

# Verify gen version has all needed tools
# Read core sections to confirm equivalence
# Then safely delete
```

### 4. Ignoring Git State
**What it is**: Deleting files when uncommitted changes exist
**Why to avoid**:
- Harder to separate this change from others
- Risk of conflicts with other work
- Difficult to revert if needed
**Found in**: Working in dirty git state
**Better approach**:
```bash
# 1. Check git status first
git status

# 2. If dirty, commit or stash other changes
git add <other files>
git commit -m "Other changes"

# 3. Then proceed with cleanup in clean state
git status  # Should show "nothing to commit"
```

### 5. Incomplete Reference Cleanup
**What it is**: Deleting files but leaving references in documentation/examples
**Why to avoid**:
- Confuses users who find references to deleted features
- Breaks mental model of codebase
- Creates maintenance burden
**Found in**: Partial cleanup efforts
**Better approach**:
```bash
# Comprehensive reference check across ALL file types
grep -r "prp-initial-" . --include="*.md"
grep -r "create-initial" . --include="*.md" --include="*.py"
grep -r "INITIAL.md Factory" .

# Update or remove ALL references found
# Document intentional historical references (examples/)
```

## Implementation Hints from Existing Code

### Similar Features Found

1. **Agent Cleanup Pattern** (Documentation Manager)
   - **Location**: `.claude/agents/documentation-manager.md`
   - **Similarity**: Proactive file updates after changes
   - **Lessons**: Use systematic grep to find all affected files
   - **Differences**: This is deletion, not update

2. **Multi-Phase Workflow Pattern** (generate-prp command)
   - **Location**: `.claude/commands/generate-prp.md`
   - **Similarity**: Orchestrates multiple subagents in sequence
   - **Lessons**: Clear phase boundaries, explicit task updates
   - **Differences**: We're removing a parallel workflow, not creating one

3. **Documentation Section Structure** (CLAUDE.md sections)
   - **Location**: `CLAUDE.md` various sections
   - **Similarity**: Large markdown sections with clear boundaries
   - **Lessons**: Preserve separators (`---`), verify next section starts clean
   - **Differences**: Removing ~200 lines vs typical 20-50 line sections

### Git Deletion Patterns from History

**Pattern**: Explicit staging with descriptive commits
```bash
# From git history (inferred best practice)
git rm path/to/deprecated/file.ext
git add path/to/updated/file.ext
git commit -m "Descriptive message

- What was deleted
- What was updated
- Why the change was needed
- Impact on users/workflow"
```

## Recommendations for PRP

Based on pattern analysis:

1. **Follow Git Safety Pattern** for clean deletion tracking
   - Check `git status` before starting
   - Use `git rm` for deletions (not `rm`)
   - Stage changes separately (deletions, then CLAUDE.md)
   - Verify with `git diff --staged`
   - Write comprehensive commit message

2. **Reuse Grep Verification Pattern** for reference checking
   - Search for "prp-initial-" across all .md files
   - Search for "create-initial" in commands and docs
   - Search for "INITIAL.md Factory" in CLAUDE.md
   - Verify zero matches after cleanup

3. **Mirror Documentation Update Pattern** for CLAUDE.md
   - Read lines 180-390 to verify section boundaries
   - Delete lines 185-378 (194 lines total)
   - Preserve line 379 (`---` separator)
   - Verify line 380 starts "## Development Patterns"
   - Update agent count references (12+ → 10)

4. **Adapt Agent Comparison Pattern** for duplicate verification
   - Compare each prp-gen-* with corresponding prp-initial-*
   - Verify tools, responsibilities, output patterns match
   - Confirm prp-gen-* version is canonical
   - Delete prp-initial-* version safely

5. **Avoid Wildcard Deletion Antipattern** based on best practices
   - Delete files one by one with explicit paths
   - Review each deletion before staging
   - Prevents accidental deletion of wrong files

## Source References

### From Archon

- **e9eb05e2bf38f125**: Mock generation infrastructure replacement (kubechain)
  - Relevance: 7/10
  - Pattern: Systematic cleanup of old infrastructure
  - Application: Similar need to remove deprecated automation

- **b8565aff9938938b**: Context engineering workflow intro
  - Relevance: 9/10
  - Pattern: Manual INITIAL.md → /generate-prp → /execute-prp
  - Application: This is the workflow we're returning to

### From Local Codebase

- **.claude/agents/prp-gen-*.md**: Agent structure pattern (lines 1-10)
  - Shows frontmatter format, tool permissions, naming convention

- **.claude/commands/generate-prp.md**: Command orchestration pattern (lines 1-100)
  - Shows phase-based workflow, Archon integration, subagent invocation

- **CLAUDE.md**: Documentation section structure (lines 185-378)
  - Shows section boundaries, separators, heading hierarchy

- **examples/prp_workflow_improvements/**: Historical patterns (all files)
  - Shows evolution of workflows, can remain as historical reference
  - Documents why factory was created and why it's being removed

## Next Steps for Assembler

When generating the PRP:

1. **Reference deletion patterns** in "Implementation Blueprint"
   - Include exact git commands for safe deletion
   - Show grep patterns for reference verification
   - Document line ranges for CLAUDE.md edit

2. **Include verification code snippets** in "Validation Gates"
   - File existence checks (negative assertions)
   - Grep verification (zero matches expected)
   - Agent count validation (exactly 10)
   - Documentation coherence check

3. **Add git antipatterns** to "Known Gotchas" section
   - Wildcard deletion risks
   - Uncommitted changes conflicts
   - Incomplete reference cleanup
   - Agent equivalence assumptions

4. **Use explicit file list** for "Desired Codebase Tree"
   - Show before/after agent directory structure
   - Document exact count: 12 agents → 10 agents
   - Highlight preserved vs deleted agents

5. **Document simplified workflow** in "Integration Points"
   - Manual INITIAL.md creation (10-20 min)
   - /generate-prp for research & PRP creation
   - /execute-prp for implementation
   - No /create-initial command (removed)

## Quality Checklist

Before considering research complete, verify:

- ✅ 5 major architectural patterns documented
- ✅ Each pattern has code examples and adaptation guidance
- ✅ Naming conventions extracted (files, agents, sections)
- ✅ File organization shows before/after structure
- ✅ Git safety patterns documented with commands
- ✅ 5 anti-patterns identified with solutions
- ✅ Source references include Archon + local files
- ✅ Clear recommendations for PRP assembler
- ✅ Comprehensive at 250+ lines
- ✅ Focused on cleanup/removal patterns specifically

## Summary

This codebase research reveals a clear cleanup pattern: **reversal of over-automation**. The INITIAL factory automated a creative thinking task (requirements gathering) that actually benefits from human judgment. The research shows:

- **What to delete**: 6 prp-initial-* agents + 1 create-initial command + ~200 lines of docs
- **What to preserve**: All prp-gen-* and prp-exec-* agents, core PRP workflow
- **How to delete safely**: Git safety checks, explicit staging, reference verification, agent comparison
- **Anti-patterns to avoid**: Wildcard deletion, incomplete cleanup, assumption of equivalence
- **Result**: Simpler workflow (Manual INITIAL → /generate-prp → /execute-prp), 50% fewer agents, 10-20 min manual work vs complex automation

The patterns emphasize **verification at every step**: check git state, compare agents, grep for references, validate documentation coherence. This is a textbook example of reducing complexity while preserving core value.
