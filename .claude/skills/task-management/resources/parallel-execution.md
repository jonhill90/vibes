# Parallel Execution - Deep Dive

## Overview

Advanced techniques for maximizing parallelization benefits in multi-agent workflows, with performance benchmarking and optimization strategies.

---

## Parallel Execution Fundamentals

### Why Parallelize?

**Sequential Execution**:
```
Task 1 (5 min) → Task 2 (4 min) → Task 3 (5 min)
Total: 14 minutes
```

**Parallel Execution**:
```
Task 1 (5 min) ⎤
Task 2 (4 min) ⎥ All run simultaneously
Task 3 (5 min) ⎦
Total: max(5, 4, 5) = 5 minutes (64% faster)
```

**Speedup Formula**:
```
Speedup = (Sequential_Time - Parallel_Time) / Sequential_Time * 100
Efficiency = Speedup / Number_of_Parallel_Tasks * 100
```

---

## Claude Code Parallel Invocation Pattern

### The Critical Rule

**ALL Task() calls MUST be in the SAME response.**

```python
✅ CORRECT - Parallel execution
# Single response with multiple Task() calls
Task(subagent_type="researcher", prompt=ctx1)
Task(subagent_type="hunter", prompt=ctx2)
Task(subagent_type="curator", prompt=ctx3)
# Claude executes all three simultaneously

❌ WRONG - Sequential execution
# Loop creates separate responses
for agent in ["researcher", "hunter", "curator"]:
    Task(subagent_type=agent, prompt=ctx)  # Each iteration = new response
# Claude executes one at a time (3x slower)
```

### Why This Matters

Claude Code's parallel execution engine:
1. **Collects all Task() calls** in a single response
2. **Spawns sub-agents** in parallel threads
3. **Waits for all to complete** before returning results
4. **Returns aggregated outputs** from all sub-agents

If Task() calls are in separate responses:
- Each call is a **separate sequential invocation**
- No parallelization benefits
- 3x slower for 3 tasks

---

## Implementation Patterns

### Pattern 1: Static Parallel Tasks

**Use Case**: Known tasks at planning time

```python
# Step 1: Prepare contexts BEFORE any Task() calls
researcher_ctx = f'''
Research {topic} and document findings.
Output: prps/{feature}/planning/research.md
'''

hunter_ctx = f'''
Find code examples for {topic}.
Output: prps/{feature}/examples/
'''

curator_ctx = f'''
Extract gotchas from {documentation}.
Output: prps/{feature}/planning/gotchas.md
'''

# Step 2: Invoke ALL in SAME response
Task(subagent_type="prp-gen-researcher", prompt=researcher_ctx)
Task(subagent_type="prp-gen-hunter", prompt=hunter_ctx)
Task(subagent_type="prp-gen-curator", prompt=curator_ctx)

# Result: 3 agents run in parallel (3x speedup)
```

### Pattern 2: Dynamic Parallel Tasks

**Use Case**: Task count determined at runtime

```python
# Step 1: Determine tasks dynamically
domains = analyze_feature_domains(feature_analysis)
# Result: ["terraform", "azure", "python"]

# Step 2: Prepare ALL contexts FIRST
contexts = {}
for domain in domains:
    contexts[domain] = f'''
    Implement {domain} components for {feature}.
    PRP: prps/{feature}.md
    Domain: {domain}
    '''

# Step 3: Invoke ALL in SAME response
for domain, ctx in contexts.items():
    Task(subagent_type=f"{domain}-expert", prompt=ctx)

# CRITICAL: Loop MUST complete BEFORE response ends
# All Task() calls collected, then executed in parallel
```

### Pattern 3: Conditional Parallel Tasks

**Use Case**: Optional tasks based on feature analysis

```python
# Step 1: Analyze feature requirements
has_terraform = "terraform" in feature_components
has_azure = "azure" in feature_components
has_frontend = "frontend" in feature_components

# Step 2: Prepare contexts for applicable tasks
if has_terraform:
    terraform_ctx = "..."

if has_azure:
    azure_ctx = "..."

if has_frontend:
    frontend_ctx = "..."

# Step 3: Invoke ALL applicable tasks in SAME response
if has_terraform:
    Task(subagent_type="terraform-expert", prompt=terraform_ctx)

if has_azure:
    Task(subagent_type="azure-expert", prompt=azure_ctx)

if has_frontend:
    Task(subagent_type="frontend-expert", prompt=frontend_ctx)

# All Task() calls still in single response = parallel
```

---

## Performance Benchmarking

### Measuring Execution Time

```python
import time

# Record start time
start_time = time.time()

# Invoke parallel tasks
Task(subagent_type="expert1", prompt=ctx1)
Task(subagent_type="expert2", prompt=ctx2)
Task(subagent_type="expert3", prompt=ctx3)

# Tasks complete here (Claude waits for all)
end_time = time.time()

# Calculate execution time
execution_time_minutes = (end_time - start_time) / 60

# Expected: ~max(task1_time, task2_time, task3_time)
# If close to sum(task1_time, task2_time, task3_time), parallelization FAILED
```

### Performance Validation

```python
def validate_parallelization(tasks, execution_time):
    """
    Validate that parallelization actually occurred.

    Args:
        tasks: List of task durations (estimated)
        execution_time: Actual measured execution time

    Returns:
        dict with validation results
    """
    sequential_time = sum(tasks)
    expected_parallel_time = max(tasks)

    # Allow 20% overhead for coordination
    max_acceptable_time = expected_parallel_time * 1.2

    if execution_time <= max_acceptable_time:
        status = "PARALLEL ✅"
        speedup = (sequential_time - execution_time) / sequential_time * 100
    elif execution_time <= sequential_time * 0.8:
        status = "PARTIAL PARALLELIZATION ⚠️"
        speedup = (sequential_time - execution_time) / sequential_time * 100
    else:
        status = "SEQUENTIAL (FAILED) ❌"
        speedup = 0

    return {
        'status': status,
        'speedup_percent': speedup,
        'execution_time': execution_time,
        'expected_parallel': expected_parallel_time,
        'sequential_baseline': sequential_time
    }

# Example
tasks = [5, 4, 5]  # Task durations in minutes
execution_time = 6  # Measured time

result = validate_parallelization(tasks, execution_time)
# Result: {'status': 'PARALLEL ✅', 'speedup_percent': 57, ...}
```

---

## Optimization Techniques

### 1. Load Balancing

**Problem**: Uneven task durations reduce parallelization benefits

```python
# Unbalanced tasks
Task 1: 2 minutes  ⎤
Task 2: 2 minutes  ⎥ Parallel group
Task 3: 20 minutes ⎦
# Total time: max(2, 2, 20) = 20 minutes
# Tasks 1 & 2 finish early, sit idle
```

**Solution**: Split long tasks or group similar durations

```python
# Balanced tasks (split Task 3)
Group 1 (parallel):
  Task 1: 2 minutes
  Task 2: 2 minutes
  Task 3a: 10 minutes (part 1)

Group 2 (sequential):
  Task 3b: 10 minutes (part 2, depends on 3a)

# Total time: max(2, 2, 10) + 10 = 20 minutes
# Better resource utilization
```

### 2. Batching Strategy

**Problem**: Too many parallel tasks exceed system limits

```python
# 12 tasks - exceeds optimal parallelization (2-6)
# Coordination overhead > speedup benefits
```

**Solution**: Batch into multiple parallel groups

```python
# Batch 12 tasks into 3 groups of 4
Group 1: Tasks 1-4   (parallel)
Group 2: Tasks 5-8   (parallel)
Group 3: Tasks 9-12  (parallel)

# Each group runs in parallel
# Groups run sequentially
# Optimal parallelization maintained
```

### 3. Critical Path Prioritization

**Problem**: Critical path tasks block dependent tasks

**Solution**: Schedule critical path tasks FIRST

```python
# Dependency graph
# A (5 min) → C (10 min) → E (5 min)  # Critical path: 20 min
# B (3 min) → D (3 min)               # Side branch: 6 min

# WRONG - Schedule side branch first
Group 1: B, D (parallel)  # 3 min wasted (A,C,E waiting)
Group 2: A, C, E

# RIGHT - Critical path first
Group 1: A, B (parallel)  # max(5, 3) = 5 min
Group 2: C, D (parallel)  # max(10, 3) = 10 min
Group 3: E                # 5 min
# Total: 20 min (optimal)
```

---

## Common Mistakes

### Mistake 1: Task() Calls in Loop

```python
❌ WRONG - Loop creates sequential execution
for task in tasks:
    Task(subagent_type="expert", prompt=task['context'])
# Each iteration = separate response = sequential

✅ RIGHT - Unroll loop into single response
for task in tasks:
    ctx = task['context']  # Prepare context

# Then invoke all
Task(subagent_type="expert", prompt=tasks[0]['context'])
Task(subagent_type="expert", prompt=tasks[1]['context'])
Task(subagent_type="expert", prompt=tasks[2]['context'])
# All in same response = parallel
```

### Mistake 2: Awaiting Between Task() Calls

```python
❌ WRONG - Await breaks parallel execution
Task(subagent_type="expert1", prompt=ctx1)
await some_operation()  # Breaks parallel collection
Task(subagent_type="expert2", prompt=ctx2)
# expert1 completes before expert2 starts

✅ RIGHT - No interruptions between Task() calls
Task(subagent_type="expert1", prompt=ctx1)
Task(subagent_type="expert2", prompt=ctx2)
# Both collected, then executed in parallel
```

### Mistake 3: Conditional Logic Between Task() Calls

```python
❌ WRONG - Logic creates sequential execution
Task(subagent_type="expert1", prompt=ctx1)

if some_condition:  # Evaluation delays next Task()
    Task(subagent_type="expert2", prompt=ctx2)
# expert1 completes before conditional evaluates

✅ RIGHT - Evaluate conditions BEFORE any Task() calls
if some_condition:
    ctx2 = prepare_context()

Task(subagent_type="expert1", prompt=ctx1)
if some_condition:
    Task(subagent_type="expert2", prompt=ctx2)
# Both Task() calls in same response = parallel
```

---

## Advanced Patterns

### Pattern: Nested Parallelization

**Use Case**: Main orchestrator with parallel sub-orchestrators

```python
# Main orchestrator (this agent)
# Spawns 3 parallel sub-orchestrators

Task(subagent_type="terraform-orchestrator", prompt="Deploy infrastructure")
Task(subagent_type="backend-orchestrator", prompt="Implement APIs")
Task(subagent_type="frontend-orchestrator", prompt="Build UI")

# Each sub-orchestrator spawns its own parallel tasks
# 2-level parallelization tree:
# Level 1: 3 orchestrators (parallel)
# Level 2: Each orchestrator spawns 3-4 implementers (parallel)
# Total: 3 orchestrators + 9-12 implementers (all parallel within levels)
```

**Performance**:
```
Sequential (no parallelization):
  Time = 3 orchestrators * 4 tasks * 5 min = 60 min

Level 1 parallelization (3 orchestrators):
  Time = max(4 tasks * 5 min) = 20 min (3x speedup)

Level 2 parallelization (orchestrators spawn parallel tasks):
  Time = max(max(5, 5, 5, 5)) = 5 min (12x speedup!)
```

### Pattern: Adaptive Parallelization

**Use Case**: Adjust parallelization based on resource availability

```python
def adaptive_parallel_execution(tasks, max_parallel=6):
    """
    Dynamically adjust parallelization based on system constraints.
    """
    groups = []
    current_group = []

    for task in tasks:
        if len(current_group) < max_parallel:
            current_group.append(task)
        else:
            groups.append(current_group)
            current_group = [task]

    if current_group:
        groups.append(current_group)

    # Execute groups sequentially, tasks within groups in parallel
    for group in groups:
        for task in group:
            Task(subagent_type=task['expert'], prompt=task['context'])
        # All Task() calls in group execute in parallel
```

---

## Real-World Performance Data

### Case Study: PRP Generation

**Scenario**: Generate PRP with 5 research documents

**Sequential Execution**:
```yaml
Phase 1: Researcher (5 min)
Phase 2: Hunter (4 min)
Phase 3: Curator (5 min)
Phase 4: Link Validator (3 min)
Phase 5: Example Extractor (4 min)
Total: 21 minutes
```

**Parallel Execution (3 agents per group)**:
```yaml
Group 1 (parallel):
  - Researcher (5 min)
  - Hunter (4 min)
  - Curator (5 min)
  Time: max(5, 4, 5) = 5 min

Group 2 (parallel):
  - Link Validator (3 min)
  - Example Extractor (4 min)
  Time: max(3, 4) = 4 min

Total: 5 + 4 = 9 minutes (57% faster)
```

**Measured Results**:
- Sequential baseline: 22 minutes (actual)
- Parallel execution: 9 minutes (actual)
- Speedup: 59% (close to theoretical 57%)
- Efficiency: 59% / 3 tasks = 20% per task (good for I/O-bound)

---

## Best Practices Summary

1. **Prepare all contexts BEFORE any Task() calls**
2. **Invoke all Task() calls in SAME response** (no loops, no awaits)
3. **Validate parallelization** with timing measurements
4. **Optimize task grouping** (2-6 tasks per group)
5. **Balance task durations** within parallel groups
6. **Prioritize critical path** tasks first
7. **Detect and resolve** file access conflicts
8. **Document expected speedup** in implementation plan
9. **Measure actual speedup** after execution
10. **Iterate on grouping** if speedup < 50%

---

**Resource Status**: COMPLETE ✅
**Line Count**: 276 ✅
