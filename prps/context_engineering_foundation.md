name: "Context Engineering Foundation - Simple Structure for PRPs and Examples"
description: |

## Purpose
Integrate foundational context engineering patterns from coleam00/context-engineering-intro into Vibes. This establishes the SIMPLE version: core structure, templates, and basic examples without complex agent factory systems. The goal is to make PRPs more effective and provide reference patterns for common tasks.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Create a solid context engineering foundation in Vibes that enables:
- Effective PRP lifecycle management (active → completed → archived)
- Specialized templates for common feature types
- Reference patterns and examples for typical development tasks
- Better organization and discoverability of PRPs
- Foundation for future subagent and advanced patterns

## Why
- **Immediate Value**: Better PRP organization and workflow right away
- **Reference Patterns**: Examples for common tasks reduce cognitive load
- **Documentation Standards**: Clear templates ensure consistency
- **Progressive Enhancement**: Structure scales from simple to complex
- **Learning**: Build muscle memory with context engineering patterns

## What
A directory structure and documentation system that includes:
- PRP lifecycle directories (active/, completed/, archived/)
- Three specialized templates (feature, tool, documentation)
- Comprehensive examples directory with real patterns
- Command to list and filter PRPs
- Updated README explaining context engineering philosophy

### Success Criteria
- [ ] PRP lifecycle directories created (active/, completed/, archived/)
- [ ] 3 new templates created (feature_template.md, tool_template.md, documentation_template.md)
- [ ] examples/ directory populated with at least 5 reference files
- [ ] examples/README.md written with clear guidance
- [ ] list-prps.md command created
- [ ] Main README.md updated with context engineering section
- [ ] Can successfully track a PRP through its lifecycle
- [ ] Examples are clear, practical, and immediately useful

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://github.com/coleam00/context-engineering-intro
  why: Original context engineering patterns and philosophy

- file: /Users/jon/source/vibes/prps/templates/prp_base.md
  why: Our current PRP template - base for new templates

- file: /Users/jon/source/vibes/prps/EXAMPLE_multi_agent_prp.md
  why: Example of a complete, comprehensive PRP

- file: /Users/jon/source/vibes/.claude/commands/generate-prp.md
  why: How PRPs are generated - informs template design

- file: /Users/jon/source/vibes/.claude/commands/execute-prp.md
  why: How PRPs are executed - informs validation design

- file: /Users/jon/source/vibes/CLAUDE.md
  why: Global rules and conventions

- file: /Users/jon/source/vibes/README.md
  why: Current README structure to extend
```

### Current Codebase Structure
```bash
/workspace/vibes/
├── .claude/
│   ├── commands/          # ✅ PRP commands exist
│   │   ├── generate-prp.md
│   │   ├── execute-prp.md
│   │   └── ...
│   └── settings.local.json
├── prps/                  # ✅ Basic PRP structure
│   ├── templates/
│   │   └── prp_base.md
│   └── EXAMPLE_multi_agent_prp.md
├── examples/              # ⚠️ Empty, needs content
├── CLAUDE.md              # ✅ Global rules
├── README.md
└── ...
```

### Desired Codebase Structure
```bash
/workspace/vibes/
├── prps/
│   ├── templates/
│   │   ├── prp_base.md              # ✅ Exists
│   │   ├── feature_template.md      # NEW: Standard feature PRP
│   │   ├── tool_template.md         # NEW: Tool integration PRP
│   │   └── documentation_template.md # NEW: Documentation PRP
│   ├── active/                       # NEW: In-progress PRPs
│   ├── completed/                    # NEW: Finished PRPs
│   ├── archived/                     # NEW: Old/reference PRPs
│   └── EXAMPLE_multi_agent_prp.md   # ✅ Exists
│
├── examples/                         # Populate with patterns
│   ├── README.md                     # NEW: Guide to examples
│   ├── prp-workflow/
│   │   ├── simple-feature.md         # NEW: Basic PRP example
│   │   └── complex-feature.md        # NEW: Multi-component PRP
│   ├── tools/
│   │   ├── api_integration.py        # NEW: API tool pattern
│   │   └── file_operations.py       # NEW: File tool pattern
│   └── documentation/
│       ├── README_template.md        # NEW: README pattern
│       └── API_doc_template.md       # NEW: API doc pattern
│
├── .claude/
│   └── commands/
│       └── list-prps.md              # NEW: List PRPs by status
│
└── README.md                         # UPDATE: Add context engineering section
```

### Known Gotchas & Conventions
```yaml
# CRITICAL: This is pure structure/documentation work - no code execution needed
# CRITICAL: Use Archon MCP server for task management (NOT TodoWrite)
# CRITICAL: Templates should be SIMPLER than prp_base.md but still comprehensive
# CRITICAL: Examples must be immediately practical and clear
# CRITICAL: Follow existing Vibes conventions for file organization
# CRITICAL: Don't modify existing working files (prp_base.md, EXAMPLE_multi_agent_prp.md)
# CRITICAL: All markdown files should have clear headers and structure
# CRITICAL: Use mcp__vibesbox__run_command for all file operations
```

## Implementation Blueprint

### Phase 1: Directory Structure Setup

```yaml
Task 1: Create PRP Lifecycle Directories
ACTION: Create directories for PRP lifecycle management
PATTERN: Standard directory creation
COMMANDS: |
  mkdir -p /workspace/vibes/prps/active
  mkdir -p /workspace/vibes/prps/completed
  mkdir -p /workspace/vibes/prps/archived

Task 2: Create Examples Directory Structure
ACTION: Set up examples organization
PATTERN: Hierarchical directory for different example types
COMMANDS: |
  mkdir -p /workspace/vibes/examples/prp-workflow
  mkdir -p /workspace/vibes/examples/tools
  mkdir -p /workspace/vibes/examples/documentation
```

### Phase 2: Enhanced Templates

```yaml
Task 3: Create feature_template.md
ACTION: Build simplified template for standard feature development
LOCATION: /workspace/vibes/prps/templates/feature_template.md
PATTERN: Based on prp_base.md but streamlined for features
SECTIONS:
  - Goal, Why, What (concise PRD)
  - Success Criteria (measurable outcomes)
  - Context (documentation, files, patterns)
  - Implementation Steps (clear task list)
  - Validation Gates (executable commands)
  - Anti-Patterns (what to avoid)

Task 4: Create tool_template.md
ACTION: Build template for tool/API integration PRPs
LOCATION: /workspace/vibes/prps/templates/tool_template.md
PATTERN: Specialized for API integrations and external tools
SECTIONS:
  - Goal (what tool/API to integrate)
  - API Documentation (links and key endpoints)
  - Authentication Setup (API keys, OAuth flow)
  - Implementation Blueprint (tool functions)
  - Error Handling (rate limits, timeouts)
  - Testing Strategy (mocked and live tests)
  - Validation Gates

Task 5: Create documentation_template.md
ACTION: Build template for documentation generation tasks
LOCATION: /workspace/vibes/prps/templates/documentation_template.md
PATTERN: Specialized for docs, READMEs, guides
SECTIONS:
  - Goal (what to document)
  - Audience (who reads this)
  - Content Structure (outline)
  - Examples to Include
  - Validation (clarity, completeness)
```

### Phase 3: Reference Examples

```yaml
Task 6: Create examples/README.md
ACTION: Write guide explaining how to use examples
LOCATION: /workspace/vibes/examples/README.md
CONTENT:
  - Purpose of examples (reference patterns, not copy-paste)
  - Directory structure explanation
  - How to adapt examples to specific needs
  - Link to related documentation

Task 7: Create simple-feature.md example
ACTION: Complete example of a basic feature PRP
LOCATION: /workspace/vibes/examples/prp-workflow/simple-feature.md
CONTENT:
  - Real example: "Add user authentication endpoint"
  - Shows all required PRP sections
  - Demonstrates validation gates
  - Clear success criteria

Task 8: Create complex-feature.md example
ACTION: Example of multi-component feature PRP
LOCATION: /workspace/vibes/examples/prp-workflow/complex-feature.md
CONTENT:
  - Real example: "Multi-agent system with research + email"
  - Shows task breakdown
  - Demonstrates progressive validation
  - Integration points

Task 9: Create api_integration.py example
ACTION: Python pattern for API integration
LOCATION: /workspace/vibes/examples/tools/api_integration.py
CONTENT: |
  """
  Example: External API Integration Pattern

  Demonstrates:
  - Configuration with environment variables
  - Async HTTP client usage
  - Error handling and retries
  - Rate limiting
  - Response validation with Pydantic
  """

  # Full working example with httpx, pydantic, tenacity

Task 10: Create file_operations.py example
ACTION: Python pattern for file operations
LOCATION: /workspace/vibes/examples/tools/file_operations.py
CONTENT: |
  """
  Example: Safe File Operations Pattern

  Demonstrates:
  - Path validation and sanitization
  - Atomic write operations
  - Error recovery
  - Backup creation
  - Context managers
  """

  # Full working example with pathlib, contextlib

Task 11: Create README_template.md
ACTION: Template for project READMEs
LOCATION: /workspace/vibes/examples/documentation/README_template.md
CONTENT:
  - Standard README structure
  - Badges and status indicators
  - Installation instructions
  - Usage examples
  - API reference section
  - Contributing guidelines

Task 12: Create API_doc_template.md
ACTION: Template for API documentation
LOCATION: /workspace/vibes/examples/documentation/API_doc_template.md
CONTENT:
  - Endpoint documentation structure
  - Request/response examples
  - Error codes and handling
  - Authentication documentation
  - Rate limiting information
```

### Phase 4: Commands and Documentation

```yaml
Task 13: Create list-prps.md command
ACTION: Build command to list and filter PRPs
LOCATION: /workspace/vibes/.claude/commands/list-prps.md
PATTERN: Follow existing command structure
CONTENT: |
  # List PRPs

  List all PRPs organized by status (active, completed, archived).

  ## Usage
  /list-prps [status]

  ## Options
  - No arguments: List all PRPs from all directories
  - active: Show only active PRPs
  - completed: Show completed PRPs
  - archived: Show archived PRPs

  ## Implementation
  - Scan prps/ directories
  - Display with status, title (from frontmatter), date modified
  - Sort by most recent first
  - Color-code by status

Task 14: Update README.md
ACTION: Add context engineering section to main README
LOCATION: /workspace/vibes/README.md
PATTERN: Add new section after "Current Capabilities"
CONTENT:
  - Context Engineering Philosophy (what and why)
  - PRP Workflow explanation (INITIAL → generate → execute → complete)
  - Directory structure guide
  - How to use templates and examples
  - Link to coleam00/context-engineering-intro
```

### Integration Points
```yaml
DIRECTORY_STRUCTURE:
  - prps/active/ - New PRPs being worked on
  - prps/completed/ - Finished, working PRPs
  - prps/archived/ - Old reference PRPs
  - examples/ - Reference patterns (never modify)

WORKFLOW:
  1. Create INITIAL.md with feature description
  2. Run /generate-prp INITIAL.md
  3. PRP created in prps/active/
  4. Run /execute-prp prps/active/{feature}.md
  5. Move to prps/completed/ when done
  6. Archive old PRPs to prps/archived/

COMMANDS:
  - /generate-prp - Creates PRPs in prps/active/
  - /execute-prp - Executes PRPs
  - /list-prps - Lists PRPs by status (NEW)
```

## Validation Loop

### Level 1: Structure Verification
```bash
# Verify PRP lifecycle directories exist
ls -la /workspace/vibes/prps/active/
ls -la /workspace/vibes/prps/completed/
ls -la /workspace/vibes/prps/archived/

# Verify templates created
ls -la /workspace/vibes/prps/templates/
test -f /workspace/vibes/prps/templates/feature_template.md && echo "✅ feature_template.md exists"
test -f /workspace/vibes/prps/templates/tool_template.md && echo "✅ tool_template.md exists"
test -f /workspace/vibes/prps/templates/documentation_template.md && echo "✅ documentation_template.md exists"

# Expected: All directories and templates exist
```

### Level 2: Examples Verification
```bash
# Verify examples directory structure
ls -R /workspace/vibes/examples/

# Verify key files
test -f /workspace/vibes/examples/README.md && echo "✅ README.md exists"
test -f /workspace/vibes/examples/prp-workflow/simple-feature.md && echo "✅ simple-feature.md exists"
test -f /workspace/vibes/examples/prp-workflow/complex-feature.md && echo "✅ complex-feature.md exists"
test -f /workspace/vibes/examples/tools/api_integration.py && echo "✅ api_integration.py exists"
test -f /workspace/vibes/examples/tools/file_operations.py && echo "✅ file_operations.py exists"

# Expected: All examples exist
```

### Level 3: Content Quality Check
```bash
# Verify command exists
test -f /workspace/vibes/.claude/commands/list-prps.md && echo "✅ list-prps.md exists"
cat /workspace/vibes/.claude/commands/list-prps.md | head -20

# Verify README updated
grep -q "Context Engineering" /workspace/vibes/README.md && echo "✅ README.md updated with Context Engineering section"

# Expected: Command exists and README updated
```

### Level 4: Manual Review
```bash
# Review template quality
echo "=== feature_template.md ===" && cat /workspace/vibes/prps/templates/feature_template.md
echo "=== tool_template.md ===" && cat /workspace/vibes/prps/templates/tool_template.md
echo "=== documentation_template.md ===" && cat /workspace/vibes/prps/templates/documentation_template.md

# Review examples quality
echo "=== examples/README.md ===" && cat /workspace/vibes/examples/README.md

# Expected: Clear, well-structured content
```

## Final Validation Checklist
- [ ] All PRP lifecycle directories created (active/, completed/, archived/)
- [ ] All 3 templates created and well-structured
- [ ] examples/README.md clearly explains purpose and usage
- [ ] 2 PRP workflow examples created (simple + complex)
- [ ] 2 tool examples created (api_integration + file_operations)
- [ ] 2 documentation examples created (README + API docs)
- [ ] list-prps.md command created
- [ ] README.md updated with context engineering section
- [ ] All files follow markdown best practices
- [ ] Directory structure matches specification
- [ ] Examples are clear and immediately useful

---

## Anti-Patterns to Avoid
- ❌ Don't modify existing prp_base.md or EXAMPLE_multi_agent_prp.md
- ❌ Don't create complex templates - keep them SIMPLE
- ❌ Don't make examples too abstract - use real scenarios
- ❌ Don't skip the README updates - documentation is critical
- ❌ Don't use TodoWrite - use Archon MCP for task management
- ❌ Don't create files that won't be immediately useful
- ❌ Don't forget validation gates in templates
- ❌ Don't make examples that are just "hello world" - make them practical

## Notes for Implementation

### Key Design Decisions
1. **Lifecycle Directories**: Separate active/completed/archived for better organization
2. **Specialized Templates**: Different feature types need different guidance
3. **Practical Examples**: Real scenarios, not toy examples
4. **Progressive Structure**: Foundation for future subagent patterns

### Why This Approach
- **Foundation First**: Establish solid structure before complexity
- **Learn by Doing**: Build muscle memory with PRPs through examples
- **Immediate Value**: Better organization and reference patterns right away
- **Scalable**: Structure supports adding advanced features later

### Success Metrics
- Can navigate PRPs easily by status
- Templates reduce time to create new PRPs
- Examples provide clear patterns to follow
- Developers understand context engineering philosophy

## Confidence Score: 9/10

High confidence due to:
- Clear, well-defined structure to create
- All documentation/organization work (no complex code)
- Strong reference materials from coleam00/context-engineering-intro
- Existing patterns to follow in Vibes
- Simple validation (file existence + manual review)

Minor uncertainty:
- Exact content of examples requires thoughtful design
- README integration needs to fit existing structure well