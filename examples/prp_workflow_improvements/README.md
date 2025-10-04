# PRP Workflow Improvements - Code Examples

## Overview

This directory contains extracted code examples to guide the improvement of generate-prp and execute-prp commands. These are REAL code files extracted from the working INITIAL.md factory, showing proven patterns for parallel execution, code extraction, subagent orchestration, and Archon integration.

**Goal**: Apply factory patterns to PRP workflow for faster, higher-quality PRP generation and execution.

## Files in This Directory

| File | Source | Purpose | Relevance |
|------|--------|---------|-----------|
| current_generate_prp.md | .claude/commands/generate-prp.md | Current PRP generation command | 10/10 |
| current_execute_prp.md | .claude/commands/execute-prp.md | Current PRP execution command | 10/10 |
| factory_parallel_pattern.md | .claude/commands/create-initial.md:126-185 | Parallel subagent invocation pattern | 10/10 |
| subagent_structure.md | .claude/agents/prp-initial-feature-clarifier.md | Subagent definition template | 10/10 |
| archon_integration_pattern.md | .claude/commands/create-initial.md:38-87 | Archon MCP project/task tracking | 10/10 |
| code_extraction_pattern.md | .claude/agents/prp-initial-example-curator.md:16-101 | Code extraction methodology | 10/10 |

## Detailed Example Guidance

### current_generate_prp.md - Baseline to Improve

**Source**: `.claude/commands/generate-prp.md`
**Original Context**: Current command for generating PRPs from INITIAL.md files

**What to Mimic**:
- Archon-first approach (health check, then search Archon before web)
- ULTRATHINK pattern before writing PRP
- Quality checklist with scoring (1-10)
- Validation gates structure (executable commands)
- Using prp_base.md template

**What to Adapt**:
- Add parallel research phase (like factory Phase 2)
- Add code extraction to examples/ directory (not just references)
- Add systematic gotcha detection phase
- Add quality gates that enforce 8+/10 minimum
- Add subagent orchestration instead of monolithic execution

**What to Skip**:
- Sequential research approach (too slow)
- Referencing examples instead of extracting them
- Manual quality assessment without scoring threshold

**Key Pattern Highlights**:

```markdown
# Archon health check pattern
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# ULTRATHINK before execution
*** CRITICAL AFTER YOU ARE DONE RESEARCHING ***
*** ULTRATHINK ABOUT THE PRP AND PLAN YOUR APPROACH ***

# Quality scoring
Score the PRP on a scale of 1-10 (confidence level to succeed)
```

**Why This Example**:
Shows the baseline that works but needs enhancement. The Archon-first approach and ULTRATHINK pattern are proven and should be kept. The sequential research and lack of code extraction are the main gaps to address.

---

### current_execute_prp.md - Baseline to Improve

**Source**: `.claude/commands/execute-prp.md`
**Original Context**: Current command for executing PRPs

**What to Mimic**:
- Load PRP → ULTRATHINK → Execute → Validate → Complete flow
- Validation loop pattern (run, fix, re-run until pass)
- Reading PRP file and following instructions
- Final checklist verification

**What to Adapt**:
- Add task dependency analysis before execution
- Add parallel execution for independent tasks
- Add Archon task tracking (not TodoWrite)
- Add automated test generation
- Add quality gates between phases

**What to Skip**:
- TodoWrite for task tracking (use Archon instead per ARCHON-FIRST RULE)
- Sequential execution of all tasks (parallelize independent tasks)
- Manual test writing (generate tests automatically)

**Key Pattern Highlights**:

```markdown
# Validation loop pattern
4. **Validate**
   - Run each validation command
   - Fix any failures
   - Re-run until all pass

# PRP re-reading pattern
6. **Reference the PRP**
   - You can always reference the PRP again if needed
```

**Why This Example**:
Shows a simple, working execution flow that's easy to understand but lacks parallelization and automation. The validation loop pattern is solid and should be preserved. The sequential execution is the main bottleneck to address.

---

### factory_parallel_pattern.md - CRITICAL Pattern

**Source**: `.claude/commands/create-initial.md` (lines 126-185)
**Original Context**: Phase 2 of INITIAL.md factory where 3 subagents run simultaneously

**What to Mimic**:
- Parallel task invocation in SINGLE message
- Preparing context for each subagent before invocation
- Using Task tool multiple times in one response
- Updating Archon tasks to "doing" before, "done" after
- Clear expected outputs for each subagent

**What to Adapt**:
- Apply to execute-prp for parallel task execution
- Apply to generate-prp for parallel research phases
- Adapt task grouping logic based on PRP task dependencies
- Use for both research tasks and implementation tasks

**What to Skip**:
- Nothing - this entire pattern should be adopted

**Key Pattern Highlights**:

```python
# ⚠️ CRITICAL: Parallel invocation - SINGLE message with multiple Task calls
parallel_invoke([
    Task(agent="prp-initial-codebase-researcher", prompt=researcher_context),
    Task(agent="prp-initial-documentation-hunter", prompt=hunter_context),
    Task(agent="prp-initial-example-curator", prompt=curator_context)
])

# DO NOT invoke sequentially
# DO send all invocations in single message
```

**Why This Example**:
This is THE KEY INNOVATION from the factory. Parallel execution achieves 3x speedup in Phase 2 (3 minutes instead of 9 minutes). This pattern MUST be applied to both generate-prp (parallel research) and execute-prp (parallel task execution).

**Application to generate-prp**:
- Phase 2: Parallel research (codebase patterns, documentation, examples, gotchas)
- 4 subagents instead of sequential steps

**Application to execute-prp**:
- Analyze PRP task list for dependencies
- Group independent tasks
- Execute each group in parallel
- Wait for group completion before next group

---

### subagent_structure.md - Subagent Template

**Source**: `.claude/agents/prp-initial-feature-clarifier.md`
**Original Context**: Phase 1 subagent for requirements analysis in factory

**What to Mimic**:
- Frontmatter format (name, description, tools, color)
- "USE PROACTIVELY" in description for automatic invocation
- Archon-first research strategy (search Archon before assumptions)
- 2-5 keyword queries (SHORT, not long sentences)
- Autonomous working protocol (no user interaction)
- Clear output file specification
- Quality checklist before completion
- Integration guidance for downstream agents

**What to Adapt**:
- Create prp-gen-* subagents for generate-prp workflow
- Create prp-exec-* subagents for execute-prp workflow
- Adapt output file paths (prps/research/prp-gen-*, prps/execution/prp-exec-*)
- Customize quality checklists for each subagent's role

**What to Skip**:
- Nothing - this is the proven subagent structure

**Key Pattern Highlights**:

```yaml
---
name: prp-gen-codebase-researcher
description: USE PROACTIVELY for pattern extraction. Searches Archon and codebase for similar implementations, extracts patterns, creates codebase-patterns.md.
tools: Read, Write, Grep, Glob, mcp__archon__rag_search_code_examples
color: green
---
```

```python
# Archon-first with SHORT queries
results = mcp__archon__rag_search_knowledge_base(
    query="FastAPI async",  # 2-5 keywords!
    match_count=5
)
```

```markdown
## Output Location
**CRITICAL**: Output file to exact path:
prps/research/codebase-patterns.md
```

**Why This Example**:
Provides the complete blueprint for creating new PRP-focused subagents. The factory has 6 proven subagents - we need to create similar ones for generate-prp (6 subagents) and execute-prp (3-5 subagents).

**Subagents to Create for generate-prp**:
1. prp-gen-feature-analyzer (reads INITIAL.md, extracts requirements)
2. prp-gen-codebase-researcher (finds patterns in codebase)
3. prp-gen-documentation-hunter (finds official docs)
4. prp-gen-example-curator (extracts code to examples/)
5. prp-gen-gotcha-detective (identifies pitfalls)
6. prp-gen-assembler (synthesizes into final PRP)

**Subagents to Create for execute-prp**:
1. prp-exec-task-analyzer (analyzes dependencies, creates execution plan)
2. prp-exec-implementer (one or more for parallel execution)
3. prp-exec-validator (runs validation gates, iterates on failures)
4. prp-exec-test-generator (generates tests based on implementation)

---

### archon_integration_pattern.md - Task Tracking

**Source**: `.claude/commands/create-initial.md` (lines 38-87)
**Original Context**: Archon MCP integration in factory orchestrator

**What to Mimic**:
- Health check FIRST before any Archon operations
- Graceful fallback if Archon unavailable
- Creating project for tracking
- Creating tasks for each phase/subagent
- Task status flow: todo → doing → done
- Task order for priority (higher = more important)
- Passing project_id to all subagents
- Updating task status before/after each phase
- Error handling with task status reset
- Storing final outputs as Archon documents

**What to Adapt**:
- Create project for PRP generation or execution
- Task titles specific to PRP workflow phases
- Assignee names for prp-gen-* and prp-exec-* subagents
- Document storage for PRPs (not INITIAL.md)

**What to Skip**:
- Nothing - this is the complete Archon integration pattern

**Key Pattern Highlights**:

```python
# Health check first
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# Graceful fallback
if not archon_available:
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
    project_id = None
```

```python
# Task status flow
mcp__archon__manage_task("update", task_id=task_id, status="doing")
# ... work ...
mcp__archon__manage_task("update", task_id=task_id, status="done")
```

```python
# Error recovery
if error:
    mcp__archon__manage_task("update",
        task_id=task_id,
        description=f"ERROR: {e}",
        status="todo"  # Reset to allow retry
    )
```

**Why This Example**:
Shows complete Archon integration that provides progress visibility, enables retry on failure, and stores artifacts for future reference. This addresses the ARCHON-FIRST RULE requirement and eliminates TodoWrite usage.

**Application to generate-prp**:
- Create project: "PRP Generation: {feature_name}"
- Create 6 tasks for 6 subagents
- Track progress through phases
- Store final PRP as Archon document

**Application to execute-prp**:
- Create project: "PRP Execution: {feature_name}"
- Create tasks from PRP task list
- Update status as tasks complete
- Track validation results

---

### code_extraction_pattern.md - CRITICAL Difference

**Source**: `.claude/agents/prp-initial-example-curator.md` (lines 16-101)
**Original Context**: Example curator subagent that extracts actual code files

**What to Mimic**:
- Extract code to PHYSICAL FILES, not just references
- Add source attribution comments to each file
- Create comprehensive README with "what to mimic" guidance
- Search Archon first, then local codebase
- Use SHORT queries (2-5 keywords)
- Rate each example X/10 for relevance
- Extract pattern highlights in README
- Provide complete context (enough to be runnable)

**What to Adapt**:
- Apply to prp-gen-example-curator for generate-prp
- Extract examples relevant to PRP feature being implemented
- Adapt README template for different feature types

**What to Skip**:
- Referencing without extracting (the WRONG approach)

**Key Pattern Highlights**:

```python
# WRONG ❌
"""See src/api/auth.py for authentication pattern"""

# RIGHT ✅
source = Read("src/api/auth.py")
auth_pattern = extract_lines(source, start=45, end=67)
Write(f"examples/{feature_name}/auth_pattern.py", auth_pattern)
```

```python
# Source attribution
attribution = f"""# Source: {original_file}
# Lines: {start_line}-{end_line}
# Pattern: {what_it_demonstrates}

{code}
"""
```

**README Requirements Per Example**:
- What to Mimic: Specific techniques to copy
- What to Adapt: Parts to customize
- What to Skip: Irrelevant code
- Pattern Highlights: Key code snippets
- Why This Example: Explanation of value

**Why This Example**:
This is the MOST IMPORTANT difference between current generate-prp and improved version. Current approach just references existing files ("See src/api/auth.py"). Factory extracts actual code to examples/ directory with comprehensive README. Developers can study, run, and modify actual code - far more useful.

**Application to generate-prp**:
- prp-gen-example-curator searches Archon + codebase
- Extracts 2-4 most relevant code examples
- Creates examples/{feature}/ directory
- Generates README with detailed guidance
- Referenced in final PRP for implementation

---

## Usage Instructions

### Study Phase

1. **Read each example file** to understand the pattern
2. **Read this README guidance** for what to mimic vs. adapt
3. **Identify commonalities** across examples (Archon-first, autonomous, quality gates)

### Application Phase - Improved generate-prp

**New Structure**:
```
Phase 0: Orchestrator reads INITIAL.md, checks Archon, creates project
Phase 1: prp-gen-feature-analyzer (autonomous)
Phase 2: Parallel - 3 subagents simultaneously:
  - prp-gen-codebase-researcher
  - prp-gen-documentation-hunter
  - prp-gen-example-curator (EXTRACTS code files)
Phase 3: prp-gen-gotcha-detective (autonomous)
Phase 4: prp-gen-assembler (synthesizes into PRP)
Phase 5: Quality check (8+/10), store in Archon, deliver
```

**Key Changes**:
1. Parallel research (Phase 2) - 3x speedup
2. Code extraction to examples/ - actual files, not references
3. Systematic gotcha detection - dedicated phase
4. Quality gate enforcement - reject if <8/10
5. Archon task tracking - visibility and retry capability

### Application Phase - Improved execute-prp

**New Structure**:
```
Phase 0: Orchestrator reads PRP, checks Archon, creates project
Phase 1: prp-exec-task-analyzer analyzes dependencies, groups tasks
Phase 2: Execute groups in parallel:
  Group 1: [independent tasks] - parallel execution
  Group 2: [tasks depending on Group 1] - parallel execution
  Group 3: [tasks depending on Group 2] - parallel execution
Phase 3: prp-exec-validator runs validation gates, iterates on failures
Phase 4: prp-exec-test-generator creates tests based on patterns
Phase 5: Final validation suite, update Archon, deliver
```

**Key Changes**:
1. Task dependency analysis - identify parallelization opportunities
2. Parallel task execution - multiple prp-exec-implementer subagents
3. Automated test generation - based on codebase patterns
4. Systematic validation gates - syntax, unit, integration
5. Archon task tracking - progress visibility

### Don't Copy-Paste Directly

These examples are PATTERNS to learn from, not code to copy verbatim:

1. **Extract the PATTERN**, not the specific implementation
2. **Adapt to PRP workflow context** (not INITIAL.md factory)
3. **Test patterns work** in your context
4. **Iterate** - use examples as starting point

## Pattern Summary

### Common Patterns Across All Examples

1. **Archon-First Strategy**:
   - Health check before operations
   - Search Archon before web/local
   - Use 2-5 keyword queries (SHORT!)
   - Graceful fallback if unavailable

2. **Autonomous Execution**:
   - Subagents work without user interaction
   - Make intelligent assumptions
   - Document all assumptions with reasoning
   - Clear output file specifications

3. **Quality Gates**:
   - Checklists before completion
   - Scoring (1-10 or X/10)
   - Minimum thresholds (8+/10)
   - Verification before proceeding

4. **Parallel Execution**:
   - Identify independent tasks
   - Invoke multiple subagents in SINGLE message
   - Use Task tool multiple times in one response
   - Collect outputs after all complete

5. **Task Tracking**:
   - Create Archon project and tasks
   - Status flow: todo → doing → done
   - Update before/after each phase
   - Reset to "todo" on error for retry

6. **Code Extraction**:
   - Extract to physical files, not references
   - Add source attribution comments
   - Create README with "what to mimic" guidance
   - Rate relevance X/10

### Testing Patterns

- Validation loops (run, fix, re-run until pass)
- Quality checklists before proceeding
- Confidence scoring (1-10)
- Multiple validation levels (syntax, unit, integration)

### Error Handling Patterns

- Health checks before operations
- Graceful fallback when services unavailable
- Task status reset on error (enables retry)
- Clear error messages with recovery options
- Continue workflow even if tracking unavailable

## Integration Notes

### How These Examples Relate to PRP Workflow Improvements

**generate-prp improvements**:
- Apply factory's 6-phase subagent architecture
- Use parallel research pattern from Phase 2
- Adopt code extraction methodology from example-curator
- Implement Archon tracking from factory orchestrator
- Enforce quality gates (8+/10 minimum)

**execute-prp improvements**:
- Add task dependency analysis (new capability)
- Apply parallel execution pattern for independent tasks
- Use Archon tracking instead of TodoWrite
- Add automated test generation based on codebase patterns
- Implement validation loops at multiple levels

**Gaps these examples don't cover**:
- Task dependency analysis logic (new, needs design)
- Test generation heuristics (new, needs patterns from codebase)
- PRP parsing for task extraction (straightforward but new)

## Quick Reference

### Factory Parallel Pattern: When to Use
- Phase 2 of generate-prp (research: codebase, docs, examples, gotchas)
- Task groups in execute-prp (independent tasks within same group)
- Any time you have 2+ independent operations

### Subagent Structure: When to Use
- Creating new prp-gen-* subagents (6 total)
- Creating new prp-exec-* subagents (3-5 total)
- Any autonomous research or execution task

### Archon Integration: When to Use
- Orchestrator level (both generate-prp and execute-prp)
- Task tracking throughout workflow
- Storing final outputs (PRPs, validation results)

### Code Extraction: When to Use
- prp-gen-example-curator in generate-prp
- Any time you want to provide code examples to developers
- When references aren't sufficient (most cases)

### Current Commands: When to Reference
- Understanding existing workflow to preserve good patterns
- Identifying gaps to address in new version
- Ensuring backward compatibility

---

Generated: 2025-10-04
Total Examples: 6 (5 code files + 1 README)
Source Types: Factory: 4, Current Commands: 2
Feature: prp_workflow_improvements
Quality Score: 10/10 - Comprehensive examples with detailed guidance
