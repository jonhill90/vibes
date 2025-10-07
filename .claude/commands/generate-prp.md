# Create PRP

Orchestrates PRP generation from INITIAL.md: a multi-subagent system that creates comprehensive, implementation-ready PRPs through systematic research and analysis.

## Feature file: $ARGUMENTS

Generate a complete PRP with thorough research using a 5-phase multi-subagent approach. Ensure context is comprehensive to enable self-validation and first-pass implementation success.

## The 5-Phase Workflow

### Phase 0: Setup & Initialization (YOU handle this)

**Immediate**: Read INITIAL.md → Extract feature name → Create directories → Check Archon → Phase 1 (no user interaction)

```python
# 1. Read INITIAL.md
initial_md_path = "$ARGUMENTS"
initial_content = Read(initial_md_path)

# 2. Extract and validate feature name (SECURITY: 6 levels of validation)
# See .claude/patterns/security-validation.md for details
import re

def extract_feature_name(filepath: str, strip_prefix: str = None, validate_no_redundant: bool = True) -> str:
    # Whitelist of allowed prefixes (security enhancement)
    ALLOWED_PREFIXES = {"INITIAL_", "EXAMPLE_"}

    if ".." in filepath: raise ValueError(f"Path traversal: {filepath}")
    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")
    # CRITICAL: Use removeprefix() instead of replace() to only strip leading prefix
    # replace() removes ALL occurrences (e.g., "INITIAL_INITIAL_test" -> "test")
    # removeprefix() only removes from start (e.g., "INITIAL_INITIAL_test" -> "INITIAL_test")
    # See: PEP 616 (https://peps.python.org/pep-0616/) for rationale
    if strip_prefix:
        if strip_prefix not in ALLOWED_PREFIXES:
            raise ValueError(
                f"Invalid strip_prefix: '{strip_prefix}'\n"
                f"Allowed prefixes: {', '.join(ALLOWED_PREFIXES)}\n"
                f"Never use 'prp_' as strip_prefix"
            )
        feature = feature.removeprefix(strip_prefix)
        if not feature:
            raise ValueError(
                f"Empty feature name after stripping prefix '{strip_prefix}'\n"
                f"File: {filepath}\n"
                f"Fix: Rename file with actual feature name after prefix"
            )
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(f"Invalid: {feature}")
    if len(feature) > 50: raise ValueError(f"Too long: {len(feature)}")
    if ".." in feature or "/" in feature or "\\" in feature: raise ValueError(f"Traversal: {feature}")
    dangerous = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(c in feature for c in dangerous): raise ValueError(f"Dangerous chars: {feature}")
    # Level 6: Redundant prefix validation (strict enforcement for new PRPs)
    # This prevents creating new PRPs with prp_ prefix (e.g., prps/prp_feature.md)
    # Fail immediately - no try/except wrapper to ensure violations are caught early
    if validate_no_redundant and feature.startswith("prp_"):
        raise ValueError(
            f"❌ Redundant 'prp_' prefix detected: '{feature}'\n"
            f"\n"
            f"PROBLEM: Files are in prps/ directory - prefix is redundant\n"
            f"EXPECTED: '{feature.removeprefix('prp_')}'\n"
            f"\n"
            f"RESOLUTION:\n"
            f"Rename: prps/{feature}.md → prps/{feature.removeprefix('prp_')}.md\n"
            f"\n"
            f"See: .claude/conventions/prp-naming.md for naming rules"
        )
    return feature

# Strict validation for NEW PRPs - reject prp_ prefix immediately (no try/except)
# This enforces naming convention from the start of PRP generation workflow
feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_", validate_no_redundant=True)

# 3. Create scoped directories (per-feature, not global)
Bash(f"mkdir -p prps/{feature_name}/planning")
Bash(f"mkdir -p prps/{feature_name}/examples")

# 4. Archon setup (see .claude/patterns/archon-workflow.md for details)
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if archon_available:
    project = mcp__archon__manage_project("create",
        title=f"PRP Generation: {feature_name}",
        description=f"Creating PRP from {initial_md_path}")
    project_id = project["project"]["id"]

    task_ids = []
    for title, assignee, order in [
        ("Phase 1: Feature Analysis", "prp-gen-feature-analyzer", 100),
        ("Phase 2A: Codebase Research", "prp-gen-codebase-researcher", 90),
        ("Phase 2B: Documentation Hunt", "prp-gen-documentation-hunter", 85),
        ("Phase 2C: Example Curation", "prp-gen-example-curator", 80),
        ("Phase 3: Gotcha Detection", "prp-gen-gotcha-detective", 75),
        ("Phase 4: PRP Assembly", "prp-gen-assembler", 70)
    ]:
        task = mcp__archon__manage_task("create", project_id=project_id,
            title=title, description=f"{assignee} - Autonomous", status="todo",
            assignee=assignee, task_order=order)
        task_ids.append(task["task"]["id"])
else:
    project_id = None
    task_ids = []
    print("ℹ️ Archon unavailable - proceeding without tracking")
```

---

### Phase 1: Feature Analysis

Analyze INITIAL.md, extract requirements (see prp-gen-feature-analyzer.md)

```python
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="doing")

Task(subagent_type="prp-gen-feature-analyzer",
     description="Analyze INITIAL.md requirements",
     prompt=f'''Analyze INITIAL.md for PRP generation.
**INITIAL.md Path**: {initial_md_path}
**Feature Name**: {feature_name}
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read INITIAL.md thoroughly
2. Extract requirements (explicit and implicit)
3. Search Archon for similar PRPs
4. Identify technical components needed
5. Make intelligent assumptions for gaps
6. Create comprehensive feature-analysis.md

**Output Path**: prps/{feature_name}/planning/feature-analysis.md
''')

if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="done")
```

---

### Phase 2: Parallel Research (3x SPEEDUP)

Execute 3 subagents simultaneously (see .claude/patterns/parallel-subagents.md)

```python
# Update all tasks to "doing" (see archon-workflow.md)
if archon_available:
    for i in [1, 2, 3]:
        mcp__archon__manage_task("update", task_id=task_ids[i], status="doing")

# CRITICAL: Invoke ALL THREE in SINGLE response for parallel execution
Task(subagent_type="prp-gen-codebase-researcher",
     description="Search codebase patterns",
     prompt=f'''Search codebase patterns for PRP generation.
**Feature Analysis**: prps/{feature_name}/planning/feature-analysis.md (READ FIRST)
**Task**: Search Archon + local codebase, extract patterns, create codebase-patterns.md
**Output**: prps/{feature_name}/planning/codebase-patterns.md
''')

Task(subagent_type="prp-gen-documentation-hunter",
     description="Find documentation",
     prompt=f'''Find official documentation for PRP generation.
**Feature Analysis**: prps/{feature_name}/planning/feature-analysis.md (READ FIRST)
**Task**: Search Archon knowledge base + WebSearch, find official docs with examples
**Output**: prps/{feature_name}/planning/documentation-links.md
''')

Task(subagent_type="prp-gen-example-curator",
     description="Extract examples",
     prompt=f'''Extract code examples for PRP generation.
**Feature Analysis**: prps/{feature_name}/planning/feature-analysis.md (READ FIRST)
**Task**: Search Archon + local codebase, EXTRACT actual code to examples/ (NOT references!)
**Outputs**: prps/{feature_name}/examples/*, prps/{feature_name}/planning/examples-to-include.md
''')

if archon_available:
    for i in [1, 2, 3]:
        mcp__archon__manage_task("update", task_id=task_ids[i], status="done")
```

---

### Phase 3: Gotcha Detection

Identify pitfalls with solutions (see prp-gen-gotcha-detective.md)

```python
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="doing")

Task(subagent_type="prp-gen-gotcha-detective",
     description="Detect pitfalls and gotchas",
     prompt=f'''Identify gotchas for PRP generation.
**Research Docs** (READ ALL): prps/{feature_name}/planning/{{feature-analysis,codebase-patterns,documentation-links}}.md
**Task**: Search Archon + WebSearch for security/performance gotchas, document SOLUTIONS (not just warnings!)
**Output**: prps/{feature_name}/planning/gotchas.md
''')

if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="done")
```

---

### Phase 4: PRP Assembly

Synthesize all research into final PRP (see prp-gen-assembler.md, quality-gates.md)

**ULTRATHINK**: Review research docs - feature analysis clear? Patterns sufficient? Docs with examples? Code extracted? Gotchas with solutions?

```python
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="doing")

Task(subagent_type="prp-gen-assembler",
     description="Synthesize final PRP",
     prompt=f'''Assemble final PRP from all research.
**Research Docs** (READ ALL 5): prps/{feature_name}/planning/{{feature-analysis,codebase-patterns,documentation-links,examples-to-include,gotchas}}.md
**Template**: prps/templates/prp_base.md (USE THIS STRUCTURE)
**Task**: Synthesize into coherent PRP, include all URLs, reference examples/, score PRP (must be >= 8/10)
**Output**: prps/{feature_name}.md (and store in Archon if available)
''')

if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="done")
```

---

### Phase 5: Quality Check & Delivery

Quality gate enforcement (see .claude/patterns/quality-gates.md)

```python
# 1. Read PRP and extract quality score
prp_content = Read(f"prps/{feature_name}.md")
import re
score_match = re.search(r'Score:\s*(\d+)/10', prp_content)
quality_score = int(score_match.group(1)) if score_match else 0

# 2. Enforce 8+/10 minimum (see quality-gates.md for enforcement pattern)
if quality_score < 8:
    print(f"⚠️ Quality Gate Failed: {quality_score}/10 (minimum: 8/10)")
    print("Options: 1. Regenerate  2. Improve sections  3. Proceed anyway")
    choice = input("Choose (1/2/3): ")
    if choice == "1":
        # Re-run Phase 2
    elif choice == "2":
        # Re-run specific subagents
    elif choice != "3":
        exit(1)
else:
    print(f"✅ Quality Gate Passed: {quality_score}/10")

# 3. Completion report
print(f'''
✅ **PRP Generated Successfully!**

**Output**: prps/{feature_name}.md

**Quality Assessment**:
- PRP Quality Score: {quality_score}/10 {'✅' if quality_score >= 8 else '⚠️'}
- Documentation sources: {doc_count} official references
- Code examples: {example_count} files extracted
- Gotchas documented: {gotcha_count} with solutions

**Next Steps**:
1. Review: cat prps/{feature_name}.md
2. Execute: /execute-prp prps/{feature_name}.md
''')

# 4. Update Archon if available
if archon_available:
    mcp__archon__manage_project("update", project_id=project_id,
        description=f"COMPLETED: PRP quality {quality_score}/10, {example_count} examples, {gotcha_count} gotchas")
```

---

## Error Handling

See .claude/patterns/archon-workflow.md for graceful degradation patterns

```python
# Subagent failures - reset task for retry
try:
    Task(subagent_type="agent", description="task", prompt=ctx)
except Exception as e:
    print(f"⚠️ Phase failed: {e}")
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id, status="todo", description=f"ERROR: {e}")
    print("Options: 1. Retry  2. Continue with partial results  3. Abort")

# Archon unavailable - graceful fallback
if not archon_available:
    print("ℹ️ Archon unavailable - proceeding without tracking")

# Quality score < 8/10 - offer regeneration (see quality-gates.md)
if quality_score < 8:
    print(f"⚠️ PRP scored {quality_score}/10 - below 8/10")
    print("Options: 1. Regenerate  2. Enhance sections  3. Accept lower quality")
```

---

## Quality Gates

See .claude/patterns/quality-gates.md for comprehensive validation checklist

```python
quality_checks = [
    "PRP score >= 8/10",
    "All 5 research docs created",
    "Examples extracted (not references)",
    "Examples have README with 'what to mimic'",
    "Documentation includes URLs",
    "Gotchas with solutions (not just warnings)",
    "Task list logical and ordered",
    "Validation gates executable"
]

issues = [c for c in quality_checks if not verify_check(c)]
if issues:
    # Handle quality issues (see quality-gates.md for iteration loop)
```

---

## Success Metrics

```python
metrics = {
    "total_time": f"{elapsed_time} min (target: <10)",
    "prp_quality": f"{quality_score}/10 (target: >=8)",
    "research_docs": "5/5 created",
    "examples": f"{example_count} extracted (target: 2-4)",
    "documentation": f"{doc_count} sources (target: 5-7)",
    "gotchas": f"{gotcha_count} documented (target: 5-10)",
    "execution_ready": "yes" if quality_score >= 8 else "no"
}
```

---

## Key Innovation: Parallel Phase 2 (3x Speedup)

See .claude/patterns/parallel-subagents.md for implementation details

**Sequential** (OLD): 5+4+5 = 14 min
**Parallel** (NEW): max(5,4,5) = 5 min (64% faster)

Implementation: All 3 Task() calls in SINGLE response

---

Goal: One-pass implementation success through comprehensive PRPs (8+/10 quality)
