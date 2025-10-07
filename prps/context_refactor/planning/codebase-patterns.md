# Codebase Patterns: PRP Context Refactor

## Overview

Analyzed CLAUDE.md, README.md, pattern files (archon-workflow.md, parallel-subagents.md, quality-gates.md), and command files (generate-prp.md, execute-prp.md) to identify duplication, compression opportunities, and extraction targets. Found 60% duplication between CLAUDE.md and README.md, identical 34-line security functions in both commands, and tutorial-style patterns that can be compressed to reference card format (373-387 lines → 120 lines target).

## Architectural Patterns

### Pattern 1: Progressive Disclosure (Two-Level Maximum)
**Source**: Current pattern files, CLAUDE.md structure
**Relevance**: 10/10 (core principle for context optimization)
**What it does**: Limits information hierarchy to two levels (command→pattern, done) to prevent context explosion

**Key Techniques**:
```markdown
# WRONG: Three-level disclosure (command → pattern → sub-pattern)
.claude/commands/generate-prp.md
  → references .claude/patterns/archon-workflow.md
    → references .claude/patterns/archon-health-check.md  # TOO DEEP!

# CORRECT: Two-level disclosure
.claude/commands/generate-prp.md
  → references .claude/patterns/archon-workflow.md (self-contained)
```

**Current state**: All 3 pattern files correctly follow two-level maximum
**Pattern files index**: `.claude/patterns/README.md` lists all patterns with quick reference table

**When to use**:
- Always when creating new patterns
- When refactoring existing documentation
- When deciding pattern vs inline code

**How to adapt**:
- CLAUDE.md should reference README.md (not duplicate)
- Pattern files should be self-contained (no sub-patterns)
- Commands should reference patterns (not duplicate implementations)

**Why this pattern**:
- Prevents context explosion (exponential growth)
- Reduces cognitive load (easier to scan)
- Enables token budget control (finite resource)

### Pattern 2: Reference Card vs Tutorial Style
**Source**: `.claude/patterns/*.md` (current: tutorial style)
**Relevance**: 10/10 (primary compression target)
**What it does**: Presents information as copy-paste ready code with minimal commentary vs extensive explanations

**Key Techniques**:
```markdown
# TUTORIAL STYLE (verbose - 373 lines)
## Health Check Pattern

Every Archon workflow must start with a health check. This is important
because it determines whether Archon is available and enables graceful
fallback if not. The health check should always be the first operation
you perform before attempting any Archon integration.

**Why this matters**: Without checking health first, your workflow will
fail if Archon is unavailable. By checking first, you can gracefully
degrade and continue working even without Archon tracking.

```python
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"
```

This code calls the health_check function...
[continues for many paragraphs]

# REFERENCE CARD STYLE (compressed - 120 lines)
## Health Check (ALWAYS FIRST)

```python
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"
# Returns: {"status": "healthy"} or raises exception
```

**Why first?** Determines Archon availability, enables graceful fallback.
```

**Current state**:
- archon-workflow.md: 373 lines (tutorial style)
- parallel-subagents.md: 387 lines (tutorial style)
- quality-gates.md: 385 lines (tutorial style)

**Compression ratio**: 68% reduction (373→120 lines per file)

**When to use**:
- Pattern files: Always reference card style
- README.md: Tutorial style (user-facing documentation)
- CLAUDE.md: Rules only (neither tutorial nor reference)

**How to adapt**:
- Remove extensive commentary (keep ≤20% commentary, 80%+ code)
- Consolidate duplicate examples (one canonical example per pattern)
- Replace verbose descriptions with terse bullet points
- Keep critical warnings and anti-patterns

**Target metrics**:
- 80%+ code snippets (by line count)
- ≤20% commentary
- 4-5 core patterns per file
- 120 lines target, 150 lines hard limit

### Pattern 3: DRY Violation - CLAUDE.md Duplicates README.md
**Source**: CLAUDE.md lines 5-285, README.md lines 1-166
**Relevance**: 10/10 (primary duplication target)
**What it does**: CLAUDE.md repeats 60% of README.md content (architecture, directory structure, MCP servers)

**Key Duplication Points**:

**Lines 5-35 (CLAUDE.md)** duplicates **Lines 1-115 (README.md)**:
```markdown
# CLAUDE.md (31 lines)
## Repository Overview
Vibes is a Claude Code workspace for AI-assisted development...

### Directory Structure
vibes/
├── .claude/
├── mcp/
├── prps/
...

### Key Components
**MCP Servers**
- mcp-vibesbox-server: Python-based MCP server...
  - Runs commands in containerized environments...
  - Takes screenshots...
  - Uses ImageMagick...

# README.md (115 lines) - IDENTICAL CONTENT
Vibes transforms Claude Desktop...
## Current Architecture
[same directory structure]
[same MCP server descriptions]
```

**Lines 157-180 (CLAUDE.md)** duplicates **Lines 22-62 (README.md)**:
```markdown
# CLAUDE.md - Working with MCP Servers
Start the vibesbox server:
cd mcp/mcp-vibesbox-server
docker-compose up -d

# README.md - Quick Start
Same exact commands
```

**Lines 247-275 (CLAUDE.md)** duplicates **Lines 64-72 (README.md)**:
```markdown
# CLAUDE.md - File Patterns → MCP Servers
Docker Compose configuration in each server directory
Main server logic in server.py
Use mcp.server.Server class

# README.md - Current Capabilities
Same descriptions
```

**Duplication summary**:
- Repository Overview: 100% duplicate
- Directory Structure: 100% duplicate
- MCP Server details: 95% duplicate
- Quick Start commands: 100% duplicate
- Key Technologies: 90% duplicate

**Total duplicate lines**: ~234 lines (60% of CLAUDE.md's 389 lines)

**When to use DRY fix**:
- Replace duplicated sections with references: "See README.md for architecture details"
- Keep unique rules in CLAUDE.md (Archon-first rule, PRP workflow, pattern references)
- README.md remains unchanged (user-facing documentation)

**How to adapt**:
```markdown
# BEFORE (389 lines)
## Repository Overview
Vibes is a Claude Code workspace... [31 lines of duplication]

### Directory Structure
vibes/
├── .claude/  [25 lines of duplication]

### Key Components
**MCP Servers**
- mcp-vibesbox-server: [60 lines of duplication]

# AFTER (100 lines)
## Repository Overview
See README.md for full architecture, directory structure, and MCP server details.

## Project Rules (CLAUDE.md-specific content)
- CRITICAL: ARCHON-FIRST RULE...
- Pattern Library: .claude/patterns/...
- PRP-Driven Development...
```

**Net savings**: 234 duplicate lines removed = 60% reduction (389→155 lines)

### Pattern 4: Security Function Extraction
**Source**: `.claude/commands/generate-prp.md` lines 33-66, `.claude/commands/execute-prp.md` lines 33-66
**Relevance**: 10/10 (eliminates duplication, improves maintainability)
**What it does**: Identical `extract_feature_name()` function duplicated in both commands (34 lines × 2 = 68 lines)

**Current duplication**:
```python
# generate-prp.md lines 33-66 (34 lines)
def extract_feature_name(filepath: str) -> str:
    """Safely extract feature name with strict validation."""
    # SECURITY: Check for path traversal in full path first
    if ".." in filepath:
        raise ValueError(f"Path traversal detected in filepath: {filepath}")

    basename = filepath.split("/")[-1]
    feature = basename.replace("INITIAL_", "").replace(".md", "")

    # SECURITY: Whitelist validation (only safe characters)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(
            f"Invalid feature name: '{feature}'\n"
            f"Must contain only: letters, numbers, hyphens, underscores\n"
            f"Examples: user_auth, web-scraper, apiClient123"
        )

    # SECURITY: Length validation
    if len(feature) > 50:
        raise ValueError(f"Feature name too long: {len(feature)} chars (max: 50)")

    # SECURITY: No directory traversal in feature name
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal detected: {feature}")

    # SECURITY: No command injection
    dangerous_chars = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(char in feature for char in dangerous_chars):
        raise ValueError(f"Dangerous characters detected: {feature}")

    return feature

feature_name = extract_feature_name(initial_md_path)

# execute-prp.md lines 33-66 (34 lines) - IDENTICAL except:
# - Line 40: removes "INITIAL_" prefix (generate-prp specific)
# - Line 65: uses `prp_path` instead of `initial_md_path`
```

**Differences**:
- generate-prp: Strips "INITIAL_" prefix (line 40)
- execute-prp: No prefix stripping (different input format)
- Parameter names: `initial_md_path` vs `prp_path`

**Extraction target**: `.claude/patterns/security-validation.md` (~40 lines)

**After extraction**:
```markdown
# .claude/patterns/security-validation.md (40 lines)
# Security Validation Pattern

## Feature Name Extraction (Path Traversal Prevention)

```python
import re

def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """Safely extract feature name with strict validation."""
    # SECURITY: Path traversal check
    if ".." in filepath:
        raise ValueError(f"Path traversal detected: {filepath}")

    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")

    if strip_prefix:
        feature = feature.replace(strip_prefix, "")

    # SECURITY: Whitelist validation
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(
            f"Invalid feature name: '{feature}'\n"
            f"Must contain only: letters, numbers, hyphens, underscores"
        )

    # SECURITY: Length validation
    if len(feature) > 50:
        raise ValueError(f"Feature name too long: {len(feature)} chars (max: 50)")

    # SECURITY: Directory traversal
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal detected: {feature}")

    # SECURITY: Command injection
    dangerous_chars = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(char in feature for char in dangerous_chars):
        raise ValueError(f"Dangerous characters detected: {feature}")

    return feature
```

**Usage**:
```python
# In generate-prp.md
feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")

# In execute-prp.md
feature_name = extract_feature_name(prp_path)
```

**Command replacement** (2 lines each):
```python
# generate-prp.md lines 33-66 → 2 lines
# See .claude/patterns/security-validation.md for implementation
feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")

# execute-prp.md lines 33-66 → 2 lines
# See .claude/patterns/security-validation.md for implementation
feature_name = extract_feature_name(prp_path)
```

**Net savings**: 68 lines - (40 + 4) = 24 lines

**When to use**:
- Any command that needs to extract feature names from file paths
- Security-critical path validation
- Scoped directory creation

**How to adapt**:
- Add `strip_prefix` parameter to handle different input formats
- Keep all 5 security checks (whitelist, path traversal, length, directory traversal, command injection)
- Reference pattern in commands (don't duplicate)

### Pattern 5: Scoped Directory Creation
**Source**: `.claude/commands/generate-prp.md` lines 67-69, execute-prp.md lines 67-68
**Relevance**: 8/10 (security-critical, repeated pattern)
**What it does**: Creates per-feature directories to prevent global pollution

**Current implementation**:
```bash
# generate-prp.md
Bash(f"mkdir -p prps/{feature_name}/planning")
Bash(f"mkdir -p prps/{feature_name}/examples")

# execute-prp.md
Bash(f"mkdir -p prps/{feature_name}/execution")
```

**Pattern principle**: Scoped, not global
```bash
# WRONG: Global directories (pollution risk)
mkdir -p prps/research/
mkdir -p prps/examples/

# CORRECT: Per-feature scoped
mkdir -p prps/{feature_name}/planning/
mkdir -p prps/{feature_name}/examples/
mkdir -p prps/{feature_name}/execution/
```

**When to use**:
- All PRP-related directory creation
- Any output that should be organized per-feature
- Validation reports, completion reports

**How to adapt**:
- Always use `prps/{feature_name}/` prefix
- Use semantic subdirectory names (planning, examples, execution)
- Preserve this pattern in refactored commands

**Why this pattern**:
- Prevents file conflicts between features
- Enables parallel PRP generation
- Simplifies cleanup (delete one directory)

## Naming Conventions

### File Naming

**Pattern files**:
- Format: `{topic}-{category}.md`
- Examples: `archon-workflow.md`, `parallel-subagents.md`, `quality-gates.md`, `security-validation.md`
- No verbs: ❌ `executing-parallel.md` ✅ `parallel-subagents.md`
- Kebab-case: ✅ `security-validation.md` ❌ `security_validation.md`

**Command files**:
- Format: `{verb}-{noun}.md`
- Examples: `generate-prp.md`, `execute-prp.md`, `list-prps.md`, `prp-cleanup.md`
- Kebab-case: ✅ `generate-prp.md` ❌ `generate_prp.md`

**Agent files**:
- Format: `prp-{phase}-{role}.md`
- Examples: `prp-gen-feature-analyzer.md`, `prp-exec-implementer.md`
- Phase prefixes: `gen` (generation), `exec` (execution)
- Kebab-case with underscores for role: ✅ `prp-gen-codebase-researcher.md`

**PRP files**:
- Format: `{feature_name}.md`
- Examples: `user_auth.md`, `web_scraper.md`, `api_client.md`
- Snake_case: ✅ `user_auth.md` ❌ `user-auth.md`
- Input format: `INITIAL_{feature_name}.md`

**Research files** (inside `prps/{feature}/planning/`):
- `feature-analysis.md` (not feature_analysis.md)
- `codebase-patterns.md`
- `documentation-links.md`
- `gotchas.md`
- Kebab-case: ✅ `codebase-patterns.md` ❌ `codebase_patterns.md`

### Class Naming

Not applicable - this is a markdown documentation project with no classes.

### Function Naming

**Security functions** (extracted to patterns):
- `extract_feature_name()` - validates and extracts feature name from path
- Snake_case: ✅ `extract_feature_name()` ❌ `extractFeatureName()`

**Archon MCP functions**:
- `mcp__archon__health_check()`
- `mcp__archon__manage_project()`
- `mcp__archon__manage_task()`
- `mcp__archon__rag_search_code_examples()`
- Double underscores: Namespace separator (mcp, archon, function)

**Pattern**: Functions described in pseudocode (not actual Python code)

## File Organization

### Directory Structure

**Current state**:
```
.claude/
├── agents/                    # Subagent definitions (10 files)
│   ├── prp-gen-feature-analyzer.md (222 lines)
│   ├── prp-gen-codebase-researcher.md (300 lines)
│   ├── prp-gen-documentation-hunter.md (369 lines)
│   ├── prp-gen-example-curator.md (389 lines)
│   ├── prp-gen-gotcha-detective.md (517 lines)
│   ├── prp-gen-assembler.md (495 lines)
│   ├── prp-exec-task-analyzer.md (431 lines)
│   ├── prp-exec-implementer.md (350 lines)
│   ├── prp-exec-validator.md (497 lines)
│   ├── prp-exec-test-generator.md (510 lines)
│   ├── documentation-manager.md (72 lines)
│   └── validation-gates.md (133 lines)
├── commands/                  # Custom slash commands (7 files)
│   ├── generate-prp.md (655 lines) ← TARGET: 330 lines
│   ├── execute-prp.md (663 lines) ← TARGET: 330 lines
│   ├── list-prps.md (134 lines)
│   ├── prp-cleanup.md (290 lines)
│   ├── prep-parallel.md (14 lines)
│   ├── execute-parallel.md (27 lines)
│   └── primer.md (16 lines)
├── patterns/                  # Reusable patterns (4 files)
│   ├── README.md (57 lines) ← UPDATE: Add security-validation.md
│   ├── archon-workflow.md (373 lines) ← TARGET: 120 lines
│   ├── parallel-subagents.md (387 lines) ← TARGET: 120 lines
│   ├── quality-gates.md (385 lines) ← TARGET: 120 lines
│   └── security-validation.md (NEW) ← CREATE: 40 lines
└── templates/                 # Report templates (3 files)
    ├── validation-report.md (105 lines)
    ├── completion-report.md (32 lines)
    └── (prp_base.md in prps/templates/)

CLAUDE.md (389 lines) ← TARGET: 100 lines
README.md (166 lines) ← NO CHANGE (user-facing)
```

**Target state** (after refactoring):
```
.claude/
├── patterns/
│   ├── README.md (60 lines) ← +3 lines (new entry)
│   ├── archon-workflow.md (120 lines) ← -253 lines (68% reduction)
│   ├── parallel-subagents.md (120 lines) ← -267 lines (69% reduction)
│   ├── quality-gates.md (120 lines) ← -265 lines (69% reduction)
│   └── security-validation.md (40 lines) ← NEW
├── commands/
│   ├── generate-prp.md (330 lines) ← -325 lines (50% reduction)
│   └── execute-prp.md (330 lines) ← -333 lines (50% reduction)

CLAUDE.md (100 lines) ← -289 lines (74% reduction)
```

**Justification**:
- Pattern files: Reference card style (80% code, 20% commentary)
- Commands: Orchestration only (reference patterns, don't duplicate)
- CLAUDE.md: Project rules only (reference README.md, don't duplicate)
- Security function: Extracted to pattern (single source of truth)

**Total reduction**:
- Pattern files: 1,145 → 360 lines (68% reduction)
- Commands: 1,318 → 660 lines (50% reduction)
- CLAUDE.md: 389 → 100 lines (74% reduction)
- **Total context per command call**: 1,044 → 430 lines (59% reduction)

## Common Utilities to Leverage

### 1. Archon MCP Integration (Health Check Pattern)
**Location**: `.claude/patterns/archon-workflow.md`
**Purpose**: Check Archon availability, graceful fallback if unavailable
**Usage Example**:
```python
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if archon_available:
    # Use Archon features
    project = mcp__archon__manage_project("create", ...)
else:
    # Graceful fallback
    project_id = None
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
```

**When to use**: All commands that need project/task tracking

### 2. Parallel Subagent Invocation (Performance Pattern)
**Location**: `.claude/patterns/parallel-subagents.md`
**Purpose**: Execute 3+ independent tasks simultaneously (3x speedup)
**Usage Example**:
```python
# CRITICAL: All Task() calls in SINGLE response
Task(subagent_type="prp-gen-codebase-researcher", ...)
Task(subagent_type="prp-gen-documentation-hunter", ...)
Task(subagent_type="prp-gen-example-curator", ...)
# System waits for ALL to complete
```

**When to use**: Research phases, independent implementation tasks

### 3. Quality Scoring and Validation Loops (Quality Pattern)
**Location**: `.claude/patterns/quality-gates.md`
**Purpose**: Enforce 8+/10 PRP quality, iterate on validation failures (max 5 attempts)
**Usage Example**:
```python
# Extract score from PRP
score_match = re.search(r'Score:\s*(\d+)/10', prp_content)
quality_score = int(score_match.group(1)) if score_match else 0

# Enforce minimum
if quality_score < 8:
    print(f"⚠️ Quality Gate Failed: {quality_score}/10")
    # Interactive choice: regenerate, review, or proceed
```

**When to use**: PRP assembly phase, execution validation

### 4. Feature Name Extraction (Security Pattern)
**Location**: `.claude/patterns/security-validation.md` (NEW)
**Purpose**: Safely extract feature names with 5 security checks
**Usage Example**:
```python
# See .claude/patterns/security-validation.md for implementation
feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")
```

**When to use**: All commands that process file paths

### 5. Pattern Reference Approach
**Location**: `.claude/patterns/README.md`
**Purpose**: Quick lookup table to find right pattern
**Usage Example**:
```markdown
**Need to...** | **See Pattern** | **Used By**
---|---|---
Integrate with Archon MCP | [archon-workflow.md](archon-workflow.md) | generate-prp, execute-prp
Execute subagents in parallel | [parallel-subagents.md](parallel-subagents.md) | Phase 2 workflows
Validate PRP/execution quality | [quality-gates.md](quality-gates.md) | Phase 5, Phase 4
Extract secure feature names | [security-validation.md](security-validation.md) | All commands
```

**When to use**: Before implementing any command or pattern

## Testing Patterns

### Unit Test Structure
**Pattern**: Not applicable - this project has no unit tests (markdown documentation only)

### Integration Test Structure
**Pattern**: Functionality test via command execution
**Example**: Run `/generate-prp` on test INITIAL.md, verify PRP created

**Validation approach** (from prp_context_cleanup):
```bash
# Level 1: File Size Validation
wc -l .claude/patterns/archon-workflow.md  # Should be ≤150 lines
wc -l CLAUDE.md  # Should be ≤120 lines

# Level 2: Duplication Check
grep "Repository Overview" CLAUDE.md  # Should NOT exist (0 results)
grep "Vibes is a Claude Code workspace" CLAUDE.md  # Should NOT exist

# Level 3: Pattern Loading Check
grep '@.claude/patterns' .claude/commands/generate-prp.md  # Should be 0 results

# Level 4: Functionality Test
/generate-prp prps/INITIAL_test_feature.md  # Should succeed

# Level 5: Token Usage Measurement
# Count total lines loaded per command call (target: ≤450 lines)
```

**Key techniques**:
- File size checks: `wc -l` against hard limits
- Duplication detection: `grep` for README.md content in CLAUDE.md
- Pattern loading: Ensure no `@` loads (documentation-style references only)
- Functionality: Run command on test input
- Metrics: Line count summation

## Anti-Patterns to Avoid

### 1. Three-Level Disclosure (Context Explosion)
**What it is**: Creating sub-patterns or nested references beyond command→pattern
**Why to avoid**: Exponential context growth, violates progressive disclosure principle
**Found in**: Current system correctly avoids this
**Better approach**: Keep two-level maximum (command→pattern, pattern is self-contained)

**Example**:
```markdown
# ANTI-PATTERN (three levels)
.claude/commands/generate-prp.md
  → references .claude/patterns/archon-workflow.md
    → references .claude/patterns/archon-health-check.md  # TOO DEEP!

# CORRECT (two levels)
.claude/commands/generate-prp.md
  → references .claude/patterns/archon-workflow.md (includes health check)
```

**Detection**: Check patterns for references to other patterns

### 2. Duplicating Pattern Code in Commands
**What it is**: Copying pattern implementations into command files instead of referencing
**Why to avoid**: Defeats DRY purpose, creates maintenance burden
**Found in**: Security function duplicated in both commands (lines 33-66)
**Better approach**: Extract to pattern, reference with 1-2 lines

**Example**:
```python
# ANTI-PATTERN (325 lines duplicated)
# In generate-prp.md:
def extract_feature_name(filepath: str) -> str:
    [34 lines of implementation]

# In execute-prp.md:
def extract_feature_name(filepath: str) -> str:
    [34 lines of identical implementation]

# CORRECT (reference pattern)
# In both commands:
# See .claude/patterns/security-validation.md for implementation
feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")
```

**Detection**: `grep "def extract_feature_name"` should return 1 result (pattern file only)

### 3. Duplicating README.md in CLAUDE.md
**What it is**: Repeating architecture, directory structure, MCP server details in both files
**Why to avoid**: 60% of CLAUDE.md is duplicated content (234 lines wasted)
**Found in**: CLAUDE.md lines 5-285 duplicate README.md content
**Better approach**: CLAUDE.md references README.md, keeps only project-specific rules

**Example**:
```markdown
# ANTI-PATTERN (234 lines duplicated)
# CLAUDE.md
## Repository Overview
Vibes is a Claude Code workspace for AI-assisted development...
[31 lines identical to README.md]

### Directory Structure
vibes/
├── .claude/
[25 lines identical to README.md]

# CORRECT (reference)
# CLAUDE.md
## Repository Overview
See README.md for full architecture, directory structure, and MCP server details.

## Project Rules (CLAUDE.md-specific)
- CRITICAL: ARCHON-FIRST RULE...
```

**Detection**: `grep "Vibes is a Claude Code workspace" CLAUDE.md` should return 0 results

### 4. Tutorial Style in Pattern Files
**What it is**: Extensive commentary, multiple variations, detailed explanations in pattern files
**Why to avoid**: Pattern files should be reference cards (80% code, 20% commentary)
**Found in**: All 3 pattern files (373-387 lines each, target 120 lines)
**Better approach**: Condensed code snippets with minimal commentary

**Example**:
```markdown
# ANTI-PATTERN (verbose tutorial)
## Health Check Pattern

Every Archon workflow must start with a health check. This is important
because it determines whether Archon is available and enables graceful
fallback if not. The health check should always be the first operation
you perform before attempting any Archon integration.

**Why this matters**: Without checking health first, your workflow will
fail if Archon is unavailable...
[continues for many paragraphs]

# CORRECT (reference card)
## Health Check (ALWAYS FIRST)

```python
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"
```

**Why first?** Determines Archon availability, enables graceful fallback.
```

**Detection**: Calculate code/commentary ratio (should be 80/20)

### 5. Loading Patterns with @ Syntax
**What it is**: Using `@.claude/patterns/archon-workflow.md` to load pattern content into context
**Why to avoid**: Defeats progressive disclosure, explodes context budget
**Found in**: Current system correctly avoids this (validation check passed)
**Better approach**: Reference patterns in documentation style ("See .claude/patterns/...")

**Example**:
```python
# ANTI-PATTERN (loads pattern into context)
# @.claude/patterns/archon-workflow.md  # Adds 373 lines to context!

# CORRECT (reference in documentation)
# Health check pattern: See .claude/patterns/archon-workflow.md
health = mcp__archon__health_check()
```

**Detection**: `grep '@.claude/patterns' .claude/commands/*.md` should return 0 results

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. prp_context_cleanup (Previous Refactoring)
**Location**: prps/prp_context_cleanup/ (completed)
**Similarity**: 95% - Same refactoring approach, security extraction, validation gates
**Lessons**:
- 5-level validation approach works (23/24 criteria passed, 95.8% success)
- Scoped directory creation prevents pollution
- Security function extraction is safe
- Archon integration with graceful fallback is reliable

**Differences**:
- prp_context_cleanup: Removed global `research/` directories
- prp_context_refactor: Compressing pattern files and CLAUDE.md

**Validation report**: `prps/prp_context_cleanup/execution/validation-report.md`
**Key metrics**:
- 116 lines added (security + scoping features)
- 23/24 validation criteria passed (95.8%)
- All functionality preserved

#### 2. Pattern Files Structure (Current State)
**Location**: `.claude/patterns/*.md`
**Similarity**: 100% - These ARE the files to refactor
**Lessons**:
- archon-workflow.md: 373 lines → compress to 120 lines (remove tutorials)
- parallel-subagents.md: 387 lines → compress to 120 lines (remove verbose examples)
- quality-gates.md: 385 lines → compress to 120 lines (remove redundant validation descriptions)
- README.md: 57 lines → update to 60 lines (add security-validation.md entry)

**Current structure** (to preserve):
- Quick reference table at top
- Self-contained patterns (no cross-references)
- Code examples with minimal commentary
- Anti-patterns section
- Usage examples

**To compress**:
- Remove extensive "Why this matters" explanations
- Consolidate duplicate examples
- Replace verbose descriptions with bullet points
- Keep critical warnings and gotchas

#### 3. Subagent Structure (Template to Follow)
**Location**: `.claude/agents/prp-gen-codebase-researcher.md` (this file!)
**Similarity**: 90% - All subagents follow same structure
**Lessons**:
- Frontmatter: name, description, tools, color
- Primary Objective: 1-2 sentences
- Core Responsibilities: Numbered list (5-7 items)
- Output Generation: Template with markdown example
- Autonomous Working Protocol: Phased approach
- Quality Standards: Checklist
- Output Location: CRITICAL note about parameterized paths

**Structure to preserve**:
- Frontmatter (YAML)
- Primary Objective (brief)
- Core Responsibilities (organized)
- Output examples (code blocks)
- Quality checklist

**Not applicable to pattern files**: Subagent structure is different from pattern structure

## Recommendations for PRP

Based on pattern analysis:

1. **Follow DRY principle** for CLAUDE.md → README.md relationship
   - Replace 234 lines of duplication with references
   - Keep only unique project rules in CLAUDE.md
   - Target: 100 lines (74% reduction from 389 lines)

2. **Reuse reference card style** instead of tutorial style
   - Compress pattern files to 120 lines each (373-387 → 120)
   - Target: 80% code snippets, ≤20% commentary
   - Remove extensive explanations, keep critical gotchas

3. **Extract security function** to `.claude/patterns/security-validation.md`
   - Create new pattern file (~40 lines)
   - Replace 68 lines of duplication with 4 lines of references
   - Net savings: 24 lines

4. **Adapt two-level disclosure** for all documentation
   - Commands reference patterns (don't duplicate)
   - Patterns are self-contained (no sub-patterns)
   - CLAUDE.md references README.md (don't duplicate)

5. **Avoid over-compression** that breaks clarity
   - Keep critical security warnings
   - Preserve all 5 security checks in extracted function
   - Don't remove anti-patterns sections
   - Maintain copy-paste ready code examples

6. **Follow existing validation approach** from prp_context_cleanup
   - 5-level validation (file size, duplication, pattern loading, functionality, token usage)
   - Same success criteria (95.8%+ validation pass rate)
   - Iterative validation loops (max 5 attempts)

## Source References

### From Archon

**No direct matches found** - This is a novel optimization pattern:
- Searched: "context optimization DRY" (0 relevant results)
- Searched: "markdown compression patterns" (0 relevant results)
- Searched: "reference card cheat sheet" (0 relevant results)

**Key insight**: Context compression is specific to Claude Code's context engineering approach. No similar PRPs exist in Archon knowledge base.

### From Local Codebase

**CLAUDE.md duplication analysis**:
- Lines 5-35: Duplicate README.md lines 1-35 (Repository Overview, Directory Structure)
- Lines 39-46: Duplicate README.md lines 11-21 (MCP Servers)
- Lines 157-180: Duplicate README.md lines 22-62 (Quick Start)
- Lines 247-275: Duplicate README.md lines 64-72 (MCP Server details)
- **Total**: ~234 lines of duplication (60% of CLAUDE.md)

**Pattern file analysis**:
- archon-workflow.md:373: Tutorial style with extensive commentary
- parallel-subagents.md:387: Tutorial style with multiple examples
- quality-gates.md:385: Tutorial style with verbose descriptions
- **Target**: Reference card style (120 lines each)

**Security function location**:
- generate-prp.md:33-66: `extract_feature_name()` function (34 lines)
- execute-prp.md:33-66: Identical function (34 lines)
- **Extraction**: `.claude/patterns/security-validation.md` (40 lines)
- **Replacement**: 2 lines per command (reference + usage)

**Command verbosity**:
- generate-prp.md:655: 50% orchestration, 50% implementation details
- execute-prp.md:663: 50% orchestration, 50% implementation details
- **Target**: 330 lines each (orchestration only, reference patterns)

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - Show current line counts: CLAUDE.md (389), patterns (373-387), commands (655-663)
   - Show target line counts: CLAUDE.md (100), patterns (120), commands (330)
   - List duplication points: CLAUDE.md lines 5-285 duplicate README.md

2. **Include key code snippets in "Implementation Blueprint"**:
   - Reference card template (from Pattern 2)
   - DRY fix approach (from Pattern 3)
   - Security function extraction (from Pattern 4)
   - Scoped directory pattern (from Pattern 5)

3. **Add anti-patterns to "Known Gotchas" section**:
   - Three-level disclosure (Anti-Pattern 1)
   - Duplicating pattern code (Anti-Pattern 2)
   - Duplicating README.md (Anti-Pattern 3)
   - Tutorial style in patterns (Anti-Pattern 4)
   - Loading patterns with @ (Anti-Pattern 5)

4. **Use file organization for "Desired Codebase Tree"**:
   - Show target structure with reduced line counts
   - Add new `security-validation.md` pattern file
   - Update `patterns/README.md` index

5. **Reference validation approach from prp_context_cleanup**:
   - 5-level validation (same structure)
   - 95.8%+ success rate preservation
   - Iterative validation loops

6. **Include compression metrics**:
   - CLAUDE.md: 389 → 100 lines (74% reduction)
   - Pattern files: 1,145 → 360 lines (68% reduction)
   - Commands: 1,318 → 660 lines (50% reduction)
   - Total context: 1,044 → 430 lines (59% reduction)

7. **Ensure task list follows logical order**:
   - Phase 1: Extract security function to pattern
   - Phase 2: Compress pattern files (archon, parallel, quality)
   - Phase 3: Compress CLAUDE.md (remove README duplication)
   - Phase 4: Update commands (reference patterns, not duplicate)
   - Phase 5: Validation (5 levels, all must pass)

8. **Provide clear validation gates**:
   - File size checks (wc -l against targets)
   - Duplication checks (grep for README content)
   - Pattern loading checks (grep for @ syntax)
   - Functionality test (run /generate-prp)
   - Token usage measurement (line count summation)
