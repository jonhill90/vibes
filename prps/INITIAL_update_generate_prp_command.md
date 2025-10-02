## FEATURE:
Update the generate-prp command to use Archon RAG as the primary research source (with graceful fallback to web search), matching the pattern used in Cole's agent factory where subagents leverage Archon for faster, more accurate documentation lookup.

## GOAL:
Enhance the PRP generation process to:
1. Check Archon availability before starting research
2. Use Archon RAG as PRIMARY research source when available
3. Fall back to web search gracefully when Archon unavailable
4. Match Cole's agent factory pattern (subagents use Archon first)
5. Improve speed, accuracy, and token efficiency of PRP generation

## EXAMPLES:

**From Cole's Agent Factory Pattern:**
```yaml
# From pydantic-ai-planner.md subagent
name: "Requirements Planner"
tools: ["web_search", "archon:rag_search_knowledge_base"]

# The planner subagent:
1. Uses Archon RAG to research Pydantic AI patterns
2. Searches code examples through Archon
3. Falls back to web search only for gaps
4. Creates better INITIAL.md as a result
```

**Current generate-prp Behavior:**
```markdown
## Research Process

1. **Codebase Analysis**
   - Search for patterns in codebase
   
2. **External Research**
   - Search online for patterns        # ❌ Just web search
   - Library documentation
   
3. **User Clarification**
   - Ask questions if needed
```

**Desired generate-prp Behavior:**
```markdown
## Research Process

0. **Check Knowledge Sources**
   - Run: archon:health_check()      # ✅ Check Archon first
   - If available: Archon-first approach
   - If not: web search fallback

1. **Knowledge Research (Archon-First)**
   - PRIMARY: archon:rag_search_knowledge_base()  # ✅ Use Archon
   - PRIMARY: archon:rag_search_code_examples()   # ✅ Use Archon
   - FALLBACK: web_search (only for gaps)

2. **Codebase Analysis**
   [unchanged]
```

## DOCUMENTATION:

**Primary References:**
- Video: https://www.youtube.com/watch?v=HJ9VvIG3Rps
  - Cole demonstrates subagents using Archon RAG
  - Quote: "Archon gives knowledge to these subagents"
  - Shows faster, more accurate research

- File: /workspace/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-planner.md
  - Example subagent with Archon tools
  - Shows Archon-first research pattern

- File: /workspace/vibes/.claude/commands/generate-prp.md
  - Current command to be updated
  - Has research section needing enhancement

- File: /workspace/vibes/CLAUDE.md
  - Global rules - includes ARCHON-FIRST RULE
  - Must follow existing patterns

- Doc: /workspace/vibes/planning/generate-prp-update.md
  - Complete update guide created during planning
  - Has exact replacement text

**Archon MCP Tools:**
- `mcp__archon__health_check()` - Check if Archon available
- `mcp__archon__rag_search_knowledge_base(query)` - Search documentation
- `mcp__archon__rag_search_code_examples(query)` - Search code patterns

## KEY REQUIREMENTS:

### 1. Update Research Process Section

**File to Modify:**
```
/workspace/vibes/.claude/commands/generate-prp.md
```

**Section to Replace:**
The entire "## Research Process" section needs enhancement.

**New Structure:**
```markdown
## Research Process

### 0. Check Knowledge Sources (FIRST)

**CRITICAL: Always check Archon availability before researching**

```bash
# Check if Archon MCP is available
mcp__archon__health_check()
```

**Evaluation:**
- If Archon available: Use Archon-first approach (faster, more accurate)
- If Archon unavailable: Use web search approach (standard fallback)

**Benefits of Archon-First:**
- Faster research (RAG retrieval vs web crawling)
- Better quality (curated documentation vs random web results)
- Token efficiency (targeted retrieval vs verbose web results)
- Consistency (same documentation every time)
- Leverages available infrastructure

### 1. Knowledge Research (Archon-First Approach)

**When Archon is Available:**

1. **Search Knowledge Base for Documentation:**
   ```bash
   mcp__archon__rag_search_knowledge_base(query="<topic>")
   ```
   
   Search for:
   - Framework documentation (e.g., "Pydantic AI agent patterns")
   - Best practices (e.g., "FastAPI error handling")
   - Architecture patterns (e.g., "React component structure")
   - API documentation (e.g., "Anthropic API parameters")
   
   Examples:
   - Query: "async function tools Pydantic AI"
   - Query: "system prompt design patterns"
   - Query: "dependency injection patterns"

2. **Search Code Examples and Implementations:**
   ```bash
   mcp__archon__rag_search_code_examples(query="<pattern>")
   ```
   
   Search for:
   - Implementation patterns (e.g., "async tool implementation")
   - API integration examples (e.g., "API client pattern")
   - Test patterns (e.g., "pytest fixture setup")
   - Configuration examples (e.g., "environment variable loading")
   
   Examples:
   - Query: "RunContext tool implementation"
   - Query: "agent.tool decorator usage"
   - Query: "validation test examples"

3. **Use web_search ONLY for:**
   - Topics not found in Archon knowledge base
   - Very recent changes/updates not yet in Archon
   - Specific version documentation if Archon doesn't have it
   - External services not documented in Archon

**When Archon is Not Available:**

Use web_search as primary research method:
- Search for similar features/patterns online
- Library documentation (include specific URLs)
- Implementation examples (GitHub/StackOverflow/blogs)
- Best practices and common pitfalls
- Document URLs for potential future Archon ingestion

### 2. Codebase Analysis

- Search for similar features/patterns in the codebase
- Identify files to reference in PRP
- Note existing conventions to follow
- Check test patterns for validation approach

### 3. User Clarification (if needed)

- Specific patterns to mirror and where to find them?
- Integration requirements and where to find them?
```

### 2. Preserve Existing Content

**CRITICAL: Do NOT modify:**
- The command structure (## Feature file: $ARGUMENTS)
- The PRP generation section
- The output format
- The quality checklist
- Any other sections

**ONLY update:**
- The "## Research Process" section
- Add Archon-first logic
- Keep all existing steps (Codebase Analysis, User Clarification)

### 3. Graceful Degradation

**The updated command MUST:**
- Work perfectly when Archon is available
- Work perfectly when Archon is NOT available
- Not break existing functionality
- Not require Archon to function

**Pattern:**
```
IF Archon available:
  Use Archon RAG (better, faster)
ELSE:
  Use web search (standard approach)
```

## SUCCESS CRITERIA:

- [ ] generate-prp.md updated with Archon-first research section
- [ ] Archon health check added at start of research process
- [ ] rag_search_knowledge_base integration documented
- [ ] rag_search_code_examples integration documented
- [ ] Graceful fallback to web search when Archon unavailable
- [ ] Examples of search queries included
- [ ] All existing functionality preserved
- [ ] Command tested with Archon available
- [ ] Command tested with Archon unavailable (graceful degradation)
- [ ] Documentation clear about benefits and usage

## CONSTRAINTS:

**Must Follow:**
- ARCHON-FIRST RULE from CLAUDE.md
- Use mcp__archon__ prefix for Archon tools
- Preserve all existing command structure
- Maintain backward compatibility

**Must NOT:**
- Break existing generate-prp functionality
- Make Archon required (optional with fallback)
- Remove web_search capability
- Modify other command sections
- Change output format or PRP structure

**Use:**
- vibes:run_command for file operations
- Existing command patterns
- Clear, actionable documentation

## VALIDATION:

```bash
# 1. Verify update applied
cat /workspace/vibes/.claude/commands/generate-prp.md | grep -A 20 "Research Process"
# Should show: Archon health check, rag_search calls, graceful fallback

# 2. Test with current INITIAL files
# Archon should be used if available
/generate-prp INITIAL_context_engineering_foundation.md

# 3. Check that Archon was used
# Look for rag_search_knowledge_base calls in output
# Research should be faster and more targeted

# 4. Verify graceful degradation
# If Archon unavailable, should fall back to web search
# Command should still work perfectly
```

## IMPLEMENTATION NOTES:

### Single File Change
This is a focused, surgical update:
- ONE file: generate-prp.md
- ONE section: Research Process
- Clear before/after
- Low risk

### Expected Behavior After Update

**When running: /generate-prp INITIAL_file.md**

With Archon:
```
✓ Checking Archon availability...
✓ Archon available - using RAG for research
✓ Searching knowledge base: "topic"
✓ Searching code examples: "pattern"
✓ Found 10 relevant documents
✓ Found 5 code examples
✓ Using web search for gaps only
✓ Research complete (faster, more accurate)
```

Without Archon:
```
✓ Checking Archon availability...
✓ Archon not available - using web search
✓ Searching online for patterns...
✓ Research complete (standard approach)
```

### Why This Matters

**For Context Engineering PRPs:**
- Both foundation and agent factory PRPs need good research
- Archon has Pydantic AI docs, patterns, examples
- Better research = better PRPs = better implementations

**For All Future PRPs:**
- Every PRP generation benefits from this enhancement
- Faster, more accurate, more consistent
- Leverages infrastructure properly

**Matches Cole's Architecture:**
- His subagents use Archon first
- Falls back to web search gracefully
- We should do the same for PRP generation

## OTHER CONSIDERATIONS:

### Timing
- This should be done BEFORE regenerating the Context Engineering PRPs
- Once updated, all future PRPs benefit automatically
- Quick task: ~15-30 minutes

### Testing Strategy
1. Update the command
2. Test with a simple INITIAL file
3. Verify Archon is being used
4. Verify fallback works
5. Then regenerate the big PRPs

### Future Enhancements
After this works:
- Could add more specific Archon queries
- Could cache common searches
- Could add quality scoring
- But start simple - just add Archon-first

## WHY THIS FEATURE:

**Problem:**
- Current generate-prp uses web search only
- Web crawling is slow (5+ minutes)
- Results are noisy and inconsistent
- Not leveraging available Archon infrastructure

**Solution:**
- Check Archon first
- Use RAG for fast, accurate retrieval
- Fall back to web search gracefully
- Match Cole's proven pattern

**Impact:**
- Faster PRP generation (1-2 min vs 5+ min)
- Better research quality (curated docs)
- More token efficient
- Every future PRP benefits
- Uses infrastructure properly

**Alignment:**
- Follows ARCHON-FIRST RULE
- Matches agent factory pattern
- Graceful degradation built-in
- Low risk, high value
