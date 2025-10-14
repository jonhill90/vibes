# PRP System Patterns - Index

This directory contains reusable implementation patterns extracted from the PRP generation and execution system. Each pattern is self-contained with code examples, gotchas, and usage guidance.

## Quick Reference

**Need to...** | **See Pattern** | **Used By**
---|---|---
Extract secure feature names | [security-validation.md](security-validation.md) | All commands
Integrate with Archon MCP | [archon-workflow.md](archon-workflow.md) | generate-prp, execute-prp
Execute subagents in parallel | [parallel-subagents.md](parallel-subagents.md) | generate-prp Phase 2, execute-prp Phase 2
Validate PRP/execution quality | [quality-gates.md](quality-gates.md) | generate-prp Phase 5, execute-prp Phase 4
Validate frontend UIs via browser | [browser-validation.md](browser-validation.md) | validation-gates, prp-exec-validator

## Pattern Categories

### Security Patterns
- **[security-validation.md](security-validation.md)**: Feature name extraction with 5-level security validation
  - Use when: Accepting user input for file paths or feature names
  - Key benefit: Prevents path traversal, command injection, and directory traversal

### Integration Patterns
- **[archon-workflow.md](archon-workflow.md)**: Health check, project/task management, graceful degradation
  - Use when: Any command needing Archon tracking
  - Key benefit: Works with or without Archon (graceful fallback)

### Performance Patterns
- **[parallel-subagents.md](parallel-subagents.md)**: Multi-task invocation in single response
  - Use when: 3+ independent tasks can run simultaneously
  - Key benefit: 3x speedup for research, 30-50% for implementation

### Quality Patterns
- **[quality-gates.md](quality-gates.md)**: Scoring criteria, validation loops
  - Use when: Output must meet quality thresholds before delivery
  - Key benefit: Prevents low-quality deliverables (8+/10 PRP score)

### Testing Patterns
- **[browser-validation.md](browser-validation.md)**: Browser automation patterns for frontend UI validation
  - Use when: Testing React frontends, validating user-facing features
  - Key benefit: End-to-end validation with accessibility-first approach (not screenshot-based)

### Reliability Patterns
- Coming soon: error-handling.md (retry logic, graceful degradation, error recovery)

### Organization Patterns
- Coming soon: file-organization.md (per-feature scoped directories)

## Usage Guidelines

1. **Read the index first**: Find the right pattern before diving in
2. **Copy-paste examples**: Patterns include ready-to-use code
3. **Don't modify patterns**: If you need variations, create a new pattern
4. **Update index when adding**: Keep this README synchronized

## Anti-Patterns (What NOT to do)

❌ Don't create sub-patterns (violates two-level disclosure rule)
❌ Don't cross-reference patterns (causes circular dependencies)
❌ Don't duplicate pattern code in commands (defeats DRY purpose)
❌ Don't abstract after <3 occurrences (premature abstraction)

## Contribution Guidelines

When adding a new pattern:
1. Verify it appears in 3+ locations (Rule of Three)
2. Include complete code examples (copy-paste ready)
3. Document gotchas and edge cases
4. Update this index with quick reference entry
5. Test pattern with actual command execution
