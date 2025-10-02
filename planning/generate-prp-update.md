# Update generate-prp.md for Archon RAG Integration

## File to Modify:
`/workspace/vibes/.claude/commands/generate-prp.md`

## Current Research Section:
```markdown
## Research Process

1. **Codebase Analysis**
   - Search for similar features/patterns in the codebase
   - Identify files to reference in PRP
   - Note existing conventions to follow
   - Check test patterns for validation approach

2. **External Research**
   - Search for similar features/patterns online
   - Library documentation (include specific URLs)
   - Implementation examples (GitHub/StackOverflow/blogs)
   - Best practices and common pitfalls

3. **User Clarification** (if needed)
   - Specific patterns to mirror and where to find them?
   - Integration requirements and where to find them?
```

## Updated Research Section:
```markdown
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
```

## Why This Change:

### Matches Cole's Agent Factory Pattern:
```yaml
# From pydantic-ai-planner.md
tools: ["web_search", "archon:rag_search_knowledge_base"]

# Planner uses Archon FIRST, web as backup
```

### Benefits:
1. **Faster Research** - RAG retrieval vs web crawling
2. **Better Quality** - Curated documentation vs random results
3. **Token Efficiency** - Targeted retrieval vs verbose web results
4. **Consistency** - Same docs every time
5. **Uses Available Infrastructure** - Why have Archon if not using it?

### Graceful Degradation:
- Still works perfectly without Archon
- Web search as reliable fallback
- No breaking changes

## After Update:

### Test the Change:
```bash
# Read updated command
cat /workspace/vibes/.claude/commands/generate-prp.md

# Regenerate foundation PRP
/generate-prp INITIAL_context_engineering_foundation.md

# Regenerate agent factory PRP  
/generate-prp INITIAL_context_engineering_agent_factory.md
```

### Expected Behavior:
- Claude checks Archon first
- Uses rag_search_knowledge_base for docs
- Uses rag_search_code_examples for patterns
- Falls back to web_search only when needed
- Much faster, more accurate research

## Result:
New PRPs will be generated with:
- Better research quality
- Faster generation time
- More accurate context
- Leveraging your Archon setup properly
