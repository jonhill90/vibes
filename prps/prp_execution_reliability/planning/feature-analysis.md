# Feature Analysis: PRP Execution Reliability

## INITIAL.md Summary

The `/execute-prp` workflow successfully implements code (100% completion) but inconsistently generates documentation (48% report coverage in task_management_ui). This creates audit gaps and prevents learning from implementation decisions. The goal is to make PRP execution 100% reliable for both implementation AND documentation by enforcing mandatory reporting, standardizing formats, and adding validation gates.

## Core Requirements

### Explicit Requirements

1. **Mandatory Report Generation**
   - 100% of tasks must generate completion reports (currently 48%)
   - Validation gate must block progression if report missing
   - Reports must follow standardized naming: `TASK{n}_COMPLETION.md`

2. **Standardized Templates**
   - Task completion report template (NEW)
   - Updated validation report template (ENHANCE EXISTING)
   - Test generation report template (NEW)

3. **Validation Gates**
   - Check report existence after each task/group
   - Verify report has minimum required sections
   - Provide actionable error messages for missing reports

4. **Path Configuration Fixes**
   - Already fixed: Hardcoded paths without `{feature_name}` variable
   - Ensure all templates use parameterized paths

5. **Documentation Quality Standards**
   - Each task report: files modified, key decisions, challenges, validation status
   - Test reports: coverage %, test count, patterns used
   - Validation reports: all gates tested, pass/fail status, fix attempts

6. **Backward Compatibility**
   - Existing PRPs continue to work
   - Optional: Version detection for legacy PRPs
   - Optional: Retrospective report generation for task_management_ui

### Implicit Requirements

1. **Subagent Accountability**
   - Subagents must understand report generation is NOT optional
   - Reports are part of task completion criteria
   - Clear feedback when reports are missing

2. **Workflow Reliability**
   - Silent failures in documentation generation must be eliminated
   - Execution should fail fast when reports missing (not continue silently)

3. **Developer Experience**
   - Clear progress indicators showing report generation
   - Easy to audit what each subagent did
   - Post-execution summary shows report coverage metrics

4. **Process Improvements**
   - Enable learning from implementation decisions
   - Facilitate post-execution analysis
   - Support auditing and debugging

## Technical Components

### Data Models

**No new data structures required**, but conceptual models include:

1. **Task Completion Report Schema**
   ```yaml
   task_number: int
   task_name: str
   group_number: int
   status: COMPLETE | PARTIAL | FAILED
   duration_minutes: int
   archon_task_id: str (optional)
   files_modified: list[str]
   key_decisions: list[str]
   challenges: list[str]
   validation_checklist: dict[str, bool]
   dependencies: list[int]
   ```

2. **Validation Report Schema**
   ```yaml
   feature_name: str
   status: ALL_PASSED | PARTIAL | FAILED
   gates: list[ValidationGate]
   fix_attempts: list[FixAttempt]
   timestamp: str
   ```

3. **Test Generation Report Schema**
   ```yaml
   feature_name: str
   coverage_percentage: float
   total_tests: int
   test_files: list[str]
   patterns_used: list[str]
   ```

### External Integrations

**None** - This is an internal tooling enhancement. However, it integrates with:

1. **Archon MCP Server** (existing)
   - Task status tracking
   - Project management
   - Already integrated in execute-prp.md

2. **File System** (existing)
   - Template loading from `.claude/templates/`
   - Report writing to `prps/{feature_name}/execution/`

3. **Existing Validation Tools** (existing)
   - ruff, mypy, pytest (no changes)
   - Execute-prp already uses these

### Core Logic

1. **Template Loading System**
   ```python
   def load_template(template_name: str, variables: dict) -> str:
       template_path = f".claude/templates/{template_name}"
       template_content = Read(template_path)
       return template_content.format(**variables)
   ```

2. **Report Validation Gate**
   ```python
   def validate_report_exists(feature_name: str, task_number: int) -> bool:
       report_path = f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md"
       if not file_exists(report_path):
           raise ValidationError(f"Task {task_number} missing report at {report_path}")
       return True

   def validate_report_sections(report_path: str, required_sections: list[str]) -> list[str]:
       report_content = Read(report_path)
       missing = [s for s in required_sections if s not in report_content]
       return missing
   ```

3. **Report Generation Enforcement in Prompts**
   ```python
   # Enhanced prompts for subagents
   implementer_prompt = f'''
   ...existing context...

   CRITICAL OUTPUT REQUIREMENTS:
   1. Implement all files listed in task
   2. Create completion report: prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md
   3. Use template: .claude/templates/task-completion-report.md
   4. Report MUST exist before you finish

   Your task is INCOMPLETE without the completion report.
   '''
   ```

4. **Post-Execution Metrics**
   ```python
   def calculate_report_coverage(feature_name: str, total_tasks: int) -> dict:
       task_reports = glob(f"prps/{feature_name}/execution/TASK*_COMPLETION.md")
       reports_found = len(task_reports)
       coverage_pct = (reports_found / total_tasks) * 100

       return {
           "total_tasks": total_tasks,
           "reports_found": reports_found,
           "coverage_percentage": coverage_pct,
           "missing_tasks": find_missing_task_numbers(total_tasks, task_reports)
       }
   ```

### UI/CLI Requirements

**No new UI** - All changes are to:

1. **Console Output Enhancements**
   - Show report generation progress: "✅ Task 3: Report generated"
   - Final summary includes report coverage: "Reports: 25/25 (100%)"
   - Warning messages for incomplete coverage

2. **Error Messages**
   - Actionable error when report missing
   - Suggest troubleshooting steps
   - Point to expected file path

## Similar Implementations Found in Archon

### 1. Context Engineering Intro - PRP Workflow Patterns
- **Relevance**: 7/10
- **Archon ID**: b8565aff9938938b
- **Key Patterns**:
  - Step-by-step validation in AI workflows
  - Template-based code generation
  - Clear success criteria definition
- **Gotchas**:
  - AI can skip steps if not explicitly required
  - Need validation loops to ensure completion

### 2. MCP Server Configuration Loading (Pydantic)
- **Relevance**: 6/10
- **Archon ID**: c0e629a894699314
- **Key Patterns**:
  - File existence validation before processing
  - Schema validation for configuration files
  - Raising explicit errors when files missing
- **Gotchas**:
  - Always check file existence first
  - Provide helpful error messages with file paths

### 3. Agent Workflow Validation (Kubechain)
- **Relevance**: 5/10
- **Archon ID**: e9eb05e2bf38f125
- **Key Patterns**:
  - Quality gates in development workflows
  - Mock generation validation
  - Comprehensive testing requirements
- **Gotchas**:
  - Without enforcement, optional steps get skipped
  - Need explicit validation after each phase

## Recommended Technology Stack

**No new technologies required** - Leveraging existing stack:

### Template System
- **Format**: Markdown with placeholder variables
- **Location**: `.claude/templates/`
- **Variable substitution**: Python string `.format()` or f-strings
- **Existing precedent**: `.claude/templates/validation-report.md` already exists

### Validation Logic
- **Language**: Python (inline in execute-prp.md workflow)
- **File operations**: Read(), Write(), Glob() tools
- **Error handling**: Python exceptions with ValidationError

### Report Storage
- **Format**: Markdown files
- **Naming convention**: `TASK{n}_COMPLETION.md` (standardized)
- **Location**: `prps/{feature_name}/execution/`
- **Already established**: Other reports already use this location

### Workflow Integration
- **Framework**: Task() subagent invocations
- **Pattern**: `.claude/patterns/quality-gates.md` (validation loops)
- **Archon integration**: Existing MCP server calls

## Assumptions Made

### 1. Template Storage Location
- **Assumption**: All templates in `.claude/templates/` directory
- **Reasoning**: Existing templates already use this location (validation-report.md, completion-report.md)
- **Source**: Codebase pattern analysis

### 2. Report Naming Convention
- **Assumption**: Standardize on `TASK{n}_COMPLETION.md` format
- **Reasoning**:
  - Currently 6 different naming patterns exist (chaos)
  - COMPLETION is most descriptive (vs COMPLETE, NOTES, REPORT)
  - Consistent with existing validation-report.md naming
- **Source**: INITIAL.md explicit requirement + MISSING_REPORTS_ANALYSIS.md evidence

### 3. Validation Gate Placement
- **Assumption**: Validate after each task group completes (not after individual tasks in parallel)
- **Reasoning**:
  - Parallel tasks run simultaneously (can't validate mid-execution)
  - Group completion is natural validation boundary
  - Already established in execute-prp.md structure
- **Source**: Execute-prp.md Phase 2 analysis

### 4. Required Report Sections
- **Assumption**: Minimum required sections are:
  - "Implementation Summary"
  - "Files Created/Modified"
  - "Validation"
- **Reasoning**: These provide minimum auditability (what was done, where, was it validated)
- **Source**: INITIAL.md template specification + best practices

### 5. Backward Compatibility Strategy
- **Assumption**: Use lenient validation for legacy PRPs (no enforcement)
- **Reasoning**:
  - Don't break existing workflows
  - New PRPs get strict enforcement
  - Optional version detection in PRP header
- **Source**: INITIAL.md explicit requirement

### 6. Error Handling Approach
- **Assumption**: Fail fast with actionable errors (don't continue silently)
- **Reasoning**:
  - Current issue is silent failures (reports missing but execution continues)
  - Failing fast prevents 13/25 tasks missing reports
  - Error messages guide resolution
- **Source**: MISSING_REPORTS_ANALYSIS root cause analysis

### 7. Subagent Prompt Enhancement
- **Assumption**: Adding "CRITICAL" and "INCOMPLETE without report" language will improve compliance
- **Reasoning**:
  - Current prompts don't emphasize report importance
  - Subagents need explicit understanding this is mandatory
  - Already proven pattern in prp-exec-validator agent
- **Source**: Subagent definition analysis + INITIAL.md Issue 1

### 8. Report Coverage Metric
- **Assumption**: Display "Reports: X/Y (Z%)" in final summary
- **Reasoning**:
  - Makes documentation reliability visible
  - Encourages 100% coverage
  - Easy to calculate from glob results
- **Source**: INITIAL.md developer experience requirements

## Success Criteria

**From INITIAL.md (Explicit)**:

### Execution Reliability
- [ ] 100% of tasks generate completion reports (verified programmatically)
- [ ] All reports follow standardized naming: `TASK{n}_COMPLETION.md`
- [ ] All reports use standardized template with required sections
- [ ] Validation gate blocks progression if report missing

### Documentation Quality
- [ ] Each task report includes: files modified, key decisions, challenges, validation status
- [ ] Test generation reports include: coverage %, test count, patterns used
- [ ] Validation reports include: all gates tested, pass/fail status, fix attempts
- [ ] Integration reports include: end-to-end test results, deployment verification

### Developer Experience
- [ ] Execute-prp provides clear progress indicators showing report generation
- [ ] Failures include actionable error messages pointing to missing reports
- [ ] Post-execution summary shows report coverage (X/Y tasks documented)
- [ ] Easy to audit what each subagent did via standardized reports

### Backward Compatibility
- [ ] Existing PRPs continue to work (don't break previous patterns)
- [ ] Optional: Regenerate missing reports for task_management_ui retrospectively

**Inferred Success Criteria**:
- [ ] Template files are complete and usable by subagents
- [ ] Validation gate catches missing reports 100% of time
- [ ] Error messages are actionable (include paths, troubleshooting steps)
- [ ] Report coverage metric calculates correctly
- [ ] Parallel execution still works (no new bottlenecks)

## Next Steps for Downstream Agents

### Codebase Researcher (Phase 2a)
**Focus Areas**:
1. **Search for existing template patterns**
   - Find all files in `.claude/templates/`
   - Analyze structure of validation-report.md and completion-report.md
   - Identify variable substitution patterns used

2. **Search for validation gate patterns**
   - Find all uses of `file_exists()` or equivalent checks
   - Look for error handling in execute-prp.md
   - Find ValidationError patterns in codebase

3. **Search for report generation patterns**
   - Find how other reports are created (glob patterns)
   - Look for report summary generation logic
   - Find metric calculation examples

**Specific Searches**:
- Grep: `glob.*execution.*\.md` to find existing report patterns
- Grep: `ValidationError|raise.*Error` to find error handling patterns
- Read: All files in `.claude/templates/` directory
- Read: `.claude/patterns/quality-gates.md` for validation patterns

### Documentation Hunter (Phase 2b)
**Focus Areas**:
1. **Template system documentation**
   - Find best practices for Markdown template design
   - Look for variable substitution documentation (Python format strings)

2. **Validation patterns documentation**
   - Find documentation on quality gates pattern
   - Look for error handling best practices

3. **PRP workflow documentation**
   - Find documentation on execute-prp.md structure
   - Look for subagent prompt design guidelines

**Specific Documentation**:
- Look for existing documentation on `.claude/patterns/quality-gates.md`
- Find examples of prompt engineering for mandatory requirements
- Search for file validation patterns in Python

### Example Curator (Phase 2c)
**Focus Areas**:
1. **Extract template examples**
   - Existing validation-report.md template
   - Existing completion-report.md template
   - Find examples of good markdown templates

2. **Extract validation gate examples**
   - Find examples from execute-prp.md validation logic
   - Look for error handling examples
   - Find report existence checking patterns

3. **Extract report generation examples**
   - Find existing report generation code
   - Look for glob pattern usage
   - Find metric calculation examples

**Specific Examples to Extract**:
- Template: `.claude/templates/validation-report.md` (reference for new templates)
- Validation: Execute-prp.md Phase 5 validation logic
- Error handling: Any existing ValidationError usage
- Report patterns: Task reports from task_management_ui (even inconsistent ones show what's needed)

### Gotcha Detective (Phase 2d)
**Focus Areas**:
1. **Template rendering gotchas**
   - Path traversal vulnerabilities (already addressed in security-validation.md)
   - Variable substitution failures (missing variables)
   - Markdown formatting issues

2. **Validation gate gotchas**
   - Race conditions in parallel execution
   - False positives (reports in wrong location)
   - File system timing issues (report not yet written when checked)

3. **Subagent compliance gotchas**
   - Subagents ignoring "optional" requirements
   - Reports created in wrong location (already happened)
   - Reports with different naming (already happened - 6 patterns found)

**Specific Investigations**:
- Review MISSING_REPORTS_ANALYSIS.md for actual failures
- Check security-validation.md for path validation patterns
- Look for race condition handling in parallel execution
- Find examples of subagents not following instructions

## Evidence from Analysis

### Current State (task_management_ui PRP)
- **Implementation**: 25/25 tasks completed ✅
- **Reports**: 12/25 reports generated (48%) ❌
- **Impact**: Cannot audit 13 tasks, no learning from those implementations

### Root Causes Identified
1. **No standardized template** → 6 different naming patterns found
2. **No validation gate** → Silent failures, execution continues despite missing reports
3. **Incorrect path instructions** → Reports saved in wrong directory (FIXED 2025-10-06)
4. **No subagent accountability** → Subagents don't understand reports are mandatory

### Validation from Existing Patterns
- **quality-gates.md pattern**: Already exists, proves validation loops work
- **archon-workflow.md pattern**: Already exists, proves MCP integration works
- **parallel-subagents.md pattern**: Already exists, proves parallel execution works
- **Templates**: validation-report.md and completion-report.md already exist

### Integration Points
- **Phase 0 (Setup)**: No changes needed (paths already fixed)
- **Phase 1 (Analysis)**: No changes needed
- **Phase 2 (Implementation)**: ADD validation gates after task groups
- **Phase 3 (Test Gen)**: ADD report requirement to prompt, ADD validation gate
- **Phase 4 (Validation)**: ADD report requirement to prompt, ADD validation gate
- **Phase 5 (Completion)**: ADD report coverage metrics

## Implementation Complexity Assessment

### Low Complexity (Easy)
- Creating markdown templates (1-2 hours)
- Adding validation gate logic (file existence checks) (1 hour)
- Updating subagent prompts with "CRITICAL" language (30 min)
- Adding report coverage metrics to final summary (30 min)

### Medium Complexity (Moderate)
- Template variable substitution system (if not using simple format()) (2-3 hours)
- Error message design (actionable, helpful) (1-2 hours)
- Testing validation gates with edge cases (2-3 hours)

### High Complexity (Challenging)
- **None identified** - This is primarily workflow and template work

### Total Estimated Effort
- **Core implementation**: 4-6 hours
- **Testing & validation**: 2-3 hours
- **Documentation**: 1-2 hours
- **Optional retrospective report generation**: 3-4 hours
- **TOTAL**: 7-11 hours (medium complexity overall)

## Risk Mitigation Strategies

### Risk 1: Subagents Still Don't Generate Reports
- **Mitigation**: Make prompts extremely explicit ("INCOMPLETE without report")
- **Mitigation**: Validation gate catches missing reports immediately (fail fast)
- **Mitigation**: Error message includes exact path expected
- **Fallback**: Manual report generation if validation fails repeatedly

### Risk 2: Breaking Existing PRPs
- **Mitigation**: Add version detection (optional, lenient mode for legacy)
- **Mitigation**: Test with task_management_ui PRP (already executed)
- **Mitigation**: Validation gates only activate for new PRPs
- **Fallback**: Disable enforcement via flag if issues arise

### Risk 3: Performance Degradation
- **Mitigation**: File existence checks are O(1) operations (milliseconds)
- **Mitigation**: No additional subagent invocations (same workflow)
- **Mitigation**: Validation runs after groups (not per-task in parallel)
- **Expected**: <1% performance impact

### Risk 4: Template Complexity
- **Mitigation**: Keep templates simple (Markdown + basic variables)
- **Mitigation**: Use Python f-strings or .format() (well-established)
- **Mitigation**: Provide clear examples in each template
- **Fallback**: Simplify template if subagents struggle

### Risk 5: Report Clutter
- **Mitigation**: All reports in single directory `prps/{feature}/execution/`
- **Mitigation**: Clear naming convention `TASK{n}_COMPLETION.md`
- **Mitigation**: Can add to .gitignore if desired (not recommended)
- **Expected**: 25-30 files per PRP (manageable)

## Open Questions for PRP Assembly

1. **Version Detection**: Should we implement PRP version detection for backward compatibility?
   - **Recommendation**: Optional for now, add if legacy PRPs break

2. **Retrospective Reports**: Should we regenerate missing reports for task_management_ui?
   - **Recommendation**: Optional stretch goal, not required for success

3. **Template Format**: Should we use f-strings, .format(), or template engine?
   - **Recommendation**: f-strings (simplest, already used in codebase)

4. **Section Validation**: How strict should section validation be?
   - **Recommendation**: Check for required sections, warn if missing, don't fail

5. **Report Coverage Threshold**: Should we require 100% or allow partial?
   - **Recommendation**: Require 100%, fail if any missing (fail fast principle)

## Files to Create/Modify

### New Template Files (3)
1. `.claude/templates/task-completion-report.md` - NEW
2. `.claude/templates/test-generation-report.md` - NEW
3. `.claude/templates/validation-report.md` - ENHANCE (already exists)

### Workflow Updates (1)
1. `.claude/commands/execute-prp.md` - MODIFY
   - Phase 2: Add validation gates after task groups
   - Phase 3: Add report requirement + validation
   - Phase 4: Add report requirement + validation
   - Phase 5: Add report coverage metrics

### Optional (If Time Permits)
1. `.claude/commands/regenerate-prp-reports.md` - NEW (retrospective tool)
2. `.claude/patterns/report-validation.md` - NEW (reusable pattern)

## Architectural Decisions

### Decision 1: Fail Fast vs Continue
- **Choice**: Fail fast when reports missing
- **Rationale**: Silent failures caused 48% report loss, failing fast prevents this
- **Alternative Rejected**: Continue with warnings (same problem as current state)

### Decision 2: Template Location
- **Choice**: `.claude/templates/` directory
- **Rationale**: Already established pattern, easy to discover
- **Alternative Rejected**: Inline templates in execute-prp.md (harder to maintain)

### Decision 3: Naming Convention
- **Choice**: `TASK{n}_COMPLETION.md` (no underscores, consistent format)
- **Rationale**: Most descriptive, easy to glob, alphabetically sorted
- **Alternative Rejected**: `TASK_{n}_REPORT.md` (less descriptive)

### Decision 4: Validation Timing
- **Choice**: After each task group completes
- **Rationale**: Natural boundary, doesn't interfere with parallelism
- **Alternative Rejected**: After each individual task (breaks parallelism)

### Decision 5: Error Message Design
- **Choice**: Include task number, expected path, actionable steps
- **Rationale**: Makes debugging easy, clear resolution path
- **Alternative Rejected**: Generic error messages (not helpful)

## Success Indicators

### Immediate (This PRP)
- ✅ Templates created and committed
- ✅ Execute-prp.md updated with validation gates
- ✅ Test PRP generates 100% reports
- ✅ Validation gate catches missing reports

### Short-term (Next PRP Execution)
- ✅ First real PRP achieves 100% report coverage
- ✅ No reports missing
- ✅ Audit trail complete
- ✅ Learning from implementation decisions enabled

### Long-term (Process Improvement)
- ✅ All future PRPs achieve 100% report coverage
- ✅ Documentation reliability matches implementation reliability
- ✅ Post-execution analysis becomes standard practice
- ✅ Knowledge accumulation from PRP executions
