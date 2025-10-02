name: "Context Engineering Foundation Integration - SIMPLE Version"
description: |

## Purpose
Integrate foundational Context Engineering patterns from coleam00/context-engineering-intro into Vibes. This is the SIMPLE version focusing on core structure, templates, and basic examples without complex agent factory patterns.

## Core Principles
1. **Context is King**: Provide comprehensive documentation, examples, and patterns
2. **Progressive Success**: Start simple, validate, then enhance
3. **Information Dense**: Use clear patterns and practical examples
4. **Keep It SIMPLE**: No subagents in this version - focus on structure
5. **Follow Global Rules**: Adhere to all rules in CLAUDE.md

---

## Goal
Create a solid Context Engineering foundation in Vibes that enables:
1. Effective PRP usage for feature development
2. Clear PRP lifecycle tracking (active → completed → archived)
3. Reference patterns and templates for common tasks
4. Easy-to-use documentation and examples
5. Foundation for future enhancements

## Why
- **Developer Productivity**: Structured PRPs reduce trial-and-error and enable first-pass success
- **Knowledge Retention**: Examples and patterns accumulate institutional knowledge
- **Quality Consistency**: Templates ensure completeness and follow best practices
- **Onboarding**: New developers/users can learn from examples
- **Foundation**: Sets up structure for future advanced patterns

## What
Implement a comprehensive Context Engineering foundation including:
- PRP lifecycle management (active/, completed/, archived/ directories)
- Three specialized templates (feature, tool, documentation)
- Examples directory with at least 5 reference patterns
- list-prps command for PRP organization
- Updated README.md with Context Engineering section

### Success Criteria
- [ ] PRP lifecycle directories created and functional
- [ ] 3 new templates created (feature, tool, documentation)
- [ ] examples/ directory populated with at least 5 well-documented reference files
- [ ] examples/README.md provides clear guidance
- [ ] list-prps.md command created and functional
- [ ] Main README.md updated with Context Engineering section
- [ ] Can successfully track a PRP through its lifecycle
- [ ] Examples are clear, practical, and helpful

## All Needed Context

### Documentation & References
```yaml
# PRIMARY REFERENCES - Context Engineering Core
- url: https://github.com/coleam00/context-engineering-intro
  why: Main reference for Context Engineering patterns and philosophy
  sections:
    - README.md: Philosophy and workflow
    - CLAUDE.md: Global rules pattern
    - PRPs/templates/prp_base.md: Template structure
    - EXAMPLE_multi_agent_prp.md: Complete PRP example

- url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  why: Official Anthropic guidance on context engineering for AI agents
  critical: Context pruning, offloading, just-in-time loading strategies

- url: https://www.datacamp.com/blog/context-engineering
  why: Comprehensive guide with practical examples
  critical: Difference between context engineering and prompt engineering

- url: https://medium.com/@alirezarezvani/context-engineering-the-complete-guide-to-building-production-ready-ai-coding-agents-6e45ed51e05e
  why: Production-ready patterns and best practices
  critical: Workflow-based architecture, tool design principles

# LOCAL REFERENCES - Existing Patterns
- file: /Users/jon/source/vibes/prps/templates/prp_base.md
  why: Current base template to follow

- file: /Users/jon/source/vibes/prps/EXAMPLE_multi_agent_prp.md
  why: Example of complete PRP structure

- file: /Users/jon/source/vibes/.claude/commands/generate-prp.md
  why: Pattern for creating Claude Code commands

- file: /Users/jon/source/vibes/.claude/commands/execute-prp.md
  why: Command structure and flow pattern

- file: /Users/jon/source/vibes/CLAUDE.md
  why: Global rules to follow
  critical: ARCHON-FIRST RULE - no TodoWrite, use Archon MCP for task management

- file: /Users/jon/source/vibes/repos/context-engineering-intro/README.md
  why: Detailed workflow and best practices
  critical: Step-by-step guide, writing effective INITIAL.md files

- file: /Users/jon/source/vibes/repos/context-engineering-intro/CLAUDE.md
  why: Example of comprehensive global rules
```

### Current Codebase Tree
```bash
/Users/jon/source/vibes/
├── .claude/
│   ├── commands/          # ✅ PRP commands exist
│   │   ├── generate-prp.md
│   │   ├── execute-prp.md
│   │   ├── prep-parallel.md
│   │   ├── execute-parallel.md
│   │   └── primer.md
│   └── settings.local.json
├── prps/                  # ✅ Basic structure exists
│   ├── templates/
│   │   └── prp_base.md
│   ├── EXAMPLE_multi_agent_prp.md
│   ├── INITIAL_context_engineering_foundation.md
│   └── INITIAL_context_engineering_agent_factory.md
├── agents/                # ✅ Empty, ready
├── examples/              # ⚠️ Empty, needs population
├── repos/                 # ✅ Contains context-engineering-intro
│   └── context-engineering-intro/
├── mcp/                   # MCP servers
│   ├── mcp-vibesbox-server/
│   └── mcp-vibes-server/
├── CLAUDE.md              # ✅ Global rules
├── INITIAL.md
└── README.md
```

### Desired Codebase Tree
```bash
/Users/jon/source/vibes/
├── prps/
│   ├── templates/
│   │   ├── prp_base.md           # ✅ Exists
│   │   ├── feature_template.md   # NEW: Simplified feature PRP template
│   │   ├── tool_template.md      # NEW: Tool/integration PRP template
│   │   └── documentation_template.md  # NEW: Documentation PRP template
│   ├── active/                    # NEW: In-progress PRPs
│   ├── completed/                 # NEW: Finished PRPs
│   ├── archived/                  # NEW: Old/reference PRPs
│   └── [existing PRP files]
│
├── examples/                      # Populate with patterns
│   ├── README.md                  # NEW: Guide to using examples
│   ├── prp-workflow/
│   │   ├── simple-feature.md      # NEW: Basic PRP example
│   │   └── complex-feature.md     # NEW: Multi-component PRP
│   ├── tools/
│   │   ├── api_integration.py     # NEW: API tool pattern
│   │   └── file_operations.py    # NEW: File tool pattern
│   └── documentation/
│       ├── README_template.md     # NEW: README pattern
│       └── API_doc_template.md    # NEW: API documentation pattern
│
└── .claude/
    └── commands/
        ├── list-prps.md           # NEW: List PRPs by status
        └── [existing commands]
```

### Known Gotchas & Library Quirks
```yaml
# CRITICAL: This is the SIMPLE version - NO subagents, NO complex agent factories
# CRITICAL: Follow ARCHON-FIRST RULE - Use Archon MCP for task management, NOT TodoWrite
# CRITICAL: Use mcp__vibesbox__run_command for all bash operations (MCP server pattern)
# CRITICAL: Don't modify existing working files (prp_base.md, existing commands, etc.)
# CRITICAL: All examples must be well-documented with clear explanations
# CRITICAL: Keep templates practical and usable - simpler than full prp_base.md
# CRITICAL: Examples are reference patterns, not copy-paste code
# GOTCHA: Examples directory exists but is empty - needs population
# GOTCHA: Context engineering is about comprehensive context, not clever prompts
# GOTCHA: PRPs should enable one-pass implementation through complete context
# GOTCHA: Validation gates must be executable by AI agents
# PATTERN: Commands use $ARGUMENTS variable for parameters
# PATTERN: Markdown files extensively used for documentation and structure
# PATTERN: MCP servers provide tools (run_command, etc.)
```

## Implementation Blueprint

### Phase 1: Create Directory Structure
```yaml
Task 1.1: Create PRP Lifecycle Directories
EXECUTE using mcp__vibesbox__run_command:
  - mkdir -p /workspace/vibes/prps/active
  - mkdir -p /workspace/vibes/prps/completed
  - mkdir -p /workspace/vibes/prps/archived
  - Verify: ls -la /workspace/vibes/prps/

Task 1.2: Create Examples Directory Structure
EXECUTE using mcp__vibesbox__run_command:
  - mkdir -p /workspace/vibes/examples/prp-workflow
  - mkdir -p /workspace/vibes/examples/tools
  - mkdir -p /workspace/vibes/examples/documentation
  - Verify: ls -R /workspace/vibes/examples/
```

### Phase 2: Create Templates
```yaml
Task 2.1: Create feature_template.md
CREATE /workspace/vibes/prps/templates/feature_template.md:
  - PATTERN: Based on prp_base.md but SIMPLER
  - SECTIONS: Goal, Why, What, Context, Implementation Steps, Validation
  - SIMPLIFY: Remove overly complex sections
  - KEEP: Core context engineering principles
  - PURPOSE: Standard feature development
  - INCLUDE: Success criteria, documentation references, validation gates

Task 2.2: Create tool_template.md
CREATE /workspace/vibes/prps/templates/tool_template.md:
  - PATTERN: Similar to feature_template.md but focused on tools
  - SECTIONS: Tool Purpose, API/Library Context, Authentication, Implementation, Testing
  - INCLUDE: API documentation references, error handling patterns
  - PURPOSE: Tool/integration PRPs
  - CRITICAL: Authentication and rate limiting considerations

Task 2.3: Create documentation_template.md
CREATE /workspace/vibes/prps/templates/documentation_template.md:
  - PATTERN: Lightweight template for doc generation
  - SECTIONS: Documentation Goal, Audience, Structure, Content Guidelines
  - PURPOSE: README, API docs, user guides
  - INCLUDE: Documentation standards, examples
```

### Phase 3: Create Examples
```yaml
Task 3.1: Create examples/README.md
CREATE /workspace/vibes/examples/README.md:
  - CONTENT: Guide to using examples effectively
  - SECTIONS:
    - What examples are for (reference patterns, not copy-paste)
    - Directory structure explanation
    - How to use each example type
    - When to reference examples in PRPs
  - PATTERN: Follow context-engineering-intro/examples/README.md structure
  - TONE: Clear, practical, educational

Task 3.2: Create PRP Workflow Examples
CREATE /workspace/vibes/examples/prp-workflow/simple-feature.md:
  - CONTENT: Complete example of a simple feature PRP
  - DEMONSTRATE: All required sections filled out
  - EXAMPLE: Add a simple API endpoint or utility function
  - SHOW: Clear validation gates, success criteria

CREATE /workspace/vibes/examples/prp-workflow/complex-feature.md:
  - CONTENT: Multi-component feature PRP example
  - DEMONSTRATE: Breaking down complex tasks
  - EXAMPLE: Multi-file feature with database, API, and CLI components
  - SHOW: Progressive success approach, multiple validation levels

Task 3.3: Create Tool Examples
CREATE /workspace/vibes/examples/tools/api_integration.py:
  - CONTENT: Well-documented example of API integration pattern
  - DEMONSTRATE:
    - Configuration with environment variables
    - Error handling and retries
    - Rate limiting
    - Authentication
  - DOCSTRINGS: Comprehensive explanations
  - COMMENTS: Why decisions were made, not just what code does

CREATE /workspace/vibes/examples/tools/file_operations.py:
  - CONTENT: Safe file operation patterns
  - DEMONSTRATE:
    - Path handling (absolute vs relative)
    - Error recovery
    - Validation
    - Atomic operations
  - DOCSTRINGS: Clear explanations
  - COMMENTS: Edge cases and gotchas

Task 3.4: Create Documentation Examples
CREATE /workspace/vibes/examples/documentation/README_template.md:
  - CONTENT: Template for README files
  - SECTIONS: Overview, Installation, Usage, API Reference, Contributing
  - DEMONSTRATE: Clear structure, practical examples
  - PATTERN: Follow Vibes README.md structure

CREATE /workspace/vibes/examples/documentation/API_doc_template.md:
  - CONTENT: API documentation template
  - SECTIONS: Endpoints, Parameters, Responses, Examples
  - DEMONSTRATE: Complete API documentation
  - PATTERN: RESTful API documentation standards
```

### Phase 4: Create list-prps Command
```yaml
Task 4.1: Create list-prps.md command
CREATE /workspace/vibes/.claude/commands/list-prps.md:
  - PATTERN: Follow generate-prp.md and execute-prp.md structure
  - FUNCTIONALITY:
    - List all PRPs organized by status (active, completed, archived)
    - Show PRP metadata (name, date, status)
    - Support filtering by status
    - Optional: Show recent PRPs first
  - USAGE: /list-prps [status]
  - IMPLEMENTATION:
    - Use mcp__vibesbox__run_command for ls/find commands
    - Format output clearly
    - Group by directory (active/completed/archived)
```

### Phase 5: Update Documentation
```yaml
Task 5.1: Update README.md
EDIT /workspace/vibes/README.md:
  - FIND: Appropriate location (after "Core Philosophy" or before "Future Vision")
  - ADD SECTION: "Context Engineering"
  - CONTENT:
    - Brief explanation of Context Engineering
    - PRP workflow (INITIAL → generate → execute → complete)
    - Directory structure overview
    - How to use templates and examples
    - Links to further resources
  - PATTERN: Follow existing README.md style
  - LENGTH: Comprehensive but concise (similar to "Current Capabilities" section)
```

## Validation Loop

### Level 1: Structure Validation
```bash
# Verify all directories created
ls -la /workspace/vibes/prps/active/
ls -la /workspace/vibes/prps/completed/
ls -la /workspace/vibes/prps/archived/

# Check templates exist
ls /workspace/vibes/prps/templates/
# Expected: prp_base.md, feature_template.md, tool_template.md, documentation_template.md

# Verify examples structure
ls -R /workspace/vibes/examples/
# Expected: README.md, prp-workflow/, tools/, documentation/ with all files

# Expected: No errors, all directories and files present
```

### Level 2: Content Quality Check
```bash
# Check template completeness
cat /workspace/vibes/prps/templates/feature_template.md
cat /workspace/vibes/prps/templates/tool_template.md
cat /workspace/vibes/prps/templates/documentation_template.md
# Expected: All sections present, clear guidance, practical

# Check examples quality
cat /workspace/vibes/examples/README.md
cat /workspace/vibes/examples/prp-workflow/simple-feature.md
cat /workspace/vibes/examples/tools/api_integration.py
# Expected: Well-documented, clear explanations, practical patterns

# Verify command
cat /workspace/vibes/.claude/commands/list-prps.md
# Expected: Clear instructions, proper command structure

# Check README update
cat /workspace/vibes/README.md
# Expected: Context Engineering section present, comprehensive, follows style
```

### Level 3: Integration Test
```bash
# Test PRP lifecycle workflow
# 1. Create a test PRP in active/
echo "# Test PRP" > /workspace/vibes/prps/active/test_feature.md

# 2. Use list-prps command (manual test in Claude Code)
/list-prps active

# 3. Move to completed
mv /workspace/vibes/prps/active/test_feature.md /workspace/vibes/prps/completed/

# 4. Verify with list-prps
/list-prps completed

# 5. Clean up
rm /workspace/vibes/prps/completed/test_feature.md

# Expected: Full workflow works smoothly, list-prps shows correct status
```

## Final Validation Checklist
- [ ] All directories created: active/, completed/, archived/
- [ ] 3 new templates created and well-structured
- [ ] At least 5 example files created
- [ ] examples/README.md provides clear guidance
- [ ] list-prps.md command created and functional
- [ ] README.md updated with Context Engineering section
- [ ] All files follow existing code style and patterns
- [ ] Examples are practical and well-documented
- [ ] Templates are simpler and more usable than full prp_base.md
- [ ] No existing files were modified (except README.md)
- [ ] Structure supports PRP lifecycle management

---

## Anti-Patterns to Avoid
- ❌ Don't add subagent complexity in this SIMPLE version
- ❌ Don't modify existing working files (prp_base.md, existing commands)
- ❌ Don't create overly complex templates - keep them practical
- ❌ Don't make examples copy-paste code - they're reference patterns
- ❌ Don't skip documentation - every file needs clear explanations
- ❌ Don't use TodoWrite tool - follow ARCHON-FIRST RULE
- ❌ Don't create templates that are harder to use than prp_base.md
- ❌ Don't forget to use mcp__vibesbox__run_command for bash operations

## Implementation Notes

### Context Engineering Philosophy
This foundation implements core Context Engineering principles:

1. **Context is King**: Provide comprehensive documentation, examples, and patterns so AI agents have everything needed for success

2. **Progressive Success**: Start with simple structure, validate, then enhance with advanced patterns later

3. **Validation Loops**: Enable AI agents to verify their work at each step

4. **Information Dense**: Templates and examples include specific, actionable guidance

### Template Design Philosophy
- **feature_template.md**: For general feature development - simpler than prp_base.md but comprehensive
- **tool_template.md**: Specialized for API/tool integrations with focus on authentication and error handling
- **documentation_template.md**: Lightweight for documentation tasks

### Examples Purpose
Examples are **reference patterns**, not copy-paste code. They demonstrate:
- How to structure code
- Best practices for error handling
- Patterns for common tasks
- What good documentation looks like

### PRP Lifecycle
- **active/**: Work in progress PRPs
- **completed/**: Successfully implemented PRPs (knowledge base)
- **archived/**: Old/reference PRPs that are no longer active

## Confidence Score: 8/10

**High confidence due to:**
- Clear, well-defined requirements
- Excellent reference materials (context-engineering-intro repo)
- Mostly documentation work (low technical risk)
- Good existing patterns to follow
- Comprehensive validation strategy

**Minor uncertainty:**
- Template usefulness will require iteration based on usage
- Examples quality depends on practical experience
- list-prps command functionality might need refinement

**Mitigation:**
- Templates can be refined based on user feedback
- Examples can be expanded over time
- Command can be enhanced in future iterations

This is a solid foundation that enables progressive enhancement without over-engineering.
