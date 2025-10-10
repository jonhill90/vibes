# Feature Analysis: Task Color Management

## INITIAL.md Summary

Add custom color selection to tasks in the Archon task manager, allowing users to visually organize and categorize tasks beyond status columns. Users will select colors via a color picker in the task edit modal, and these colors will be displayed on task cards with the existing glassmorphism design. The feature extends the existing `featureColor` pattern (used for feature tag badges) to include a new `taskColor` field for overall task card styling.

## Core Requirements

### Explicit Requirements

1. **Color Selection Interface**
   - Color picker component integrated into TaskEditModal
   - Support for preset color swatches (8 common colors)
   - Custom color input using HTML5 color picker
   - Clear/reset color functionality

2. **Data Persistence**
   - Add `taskColor` field to Task type (separate from existing `featureColor`)
   - Store color as hex string format (e.g., `#ef4444`)
   - Persist to database via existing flexible JSON schema
   - No database migration required (backend supports dynamic fields)

3. **Visual Display**
   - Apply task color to TaskCard component
   - Use alpha transparency for glassmorphism compatibility (e.g., `${taskColor}10` for background)
   - Support both light and dark modes
   - Complement existing priority indicator (left border), don't replace it

4. **User Experience**
   - Color picker should match Tron-inspired glassmorphism design
   - No performance degradation with colored tasks
   - Intuitive UI that doesn't disrupt existing workflows
   - Colors persist across sessions and views

### Implicit Requirements

1. **Type Safety**
   - Update TypeScript interfaces in `task.ts`
   - Include `taskColor?: string` in CreateTaskRequest and UpdateTaskRequest
   - Maintain consistency with existing featureColor pattern

2. **State Management**
   - Use TanStack Query patterns for mutations
   - Implement optimistic updates with nanoid-based IDs
   - Follow existing `useTaskQueries` mutation patterns

3. **API Integration**
   - No new endpoints needed (existing PUT /api/projects/{id}/tasks/{task_id})
   - Backend automatically accepts new fields in flexible schema
   - Include taskColor in request payload

4. **Testing**
   - Unit tests for TaskColorPicker component
   - Integration tests for TaskCard color display
   - Test color persistence through mutation hooks

5. **Accessibility**
   - Proper ARIA labels for color picker
   - Keyboard navigation support
   - Visual indicators that work in high contrast modes

## Technical Components

### Data Models

**Task Type Extension** (`task.ts`):
```typescript
export interface Task {
  // ... existing fields ...
  featureColor?: string;    // Existing - for feature tag badges
  taskColor?: string;       // NEW - for overall task card styling
}

export interface CreateTaskRequest {
  // ... existing fields ...
  featureColor?: string;
  taskColor?: string;       // NEW
}

export interface UpdateTaskRequest {
  // ... existing fields ...
  featureColor?: string;
  taskColor?: string;       // NEW
}
```

**Color Picker Props**:
```typescript
interface TaskColorPickerProps {
  value?: string;                              // Current color (hex format)
  onChange: (color: string | undefined) => void;  // Callback with hex string or undefined
  label?: string;                              // Optional label text
  disabled?: boolean;                          // Disable picker during saves
}
```

### External Integrations

**Radix UI Popover** (already available):
- Location: `@radix-ui/react-popover`
- Pattern: Already used in ComboBox component (`combobox.tsx`)
- Usage: Dropdown container for color picker UI

**HTML5 Color Input**:
- Native `<input type="color">` for custom color selection
- Fallback to text input if not supported
- Browser handles color picker UI

**Existing UI Primitives**:
- Button component for color swatches
- Label component for form fields
- Glassmorphism utilities from `styles.ts`

### Core Logic

**Color Application Strategy**:
1. **Background Tint**: Apply taskColor with 10-20% opacity (`${taskColor}10`)
2. **Border Accent**: Subtle border color with 30-50% opacity (`${taskColor}30`)
3. **Box Shadow**: Glow effect for depth (`0 0 10px ${taskColor}20`)
4. **Fallback**: Use existing styles when no taskColor present

**Color Format**:
- Standard: 6-character hex with leading `#` (e.g., `#ef4444`)
- Validation: Regex pattern `/^#[0-9A-Fa-f]{6}$/`
- Storage: Stored as-is in database (no RGB conversion)

**Preset Colors** (8 common Tailwind colors):
```typescript
const PRESET_COLORS = [
  "#ef4444", // red-500
  "#f97316", // orange-500
  "#eab308", // yellow-500
  "#22c55e", // green-500
  "#06b6d4", // cyan-500
  "#3b82f6", // blue-500
  "#8b5cf6", // purple-500
  "#ec4899", // pink-500
];
```

### UI/CLI Requirements

**TaskColorPicker Component** (NEW):
- Radix Popover trigger (button showing current color or default state)
- Popover content with:
  - Grid of 8 preset color swatches (2x4 layout)
  - HTML5 color input for custom colors
  - "Clear Color" button to reset to undefined
- Glassmorphism styling matching existing primitives
- Hover effects and focus states

**TaskEditModal Integration** (MODIFIED):
- Add TaskColorPicker after existing Feature field
- Position in FormGrid with 2 columns (alongside Feature or Status)
- Label: "Task Color" or "Color"
- Store color in `localTask` state
- Include in save mutation payload

**TaskCard Display** (MODIFIED):
- Conditional inline styles when taskColor present
- Apply to main card container (lines 159-161 in current implementation)
- Preserve existing glassmorphism base styles
- Maintain priority indicator (left border)

## Similar Implementations Found in Archon

### 1. Radix Popover Pattern - ComboBox Component
- **Relevance**: 9/10
- **Location**: `archon-ui-main/src/features/ui/primitives/combobox.tsx`
- **Key Patterns**:
  - Popover.Root/Trigger/Portal/Content structure
  - Glassmorphism styling with backdrop-blur
  - Focus management with requestAnimationFrame
  - Keyboard navigation (Enter, Escape, Tab)
- **Reusable Code**:
  ```typescript
  <Popover.Root open={open} onOpenChange={setOpen}>
    <Popover.Trigger asChild>
      <Button variant="ghost" className="...glassmorphism...">
        {/* Trigger content */}
      </Button>
    </Popover.Trigger>
    <Popover.Portal>
      <Popover.Content className="...glassmorphism..." sideOffset={4}>
        {/* Picker content */}
      </Popover.Content>
    </Popover.Portal>
  </Popover.Root>
  ```
- **Gotchas**:
  - Must use `onOpenAutoFocus={(e) => e.preventDefault()}` to prevent focus issues
  - Need `e.stopPropagation()` on click handlers to prevent event bubbling
  - Use `asChild` prop to merge button props properly

### 2. Feature Color Pattern - TaskCard Implementation
- **Relevance**: 10/10
- **Location**: `archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx` (lines 171-182)
- **Key Patterns**:
  ```typescript
  {task.feature && (
    <div
      className="px-2 py-1 rounded-md text-xs font-medium backdrop-blur-md"
      style={{
        backgroundColor: `${task.featureColor}20`,  // 20% opacity
        color: task.featureColor,
        boxShadow: `0 0 10px ${task.featureColor}20`,
      }}
    >
      <Tag className="w-3 h-3" />
      {task.feature}
    </div>
  )}
  ```
- **Reusable Code**: Exact pattern for applying taskColor to card container
- **Gotchas**:
  - Alpha values in hex format (e.g., `20` = 12.5% opacity in CSS)
  - Must work with existing glassmorphism gradients
  - Test in both light and dark modes

### 3. Form Field Integration - TaskEditModal
- **Relevance**: 8/10
- **Location**: `archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx`
- **Key Patterns**:
  - FormField wrapper with Label component
  - FormGrid for 2-column layout (lines 119-159)
  - Local state management with `setLocalTask`
  - Memoized change handlers with useCallback
- **Reusable Code**:
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
  </FormGrid>
  ```
- **Gotchas**:
  - Must handle `undefined` for clearing color
  - Preserve null-safety with `prev ? { ...prev } : null` pattern
  - No need to memoize onChange since TaskColorPicker is stable

### 4. TanStack Query Mutation Pattern - useTaskQueries
- **Relevance**: 10/10
- **Location**: `archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts`
- **Key Patterns**:
  - Optimistic updates with `createOptimisticEntity` / `replaceOptimisticEntity`
  - Query key factories (`taskKeys`)
  - Mutation with onMutate/onError/onSuccess lifecycle
- **Reusable Code**: Existing mutations already include all Task fields
- **Gotchas**:
  - No changes needed to mutation hooks (taskColor passes through automatically)
  - Backend flexible schema accepts new fields without schema changes
  - Must include taskColor in type definitions only

### 5. Dropdown Menu Glassmorphism - dropdown-menu.tsx
- **Relevance**: 7/10
- **Location**: `archon-ui-main/src/features/ui/primitives/dropdown-menu.tsx`
- **Key Patterns**:
  - `glassmorphism.background.strong` for content
  - `glassmorphism.border.default` for borders
  - `glassmorphism.shadow.lg` for elevation
  - Animation classes for open/close states
- **Reusable Code**:
  ```typescript
  className={cn(
    "rounded-lg p-1",
    glassmorphism.background.strong,
    glassmorphism.border.default,
    glassmorphism.shadow.lg,
    "data-[state=open]:animate-in data-[state=closed]:animate-out",
  )}
  ```
- **Gotchas**:
  - Import `glassmorphism` from `./styles`
  - Combine with `cn()` utility for conditional classes

## Recommended Technology Stack

Based on existing codebase patterns and Archon architecture:

### Framework & Libraries
- **React 18**: Existing framework (hooks, memo, forwardRef)
- **TypeScript 5**: Strict type checking
- **Radix UI Popover**: Already installed (`@radix-ui/react-popover`)
- **Tailwind CSS**: Styling with glassmorphism utilities
- **TanStack Query v5**: State management (no changes needed)

### UI Components (Already Available)
- **Button**: `archon-ui-main/src/features/ui/primitives/button.tsx`
- **Label**: `archon-ui-main/src/features/ui/primitives/`
- **FormField/FormGrid**: Used in TaskEditModal
- **Glassmorphism utilities**: `archon-ui-main/src/features/ui/primitives/styles.ts`

### Testing
- **Vitest**: Unit test framework (already configured)
- **React Testing Library**: Component testing
- **@testing-library/user-event**: User interaction simulation

### Backend
- **No changes required**: FastAPI backend with flexible JSON schema
- **Python 3.12**: Existing backend
- **Supabase**: Database with JSONB support

## Assumptions Made

### 1. **Color Storage Format**: Hex strings
- **Assumption**: Store colors as 6-character hex strings (e.g., `#ef4444`)
- **Reasoning**:
  - Matches existing featureColor pattern
  - CSS-native format (no conversion needed)
  - Compact storage (7 bytes)
  - Human-readable in database
- **Source**: TaskCard.tsx lines 174-177 (featureColor usage)

### 2. **Database Schema Flexibility**: No migration needed
- **Assumption**: Backend accepts taskColor field without schema changes
- **Reasoning**:
  - INITIAL.md states "backend uses flexible schema"
  - Python FastAPI services use Pydantic with extra fields allowed
  - Archon patterns show dynamic field support
- **Source**: INITIAL.md lines 116-117, backend architecture

### 3. **Color Application Strategy**: Background tint + border accent
- **Assumption**: Apply color with 10-20% opacity to background, 30-50% to border
- **Reasoning**:
  - Maintains glassmorphism aesthetic
  - Doesn't overpower existing priority indicators
  - Provides visual distinction without being garish
  - Matches featureColor badge pattern (line 175: `${task.featureColor}20`)
- **Source**: INITIAL.md lines 99-101, TaskCard.tsx lines 174-177

### 4. **Preset Colors**: 8 Tailwind colors
- **Assumption**: Provide 8 preset colors matching Tailwind's 500-series palette
- **Reasoning**:
  - Common, recognizable color palette
  - Covers major color categories (red, orange, yellow, green, cyan, blue, purple, pink)
  - Consistent with Tron theme (includes cyan)
  - Easy to extend if needed
- **Source**: Best practice from design systems, Tailwind documentation

### 5. **Component Placement**: After Feature field in FormGrid
- **Assumption**: Place TaskColorPicker in same FormGrid row as Feature field
- **Reasoning**:
  - Both are optional styling fields
  - Logical grouping (visual customization together)
  - Maintains 2-column layout consistency
  - Doesn't push critical fields below fold
- **Source**: TaskEditModal.tsx lines 161-187 (FormGrid structure)

### 6. **Clear Color UX**: Button in popover, sets to undefined
- **Assumption**: Include "Clear Color" button that sets taskColor to undefined
- **Reasoning**:
  - Users need way to remove color once set
  - undefined vs null semantics (optional field)
  - Matches pattern: featureColor is optional
  - Better UX than having to select "no color" preset
- **Source**: INITIAL.md line 18 ("Remove/reset colors back to default styling")

### 7. **Performance**: No special optimization needed
- **Assumption**: Inline styles for taskColor won't cause performance issues
- **Reasoning**:
  - Modern React efficiently handles inline styles
  - Color only changes on user action (infrequent)
  - No complex calculations or animations
  - Existing featureColor uses inline styles without issues
- **Source**: TaskCard.tsx performance characteristics, INITIAL.md line 27

### 8. **Validation**: Minimal - rely on HTML5 color input
- **Assumption**: No complex color validation beyond hex format check
- **Reasoning**:
  - HTML5 color input always returns valid hex
  - Preset colors are hardcoded and valid
  - Database accepts any string (no schema constraint)
  - Invalid colors simply won't display (fail gracefully)
- **Source**: Best practice for progressive enhancement

### 9. **Accessibility**: Basic ARIA labels sufficient
- **Assumption**: Standard ARIA labels and roles meet accessibility requirements
- **Reasoning**:
  - Radix UI provides baseline accessibility
  - Color picker is enhancement, not critical feature
  - Task title/description remain primary content
  - Follow existing ComboBox ARIA patterns
- **Source**: combobox.tsx ARIA implementation (lines 242-256)

### 10. **Backend Compatibility**: Python service auto-handles new field
- **Assumption**: Task service and API routes require no modifications
- **Reasoning**:
  - Pydantic models in FastAPI allow extra fields by default
  - Supabase JSONB columns accept any valid JSON
  - Similar pattern used for featureColor addition
  - No validation rules needed for optional color string
- **Source**: INITIAL.md lines 166-171, Archon backend architecture

## Success Criteria

Based on INITIAL.md (lines 21-27) and inferred from requirements:

### Functional Criteria
1. ✅ Users can select a color from preset swatches OR enter custom hex color
2. ✅ Selected color persists to database and survives page refresh
3. ✅ Task cards display selected color with glassmorphism styling
4. ✅ Color can be cleared/reset to default (undefined state)
5. ✅ Color picker UI matches Tron glassmorphism design
6. ✅ No TypeScript errors or linting issues

### Technical Criteria
7. ✅ No performance degradation (measured via React DevTools profiler)
8. ✅ Works in both light and dark modes
9. ✅ All unit tests pass (TaskColorPicker component)
10. ✅ Integration tests pass (TaskCard color display)
11. ✅ Biome checks pass (`npm run biome`)
12. ✅ TypeScript compiles without errors (`npx tsc --noEmit`)

### UX Criteria
13. ✅ Color picker opens/closes smoothly (no layout shift)
14. ✅ Keyboard navigation works (Enter, Escape, Tab)
15. ✅ Visual feedback on hover/focus states
16. ✅ Color complements priority indicator (doesn't replace or clash)
17. ✅ Intuitive "Clear Color" action

### Quality Criteria
18. ✅ Code follows existing patterns (Radix UI, glassmorphism)
19. ✅ No breaking changes to existing features
20. ✅ Accessible (ARIA labels, keyboard support)

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus on:**
1. Examine `combobox.tsx` for complete Popover pattern (focus management, keyboard nav)
2. Review `TaskCard.tsx` lines 159-165 for card container styling injection point
3. Study `useTaskQueries.ts` mutation lifecycle (confirm no changes needed)
4. Inspect `styles.ts` for available glassmorphism utilities
5. Check `TaskEditModal.tsx` FormGrid layout pattern (lines 119-187)

**Specific questions to answer:**
- What's the exact import path for Radix Popover?
- Are there any existing color-related utilities in the codebase?
- How does optimistic update handle undefined fields?

### Documentation Hunter
**Find docs for:**
1. Radix UI Popover API (open/onOpenChange, Trigger, Content props)
2. HTML5 color input browser support and fallback strategies
3. CSS alpha transparency patterns (hex + opacity suffix)
4. React Testing Library - testing Popover components
5. Vitest - mocking inline styles in tests

**Priority sources:**
- Radix UI official documentation
- MDN Web Docs for `<input type="color">`
- Existing test files in `archon-ui-main/src/features/*/tests/`

### Example Curator
**Extract examples showing:**
1. **Popover with custom content**: Full ComboBox implementation (combobox.tsx)
2. **Inline style application**: TaskCard featureColor pattern (TaskCard.tsx:174-177)
3. **Form field integration**: Any FormField usage in TaskEditModal
4. **Glassmorphism styling**: DropdownMenu content styles (dropdown-menu.tsx:15-42)
5. **Mutation payload inclusion**: useTaskQueries create/update mutations

**Format as:**
- Code snippets with line numbers
- Before/after examples
- Common pitfalls and solutions

### Gotcha Detective
**Investigate:**
1. **Radix Popover z-index conflicts**: Check if existing modals/dropdowns clash
2. **Focus trap issues**: Popover inside Dialog (TaskEditModal) - does focus work correctly?
3. **Optimistic update edge cases**: What happens when taskColor is undefined?
4. **Dark mode color visibility**: Test all 8 preset colors in dark mode
5. **Color input browser support**: Safari/Firefox/Chrome differences
6. **Inline style specificity**: Can Tailwind classes override inline styles?
7. **FormGrid responsiveness**: Does 2-column layout break on mobile?

**Document findings:**
- Browser compatibility matrix
- Recommended workarounds
- Testing strategies for each gotcha

---

## Implementation Roadmap

### Phase 1: Type Definitions (15 min)
- Add `taskColor?: string` to Task, CreateTaskRequest, UpdateTaskRequest
- No migration or backend changes needed
- Run TypeScript checks to verify

### Phase 2: TaskColorPicker Component (2 hours)
- Create new component using Radix Popover
- Implement preset swatches (2x4 grid)
- Add HTML5 color input for custom colors
- Add "Clear Color" button
- Apply glassmorphism styling
- Add keyboard navigation (Enter, Escape)
- Write unit tests

### Phase 3: TaskEditModal Integration (30 min)
- Add TaskColorPicker to FormGrid
- Wire up onChange handler
- Include in save payload
- Test modal interaction

### Phase 4: TaskCard Display (1 hour)
- Add conditional styling to card container
- Apply background tint and border accent
- Test with various colors in light/dark modes
- Ensure priority indicator remains visible
- Write display tests

### Phase 5: Testing & Validation (1 hour)
- Run all tests (`npm run test`)
- Check TypeScript (`npx tsc --noEmit`)
- Run Biome checks (`npm run biome`)
- Manual QA in browser (light/dark mode)
- Test keyboard navigation
- Verify persistence (page refresh)

**Total Estimated Time**: 5 hours
**Risk Level**: Low (extends existing patterns, no breaking changes)
**Dependencies**: None (all libraries already available)

---

## File Modification Summary

### New Files (1)
- `archon-ui-main/src/features/projects/tasks/components/TaskColorPicker.tsx`
- `archon-ui-main/src/features/projects/tasks/components/tests/TaskColorPicker.test.tsx`

### Modified Files (4)
- `archon-ui-main/src/features/projects/tasks/types/task.ts` (add taskColor field)
- `archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx` (integrate picker)
- `archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx` (display color)
- `archon-ui-main/src/features/projects/tasks/components/tests/TaskCard.test.tsx` (add color tests)

### No Changes Needed (Backend)
- Task service automatically accepts new field
- No API route modifications
- No database migration

---

## Confidence Assessment

**Overall Confidence**: 95%

**High Confidence Areas** (95-100%):
- Type definitions (exact pattern exists)
- TaskCard color display (identical to featureColor)
- Form integration (straightforward FormField addition)
- Mutation hooks (no changes needed)
- Backend compatibility (flexible schema confirmed)

**Medium Confidence Areas** (80-90%):
- Popover implementation details (need to verify focus management)
- Color picker UX (preset grid layout needs refinement)
- Dark mode color visibility (needs testing)

**Low Risk Areas**:
- Performance (inline styles are efficient)
- Browser compatibility (HTML5 color widely supported)
- Accessibility (Radix provides baseline)

**Recommendations**:
1. Prototype TaskColorPicker quickly to validate Popover patterns
2. Test all preset colors in dark mode early
3. Consider adding color name tooltips for accessibility
4. Document color format expectations in component JSDoc

---

## Appendix: Quick Reference

### Key File Locations
- **Types**: `archon-ui-main/src/features/projects/tasks/types/task.ts`
- **TaskCard**: `archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx`
- **TaskEditModal**: `archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx`
- **Primitives**: `archon-ui-main/src/features/ui/primitives/`
- **Query Hooks**: `archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts`

### Color Format Examples
- **Preset Red**: `#ef4444`
- **Background Tint**: `backgroundColor: '#ef444410'` (10% opacity)
- **Border Accent**: `borderColor: '#ef444430'` (30% opacity)
- **Box Shadow**: `boxShadow: '0 0 10px #ef444420'` (20% opacity)

### Testing Commands
```bash
# TypeScript check
npx tsc --noEmit 2>&1 | grep "src/features/projects/tasks"

# Biome lint/format
npm run biome:fix

# Run task tests
npm run test src/features/projects/tasks

# Run specific test file
npm run test TaskColorPicker.test.tsx
```

### Useful Patterns
```typescript
// Conditional inline styles
style={{
  ...(taskColor && {
    backgroundColor: `${taskColor}10`,
    borderColor: `${taskColor}30`,
    boxShadow: `0 0 10px ${taskColor}20`,
  }),
}}

// Optional field update
setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null))

// Clear color (set to undefined)
onChange(undefined)
```
