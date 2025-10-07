# Task Completion Report Template

<!--
USAGE INSTRUCTIONS:
This template is used for documenting task implementation completion in PRP execution.
It should be filled out after completing each implementation task.

REQUIRED VARIABLES:
- {task_id}: Archon task UUID (if available, otherwise "N/A")
- {task_number}: Task number (e.g., 1, 2, 17)
- {task_name}: Human-readable task name (e.g., "Task 17: Frontend - List View")
- {responsibility}: What this task accomplishes (brief description)
- {status}: COMPLETE | PARTIAL | FAILED - Ready for Review
- {feature_name}: Name of the feature/PRP being implemented
- {files_created}: List of created files with line counts and descriptions
- {files_modified}: List of modified files with changes made
- {core_features}: Bulleted list of main features implemented
- {gotchas_addressed}: Critical gotchas from PRP that were addressed
- {dependencies_completed}: List of completed dependencies verified
- {dependencies_external}: External dependencies required (libraries, etc.)
- {testing_checklist}: Manual testing steps (when applicable)
- {validation_results}: Results of automated validation checks
- {success_metrics}: PRP requirements checklist
- {code_quality_notes}: Quality standards met
- {completion_status}: Overall status (COMPLETE, PARTIAL, BLOCKED)
- {implementation_time}: Approximate time spent (e.g., "~35 minutes")
- {confidence_level}: HIGH | MEDIUM | LOW
- {blockers}: Any blockers encountered (or "None")
- {files_count_created}: Number of files created
- {files_count_modified}: Number of files modified
- {total_lines}: Total lines of code added/modified

EXAMPLE USAGE (Python):
```python
from pathlib import Path

template = Path(".claude/templates/task-completion-report.md").read_text()
report = template.format(
    task_id="8a136a74-32d6-4b2f-bee8-49e662ac47e8",
    task_number=17,
    task_name="Task 17: Frontend - List View",
    responsibility="Filterable table view with sorting",
    status="COMPLETE - Ready for Review",
    feature_name="task_management_ui",
    files_created="""1. **`/path/to/file.tsx`** (452 lines)
   - Main component with filtering
   - URL-based state management""",
    files_modified="""1. **`/path/to/index.ts`**
   - Added: export statement""",
    core_features="""#### 1. Filter Controls
- Status filter dropdown
- URL-based state""",
    gotchas_addressed="""#### Gotcha #1: URL Query Params
**Implementation**: Used useSearchParams()""",
    dependencies_completed="""- Task 13 (useProjectTasks): Hook exists""",
    dependencies_external="""- react-router-dom: Required for routing""",
    testing_checklist="""- [ ] Navigate to page
- [ ] Verify table displays""",
    validation_results="""- Filters update query parameters
- Sorting works correctly""",
    success_metrics="""- [x] Create component
- [x] Add filters""",
    code_quality_notes="""- Comprehensive documentation
- Full TypeScript typing""",
    completion_status="COMPLETE - Ready for Review",
    implementation_time="~35 minutes",
    confidence_level="HIGH",
    blockers="None",
    files_count_created=2,
    files_count_modified=1,
    total_lines=569
)
Path(f"prps/task_management_ui/execution/TASK17_COMPLETION.md").write_text(report)
```
-->

# Task {task_number} Implementation Complete: {task_name}

## Task Information
- **Task ID**: {task_id}
- **Task Name**: {task_name}
- **Responsibility**: {responsibility}
- **Status**: {status}

## Files Created/Modified

### Created Files:
{files_created}

### Modified Files:
{files_modified}

## Implementation Details

### Core Features Implemented

{core_features}

### Critical Gotchas Addressed

{gotchas_addressed}

## Dependencies Verified

### Completed Dependencies:
{dependencies_completed}

### External Dependencies:
{dependencies_external}

## Testing Checklist

### Manual Testing (When Routing Added):
{testing_checklist}

### Validation Results:
{validation_results}

## Success Metrics

**All PRP Requirements Met**:
{success_metrics}

**Code Quality**:
{code_quality_notes}

## Completion Report

**Status**: {completion_status}
**Implementation Time**: {implementation_time}
**Confidence Level**: {confidence_level}
**Blockers**: {blockers}

### Files Created: {files_count_created}
### Files Modified: {files_count_modified}
### Total Lines of Code: ~{total_lines} lines

**Ready for integration and next steps.**
