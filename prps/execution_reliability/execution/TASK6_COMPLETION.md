# Task 6 Implementation Complete: Update Subagent Prompts with Mandatory Language

## Task Information
- **Task ID**: N/A
- **Task Name**: Task 6: Update Subagent Prompts with Mandatory Language
- **Responsibility**: Make report generation explicitly mandatory in prompts
- **Status**: COMPLETE - Ready for Review

## Files Created/Modified

### Created Files:
None - this task modified existing files only.

### Modified Files:
1. **`.claude/commands/execute-prp.md`** (217 lines added)
   - Enhanced prp-exec-implementer prompt (parallel mode) - lines 259-311
   - Enhanced prp-exec-implementer prompt (sequential mode) - lines 345-395
   - Enhanced prp-exec-test-generator prompt - lines 426-475
   - Enhanced prp-exec-validator prompt - lines 483-536
   - Added CRITICAL OUTPUT REQUIREMENTS sections to all 4 subagent prompts
   - Added visual separators (═══, ⚠️) to highlight mandatory requirements
   - Added exact report paths with standardized naming
   - Added validation consequences and enforcement language

## Implementation Details

### Core Features Implemented

#### 1. Parallel Implementer Prompt Enhancement (Lines 259-311)
- Added structured **CONTEXT** section with all task parameters
- Added **CRITICAL OUTPUT REQUIREMENTS** section with visual separators
- Specified exact report path: `prps/{feature_name}/execution/TASK{task['number']}_COMPLETION.md`
- Listed all required report sections (Implementation Summary, Files, Key Decisions, Challenges, Validation)
- Added "YOUR TASK IS INCOMPLETE WITHOUT THE COMPLETION REPORT" warning
- Listed 4 reasons why report is mandatory (auditing, learning, debugging, validation gates)
- Added **VALIDATION** section explaining immediate validation after completion
- Added explicit warning: "If report is missing, you will receive a VALIDATION ERROR"
- Enhanced **WORKFLOW** section including completion report as step 5

#### 2. Sequential Implementer Prompt Enhancement (Lines 345-395)
- Applied identical enhancement pattern as parallel mode
- Ensured consistency across both execution modes
- Same structured sections: CONTEXT, CRITICAL OUTPUT REQUIREMENTS, VALIDATION, WORKFLOW
- Same exact report path specification
- Same mandatory language and visual separators

#### 3. Test Generator Prompt Enhancement (Lines 426-475)
- Added structured **CONTEXT** section
- Added **CRITICAL OUTPUT REQUIREMENTS** for test-generation-report.md
- Specified exact report path: `prps/{feature_name}/execution/test-generation-report.md`
- Listed test-specific required sections (Test Summary, Coverage Analysis, Patterns, Edge Cases)
- Added "YOUR TASK IS INCOMPLETE WITHOUT THE TEST GENERATION REPORT" warning
- Listed 4 reasons why report is mandatory for test generation
- Added **VALIDATION** section with 5 validation checks (test files, pytest pass, coverage ≥70%, report exists, sections complete)
- Enhanced **WORKFLOW** section to include test-generation-report.md as final step

#### 4. Validator Prompt Enhancement (Lines 483-536)
- Added structured **CONTEXT** section
- Added **CRITICAL OUTPUT REQUIREMENTS** for validation-report.md
- Specified exact report path: `prps/{feature_name}/execution/validation-report.md`
- Listed validation-specific required sections (Validation Levels, Iteration Tracking, Error Analysis, Fix Applications, Next Steps)
- Added "YOUR TASK IS INCOMPLETE WITHOUT THE VALIDATION REPORT" warning
- Listed 4 reasons why report is mandatory for validation
- Added **VALIDATION** section with 5 validation checks (all levels attempted, iteration loop, report exists, sections complete, tracking table)
- Enhanced **WORKFLOW** section to include validation-report.md with complete tracking

### Critical Gotchas Addressed

#### Gotcha #4: Subagents Ignoring Mandatory Requirements (PRP lines 333-376)
**Problem**: 48% report coverage in task_management_ui execution (13/25 tasks produced no reports)
**Root Cause**: Vague prompts like "Consider creating a completion report" treated as optional
**Implementation**:
- Used "CRITICAL", "MANDATORY", "INCOMPLETE without" language throughout
- Visual separators (═══════════, ⚠️) highlight non-negotiable requirements
- Exact path specification prevents naming inconsistencies
- Positioned critical requirements early in prompt (after CONTEXT, before detailed workflow)
- Repeated mandatory nature multiple times in different sections
- Explicit validation consequences: "you will receive a VALIDATION ERROR"

#### Gotcha from Context Engineering Documentation (PRP lines 130-140)
**Pattern**: Anthropic effective context engineering principles applied
**Implementation**:
- Structured sections with clear headers (CONTEXT, CRITICAL OUTPUT REQUIREMENTS, VALIDATION, WORKFLOW)
- Output cues positioned prominently (visual separators make them impossible to miss)
- Format specification explicit (exact paths, required sections listed)
- Critical requirements positioned early and repeated
- Action-oriented language: "YOUR TASK IS INCOMPLETE WITHOUT"

#### Report Naming Standardization (PRP lines 460-497)
**Problem**: 6 different naming patterns in task_management_ui (TASK5_IMPLEMENTATION_NOTES.md, TASK_17_COMPLETION.md, TASK_18_COMPLETE.md, etc.)
**Implementation**:
- Exact path specification in all prompts: `TASK{task['number']}_COMPLETION.md`
- No underscore before number (TASK17, not TASK_17)
- COMPLETION not COMPLETE, NOTES, or REPORT
- Standardized across all 4 subagent types

#### Path Specification Consistency
**Implementation**:
- All paths use exact same format: `prps/{feature_name}/execution/TASK{task['number']}_TYPE.md`
- Template paths specified: `.claude/templates/task-completion-report.md`, etc.
- No ambiguity in path construction
- Feature name from validated extract_feature_name() function (security validated in Phase 0)

## Dependencies Verified

### Completed Dependencies:
- **Task 1** (Create Task Completion Report Template): Template exists at `.claude/templates/task-completion-report.md` (verified 139 lines)
- **Task 5** (Add Validation Gates to Execute-PRP Phase 2): Validation gates exist in execute-prp.md lines 269-290 and 397-418 (verified)
- Validation gate functions exist in Phase 0: `validate_report_exists()`, `format_missing_report_error()` (verified lines 112-153)

### External Dependencies:
None - this task modifies only markdown documentation (no runtime dependencies)

## Testing Checklist

### Manual Validation Performed:
- [x] Verified all 4 subagent prompts updated (implementer parallel, implementer sequential, test-generator, validator)
- [x] Confirmed visual separators present (12 separator lines = 3 per subagent × 4)
- [x] Confirmed "CRITICAL OUTPUT REQUIREMENTS" headers present (4 occurrences, one per subagent)
- [x] Confirmed "YOUR TASK IS INCOMPLETE WITHOUT" warnings present (4 occurrences)
- [x] Verified exact report paths specified in all prompts
- [x] Verified required sections listed for each report type
- [x] Verified validation consequences explained in all prompts
- [x] Verified WORKFLOW sections updated to include report generation
- [x] Checked file line count: 599 lines total (was 382, added 217 lines)

### Validation Results:
- **Line Count**: 599 lines (confirmed via `wc -l`)
- **Visual Separators**: 12 occurrences (3 per subagent × 4 = correct)
- **Critical Headers**: 4 occurrences (one per subagent type = correct)
- **Mandatory Warnings**: 4 occurrences (one per subagent type = correct)
- **Markdown Syntax**: Valid (no linting errors expected - markdown documentation)
- **Pattern Consistency**: All 4 prompts follow same structure (CONTEXT → CRITICAL OUTPUT REQUIREMENTS → VALIDATION → WORKFLOW)

## Success Metrics

**All PRP Requirements Met**:
- [x] All 4 subagent prompts updated (implementer ×2, test-generator, validator)
- [x] "CRITICAL" and "MANDATORY" language used throughout
- [x] Exact report paths specified for each subagent type
- [x] Visual separators (═══, ⚠️) highlight requirements
- [x] "INCOMPLETE without" language used
- [x] Validation consequences explained
- [x] Standardized naming enforced: TASK{n}_COMPLETION.md (no underscore before number)
- [x] Template paths referenced: `.claude/templates/task-completion-report.md`, etc.
- [x] Required sections listed for each report type
- [x] Validation checks enumerated (4-5 checks per subagent)

**Code Quality**:
- Consistent structure across all 4 subagent prompts
- Clear visual hierarchy with separators and emojis
- Actionable language: "YOUR TASK IS INCOMPLETE WITHOUT"
- Specific consequences: "you will receive a VALIDATION ERROR"
- Multiple reinforcement: requirements stated in 3 different sections (header, body, validation)
- Exact paths prevent ambiguity
- Template references provide clear guidance

## Completion Report

**Status**: COMPLETE - Ready for Review
**Implementation Time**: ~25 minutes
**Confidence Level**: HIGH

### Reasoning for High Confidence:
1. **Pattern Followed**: Applied exact pattern from PRP Gotcha #4 (lines 333-376) and Anthropic context engineering principles
2. **Validation Complete**: All 4 subagent types updated and verified via grep
3. **Consistency Verified**: All prompts follow identical structure (CONTEXT, CRITICAL OUTPUT REQUIREMENTS, VALIDATION, WORKFLOW)
4. **Dependencies Met**: Task 1 template exists, Task 5 validation gates in place
5. **No Ambiguity**: Exact paths specified, standardized naming enforced, template paths referenced
6. **Multiple Reinforcement**: Mandatory nature stated 3 times in different ways per prompt
7. **Visual Hierarchy**: Separators and emojis make requirements unmissable
8. **Quantitative Validation**: Line counts, grep counts all match expected values

**Blockers**: None

### Files Created: 0
### Files Modified: 1
### Total Lines of Code: ~217 lines added

**Ready for integration and next steps.**

---

## Next Steps

This task (Task 6) completes the prompt enhancement requirements. The updated prompts will work in conjunction with:

1. **Task 1** (template) - Provides the structure subagents must follow
2. **Task 5** (validation gates) - Enforces report existence immediately after task completion
3. **Future executions** - All PRP executions from now on will have enhanced prompts with mandatory language

**Expected Impact**:
- Report coverage should increase from 48% to close to 100% in future PRP executions
- Subagents will understand reports are non-negotiable
- Validation gates will catch any missing reports immediately
- Standardized naming will eliminate the 6 different naming patterns observed in task_management_ui

**Testing Recommendation**:
When Task 8 (Test PRP Execution with Validation Gates) runs, these enhanced prompts will be tested end-to-end to verify they produce the desired effect (100% report coverage).
