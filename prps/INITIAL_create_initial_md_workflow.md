## FEATURE:

Build a multi-subagent workflow system for creating comprehensive INITIAL.md files that feed into the PRP generation process. This system uses 6 specialized subagents for research, analysis, and assembly - mirroring the agent-factory pattern but focused on INITIAL.md creation.

The workflow automates the process of:
1. Deep feature clarification and analysis
2. Parallel research (codebase patterns, documentation, examples)
3. Gotcha detection and security analysis
4. Final synthesis into high-quality INITIAL.md

This enables users to get production-ready INITIAL.md files in <10 minutes with minimal interaction, ready for immediate PRP generation.

## ARCHITECTURE:

### Multi-Subagent Workflow
```
User: "Help me create INITIAL.md for [feature]"
           ↓
Phase 0: Main Claude Code (2-3 clarifying questions)
           ↓
Phase 1: prp-initial-feature-clarifier (autonomous deep analysis)
           ↓
Phase 2: Parallel execution (3 agents simultaneously)
    ├─ prp-initial-codebase-researcher
    ├─ prp-initial-documentation-hunter
    └─ prp-initial-example-curator
           ↓
Phase 3: prp-initial-gotcha-detective (security & pitfalls)
           ↓
Phase 4: prp-initial-assembler (synthesis)
           ↓
Output: prps/INITIAL_{feature-name}.md (ready for /generate-prp)
```

### Directory Structure
```
vibes/
├── .claude/
│   ├── agents/                                    # Subagent definitions
│   │   ├── prp-initial-feature-clarifier.md
│   │   ├── prp-initial-codebase-researcher.md
│   │   ├── prp-initial-documentation-hunter.md
│   │   ├── prp-initial-example-curator.md
│   │   ├── prp-initial-gotcha-detective.md
│   │   └── prp-initial-assembler.md
│   │
│   └── commands/
│       └── initial-factory/
│           └── create-initial.md                  # Main orchestrator
│
├── prps/
│   ├── INITIAL_{feature-name}.md                  # Generated outputs
│   └── research/                                   # Subagent outputs
│       ├── feature-analysis.md
│       ├── codebase-patterns.md
│       ├── documentation-links.md
│       ├── examples-to-include.md
│       └── gotchas.md
```

## EXAMPLES:

### Agent-Factory Pattern (Primary Reference)
- repos/context-engineering-intro/use-cases/agent-factory-with-subagents/CLAUDE.md
  → Multi-phase orchestration workflow
  → Autonomous subagent invocation patterns
  → Parallel execution strategy
  → Quality gates and validation

- repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/
  → pydantic-ai-planner.md - Requirements gathering pattern
  → pydantic-ai-prompt-engineer.md - Specialized analysis pattern
  → pydantic-ai-tool-integrator.md - Research and synthesis pattern
  → YAML frontmatter structure with tools, color, model

### Archon Agent Examples
- infra/archon/.claude/agents/codebase-analyst.md
  → Systematic analysis methodology
  → Output format patterns
  → Search strategy patterns
  
- infra/archon/.claude/agents/library-researcher.md
  → Documentation research patterns
  → Archon MCP tool integration
  → Output structuring for downstream use

### INITIAL.md Structure
- repos/context-engineering-intro/INITIAL_EXAMPLE.md
  → Target output format
  → Section organization
  → Level of detail needed

### Command Structure
- repos/context-engineering-intro/.claude/commands/generate-prp.md
  → Research process pattern
  → Validation gates pattern
  → Quality checklist approach

## DOCUMENTATION:

### Official Documentation
- Claude Code Subagents: https://docs.claude.com/en/docs/claude-code/sub-agents
  → Subagent concept and benefits
  → YAML frontmatter format
  → Tool restriction patterns
  → Separate context window advantages

- Context Engineering Intro README: repos/context-engineering-intro/README.md
  → PRP workflow philosophy
  → Context engineering principles
  → Writing effective INITIAL.md files

### Archon MCP Integration
- Available Tools:
  - mcp__archon__perform_rag_query - Search knowledge base
  - mcp__archon__search_code_examples - Find code patterns
  - mcp__archon__rag_get_available_sources - List sources
  - mcp__archon__find_projects - Search projects
  - mcp__archon__manage_project - Project CRUD
  - mcp__archon__find_tasks - Search tasks
  - mcp__archon__manage_task - Task CRUD
  - mcp__archon__manage_document - Document CRUD

- Standard Claude Code Tools:
  - Read, Write, Grep, Glob, Bash
  - Task, TodoWrite
  - WebSearch

## COMPONENTS TO BUILD:

### 1. Six Specialized Subagents (.claude/agents/)

#### prp-initial-feature-clarifier.md
- **Purpose**: Deep feature analysis and gap identification
- **Tools**: Write, TodoWrite, mcp__archon__perform_rag_query, mcp__archon__find_projects
- **Output**: prps/research/feature-analysis.md
- **Key Behaviors**:
  - Search Archon for similar past features
  - Decompose user request into components
  - Identify explicit and implicit requirements
  - Generate intelligent clarifying questions (stored in doc, not interactive)
  - Make reasonable assumptions when gaps exist

#### prp-initial-codebase-researcher.md
- **Purpose**: Find similar implementations and patterns in codebase
- **Tools**: Read, Grep, Glob, Write, mcp__archon__search_code_examples, mcp__archon__perform_rag_query
- **Output**: prps/research/codebase-patterns.md
- **Key Behaviors**:
  - Search Archon code examples first
  - Use Grep to find similar local implementations
  - Extract naming conventions and patterns
  - Identify testing patterns
  - Document integration approaches

#### prp-initial-documentation-hunter.md
- **Purpose**: Find official docs, API references, tutorials
- **Tools**: WebSearch, Write, mcp__archon__perform_rag_query, mcp__archon__rag_get_available_sources
- **Output**: prps/research/documentation-links.md
- **Key Behaviors**:
  - Check Archon knowledge base first
  - Use WebSearch for official docs if not in Archon
  - Find quickstart guides and API references
  - Collect real-world implementation examples
  - Note version-specific considerations

#### prp-initial-example-curator.md
- **Purpose**: Identify which code examples to reference
- **Tools**: Read, Glob, Write, mcp__archon__search_code_examples
- **Output**: prps/research/examples-to-include.md
- **Key Behaviors**:
  - Search Archon for relevant examples
  - Review local examples/ folder
  - Match examples to feature requirements
  - Explain what to mimic vs. what to skip
  - Prioritize examples by relevance

#### prp-initial-gotcha-detective.md
- **Purpose**: Identify pitfalls, security concerns, common issues
- **Tools**: WebSearch, Write, mcp__archon__perform_rag_query
- **Output**: prps/research/gotchas.md
- **Key Behaviors**:
  - Search Archon for known gotchas
  - Research common pitfalls via web
  - Identify security considerations
  - Document performance concerns
  - Note rate limits and quotas

#### prp-initial-assembler.md
- **Purpose**: Synthesize all research into final INITIAL.md
- **Tools**: Read, Write, mcp__archon__manage_document
- **Output**: prps/INITIAL_{feature-name}.md
- **Key Behaviors**:
  - Read all 5 research documents
  - Synthesize into coherent INITIAL.md structure
  - Follow INITIAL_EXAMPLE.md format
  - Ensure comprehensive coverage
  - Optionally store in Archon for future reference

### 2. Main Orchestrator Command (.claude/commands/initial-factory/create-initial.md)

**Purpose**: Coordinate all subagents through workflow phases

**Workflow**:
```
Phase 0: Recognition & Basic Clarification (Main Claude Code)
- Recognize INITIAL.md creation request
- Ask 2-3 high-level questions
- Get feature name and general direction
- Create prps/research/ directory

Phase 1: Deep Feature Analysis
- Invoke prp-initial-feature-clarifier
- Wait for feature-analysis.md completion

Phase 2: Parallel Research (CRITICAL: Use parallel tool invocation)
- Invoke ALL THREE simultaneously in single message:
  - prp-initial-codebase-researcher
  - prp-initial-documentation-hunter
  - prp-initial-example-curator
- Wait for all three to complete

Phase 3: Gotcha Analysis
- Invoke prp-initial-gotcha-detective
- Wait for gotchas.md completion

Phase 4: Final Assembly
- Invoke prp-initial-assembler
- Wait for INITIAL_{feature-name}.md completion

Phase 5: Delivery
- Present INITIAL.md to user
- Provide next steps (/generate-prp command)
```

**Recognition Patterns** (trigger command):
- "Help me create INITIAL.md for [feature]"
- "I need to build INITIAL.md for [feature]"
- "Create INITIAL.md for [feature]"
- "Generate INITIAL requirements for [feature]"

**Archon Integration** (if available):
- Create Archon project for tracking
- Create tasks for each phase
- Update task status as phases complete
- Store final INITIAL.md as Archon document

## SUBAGENT YAML FRONTMATTER STRUCTURE:

Each subagent must have this format:

```yaml
---
name: "agent-name"                                # Unique identifier
description: "USE PROACTIVELY when [trigger]"     # When to invoke
model: "sonnet"                                   # Preferred model
tools: Read, Write, Grep, mcp__archon__*          # Available tools
color: blue                                       # UI color coding
---

# Agent Title

[Detailed markdown instructions following pattern from examples]

## Your Mission
[Clear objective]

## Methodology
[Step-by-step approach]

## Output Format
[Structured output specification]

## Key Principles
[Important behaviors and constraints]
```

## OTHER CONSIDERATIONS:

### Critical Implementation Details

**Parallel Execution Pattern**:
- Phase 2 MUST use parallel tool invocation
- All three agents called in single message with multiple tool uses
- NOT sequential (don't wait for one before calling next)
- This is critical for performance (<10 minute goal)

**Autonomous Operation**:
- Subagents work WITHOUT user interaction after Phase 0
- Make intelligent assumptions when information is incomplete
- Document assumptions in output
- Follow "Start simple, make it work" philosophy

**Archon Tool Usage**:
- Always check Archon FIRST before external searches
- Use mcp__archon__perform_rag_query for general knowledge
- Use mcp__archon__search_code_examples for code patterns
- Fall back to WebSearch only if Archon has no results

**Research Output Location**:
- All research goes to prps/research/
- Create directory if it doesn't exist
- Each agent writes to its specific file
- Assembler reads from all research files

**Futureproof Naming**:
- Agent names: prp-initial-{role}
- Leaves room for future workflows:
  - prp-execute-* (execution workflow)
  - prp-validate-* (validation workflow)
  - project-setup-* (project initialization)

**Quality Gates**:
- Feature description must be specific and comprehensive
- All examples must have "what to mimic" explanations
- Documentation must include working code examples
- Gotchas must include solutions, not just problems
- Final INITIAL.md should score 8+/10 for PRP generation

**Error Handling**:
- If subagent fails, log error and continue with partial results
- Main orchestrator should provide best-effort INITIAL.md
- Clearly document what's missing due to failures
- Allow user to regenerate specific phases if needed

**Validation Commands**:
```bash
# Check all agents exist
ls .claude/agents/prp-initial-*.md

# Check orchestrator exists
ls .claude/commands/initial-factory/create-initial.md

# Verify research directory structure
mkdir -p prps/research

# Test invocation (from Claude Code)
/create-initial "test feature"
```

## SUCCESS CRITERIA:

- [ ] All 6 subagent files created in .claude/agents/
- [ ] Orchestrator command created in .claude/commands/initial-factory/
- [ ] Each subagent has proper YAML frontmatter with Archon tools
- [ ] Parallel execution pattern implemented in Phase 2
- [ ] Research directory structure auto-created
- [ ] Complete workflow from user request to INITIAL.md in <10 minutes
- [ ] Generated INITIAL.md follows INITIAL_EXAMPLE.md structure
- [ ] All research documents properly formatted and comprehensive
- [ ] Archon integration works (RAG search, code examples)
- [ ] Quality score: 8+/10 for generated INITIAL.md files

## IMPLEMENTATION BLUEPRINT:

### Task 1: Create Research Directory Structure
```bash
mkdir -p prps/research
mkdir -p .claude/agents
mkdir -p .claude/commands/initial-factory
```

### Task 2: Create prp-initial-feature-clarifier.md
- Follow YAML frontmatter pattern from examples
- Include Archon tools for context search
- Implement autonomous analysis methodology
- Output to prps/research/feature-analysis.md
- Document assumptions clearly

### Task 3: Create prp-initial-codebase-researcher.md
- Search Archon code examples first
- Use Grep/Glob for local patterns
- Extract architectural patterns
- Output to prps/research/codebase-patterns.md

### Task 4: Create prp-initial-documentation-hunter.md
- Check Archon knowledge base first
- Use WebSearch for external docs
- Focus on implementation-critical sections
- Output to prps/research/documentation-links.md

### Task 5: Create prp-initial-example-curator.md
- Search Archon examples
- Review local examples/ folder
- Match to requirements
- Output to prps/research/examples-to-include.md

### Task 6: Create prp-initial-gotcha-detective.md
- Search Archon for known issues
- Research common pitfalls
- Document security considerations
- Output to prps/research/gotchas.md

### Task 7: Create prp-initial-assembler.md
- Read all 5 research files
- Synthesize into INITIAL.md structure
- Follow INITIAL_EXAMPLE.md format
- Output to prps/INITIAL_{feature-name}.md

### Task 8: Create Orchestrator Command
- Implement Phase 0-5 workflow
- Use parallel tool invocation for Phase 2
- Add Archon project/task tracking
- Include recognition patterns
- Add error handling

### Task 9: Test Complete Workflow
- Run /create-initial with test feature
- Verify all research files created
- Check INITIAL.md quality
- Validate Archon integration
- Measure total time (<10 minutes goal)

### Task 10: Documentation and Examples
- Create README for the workflow
- Add example usage
- Document troubleshooting steps
- Include quality criteria

## VALIDATION GATES:

**After Each Agent Creation**:
```bash
# Verify YAML frontmatter is valid
head -10 .claude/agents/prp-initial-{agent}.md

# Check file exists and is readable
cat .claude/agents/prp-initial-{agent}.md | head -50
```

**After Orchestrator Creation**:
```bash
# Verify command exists
ls .claude/commands/initial-factory/create-initial.md

# Check command structure
cat .claude/commands/initial-factory/create-initial.md
```

**End-to-End Test**:
```bash
# Clean slate
rm -rf prps/research prps/INITIAL_test.md

# Run workflow
# In Claude Code: /create-initial "web scraper with rate limiting"

# Verify outputs
ls prps/research/
cat prps/INITIAL_web_scraper.md

# Quality check
# - Is feature description comprehensive?
# - Are examples properly referenced?
# - Is documentation actionable?
# - Are gotchas documented with solutions?
```

## ANTI-PATTERNS TO AVOID:

- ❌ Sequential execution in Phase 2 (must be parallel)
- ❌ Interactive questions after Phase 0 (agents must be autonomous)
- ❌ Skipping Archon search and going straight to WebSearch
- ❌ Creating generic agent names (must be prp-initial-* prefix)
- ❌ Putting code in research documents (should be patterns/links)
- ❌ Missing YAML frontmatter in agent files
- ❌ Not documenting assumptions made by clarifier
- ❌ Assembler creating new content (must synthesize existing research)

## NOTES:

This is a meta-level implementation - we're using the PRP process to build tooling that makes the PRP process better. The INITIAL.md factory system will:

1. **Reduce Time**: From 30+ minutes of manual INITIAL.md writing to <10 minutes automated
2. **Improve Quality**: Systematic research ensures nothing is missed
3. **Enable Consistency**: Standard format and quality every time
4. **Scale Knowledge**: Archon integration means each INITIAL.md gets smarter
5. **Future-Ready**: Naming convention allows for additional workflows

The key innovation is using parallel subagents with separate context windows to do comprehensive research without context pollution, then synthesizing into a single high-quality artifact ready for PRP generation.

---

## ADDITIONAL REQUIREMENTS (CRITICAL ADDITIONS):

### 1. Examples Management System

**Problem**: The current PRP only REFERENCES examples, but doesn't EXTRACT or ORGANIZE them for the new feature.

**Solution**: Add example extraction and organization to the workflow:

#### Update prp-initial-example-curator.md to:
1. **Not just identify** examples to reference
2. **Extract relevant code snippets** from Archon or repos
3. **Copy/organize** into `examples/{feature-name}/` directory
4. **Create README.md** in examples folder explaining each file

**Example extraction workflow**:
```yaml
examples/{feature-name}/
├── README.md                    # What each example demonstrates
├── api_endpoint_pattern.py      # Extracted from codebase
├── validation_pattern.py        # Extracted from codebase
└── test_pattern.py              # Extracted from tests
```

**Enhanced Output Format for prp-initial-example-curator.md**:
```yaml
examples_to_extract:
  - source: repos/project/src/auth/login.py
    extract_lines: [45-67, 89-102]
    destination: examples/{feature-name}/auth_pattern.py
    description: "Authentication and validation pattern"
  
  - source: archon_code_example_id_123
    destination: examples/{feature-name}/error_handling.py
    description: "Error handling with retry logic"

extraction_actions:
  - action: copy_lines
    from_file: src/existing/feature.py
    lines: [20-45]
    to_file: examples/{feature-name}/similar_pattern.py
  
  - action: create_readme
    file: examples/{feature-name}/README.md
    content: |
      # {Feature Name} Examples
      
      ## api_pattern.py
      Demonstrates: [what it shows]
      From: [source file]
      Key points: [what to learn]
```

**Update assembler to include**:
- Path to examples folder in INITIAL.md
- Clear explanation of what each example demonstrates
- Note which files to study vs. which to copy patterns from

---

### 2. CLAUDE.md Workflow Integration

**Problem**: CLAUDE.md doesn't know about the INITIAL.md factory workflow.

**Solution**: Add comprehensive INITIAL.md workflow section to CLAUDE.md

**Required CLAUDE.md Additions**:

```markdown
# INITIAL.md Factory Workflow

## Overview
Multi-subagent system for creating comprehensive INITIAL.md files that feed into PRP generation.
Uses 6 specialized subagents with Archon MCP integration for knowledge-augmented research.

## Workflow Recognition & Triggers

**CRITICAL**: When user requests INITIAL.md creation, follow this workflow:

### Trigger Patterns (Activate workflow on ANY of these):
- "Help me create INITIAL.md for [feature]"
- "I need to build INITIAL.md for [feature]"
- "Create INITIAL.md for [feature]"
- "Generate INITIAL requirements for [feature]"
- "Write INITIAL.md for [feature]"
- "I want to make an INITIAL.md for [feature]"

### Immediate Actions:
1. ✅ Recognize this as INITIAL.md factory request
2. ✅ STOP any other work
3. ✅ Follow Phase 0 first - ask clarifying questions
4. ✅ WAIT for user responses before proceeding
5. ✅ Check Archon availability with health_check
6. ✅ Create prps/research/ directory structure
7. ✅ Begin systematic 5-phase workflow

## The 5-Phase Workflow

### Phase 0: Recognition & Basic Clarification (Main Claude Code)
**YOU** handle this phase - do NOT delegate yet.

**Actions**:
1. Acknowledge INITIAL.md creation request
2. Ask 2-3 targeted clarifying questions:
   - Primary functionality and use case
   - Technology stack or framework preference
   - Any specific integrations or APIs needed
3. **CRITICAL**: STOP and WAIT for user to respond
4. Determine feature name (snake_case format)
5. Create directory structure:
   ```bash
   mkdir -p prps/research
   mkdir -p examples/{feature-name}
   ```

### Phase 1: Deep Feature Analysis
**Subagent**: `prp-initial-feature-clarifier`
**Trigger**: Automatic after Phase 0 complete
**Mode**: AUTONOMOUS (no user interaction)

**Your Actions**:
```python
# Create Archon project if available
if archon_available:
    project = manage_project("create", 
        title=f"INITIAL.md: {feature_name}",
        description=f"Creating INITIAL.md for {feature_description}"
    )
    
    # Create tracking tasks
    tasks = [
        "Phase 1: Feature Analysis",
        "Phase 2A: Codebase Research", 
        "Phase 2B: Documentation Hunt",
        "Phase 2C: Example Curation",
        "Phase 3: Gotcha Detection",
        "Phase 4: Assembly"
    ]
    for task in tasks:
        manage_task("create", project_id=project.id, title=task)

# Invoke clarifier
invoke_subagent("prp-initial-feature-clarifier", context={
    "user_request": original_request,
    "clarifications": user_responses,
    "feature_name": feature_name,
    "archon_project_id": project.id if archon_available
})
```

**Expected Output**: `prps/research/feature-analysis.md`

### Phase 2: Parallel Research (THREE subagents simultaneously)
**CRITICAL**: Use parallel tool invocation - call all three in SINGLE message

**Your Actions**:
```python
# Update Archon tasks if available
if archon_available:
    manage_task("update", task_id=phase1_task, status="done")
    for task in phase2_tasks:
        manage_task("update", task_id=task, status="doing")

# Invoke ALL THREE in parallel (single message, multiple tool calls)
parallel_invoke([
    ("prp-initial-codebase-researcher", {
        "feature_analysis": "prps/research/feature-analysis.md",
        "feature_name": feature_name
    }),
    ("prp-initial-documentation-hunter", {
        "feature_analysis": "prps/research/feature-analysis.md"
    }),
    ("prp-initial-example-curator", {
        "feature_analysis": "prps/research/feature-analysis.md",
        "feature_name": feature_name,
        "examples_dir": f"examples/{feature_name}/"
    })
])
```

**Expected Outputs**:
- `prps/research/codebase-patterns.md`
- `prps/research/documentation-links.md`
- `prps/research/examples-to-include.md`
- `examples/{feature-name}/` directory with extracted code

### Phase 3: Gotcha Analysis
**Subagent**: `prp-initial-gotcha-detective`

**Your Actions**:
```python
# Update Archon
if archon_available:
    for task in phase2_tasks:
        manage_task("update", task_id=task, status="done")
    manage_task("update", task_id=phase3_task, status="doing")

# Invoke gotcha detective
invoke_subagent("prp-initial-gotcha-detective", context={
    "feature_analysis": "prps/research/feature-analysis.md",
    "codebase_patterns": "prps/research/codebase-patterns.md",
    "documentation": "prps/research/documentation-links.md"
})
```

**Expected Output**: `prps/research/gotchas.md`

### Phase 4: Final Assembly
**Subagent**: `prp-initial-assembler`

**Your Actions**:
```python
# Update Archon
if archon_available:
    manage_task("update", task_id=phase3_task, status="done")
    manage_task("update", task_id=phase4_task, status="doing")

# Invoke assembler
invoke_subagent("prp-initial-assembler", context={
    "feature_name": feature_name,
    "research_dir": "prps/research/",
    "examples_dir": f"examples/{feature_name}/",
    "archon_project_id": project.id if archon_available
})
```

**Expected Output**: `prps/INITIAL_{feature_name}.md`

### Phase 5: Delivery & Next Steps
**YOU** handle this phase.

**Actions**:
1. Review generated INITIAL.md
2. Present to user with summary:
   ```
   ✅ INITIAL.md created: prps/INITIAL_{feature_name}.md
   ✅ Research documents: prps/research/
   ✅ Code examples: examples/{feature_name}/
   
   Next Steps:
   1. Review the INITIAL.md for accuracy
   2. Run: /generate-prp prps/INITIAL_{feature_name}.md
   3. Then: /execute-prp PRPs/{feature_name}.md
   ```
3. Update Archon if available:
   ```python
   manage_task("update", task_id=phase4_task, status="done")
   manage_document("create", 
       project_id=project.id,
       title=f"INITIAL: {feature_name}",
       content=initial_md_content,
       document_type="spec"
   )
   ```

## Subagent Reference

All subagents located in `.claude/agents/`:
- `prp-initial-feature-clarifier.md` - Deep analysis
- `prp-initial-codebase-researcher.md` - Pattern extraction  
- `prp-initial-documentation-hunter.md` - Doc research
- `prp-initial-example-curator.md` - Example extraction & organization
- `prp-initial-gotcha-detective.md` - Pitfall identification
- `prp-initial-assembler.md` - Final synthesis

## Archon Integration

**Always check Archon first**:
```python
health_check()  # Verify Archon available
```

**If Archon available**:
- Create project for tracking
- Create tasks for each phase
- Update task status as phases progress
- Store final INITIAL.md as document
- Use RAG for research augmentation

**If Archon unavailable**:
- Proceed with workflow without tracking
- Use TodoWrite for local task management
- Skip document storage step

## Key Principles

1. **Autonomous After Phase 0**: Subagents work without user input
2. **Parallel Execution**: Phase 2 runs three agents simultaneously
3. **Archon-First**: Always search Archon before external sources
4. **Example Extraction**: Don't just reference - extract and organize
5. **Quality Over Speed**: Take time to research thoroughly
6. **Comprehensive Context**: INITIAL.md must enable one-pass PRP success

## Error Handling

If any subagent fails:
1. Log the error with context
2. Continue with partial results
3. Document what's missing in INITIAL.md
4. Offer user option to regenerate specific phase
5. Provide best-effort INITIAL.md

## Quality Gates

Before delivering INITIAL.md, verify:
- [ ] Feature description is specific and comprehensive
- [ ] All examples have "what to mimic" explanations  
- [ ] Code examples extracted to examples/{feature_name}/
- [ ] Documentation includes working code examples
- [ ] Gotchas documented with solutions
- [ ] INITIAL.md ready for immediate PRP generation
- [ ] Quality score: 8+/10

## Manual Override

User can request specific phases:
- "Regenerate codebase research for [feature]"
- "Update documentation links for [feature]"
- "Add more examples for [feature]"

Invoke the specific subagent with updated context.
```

**Where to add in CLAUDE.md**:
- Add new section after "## Common Development Workflows"
- Before "## Development Patterns"
- Make it prominent so it's discovered early

---

## IMPLEMENTATION TASK UPDATES:

### Task 5 Enhancement: prp-initial-example-curator.md

**Add to agent capabilities**:

1. **Extract Code Snippets**:
```python
def extract_code_snippet(source_file, start_line, end_line, dest_file):
    """Extract lines from source and save to destination"""
    lines = read_file(source_file)[start_line:end_line]
    write_file(dest_file, lines)
```

2. **Create Examples Directory**:
```bash
mkdir -p examples/{feature_name}
```

3. **Generate README**:
```markdown
# {Feature Name} Examples

## Files in This Directory

### api_pattern.py
**Source**: src/api/endpoints/user.py (lines 45-67)
**Demonstrates**: RESTful endpoint with validation
**Key Patterns**:
- Input validation with Pydantic
- Error handling with try/except
- Async/await pattern

### validation_pattern.py
**Source**: Archon code example #123
**Demonstrates**: Multi-step validation logic
**What to Mimic**: Error collection pattern
**What to Skip**: Specific business logic
```

4. **Update Output Format**:
Include file extraction actions, not just references

### Task 11: Update CLAUDE.md

**New task to add**:

```yaml
Task 11: Update CLAUDE.md with INITIAL Factory Workflow
- Add comprehensive INITIAL.md factory section
- Include trigger patterns
- Document 5-phase workflow
- Add Archon integration notes
- Explain subagent reference
- Include error handling procedures
- Add quality gates checklist
```

---

## UPDATED SUCCESS CRITERIA:

- [ ] All 6 subagent files created in .claude/agents/
- [ ] Orchestrator command created in .claude/commands/initial-factory/
- [ ] Each subagent has proper YAML frontmatter with Archon tools
- [ ] **prp-initial-example-curator extracts and organizes code snippets**
- [ ] **examples/{feature_name}/ directory auto-created with README**
- [ ] **CLAUDE.md updated with comprehensive workflow documentation**
- [ ] Parallel execution pattern implemented in Phase 2
- [ ] Research directory structure auto-created
- [ ] Complete workflow from user request to INITIAL.md in <10 minutes
- [ ] Generated INITIAL.md follows INITIAL_EXAMPLE.md structure
- [ ] All research documents properly formatted and comprehensive
- [ ] Archon integration works (RAG search, code examples, project tracking)
- [ ] Quality score: 8+/10 for generated INITIAL.md files

---

## VALIDATION UPDATES:

**After Example Curator Creation**:
```bash
# Verify extraction capabilities
grep -A 10 "extract_code_snippet\|copy.*file" .claude/agents/prp-initial-example-curator.md

# Check examples directory handling
grep -A 5 "examples/{feature_name}" .claude/agents/prp-initial-example-curator.md
```

**After CLAUDE.md Update**:
```bash
# Verify workflow section added
grep -A 20 "INITIAL.md Factory Workflow" CLAUDE.md

# Check trigger patterns
grep "Help me create INITIAL.md" CLAUDE.md

# Verify phase documentation
grep "Phase [0-5]:" CLAUDE.md
```

**End-to-End Validation**:
```bash
# Run workflow
# In Claude Code: /create-initial "web scraper with rate limiting"

# Verify examples extracted
ls examples/web_scraper/
cat examples/web_scraper/README.md

# Verify CLAUDE.md awareness
# Ask: "What happens when I say 'Help me create INITIAL.md for X'?"
# Should describe the 5-phase workflow
```

---

## DETAILED TASK SPECIFICATIONS

### Task 10 - DETAILED: Enhanced Example Curator Agent

The `prp-initial-example-curator.md` agent needs these specific capabilities:

#### Additional Agent Behaviors

**1. Code Extraction Function**
The agent must extract code snippets programmatically:

```markdown
## Code Extraction Methodology

When you identify relevant code examples from Archon or the codebase:

1. **For Archon Code Examples**:
   - Use `mcp__archon__search_code_examples` to find examples
   - Read the example content from results
   - Extract the relevant portions
   - Save to `examples/{feature_name}/[descriptive-name].py`

2. **For Local Codebase Examples**:
   - Use `Read` tool to get file contents
   - Identify start/end lines of relevant code
   - Extract those specific lines
   - Save to `examples/{feature_name}/[descriptive-name].py`

3. **For Multi-file Examples**:
   - Create subdirectories if needed: `examples/{feature_name}/pattern_name/`
   - Preserve relative structure for complex examples
```

**2. Examples Directory Management**

```markdown
## Directory Creation

ALWAYS create the examples directory structure:

```bash
mkdir -p examples/{feature_name}
```

Expected structure after curator runs:
```
examples/{feature_name}/
├── README.md                    # Overview of all examples
├── pattern_1.py                 # Extracted code
├── pattern_2.py                 # Extracted code
└── complex_example/             # Multi-file example
    ├── main.py
    └── helpers.py
```
```

**3. README.md Generation**

```markdown
## Examples README Template

Create `examples/{feature_name}/README.md` with this format:

```markdown
# {Feature Name} - Code Examples

This directory contains extracted code examples to reference while implementing {feature_name}.

## Quick Reference

| File | Source | Purpose |
|------|--------|---------|
| pattern_1.py | src/api/auth.py | Authentication pattern |
| pattern_2.py | Archon #123 | Validation logic |

## Detailed Examples

### pattern_1.py
**Source**: `src/api/auth.py` (lines 45-67)
**Original Context**: User authentication endpoint

**What to Mimic**:
- Token validation approach
- Error handling pattern
- Response structure

**What to Adapt**:
- Replace user-specific logic with your feature logic
- Adjust validation rules for your use case
- Keep the error handling pattern intact

**Key Patterns**:
```python
# Pattern highlights
try:
    validate_input()
    process_request()
    return success_response()
except ValidationError as e:
    return error_response(e)
```

### pattern_2.py
**Source**: Archon code example #123
**Original Context**: Multi-step validation workflow

**What to Mimic**:
- Error collection pattern (collect all errors, don't fail fast)
- Structured error responses
- Async/await handling

**What to Skip**:
- Business-specific validation rules
- Database-specific queries
- UI rendering logic

**Why This Example**:
This demonstrates how to validate multiple fields and return comprehensive error messages, which is critical for {specific reason related to feature}.
```
```

**4. Updated Output Format**

```markdown
## Output: examples-to-include.md Format

The curator's output file should include extraction actions:

```yaml
# Research Output: examples-to-include.md

## Examples Identified

### Example 1: Authentication Pattern
- **Source**: src/api/auth.py
- **Lines**: 45-67
- **Destination**: examples/{feature_name}/auth_pattern.py
- **Relevance**: Shows token validation (8/10 relevance)
- **Extraction Status**: ✅ Extracted

### Example 2: Validation Logic
- **Source**: Archon code example #123
- **Lines**: N/A (full example)
- **Destination**: examples/{feature_name}/validation_pattern.py
- **Relevance**: Error collection pattern (9/10 relevance)
- **Extraction Status**: ✅ Extracted

### Example 3: Test Pattern
- **Source**: tests/test_api.py
- **Lines**: 20-45
- **Destination**: examples/{feature_name}/test_pattern.py
- **Relevance**: Testing approach for similar feature (7/10 relevance)
- **Extraction Status**: ✅ Extracted

## Examples Directory Created

✅ `examples/{feature_name}/` created
✅ README.md generated with 3 examples documented
✅ 3 code files extracted and organized

## Usage in INITIAL.md

Reference examples directory in INITIAL.md like this:

```markdown
## EXAMPLES:

See `examples/{feature_name}/` directory for extracted code examples.
- `examples/{feature_name}/README.md` - Overview and guidance
- `examples/{feature_name}/auth_pattern.py` - Use for authentication
- `examples/{feature_name}/validation_pattern.py` - Use for input validation
- `examples/{feature_name}/test_pattern.py` - Use for testing approach
```
```
```

**5. Agent Validation Checklist**

Add to the agent instructions:

```markdown
## Before Completing, Verify:

- [ ] At least 2-4 relevant examples identified
- [ ] Examples directory created: `examples/{feature_name}/`
- [ ] Code extracted to individual files
- [ ] README.md created with detailed guidance
- [ ] Each example has "what to mimic" and "what to skip" notes
- [ ] Relevance scores provided (1-10)
- [ ] All extracted files are syntactically valid
- [ ] Examples cover different aspects (patterns, tests, validation, etc.)
```

---

### Task 11 - DETAILED: CLAUDE.md Workflow Documentation

Add this complete section to ANY CLAUDE.md file (vibes root or agent-factory specific):

```markdown
---

# 📋 INITIAL.md Factory Workflow

## Overview

Multi-subagent system for creating comprehensive INITIAL.md files that feed into the PRP generation process. This workflow automates the research and requirements gathering that typically takes 30+ minutes manually, reducing it to <10 minutes with higher quality and consistency.

**Key Innovation**: Uses 6 specialized subagents with separate context windows running in parallel to conduct comprehensive research without context pollution, then synthesizes into a single production-ready INITIAL.md.

## When to Use This Workflow

✅ **Trigger this workflow when user says ANY of these**:
- "Help me create INITIAL.md for [feature]"
- "I need to build INITIAL.md for [feature]"  
- "Create INITIAL.md for [feature]"
- "Generate INITIAL requirements for [feature]"
- "Write INITIAL.md for [feature]"
- "I want to make an INITIAL.md for [feature]"
- "Build requirements for [feature]"

❌ **Don't use this workflow for**:
- Executing/implementing existing INITIAL.md (use `/execute-prp` instead)
- Generating PRP from existing INITIAL.md (use `/generate-prp` instead)
- Creating agents (use `/create-agent` instead)

## Immediate Recognition Actions

When you detect an INITIAL.md creation request:

1. ✅ **STOP** any other work immediately
2. ✅ **ACKNOWLEDGE**: "I'll help you create a comprehensive INITIAL.md using the factory workflow"
3. ✅ **PROCEED** to Phase 0 (don't ask for permission to use the workflow)
4. ✅ **NEVER** skip Phase 0 clarifications
5. ✅ **NEVER** try to write INITIAL.md directly without the workflow

## The 5-Phase Workflow

### Phase 0: Recognition & Basic Clarification
**Who handles this**: YOU (main Claude Code, not a subagent)
**Time**: 2-3 minutes (includes waiting for user response)
**Goal**: Get just enough information to start deep research

**Your Actions**:

```markdown
**Acknowledged!** I'll use the INITIAL.md factory workflow to create a comprehensive requirements document for you.

First, I need to ask a few clarifying questions:

1. **Primary Use Case**: What is the main problem this feature solves? Who will use it?

2. **Technical Preferences**: Are there specific technologies, frameworks, or APIs you want to use? Or should I recommend based on best practices?

3. **Integration Context**: Does this need to integrate with any existing systems, databases, or services?

*[WAIT FOR USER RESPONSE - DO NOT PROCEED TO PHASE 1 YET]*
```

**After user responds**:

1. Determine feature name (use snake_case: `web_scraper`, `auth_system`, `data_pipeline`)
2. Create directory structure:
   ```bash
   mkdir -p prps/research
   mkdir -p examples/{feature_name}
   ```
3. Check Archon availability:
   ```python
   health_check()  # Verify Archon MCP is available
   ```
4. If Archon available, create project and tasks (see Archon Integration section)
5. Proceed to Phase 1

---

### Phase 1: Deep Feature Analysis
**Subagent**: `prp-initial-feature-clarifier`
**Time**: 2-3 minutes
**Mode**: AUTONOMOUS (no user interaction)

**What This Agent Does**:
- Searches Archon for similar past features
- Decomposes user request into technical components
- Identifies explicit and implicit requirements
- Makes intelligent assumptions about missing details
- Documents assumptions clearly

**Your Actions**:

```python
# Update Archon task if available
if archon_available:
    manage_task("update", task_id=phase1_task_id, status="doing")

# Invoke the clarifier
invoke_subagent("prp-initial-feature-clarifier", {
    "user_request": original_user_request,
    "clarifications": user_responses_from_phase_0,
    "feature_name": feature_name_snake_case,
    "archon_project_id": project_id if archon_available else None
})
```

**Expected Output**: `prps/research/feature-analysis.md`

**What to do while waiting**: Nothing - let the subagent work autonomously

---

### Phase 2: Parallel Research (CRITICAL PHASE)
**Subagents**: THREE running simultaneously
- `prp-initial-codebase-researcher`
- `prp-initial-documentation-hunter`  
- `prp-initial-example-curator`

**Time**: 3-5 minutes (all three run in parallel)
**Mode**: AUTONOMOUS

⚠️ **CRITICAL**: You MUST invoke all three agents in a SINGLE message using parallel tool invocation. Do NOT call them sequentially!

**What Each Agent Does**:

1. **codebase-researcher**: 
   - Searches Archon code examples
   - Greps local codebase for similar patterns
   - Documents naming conventions, file structures
   - Identifies existing integration approaches

2. **documentation-hunter**:
   - Checks Archon knowledge base first
   - Falls back to WebSearch for official docs
   - Finds API references, quickstart guides
   - Notes version-specific considerations

3. **example-curator**:
   - Finds relevant code examples in Archon and locally
   - EXTRACTS code snippets to `examples/{feature_name}/`
   - Creates README.md explaining each example
   - Documents what to mimic vs. what to skip

**Your Actions**:

```python
# Update Archon tasks
if archon_available:
    manage_task("update", task_id=phase1_task_id, status="done")
    for task in [phase2a_task_id, phase2b_task_id, phase2c_task_id]:
        manage_task("update", task_id=task, status="doing")

# Invoke ALL THREE in parallel (SINGLE message with multiple tool calls)
parallel_invoke([
    SubagentCall(
        agent="prp-initial-codebase-researcher",
        context={
            "feature_analysis": "prps/research/feature-analysis.md",
            "feature_name": feature_name,
            "archon_project_id": project_id if archon_available else None
        }
    ),
    SubagentCall(
        agent="prp-initial-documentation-hunter",
        context={
            "feature_analysis": "prps/research/feature-analysis.md",
            "feature_name": feature_name,
            "archon_project_id": project_id if archon_available else None
        }
    ),
    SubagentCall(
        agent="prp-initial-example-curator",
        context={
            "feature_analysis": "prps/research/feature-analysis.md",
            "feature_name": feature_name,
            "examples_dir": f"examples/{feature_name}/",
            "archon_project_id": project_id if archon_available else None
        }
    )
])
```

**Expected Outputs**:
- `prps/research/codebase-patterns.md`
- `prps/research/documentation-links.md`
- `prps/research/examples-to-include.md`
- `examples/{feature_name}/` directory with extracted code files
- `examples/{feature_name}/README.md`

---

### Phase 3: Gotcha Analysis
**Subagent**: `prp-initial-gotcha-detective`
**Time**: 2 minutes
**Mode**: AUTONOMOUS

**What This Agent Does**:
- Searches Archon for known issues with similar features
- Researches common pitfalls via web
- Identifies security considerations
- Documents performance concerns
- Notes rate limits, quotas, and scaling issues

**Your Actions**:

```python
# Update Archon tasks
if archon_available:
    for task in [phase2a_task_id, phase2b_task_id, phase2c_task_id]:
        manage_task("update", task_id=task, status="done")
    manage_task("update", task_id=phase3_task_id, status="doing")

# Invoke gotcha detective
invoke_subagent("prp-initial-gotcha-detective", {
    "feature_analysis": "prps/research/feature-analysis.md",
    "codebase_patterns": "prps/research/codebase-patterns.md",
    "documentation": "prps/research/documentation-links.md",
    "archon_project_id": project_id if archon_available else None
})
```

**Expected Output**: `prps/research/gotchas.md`

---

### Phase 4: Final Assembly
**Subagent**: `prp-initial-assembler`
**Time**: 1-2 minutes  
**Mode**: AUTONOMOUS

**What This Agent Does**:
- Reads ALL 5 research documents
- Synthesizes into coherent INITIAL.md structure
- Follows INITIAL_EXAMPLE.md format
- References examples directory appropriately
- Ensures PRP-ready quality (8+/10)

**Your Actions**:

```python
# Update Archon tasks
if archon_available:
    manage_task("update", task_id=phase3_task_id, status="done")
    manage_task("update", task_id=phase4_task_id, status="doing")

# Invoke assembler
invoke_subagent("prp-initial-assembler", {
    "feature_name": feature_name,
    "research_dir": "prps/research/",
    "examples_dir": f"examples/{feature_name}/",
    "archon_project_id": project_id if archon_available else None
})
```

**Expected Output**: `prps/INITIAL_{feature_name}.md`

---

### Phase 5: Delivery & Next Steps
**Who handles this**: YOU (main Claude Code)
**Time**: 1 minute
**Goal**: Present results and guide user to next steps

**Your Actions**:

```markdown
✅ **INITIAL.md Created Successfully!**

**Generated Files**:
- 📄 `prps/INITIAL_{feature_name}.md` - Comprehensive requirements document
- 📁 `examples/{feature_name}/` - Extracted code examples ({N} files)
- 📋 `prps/research/` - Supporting research (5 documents)

**Quality Check**:
- Feature description: ✅ Comprehensive
- Examples: ✅ {N} relevant examples extracted
- Documentation: ✅ Official sources referenced
- Gotchas: ✅ {N} important considerations documented
- PRP-Ready Score: {X}/10

**Next Steps**:

1. **Review the INITIAL.md** (recommended):
   ```bash
   cat prps/INITIAL_{feature_name}.md
   ```

2. **Review extracted examples** (optional but helpful):
   ```bash
   cat examples/{feature_name}/README.md
   ```

3. **Generate the PRP** (when ready):
   ```bash
   /generate-prp prps/INITIAL_{feature_name}.md
   ```

4. **Execute the feature** (after PRP generation):
   ```bash
   /execute-prp PRPs/{feature_name}.md
   ```

Would you like me to review any specific section of the INITIAL.md, or shall we proceed to PRP generation?
```

**Update Archon** (if available):

```python
# Mark Phase 4 complete
manage_task("update", task_id=phase4_task_id, status="done")

# Store INITIAL.md as document
manage_document("create",
    project_id=project_id,
    title=f"INITIAL: {feature_name}",
    content=read_file(f"prps/INITIAL_{feature_name}.md"),
    document_type="spec",
    tags=["initial", "requirements", feature_name]
)
```

---

## Subagent Reference

All subagents located in `.claude/agents/`:

| Agent | Purpose | Output File |
|-------|---------|-------------|
| `prp-initial-feature-clarifier` | Deep requirements analysis | `prps/research/feature-analysis.md` |
| `prp-initial-codebase-researcher` | Pattern extraction from codebase | `prps/research/codebase-patterns.md` |
| `prp-initial-documentation-hunter` | Official documentation research | `prps/research/documentation-links.md` |
| `prp-initial-example-curator` | Code example extraction & organization | `prps/research/examples-to-include.md` + `examples/{feature}/` |
| `prp-initial-gotcha-detective` | Security & pitfall identification | `prps/research/gotchas.md` |
| `prp-initial-assembler` | Final INITIAL.md synthesis | `prps/INITIAL_{feature_name}.md` |

**Tool Access**: All subagents have access to:
- Standard Claude Code tools: Read, Write, Grep, Glob
- Archon MCP tools: `mcp__archon__*` functions
- WebSearch: For external documentation
- Task management: TodoWrite for local tracking

**Invocation Pattern**:
```python
invoke_subagent("agent-name", {
    "context_key": "context_value",
    "feature_name": "actual_feature_name",
    "archon_project_id": "uuid-if-available"
})
```

---

## Archon Integration

### Health Check (Always First)

Before creating projects/tasks, verify Archon is available:

```python
result = health_check()
archon_available = result["status"] == "healthy"
```

### Project Creation (If Available)

After Phase 0, create Archon project for tracking:

```python
if archon_available:
    project = manage_project("create",
        title=f"INITIAL.md: {feature_name_display}",
        description=f"Creating comprehensive INITIAL.md for {feature_description}"
    )
    project_id = project["project"]["id"]
```

### Task Creation (All 7 Tasks)

Create tasks for each workflow phase:

```python
if archon_available:
    tasks = []
    
    # Phase 1
    task1 = manage_task("create",
        project_id=project_id,
        title="Phase 1: Requirements Analysis",
        description="prp-initial-feature-clarifier - Deep feature analysis",
        status="todo",
        assignee="prp-initial-feature-clarifier"
    )
    tasks.append(task1["task"]["id"])
    
    # Phase 2A-C
    task2a = manage_task("create",
        project_id=project_id,
        title="Phase 2A: Codebase Research",
        description="prp-initial-codebase-researcher - Pattern extraction",
        status="todo",
        assignee="prp-initial-codebase-researcher"
    )
    tasks.append(task2a["task"]["id"])
    
    task2b = manage_task("create",
        project_id=project_id,
        title="Phase 2B: Documentation Hunt",
        description="prp-initial-documentation-hunter - Official docs research",
        status="todo",
        assignee="prp-initial-documentation-hunter"
    )
    tasks.append(task2b["task"]["id"])
    
    task2c = manage_task("create",
        project_id=project_id,
        title="Phase 2C: Example Curation",
        description="prp-initial-example-curator - Code extraction",
        status="todo",
        assignee="prp-initial-example-curator"
    )
    tasks.append(task2c["task"]["id"])
    
    # Phase 3
    task3 = manage_task("create",
        project_id=project_id,
        title="Phase 3: Gotcha Analysis",
        description="prp-initial-gotcha-detective - Pitfall identification",
        status="todo",
        assignee="prp-initial-gotcha-detective"
    )
    tasks.append(task3["task"]["id"])
    
    # Phase 4
    task4 = manage_task("create",
        project_id=project_id,
        title="Phase 4: Assembly",
        description="prp-initial-assembler - Final INITIAL.md synthesis",
        status="todo",
        assignee="prp-initial-assembler"
    )
    tasks.append(task4["task"]["id"])
    
    # Store task IDs for status updates
    phase1_task_id = tasks[0]
    phase2a_task_id = tasks[1]
    phase2b_task_id = tasks[2]
    phase2c_task_id = tasks[3]
    phase3_task_id = tasks[4]
    phase4_task_id = tasks[5]
```

### Task Status Updates

Update task status as you progress:

```python
# When starting a phase
manage_task("update", task_id=task_id, status="doing")

# When completing a phase  
manage_task("update", task_id=task_id, status="done")

# If a phase fails
manage_task("update", task_id=task_id, status="todo",
    description=f"Original description + ERROR: {error_message}")
```

### Using Archon in Subagents

Pass project ID to subagents so they can use Archon tools:

```python
invoke_subagent("agent-name", {
    "archon_project_id": project_id,
    # ... other context
})
```

Subagents can then use:
- `mcp__archon__perform_rag_query` - Search knowledge base
- `mcp__archon__search_code_examples` - Find code patterns
- Task updates for their assigned task

### Graceful Degradation

If Archon is unavailable:
- Set `archon_available = False`
- Skip all `manage_project`, `manage_task`, `manage_document` calls
- Use `TodoWrite` for local task tracking
- Workflow proceeds normally without tracking

---

## Key Principles

### 1. Autonomous After Phase 0
Only Phase 0 requires user interaction (clarifying questions). All other phases run autonomously without asking the user questions. Subagents make intelligent assumptions based on context and best practices.

### 2. Parallel Execution (Critical)
Phase 2 MUST use parallel tool invocation - all three agents called in a single message. This is essential for meeting the <10 minute goal. Sequential execution would take 15-20 minutes.

### 3. Archon-First Strategy
Always check Archon knowledge base before external searches:
1. Try `mcp__archon__perform_rag_query` first
2. Try `mcp__archon__search_code_examples` for code
3. Fall back to `WebSearch` only if Archon has no results

This ensures we leverage accumulated knowledge and reduces external API calls.

### 4. Example Extraction (Not Just References)
The example-curator agent must EXTRACT code, not just reference it:
- Copy actual code files to `examples/{feature_name}/`
- Create comprehensive README explaining each example
- Make examples immediately usable for implementation

### 5. Quality Over Speed
While targeting <10 minutes, don't sacrifice quality:
- Better to take 12 minutes with comprehensive research
- Than to rush and deliver incomplete INITIAL.md
- The downstream PRP generation and execution depend on quality here

### 6. Make Assumptions Explicit
When subagents make assumptions (they will need to):
- Document the assumption clearly
- Explain the reasoning
- Note if user should validate later

### 7. Synthesis, Not Duplication
The assembler agent synthesizes research, doesn't copy/paste:
- Transform research into INITIAL.md structure
- Connect dots between different research findings
- Add narrative that explains the "why" not just "what"

---

## Error Handling

### If a Subagent Fails

```python
try:
    invoke_subagent("agent-name", context)
except SubagentError as e:
    # Log the error
    log_error(f"Phase X failed: {e}")
    
    # Update Archon task if available
    if archon_available:
        manage_task("update", task_id=task_id, status="todo",
            description=f"ERROR: {e}")
    
    # Continue with partial results
    proceed_to_next_phase_with_note(f"Phase X incomplete due to: {e}")
```

### If Archon Unavailable

```python
if not archon_available:
    # Use TodoWrite for local tracking
    TodoWrite("Phase 1: Requirements Analysis - STARTED")
    
    # Proceed with workflow
    invoke_subagent("prp-initial-feature-clarifier", {
        # Don't pass archon_project_id
        "feature_name": feature_name,
        # ...
    })
    
    TodoWrite("Phase 1: Requirements Analysis - COMPLETED")
```

### If User Abandons Mid-Workflow

Research files remain in `prps/research/` and can be resumed:
- Check which phase was last completed
- Resume from next phase
- User can also manually review research files

---

## Quality Gates

Before delivering INITIAL.md to user in Phase 5, verify:

- [ ] **Feature description is comprehensive** (not vague or missing key details)
- [ ] **All examples extracted** (not just referenced - actual files exist)
- [ ] **Examples have "what to mimic" guidance** (not just raw code dumps)
- [ ] **Documentation includes working examples** (not just conceptual explanations)
- [ ] **Gotchas documented with solutions** (not just "watch out for X")
- [ ] **INITIAL.md follows INITIAL_EXAMPLE.md structure** (correct sections, format)
- [ ] **Ready for immediate PRP generation** (no placeholders, TODOs, or gaps)
- [ ] **Quality score: 8+/10** (subjective but important - if you're not confident, iterate)

If any of these fail, either:
1. Regenerate the failing phase/agent
2. Document the gap clearly in INITIAL.md
3. Offer user option to iterate

---

## Manual Override

User can request specific phase regeneration:

```markdown
User: "Regenerate codebase research for web_scraper"

Response:
I'll re-run the codebase researcher for your web scraper feature.

[invoke_subagent("prp-initial-codebase-researcher", {...})]
```

User can also request additions:

```markdown
User: "Add more examples for web_scraper"

Response:
I'll expand the examples collection for your web scraper feature.

[invoke_subagent("prp-initial-example-curator", {
    "mode": "expand",
    "existing_examples": "examples/web_scraper/",
    # ...
})]
```

---

## Common Questions

### Q: Can I skip phases?
**A**: No. Each phase builds on the previous. Skipping creates gaps that hurt PRP quality.

### Q: Can I run phases sequentially instead of parallel in Phase 2?
**A**: Technically yes, but strongly discouraged. It doubles the time and defeats the purpose of separate context windows.

### Q: What if Archon doesn't have relevant information?
**A**: Subagents fall back to WebSearch and local codebase search. That's expected and fine.

### Q: Can I modify the INITIAL.md after it's generated?
**A**: Yes! It's a starting point. Review and refine before running `/generate-prp`.

### Q: How do I know if INITIAL.md is good enough?
**A**: Use the quality gates checklist above. If 8+ criteria pass, you're good. If not, iterate.

---

## Troubleshooting

### "No examples found"
**Likely cause**: Feature is very novel, no similar patterns exist
**Solution**: example-curator should explain this and suggest manual example collection

### "Research files incomplete"
**Likely cause**: Subagent failed mid-execution
**Solution**: Check error logs, re-run specific phase

### "INITIAL.md too vague"
**Likely cause**: Phase 0 clarifications were insufficient
**Solution**: Ask user follow-up questions, re-run Phase 1 with better context

### "Examples don't match feature"
**Likely cause**: Curator misunderstood requirements
**Solution**: Review feature-analysis.md, re-run curator with corrected understanding

---

## Success Metrics

A successful INITIAL.md factory run achieves:
- ✅ Total time: <10 minutes (excluding user response time in Phase 0)
- ✅ Quality score: 8+/10 (comprehensive, actionable, well-researched)
- ✅ Examples: 2-4 relevant code examples extracted
- ✅ Documentation: 3-5 authoritative sources referenced
- ✅ Gotchas: 2-5 important considerations documented
- ✅ PRP generation: Works on first attempt without needing clarifications
- ✅ User satisfaction: User feels confident proceeding to implementation

---
```

**Placement in CLAUDE.md**:
- Add after "## Common Development Workflows" section
- Before "## Development Patterns" section  
- Make it prominent so it's discovered early in the file

**Alternative placement options**:
1. Create dedicated `CLAUDE_INITIAL_FACTORY.md` and reference from main CLAUDE.md
2. Add to agent-factory CLAUDE.md if this is factory-specific
3. Add to root vibes CLAUDE.md if this is system-wide

---

## Implementation Notes for Task 11

When implementing this task:

1. **Check which CLAUDE.md to update**:
   ```bash
   # If this is for vibes root
   vim /workspace/vibes/CLAUDE.md
   
   # If this is for agent-factory specifically
   vim /workspace/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/CLAUDE.md
   ```

2. **Find insertion point**:
   ```bash
   grep -n "## Common Development Workflows\|## Development Patterns" CLAUDE.md
   # Insert the new section between these two
   ```

3. **Verify after addition**:
   ```bash
   # Check section exists
   grep "INITIAL.md Factory Workflow" CLAUDE.md
   
   # Check trigger patterns
   grep "Help me create INITIAL.md" CLAUDE.md
   
   # Check phase documentation  
   grep "Phase [0-5]:" CLAUDE.md
   
   # Verify quality gates
   grep "Quality Gates" CLAUDE.md
   ```

4. **Test awareness**:
   - Start new Claude Code session
   - Ask: "What happens when I say 'Help me create INITIAL.md for a web scraper'?"
   - Should describe the 5-phase workflow in detail
   - Should NOT ask "Would you like me to use the factory?" (should just use it)

---

