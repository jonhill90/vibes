# Create PRP

## Feature file: $ARGUMENTS

Generate a complete PRP for general feature implementation with thorough research. Ensure context is passed to the AI agent to enable self-validation and iterative refinement. Read the feature file first to understand what needs to be created, how the examples provided help, and any other considerations.

The AI agent only gets the context you are appending to the PRP and training data. Assuma the AI agent has access to the codebase and the same knowledge cutoff as you, so its important that your research findings are included or referenced in the PRP. The Agent has Websearch capabilities, so pass urls to documentation and examples.

## Research Process

### 0. Check Knowledge Sources (FIRST)
```bash
# CRITICAL: Check if Archon MCP is available
mcp__archon__health_check()
```

**If Archon Available:**
- Use Archon RAG as PRIMARY research source
- Benefits: Faster, more accurate, curated documentation
- Web search only for gaps in Archon knowledge

**If Archon Not Available:**
- Use web_search as primary source
- Document URLs for future Archon ingestion

### 1. Knowledge Research (Archon-First Approach)

**When Archon is Available:**
1. Search knowledge base for relevant documentation:
   ```
   mcp__archon__rag_search_knowledge_base(query="<topic>")
   ```
   Examples:
   - "Pydantic AI agent patterns"
   - "FastAPI best practices"
   - "React component architecture"

2. Search for code examples and implementations:
   ```
   mcp__archon__rag_search_code_examples(query="<pattern>")
   ```
   Examples:
   - "async tool implementation"
   - "API integration pattern"
   - "test fixture setup"

3. Use web_search ONLY for:
   - Topics not in Archon knowledge base
   - Very recent changes/updates
   - Specific version documentation

**When Archon is Not Available:**
- Use web_search extensively
- Search for library documentation (include specific URLs)
- Implementation examples (GitHub/StackOverflow/blogs)
- Best practices and common pitfalls

### 2. Codebase Analysis
- Search for similar features/patterns in the codebase
- Identify files to reference in PRP
- Note existing conventions to follow
- Check test patterns for validation approach

### 3. User Clarification (if needed)
- Specific patterns to mirror and where to find them?
- Integration requirements and where to find them?

## PRP Generation

Using PRPs/templates/prp_base.md as template:

### Critical Context to Include and pass to the AI agent as part of the PRP
- **Documentation**: URLs with specific sections
- **Code Examples**: Real snippets from codebase
- **Gotchas**: Library quirks, version issues
- **Patterns**: Existing approaches to follow

### Implementation Blueprint
- Start with pseudocode showing approach
- Reference real files for patterns
- Include error handling strategy
- list tasks to be completed to fullfill the PRP in the order they should be completed

### Validation Gates (Must be Executable) eg for python
```bash
# Syntax/Style
ruff check --fix && mypy .

# Unit Tests
uv run pytest tests/ -v

```

*** CRITICAL AFTER YOU ARE DONE RESEARCHING AND EXPLORING THE CODEBASE BEFORE YOU START WRITING THE PRP ***

*** ULTRATHINK ABOUT THE PRP AND PLAN YOUR APPROACH THEN START WRITING THE PRP ***

## Output
Save as: `PRPs/{feature-name}.md`

## Quality Checklist
- [ ] All necessary context included
- [ ] Validation gates are executable by AI
- [ ] References existing patterns
- [ ] Clear implementation path
- [ ] Error handling documented

Score the PRP on a scale of 1-10 (confidence level to succeed in one-pass implementation using claude codes)

Remember: The goal is one-pass implementation success through comprehensive context.