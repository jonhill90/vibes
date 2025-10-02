# Simple Subagent Pattern

This example demonstrates the basic pattern for creating a specialized subagent that performs a single, focused task.

## Pattern Overview

**Concept**: One agent, one responsibility, clear input/output

A simple subagent:
1. Receives specific inputs (file paths, context)
2. Performs focused processing
3. Produces structured output
4. Reports completion

## Example: Requirements Analyzer

### Frontmatter Definition

```markdown
---
name: requirements-analyzer
description: Analyzes user requirements and creates structured specification document
tools: Read, Write, Grep, Glob
color: blue
---
```

**Frontmatter explained**:
- `name`: Unique identifier for the agent (used in Task tool `subagent_type` parameter)
- `description`: When and why to use this agent
- `tools`: Claude Code tools this agent can access
- `color`: Visual identifier (blue=planning, green=validation, purple=implementation, etc.)

### System Prompt

```markdown
# Requirements Analyzer

You are a requirements analysis specialist. Your role is to take raw user requirements and transform them into structured, actionable specifications.

## Primary Objective

Read user requirements from an input file, analyze them for completeness and clarity, and create a well-structured specification document that developers can implement from.

## Input Specifications

### Required Inputs
- **Requirements File**: `[project]/requirements.txt` - Raw user requirements
- **Project Context**: Understanding of project goals and constraints
- **Output Path**: Where to write the specification

### What You Receive in Your Prompt
```yaml
You are requirements-analyzer.

Input File: projects/my-feature/requirements.txt
Output File: projects/my-feature/SPEC.md
Project Name: my-feature
```
```

### Processing Logic

```markdown
## Core Responsibilities

### 1. Read and Understand Requirements
- Read the requirements file completely
- Identify all functional requirements
- Identify all technical constraints
- Note any ambiguities or gaps

### 2. Structure Analysis
Organize requirements into:
- **Functional Requirements**: What the system must do
- **Technical Requirements**: How it should be built
- **Constraints**: Limitations and requirements
- **Success Criteria**: How to validate completion

### 3. Create Specification Document

Output structure:
```markdown
# [Project Name] Specification

## Overview
[Brief summary]

## Functional Requirements
1. [Requirement 1]
2. [Requirement 2]
...

## Technical Requirements
- [Tech requirement 1]
- [Tech requirement 2]
...

## Constraints
- [Constraint 1]
...

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
...
```
```

### Quality Standards

```markdown
## Quality Checklist

Before finalizing output:
- [ ] All input requirements addressed
- [ ] Requirements are specific and measurable
- [ ] Technical approach is clear
- [ ] Success criteria are testable
- [ ] No ambiguous language
- [ ] File written to correct path
```

## Invocation Example

### From Main Orchestrator

```markdown
I'm analyzing the requirements for the new feature...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Analyze feature requirements</description>
    <prompt>
You are requirements-analyzer.

**Task**: Analyze the user requirements and create a structured specification.

**Input**:
- Requirements file: `projects/authentication-system/requirements.txt`
- Project name: `authentication-system`

**Output**:
- Specification file: `projects/authentication-system/SPEC.md`

Please read the requirements, analyze them for completeness, and create a well-structured specification document following your standard format.

Include:
- Functional requirements (what the system must do)
- Technical requirements (how it should be built)
- Constraints (limitations)
- Success criteria (validation checklist)

Ensure all requirements are specific, measurable, and actionable.
    </prompt>
    <subagent_type>requirements-analyzer</subagent_type>
  </parameters>
</tool_use>
```

### Input File Example

`projects/authentication-system/requirements.txt`:
```
User needs to log in with email and password
System should remember users
Passwords need to be secure
Users should be able to reset passwords
Need social login with Google
```

### Output File Example

`projects/authentication-system/SPEC.md`:
```markdown
# Authentication System Specification

## Overview
Build a secure authentication system with email/password login, session management, password reset, and OAuth integration with Google.

## Functional Requirements

1. **Email/Password Authentication**
   - Users can create accounts with email and password
   - Users can log in with email and password
   - Invalid credentials return clear error messages

2. **Session Management**
   - Successful login creates persistent session
   - Sessions expire after 30 days of inactivity
   - Users can log out to end session

3. **Password Reset**
   - Users can request password reset via email
   - Reset links expire after 1 hour
   - New passwords must meet security requirements

4. **OAuth Integration**
   - Users can sign in with Google account
   - OAuth creates or links to existing account
   - Profile information populated from Google

## Technical Requirements

- **Password Security**: Use bcrypt with min 10 rounds
- **Session Storage**: Redis for session data
- **Email Service**: SendGrid for password reset emails
- **OAuth Library**: Use passport.js with Google strategy
- **Database**: PostgreSQL for user data

## Constraints

- Must comply with GDPR for user data
- Password reset emails must be sent within 5 minutes
- OAuth callback must complete within 30 seconds
- Support 10,000 concurrent sessions

## Success Criteria

- [ ] Users can successfully register and log in
- [ ] Sessions persist across browser restarts
- [ ] Password reset flow works end-to-end
- [ ] Google OAuth login creates/links accounts
- [ ] All passwords stored as bcrypt hashes
- [ ] Unit tests cover auth logic (>80% coverage)
- [ ] Integration tests validate full flows
```

## Key Principles Demonstrated

### 1. Single Responsibility
- **Only** analyzes requirements and creates specs
- Does NOT implement features
- Does NOT write code
- Does NOT create tests

### 2. Clear Input/Output Contract
- **Input**: Defined file path with raw requirements
- **Output**: Defined file path with structured spec
- **Format**: Markdown with consistent structure

### 3. Autonomy
- Receives all context in invocation prompt
- Operates independently
- Reports completion when done
- Does not require follow-up interaction

### 4. Quality Standards
- Built-in validation checklist
- Consistent output structure
- Measurable success criteria

## Integration with Workflows

### How It Fits in a Multi-Phase Workflow

```
Phase 1: Requirements Analysis
└─> requirements-analyzer reads requirements.txt
    └─> creates SPEC.md

Phase 2: Design (runs after Phase 1 completes)
└─> design-architect reads SPEC.md
    └─> creates DESIGN.md

Phase 3: Implementation (runs after Phase 2 completes)
└─> main Claude reads SPEC.md + DESIGN.md
    └─> implements features
```

### Markdown Communication Chain

```
[User Input]
    ↓
requirements.txt (unstructured)
    ↓
[requirements-analyzer processes]
    ↓
SPEC.md (structured)
    ↓
[Next agent consumes]
```

## Common Use Cases

### Use Case 1: New Feature Development
- User provides high-level feature description
- Subagent creates detailed specification
- Implementation team works from spec

### Use Case 2: Requirement Validation
- User provides requirements
- Subagent identifies gaps and ambiguities
- User provides clarifications
- Subagent updates spec

### Use Case 3: Documentation Generation
- Existing feature needs documentation
- Subagent analyzes code/behavior
- Creates specification retroactively

## Extending This Pattern

### Add Research Capability

```markdown
tools: Read, Write, Grep, Glob, WebSearch, mcp__archon__rag_search_knowledge_base

## Core Responsibilities

### 1. Research Best Practices
- Search knowledge base for similar features
- Find existing patterns in codebase
- Incorporate best practices in spec
```

### Add Validation

```markdown
## Validation Steps

1. Check requirements completeness
2. Validate technical feasibility
3. Identify potential conflicts
4. Flag security concerns
5. Estimate complexity
```

### Add Archon Integration

```markdown
## Research Phase

```python
# Search knowledge base for patterns
results = mcp__archon__rag_search_knowledge_base(
    query="authentication patterns",
    match_count=5
)

# Find code examples
examples = mcp__archon__rag_search_code_examples(
    query="oauth implementation",
    match_count=3
)
```
```

## Testing the Pattern

### Manual Test
1. Create test requirements file
2. Invoke subagent with Task tool
3. Verify output file created
4. Validate output structure and content

### Automated Test
```python
# In workflow validation
assert Path("projects/test/SPEC.md").exists()
spec_content = Path("projects/test/SPEC.md").read_text()
assert "## Functional Requirements" in spec_content
assert "## Success Criteria" in spec_content
```

## Summary

**Simple Subagent Pattern**:
- ✅ Single, focused responsibility
- ✅ Clear input/output contract
- ✅ Operates autonomously
- ✅ Produces consistent, structured output
- ✅ Easy to test and validate
- ✅ Integrates via markdown communication

**When to use**:
- Task is well-defined and focused
- Input/output can be clearly specified
- No complex multi-step interactions needed
- Autonomy is important

**When NOT to use**:
- Task requires interactive clarification
- Output depends on complex decision trees
- Need to coordinate with multiple other agents simultaneously
- Task is too simple to warrant a subagent

---

See [parallel-workflow.md](./parallel-workflow.md) for the next pattern: running multiple subagents simultaneously.
