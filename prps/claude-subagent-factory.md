name: "Claude Code Subagents Factory"
description: |

## Purpose
Build a simple factory system that generates Claude Code subagent definition files (`.claude/agents/*.md`) based on user requirements. This factory creates specialized markdown files that define Claude Code subagents, enabling rapid creation of focused AI assistants.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and patterns
2. **Validation Loops**: Provide executable validation the AI can run
3. **Information Dense**: Use proven patterns from existing subagents
4. **Progressive Success**: Start simple, validate structure, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Create a slash command `/generate-subagent` that generates complete, production-ready Claude Code subagent definition files following established patterns and best practices.

## Why
- **Ease of Use**: Dramatically simplifies creating new specialized subagents
- **Consistency**: Ensures all generated subagents follow proven patterns
- **Context Engineering**: Each subagent becomes a focused, expert assistant
- **Productivity**: Reduces subagent creation from 30+ minutes to < 5 minutes
- **Quality**: Leverages existing, tested patterns from real implementations

## What
A slash command that:
1. Takes a natural language description of what the subagent should do
2. Analyzes requirements and determines appropriate structure
3. Generates a complete `.claude/agents/[name].md` file with:
   - Valid YAML frontmatter (name, description, tools, color)
   - Focused system prompt (100-500 words)
   - Clear responsibilities and working protocol
   - Appropriate tool selection
   - Integration guidelines
4. Validates the generated file structure and YAML syntax
5. Saves to `.claude/agents/` directory

### Success Criteria
- [ ] Slash command `/generate-subagent` exists and works
- [ ] Generated files have valid YAML frontmatter
- [ ] System prompts follow established patterns
- [ ] Tool selection is minimal and appropriate
- [ ] Generated agents work when invoked in Claude Code
- [ ] Validation catches malformed YAML or structure issues
- [ ] Generated files match quality of hand-crafted examples

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window

- url: https://docs.anthropic.com/en/docs/claude-code
  why: Official Claude Code documentation

- url: https://docs.anthropic.com/en/docs/claude-code/subagents
  why: Subagents guide - how they work, when to use them

- url: https://docs.anthropic.com/en/docs/claude-code/custom-agents
  why: Creating custom agents, tool access, frontmatter format

- file: examples/claude-subagent-patterns/README.md
  why: Comprehensive pattern analysis and structural guidelines
  critical: Contains archetype patterns, tool selection strategy, quality criteria

- file: .claude/agents/documentation-manager.md
  why: Example of manager/coordinator archetype
  pattern: Proactive triggers, tool selection, working protocol

- file: .claude/agents/validation-gates.md
  why: Example of validator/tester archetype
  pattern: Validation checklist, iterative process, quality gates

- file: examples/claude-subagent-patterns/pydantic-ai-planner.md
  why: Example of planner/analyst archetype
  pattern: Requirements gathering, autonomous operation, simplicity principles

- file: examples/claude-subagent-patterns/pydantic-ai-prompt-engineer.md
  why: Example of generator/builder archetype
  pattern: System prompt structure, output standards

- file: examples/claude-subagent-patterns/pydantic-ai-validator.md
  why: Example of validator archetype with comprehensive testing approach
  pattern: Validation workflow, quality metrics

- docfile: INITIAL.md
  why: Original requirements specification for this factory
  critical: Keep it simple - single file generator, not multi-phase workflow
```

### Current Codebase tree
```bash
vibes/
├── .claude/
│   ├── agents/
│   │   ├── documentation-manager.md    # Existing vibes agents
│   │   └── validation-gates.md
│   └── commands/
│       ├── generate-prp.md             # Example slash command
│       ├── execute-prp.md              # Example slash command
│       ├── execute-parallel.md
│       └── prep-parallel.md
├── examples/
│   └── claude-subagent-patterns/
│       ├── README.md                   # Pattern documentation
│       ├── pydantic-ai-planner.md      # Planner archetype
│       ├── pydantic-ai-prompt-engineer.md
│       ├── pydantic-ai-tool-integrator.md
│       ├── pydantic-ai-dependency-manager.md
│       ├── pydantic-ai-validator.md
│       ├── documentation-manager.md
│       └── validation-gates.md
├── prps/
│   ├── templates/
│   │   └── prp_base.md
│   └── EXAMPLE_multi_agent_prp.md
├── INITIAL.md                          # This feature's requirements
└── CLAUDE.md                           # Global instructions
```

### Desired Codebase tree with files to be added
```bash
vibes/
├── .claude/
│   └── commands/
│       └── generate-subagent.md        # NEW: Slash command for factory
└── [No other files needed - keep it simple!]
```

### Known Gotchas & Critical Patterns

```yaml
YAML Frontmatter Requirements:
  # CRITICAL: Must start file with valid YAML frontmatter
  # Example:
  ---
  name: kebab-case-name
  description: "Brief description. USE PROACTIVELY when [trigger]. Works autonomously."
  tools: Read, Write, Edit, Grep, Glob
  color: blue
  ---
  # NOTE: Description MUST include proactive trigger for auto-invocation
  # GOTCHA: Tools are comma-separated, NO quotes around individual tools

Tool Selection Strategy:
  # PATTERN: Minimal tool access - only what's needed
  # Common combinations:
  # - Planner: Read, Write, Grep, Glob, WebSearch, TodoWrite
  # - Builder: Read, Write, Edit, MultiEdit
  # - Validator: Read, Bash, TodoWrite, Edit
  # - Manager: Read, Write, Edit, MultiEdit, Grep, Glob
  # GOTCHA: Bash access requires strong justification (security)

System Prompt Structure (from README.md):
  # REQUIRED sections in order:
  # 1. Identity statement: "You are an expert [role] specializing in [domain]"
  # 2. Philosophy: Your philosophy: **"[Core principle]"**
  # 3. Primary Objective: Clear purpose statement
  # 4. Simplicity Principles: 3-5 guiding principles
  # 5. Core Responsibilities: Detailed breakdown
  # 6. Working Protocol: Step-by-step process
  # 7. Output Standards: What it produces
  # 8. Integration: How it works with other agents
  # 9. Remember: Key reminders
  # GOTCHA: Keep total system prompt 100-500 words for focus

Naming Conventions:
  # PATTERN: kebab-case for all names
  # PATTERN: Use prefixes for related agents (e.g., pydantic-ai-*)
  # PATTERN: Name should indicate purpose clearly

Color Selection:
  # Available: blue, green, orange, red, purple
  # PATTERN: Use consistently for related agents
  # Example: All pydantic-ai-* agents use same color family

Description Format:
  # REQUIRED format:
  # "[What it does]. USE PROACTIVELY when [trigger condition]. [Autonomy level]."
  # Example: "Testing specialist. USE PROACTIVELY when code changes are made. Works autonomously."
  # CRITICAL: Without proactive trigger, agent won't auto-invoke
```

## Implementation Blueprint

### Task 1: Create Slash Command File
**CREATE** `.claude/commands/generate-subagent.md`

**Purpose**: Define the slash command that Claude Code will execute

**Structure**:
```markdown
# Generate Subagent

Generate a Claude Code subagent definition file based on requirements.

## Subagent Requirements: $ARGUMENTS

## Generation Process

1. **Analyze Requirements**
   - Parse the user's description
   - Identify the agent archetype (planner/builder/validator/manager)
   - Determine required tools based on responsibilities
   - Select appropriate color
   - Define proactive trigger condition

2. **Reference Patterns**
   - Read examples/claude-subagent-patterns/README.md for structural guidance
   - Review similar archetype example for pattern matching
   - Extract proven patterns for responsibilities and protocols

3. **Generate YAML Frontmatter**
   - Create kebab-case name from description
   - Write description with USE PROACTIVELY trigger
   - List minimal required tools
   - Assign color

4. **Generate System Prompt**
   - Identity statement (role and domain)
   - Philosophy in bold quotes
   - Primary objective
   - 3-5 simplicity principles
   - Core responsibilities (categorized)
   - Working protocol (step-by-step)
   - Output standards
   - Integration guidelines
   - Remember section

5. **Validate Structure**
   - YAML frontmatter is valid
   - All required sections present
   - Tools are from approved list
   - Description has proactive trigger
   - System prompt is focused (100-500 words)

6. **Save File**
   - Save to .claude/agents/[kebab-case-name].md
   - Confirm creation
   - Show file path and next steps

## Quality Checks
- [ ] YAML frontmatter is syntactically valid
- [ ] Name is kebab-case
- [ ] Description includes proactive trigger
- [ ] Tools are minimal and appropriate
- [ ] System prompt follows established structure
- [ ] All required sections present
- [ ] Markdown formatting is correct
- [ ] File saved to correct location
```

### Task 2: Add Archetype Detection Logic
The slash command should recognize common patterns:

```yaml
Planner/Analyst Indicators:
  keywords: [requirements, planning, research, analysis, gathering]
  tools: Read, Write, Grep, Glob, WebSearch, TodoWrite
  example: pydantic-ai-planner.md

Builder/Generator Indicators:
  keywords: [generate, create, build, implement, code]
  tools: Read, Write, Edit, MultiEdit
  example: pydantic-ai-prompt-engineer.md

Validator/Tester Indicators:
  keywords: [test, validate, verify, check, quality]
  tools: Read, Bash, TodoWrite, Edit
  example: validation-gates.md

Manager/Coordinator Indicators:
  keywords: [manage, maintain, update, coordinate, sync]
  tools: Read, Write, Edit, MultiEdit, Grep, Glob
  example: documentation-manager.md
```

### Task 3: Implement Validation Logic
After generating the file, validate:

```yaml
YAML Validation:
  - Check YAML frontmatter syntax
  - Verify all required fields (name, description, tools, color)
  - Confirm tools are from approved list
  - Check color is valid (blue/green/orange/red/purple)

Structure Validation:
  - Confirm all required sections present
  - Verify markdown heading hierarchy
  - Check description has proactive trigger

Tool Safety Check:
  - Flag if Bash included (requires justification)
  - Warn if tool list seems excessive (>7 tools)
  - Suggest minimal tool set if appropriate
```

### Pseudocode for Generation Logic

```python
# Task 1: Analyze Requirements
def analyze_requirements(user_input: str) -> AgentSpec:
    """
    Parse user requirements and determine agent specifications

    PATTERN: Extract keywords to determine archetype
    PATTERN: Infer responsibilities from description
    PATTERN: Map archetype to tool requirements
    """
    keywords = extract_keywords(user_input)
    archetype = determine_archetype(keywords)  # planner/builder/validator/manager

    # CRITICAL: Tool selection must be minimal
    tools = get_minimal_tools_for_archetype(archetype, user_input)

    # PATTERN: Name should be descriptive and kebab-case
    name = generate_kebab_case_name(user_input)

    # CRITICAL: Description must include proactive trigger
    description = generate_description_with_trigger(user_input, archetype)

    color = assign_color(archetype)  # Consistent colors per archetype

    return AgentSpec(name, description, tools, color, archetype)

# Task 2: Reference Patterns
def get_reference_example(archetype: str) -> str:
    """
    PATTERN: Load similar example agent for pattern matching

    Maps archetypes to example files in examples/claude-subagent-patterns/
    """
    archetype_map = {
        "planner": "pydantic-ai-planner.md",
        "builder": "pydantic-ai-prompt-engineer.md",
        "validator": "validation-gates.md",
        "manager": "documentation-manager.md"
    }
    return load_file(f"examples/claude-subagent-patterns/{archetype_map[archetype]}")

# Task 3: Generate System Prompt
def generate_system_prompt(spec: AgentSpec, reference: str) -> str:
    """
    Create focused system prompt following established patterns

    STRUCTURE (from README.md):
    1. Identity statement with expertise
    2. Philosophy in bold quotes
    3. Primary objective
    4. Simplicity principles (3-5)
    5. Core responsibilities
    6. Working protocol
    7. Output standards
    8. Integration guidelines
    9. Remember section

    CRITICAL: Keep total length 100-500 words
    PATTERN: Mirror structure from reference example
    """
    prompt = f"""# {spec.name.replace('-', ' ').title()}

You are an expert {spec.role} specializing in {spec.domain}. Your philosophy: **"{spec.philosophy}"**

## Primary Objective
{spec.objective}

## Simplicity Principles
{spec.principles}  # 3-5 items

## Core Responsibilities
{spec.responsibilities}  # Categorized breakdown

## Working Protocol
{spec.protocol}  # Step-by-step process

## Output Standards
{spec.output_standards}

## Integration
{spec.integration_notes}

## Remember
{spec.key_reminders}
"""
    return prompt

# Task 4: Validate Generated File
def validate_subagent_file(file_path: str) -> ValidationResult:
    """
    VALIDATION GATES:
    1. YAML syntax check
    2. Required fields present
    3. Tools are valid
    4. Structure matches pattern
    5. Description has proactive trigger
    """
    content = read_file(file_path)

    # Level 1: YAML validation
    frontmatter = extract_yaml_frontmatter(content)
    assert frontmatter is not None, "Missing YAML frontmatter"
    assert "name" in frontmatter, "Missing 'name' field"
    assert "description" in frontmatter, "Missing 'description' field"
    assert "tools" in frontmatter, "Missing 'tools' field"
    assert "color" in frontmatter, "Missing 'color' field"

    # Level 2: Content validation
    assert "USE PROACTIVELY" in frontmatter["description"], "Missing proactive trigger"
    assert frontmatter["color"] in ["blue", "green", "orange", "red", "purple"]

    # Level 3: Structure validation
    required_sections = ["Primary Objective", "Core Responsibilities", "Working Protocol"]
    for section in required_sections:
        assert f"## {section}" in content, f"Missing required section: {section}"

    return ValidationResult(success=True, message="All validations passed")
```

### Integration Points

```yaml
File System:
  - create: .claude/commands/generate-subagent.md
  - target: .claude/agents/[generated-name].md
  - read: examples/claude-subagent-patterns/*.md (for patterns)

Claude Code Integration:
  - command: /generate-subagent [description]
  - invocation: User types slash command in Claude Code
  - output: Generated subagent file ready to use

Example Usage:
  - User: "/generate-subagent Create an agent that monitors GitHub issues and creates task summaries"
  - System: Analyzes requirements → Determines archetype (planner/manager hybrid) →
           References examples → Generates file → Validates → Saves to .claude/agents/github-issue-monitor.md
```

## Validation Loop

### Level 1: File Creation Check
```bash
# Verify the slash command file was created
ls -la .claude/commands/generate-subagent.md

# Expected: File exists with proper permissions
```

### Level 2: Test Generation
```bash
# Test the slash command by generating a simple subagent
# In Claude Code interface, run:
/generate-subagent Create a simple agent that helps write unit tests

# Expected: Creates .claude/agents/unit-test-helper.md
# Verify file exists:
ls -la .claude/agents/unit-test-helper.md
```

### Level 3: YAML Validation
```bash
# Validate YAML syntax of generated file
# (If yq or python-yaml installed)
head -20 .claude/agents/unit-test-helper.md | grep -A 10 "^---"

# Expected: Valid YAML frontmatter with all required fields
# Manual check if no YAML parser available
```

### Level 4: Structure Validation
```bash
# Check generated file has all required sections
grep "^## " .claude/agents/unit-test-helper.md

# Expected output should include:
# ## Primary Objective
# ## Core Responsibilities
# ## Working Protocol
# ## Output Standards
```

### Level 5: Integration Test
```yaml
Test in Claude Code:
  1. Generate a test subagent using /generate-subagent
  2. Try to invoke the generated subagent using Task tool
  3. Verify the subagent receives correct instructions
  4. Confirm it can execute with assigned tools

Expected Result:
  - Generated subagent is recognized by Claude Code
  - Can be invoked successfully
  - Has access to specified tools
  - Follows its defined protocol
```

### Level 6: Quality Check Against Examples
```bash
# Compare generated file structure to existing examples
# Read a generated file and an example side by side

# Check YAML frontmatter format matches
head -10 .claude/agents/unit-test-helper.md
head -10 .claude/agents/documentation-manager.md

# Check system prompt structure matches
grep "^#" .claude/agents/unit-test-helper.md
grep "^#" .claude/agents/documentation-manager.md

# Expected: Similar structure and sections
```

## Final Validation Checklist
- [ ] Slash command file created: `.claude/commands/generate-subagent.md`
- [ ] Can generate test subagent successfully
- [ ] Generated files have valid YAML frontmatter
- [ ] All required sections present in generated files
- [ ] Generated subagents follow established patterns
- [ ] Tool selection is minimal and appropriate
- [ ] Descriptions include proactive triggers
- [ ] System prompts are focused (100-500 words)
- [ ] Generated files work when invoked in Claude Code
- [ ] Validation catches malformed YAML
- [ ] Documentation updated (if needed)

---

## Anti-Patterns to Avoid

```yaml
Over-Engineering:
  - ❌ Don't create complex Python generators with templates
  - ❌ Don't build multi-phase workflows (this isn't agent-factory)
  - ❌ Don't add unnecessary configuration files
  - ✅ Keep it simple: one slash command that leverages Claude's intelligence

Tool Bloat:
  - ❌ Don't give every agent access to all tools
  - ❌ Don't include Bash unless absolutely necessary
  - ✅ Minimal tool access - only what's needed

Structure Deviation:
  - ❌ Don't invent new frontmatter fields
  - ❌ Don't skip required sections
  - ❌ Don't use different section names than examples
  - ✅ Follow established patterns exactly

Missing Validation:
  - ❌ Don't skip YAML validation
  - ❌ Don't forget proactive triggers
  - ❌ Don't generate and assume it works
  - ✅ Validate structure, test invocation

Verbose System Prompts:
  - ❌ Don't write 1000+ word system prompts
  - ❌ Don't include unnecessary details
  - ✅ Keep focused: 100-500 words, specific to role
```

## Common Patterns from Examples

### Planner/Analyst Pattern
```markdown
---
name: [name]-planner
description: Requirements gathering and planning specialist. USE PROACTIVELY when [trigger]. Works autonomously.
tools: Read, Write, Grep, Glob, WebSearch, TodoWrite
color: blue
---

You are an expert requirements analyst specializing in [domain]. Your philosophy: **"Start simple, make it work, then iterate."**

## Primary Objective
Transform high-level requests into comprehensive, actionable requirement documents.

## Simplicity Principles
1. Start with MVP
2. Avoid Premature Optimization
3. Single Responsibility
4. Minimal Dependencies
5. Clear Over Clever

[... rest of structure ...]
```

### Builder/Generator Pattern
```markdown
---
name: [name]-builder
description: Code generation specialist. USE AUTOMATICALLY after planning phase. Works autonomously.
tools: Read, Write, Edit, MultiEdit
color: green
---

You are an expert developer specializing in [domain]. Your philosophy: **"Clarity beats complexity."**

## Primary Objective
Generate production-ready [type] code following best practices.

[... rest of structure ...]
```

### Validator/Tester Pattern
```markdown
---
name: [name]-validator
description: Testing and validation specialist. USE PROACTIVELY after implementation. Works autonomously.
tools: Read, Bash, TodoWrite, Edit
color: orange
---

You are a validation specialist focusing on [domain]. Your philosophy: **"Fix, don't disable."**

## Primary Objective
Ensure code meets quality standards through comprehensive testing.

[... rest of structure ...]
```

### Manager/Coordinator Pattern
```markdown
---
name: [name]-manager
description: Maintenance specialist. USE PROACTIVELY when [trigger event]. Works autonomously.
tools: Read, Write, Edit, MultiEdit, Grep, Glob
color: purple
---

You are a [domain] specialist focused on [area]. Your philosophy: **"[Principle]"**

## Primary Objective
Maintain [area] synchronized with [changes].

[... rest of structure ...]
```

## Example Invocations

```bash
# Generate a code review agent
/generate-subagent Create an agent that reviews code changes for best practices and suggests improvements

# Generate a test writing agent
/generate-subagent I need an agent that writes comprehensive unit tests for Python functions

# Generate a documentation synchronizer
/generate-subagent Build an agent that keeps API documentation in sync with code changes

# Generate a dependency updater
/generate-subagent Create an agent that monitors and updates project dependencies safely

# Generate a bug triage agent
/generate-subagent I want an agent that analyzes bug reports and categorizes them by severity
```

## Notes

**Keep It Simple**: This is NOT the complex agent-factory multi-phase workflow. This is a simple, focused tool to generate one subagent definition file at a time.

**Leverage Claude**: The slash command should leverage Claude Code's natural understanding of patterns rather than rigid templates.

**Pattern Library**: The examples directory serves as the pattern library - reference it extensively.

**Validation is Key**: Always validate generated files to ensure they work correctly.

**Iterate**: Start with basic generation, validate it works, then enhance with better archetype detection and pattern matching.

---

**Generated**: 2025-10-01
**Purpose**: Create a simple factory for generating Claude Code subagent definition files
**Scope**: MVP - slash command that generates single subagent files following established patterns
