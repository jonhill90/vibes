# Documentation Resources: Initial Factory Removal

## Overview

This cleanup task involves removing 6 INITIAL factory subagent files, 1 command file, and ~193 lines from CLAUDE.md. Documentation was found covering git deletion best practices, markdown documentation maintenance, Claude Code subagent management, and cleanup workflows. Since this is primarily a cleanup/removal task rather than feature implementation, documentation focuses on safe deletion patterns, commit conventions, and documentation refactoring practices.

## Primary Framework Documentation

### Claude Code Subagent System
**Official Docs**: https://docs.claude.com/en/docs/claude-code/sub-agents/
**Version**: Current (2025)
**Archon Source**: 9a7d4217c64c9a0a (Anthropic Documentation)
**Relevance**: 10/10

**Sections to Read**:
1. **Creating and Managing Subagents**: https://docs.claude.com/en/docs/claude-code/sub-agents/#creating-subagents
   - **Why**: Understanding proper lifecycle management including deletion
   - **Key Concepts**: Use `/agents` command to create, edit, and delete custom subagents; subagents stored in `.claude/agents/` directory

2. **File Structure and Storage**: https://docs.claude.com/en/docs/claude-code/sub-agents/#file-locations
   - **Why**: Confirms proper location for agent files being deleted
   - **Key Concepts**:
     - Project-level: `.claude/agents/` (our deletion target)
     - User-level: `~/.claude/agents/`
     - Filename format: lowercase with hyphens

3. **Best Practices for Subagent Lifecycle**: https://docs.claude.com/en/docs/claude-code/sub-agents/#best-practices
   - **Why**: Guidance on maintaining clean subagent architecture
   - **Key Concepts**:
     - Create focused subagents with "single, clear responsibilities"
     - Version control project-level subagents for team collaboration
     - Delete subagents that no longer serve a purpose

**Code Examples from Docs**:
```markdown
# Subagent File Structure (YAML frontmatter)
---
name: code-reviewer
description: Reviews code changes for quality and best practices
tools: Read,Write,Grep,Glob
model: sonnet
---

[System prompt content here]
```

**Gotchas from Documentation**:
- Project-specific agents take precedence over global agents with same name
- Deleting agent files directly from filesystem is safe (no database dependencies)
- Must ensure no commands reference deleted agents
- `/agents` command only lists agents in current project context

---

### Git File Deletion and Commit Best Practices
**Official Docs**: https://git-scm.com/docs/git-commit
**Supplementary**: https://www.conventionalcommits.org/en/v1.0.0/
**Version**: Current
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Pages**:
- **Git Commit Documentation**: https://git-scm.com/docs/git-commit
  - **Use Case**: Official reference for commit command and options
  - **Example**: `git add -A && git commit -m "type: description"`

- **Conventional Commits Specification**: https://www.conventionalcommits.org/en/v1.0.0/
  - **Use Case**: Standard format for commit messages
  - **Example**:
  ```
  chore: remove INITIAL.md factory workflow system

  Remove 6 prp-initial-* subagent files and create-initial command.
  This cleanup reduces agent count by 50% and removes ~200 lines
  from CLAUDE.md documentation.

  BREAKING CHANGE: /create-initial command no longer available
  ```

**API Reference**:
- **Commit Types for Removal**:
  - **`chore:`**: Used for maintenance tasks, dependency updates, configuration changes
  - **`refactor:`**: Code restructuring without changing external behavior
  - **`remove:`**: Explicit type for removing deprecated features (non-standard but clear)
  - **Breaking Change Marker**: Use `!` after type or `BREAKING CHANGE:` footer

**Applicable Patterns**:
```bash
# Pattern 1: Standard deletion commit
git rm .claude/agents/prp-initial-*.md
git commit -m "chore: remove INITIAL factory subagent files"

# Pattern 2: Commit with breaking change
git commit -m "chore!: remove /create-initial command

BREAKING CHANGE: The INITIAL.md factory workflow has been removed.
Users should manually create INITIAL.md files instead."

# Pattern 3: Comprehensive cleanup commit
git add -A
git commit -m "refactor: simplify PRP workflow by removing factory system

- Delete 6 prp-initial-* subagent files
- Remove /create-initial command
- Update CLAUDE.md to remove factory documentation (~193 lines)
- Preserve all prp-gen-* and prp-exec-* agents

Reduces complexity and agent count from 12+ to 10."
```

---

### Markdown Documentation Maintenance
**Official Docs**: https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown
**Supplementary**: https://google.github.io/styleguide/docguide/style.html
**Version**: Current
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Sections to Read**:
1. **Markdown Best Practices**: https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown#markdown-best-practices
   - **Why**: Guidance on maintaining clean documentation structure
   - **Key Concepts**:
     - Use no more than three heading levels to avoid choppy documents
     - Use one H1 heading as title, subsequent headings H2 or deeper
     - Delete cruft frequently and in small batches
     - "A small set of fresh and accurate docs is better than sprawling assembly in disrepair"

2. **Google Markdown Style Guide**: https://google.github.io/styleguide/docguide/style.html
   - **Why**: Industry-standard practices for documentation structure
   - **Key Concepts**:
     - Use ATX-style headings (# syntax)
     - Separate sections with `---` horizontal rules
     - Keep line length reasonable for readability

**Code Examples**:
```markdown
# Before: Complex nested structure
## Main Section
### Subsection 1
#### Deep subsection
##### Too deep
###### Way too deep

# After: Simplified structure
## Main Section
### Subsection 1
Content organized more flatly

## Next Main Section
Clear separation between major topics
```

**Documentation Refactoring Pattern**:
```markdown
# Removing Large Section Pattern

1. Identify section boundaries
   - Start: ## INITIAL.md Factory Workflow (line 185)
   - End: Last line before next section (line 378)

2. Verify no orphaned references
   - Search for section links: grep -r "INITIAL.md Factory" docs/
   - Check for anchor links: grep -r "#initial-factory" docs/

3. Remove section cleanly
   - Delete lines 185-378
   - Preserve separator line (---) if present
   - Ensure next section flows logically

4. Verify document coherence
   - Check heading hierarchy remains consistent
   - Ensure no broken internal links
   - Review table of contents if present
```

---

## Library Documentation

### 1. Git (Version Control)
**Official Docs**: https://git-scm.com/doc
**Purpose**: Version control for tracking file deletions
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Key Pages**:
- **git-rm Documentation**: https://git-scm.com/docs/git-rm
  - **Use Case**: Removing files from working tree and index
  - **Example**:
  ```bash
  # Remove files and stage deletion
  git rm .claude/agents/prp-initial-*.md
  git rm .claude/commands/create-initial.md

  # Or remove from index only (keep file locally)
  git rm --cached file.md
  ```

- **git-status**: https://git-scm.com/docs/git-status
  - **Use Case**: Verify deletions are properly staged
  - **Example**:
  ```bash
  git status
  # Should show "deleted: .claude/agents/prp-initial-feature-clarifier.md"
  ```

**Gotchas**:
- Using `rm` (shell command) requires separate `git add` to stage deletion
- `git rm` removes file AND stages deletion in one step
- Wildcards work with `git rm` but may need quotes: `git rm "*.md"`

---

### 2. Grep/Ripgrep (Pattern Search)
**Official Docs**: https://github.com/BurntSushi/ripgrep
**Purpose**: Verifying no references exist to deleted files
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Commands**:
```bash
# Find all references to prp-initial agents
rg "prp-initial-" .claude/

# Find references to create-initial command
rg "create-initial" --type md

# Find references in specific directory
rg "INITIAL.md Factory" CLAUDE.md

# Case-insensitive search
rg -i "factory workflow" docs/
```

**Verification Pattern**:
```bash
# Step 1: Search for agent file references
rg "prp-initial-feature-clarifier" .
# Expected: Only matches in files being deleted or updated

# Step 2: Search for command references
rg "/create-initial" .
# Expected: Only in CLAUDE.md section being removed

# Step 3: Verify no broken links
rg "\[.*\]\(.*prp-initial.*\)" --type md
# Expected: No matches after cleanup
```

---

## Integration Guides

### Safe File Deletion Workflow
**Guide URL**: https://www.datacamp.com/tutorial/how-to-remove-files-from-git-repositories
**Source Type**: Tutorial
**Quality**: 8/10
**Archon Source**: Not applicable

**What it covers**:
- Safe patterns for removing files from git repositories
- Difference between `git rm` and `rm` + `git add`
- How to remove files from history (not needed here)
- Verification steps after deletion

**Code examples**:
```bash
# Safe deletion workflow
# 1. Verify files to be deleted
ls .claude/agents/prp-initial-*.md
ls .claude/commands/create-initial.md

# 2. Remove files and stage deletion
git rm .claude/agents/prp-initial-*.md
git rm .claude/commands/create-initial.md

# 3. Verify staged deletions
git status

# 4. Commit with descriptive message
git commit -m "chore: remove INITIAL factory subagent files

Removes 6 prp-initial-* agent files and create-initial command
as part of workflow simplification."

# 5. Verify no dangling references
rg "prp-initial-|create-initial" .
```

**Applicable patterns**:
- Always use `git status` before committing deletions
- Verify deletions are staged (not just untracked)
- Check for references before finalizing deletion

---

### Documentation Section Removal Pattern
**Guide URL**: https://www.markdowntoolbox.com/blog/markdown-best-practices-for-documentation/
**Source Type**: Best Practices Guide
**Quality**: 7/10

**What it covers**:
- Best practices for maintaining documentation
- How to remove sections without breaking document flow
- Importance of regular cleanup to prevent documentation sprawl

**Key Practices**:
1. **Identify Section Boundaries**:
   ```markdown
   # Find section start
   ## INITIAL.md Factory Workflow  # <-- Line 185

   # Find section end (before next major section)
   ---
   ## Development Patterns  # <-- Line 380
   ```

2. **Extract Section Cleanly**:
   - Read file to understand context before/after
   - Note line numbers: 185-378 (193 lines)
   - Preserve separator lines (---)
   - Ensure next section has proper heading

3. **Verify Document Coherence**:
   - Check table of contents is updated
   - Verify internal links still work
   - Ensure heading hierarchy is consistent
   - Review surrounding context for flow

**Example Pattern**:
```bash
# 1. Read file first to understand structure
cat CLAUDE.md | less

# 2. Identify exact line range
sed -n '185,378p' CLAUDE.md  # Preview section to be removed

# 3. Verify boundaries
sed -n '184,186p' CLAUDE.md  # Check start context
sed -n '377,380p' CLAUDE.md  # Check end context

# 4. After removal, verify document
cat CLAUDE.md | grep "^##"  # View all section headers
```

---

## Best Practices Documentation

### Git Commit Message Best Practices
**Resource**: https://initialcommit.com/blog/git-commit-messages-best-practices
**Type**: Community Standard
**Relevance**: 9/10

**Key Practices**:
1. **Use Imperative Mood**: "Remove" not "Removed" or "Removing"
   - **Why**: Matches git's own convention ("Merge branch", "Revert commit")
   - **Example**: `chore: remove INITIAL factory agents`

2. **Be Descriptive About Why**: Explain the reason, not just what changed
   - **Why**: Helps future maintainers understand context
   - **Example**:
   ```
   chore: remove INITIAL.md factory workflow system

   The factory added unnecessary complexity by automating a creative
   thinking task that requires human judgment. Manual INITIAL.md
   creation takes 10-20 minutes and is more appropriate.

   This reduces agent count by 50% (from 12+ to 10 agents).
   ```

3. **Use Conventional Commits**: Type-based prefixes for clarity
   - **Why**: Enables automated changelog generation and semantic versioning
   - **Example**:
   ```
   Types:
   - chore: Maintenance tasks, tooling, configuration
   - refactor: Code restructuring without behavior change
   - docs: Documentation only changes
   - remove: Explicit feature removal (non-standard but clear)
   ```

4. **Keep Subject Line Under 50 Characters**: Forces conciseness
   - **Why**: Readable in git log one-line format
   - **Example**:
   ```
   Good: "chore: remove INITIAL factory agents"
   Bad:  "chore: remove the INITIAL.md factory workflow system including all 6 subagent files"
   ```

5. **Separate Subject from Body**: Blank line between subject and details
   - **Why**: Tools parse this format automatically
   - **Example**:
   ```
   chore: remove INITIAL factory subagent system

   Deletes 6 prp-initial-* agent files and /create-initial command.
   Updates CLAUDE.md to remove ~193 lines of factory documentation.
   ```

---

### Documentation Maintenance Principles
**Resource**: https://www.dpconline.org/digipres/implement-digipres/digital-preservation-documentation-guide/digital-preservation-documentation-revising
**Type**: Official Guide
**Relevance**: 8/10

**Key Practices**:
1. **Regular Scheduled Maintenance**: Don't wait for major overhauls
   - **Why**: Small incremental updates prevent documentation debt
   - **Pattern**: Review docs quarterly, remove outdated content

2. **Delete Cruft Frequently**: Small batches are better than big purges
   - **Why**: "Fresh and accurate docs are better than sprawling assembly in disrepair"
   - **Pattern**: Remove 1-2 outdated sections per sprint/iteration

3. **Document What Changed**: Keep changelog of significant updates
   - **Why**: Helps users understand evolution of project
   - **Pattern**: Add entry to CHANGELOG.md or commit message body

4. **Verify No Broken Links**: Check references before deletion
   - **Why**: Prevents 404 errors and confusion
   - **Pattern**:
   ```bash
   # Find all markdown links to section
   rg "\[.*\]\(#initial-factory.*\)" --type md

   # Find all references to removed content
   rg "INITIAL.md Factory|create-initial" docs/
   ```

5. **Maintain Version History**: Use git for documentation versioning
   - **Why**: Allows rollback if removal was premature
   - **Pattern**: Clear commit messages document what was removed and why

**Example Application to This Task**:
```markdown
## Checklist for Documentation Removal

- [ ] Identify exact section boundaries (lines 185-378)
- [ ] Search for all references to removed content
  - [ ] grep "INITIAL.md Factory"
  - [ ] grep "create-initial"
  - [ ] grep "prp-initial-"
- [ ] Preview section to be removed
- [ ] Verify next section flows logically after removal
- [ ] Remove section cleanly
- [ ] Check document renders correctly
- [ ] Update any table of contents
- [ ] Commit with descriptive message explaining why
```

---

## Testing Documentation

### File Deletion Verification
**Testing Framework**: Manual verification with git and grep
**Archon Source**: Not in Archon

**Relevant Verification Steps**:

1. **Pre-Deletion Checks**:
   ```bash
   # List files to be deleted
   ls -la .claude/agents/prp-initial-*.md
   ls -la .claude/commands/create-initial.md

   # Count references before deletion
   rg "prp-initial-" . | wc -l
   rg "create-initial" . | wc -l
   ```

2. **Post-Deletion Verification**:
   ```bash
   # Verify files are deleted
   ls .claude/agents/prp-initial-*.md  # Should fail
   ls .claude/commands/create-initial.md  # Should fail

   # Verify git shows deletions
   git status
   # Expected: "deleted: .claude/agents/prp-initial-*.md" (6 files)

   # Verify no dangling references
   rg "prp-initial-" .claude/  # Should only match in git history
   rg "create-initial" CLAUDE.md  # Should be zero matches
   ```

3. **Documentation Update Verification**:
   ```bash
   # Verify section removed from CLAUDE.md
   grep "INITIAL.md Factory Workflow" CLAUDE.md
   # Expected: No matches

   # Count lines in CLAUDE.md
   wc -l CLAUDE.md
   # Expected: ~193 lines fewer than before

   # Verify next section is intact
   grep "## Development Patterns" CLAUDE.md
   # Expected: Section should be present and properly formatted
   ```

4. **Functional Testing**:
   ```bash
   # Verify /generate-prp still works
   # (manual test - invoke command and check it references correct agents)

   # Verify /execute-prp still works
   # (manual test - invoke command and check it references correct agents)

   # Verify preserved agents still exist
   ls .claude/agents/prp-gen-*.md  # Should show 6 files
   ls .claude/agents/prp-exec-*.md  # Should show 4 files
   ```

**Test Checklist**:
```markdown
## Pre-Deletion Validation
- [ ] Listed all files to be deleted (7 total)
- [ ] Counted references to deleted content
- [ ] Verified preserved agents exist (10 files)
- [ ] Backed up CLAUDE.md (optional but safe)

## Deletion Execution
- [ ] Deleted 6 prp-initial-* agent files
- [ ] Deleted create-initial.md command
- [ ] Updated CLAUDE.md (removed lines 185-378)
- [ ] Staged all changes with git

## Post-Deletion Validation
- [ ] No prp-initial-*.md files exist
- [ ] No create-initial.md file exists
- [ ] Zero references to "prp-initial-" in .claude/
- [ ] Zero references to "create-initial" in CLAUDE.md
- [ ] Zero references to "INITIAL.md Factory" in CLAUDE.md
- [ ] All prp-gen-* agents present (6 files)
- [ ] All prp-exec-* agents present (4 files)
- [ ] CLAUDE.md renders correctly
- [ ] No orphaned sections in CLAUDE.md
- [ ] Git status shows clean deletions

## Functional Validation
- [ ] /generate-prp command file intact
- [ ] /execute-prp command file intact
- [ ] Documentation flow is coherent
- [ ] Agent count references updated (12+ → 10)
```

---

## Additional Resources

### Tutorials with Code
1. **How to Remove Files from Git Repositories**: https://www.datacamp.com/tutorial/how-to-remove-files-from-git-repositories
   - **Format**: Tutorial article
   - **Quality**: 8/10
   - **What makes it useful**: Step-by-step walkthrough of git rm command with examples

2. **Conventional Commits Cheatsheet**: https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13
   - **Format**: GitHub Gist reference
   - **Quality**: 9/10
   - **What makes it useful**: Quick reference for commit message formats, includes all standard types

3. **Markdown Style Guide (Google)**: https://google.github.io/styleguide/docguide/style.html
   - **Format**: Official style guide
   - **Quality**: 9/10
   - **What makes it useful**: Industry-standard practices for documentation structure and maintenance

### API References
1. **git-rm**: https://git-scm.com/docs/git-rm
   - **Coverage**: Complete reference for file removal command
   - **Examples**: Yes, includes common patterns

2. **git-commit**: https://git-scm.com/docs/git-commit
   - **Coverage**: Full commit command documentation
   - **Examples**: Yes, includes message formatting

### Community Resources
1. **Awesome Claude Code Subagents**: https://github.com/VoltAgent/awesome-claude-code-subagents
   - **Type**: GitHub repository
   - **Why included**: 100+ production-ready subagent examples showing best practices
   - **Relevance**: Shows patterns for organizing and managing subagent files

2. **Stack Overflow: Semantic commit type when removing**: https://stackoverflow.com/questions/48075169/semantic-commit-type-when-remove-something
   - **Type**: Community Q&A
   - **Why included**: Real-world discussion on best commit type for removals
   - **Consensus**: Use `chore:` for maintenance, `remove:` for explicit feature removal, `refactor!:` for breaking changes

---

## Documentation Gaps

**Not found in Archon or Web**:
- **Claude Code agent deprecation patterns**: No official guidance on how to deprecate agents before removing them
  - **Recommendation**: Add deprecation notice in agent description field before removal, wait one release cycle

- **CLAUDE.md schema validation**: No tools to validate CLAUDE.md structure after editing
  - **Recommendation**: Manual review of markdown syntax and section hierarchy

**Outdated or Incomplete**:
- **Claude Code subagent documentation**: Limited guidance on removing subagents vs creating them
  - **Suggested alternative**: Follow general file deletion best practices from git documentation
  - **Gap**: No mention of cleanup workflows or agent lifecycle management beyond creation

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Framework Docs:
  - Claude Code Subagents: https://docs.claude.com/en/docs/claude-code/sub-agents/
  - Git Documentation: https://git-scm.com/doc

Commit Conventions:
  - Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/
  - Git Commit Best Practices: https://initialcommit.com/blog/git-commit-messages-best-practices

Documentation Maintenance:
  - Markdown Best Practices: https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown
  - Google Markdown Style Guide: https://google.github.io/styleguide/docguide/style.html
  - Documentation Revising: https://www.dpconline.org/digipres/implement-digipres/digital-preservation-documentation-guide/digital-preservation-documentation-revising

File Deletion:
  - git-rm: https://git-scm.com/docs/git-rm
  - Remove Files from Git: https://www.datacamp.com/tutorial/how-to-remove-files-from-git-repositories

Community Resources:
  - Conventional Commits Cheatsheet: https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13
  - Awesome Claude Code Subagents: https://github.com/VoltAgent/awesome-claude-code-subagents
```

## Recommendations for PRP Assembly

When generating the PRP:
1. **Include these URLs** in "Documentation & References" section
   - Primary: Claude Code subagents, Conventional Commits, git-rm
   - Secondary: Markdown best practices, documentation maintenance guides

2. **Extract code examples** shown above into PRP context
   - Git deletion workflow examples
   - Commit message templates for cleanup
   - Verification bash scripts

3. **Highlight gotchas** from documentation in "Known Gotchas" section
   - Must verify no commands reference deleted agents
   - Project-level agents take precedence (affects search)
   - Conventional commits: `chore:` vs `remove:` vs `refactor!:`
   - Documentation: preserve section separators, check heading hierarchy

4. **Reference specific sections** in implementation tasks
   - Task 1: "See git-rm docs for deletion syntax"
   - Task 2: "Follow markdown best practices for section removal"
   - Task 3: "Use Conventional Commits format for commit message"

5. **Note gaps** so implementation can compensate
   - No official Claude Code agent deprecation workflow
   - No automated CLAUDE.md structure validation
   - Limited guidance on cleanup vs creation workflows

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:
- https://www.conventionalcommits.org/en/v1.0.0/ - Standard for commit message format, widely used in modern development
- https://google.github.io/styleguide/docguide/style.html - Industry-standard markdown documentation practices
- https://initialcommit.com/blog/git-commit-messages-best-practices - Comprehensive guide to commit message best practices
- https://www.datacamp.com/tutorial/how-to-remove-files-from-git-repositories - Practical guide for safe file deletion in git

**Why these are valuable for future PRPs**:
- Conventional Commits: Referenced in many codebases, essential for changelog automation
- Markdown Style Guide: Useful for any documentation maintenance tasks
- Git Best Practices: Common cleanup and refactoring tasks require this knowledge
- Safe File Deletion: Pattern repeats in deprecation and cleanup workflows

These resources would improve Archon's ability to help with maintenance, cleanup, and documentation tasks across projects.

---

## Summary Statistics

**Documentation Sources Found**: 15 primary sources
**Archon Sources Used**: 1 (Anthropic Documentation for Claude Code)
**Web Sources**: 14 (Git, Conventional Commits, Markdown guides, tutorials)
**Code Examples Extracted**: 12 practical examples
**Gotchas Documented**: 8 specific issues with solutions
**Verification Patterns**: 4 comprehensive checklists

**Quality Assessment**: 8/10
- ✅ Comprehensive coverage of cleanup workflow
- ✅ Official documentation for all major components
- ✅ Practical examples for file deletion and commit conventions
- ✅ Clear verification patterns
- ⚠️ Limited official guidance on agent deprecation (filled gap with general practices)
- ⚠️ No automated validation tools for CLAUDE.md structure (manual review required)

**Time to Compile**: ~15 minutes (Archon search + web research + synthesis)

This documentation package provides complete context for safely removing the INITIAL factory workflow system while following industry best practices for git commits, documentation maintenance, and cleanup verification.
