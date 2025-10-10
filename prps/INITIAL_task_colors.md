name: "INITIAL: Add Custom Colors to Task Manager"
description: |

## Goal
Add the ability for users to assign custom colors to tasks in the Archon task manager, making it easier to visually organize and prioritize work.

## Why
- **Visual Organization**: Colors provide instant visual categorization of tasks beyond status columns
- **User Customization**: Allow users to develop their own color-coding system (urgency, task type, team, etc.)
- **Enhanced UX**: Current system only uses priority-based left border colors - expand to full task customization
- **Existing Pattern**: Task cards already support `featureColor` for feature tags - extend this to the entire task

## What
Enable users to:
1. Choose a color for any task via a color picker in the task edit modal
2. See the task color reflected in the task card (background tint, border, or accent)
3. Persist color choices to the database
4. Remove/reset colors back to default styling
5. Optionally see color in task lists and other views

### Success Criteria
- [ ] Users can select a color from a color picker when editing a task
- [ ] Selected color is stored in the database and persists across sessions
- [ ] Task cards display the selected color in a visually appealing way
- [ ] Color can be cleared/reset to default
- [ ] Color picker UI is intuitive and matches the existing Tron-inspired glassmorphism design
- [ ] No performance degradation with colored tasks

## Context

### Documentation & References
```yaml
- file: infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx
  why: Current task card implementation with glassmorphism styling and featureColor support (line 174-182)

- file: infra/archon/archon-ui-main/src/features/projects/tasks/utils/task-styles.tsx
  why: Existing color utilities for task styling (priority colors, assignee colors, column colors)

- file: infra/archon/archon-ui-main/src/features/projects/tasks/types/task.ts
  why: Task type definition - already has optional featureColor field (line 70, 82, 95)

- file: infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx
  why: Modal where color picker should be added

- pattern: Radix UI primitives
  location: infra/archon/archon-ui-main/src/features/ui/primitives/
  why: Use existing UI primitives for consistent design

- pattern: TanStack Query mutations
  location: infra/archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts
  why: Follow existing mutation patterns for updating tasks
```

### Current Structure
```bash
infra/archon/
├── archon-ui-main/src/features/projects/tasks/
│   ├── components/
│   │   ├── TaskCard.tsx                 # Displays task with color
│   │   ├── TaskEditModal.tsx            # Where color picker will go
│   │   └── TaskCardActions.tsx          # Task actions
│   ├── hooks/
│   │   ├── useTaskQueries.ts            # Query hooks & mutations
│   │   └── useTaskActions.ts            # Task business logic
│   ├── services/
│   │   └── taskService.ts               # API calls
│   ├── types/
│   │   └── task.ts                      # Task types (has featureColor)
│   └── utils/
│       └── task-styles.tsx              # Color utilities
└── python/src/server/
    ├── api_routes/
    │   └── projects_api.py              # Task API endpoints
    └── services/
        └── projects/task_service.py      # Task business logic
```

### Desired Structure
```bash
infra/archon/
├── archon-ui-main/src/features/projects/tasks/
│   ├── components/
│   │   ├── TaskCard.tsx                 # MODIFIED: Apply task color styling
│   │   ├── TaskEditModal.tsx            # MODIFIED: Add color picker
│   │   ├── TaskColorPicker.tsx          # NEW: Color picker component
│   │   └── TaskCardActions.tsx          # (no changes)
│   ├── hooks/
│   │   └── useTaskQueries.ts            # MODIFIED: Add taskColor to mutations
│   ├── services/
│   │   └── taskService.ts               # MODIFIED: Include taskColor in API calls
│   └── types/
│       └── task.ts                      # MODIFIED: Add taskColor field
└── python/
    └── (database already supports flexible JSON - no schema changes needed)
```

### Known Gotchas & Patterns
```typescript
// PATTERN: Use existing glassmorphism styling from TaskCard.tsx
// The card uses: "bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30"
// New color should integrate with this, not replace it

// PATTERN: Color picker should use Radix UI primitives
// See: infra/archon/archon-ui-main/src/features/ui/primitives/

// PATTERN: Follow existing mutation pattern from useTaskQueries.ts
// Use optimistic updates with createOptimisticEntity/replaceOptimisticEntity

// CRITICAL: Task type already has featureColor (for feature tags)
// Consider: Should we rename to taskColor and use it for both? Or add separate field?
// Decision: Add taskColor field separate from featureColor
//   - featureColor: For the feature tag badge (line 174-182 in TaskCard.tsx)
//   - taskColor: For the overall task card styling

// CRITICAL: Database schema uses archon_tasks table
// The table likely uses JSONB or flexible fields - verify taskColor can be added
// Backend: python/src/server/services/projects/task_service.py

// PATTERN: Color should work with both light and dark modes
// Use alpha channel for subtlety: background-color with /20 or /30 opacity
// See existing pattern: backgroundColor: `${task.featureColor}20`
```

## Implementation

### Task List
```yaml
Task 1: Add taskColor field to Task type
ACTION: Update Task interface to include optional taskColor field
FILES:
  - infra/archon/archon-ui-main/src/features/projects/tasks/types/task.ts
PATTERN: Follow existing featureColor pattern (lines 70, 82, 95)

Task 2: Create TaskColorPicker component
ACTION: Build a color picker component using Radix UI primitives
FILES:
  - infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskColorPicker.tsx (NEW)
PATTERN:
  - Use Radix UI Popover for picker UI
  - Provide preset colors + custom color input
  - Match glassmorphism design from existing components
  - Include "Clear Color" option

Task 3: Integrate color picker into TaskEditModal
ACTION: Add color picker to the task edit modal UI
FILES:
  - infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx
PATTERN: Add field similar to feature/assignee/priority fields

Task 4: Update TaskCard to display taskColor
ACTION: Apply taskColor to task card styling (background tint, border glow, or accent)
FILES:
  - infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx
PATTERN:
  - Use conditional styling similar to featureColor badge (lines 174-182)
  - Apply color with alpha transparency for glassmorphism effect
  - Ensure works in both light and dark modes

Task 5: Update mutation hooks to include taskColor
ACTION: Modify create/update task mutations to send taskColor
FILES:
  - infra/archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts
  - infra/archon/archon-ui-main/src/features/projects/tasks/services/taskService.ts
PATTERN: Follow existing mutation patterns with optimistic updates

Task 6: Verify backend supports taskColor
ACTION: Ensure backend accepts and persists taskColor field
FILES:
  - infra/archon/python/src/server/services/projects/task_service.py
  - infra/archon/python/src/server/api_routes/projects_api.py
PATTERN: Backend uses flexible schema - should accept new field automatically

Task 7: Add tests for color functionality
ACTION: Write tests for color picker and task color display
FILES:
  - infra/archon/archon-ui-main/src/features/projects/tasks/components/tests/TaskColorPicker.test.tsx (NEW)
  - infra/archon/archon-ui-main/src/features/projects/tasks/components/tests/TaskCard.test.tsx
PATTERN: Follow existing test patterns in tasks/components/tests/
```

### Key Implementation Details
```typescript
// Task 2: TaskColorPicker Component Structure
interface TaskColorPickerProps {
  value?: string;              // Current color (hex format)
  onChange: (color: string | undefined) => void;
  label?: string;
}

const PRESET_COLORS = [
  "#ef4444", // red
  "#f97316", // orange
  "#eab308", // yellow
  "#22c55e", // green
  "#06b6d4", // cyan
  "#3b82f6", // blue
  "#8b5cf6", // purple
  "#ec4899", // pink
];

// Task 4: TaskCard color styling
// Option A: Background tint with border accent
<div
  className={`${cardBaseStyles} ...`}
  style={{
    backgroundColor: taskColor ? `${taskColor}10` : undefined,
    borderColor: taskColor ? `${taskColor}50` : undefined,
  }}
>

// Option B: Left border (stronger accent)
<div
  className="absolute left-0 top-0 bottom-0 w-1 rounded-l-lg"
  style={{
    backgroundColor: taskColor || getOrderColor(task.task_order),
    boxShadow: taskColor ? `0 0 10px ${taskColor}70` : undefined,
  }}
/>

// Task 5: Mutation with taskColor
export function useUpdateTask() {
  // ... existing pattern ...
  mutationFn: ({ taskId, updates }: { taskId: string; updates: UpdateTaskRequest }) =>
    taskService.updateTask(taskId, updates), // updates includes taskColor

  onMutate: async ({ taskId, updates }) => {
    // Optimistic update includes taskColor
    queryClient.setQueryData(taskKeys.lists(), (old: Task[] = []) =>
      old.map(task => task.id === taskId ? { ...task, ...updates } : task)
    );
  },
}
```

### Integration Points
```yaml
DATABASE:
  - Table: archon_tasks
  - Field: taskColor (string, optional)
  - Action: No migration needed - backend accepts dynamic fields

FRONTEND TYPES:
  - File: infra/archon/archon-ui-main/src/features/projects/tasks/types/task.ts
  - Add: taskColor?: string to Task, CreateTaskRequest, UpdateTaskRequest

API:
  - Endpoint: PUT /api/projects/{project_id}/tasks/{task_id}
  - Payload: Include taskColor in request body
  - No route changes needed

UI COMPONENTS:
  - Radix UI Popover: For color picker dropdown
  - Color input: HTML5 color input for custom colors
  - Preset swatches: Clickable color buttons
```

## Validation

### Level 1: Syntax & Style
```bash
# Frontend checks
cd infra/archon/archon-ui-main
npm run biome:fix
npm run biome
npx tsc --noEmit

# Expected: No errors
```

### Level 2: Unit Tests
```typescript
// Test: Color picker component
describe("TaskColorPicker", () => {
  test("renders preset colors", () => {
    render(<TaskColorPicker value={undefined} onChange={vi.fn()} />);
    expect(screen.getAllByRole("button")).toHaveLength(PRESET_COLORS.length + 1); // +1 for clear
  });

  test("calls onChange with selected color", () => {
    const onChange = vi.fn();
    render(<TaskColorPicker value={undefined} onChange={onChange} />);
    fireEvent.click(screen.getByLabelText("Select color #ef4444"));
    expect(onChange).toHaveBeenCalledWith("#ef4444");
  });

  test("clears color when clear button clicked", () => {
    const onChange = vi.fn();
    render(<TaskColorPicker value="#ef4444" onChange={onChange} />);
    fireEvent.click(screen.getByText("Clear Color"));
    expect(onChange).toHaveBeenCalledWith(undefined);
  });
});

// Test: TaskCard displays color
describe("TaskCard with color", () => {
  test("applies taskColor styling when present", () => {
    const task = { ...mockTask, taskColor: "#ef4444" };
    render(<TaskCard task={task} {...defaultProps} />);
    const card = screen.getByRole("button");
    expect(card.style.backgroundColor).toContain("#ef4444");
  });

  test("uses default styling when no taskColor", () => {
    const task = { ...mockTask, taskColor: undefined };
    render(<TaskCard task={task} {...defaultProps} />);
    // Verify no custom color styling applied
  });
});
```

```bash
# Run tests
npm run test src/features/projects/tasks

# Expected: All tests pass
```

### Level 3: Integration Test
```bash
# Manual testing checklist:
1. Open task manager in browser
2. Click edit on any task
3. Verify color picker appears in modal
4. Select a preset color → verify preview in modal
5. Save task → verify color appears on task card
6. Verify color works in both light and dark modes
7. Clear color → verify task returns to default styling
8. Create new task with color → verify color persists
9. Drag colored task between columns → verify color maintained

# Expected: All interactions work smoothly with no visual glitches
```

## Final Checklist
- [ ] TaskColorPicker component created and styled
- [ ] Color picker integrated into TaskEditModal
- [ ] TaskCard displays task colors correctly
- [ ] Colors work in both light and dark modes
- [ ] Color persists to database via API
- [ ] Clear/reset color functionality works
- [ ] All tests pass
- [ ] No TypeScript errors
- [ ] Biome checks pass
- [ ] No performance degradation

---

## Design Decisions

### Color Application Strategy
**Question**: How should we visually apply the task color?
**Options**:
1. Background tint (subtle, current pattern)
2. Left border accent (current priority indicator)
3. Full border glow
4. Header background

**Recommendation**: Start with background tint (similar to featureColor badge pattern) for consistency with existing glassmorphism design. Can iterate based on user feedback.

### Color Picker UI
**Recommendation**: Use Radix UI Popover with:
- 8 preset colors (common task color categories)
- HTML5 color input for custom colors
- Clear button to remove color
- Live preview

### Database Field
**Decision**: Add `taskColor` separate from `featureColor`
- `featureColor`: For feature tag badges (existing)
- `taskColor`: For overall task card styling (new)

This separation allows:
- Feature tags to remain distinct
- Tasks without features to still have colors
- Different visual hierarchy (feature = context, task color = user organization)

---

## Anti-Patterns to Avoid
- ❌ Don't replace existing priority color indicator - complement it
- ❌ Don't make colors too bold - maintain glassmorphism aesthetic
- ❌ Don't forget dark mode compatibility
- ❌ Don't hardcode color values - make them user-selectable
- ❌ Don't skip the "Clear Color" option
