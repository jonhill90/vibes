# Vibes Examples

This directory contains reference patterns and examples for common development tasks in Vibes. These examples demonstrate best practices, coding patterns, and approaches that work well within the Vibes ecosystem.

## Purpose

**Examples are NOT meant to be copied directly.** They are reference patterns showing best practices and approaches that you should adapt to your specific needs. Think of them as templates or inspiration, not boilerplate code.

## Directory Structure

```
examples/
├── README.md                 # This file
├── prp-workflow/            # PRP (Product Requirements Prompt) examples
│   ├── simple-feature.md    # Basic feature PRP
│   └── complex-feature.md   # Multi-component feature PRP
├── tools/                   # Tool integration patterns
│   ├── api_integration.py   # External API integration
│   └── file_operations.py   # Safe file operations
└── documentation/           # Documentation templates
    ├── README_template.md   # Project README structure
    └── API_doc_template.md  # API documentation format
```

## How to Use Examples

### 1. Browse and Understand
- Read through examples relevant to your task
- Understand the patterns and principles demonstrated
- Note the comments explaining "why" not just "what"

### 2. Adapt, Don't Copy
- Adapt the patterns to your specific use case
- Change variable names, structure, and logic as needed
- Keep the core principles but make it yours

### 3. Follow the Patterns
- Error handling approaches
- Configuration management
- Testing strategies
- Code organization

## Example Categories

### PRP Workflow Examples
Located in `prp-workflow/`, these show how to structure PRPs (Product Requirements Prompts) for different complexity levels:

- **simple-feature.md**: Straightforward single-component features
- **complex-feature.md**: Multi-component systems with multiple integration points

**When to use**: Creating new PRPs for feature implementation

### Tool Integration Examples
Located in `tools/`, these demonstrate how to integrate external tools and APIs:

- **api_integration.py**: Async HTTP client with error handling, rate limiting, retries
- **file_operations.py**: Safe file I/O with validation, atomic operations, backups

**When to use**: Adding new integrations, building tools, working with external systems

### Documentation Examples
Located in `documentation/`, these provide templates for project documentation:

- **README_template.md**: Standard README structure with all essential sections
- **API_doc_template.md**: API endpoint documentation format

**When to use**: Creating or updating project documentation

## Key Principles Demonstrated

All examples follow these core principles:

### 1. **Error Handling**
- Graceful degradation
- Specific exception catching
- Informative error messages
- Retry logic for transient failures

### 2. **Configuration**
- Environment variables for sensitive data
- Sane defaults
- Type validation
- Clear documentation

### 3. **Async Patterns**
- Proper async/await usage
- Context managers for resources
- Concurrent operations where appropriate

### 4. **Type Safety**
- Type hints throughout
- Pydantic models for validation
- Clear interfaces

### 5. **Testing**
- Unit tests with mocked dependencies
- Integration tests where appropriate
- Edge case coverage

## Using Examples with PRPs

Examples work hand-in-hand with PRPs (Product Requirements Prompts):

1. **Start with a PRP template** (`prps/templates/`)
2. **Reference relevant examples** from this directory
3. **Include example references in your PRP** to guide implementation
4. **Adapt patterns** to your specific feature

Example PRP reference:
```yaml
- file: examples/tools/api_integration.py
  why: Follow async HTTP client pattern for Brave Search API
```

## Contributing Examples

When adding new examples:

1. **Focus on patterns**, not specific implementations
2. **Include comprehensive comments** explaining the "why"
3. **Demonstrate best practices** from the Vibes codebase
4. **Keep examples self-contained** but realistic
5. **Test your examples** - they should actually work

## Related Documentation

- [PRP Templates](../prps/templates/) - Templates for creating PRPs
- [PRP Base Template](../prps/templates/prp_base.md) - Comprehensive PRP structure
- [CLAUDE.md](../CLAUDE.md) - Global rules and conventions
- [Context Engineering Intro](https://github.com/coleam00/context-engineering-intro) - Context engineering philosophy

## Questions?

If you're unsure which example to reference or how to adapt a pattern:
1. Review the example's comments
2. Check similar features in the codebase
3. Reference the PRP that created the example
4. Ask in the project discussions

---

**Remember**: Examples are starting points, not endpoints. Understand the pattern, adapt it to your needs, and make it better!
