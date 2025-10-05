# INITIAL: PRP System Context Cleanup & Optimization

## FEATURE

Refactor the PRP generation and execution system to eliminate context pollution while preserving all advanced functionality (Archon integration, parallel execution, quality scoring, validation loops).

**Specific Goals**:
1. Reduce command file sizes by 80% (582→120 lines for generate-prp, 620→100 lines for execute-prp)
2. Extract implementation patterns to dedicated reference documents
3. Consolidate Archon workflow to single source of truth
4. Maintain or improve functionality and performance
5. Improve maintainability and token efficiency

## CURRENT STATE

**Problems Identified**:
- ⚠️ Context pollution in command files (8.4x-15.5x bloat vs original)
- 🔄 Repeated Archon patterns across 6+ locations
- 📝 Pseudocode in commands instead of reference docs
- 🎨 Excessive visual markers (50+ emojis) diminishing emphasis
- 📋 Duplicate quality gates in multiple locations
- 📁 File organization pollution (global research/, root examples/)

**Current Structure**:
```
.claude/
├── commands/
│   ├── generate-prp.md          # 582 lines (should be ~80)
│   └── execute-prp.md           # 620 lines (should be ~100)
└── agents/
    ├── prp-gen-*.md             # Generation subagents
    └── prp-exec-*.md            # Execution subagents

prps/
├── templates/
│   └── prp_base.md              # 212 lines (good - no change)
├── research/                    # ❌ POLLUTION: Global, unclear ownership
│   ├── feature-analysis.md      # Which feature?
│   ├── codebase-patterns.md     # Which feature?
│   └── gotchas.md               # Which feature?
└── user_auth.md

examples/                        # ❌ POLLUTION: Root directory clutter
├── user_auth/                   # Feature-specific but pollutes root
├── payment_processing/
└── notification_system/
```

**File Organization Problems**:
- After 5 PRPs: 25 files in `prps/research/` with no clear ownership
- Root `examples/` directory polluted with generated artifacts
- Cannot easily cleanup/archive completed features
- Unclear which research docs belong to which PRP

## DESIRED STATE

**New Structure**:
```
.claude/
├── commands/
│   ├── generate-prp.md          # 80-120 lines (high-level workflow)
│   ├── execute-prp.md           # 80-120 lines (high-level workflow)
│   └── prp-cleanup.md           # NEW: Archive completed feature artifacts
├── patterns/
│   ├── archon-workflow.md       # Centralized Archon integration patterns
│   ├── parallel-subagents.md    # Parallel execution implementation guide
│   ├── quality-gates.md         # Quality check procedures
│   └── error-handling.md        # Standard error recovery patterns
├── templates/
│   ├── completion-report.md     # Success metrics template
│   └── validation-report.md     # Validation results template
└── agents/
    ├── prp-gen-*.md             # Generation subagents (no change)
    └── prp-exec-*.md            # Execution subagents (no change)

prps/
├── templates/
│   └── prp_base.md              # 212 lines (no change)
├── archive/                     # NEW: Archived completed features
└── user_auth/                   # ✅ CLEAN: Self-contained per feature
    ├── INITIAL.md
    ├── user_auth.md             # Main deliverable
    ├── planning/                # Research artifacts (scoped)
    │   ├── feature-analysis.md
    │   ├── codebase-patterns.md
    │   ├── documentation-links.md
    │   ├── examples-to-include.md
    │   └── gotchas.md
    ├── examples/                # Extracted code (scoped, not root pollution)
    │   ├── README.md
    │   └── *.py files
    └── execution/               # Implementation artifacts (scoped)
        ├── execution-plan.md
        ├── test-generation-report.md
        └── validation-report.md
```

**File Organization Benefits**:
- ✅ Self-contained features (easy cleanup/archive)
- ✅ No root directory pollution (examples scoped per-feature)
- ✅ Clear artifact ownership (all in `prps/{feature}/`)
- ✅ Easy archival: `mv prps/user_auth prps/archive/`
- ✅ Visible planning/execution dirs (no secrets, user requested)
- ✅ Less context pollution (only load relevant feature's examples)

## EXAMPLES

**Pattern to Follow**: Context-Engineering-Intro original approach
- Location: `repos/context-engineering-intro/claude-code-full-guide/.claude/commands/`
- What to mimic: Concise commands (40-69 lines) with clear phase descriptions
- Contrast with: Current bloated versions with excessive pseudocode

**Reference for Archon Integration**:
- File: `CLAUDE.md` lines 424-509 (Archon Integration & Workflow section)
- What exists: Already has good Archon documentation
- What to add: Consolidate ALL Archon patterns from commands here

**Quality Gate Pattern**:
- File: `prps/templates/prp_base.md` lines 195-202
- Pattern: Already has validation checklist
- Action: Reference this instead of duplicating in commands

## DOCUMENTATION

**Context Engineering Principles**:
- URL: https://github.com/coleam00/Context-Engineering-Intro
- Why: Original system design philosophy - concise commands, comprehensive context
- Key insight: Commands define WHAT, not HOW

**Claude Code Command Best Practices**:
- Principle: Commands should be high-level workflows
- Principle: Implementation details belong in referenced documents
- Principle: Use progressive disclosure (overview → details when needed)

**Current Implementation to Preserve**:
- Archon MCP integration
- Parallel subagent execution (3x speedup)
- Quality scoring system (8+/10 minimum)
- Physical code extraction to examples/
- Systematic validation with iteration loops
- Time tracking and success metrics

## TASK BREAKDOWN

### Phase 0: Fix File Organization (Foundation)

**Why First**: Establish clean structure before refactoring commands. Avoids drift from original while improving organization.

**Task 0.1: Update generate-prp.md File Paths**
- MODIFY `.claude/commands/generate-prp.md`
- CHANGE: `prps/research/` → `prps/{feature}/planning/`
- CHANGE: `examples/{feature}/` → `prps/{feature}/examples/`
- UPDATE: All subagent prompts to use new paths
- PRESERVE: All functionality, just change output directories

**Task 0.2: Update execute-prp.md File Paths**
- MODIFY `.claude/commands/execute-prp.md`
- CHANGE: Read from `prps/{feature}/planning/` instead of `prps/research/`
- CHANGE: Output to `prps/{feature}/execution/` instead of `prps/`
- UPDATE: All subagent prompts to use new paths
- PRESERVE: All functionality, just change input/output directories

**Task 0.3: Update Subagent Prompts**
- MODIFY all `prp-gen-*.md` agents
- UPDATE: Output paths to `prps/{feature}/planning/`
- MODIFY all `prp-exec-*.md` agents
- UPDATE: Input paths from `prps/{feature}/planning/`
- UPDATE: Output paths to `prps/{feature}/execution/`

**Task 0.4: Create Cleanup Command**
- CREATE `.claude/commands/prp-cleanup.md`
- FUNCTIONALITY: Archive or delete planning/, examples/, execution/ directories
- KEEP: INITIAL.md and {feature}.md (core artifacts)
- MOVE TO: `prps/archive/{feature}/` with timestamp
- INTERACTIVE: Offer user choice (archive/delete/cancel)
- VALIDATION: Confirm feature exists before cleanup

**Task 0.5: Test New File Organization**
- CREATE: `prps/test_file_org/INITIAL.md` (simple test feature)
- RUN: `/generate-prp prps/test_file_org/INITIAL.md`
- VERIFY: Creates `prps/test_file_org/planning/` (not `prps/research/`)
- VERIFY: Creates `prps/test_file_org/examples/` (not root `examples/`)
- VERIFY: All 5 research docs in correct location
- RUN: `/prp-cleanup test_file_org`
- VERIFY: Archives correctly to `prps/archive/test_file_org/`

### Phase 1: Create Pattern Reference Documents

**Task 1.1: Extract Archon Workflow Pattern**
- CREATE `.claude/patterns/archon-workflow.md`
- Content: Health check, project creation, task management, status updates
- Extract from: `generate-prp.md` and `execute-prp.md` repeated patterns
- Include: When to skip Archon (graceful degradation), error handling

**Task 1.2: Extract Parallel Execution Pattern**
- CREATE `.claude/patterns/parallel-subagents.md`
- Content: How to invoke multiple Task tools in single message
- Extract from: Phase 2 sections in both commands
- Include: Code examples, timing benefits, pitfall avoidance

**Task 1.3: Extract Quality Gates Pattern**
- CREATE `.claude/patterns/quality-gates.md`
- Content: Quality scoring criteria, validation levels, pass/fail thresholds
- Extract from: generate-prp.md lines 500-524, execute-prp.md lines 530-549
- Include: Reference to prp_base.md validation checklist

**Task 1.4: Extract Error Handling Pattern**
- CREATE `.claude/patterns/error-handling.md`
- Content: Subagent failure recovery, Archon unavailable handling, quality score failures
- Extract from: Error handling sections in both commands
- Include: User interaction decision trees

### Phase 2: Create Report Templates

**Task 2.1: Create Completion Report Template**
- CREATE `.claude/templates/completion-report.md`
- Content: Success metrics structure, file listing format, next steps
- Extract from: Phase 5 sections in both commands
- Include: Placeholders for dynamic values

**Task 2.2: Create Validation Report Template**
- CREATE `.claude/templates/validation-report.md`
- Content: Validation level results, iteration history, final status
- Used by: prp-exec-validator subagent
- Include: Links to relevant log files

### Phase 3: Simplify Command Files

**Task 3.1: Refactor generate-prp.md**
- REDUCE from 582 to ~100 lines
- REMOVE: Lines 24-77 (setup pseudocode), lines 143-227 (detailed context templates)
- REMOVE: Lines 500-524 (quality checks), lines 542-582 (detailed metrics)
- KEEP: Phase overview, subagent names, quality minimums, key innovations
- ADD: References to `.claude/patterns/` for implementation details
- PRESERVE: All functionality (5-phase workflow, parallel Phase 2, Archon integration)

**Task 3.2: Refactor execute-prp.md**
- REDUCE from 620 to ~100 lines
- REMOVE: Lines 24-71 (setup pseudocode), lines 83-231 (detailed implementation per group)
- REMOVE: Lines 530-549 (quality checks), lines 587-597 (parallel execution math)
- KEEP: Phase overview, dependency analysis, parallel/sequential logic, validation iteration
- ADD: References to `.claude/patterns/` for implementation details
- PRESERVE: All functionality (5-phase workflow, parallel task execution, test generation)

### Phase 4: Update CLAUDE.md

**Task 4.1: Add Archon Pattern Section**
- MODIFY `CLAUDE.md` Archon Integration section (lines 424-509)
- ADD: Consolidated Archon workflow from extracted patterns
- ADD: Reference to `.claude/patterns/archon-workflow.md` for details
- ENSURE: Single source of truth for Archon integration

**Task 4.2: Add Pattern Reference Section**
- ADD new section: "## PRP Implementation Patterns"
- Content: Index of all pattern documents with brief descriptions
- Location: After Archon Integration section
- Purpose: Quick reference for implementation details

### Phase 5: Validation & Testing

**Task 5.1: Test PRP Generation**
- RUN: `/generate-prp prps/INITIAL_test_feature.md`
- VERIFY: All 5 phases execute correctly
- VERIFY: Archon integration works (or gracefully skips)
- VERIFY: Quality score >= 8/10
- VERIFY: Physical code extraction to examples/
- MEASURE: Token usage reduction

**Task 5.2: Test PRP Execution**
- CREATE: Simple test PRP
- RUN: `/execute-prp prps/test_feature.md`
- VERIFY: All 5 phases execute correctly
- VERIFY: Parallel task execution works
- VERIFY: Validation iteration loops work
- MEASURE: Functionality preservation

**Task 5.3: Documentation Update**
- UPDATE `README.md` if needed
- CREATE migration notes for users
- DOCUMENT new pattern structure
- ADD examples of referencing patterns from commands

**Task 5.4: File Organization Migration**
- DOCUMENT migration path for existing PRPs
- CREATE script or instructions for moving old structure to new
- EXAMPLE:
  ```bash
  # Migrate existing PRP to new structure
  mkdir -p prps/user_auth/planning
  mv prps/research/*auth* prps/user_auth/planning/

  mkdir -p prps/user_auth/examples
  mv examples/user_auth/* prps/user_auth/examples/
  rmdir examples/user_auth
  ```
- ADD to CLAUDE.md or separate migration guide

## OTHER CONSIDERATIONS

### Critical Success Factors

**Preserve Functionality**:
- ✅ Archon integration (health check → project → tasks → tracking)
- ✅ Parallel Phase 2 research (3x speedup)
- ✅ Parallel Phase 2 implementation (30-50% speedup)
- ✅ Quality scoring (8+/10 minimum)
- ✅ Physical code extraction
- ✅ Validation iteration loops
- ✅ Time tracking

**Don't Break**:
- ❌ Existing PRPs (should still be executable with new commands)
- ❌ Subagent interfaces (they reference commands via context)
- ❌ User workflows (same `/generate-prp` and `/execute-prp` entry points)

### Gotchas to Avoid

**Common Pitfalls**:
1. Over-simplifying commands → losing necessary context
2. Breaking subagent prompts that reference command structure
3. Removing Archon graceful degradation (when MCP unavailable)
4. Losing performance metrics and time tracking
5. Making patterns too abstract (need concrete examples)

**Validation Requirements**:
1. Commands must still provide enough context for subagents
2. Pattern documents must be easily discoverable
3. Templates must be actually used (not just created and ignored)
4. Token reduction must not sacrifice functionality

### Token Budget Impact

**Current Usage** (estimated):
- generate-prp command: ~1800 tokens
- execute-prp command: ~2000 tokens
- Total per PRP lifecycle: ~3800 tokens

**Target Usage**:
- generate-prp command: ~400 tokens (78% reduction)
- execute-prp command: ~350 tokens (82% reduction)
- Pattern docs (loaded on-demand): ~800 tokens
- Net savings per invocation: ~2250 tokens (59% reduction)

### Migration Notes

**Backwards Compatibility**:
- Existing PRPs should execute without modification
- Subagents may need minor prompt updates (reference new pattern paths)
- Users should see no difference in workflow

**Rollout Strategy**:
1. **Phase 0 First**: Fix file organization (foundation for rest)
   - Update file paths in generate-prp, execute-prp
   - Create cleanup command
   - Test with sample feature
2. Create pattern docs (non-breaking)
3. Test pattern docs with sample PRPs
4. Simplify commands with references to patterns
5. Update CLAUDE.md last (consolidate learnings)
6. Archive old versions for comparison

**Migration Path for Existing PRPs**:
- Old structure PRPs will still execute (backwards compatible)
- New PRPs will use new per-feature structure
- Gradual migration: Use `/prp-cleanup` to reorganize completed PRPs
- Script provided for bulk migration if needed

## SUCCESS CRITERIA

**File Organization**:
- [ ] New PRPs create `prps/{feature}/planning/` (not global `prps/research/`)
- [ ] New PRPs create `prps/{feature}/examples/` (not root `examples/{feature}/`)
- [ ] New PRPs create `prps/{feature}/execution/` (scoped reports)
- [ ] `/prp-cleanup` command works correctly (archive/delete options)
- [ ] No root directory pollution from generated artifacts

**Command Simplification**:
- [ ] generate-prp.md reduced to 80-120 lines (from 582)
- [ ] execute-prp.md reduced to 80-120 lines (from 620)
- [ ] All implementation patterns extracted to `.claude/patterns/`
- [ ] Archon workflow consolidated to single source of truth
- [ ] Report templates created and used by subagents

**Functionality Preservation**:
- [ ] Test PRP generation completes successfully with new structure
- [ ] Test PRP execution completes successfully with new structure
- [ ] All functionality preserved (no regressions)
- [ ] Existing PRPs still executable without modification (backwards compatible)

**Efficiency & Documentation**:
- [ ] Token usage reduced by ~50% per command invocation
- [ ] Documentation updated to reflect new structure
- [ ] Migration path documented for users
- [ ] Cleanup workflow documented

## VALIDATION GATES

### Level 1: Structure Validation
```bash
# Verify new files created
ls -la .claude/patterns/
ls -la .claude/templates/

# Expected: 4 pattern files, 2 template files
```

### Level 2: File Organization Validation
```bash
# Test PRP generation with new structure
/generate-prp prps/test_simple_feature/INITIAL.md

# Verify new structure (not old paths)
ls -la prps/test_simple_feature/test_simple_feature.md      # Main PRP
ls -la prps/test_simple_feature/planning/                   # NOT prps/research/
ls -la prps/test_simple_feature/examples/                   # NOT root examples/

# Expected: All artifacts in prps/test_simple_feature/ directory
# Expected: 5 files in planning/, 2-4 files in examples/

# Verify old paths NOT created
test ! -d prps/research && echo "✅ No global research pollution"
test ! -d examples/test_simple_feature && echo "✅ No root examples pollution"
```

### Level 3: Cleanup Command Validation
```bash
# Test cleanup command
/prp-cleanup test_simple_feature

# Verify archive created
ls -la prps/archive/test_simple_feature/planning/
ls -la prps/archive/test_simple_feature/examples/
ls -la prps/archive/test_simple_feature/execution/

# Verify core files remain
ls -la prps/test_simple_feature/INITIAL.md
ls -la prps/test_simple_feature/test_simple_feature.md

# Expected: Artifacts archived, core PRPs remain
```

### Level 4: Functionality Validation
```bash
# Test PRP execution with new structure
/execute-prp prps/test_simple_feature/test_simple_feature.md

# Verify execution artifacts in correct location
ls -la prps/test_simple_feature/execution/execution-plan.md
ls -la prps/test_simple_feature/execution/validation-report.md

# Expected: PRP executes, artifacts in scoped execution/ directory
```

### Level 5: Token Efficiency Validation
```bash
# Measure command size reduction
wc -l .claude/commands/generate-prp.md  # Target: 80-120 lines
wc -l .claude/commands/execute-prp.md   # Target: 80-120 lines

# Calculate reduction
# Original: 582 + 620 = 1202 lines
# Target: 120 + 100 = 220 lines
# Reduction: 82% fewer lines
```

### Level 6: Regression Testing
```bash
# Test existing PRP execution
/execute-prp prps/EXAMPLE_multi_agent_prp.md

# Expected: Executes without errors (backwards compatible)
```

## ANTI-PATTERNS TO AVOID

**Command Refactoring**:
- ❌ Don't remove context needed by subagents
- ❌ Don't create pattern docs that never get referenced
- ❌ Don't break Archon graceful degradation
- ❌ Don't lose performance metrics/time tracking
- ❌ Don't make patterns too abstract (keep concrete examples)
- ❌ Don't duplicate content between patterns and CLAUDE.md
- ❌ Don't sacrifice readability for brevity
- ❌ Don't remove error handling/recovery logic

**File Organization**:
- ❌ Don't create global shared directories (causes pollution)
- ❌ Don't pollute root directory with generated artifacts
- ❌ Don't mix user-curated examples with generated examples
- ❌ Don't make cleanup difficult (keep artifacts scoped)
- ❌ Don't break backwards compatibility (old PRPs must still work)

---

**Estimated Implementation Time**: 6-9 hours
- Phase 0 (File Organization): 2 hours
- Phases 1-4 (Refactoring): 4-5 hours
- Phase 5 (Testing): 1-2 hours

**Expected Benefits**:
- 59% token reduction per command invocation
- 50% easier maintenance (centralized patterns)
- Improved clarity (separation of concerns)
- Zero root directory pollution from generated artifacts
- Easy cleanup/archival of completed features
- Self-contained feature directories

**Risk Level**: Medium (touching core workflow, but preserving functionality and backwards compatibility)
