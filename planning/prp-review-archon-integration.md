# PRP Review: Archon Integration Analysis

## Files Reviewed:
- `/workspace/vibes/prps/context_engineering_foundation.md` (456 lines)
- `/workspace/vibes/prps/context_engineering_agent_factory.md` (1061 lines)

---

## ✅ GOOD NEWS: Archon IS Mentioned

Both PRPs include:
- **ARCHON-FIRST RULE** in critical gotchas
- References to using Archon MCP for task management
- Optional Archon integration for agent factory

### Foundation PRP:
```yaml
# Found in "Known Gotchas":
- CRITICAL: Follow ARCHON-FIRST RULE - Use Archon MCP for task management, NOT TodoWrite
```

### Agent Factory PRP:
```yaml
# Found in "Known Gotchas":
- CRITICAL: Archon integration is OPTIONAL - must work without it
  Check Archon availability first with mcp__archon__health_check
  If available: create project, tasks, use RAG
  If not: proceed with local tracking, web search only
```

---

## ❌ MISSING: Archon RAG for Research During PRP Generation

### The Gap:

Neither PRP explicitly tells the **generate-prp command itself** to use Archon RAG for research.

**Current State:**
- PRPs mention using Archon in the **implemented features** (agent factory uses it)
- PRPs don't mention using Archon in the **PRP generation process** itself

**What Cole's Agent Factory Does:**
```yaml
# From pydantic-ai-planner.md subagent
tools: ["web_search", "archon:rag_search_knowledge_base"]

# Planner uses Archon RAG to research Pydantic AI patterns
# Then creates INITIAL.md with that knowledge
```

**What generate-prp Currently Does:**
```markdown
## Research Process

1. **Codebase Analysis** - Search for patterns
2. **External Research** - Search online (web_search only)
3. **User Clarification** - Ask questions
```

**What generate-prp SHOULD Do:**
```markdown
## Research Process

1. **Check Archon Availability**
   - Run archon:health_check
   - If available: Proceed with Archon-first approach
   - If not: Fall back to web search

2. **Knowledge Research (Archon-First)**
   - If Archon available:
     * archon:rag_search_knowledge_base("relevant topic")
     * archon:rag_search_code_examples("implementation patterns")
   - If not available:
     * web_search for documentation
     * Library docs with URLs

3. **Codebase Analysis** [...]
```

---

## 🎯 The Core Issue:

Your observation is **100% correct**. The generate-prp command should:

1. **Check if Archon is available**
2. **Use Archon RAG FIRST** for research (faster, better)
3. **Fall back to web search** only if Archon unavailable

This matches Cole's pattern where subagents have:
- `tools: ["web_search", "archon:rag_search_knowledge_base"]`
- Use Archon first, web as backup

---

## 📋 What Needs to Change:

### Option A: Update generate-prp.md (Best)

Add to `/workspace/vibes/.claude/commands/generate-prp.md`:

```markdown
## Research Process

### 1. Check Knowledge Sources
```bash
# CRITICAL: Check if Archon MCP is available
archon:health_check()
```

If Archon available:
- Primary: Archon knowledge base and code examples
- Secondary: Web search for gaps
- Benefit: Faster, more accurate, consistent results

If Archon unavailable:
- Primary: Web search
- Note: Document sources for future Archon ingestion

### 2. Knowledge Research (Archon-First Approach)

**When Archon Available:**
1. Search knowledge base: `archon:rag_search_knowledge_base(query="topic")`
2. Search code examples: `archon:rag_search_code_examples(query="pattern")`
3. Use web_search only to fill gaps

**When Archon Unavailable:**
1. Use web_search extensively
2. Include specific documentation URLs in PRP
3. Note: These URLs can be added to Archon later

### 3. Codebase Analysis
[rest of process...]
```

### Option B: Create New PRP (Alternative)

Create: `INITIAL_enhance_generate_prp_command.md`
- Updates generate-prp.md to use Archon RAG
- Adds research prioritization logic
- Documents Archon-first pattern

### Option C: Add to Existing PRPs (Quick Fix)

Add a task to both PRPs:
```yaml
Task X.X: Update generate-prp Command for Archon RAG
MODIFY /workspace/vibes/.claude/commands/generate-prp.md:
  - ADD Archon availability check
  - ADD Archon RAG research section
  - UPDATE research process to be Archon-first
  - KEEP web search as fallback
```

---

## 🚀 Recommendation:

### **Option A: Update generate-prp.md Directly**

**Why:**
1. **Immediate improvement** - Every PRP generation benefits
2. **Matches Cole's pattern** - Subagents use Archon first
3. **Better results** - Faster research, more accurate
4. **Graceful degradation** - Works without Archon

**How:**
Add a new task to the **Agent Factory PRP** (since it already deals with Archon):

```yaml
Task 0.1: Enhance generate-prp Command (Prerequisites)
BEFORE starting main implementation, update generate-prp:

MODIFY /workspace/vibes/.claude/commands/generate-prp.md:
  - FIND "## Research Process" section
  - INJECT Archon availability check at the start
  - UPDATE research priority: Archon first, web fallback
  - PRESERVE existing research steps
  - ADD documentation about Archon benefits

RATIONALE:
- This PRP will need good research capabilities
- Archon RAG provides better, faster results
- Matches agent factory pattern where subagents use Archon
- Future PRPs will benefit from enhanced research
```

---

## 📊 Impact Analysis:

### If We DON'T Update generate-prp:

**Downsides:**
- ❌ PRP generation slower (web crawling vs Archon RAG)
- ❌ Less accurate research (web results vs curated knowledge)
- ❌ More tokens consumed (web search verbose)
- ❌ Inconsistent with Cole's pattern
- ❌ Not using available infrastructure

**Current State:**
- ✅ Both PRPs know about ARCHON-FIRST RULE
- ✅ Agent factory will use Archon properly
- ⚠️ But PRP generation itself doesn't leverage it

### If We DO Update generate-prp:

**Upsides:**
- ✅ Faster PRP generation (RAG retrieval vs web)
- ✅ Better research quality (curated docs)
- ✅ Fewer tokens (targeted retrieval)
- ✅ Consistent with Cole's pattern
- ✅ Leverages existing infrastructure
- ✅ Every future PRP benefits

**Implementation:**
- Small change to generate-prp.md
- Graceful degradation (works without Archon)
- Can be done as first task in agent factory PRP

---

## 🎯 Specific Changes Needed:

### File: `/workspace/vibes/.claude/commands/generate-prp.md`

**Current Section:**
```markdown
## Research Process

1. **Codebase Analysis**
   - Search for similar features/patterns in the codebase
   
2. **External Research**
   - Search for similar features/patterns online
   - Library documentation (include specific URLs)
   ...
```

**Enhanced Section:**
```markdown
## Research Process

0. **Check Knowledge Sources**
   ```bash
   # Check if Archon MCP is available for enhanced research
   mcp__archon__health_check()
   ```
   - If available: Use Archon-first approach (faster, better)
   - If not: Use web search (standard approach)

1. **Knowledge Research** (Priority: Archon > Web)
   
   **If Archon Available:**
   - Primary: `mcp__archon__rag_search_knowledge_base(query="<topic>")`
   - Search code examples: `mcp__archon__rag_search_code_examples(query="<pattern>")`
   - Benefits: Faster retrieval, curated docs, consistent results
   - Fallback: Use web_search only for gaps in Archon knowledge
   
   **If Archon Not Available:**
   - Primary: web_search for documentation
   - Include specific URLs in PRP
   - Note: These can be ingested into Archon later

2. **Codebase Analysis**
   - Search for similar features/patterns in the codebase
   - Identify files to reference in PRP
   ...

[rest unchanged]
```

---

## 💡 Key Insight:

Your question revealed a gap in the PRPs:
- ✅ They know to USE Archon in implementations
- ❌ They don't know to USE Archon during their own creation

This is exactly what Cole's agent factory does:
- Subagents have access to Archon RAG
- They research documentation through Archon
- They create better plans as a result

**We should do the same for PRP generation!**

---

## ✅ Action Items:

### Immediate (Before Executing PRPs):

1. **Add Task to Agent Factory PRP:**
   - Task 0.1: Update generate-prp.md for Archon RAG
   - Make it the FIRST task (prerequisite)
   - Enhances all future PRP generation

2. **Benefits:**
   - This PRP will use enhanced research
   - All future PRPs will benefit
   - Consistent with Cole's architecture

### Alternative (Separate Enhancement):

1. **Create new PRP:** `INITIAL_enhance_prp_generation.md`
2. **Focus:** Update generate-prp to use Archon
3. **Execute:** Before other PRPs for maximum benefit

---

## 🎬 Conclusion:

**Your observation is spot-on.** The PRPs should be generated using the same high-quality research they're recommending for implementations.

**Recommendation:**
Add Task 0.1 to the Agent Factory PRP to update generate-prp.md first, then the rest of the implementation will benefit from better research capabilities.

This creates a virtuous cycle:
1. Update generate-prp to use Archon
2. Future PRPs generated with better research
3. Implementations have better context
4. Higher quality results overall

🎯 **Should we add this task to the Agent Factory PRP?**
