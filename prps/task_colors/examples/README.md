# Task Color Management - Code Examples

## Overview

This directory contains **physical code extracts** (not just references) from the Archon codebase showing the exact patterns needed to implement task color management. Each file demonstrates a critical pattern with detailed comments explaining what to mimic, adapt, and skip.

**Total Examples**: 5 extracted files
**Quality Score**: 9/10 (comprehensive coverage of all requirements)

---

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| combobox-popover-pattern.tsx | combobox.tsx:1-375 | Radix Popover structure | 9/10 |
| feature-color-styling.tsx | TaskCard.tsx:171-182 | Alpha transparency color | 10/10 |
| form-field-integration.tsx | TaskEditModal.tsx:1-210 | Modal form field pattern | 8/10 |
| task-mutation-pattern.tsx | useTaskQueries.ts:1-220 | TanStack Query mutations | 10/10 |
| color-picker-tests.test.tsx | ProjectCard.test.tsx:1-140 | Component testing | 7/10 |

---

## Example 1: Radix Popover Pattern

**File**: `combobox-popover-pattern.tsx`
**Source**: `infra/archon/archon-ui-main/src/features/ui/primitives/combobox.tsx`
**Relevance**: 9/10

### What to Mimic

- **Radix Popover Structure**: The exact pattern for building interactive dropdowns
  ```typescript
  <Popover.Root open={open} onOpenChange={setOpen}>
    <Popover.Trigger asChild>
      <Button onClick={(e) => e.stopPropagation()}>
        {/* Trigger content */}
      </Button>
    </Popover.Trigger>
    <Popover.Portal>
      <Popover.Content onOpenAutoFocus={(e) => e.preventDefault()}>
        {/* Picker content */}
      </Popover.Content>
    </Popover.Portal>
  </Popover.Root>
  ```

- **Focus Management**: Use `requestAnimationFrame` for reliable focus
  ```typescript
  React.useEffect(() => {
    if (open) {
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    }
  }, [open]);
  ```

- **Event Handling**: ALWAYS stop propagation to prevent bubbling
  ```typescript
  onClick={(e) => e.stopPropagation()}
  onKeyDown={(e) => {
    e.stopPropagation();
    handleKeyDown(e);
  }}
  ```

- **Glassmorphism Styling**: Backdrop blur with gradient backgrounds
  ```typescript
  className={cn(
    "bg-gradient-to-b from-white/95 to-white/90",
    "dark:from-gray-900/95 dark:to-black/95",
    "backdrop-blur-xl",  // CRITICAL for glassmorphism
    "border border-gray-200 dark:border-gray-700",
    "rounded-lg shadow-xl",
  )}
  ```

- **Keyboard Navigation**: Handle Enter, Escape, Tab keys
  ```typescript
  case "Enter":
    e.preventDefault();
    handleSelect();
    break;
  case "Escape":
    e.preventDefault();
    setOpen(false);
    break;
  ```

### What to Adapt

- **Replace Search Input**: Remove search functionality, add color preset grid instead
- **Change Trigger Button**: Show current color as colored circle, not text
- **Simplify Content**:
  - 2x4 grid of color swatches
  - HTML5 color input below grid
  - "Clear Color" button at bottom
- **Remove Arrow Navigation**: Not needed for grid layout

### What to Skip

- **ComboBox-Specific Logic**: Search filtering, custom values, highlighted index tracking
- **Complex Keyboard Nav**: Arrow up/down (not needed for color swatches)
- **Option Mapping**: Colors are static, not dynamic options

### Pattern Highlights

```typescript
// THE KEY PATTERN: Popover with event stopPropagation
<Popover.Root open={open} onOpenChange={setOpen}>
  <Popover.Trigger asChild>
    <Button
      onClick={(e) => e.stopPropagation()}  // CRITICAL!
      onKeyDown={(e) => {
        e.stopPropagation();  // CRITICAL!
        // Handle keyboard shortcuts
      }}
    >
      {/* Show current color or placeholder */}
    </Button>
  </Popover.Trigger>

  <Popover.Portal>
    <Popover.Content
      onOpenAutoFocus={(e) => e.preventDefault()}  // CRITICAL!
      className="backdrop-blur-xl"  // Glassmorphism
    >
      {/* Color picker UI */}
    </Popover.Content>
  </Popover.Portal>
</Popover.Root>

// This works because:
// 1. asChild merges Button props with Trigger
// 2. stopPropagation prevents modal from closing
// 3. onOpenAutoFocus prevents focus stealing
// 4. backdrop-blur-xl creates glass effect
```

### Why This Example

ComboBox is the **closest existing component** to TaskColorPicker in the codebase. It demonstrates:
- Exact Radix Popover API usage
- Focus management edge cases
- Event handling gotchas
- Glassmorphism styling patterns
- ARIA accessibility attributes

You can literally copy the structure and replace the content area with color swatches.

---

## Example 2: Feature Color Styling

**File**: `feature-color-styling.tsx`
**Source**: `infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx` (lines 171-182)
**Relevance**: 10/10

### What to Mimic

- **Hex Colors with Alpha Suffix**: Use hex string + two-digit alpha
  ```typescript
  style={{
    backgroundColor: `${task.featureColor}20`,  // 20 = 12.5% opacity
    color: task.featureColor,                   // Full opacity
    boxShadow: `0 0 10px ${task.featureColor}20`,  // Glow effect
  }}
  ```

- **Inline Styles for Dynamic Colors**: Tailwind can't handle runtime colors
  ```typescript
  // DON'T use Tailwind classes for dynamic colors
  // DO use inline styles with template literals
  style={{
    backgroundColor: `${taskColor}10`,
    borderColor: `${taskColor}30`,
    boxShadow: `0 0 10px ${taskColor}20`,
  }}
  ```

- **Conditional Style Application**: Use spread operator
  ```typescript
  style={{
    // Base styles always applied
    // Conditional color overlay
    ...(task.taskColor && {
      backgroundColor: `${task.taskColor}10`,
      borderColor: `${task.taskColor}30`,
      boxShadow: `0 0 10px ${task.taskColor}20`,
    }),
  }}
  ```

- **Alpha Transparency Guidelines**:
  - Background: `10` (6.25% opacity) - Very subtle, doesn't overpower
  - Border: `30` (18.75% opacity) - Visible accent
  - Shadow: `20` (12.5% opacity) - Soft glow

### What to Adapt

- **Apply to Card Container**: Not to a badge, but to main card div
- **Location**: TaskCard.tsx lines 159-161 (main card div)
- **Preserve Existing**:
  - Keep glassmorphism gradient background
  - Keep priority indicator (left border)
  - Keep feature color badge (separate from taskColor)

### What to Skip

- **Feature Badge Specific**: The Tag icon and feature name display
- **Badge-Specific Styling**: `px-2 py-1 rounded-md text-xs` (only for badges)

### Pattern Highlights

```typescript
// THE EXACT PATTERN for applying taskColor to TaskCard

// Base glassmorphism (KEEP THIS)
const cardBaseStyles =
  "bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30";

return (
  <div
    className={cardBaseStyles}
    style={{
      // CRITICAL: Conditional inline styles
      ...(task.taskColor && {
        // Background tint (subtle)
        backgroundColor: `${task.taskColor}10`,

        // Border accent (more visible)
        borderColor: `${task.taskColor}30`,

        // Glow effect (depth)
        boxShadow: `0 0 10px ${task.taskColor}20`,
      }),
    }}
  >
    {/* Card content */}
  </div>
);

// This works because:
// 1. Inline styles override Tailwind background
// 2. Alpha suffix creates transparency (10 = 6.25%)
// 3. Spread operator only applies when taskColor exists
// 4. Preserves glassmorphism when no color set
```

### Why This Example

This is the **EXACT pattern already used in the codebase** for featureColor. TaskColor will use the identical approach, just applied to a different element (card container vs badge). No guesswork needed - this pattern is proven to work with glassmorphism in both light and dark modes.

---

## Example 3: Form Field Integration

**File**: `form-field-integration.tsx`
**Source**: `infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx` (lines 1-210)
**Relevance**: 8/10

### What to Mimic

- **Local State Pattern**: Store all form changes until save
  ```typescript
  const [localTask, setLocalTask] = useState<Partial<Task> | null>(null);

  // Sync with editing task
  useEffect(() => {
    if (editingTask) {
      setLocalTask(editingTask);
    } else {
      setLocalTask({
        title: "",
        status: "todo",
        taskColor: undefined,  // NEW field
      });
    }
  }, [editingTask]);
  ```

- **Change Handler Pattern**: Null-safe updates
  ```typescript
  // ALWAYS use this pattern for optional fields
  setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null));

  // This works because:
  // - Checks prev exists before spreading
  // - Merges new value into existing state
  // - Handles undefined (clear color)
  ```

- **FormGrid Layout**: 2-column side-by-side fields
  ```typescript
  <FormGrid columns={2}>
    <FormField>
      <Label>Task Color</Label>
      <TaskColorPicker
        value={localTask?.taskColor}
        onChange={(color) =>
          setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null))
        }
      />
    </FormField>

    <FormField>
      {/* Second field or empty div */}
    </FormField>
  </FormGrid>
  ```

- **Save Integration**: Mutations automatically include all fields
  ```typescript
  const handleSave = useCallback(() => {
    saveTask(localTask, editingTask, () => {
      onSaved?.();
      onClose();
    });
    // localTask includes taskColor - no special handling needed!
  }, [localTask, editingTask, saveTask, onSaved, onClose]);
  ```

### What to Adapt

- **Placement**: Add AFTER Feature field (around line 187 in TaskEditModal)
- **Label**: Use "Task Color" or just "Color"
- **Handler**: Inline is fine, no need to memoize
  ```typescript
  onChange={(color) =>
    setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null))
  }
  ```

### What to Skip

- **ComboBox Specific**: ASSIGNEE_OPTIONS array, allowCustomValue logic
- **FeatureSelect Specific**: projectFeatures, isLoadingFeatures props
- **Other Fields**: Don't modify Status, Priority, Assignee, Feature

### Pattern Highlights

```typescript
// THE COMPLETE INTEGRATION PATTERN

// 1. Add to initial state
useEffect(() => {
  if (editingTask) {
    setLocalTask(editingTask);
  } else {
    setLocalTask({
      // ... existing fields ...
      taskColor: undefined,  // NEW: Optional color field
    });
  }
}, [editingTask]);

// 2. Add FormField in FormGrid
<FormGrid columns={2}>
  <FormField>
    <Label>Task Color</Label>
    <TaskColorPicker
      value={localTask?.taskColor}
      onChange={(color) =>
        setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null))
      }
      disabled={isSavingTask}
    />
  </FormField>

  <div /> {/* Empty second column or another field */}
</FormGrid>

// 3. Save automatically includes taskColor
const handleSave = useCallback(() => {
  saveTask(localTask, editingTask, callback);
  // localTask.taskColor is in the payload!
}, [localTask, editingTask, saveTask]);

// This works because:
// 1. setLocalTask merges taskColor into state
// 2. saveTask includes all fields from localTask
// 3. Mutation hooks pass through all fields
// 4. Backend flexible schema accepts new field
```

### Why This Example

Shows the **complete form integration lifecycle**:
1. Initialize state with new field
2. Add UI component to form
3. Wire up onChange handler
4. Save includes new field automatically

No complex logic needed - just follow the existing pattern for optional fields like `feature`.

---

## Example 4: Task Mutation Pattern

**File**: `task-mutation-pattern.tsx`
**Source**: `infra/archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts` (lines 1-220)
**Relevance**: 10/10

### What to Mimic

- **Query Key Factories**: Each feature owns its keys
  ```typescript
  export const taskKeys = {
    all: ["tasks"] as const,
    lists: () => [...taskKeys.all, "list"] as const,
    byProject: (projectId: string) => ["projects", projectId, "tasks"] as const,
  };
  ```

- **Optimistic Updates with Nanoid**: Stable IDs for optimistic entities
  ```typescript
  onMutate: async (newTaskData) => {
    // Create optimistic task
    const optimisticTask = createOptimisticEntity<Task>({
      ...newTaskData,
      // taskColor automatically included!
    });

    // Add to cache
    queryClient.setQueryData(taskKeys.byProject(projectId), (old) =>
      old ? [...old, optimisticTask] : [optimisticTask]
    );

    return { previousTasks, optimisticId: optimisticTask._localId };
  }
  ```

- **Rollback on Error**: Restore previous state
  ```typescript
  onError: (error, variables, context) => {
    if (context?.previousTasks) {
      queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
    }
    showToast("Failed to update task", "error");
  }
  ```

- **Replace Optimistic with Server**: Merge real data
  ```typescript
  onSuccess: (serverTask, variables, context) => {
    queryClient.setQueryData(
      taskKeys.byProject(projectId),
      (tasks) => replaceOptimisticEntity(tasks, context.optimisticId, serverTask)
    );
  }
  ```

### What to Adapt

**CRITICAL INSIGHT**: You DON'T need to change these hooks!

The mutation hooks automatically pass through all fields from the request object. Just add `taskColor` to the type definitions and it flows through:

```typescript
// task.ts - ADD THESE THREE LINES:
export interface Task {
  // ... existing fields ...
  taskColor?: string;  // NEW
}

export interface CreateTaskRequest {
  // ... existing fields ...
  taskColor?: string;  // NEW
}

export interface UpdateTaskRequest {
  // ... existing fields ...
  taskColor?: string;  // NEW
}

// That's it! No changes to useTaskQueries.ts needed!
```

### What to Skip

- **ALL OF IT**: Don't modify useTaskQueries.ts
- The spread operator in mutations includes taskColor automatically
- Backend flexible schema accepts new fields
- No special handling required

### Pattern Highlights

```typescript
// HOW TASKCOLOR FLOWS THROUGH AUTOMATICALLY

// 1. In TaskEditModal.tsx
setLocalTask((prev) => (prev ? { ...prev, taskColor: "#ef4444" } : null));

// 2. In save handler
saveTask(localTask);  // localTask.taskColor is included

// 3. In useTaskEditor hook (not shown, but internally)
const mutation = useCreateTask();
mutation.mutate({
  ...localTask,  // Spread includes taskColor!
  project_id: projectId,
});

// 4. In useTaskQueries.ts (UNCHANGED)
mutationFn: (taskData: CreateTaskRequest) => taskService.createTask(taskData),
// taskData includes taskColor - no code changes needed

// 5. In optimistic update (UNCHANGED)
const optimisticTask = createOptimisticEntity<Task>({
  ...newTaskData,  // Spread includes taskColor!
});

// 6. Backend receives taskColor in JSON payload
// 7. Backend returns taskColor in response
// 8. Frontend replaces optimistic with real data

// This works because:
// - TypeScript interfaces allow extra properties
// - Spread operators include all fields
// - Backend flexible JSON schema accepts new fields
// - No validation needed (optional field)
```

### Why This Example

Demonstrates the **MOST IMPORTANT INSIGHT**: You don't need to modify mutation hooks! The existing architecture is designed for this kind of extension. Just add the type definitions and taskColor flows through automatically. This saves significant development time and reduces risk of breaking existing functionality.

---

## Example 5: Component Testing

**File**: `color-picker-tests.test.tsx`
**Source**: `infra/archon/archon-ui-main/src/features/projects/components/tests/ProjectCard.test.tsx` (lines 1-140)
**Relevance**: 7/10

### What to Mimic

- **Test Structure**: describe/it blocks with beforeEach
  ```typescript
  describe("TaskColorPicker", () => {
    const mockHandlers = {
      onChange: vi.fn(),
    };

    beforeEach(() => {
      vi.clearAllMocks();
    });

    it("should render with placeholder when no color selected", () => {
      render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
      expect(screen.getByRole("button")).toBeInTheDocument();
    });
  });
  ```

- **User Interaction Testing**: fireEvent for clicks and keyboard
  ```typescript
  it("should call onChange when preset color clicked", async () => {
    render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);

    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);

    const redSwatch = await screen.findByLabelText("Red");
    fireEvent.click(redSwatch);

    expect(mockHandlers.onChange).toHaveBeenCalledWith("#ef4444");
  });
  ```

- **Conditional Rendering**: Test elements appear/disappear
  ```typescript
  it("should show color swatches when popover open", async () => {
    const { container } = render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);

    fireEvent.click(screen.getByRole("button"));

    await waitFor(() => {
      expect(screen.getByText("Clear Color")).toBeInTheDocument();
    });
  });
  ```

- **Prop Variations**: Test different input combinations
  ```typescript
  it("should not open when disabled", () => {
    render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} disabled />);

    const trigger = screen.getByRole("button");
    expect(trigger).toBeDisabled();
  });
  ```

### What to Adapt

Tests to write for TaskColorPicker:
1. **Rendering**: With/without color, disabled state
2. **Opening**: Click trigger to open popover
3. **Preset Selection**: Click color swatch, verify onChange
4. **Custom Color**: Change HTML5 input, verify onChange
5. **Clear Color**: Click clear button, verify onChange(undefined)
6. **Keyboard**: Escape to close popover
7. **Visual**: Color indicator shows current color
8. **Edge Cases**: All 8 presets visible, long color strings

### What to Skip

- **Radix UI Internals**: Don't test Popover's implementation
- **Browser APIs**: Don't test HTML5 color picker UI
- **CSS Details**: Don't test exact pixel positioning or transitions

### Pattern Highlights

```typescript
// COMPLETE TEST SUITE EXAMPLE

describe("TaskColorPicker", () => {
  const mockHandlers = {
    onChange: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Test 1: Basic rendering
  it("should render trigger button", () => {
    render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  // Test 2: Color selection
  it("should select preset color", async () => {
    render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);

    fireEvent.click(screen.getByRole("button"));

    const redSwatch = await screen.findByLabelText("Red");
    fireEvent.click(redSwatch);

    expect(mockHandlers.onChange).toHaveBeenCalledWith("#ef4444");
    expect(mockHandlers.onChange).toHaveBeenCalledTimes(1);
  });

  // Test 3: Clear color
  it("should clear color", async () => {
    render(<TaskColorPicker value="#ef4444" onChange={mockHandlers.onChange} />);

    fireEvent.click(screen.getByRole("button"));

    const clearButton = await screen.findByText("Clear Color");
    fireEvent.click(clearButton);

    expect(mockHandlers.onChange).toHaveBeenCalledWith(undefined);
  });

  // Test 4: Keyboard navigation
  it("should close on Escape", async () => {
    render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);

    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);

    await waitFor(() => {
      expect(screen.getByText("Clear Color")).toBeInTheDocument();
    });

    fireEvent.keyDown(trigger, { key: "Escape" });

    await waitFor(() => {
      expect(screen.queryByText("Clear Color")).not.toBeInTheDocument();
    });
  });

  // Test 5: Disabled state
  it("should not open when disabled", () => {
    render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} disabled />);

    expect(screen.getByRole("button")).toBeDisabled();
  });
});

// This works because:
// 1. vi.fn() mocks callback functions
// 2. fireEvent simulates user interactions
// 3. waitFor handles async state updates
// 4. screen queries find elements in DOM
// 5. expect assertions verify behavior
```

### Why This Example

Shows the **standard testing approach** used throughout the Archon codebase. Vitest + React Testing Library patterns for:
- Component rendering
- User interactions
- Callback verification
- Conditional styling
- Edge cases

Follow these patterns for TaskColorPicker tests to maintain consistency with existing test suite.

---

## Usage Instructions

### Study Phase

1. **Read Each Example File**: Start with combobox-popover-pattern.tsx (most important)
2. **Understand Attribution Headers**: Each file shows exactly where code came from
3. **Focus on "What to Mimic" Comments**: These are the key patterns to copy
4. **Note "What to Adapt" Sections**: Customizations needed for TaskColorPicker
5. **Review "Pattern Highlights"**: Explained code snippets with reasoning

### Application Phase

1. **Start with Types** (task.ts):
   - Add `taskColor?: string` to Task interface
   - Add to CreateTaskRequest and UpdateTaskRequest
   - No other changes needed

2. **Create TaskColorPicker Component**:
   - Copy Popover structure from combobox-popover-pattern.tsx
   - Replace search input with 2x4 color grid
   - Add HTML5 color input
   - Add "Clear Color" button
   - Keep all event stopPropagation and focus management

3. **Apply Color to TaskCard**:
   - Copy inline style pattern from feature-color-styling.tsx
   - Apply to main card div (lines 159-161)
   - Use conditional spread operator
   - Test in both light and dark modes

4. **Integrate into TaskEditModal**:
   - Follow form-field-integration.tsx pattern
   - Add FormField with Label
   - Wire up onChange to update localTask
   - Place after Feature field in FormGrid

5. **Verify Mutations Work**:
   - Run app and create/edit task with color
   - Check network tab: taskColor in request payload
   - Check response: taskColor in server response
   - No code changes needed (task-mutation-pattern.tsx explains why)

6. **Write Tests**:
   - Follow color-picker-tests.test.tsx patterns
   - Test rendering, interactions, edge cases
   - Use vi.fn() for mocks, fireEvent for interactions

### Testing Patterns

**TaskColorPicker Unit Tests**:
- Rendering with/without color
- Opening/closing popover
- Selecting preset colors
- Custom color input
- Clearing color (undefined)
- Keyboard navigation
- Disabled state

**TaskCard Integration Tests**:
- Card displays with taskColor
- Inline styles applied correctly
- Works in dark mode
- Persists after page refresh

**TaskEditModal Integration Tests**:
- Color picker appears in modal
- Saves taskColor to database
- Clears color (sets to undefined)
- Disabled during save operation

---

## Pattern Summary

### Common Patterns Across Examples

1. **Radix UI Integration**:
   - Popover.Root > Trigger > Portal > Content structure
   - asChild prop to merge button props
   - onOpenAutoFocus={(e) => e.preventDefault()}
   - Portal for z-index layering

2. **Event Handling**:
   - ALWAYS e.stopPropagation() on clicks and keyDown
   - Keyboard shortcuts (Enter, Escape, Tab)
   - Focus management with requestAnimationFrame
   - useCallback for memoized handlers

3. **Glassmorphism Styling**:
   - backdrop-blur-xl for glass effect
   - Gradient backgrounds (from-white/95 to-white/90)
   - Border with opacity
   - Shadow with cyan tint
   - Dark mode variants

4. **Color with Alpha Transparency**:
   - Inline styles (not Tailwind classes)
   - Hex color + alpha suffix (e.g., "10", "20", "30")
   - Template literals for dynamic values
   - Conditional application with spread operator

5. **Form State Management**:
   - Local state with useState
   - Sync with useEffect
   - Null-safe updates: prev ? { ...prev, field: value } : null
   - Mutations automatically include all fields

6. **TanStack Query Mutations**:
   - Query key factories per feature
   - Optimistic updates with createOptimisticEntity
   - Rollback on error
   - Replace optimistic with server data on success
   - Smart polling with visibility awareness

7. **Testing Approach**:
   - describe/it structure
   - beforeEach for setup
   - vi.fn() for mocks
   - fireEvent for interactions
   - waitFor for async updates

### Anti-Patterns Observed

1. **Don't Hardcode Colors in Tailwind**: Dynamic colors require inline styles
2. **Don't Skip stopPropagation**: Prevents modal closing when clicking picker
3. **Don't Skip onOpenAutoFocus**: Causes focus issues in nested components
4. **Don't Use Full Opacity Backgrounds**: Alpha "10" or "20" for subtle tint
5. **Don't Modify Mutation Hooks**: Types + spread operator handle new fields
6. **Don't Test Implementation Details**: Focus on user-facing behavior

---

## Integration with PRP

### How PRP Assembly Should Use These Examples

1. **Reference in "All Needed Context"**:
   ```markdown
   ## Code Examples
   See prps/task_colors/examples/ for extracted patterns:
   - combobox-popover-pattern.tsx: Radix Popover structure
   - feature-color-styling.tsx: Alpha transparency colors
   - form-field-integration.tsx: Modal form integration
   - task-mutation-pattern.tsx: TanStack Query mutations
   - color-picker-tests.test.tsx: Testing patterns
   ```

2. **Include Key Patterns in Implementation Blueprint**:
   - Popover structure snippet
   - Inline style pattern
   - Form field integration example
   - Test case template

3. **Direct Implementer to Study Before Coding**:
   ```markdown
   ## Before Implementation
   1. Read examples/README.md completely
   2. Study combobox-popover-pattern.tsx (focus management critical)
   3. Review feature-color-styling.tsx (exact TaskCard pattern)
   4. Understand task-mutation-pattern.tsx (no changes needed!)
   ```

4. **Use for Validation**:
   - Can TaskColorPicker be adapted from ComboBox? YES (examples show how)
   - Can taskColor use existing mutation hooks? YES (no changes needed)
   - Are there existing color patterns? YES (featureColor is identical)
   - What testing approach to use? Follow ProjectCard.test.tsx patterns

### Reference in PRP Sections

**All Needed Context**:
```markdown
Code examples extracted to prps/task_colors/examples/:
- 5 physical code files (not references)
- Comprehensive README with usage instructions
- "What to Mimic/Adapt/Skip" for each example
- Pattern highlights with explanations
```

**Implementation Blueprint**:
```markdown
TaskColorPicker Component:
- Structure: Copy from combobox-popover-pattern.tsx
- Content: 2x4 color grid + HTML5 input + clear button
- Styling: Glassmorphism pattern from examples
- Events: stopPropagation pattern (CRITICAL)

TaskCard Integration:
- Pattern: feature-color-styling.tsx lines 40-70
- Location: TaskCard.tsx line 160 (main div)
- Styles: Conditional inline styles with spread operator
```

**Testing Strategy**:
```markdown
Unit Tests:
- Follow color-picker-tests.test.tsx patterns
- Test: rendering, interactions, keyboard, disabled state

Integration Tests:
- TaskCard displays color
- TaskEditModal saves color
- Persistence across page refresh
```

---

## Source Attribution

### From Archon Codebase

All examples extracted from `infra/archon/archon-ui-main/`:

- **ComboBox**: `src/features/ui/primitives/combobox.tsx`
- **TaskCard**: `src/features/projects/tasks/components/TaskCard.tsx`
- **TaskEditModal**: `src/features/projects/tasks/components/TaskEditModal.tsx`
- **useTaskQueries**: `src/features/projects/tasks/hooks/useTaskQueries.ts`
- **ProjectCard.test**: `src/features/projects/components/tests/ProjectCard.test.tsx`

### Extraction Metadata

- **Extracted**: 2025-10-10
- **Feature**: task_colors
- **Purpose**: PRP generation code examples
- **Format**: Physical TypeScript/TSX files with comments
- **Quality**: 9/10 coverage (all requirements addressed)

---

## Quality Assessment

### Coverage Analysis

- **ComboBox Pattern**: 9/10 (comprehensive Popover example)
- **Color Styling**: 10/10 (exact featureColor pattern)
- **Form Integration**: 8/10 (complete modal pattern)
- **Mutations**: 10/10 (shows no changes needed)
- **Testing**: 7/10 (good patterns, not color-specific)

**Overall**: 9/10

### Completeness Checklist

- ✅ Radix Popover structure and usage
- ✅ Focus management edge cases
- ✅ Event stopPropagation pattern
- ✅ Glassmorphism styling
- ✅ Alpha transparency colors
- ✅ Inline style application
- ✅ FormGrid layout pattern
- ✅ Local state management
- ✅ TanStack Query mutations
- ✅ Optimistic updates
- ✅ Testing patterns
- ✅ ARIA accessibility

### Gaps (Minor)

- No color-specific test examples (generic patterns provided)
- No HTML5 color input examples (straightforward, well-documented)
- No 2x4 grid layout example (simple CSS grid)

These gaps are acceptable because:
1. Generic test patterns apply to TaskColorPicker
2. HTML5 color input is standard web API
3. CSS grid is basic layout (not specific to this feature)

---

## Recommendations for Implementation

### High Priority

1. **Start with ComboBox Pattern**: Copy Popover structure exactly
2. **Verify Event Handling**: Test stopPropagation thoroughly
3. **Apply Color Pattern**: Use exact featureColor approach
4. **Test Dark Mode**: All 8 preset colors must be visible
5. **Integration Test**: End-to-end save and display

### Medium Priority

1. **Custom Color Validation**: Regex check hex format
2. **Keyboard Accessibility**: Test with keyboard only
3. **Mobile Responsiveness**: Test on small screens
4. **Error States**: Handle invalid colors gracefully

### Low Priority

1. **Color Name Tooltips**: Enhance accessibility (nice-to-have)
2. **Recently Used Colors**: Track user's recent selections (future)
3. **Color Palette Editor**: Let users customize presets (future)

---

Generated: 2025-10-10
Feature: task_colors
Total Examples: 5
Quality Score: 9/10
