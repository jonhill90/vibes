# INITIAL: PRP Context Refactor (Phase 2)

## FEATURE

Eliminate remaining context pollution from the PRP system by optimizing files that successfully passed validation but still contain inefficiencies. This is Phase 2 cleanup following the successful prp_context_cleanup implementation (95.8% success rate).

**Target Reductions**:
- CLAUDE.md: 389 → 100 lines (74% reduction, -289 lines)
- Pattern files: 373-387 → 120 lines each (68% reduction, -800 lines total)
- Commands: 655/663 → 330 lines each (50% reduction, -658 lines total)
- Security duplication: 64 lines → 0 lines (extract to pattern)
- **Total context per command call**: 1,044 → 430 lines (59% reduction)

**Scope**: Optimize existing validated code, NOT add new features. Focus on density and clarity.

**Key Constraints**:
- MUST preserve all functionality (security, scoping, parallel execution, Archon integration)
- MUST maintain 95.8%+ validation success rate
- MUST keep patterns as reference cards (not tutorials)
- MUST use copy-paste ready code snippets only

## CURRENT STATE (From Validation Report)

**Validation Status**: ✅ 23/24 criteria passed (prps/prp_context_cleanup/execution/validation-report.md)

**What's Working**:
- ✅ Pattern extraction successful (1,145 lines extracted)
- ✅ DRY principle achieved (no command/pattern duplication)
- ✅ Security validation implemented (5 checks)
- ✅ Scoped directories implemented
- ✅ Patterns referenced but not loaded (correct approach)

**Remaining Pollution** (Identified Issues):

### Issue 1: CLAUDE.md Bloat (389 lines)
```
Current Structure:
├── Repository Overview (duplicates README.md)
├── Directory Structure (duplicates README.md)
├── Key Components (partially duplicates README.md)
├── Working with PRPs (duplicates command docs)
├── Pattern Library (unique content ✅)
├── Development Patterns (duplicates pattern docs)
└── Total duplication: ~60%

Target: 100 lines of project-specific rules ONLY
```

**Lines to keep**: CRITICAL rules, Archon-first rule, PRP workflow, pattern references, code standards
**Lines to remove**: Architecture (in README), directory structure (in README), workflow details (in commands), duplicate examples

### Issue 2: Pattern Files Are Mini-Tutorials (373-387 lines each)

**Current**: Tutorial style with extensive commentary, multiple variations, detailed explanations
**Target**: Reference card style with copy-paste snippets only

**Example from archon-workflow.md** (373 lines → 120 lines target):
- Currently has: Full field descriptions, multiple example variations, extensive error handling commentary
- Should have: 4-5 code snippets with minimal comments (health check, project creation, task flow, parallel updates)

**Same issue in**:
- parallel-subagents.md (387 lines → 120 lines)
- quality-gates.md (385 lines → 120 lines)

### Issue 3: Security Validation Duplication (64 lines)

**Current**: extract_feature_name() function embedded in both commands
- generate-prp.md lines 33-66 (34 lines)
- execute-prp.md lines 33-66 (34 lines)
- Total: 68 lines (34 × 2 commands, but 2 lines overlap = 64 unique)

**Target**: Extract to `.claude/patterns/security-validation.md`
- Commands: 2 lines each (comment + function call)
- Pattern: 40 lines (copy-paste ready function)
- Savings: 64 - 42 = 22 lines

### Issue 4: Command Verbosity (Still Room for Compression)

**Current**: 655/663 lines (validator says "justified by new features")
**Reality**: 50% justified (security/scoping), 50% verbose orchestration

**Example verbose sections**:
- Phase descriptions with extensive context setup (could be condensed)
- Repeated Archon update patterns (could reference pattern)
- Inline error handling examples (could reference pattern)

**Target**: 330 lines each (keep orchestration, remove pseudocode details)

## EXAMPLES

### Example 1: Slim CLAUDE.md (Before/After)

**Before** (389 lines with duplication):
```markdown
## Directory Structure
```
vibes/
├── .claude/
│   ├── agents/
│   └── commands/
├── mcp/
└── prps/
```
[50+ lines duplicating README.md]

## Key Components

**MCP Servers**
- mcp-vibesbox-server: Python-based MCP server...
[60+ lines duplicating README.md]
```

**After** (100 lines, unique content only):
```markdown
# CLAUDE.md - Vibes Project Rules

## CRITICAL: Archon-First Rule
BEFORE any task: Use find_tasks(), NEVER TodoWrite

## PRP Workflow
/generate-prp INITIAL.md → /execute-prp prps/feature.md → /prp-cleanup feature

## Patterns
See .claude/patterns/README.md

## Code Standards
- Max 500 lines/file, Pytest for all, Format: ruff + mypy
- Security: Validate inputs (see patterns/security-validation.md)

## Architecture
See README.md for full details
```

### Example 2: Compress Pattern File (Before/After)

**Before** - archon-workflow.md (373 lines, tutorial style):
```markdown
## Task Creation with Priority

Create tasks for each major phase or component:

```python
task = mcp__archon__manage_task("create",
    project_id=project_id,
    title="Phase 1: Feature Analysis",
    description="Extract requirements from INITIAL.md",
    status="todo",
    assignee="prp-gen-feature-analyzer",
    task_order=100  # Higher = higher priority (0-100)
)
task_id = task["task"]["id"]
```

**Fields:**
- `project_id`: Links task to project
- `title`: Brief task name
- `description`: What the task accomplishes
- `status`: Initial status (always `"todo"`)
- `assignee`: Who/what executes the task (subagent name or "user")
- `task_order`: Priority (higher number = higher priority, use 0-100 range)

**Priority pattern:** Start at 100 and count down (100, 90, 85, 80, 75, 70...)

**Returns:** `{"task": {"id": "uuid-string", ...}}`

[Continues for many more lines with variations...]
```

**After** - archon-workflow.md (120 lines, reference card style):
```markdown
## Task Creation
```python
task = mcp__archon__manage_task("create",
    project_id=project_id,
    title="Phase 1: Feature Analysis",
    status="todo",
    assignee="prp-gen-feature-analyzer",
    task_order=100  # Higher = higher priority (0-100)
)
task_id = task["task"]["id"]
```
```

### Example 3: Extract Security Pattern (Before/After)

**Before** - Duplicated in both commands (68 lines total):
```python
# generate-prp.md lines 33-66 (34 lines)
# execute-prp.md lines 33-66 (34 lines)

def extract_feature_name(filepath: str) -> str:
    """Safely extract feature name with strict validation."""
    # SECURITY: Check for path traversal in full path first
    if ".." in filepath:
        raise ValueError(f"Path traversal detected in filepath: {filepath}")

    basename = filepath.split("/")[-1]
    feature = basename.replace("INITIAL_", "").replace(".md", "")

    # SECURITY: Whitelist validation (only safe characters)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(...)

    # [28 more lines of security checks...]
```

**After**:

**Commands** (2 lines each):
```python
# Extract and validate feature name (see .claude/patterns/security-validation.md)
feature_name = extract_feature_name(initial_md_path)
```

**New pattern file** `.claude/patterns/security-validation.md` (~40 lines):
```markdown
# Security Validation Pattern

## Feature Name Extraction
```python
import re

def extract_feature_name(filepath: str) -> str:
    """Safely extract feature name with strict validation."""
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    basename = filepath.split("/")[-1]
    feature = basename.replace("INITIAL_", "").replace(".md", "")

    # Whitelist: letters, numbers, hyphens, underscores only
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid chars: {feature}")

    # [Security checks...]

    return feature
```

Copy-paste into your command. Done.
```

## DOCUMENTATION

**Primary References**:
- prps/prp_context_cleanup/execution/validation-report.md - Current state analysis
- .claude/patterns/README.md - Pattern library structure
- CLAUDE.md - Current bloated version (389 lines)
- .claude/patterns/archon-workflow.md - Current tutorial style (373 lines)
- .claude/patterns/parallel-subagents.md - Current tutorial style (387 lines)
- .claude/patterns/quality-gates.md - Current tutorial style (385 lines)

**Progressive Disclosure Research**:
- https://www.nngroup.com/articles/progressive-disclosure/ - Two-level max, reference card style
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents - Context as finite resource, minimal information philosophy

**DRY Principle**:
- https://en.wikipedia.org/wiki/Don't_repeat_yourself - Single source of truth
- Current duplication: CLAUDE.md duplicates README.md (~60%)

**Original Context Engineering**:
- repos/context-engineering-intro/README.md - Original template (68 + 39 = 107 lines total)
- Compare to current: 1,318 lines (12x larger)

## OTHER CONSIDERATIONS

### Gotchas & Constraints

1. **DO NOT Break Validation**: Must maintain 95.8%+ success rate from prp_context_cleanup
2. **DO NOT Add Features**: This is optimization ONLY, not enhancement
3. **DO NOT Remove Security**: All 5 security checks must remain (just relocated)
4. **DO NOT Load Patterns**: Commands must reference patterns, not @ load them
5. **DO NOT Create Sub-Patterns**: Two-level disclosure max (command → pattern, done)

### Critical Success Criteria

**File Size Targets** (Hard Limits):
- CLAUDE.md: MUST be ≤ 120 lines (target: 100 lines)
- Each pattern file: MUST be ≤ 150 lines (target: 120 lines)
- generate-prp.md: MUST be ≤ 350 lines (target: 330 lines)
- execute-prp.md: MUST be ≤ 350 lines (target: 330 lines)

**Quality Preservation**:
- All 23 passing validation criteria MUST still pass
- Security validation MUST remain robust (5 checks)
- Parallel execution MUST still work (3x speedup)
- Archon integration MUST still work (graceful degradation)

**Density Metrics**:
- Pattern files: 80%+ code snippets (≤20% commentary)
- CLAUDE.md: 0% duplication with README.md
- Commands: Reference patterns (not duplicate them)

### Testing Requirements

**Validation Levels** (Same as prp_context_cleanup):
1. File size validation (wc -l checks against targets)
2. Duplication check (grep for README content in CLAUDE.md = 0 results)
3. Pattern loading check (grep '@.claude/patterns' in commands = 0 results)
4. Functionality test (run /generate-prp on test INITIAL.md, verify success)
5. Token usage measurement (total lines loaded per command call)

**Expected Results**:
- Total context per /generate-prp call: ≤ 450 lines (vs 1,044 current)
- Total context per /execute-prp call: ≤ 450 lines (vs 1,052 current)
- Pattern files: ≤ 450 total lines (vs 1,145 current)
- Security duplication: 0 instances (vs 2 current)

### Migration Strategy

**Phase 1**: Slim CLAUDE.md (1 hour)
- Remove architecture duplication
- Remove directory structure duplication
- Remove workflow detail duplication
- Keep: CRITICAL rules, Archon-first, PRP workflow, pattern refs, code standards

**Phase 2**: Extract Security Pattern (30 min)
- Create .claude/patterns/security-validation.md
- Update pattern index README.md
- Replace command implementations with references

**Phase 3**: Compress Pattern Files (3 hours)
- Archon-workflow: 373 → 120 lines (remove tutorials, keep snippets)
- Parallel-subagents: 387 → 120 lines (remove commentary, keep critical rules)
- Quality-gates: 385 → 120 lines (remove variations, keep core examples)

**Phase 4**: Optimize Commands (2 hours)
- Remove verbose phase descriptions
- Condense context setup blocks
- Reference patterns for repeated Archon patterns
- Remove inline error handling examples

**Phase 5**: Validate & Measure (1 hour)
- Run all 5 validation levels
- Measure token usage (before/after)
- Verify 23/24 criteria still pass
- Confirm functionality preservation

**Total Effort**: ~8 hours
**Expected ROI**: 59% context reduction per command call

### Known Risks

**Risk 1**: Over-compression breaks clarity
- Mitigation: Maintain copy-paste ready code snippets
- Validation: Test patterns work when copy-pasted into commands

**Risk 2**: Breaking existing validation criteria
- Mitigation: Run validation after each phase
- Rollback: Keep backups before each phase

**Risk 3**: Removing necessary context
- Mitigation: Use validation report as checklist (what MUST stay)
- Test: Verify all 23 passing criteria still pass

### Success Metrics

**Quantitative**:
- CLAUDE.md: ≥74% reduction (389 → 100 lines)
- Patterns: ≥68% reduction (1,145 → 360 lines)
- Commands: ≥50% reduction (1,318 → 660 lines)
- Security duplication: 100% elimination (64 → 0 unique lines)
- Total context per call: ≥59% reduction (1,044 → 430 lines)

**Qualitative**:
- Pattern files feel like "cheat sheets" not "tutorials"
- CLAUDE.md is project rules ONLY
- Commands are orchestration ONLY
- Zero duplication across files
- Faster to scan and reference

**Validation**:
- All 23 passing criteria MUST still pass
- Optional: Fix 24th criterion (documentation paths) for 100% pass rate
