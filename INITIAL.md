## FEATURE:
Integrate Context Engineering patterns from coleam00/context-engineering-intro into Vibes to enable easy creation and management of Claude subagents and features. This includes setting up proper directory structure, templates, and workflows for PRP-based development.

## GOAL:
Create a well-organized structure in Vibes that makes it trivial to:
1. Add new Claude subagents (research, email, coding, analysis, etc.)
2. Use PRPs to develop features with high reliability
3. Maintain examples that serve as learning patterns
4. Track PRP lifecycle from active → completed

## EXAMPLES:
The following structure from context-engineering-intro should guide implementation:

**Current Vibes Structure (already good):**
```
/workspace/vibes/
├── .claude/
│   ├── commands/          # ✅ Already have PRP commands
│   │   ├── generate-prp.md
│   │   ├── execute-prp.md
│   │   └── ...
│   ├── agents/            # ✅ Good place for subagents
│   └── settings.local.json
├── prps/                  # ✅ Already have this
│   ├── templates/
│   │   └── prp_base.md
│   └── EXAMPLE_multi_agent_prp.md
├── agents/                # ✅ For agent implementations
├── examples/              # ✅ Exists - needs population
├── CLAUDE.md              # ✅ Global rules
└── INITIAL.md             # ✅ This file
```

**Needed Additions:**
```
/workspace/vibes/
├── .claude/
│   ├── agents/                    # NEW: Subagent specifications
│   │   ├── research-agent.md
│   │   ├── email-agent.md
│   │   ├── coding-agent.md
│   │   └── analysis-agent.md
│   └── commands/
│       └── spawn-agent.md        # NEW: Command to spawn subagents
│
├── agents/                        # Actual agent implementations
│   ├── research/                 # NEW: Research agent implementation
│   │   ├── agent.py
│   │   ├── tools.py
│   │   └── providers.py
│   ├── email/                    # NEW: Email agent implementation
│   │   ├── agent.py
│   │   └── gmail_tool.py
│   └── shared/                   # NEW: Shared utilities
│       ├── dependencies.py
│       └── models.py
│
├── prps/
│   ├── templates/
│   │   ├── prp_base.md           # ✅ Already exists
│   │   ├── subagent_template.md # NEW: Template for new subagents
│   │   └── tool_template.md     # NEW: Template for new tools
│   ├── active/                    # NEW: Currently executing PRPs
│   └── completed/                 # NEW: Finished PRPs
│
└── examples/                      # Critical reference examples
    ├── README.md                  # NEW: Explain examples purpose
    ├── cli/
    │   └── agent_cli.py           # NEW: Example CLI pattern
    ├── agents/
    │   ├── simple_agent.py        # NEW: Simple single-agent example
    │   └── multi_agent.py         # NEW: Multi-agent delegation
    └── tools/
        ├── api_tool.py            # NEW: Example API tool
        └── file_tool.py           # NEW: Example file tool
```

**From context-engineering-intro repo examples:**
- `examples/cli.py` - Template for CLI structure with streaming
- `examples/agent/agent.py` - Pattern for agent creation with tools
- `examples/agent/providers.py` - Multi-provider LLM configuration

## DOCUMENTATION:
Primary reference: https://github.com/coleam00/context-engineering-intro
- README.md explains the full context engineering workflow
- EXAMPLE_multi_agent_prp.md shows complete PRP structure
- templates/prp_base.md is the base template

## KEY REQUIREMENTS:

### 1. Directory Structure
- Create all NEW directories and maintain existing ✅ ones
- Use numbered hierarchy (00-99) where it makes sense in prps/
- Keep .claude/agents/ for subagent specs
- Keep agents/ for actual Python implementations

### 2. Templates to Create
**prps/templates/subagent_template.md:**
- Template for creating new subagent PRPs
- Should include sections: Purpose, Context, Examples, Validation
- Follow EXAMPLE_multi_agent_prp.md pattern

**prps/templates/tool_template.md:**
- Template for creating new tool/integration PRPs
- Include API documentation references
- Include authentication/setup requirements

**.claude/commands/spawn-agent.md:**
- Command to create a new subagent from template
- Should prompt for: agent name, purpose, tools needed
- Auto-generate directory structure and initial files

### 3. Examples to Port
Create working examples in examples/ directory:
- Simple single-agent pattern (similar to context-engineering-intro)
- Multi-agent delegation pattern
- API tool integration pattern
- File operation tool pattern

### 4. Integration Points
**For adding new subagents:**
```bash
# 1. Create agent spec: .claude/agents/new-agent.md
# 2. Generate PRP: Use spawn-agent command
# 3. Add implementation: agents/new-agent/
# 4. Add examples: examples/agents/new_agent_example.py
```

**For adding features:**
```bash
# 1. Write feature request: INITIAL.md
# 2. Generate PRP: .claude/commands/generate-prp.md
# 3. Execute PRP: .claude/commands/execute-prp.md
# 4. Track: prps/active/ → prps/completed/
```

### 5. Documentation Requirements
- Update README.md with context engineering section
- Add examples/README.md explaining how to use examples
- Document the workflow: INITIAL → generate-prp → execute-prp → complete
- Include .env.example for any API keys needed by example agents

## SUCCESS CRITERIA:
- [ ] All NEW directories created with proper structure
- [ ] Templates created (subagent_template.md, tool_template.md)
- [ ] spawn-agent.md command created and tested
- [ ] At least 2 working examples in examples/ directory
- [ ] prps/active/ and prps/completed/ directories exist
- [ ] Documentation updated (README.md, examples/README.md)
- [ ] Can successfully create a new subagent using the templates
- [ ] PRP lifecycle tracking works (active → completed)

## CONSTRAINTS:
- DO NOT modify existing working files in .claude/commands/
- DO NOT change existing prps/templates/prp_base.md
- DO NOT modify CLAUDE.md (global rules)
- Use vibes:run_command for all file operations
- Maintain Vibes' existing folder organization patterns
- Keep it simple - focus on the structure and templates first

## VALIDATION:
After implementation:
```bash
# Verify structure
ls -la /workspace/vibes/.claude/agents/
ls -la /workspace/vibes/prps/templates/
ls -la /workspace/vibes/prps/active/
ls -la /workspace/vibes/prps/completed/
ls -la /workspace/vibes/examples/

# Test spawn-agent command exists
cat /workspace/vibes/.claude/commands/spawn-agent.md

# Verify templates exist
cat /workspace/vibes/prps/templates/subagent_template.md
cat /workspace/vibes/prps/templates/tool_template.md

# Check examples
ls /workspace/vibes/examples/agents/
ls /workspace/vibes/examples/tools/
```
