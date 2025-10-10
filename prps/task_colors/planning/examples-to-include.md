# Examples Curated: task_colors

## Summary

Extracted **5 physical code files** to the examples directory (`prps/task_colors/examples/`). All files contain actual code (not just references) with comprehensive attribution headers and inline comments explaining what to mimic, adapt, and skip.

**Quality Score**: 9/10 (comprehensive coverage of all requirements)

---

## Files Created

### 1. combobox-popover-pattern.tsx
**Source**: `infra/archon/archon-ui-main/src/features/ui/primitives/combobox.tsx` (lines 1-375)
**Pattern**: Radix UI Popover with glassmorphism styling
**Relevance**: 9/10

**Key Patterns**:
- Popover.Root/Trigger/Portal/Content structure
- Focus management with requestAnimationFrame
- Event stopPropagation (CRITICAL for nested components)
- Glassmorphism backdrop-blur styling
- Keyboard navigation (Enter, Escape, Tab)
- ARIA attributes for accessibility

**What to Mimic**:
- Exact Radix Popover API usage
- `onOpenAutoFocus={(e) => e.preventDefault()}` pattern
- `onClick={(e) => e.stopPropagation()}` on all interactive elements
- `asChild` prop for trigger button
- Focus management lifecycle

**What to Adapt**:
- Replace search input with 2x4 color grid
- Change trigger button to show current color
- Simplify keyboard navigation (no arrow keys needed)
- Add HTML5 color input and clear button

### 2. feature-color-styling.tsx
**Source**: `infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx` (lines 171-182)
**Pattern**: Color with alpha transparency
**Relevance**: 10/10

**Key Patterns**:
- Inline styles for dynamic colors (not Tailwind)
- Hex color + alpha suffix (`"10"`, `"20"`, `"30"`)
- Template literals: `` `${color}20` ``
- Conditional style application with spread operator
- Three properties: backgroundColor, borderColor, boxShadow

**What to Mimic**:
- Exact alpha transparency values (10%, 20%, 30%)
- Inline style object structure
- Conditional spread: `...(color && { styles })`
- Works with existing glassmorphism

**What to Adapt**:
- Apply to card container (not badge)
- Location: TaskCard.tsx line 160
- Preserve priority indicator and feature badge

### 3. form-field-integration.tsx
**Source**: `infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx` (lines 1-210)
**Pattern**: Form field in modal with local state
**Relevance**: 8/10

**Key Patterns**:
- Local state: `useState<Partial<Task> | null>(null)`
- Sync with useEffect when editingTask changes
- Null-safe updates: `setLocalTask((prev) => (prev ? { ...prev, field: value } : null))`
- FormGrid for 2-column layout
- Save handler includes all fields automatically

**What to Mimic**:
- State initialization pattern
- Change handler null-safety
- FormField + Label structure
- Placement in FormGrid

**What to Adapt**:
- Add after Feature field (line 187)
- Inline onChange (no need to memoize)
- Pass `disabled={isSavingTask}` prop

### 4. task-mutation-pattern.tsx
**Source**: `infra/archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts` (lines 1-220)
**Pattern**: TanStack Query mutations with optimistic updates
**Relevance**: 10/10

**Key Patterns**:
- Query key factories per feature
- Optimistic updates with createOptimisticEntity
- Rollback on error with context
- Replace optimistic with server data on success
- Smart polling with visibility awareness

**CRITICAL INSIGHT**: You DON'T need to change these hooks!
- Backend flexible schema accepts taskColor automatically
- Spread operators include all fields
- Just add to type definitions (Task, CreateTaskRequest, UpdateTaskRequest)
- Mutations pass through taskColor without code changes

**What to Mimic**:
- Nothing - understand why NO changes needed
- Backend flexibility pattern
- Type-driven field inclusion

**What to Adapt**:
- Only type definitions in task.ts
- No changes to useTaskQueries.ts
- No changes to taskService.ts

### 5. color-picker-tests.test.tsx
**Source**: `infra/archon/archon-ui-main/src/features/projects/components/tests/ProjectCard.test.tsx` (lines 1-140)
**Pattern**: Component testing with Vitest + React Testing Library
**Relevance**: 7/10

**Key Patterns**:
- describe/it test structure
- beforeEach for mock cleanup
- vi.fn() for callback mocks
- fireEvent for user interactions
- waitFor for async updates
- screen queries for element access

**What to Mimic**:
- Test structure and organization
- Mock handler pattern
- User interaction testing
- Conditional rendering tests

**What to Adapt**:
- Test TaskColorPicker specific behaviors:
  - Opening/closing popover
  - Selecting preset colors
  - Custom color input
  - Clearing color (undefined)
  - Keyboard navigation
  - Disabled state

---

## Key Patterns Extracted

### 1. Radix Popover Architecture
**From**: combobox-popover-pattern.tsx

```typescript
<Popover.Root open={open} onOpenChange={setOpen}>
  <Popover.Trigger asChild>
    <Button onClick={(e) => e.stopPropagation()}>
      {/* Trigger content */}
    </Button>
  </Popover.Trigger>
  <Popover.Portal>
    <Popover.Content
      onOpenAutoFocus={(e) => e.preventDefault()}
      className="backdrop-blur-xl"
    >
      {/* Content */}
    </Popover.Content>
  </Popover.Portal>
</Popover.Root>
```

**Why Critical**: This is the foundation for TaskColorPicker. Every detail matters:
- `asChild` merges button props
- `stopPropagation` prevents modal closing
- `onOpenAutoFocus` prevents focus issues
- `backdrop-blur-xl` creates glassmorphism

### 2. Alpha Transparency Pattern
**From**: feature-color-styling.tsx

```typescript
style={{
  ...(task.taskColor && {
    backgroundColor: `${task.taskColor}10`,  // 10% opacity
    borderColor: `${task.taskColor}30`,      // 30% opacity
    boxShadow: `0 0 10px ${task.taskColor}20`, // 20% opacity
  }),
}}
```

**Why Critical**: This is the EXACT pattern already used for featureColor. No guesswork needed - proven to work with glassmorphism in both light and dark modes.

### 3. Form State Pattern
**From**: form-field-integration.tsx

```typescript
// Initialize with new field
useEffect(() => {
  setLocalTask({
    // ... existing fields ...
    taskColor: undefined,  // NEW
  });
}, [editingTask]);

// Update with null-safety
setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null));

// Save includes automatically
saveTask(localTask);  // taskColor in payload!
```

**Why Critical**: Shows the complete lifecycle from initialization to save. No special handling needed - just follow existing pattern.

### 4. Mutation Pass-Through
**From**: task-mutation-pattern.tsx

```typescript
// Type definitions (ONLY CHANGES NEEDED):
export interface Task {
  taskColor?: string;  // NEW
}

export interface CreateTaskRequest {
  taskColor?: string;  // NEW
}

export interface UpdateTaskRequest {
  taskColor?: string;  // NEW
}

// Hooks automatically include taskColor - NO CHANGES:
const optimisticTask = createOptimisticEntity<Task>({
  ...newTaskData,  // Spread includes taskColor!
});
```

**Why Critical**: Demonstrates that the architecture is designed for this kind of extension. Most important time-saving insight.

### 5. Testing Structure
**From**: color-picker-tests.test.tsx

```typescript
describe("TaskColorPicker", () => {
  const mockHandlers = { onChange: vi.fn() };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should select preset color", async () => {
    render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);

    fireEvent.click(screen.getByRole("button"));
    const redSwatch = await screen.findByLabelText("Red");
    fireEvent.click(redSwatch);

    expect(mockHandlers.onChange).toHaveBeenCalledWith("#ef4444");
  });
});
```

**Why Critical**: Standard testing approach used throughout codebase. Maintains consistency.

---

## Recommendations for PRP Assembly

### 1. Reference Examples Directory in PRP

**"All Needed Context" Section**:
```markdown
## Code Examples
Physical code files extracted to prps/task_colors/examples/:

1. **combobox-popover-pattern.tsx**: Complete Radix Popover implementation
   - Relevance: 9/10
   - Focus: Popover structure, focus management, event handling

2. **feature-color-styling.tsx**: Alpha transparency color pattern
   - Relevance: 10/10
   - Focus: Inline styles, conditional application, opacity values

3. **form-field-integration.tsx**: Modal form field pattern
   - Relevance: 8/10
   - Focus: Local state, FormGrid layout, save integration

4. **task-mutation-pattern.tsx**: TanStack Query mutations
   - Relevance: 10/10
   - Focus: NO CHANGES NEEDED - explains why

5. **color-picker-tests.test.tsx**: Testing patterns
   - Relevance: 7/10
   - Focus: Test structure, user interactions, assertions

See examples/README.md for comprehensive usage guide.
```

### 2. Include Key Patterns in Implementation Blueprint

**TaskColorPicker Component**:
```markdown
Structure: Copy from combobox-popover-pattern.tsx (lines 169-215)
- Popover.Root > Trigger > Portal > Content
- Button with e.stopPropagation() on click and keyDown
- Content with onOpenAutoFocus={(e) => e.preventDefault()}
- Glassmorphism styling with backdrop-blur-xl

Content: 2x4 grid of color swatches + HTML5 input + clear button
- Grid layout: grid-cols-4 gap-2
- Each swatch: Button with backgroundColor inline style
- HTML5 input: <input type="color" onChange={...} />
- Clear button: Sets onChange(undefined)
```

**TaskCard Color Application**:
```markdown
Pattern: feature-color-styling.tsx (lines 40-70)
Location: TaskCard.tsx line 160 (main card div)

style={{
  ...(task.taskColor && {
    backgroundColor: `${task.taskColor}10`,
    borderColor: `${task.taskColor}30`,
    boxShadow: `0 0 10px ${task.taskColor}20`,
  }),
}}
```

**TaskEditModal Integration**:
```markdown
Pattern: form-field-integration.tsx (lines 161-187)
Placement: After Feature field in FormGrid

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
</FormGrid>
```

### 3. Direct Implementer to Study Examples First

**Pre-Implementation Checklist**:
```markdown
Before writing code:
1. ✅ Read examples/README.md completely (15 minutes)
2. ✅ Study combobox-popover-pattern.tsx (focus management is critical)
3. ✅ Review feature-color-styling.tsx (exact pattern for TaskCard)
4. ✅ Understand task-mutation-pattern.tsx (NO CHANGES NEEDED!)
5. ✅ Note testing patterns from color-picker-tests.test.tsx

Key insights to internalize:
- Event stopPropagation is CRITICAL (prevents modal closing)
- onOpenAutoFocus prevention is CRITICAL (prevents focus issues)
- Inline styles for colors (Tailwind can't handle dynamic)
- Alpha "10" = 6.25% opacity (not 10%)
- Mutation hooks need NO changes (spread operator includes fields)
```

### 4. Use Examples for Validation

**Validation Checklist**:
```markdown
Can TaskColorPicker be built from existing patterns?
✅ YES - ComboBox provides exact Popover structure

Can taskColor use existing mutation hooks?
✅ YES - Spread operator includes new field automatically

Are there existing color patterns in codebase?
✅ YES - featureColor uses identical alpha transparency approach

What testing approach should be used?
✅ Follow ProjectCard.test.tsx patterns (Vitest + RTL)

Is glassmorphism styling documented?
✅ YES - ComboBox shows exact classes and structure

Are there edge cases to consider?
✅ YES - Examples show: disabled state, keyboard nav, dark mode, undefined handling
```

---

## Coverage Assessment

### Requirements Coverage

| Requirement | Example Coverage | Notes |
|------------|------------------|-------|
| Color picker UI | combobox-popover-pattern.tsx | 9/10 - Complete Popover pattern |
| Preset colors | feature-color-styling.tsx | 10/10 - Alpha transparency pattern |
| Custom color input | (Standard HTML5) | 7/10 - Not specific to codebase |
| Color display on cards | feature-color-styling.tsx | 10/10 - Exact featureColor pattern |
| Form integration | form-field-integration.tsx | 8/10 - Complete modal pattern |
| Data persistence | task-mutation-pattern.tsx | 10/10 - NO CHANGES NEEDED insight |
| Testing approach | color-picker-tests.test.tsx | 7/10 - Generic patterns apply |
| Glassmorphism styling | combobox-popover-pattern.tsx | 9/10 - Complete styling guide |
| Dark mode support | feature-color-styling.tsx | 10/10 - Built into pattern |
| Keyboard accessibility | combobox-popover-pattern.tsx | 9/10 - Full keyboard nav |

**Overall Coverage**: 9/10

### Gaps (Minor)

1. **No HTML5 Color Input Example**: Standard web API, not codebase-specific
2. **No CSS Grid Layout Example**: Basic CSS, not unique to Archon
3. **No Color-Specific Tests**: Generic test patterns apply

**Why These Gaps Are Acceptable**:
- HTML5 `<input type="color">` is well-documented standard
- CSS Grid is basic layout technique
- Test patterns are generic enough to apply to colors

### Strengths

1. **Physical Code Files**: Actual extractable code, not just references
2. **Comprehensive Comments**: Every pattern explained with "why"
3. **Attribution Headers**: Exact source file and line numbers
4. **What to Mimic/Adapt/Skip**: Clear guidance for each example
5. **Pattern Highlights**: Key code snippets with explanations
6. **README.md**: 400+ lines of usage instructions

---

## Usage Instructions for PRP Implementer

### Phase 1: Study (30 minutes)

1. **Read examples/README.md**: Complete overview of all patterns
2. **Study combobox-popover-pattern.tsx**: Most important - focus management
3. **Review feature-color-styling.tsx**: 5 minutes - simple pattern
4. **Scan task-mutation-pattern.tsx**: Key insight - no changes needed
5. **Note test patterns**: Reference for later

### Phase 2: Implementation (3-4 hours)

1. **Types First** (15 min):
   - Add `taskColor?: string` to Task, CreateTaskRequest, UpdateTaskRequest
   - Verify TypeScript compiles

2. **TaskColorPicker Component** (2 hours):
   - Copy Popover structure from combobox
   - Create 2x4 color grid
   - Add HTML5 color input
   - Add clear button
   - Test in isolation

3. **TaskCard Integration** (30 min):
   - Copy inline style pattern
   - Apply to line 160
   - Test with different colors
   - Verify dark mode

4. **TaskEditModal Integration** (30 min):
   - Add FormField in FormGrid
   - Wire up onChange
   - Test save flow

5. **Testing** (1 hour):
   - Write unit tests
   - Test integration
   - Verify persistence

### Phase 3: Validation (30 minutes)

1. **Visual Testing**:
   - All 8 preset colors work
   - Dark mode looks good
   - Glassmorphism preserved
   - Priority indicator visible

2. **Functional Testing**:
   - Create task with color
   - Edit task color
   - Clear task color
   - Persist across refresh

3. **Quality Checks**:
   - TypeScript compiles
   - Biome checks pass
   - Tests pass
   - No console errors

---

## Quality Score Breakdown

### Coverage (9/10)
- ✅ All major patterns extracted
- ✅ Physical code files (not references)
- ✅ Comprehensive README
- ⚠️ Minor gaps (HTML5, CSS Grid - acceptable)

### Relevance (9/10)
- ✅ ComboBox is closest existing component (9/10)
- ✅ FeatureColor is identical pattern (10/10)
- ✅ TaskEditModal shows exact integration (8/10)
- ✅ Mutations insight saves significant time (10/10)
- ⚠️ Tests are generic (7/10 - but applicable)

### Completeness (9/10)
- ✅ All examples have attribution headers
- ✅ Inline comments explain "why"
- ✅ "What to Mimic/Adapt/Skip" sections
- ✅ Pattern highlights with code
- ✅ README with usage instructions
- ✅ Integration guidance for PRP

### Overall Quality: 9/10

**Strengths**:
- Physical code extraction (not just paths)
- Comprehensive comments and guidance
- Exact source attribution
- Usage instructions
- Time-saving insights (mutations)

**Improvements Possible** (not critical):
- Add HTML5 color input example
- Add CSS Grid layout example
- Add color-specific test example

---

## Summary

Successfully extracted 5 physical code files to `prps/task_colors/examples/` with comprehensive README.md. All files contain:
- Actual code (not references)
- Source attribution headers
- Inline comments explaining patterns
- "What to Mimic/Adapt/Skip" guidance
- Pattern highlights with reasoning

**Key Insights Captured**:
1. ComboBox provides exact Popover structure
2. FeatureColor uses identical alpha transparency pattern
3. Mutation hooks need NO CHANGES (spread includes fields)
4. Form integration follows existing modal patterns
5. Testing uses standard Vitest + RTL approach

**Ready for PRP Assembly**: Examples directory can be directly referenced in PRP "All Needed Context" section with confidence that implementer has all patterns needed.

---

Generated: 2025-10-10
Feature: task_colors
Examples Directory: prps/task_colors/examples/
Total Files: 5 code files + 1 README
Overall Quality: 9/10
