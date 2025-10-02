---
name: "[Workflow Name]"
description: "[One-line description of what this workflow accomplishes and when to use it]"
---

# [Workflow Name] - Orchestration Workflow

[2-3 sentence overview of what this workflow does, what it transforms (input → output), and its primary value proposition]

**Core Philosophy**: [One sentence capturing the workflow's guiding principle]

---

## 🎯 Trigger Recognition

**When to invoke this workflow:**

This workflow should be recognized and triggered when user requests match these patterns:

- "[Pattern 1 that indicates this workflow]"
- "[Pattern 2 that indicates this workflow]"
- "[Pattern 3 that indicates this workflow]"
- Any request mentioning [key concepts] + [action verbs]

**Recognition Rules**:
1. [Rule for when to trigger this workflow]
2. [Rule for what takes precedence]
3. [Rule for edge cases]

---

## 🔄 Complete [N]-Phase Workflow

### Phase 0: [Initial Phase Name] (if needed)

**Mode**: [INTERACTIVE | AUTONOMOUS | HYBRID]
**Actor**: [Main Claude Code | Specific Subagent | User]
**Duration**: [Estimated time]

**Trigger**: [What causes this phase to start]

**Actions**:
```
1. [Action 1]
   - [Sub-action or detail]
   - [Sub-action or detail]

2. [Action 2]
   ⚠️ CRITICAL: [Important constraint or requirement]

3. [Action 3]

4. [Completion criteria]
```

**Integration Points** (if applicable):
```python
# Archon integration example (if used)
project = mcp__archon__manage_project(
    action="create",
    title="[Project Name]",
    description="[Description]"
)

# Task creation for tracking
tasks = [
    {"title": "[Task 1]", "assignee": "[agent]", "task_order": 100},
    {"title": "[Task 2]", "assignee": "[agent]", "task_order": 90},
]

for task in tasks:
    mcp__archon__manage_task(action="create", project_id=project_id, **task)
```

**Quality Gate**:
- ✅ [Criterion 1 that must be met]
- ✅ [Criterion 2 that must be met]

---

### Phase 1: [Phase Name]

**Mode**: AUTONOMOUS
**Subagent**: `[subagent-name]` (or "Main Claude Code")
**Duration**: [Estimated time]

**Actions**:
```
1. [If Archon available]: Update Task [N] to status="doing"

2. [Primary action of this phase]
   - [Detail 1]
   - [Detail 2]

3. [Subagent invocation OR direct implementation]

4. [If Archon available]: Update Task [N] to status="done"
```

**Input**: [What this phase receives]
**Output**: [What this phase produces - exact file paths]

**Success Criteria**:
- ✅ [Deliverable 1 created]
- ✅ [Quality standard met]
- ✅ [Integration point satisfied]

---

### Phase 2: [Phase Name] - PARALLEL EXECUTION ⚡

**Mode**: PARALLEL - [N] subagents work simultaneously
**Duration**: [Estimated time]

**CRITICAL: Parallel Invocation Pattern**

⚠️ **YOU MUST invoke all [N] subagents in a SINGLE message with multiple Task tool uses**:

```
❌ WRONG (Sequential):
1. Invoke subagent-1, wait for completion
2. Then invoke subagent-2, wait for completion
3. Then invoke subagent-3, wait for completion

✅ RIGHT (Parallel):
Send ONE message containing [N] Task tool invocations

Steps:
1. [If Archon available]: Update Tasks [X, Y, Z] to "doing"
2. Invoke ALL [N] subagents in parallel (single message):
   - [subagent-1]
   - [subagent-2]
   - [subagent-3]
3. Wait for all to complete
4. [If Archon available]: Update Tasks to "done"
```

#### 2A: [Subworkflow A]

**Subagent**: `[subagent-a-name]`
**Input**: [What it reads]
**Output**: [What it creates - exact path]
**Content**: [What the output contains]

#### 2B: [Subworkflow B]

**Subagent**: `[subagent-b-name]`
**Input**: [What it reads]
**Output**: [What it creates - exact path]
**Content**: [What the output contains]

#### 2C: [Subworkflow C]

**Subagent**: `[subagent-c-name]`
**Input**: [What it reads]
**Output**: [What it creates - exact path]
**Content**: [What the output contains]

**Phase 2 Complete When**: All [N] subagents report completion

**Parallel Execution Checklist**:
- [ ] All subagents have independent inputs (no dependencies on each other)
- [ ] All subagents write to different files (no conflicts)
- [ ] All subagents receive complete context in their prompts
- [ ] All subagents invoked in SINGLE message with multiple tool calls

---

### Phase 3: [Phase Name]

**Actor**: [Main Claude Code | Specific Subagent]
**Mode**: AUTONOMOUS
**Duration**: [Estimated time]

**Actions**:
```
1. [If Archon available]: Update Task [N] to status="doing"

2. READ all required inputs:
   - [file/path/1]
   - [file/path/2]
   - [file/path/3]

3. [If Archon available]: Use RAG for [research needs]
   - mcp__archon__rag_search_knowledge_base(query="[keywords]")
   - mcp__archon__rag_search_code_examples(query="[pattern]")

4. [Core implementation work]:
   - [Step 1]
   - [Step 2]
   - [Step 3]

5. [Final structure/organization]

6. [If Archon available]: Update Task [N] to status="done"
```

**Quality Gate**:
- ✅ [Requirement 1 verified]
- ✅ [Requirement 2 verified]

---

### Phase [N]: [Final Phase Name]

**Actor**: [Who performs this phase]
**Mode**: AUTONOMOUS
**Duration**: [Estimated time]

**Actions**:
```
1. [If Archon available]: Update final task to status="doing"

2. [Finalization work]:
   - [Step 1]
   - [Step 2]

3. [If Archon available]:
   - Update task to status="done"
   - [Any final Archon updates]

4. Provide user with summary:
   - [Key deliverable 1]
   - [Key deliverable 2]
   - [Next steps]
```

---

## 📁 Expected Output Structure

Every successful workflow run produces:

```
[output-directory]/
├── [subdirectory-1]/
│   ├── [file-1]        # [Description]
│   ├── [file-2]        # [Description]
│   └── [file-3]        # [Description]
├── [file-a]            # [Description]
├── [file-b]            # [Description]
└── [final-deliverable] # [Description]
```

---

## 🛡️ Quality Assurance

### Every Workflow Run MUST Have:
1. **[Quality requirement 1]** - [Why it matters]
2. **[Quality requirement 2]** - [Why it matters]
3. **[Quality requirement 3]** - [Why it matters]
4. **[Quality requirement 4]** - [Why it matters]

### Pre-Delivery Checklist:
- [ ] [Deliverable 1] meets specifications
- [ ] [Deliverable 2] complete and tested
- [ ] [Integration point] verified
- [ ] [Documentation] updated
- [ ] [Quality gate] passed

---

## 🚨 Critical Rules

### ALWAYS:
- ✅ [Critical requirement 1]
- ✅ [Critical requirement 2]
- ✅ [Critical requirement 3]
- ✅ Use parallel invocation when [condition]
- ✅ [Archon integration requirement]

### NEVER:
- ❌ [Anti-pattern 1]
- ❌ [Anti-pattern 2]
- ❌ Invoke subagents sequentially when parallel execution is needed
- ❌ [Anti-pattern 3]
- ❌ [Anti-pattern 4]

---

## 🔧 Error Handling

If any phase fails:
```
1. Log error with full context
2. [If Archon available]: Add note to failed task with error details
3. Attempt automatic recovery if possible:
   - [Recovery strategy 1]
   - [Recovery strategy 2]
4. If recovery fails: Ask user for guidance
5. Continue with partial implementation if possible
6. Document limitations in [final deliverable]
```

### Graceful Degradation:
- **If Archon unavailable**: [Fallback behavior]
- **If [subagent] fails**: [Fallback behavior]
- **If [integration] fails**: [Fallback behavior]

---

## 📊 Success Metrics

- **Time to Completion**: Target [X] minutes for standard cases
- **Phases Complete**: All [N] phases must complete successfully
- **Validation**: [X]% of requirements tested
- **User Intervention**: Minimize to [when/where]

---

## 🎯 Invocation Examples

### Example 1: [Simple Use Case]

**User**: "[Example user request]"

**Phase 0 - [Initial Phase]**:
```
[What Claude responds with]

[Questions to ask, if interactive]

[WAIT FOR USER RESPONSE - if interactive]
```

**After [trigger event]**:
```
[Status update to user]

📋 Phase 1: [Phase name]...
[Invoke relevant agent/action]

⚙️ Phase 2: [Phase name] (parallel)...
[Invoke N subagents in SINGLE message]

🔨 Phase 3: [Phase name]...
[Main implementation]

✅ Phase N: [Final phase]...
[Completion work]

🎉 [Workflow] Complete!
Location: [output location]
```

### Example 2: [Complex Use Case]

**User**: "[More complex request with specific requirements]"

**Phase 0 - [Initial Phase]**:
```
[Initial response]

[Clarifying questions]

[WAIT FOR USER RESPONSE]
```

[Process continues autonomously through all phases]

---

## 🔍 Monitoring & Status Updates

Provide clear progress indicators to user:
```
✅ Phase 0: [Phase name] Complete
✅ Phase 1: [Phase name] Complete ([deliverable] created)
⏳ Phase 2: [Phase name] ([N] subagents working in parallel...)
  ✅ [Subagent A]: Complete
  ✅ [Subagent B]: Complete
  ✅ [Subagent C]: Complete
⏳ Phase 3: [Phase name] in progress...
⏳ Phase N: [Final phase] pending...
```

---

## 📝 Archon Integration Details

When Archon is available, this workflow:
1. Creates a project for [purpose]
2. Creates [N] tasks (one per phase/subphase)
3. Updates task status as phases progress
4. Uses RAG for [what documentation/patterns]
5. Stores final notes about [what information]

When Archon is unavailable:
- Workflow still executes completely
- No task tracking (acceptable)
- No RAG assistance (use WebSearch instead)
- All core functionality preserved

---

## 🎨 Advanced Features

### Debug Mode
Enable with: "[Trigger phrase for debug mode]"
- Verbose logging from all subagents
- Intermediate outputs preserved
- Step-by-step confirmation
- Performance metrics

### Custom Workflows
Users can request:
- Specific subagent configurations
- Alternative phase sequences
- Integration with existing [systems]
- Custom validation criteria

---

## 🔀 Decision Trees

### When to Use Parallel vs Sequential Execution

**Use PARALLEL when**:
```
✅ Tasks are independent (don't depend on each other's output)
✅ Tasks work on different files (no conflicts)
✅ Tasks can be clearly specified upfront
✅ You want to minimize total execution time
```

**Use SEQUENTIAL when**:
```
❌ Task B depends on output from Task A
❌ Tasks modify the same file
❌ You need to review Task A before starting Task B
❌ Tasks require iterative refinement
```

### Parallel Invocation Pattern

**Pattern**: Single message with multiple Task tool calls

```markdown
I'm executing [N] tasks in parallel:

[Brief explanation of what each task does]

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>[5-10 word description]</description>
    <prompt>
You are [subagent-name].

Input: [What to read]
Output: [Where to write]
Task: [What to do]

[Detailed instructions...]
    </prompt>
    <subagent_type>[subagent-type]</subagent_type>
  </parameters>
</tool_use>

[Repeat for each parallel task]
```

---

## 📋 Markdown Communication Protocol

### Between Phases
Each phase communicates via markdown files:

**Producer creates**:
```markdown
# [Document Title]

## [Section with specific information]
[Content that consumer needs]

## [Another section]
[More required information]
```

**Consumer reads**:
- Uses Read tool to access producer's output
- Extracts necessary information
- Validates completeness before proceeding
- Uses exact paths specified in workflow

### File Naming Conventions
- `[name].md` - Planning/specification documents
- `[name]_REPORT.md` - Status/validation reports
- `INITIAL.md` - First requirements document
- `README.md` - Final user-facing documentation

---

## 🧪 Testing the Workflow

### Validation Levels

**Level 1: Structure**
- [ ] All required directories created
- [ ] All required files present
- [ ] File naming conventions followed

**Level 2: Content**
- [ ] All markdown files have required sections
- [ ] All specifications complete
- [ ] All integrations documented

**Level 3: Functional**
- [ ] [Workflow-specific functional test]
- [ ] [Workflow-specific functional test]
- [ ] End-to-end execution successful

**Level 4: Integration**
- [ ] Archon integration works (if available)
- [ ] [External integration 1] verified
- [ ] [External integration 2] verified

---

This orchestrator ensures consistent, high-quality [deliverable] through a proven [N]-phase workflow with specialized subagents, parallel execution, and comprehensive validation.

---

## Template Usage Instructions

When creating a new workflow from this template:

1. **Define the workflow purpose** - What transformation does it perform?
2. **Identify all phases** - Break down the work into logical phases
3. **Determine parallelization opportunities** - Which phases can run simultaneously?
4. **Specify inputs/outputs clearly** - Document exact file paths for all artifacts
5. **Create decision trees** - When to use this workflow vs alternatives
6. **Define quality gates** - What must be true at each phase completion
7. **Plan error handling** - What happens when things fail
8. **Document Archon integration** - How does task tracking work
9. **Add examples** - Show common use cases
10. **Test end-to-end** - Verify the workflow works before using in production

**Key Principles**:
- **Clarity**: Every phase should have clear inputs, outputs, and success criteria
- **Autonomy**: Minimize user interaction after initial clarification
- **Resilience**: Handle failures gracefully with clear fallback strategies
- **Observability**: Keep users informed of progress at each phase
- **Quality**: Never sacrifice quality for speed - validate thoroughly
