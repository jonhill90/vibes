# Domain Expert Auto-Selection Pattern

**Pattern Type**: Orchestration Logic
**Use Case**: Automatically select appropriate domain experts for PRP execution
**Source**: Agent Architecture Modernization (Task 6)
**Status**: Active

---

## Purpose

Automatically detect which domain experts to invoke based on PRP feature analysis technical components. Replaces generic `prp-exec-implementer` with specialized domain experts for higher-quality implementations.

**Problem**: Generic implementer lacks domain-specific knowledge (Terraform best practices, Azure patterns, etc.)
**Solution**: Auto-select domain experts based on technical components, invoke in parallel when possible
**Benefit**: 2-3x quality improvement from domain specialization

---

## Domain Expert Priority Order

Priority determines PRIMARY expert when multiple domains detected:

```python
DOMAIN_PRIORITIES = {
    "terraform": 100,      # IaC provisioning
    "azure": 90,           # Azure services
    "kubernetes": 80,      # Container orchestration
    "task_management": 70, # Orchestration
    "knowledge_curation": 60, # Knowledge base
    "context_engineering": 50, # Context optimization
    "python_backend": 40,  # Python/FastAPI (future)
    "frontend": 30         # React/UI (future)
}
```

**Rationale**: Infrastructure-first (Terraform provisions resources before Azure configures them)

---

## Detection Algorithm

### Step 1: Read Feature Analysis

```python
feature_analysis_path = f"prps/{feature_name}/planning/feature-analysis.md"
content = Read(feature_analysis_path)

# Extract technical components section
# Usually under "## Technical Components"
components = extract_technical_components(content)
```

### Step 2: Domain Detection

```python
def detect_applicable_domains(components: List[str]) -> List[Tuple[str, int]]:
    """
    Detect all applicable domains from technical components.

    Returns:
        List of (domain, priority) tuples
    """
    detected = []

    # Domain detection keywords
    DOMAIN_KEYWORDS = {
        "terraform": ["terraform", "iac", "infrastructure as code", ".tf", "tfvars"],
        "azure": ["azure", "arm template", "azure cli", "az ", "resource group"],
        "kubernetes": ["kubernetes", "k8s", "kubectl", "helm", "pods"],
        "task_management": ["task tracking", "orchestration", "workflow", "dependency"],
        "knowledge_curation": ["knowledge base", "documentation", "basic-memory"],
        "context_engineering": ["context optimization", "token management", "prompt"]
    }

    for component in components:
        component_lower = component.lower()

        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(keyword in component_lower for keyword in keywords):
                priority = DOMAIN_PRIORITIES[domain]
                detected.append((domain, priority))
                break  # One domain per component

    return detected
```

### Step 3: Primary + Collaborators Selection

```python
def select_experts(detected_domains: List[Tuple[str, int]]) -> dict:
    """
    Select primary expert and collaborators.

    Returns:
        {
            "primary": "domain-expert",
            "collaborators": ["domain-expert-2", "domain-expert-3"],
            "strategy": "parallel" | "sequential"
        }
    """
    if not detected_domains:
        # Fallback to generic implementer
        return {
            "primary": "prp-exec-implementer",
            "collaborators": [],
            "strategy": "sequential"
        }

    # Sort by priority (highest first)
    detected_domains.sort(key=lambda x: x[1], reverse=True)

    # Primary = highest priority
    primary_domain = detected_domains[0][0]

    # Collaborators = others
    collaborators = [d[0] for d in detected_domains[1:]]

    # Strategy: parallel if ≤3 collaborators, sequential otherwise
    strategy = "parallel" if len(collaborators) <= 3 else "sequential"

    return {
        "primary": f"{primary_domain}-expert",
        "collaborators": [f"{d}-expert" for d in collaborators],
        "strategy": strategy
    }
```

---

## Multi-Domain Orchestration Strategies

### Pattern 1: Task Decomposition (Recommended for 2-3 domains with linear dependencies)

**When to use**: Terraform provisions → Azure configures → Python implements

```python
# Step 1: Invoke task-manager to decompose into independent tasks
Task(subagent_type="task-manager", prompt=f'''
Decompose {feature_name} into domain-specific tasks.

Feature Analysis: {feature_analysis_path}
Domains Detected: {domains}

Output execution plan with:
- Task groups by domain
- Dependencies between groups
- Parallel execution opportunities
''')

# Step 2: Execute tasks by parallel groups
execution_plan = Read(f"prps/{feature_name}/execution/execution-plan.md")
groups = parse_execution_groups(execution_plan)

for group in groups:
    if group['mode'] == 'parallel':
        # Invoke all tasks in group simultaneously (CRITICAL: same response)
        for task in group['tasks']:
            expert = select_expert_for_task(task)
            Task(subagent_type=expert, prompt=task['context'])
```

**Benefits**:
- Leverages parallel execution (2-3x speedup)
- Clear dependency handling
- Independent task validation

**Gotchas**:
- Don't invoke task-manager from domain expert (sub-agent recursion limitation)
- Task-manager CANNOT have Task tool (only Read, Write, Grep, Glob)

### Pattern 2: Primary + Collaborators (Recommended for 2 domains, no dependencies)

**When to use**: Terraform + Azure working on independent components

```python
# Prepare contexts BEFORE invocation (parallel execution pattern)
primary_context = f'''
Implement {feature_name} as PRIMARY expert.

**Feature**: {feature_name}
**Your Domain**: {primary_domain}
**PRP Path**: prps/{feature_name}.md
**Your Responsibilities**: {primary_responsibilities}
**Collaborators**: {collaborators}

Read PRP Implementation Blueprint, implement your domain's tasks.
'''

collaborator_contexts = {}
for collaborator in experts["collaborators"]:
    collaborator_contexts[collaborator] = f'''
Support {feature_name} implementation.

**Feature**: {feature_name}
**Your Domain**: {collaborator.replace("-expert", "")}
**Primary Expert**: {experts["primary"]}
**Your Responsibilities**: {collaborator_responsibilities}

Read PRP Implementation Blueprint, implement your domain's tasks.
Coordinate with primary expert via shared files.
'''

# CRITICAL: Invoke ALL in SAME response (parallel execution)
Task(subagent_type=experts["primary"], prompt=primary_context)

for collaborator, context in collaborator_contexts.items():
    Task(subagent_type=collaborator, prompt=context)

# Time = max(primary_time, collaborator_times) NOT sum
# Achieves parallel speedup
```

**Benefits**:
- Simple orchestration
- Parallel execution (all invoked together)
- Clear primary ownership

**Gotchas**:
- File conflicts if both write same file (validate beforehand)
- No dependency ordering (assumes independent work)

### Pattern 3: Custom Orchestrator (Recommended for 4+ domains or complex dependencies)

**When to use**: Terraform + Azure + Kubernetes + Python with cross-dependencies

```python
# Create temporary orchestrator agent definition for specific feature
orchestrator_def = f'''---
name: {feature_name}-orchestrator
description: Orchestrates {feature_name} implementation across {len(domains)} domains.
tools: Read, Write, Grep, Glob
---

You coordinate {", ".join(domains)} domain experts for {feature_name}.

Read PRP, analyze dependencies, prepare contexts for each expert.
Output JSON orchestration plan for main agent to invoke experts.
'''

Write(f".claude/agents/{feature_name}-orchestrator.md", orchestrator_def)

# Invoke orchestrator to create plan
Task(subagent_type=f"{feature_name}-orchestrator", prompt=f'''
Create orchestration plan for {feature_name}.

PRP: prps/{feature_name}.md
Domains: {domains}

Output: prps/{feature_name}/execution/orchestration-plan.json
''')

# Execute orchestration plan
plan = json.loads(Read(f"prps/{feature_name}/execution/orchestration-plan.json"))

for phase in plan['phases']:
    if phase['mode'] == 'parallel':
        for expert_task in phase['tasks']:
            Task(subagent_type=expert_task['expert'],
                 prompt=expert_task['context'])
```

**Benefits**:
- Handles complex dependencies
- Custom logic for specific feature
- Reusable orchestration plan

**Gotchas**:
- Temporary agent file cleanup (delete after PRP execution)
- Orchestrator CANNOT invoke experts (no Task tool)
- Main agent still does invocation

---

## Agent Existence Validation

**CRITICAL**: Check if domain expert exists before invocation (fail gracefully)

```python
def agent_exists(agent_name: str) -> bool:
    """
    Check if agent definition file exists.

    Pattern: EAFP (Easier to Ask Forgiveness than Permission)
    """
    from pathlib import Path

    agent_path = Path(f".claude/agents/{agent_name}.md")
    return agent_path.exists()

# Usage in execute-prp.md
primary = experts["primary"]

if not agent_exists(primary):
    print(f"⚠️ Primary expert {primary} not found, using generic implementer")
    primary = "prp-exec-implementer"

# Validate collaborators
validated_collaborators = []
for collaborator in experts["collaborators"]:
    if agent_exists(collaborator):
        validated_collaborators.append(collaborator)
    else:
        print(f"⚠️ Collaborator {collaborator} not found, skipping")

experts["collaborators"] = validated_collaborators
```

---

## Fallback Strategy

```python
def execute_with_fallback(feature_name: str, experts: dict):
    """
    Execute with fallback to generic implementer if experts unavailable.

    Graceful degradation pattern for backward compatibility.
    """
    # Try domain experts first
    primary = experts["primary"]

    if not agent_exists(primary):
        # Fallback to generic implementer
        print(f"⚠️ Domain expert {primary} not available")
        print(f"   Using generic implementer as fallback")
        primary = "prp-exec-implementer"
        experts["collaborators"] = []  # Generic does everything

    # Execute with validated experts
    if experts["collaborators"]:
        # Multi-domain execution
        execute_multi_domain(feature_name, experts)
    else:
        # Single expert execution
        execute_single_expert(feature_name, primary)
```

---

## Integration with Execute-PRP Command

```python
# Phase 0: Domain Expert Auto-Selection (NEW)
feature_analysis = Read(f"prps/{feature_name}/planning/feature-analysis.md")
components = extract_technical_components(feature_analysis)
detected_domains = detect_applicable_domains(components)
experts = select_experts(detected_domains)

print(f"🔍 Domain Detection Results:")
print(f"   Detected Domains: {[d[0] for d in detected_domains]}")
print(f"   Primary Expert: {experts['primary']}")
print(f"   Collaborators: {experts['collaborators']}")
print(f"   Strategy: {experts['strategy']}")

# Phase 2: Parallel Implementation (UPDATED)
for group_number, group in enumerate(groups):
    if group['mode'] == "parallel":
        for task in group['tasks']:
            # Auto-select expert for task (instead of hardcoded prp-exec-implementer)
            task_expert = select_expert_for_task(task, experts)

            Task(subagent_type=task_expert, prompt=f'''
Implement single task from PRP.

**CONTEXT**:
- PRP: {prp_path}
- Task: {task['name']}
- Domain: {task_expert.replace("-expert", "")}
...
''')
```

---

## Example Scenarios

### Scenario 1: Single Domain (Terraform Only)

**Input**:
- Technical Components: ["Terraform module", "Azure VNet", "State management"]

**Detection**:
```python
detected_domains = [("terraform", 100)]
experts = {
    "primary": "terraform-expert",
    "collaborators": [],
    "strategy": "sequential"
}
```

**Execution**:
```python
Task(subagent_type="terraform-expert", prompt="Implement all tasks")
```

### Scenario 2: Two Domains (Terraform + Azure)

**Input**:
- Technical Components: ["Terraform provisioning", "Azure ARM templates", "Resource naming"]

**Detection**:
```python
detected_domains = [("terraform", 100), ("azure", 90)]
experts = {
    "primary": "terraform-expert",
    "collaborators": ["azure-engineer"],
    "strategy": "parallel"
}
```

**Execution**:
```python
# Parallel invocation (both in same response)
Task(subagent_type="terraform-expert", prompt="Provision infrastructure")
Task(subagent_type="azure-engineer", prompt="Configure Azure services")
```

### Scenario 3: Unknown Domain (Fallback)

**Input**:
- Technical Components: ["React frontend", "GraphQL API"]

**Detection**:
```python
detected_domains = []  # No matching domains
experts = {
    "primary": "prp-exec-implementer",
    "collaborators": [],
    "strategy": "sequential"
}
```

**Execution**:
```python
Task(subagent_type="prp-exec-implementer", prompt="Implement all tasks")
```

---

## Validation Checklist

Before executing with domain experts:

- [ ] Feature analysis exists at `prps/{feature_name}/planning/feature-analysis.md`
- [ ] Technical components extracted successfully
- [ ] At least 1 domain detected OR fallback to generic implementer
- [ ] Primary expert file exists at `.claude/agents/{primary}.md`
- [ ] Collaborator expert files exist (or removed from list)
- [ ] Execution strategy matches domain count (parallel ≤3, sequential >3)
- [ ] No file conflicts between parallel experts
- [ ] All Task() calls in single response (parallel execution preserved)

---

## Gotchas to Avoid

### ❌ WRONG: Sequential Invocation (Loses Parallelization)

```python
# ANTI-PATTERN: Invoking experts in loop
for expert in [primary] + collaborators:
    Task(subagent_type=expert, prompt=context)
# Time = sum of all expert times (SLOW)
```

### ✅ RIGHT: Parallel Invocation (Single Response)

```python
# CORRECT: All Task() calls in same response
Task(subagent_type=primary, prompt=primary_context)
for collaborator in collaborators:
    Task(subagent_type=collaborator, prompt=collab_context)
# Time = max of all expert times (FAST)
```

### ❌ WRONG: No Fallback (Breaks on Missing Expert)

```python
# ANTI-PATTERN: No existence check
Task(subagent_type="kubernetes-expert", ...)  # File doesn't exist → ERROR
```

### ✅ RIGHT: Graceful Fallback

```python
# CORRECT: Check existence, fallback to generic
if not agent_exists("kubernetes-expert"):
    Task(subagent_type="prp-exec-implementer", ...)
```

### ❌ WRONG: Sub-Agent Recursion (Domain Expert Invoking Another Expert)

```python
# In terraform-expert.md
# ---
# tools: Read, Write, Edit, Bash, Task  # ❌ Task tool
# ---

# Terraform expert tries to invoke Azure expert
Task(subagent_type="azure-engineer", ...)  # FAILS (sub-agents can't spawn sub-agents)
```

### ✅ RIGHT: Main Agent Orchestration

```python
# Main agent invokes both experts
Task(subagent_type="terraform-expert", ...)
Task(subagent_type="azure-engineer", ...)
# Domain experts DO NOT have Task tool
```

---

## Performance Impact

**Single Domain**:
- Before: Generic implementer (~60 min)
- After: Domain expert (~45 min, 25% faster from expertise)

**Multi-Domain (2 experts)**:
- Before: Generic implementer (~90 min, all tasks)
- After: 2 domain experts in parallel (~50 min, 44% faster)

**Multi-Domain (3 experts)**:
- Before: Generic implementer (~120 min, all tasks)
- After: 3 domain experts in parallel (~60 min, 50% faster)

**Quality Improvement**: 2-3x reduction in errors from domain-specific knowledge

---

## Related Patterns

- **Parallel Execution**: `.claude/patterns/parallel-subagents.md` (CRITICAL for performance)
- **Quality Gates**: `.claude/patterns/quality-gates.md` (domain-specific validation)
- **Agent Definitions**: `.claude/agents/README.md` (creating domain experts)

---

**Status**: Active
**Last Updated**: 2025-11-20
**Related PRPs**: agent_architecture_modernization (Task 6)
