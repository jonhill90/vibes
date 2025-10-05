# PRP: Context Refactor (Phase 2 Cleanup)

**Generated**: 2025-10-05
**Based On**: prps/INITIAL_prp_context_refactor.md
**Archon Project**: 54726e9e-7c06-4eb4-8f20-0c674b720804

---

## Goal

Eliminate remaining context pollution through CLAUDE.md deduplication, pattern file compression (tutorial→reference card), security function extraction, and command optimization. Achieve 59% total context reduction (1,044→430 lines per command call) while preserving all functionality and 95.8%+ validation success rate.

**End State**:
- CLAUDE.md: 100 lines (74% reduction from 389 lines, zero README.md duplication)
- Pattern files: 120 lines each (68% reduction from 373-387 lines, 80%+ code density)
- Commands: 330 lines each (50% reduction from 655/663 lines, orchestration only)
- Security function: Extracted to shared pattern (single source of truth)
- Total context per command: 430 lines (59% reduction from 1,044 lines)

## Why

**Current Pain Points**:
- Context bloat: Current system (1,044 lines/command) is 9.7x larger than original baseline (107 lines)
- DRY violations: CLAUDE.md duplicates 60% of README.md content (234 lines wasted)
- Tutorial-style patterns: 373-387 line files with 40% code density (should be 80%+ reference cards)
- Function duplication: Identical 34-line security function in both commands (64 unique lines)
- Token waste: 614 unnecessary lines loaded per command call (59% of context)

**Business Value**:
- **3x faster context scanning**: Developers find patterns in seconds vs minutes
- **54% performance improvement**: Based on Anthropic context engineering research (compaction strategy)
- **95.8%+ reliability maintained**: All 23/24 validation criteria preserved
- **Parallel execution preserved**: Scoped directories and security checks intact
- **Maintainability**: Single source of truth (DRY principle) reduces update burden

## What

### Core Features

1. **CLAUDE.md Compression** (389→100 lines):
   - Remove 234 lines of README.md duplication (60% of content)
   - Replace with references: "See README.md for architecture details"
   - Preserve unique rules: Archon-first, PRP workflow, pattern references
   - Zero duplication validation (grep check passes)

2. **Pattern File Compression** (373-387→120 lines each):
   - Convert tutorial style to reference card style
   - Achieve 80%+ code snippet density (≤20% commentary)
   - Remove 121-line working examples (users see real code in commands)
   - Condense explanations to inline comments (12→3 lines per section)
   - Create "Field Reference" sections (eliminate repeated descriptions)

3. **Security Function Extraction** (66→44 lines net):
   - Extract duplicate function to `.claude/patterns/security-validation.md` (40 lines)
   - Condense inline versions (34→19 lines each)
   - Preserve all 5 security checks (whitelist, traversal, length, directory, injection)
   - Single source of truth for validation logic

4. **Command Optimization** (655/663→330 lines each):
   - Condense orchestration descriptions
   - Reference patterns instead of duplicating implementations
   - Preserve critical logic: security validation, scoped directories, Archon integration
   - Remove verbose phase descriptions (replace with terse summaries)

5. **Validation Preservation** (95.8%+ success rate):
   - All 23 passing criteria MUST still pass
   - 5-level validation after each phase (file size, duplication, pattern loading, functionality, token usage)
   - Iterative fix loops (max 5 attempts per failure)

### Success Criteria

**Quantitative** (all must pass):
- [ ] CLAUDE.md ≤120 lines (target 100)
- [ ] Pattern files ≤150 lines each (target 120)
- [ ] Commands ≤350 lines each (target 330)
- [ ] Total context ≤450 lines per command (target 430)
- [ ] 59%+ total reduction achieved (1,044→430 lines)
- [ ] 95.8%+ validation success rate maintained (23/24 criteria)

**Qualitative**:
- [ ] Pattern files feel like "cheat sheets" not tutorials
- [ ] CLAUDE.md is project rules only (zero architecture duplication)
- [ ] Commands are orchestration only (reference patterns, don't duplicate)
- [ ] Security function has single source of truth
- [ ] Developer feedback: "Faster to scan and reference"

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Progressive Disclosure & Context Engineering
- url: https://www.nngroup.com/articles/progressive-disclosure/
  sections:
    - "Core Definition" - Fundamental principle for reducing cognitive load
    - "Two-Level Maximum Rule" - Critical constraint (command→pattern, done)
    - "When to Use Progressive Disclosure" - Determines content placement
  why: Authoritative source on two-level disclosure maximum (going beyond 2 levels causes lost users)
  critical_gotchas:
    - "Designs that go beyond 2 levels typically have low usability"
    - Pattern files should NEVER reference other patterns (creates Level 3)
    - Must make progression from primary to secondary obvious

- url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  sections:
    - "Context as Finite Resource" - Core philosophy (context rot with n² relationships)
    - "Compaction Strategies" - Direct approach for 1,044→430 reduction
    - "Structured Note-Taking" - Pattern for extracting to separate files
    - "Sub-Agent Architectures" - Justification for pattern separation
  why: CRITICAL resource from Claude creators on context optimization (54% performance improvement, 84% token reduction)
  critical_gotchas:
    - Context rot happens gradually - requires periodic compression
    - Over-optimization can remove critical signals
    - "Smallest possible set of high-signal tokens that maximize likelihood of desired outcome"
    - Balance minimal tokens with preserving essential context

- url: https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md
  sections:
    - "Context is Everything" - What should be included
    - "Flexible Context Structuring" - Permission to create custom formats
    - "Context Window Optimization" - Techniques for maximizing information density
  why: Factor 3 directly applicable to markdown documentation compression
  critical_gotchas:
    - Don't rely solely on standard formats (create optimized structures)
    - Maximize information density (pack efficiently)
    - Custom tagging systems for efficient parsing

# MUST READ - DRY Principle & Single Source of Truth
- url: https://en.wikipedia.org/wiki/Don't_repeat_yourself
  sections:
    - "Definition" - Every piece of knowledge has single representation
    - "Scope" - Applies to documentation too
  why: CLAUDE.md violates DRY by duplicating 60% of README.md (234 lines)
  critical_gotchas:
    - Incidental duplication (similar syntax, different concepts) vs true duplication
    - Sandi Metz: "Duplication is far cheaper than the wrong abstraction"
    - Rule of Three: Wait for 3rd occurrence before extracting

- url: https://en.wikipedia.org/wiki/Single_source_of_truth
  sections:
    - "Data Centralization" - Master in only one place
  why: Architecture details live in README.md only, CLAUDE.md references them
  critical_gotchas:
    - Cross-referencing strategy: Link to canonical source with section anchors
    - Use relative paths (not absolute)

# MUST READ - Technical Writing Best Practices
- url: https://idratherbewriting.com/quickreferenceguides/
  sections:
    - "Quick Reference Guide Layouts" - Cheat sheet formatting patterns
    - "Code Snippet Density" - 80%+ code best practices
  why: Pattern files should follow reference card format (not tutorial format)
  critical_gotchas:
    - Minimal field descriptions (just enough to understand)
    - Copy-paste ready code blocks
    - No duplicate examples or variations

- url: https://www.codecademy.com/resources/cheatsheets/all
  sections:
    - "Cheat Sheet Examples" - Real-world high-density documentation
  why: Shows 80%+ code / ≤20% commentary ratio in practice
  critical_gotchas:
    - Quick accurate ready-to-use code snippets
    - Practical examples demonstrating real-world usage
    - Highlight and copy-paste workflow

# ESSENTIAL LOCAL FILES
- file: prps/prp_context_refactor/examples/README.md
  why: Comprehensive guide with usage instructions, pattern highlights
  pattern: Study before implementing - shows ACTUAL before/after with exact line counts
  critical: Contains "what to mimic/adapt/skip" for each compression pattern

- file: prps/prp_context_refactor/examples/example_claude_md_before_after.md
  why: Shows CLAUDE.md compression (389→100 lines, 74% reduction)
  pattern: DRY principle - identify and remove README.md duplicates
  critical: Demonstrates semantic duplication detection (not just string matching)

- file: prps/prp_context_refactor/examples/example_pattern_compression.md
  why: Shows pattern compression (373→120 lines, 68% reduction)
  pattern: Tutorial→reference card transformation (40%→79% code density)
  critical: 5 compression strategies (separator removal, section condensing, explanation→comments)

- file: prps/prp_context_refactor/examples/example_security_extraction.md
  why: Shows duplicate function extraction (66→44 lines net)
  pattern: Extract to shared pattern, condense inline versions
  critical: Preserve all 5 security checks (whitelist, traversal, length, directory, injection)

- file: prps/prp_context_refactor/examples/example_original_baseline.md
  why: Original 107-line baseline (context-engineering-intro template)
  pattern: Growth ratio analysis (9.7x current vs 4.0x proposed)
  critical: Context bloat happens gradually, requires periodic compression

- file: prps/prp_context_cleanup/execution/validation-report.md
  why: Previous refactoring validation results (23/24 criteria, 95.8% success)
  pattern: 5-level validation approach (file size, duplication, pattern loading, functionality, token usage)
  critical: Same validation gates must pass after this refactoring

- file: .claude/patterns/archon-workflow.md
  why: Current 373-line tutorial-style pattern (compression target)
  pattern: Health check, project management, task tracking
  critical: Must preserve graceful degradation (try/except for Archon failures)

- file: .claude/patterns/parallel-subagents.md
  why: Current 387-line tutorial-style pattern (compression target)
  pattern: Parallel Task() invocation, wait for all completion
  critical: Must preserve "All Task() calls in SINGLE response" requirement

- file: .claude/patterns/quality-gates.md
  why: Current 385-line tutorial-style pattern (compression target)
  pattern: Quality scoring (8+/10), validation loops (max 5 attempts)
  critical: Must preserve iterative fix approach

- file: .claude/commands/generate-prp.md
  why: Current 655-line command (50% compression target)
  pattern: Security function at lines 33-66 (extraction target)
  critical: Must preserve scoped directory creation (prps/{feature_name}/)

- file: .claude/commands/execute-prp.md
  why: Current 663-line command (50% compression target)
  pattern: Identical security function at lines 33-66 (extraction target)
  critical: Must preserve all validation gates and parallel execution
```

### Current Codebase Tree

```
.claude/
├── agents/                    # 12 subagent definitions (no changes)
├── commands/
│   ├── generate-prp.md        # 655 lines → TARGET: 330 lines
│   │   └── Lines 33-66: extract_feature_name() [DUPLICATE]
│   ├── execute-prp.md         # 663 lines → TARGET: 330 lines
│   │   └── Lines 33-66: extract_feature_name() [DUPLICATE]
│   └── [other commands]       # No changes
├── patterns/
│   ├── README.md              # 57 lines → UPDATE: Add security-validation.md entry
│   ├── archon-workflow.md     # 373 lines → TARGET: 120 lines
│   ├── parallel-subagents.md  # 387 lines → TARGET: 120 lines
│   ├── quality-gates.md       # 385 lines → TARGET: 120 lines
│   └── security-validation.md # NEW: 40 lines (extracted function)
└── templates/                 # No changes

CLAUDE.md                      # 389 lines → TARGET: 100 lines
README.md                      # 166 lines → NO CHANGES (user-facing)

prps/prp_context_refactor/
├── planning/                  # Research documents (no changes)
└── examples/                  # 4 examples + README.md (reference only)
```

### Desired Codebase Tree

```
.claude/
├── patterns/
│   ├── README.md              # 60 lines (+3 lines: new entry)
│   ├── archon-workflow.md     # 120 lines (-253 lines, 68% reduction)
│   ├── parallel-subagents.md  # 120 lines (-267 lines, 69% reduction)
│   ├── quality-gates.md       # 120 lines (-265 lines, 69% reduction)
│   └── security-validation.md # 40 lines (NEW)
├── commands/
│   ├── generate-prp.md        # 330 lines (-325 lines, 50% reduction)
│   └── execute-prp.md         # 330 lines (-333 lines, 50% reduction)

CLAUDE.md                      # 100 lines (-289 lines, 74% reduction)

**Total context per /generate-prp call**:
- Before: CLAUDE.md (389) + generate-prp.md (655) = 1,044 lines
- After: CLAUDE.md (100) + generate-prp.md (330) = 430 lines
- Reduction: 59% (614 lines saved)

**New Files**:
- .claude/patterns/security-validation.md (40 lines)
```

### Known Gotchas & Library Quirks

```python
# CRITICAL GOTCHA 1: Over-Compression Breaking Clarity
# Source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
# Risk: Removing too much commentary creates unusable abstractions

# ❌ WRONG - Over-compressed (lost critical context)
## Archon Health Check
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# ✅ RIGHT - Optimal compression (preserves essential context)
## Archon Health Check (ALWAYS FIRST)

# Check Archon availability before using features
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if not archon_available:
    # Graceful degradation - continue without Archon tracking
    project_id = None
    print("ℹ️ Archon unavailable - proceeding without project tracking")

# Why first? Prevents workflow failures if Archon unavailable.
# Returns: {"status": "healthy"} or raises exception.

# Compression checklist:
# ✅ Keep ALL security warnings (non-negotiable)
# ✅ Preserve copy-paste ready code snippets
# ✅ Include minimal "why" context (1-2 sentences)
# ✅ Retain critical anti-patterns
# ❌ Remove verbose explanations
# ❌ Cut duplicate examples (keep best one)

# Quality gate: Can a developer use this pattern without reading the original 373-line version?


# CRITICAL GOTCHA 2: Validation Regression (Breaking 95.8% Pass Rate)
# Source: prps/prp_context_cleanup/execution/validation-report.md
# Risk: Refactoring breaks existing functionality (23/24 criteria must still pass)

# ❌ WRONG - Removed security check during compression
def extract_feature_name(filepath: str) -> str:
    basename = filepath.split("/")[-1]
    return basename.replace("INITIAL_", "").replace(".md", "")
    # MISSING: All 5 security validations!

# ✅ RIGHT - Preserved all 5 security checks
def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """Safely extract feature name with strict validation."""
    # CHECK 1: Path traversal in full path
    if ".." in filepath:
        raise ValueError(f"Path traversal detected: {filepath}")

    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")
    if strip_prefix:
        feature = feature.replace(strip_prefix, "")

    # CHECK 2: Whitelist validation (only safe characters)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid feature name: '{feature}'")

    # CHECK 3: Length validation (prevent resource exhaustion)
    if len(feature) > 50:
        raise ValueError(f"Feature name too long")

    # CHECK 4: Directory traversal in feature name
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal detected: {feature}")

    # CHECK 5: Command injection prevention
    dangerous_chars = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(char in feature for char in dangerous_chars):
        raise ValueError(f"Dangerous characters detected")

    return feature

# Validation loop: Run 5-level validation after each phase
# Level 1: File sizes (wc -l checks)
# Level 2: Duplication (grep README content in CLAUDE.md)
# Level 3: Pattern loading (grep '@.claude/patterns' = 0 results)
# Level 4: Functionality (run /generate-prp on test)
# Level 5: Token usage (total lines ≤450)


# CRITICAL GOTCHA 3: Premature DRY Abstraction (Wrong Abstraction Worse Than Duplication)
# Source: https://stackoverflow.com/questions/17788738/is-violation-of-dry-principle-always-bad
# Risk: Removing incidental duplication (similar syntax, different concepts)

# ❌ WRONG - Forced unification creates complexity
def extract_feature_name(filepath: str, mode: str) -> str:
    if mode == "generate":
        feature = basename.replace("INITIAL_", "").replace(".md", "")
    elif mode == "execute":
        feature = basename.replace(".md", "")
    else:
        raise ValueError(f"Invalid mode: {mode}")
    # Now coupled! Changing one affects the other.

# ✅ RIGHT - Flexible parameter (same concept, different inputs)
def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """Safely extract feature name with strict validation.

    Args:
        filepath: Path to feature file
        strip_prefix: Optional prefix to remove (e.g., "INITIAL_")
    """
    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")

    if strip_prefix:
        feature = feature.replace(strip_prefix, "")

    # [5 security checks here...]
    return feature

# Usage:
# generate-prp.md: feature = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")
# execute-prp.md: feature = extract_feature_name(prp_path)

# Sandi Metz's Test: If unsure, prefer duplication. Easier to extract later than untangle wrong abstraction.


# CRITICAL GOTCHA 4: Three-Level Disclosure Violation (Lost User Syndrome)
# Source: https://www.nngroup.com/articles/progressive-disclosure/
# Risk: "Designs that go beyond 2 disclosure levels typically have low usability"

# ❌ WRONG - Three-level disclosure
# .claude/commands/generate-prp.md (Level 1)
# See .claude/patterns/parallel-subagents.md for implementation.
#
# .claude/patterns/parallel-subagents.md (Level 2)
# See .claude/patterns/task-invocation-details.md for syntax.
# ^^^ LEVEL 3! User is now lost.

# ✅ RIGHT - Two-level maximum (self-contained pattern)
# .claude/commands/generate-prp.md (Level 1)
# See .claude/patterns/parallel-subagents.md for implementation.
#
# .claude/patterns/parallel-subagents.md (Level 2 - SELF-CONTAINED)
# CRITICAL: All Task() calls in SINGLE response
# Task(subagent_type="prp-gen-codebase-researcher", ...)
# Task(subagent_type="prp-gen-documentation-hunter", ...)
# [Everything needed is HERE - no Level 3]

# Architecture rule: Patterns should NEVER reference other patterns. Only commands reference patterns.
# Detection: grep "See .claude/patterns" .claude/patterns/*.md → should return 0 results


# HIGH PRIORITY GOTCHA 5: Reference Fragility (Broken Cross-File Links)
# Source: Documentation maintenance best practices
# Risk: Cross-references break when files moved/renamed

# ❌ WRONG - Fragile references
# See README.md section "Current Architecture" for details.
# PROBLEM: If section renamed to "System Design", reference breaks silently

# ✅ RIGHT - Robust references
## Repository Overview
See README.md for full architecture, directory structure, and MCP server details.

**Key differences for Claude Code**:
- `.claude/` directory: Custom agents, commands, and patterns
- ARCHON-FIRST RULE: Use Archon MCP for all task management
- PRP workflow: /generate-prp and /execute-prp for feature implementation

# Checklist:
# ✅ Use relative paths (../README.md, not /absolute/path)
# ✅ Reference whole documents, not sections (more stable)
# ✅ Include fallback search terms if specific section referenced
# ✅ Test all references after file moves/renames


# HIGH PRIORITY GOTCHA 6: Token Budget Miscalculation (Missing Hidden Context)
# Source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
# Risk: Counting only explicit files but missing implicit context (tool descriptions, frontmatter)

# ❌ WRONG - Incomplete calculation
wc -l .claude/commands/generate-prp.md  # 330 lines
# "We're under 450! Success!"
# ACTUAL context loaded:
# - CLAUDE.md: 100 lines
# - generate-prp.md: 330 lines
# - Tool descriptions: 50 lines (implicit)
# - Frontmatter: 20 lines (implicit)
# TOTAL: 500 lines (OVER TARGET!)

# ✅ RIGHT - Complete calculation
claude_lines=$(wc -l < .claude/CLAUDE.md)                   # 100
command_lines=$(wc -l < .claude/commands/generate-prp.md)   # 330
implicit_lines=150  # Tool descriptions + frontmatter estimate

total=$((claude_lines + command_lines + implicit_lines))
echo "TOTAL CONTEXT: $total lines (target: ≤450)"

# Implicit context sources (often missed):
# - Tool descriptions (50-100 lines depending on enabled tools)
# - Agent frontmatter (20 lines × number of subagents invoked)
# - System prompts (varies)
# - MCP server metadata (if Archon enabled)


# HIGH PRIORITY GOTCHA 7: Pattern Loading Anti-Pattern (Defeating Progressive Disclosure)
# Source: Current validation passing (Level 3 check)
# Risk: Using @ syntax loads 120-373 lines PER PATTERN into context

# ❌ WRONG - Loading pattern into context
# @.claude/patterns/archon-workflow.md
# ^^^ This loads entire 120-line file into context!

# ✅ RIGHT - Documentation-style reference
# Health check pattern: See .claude/patterns/archon-workflow.md
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if not archon_available:
    # Graceful degradation
    project_id = None
    print("ℹ️ Archon unavailable - proceeding without tracking")

# Pattern usage:
# - Human reference: Developer reads pattern when confused
# - Copy-paste source: Developer copies code snippet
# - NOT machine-loaded: Claude doesn't load pattern files
#
# Quality gate: grep '@' .claude/commands/*.md | grep -v '#' → 0 results


# HIGH PRIORITY GOTCHA 8: Security Check Degradation (Subtle Weakening)
# Source: prps/prp_context_cleanup validation report
# Risk: Accidentally weakening validations during refactoring

# Security test cases (all must raise ValueError):
test_cases = [
    "../../etc/passwd",           # Path traversal
    "test; rm -rf /",             # Command injection
    "test$(whoami)",              # Command substitution
    "test`id`",                   # Backtick execution
    "test|cat /etc/passwd",       # Pipe injection
    "test\nmalicious",            # Newline injection
    "test/subdir",                # Directory traversal
    "a" * 51,                     # Length overflow
    "test@feature",               # Special character
]

# Valid cases (must succeed):
valid_cases = ["user_auth", "web-scraper", "apiClient123", "TEST_Feature-v2"]

# Copy original exactly: Use copy-paste, not manual retyping (prevents transcription errors)


# MEDIUM PRIORITY GOTCHA 9: README.md Duplication Detection Errors (False Negatives)
# Risk: Missing paraphrased duplicates (same meaning, different wording)

# ❌ WRONG - Only exact string matching
grep "Vibes is a Claude Code workspace" .claude/CLAUDE.md
# Misses: "Vibes workspace for Claude Code AI development"

# ✅ RIGHT - Semantic section comparison
# 1. Identify duplicate SECTIONS (not just exact strings)
grep "^##" README.md
grep "^##" .claude/CLAUDE.md

# 2. Compare section purposes (not exact wording):
# README.md: "## Current Architecture" → describes directory structure
# CLAUDE.md: "## Directory Structure" → SAME PURPOSE → semantic duplication!

# Target sections with high duplication:
# - Repository Overview (100% duplicate)
# - Directory Structure (100% duplicate)
# - MCP Server descriptions (95% duplicate)
# - Quick Start commands (100% duplicate)
# - Key Technologies (90% duplicate)


# MEDIUM PRIORITY GOTCHA 10: Scoped Directory Pattern Loss (Global Pollution Returns)
# Source: prps/prp_context_cleanup validation report
# Risk: Reverting to global directory pattern (breaks parallel execution)

# ❌ WRONG - Global directories
mkdir -p prps/research/
mkdir -p prps/examples/
# Multiple features write to SAME directories → conflicts!

# ✅ RIGHT - Scoped per-feature
mkdir -p prps/${feature_name}/planning
mkdir -p prps/${feature_name}/examples
# Each feature has OWN directories → no conflicts

# Why scoping matters:
# - Parallel execution: 2 PRPs can generate simultaneously
# - Easy cleanup: Delete entire prps/{feature}/ directory
# - Organization: All feature artifacts in one place

# Detection:
grep "mkdir -p prps/research" .claude/commands/*.md  # Should be 0 results
grep "mkdir -p prps/\${feature" .claude/commands/*.md  # Should find all


# MEDIUM PRIORITY GOTCHA 11: Archon Graceful Degradation Loss (Hard Failures)
# Source: .claude/patterns/archon-workflow.md
# Risk: Removing error handling causes crashes when Archon unavailable

# ❌ WRONG - No error handling
health = mcp__archon__health_check()  # If raises exception, entire command fails!
project = mcp__archon__manage_project("create", ...)

# ✅ RIGHT - Graceful degradation preserved
try:
    health = mcp__archon__health_check()
    archon_available = health["status"] == "healthy"
except Exception as e:
    archon_available = False
    print(f"ℹ️ Archon health check failed: {e}")

if archon_available:
    project = mcp__archon__manage_project("create", title=feature_name, ...)
    project_id = project["id"]
else:
    project_id = None  # Graceful fallback
    print("ℹ️ Archon unavailable - proceeding without project tracking")

# Critical: Never remove error handling or fallback logic during compression!


# MEDIUM PRIORITY GOTCHA 12: Pattern README Index Staleness
# Risk: Creating security-validation.md but forgetting to update patterns/README.md

# Detection:
for pattern in .claude/patterns/*.md; do
    basename=$(basename "$pattern")
    if [ "$basename" != "README.md" ]; then
        grep -q "$basename" .claude/patterns/README.md || echo "❌ MISSING: $basename"
    fi
done

# Update checklist when adding patterns:
# ✅ Create pattern file (.claude/patterns/new-pattern.md)
# ✅ Add row to README.md table (Need to... | See Pattern | Used By)
# ✅ Update pattern count (was 3, now 4)
# ✅ Reference pattern in relevant commands


# LOW PRIORITY GOTCHA 13: Inconsistent Compression Ratios
# Risk: One pattern at 95 lines, another at 145 lines (inconsistent experience)

# Acceptable variance: 110-130 lines (120±10)
# Concerning variance: 90-150 lines (requires review)

# If one pattern significantly shorter (95 lines): Check if critical content removed
# If one pattern significantly longer (145 lines): Check if more compression possible


# LOW PRIORITY GOTCHA 14: Comment Compression Over-Zealousness
# Risk: Removing ALL comments to maximize code density

# ❌ WRONG - No comments (what does this do?)
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# ✅ RIGHT - Minimal essential comments
# Check Archon availability before using features
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# Comment guidelines:
# ✅ Keep: Security warnings, gotcha alerts, "why" explanations
# ✅ Keep: Unusual syntax explanations, return value descriptions
# ❌ Remove: Obvious descriptions, redundant field docs
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Study Examples** (30-40 minutes):
   - Read `prps/prp_context_refactor/examples/README.md` (overview and patterns)
   - Read each example file (understand techniques)
   - Focus on "What to Mimic" sections (copy these patterns)
   - Note "What to Adapt" for customization

2. **Review Current State**:
   - Read current CLAUDE.md (identify README.md duplicates)
   - Read one pattern file (understand tutorial vs reference card)
   - Read security function in both commands (confirm duplication)
   - Read validation report (understand 23/24 passing criteria)

3. **Understand Success Criteria**:
   - File size targets (100, 120, 330 lines)
   - Total context target (≤450 lines per command)
   - Validation preservation (95.8%+ pass rate)
   - Quality standards (80%+ code density, zero duplication)

### Task List (Execute in Order)

```yaml
Task 1: Extract Security Function to Shared Pattern
RESPONSIBILITY: Eliminate 64 unique lines of duplication, create single source of truth

FILES TO CREATE:
  - .claude/patterns/security-validation.md (40 lines)

FILES TO MODIFY:
  - .claude/commands/generate-prp.md (lines 33-66 → condense to 19 lines)
  - .claude/commands/execute-prp.md (lines 33-66 → condense to 19 lines)
  - .claude/patterns/README.md (add new pattern entry)

PATTERN TO FOLLOW: prps/prp_context_refactor/examples/example_security_extraction.md

SPECIFIC STEPS:
  1. Copy extract_feature_name() function from generate-prp.md lines 33-66
  2. Create .claude/patterns/security-validation.md with:
     - Function definition (32 lines)
     - Usage examples (4 lines)
     - Security test cases (4 lines)
  3. Add strip_prefix parameter (enable both use cases)
  4. Preserve ALL 5 security checks:
     - Path traversal in full path (if ".." in filepath)
     - Whitelist validation (re.match r'^[a-zA-Z0-9_-]+$')
     - Length validation (len < 50)
     - Directory traversal in feature name (no .., /, \)
     - Command injection (no $, backtick, ;, &, |, >, <, newlines)
  5. Condense inline versions in both commands (keep executable, remove comments)
  6. Update .claude/patterns/README.md table:
     - Row: "Extract secure feature names | security-validation.md | All commands"

VALIDATION:
  - Security test cases pass (malicious inputs raise ValueError)
  - Valid inputs succeed (user_auth, web-scraper, etc.)
  - Both commands executable with condensed version
  - Pattern file has comprehensive docs (40 lines total)
  - Net savings: 15 lines per command when loaded

---

Task 2: Compress archon-workflow.md Pattern (373→120 lines)
RESPONSIBILITY: Convert tutorial style to reference card style (68% reduction, 79%+ code density)

FILES TO MODIFY:
  - .claude/patterns/archon-workflow.md (373 lines → 120 lines)

PATTERN TO FOLLOW: prps/prp_context_refactor/examples/example_pattern_compression.md

SPECIFIC STEPS:
  1. Move summary to TOP (line 1, not buried at line 327)
     - Pattern: "Archon MCP integration pattern (health check, project/task management, graceful degradation)"

  2. Remove 121-line "Complete Working Example" section
     - Users see real implementations in generate-prp.md and execute-prp.md
     - Keep only 4-5 core code snippets (health check, create project, update task, graceful fallback)

  3. Condense explanations to inline comments
     - Before: 12 lines of "Why this matters" prose
     - After: 3 lines of comments in code snippet
     - Example: "# Check Archon availability before using features"

  4. Create "Field Reference" section
     - Single table of field descriptions (eliminates repeated explanations)
     - Format: | Field | Type | Purpose | Example |

  5. Remove separator lines (save ~15 lines)
     - Delete "---" between sections
     - Use ## headers for separation

  6. Consolidate duplicate examples
     - Keep best example per pattern
     - Remove variations and edge cases (users can read official docs)

  7. Preserve critical content:
     - ✅ ALL security warnings
     - ✅ Graceful degradation logic (try/except)
     - ✅ Anti-patterns section
     - ✅ Copy-paste ready code snippets

VALIDATION:
  - File size ≤150 lines (target 120)
  - Code density ≥80% (count code lines vs prose lines)
  - Developer test: Can someone use this pattern without reading 373-line original?
  - All critical patterns preserved (health check, create project, update task)

---

Task 3: Compress parallel-subagents.md Pattern (387→120 lines)
RESPONSIBILITY: Convert tutorial style to reference card style (69% reduction, 79%+ code density)

FILES TO MODIFY:
  - .claude/patterns/parallel-subagents.md (387 lines → 120 lines)

PATTERN TO FOLLOW: Same as Task 2 (archon-workflow.md compression)

SPECIFIC STEPS:
  1. Move summary to TOP
  2. Remove working examples (users see real parallel invocations in generate-prp.md Phase 2)
  3. Condense explanations to inline comments
  4. Create "Field Reference" section for Task() parameters
  5. Remove separator lines
  6. Consolidate duplicate examples
  7. Preserve critical content:
     - ✅ "CRITICAL: All Task() calls in SINGLE response" warning
     - ✅ Wait-for-all-completion logic
     - ✅ Context passing requirements
     - ✅ Anti-pattern: Sequential execution when should be parallel

VALIDATION:
  - File size ≤150 lines (target 120)
  - Code density ≥80%
  - Parallel execution pattern clear and copy-paste ready
  - Critical "SINGLE response" requirement preserved

---

Task 4: Compress quality-gates.md Pattern (385→120 lines)
RESPONSIBILITY: Convert tutorial style to reference card style (69% reduction, 79%+ code density)

FILES TO MODIFY:
  - .claude/patterns/quality-gates.md (385 lines → 120 lines)

PATTERN TO FOLLOW: Same as Task 2 (archon-workflow.md compression)

SPECIFIC STEPS:
  1. Move summary to TOP
  2. Remove working examples (users see real quality scoring in prp-gen-assembler.md)
  3. Condense explanations to inline comments
  4. Create "Field Reference" section for quality metrics
  5. Remove separator lines
  6. Consolidate duplicate examples
  7. Preserve critical content:
     - ✅ 8+/10 minimum score requirement
     - ✅ Iterative fix loops (max 5 attempts)
     - ✅ Deduction reasoning format
     - ✅ Anti-pattern: Proceeding with <8/10 score

VALIDATION:
  - File size ≤150 lines (target 120)
  - Code density ≥80%
  - Quality scoring pattern clear (extract score, validate ≥8, iterate if needed)
  - Max 5 attempts limit preserved

---

Task 5: Compress CLAUDE.md (389→100 lines)
RESPONSIBILITY: Remove 234 lines of README.md duplication (74% reduction, zero duplication)

FILES TO MODIFY:
  - .claude/CLAUDE.md (389 lines → 100 lines)

PATTERN TO FOLLOW: prps/prp_context_refactor/examples/example_claude_md_before_after.md

SPECIFIC STEPS:
  1. Identify semantic duplicates (not just string matching)
     - Repository Overview section (lines 5-35) → README.md lines 1-35
     - Directory Structure section → README.md architecture
     - MCP Server details → README.md capabilities
     - Quick Start commands → README.md setup
     - Key Technologies → README.md tech stack

  2. Replace duplicated sections with references
     - Pattern: "See README.md for [topic]"
     - Add "Key differences for Claude Code:" subsection (CLAUDE-specific notes)

  3. Preserve unique project rules (100% unique content)
     - ✅ ARCHON-FIRST RULE (lines 90-104)
     - ✅ Archon Integration & Workflow section
     - ✅ Pattern Library reference (.claude/patterns/)
     - ✅ PRP-Driven Development section
     - ✅ Validation Loop Pattern
     - ✅ Development Patterns specific to Claude Code
     - ✅ Quality Standards

  4. Structure (target 100 lines):
     - Repository Overview: 5 lines (reference README.md + Claude-specific notes)
     - ARCHON-FIRST RULE: 15 lines (keep verbatim)
     - Archon Integration: 25 lines (task-driven workflow, RAG, tools)
     - Pattern Library: 10 lines (reference .claude/patterns/README.md)
     - PRP-Driven Development: 20 lines (workflow, philosophy, validation)
     - Development Patterns: 15 lines (reference .claude/patterns/)
     - Quality Standards: 10 lines (key principles)

  5. Use relative paths for references
     - ✅ "../README.md" not "/Users/jon/source/vibes/README.md"
     - ✅ ".claude/patterns/README.md" not absolute paths

VALIDATION:
  - File size ≤120 lines (target 100)
  - Zero README.md duplication: grep "Vibes is a Claude Code workspace" = 0 results
  - Zero architecture duplication: grep "Directory Structure" CLAUDE.md = 0 results (only reference)
  - All unique rules preserved (ARCHON-FIRST, PRP workflow, quality standards)
  - Semantic check: Compare section purposes (not exact wording)

---

Task 6: Optimize generate-prp.md Command (655→330 lines)
RESPONSIBILITY: Condense orchestration, reference patterns (50% reduction)

FILES TO MODIFY:
  - .claude/commands/generate-prp.md (655 lines → 330 lines)

PATTERN TO FOLLOW: Command optimization (orchestration only, reference patterns)

SPECIFIC STEPS:
  1. Replace security function with condensed version (34→19 lines)
     - Use condensed inline version from Task 1
     - Keep executable (no full docs)

  2. Condense phase descriptions
     - Before: "In this phase we analyze the INITIAL.md file to extract requirements..."
     - After: "Analyze INITIAL.md, extract requirements (see prp-gen-feature-analyzer.md)"

  3. Reference patterns instead of duplicating
     - Archon health check: Reference archon-workflow.md (don't duplicate 20 lines)
     - Parallel execution: Reference parallel-subagents.md (don't duplicate 30 lines)
     - Quality gates: Reference quality-gates.md (don't duplicate 25 lines)

  4. Remove verbose Archon update patterns
     - Keep: Essential Archon calls (health check, create project, update task status)
     - Remove: Repeated explanations of graceful degradation
     - Pattern: "See archon-workflow.md for Archon integration details"

  5. Condense subagent invocation sections
     - Before: 15 lines explaining context requirements
     - After: 5 lines showing Task() call with context dict

  6. Preserve critical logic (non-negotiable):
     - ✅ Security validation (condensed version from Task 1)
     - ✅ Scoped directory creation (prps/{feature_name}/planning, /examples)
     - ✅ Archon graceful degradation (try/except preserved)
     - ✅ Parallel Phase 2 execution (3 subagents simultaneously)
     - ✅ Quality gate enforcement (8+/10 minimum score)

VALIDATION:
  - File size ≤350 lines (target 330)
  - No pattern loading: grep '@.claude/patterns' = 0 results
  - Functionality preserved: /generate-prp prps/INITIAL_test.md succeeds
  - All 5 phases executable
  - Scoped directories created correctly

---

Task 7: Optimize execute-prp.md Command (663→330 lines)
RESPONSIBILITY: Condense orchestration, reference patterns (50% reduction)

FILES TO MODIFY:
  - .claude/commands/execute-prp.md (663 lines → 330 lines)

PATTERN TO FOLLOW: Same as Task 6 (generate-prp.md optimization)

SPECIFIC STEPS:
  1. Replace security function with condensed version (34→19 lines)
  2. Condense phase descriptions
  3. Reference patterns instead of duplicating
  4. Remove verbose Archon update patterns
  5. Condense subagent invocation sections
  6. Preserve critical logic:
     - ✅ Security validation (condensed version)
     - ✅ Scoped directory creation (prps/{feature_name}/execution)
     - ✅ Archon graceful degradation
     - ✅ Parallel task execution (dependency groups)
     - ✅ Validation iteration loops (max 5 attempts)
     - ✅ Test generation and validation gates

VALIDATION:
  - File size ≤350 lines (target 330)
  - No pattern loading: grep '@.claude/patterns' = 0 results
  - Functionality preserved: /execute-prp prps/test_feature.md succeeds
  - All 5 phases executable
  - Validation loops iterate on failures

---

Task 8: Comprehensive Validation (5 Levels)
RESPONSIBILITY: Verify all targets met, functionality preserved, 95.8%+ success rate maintained

VALIDATION GATES:

Level 1: File Size Validation
  wc -l .claude/CLAUDE.md                          # ≤120 lines (target 100)
  wc -l .claude/patterns/archon-workflow.md         # ≤150 lines (target 120)
  wc -l .claude/patterns/parallel-subagents.md      # ≤150 lines (target 120)
  wc -l .claude/patterns/quality-gates.md           # ≤150 lines (target 120)
  wc -l .claude/patterns/security-validation.md     # ≤50 lines (target 40)
  wc -l .claude/commands/generate-prp.md            # ≤350 lines (target 330)
  wc -l .claude/commands/execute-prp.md             # ≤350 lines (target 330)

Level 2: Duplication Check
  grep "Vibes is a Claude Code workspace" .claude/CLAUDE.md  # 0 results
  grep "Repository Overview" .claude/CLAUDE.md               # Only as section reference
  grep "Directory Structure" .claude/CLAUDE.md               # Only as section reference
  # Semantic check: No README.md content duplicated

Level 3: Pattern Loading Check
  grep '@.claude/patterns' .claude/commands/generate-prp.md  # 0 results
  grep '@.claude/patterns' .claude/commands/execute-prp.md   # 0 results
  # Documentation-style references only

Level 4: Functionality Test
  /generate-prp prps/INITIAL_test_context_refactor.md        # Must succeed
  # Verify:
  # - All 5 phases execute
  # - Research documents created
  # - Examples extracted
  # - PRP assembled with 8+/10 score
  # - No errors or crashes

Level 5: Token Usage Measurement
  claude_lines=$(wc -l < .claude/CLAUDE.md)                    # 100
  generate_lines=$(wc -l < .claude/commands/generate-prp.md)   # 330
  execute_lines=$(wc -l < .claude/commands/execute-prp.md)     # 330

  generate_total=$((claude_lines + generate_lines))            # 430
  execute_total=$((claude_lines + execute_lines))              # 430

  echo "Total context per /generate-prp: $generate_total lines (target: ≤450)"
  echo "Total context per /execute-prp: $execute_total lines (target: ≤450)"

  # Reduction calculation:
  original_generate=1044
  reduction_generate=$(( (original_generate - generate_total) * 100 / original_generate ))
  echo "Reduction: $reduction_generate% (target: ≥59%)"

ITERATION LOOP:
  - If any Level 1-5 check fails: Document failure, fix, re-validate
  - Max 5 fix attempts per failure
  - If 5 attempts exhausted: Escalate to user with detailed report

SUCCESS CRITERIA (all must pass):
  - [ ] All file size targets met (7 files)
  - [ ] Zero README.md duplication in CLAUDE.md
  - [ ] Zero pattern loading (@ syntax)
  - [ ] Functionality test succeeds
  - [ ] Total context ≤450 lines per command
  - [ ] 59%+ reduction achieved
  - [ ] All 23 previous validation criteria still pass (from prp_context_cleanup)
```

### Implementation Pseudocode

```python
# Task 1: Security Function Extraction
# Pattern: DRY principle - single source of truth

# Step 1: Create pattern file
def create_security_pattern():
    content = """
# Security Validation Pattern

## Feature Name Extraction (Path Traversal Prevention)

def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    '''Safely extract feature name with strict validation.

    Args:
        filepath: Path to feature file
        strip_prefix: Optional prefix to remove (e.g., "INITIAL_")

    Returns:
        Validated feature name (alphanumeric, hyphens, underscores only)

    Raises:
        ValueError: If validation fails (path traversal, injection, etc.)
    '''
    import re

    # CHECK 1: Path traversal in full path
    if ".." in filepath:
        raise ValueError(f"Path traversal detected in filepath: {filepath}")

    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")

    if strip_prefix:
        feature = feature.replace(strip_prefix, "")

    # CHECK 2: Whitelist validation (only safe characters)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(
            f"Invalid feature name: '{feature}'\\n"
            f"Must contain only: letters, numbers, hyphens, underscores"
        )

    # CHECK 3: Length validation (prevent resource exhaustion)
    if len(feature) > 50:
        raise ValueError(f"Feature name too long: {len(feature)} chars (max: 50)")

    # CHECK 4: Directory traversal in feature name
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal detected: {feature}")

    # CHECK 5: Command injection prevention
    dangerous_chars = ['$', '`', ';', '&', '|', '>', '<', '\\n', '\\r']
    if any(char in feature for char in dangerous_chars):
        raise ValueError(f"Dangerous characters detected: {feature}")

    return feature

## Usage Examples

# generate-prp.md
feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")

# execute-prp.md
feature_name = extract_feature_name(prp_path)

## Security Test Cases

# Must raise ValueError:
test_cases = ["../../etc/passwd", "test; rm -rf /", "test$(whoami)", ...]

# Must succeed:
valid_cases = ["user_auth", "web-scraper", "apiClient123"]
"""
    Write(".claude/patterns/security-validation.md", content)

# Step 2: Condense inline versions in commands
def condense_inline_version():
    # generate-prp.md: Replace lines 33-66 with:
    condensed = """
import re

def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    if ".." in filepath: raise ValueError(f"Path traversal: {filepath}")
    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")
    if strip_prefix: feature = feature.replace(strip_prefix, "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(f"Invalid: {feature}")
    if len(feature) > 50: raise ValueError(f"Too long: {len(feature)}")
    if ".." in feature or "/" in feature or "\\" in feature: raise ValueError(f"Traversal: {feature}")
    dangerous = ['$', '`', ';', '&', '|', '>', '<', '\\n', '\\r']
    if any(c in feature for c in dangerous): raise ValueError(f"Dangerous: {feature}")
    return feature

feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")
"""
    # 19 lines vs 34 original
    # Gotcha to avoid: Must preserve ALL 5 security checks


# Task 2-4: Pattern Compression
# Pattern: Tutorial→reference card transformation

def compress_pattern_file(pattern_file: str):
    # Step 1: Move summary to top
    summary = "Pattern summary (what it does, when to use, key gotchas)"

    # Step 2: Extract core snippets (4-5 examples)
    core_snippets = [
        ("Health Check", "health = mcp__archon__health_check()..."),
        ("Create Project", "project = mcp__archon__manage_project(...)"),
        ("Update Task", "mcp__archon__manage_task('update', ...)"),
        ("Graceful Fallback", "try/except with fallback logic"),
    ]

    # Step 3: Condense explanations to inline comments
    # Before: 12 lines of prose
    # After: 3 lines of comments in code

    # Step 4: Create field reference table
    field_reference = """
| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| project_id | str | Archon project UUID | "abc-123" |
| task_id | str | Archon task UUID | "task-456" |
| status | str | Task status | "doing" |
"""

    # Step 5: Remove separators (save 15 lines)
    # Delete "---" between sections

    # Step 6: Consolidate examples
    # Keep best example, remove variations

    # Step 7: Preserve critical content
    critical_content = [
        "Security warnings (non-negotiable)",
        "Graceful degradation logic",
        "Anti-patterns section",
        "Copy-paste ready snippets"
    ]

    # Target: 120 lines, 79%+ code density
    # Gotcha to avoid: Don't remove so much context that pattern becomes unusable


# Task 5: CLAUDE.md Compression
# Pattern: DRY principle - remove README.md duplication

def compress_claude_md():
    # Step 1: Identify semantic duplicates
    duplicates = {
        "Repository Overview": "README.md lines 1-35",
        "Directory Structure": "README.md architecture section",
        "MCP Servers": "README.md capabilities section",
        "Quick Start": "README.md setup section",
    }

    # Step 2: Replace with references
    new_overview = """
## Repository Overview

See README.md for full architecture, directory structure, and MCP server details.

**Key differences for Claude Code**:
- `.claude/` directory: Custom agents, commands, and patterns
- ARCHON-FIRST RULE: Use Archon MCP for all task management
- PRP workflow: /generate-prp and /execute-prp for feature implementation
"""

    # Step 3: Preserve unique rules (100 lines)
    unique_content = [
        "ARCHON-FIRST RULE (15 lines)",
        "Archon Integration & Workflow (25 lines)",
        "Pattern Library reference (10 lines)",
        "PRP-Driven Development (20 lines)",
        "Development Patterns (15 lines)",
        "Quality Standards (10 lines)",
    ]

    # Gotcha to avoid: Don't use absolute paths in references


# Task 6-7: Command Optimization
# Pattern: Orchestration only, reference patterns

def optimize_command(command_file: str):
    # Step 1: Replace security function (34→19 lines)
    # Use condensed inline version from Task 1

    # Step 2: Condense phase descriptions
    # Before: "In this phase we will..."
    # After: "Phase 1: Analyze INITIAL.md (see prp-gen-feature-analyzer.md)"

    # Step 3: Reference patterns
    archon_reference = "# See .claude/patterns/archon-workflow.md for Archon integration"
    parallel_reference = "# See .claude/patterns/parallel-subagents.md for parallel execution"

    # Step 4: Remove verbose Archon updates
    # Keep essential calls, remove repeated explanations

    # Step 5: Condense subagent invocations
    condensed_invocation = """
# Phase 2: Parallel Research (3 subagents simultaneously)
Task(subagent_type="prp-gen-codebase-researcher", context={...})
Task(subagent_type="prp-gen-documentation-hunter", context={...})
Task(subagent_type="prp-gen-example-curator", context={...})
"""

    # Step 6: Preserve critical logic
    critical_logic = [
        "Security validation (all 5 checks)",
        "Scoped directories (prps/{feature_name}/)",
        "Graceful degradation (try/except)",
        "Parallel execution or validation loops",
    ]

    # Target: 330 lines (50% reduction)
    # Gotcha to avoid: Don't remove error handling or security checks


# Task 8: Validation
# Pattern: 5-level validation with iteration loops

def validate_refactoring():
    results = {
        "level_1_file_sizes": check_file_sizes(),
        "level_2_duplication": check_duplication(),
        "level_3_pattern_loading": check_pattern_loading(),
        "level_4_functionality": test_functionality(),
        "level_5_token_usage": calculate_token_usage(),
    }

    # Iterate on failures (max 5 attempts)
    for level, result in results.items():
        if not result["passed"]:
            for attempt in range(1, 6):
                print(f"⚠️ {level} failed: {result['reason']}")
                print(f"Attempt {attempt}/5 to fix...")
                # Fix issue
                result = re_validate(level)
                if result["passed"]:
                    print(f"✅ {level} now passing")
                    break
            if not result["passed"]:
                raise ValidationError(f"{level} failed after 5 attempts")

    # Generate validation report
    generate_validation_report(results)
```

---

## Validation Loop

### Level 1: File Size Validation

```bash
# Check all file size targets
echo "=== Level 1: File Size Validation ==="

wc -l .claude/CLAUDE.md                          # Target: ≤120 (goal 100)
wc -l .claude/patterns/archon-workflow.md         # Target: ≤150 (goal 120)
wc -l .claude/patterns/parallel-subagents.md      # Target: ≤150 (goal 120)
wc -l .claude/patterns/quality-gates.md           # Target: ≤150 (goal 120)
wc -l .claude/patterns/security-validation.md     # Target: ≤50 (goal 40)
wc -l .claude/commands/generate-prp.md            # Target: ≤350 (goal 330)
wc -l .claude/commands/execute-prp.md             # Target: ≤350 (goal 330)

# Expected: All files at or below targets
# If over: Identify which file, compress further, re-validate
```

### Level 2: Duplication Check

```bash
# Check CLAUDE.md for README.md duplication
echo "=== Level 2: Duplication Check ==="

grep "Vibes is a Claude Code workspace" .claude/CLAUDE.md  # Expect: 0 results
grep "Repository Overview" .claude/CLAUDE.md               # Expect: Only section reference
grep "Directory Structure" .claude/CLAUDE.md               # Expect: Only section reference
grep "mcp-vibesbox-server" .claude/CLAUDE.md               # Expect: 0 results (in README only)

# Semantic check: Read CLAUDE.md sections, verify no README.md content duplicated
# Expected: Only references like "See README.md for architecture"
# If duplicates found: Remove and replace with reference, re-validate
```

### Level 3: Pattern Loading Check

```bash
# Check commands don't load patterns with @ syntax
echo "=== Level 3: Pattern Loading Check ==="

grep '@.claude/patterns' .claude/commands/generate-prp.md  # Expect: 0 results
grep '@.claude/patterns' .claude/commands/execute-prp.md   # Expect: 0 results

# Expected: No @ pattern loading (only documentation-style references)
# If found: Replace @ loads with references, re-validate
```

### Level 4: Functionality Test

```bash
# Test that commands still work after compression
echo "=== Level 4: Functionality Test ==="

# Create test INITIAL.md
cat > prps/INITIAL_test_context_refactor.md << 'EOF'
# Test Feature for Context Refactor Validation

Simple test feature to verify /generate-prp still works after compression.

**Goal**: Create a simple validation test.
**Why**: Ensure refactoring preserved functionality.
**What**: Generate PRP with all 5 phases.
EOF

# Run /generate-prp command
/generate-prp prps/INITIAL_test_context_refactor.md

# Verify success:
# - All 5 phases execute (Setup, Feature Analysis, Parallel Research, Gotcha Detection, Assembly)
# - Research documents created in prps/test_context_refactor/planning/
# - Examples extracted to prps/test_context_refactor/examples/
# - Final PRP created: prps/test_context_refactor.md
# - Quality score ≥8/10
# - No errors or crashes

# If failure: Debug which phase broke, fix, re-validate
```

### Level 5: Token Usage Measurement

```bash
# Calculate total context per command call
echo "=== Level 5: Token Usage Measurement ==="

claude_lines=$(wc -l < .claude/CLAUDE.md)                    # 100
generate_lines=$(wc -l < .claude/commands/generate-prp.md)   # 330
execute_lines=$(wc -l < .claude/commands/execute-prp.md)     # 330

generate_total=$((claude_lines + generate_lines))            # 430
execute_total=$((claude_lines + execute_lines))              # 430

echo "Total context per /generate-prp: $generate_total lines (target: ≤450)"
echo "Total context per /execute-prp: $execute_total lines (target: ≤450)"

# Calculate reduction percentage
original_generate=1044
original_execute=1052
reduction_generate=$(( (original_generate - generate_total) * 100 / original_generate ))
reduction_execute=$(( (original_execute - execute_total) * 100 / original_execute ))

echo "generate-prp reduction: $reduction_generate% (target: ≥59%)"
echo "execute-prp reduction: $reduction_execute% (target: ≥59%)"

# Expected: ≤450 lines per command, ≥59% reduction
# If over target: Identify which file(s) too large, compress further, re-validate
```

---

## Final Validation Checklist

**Quantitative Metrics** (all must pass):
- [ ] CLAUDE.md: ≤120 lines (actual: ___)
- [ ] archon-workflow.md: ≤150 lines (actual: ___)
- [ ] parallel-subagents.md: ≤150 lines (actual: ___)
- [ ] quality-gates.md: ≤150 lines (actual: ___)
- [ ] security-validation.md: ≤50 lines (actual: ___)
- [ ] generate-prp.md: ≤350 lines (actual: ___)
- [ ] execute-prp.md: ≤350 lines (actual: ___)
- [ ] Total context /generate-prp: ≤450 lines (actual: ___)
- [ ] Total context /execute-prp: ≤450 lines (actual: ___)
- [ ] Reduction percentage: ≥59% (actual: ___%)

**Duplication Checks**:
- [ ] CLAUDE.md has 0 README.md duplicates
- [ ] grep "Vibes is a Claude Code workspace" CLAUDE.md = 0 results
- [ ] Semantic check passed (no architecture duplication)

**Pattern Loading**:
- [ ] Commands use documentation-style references only (no @ loads)
- [ ] grep '@.claude/patterns' in commands = 0 results

**Functionality Preservation**:
- [ ] /generate-prp on test INITIAL.md succeeds
- [ ] All 5 phases execute without errors
- [ ] Research documents created correctly
- [ ] Examples extracted correctly
- [ ] Final PRP assembled with 8+/10 score
- [ ] Security validation works (all 5 checks)
- [ ] Scoped directories created correctly
- [ ] Archon graceful degradation works (try/except preserved)
- [ ] Parallel execution works (Phase 2 research)

**Code Quality**:
- [ ] Pattern files feel like "cheat sheets" not tutorials
- [ ] Code density in patterns ≥80%
- [ ] All security warnings preserved
- [ ] All anti-patterns sections preserved
- [ ] Copy-paste ready code snippets present
- [ ] Pattern README.md index updated (security-validation.md added)

**Validation Preservation** (from prp_context_cleanup):
- [ ] All 23 previously passing criteria still pass
- [ ] Validation success rate ≥95.8% (23/24 or 24/24)

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Grep-Driven DRY (Removing All String Matches)

**What it is**: Running `grep "common phrase" *.md` and removing every match without considering context.

**Why it's bad**:
- Destroys semantic meaning
- Removes necessary repetition (e.g., critical warnings repeated for emphasis)
- Creates incomplete references

**Better approach**:
```markdown
# Don't just search for "Vibes is a Claude Code workspace" and delete
# Ask: Is this the SAME information as README.md or different context?

# README.md (user-facing):
"Vibes is a Claude Code workspace for AI-assisted development"
→ Explains to new users what Vibes is

# CLAUDE.md (AI-facing):
"Vibes is a Claude Code workspace for AI-assisted development"
→ Orients Claude to the codebase
→ SAME purpose → TRUE duplication → can reference README

# Command documentation:
"Generate PRPs for Claude Code workspace features"
→ DIFFERENT purpose (task description) → NOT duplication → keep as-is
```

### Anti-Pattern 2: Hard-Coding File Paths (Breaking Portability)

**What it is**: Using absolute paths in cross-references: `/Users/jon/vibes/README.md` instead of relative paths.

**Why it's bad**:
- Breaks on other machines
- Breaks when project cloned
- Not portable across environments

**Better approach**:
```markdown
# ❌ WRONG
See /Users/jon/source/vibes/README.md for details
See C:\Users\developer\vibes\README.md for details

# ✅ RIGHT
See README.md for details
See ../README.md for details (from .claude/ directory)
See [README.md](../README.md) for details (Markdown link)
```

### Anti-Pattern 3: Inline Pattern Duplication (Defeating Extraction Purpose)

**What it is**: Extracting security function to pattern but still including full implementation inline in commands "for convenience."

**Why it's bad**:
- Negates DRY benefits
- Maintenance burden (update two places)
- Increases context (defeats compression)

**Better approach**:
```markdown
# ❌ WRONG
# .claude/patterns/security-validation.md: [34 lines of function]
# .claude/commands/generate-prp.md: [34 lines of same function "for convenience"]
# Total: 68 lines (duplication!)

# ✅ RIGHT
# .claude/patterns/security-validation.md: [34 lines of function]
# .claude/commands/generate-prp.md: [2 lines: reference + usage]
# Total: 36 lines (DRY principle)
```

### Anti-Pattern 4: Over-Compression (Removing Critical Context)

**What it is**: Aggressively removing commentary to hit line targets, creating unusable patterns.

**Why it's bad**:
- Patterns become cryptic
- Copy-paste fails (missing context)
- Developers waste time reverse-engineering

**Better approach**:
```python
# ❌ WRONG - Over-compressed (no context)
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# ✅ RIGHT - Optimal compression (preserves essential context)
# Check Archon availability before using features
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if not archon_available:
    # Graceful degradation
    project_id = None
    print("ℹ️ Archon unavailable - proceeding without tracking")

# Why first? Prevents workflow failures.
# Returns: {"status": "healthy"} or raises exception.
```

### Anti-Pattern 5: Three-Level Disclosure (Lost User Syndrome)

**What it is**: Creating pattern sub-files or nested references beyond command→pattern.

**Why it's bad**:
- Users lose track of hierarchy
- Exponential context growth
- Cognitive overload

**Better approach**:
```markdown
# ❌ WRONG - Three levels
# Command → Pattern → Sub-Pattern (TOO DEEP!)

# ✅ RIGHT - Two levels (self-contained)
# Command → Pattern (everything needed is here)
```

---

## Success Metrics

### Quantitative (all must pass):
- ✅ CLAUDE.md: 100 lines (74% reduction from 389)
- ✅ Pattern files: 360 lines total (68% reduction from 1,145)
- ✅ Commands: 660 lines total (50% reduction from 1,318)
- ✅ Total context: 430 lines per command (59% reduction from 1,044)
- ✅ Zero README.md duplication in CLAUDE.md
- ✅ Zero pattern loading (@ syntax)
- ✅ 95.8%+ validation success rate maintained

### Qualitative:
- ✅ Pattern files feel like "cheat sheets" (developer feedback)
- ✅ 80%+ code snippet density in patterns
- ✅ Faster to scan and reference (30 seconds vs 3 minutes)
- ✅ All security warnings preserved
- ✅ Copy-paste ready code snippets

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research docs thorough (3,600+ combined lines)
  - Feature analysis: 506 lines
  - Codebase patterns: 930 lines
  - Documentation links: 644 lines (8+ official sources)
  - Examples: 428 lines (4 before/after examples)
  - Gotchas: 1,100+ lines (14 documented gotchas)

- ✅ **Clear task breakdown**: 8 sequential tasks with specific steps
  - Task 1: Security extraction (40 lines pattern, condense to 19 inline)
  - Tasks 2-4: Pattern compression (373-387→120 lines each)
  - Task 5: CLAUDE.md compression (389→100 lines)
  - Tasks 6-7: Command optimization (655/663→330 lines each)
  - Task 8: 5-level validation (comprehensive checks)

- ✅ **Proven patterns**: 4 extracted examples from local codebase
  - Example 1: CLAUDE.md compression (DRY principle)
  - Example 2: Pattern compression (tutorial→reference card)
  - Example 3: Security extraction (single source of truth)
  - Example 4: Baseline comparison (9.7x→4.0x growth justified)

- ✅ **Validation strategy**: 5-level validation with iteration loops
  - Level 1: File size checks (7 files, hard limits)
  - Level 2: Duplication detection (semantic, not just grep)
  - Level 3: Pattern loading check (no @ syntax)
  - Level 4: Functionality test (/generate-prp on test INITIAL.md)
  - Level 5: Token usage calculation (complete count including implicit)

- ✅ **Error handling**: 14 documented gotchas with solutions
  - 4 critical (over-compression, validation regression, premature DRY, three-level disclosure)
  - 4 high priority (reference fragility, token miscalculation, pattern loading, security degradation)
  - 4 medium priority (duplication detection, scoped directories, graceful degradation, README index)
  - 2 low priority (compression ratios, comment compression)

**Deduction reasoning** (-1 point):
- **Gap 1**: No automated tools for 80/20 ratio validation (manual counting required)
  - **Mitigation**: Provide clear formula (count code lines vs prose lines), examples show target
- **Gap 2**: Progressive disclosure research from 2022 (pre-LLM era)
  - **Mitigation**: Combined with Anthropic 2025 context engineering guidance
- **Gap 3**: No markdown-specific compression guide exists
  - **Mitigation**: Apply general context engineering principles to markdown format

**Mitigations**:
- All examples show exact before/after line counts (no guessing needed)
- "What to Mimic" sections in examples provide copy-paste patterns
- 5-level validation with iteration loops catches issues early
- Comprehensive gotcha documentation prevents common mistakes
- Previous validation report (prp_context_cleanup) provides success template

**Why not 10/10**:
- Manual line counting required for code density validation (no automated tool)
- Some documentation sources pre-date LLMs (requires adaptation)
- Novel optimization pattern (no similar PRPs in Archon to reference)

**Confidence Level**: HIGH - This PRP provides implementer with everything needed for first-pass success with 95.8%+ validation pass rate.
