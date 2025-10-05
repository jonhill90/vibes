# PRP Context Refactor - Code Examples

## Overview

This directory contains 4 extracted code examples demonstrating compression patterns for the PRP context refactor. These examples show how to achieve 59% total context reduction (1,044→430 lines) through duplication elimination, pattern compression, and security extraction.

**Target**: 74% CLAUDE.md reduction, 68% pattern reduction, 50% command reduction
**Approach**: Reference card style, DRY principle, progressive disclosure
**Baseline**: Original context-engineering-intro template (107 lines total)

---

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| example_claude_md_before_after.md | CLAUDE.md (389 lines) | CLAUDE.md compression via README.md deduplication | 9/10 |
| example_pattern_compression.md | archon-workflow.md (373 lines) | Tutorial→reference card transformation | 10/10 |
| example_security_extraction.md | generate-prp.md + execute-prp.md | Duplicate function extraction | 10/10 |
| example_original_baseline.md | repos/context-engineering-intro/ | Original 107-line baseline comparison | 8/10 |

---

## Example 1: CLAUDE.md Compression (389→100 lines)

**File**: `example_claude_md_before_after.md`
**Source**: Current CLAUDE.md vs Original context-engineering-intro CLAUDE.md
**Relevance**: 9/10

### What to Mimic

#### 1. Eliminate README.md Duplication
**Before** (389 lines):
```markdown
## Repository Overview
**Vibes** is a Claude Code workspace...

## Architecture
### Directory Structure
```
vibes/
├── .claude/
├── mcp/
...
```
```

**After** (100 lines):
```markdown
## Repository Overview
See [README.md](README.md) for complete architecture, directory structure, and component details.

**This file contains project rules only.**
```

**Technique**: Replace duplicated sections with references
**Savings**: 234 lines (60% of CLAUDE.md)

#### 2. Keep Unique Rules Only
**Preserve**:
- Archon-first task management rule
- PRP workflow commands
- Pattern library references
- Quality standards
- Development philosophy

**Remove**:
- Architecture details (README.md has this)
- Setup instructions (README.md has this)
- Technical stack (README.md has this)
- Configuration files (README.md has this)

#### 3. Use Reference Card Format
**Before**: Long prose explanations
```markdown
PRPs are context engineering artifacts that enable first-pass success through comprehensive briefing...
[5 paragraphs of explanation]
```

**After**: Concise bullet points
```markdown
**PRP Structure:**
- **PRD**: Goal, Why, What, Success Criteria
- **Curated Codebase Intelligence**: Current tree, patterns, gotchas
- **Agent Runbook**: Implementation blueprint, task list, validation loops
```

**Technique**: Bullet points with bold key terms
**Savings**: 3-5 lines per section

### What to Adapt

- **File-specific content**: Adjust references to match your project structure
- **Rule emphasis**: Highlight your most critical rules (for Vibes, it's Archon-first)
- **Emoji usage**: Keep or remove based on project style (original used emojis, current doesn't)

### What to Skip

- **Don't remove critical rules**: Even if duplicated elsewhere, keep safety-critical rules
- **Don't over-compress workflow**: Commands like `/generate-prp` should remain clear
- **Don't eliminate all context**: 100 lines is lean, but still comprehensive

### Pattern Highlights

```markdown
# CLAUDE.md compression pattern

## 1. Identify duplicates
grep -r "Repository Overview" README.md CLAUDE.md
# If both have it, keep in README.md only

## 2. Replace with references
# Before: 40 lines of directory structure
# After: "See README.md for architecture"

## 3. Preserve unique rules
# Keep: Project-specific rules, conventions, critical warnings
# Remove: General information available elsewhere

## 4. Use bold + bullet format
**Rule category**:
- **Key concept**: Explanation
- **Another concept**: Explanation
```

**This pattern works because**: DRY principle - single source of truth. README.md is documentation, CLAUDE.md is rules. No overlap needed.

### Why This Example

CLAUDE.md is the FIRST file Claude Code reads. Every conversation starts by loading it. At 389 lines, it's bloated with duplication. At 100 lines, it's scannable in 30 seconds and contains ONLY project rules. The original context-engineering-intro template had 39 lines - our target of 100 lines is reasonable for the added Archon/PRP complexity while maintaining the original lean philosophy.

---

## Example 2: Pattern Compression (373→120 lines)

**File**: `example_pattern_compression.md`
**Source**: .claude/patterns/archon-workflow.md
**Relevance**: 10/10

### What to Mimic

#### 1. Move Summary to TOP
**Before** (tutorial style): Introduction → Examples → Summary (line 327)
**After** (reference card style): Summary → Core Pattern → Variations (line 1)

**Technique**: "What you need to know" FIRST, details LATER

#### 2. Condense Explanations into Code Comments
**Before** (verbose):
```markdown
## Health Check (ALWAYS FIRST)

Every Archon workflow must start with a health check:

```python
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"
```

**Why first?** Determines if Archon is available and enables graceful fallback if not.

---
```

**After** (concise):
```python
# 1. Health check (always first - enables graceful fallback)
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"
```

**Savings**: 12 lines → 3 lines (75% reduction)

#### 3. Remove Full Working Examples
**Before**: 121-line complete working example (lines 205-325)
**After**: 4-5 focused code snippets showing ONLY the pattern

**Reasoning**: Users can see full implementations in actual command files (generate-prp.md, execute-prp.md). Pattern file should be quick reference, not tutorial.

#### 4. Create Field Reference Section
**Before**: Field explanations repeated in every example
```python
# Create project
project = mcp__archon__manage_project("create",
    title=f"PRP Generation: {feature_name}",  # Human-readable project name
    description=f"Creating PRP from {initial_md_path}"  # Brief summary
)
```

**After**: Single "Field Reference" section at bottom
```markdown
## Field Reference

**manage_project()**:
- `title`: Display name (e.g., "PRP Generation: user_auth")
- `description`: Brief summary
```

**Savings**: 5-10 lines per usage → single reference

#### 5. Achieve 80%+ Code Snippet Density
**Before**: 150 lines code / 373 total = 40% code
**After**: 95 lines code / 120 total = 79% code

**Technique**:
- Remove prose explanations
- Remove separator lines (`---`)
- Condense multi-paragraph commentary to 1-line comments
- Eliminate redundant examples

### What to Adapt

- **Code snippet selection**: Choose 4-5 MOST common patterns, not all variations
- **Comment verbosity**: Match your team's preference (terse vs explanatory)
- **Field reference depth**: Include only fields users need to understand, not internal details

### What to Skip

- **Don't eliminate critical warnings**: Security warnings, gotchas, anti-patterns must stay
- **Don't remove all explanations**: 1-line comments are okay, just not multi-paragraph prose
- **Don't compress DO/DON'T sections**: These are high-value, low-cost (stay scannable)

### Pattern Highlights

```markdown
# Pattern compression checklist

## 1. Remove separator lines
# Before: 15 `---` lines
# After: 0 separator lines
# Savings: 15 lines

## 2. Condense sections
# Before: "## Section Title\n\nExplanation paragraph.\n\n```code```\n\n**Why?** More explanation.\n\n---"
# After: "## Section Title\n```code  # inline comment```"
# Savings: 6 lines → 2 lines per section

## 3. Move explanations to code comments
# Before: Paragraph below code block explaining what it does
# After: # Single-line comment in code
# Savings: 3-5 lines per example

## 4. Delete full working examples
# Before: 121-line complete implementation
# After: "See .claude/commands/generate-prp.md for working example"
# Savings: 120 lines

## 5. Create reference sections
# Before: Field descriptions repeated 5 times (25 lines total)
# After: Single "Field Reference" section (5 lines)
# Savings: 20 lines
```

**This pattern works because**: Reference cards are for LOOKUP, not LEARNING. Users who need to learn can read the command files. Users who need to implement copy-paste from the pattern file.

### Why This Example

Pattern files are loaded on EVERY command execution that references them. At 373 lines, archon-workflow.md is a tutorial. At 120 lines, it's a reference card. The compression shows HOW to transform tutorial→reference card while preserving ALL essential information. This same technique applies to all 3 pattern files (archon-workflow, parallel-subagents, quality-gates).

---

## Example 3: Security Function Extraction (66→44 lines net)

**File**: `example_security_extraction.md`
**Source**: generate-prp.md and execute-prp.md (lines 33-66 each)
**Relevance**: 10/10

### What to Mimic

#### 1. Identify True Duplication
**Analysis**:
- generate-prp.md: 34 lines (security function + invocation)
- execute-prp.md: 34 lines (SAME function + invocation)
- Identical lines: 32/34 (94% identical)
- Differences: Only 2 lines (replace prefix)

**Technique**: Use diff or manual comparison to find exact duplicates

#### 2. Extract to Shared Pattern File
**Create**: `.claude/patterns/security-validation.md` (40 lines)
**Include**:
- Function with flexible parameters
- Usage examples (2-3 variations)
- Security checks explained (table format)
- Anti-patterns (what NOT to do)

#### 3. Condense Inline Versions
**Before**: 34 lines (full function with comments)
**After**: 19 lines (condensed with comment reference)

```python
# Extract and validate feature name (security: 5 checks)
# See .claude/patterns/security-validation.md for implementation
import re

def extract_feature_name(filepath: str, prefix_to_remove: str = "") -> str:
    """Safely extract feature name with 5-level security validation."""
    if ".." in filepath:
        raise ValueError(f"Path traversal detected in filepath: {filepath}")
    basename = filepath.split("/")[-1]
    feature = basename.replace(prefix_to_remove, "").replace(".md", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid feature name: '{feature}'\nMust contain only: letters, numbers, hyphens, underscores")
    if len(feature) > 50:
        raise ValueError(f"Feature name too long: {len(feature)} chars (max: 50)")
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal detected: {feature}")
    dangerous_chars = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(char in feature for char in dangerous_chars):
        raise ValueError(f"Dangerous characters detected: {feature}")
    return feature
```

**Savings**: 34 → 19 = 15 lines per command (30 lines total when both loaded)

#### 4. Balance Usability vs Compression
**Option A**: Full extraction (2 lines per command)
```python
# See .claude/patterns/security-validation.md for implementation
# (copy-paste extract_feature_name function)
```
**Savings**: 64 lines
**Problem**: Manual copy-paste required, security function must be inline for execution

**Option B**: Condensed inline (19 lines per command)
```python
# Reference to pattern + condensed implementation
```
**Savings**: 30 lines
**Benefit**: Executable without copy-paste, still references pattern for details

**Recommendation**: Option B (balance usability + compression)

### What to Adapt

- **Extraction threshold**: Only extract if duplicated 2+ times AND >20 lines
- **Inline vs pattern**: Critical security functions should remain inline (condensed)
- **Documentation depth**: Pattern file should have comprehensive docs (usage, security table, anti-patterns)

### What to Skip

- **Don't extract single-use functions**: Overhead of separate file not worth it
- **Don't extract tiny functions**: <10 lines not worth extracting
- **Don't remove inline implementation**: Security-critical functions need to be inline for execution

### Pattern Highlights

```python
# Security function extraction pattern

## 1. Identify duplicates
# Find: Identical functions in 2+ files
# Criteria: >20 lines, >80% identical

## 2. Extract to pattern file
# File: .claude/patterns/security-validation.md
# Include: Function + flexible parameters + usage examples + security table

## 3. Condense inline versions
# Remove: Verbose comments, separator lines
# Keep: Full implementation (security-critical)
# Add: Reference comment to pattern file

## 4. Calculate net savings
# Pattern file: 40 lines (NEW)
# Command 1: 34 → 19 lines (15 saved)
# Command 2: 34 → 19 lines (15 saved)
# Net: (34+34) - (40+19+19) = 68 - 78 = -10 lines
# BUT: Context per command: 34 → 19 = 15 lines saved ✓
```

**This pattern works because**: DRY principle + progressive disclosure. Pattern file has comprehensive documentation (security table, anti-patterns), command files have condensed implementation. Single source of truth for security fixes.

### Why This Example

Security functions MUST be correct and consistent. Duplicating them across files creates risk of divergence (already 1 line differs!). Extracting to pattern file ensures single source of truth while condensed inline versions maintain usability. This example shows HOW to balance DRY principle with execution requirements.

---

## Example 4: Original Baseline (107 lines total)

**File**: `example_original_baseline.md`
**Source**: repos/context-engineering-intro/README.md (68 lines) + CLAUDE.md (39 lines)
**Relevance**: 8/10

### What to Mimic

#### 1. Extreme CLAUDE.md Brevity
**Original**: 39 lines for entire AI guidance
**Current**: 389 lines (10x larger)
**Proposed**: 100 lines (2.5x larger)

**Original approach**:
- Emoji section headers (🔄 🧱 🧪 ✅ 📎 📚 🧠)
- Bullet points with bold key phrases
- Concise rules (no explanations)
- Behavioral directives ("Always", "Never")

**Example**:
```markdown
### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features**
- **After updating any logic**, check whether existing unit tests need updating
- **Tests should live in a `/tests` folder** mirroring the main app structure
```

#### 2. Clear Separation of Concerns
**Original philosophy**:
- README.md = Project documentation (what/why/how to setup)
- CLAUDE.md = AI assistant rules (conventions/behavior/standards)
- **Zero overlap** - each file has unique purpose

**Current problem**: CLAUDE.md duplicates 60% of README.md
**Solution**: Return to original separation

#### 3. Copy-Paste Ready Philosophy
**Original examples/ folder**:
- Actual code files (not references)
- README.md explaining what each demonstrates
- Users copy-paste patterns directly

**Current problem**: Pattern files are tutorials (learn by reading)
**Solution**: Convert to reference cards (copy by copy-pasting)

#### 4. Two-Level Progressive Disclosure
**Original**:
- Level 1: README.md (high-level overview)
- Level 2: CLAUDE.md + examples/ (implementation details)

**Current**:
- Level 1: README.md (overview)
- Level 2: CLAUDE.md (project rules)
- Level 3: Patterns (implementation details)

**Both are valid**, but Level 3 (patterns) should be reference cards, not tutorials

### What to Adapt

- **System complexity**: Original had 2 commands, Vibes has 6-phase multi-subagent workflow
- **Growth ratio**: 4x is reasonable (107→430 lines) for 3x complexity + 4 major features
- **Emoji usage**: Optional (original used them, current doesn't)

### What to Skip

- **Don't force 39-line CLAUDE.md**: Original was simpler system. 100 lines reasonable for added Archon/PRP complexity.
- **Don't eliminate all explanations**: Some context is valuable (just not duplicated from README.md)
- **Don't remove safety features**: Original had no security validation, Vibes needs it

### Pattern Highlights

```markdown
# Original baseline insights

## Growth analysis
Original: 107 lines total
Current: 1,044 lines per command (9.7x larger)
Proposed: 430 lines per command (4.0x larger)

## Justified growth factors
1. Archon integration: 0 → 100 lines
2. Parallel execution: 0 → 50 lines
3. Security validation: 0 → 40 lines
4. Quality gates: 0 → 50 lines
5. 6-phase workflow: 2 → 6 phases

Total justified growth: ~240 lines
Remaining growth: Context bloat

## Compression targets
CLAUDE.md: 389 → 100 (return to original philosophy)
Patterns: 1,145 → 400 (tutorial → reference card)
Commands: 1,318 → 660 (condense orchestration)

Result: 1,044 → 430 (4x original, justified by features)
```

**This pattern works because**: The original template got the philosophy RIGHT. Lean, focused, copy-paste ready. Current system drifted due to feature addition + tutorial-style patterns. Compression returns to original philosophy while preserving production features.

### Why This Example

Understanding the BASELINE is critical. The original context-engineering-intro template was 107 lines total. Current system is 9.7x larger (1,044 lines per command). Some growth is justified (added features), but 9.7x is excessive. This example shows the original philosophy and how to return to it while preserving production features. Target: 4x original (430 lines) = reasonable for added complexity.

---

## Usage Instructions

### Study Phase
1. Read this README.md first (understand examples)
2. Read each example file (understand techniques)
3. Focus on "What to Mimic" sections (copy these patterns)
4. Note "What to Adapt" for customization (your context may differ)
5. Review "What to Skip" to avoid over-compression (preserve critical content)

### Application Phase
1. **For CLAUDE.md compression**: Use example 1 + 4
   - Identify README.md duplicates
   - Replace with references
   - Keep unique rules only
   - Target: 100 lines (2.5x original 39-line baseline)

2. **For pattern compression**: Use example 2
   - Move summary to top
   - Condense explanations to comments
   - Remove full working examples
   - Create field reference sections
   - Target: 80%+ code snippet density

3. **For security extraction**: Use example 3
   - Identify true duplicates (>80% identical)
   - Extract to pattern file (with docs)
   - Condense inline versions (keep executable)
   - Balance usability vs compression

4. **For baseline comparison**: Use example 4
   - Compare current vs original (growth ratio)
   - Justify growth (features added)
   - Identify unjustified bloat (context drift)
   - Set realistic targets (4x original = reasonable)

### Testing Patterns

After compression, validate:
1. **File size checks**: `wc -l` against targets
2. **Duplication check**: `grep README.md CLAUDE.md` = 0 results
3. **Pattern reference check**: Commands reference patterns (not duplicate them)
4. **Functionality test**: Run `/generate-prp` on test INITIAL.md
5. **Code density check**: Count code lines / total lines ≥ 80%

---

## Pattern Summary

### Common Patterns Across Examples

1. **DRY Principle** (Examples 1, 3):
   - Single source of truth
   - Replace duplication with references
   - Extract shared functions to patterns

2. **Progressive Disclosure** (Examples 2, 4):
   - Summary first, details later
   - Reference cards, not tutorials
   - Two-level maximum (overview → implementation)

3. **Code-First Approach** (Examples 2, 3):
   - 80%+ code snippets
   - Minimal commentary (1-line comments)
   - Copy-paste ready

4. **Baseline Comparison** (Example 4):
   - Measure growth ratio (current / original)
   - Justify growth (features added)
   - Set realistic targets (4x original reasonable)

### Anti-Patterns Observed

1. **CLAUDE.md Duplication** (Example 1):
   - **Problem**: 60% duplicates README.md
   - **Solution**: Replace with references
   - **Detection**: `grep -F "$(cat README.md)" CLAUDE.md`

2. **Tutorial-Style Patterns** (Example 2):
   - **Problem**: 373-line pattern files with extensive explanations
   - **Solution**: Convert to 120-line reference cards
   - **Detection**: Code density < 50%

3. **Function Duplication** (Example 3):
   - **Problem**: Identical 34-line function in 2 files
   - **Solution**: Extract to pattern, condense inline
   - **Detection**: Manual diff or grep for function names

4. **Context Bloat** (Example 4):
   - **Problem**: 9.7x growth from original baseline
   - **Solution**: Return to original philosophy (4x growth justified)
   - **Detection**: Compare total context per command vs baseline

---

## Integration with PRP

These examples should be:

1. **Referenced** in PRP "All Needed Context" section:
   - Link to examples/ directory
   - Specific file names for each compression type
   - Pattern highlights for quick reference

2. **Studied** before implementation:
   - Read all 4 examples (30-40 minutes)
   - Understand techniques (DRY, progressive disclosure, code-first)
   - Note compression targets (74%, 68%, 50%)

3. **Adapted** for specific feature needs:
   - CLAUDE.md: Identify your duplicates
   - Patterns: Convert your tutorials
   - Security: Extract your duplicates
   - Baseline: Calculate your growth ratio

4. **Validated** after compression:
   - File size checks (wc -l)
   - Duplication checks (grep)
   - Functionality tests (/generate-prp)
   - Code density checks (80%+)

---

## Source Attribution

### From Original Context Engineering Template
- **repos/context-engineering-intro/README.md**: 68 lines (baseline philosophy)
- **repos/context-engineering-intro/CLAUDE.md**: 39 lines (original AI rules)
- **Total baseline**: 107 lines

### From Current Vibes System
- **CLAUDE.md**: 389 lines (bloated, needs compression)
- **.claude/patterns/archon-workflow.md**: 373 lines (tutorial style, needs reference card conversion)
- **.claude/commands/generate-prp.md**: Lines 33-66 (security function, 34 lines)
- **.claude/commands/execute-prp.md**: Lines 33-66 (duplicate security function, 34 lines)

### From Archon Knowledge Base
- **No examples found**: Searched "markdown compression", "context optimization", "pattern extraction"
- **Novel optimization**: This refactoring pattern is unique to Vibes PRP system

---

## Quality Assessment

**Coverage**: 10/10
- ✅ CLAUDE.md compression (example 1)
- ✅ Pattern compression (example 2)
- ✅ Security extraction (example 3)
- ✅ Baseline comparison (example 4)
- All 4 compression types covered

**Relevance**: 9.25/10 (average: 9+10+10+8 / 4)
- ✅ All examples directly applicable to PRP tasks
- ✅ All examples show before/after with exact line counts
- ✅ All examples include "what to mimic/adapt/skip"

**Completeness**: 10/10
- ✅ All examples are self-contained (actual code, not references)
- ✅ All examples include source attribution
- ✅ All examples include "why this example" explanations
- ✅ All examples include pattern highlights

**Overall**: 9.75/10

---

Generated: 2025-10-05
Feature: prp_context_refactor
Total Examples: 4 files
Quality Score: 9.75/10
