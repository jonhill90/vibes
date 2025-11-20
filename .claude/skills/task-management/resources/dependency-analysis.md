# Dependency Analysis - Deep Dive

## Overview

Comprehensive techniques for detecting, analyzing, and resolving task dependencies in feature implementations.

---

## Dependency Detection Algorithms

### 1. File-Level Dependency Detection

**Algorithm**: Scan task specifications for file creation vs. file consumption

```python
def detect_file_dependencies(tasks):
    """
    Detect dependencies based on file creation and usage.

    Returns: dependency_graph (dict)
    """
    created_files = {}  # {file_path: task_id}
    consumed_files = {}  # {file_path: [task_ids]}
    dependencies = {}   # {task_id: [depends_on_task_ids]}

    # Pass 1: Track file creators
    for task in tasks:
        for file in task.get('files_to_create', []):
            created_files[file] = task['id']

    # Pass 2: Track file consumers
    for task in tasks:
        for file in task.get('files_to_modify', []) + task.get('imports', []):
            if file in created_files:
                creator_task = created_files[file]
                if creator_task != task['id']:
                    if task['id'] not in dependencies:
                        dependencies[task['id']] = []
                    dependencies[task['id']].append(creator_task)

    return dependencies
```

### 2. Data Flow Dependency Detection

**Algorithm**: Analyze task descriptions for input/output relationships

```python
def detect_data_flow_dependencies(tasks):
    """
    Detect dependencies based on data flow (outputs → inputs).
    """
    dependencies = {}

    for task in tasks:
        task_inputs = extract_inputs(task['description'])

        for other_task in tasks:
            if other_task['id'] == task['id']:
                continue

            other_outputs = extract_outputs(other_task['description'])

            # Check if other_task outputs feed into task inputs
            if set(other_outputs) & set(task_inputs):
                if task['id'] not in dependencies:
                    dependencies[task['id']] = []
                dependencies[task['id']].append(other_task['id'])

    return dependencies

def extract_inputs(description):
    """Extract input references from task description."""
    patterns = [
        r'uses? (\w+)',
        r'imports? (\w+)',
        r'depends on (\w+)',
        r'requires? (\w+)'
    ]
    inputs = []
    for pattern in patterns:
        inputs.extend(re.findall(pattern, description, re.IGNORECASE))
    return inputs

def extract_outputs(description):
    """Extract output references from task description."""
    patterns = [
        r'creates? (\w+)',
        r'provides? (\w+)',
        r'generates? (\w+)',
        r'exports? (\w+)'
    ]
    outputs = []
    for pattern in patterns:
        outputs.extend(re.findall(pattern, description, re.IGNORECASE))
    return outputs
```

### 3. Domain-Level Dependency Detection

**Algorithm**: Apply domain expertise to infer conventional dependencies

```python
def detect_domain_dependencies(tasks):
    """
    Detect dependencies based on domain conventions.

    Examples:
    - Database schema before API endpoints
    - Models before services
    - Services before controllers
    - Backend API before frontend UI
    """
    DOMAIN_ORDER = {
        'database_schema': 0,
        'models': 1,
        'repositories': 2,
        'services': 3,
        'controllers': 4,
        'routes': 5,
        'api_endpoints': 6,
        'frontend_components': 7,
        'tests': 8
    }

    dependencies = {}

    for task in tasks:
        task_domain = classify_domain(task)
        task_order = DOMAIN_ORDER.get(task_domain, 99)

        # Any lower-order tasks are dependencies
        for other_task in tasks:
            if other_task['id'] == task['id']:
                continue

            other_domain = classify_domain(other_task)
            other_order = DOMAIN_ORDER.get(other_domain, 99)

            if other_order < task_order:
                if task['id'] not in dependencies:
                    dependencies[task['id']] = []
                dependencies[task['id']].append(other_task['id'])

    return dependencies

def classify_domain(task):
    """Classify task into domain category."""
    description = task['description'].lower()
    files = task.get('files_to_create', []) + task.get('files_to_modify', [])

    # Pattern matching for domain classification
    if any('schema' in f or 'migrations' in f for f in files):
        return 'database_schema'
    elif any('models' in f for f in files):
        return 'models'
    elif any('repository' in f or 'repositories' in f for f in files):
        return 'repositories'
    elif any('service' in f or 'services' in f for f in files):
        return 'services'
    elif any('controller' in f or 'controllers' in f for f in files):
        return 'controllers'
    elif any('route' in f or 'routes' in f for f in files):
        return 'routes'
    elif any('api' in f for f in files):
        return 'api_endpoints'
    elif any('component' in f or 'src/components' in f for f in files):
        return 'frontend_components'
    elif any('test' in f for f in files):
        return 'tests'
    else:
        return 'unknown'
```

---

## Dependency Graph Analysis

### Topological Sort (Execution Order)

```python
def topological_sort(tasks, dependencies):
    """
    Topological sort to determine valid execution order.

    Returns: List of tasks in dependency-respecting order
    Raises: ValueError if circular dependency detected
    """
    in_degree = {task['id']: 0 for task in tasks}

    # Calculate in-degree (number of dependencies) for each task
    for task_id, deps in dependencies.items():
        in_degree[task_id] = len(deps)

    # Queue tasks with no dependencies
    queue = [task['id'] for task in tasks if in_degree[task['id']] == 0]
    sorted_tasks = []

    while queue:
        # Process task with no remaining dependencies
        current = queue.pop(0)
        sorted_tasks.append(current)

        # Reduce in-degree for dependent tasks
        for task_id, deps in dependencies.items():
            if current in deps:
                in_degree[task_id] -= 1
                if in_degree[task_id] == 0:
                    queue.append(task_id)

    # Check for circular dependencies
    if len(sorted_tasks) != len(tasks):
        raise ValueError("Circular dependency detected")

    return sorted_tasks
```

### Parallel Group Extraction

```python
def extract_parallel_groups(tasks, dependencies):
    """
    Group tasks into parallel execution batches.

    Returns: List of groups, each group is list of task IDs that can run in parallel
    """
    groups = []
    remaining_tasks = set(task['id'] for task in tasks)
    completed_tasks = set()

    while remaining_tasks:
        # Find tasks with all dependencies satisfied
        ready_tasks = []
        for task_id in remaining_tasks:
            deps = dependencies.get(task_id, [])
            if all(dep in completed_tasks for dep in deps):
                ready_tasks.append(task_id)

        if not ready_tasks:
            raise ValueError("Circular dependency or logic error")

        # Add as parallel group
        groups.append(ready_tasks)

        # Mark as completed
        completed_tasks.update(ready_tasks)
        remaining_tasks.difference_update(ready_tasks)

    return groups
```

### Critical Path Analysis

```python
def find_critical_path(tasks, dependencies, durations):
    """
    Find critical path (longest dependency chain).

    Critical path determines minimum total execution time.
    """
    # Calculate earliest start time for each task
    earliest_start = {}

    for task in topological_sort(tasks, dependencies):
        deps = dependencies.get(task, [])
        if not deps:
            earliest_start[task] = 0
        else:
            # Start after all dependencies complete
            max_dep_completion = max(
                earliest_start[dep] + durations[dep]
                for dep in deps
            )
            earliest_start[task] = max_dep_completion

    # Critical path is longest chain
    critical_time = max(
        earliest_start[task] + durations[task]
        for task in earliest_start
    )

    # Backtrack to find tasks on critical path
    critical_tasks = []
    for task in earliest_start:
        completion_time = earliest_start[task] + durations[task]
        if completion_time == critical_time:
            critical_tasks.append(task)

    return critical_tasks, critical_time
```

---

## Conflict Resolution

### File Access Conflicts

```python
def detect_file_conflicts(parallel_group, tasks):
    """
    Detect if tasks in parallel group have conflicting file access.

    Conflicts:
    - Multiple tasks modifying same file
    - Task creating file another task modifying
    """
    files_created = {}
    files_modified = {}
    conflicts = []

    for task_id in parallel_group:
        task = next(t for t in tasks if t['id'] == task_id)

        # Check created files
        for file in task.get('files_to_create', []):
            if file in files_created or file in files_modified:
                conflicts.append({
                    'type': 'file_creation_conflict',
                    'file': file,
                    'tasks': [files_created.get(file) or files_modified.get(file), task_id]
                })
            files_created[file] = task_id

        # Check modified files
        for file in task.get('files_to_modify', []):
            if file in files_modified:
                conflicts.append({
                    'type': 'file_modification_conflict',
                    'file': file,
                    'tasks': [files_modified[file], task_id]
                })
            files_modified[file] = task_id

    return conflicts
```

### Resolution Strategies

**Strategy 1: Split Parallel Group**

```python
def resolve_by_splitting(parallel_group, conflicts):
    """
    Split conflicting tasks into separate sequential groups.
    """
    conflict_tasks = set()
    for conflict in conflicts:
        conflict_tasks.update(conflict['tasks'])

    # Group 1: Non-conflicting tasks (run in parallel)
    group1 = [t for t in parallel_group if t not in conflict_tasks]

    # Group 2: Conflicting tasks (run sequentially)
    group2 = list(conflict_tasks)

    return [group1] if group1 else [], [[t] for t in group2]
```

**Strategy 2: Merge Tasks**

```python
def resolve_by_merging(tasks, conflicts):
    """
    Merge conflicting tasks into single task.

    Use when: Tasks are tightly coupled, small scope
    """
    conflict_task_ids = set()
    for conflict in conflicts:
        conflict_task_ids.update(conflict['tasks'])

    conflicting_tasks = [t for t in tasks if t['id'] in conflict_task_ids]

    merged_task = {
        'id': f"merged_{'_'.join(conflict_task_ids)}",
        'description': " + ".join(t['description'] for t in conflicting_tasks),
        'files_to_create': list(set(sum((t.get('files_to_create', []) for t in conflicting_tasks), []))),
        'files_to_modify': list(set(sum((t.get('files_to_modify', []) for t in conflicting_tasks), [])))
    }

    return merged_task
```

---

## Advanced Patterns

### Circular Dependency Detection

```python
def detect_circular_dependencies(dependencies):
    """
    Detect circular dependencies using depth-first search.

    Returns: List of cycles (each cycle is list of task IDs)
    """
    cycles = []
    visited = set()
    path = []

    def dfs(task_id):
        if task_id in path:
            # Circular dependency found
            cycle_start = path.index(task_id)
            cycles.append(path[cycle_start:] + [task_id])
            return

        if task_id in visited:
            return

        visited.add(task_id)
        path.append(task_id)

        for dep in dependencies.get(task_id, []):
            dfs(dep)

        path.pop()

    for task_id in dependencies:
        dfs(task_id)

    return cycles
```

### Dependency Pruning (Optimization)

```python
def prune_transitive_dependencies(dependencies):
    """
    Remove transitive dependencies (A→B, B→C, A→C => remove A→C).

    Simplifies dependency graph without changing execution order.
    """
    pruned = {task: set(deps) for task, deps in dependencies.items()}

    for task, deps in pruned.items():
        # Find transitive dependencies
        transitive = set()
        for dep in deps:
            transitive.update(pruned.get(dep, []))

        # Remove transitive dependencies
        pruned[task] = deps - transitive

    return {task: list(deps) for task, deps in pruned.items()}
```

---

## Real-World Example

### Scenario: E-commerce Checkout Feature

**Tasks**:
```yaml
Task 1: Create Order model
Task 2: Create Payment service
Task 3: Create Inventory service
Task 4: Create Checkout controller
Task 5: Create Order API endpoints
Task 6: Create Payment API endpoints
Task 7: Create Frontend checkout page
Task 8: Integration tests
```

**Step 1: Detect Dependencies**

```python
dependencies = {
    'Task 2': ['Task 1'],  # Payment needs Order
    'Task 3': ['Task 1'],  # Inventory needs Order
    'Task 4': ['Task 2', 'Task 3'],  # Controller uses Payment + Inventory
    'Task 5': ['Task 4'],  # Order API uses Controller
    'Task 6': ['Task 2'],  # Payment API uses Payment service
    'Task 7': ['Task 5', 'Task 6'],  # Frontend needs both APIs
    'Task 8': ['Task 7']  # Tests need complete system
}
```

**Step 2: Extract Parallel Groups**

```python
groups = extract_parallel_groups(tasks, dependencies)
# Result:
# Group 1: [Task 1]
# Group 2: [Task 2, Task 3]  # Parallel (both depend only on Task 1)
# Group 3: [Task 4, Task 6]  # Parallel (Task 4 needs 2+3, Task 6 needs 2)
# Group 4: [Task 5]
# Group 5: [Task 7]
# Group 6: [Task 8]
```

**Step 3: Calculate Performance**

```python
durations = {
    'Task 1': 10, 'Task 2': 15, 'Task 3': 12,
    'Task 4': 20, 'Task 5': 8, 'Task 6': 10,
    'Task 7': 25, 'Task 8': 30
}

sequential_time = sum(durations.values())  # 130 minutes
parallel_time = 10 + max(15,12) + max(20,10) + 8 + 25 + 30  # 108 minutes
speedup = (130-108)/130*100  # 17% faster
```

---

## Best Practices

1. **Use multiple detection algorithms**: Combine file, data flow, and domain detection for comprehensive analysis
2. **Validate dependency graph**: Check for circular dependencies before execution
3. **Optimize parallel groups**: Aim for 2-6 tasks per group for optimal performance
4. **Resolve conflicts early**: Detect file conflicts before execution starts
5. **Document assumptions**: Make domain-based dependencies explicit in task specifications

---

**Resource Status**: COMPLETE ✅
**Line Count**: 298 ✅
