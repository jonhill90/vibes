# Context Engineering Foundation Integration

## FEATURE:
Integrate foundational Context Engineering patterns from coleam00/context-engineering-intro into Vibes. This is the **SIMPLE** version focusing on core structure, templates, and basic examples without the full agent factory complexity.

## GOAL:
Create a solid foundation in Vibes that makes it easy to:
1. Use PRPs effectively for feature development
2. Create and organize documentation and examples
3. Track PRP lifecycle (active → completed)
4. Have reference patterns for common tasks
5. Set up basic structure for future subagent work

## EXAMPLES:

**Current Vibes Structure (already good):**
```
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
├── agents/                # ✅ Empty, ready
├── examples/              # ✅ Empty, needs content
├── CLAUDE.md              # ✅ Global rules
└── INITIAL.md
```

**Additions for Foundation:**
```
/workspace/vibes/
├── prps/
│   ├── templates/
│   │   ├── prp_base.md           # ✅ Exists
│   │   ├── feature_template.md   # NEW: Standard feature PRP
│   │   ├── tool_template.md      # NEW: For tool integration
│   │   └── documentation_template.md  # NEW: For doc generation
│   ├── active/                    # NEW: In-progress PRPs
│   ├── completed/                 # NEW: Finished PRPs
│   └── archived/                  # NEW: Old/reference PRPs
│
├── examples/                      # Populate with patterns
│   ├── README.md                  # NEW: Guide to examples
│   ├── prp-workflow/
│   │   ├── simple-feature.md      # NEW: Basic PRP example
│   │   └── complex-feature.md     # NEW: Multi-component PRP
│   ├── tools/
│   │   ├── api_integration.py     # NEW: API tool pattern
│   │   └── file_operations.py    # NEW: File tool pattern
│   └── documentation/
│       ├── README_template.md     # NEW: README pattern
│       └── API_doc_template.md    # NEW: API doc pattern
│
└── .claude/
    └── commands/
        └── list-prps.md           # NEW: List PRPs by status
```

## DOCUMENTATION:

**Primary References:**
- https://github.com/coleam00/context-engineering-intro
  - README.md - Context engineering philosophy
  - PRPs/templates/prp_base.md - Base template
  - EXAMPLE_multi_agent_prp.md - Complete example

**Local References:**
- /workspace/vibes/repos/context-engineering-intro/ (already cloned)
- /workspace/vibes/prps/templates/prp_base.md (our current template)
- /workspace/vibes/CLAUDE.md (our global rules)

## KEY REQUIREMENTS:

### 1. PRP Lifecycle Management

**Create Directory Structure:**
```bash
mkdir -p /workspace/vibes/prps/active
mkdir -p /workspace/vibes/prps/completed
mkdir -p /workspace/vibes/prps/archived
```

**Workflow:**
- New PRPs start in `prps/active/`
- Completed PRPs move to `prps/completed/`
- Old/reference PRPs go to `prps/archived/`

### 2. Enhanced Templates

**prps/templates/feature_template.md:**
- Standard feature development template
- Includes: Goal, Why, What, Context, Implementation Blueprint
- Validation gates included
- Simpler than full prp_base.md

**prps/templates/tool_template.md:**
- For adding new tools/integrations
- API documentation references
- Authentication setup
- Error handling patterns

**prps/templates/documentation_template.md:**
- For documentation generation tasks
- README structure
- API documentation
- User guides

### 3. Examples Directory

**examples/README.md:**
```markdown
# Vibes Examples

This directory contains reference patterns and examples for common development tasks.

## Structure
- prp-workflow/ - How to use PRPs effectively
- tools/ - Tool integration patterns
- documentation/ - Documentation templates

## How to Use
Examples are NOT meant to be copied directly. They are reference patterns
showing best practices and approaches. Adapt them to your specific needs.
```

**examples/prp-workflow/simple-feature.md:**
- Complete example of a simple feature PRP
- Shows all required sections
- Demonstrates validation gates
- Clear success criteria

**examples/prp-workflow/complex-feature.md:**
- Multi-component feature example
- Shows how to break down complex tasks
- Demonstrates progressive success approach

**examples/tools/api_integration.py:**
```python
"""
Example pattern for integrating external APIs.
Demonstrates:
- Configuration management with python-dotenv
- Error handling
- Rate limiting
- Retry logic
"""
```

**examples/tools/file_operations.py:**
```python
"""
Example pattern for file operations.
Demonstrates:
- Safe file reading/writing
- Path handling
- Error recovery
- Validation
"""
```

### 4. Commands

**list-prps.md:**
```markdown
# List PRPs

List all PRPs organized by status (active, completed, archived).

## Usage
Show PRPs with optional filtering:
- All PRPs: List everything
- By status: Show active/completed/archived
- By date: Recent PRPs first
```

### 5. Documentation

**Update README.md:**
Add section explaining:
- Context engineering philosophy
- PRP workflow (INITIAL → generate → execute → complete)
- Directory structure
- How to use examples

## SUCCESS CRITERIA:
- [ ] PRP lifecycle directories created (active/, completed/, archived/)
- [ ] 3 new templates created (feature, tool, documentation)
- [ ] examples/ directory populated with at least 5 reference files
- [ ] examples/README.md written with clear guidance
- [ ] list-prps.md command created
- [ ] Main README.md updated with context engineering section
- [ ] Can successfully track a PRP through lifecycle
- [ ] Examples are clear and helpful

## CONSTRAINTS:
- Keep it SIMPLE - no subagents in this version
- Focus on structure and patterns, not complexity
- All examples must be well-documented
- Don't modify existing working files
- Use vibes:run_command for all operations

## VALIDATION:
```bash
# Verify structure
ls -la /workspace/vibes/prps/active/
ls -la /workspace/vibes/prps/completed/
ls -la /workspace/vibes/prps/archived/

# Check templates
ls /workspace/vibes/prps/templates/
cat /workspace/vibes/prps/templates/feature_template.md

# Verify examples
ls -R /workspace/vibes/examples/
cat /workspace/vibes/examples/README.md

# Test command
cat /workspace/vibes/.claude/commands/list-prps.md
```

## IMPLEMENTATION NOTES:

### Phase 1: Structure
1. Create directory structure
2. Add lifecycle folders
3. Set up examples skeleton

### Phase 2: Templates
1. Create feature_template.md
2. Create tool_template.md
3. Create documentation_template.md

### Phase 3: Examples
1. Write examples/README.md
2. Create PRP workflow examples
3. Add tool patterns
4. Add documentation templates

### Phase 4: Commands & Docs
1. Create list-prps.md command
2. Update main README.md
3. Test full workflow

## WHY THIS VERSION:

**Foundation First Approach:**
- Establish solid structure before complexity
- Learn context engineering basics
- Build muscle memory with PRPs
- Set up for future enhancements

**Progressive Enhancement:**
- This foundation supports adding subagents later
- Examples can be extended with advanced patterns
- Structure scales from simple to complex

**Immediate Value:**
- Better PRP organization right away
- Reference patterns for common tasks
- Clear workflow for feature development
- Documentation standards established
