# Generate PRP (Codex CLI)

Orchestrates PRP generation from INITIAL.md using a 5-phase multi-agent workflow optimized for Codex CLI with parallel Phase 2 execution for 3x speedup.

## Feature file: $ARGUMENTS

Generate a complete, implementation-ready PRP through systematic research and analysis. Ensure comprehensive context for self-validation and first-pass implementation success.

---

## CRITICAL: Codex CLI Execution Pattern

**You are executing in Codex CLI, NOT Claude Desktop.** Key differences:

1. **No Task() subagents** - Use `codex exec` with bash job control (`&`, `wait`, PID tracking)
2. **No parallel Task() invocations** - Launch background processes with timeout wrappers
3. **Profile enforcement** - Always use `--profile codex-prp` (never default profile)
4. **Timeout wrappers** - Wrap all `codex exec` calls with GNU `timeout` to prevent zombie processes
5. **Exit code handling** - Distinguish timeout (124), timeout failed (125), SIGKILL (137)

---

## The 5-Phase Workflow

### Phase 0: Setup & Initialization

**Immediate**: Read INITIAL.md → Extract feature name → Create directories → Check Archon → Phase 1 (no user interaction)

**CRITICAL SECURITY: 6-Level Feature Name Validation**

```bash
#!/bin/bash
set -euo pipefail

# Read INITIAL.md path from arguments
INITIAL_MD="$1"

# ========================================
# SECURITY VALIDATION (6 LEVELS)
# ========================================
# See .claude/patterns/security-validation.md
# Prevents: Path traversal, command injection, redundant prefixes

validate_feature_name() {
    local feature="$1"
    local validate_redundant="${2:-true}"

    # Level 1: Path traversal in feature name
    if [[ "$feature" == *".."* || "$feature" == *"/"* || "$feature" == *"\\"* ]]; then
        echo "❌ Path traversal detected: $feature" >&2
        return 1
    fi

    # Level 2: Whitelist check (alphanumeric, underscore, hyphen only)
    if [[ ! "$feature" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "❌ Invalid characters in feature name: $feature" >&2
        echo "Allowed: letters, numbers, underscore, hyphen" >&2
        return 1
    fi

    # Level 3: Length check (max 50 chars)
    if [ ${#feature} -gt 50 ]; then
        echo "❌ Feature name too long: ${#feature} chars (max 50)" >&2
        return 1
    fi

    # Level 4: Command injection characters
    local dangerous='$`;&|><'
    for (( i=0; i<${#dangerous}; i++ )); do
        local char="${dangerous:$i:1}"
        if [[ "$feature" == *"$char"* ]]; then
            echo "❌ Dangerous character detected: $char" >&2
            return 1
        fi
    done

    # Level 5: Redundant prp_ prefix check
    if [[ "$validate_redundant" == "true" && "$feature" == prp_* ]]; then
        echo "❌ Redundant 'prp_' prefix detected: $feature" >&2
        echo "Files are in prps/ directory - prefix is redundant" >&2
        echo "Expected: ${feature#prp_}" >&2
        return 1
    fi

    # Level 6: Reserved names
    local reserved=("." ".." "CON" "PRN" "AUX" "NUL")
    for name in "${reserved[@]}"; do
        if [[ "${feature^^}" == "$name" ]]; then
            echo "❌ Reserved name: $feature" >&2
            return 1
        fi
    done

    return 0
}

extract_feature_name() {
    local filepath="$1"

    # Level 0: Path traversal in FULL PATH (before basename)
    if [[ "$filepath" == *".."* ]]; then
        echo "❌ Path traversal in filepath: $filepath" >&2
        return 1
    fi

    # Extract basename, remove extension
    local basename=$(basename "$filepath" .md)

    # CRITICAL: Use ${var#prefix} NOT ${var//pattern/}
    # ${var#prefix} removes from START only (correct)
    # ${var//pattern/} removes ALL occurrences (wrong for "INITIAL_INITIAL_test")
    local feature="${basename#INITIAL_}"

    # Empty after stripping?
    if [ -z "$feature" ]; then
        echo "❌ Empty feature name after stripping INITIAL_" >&2
        return 1
    fi

    # Validate extracted name
    if ! validate_feature_name "$feature" true; then
        return 1
    fi

    echo "$feature"
}

# Extract and validate feature name
FEATURE_NAME=$(extract_feature_name "$INITIAL_MD") || {
    echo "❌ Feature name validation failed"
    exit 1
}

echo "=========================================="
echo "Codex PRP Generation Workflow"
echo "=========================================="
echo "Feature: $FEATURE_NAME"
echo "INITIAL.md: $INITIAL_MD"
echo "Output: prps/${FEATURE_NAME}.md"
echo ""

# ========================================
# CREATE DIRECTORIES
# ========================================
mkdir -p "prps/${FEATURE_NAME}/planning"
mkdir -p "prps/${FEATURE_NAME}/examples"
mkdir -p "prps/${FEATURE_NAME}/codex/logs"

# ========================================
# ARCHON SETUP (Graceful Degradation)
# ========================================
# Check if Archon MCP server is available
# If not, proceed without task tracking
ARCHON_AVAILABLE=false
PROJECT_ID=""

# Test Archon health
if mcp__archon__health_check 2>/dev/null | grep -q "healthy"; then
    ARCHON_AVAILABLE=true

    # Create project for PRP generation tracking
    PROJECT_RESULT=$(mcp__archon__manage_project "create" \
        --title "PRP Generation: ${FEATURE_NAME}" \
        --description "Creating PRP from ${INITIAL_MD}")
    PROJECT_ID=$(echo "$PROJECT_RESULT" | jq -r '.project.id')

    # Create tasks for each phase
    # Phase 1: Feature Analysis
    mcp__archon__manage_task "create" \
        --project-id "$PROJECT_ID" \
        --title "Phase 1: Feature Analysis" \
        --assignee "prp-gen-feature-analyzer" \
        --status "todo" \
        --task-order 100

    # Phase 2A: Codebase Research
    mcp__archon__manage_task "create" \
        --project-id "$PROJECT_ID" \
        --title "Phase 2A: Codebase Research" \
        --assignee "prp-gen-codebase-researcher" \
        --status "todo" \
        --task-order 90

    # Phase 2B: Documentation Hunt
    mcp__archon__manage_task "create" \
        --project-id "$PROJECT_ID" \
        --title "Phase 2B: Documentation Hunt" \
        --assignee "prp-gen-documentation-hunter" \
        --status "todo" \
        --task-order 85

    # Phase 2C: Example Curation
    mcp__archon__manage_task "create" \
        --project-id "$PROJECT_ID" \
        --title "Phase 2C: Example Curation" \
        --assignee "prp-gen-example-curator" \
        --status "todo" \
        --task-order 80

    # Phase 3: Gotcha Detection
    mcp__archon__manage_task "create" \
        --project-id "$PROJECT_ID" \
        --title "Phase 3: Gotcha Detection" \
        --assignee "prp-gen-gotcha-detective" \
        --status "todo" \
        --task-order 75

    # Phase 4: PRP Assembly
    mcp__archon__manage_task "create" \
        --project-id "$PROJECT_ID" \
        --title "Phase 4: PRP Assembly" \
        --assignee "prp-gen-assembler" \
        --status "todo" \
        --task-order 70

    echo "✅ Archon project created: $PROJECT_ID"
else
    echo "ℹ️  Archon unavailable - proceeding without tracking"
fi
```

---

### Phase 1: Feature Analysis

Analyze INITIAL.md, extract requirements, search for similar PRPs.

**Execution**:
```bash
echo "=========================================="
echo "Phase 1: Feature Analysis"
echo "=========================================="

# Update Archon task (if available)
if [ "$ARCHON_AVAILABLE" = true ]; then
    # Find task by title
    TASK_1_ID=$(mcp__archon__find_tasks --filter-by "project" --filter-value "$PROJECT_ID" | \
                jq -r '.tasks[] | select(.title | contains("Phase 1")) | .id')
    mcp__archon__manage_task "update" --task-id "$TASK_1_ID" --status "doing"
fi

# Execute Phase 1 agent
TIMEOUT_SEC=300  # 5 minutes
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"

timeout --kill-after=5s ${TIMEOUT_SEC}s codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "
Analyze INITIAL.md for PRP generation.

**INITIAL.md Path**: ${INITIAL_MD}
**Feature Name**: ${FEATURE_NAME}
**Archon Project ID**: ${PROJECT_ID}

**Your Task**:
1. Read INITIAL.md thoroughly
2. Extract requirements (explicit and implicit)
3. Search Archon for similar PRPs (if available)
4. Identify technical components needed
5. Make intelligent assumptions for gaps
6. Create comprehensive feature-analysis.md

**Output Path**: prps/${FEATURE_NAME}/planning/feature-analysis.md

**Output Format**:
\`\`\`markdown
# Feature Analysis: ${FEATURE_NAME}

## Requirements (from INITIAL.md)
- [List all explicit requirements]

## Implicit Requirements
- [Infer from context]

## Technical Components
- [What needs to be built]

## Similar PRPs (from Archon)
- [Reference similar implementations]

## Assumptions
- [Document gaps filled with assumptions]

## Success Criteria
- [Clear, measurable outcomes]
\`\`\`

**Quality Standard**: Comprehensive enough for Phase 2 agents to work independently.
" > "prps/${FEATURE_NAME}/codex/logs/phase1.log" 2>&1

PHASE1_EXIT=$?

# Check exit code
if [ $PHASE1_EXIT -eq 0 ]; then
    echo "✅ Phase 1 complete"
    if [ "$ARCHON_AVAILABLE" = true ]; then
        mcp__archon__manage_task "update" --task-id "$TASK_1_ID" --status "done"
    fi
elif [ $PHASE1_EXIT -eq 124 ]; then
    echo "❌ Phase 1 TIMEOUT (exceeded ${TIMEOUT_SEC}s)"
    exit 1
else
    echo "❌ Phase 1 failed (exit: $PHASE1_EXIT)"
    tail -20 "prps/${FEATURE_NAME}/codex/logs/phase1.log"
    exit 1
fi
```

---

### Phase 2: Parallel Research (3x SPEEDUP)

**CRITICAL**: Execute 3 agents simultaneously using bash job control.

**Pattern**: `codex exec &` + immediate `$!` capture + individual `wait` calls with exit code capture

```bash
echo "=========================================="
echo "Phase 2: Parallel Research (3 agents)"
echo "=========================================="

# Update Archon tasks to "doing" (if available)
if [ "$ARCHON_AVAILABLE" = true ]; then
    for phase in "Phase 2A" "Phase 2B" "Phase 2C"; do
        TASK_ID=$(mcp__archon__find_tasks --filter-by "project" --filter-value "$PROJECT_ID" | \
                  jq -r ".tasks[] | select(.title | contains(\"$phase\")) | .id")
        mcp__archon__manage_task "update" --task-id "$TASK_ID" --status "doing"
    done
fi

# Configuration
TIMEOUT_SEC=600  # 10 minutes for research agents
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"
START_TIME=$(date +%s)

# ========================================
# AGENT 2A: Codebase Researcher
# ========================================
timeout --kill-after=5s ${TIMEOUT_SEC}s codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "
Search codebase patterns for PRP generation.

**Feature Analysis**: prps/${FEATURE_NAME}/planning/feature-analysis.md (READ FIRST)
**Your Task**:
1. Read feature-analysis.md to understand requirements
2. Search Archon knowledge base for similar patterns (if available)
3. Grep local codebase for relevant implementations
4. Extract naming conventions, file structure, coding patterns
5. Document what to mimic vs what to adapt

**Output**: prps/${FEATURE_NAME}/planning/codebase-patterns.md

**Output Format**:
\`\`\`markdown
# Codebase Patterns: ${FEATURE_NAME}

## Similar Implementations
- [List from Archon/codebase with file paths]

## Patterns to Mimic
- [Specific patterns with code examples]

## Patterns to Adapt
- [What needs customization]

## Naming Conventions
- [File names, function names, variable names]

## File Structure
- [Directory layout, where files go]
\`\`\`
" > "prps/${FEATURE_NAME}/codex/logs/phase2a.log" 2>&1 &
PID_2A=$!
echo "   Agent 2A (Codebase Research):  PID $PID_2A"

# ========================================
# AGENT 2B: Documentation Hunter
# ========================================
timeout --kill-after=5s ${TIMEOUT_SEC}s codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "
Find official documentation for PRP generation.

**Feature Analysis**: prps/${FEATURE_NAME}/planning/feature-analysis.md (READ FIRST)
**Your Task**:
1. Read feature-analysis.md to understand technologies needed
2. Search Archon knowledge base for documentation (if available)
3. Use WebSearch for official docs
4. Find sections with code examples
5. Document URLs with specific sections

**Output**: prps/${FEATURE_NAME}/planning/documentation-links.md

**Output Format**:
\`\`\`markdown
# Documentation Links: ${FEATURE_NAME}

## Primary Documentation
- **Library/Framework**: [Name]
  - URL: [Full URL]
  - Sections: [Specific sections to read]
  - Why: [Relevance to this feature]
  - Code Examples: [Yes/No, which sections]

## Secondary Documentation
- [Additional resources]

## Critical Gotchas from Docs
- [Security warnings, performance notes, deprecated APIs]
\`\`\`
" > "prps/${FEATURE_NAME}/codex/logs/phase2b.log" 2>&1 &
PID_2B=$!
echo "   Agent 2B (Documentation Hunt):   PID $PID_2B"

# ========================================
# AGENT 2C: Example Curator
# ========================================
timeout --kill-after=5s ${TIMEOUT_SEC}s codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "
Extract code examples for PRP generation.

**Feature Analysis**: prps/${FEATURE_NAME}/planning/feature-analysis.md (READ FIRST)
**Your Task**:
1. Read feature-analysis.md to understand what examples are needed
2. Search Archon + local codebase for relevant code
3. EXTRACT actual code to prps/${FEATURE_NAME}/examples/ (NOT just references!)
4. Create README.md in examples/ with \"what to mimic\" guidance
5. Document examples in examples-to-include.md

**Outputs**:
- prps/${FEATURE_NAME}/examples/*.{py,sh,js,etc} (actual code files)
- prps/${FEATURE_NAME}/examples/README.md (usage guide)
- prps/${FEATURE_NAME}/planning/examples-to-include.md (index)

**Example README Format**:
\`\`\`markdown
# Examples: ${FEATURE_NAME}

## Example 1: [Name]
**File**: [filename]
**Source**: [origin with line numbers]
**Pattern**: [What pattern it demonstrates]

### What to Mimic
- [Specific patterns to copy]

### What to Adapt
- [What needs customization]

### What to Skip
- [Irrelevant sections]
\`\`\`
" > "prps/${FEATURE_NAME}/codex/logs/phase2c.log" 2>&1 &
PID_2C=$!
echo "   Agent 2C (Example Curation):    PID $PID_2C"

echo ""
echo "   Waiting for all 3 agents to complete..."

# ========================================
# WAIT FOR ALL AGENTS (CRITICAL PATTERN)
# ========================================
# GOTCHA #1: Exit code timing - MUST capture immediately after wait
# WRONG: wait $PID_2A; wait $PID_2B; wait $PID_2C; EXIT=$?  (loses 2A and 2B)
# RIGHT: wait $PID; EXIT=$? for EACH agent

wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# ========================================
# VALIDATE ALL SUCCEEDED
# ========================================
echo ""
if [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]]; then
    echo "✅ Phase 2 complete (all agents succeeded)"
    echo "   Duration: ${DURATION}s"

    # Update Archon tasks to "done"
    if [ "$ARCHON_AVAILABLE" = true ]; then
        for phase in "Phase 2A" "Phase 2B" "Phase 2C"; do
            TASK_ID=$(mcp__archon__find_tasks --filter-by "project" --filter-value "$PROJECT_ID" | \
                      jq -r ".tasks[] | select(.title | contains(\"$phase\")) | .id")
            mcp__archon__manage_task "update" --task-id "$TASK_ID" --status "done"
        done
    fi
else
    echo "❌ Phase 2 failed - Agent exit codes:"
    echo "   - Agent 2A (Codebase):  exit $EXIT_2A"
    echo "   - Agent 2B (Docs):      exit $EXIT_2B"
    echo "   - Agent 2C (Examples):  exit $EXIT_2C"
    echo ""
    echo "Logs:"
    if [ $EXIT_2A -ne 0 ]; then
        echo "=== Agent 2A Errors ==="
        tail -20 "prps/${FEATURE_NAME}/codex/logs/phase2a.log"
    fi
    if [ $EXIT_2B -ne 0 ]; then
        echo "=== Agent 2B Errors ==="
        tail -20 "prps/${FEATURE_NAME}/codex/logs/phase2b.log"
    fi
    if [ $EXIT_2C -ne 0 ]; then
        echo "=== Agent 2C Errors ==="
        tail -20 "prps/${FEATURE_NAME}/codex/logs/phase2c.log"
    fi

    exit 1
fi
```

---

### Phase 3: Gotcha Detection

Identify pitfalls with solutions (not just warnings).

```bash
echo "=========================================="
echo "Phase 3: Gotcha Detection"
echo "=========================================="

# Update Archon task (if available)
if [ "$ARCHON_AVAILABLE" = true ]; then
    TASK_3_ID=$(mcp__archon__find_tasks --filter-by "project" --filter-value "$PROJECT_ID" | \
                jq -r '.tasks[] | select(.title | contains("Phase 3")) | .id')
    mcp__archon__manage_task "update" --task-id "$TASK_3_ID" --status "doing"
fi

TIMEOUT_SEC=300  # 5 minutes
timeout --kill-after=5s ${TIMEOUT_SEC}s codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "
Identify gotchas for PRP generation.

**Research Docs** (READ ALL):
- prps/${FEATURE_NAME}/planning/feature-analysis.md
- prps/${FEATURE_NAME}/planning/codebase-patterns.md
- prps/${FEATURE_NAME}/planning/documentation-links.md

**Your Task**:
1. Read all research documents
2. Search Archon for common gotchas (if available)
3. Use WebSearch for security/performance gotchas
4. Document SOLUTIONS (not just warnings)
5. Categorize by severity (Critical, High, Medium, Low)

**Output**: prps/${FEATURE_NAME}/planning/gotchas.md

**Output Format**:
\`\`\`markdown
# Known Gotchas: ${FEATURE_NAME}

## Critical Gotchas
### 1. [Gotcha Name]
**Severity**: Critical
**What it is**: [Explanation]
**Why it's a problem**: [Impact]
**How to detect**: [Detection method]
**How to avoid/fix**: [Solution with code example]

## High Priority Gotchas
[Same format]

## Medium Priority Gotchas
[Same format]
\`\`\`

**Quality Standard**: Every gotcha MUST have a concrete solution with code.
" > "prps/${FEATURE_NAME}/codex/logs/phase3.log" 2>&1

PHASE3_EXIT=$?

if [ $PHASE3_EXIT -eq 0 ]; then
    echo "✅ Phase 3 complete"
    if [ "$ARCHON_AVAILABLE" = true ]; then
        mcp__archon__manage_task "update" --task-id "$TASK_3_ID" --status "done"
    fi
elif [ $PHASE3_EXIT -eq 124 ]; then
    echo "❌ Phase 3 TIMEOUT (exceeded ${TIMEOUT_SEC}s)"
    exit 1
else
    echo "❌ Phase 3 failed (exit: $PHASE3_EXIT)"
    tail -20 "prps/${FEATURE_NAME}/codex/logs/phase3.log"
    exit 1
fi
```

---

### Phase 4: PRP Assembly

Synthesize all research into final PRP.

```bash
echo "=========================================="
echo "Phase 4: PRP Assembly"
echo "=========================================="

# Update Archon task (if available)
if [ "$ARCHON_AVAILABLE" = true ]; then
    TASK_4_ID=$(mcp__archon__find_tasks --filter-by "project" --filter-value "$PROJECT_ID" | \
                jq -r '.tasks[] | select(.title | contains("Phase 4")) | .id')
    mcp__archon__manage_task "update" --task-id "$TASK_4_ID" --status "doing"
fi

TIMEOUT_SEC=180  # 3 minutes
timeout --kill-after=5s ${TIMEOUT_SEC}s codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "
Assemble final PRP from all research.

**Research Docs** (READ ALL 5):
- prps/${FEATURE_NAME}/planning/feature-analysis.md
- prps/${FEATURE_NAME}/planning/codebase-patterns.md
- prps/${FEATURE_NAME}/planning/documentation-links.md
- prps/${FEATURE_NAME}/planning/examples-to-include.md
- prps/${FEATURE_NAME}/planning/gotchas.md

**Template**: prps/templates/prp_base.md (USE THIS STRUCTURE)

**Your Task**:
1. Read all 5 research documents thoroughly
2. Read PRP template for structure
3. Synthesize into coherent PRP with these sections:
   - Goal (from feature-analysis)
   - Why (business value, pain points)
   - What (core features, success criteria)
   - All Needed Context (documentation links, codebase patterns)
   - Implementation Blueprint (task list from analysis)
   - Known Gotchas (all gotchas with solutions)
   - Validation Loop (how to verify implementation)
4. Include ALL documentation URLs from documentation-links.md
5. Reference examples directory (not inline code)
6. **SCORE THE PRP** (must be >= 8/10)

**Output**: prps/${FEATURE_NAME}.md

**PRP Quality Scoring**:
- 10/10: Comprehensive, all sections complete, 8+ examples, 10+ gotchas, clear validation
- 9/10:  Very good, minor gaps, 5+ examples, 8+ gotchas
- 8/10:  Good, sufficient for implementation, 3+ examples, 5+ gotchas
- 7/10:  Acceptable, some sections thin, 2+ examples, 3+ gotchas
- <7/10: Insufficient - regenerate research

**Add at end of PRP**:
\`\`\`markdown
## PRP Quality Self-Assessment

**Score: X/10**

**Reasoning**:
- ✅ [What's strong]
- ✅ [What's comprehensive]
- ⚠️  [What could be better]

**Deduction reasoning**: [Why not 10/10]

**Overall Confidence**: [HIGH/MEDIUM/LOW] - [explanation]
\`\`\`

**Store in Archon** (if available):
- Create document with title \"PRP: ${FEATURE_NAME}\"
- Type: \"prp\"
- Content: Full PRP markdown
" > "prps/${FEATURE_NAME}/codex/logs/phase4.log" 2>&1

PHASE4_EXIT=$?

if [ $PHASE4_EXIT -eq 0 ]; then
    echo "✅ Phase 4 complete"
    if [ "$ARCHON_AVAILABLE" = true ]; then
        mcp__archon__manage_task "update" --task-id "$TASK_4_ID" --status "done"
    fi
elif [ $PHASE4_EXIT -eq 124 ]; then
    echo "❌ Phase 4 TIMEOUT (exceeded ${TIMEOUT_SEC}s)"
    exit 1
else
    echo "❌ Phase 4 failed (exit: $PHASE4_EXIT)"
    tail -20 "prps/${FEATURE_NAME}/codex/logs/phase4.log"
    exit 1
fi
```

---

### Phase 5: Quality Check & Delivery

Enforce quality gate (≥8/10), offer regeneration if needed.

```bash
echo "=========================================="
echo "Phase 5: Quality Check & Delivery"
echo "=========================================="

# ========================================
# EXTRACT QUALITY SCORE
# ========================================
PRP_FILE="prps/${FEATURE_NAME}.md"

if [ ! -f "$PRP_FILE" ]; then
    echo "❌ PRP file not found: $PRP_FILE"
    exit 1
fi

# Extract score using regex
QUALITY_SCORE=$(grep -iE 'Score[[:space:]]*:[[:space:]]*[0-9]+/10' "$PRP_FILE" | \
                sed -E 's/.*Score[[:space:]]*:[[:space:]]*([0-9]+)\/10.*/\1/' | \
                head -1)

if [ -z "$QUALITY_SCORE" ]; then
    echo "⚠️  Warning: No quality score found in PRP"
    QUALITY_SCORE=0
fi

echo "PRP Quality Score: ${QUALITY_SCORE}/10"

# ========================================
# QUALITY GATE ENFORCEMENT (≥8/10)
# ========================================
MIN_SCORE=8

if [ "$QUALITY_SCORE" -ge "$MIN_SCORE" ]; then
    echo "✅ Quality Gate PASSED (${QUALITY_SCORE}/10 >= ${MIN_SCORE}/10)"
else
    echo "❌ Quality Gate FAILED (${QUALITY_SCORE}/10 < ${MIN_SCORE}/10)"
    echo ""
    echo "Options:"
    echo "  1. Regenerate entire PRP (re-run all phases)"
    echo "  2. Regenerate research only (re-run Phase 2)"
    echo "  3. Manually improve PRP sections"
    echo "  4. Proceed anyway (not recommended)"
    echo "  5. Abort"
    echo ""
    read -p "Choose (1/2/3/4/5): " choice

    case "$choice" in
        1)
            echo "Regenerating entire PRP..."
            # Re-run workflow (recursive call)
            exec "$0" "$INITIAL_MD"
            ;;
        2)
            echo "Regenerating Phase 2 research..."
            # Re-run Phase 2 section above (implementation needed)
            echo "⚠️  Not implemented yet - please re-run full workflow"
            exit 1
            ;;
        3)
            echo "Manual improvement:"
            echo "  1. Edit: $PRP_FILE"
            echo "  2. Update score in PRP file"
            echo "  3. Re-run quality check"
            exit 1
            ;;
        4)
            echo "⚠️  Proceeding with ${QUALITY_SCORE}/10 quality"
            ;;
        5)
            echo "Aborted by user"
            exit 1
            ;;
        *)
            echo "Invalid choice - aborting"
            exit 1
            ;;
    esac
fi

# ========================================
# COMPLETION REPORT
# ========================================
echo ""
echo "=========================================="
echo "✅ PRP Generated Successfully!"
echo "=========================================="
echo ""
echo "**Output**: $PRP_FILE"
echo ""
echo "**Quality Assessment**:"
echo "- PRP Quality Score: ${QUALITY_SCORE}/10"
echo "- Documentation sources: $(grep -c '^- url:' "$PRP_FILE" || echo "0") URLs"
echo "- Code examples: $(find "prps/${FEATURE_NAME}/examples" -type f 2>/dev/null | wc -l) files"
echo "- Gotchas documented: $(grep -c '^### [0-9]' "prps/${FEATURE_NAME}/planning/gotchas.md" 2>/dev/null || echo "0")"
echo ""
echo "**Next Steps**:"
echo "1. Review: cat $PRP_FILE"
echo "2. Execute: codex exec --prompt \"Implement prps/${FEATURE_NAME}.md\""
echo ""

# Update Archon project (if available)
if [ "$ARCHON_AVAILABLE" = true ]; then
    mcp__archon__manage_project "update" \
        --project-id "$PROJECT_ID" \
        --description "COMPLETED: PRP quality ${QUALITY_SCORE}/10"

    # Store PRP as document
    # (Implementation depends on Archon document API)
    echo "✅ Archon project updated: $PROJECT_ID"
fi
```

---

## Critical Gotchas (MUST AVOID)

### Gotcha #1: Exit Code Loss from Timing Race Condition
**Pattern**: `wait $PID; EXIT=$?` IMMEDIATELY (semicolon enforces sequential)

```bash
# ❌ WRONG - Only captures last exit code
wait $PID_2A
wait $PID_2B
wait $PID_2C
EXIT=$?  # Only has 2C exit code!

# ✅ RIGHT - Immediate capture
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?
```

### Gotcha #2: Security Validation Bypass
**Pattern**: 6-level validation BEFORE any path operations

```bash
# ❌ WRONG - No validation
FEATURE=$(basename "$INITIAL_MD" .md | sed 's/INITIAL_//')
mkdir -p "prps/${FEATURE}/planning"  # DANGER!

# ✅ RIGHT - Validate first
FEATURE=$(extract_feature_name "$INITIAL_MD") || exit 1
mkdir -p "prps/${FEATURE}/planning"  # Safe
```

### Gotcha #3: Zombie Processes from Missing Timeout
**Pattern**: ALWAYS wrap `codex exec` with `timeout`

```bash
# ❌ WRONG - Can hang forever
codex exec --prompt "..." &

# ✅ RIGHT - Timeout wrapper
timeout --kill-after=5s 600s codex exec --prompt "..." &
```

### Gotcha #4: Profile Omission
**Pattern**: ALWAYS use `--profile codex-prp`

```bash
# ❌ WRONG - Uses default profile
codex exec --prompt "..."

# ✅ RIGHT - Explicit profile
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"
codex exec --profile "$CODEX_PROFILE" --prompt "..."
```

### Gotcha #5: Output Interleaving
**Pattern**: Separate log file per agent

```bash
# ❌ WRONG - Shared stdout (corrupted logs)
codex exec --prompt "2a" &
codex exec --prompt "2b" &

# ✅ RIGHT - Separate files
codex exec --prompt "2a" > logs/2a.log 2>&1 &
codex exec --prompt "2b" > logs/2b.log 2>&1 &
```

### Gotcha #6: Sequential Execution (Anti-Pattern)
**Pattern**: Use `&` for parallel execution

```bash
# ❌ WRONG - Sequential (wastes 10 minutes)
execute_phase "phase2a"
execute_phase "phase2b"
execute_phase "phase2c"

# ✅ RIGHT - Parallel (3x speedup)
execute_phase "phase2a" &
execute_phase "phase2b" &
execute_phase "phase2c" &
wait
```

### Gotcha #7: Timeout Exit Code Confusion
**Pattern**: Distinguish 124 (timeout), 125 (timeout failed), 137 (SIGKILL)

```bash
# ❌ WRONG - Generic handling
if [ $EXIT -ne 0 ]; then
    echo "Failed"
fi

# ✅ RIGHT - Specific handling
case $EXIT in
    0)   echo "✅ Success" ;;
    124) echo "❌ TIMEOUT" ;;
    125) echo "❌ Timeout command failed" ;;
    137) echo "❌ KILLED (SIGKILL)" ;;
    *)   echo "❌ Failed (exit $EXIT)" ;;
esac
```

### Gotcha #8-13: See Full Gotchas Document
- **#8**: Race condition in process spawning (use immediate `$!` capture)
- **#9**: JSONL manifest corruption (use separate files, merge after)
- **#10**: Approval policy blocking (use `on-failure` for Phase 2)
- **#11**: Dependency validation omission (check dependencies before phase)
- **#12**: Redundant `prp_` prefix (validation rejects)
- **#13**: `removeprefix()` vs `replace()` (use `${var#prefix}` in bash)

**See**: `prps/codex_commands/planning/gotchas.md` for full details with code examples.

---

## Error Handling

```bash
# Agent failure - offer retry/skip/abort
if [ $EXIT -ne 0 ]; then
    echo "❌ Agent failed (exit: $EXIT)"
    echo "Options: 1. Retry  2. Skip  3. Abort"
    read -p "Choose (1/2/3): " choice
    case "$choice" in
        1) # Retry logic ;;
        2) echo "⚠️  Skipping, continuing with partial results" ;;
        3) exit 1 ;;
    esac
fi

# Archon unavailable - graceful degradation
if [ "$ARCHON_AVAILABLE" = false ]; then
    echo "ℹ️  Archon unavailable - proceeding without tracking"
fi

# Quality score <8/10 - offer regeneration
if [ "$QUALITY_SCORE" -lt 8 ]; then
    echo "⚠️  PRP scored ${QUALITY_SCORE}/10 - below 8/10"
    # Interactive menu (see Phase 5)
fi
```

---

## Success Metrics

```bash
# Calculate metrics
TOTAL_TIME=$(($(date +%s) - START_TIME))
DOC_COUNT=$(grep -c '^- url:' "$PRP_FILE" || echo "0")
EXAMPLE_COUNT=$(find "prps/${FEATURE_NAME}/examples" -type f 2>/dev/null | wc -l)
GOTCHA_COUNT=$(grep -c '^### [0-9]' "prps/${FEATURE_NAME}/planning/gotchas.md" 2>/dev/null || echo "0")

echo "Metrics:"
echo "- Total time: ${TOTAL_TIME}s (target: <900s / 15min)"
echo "- PRP quality: ${QUALITY_SCORE}/10 (target: >=8)"
echo "- Documentation: ${DOC_COUNT} sources (target: 5-7)"
echo "- Examples: ${EXAMPLE_COUNT} files (target: 2-4)"
echo "- Gotchas: ${GOTCHA_COUNT} documented (target: 5-10)"
echo "- Execution ready: $([ "$QUALITY_SCORE" -ge 8 ] && echo "yes" || echo "no")"
```

---

## Key Innovations

### 1. Parallel Phase 2 (3x Speedup)
- Sequential: 5min + 4min + 5min = 14 min
- Parallel: max(5min, 4min, 5min) = 5 min
- **64% faster**

### 2. Bash Job Control
- Background processes: `&`
- PID tracking: `$!` (immediate capture)
- Exit codes: `wait $PID; EXIT=$?` (immediate)

### 3. Security Validation
- 6-level validation (defense in depth)
- Whitelist approach (not blacklist)
- Prevents path traversal, command injection

### 4. Quality Gates
- Extract score: regex + sed
- Enforce ≥8/10 minimum
- Interactive regeneration (max 3 attempts)

---

Goal: One-pass implementation success through comprehensive PRPs (8+/10 quality) with 3x speedup via parallel execution.
