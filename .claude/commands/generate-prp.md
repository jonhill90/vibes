# Create PRP

Orchestrates PRP generation from INITIAL.md: a multi-subagent system that creates comprehensive, implementation-ready PRPs through systematic research and analysis.

## Feature file: $ARGUMENTS

Generate a complete PRP with thorough research using a 5-phase multi-subagent approach. Ensure context is comprehensive to enable self-validation and first-pass implementation success.

## The 5-Phase Workflow

### Phase 0: Setup & Initialization (YOU handle this)

**Immediate**: Read INITIAL.md → Extract feature name → Create directories → Initialize state → Phase 1 (no user interaction)

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

# 4. Initialize task tracking (file-based state)
# See .claude/patterns/task-tracking.md for details
import uuid
import json
from datetime import datetime

project_id = str(uuid.uuid4())
state_path = f"prps/{feature_name}/execution/state.json"

# Create project state
state = {
    "project_id": project_id,
    "name": feature_name,
    "description": f"Creating PRP from {initial_md_path}",
    "created_at": datetime.now().isoformat(),
    "tasks": {}
}

Bash(f"mkdir -p prps/{feature_name}/execution")
Write(state_path, json.dumps(state, indent=2))

# Create tasks
task_ids = []
for title, assignee, order in [
    ("Phase 1: Feature Analysis", "prp-gen-feature-analyzer", 100),
    ("Phase 2A: Codebase Research", "prp-gen-codebase-researcher", 90),
    ("Phase 2B: Documentation Hunt", "prp-gen-documentation-hunter", 85),
    ("Phase 2C: Example Curation", "prp-gen-example-curator", 80),
    ("Phase 3: Gotcha Detection", "prp-gen-gotcha-detective", 75),
    ("Phase 4: PRP Assembly", "prp-gen-assembler", 70)
]:
    task_id = str(uuid.uuid4())
    state = json.loads(Read(state_path))
    state["tasks"][task_id] = {
        "title": title,
        "assignee": assignee,
        "status": "todo",
        "task_order": order,
        "created_at": datetime.now().isoformat(),
        "project_id": project_id
    }
    Write(state_path, json.dumps(state, indent=2))
    task_ids.append(task_id)
```

---

### Phase 1: Feature Analysis

Analyze INITIAL.md, extract requirements (see prp-gen-feature-analyzer.md)

```python
# Update task status: todo -> doing
state = json.loads(Read(state_path))
state["tasks"][task_ids[0]]["status"] = "doing"
state["tasks"][task_ids[0]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))

Task(subagent_type="prp-gen-feature-analyzer",
     description="Analyze INITIAL.md requirements",
     prompt=f'''Analyze INITIAL.md for PRP generation.
**INITIAL.md Path**: {initial_md_path}
**Feature Name**: {feature_name}
**Project ID**: {project_id}

**Your Task**:
1. Read INITIAL.md thoroughly
2. Extract requirements (explicit and implicit)
3. Search basic-memory for similar PRPs (use project="obsidian")
4. Identify technical components needed
5. Detect domain expertise required (terraform, azure, kubernetes, python, etc.)
6. Make intelligent assumptions for gaps
7. Create comprehensive feature-analysis.md

**IMPORTANT - Domain Expert Detection**:
Analyze technical components and recommend domain experts:
- Terraform (.tf files, IaC) → terraform-expert
- Azure (ARM, azure-cli, resource groups) → azure-engineer
- Kubernetes (k8s, helm, deployments) → kubernetes-operator
- Python (FastAPI, Django, Flask) → python-backend-expert
- Task management (workflows, orchestration) → task-manager
- Knowledge curation (documentation, notes) → knowledge-curator
- Context optimization (prompts, tokens) → context-engineer

Include recommended experts in feature-analysis.md under "Recommended Domain Experts" section.

**Output Path**: prps/{feature_name}/planning/feature-analysis.md
''')

# Update task status: doing -> done
state = json.loads(Read(state_path))
state["tasks"][task_ids[0]]["status"] = "done"
state["tasks"][task_ids[0]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))
```

---

### Phase 2: Parallel Research (3x SPEEDUP)

Execute 3 subagents simultaneously (see .claude/patterns/parallel-subagents.md)

```python
# Update all tasks to "doing"
state = json.loads(Read(state_path))
for i in [1, 2, 3]:
    state["tasks"][task_ids[i]]["status"] = "doing"
    state["tasks"][task_ids[i]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))

# CRITICAL: Invoke ALL THREE in SINGLE response for parallel execution
Task(subagent_type="prp-gen-codebase-researcher",
     description="Search codebase patterns",
     prompt=f'''Search codebase patterns for PRP generation.
**Feature Analysis**: prps/{feature_name}/planning/feature-analysis.md (READ FIRST)
**Task**: Search basic-memory (project="obsidian") + local codebase, extract patterns, create codebase-patterns.md

**Basic-Memory Integration**:
Use mcp__basic_memory__search_notes(query="patterns", project="obsidian", page_size=5)
Keep queries SHORT (2-5 keywords) for optimal results.

**Output**: prps/{feature_name}/planning/codebase-patterns.md
''')

Task(subagent_type="prp-gen-documentation-hunter",
     description="Find documentation",
     prompt=f'''Find official documentation for PRP generation.
**Feature Analysis**: prps/{feature_name}/planning/feature-analysis.md (READ FIRST)
**Task**: Search basic-memory knowledge base (project="obsidian") + WebSearch, find official docs with examples

**Basic-Memory Integration**:
Use mcp__basic_memory__search_notes(query="documentation", project="obsidian", page_size=5)
Use mcp__basic_memory__list_directory(project="obsidian", folder="01-notes/01r-research/")

**Output**: prps/{feature_name}/planning/documentation-links.md
''')

Task(subagent_type="prp-gen-example-curator",
     description="Extract examples",
     prompt=f'''Extract code examples for PRP generation.
**Feature Analysis**: prps/{feature_name}/planning/feature-analysis.md (READ FIRST)
**Task**: Search basic-memory (project="obsidian") + local codebase, EXTRACT actual code to examples/ (NOT references!)

**Basic-Memory Integration**:
Use mcp__basic_memory__search_notes(query="examples", project="obsidian", page_size=5)

**Outputs**: prps/{feature_name}/examples/*, prps/{feature_name}/planning/examples-to-include.md
''')

# Update all tasks to "done"
state = json.loads(Read(state_path))
for i in [1, 2, 3]:
    state["tasks"][task_ids[i]]["status"] = "done"
    state["tasks"][task_ids[i]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))
```

---

### Phase 3: Gotcha Detection

Identify pitfalls with solutions (see prp-gen-gotcha-detective.md)

```python
# Update task status: todo -> doing
state = json.loads(Read(state_path))
state["tasks"][task_ids[4]]["status"] = "doing"
state["tasks"][task_ids[4]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))

Task(subagent_type="prp-gen-gotcha-detective",
     description="Detect pitfalls and gotchas",
     prompt=f'''Identify gotchas for PRP generation.
**Research Docs** (READ ALL): prps/{feature_name}/planning/{{feature-analysis,codebase-patterns,documentation-links}}.md
**Task**: Search basic-memory (project="obsidian") + WebSearch for security/performance gotchas, document SOLUTIONS (not just warnings!)

**Basic-Memory Integration**:
Use mcp__basic_memory__search_notes(query="gotchas security", project="obsidian", page_size=10)
Use mcp__basic_memory__search_notes(query="performance pitfalls", project="obsidian", page_size=10)

**Output**: prps/{feature_name}/planning/gotchas.md
''')

# Update task status: doing -> done
state = json.loads(Read(state_path))
state["tasks"][task_ids[4]]["status"] = "done"
state["tasks"][task_ids[4]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))
```

---

### Phase 4: PRP Assembly

Synthesize all research into final PRP (see prp-gen-assembler.md, quality-gates.md)

**ULTRATHINK**: Review research docs - feature analysis clear? Patterns sufficient? Docs with examples? Code extracted? Gotchas with solutions?

```python
# Update task status: todo -> doing
state = json.loads(Read(state_path))
state["tasks"][task_ids[5]]["status"] = "doing"
state["tasks"][task_ids[5]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))

Task(subagent_type="prp-gen-assembler",
     description="Synthesize final PRP",
     prompt=f'''Assemble final PRP from all research.
**Research Docs** (READ ALL 5): prps/{feature_name}/planning/{{feature-analysis,codebase-patterns,documentation-links,examples-to-include,gotchas}}.md
**Template**: prps/templates/prp_base.md (USE THIS STRUCTURE)
**Task**: Synthesize into coherent PRP, include all URLs, reference examples/, score PRP (must be >= 8/10)

**CRITICAL - Domain Expert Recommendations**:
Read feature-analysis.md "Recommended Domain Experts" section and include in PRP:

1. Add "Recommended Domain Experts" section in PRP after "What" section
2. List primary expert and collaborators (from feature-analysis.md)
3. Include when to use each expert
4. Add expert selection logic to Implementation Blueprint

Example format:
```markdown
## Recommended Domain Experts

**Primary Expert**: terraform-expert
- Use for: Infrastructure provisioning, .tf file creation, state management

**Collaborators**:
- azure-engineer: Azure resource configuration, ARM templates
- task-manager: Workflow orchestration, dependency analysis
```

**Output**: prps/{feature_name}.md
''')

# Update task status: doing -> done
state = json.loads(Read(state_path))
state["tasks"][task_ids[5]]["status"] = "done"
state["tasks"][task_ids[5]]["updated_at"] = datetime.now().isoformat()
Write(state_path, json.dumps(state, indent=2))
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

# 4. Update project state
state = json.loads(Read(state_path))
state["completed_at"] = datetime.now().isoformat()
state["quality_score"] = quality_score
state["description"] = f"COMPLETED: PRP quality {quality_score}/10, {example_count} examples, {gotcha_count} gotchas"
Write(state_path, json.dumps(state, indent=2))
```

---

## Error Handling

See .claude/patterns/task-tracking.md for state management patterns

```python
# Subagent failures - reset task for retry
try:
    Task(subagent_type="agent", description="task", prompt=ctx)
except Exception as e:
    print(f"⚠️ Phase failed: {e}")
    # Update state with error
    state = json.loads(Read(state_path))
    state["tasks"][task_id]["status"] = "todo"
    state["tasks"][task_id]["error"] = str(e)
    state["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
    Write(state_path, json.dumps(state, indent=2))
    print("Options: 1. Retry  2. Continue with partial results  3. Abort")

# Basic-memory unavailable - graceful fallback
try:
    mcp__basic_memory__search_notes(query="test", project="obsidian", page_size=1)
except Exception:
    print("ℹ️ basic-memory unavailable - using local search only")

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
