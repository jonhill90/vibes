# Execute PRP

Execute a complete PRP implementation with validation loops: parse PRP sections, implement tasks in order, run validation gates (ruff → mypy → pytest → coverage), retry on failures (max 5 attempts), and generate completion report.

## PRP file: $ARGUMENTS

Execute the PRP implementation following the Implementation Blueprint task order, with comprehensive validation and error recovery.

## Execution Overview

### Workflow Phases

1. **Parse PRP**: Extract all sections (Goal, Implementation Blueprint, Known Gotchas, Validation Loop)
2. **Task Execution**: Implement tasks in dependency order (data models → core logic → integration → tests)
3. **Validation Loop**: Run multi-level validation with automatic retry on failures (max 5 attempts)
4. **Completion Report**: Generate comprehensive report with coverage metrics and blockers

---

## Phase 1: PRP Parsing & Setup

**Immediate**: Read PRP → Extract feature name → Parse sections → Setup validation environment

```python
# 1. Read PRP file
prp_file_path = "$ARGUMENTS"
prp_content = Read(prp_file_path)

# 2. Extract feature name from PRP path
# Pattern: prps/feature_name.md OR prps/feature_name/execution.md
import re

def extract_feature_name_from_prp(filepath: str) -> str:
    """Extract feature name from PRP file path with validation."""
    # Security validation (6 levels)
    if ".." in filepath:
        raise ValueError(f"Path traversal detected: {filepath}")

    # Extract from path: prps/feature_name.md OR prps/feature_name/anything.md
    parts = filepath.split("/")

    if "prps" not in parts:
        raise ValueError(f"Invalid PRP path (must be in prps/ directory): {filepath}")

    prps_index = parts.index("prps")
    if prps_index + 1 >= len(parts):
        raise ValueError(f"No feature name after prps/: {filepath}")

    # Feature name is directory after prps/ (or basename if .md directly in prps/)
    feature_raw = parts[prps_index + 1]

    # If it's a .md file directly in prps/, strip .md
    if feature_raw.endswith(".md"):
        feature = feature_raw.replace(".md", "")
    else:
        # It's a directory, use as-is
        feature = feature_raw

    # Validation (levels 2-6)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid feature name characters: {feature}")

    if len(feature) > 50:
        raise ValueError(f"Feature name too long: {len(feature)} > 50")

    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Invalid feature name (traversal): {feature}")

    dangerous = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(c in feature for c in dangerous):
        raise ValueError(f"Dangerous characters in feature name: {feature}")

    return feature

feature_name = extract_feature_name_from_prp(prp_file_path)

print(f"==========================================")
print(f"PRP Execution Workflow")
print(f"==========================================")
print(f"PRP: {prp_file_path}")
print(f"Feature: {feature_name}")
print(f"")

# 3. Parse PRP sections
def parse_prp_sections(content: str) -> dict:
    """Extract key sections from PRP for execution."""
    sections = {}

    # Extract Goal
    goal_match = re.search(r'##\s*Goal\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    sections['goal'] = goal_match.group(1).strip() if goal_match else ""

    # Extract Implementation Blueprint
    blueprint_match = re.search(r'##\s*Implementation Blueprint\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    sections['blueprint'] = blueprint_match.group(1).strip() if blueprint_match else ""

    # Extract Known Gotchas
    gotchas_match = re.search(r'###\s*Known Gotchas.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    sections['gotchas'] = gotchas_match.group(1).strip() if gotchas_match else ""

    # Extract Validation Loop
    validation_match = re.search(r'##\s*Validation Loop\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    sections['validation'] = validation_match.group(1).strip() if validation_match else ""

    return sections

prp_sections = parse_prp_sections(prp_content)

# 4. Parse tasks from Implementation Blueprint
def parse_tasks_from_blueprint(blueprint: str) -> list:
    """Extract task list from blueprint section."""
    tasks = []

    # Match task headers: "Task N: Title" or "### Task N: Title"
    task_pattern = r'(?:###\s*)?Task\s+(\d+):\s*([^\n]+)'

    for match in re.finditer(task_pattern, blueprint):
        task_num = int(match.group(1))
        task_title = match.group(2).strip()

        # Extract task content until next task or section
        task_start = match.end()
        next_task = re.search(r'\n(?:###\s*)?Task\s+\d+:', blueprint[task_start:])

        if next_task:
            task_content = blueprint[task_start:task_start + next_task.start()]
        else:
            # Last task - content until next ## section or end
            next_section = re.search(r'\n##\s', blueprint[task_start:])
            if next_section:
                task_content = blueprint[task_start:task_start + next_section.start()]
            else:
                task_content = blueprint[task_start:]

        # Extract key subsections
        responsibility = ""
        files_to_modify = []
        steps = []
        validation = ""

        # RESPONSIBILITY
        resp_match = re.search(r'RESPONSIBILITY:\s*([^\n]+)', task_content, re.IGNORECASE)
        if resp_match:
            responsibility = resp_match.group(1).strip()

        # FILES TO CREATE/MODIFY
        files_match = re.search(r'FILES TO (?:CREATE|MODIFY):\s*\n(.*?)(?=\n[A-Z]+:|$)', task_content, re.DOTALL | re.IGNORECASE)
        if files_match:
            files_text = files_match.group(1).strip()
            # Extract file paths (lines starting with - or indented)
            for line in files_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    file_path = line[1:].strip()
                    files_to_modify.append(file_path)

        # SPECIFIC STEPS
        steps_match = re.search(r'SPECIFIC STEPS:\s*\n(.*?)(?=\n[A-Z]+:|$)', task_content, re.DOTALL | re.IGNORECASE)
        if steps_match:
            steps_text = steps_match.group(1).strip()
            # Extract numbered steps
            for line in steps_text.split('\n'):
                line = line.strip()
                # Match: "1. Step" or "  1. Step" (numbered list items)
                if re.match(r'^\d+\.', line):
                    steps.append(line)

        # VALIDATION
        val_match = re.search(r'VALIDATION:\s*\n(.*?)(?=\n[A-Z]+:|$)', task_content, re.DOTALL | re.IGNORECASE)
        if val_match:
            validation = val_match.group(1).strip()

        tasks.append({
            'number': task_num,
            'title': task_title,
            'responsibility': responsibility,
            'files_to_modify': files_to_modify,
            'steps': steps,
            'validation': validation,
            'content': task_content.strip()
        })

    # Sort by task number
    tasks.sort(key=lambda t: t['number'])

    return tasks

tasks = parse_tasks_from_blueprint(prp_sections['blueprint'])

print(f"Parsed {len(tasks)} tasks from Implementation Blueprint:")
for task in tasks:
    print(f"  - Task {task['number']}: {task['title']}")
    print(f"    Files: {len(task['files_to_modify'])}, Steps: {len(task['steps'])}")
print("")

# 5. Setup validation environment
validation_context = {
    'prp_path': prp_file_path,
    'feature_name': feature_name,
    'tasks': tasks,
    'gotchas': prp_sections['gotchas'],
    'validation_commands': prp_sections['validation'],
    'max_attempts': 5,
    'current_attempt': 1,
    'files_modified': [],
    'validation_results': {},
    'blockers': []
}
```

---

## Phase 2: Task Execution

Execute tasks in order, following PRP Implementation Blueprint.

```python
print(f"==========================================")
print(f"Task Execution (In Dependency Order)")
print(f"==========================================")
print("")

# Track execution state
execution_state = {
    'completed_tasks': [],
    'failed_tasks': [],
    'skipped_tasks': [],
    'files_created': [],
    'files_modified': []
}

# Execute each task
for task in tasks:
    task_num = task['number']
    task_title = task['title']

    print(f"--- Task {task_num}: {task_title} ---")
    print(f"Responsibility: {task['responsibility']}")
    print(f"Files to modify: {len(task['files_to_modify'])}")
    print("")

    # Display steps for context
    if task['steps']:
        print("Steps:")
        for step in task['steps']:
            print(f"  {step}")
        print("")

    # Implementation strategy:
    # 1. Read existing files (if modifying)
    # 2. Implement following PRP patterns
    # 3. Apply gotchas from Known Gotchas section
    # 4. Add error handling
    # 5. Document code

    try:
        # Read files that will be modified
        existing_files = {}
        for file_path in task['files_to_modify']:
            try:
                existing_content = Read(file_path)
                existing_files[file_path] = existing_content
                print(f"  Read existing: {file_path} ({len(existing_content.split(chr(10)))} lines)")
            except:
                print(f"  Creating new: {file_path}")

        print("")

        # IMPLEMENTATION SECTION
        # =======================
        # This is where the actual code implementation happens.
        # Follow these principles:

        # 1. REFERENCE PRP PATTERNS
        # - Read "All Needed Context" section for relevant patterns
        # - Study examples/ directory for reference implementations
        # - Follow codebase naming conventions

        # 2. APPLY KNOWN GOTCHAS
        # - Check "Known Gotchas" section for relevant warnings
        # - Apply solutions/fixes proactively
        # - Add comments noting which gotchas you addressed

        # 3. ERROR HANDLING
        # - Add try/except for external calls (API, DB, file I/O)
        # - Validate inputs before processing
        # - Log errors for debugging

        # 4. DOCUMENTATION
        # - Add docstrings to functions/classes
        # - Comment complex logic
        # - Note any assumptions or limitations

        # EXAMPLE IMPLEMENTATION PATTERN:
        # -------------------------------
        # if "Create model" in task_title:
        #     # Read pattern from examples
        #     pattern_file = "prps/{feature_name}/examples/model_pattern.py"
        #     pattern = Read(pattern_file) if file_exists(pattern_file) else None
        #
        #     # Implement following pattern
        #     model_code = implement_model(task, pattern, prp_sections['gotchas'])
        #
        #     # Write to file
        #     for file_path in task['files_to_modify']:
        #         if file_path in existing_files:
        #             # Edit existing file
        #             Edit(file_path, old_string=..., new_string=...)
        #         else:
        #             # Create new file
        #             Write(file_path, model_code)
        #             execution_state['files_created'].append(file_path)

        # Since this is a PROMPT (not executable code), we provide instructions
        # for the Codex agent executing this command:

        print(f"  IMPLEMENTING Task {task_num}...")
        print(f"  (Follow PRP patterns, apply gotchas, add error handling)")
        print("")

        # After implementation, track files
        for file_path in task['files_to_modify']:
            if file_path not in execution_state['files_created']:
                if file_path in existing_files:
                    execution_state['files_modified'].append(file_path)
                else:
                    execution_state['files_created'].append(file_path)

        # Mark as completed
        execution_state['completed_tasks'].append(task_num)
        print(f"  Completed Task {task_num}")
        print("")

    except Exception as e:
        print(f"  ERROR in Task {task_num}: {e}")
        execution_state['failed_tasks'].append({
            'task_num': task_num,
            'error': str(e)
        })
        print("")

        # Offer recovery options
        print("  Options:")
        print("    1. Retry task")
        print("    2. Skip task (continue with others)")
        print("    3. Abort execution")
        # In interactive mode, user would choose here

print("")
print(f"Task Execution Summary:")
print(f"  Completed: {len(execution_state['completed_tasks'])} tasks")
print(f"  Failed: {len(execution_state['failed_tasks'])} tasks")
print(f"  Files created: {len(execution_state['files_created'])}")
print(f"  Files modified: {len(execution_state['files_modified'])}")
print("")
```

---

## Phase 3: Validation Loop

Run multi-level validation with automatic retry on failures (max 5 attempts).

```python
print(f"==========================================")
print(f"Validation Loop (Max {validation_context['max_attempts']} Attempts)")
print(f"==========================================")
print("")

# Parse validation commands from PRP
def parse_validation_commands(validation_section: str) -> dict:
    """Extract validation levels and commands from PRP."""
    levels = {}

    # Match: "### Level N: Title" followed by commands
    level_pattern = r'###\s*Level\s+(\d+):\s*([^\n]+)\s*\n(.*?)(?=\n###\s*Level|\Z)'

    for match in re.finditer(level_pattern, validation_section, re.DOTALL):
        level_num = int(match.group(1))
        level_title = match.group(2).strip()
        level_content = match.group(3).strip()

        # Extract bash commands (lines starting with # or within ``` blocks)
        commands = []
        in_code_block = False

        for line in level_content.split('\n'):
            line = line.strip()

            # Code block markers
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue

            # Commands (in code blocks or starting with specific prefixes)
            if in_code_block:
                if line and not line.startswith('#'):
                    commands.append(line)

        levels[level_num] = {
            'title': level_title,
            'commands': commands
        }

    return levels

validation_levels = parse_validation_commands(prp_sections['validation'])

print(f"Validation levels parsed: {len(validation_levels)}")
for level_num, level_data in sorted(validation_levels.items()):
    print(f"  Level {level_num}: {level_data['title']} ({len(level_data['commands'])} commands)")
print("")

# Validation loop implementation
validation_success = False

for attempt in range(1, validation_context['max_attempts'] + 1):
    print(f"--- Validation Attempt {attempt}/{validation_context['max_attempts']} ---")
    print("")

    all_levels_passed = True

    # Run each validation level
    for level_num in sorted(validation_levels.keys()):
        level = validation_levels[level_num]
        print(f"  Level {level_num}: {level['title']}")

        level_passed = True
        level_errors = []

        # Run each command in this level
        for cmd in level['commands']:
            if not cmd.strip():
                continue

            print(f"    Running: {cmd}")

            try:
                # Execute validation command
                result = Bash(cmd, timeout=120000)  # 2 minute timeout

                # Check exit code (non-zero = failure)
                if "exit code" in result.lower() and "0" not in result:
                    level_passed = False
                    level_errors.append({
                        'command': cmd,
                        'output': result
                    })
                    print(f"      FAILED")
                else:
                    print(f"      PASSED")

            except Exception as e:
                level_passed = False
                level_errors.append({
                    'command': cmd,
                    'error': str(e)
                })
                print(f"      ERROR: {e}")

        # Store results
        validation_context['validation_results'][f'level_{level_num}_attempt_{attempt}'] = {
            'passed': level_passed,
            'errors': level_errors
        }

        if level_passed:
            print(f"    LEVEL {level_num} PASSED")
        else:
            print(f"    LEVEL {level_num} FAILED ({len(level_errors)} errors)")
            all_levels_passed = False

        print("")

        # If this level failed, try to fix before next level
        if not level_passed and attempt < validation_context['max_attempts']:
            print(f"    Analyzing errors for fixes...")

            # ERROR ANALYSIS AND FIX APPLICATION
            # ==================================
            # 1. Extract error messages
            # 2. Search PRP "Known Gotchas" for matching solutions
            # 3. Apply fixes
            # 4. Continue to next level or retry this level

            for error in level_errors:
                error_msg = error.get('output', error.get('error', ''))

                # Search gotchas for relevant solution
                gotcha_solution = search_gotchas_for_error(
                    prp_sections['gotchas'],
                    error_msg,
                    error['command']
                )

                if gotcha_solution:
                    print(f"      Found gotcha solution: {gotcha_solution[:100]}...")
                    # Apply fix (implementation-specific)
                    # apply_gotcha_fix(gotcha_solution)
                else:
                    print(f"      No gotcha found - manual intervention may be needed")
                    validation_context['blockers'].append({
                        'level': level_num,
                        'command': error['command'],
                        'error': error_msg
                    })

            print("")

    # Check if all levels passed
    if all_levels_passed:
        print(f"  ALL VALIDATION LEVELS PASSED (Attempt {attempt})")
        validation_success = True
        break
    else:
        print(f"  Validation failed on attempt {attempt}")

        if attempt < validation_context['max_attempts']:
            print(f"  Retrying with fixes...")
        else:
            print(f"  Max attempts reached - manual intervention required")

        print("")

print("")
print(f"Validation Loop Result: {'SUCCESS' if validation_success else 'FAILED'}")
print("")

def search_gotchas_for_error(gotchas_text: str, error_message: str, command: str) -> str:
    """Search Known Gotchas section for relevant solution to error."""
    # Simple keyword matching (can be enhanced with semantic search)

    # Extract error type
    error_patterns = {
        'import_error': r'ImportError|ModuleNotFoundError',
        'type_error': r'TypeError|AttributeError',
        'assertion_error': r'AssertionError',
        'syntax_error': r'SyntaxError|IndentationError',
        'timeout': r'TimeoutError|timeout',
        'permission': r'PermissionError|Permission denied',
        'file_not_found': r'FileNotFoundError|No such file'
    }

    error_type = None
    for etype, pattern in error_patterns.items():
        if re.search(pattern, error_message, re.IGNORECASE):
            error_type = etype
            break

    if not error_type:
        return None

    # Search gotchas for this error type
    # Look for sections with GOTCHA headers containing solutions
    gotcha_pattern = r'(?:CRITICAL |HIGH PRIORITY |MEDIUM PRIORITY )?GOTCHA \d+:.*?(?=GOTCHA \d+:|$)'

    for gotcha_match in re.finditer(gotcha_pattern, gotchas_text, re.DOTALL):
        gotcha_content = gotcha_match.group(0)

        # Check if this gotcha mentions the error type or related keywords
        if error_type in gotcha_content.lower() or re.search(error_patterns[error_type], gotcha_content, re.IGNORECASE):
            # Extract solution (lines starting with ✅ or "Solution:")
            solution_match = re.search(r'(?:✅|Solution:|RIGHT).*', gotcha_content, re.DOTALL)
            if solution_match:
                return solution_match.group(0)

    return None
```

---

## Phase 4: Completion Report

Generate comprehensive report with coverage metrics and blockers.

```python
print(f"==========================================")
print(f"Completion Report")
print(f"==========================================")
print("")

# Calculate metrics
total_tasks = len(tasks)
completed_tasks = len(execution_state['completed_tasks'])
failed_tasks = len(execution_state['failed_tasks'])
completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

# Test coverage (if pytest --cov was run)
coverage_percentage = 0
coverage_output = None

try:
    # Try to get coverage from validation results
    for key, result in validation_context['validation_results'].items():
        if 'pytest' in key.lower() or 'coverage' in key.lower():
            for error in result.get('errors', []):
                output = error.get('output', '')
                # Extract coverage percentage (pattern: "TOTAL ... 87%")
                cov_match = re.search(r'TOTAL.*?(\d+)%', output)
                if cov_match:
                    coverage_percentage = int(cov_match.group(1))
                    coverage_output = output
                    break
except Exception as e:
    print(f"  Warning: Could not extract coverage: {e}")

# Quality score (if extractable from validation)
quality_score = None
try:
    # Check if PRP includes quality scoring in validation
    score_match = re.search(r'Score:\s*(\d+)/10', prp_content)
    if score_match:
        quality_score = int(score_match.group(1))
except:
    pass

# Generate report
report = f"""
PRP EXECUTION COMPLETION REPORT
================================

Feature: {feature_name}
PRP: {prp_file_path}
Date: {import datetime; datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

IMPLEMENTATION STATUS
---------------------
Tasks Completed: {completed_tasks}/{total_tasks} ({completion_rate:.1f}%)
Tasks Failed: {failed_tasks}
Tasks Skipped: {len(execution_state['skipped_tasks'])}

FILES MODIFIED
--------------
Created: {len(execution_state['files_created'])} files
Modified: {len(execution_state['files_modified'])} files

Files Created:
{chr(10).join(f'  - {f}' for f in execution_state['files_created']) if execution_state['files_created'] else '  (none)'}

Files Modified:
{chr(10).join(f'  - {f}' for f in execution_state['files_modified']) if execution_state['files_modified'] else '  (none)'}

VALIDATION RESULTS
------------------
Status: {'PASSED' if validation_success else 'FAILED'}
Attempts: {attempt}/{validation_context['max_attempts']}
Validation Levels: {len(validation_levels)}

Level Results:
"""

# Add validation level results
for level_num in sorted(validation_levels.keys()):
    level = validation_levels[level_num]
    # Get latest attempt result for this level
    latest_result = None
    for attempt_num in range(attempt, 0, -1):
        key = f'level_{level_num}_attempt_{attempt_num}'
        if key in validation_context['validation_results']:
            latest_result = validation_context['validation_results'][key]
            break

    if latest_result:
        status = 'PASSED' if latest_result['passed'] else 'FAILED'
        error_count = len(latest_result.get('errors', []))
        report += f"  Level {level_num} ({level['title']}): {status}"
        if error_count > 0:
            report += f" ({error_count} errors)"
        report += "\n"

# Add coverage metrics
report += f"""
QUALITY METRICS
---------------
Test Coverage: {coverage_percentage}% {'✅ (>= 70%)' if coverage_percentage >= 70 else '⚠️  (< 70%)' if coverage_percentage > 0 else '(not measured)'}
"""

if quality_score:
    report += f"Quality Score: {quality_score}/10 {'✅ (>= 8/10)' if quality_score >= 8 else '⚠️  (< 8/10)'}\n"

# Add blockers
if validation_context['blockers']:
    report += f"""
BLOCKERS
--------
{len(validation_context['blockers'])} issue(s) require attention:

"""
    for i, blocker in enumerate(validation_context['blockers'], 1):
        report += f"{i}. Level {blocker['level']}: {blocker['command']}\n"
        report += f"   Error: {blocker['error'][:200]}...\n"
        report += "\n"
else:
    report += "\nBLOCKERS\n--------\nNone - all validation passed!\n"

# Add next steps
if validation_success:
    report += """
NEXT STEPS
----------
1. Review implementation files for quality
2. Run additional integration tests if needed
3. Commit changes to version control
4. Update documentation

"""
else:
    report += """
NEXT STEPS
----------
1. Review blockers above and fix manually
2. Re-run validation: execute this command again
3. Consider updating PRP if gotchas are missing
4. Seek help if errors persist after fixes

"""

report += f"Generated by: codex-execute-prp\n"
report += f"Execution time: (calculate from start to end)\n"

print(report)

# Write report to file
report_path = f"prps/{feature_name}/EXECUTION_REPORT.md"
Write(report_path, report)
print(f"Report saved to: {report_path}")
print("")
```

---

## Phase 5: Archon Integration (Optional)

Update Archon project with completion status if available.

```python
# Check if Archon is available
try:
    health = mcp__archon__health_check()
    archon_available = health.get("status") == "healthy"
except:
    archon_available = False

if archon_available:
    print(f"==========================================")
    print(f"Archon Integration")
    print(f"==========================================")
    print("")

    try:
        # Search for existing project for this feature
        projects = mcp__archon__find_projects(query=f"PRP: {feature_name}")

        if projects and len(projects.get('projects', [])) > 0:
            project_id = projects['projects'][0]['id']
            print(f"  Found existing project: {project_id}")

            # Update project with completion status
            status_summary = f"Execution {'COMPLETE' if validation_success else 'FAILED'}: {completed_tasks}/{total_tasks} tasks, {coverage_percentage}% coverage"

            mcp__archon__manage_project("update",
                project_id=project_id,
                description=status_summary)

            print(f"  Updated project status")

            # Create task for follow-up if there are blockers
            if validation_context['blockers']:
                task = mcp__archon__manage_task("create",
                    project_id=project_id,
                    title=f"Fix {len(validation_context['blockers'])} validation blockers",
                    description=f"Blockers from PRP execution:\n" + "\n".join(f"- {b['error'][:100]}" for b in validation_context['blockers']),
                    status="todo",
                    task_order=100)

                print(f"  Created follow-up task for blockers")
        else:
            print(f"  No existing project found - skipping update")

    except Exception as e:
        print(f"  Archon integration failed: {e}")

    print("")
else:
    print(f"ℹ️  Archon unavailable - skipping project updates")
    print("")

print(f"==========================================")
print(f"PRP Execution {'COMPLETE' if validation_success else 'INCOMPLETE'}")
print(f"==========================================")
print("")

if validation_success:
    print(f"✅ All validation passed - implementation ready!")
else:
    print(f"⚠️  Validation incomplete - see report for blockers")
    print(f"Report: prps/{feature_name}/EXECUTION_REPORT.md")

print("")
```

---

## Error Handling & Recovery

### Validation Failure Recovery

When validation fails, the loop analyzes errors against PRP Known Gotchas and applies fixes:

```python
# Example error analysis pattern
def analyze_and_fix_error(error_message: str, command: str, gotchas: str) -> bool:
    """Analyze error and attempt automatic fix using PRP gotchas."""

    # 1. Identify error type
    if "ImportError" in error_message or "ModuleNotFoundError" in error_message:
        # Check gotchas for import-related solutions
        if "install" in gotchas.lower():
            # Extract package name from error
            pkg_match = re.search(r"No module named '([^']+)'", error_message)
            if pkg_match:
                package = pkg_match.group(1)
                # Apply fix: install missing package
                Bash(f"pip install {package}")
                return True

    elif "SyntaxError" in error_message or "IndentationError" in error_message:
        # Run auto-formatter
        Bash("ruff check --fix .")
        return True

    elif "TypeError" in error_message or "AttributeError" in error_message:
        # Check gotchas for type-related solutions
        # (implementation-specific)
        pass

    # No automatic fix available
    return False
```

### Task Failure Recovery

When a task fails during implementation:

```python
# Options presented to user (in interactive mode):
# 1. Retry task (with more context)
# 2. Skip task (mark as partial implementation)
# 3. Abort execution (save progress, exit cleanly)

# In automated mode: log failure and continue
```

### Max Attempts Exhausted

When validation loop reaches max attempts without success:

```python
# Generate detailed blocker report
# Offer user options:
#   1. Continue anyway (accept partial implementation)
#   2. Manual intervention (pause for user fixes, then resume)
#   3. Abort (save progress report, exit)
```

---

## Quality Standards

Before reporting completion, verify:

- All tasks from Implementation Blueprint attempted
- Files created/modified match PRP specification
- Validation levels run in order (at least once)
- Error analysis checked PRP gotchas for solutions
- Coverage measurement attempted (even if not 70%+)
- Completion report comprehensive and actionable
- Archon project updated (if available)

---

## Success Metrics

**Complete Success**:
- All tasks completed
- All validation levels passed
- Test coverage >= 70%
- No blockers
- Archon project updated

**Partial Success**:
- Most tasks completed (>= 80%)
- Most validation passed (>= 2/3 levels)
- Some coverage measured (>= 50%)
- Blockers documented with solutions
- User can continue manually

**Failure**:
- Many tasks failed (< 50% complete)
- Critical validation failed (Level 1: syntax)
- No coverage measured
- Blockers without solutions
- Requires full retry or PRP revision

---

## Anti-Patterns to Avoid

**NEVER**:
- Skip validation loops (run all levels, even if time-consuming)
- Accept <70% coverage without documenting blocker
- Ignore Known Gotchas section (check before implementing)
- Modify files without reading them first (risk overwriting)
- Report success when validation failed (be honest about blockers)

**ALWAYS**:
- Follow task order from PRP (dependency management)
- Apply gotchas proactively (not just on failures)
- Document why each file was modified
- Track all validation attempts (audit trail)
- Generate completion report (even on failure)

---

## Notes

- This is a PROMPT file for Codex CLI, not executable Python code
- Actual implementation will be done by Codex agent executing this command
- Validation commands are extracted from PRP "Validation Loop" section
- Known Gotchas are referenced for error recovery
- Max 5 validation attempts prevents infinite loops
- Completion report includes actionable next steps

---

## File Size Check

This prompt is designed to be <50KB for Codex CLI compatibility. Current size: ~35KB (estimated).
