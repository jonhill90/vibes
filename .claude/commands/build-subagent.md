# Build Claude Code Subagent

Triggers multi-agent workflow to create a production-ready Claude Code subagent through a systematic 6-phase process.

## Usage

```bash
/build-subagent <requirement>
```

**Examples:**
- `/build-subagent Create a subagent that monitors dependency vulnerabilities`
- `/build-subagent Build a subagent for managing API documentation`
- `/build-subagent I need a subagent that formats code automatically`

## Workflow Overview

```
Phase 0: Clarification (Main Agent)
    ↓
Phase 1: Planning (claude-subagent-planner)
    ↓
Phase 2: Parallel Research (3 subagents simultaneously)
    ├─→ claude-subagent-researcher
    ├─→ claude-subagent-tool-analyst
    └─→ claude-subagent-pattern-analyzer
    ↓
Phase 3: Generation (Main Agent)
    ↓
Phase 4: Validation (claude-subagent-validator)
    ↓
Phase 5: Delivery (Main Agent)
```

## Phase 0: Clarification

**Purpose**: Gather essential context from user before autonomous workflow begins.

**Actions**:
1. Acknowledge the subagent creation request
2. Ask 2-3 targeted questions:
   - **Core Purpose**: "What should this subagent do specifically?"
   - **Archetype Hint**: "Is this for planning, building, validating, or managing tasks?"
   - **Tool Hints**: "Will it need to run commands, search code, or just read/write files?"

3. **CRITICAL**: STOP and WAIT for user responses
   - Do NOT proceed to Phase 1 without user input
   - Do NOT make assumptions to "keep things moving"
   - Do NOT create directories or invoke subagents yet

4. After user responds:
   - Determine subagent folder name (kebab-case from requirement)
   - Example: "API documentation manager" → `api-documentation-manager`

**Output**: Clear understanding of requirement + folder name

---

## Phase 1: Planning

**Purpose**: Create comprehensive requirements document.

**Invoke**: `claude-subagent-planner`

**Input to Planner**:
```
User request: [original requirement]
Clarifications: [answers from Phase 0]
Folder name: [determined kebab-case name]
Task: Create INITIAL.md in planning/[folder-name]/INITIAL.md
```

**Expected Output**:
- `planning/[subagent-name]/INITIAL.md` created
- Contains: Purpose, Archetype, Responsibilities, Tools, Protocol outline, Success criteria

**Quality Check**:
- File exists at correct location
- Archetype identified (Planner/Generator/Validator/Manager)
- Tools justified
- Success criteria measurable

**Duration**: ~2-3 minutes

---

## Phase 2: Parallel Research

**Purpose**: Conduct comprehensive research from multiple angles simultaneously.

**CRITICAL**: Invoke all 3 subagents in SINGLE message with 3 Task tool calls for true parallel execution.

### Phase 2A: Pattern Research
**Invoke**: `claude-subagent-researcher`

**Input**:
```
Read: planning/[subagent-name]/INITIAL.md
Task: Research similar patterns in examples/claude-subagent-patterns/
Output: planning/[subagent-name]/research.md
```

**Expected Output**:
- Identified 2-3 similar example subagents
- Extracted successful patterns
- Documented archetype-specific approaches
- Provided concrete recommendations

### Phase 2B: Tool Analysis
**Invoke**: `claude-subagent-tool-analyst`

**Input**:
```
Read: planning/[subagent-name]/INITIAL.md
Task: Analyze tool requirements and validate against archetype patterns
Output: planning/[subagent-name]/tools.md
```

**Expected Output**:
- Validated tool selections
- Security analysis (especially Bash access)
- Tool-to-capability mapping
- Minimal but sufficient tool set recommended

### Phase 2C: Structural Analysis
**Invoke**: `claude-subagent-pattern-analyzer`

**Input**:
```
Read: planning/[subagent-name]/INITIAL.md
Task: Extract precise structural patterns for this archetype
Output: planning/[subagent-name]/patterns.md
```

**Expected Output**:
- YAML frontmatter pattern extracted
- System prompt structure documented
- Section organization patterns
- Naming and terminology conventions

**Phase 2 Completion**: All 3 .md files created in `planning/[subagent-name]/`

**Duration**: ~3-5 minutes (parallel execution)

---

## Phase 3: Generation

**Purpose**: Synthesize all research into complete subagent definition.

**Actor**: Main Claude Code Agent (not a subagent)

**Actions**:
1. **Read all planning documents**:
   - `planning/[subagent-name]/INITIAL.md`
   - `planning/[subagent-name]/research.md`
   - `planning/[subagent-name]/tools.md`
   - `planning/[subagent-name]/patterns.md`

2. **Synthesize findings**:
   - Combine requirements with discovered patterns
   - Use structural templates from pattern analysis
   - Apply tool recommendations from tool analysis
   - Incorporate successful patterns from research

3. **Generate complete subagent**:
   - Create `.claude/agents/[subagent-name].md`
   - Follow YAML frontmatter pattern exactly
   - Structure system prompt per archetype pattern
   - Ensure all required sections present
   - Keep focused (300-700 words target)

4. **Generation Template**:
   ```markdown
   ---
   name: [from patterns.md]
   description: "[from patterns.md pattern]"
   tools: [from tools.md recommendations]
   color: [from patterns.md archetype pattern]
   ---

   # [Title from patterns]

   You are an expert [role from INITIAL.md].
   Your philosophy: **"[core principle from research.md]"**

   ## Primary Objective
   [From INITIAL.md, refined with research.md insights]

   ## Core Responsibilities
   [From INITIAL.md, organized per patterns.md structure]

   ## Working Protocol
   [From INITIAL.md outline, detailed per patterns.md format]

   ## Output Standards
   [From INITIAL.md, formatted per patterns.md templates]

   ## Remember
   [Key points from research.md and patterns.md]
   ```

**Quality Self-Check**:
- YAML valid (proper quotes, structure)
- All required sections present
- Length reasonable (300-700 words)
- Matches archetype from research

**Output**: `.claude/agents/[subagent-name].md` generated

**Duration**: ~2-3 minutes

---

## Phase 4: Validation

**Purpose**: Ensure generated subagent meets all quality standards.

**Invoke**: `claude-subagent-validator`

**Input**:
```
File: .claude/agents/[subagent-name].md
Task: Validate YAML, structure, content, pattern adherence
Iterate until passing
```

**Validation Checks**:
- YAML frontmatter valid and complete
- Required sections all present
- Content quality (length, clarity, focus)
- Pattern adherence (matches archetype examples)
- Tool appropriateness

**Iteration Loop**:
1. Validator analyzes file
2. If issues found: Provides detailed feedback
3. Main agent fixes issues based on feedback
4. Validator re-validates
5. Repeat until passing

**Expected Outcome**:
- ✅ Validation passed
- Quality score reported
- File ready for production use

**Duration**: ~2-4 minutes (including iterations)

---

## Phase 5: Delivery

**Purpose**: Provide user with complete summary and usage instructions.

**Actor**: Main Claude Code Agent

**Actions**:
1. Generate summary report
2. Provide usage examples
3. Document location and access

**Delivery Report Template**:
```markdown
# ✅ Claude Code Subagent Created Successfully

## Generated Subagent
- **Name**: [subagent-name]
- **Location**: `.claude/agents/[subagent-name].md`
- **Archetype**: [Planner/Generator/Validator/Manager]
- **Quality Score**: [X/10]

## Capabilities
[List core responsibilities from INITIAL.md]

## Tools
[List tools with justifications]

## How to Use

### Invoke Manually
Use the Task tool in Claude Code to invoke:
```
Invoke: [subagent-name]
Task: [specific task description]
```

### Proactive Activation
This subagent will automatically activate when:
[Proactive trigger from description]

## Research Artifacts
Planning documents saved in `planning/[subagent-name]/`:
- INITIAL.md - Requirements
- research.md - Pattern findings
- tools.md - Tool analysis
- patterns.md - Structural patterns

## Next Steps
1. Test the subagent with a sample task
2. Verify it produces expected outputs
3. Iterate on prompt if needed
4. Use in production workflows

## Quality Validation
✅ YAML frontmatter valid
✅ All required sections present
✅ Pattern adherence verified
✅ Tool selection appropriate
✅ Content quality meets standards

---
Generated: [timestamp]
Total workflow time: ~10-15 minutes
```

**Duration**: ~1 minute

---

## Complete Workflow Example

**User Request**: `/build-subagent Create a subagent that monitors test coverage and suggests improvements`

### Phase 0 Output:
```
I'll help you build a test coverage monitoring subagent. Let me ask a few quick questions:

1. What test framework are you using? (pytest, jest, vitest, etc.)
2. Should it just report coverage or also suggest specific tests to write?
3. Will it need to run test commands or just analyze existing coverage reports?

[WAITS FOR USER RESPONSE]
```

### User Responds:
```
1. pytest
2. Both - report and suggest
3. It should run pytest commands
```

### Remaining Phases Execute Automatically:
```
📋 Phase 1: Creating requirements (claude-subagent-planner)...
✅ Requirements complete: planning/test-coverage-monitor/INITIAL.md

⚡ Phase 2: Parallel research (3 subagents)...
✅ Research complete: research.md, tools.md, patterns.md

🔨 Phase 3: Generating subagent...
✅ Generated: .claude/agents/test-coverage-monitor.md

🔍 Phase 4: Validating quality...
✅ Validation passed (8/10)

📦 Phase 5: Ready for use!
```

---

## Integration with Task Tracking

### TodoWrite Integration
The main agent should use TodoWrite to track phases:
```
- [ ] Phase 0: Gather clarifications
- [ ] Phase 1: Requirements planning
- [ ] Phase 2: Parallel research
- [ ] Phase 3: Subagent generation
- [ ] Phase 4: Quality validation
- [ ] Phase 5: Delivery
```

### Archon Integration (Optional)
If Archon MCP is available:
1. Create Archon project for subagent creation
2. Create tasks for each phase
3. Update status as phases complete
4. Store artifacts in Archon docs

---

## Error Handling

### Phase 1 Failure
If planner fails to create INITIAL.md:
- Review error message
- Verify planning directory exists
- Retry with additional context
- If still failing, ask user for more details

### Phase 2 Partial Success
If only 1-2 of 3 subagents complete:
- Wait for all 3 to finish
- If timeout, retry failed subagent individually
- Can proceed with 2/3 if critical path (planner + researcher minimum)

### Phase 3 Generation Issues
If generation creates invalid YAML or structure:
- Re-read planning documents
- Review examples/claude-subagent-patterns/ directly
- Regenerate with stricter pattern adherence

### Phase 4 Validation Failure
If validator fails multiple times:
- Review specific feedback carefully
- Fix issues one at a time
- Compare to example files directly
- Maximum 3 iterations before escalating to user

---

## Quality Standards

Every generated subagent must meet:
- ✅ Valid YAML frontmatter (parseable)
- ✅ All required sections present
- ✅ Length: 300-700 words (acceptable: 200-1000)
- ✅ Clear philosophy statement
- ✅ Actionable responsibilities
- ✅ Step-by-step protocol
- ✅ Concrete output standards
- ✅ Archetype-appropriate tools
- ✅ Proactive trigger in description
- ✅ Pattern adherence to examples

---

## Tips for Best Results

1. **Clear Requirements**: More specific user requirements = better subagent
2. **Answer Clarifications**: Phase 0 questions help guide entire workflow
3. **Trust the Process**: Workflow is designed for autonomous execution after Phase 0
4. **Review Planning Docs**: Check `planning/[name]/` if you want to see research
5. **Iterate if Needed**: Generated subagents can be refined post-validation

---

## Related Commands

- `/generate-prp` - Create PRPs for complex features
- `/execute-prp` - Execute PRP implementations
- Task tool - Invoke specific subagents manually

---

**Command Version**: 1.0
**Created**: 2025-10-01
**Methodology**: Multi-agent orchestration with parallel research
**Expected Success Rate**: >90% for well-specified requirements
