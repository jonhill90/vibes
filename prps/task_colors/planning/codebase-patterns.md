# Codebase Patterns: Task Color Management

## Overview

Research conducted across Archon knowledge base and local codebase reveals strong existing patterns for implementing task color selection. The codebase already has a `featureColor` pattern in TaskCard (lines 171-182), Radix UI Popover implementation in ComboBox, and comprehensive glassmorphism styling utilities. This feature will extend existing patterns rather than introducing new architectural concepts.

## Architectural Patterns

### Pattern 1: Radix Popover with Glassmorphism
**Source**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/combobox.tsx`
**Relevance**: 10/10
**What it does**: Provides a complete implementation of Radix UI Popover with search functionality, keyboard navigation, and Tron-inspired glassmorphism styling.

**Key Techniques**:
```typescript
import * as Popover from "@radix-ui/react-popover";

// Basic structure
<Popover.Root open={open} onOpenChange={setOpen}>
  <Popover.Trigger asChild>
    <Button
      variant="ghost"
      onClick={(e) => e.stopPropagation()}
      className={cn(
        "bg-gray-100/50 dark:bg-gray-800/50",
        "hover:bg-gray-200/50 dark:hover:bg-gray-700/50",
        "border border-gray-300/50 dark:border-gray-600/50",
        "focus:outline-none focus:ring-1 focus:ring-cyan-400"
      )}
    >
      {/* Trigger content */}
    </Button>
  </Popover.Trigger>

  <Popover.Portal>
    <Popover.Content
      className={cn(
        "w-full min-w-[var(--radix-popover-trigger-width)]",
        "bg-gradient-to-b from-white/95 to-white/90",
        "dark:from-gray-900/95 dark:to-black/95",
        "backdrop-blur-xl",
        "border border-gray-200 dark:border-gray-700",
        "rounded-lg shadow-xl",
        "z-50"
      )}
      align="start"
      sideOffset={4}
      onOpenAutoFocus={(e) => e.preventDefault()}
    >
      {/* Popover content */}
    </Popover.Content>
  </Popover.Portal>
</Popover.Root>
```

**When to use**:
- Creating dropdown/overlay UI elements
- Need search or interactive content inside popup
- Require keyboard navigation and accessibility
- Want to match existing Archon UI patterns

**How to adapt**:
- Replace ComboBox search input with color swatch grid (2x4 layout)
- Add HTML5 `<input type="color">` for custom color selection
- Include "Clear Color" button to reset to undefined
- Keep same glassmorphism styling and animation patterns
- Maintain `e.stopPropagation()` pattern to prevent event bubbling

**Why this pattern**:
- Already used throughout Archon (ComboBox, DropdownMenu)
- Provides excellent accessibility out of the box
- Handles focus management automatically
- Portal ensures proper z-index stacking
- CSS variables enable responsive width matching

### Pattern 2: Inline Color Styling with Alpha Transparency
**Source**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx` (lines 171-182)
**Relevance**: 10/10
**What it does**: Applies custom colors to UI elements using inline styles with alpha transparency to maintain glassmorphism aesthetic.

**Key Techniques**:
```typescript
{task.feature && (
  <div
    className="px-2 py-1 rounded-md text-xs font-medium backdrop-blur-md"
    style={{
      backgroundColor: `${task.featureColor}20`,  // 20 = 12.5% opacity
      color: task.featureColor,
      boxShadow: `0 0 10px ${task.featureColor}20`,
    }}
  >
    <Tag className="w-3 h-3" />
    {task.feature}
  </div>
)}
```

**When to use**:
- Applying user-selected colors to components
- Need dynamic colors that can't be predefined in Tailwind
- Want to preserve glassmorphism with custom colors
- Background tints, border accents, and glow effects

**How to adapt**:
```typescript
// Apply to TaskCard container (lines 159-161)
<div
  className={`${cardBaseStyles} ${transitionStyles} ...`}
  style={{
    ...(task.taskColor && {
      backgroundColor: `${task.taskColor}10`,  // 10% opacity for subtle tint
      borderColor: `${task.taskColor}30`,      // 30% for visible border
      boxShadow: `0 0 10px ${task.taskColor}20`, // 20% for glow
    }),
  }}
>
```

**Why this pattern**:
- Hex color + two-digit opacity suffix is CSS-native
- Inline styles bypass Tailwind purge/JIT limitations
- Preserves existing glassmorphism gradients
- Works seamlessly in both light and dark modes
- No performance penalty with React's reconciliation

### Pattern 3: FormGrid Two-Column Layout
**Source**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx` (lines 161-187)
**Relevance**: 9/10
**What it does**: Organizes form fields in a responsive grid layout with consistent spacing and alignment.

**Key Techniques**:
```typescript
import { FormField, FormGrid, Label } from "../../../ui/primitives";

<FormGrid columns={2}>
  <FormField>
    <Label>Assignee</Label>
    <ComboBox
      value={localTask?.assignee || "User"}
      onValueChange={(value) =>
        setLocalTask((prev) => (prev ? { ...prev, assignee: value } : null))
      }
    />
  </FormField>

  <FormField>
    <Label>Feature</Label>
    <FeatureSelect
      value={localTask?.feature || ""}
      onChange={handleFeatureChange}
    />
  </FormField>
</FormGrid>
```

**When to use**:
- Grouping related form fields horizontally
- Maintaining consistent spacing across modal forms
- Supporting responsive layouts (mobile switches to single column)
- Aligning with existing TaskEditModal structure

**How to adapt**:
```typescript
// Add after existing Feature field (line 187)
<FormGrid columns={2}>
  <FormField>
    <Label>Feature</Label>
    <FeatureSelect {...existing props} />
  </FormField>

  <FormField>
    <Label>Task Color</Label>
    <TaskColorPicker
      value={localTask?.taskColor}
      onChange={(color) =>
        setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null))
      }
    />
  </FormField>
</FormGrid>
```

**Why this pattern**:
- FormGrid already configured for 2-column responsive layout
- FormField provides consistent vertical spacing (`space-y-1`)
- Label component handles required field indicators
- Matches existing modal structure exactly

### Pattern 4: TanStack Query Mutation with Optimistic Updates
**Source**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts` (lines 122-176)
**Relevance**: 10/10
**What it does**: Implements mutation lifecycle with optimistic UI updates, error rollback, and server reconciliation using nanoid-based IDs.

**Key Techniques**:
```typescript
import { createOptimisticEntity, replaceOptimisticEntity } from "@/features/shared/utils/optimistic";

export function useUpdateTask(projectId: string) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation<Task, Error, { taskId: string; updates: UpdateTaskRequest }, { previousTasks?: Task[] }>({
    mutationFn: ({ taskId, updates }) => taskService.updateTask(taskId, updates),

    onMutate: async ({ taskId, updates }) => {
      // Cancel in-flight queries
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

      // Snapshot for rollback
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(projectId));

      // Optimistic update
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) => {
        if (!old) return old;
        return old.map((task) => (task.id === taskId ? { ...task, ...updates } : task));
      });

      return { previousTasks };
    },

    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }
      showToast(`Failed to update task: ${error.message}`, "error");
    },

    onSuccess: (data) => {
      // Merge server response
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) =>
        old ? old.map((t) => (t.id === data.id ? data : t)) : old
      );
    },
  });
}
```

**When to use**:
- All task mutations (create, update, delete)
- Need instant UI feedback before server response
- Want automatic error recovery
- Maintain consistency with existing mutation patterns

**How to adapt**:
- No changes needed! `taskColor` field will pass through automatically
- Backend's flexible JSON schema accepts new fields
- TypeScript types updated in `task.ts` only
- Mutation hooks already include all Task fields

**Why this pattern**:
- Provides instant feedback (optimistic updates)
- Handles errors gracefully with rollback
- Maintains cache consistency
- Standard pattern across all Archon features

### Pattern 5: Glassmorphism Style Utilities
**Source**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/styles.ts`
**Relevance**: 9/10
**What it does**: Provides centralized glassmorphism style constants following Tron-inspired design system with automatic dark mode support.

**Key Techniques**:
```typescript
export const glassmorphism = {
  background: {
    subtle: "backdrop-blur-md bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30",
    strong: "backdrop-blur-md bg-gradient-to-b from-white/95 to-white/90 dark:from-gray-800/95 dark:to-gray-900/95",
    card: "backdrop-blur-md bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30",
  },

  border: {
    default: "border border-gray-200 dark:border-gray-700",
    focus: "focus:border-cyan-500 focus:shadow-[0_0_20px_5px_rgba(34,211,238,0.5)]",
    hover: "hover:border-cyan-400/70 hover:shadow-[0_0_15px_rgba(34,211,238,0.4)]",
  },

  shadow: {
    lg: "shadow-lg dark:shadow-2xl",
    glow: {
      cyan: "shadow-[0_0_10px_2px_rgba(34,211,238,0.4)] dark:shadow-[0_0_20px_5px_rgba(34,211,238,0.7)]",
      // ... other colors
    },
  },

  animation: {
    fadeIn: "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
    slideIn: "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
  },
};

// Utility function
export function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ");
}
```

**When to use**:
- All new components in `/features` directory
- Applying consistent styling across UI primitives
- Need automatic light/dark mode support
- Building popovers, dropdowns, or floating panels

**How to adapt**:
```typescript
import { cn, glassmorphism } from "../../../ui/primitives/styles";

// Apply to TaskColorPicker Popover.Content
<Popover.Content
  className={cn(
    "rounded-lg p-2",
    glassmorphism.background.strong,
    glassmorphism.border.default,
    glassmorphism.shadow.lg,
    glassmorphism.animation.fadeIn,
    glassmorphism.animation.slideIn
  )}
>
```

**Why this pattern**:
- Ensures UI consistency across all features
- Tailwind's `dark:` prefix handles theme switching
- Pre-defined classes prevent style drift
- Matches Tron-inspired aesthetic throughout app

## Naming Conventions

### File Naming
**Pattern**: `{Feature}{ComponentType}.tsx` (PascalCase)
**Examples**:
- `TaskCard.tsx` - Display component
- `TaskEditModal.tsx` - Modal component
- `TaskColorPicker.tsx` - NEW component for color selection
- `useTaskQueries.ts` - Query hooks file

### Class Naming
**Pattern**: Export as `{Feature}{ComponentType}`
**Examples**:
```typescript
export const TaskCard: React.FC<TaskCardProps> = ({ ... }) => { ... };
export const TaskColorPicker: React.FC<TaskColorPickerProps> = ({ ... }) => { ... };
```

### Function Naming
**Pattern**:
- Mutation hooks: `useCreate{Entity}`, `useUpdate{Entity}`, `useDelete{Entity}`
- Query hooks: `use{Entity}Detail`, `use{Parent}{Entity}`
- Event handlers: `handle{Action}`, `on{Event}Change`

**Examples**:
```typescript
// Hooks
export function useUpdateTask(projectId: string) { ... }
export function useProjectTasks(projectId: string | undefined) { ... }

// Handlers (in components)
const handleColorChange = useCallback((color: string | undefined) => {
  setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null));
}, []);
```

### Type Naming
**Pattern**:
- Props interfaces: `{ComponentName}Props`
- Request types: `Create{Entity}Request`, `Update{Entity}Request`
- Core types: `{Entity}` (e.g., `Task`)

**Examples** (from `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/types/task.ts`):
```typescript
export interface Task {
  id: string;
  taskColor?: string;  // NEW field - optional
  featureColor?: string;  // Existing pattern
  // ... other fields
}

export interface CreateTaskRequest {
  taskColor?: string;  // NEW field
  // ... other fields
}

export interface UpdateTaskRequest {
  taskColor?: string;  // NEW field
  // ... other fields
}

export interface TaskColorPickerProps {
  value?: string;
  onChange: (color: string | undefined) => void;
  disabled?: boolean;
}
```

## File Organization

### Directory Structure
```
archon-ui-main/src/features/projects/tasks/
├── components/
│   ├── TaskCard.tsx              (MODIFY - add color display)
│   ├── TaskEditModal.tsx         (MODIFY - integrate picker)
│   ├── TaskColorPicker.tsx       (NEW - color selection UI)
│   └── tests/
│       ├── TaskCard.test.tsx     (MODIFY - add color tests)
│       └── TaskColorPicker.test.tsx (NEW - picker tests)
├── hooks/
│   └── useTaskQueries.ts         (NO CHANGE - passes through)
├── services/
│   └── taskService.ts            (NO CHANGE - flexible backend)
└── types/
    └── task.ts                   (MODIFY - add taskColor field)
```

**Justification**:
- Follows vertical slice architecture (feature owns all layers)
- TaskColorPicker lives with other task components
- Types updated in central task.ts file
- Hooks and services unchanged (backend accepts new field automatically)
- Tests colocated with components

### Component Location Rationale
**Why TaskColorPicker in `tasks/components/`**:
- Feature-specific component (only used for tasks)
- Not reusable across other features
- Keeps task-related UI together
- Follows existing pattern (TaskPriorityComponent, TaskAssignee)

**Not in `ui/primitives/` because**:
- Too specific to task domain
- Uses task-specific presets (8 Tailwind colors)
- Tightly coupled to Task type

## Common Utilities to Leverage

### 1. Optimistic Update Utilities
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/shared/utils/optimistic.ts`
**Purpose**: Create and replace optimistic entities with stable IDs
**Usage Example**:
```typescript
import { createOptimisticEntity, replaceOptimisticEntity } from "@/features/shared/utils/optimistic";

// Already used in useTaskQueries.ts - no changes needed
const optimisticTask = createOptimisticEntity<Task>({ taskColor: "#ef4444", ... });
```

### 2. cn() Utility Function
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/styles.ts`
**Purpose**: Conditionally combine className strings
**Usage Example**:
```typescript
import { cn } from "../../../ui/primitives/styles";

className={cn(
  "base-classes",
  isSelected && "selected-classes",
  disabled && "disabled-classes"
)}
```

### 3. Smart Polling Hook
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/shared/hooks` (via index)
**Purpose**: Visibility-aware polling for TanStack Query
**Usage Example**:
```typescript
import { useSmartPolling } from "../../../shared/hooks";

// Already used in useTaskQueries.ts - no changes needed
const { refetchInterval } = useSmartPolling(2000);
```

### 4. Toast Notifications
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/shared/hooks/useToast.ts`
**Purpose**: User feedback for mutations
**Usage Example**:
```typescript
import { useToast } from "../../../shared/hooks/useToast";

const { showToast } = useToast();
showToast("Task color updated", "success");
```

### 5. Radix UI Primitives
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/`
**Purpose**: Pre-styled, accessible UI components
**Usage Example**:
```typescript
import { Button, Label, FormField, FormGrid } from "../../../ui/primitives";
import * as Popover from "@radix-ui/react-popover";

// All primitives already have glassmorphism styling
```

## Testing Patterns

### Unit Test Structure
**Pattern**: Vitest + React Testing Library
**Example**: Similar structure to existing task tests
**Key techniques**:
```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { TaskColorPicker } from "../TaskColorPicker";

describe("TaskColorPicker", () => {
  it("renders trigger button with current color", () => {
    const onChange = vi.fn();
    render(<TaskColorPicker value="#ef4444" onChange={onChange} />);

    const trigger = screen.getByRole("button");
    expect(trigger).toBeInTheDocument();
  });

  it("opens popover on click", async () => {
    const onChange = vi.fn();
    render(<TaskColorPicker value="#ef4444" onChange={onChange} />);

    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);

    await waitFor(() => {
      expect(screen.getByText(/Select color/i)).toBeInTheDocument();
    });
  });

  it("calls onChange with selected color", async () => {
    const onChange = vi.fn();
    render(<TaskColorPicker value={undefined} onChange={onChange} />);

    fireEvent.click(screen.getByRole("button"));

    const redSwatch = await screen.findByLabelText("Red");
    fireEvent.click(redSwatch);

    expect(onChange).toHaveBeenCalledWith("#ef4444");
  });

  it("clears color when clear button clicked", async () => {
    const onChange = vi.fn();
    render(<TaskColorPicker value="#ef4444" onChange={onChange} />);

    fireEvent.click(screen.getByRole("button"));

    const clearButton = await screen.findByText(/clear/i);
    fireEvent.click(clearButton);

    expect(onChange).toHaveBeenCalledWith(undefined);
  });
});
```

### Integration Test Structure
**Pattern**: Test TaskCard color display
**Example**:
```typescript
describe("TaskCard with taskColor", () => {
  it("applies custom color styles when taskColor present", () => {
    const task: Task = {
      id: "1",
      title: "Test Task",
      taskColor: "#ef4444",
      // ... other fields
    };

    const { container } = render(
      <TaskCard task={task} projectId="proj-1" {...otherProps} />
    );

    const cardContainer = container.querySelector(".min-h-\\[140px\\]");
    expect(cardContainer).toHaveStyle({
      backgroundColor: "#ef444410",
      borderColor: "#ef444430",
    });
  });

  it("renders without color styles when taskColor undefined", () => {
    const task: Task = {
      id: "1",
      title: "Test Task",
      taskColor: undefined,
      // ... other fields
    };

    const { container } = render(
      <TaskCard task={task} projectId="proj-1" {...otherProps} />
    );

    const cardContainer = container.querySelector(".min-h-\\[140px\\]");
    expect(cardContainer).not.toHaveAttribute("style");
  });
});
```

### Mocking Patterns
```typescript
// Mock services
vi.mock("../../services", () => ({
  taskService: {
    updateTask: vi.fn(),
  },
}));

// Mock shared patterns
vi.mock("../../../shared/config/queryPatterns", () => ({
  DISABLED_QUERY_KEY: ["disabled"] as const,
  STALE_TIMES: {
    instant: 0,
    frequent: 5_000,
    normal: 30_000,
  },
}));
```

## Anti-Patterns to Avoid

### 1. Creating Translation Layers for Database Values
**What it is**: Mapping database values to different frontend values
**Why to avoid**:
- Increases complexity with no benefit
- Creates sync issues between FE/BE
- Violates Archon's "direct database values" principle
**Found in**: NOT in codebase - Archon uses database values directly
**Better approach**:
```typescript
// ✅ CORRECT - Use database value directly
export type DatabaseTaskStatus = "todo" | "doing" | "review" | "done";
type Task = { status: DatabaseTaskStatus };

// ❌ WRONG - Don't create mapping layers
const STATUS_MAP = { TODO: "todo", DOING: "doing" }; // Don't do this
```

### 2. Hardcoding Time Values
**What it is**: Using literal numbers instead of STALE_TIMES constants
**Why to avoid**: Inconsistent cache behavior, harder to maintain
**Found in**: NOT in current codebase (refactored in Phase 2)
**Better approach**:
```typescript
// ✅ CORRECT
import { STALE_TIMES } from "@/features/shared/config/queryPatterns";
staleTime: STALE_TIMES.frequent

// ❌ WRONG
staleTime: 5000
```

### 3. Manual Cache Invalidation with setTimeout
**What it is**: Using timers to invalidate queries manually
**Why to avoid**: TanStack Query handles this automatically
**Found in**: Removed during Phase 5 refactor
**Better approach**: Let TanStack Query's staleTime and refetchInterval handle cache freshness

### 4. Mixing Query Keys Between Features
**What it is**: Using projectKeys in task hooks or vice versa
**Why to avoid**: Violates vertical slice architecture, creates coupling
**Found in**: NOT in codebase - each feature owns its keys
**Better approach**:
```typescript
// ✅ CORRECT - Tasks use taskKeys
export const taskKeys = {
  byProject: (projectId: string) => ["projects", projectId, "tasks"] as const,
};

// Task hooks only reference taskKeys, never projectKeys directly
```

### 5. Creating Generic Color Picker Utilities
**What it is**: Making TaskColorPicker overly generic or putting in ui/primitives/
**Why to avoid**: YAGNI - we only need it for tasks right now
**Better approach**: Keep it specific to tasks in `tasks/components/`. If another feature needs color picking later, we can extract commonalities then.

### 6. RGB/HSL Color Conversions
**What it is**: Converting hex colors to other formats in JavaScript
**Why to avoid**:
- CSS natively supports hex + opacity suffix (`#ef444420`)
- No conversion needed for our use case
- Adds complexity without benefit
**Better approach**: Store and use hex format throughout

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. Feature Color Badge in TaskCard
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx` (lines 171-182)
**Similarity**: Identical color application pattern
**Lessons**:
- Inline styles with hex + opacity work perfectly
- Conditional rendering with `task.feature &&` pattern
- boxShadow creates nice glow effect
- backdrop-blur-md maintains glassmorphism
**Differences**:
- featureColor applies to badge, taskColor applies to entire card
- featureColor tied to feature tag, taskColor independent

#### 2. ComboBox with Custom Values
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/combobox.tsx`
**Similarity**: Popover-based selection UI with custom input support
**Lessons**:
- Focus management with requestAnimationFrame (line 155)
- `onOpenAutoFocus={(e) => e.preventDefault()}` prevents focus issues (line 234)
- `e.stopPropagation()` on click handlers prevents bubbling (lines 176, 263, 266)
- Keyboard navigation with ArrowUp/ArrowDown/Enter/Escape
**Differences**:
- ComboBox has search input, TaskColorPicker has swatch grid
- ComboBox allows custom text values, TaskColorPicker allows custom hex colors

#### 3. Priority Selection in TaskPriorityComponent
**Location**: Referenced in TaskCard line 228, likely uses DropdownMenu
**Similarity**: Inline field change with optimistic updates
**Lessons**:
- Direct mutation call without opening modal
- Immediate visual feedback
- isLoading state during mutation
**Differences**:
- Priority is dropdown, color is popover with visual swatches

## Recommendations for PRP

Based on pattern analysis:

1. **Follow Radix Popover pattern** from ComboBox for TaskColorPicker structure
   - Use exact same glassmorphism styling classes
   - Implement focus management with RAF
   - Include `e.stopPropagation()` on all interactive elements
   - Add keyboard navigation (Escape to close, Tab to exit)

2. **Reuse inline style pattern** from featureColor for taskColor display
   - Apply to TaskCard container (lines 159-161)
   - Use `${taskColor}10` for background (10% opacity)
   - Use `${taskColor}30` for border (30% opacity)
   - Use `${taskColor}20` for boxShadow (20% opacity)

3. **Mirror FormGrid layout** from TaskEditModal
   - Add TaskColorPicker in FormGrid after Feature field (line 187)
   - Use same two-column layout pattern
   - Wrap in FormField for consistent spacing

4. **Adapt existing mutation pattern** - no changes needed!
   - taskColor field passes through automatically
   - Backend's flexible schema accepts new fields
   - Optimistic updates work without modification

5. **Avoid creating new patterns** - use existing utilities
   - Import glassmorphism from styles.ts
   - Use cn() for className composition
   - Follow naming conventions exactly

6. **Define 8 preset colors** as TypeScript constant
   ```typescript
   const PRESET_COLORS = [
     { value: "#ef4444", label: "Red" },
     { value: "#f97316", label: "Orange" },
     { value: "#eab308", label: "Yellow" },
     { value: "#22c55e", label: "Green" },
     { value: "#06b6d4", label: "Cyan" },
     { value: "#3b82f6", label: "Blue" },
     { value: "#8b5cf6", label: "Purple" },
     { value: "#ec4899", label: "Pink" },
   ] as const;
   ```

7. **Test in both light and dark modes** early
   - All 8 preset colors should be visible in dark mode
   - Glassmorphism styling handles theme switching
   - No need for separate dark mode logic

8. **Keep TaskColorPicker simple** - don't over-engineer
   - Grid of 8 swatches (4 columns × 2 rows)
   - HTML5 color input for custom colors
   - "Clear Color" button
   - No color palette libraries needed

## Source References

### From Archon Knowledge Base
- No directly relevant Radix Popover API docs found in search
- General React/TypeScript patterns available but not specifically needed
- Local codebase examples sufficient for implementation

### From Local Codebase
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/combobox.tsx`: Complete Popover implementation - Relevance 10/10
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx:171-182`: Color styling pattern - Relevance 10/10
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx:161-187`: Form layout pattern - Relevance 9/10
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts:122-176`: Mutation pattern - Relevance 10/10
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/styles.ts`: Glassmorphism utilities - Relevance 9/10
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/dropdown-menu.tsx`: Alternative Radix pattern - Relevance 7/10
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/projects/tasks/types/task.ts`: Type definitions - Relevance 10/10
- `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/primitives/input.tsx:86-110`: FormField/FormGrid components - Relevance 9/10

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - Include ComboBox.tsx as primary Popover example
   - Show TaskCard.tsx featureColor lines as color styling template
   - Reference TaskEditModal.tsx FormGrid structure
   - Note useTaskQueries.ts requires no changes

2. **Include key code snippets in "Implementation Blueprint"**:
   - Popover structure from ComboBox (lines 170-215)
   - Inline style pattern from TaskCard (lines 174-177)
   - FormGrid integration from TaskEditModal (lines 161-187)
   - No mutation hook changes needed

3. **Add these to "Known Gotchas" section**:
   - Must use `e.stopPropagation()` in Popover to prevent event bubbling
   - Must use `onOpenAutoFocus={(e) => e.preventDefault()}` to avoid focus issues
   - Test all 8 preset colors in dark mode for visibility
   - HTML5 color input has different UIs across browsers (acceptable)

4. **Use file organization for "Desired Codebase Tree"**:
   ```
   tasks/
   ├── components/
   │   ├── TaskColorPicker.tsx          (NEW)
   │   ├── TaskCard.tsx                 (MODIFY - lines 159-161)
   │   └── TaskEditModal.tsx            (MODIFY - after line 187)
   └── types/
       └── task.ts                      (MODIFY - add taskColor field)
   ```

5. **Emphasize "no backend changes" in PRP**:
   - Backend's flexible JSON schema accepts taskColor automatically
   - No API route modifications needed
   - No database migration required
   - Mutation hooks pass through all fields

6. **Quality gates in PRP**:
   - TypeScript compiles without errors: `npx tsc --noEmit`
   - Biome checks pass: `npm run biome`
   - Unit tests pass: `npm run test TaskColorPicker.test.tsx`
   - Manual testing: Color persists on page refresh (validates backend storage)

## Confidence Level

**Overall**: 95%

**High confidence (100%)**:
- Type definitions (exact featureColor pattern exists)
- TaskCard color display (identical to featureColor badge)
- Mutation hooks (no changes needed)
- Backend compatibility (flexible schema confirmed)

**Medium confidence (90%)**:
- Popover implementation (ComboBox provides template, need to adapt for color swatches)
- Dark mode visibility (need to test all preset colors)

**No concerns**:
- Performance (inline styles are efficient)
- Browser compatibility (hex colors universally supported)
- Accessibility (Radix provides baseline, ARIA labels easy to add)

This research provides comprehensive patterns for implementing task color management with minimal risk and maximum consistency with existing Archon codebase.
