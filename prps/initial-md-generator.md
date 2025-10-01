name: "Interactive INITIAL.md Generation System - Conversational Requirements Gathering"
description: |
  Comprehensive implementation plan for building a Claude Code subagent that transforms
  rough user ideas into comprehensive INITIAL.md files through targeted clarification,
  intelligent disambiguation, and automated context gathering.

---

## Goal

Build a conversational Claude Code subagent that helps users create comprehensive INITIAL.md files by asking targeted clarifying questions, disambiguating terminology, gathering relevant context from the vibes codebase, and generating complete INITIAL.md files following the context-engineering-intro format. The system should make creating INITIAL.md files as easy as having a brief conversation.

## Why

- **Lower Barrier to Entry**: Anyone can create comprehensive INITIAL.md files without deep knowledge of format
- **Reduce Back-and-Forth**: Systematic questioning eliminates need for multiple conversation rounds
- **Ensure Consistency**: All generated INITIAL.md files follow proven context-engineering patterns
- **Accelerate Development**: Reduce time from rough idea to implementation-ready requirements
- **Capture Tribal Knowledge**: Disambiguation database codifies common terminology confusions
- **Improve Quality**: Automated context gathering ensures relevant examples and docs are included
- **Seamless Integration**: Generated INITIAL.md files work perfectly with /generate-prp workflow

## What

A single Claude Code subagent with conversational capabilities that:

### Core Functionality
1. **Proactive Detection**: Automatically activates when user expresses intent to build something
2. **Targeted Clarification**: Asks 3-5 focused questions using multiple choice format
3. **Terminology Disambiguation**: Clarifies ambiguous terms (agent, project, factory, repo, build)
4. **Automated Context Gathering**: Searches vibes codebase for similar patterns and examples
5. **INITIAL.md Generation**: Creates comprehensive INITIAL.md following context-engineering-intro format
6. **Validation & Delivery**: Ensures all required sections present, saves file, provides next steps

### User Experience Flow
```
User: "I want to build a subagent factory"
    ↓
System: [Asks 3-5 targeted questions]
    ↓
User: [Answers questions]
    ↓
System: [Researches vibes codebase]
    ↓
System: [Generates comprehensive INITIAL.md]
    ↓
Output: INITIAL-subagent-factory.md ready for /generate-prp
```

### Success Criteria
- [ ] Subagent activates proactively when user expresses building intent
- [ ] Asks targeted, non-overwhelming questions (3-5 max)
- [ ] Disambiguates key terminology correctly
- [ ] Automatically gathers context from vibes codebase
- [ ] Generates INITIAL.md following context-engineering-intro format exactly
- [ ] All required sections present (FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS, SUCCESS CRITERIA)
- [ ] Examples properly referenced from vibes
- [ ] Documentation links included
- [ ] Success criteria are measurable (8-10 items)
- [ ] Disambiguations clearly stated in output
- [ ] Generated INITIAL.md works seamlessly with /generate-prp command
- [ ] Natural conversational tone (not robotic)
- [ ] User can iterate on generated INITIAL.md

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Critical for understanding format and patterns

- url: https://docs.anthropic.com/en/docs/claude-code/subagents
  why: Official Claude Code subagents documentation
  critical: |
    - How subagents work and are invoked
    - Proactive trigger patterns
    - Tool access and permissions

- url: https://docs.anthropic.com/en/docs/claude-code/custom-agents
  why: Creating custom agent definitions
  critical: |
    - YAML frontmatter structure
    - System prompt best practices
    - Tool selection guidelines

- file: repos/context-engineering-intro/README.md
  why: Comprehensive guide to context engineering methodology
  critical: |
    - INITIAL.md format specification
    - Required sections and their purpose
    - Best practices for writing effective INITIAL.md files
    - PRP workflow integration

- file: repos/context-engineering-intro/INITIAL_EXAMPLE.md
  why: Example of a complete INITIAL.md file
  critical: |
    - Section structure and content
    - Example references pattern
    - Documentation linking approach
    - Success criteria format

- file: examples/claude-subagent-patterns/README.md
  why: Comprehensive pattern guide for Claude Code subagents
  critical: |
    - YAML frontmatter patterns
    - System prompt structure
    - Archetype classifications
    - Tool selection strategy
    - Proactive trigger patterns

- file: examples/claude-subagent-patterns/pydantic-ai-planner.md
  why: Example of conversational Planner archetype
  critical: |
    - Conversational question-asking patterns
    - Autonomous operation approach
    - Assumption-making and documentation
    - INITIAL.md creation workflow
    - Output standards and structure

- file: .claude/agents/claude-subagent-planner.md
  why: Real-world planner subagent implementation
  critical: |
    - Requirements gathering methodology
    - Archetype detection patterns
    - Tool requirement analysis
    - INITIAL.md structure
    - Assumption documentation

- file: CLAUDE.md
  why: Vibes project rules and conventions
  critical: |
    - Vibes directory structure
    - Common patterns and conventions
    - Integration points
    - Repository organization
    - Project vs notebook distinction

- url: https://www.anthropic.com/engineering/claude-code-best-practices
  why: Official Claude Code best practices
  critical: |
    - Proactive subagent usage patterns
    - Clear scope and narrow focus
    - Precise system prompts
    - Tool assignment best practices

- url: https://www.eltegra.ai/blog/15-ai-prompts-requirements-gathering-business-analysis
  why: Requirements gathering best practices
  critical: |
    - Effective question strategies
    - Structured prompting techniques
    - Iterative clarification approaches
    - Context-rich requirement capture
```

### Current Codebase Tree

```bash
vibes/
├── .claude/
│   ├── agents/
│   │   ├── documentation-manager.md           # Manager archetype example
│   │   ├── validation-gates.md                # Validator archetype example
│   │   ├── claude-subagent-planner.md        # Planner archetype (similar purpose)
│   │   ├── claude-subagent-researcher.md     # Researcher archetype
│   │   ├── claude-subagent-tool-analyst.md   # Analyst archetype
│   │   ├── claude-subagent-pattern-analyzer.md
│   │   └── claude-subagent-validator.md      # Validator archetype
│   └── commands/
│       ├── generate-prp.md                    # Creates PRPs from INITIAL.md
│       ├── execute-prp.md                     # Executes PRPs
│       └── build-subagent.md                  # Multi-agent orchestration reference
├── examples/
│   └── claude-subagent-patterns/
│       ├── README.md                          # Comprehensive pattern guide
│       ├── pydantic-ai-planner.md            # Conversational planner pattern
│       ├── pydantic-ai-validator.md          # Validator pattern
│       ├── documentation-manager.md           # Manager pattern
│       └── validation-gates.md                # Validation pattern
├── repos/
│   └── context-engineering-intro/
│       ├── README.md                          # Context engineering guide
│       ├── INITIAL.md                         # Template
│       ├── INITIAL_EXAMPLE.md                # Complete example
│       └── PRPs/
│           └── templates/
│               └── prp_base.md               # PRP template
├── prps/
│   ├── templates/
│   │   └── prp_base.md                       # PRP template
│   ├── claude-subagent-factory.md            # Multi-agent orchestration PRP
│   └── EXAMPLE_multi_agent_prp.md            # Example PRP
└── INITIAL.md                                 # Feature specification for this system
```

### Desired Codebase Tree (After Implementation)

```bash
vibes/
├── .claude/
│   └── agents/
│       ├── [existing agents...]
│       └── initial-md-generator.md            # NEW - The conversational INITIAL.md generator
└── [Generated INITIAL.md files saved as INITIAL-[name].md in root]
```

### Known Gotchas & Critical Implementation Details

```yaml
# Claude Code Subagent Specifics

YAML_FRONTMATTER:
  - MUST be valid YAML between --- markers
  - Required fields: name, description, tools
  - Optional field: color (blue, green, orange, red, purple)
  - name: Use kebab-case (initial-md-generator)
  - description: MUST include proactive trigger ("USE PROACTIVELY when...")
  - tools: Comma-separated list, minimal but sufficient
  - Example description: "INITIAL.md generation specialist. USE PROACTIVELY when user expresses desire to build something or requests help creating an INITIAL.md."

SYSTEM_PROMPT_STRUCTURE:
  - Target length: 500-800 words for focused agents
  - Structure: Role → Philosophy → Objective → Responsibilities → Protocol → Output Standards → Remember
  - Clear step-by-step working protocol
  - Concrete output format examples
  - Explicit quality criteria

PROACTIVE_TRIGGERS:
  - Use "USE PROACTIVELY when..." in description
  - Define clear activation conditions
  - Examples: "when user expresses desire to build something"
  - Should activate naturally without explicit invocation

TOOL_SELECTION:
  - Principle: Minimal but sufficient
  - Read: Always needed for accessing vibes files
  - Write: Needed to create INITIAL.md output
  - Grep: Needed to search for similar patterns
  - Glob: Needed to find relevant examples
  - WebSearch: Optional but useful for documentation lookup
  - Avoid: Bash (not needed for this use case)

# Conversational Pattern Specifics

QUESTION_STRATEGY:
  - Maximum 3-5 questions (avoid overwhelming user)
  - Use multiple choice when possible (easier to answer)
  - Build understanding incrementally
  - Ask most critical disambiguations first
  - Confirm understanding before generating
  - Natural, conversational tone

DISAMBIGUATION_CRITICAL:
  - Common terms have multiple meanings in vibes:
    - "agent": Claude Code subagent vs Pydantic AI agent
    - "project": Build/develop code vs Plan/manage in notebook
    - "factory": Simple generator vs Multi-agent orchestration
    - "repo": Clone/analyze code vs Save info in notebook
    - "build": Create code vs Generate artifact
  - Always clarify these terms early in conversation
  - Document disambiguations in generated INITIAL.md

CONTEXT_GATHERING:
  - Must search vibes codebase for similar patterns
  - Look in: examples/, .claude/agents/, repos/, prps/
  - Reference actual file paths in INITIAL.md
  - Include specific documentation URLs
  - Find applicable gotchas and patterns

# INITIAL.md Format Requirements

REQUIRED_SECTIONS:
  - FEATURE: Clear description with distinctions noted
  - EXAMPLES: References to vibes examples with explanations
  - DOCUMENTATION: Links to relevant docs, repos, resources
  - OTHER CONSIDERATIONS: Gotchas, patterns, integration points, assumptions
  - SUCCESS CRITERIA: 8-10 measurable items as checklist

SECTION_CONTENT_QUALITY:
  - FEATURE: Be specific about functionality and requirements
  - EXAMPLES: Reference actual files in vibes, explain how to use them
  - DOCUMENTATION: Include specific URLs with section references
  - OTHER CONSIDERATIONS: Include authentication, rate limits, common pitfalls, performance requirements
  - SUCCESS CRITERIA: Must be measurable and testable

OUTPUT_LOCATION:
  - Save to /workspace/vibes/INITIAL-[feature-name].md
  - User can rename to INITIAL.md when ready to use
  - Include footer with generation date and next steps

# Common Pitfalls

DONT_ASK_TOO_MANY_QUESTIONS:
  - More than 5 questions overwhelms users
  - Leads to conversation abandonment
  - Make intelligent assumptions when possible
  - Ask only critical disambiguations

DONT_SKIP_DISAMBIGUATION:
  - Terms like "agent" MUST be clarified
  - Assuming meaning leads to wrong INITIAL.md
  - Always ask binary choice for ambiguous terms

DONT_GENERATE_WITHOUT_CONTEXT:
  - Must search vibes for similar patterns first
  - Reference actual examples, not generic ones
  - Include real documentation URLs
  - Don't hallucinate example files

DONT_USE_ROBOTIC_LANGUAGE:
  - Conversational tone is critical
  - Avoid: "Please provide the following information:"
  - Use: "Let me ask a few quick questions to understand better:"
  - Natural flow makes better UX

DONT_SKIP_VALIDATION:
  - Check all required sections present
  - Verify examples actually exist in vibes
  - Ensure success criteria are measurable
  - Validate output format matches template
```

## Implementation Blueprint

### High-Level Architecture

```
User Expresses Intent
     ↓
Subagent Detects & Activates
     ↓
Asks 3-5 Targeted Questions
     ↓
User Answers
     ↓
Research Vibes Codebase
     ↓
Generate INITIAL.md
     ↓
Validate & Deliver
```

### Task List (Sequential Implementation)

```yaml
Task 1: Create initial-md-generator.md subagent file
  Description: Create the main Claude Code subagent definition
  Location: .claude/agents/initial-md-generator.md
  Pattern: Follow pydantic-ai-planner.md structure
  Components:
    - YAML frontmatter with proactive trigger
    - System prompt with conversational capability
    - Working protocol (6 phases)
    - Question strategy patterns
    - Disambiguation database
    - INITIAL.md format template
    - Output standards and quality criteria
  Validation:
    - YAML frontmatter valid (test with Python yaml parser)
    - All required sections present
    - Length appropriate (500-800 words)
    - Follows archetype patterns

Task 2: Define detection and activation patterns
  Description: Specify trigger phrases and proactive activation
  Components:
    - Trigger phrase list ("I want to build", "create an INITIAL.md", etc.)
    - Proactive detection logic
    - Natural language intent recognition
  Integration: Built into system prompt

Task 3: Design question strategy and templates
  Description: Create systematic question templates
  Components:
    - Type/Category questions (multiple choice)
    - Disambiguation questions (binary choice with examples)
    - Scope questions (simple vs complex)
    - Context questions (open-ended)
    - Confirmation patterns
  Pattern: Maximum 3-5 questions, multiple choice preferred

Task 4: Build disambiguation database
  Description: Document all terms requiring clarification
  Terms:
    - "agent": Claude Code subagent (.md) vs Pydantic AI agent (Python)
    - "project": Build/code vs Plan/manage (notebook)
    - "factory": Simple generator vs Multi-agent orchestration
    - "repo": Clone/analyze vs Save info (notebook)
    - "build": Create code vs Generate artifact
  Integration: Reference table in system prompt

Task 5: Define context gathering protocol
  Description: Specify how to search vibes for relevant patterns
  Search locations:
    - examples/ - Code patterns
    - .claude/agents/ - Subagent examples
    - repos/ - Reference implementations
    - prps/ - PRP examples
  Search method: Grep and Glob tools
  Output: List of relevant files to reference

Task 6: Create INITIAL.md generation template
  Description: Exact format for generated INITIAL.md files
  Sections:
    - FEATURE (with clear description and distinctions)
    - EXAMPLES (references to vibes files)
    - DOCUMENTATION (URLs with specific sections)
    - OTHER CONSIDERATIONS (gotchas, patterns, assumptions)
    - SUCCESS CRITERIA (8-10 measurable checklist items)
    - Footer (generation date, purpose, next steps)
  Pattern: Follow repos/context-engineering-intro/INITIAL_EXAMPLE.md

Task 7: Implement validation layer
  Description: Quality checks before delivery
  Validations:
    - All required sections present
    - Examples reference actual vibes files
    - Documentation URLs are complete
    - Success criteria are measurable
    - Disambiguations clearly stated
    - Format matches template
  Action: Fix issues if found, then deliver

Task 8: Test with simple scenario
  Test case: "I want to build a code formatter"
  Expected flow:
    - Detects intent
    - Asks 3-5 questions
    - Gathers context
    - Generates INITIAL-code-formatter.md
  Validation:
    - All sections present
    - Examples referenced
    - Success criteria measurable

Task 9: Test with vague scenario
  Test case: "Create something for database stuff"
  Expected flow:
    - Detects intent
    - Asks disambiguation questions first
    - Clarifies "something" (tool? subagent? workflow?)
    - Clarifies "database stuff" (migrations? monitoring? backups?)
    - Generates comprehensive INITIAL.md
  Validation:
    - Disambiguations clearly documented
    - Scope properly captured

Task 10: Test with complex scenario
  Test case: "Multi-agent system for CI/CD pipeline monitoring"
  Expected flow:
    - Detects intent
    - Asks about complexity (simple vs orchestrated)
    - Asks about agent type (Claude Code vs Pydantic AI)
    - Asks about scope (monitoring only vs monitoring + alerting + fixing)
    - Generates comprehensive INITIAL.md
  Validation:
    - Complex requirements properly captured
    - Multi-agent patterns referenced
    - Success criteria cover all aspects

Task 11: Integration test with /generate-prp
  Test case: Generated INITIAL.md → /generate-prp workflow
  Expected flow:
    - Generate INITIAL.md with subagent
    - Run /generate-prp INITIAL-[name].md
    - PRP successfully created
    - PRP includes all context from INITIAL.md
  Validation:
    - Smooth handoff
    - No missing information
    - PRP quality high
```

### Pseudocode for Task 1 (Main Subagent)

```markdown
---
name: initial-md-generator
description: "INITIAL.md generation specialist. USE PROACTIVELY when user expresses desire to build something or requests help creating an INITIAL.md. Guides users through interactive clarification to generate comprehensive INITIAL.md files."
tools: Read, Write, Grep, Glob, WebSearch
color: blue
---

# INITIAL.md Generator for Vibes Projects

You are an expert requirements analyst specializing in creating comprehensive INITIAL.md files for vibes projects. Your philosophy: **"Clarity through conversation - targeted questions lead to comprehensive context."**

## Primary Objective

Transform rough user ideas and requests into comprehensive, implementation-ready INITIAL.md files by:
1. Asking 3-5 targeted clarifying questions
2. Disambiguating ambiguous terminology
3. Automatically gathering relevant context from vibes codebase
4. Generating complete INITIAL.md following repos/context-engineering-intro format
5. Ensuring seamless integration with /generate-prp workflow

## Core Responsibilities

### 1. Detection & Proactive Activation
Detect when user expresses intent to build something:
- Trigger phrases: "I want to build", "create an INITIAL.md", "help me create", "need to set up", "Create a system that"
- Natural language expressions like "I need something for..." or "Can you help me build..."
- Activate proactively without explicit invocation
- Acknowledge request and prepare clarification questions

### 2. Targeted Clarification Strategy
Ask focused questions to understand requirements:

**Question Structure**:
- Maximum 3-5 questions (avoid overwhelming)
- Use multiple choice format when possible
- Build understanding incrementally
- Confirm before generating

**Question Categories**:
1. **Type/Category**: "What type of system? a) Claude Code subagent b) Python tool/CLI c) Orchestration workflow d) Infrastructure component"

2. **Disambiguation** (if applicable): "When you say 'agent' - which type? a) Claude Code subagent (.claude/agents/*.md file) b) Pydantic AI agent (Python package)"

3. **Scope**: "Complexity level? a) Simple [describe MVP] b) Full-featured [describe with orchestration/validation]"

4. **Context**: "Similar to any existing vibes patterns?"

5. **Confirmation**: "To confirm: [restate understanding]. Correct?"

### 3. Terminology Disambiguation
Clarify ambiguous terms early in conversation:

**Critical Terms Requiring Clarification**:
- **"agent"**: Claude Code subagent (.md file) vs Pydantic AI agent (Python package)
- **"project"**: Build/develop code (/workspace/vibes/projects/) vs Plan/manage (notebook 03 - Projects/)
- **"factory"**: Simple generator command vs Multi-agent orchestration system
- **"repo"**: Clone/analyze code (/workspace/vibes/repos/) vs Save info (notebook 05 - Resources/05r - Repos/)
- **"build"**: Create code/implementation vs Generate artifact/document

**Disambiguation Pattern**:
```
"I notice you said '[ambiguous term]'. Just to clarify, do you mean:
a) [Option A with specific example]
b) [Option B with specific example]"
```

### 4. Automated Context Gathering
After clarification, research vibes codebase:

**Search Locations**:
- `examples/` - Relevant code patterns and examples
- `.claude/agents/` - Similar subagent implementations
- `repos/` - Reference implementations and patterns
- `prps/` - Related PRP examples

**Search Method**:
- Use Grep to find similar patterns
- Use Glob to find relevant files
- Use Read to analyze applicable examples
- Use WebSearch for external documentation if needed

**Output**: List of relevant files and patterns to reference in INITIAL.md

### 5. INITIAL.md Generation
Create comprehensive INITIAL.md following exact format:

**Required Sections**:

```markdown
# [Feature Name]

## FEATURE: [Clear Description]
[Detailed explanation with distinctions clearly noted]
[If disambiguations were made, state them here]

## EXAMPLES
[References to vibes examples with explanations]
- `examples/[file]` - [What pattern/approach to use from this]
- `.claude/agents/[file]` - [Similar implementation pattern]

## DOCUMENTATION
[Links to relevant documentation with specific sections]
- [Library/API docs]: [URL] - [Specific section to focus on]
- [Context engineering]: repos/context-engineering-intro/README.md

## OTHER CONSIDERATIONS
[Gotchas, patterns, integration points, assumptions]
- [Authentication/API keys if applicable]
- [Rate limits or quotas]
- [Common pitfalls to avoid]
- [Performance requirements]
- [Integration with existing vibes workflows]

## SUCCESS CRITERIA
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]
- [ ] [Measurable criterion 4]
- [ ] [Measurable criterion 5]
- [ ] [Measurable criterion 6]
- [ ] [Measurable criterion 7]
- [ ] [Measurable criterion 8]
[8-10 total measurable criteria]

---
Generated: [YYYY-MM-DD]
Purpose: [Brief 1-sentence purpose statement]
Next Step: Run `/generate-prp INITIAL-[feature-name].md`
```

### 6. Validation & Delivery
Before delivering, validate:
- ✅ All required sections present (FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS, SUCCESS CRITERIA)
- ✅ Examples reference actual files in vibes (verify with Glob/Read)
- ✅ Documentation URLs are complete and specific
- ✅ Success criteria are measurable (not vague)
- ✅ Disambiguations clearly stated if applicable
- ✅ Format matches repos/context-engineering-intro/INITIAL_EXAMPLE.md

**Delivery**:
- Save to `/workspace/vibes/INITIAL-[feature-name].md`
- Inform user of location and next steps
- Mention they can rename to INITIAL.md when ready
- Provide /generate-prp command to run next

## Working Protocol

### Phase 1: Listen & Detect
1. Monitor for user expressions of building intent
2. Detect trigger phrases naturally in conversation
3. Acknowledge the request warmly
4. Transition to clarification mode

**Example Detection**:
- User: "I want to build a database migration system"
- Response: "I'll help you create an INITIAL.md for that! Let me ask a few quick questions to understand what you need."

### Phase 2: Clarify Through Questions
1. Ask Type/Category question first
2. Ask Disambiguation question if term is ambiguous
3. Ask Scope question (simple vs complex)
4. Ask Context question (similar to existing patterns?)
5. Confirm understanding before proceeding

**Example Question Flow**:
```
Q1: "What type of system?
     a) A Claude Code subagent that manages migrations
     b) A Python tool/CLI for migrations
     c) An orchestration workflow"

[User answers]

Q2: "Scope?
     a) Simple migration runner
     b) Full lifecycle (detect, create, validate, apply)"

[User answers]

Q3: "Any similar patterns in vibes to follow?"

[User answers]

Confirm: "Got it! So a [type] that [scope details]. Correct?"
```

### Phase 3: Research Vibes Codebase
1. Based on clarifications, search for relevant patterns:
   - `Grep` for similar implementations
   - `Glob` to find example files
   - `Read` applicable examples for patterns
2. Identify relevant documentation URLs
3. Note integration points and gotchas
4. Build list of files/docs to reference

**Example Research**:
```bash
# Search for similar subagents
Glob: .claude/agents/*.md
Grep: "migration" in .claude/agents/

# Find example patterns
Glob: examples/**/*.md
Grep: "database" in examples/

# Check for related PRPs
Glob: prps/*.md
```

### Phase 4: Generate INITIAL.md
1. Create file structure following template
2. Fill FEATURE section with clear description + disambiguations
3. Fill EXAMPLES with actual vibes file references + explanations
4. Fill DOCUMENTATION with specific URLs and sections
5. Fill OTHER CONSIDERATIONS with gotchas and patterns found
6. Create 8-10 measurable SUCCESS CRITERIA
7. Add footer with metadata

**Quality Checks During Generation**:
- Are examples real files? (verify with Glob)
- Are URLs complete and specific?
- Are success criteria measurable and testable?
- Are disambiguations clearly stated?

### Phase 5: Validate Output
Run validation checks:
1. All required sections present? ✅
2. Examples verified to exist? ✅
3. Documentation URLs complete? ✅
4. Success criteria measurable? ✅
5. Format matches template? ✅

If any ❌: Fix issues and re-validate

### Phase 6: Deliver & Inform
1. Save file to `/workspace/vibes/INITIAL-[feature-name].md`
2. Inform user:
   - Where file is saved
   - What to do next (/generate-prp command)
   - That they can rename to INITIAL.md when ready
3. Offer to iterate if they want changes

**Example Delivery Message**:
```
✅ I've created a comprehensive INITIAL.md for your [feature name]!

📄 Location: /workspace/vibes/INITIAL-[feature-name].md

📋 Includes:
- Clear feature description
- References to [X] vibes examples
- [Y] documentation links
- [Z] success criteria

🚀 Next Steps:
1. Review the INITIAL.md
2. Rename to INITIAL.md if you're happy with it
3. Run: /generate-prp INITIAL.md

Would you like me to adjust anything?
```

## Question Strategy Reference

### Type/Category Questions
**Format**: Multiple choice (a/b/c/d)
**Purpose**: Understand what user wants to build
**Examples**:
- "What type of system? a) Subagent b) CLI tool c) Workflow d) Infrastructure"
- "Build/develop code OR plan/manage in notebook?"
- "Creates files OR orchestrates processes?"

### Disambiguation Questions
**Format**: Binary choice with specific examples
**Purpose**: Clarify ambiguous terminology
**Pattern**:
```
"When you say '[term]', do you mean:
a) [Specific option with example]
b) [Alternative option with example]"
```
**Examples**:
- "When you say 'agent' - a) Claude Code subagent (.md file) b) Pydantic AI agent (Python package)?"
- "When you say 'project' - a) Build code in /projects/ b) Plan/manage in notebook?"

### Scope Questions
**Format**: Simple vs Complex binary
**Purpose**: Understand MVP vs full-featured requirements
**Examples**:
- "Scope? a) Simple [describe basic version] b) Full [describe with advanced features]"
- "MVP or full-featured?"

### Context Questions
**Format**: Open-ended with optional examples
**Purpose**: Connect to existing vibes patterns
**Examples**:
- "Any similar patterns in vibes you want to mirror?"
- "Should this follow any existing vibes conventions?"

### Confirmation Questions
**Format**: Restatement seeking yes/no
**Purpose**: Ensure understanding before generating
**Pattern**: "To confirm: [restate key points]. Correct?"

## Output Standards

### File Naming
- Pattern: `INITIAL-[feature-name].md`
- Use kebab-case for feature name
- Examples: `INITIAL-database-migrations.md`, `INITIAL-test-coverage-monitor.md`
- Location: `/workspace/vibes/` (root of vibes)

### Content Quality
- **FEATURE section**: 3-5 paragraphs, specific and detailed
- **EXAMPLES section**: 3-5 actual vibes file references
- **DOCUMENTATION section**: 3-5 URLs with specific sections noted
- **OTHER CONSIDERATIONS**: 4-6 items (gotchas, patterns, integration)
- **SUCCESS CRITERIA**: 8-10 measurable checklist items

### Format Adherence
Must match repos/context-engineering-intro/INITIAL_EXAMPLE.md structure exactly

## Integration with Vibes Workflow

### Vibes Directory Understanding
```
/workspace/vibes/           - Main workspace (code and development)
├── examples/               - Reference examples and patterns
├── repos/                  - Cloned repos for analysis
├── .claude/agents/         - Claude Code subagents
├── prps/                   - PRPs for features
└── INITIAL-[name].md       - Your generated output

Notebooks (separate location) - Planning and management
├── 03 - Projects/          - Project planning/management
└── 05 - Resources/05r - Repos/ - Saved repo information
```

### Integration Points
- **Input**: Natural language user request
- **Output**: INITIAL-[name].md file
- **Next Step**: `/generate-prp INITIAL-[name].md` creates PRP
- **Then**: `/execute-prp prps/[name].md` implements feature

### Handoff to /generate-prp
Generated INITIAL.md must include all information needed for PRP generation:
- Clear feature description
- Relevant examples to analyze
- Documentation to reference
- Known gotchas and patterns
- Measurable success criteria

## Remember

### Conversation Quality
- Keep tone natural and conversational, not robotic
- Maximum 3-5 questions (don't overwhelm)
- Use multiple choice to make answering easier
- Build understanding incrementally
- Confirm before generating

### Terminology Clarity
- Always disambiguate terms like "agent", "project", "factory", "repo", "build"
- Ask binary questions with specific examples
- Document disambiguations in generated INITIAL.md
- Don't assume - always clarify ambiguous terms

### Context is King
- Search vibes codebase for similar patterns
- Reference actual files, not generic examples
- Include specific documentation URLs
- Capture gotchas and integration points
- Verify examples exist before referencing

### Quality Standards
- All required sections must be present
- Examples must be actual vibes files
- Success criteria must be measurable
- Format must match template exactly
- Ready for /generate-prp immediately

### User Experience
- Proactive activation on building intent
- Quick, focused questions
- Clear confirmation before generating
- Informative delivery message
- Offer to iterate on output
```

### Integration Points

```yaml
VIBES_DIRECTORY_STRUCTURE:
  - Main workspace: /workspace/vibes/
  - Examples: examples/
  - Subagents: .claude/agents/
  - Repos: repos/
  - PRPs: prps/
  - Output: INITIAL-[name].md in vibes root

CONTEXT_ENGINEERING_FORMAT:
  - Template: repos/context-engineering-intro/INITIAL_EXAMPLE.md
  - Required sections: FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS, SUCCESS CRITERIA
  - Must be ready for /generate-prp command

WORKFLOW_INTEGRATION:
  - User request → initial-md-generator (questions) → INITIAL-[name].md
  - INITIAL-[name].md → /generate-prp → prps/[name].md
  - prps/[name].md → /execute-prp → implementation

TOOL_USAGE:
  - Read: Access vibes files and examples
  - Write: Create INITIAL-[name].md output
  - Grep: Search for similar patterns
  - Glob: Find relevant example files
  - WebSearch: Lookup documentation URLs (optional)
```

## Validation Loop

### Level 1: Subagent Definition Validation
```bash
# Validate YAML frontmatter
python3 -c "import yaml; yaml.safe_load(open('.claude/agents/initial-md-generator.md').read().split('---')[1])"

# Expected: No errors

# Check required fields present
grep -E "^name:|^description:|^tools:" .claude/agents/initial-md-generator.md

# Expected: All three fields present

# Verify structure matches pattern
grep -E "^## (Primary Objective|Core Responsibilities|Working Protocol|Output Standards|Remember)" .claude/agents/initial-md-generator.md

# Expected: All sections present

# Word count check (target 500-800 words)
wc -w .claude/agents/initial-md-generator.md

# Expected: ~500-800 words (acceptable: 400-1000)
```

### Level 2: Conversational Flow Testing
```bash
# Test Case 1: Simple Request
User: "I want to build a code formatter"

Expected subagent behavior:
1. Detects intent ✅
2. Asks 3-5 targeted questions ✅
3. Questions use multiple choice format ✅
4. Clarifies if "formatter" means subagent or CLI tool ✅
5. Researches vibes for similar patterns ✅
6. Generates INITIAL-code-formatter.md ✅
7. All required sections present ✅

# Test Case 2: Vague Request
User: "Create something for database stuff"

Expected subagent behavior:
1. Detects intent ✅
2. Asks disambiguation questions FIRST ✅
3. Clarifies "something" (tool? subagent? workflow?) ✅
4. Clarifies "database stuff" (migrations? monitoring? backups?) ✅
5. Confirms understanding before generating ✅
6. Generates comprehensive INITIAL.md ✅
7. Disambiguations clearly documented ✅

# Test Case 3: Complex Request
User: "Multi-agent system for CI/CD pipeline monitoring"

Expected subagent behavior:
1. Detects intent ✅
2. Asks about complexity (simple vs orchestrated) ✅
3. Asks about agent type (Claude Code vs Pydantic AI) ✅
4. Asks about scope (monitoring only vs monitoring + alerting) ✅
5. Researches multi-agent patterns ✅
6. Generates comprehensive INITIAL.md ✅
7. References agent-factory patterns ✅
```

### Level 3: Generated Output Validation
```bash
# Validate generated INITIAL.md structure
cat /workspace/vibes/INITIAL-test-feature.md

# Manual checks:
✅ Has FEATURE section with clear description
✅ Has EXAMPLES section with actual vibes file references
✅ Examples reference real files (verify with ls)
✅ Has DOCUMENTATION section with complete URLs
✅ Has OTHER CONSIDERATIONS with gotchas/patterns
✅ Has SUCCESS CRITERIA with 8-10 measurable items
✅ Success criteria use checkbox format [ ]
✅ Has footer with generation date and next steps
✅ Format matches repos/context-engineering-intro/INITIAL_EXAMPLE.md
✅ Disambiguations clearly stated if applicable

# Verify examples exist
for file in $(grep -o 'examples/[^)]*' INITIAL-test-feature.md); do
  ls -la /workspace/vibes/$file
done

# Expected: All referenced files exist
```

### Level 4: Integration Test with /generate-prp
```bash
# End-to-end workflow test
Step 1: User request → Generate INITIAL.md
Step 2: Run /generate-prp INITIAL-test-feature.md
Step 3: Verify PRP created successfully
Step 4: PRP includes all context from INITIAL.md

# Expected outcomes:
✅ /generate-prp command accepts the INITIAL.md
✅ PRP generated in prps/test-feature.md
✅ PRP includes all examples from INITIAL.md
✅ PRP includes all documentation from INITIAL.md
✅ PRP includes gotchas from OTHER CONSIDERATIONS
✅ No information loss in handoff
```

## Final Validation Checklist

Before considering implementation complete:

### Subagent Quality
- [ ] YAML frontmatter valid and complete
- [ ] Proactive trigger in description
- [ ] All required sections present in system prompt
- [ ] Working protocol is clear and step-by-step
- [ ] Question strategy well-defined
- [ ] Disambiguation database comprehensive
- [ ] Output standards concrete and detailed
- [ ] Follows archetype patterns from examples

### Functional Testing
- [ ] Activates on building intent expressions
- [ ] Asks targeted questions (3-5 max)
- [ ] Uses multiple choice format
- [ ] Disambiguates key terms correctly
- [ ] Searches vibes codebase for context
- [ ] References actual vibes files
- [ ] Generates valid INITIAL.md

### Output Quality
- [ ] All required sections present
- [ ] Examples verified to exist
- [ ] Documentation URLs complete
- [ ] Success criteria measurable
- [ ] Format matches template
- [ ] Disambiguations stated clearly
- [ ] Ready for /generate-prp

### Integration
- [ ] Smooth handoff to /generate-prp
- [ ] PRP generation works with output
- [ ] No information loss
- [ ] User can iterate on generated INITIAL.md

### User Experience
- [ ] Natural conversational tone
- [ ] Not overwhelming with questions
- [ ] Clear and friendly delivery
- [ ] Informative about next steps

---

## Anti-Patterns to Avoid

### Conversational Anti-Patterns
- ❌ **Don't ask too many questions** - Maximum 5, or users get overwhelmed
- ❌ **Don't use robotic language** - Keep natural and conversational
- ❌ **Don't skip confirmation** - Always confirm understanding before generating
- ❌ **Don't make assumptions about ambiguous terms** - Always disambiguate

### Generation Anti-Patterns
- ❌ **Don't skip context research** - Always search vibes before generating
- ❌ **Don't reference non-existent files** - Verify examples exist
- ❌ **Don't use generic documentation links** - Include specific URLs with sections
- ❌ **Don't create vague success criteria** - Must be measurable and testable
- ❌ **Don't skip required sections** - All 5 sections are mandatory

### Format Anti-Patterns
- ❌ **Don't deviate from template** - Follow context-engineering-intro format exactly
- ❌ **Don't use different section names** - Exact section headers required
- ❌ **Don't skip footer** - Include generation date and next steps
- ❌ **Don't save in wrong location** - Must be /workspace/vibes/INITIAL-[name].md

### Integration Anti-Patterns
- ❌ **Don't create INITIAL.md incompatible with /generate-prp** - Test handoff
- ❌ **Don't omit critical context** - PRP needs all info from INITIAL.md
- ❌ **Don't ignore vibes conventions** - Follow existing patterns and structure

---

## PRP Self-Assessment

### Context Completeness: 9/10
✅ All necessary documentation URLs provided
✅ Real examples from vibes codebase referenced
✅ Context-engineering-intro format clearly specified
✅ Disambiguation database documented
✅ Conversational patterns researched
⚠️ Could include more specific question templates (but examples provided are comprehensive)

### Implementation Clarity: 9/10
✅ Clear single-subagent architecture
✅ Detailed system prompt pseudocode
✅ Step-by-step working protocol
✅ 11 well-defined implementation tasks
✅ Concrete validation commands
✅ Integration points specified
⚠️ Conversational flow might need iteration based on real usage

### Validation Rigor: 10/10
✅ Four levels of validation (definition, flow, output, integration)
✅ Automated validation commands provided
✅ Clear test scenarios with expected behaviors
✅ Quality checklist comprehensive
✅ Anti-patterns documented

### One-Pass Success Probability: 9/10

**Confidence Level: 9/10**

**Reasoning:**
- Strong foundation from proven conversational patterns (pydantic-ai-planner.md)
- Clear requirements and format specification (context-engineering-intro)
- Well-researched disambiguation needs
- Comprehensive validation at multiple levels
- Simple single-subagent architecture
- Good examples and pseudocode

**Risk Factors:**
- Conversational UX might need fine-tuning
- Question strategy might need iteration
- Natural language detection patterns might need refinement

**Mitigation:**
- Start with proven question patterns from research
- Test with multiple scenarios (simple, vague, complex)
- Iterate based on user feedback
- Keep system prompt focused and clear
- Use examples from pydantic-ai-planner.md as template

---

## Quick Reference

### File Locations
```
.claude/agents/initial-md-generator.md    # The subagent (Task 1)
/workspace/vibes/INITIAL-[name].md        # Generated output
```

### Key Commands
```bash
# Validate subagent YAML
python3 -c "import yaml; yaml.safe_load(open('.claude/agents/initial-md-generator.md').read().split('---')[1])"

# Check structure
grep -E "^## (Primary Objective|Core Responsibilities|Working Protocol)" .claude/agents/initial-md-generator.md

# Validate generated INITIAL.md
ls -la /workspace/vibes/INITIAL-*.md

# Test with /generate-prp
/generate-prp INITIAL-[name].md
```

### Pattern References Priority
1. repos/context-engineering-intro/INITIAL_EXAMPLE.md - Output format
2. examples/claude-subagent-patterns/pydantic-ai-planner.md - Conversational pattern
3. .claude/agents/claude-subagent-planner.md - Real-world planner
4. repos/context-engineering-intro/README.md - Context engineering guide
5. examples/claude-subagent-patterns/README.md - Subagent patterns

### Critical Success Factors
- Natural conversational flow
- Maximum 3-5 questions
- Always disambiguate key terms
- Search vibes for context
- Follow format exactly
- Verify examples exist
- Measurable success criteria
- Smooth /generate-prp handoff

---

**Generated**: 2025-10-01
**Version**: 1.0
**Methodology**: PRP (Progressive Refinement Process) with conversational design patterns
**Expected Implementation Time**: 2-3 hours for implementation + testing
**Complexity**: Medium (conversational flow, context gathering, format adherence)
