# Create PRP

Orchestrates PRP generation from INITIAL.md: a multi-subagent system that creates comprehensive, implementation-ready PRPs through systematic research and analysis.

## Feature file: $ARGUMENTS

Generate a complete PRP with thorough research using a 5-phase multi-subagent approach. Ensure context is comprehensive to enable self-validation and first-pass implementation success.

## The 5-Phase Workflow

### Phase 0: Setup & Initialization (YOU handle this)

**Immediate Actions**:

1. ✅ Acknowledge the PRP generation request
2. ✅ Read the INITIAL.md file to understand requirements
3. ✅ Extract feature name (snake_case) from file name or content
4. ✅ Create necessary directories
5. ✅ Check Archon availability
6. ✅ Proceed to Phase 1 (no user interaction needed)

**Setup Process**:

```python
# 1. Read INITIAL.md
initial_md_path = "$ARGUMENTS"
initial_content = Read(initial_md_path)

# 2. Extract and validate feature name (SECURITY: prevent command injection)
# From file name: prps/INITIAL_user_auth.md → "user_auth"
import re

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

# 3. Create scoped directories (per-feature, not global)
Bash(f"mkdir -p prps/{feature_name}/planning")
Bash(f"mkdir -p prps/{feature_name}/examples")

# 4. Check Archon availability and setup project/tasks
# For Archon integration patterns, see: .claude/patterns/archon-workflow.md
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if archon_available:
    # Create project
    project = mcp__archon__manage_project("create",
        title=f"PRP Generation: {feature_display_name}",
        description=f"Creating comprehensive PRP from {initial_md_path}"
    )
    project_id = project["project"]["id"]

    # Create 6 tasks (one per phase/subagent)
    tasks = [
        {"title": "Phase 1: Feature Analysis", "assignee": "prp-gen-feature-analyzer", "order": 100},
        {"title": "Phase 2A: Codebase Research", "assignee": "prp-gen-codebase-researcher", "order": 90},
        {"title": "Phase 2B: Documentation Hunt", "assignee": "prp-gen-documentation-hunter", "order": 85},
        {"title": "Phase 2C: Example Curation", "assignee": "prp-gen-example-curator", "order": 80},
        {"title": "Phase 3: Gotcha Detection", "assignee": "prp-gen-gotcha-detective", "order": 75},
        {"title": "Phase 4: PRP Assembly", "assignee": "prp-gen-assembler", "order": 70}
    ]

    task_ids = []
    for task_def in tasks:
        task = mcp__archon__manage_task("create",
            project_id=project_id,
            title=task_def["title"],
            description=f"{task_def['assignee']} - Autonomous execution",
            status="todo",
            assignee=task_def["assignee"],
            task_order=task_def["order"]
        )
        task_ids.append(task["task"]["id"])
else:
    # Graceful fallback - continue without tracking
    project_id = None
    task_ids = []
    print("ℹ️ Archon MCP not available - proceeding without project tracking")

# 6. Proceed to Phase 1
```

---

### Phase 1: Feature Analysis

**Subagent**: `prp-gen-feature-analyzer`
**Mode**: AUTONOMOUS - Works without user interaction
**Duration**: 2-3 minutes

**Your Actions**:

```python
# 1. Update Archon task to "doing"
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="doing")

# 2. Prepare context for subagent
context = f'''You are analyzing an INITIAL.md file to create feature analysis for PRP generation.

**INITIAL.md Path**: {initial_md_path}
**Feature Name**: {feature_name}
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read the INITIAL.md file thoroughly
2. Extract requirements (explicit and implicit)
3. Search Archon for similar PRPs or implementations
4. Identify technical components needed
5. Make intelligent assumptions for gaps
6. Create comprehensive feature-analysis.md

**Output Path**: prps/{feature_name}/planning/feature-analysis.md
'''

# 3. Invoke analyzer
Task(subagent_type="prp-gen-feature-analyzer",
     description="Analyze INITIAL.md requirements",
     prompt=context)

# 4. Wait for completion - subagent will create prps/{feature_name}/planning/feature-analysis.md

# 5. Mark task complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="done")
```

**Expected Output**: `prps/{feature_name}/planning/feature-analysis.md`

---

### Phase 2: Parallel Research (CRITICAL PHASE - 3x SPEEDUP)

**Subagents**: THREE simultaneously
- `prp-gen-codebase-researcher`
- `prp-gen-documentation-hunter`
- `prp-gen-example-curator`

**Mode**: PARALLEL EXECUTION
**Duration**: 3-5 minutes (all run in parallel, NOT 9-15 minutes sequentially)

⚠️ **CRITICAL**: Invoke all THREE in SINGLE message with multiple Task tool calls

**Your Actions**:

```python
# 1. Update all three Archon tasks to "doing"
if archon_available:
    for i in [1, 2, 3]:  # Tasks 2A, 2B, 2C
        mcp__archon__manage_task("update", task_id=task_ids[i], status="doing")

# 2. Prepare context for each subagent

researcher_context = f'''You are searching for codebase patterns for PRP generation.

**Feature Analysis Path**: prps/{feature_name}/planning/feature-analysis.md (READ THIS FIRST)
**Feature Name**: {feature_name}
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read feature-analysis.md to understand requirements
2. Search Archon code examples for similar patterns
3. Search local codebase for similar implementations
4. Extract naming conventions, file organization, utilities
5. Create comprehensive codebase-patterns.md

**Output Path**: prps/{feature_name}/planning/codebase-patterns.md
'''

hunter_context = f'''You are finding official documentation for PRP generation.

**Feature Analysis Path**: prps/{feature_name}/planning/feature-analysis.md (READ THIS FIRST)
**Feature Name**: {feature_name}
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read feature-analysis.md to understand technologies needed
2. Search Archon knowledge base for documentation
3. Use WebSearch for gaps not in Archon
4. Find official docs with working examples
5. Create comprehensive documentation-links.md

**Output Path**: prps/{feature_name}/planning/documentation-links.md
'''

curator_context = f'''You are extracting code examples for PRP generation.

**Feature Analysis Path**: prps/{feature_name}/planning/feature-analysis.md (READ THIS FIRST)
**Feature Name**: {feature_name}
**Examples Directory**: prps/{feature_name}/examples/
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read feature-analysis.md to understand patterns needed
2. Search Archon code examples
3. Search local codebase for similar code
4. EXTRACT actual code to prps/{feature_name}/examples/ (NOT just references!)
5. Create README.md with "what to mimic" guidance
6. Create examples-to-include.md report

**Output Paths**:
- prps/{feature_name}/examples/example_*.py (2-4 code files)
- prps/{feature_name}/examples/README.md
- prps/{feature_name}/planning/examples-to-include.md
'''

# 3. ⚠️ CRITICAL: Parallel invocation - SINGLE message with THREE Task calls
# ALL THREE subagents will work simultaneously

I'm now invoking all three Phase 2 research subagents in parallel for maximum efficiency:
'''

Then invoke three Task tools in this same response:

Task(subagent_type="prp-gen-codebase-researcher",
     description="Search codebase patterns",
     prompt=researcher_context)

Task(subagent_type="prp-gen-documentation-hunter",
     description="Find official documentation",
     prompt=hunter_context)

Task(subagent_type="prp-gen-example-curator",
     description="Extract code examples",
     prompt=curator_context)

# 4. After all three complete, mark tasks done
if archon_available:
    for i in [1, 2, 3]:
        mcp__archon__manage_task("update", task_id=task_ids[i], status="done")
```

**Expected Outputs**:
- `prps/research/codebase-patterns.md`
- `prps/research/documentation-links.md`
- `prps/research/examples-to-include.md`
- `examples/{feature_name}/` directory with 2-4 code files + README.md

---

### Phase 3: Gotcha Detection

**Subagent**: `prp-gen-gotcha-detective`
**Mode**: AUTONOMOUS
**Duration**: 2 minutes

**Your Actions**:

```python
# 1. Update Archon task
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="doing")

# 2. Prepare context
context = f'''You are identifying gotchas and pitfalls for PRP generation.

**Research Documents** (READ ALL):
- prps/{feature_name}/planning/feature-analysis.md
- prps/{feature_name}/planning/codebase-patterns.md
- prps/{feature_name}/planning/documentation-links.md

**Feature Name**: {feature_name}
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read all Phase 2 research documents
2. Search Archon for known issues with technologies
3. Use WebSearch for security/performance gotchas
4. Document SOLUTIONS (not just warnings!)
5. Create comprehensive gotchas.md

**Output Path**: prps/{feature_name}/planning/gotchas.md
'''

# 3. Invoke detective
Task(subagent_type="prp-gen-gotcha-detective",
     description="Detect pitfalls and gotchas",
     prompt=context)

# 4. Wait for completion

# 5. Mark complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="done")
```

**Expected Output**: `prps/{feature_name}/planning/gotchas.md`

---

### Phase 4: PRP Assembly

**Subagent**: `prp-gen-assembler`
**Mode**: AUTONOMOUS
**Duration**: 1-2 minutes

**Before invoking assembler, perform ULTRATHINK**:

*** CRITICAL: ULTRATHINK ABOUT THE PRP ***

Review all research documents briefly:
1. Feature analysis - clear requirements?
2. Codebase patterns - sufficient guidance?
3. Documentation - official sources with examples?
4. Examples - actual code extracted?
5. Gotchas - solutions provided?

If any area seems insufficient, note it for assembler to address.

**Your Actions**:

```python
# 1. Update Archon task
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="doing")

# 2. Prepare context
context = f'''You are assembling the final PRP from all research.

**Research Documents** (READ ALL 5):
1. prps/{feature_name}/planning/feature-analysis.md
2. prps/{feature_name}/planning/codebase-patterns.md
3. prps/{feature_name}/planning/documentation-links.md
4. prps/{feature_name}/planning/examples-to-include.md
5. prps/{feature_name}/planning/gotchas.md

**Template**: prps/templates/prp_base.md (USE THIS STRUCTURE)
**Feature Name**: {feature_name}
**Examples Directory**: prps/{feature_name}/examples/
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read all 5 research documents thoroughly
2. Read prp_base.md template for structure
3. Synthesize research into coherent PRP
4. Include all documentation URLs
5. Reference examples directory
6. Incorporate all gotchas with solutions
7. Create logical task list from requirements
8. Score the PRP (must be >= 8/10)
9. If score < 8/10, document what's missing
10. Create prps/{feature_name}.md

**CRITICAL**: PRP must score 8+/10 for implementation readiness.

**Output Path**: prps/{feature_name}/{feature_name}.md (and store in Archon if available)
'''

# 3. Invoke assembler
Task(subagent_type="prp-gen-assembler",
     description="Synthesize final PRP",
     prompt=context)

# 4. Wait for completion

# 5. Mark complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="done")
```

**Expected Output**: `prps/{feature_name}.md`

---

### Phase 5: Quality Check & Delivery (YOU handle this)

**Quality Gate Check**:

For quality scoring criteria and enforcement patterns, see: `.claude/patterns/quality-gates.md`

For comprehensive validation checklist, reference: `prps/templates/prp_base.md` - Final validation Checklist section

```python
# 1. Read the generated PRP
prp_content = Read(f"prps/{feature_name}/{feature_name}.md")

# 2. Extract quality score (pattern from quality-gates.md)
import re
score_match = re.search(r'Score:\s*(\d+)/10', prp_content)
quality_score = int(score_match.group(1)) if score_match else 0

# 3. Verify minimum quality (8+/10 enforcement)
if quality_score < 8:
    print(f"⚠️ Quality Gate Failed: PRP scored {quality_score}/10 (minimum: 8/10)")
    print("\nOptions:")
    print("1. Regenerate with additional research")
    print("2. Review and improve specific sections")
    print("3. Proceed anyway (not recommended)")

    choice = input("Choose (1/2/3): ")

    if choice == "1":
        # Re-run research phases with enhanced criteria
        print("Re-running research phases...")
        # Trigger Phase 2 again
    elif choice == "2":
        # Identify and enhance weak sections
        gaps = identify_missing_sections(prp_content)
        print("\nIdentified gaps:")
        for gap in gaps:
            print(f"  - {gap}")
        # Re-run specific subagents
    elif choice != "3":
        print("❌ Invalid choice - aborting")
        exit(1)
    else:
        print("⚠️ Proceeding with quality score below threshold")
else:
    print(f"✅ Quality Gate Passed: {quality_score}/10")
    # Proceed to delivery
```

**Completion Report**:

See `.claude/patterns/quality-gates.md` for quality metrics structure.

```markdown
✅ **PRP Generated Successfully!**

**Output**: `prps/{feature_name}/{feature_name}.md`

**Quality Assessment**:
- PRP Quality Score: {quality_score}/10 {'✅' if quality_score >= 8 else '⚠️'}
- Documentation sources: {doc_count} official references
- Code examples: {example_count} files extracted with guidance
- Gotchas documented: {gotcha_count} with solutions
- Task breakdown: {task_count} tasks with clear dependencies
- Validation gates: ✅ Executable commands provided

**Research Artifacts**:
- `prps/{feature_name}/planning/feature-analysis.md`
- `prps/{feature_name}/planning/codebase-patterns.md`
- `prps/{feature_name}/planning/documentation-links.md`
- `prps/{feature_name}/planning/examples-to-include.md`
- `prps/{feature_name}/planning/gotchas.md`

**Extracted Examples**:
- `prps/{feature_name}/examples/` ({example_count} files)

**Time to Generate**: {elapsed_time} minutes

**Next Steps**:

1. **Review the PRP** (recommended):
   ```bash
   cat prps/{feature_name}/{feature_name}.md
   ```

2. **Review extracted examples** (optional but helpful):
   ```bash
   cat prps/{feature_name}/examples/README.md
   ```

3. **Execute the PRP** (when ready to implement):
   ```bash
   /execute-prp prps/{feature_name}/{feature_name}.md
   ```

4. **(Optional) Cleanup after execution**:
   ```bash
   /prp-cleanup {feature_name}
   ```

**Archon Tracking**: {if available, show project URL or note unavailable}

Would you like me to review any specific section of the PRP, or are you ready to execute it?
```

**Update Archon** (if available):

```python
# 1. Add final notes to project
mcp__archon__manage_project("update",
    project_id=project_id,
    description=f"COMPLETED: Generated PRP with quality score {quality_score}/10, {example_count} examples, {gotcha_count} gotchas documented"
)

# 2. PRP already stored by assembler as document
# No additional action needed
```

---

## Error Handling

### If Subagent Fails

```python
try:
    # Invoke subagent
    Task(subagent_type="agent-name", description="task", prompt=context)
except Exception as e:
    # Log error
    print(f"⚠️ Phase X failed: {e}")

    # Update Archon if available
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id,
            description=f"ERROR: {e}",
            status="todo"  # Reset to allow retry
        )

    # Inform user with options
    print("Would you like me to:")
    print("1. Retry this phase")
    print("2. Continue with partial results")
    print("3. Abort PRP generation")
    # Wait for user decision
```

### If Archon Unavailable

```python
# Proceed without tracking
if not archon_available:
    print("ℹ️  Archon MCP not available - proceeding without project tracking")
    # Continue workflow normally
```

### If Quality Score < 8/10

```python
if quality_score < 8:
    # Identify gaps
    gaps = identify_missing_sections(prp_content)

    # Offer regeneration
    print(f"⚠️ PRP scored {quality_score}/10 - below minimum 8/10")
    print(f"\nIdentified gaps:")
    for gap in gaps:
        print(f"  - {gap}")

    print("\nOptions:")
    print("1. Regenerate specific research phases")
    print("2. Enhance current PRP manually")
    print("3. Accept lower quality (not recommended)")
```

---

## Quality Gates

Before delivering PRP, verify:

```python
quality_checks = [
    "PRP score >= 8/10",
    "All 5 research documents created",
    "Examples extracted to examples/{feature}/ (not just references)",
    "Examples have README with 'what to mimic' guidance",
    "Documentation includes URLs with specific sections",
    "Gotchas documented with solutions (not just warnings)",
    "Task list is logical and ordered",
    "Validation gates are executable commands",
    "Codebase patterns referenced appropriately"
]

issues = []
for check in quality_checks:
    if not verify_check(check):
        issues.append(check)

if issues:
    # Handle quality issues
```

---

## Success Metrics

Track and report at end:

- ✅ Total time: {X} minutes (target: <10 minutes)
- ✅ PRP quality score: {X}/10 (target: >= 8/10)
- ✅ Research documents: 5/5 created
- ✅ Examples extracted: {count} (target: 2-4)
- ✅ Documentation sources: {count} (target: 5-7)
- ✅ Gotchas documented: {count} (target: 5-10)
- ✅ Execution ready: {yes/no}

---

## Key Differences from Old generate-prp

**OLD Approach** ❌:
- Sequential research (15-20 minutes)
- References to code (no extraction)
- Manual quality assessment
- No systematic gotcha detection
- No Archon tracking

**NEW Approach** ✅:
- Parallel research Phase 2 (3-5 minutes) = **3x faster**
- Physical code extraction to examples/
- Quality scoring with 8+/10 minimum
- Dedicated gotcha detection phase
- Full Archon project/task tracking
- Multi-subagent specialization

---

## Parallel Execution Details

**Phase 2 is the KEY INNOVATION**:

Instead of sequential:
```
Codebase research: 5 min
Documentation hunt: 4 min
Example curation: 5 min
Total: 14 minutes
```

Parallel execution:
```
All three simultaneously: max(5, 4, 5) = 5 minutes
Speedup: 14 min → 5 min = 64% faster
```

**Implementation**: Use Task tool THREE times in SINGLE message.

---

Remember: The goal is one-pass implementation success through comprehensive, production-ready PRPs with quality scores >= 8/10.
