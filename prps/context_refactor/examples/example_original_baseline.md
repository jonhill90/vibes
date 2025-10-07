# Source: repos/context-engineering-intro/README.md and CLAUDE.md
# Lines: README.md (68 lines) + CLAUDE.md (39 lines) = 107 lines TOTAL
# Pattern: Original context engineering template baseline
# Extracted: 2025-10-05
# Relevance: 8/10

## The Original Baseline: 107 Lines Total

**Context Engineering Intro Repository** (by Cole Medin):
- **README.md**: 68 lines (project documentation)
- **CLAUDE.md**: 39 lines (AI assistant rules)
- **Total system context**: 107 lines

This is the ORIGINAL template that inspired the Vibes PRP system.

---

## README.md (68 lines) - Project Documentation

**Full original README.md structure:**

```markdown
# Context Engineering Template

A comprehensive template for getting started with Context Engineering - the discipline of engineering context for AI coding assistants so they have the information necessary to get the job done end to end.

> **Context Engineering is 10x better than prompt engineering and 100x better than vibe coding.**

## 🚀 Quick Start

```bash
# 1. Clone this template
git clone https://github.com/coleam00/Context-Engineering-Intro.git
cd Context-Engineering-Intro

# 2. Set up your project rules (optional - template provided)
# Edit CLAUDE.md to add your project-specific guidelines

# 3. Add examples (highly recommended)
# Place relevant code examples in the examples/ folder

# 4. Create your initial feature request
# Edit INITIAL.md with your feature requirements

# 5. Generate a comprehensive PRP (Product Requirements Prompt)
# In Claude Code, run:
/generate-prp INITIAL.md

# 6. Execute the PRP to implement your feature
# In Claude Code, run:
/execute-prp PRPs/your-feature-name.md
```

## 📚 Table of Contents

- [What is Context Engineering?](#what-is-context-engineering)
- [Template Structure](#template-structure)
- [Step-by-Step Guide](#step-by-step-guide)
- [Writing Effective INITIAL.md Files](#writing-effective-initialmd-files)
- [The PRP Workflow](#the-prp-workflow)
- [Using Examples Effectively](#using-examples-effectively)
- [Best Practices](#best-practices)

## What is Context Engineering?

Context Engineering represents a paradigm shift from traditional prompt engineering:

### Prompt Engineering vs Context Engineering

**Prompt Engineering:**
- Focuses on clever wording and specific phrasing
- Limited to how you phrase a task
- Like giving someone a sticky note

**Context Engineering:**
- A complete system for providing comprehensive context
- Includes documentation, examples, rules, patterns, and validation
- Like writing a full screenplay with all the details

### Why Context Engineering Matters

1. **Reduces AI Failures**: Most agent failures aren't model failures - they're context failures
2. **Ensures Consistency**: AI follows your project patterns and conventions
3. **Enables Complex Features**: AI can handle multi-step implementations with proper context
4. **Self-Correcting**: Validation loops allow AI to fix its own mistakes

[... additional sections explaining template structure, workflows, best practices ...]
```

**Key Characteristics**:
- Philosophy-driven (explains "why context engineering matters")
- Tutorial style (step-by-step guide)
- Beginner-friendly (extensive explanations)
- Self-contained (no external dependencies)

**Line count**: 68 lines (including code blocks, headers, explanations)

---

## CLAUDE.md (39 lines) - AI Assistant Rules

**Full original CLAUDE.md:**

```markdown
### 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Use venv_linux** (the virtual environment) whenever executing Python commands, including for unit tests.

### 🧱 Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
  For agents this looks like:
    - `agent.py` - Main agent definition and execution logic
    - `tools.py` - Tool functions used by the agent
    - `prompts.py` - System prompts
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use python_dotenv and load_env()** for environment variables.

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case

### ✅ Task Completion
- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a "Discovered During Work" section.

### 📎 Style & Conventions
- **Use Python** as the primary language.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- Use `FastAPI` for APIs and `SQLAlchemy` or `SQLModel` for ORM if applicable.
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

### 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.
```

**Key Characteristics**:
- Rule-based (bullet points, clear directives)
- Emoji section headers (visual organization)
- Specific conventions (PEP8, black, pydantic)
- Behavioral rules ("never assume", "always confirm")
- Concise (39 lines for entire AI guidance)

**Line count**: 39 lines (including emoji headers, code examples, behavioral rules)

---

## Total System Context: 107 Lines

**Breakdown**:
- README.md: 68 lines (project documentation)
- CLAUDE.md: 39 lines (AI assistant rules)
- **Total**: 107 lines

**This is the BASELINE for context engineering.**

---

## Current Vibes System: 1,318 Lines (12.3x larger)

**Current state**:
- README.md: ~200 lines (similar to original)
- CLAUDE.md: 389 lines (10x larger than original)
- Pattern files: 1,145 lines (NEW - didn't exist in original)
- Commands: 1,318 lines (NEW - didn't exist in original)
- **Total context per command call**: 1,044 lines (9.7x larger)

**Why the growth?**:
1. **Added complexity**: Archon integration, parallel execution, multi-phase workflows
2. **Added features**: 6 subagents, task management, quality gates
3. **Tutorial drift**: Patterns became tutorials (373-387 lines each vs reference cards)
4. **Duplication**: CLAUDE.md duplicates README.md (60% duplication)
5. **Security**: Added comprehensive validation (64 lines across 2 files)

**Growth is JUSTIFIED (partially)**:
- Original template: Simple 2-command workflow (/generate-prp, /execute-prp)
- Vibes system: Complex 6-phase multi-subagent parallel execution with Archon integration
- BUT: 12.3x growth is EXCESSIVE (should be ~3-4x for added complexity)

---

## Proposed Compressed System: 430 Lines (4x larger)

**After compression**:
- README.md: ~200 lines (unchanged - already lean)
- CLAUDE.md: 100 lines (2.5x larger than original 39, but includes Archon rules)
- Pattern files: 400 lines (3.3 lines each vs 1,145 current)
- Commands: 660 lines (330 each vs 1,318 current)
- **Total context per command call**: 430 lines (4x original baseline)

**Is 4x growth justified?**

**YES**, because:
1. **Archon integration**: 0 → 100 lines (health check, project/task management, graceful fallback)
2. **Parallel execution**: 0 → 50 lines (3-subagent coordination, performance math)
3. **Security validation**: 0 → 40 lines (5-level validation for production use)
4. **Quality gates**: 0 → 50 lines (8/10 scoring, validation loops)
5. **Multi-phase workflow**: 2 phases → 6 phases (3x complexity)

**Original**: Simple template for learning context engineering
**Vibes**: Production-ready system with enterprise features

**4x growth = reasonable** for 3x workflow complexity + 4 major new features.

---

## Key Lessons from Original Baseline

### 1. Separation of Concerns
- **README.md**: Project documentation (architecture, setup, philosophy)
- **CLAUDE.md**: AI assistant rules (conventions, behavior, standards)
- **No duplication**: Each file has unique purpose

**Current problem**: CLAUDE.md duplicates 60% of README.md content
**Solution**: Return to original separation (CLAUDE.md = rules only)

---

### 2. Concise Rule Format
Original CLAUDE.md (39 lines) used:
- Emoji section headers (visual organization)
- Bullet points (scannable)
- Bold key phrases ("Always", "Never")
- Minimal explanation (rules, not tutorials)

**Current problem**: CLAUDE.md became verbose documentation (389 lines)
**Solution**: Return to concise rule format (100 lines)

---

### 3. Progressive Disclosure
Original template:
- README.md: High-level overview (what/why)
- CLAUDE.md: Rules (how)
- Examples: Code patterns (implementation)

**Two-level maximum**: Overview → Rules (done)

**Current problem**: Added third level (commands → patterns), but patterns became tutorials
**Solution**: Keep three levels, but make patterns reference cards (not tutorials)

---

### 4. Copy-Paste Philosophy
Original examples/ folder:
- Actual code files
- README.md explaining what each demonstrates
- Copy-paste ready

**Current problem**: Pattern files are tutorials (read and learn), not reference cards (copy and use)
**Solution**: Convert patterns to reference cards (80%+ code snippets)

---

## Evolution Timeline

**2024**: Original context-engineering-intro template
- 107 lines total
- Simple 2-command workflow
- Learning-focused

**2025 Q1**: Vibes system development
- Added Archon integration
- Added parallel execution
- Added 6-phase workflow
- Added 6 subagents
- Grew to 1,318 lines (12.3x)

**2025 Q2**: Context cleanup (Phase 1)
- Validation report: 95.8% pass rate
- Identified bloat: 1,044 lines per command call
- Proposed compression: 59% reduction

**2025 Q3** (this PRP): Context refactor (Phase 2)
- Target: 430 lines per command call (4x original baseline)
- Justified by added complexity and features
- Return to original separation of concerns
- Maintain production-ready features

---

## Compression Strategy Informed by Original

### What to Preserve from Original
1. ✅ Concise CLAUDE.md (39 lines → target 100 lines for added rules)
2. ✅ Clear separation (README = docs, CLAUDE.md = rules)
3. ✅ Emoji organization (visual scanning)
4. ✅ Bold key phrases ("Always", "Never", "CRITICAL")
5. ✅ Copy-paste ready code

### What to Add (vs Original)
1. ➕ Archon integration rules (CRITICAL: Archon-first)
2. ➕ Pattern references (link to .claude/patterns/)
3. ➕ Multi-phase workflow guidance
4. ➕ Security validation patterns

### What to Remove (vs Current)
1. ❌ README.md duplication in CLAUDE.md (234 lines)
2. ❌ Tutorial-style patterns (convert to reference cards)
3. ❌ Verbose explanations (condensed to code comments)
4. ❌ Redundant examples (one example per pattern)

---

## Metrics Comparison

| Metric | Original (2024) | Current (2025 Q2) | Proposed (2025 Q3) | Growth Ratio |
|--------|----------------|-------------------|-------------------|--------------|
| **Total Context** | 107 lines | 1,044 lines | 430 lines | 4.0x |
| **CLAUDE.md** | 39 lines | 389 lines | 100 lines | 2.5x |
| **Pattern Files** | 0 lines | 1,145 lines | 400 lines | N/A |
| **Commands** | ~500 lines | 1,318 lines | 660 lines | 1.3x |
| **README.md** | 68 lines | ~200 lines | ~200 lines | 2.9x |

**Growth Analysis**:
- **4.0x total context**: Reasonable for added complexity
- **2.5x CLAUDE.md**: Justified by Archon rules + pattern references
- **1.3x commands**: Excellent (minimal growth despite 3x features)
- **2.9x README.md**: Justified by additional architecture

**Conclusion**: Proposed compression returns system to reasonable growth ratio (4x vs current 12.3x) while preserving all production features.

---

## What to Mimic from Original

1. **CLAUDE.md brevity**: 39 lines → 100 lines (not 389 lines)
2. **Emoji section headers**: Visual organization
3. **Bold key phrases**: "Always", "Never", "CRITICAL"
4. **Separation of concerns**: CLAUDE.md = rules only
5. **Copy-paste ready**: Code snippets, not explanations
6. **Progressive disclosure**: Two-level maximum (overview → implementation)

**The original template got it RIGHT.** Current system drifted. This PRP brings it back to original philosophy while preserving production features.
