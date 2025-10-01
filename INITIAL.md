# Claude Code Subagents Factory

## FEATURE: Claude Code Subagents Generator

Build a factory system that generates **Claude Code subagent definition files** (`.claude/agents/*.md`) based on user requirements. This factory creates the specialized markdown files that define Claude Code subagents, NOT Pydantic AI agents.

### What This Factory Creates

The factory generates `.claude/agents/[agent-name].md` files with:
- YAML frontmatter (name, description, tools, color)
- System prompt defining agent's role and behavior
- Responsibilities and capabilities
- Working protocols and patterns
- Integration guidelines
- Quality standards

### Core Functionality (MVP)

1. **Requirements Gathering**: Understand what the subagent needs to do
2. **Subagent Definition Generation**: Create complete `.claude/agents/*.md` file with:
   - Proper YAML frontmatter
   - Focused system prompt (100-500 words)
   - Clear responsibilities
   - Tool requirements
   - Working protocols
3. **Validation**: Ensure generated subagent follows Claude Code patterns

### Workflow Pattern

```
User Request → Analyze Requirements → Generate Subagent Definition → Validate Structure
```

**NOT** the complex multi-phase workflow from agent-factory (that's for Pydantic AI agents).

## EXAMPLES

Reference implementations in `examples/claude-subagent-patterns/`:

### Existing Subagent Definitions (from agent-factory repo)
- `pydantic-ai-planner.md` - Requirements gathering specialist
- `pydantic-ai-prompt-engineer.md` - System prompt crafting
- `pydantic-ai-tool-integrator.md` - Tool specification design
- `pydantic-ai-dependency-manager.md` - Configuration setup
- `pydantic-ai-validator.md` - Testing and validation

### Vibes Existing Subagents (from vibes repo)
- `documentation-manager.md` - Proactive documentation updates
- `validation-gates.md` - Testing and validation specialist

### Structure Patterns
```markdown
---
name: agent-name
description: Brief description of what this agent does. USE PROACTIVELY when [trigger condition]. Works autonomously.
tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite
color: blue|green|orange|red|purple
---

# Agent Title

You are an expert [role] specializing in [domain]. Your philosophy: **"[Core principle]"**

## Primary Objective
[Clear statement of purpose]

## Simplicity Principles
[Key guiding principles, 3-5 items]

## Core Responsibilities
[Detailed breakdown of what this agent does]

## Working Protocol
[Step-by-step process the agent follows]

## Output Standards
[What the agent produces and quality criteria]

## Integration
[How this agent works with others]

## Remember
[Key reminders and principles]
```

## DOCUMENTATION

### Claude Code Resources
- Claude Code documentation: https://docs.anthropic.com/en/docs/claude-code
- Subagents guide: https://docs.anthropic.com/en/docs/claude-code/subagents
- Custom agents: https://docs.anthropic.com/en/docs/claude-code/custom-agents

### Reference Repositories
- Agent Factory patterns: repos/agent-factory-with-subagents/.claude/agents/
- Context Engineering: repos/context-engineering-intro/README.md
- Vibes existing agents: .claude/agents/

### Key Patterns to Follow
1. **YAML Frontmatter**:
   - `name`: kebab-case identifier
   - `description`: Clear description with USE PROACTIVELY trigger
   - `tools`: Comma-separated list of available tools
   - `color`: Visual identifier (blue, green, orange, red, purple)

2. **System Prompt Structure**:
   - Identity statement with expertise
   - Philosophy/core principle (bold quote)
   - Primary objective
   - Simplicity principles (3-5 items)
   - Core responsibilities
   - Working protocol
   - Output standards
   - Integration notes
   - Remember section

3. **Tool Selection**:
   - Read: Reading files
   - Write: Creating new files
   - Edit/MultiEdit: Modifying existing files
   - Grep: Searching file contents
   - Glob: Finding files by pattern
   - Bash: Running commands
   - TodoWrite: Task tracking
   - WebSearch: Online research
   - mcp__archon__*: Archon integration (optional)

## SUCCESS CRITERIA

- [ ] Generated subagent has valid YAML frontmatter
- [ ] System prompt is focused (100-500 words)
- [ ] Responsibilities are clearly defined
- [ ] Working protocol is actionable
- [ ] Tool requirements are appropriate
- [ ] Follows established patterns from examples
- [ ] File is valid markdown
- [ ] Generated in correct location: `.claude/agents/[name].md`

## TECHNICAL SETUP

### Input Format
The factory should accept:
```
User: "Create a subagent that [does X]"
or
User: "I need an agent for [specific task]"
```

### Output Format
Single `.claude/agents/[agent-name].md` file with complete subagent definition

### Location
- Generated files go to: `/workspace/vibes/.claude/agents/`
- Examples stored in: `/workspace/vibes/examples/claude-subagent-patterns/`

## OTHER CONSIDERATIONS

### Keep It Simple
- This is a single-agent generator, not a multi-phase orchestration system
- Focus on generating ONE subagent definition file well
- Avoid over-engineering the factory itself

### Pattern Adherence
- Study existing subagents carefully
- Maintain consistent structure across all generated agents
- Use proven patterns from examples

### Tool Safety
- Only include tools the agent actually needs
- Don't give Bash access unless necessary
- Consider security implications of tool combinations

### Integration
- Generated agents should work within existing vibes workflow
- Can be invoked manually or automatically (USE PROACTIVELY)
- Should integrate with existing PRP system if relevant

### Validation
- Check YAML frontmatter is valid
- Ensure markdown structure is correct
- Verify tool references are accurate
- Test that description trigger is clear

## ASSUMPTIONS

1. Factory generates one subagent at a time
2. User provides clear description of what agent should do
3. Generated agents follow existing vibes patterns
4. No need for multi-agent orchestration (that's what agent-factory does)
5. Focus on quality over quantity of features

---

**Generated**: 2025-10-01
**Purpose**: Set up context engineering for building a Claude Code subagents factory
**Next Step**: Run `/generate-prp INITIAL.md` to create comprehensive implementation plan
