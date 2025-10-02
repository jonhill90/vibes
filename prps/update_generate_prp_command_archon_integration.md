name: "Update generate-prp Command for Archon RAG Integration"
description: |
  Enhance the /generate-prp command to use Archon RAG as the primary research source,
  matching Cole's agent factory pattern where subagents leverage Archon for faster,
  more accurate documentation lookup. Falls back gracefully to web search when unavailable.

---

## Goal

Update the `/generate-prp` command to check Archon availability and use Archon RAG as the PRIMARY research source when available, with graceful fallback to web search when Archon is unavailable.

**End State**: The generate-prp command will automatically leverage Archon's knowledge base for faster, more accurate, and more consistent PRP research, while maintaining full backward compatibility.

## Why

### Business Value
- **Speed**: RAG retrieval (1-2 min) vs web crawling (5+ min) = 3-4x faster PRP generation
- **Quality**: Curated documentation from Archon vs random web results = more accurate context
- **Token Efficiency**: Targeted retrieval vs verbose web content = lower costs, better signal-to-noise
- **Consistency**: Same documentation every time vs varying web results = reproducible PRPs
- **Infrastructure Alignment**: Leverages existing Archon setup properly

### Integration with Existing Features
- **Matches Agent Factory Pattern**: Cole's subagents use Archon RAG first, then web search
- **Enhances PRP Quality**: Better research → better context → better PRPs → better implementations
- **Future-Proofs Workflow**: As Archon knowledge base grows, PRPs automatically improve

### Problems This Solves
- **Slow Research**: Current web-only approach takes 5+ minutes
- **Inconsistent Results**: Web search returns different results each time
- **Token Waste**: Web content is verbose and unfocused
- **Missed Infrastructure**: Archon is available but not being used by generate-prp
- **Pattern Misalignment**: Subagents use Archon, but generate-prp doesn't

## What

### User-Visible Behavior

**Before (Current)**:
```
/generate-prp INITIAL_feature.md
→ Researching codebase...
→ Searching web for patterns... (5+ min)
→ Creating PRP...
```

**After (With Archon Available)**:
```
/generate-prp INITIAL_feature.md
→ Checking knowledge sources...
→ Archon available - using RAG for research
→ Searching knowledge base: "topic" (fast)
→ Searching code examples: "pattern" (fast)
→ Using web search only for gaps
→ Creating PRP... (1-2 min total)
```

**After (Without Archon)**:
```
/generate-prp INITIAL_feature.md
→ Checking knowledge sources...
→ Archon not available - using web search
→ Searching web for patterns...
→ Creating PRP... (works exactly as before)
```

### Technical Requirements

1. **Archon Health Check**: Add step 0 to check `mcp__archon__health_check()`
2. **RAG Integration**: Use `mcp__archon__rag_search_knowledge_base()` for documentation
3. **Code Search**: Use `mcp__archon__rag_search_code_examples()` for implementation patterns
4. **Graceful Fallback**: If Archon unavailable, use web search (current behavior)
5. **Backward Compatibility**: Command works identically when Archon not available
6. **Section Preservation**: ALL other sections of generate-prp.md remain unchanged

### Success Criteria

- ✅ generate-prp.md updated with Archon-first research section
- ✅ Archon health check runs before research begins
- ✅ RAG search used when Archon available (rag_search_knowledge_base, rag_search_code_examples)
- ✅ Graceful fallback to web search when Archon unavailable
- ✅ All existing functionality preserved (no breaking changes)
- ✅ Command tested with Archon available
- ✅ Command tested with Archon unavailable (graceful degradation verified)
- ✅ Documentation clear about benefits and usage
- ✅ Examples of search queries included in updated section

---

## All Needed Context

### Documentation & References

```yaml
# PRIMARY REFERENCES

- url: https://www.youtube.com/watch?v=HJ9VvIG3Rps
  why: Cole demonstrates subagents using Archon RAG for research
  quote: "Archon gives knowledge to these subagents"
  section: Shows Archon-first pattern in action
  critical: This is the pattern we're matching

- file: /Users/jon/source/vibes/.claude/commands/generate-prp.md
  why: Current command file to be updated
  lines: 9-25 (Research Process section to be replaced)
  critical: ONLY modify this section, preserve everything else

- file: /Users/jon/source/vibes/planning/generate-prp-update.md
  why: Contains exact replacement text for Research Process section
  critical: Use this as reference for new section structure
  contains: Complete before/after comparison

- file: /Users/jon/source/vibes/CLAUDE.md
  why: Contains ARCHON-FIRST RULE that this change aligns with
  lines: 204-211 (CRITICAL: ARCHON-FIRST RULE)
  critical: This change implements the global Archon-first principle

- file: /Users/jon/source/vibes/prps/templates/prp_base.md
  why: PRP template structure this implementation will follow
  critical: Understand PRP format standards

- file: /Users/jon/source/vibes/prps/INITIAL_update_generate_prp_command.md
  why: Original feature request with complete requirements
  critical: Contains all success criteria and constraints

# ARCHON MCP TOOLS

- tool: mcp__archon__health_check()
  signature: mcp__archon__health_check() -> status
  purpose: Check if Archon MCP server is available
  usage: First step in research process

- tool: mcp__archon__rag_search_knowledge_base(query)
  signature: mcp__archon__rag_search_knowledge_base(query="<topic>") -> results
  purpose: Search curated documentation in Archon knowledge base
  examples:
    - query: "Pydantic AI agent patterns"
    - query: "FastAPI error handling best practices"
    - query: "async function tools implementation"

- tool: mcp__archon__rag_search_code_examples(query)
  signature: mcp__archon__rag_search_code_examples(query="<pattern>") -> code_snippets
  purpose: Search for code implementation patterns and examples
  examples:
    - query: "RunContext tool implementation"
    - query: "agent.tool decorator usage"
    - query: "pytest fixture setup patterns"
```

### Current Codebase Structure

```
vibes/
├── .claude/
│   └── commands/
│       └── generate-prp.md          # ← FILE TO UPDATE (lines 9-25)
├── planning/
│   └── generate-prp-update.md       # Reference for exact replacement
├── prps/
│   ├── templates/
│   │   └── prp_base.md              # PRP template structure
│   └── INITIAL_update_generate_prp_command.md  # Original requirements
└── CLAUDE.md                         # Global rules (ARCHON-FIRST)
```

### Known Gotchas & Critical Insights

```python
# CRITICAL: This is a markdown file update, not Python code
# File: /Users/jon/source/vibes/.claude/commands/generate-prp.md
# Type: Markdown command definition

# GOTCHA 1: Preserve exact structure
# Only replace lines 9-25 (## Research Process section)
# Do NOT modify:
#   - Lines 1-8 (header and preamble)
#   - Lines 27-69 (PRP Generation, Output, Quality Checklist)

# GOTCHA 2: MCP tool prefix
# Archon tools use mcp__archon__ prefix
# Correct: mcp__archon__health_check()
# Wrong: archon.health_check() or health_check()

# GOTCHA 3: Graceful degradation is REQUIRED
# Command MUST work when Archon is unavailable
# Pattern: IF Archon available THEN use RAG ELSE use web search

# GOTCHA 4: Backward compatibility
# Existing behavior when Archon unavailable must be identical
# Users should see no breaking changes

# GOTCHA 5: Section replacement, not insertion
# REPLACE the entire "## Research Process" section
# Don't append or insert - full replacement

# GOTCHA 6: Example queries matter
# Include concrete examples so AI knows what queries to construct
# Good: "Pydantic AI agent patterns"
# Bad: "<insert topic here>"
```

### Existing Pattern from Planning Document

The `/Users/jon/source/vibes/planning/generate-prp-update.md` file contains the EXACT replacement text structured as:

```markdown
## Research Process

### 0. Check Knowledge Sources (FIRST)
[Archon health check logic]

### 1. Knowledge Research (Archon-First Approach)
**When Archon is Available:**
[RAG search instructions with examples]

**When Archon is Not Available:**
[Web search fallback instructions]

### 2. Codebase Analysis
[Unchanged from current]

### 3. User Clarification (if needed)
[Unchanged from current]
```

---

## Implementation Blueprint

### Task List (Execute in Order)

```yaml
Task 1: Read and Understand Current File
ACTION: Read /Users/jon/source/vibes/.claude/commands/generate-prp.md
PURPOSE: Confirm current structure and identify exact section to replace
VALIDATE: Identify lines 9-25 as "## Research Process" section
OUTPUT: Understanding of current file structure

Task 2: Read Replacement Section
ACTION: Read /Users/jon/source/vibes/planning/generate-prp-update.md
PURPOSE: Get exact replacement text for Research Process section
VALIDATE: Understand new structure with Archon-first approach
OUTPUT: Clear understanding of new section content

Task 3: Replace Research Process Section
ACTION: Use Edit tool to replace lines 9-25 with Archon-first version
FIND: "## Research Process\n\n1. **Codebase Analysis**..."
REPLACE WITH: New section from generate-prp-update.md
CRITICAL:
  - Replace ENTIRE section from "## Research Process" through line 25
  - Preserve all content before and after this section
  - Use exact tool names: mcp__archon__health_check, etc.
  - Include concrete example queries
VALIDATE: Section replaced with Archon-first version

Task 4: Verify File Integrity
ACTION: Read updated generate-prp.md file
PURPOSE: Confirm update applied correctly and other sections preserved
CHECKS:
  - "## Research Process" section now has Archon-first logic
  - "### 0. Check Knowledge Sources" is present
  - Archon MCP tools mentioned: health_check, rag_search_knowledge_base, rag_search_code_examples
  - "## PRP Generation" section unchanged
  - "## Output" section unchanged
  - "## Quality Checklist" section unchanged
VALIDATE: File updated correctly with all sections intact

Task 5: Test Reading Updated Section
ACTION: Read lines around Research Process section
PURPOSE: Verify section formatting is correct
COMMAND: Read file, focus on lines 1-60
VALIDATE: Markdown formatting valid, no syntax errors
```

### Pseudocode for Section Replacement

```python
# Task 3: Replace Research Process Section

# PATTERN: Section replacement in markdown file
# Current section (lines 9-25):
old_section = """
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
"""

# New section (from generate-prp-update.md):
new_section = """
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
"""

# IMPLEMENTATION:
# Use Edit tool to replace old_section with new_section
Edit(
    file_path="/Users/jon/source/vibes/.claude/commands/generate-prp.md",
    old_string=old_section,
    new_string=new_section
)

# CRITICAL CHECKS after edit:
# 1. Section starts with "## Research Process"
# 2. Has subsection "### 0. Check Knowledge Sources (FIRST)"
# 3. Contains mcp__archon__health_check()
# 4. Contains mcp__archon__rag_search_knowledge_base(query="<topic>")
# 5. Contains mcp__archon__rag_search_code_examples(query="<pattern>")
# 6. Has "When Archon is Available:" section
# 7. Has "When Archon is Not Available:" fallback section
# 8. Preserves steps 2 and 3 (Codebase Analysis, User Clarification)
```

### Integration Points

```yaml
FILE_TO_MODIFY:
  path: /Users/jon/source/vibes/.claude/commands/generate-prp.md
  section: Lines 9-25 (## Research Process)
  operation: Replace entire section
  preserve: All other sections (header, PRP Generation, Output, Quality Checklist)

REFERENCES_NEEDED:
  - /Users/jon/source/vibes/planning/generate-prp-update.md (exact replacement text)
  - /Users/jon/source/vibes/CLAUDE.md (ARCHON-FIRST RULE context)

NO_CODE_CHANGES:
  - This is a markdown file update only
  - No Python code to write
  - No tests to create (markdown command definition)
  - No dependencies to install

VALIDATION_METHOD:
  - Read updated file to verify section replaced
  - Check Archon tools mentioned correctly
  - Verify graceful fallback documented
  - Confirm all other sections preserved
```

---

## Validation Loop

### Level 1: File Verification

```bash
# STEP 1: Verify section was replaced correctly
cat /Users/jon/source/vibes/.claude/commands/generate-prp.md | grep -A 50 "Research Process"

# EXPECTED OUTPUT:
# - Should show "### 0. Check Knowledge Sources (FIRST)"
# - Should show "mcp__archon__health_check()"
# - Should show "mcp__archon__rag_search_knowledge_base(query=...)"
# - Should show "mcp__archon__rag_search_code_examples(query=...)"
# - Should show "When Archon is Available:" section
# - Should show "When Archon is Not Available:" fallback section
# - Should show "### 2. Codebase Analysis" (preserved)
# - Should show "### 3. User Clarification" (preserved)

# STEP 2: Verify other sections unchanged
cat /Users/jon/source/vibes/.claude/commands/generate-prp.md | grep -A 5 "PRP Generation"

# EXPECTED OUTPUT:
# Should show unchanged "## PRP Generation" section
# Should show "Using PRPs/templates/prp_base.md as template:"

# STEP 3: Count total lines (should be longer now)
wc -l /Users/jon/source/vibes/.claude/commands/generate-prp.md

# EXPECTED: More than 69 lines (original was 69, new section is longer)
```

### Level 2: Content Validation

```bash
# Verify Archon tools mentioned correctly
grep "mcp__archon__health_check" /Users/jon/source/vibes/.claude/commands/generate-prp.md
grep "mcp__archon__rag_search_knowledge_base" /Users/jon/source/vibes/.claude/commands/generate-prp.md
grep "mcp__archon__rag_search_code_examples" /Users/jon/source/vibes/.claude/commands/generate-prp.md

# EXPECTED: Each grep should return 1+ matches
# If any return 0 matches, the update failed
```

### Level 3: Functional Test (Optional)

```bash
# Test the updated command works (if time permits)
# This would require running the actual command, but since we're in planning mode,
# this is optional validation for later

# Example test:
# /generate-prp prps/INITIAL_simple_test.md

# Expected behavior:
# 1. Command should check Archon availability
# 2. If Archon available, should use RAG for research
# 3. If Archon unavailable, should fall back to web search gracefully
# 4. Should still generate valid PRP in either case
```

### Validation Checklist

```yaml
Before Marking Complete:
  - ✅ Read updated generate-prp.md file
  - ✅ Verify "### 0. Check Knowledge Sources" section exists
  - ✅ Confirm mcp__archon__health_check() mentioned
  - ✅ Confirm mcp__archon__rag_search_knowledge_base() mentioned
  - ✅ Confirm mcp__archon__rag_search_code_examples() mentioned
  - ✅ Verify "When Archon is Available:" section exists
  - ✅ Verify "When Archon is Not Available:" fallback exists
  - ✅ Verify "### 2. Codebase Analysis" section preserved
  - ✅ Verify "### 3. User Clarification" section preserved
  - ✅ Verify "## PRP Generation" section unchanged
  - ✅ Verify "## Output" section unchanged
  - ✅ Verify "## Quality Checklist" section unchanged
  - ✅ Verify example queries included (e.g., "Pydantic AI agent patterns")
  - ✅ Verify graceful degradation clearly documented
  - ✅ No syntax errors in markdown
```

---

## Final Validation Checklist

- ✅ All tests pass: N/A (markdown file, no executable tests)
- ✅ No linting errors: N/A (markdown file)
- ✅ No type errors: N/A (markdown file)
- ✅ Manual verification successful: Read file, verify section replaced
- ✅ Error cases handled gracefully: Archon unavailable fallback documented
- ✅ Documentation updated: The command itself IS the documentation
- ✅ Backward compatibility maintained: Works with or without Archon

---

## Anti-Patterns to Avoid

- ❌ **Don't modify other sections** - Only replace Research Process (lines 9-25)
- ❌ **Don't create new files** - This is a single file edit
- ❌ **Don't use wrong tool names** - Must use mcp__archon__ prefix
- ❌ **Don't skip graceful fallback** - MUST work without Archon
- ❌ **Don't remove existing functionality** - Web search must remain as fallback
- ❌ **Don't add Python code** - This is a markdown command file
- ❌ **Don't change file structure** - Replace section only, preserve everything else
- ❌ **Don't skip validation** - Must verify update applied correctly

---

## Expected Behavior After Implementation

### Scenario 1: Archon Available
```
User runs: /generate-prp INITIAL_feature.md

Claude's Process:
1. Reads INITIAL_feature.md to understand feature
2. Runs: mcp__archon__health_check()
   → Result: Archon available ✓
3. Runs: mcp__archon__rag_search_knowledge_base(query="relevant topic")
   → Gets curated documentation (fast, accurate)
4. Runs: mcp__archon__rag_search_code_examples(query="implementation pattern")
   → Gets code examples (fast, targeted)
5. Uses web_search only for gaps not in Archon
6. Creates comprehensive PRP with high-quality context
7. Saves to: prps/feature_name.md

Time: 1-2 minutes (vs 5+ minutes with web-only)
Quality: Higher (curated docs vs random web)
```

### Scenario 2: Archon Unavailable
```
User runs: /generate-prp INITIAL_feature.md

Claude's Process:
1. Reads INITIAL_feature.md to understand feature
2. Runs: mcp__archon__health_check()
   → Result: Archon not available ✗
3. Falls back to web_search (current behavior)
   → Searches web for patterns, documentation
4. Creates comprehensive PRP using web research
5. Saves to: prps/feature_name.md

Time: 5+ minutes (same as current)
Quality: Good (same as current web-only approach)
Result: Works exactly as it does now - NO BREAKING CHANGES
```

### Key Benefits Achieved

1. **Speed**: 3-4x faster when Archon available
2. **Quality**: Better context from curated documentation
3. **Consistency**: Reproducible results every time
4. **Alignment**: Matches agent factory Archon-first pattern
5. **Compatibility**: Zero breaking changes, graceful degradation
6. **Infrastructure**: Properly leverages existing Archon setup

---

## Risk Assessment

### Low Risk Change
- ✅ Single file edit (generate-prp.md)
- ✅ Single section replacement (lines 9-25)
- ✅ Markdown file (not executable code)
- ✅ Graceful degradation (fallback to web search)
- ✅ No dependencies added
- ✅ No API changes
- ✅ Backward compatible

### Failure Modes & Mitigations

| Failure Mode | Likelihood | Impact | Mitigation |
|--------------|------------|--------|------------|
| Edit tool fails | Low | Medium | Read file first, verify structure |
| Section boundaries wrong | Low | Medium | Use exact text matching from planning doc |
| Archon tools named incorrectly | Low | Medium | Reference INITIAL file for exact names |
| Other sections modified | Low | High | Use precise old_string matching |
| Markdown syntax broken | Low | Medium | Verify with grep after edit |

---

## Confidence Score: 9/10

### Why High Confidence?

1. **Focused Scope**: Single file, single section replacement
2. **Exact Reference**: Planning doc has exact replacement text
3. **Low Complexity**: Markdown edit, not code changes
4. **Clear Validation**: Easy to verify with cat/grep
5. **Graceful Degradation**: Fallback ensures no breaking changes
6. **No Dependencies**: No new tools or libraries needed
7. **Well-Documented**: Clear before/after in planning doc

### Why Not 10/10?

- Minor risk: Edit tool could misalign section boundaries if old_string not exact match
- Mitigation: Use precise text from current file for old_string

### One-Pass Success Likelihood

**95%** - Very high confidence this can be implemented correctly in a single pass by following the task list in order and verifying each step.

---

## Summary

This PRP provides comprehensive context for a focused, low-risk enhancement to the generate-prp command. By adding Archon RAG as the primary research source with graceful web search fallback, we align with the agent factory pattern, improve PRP generation speed by 3-4x, and enhance research quality—all while maintaining full backward compatibility.

The implementation is straightforward: replace one section in one markdown file with content that's already defined in the planning document. Validation is simple: read the file and verify the new section is present and other sections are preserved.

**Expected outcome**: Every future PRP generation will automatically benefit from faster, more accurate research when Archon is available, with zero disruption when it's not.
