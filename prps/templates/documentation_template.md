name: "Documentation Template - For READMEs, Guides, and API Docs"
description: |

## Purpose
Template for creating or updating documentation including READMEs, user guides, API documentation, and technical specifications. Use this when documentation needs to be comprehensive and well-structured.

## Core Principles
1. **Audience First**: Write for the target reader's skill level
2. **Clear Structure**: Logical flow from overview to details
3. **Examples Included**: Show, don't just tell
4. **Validation**: Ensure accuracy and completeness

---

## Goal
[Specific documentation to create or update]

Example: "Create comprehensive API documentation for the MCP server endpoints with request/response examples"

## Why
- **User Benefit**: [How does this help users understand or use the system?]
- **Reduces Support**: [What questions will this answer proactively?]
- **Onboarding**: [How does this help new users/developers?]

## What
[Detailed description of documentation scope and content]

### Success Criteria
- [ ] [Documentation is clear and accurate]
- [ ] [All examples work correctly]
- [ ] [Covers all required topics]
- [ ] [Appropriate for target audience]
- [ ] [Easy to navigate and search]

## Context

### Audience
```yaml
PRIMARY_AUDIENCE: [Developers | Users | DevOps | Mixed]
SKILL_LEVEL: [Beginner | Intermediate | Advanced]
USE_CASE: [Getting Started | Reference | Troubleshooting | Deep Dive]
```

### Existing Documentation
```yaml
# Related docs to review for consistency
- file: [path/to/existing/README.md]
  why: [Follow same structure/style]

- file: [path/to/API_docs.md]
  why: [Reference for API documentation format]

- url: [Similar project documentation]
  why: [Good examples of structure/clarity]
```

### Content to Document
```yaml
# What needs to be covered
FEATURES:
  - Feature 1: [Description]
  - Feature 2: [Description]

API_ENDPOINTS (if applicable):
  - GET /endpoint: [Purpose]
  - POST /endpoint: [Purpose]

CONFIGURATION:
  - Environment variables
  - Config files
  - Setup requirements
```

### Known Gaps
```yaml
# What's currently missing or unclear
MISSING:
  - [Installation instructions]
  - [Configuration examples]
  - [Troubleshooting guide]

UNCLEAR:
  - [Authentication flow not explained]
  - [Error messages not documented]
```

## Implementation

### Documentation Structure
```markdown
# [Project/Feature Name]

## Overview
[Brief description - what it is and why it exists]

## Quick Start
[Minimal steps to get started - works in 5 minutes]

## Installation
[Detailed installation instructions]

## Configuration
[All configuration options with examples]

## Usage
[Common use cases with examples]

## API Reference (if applicable)
[Detailed endpoint documentation]

## Examples
[Real-world examples]

## Troubleshooting
[Common issues and solutions]

## Advanced Topics
[Deep dives for power users]

## Contributing (if open source)
[How to contribute]
```

### Task List
```yaml
Task 1: Create documentation outline
ACTION: Set up structure and sections
FILES: [path/to/new/documentation.md]
PATTERN: Follow existing doc structure

Task 2: Write overview and quick start
ACTION: High-level intro and minimal working example
FOCUS: Get users up and running quickly

Task 3: Document installation and setup
ACTION: Step-by-step installation guide
INCLUDE: Prerequisites, dependencies, verification

Task 4: Create configuration guide
ACTION: Document all configuration options
INCLUDE: Environment variables, config files, examples

Task 5: Write usage examples
ACTION: Common use cases with working code
INCLUDE: Simple and advanced examples

Task 6: Add API reference (if applicable)
ACTION: Document all endpoints/functions
INCLUDE: Parameters, returns, errors, examples

Task 7: Create troubleshooting section
ACTION: Common issues and solutions
INCLUDE: Error messages, debugging tips

Task 8: Add diagrams/screenshots (if helpful)
ACTION: Visual aids for complex concepts
TOOLS: Mermaid diagrams, screenshots
```

### Content Guidelines

#### Code Examples
```yaml
# All code examples must be:
COMPLETE: Runnable without modification
TESTED: Verified to work
COMMENTED: Explain non-obvious parts
FORMATTED: Use proper syntax highlighting
```

```python
# Example: API usage
from api_client import Client

# Initialize client with API key
client = Client(api_key="your_key_here")

# Make a request
response = await client.get_user(user_id=123)
print(response)

# Expected output:
# {'id': 123, 'name': 'John Doe', 'email': 'john@example.com'}
```

#### API Documentation Format
```markdown
### GET /api/users/{user_id}

Retrieve a single user by ID.

**Authentication**: Required (API Key)

**Parameters**:
- `user_id` (path, required): The user's unique identifier
  - Type: integer
  - Example: `123`

**Query Parameters**:
- `include_metadata` (optional): Include user metadata in response
  - Type: boolean
  - Default: `false`

**Request Example**:
```bash
curl -X GET https://api.example.com/api/users/123 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

**Response (200 OK)**:
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing API key
- `404 Not Found`: User does not exist
- `429 Too Many Requests`: Rate limit exceeded
```

## Validation

### Level 1: Accuracy Check
```bash
# Verify all code examples work
# Copy each code block and run it

# For Python examples:
python -m pytest docs/examples/test_examples.py

# For shell commands:
bash docs/examples/verify_commands.sh

# Expected: All examples execute successfully
```

### Level 2: Completeness Check
```yaml
# Verify all required sections present
- [ ] Overview/Introduction
- [ ] Quick Start / Getting Started
- [ ] Installation
- [ ] Configuration
- [ ] Usage / Examples
- [ ] API Reference (if applicable)
- [ ] Troubleshooting
- [ ] Link to related documentation
```

### Level 3: Readability Review
```bash
# Check for clarity and grammar
# Tools to use:
- Grammarly or similar for grammar
- Vale linter for technical writing style
- Markdown linter for formatting

# Manual checks:
- [ ] Clear headings and structure
- [ ] Examples are understandable
- [ ] No jargon without explanation
- [ ] Logical flow from simple to complex
```

### Level 4: User Testing
```yaml
# Have someone unfamiliar try to follow the docs
TESTER: [New team member or target audience member]
TASK: Follow documentation to complete a task
OBSERVE:
  - Where do they get stuck?
  - What's confusing?
  - What's missing?
ITERATE: Fix issues and retest
```

## Final Checklist
- [ ] All sections complete
- [ ] All code examples tested and working
- [ ] All links valid and working
- [ ] Screenshots/diagrams included where helpful
- [ ] Appropriate for target audience
- [ ] No typos or grammatical errors
- [ ] Follows existing documentation style
- [ ] Table of contents (if long document)
- [ ] Search-friendly headings
- [ ] Troubleshooting section covers common issues

---

## Anti-Patterns to Avoid
- ❌ Don't assume reader knowledge - explain concepts
- ❌ Don't use untested code examples
- ❌ Don't write "wall of text" - use headings and lists
- ❌ Don't skip the "why" - explain reasoning
- ❌ Don't use jargon without definitions
- ❌ Don't forget error cases and troubleshooting
- ❌ Don't skip examples - show, don't just tell
- ❌ Don't make documentation a "dump" - organize logically

## Documentation Best Practices

### README Structure Template
```markdown
# Project Name

[![Build Status](badge-url)](link)
[![License](badge-url)](link)

One-sentence description of what this project does.

## Features
- Feature 1
- Feature 2
- Feature 3

## Quick Start
```bash
# Three commands to get started
npm install
npm run dev
# Visit http://localhost:3000
```

## Installation
Detailed installation instructions...

## Usage
Common use cases...

## Configuration
Environment variables and config...

## API Reference
Link to full API documentation...

## Contributing
How to contribute...

## License
License information...
```

### API Endpoint Documentation Template
```markdown
## [HTTP Method] /path/to/endpoint

Brief description of what this endpoint does.

**Authentication**: [Required | Optional | None]

**Rate Limiting**: [X requests per minute]

### Request
- **Headers**:
  - `Authorization`: Bearer token (required)
  - `Content-Type`: application/json

- **Parameters**:
  - `param1` (type): Description
  - `param2` (type, optional): Description

- **Body** (for POST/PUT):
  ```json
  {
    "field": "value"
  }
  ```

### Response
**Success (200)**:
```json
{
  "result": "success"
}
```

**Errors**:
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Resource not found
```

### Common Troubleshooting Format
```markdown
## Troubleshooting

### Error: "Connection refused"

**Cause**: Service is not running or wrong port

**Solution**:
1. Check if service is running: `ps aux | grep service-name`
2. Verify port in configuration
3. Start service: `npm start`

### Error: "Authentication failed"

**Cause**: Invalid or expired API key

**Solution**:
1. Verify API key in .env file
2. Check key hasn't expired in dashboard
3. Generate new key if needed
```
