# Task Manager Header Redesign - Code Examples

## Overview

Extracted 5 code examples demonstrating the exact patterns needed for fixing the task manager header layout and implementing a working dark mode toggle. These examples are taken from working implementations in the codebase, showing both the current state and the target patterns.

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| example_1_tailwind_darkmode_config.js | infra/archon/archon-ui-main/tailwind.config.js | Tailwind dark mode setup | 10/10 |
| example_2_theme_context_pattern.tsx | infra/task-manager/frontend/src/contexts/ThemeContext.tsx | React Context for theme | 9/10 |
| example_3_theme_toggle_component.tsx | infra/task-manager/frontend/src/components/ThemeToggle.tsx | Toggle button UI | 9/10 |
| example_4_header_layout_pattern.tsx | infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx | Header layout (current) | 10/10 |
| example_5_alternative_theme_toggle.tsx | infra/archon/archon-ui-main/src/components/ui/ThemeToggle.tsx | Alternative styling | 6/10 |

---

## Example 1: Tailwind Dark Mode Configuration

**File**: `example_1_tailwind_darkmode_config.js`
**Source**: infra/archon/archon-ui-main/tailwind.config.js
**Relevance**: 10/10 - **THIS IS THE CRITICAL FIX**

### What to Mimic

- **Add darkMode property**: This single line enables class-based dark mode
  ```javascript
  darkMode: "selector",  // Enables dark: variants via .dark class on html element
  ```

- **Configuration structure**: The minimal config needed
  ```javascript
  module.exports = {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    darkMode: "selector",  // ← THE KEY FIX
    theme: { extend: {} },
    plugins: [],
  }
  ```

### What to Adapt

- **Keep existing content paths**: Don't change the content array
- **Preserve existing theme extensions**: Keep any custom colors or spacing
- **Add darkMode property only**: Just insert the one line needed

### What to Skip

- **Custom color system**: The Archon example has extensive HSL color variables - task-manager doesn't need these
- **Container configuration**: Task-manager doesn't use Tailwind containers
- **Custom animations**: Archon's keyframes and animations are specific to its UI

### Pattern Highlights

```javascript
// THE ENTIRE FIX for dark mode:
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: "selector",  // ← Just add this one line!
  theme: { extend: {} },
  plugins: [],
}

// This enables ALL dark: variants to work when .dark class is on <html>
// Example: dark:bg-gray-900, dark:text-white, etc.
```

### Why This Example

**This is the root cause of the theme toggle not working.** Without `darkMode: "selector"` in the Tailwind config, all `dark:` classes in the codebase are ignored during compilation. The ThemeContext correctly adds/removes the "dark" class, but Tailwind doesn't know to look for it. Adding this one line will instantly fix the theme toggle functionality.

**After adding this**: You MUST restart the dev server for Tailwind to recompile with the new configuration.

---

## Example 2: Theme Context Pattern

**File**: `example_2_theme_context_pattern.tsx`
**Source**: infra/task-manager/frontend/src/contexts/ThemeContext.tsx (current implementation)
**Relevance**: 9/10

### What to Mimic

- **Two-useEffect pattern**: Separate initialization from updates
  ```typescript
  // Effect 1: Initialize from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored === "dark" || stored === "light") {
      setTheme(stored);
    }
  }, []);

  // Effect 2: Apply theme changes and persist
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);
  ```

- **Type-safe theme values**: Use literal types
  ```typescript
  type Theme = "light" | "dark";  // Not string!
  ```

- **Guard clause for useTheme hook**: Enforce provider usage
  ```typescript
  export function useTheme() {
    const context = useContext(ThemeContext);
    if (context === undefined) {
      throw new Error("useTheme must be used within a ThemeProvider");
    }
    return context;
  }
  ```

### What to Adapt

- **Default theme**: Currently "light", could be "dark" or system preference
- **localStorage key**: Currently "theme", could be "task-manager-theme" for namespacing
- **Validation logic**: Could add system preference detection

### What to Skip

- Nothing - this implementation is already correct and in use

### Pattern Highlights

```typescript
// The key insight: Separate concerns with two effects

// ✅ GOOD: Initialize once on mount
useEffect(() => {
  const stored = localStorage.getItem("theme") as Theme | null;
  if (stored === "dark" || stored === "light") {
    setTheme(stored);  // Only set if valid value exists
  }
}, []); // Empty deps = runs once on mount

// ✅ GOOD: React to theme changes
useEffect(() => {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem("theme", theme);
}, [theme]); // Runs whenever theme changes

// ❌ BAD: Combining both in one effect causes infinite loops
```

### Why This Example

This pattern correctly handles the race condition between localStorage initialization and theme application. It also prevents infinite re-renders by separating the initialization logic from the update logic. **This implementation is already correct** - the issue is purely in the Tailwind config, not the React code.

---

## Example 3: Theme Toggle Component

**File**: `example_3_theme_toggle_component.tsx`
**Source**: infra/task-manager/frontend/src/components/ThemeToggle.tsx (current implementation)
**Relevance**: 9/10

### What to Mimic

- **Icon switching logic**: Conditional rendering based on theme
  ```typescript
  {theme === "light" ? (
    <Moon className="w-5 h-5 text-gray-700" aria-hidden="true" />
  ) : (
    <Sun className="w-5 h-5 text-gray-300" aria-hidden="true" />
  )}
  ```

- **Comprehensive dark mode classes**: Every state has light and dark variants
  ```typescript
  className="
    p-2 rounded-lg
    bg-gray-200 dark:bg-gray-700
    hover:bg-gray-300 dark:hover:bg-gray-600
    focus:ring-blue-500 dark:focus:ring-blue-400
    focus:ring-offset-2 dark:focus:ring-offset-gray-900
  "
  ```

- **Accessibility attributes**: ARIA labels and titles
  ```typescript
  aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
  title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
  ```

- **Icon accessibility**: aria-hidden on decorative icons
  ```typescript
  <Moon className="w-5 h-5" aria-hidden="true" />
  ```

### What to Adapt

- **Button styling**: Could match project design system
- **Icon size**: Currently w-5 h-5, could be larger/smaller
- **Transition timing**: Currently duration-200, could adjust

### What to Skip

- Nothing - this is a minimal, correct implementation

### Pattern Highlights

```typescript
// Key pattern: Every visual state needs dark: variant

// ✅ GOOD: Paired light/dark classes
bg-gray-200 dark:bg-gray-700          // Background
hover:bg-gray-300 dark:hover:bg-gray-600  // Hover state
focus:ring-blue-500 dark:focus:ring-blue-400  // Focus ring

// ❌ BAD: Missing dark variants
bg-gray-200  // No dark mode equivalent!

// ✅ GOOD: Descriptive ARIA labels that change with state
aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}

// ❌ BAD: Static label
aria-label="Toggle theme"  // Not descriptive enough
```

### Why This Example

This component demonstrates the correct onClick handler binding and comprehensive dark mode styling. **The component itself works perfectly** - it calls `toggleTheme()` correctly. The issue is that without the Tailwind `darkMode` config, all the `dark:` classes are compiled away and do nothing.

---

## Example 4: Header Layout Pattern (CURRENT STATE)

**File**: `example_4_header_layout_pattern.tsx`
**Source**: infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx (lines 117-149)
**Relevance**: 10/10 - **THIS SHOWS WHAT NEEDS TO CHANGE**

### What to Mimic

- **Flex justify-between pattern**: For left/right positioning
  ```tsx
  <div className="mb-6 flex items-center justify-between">
    <div>{/* Left content */}</div>
    <div>{/* Right content */}</div>
  </div>
  ```

- **Semantic heading hierarchy**: h1 for main title, h2 for section headers
- **Consistent spacing**: mb-6 for section separation

### What to Adapt

- **ProjectSelector placement**: MOVE from header row to sub-header section
  ```tsx
  // ❌ CURRENT (Wrong):
  <div className="flex items-center justify-between">
    <div>Title</div>
    <div className="flex gap-4">
      <ProjectSelector />  {/* Should NOT be here */}
      <ThemeToggle />
    </div>
  </div>

  // ✅ DESIRED (Correct):
  <div className="flex items-center justify-between">
    <div>Title</div>
    <ThemeToggle />  {/* Only toggle in header */}
  </div>

  <div className="mb-6">
    <ProjectSelector />  {/* Moved here, replaces h2 */}
    <p>Task count</p>
  </div>
  ```

- **Remove "Kanban Board" h2**: Replace with ProjectSelector component

### What to Skip

- **Task count display**: Keep this, it's useful
- **Column grid**: No changes needed to the Kanban columns

### Pattern Highlights

```tsx
// BEFORE (Current - lines 119-149):
<div className="mb-6 flex items-center justify-between">
  <div>
    <h1>Task Management</h1>
    <p>subtitle</p>
  </div>
  <div className="flex items-center gap-4">
    <ProjectSelector />  {/* ❌ Wrong location */}
    <ThemeToggle />
  </div>
</div>
<div className="mb-6">
  <h2>Kanban Board</h2>  {/* ❌ Should be removed */}
  <p>0 tasks total</p>
</div>

// AFTER (Target):
<div className="mb-6 flex items-center justify-between">
  <div>
    <h1>Task Management</h1>
    <p>subtitle</p>
  </div>
  <ThemeToggle />  {/* ✅ Only toggle here */}
</div>
<div className="mb-6">
  <ProjectSelector />  {/* ✅ Moved here */}
  <p>0 tasks total</p>
</div>
```

### Why This Example

This shows the **exact code that needs to be changed** for the layout fix. The restructure is purely JSX reorganization - no logic changes needed. The ProjectSelector component works fine, it just needs to move to a different position in the render tree.

---

## Example 5: Alternative Theme Toggle (OPTIONAL)

**File**: `example_5_alternative_theme_toggle.tsx`
**Source**: infra/archon/archon-ui-main/src/components/ui/ThemeToggle.tsx
**Relevance**: 6/10 - Optional inspiration for future styling

### What to Mimic

- **Accent color system**: Configurable color variants
- **Glassmorphism effect**: backdrop-blur-md for modern UI
- **Gradient backgrounds**: bg-gradient-to-b with multiple stops

### What to Adapt

- Everything - this is just inspiration, not a direct pattern to copy

### What to Skip

- **Complexity**: Task-manager doesn't need accent color system
- **Advanced styling**: Current simple toggle is fine for MVP

### Pattern Highlights

```typescript
// Advanced pattern: Configurable theming
const accentColorMap = {
  blue: {
    border: 'border-blue-300 dark:border-blue-500/30',
    hover: 'hover:border-blue-400 dark:hover:border-blue-500/60',
    text: 'text-blue-600 dark:text-blue-500',
    bg: 'from-blue-100/80 to-blue-50/60 dark:from-white/10 dark:to-black/30'
  },
  // ... more colors
};

// Apply dynamically
className={`${accentColorMap[accentColor].bg} ${accentColorMap[accentColor].border}`}
```

### Why This Example

Included as **optional inspiration** for future improvements. The current simple toggle (Example 3) is perfectly fine. This shows how to add more sophisticated styling if/when the design system evolves.

---

## Usage Instructions

### Study Phase

1. **Start with Example 1** - Understand the Tailwind config fix (most critical)
2. **Read Example 4** - Identify exact JSX changes needed for layout
3. **Review Examples 2-3** - Understand current implementation (already correct)
4. **Optionally review Example 5** - Future styling inspiration

### Application Phase

1. **Fix 1: Tailwind Config** (Example 1)
   - Open `tailwind.config.js`
   - Add `darkMode: "selector",` after content array
   - Restart dev server

2. **Fix 2: Layout Restructure** (Example 4)
   - Open `KanbanBoard.tsx`
   - Move `<ProjectSelector />` from lines 131-136 to line 142 area
   - Remove `<h2>Kanban Board</h2>` at line 143-145
   - Keep ThemeToggle in header (line 137)

3. **Verify**
   - Theme toggle should now work (click it, see colors change)
   - Layout should match mockup (ProjectSelector below title)

### Testing Patterns

#### Manual Testing Checklist

```bash
# 1. Verify Tailwind config
cat tailwind.config.js | grep darkMode
# Expected: darkMode: "selector",

# 2. Test theme toggle
# - Click toggle button
# - Verify background/text colors change
# - Refresh page
# - Verify theme persists

# 3. Test layout
# - Verify "Task Management" on left, toggle on right (same row)
# - Verify ProjectSelector below title (not in header row)
# - Verify "Kanban Board" h2 is gone
```

#### Browser DevTools Verification

```javascript
// Open console, click theme toggle, run:
document.documentElement.classList.contains('dark')
// Should return true in dark mode, false in light mode

// Check localStorage:
localStorage.getItem('theme')
// Should return "dark" or "light"

// Verify dark classes apply:
document.querySelector('body').className
// Should include dark: variant classes when in dark mode
```

---

## Pattern Summary

### Common Patterns Across Examples

1. **Tailwind Dark Mode Strategy**: Class-based via `darkMode: "selector"`
   - Requires config change to enable
   - All components use `dark:` prefix for dark mode styles
   - Class applied to `document.documentElement`

2. **React Context Pattern**: Separate initialization from updates
   - One useEffect for localStorage initialization (runs once)
   - One useEffect for theme application (runs on change)
   - Guard clauses enforce provider usage

3. **Component Composition**: Flex layouts with justify-between
   - Left content in first div
   - Right content in second div
   - Parent has `flex items-center justify-between`

4. **Accessibility First**: Comprehensive ARIA attributes
   - aria-label on interactive elements
   - aria-hidden on decorative icons
   - Title attributes for tooltips
   - Focus visible states

### Anti-Patterns Observed

1. **Missing Tailwind Config**: Example 1 shows the fix for this anti-pattern
   - Without `darkMode: "selector"`, dark: classes do nothing
   - Silent failure - no errors, just non-functional styling

2. **Wrong Component Placement**: Example 4 shows current anti-pattern
   - ProjectSelector in header instead of sub-header
   - Creates visual hierarchy mismatch

3. **Combined useEffect**: Not shown, but avoid this
   - Don't combine initialization and updates in one effect
   - Causes infinite loops and unnecessary re-renders

---

## Integration with PRP

These examples should be:

1. **Referenced** in PRP "All Needed Context" section
   - Point to this examples directory
   - Highlight Example 1 (Tailwind config) as critical

2. **Studied** before implementation
   - Developer should read Examples 1 and 4 first
   - Then verify Examples 2-3 match current code

3. **Adapted** for the specific feature needs
   - Tailwind config: Copy Example 1 darkMode line exactly
   - Layout: Restructure per Example 4 pattern
   - Theme components: Keep as-is (already correct)

4. **Extended** if additional patterns emerge
   - Example 5 available for future UI polish
   - Pattern library can grow with more examples

---

## Source Attribution

### From Local Codebase

**Working Implementation (Archon)**:
- `infra/archon/archon-ui-main/tailwind.config.js` - Dark mode config ✅
- `infra/archon/archon-ui-main/src/contexts/ThemeContext.tsx` - Alternative Context pattern
- `infra/archon/archon-ui-main/src/components/ui/ThemeToggle.tsx` - Fancy toggle variant

**Current Implementation (Task Manager - Needs Fix)**:
- `infra/task-manager/frontend/tailwind.config.js` - Missing darkMode ❌
- `infra/task-manager/frontend/src/contexts/ThemeContext.tsx` - Context (correct) ✅
- `infra/task-manager/frontend/src/components/ThemeToggle.tsx` - Toggle (correct) ✅
- `infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx` - Layout (wrong) ❌

### From Archon (Not Directly Used)

No relevant examples found in Archon knowledge base for this specific use case. All examples are from local codebase self-reference.

---

## Quick Reference: The Two Fixes Needed

### Fix 1: Tailwind Config (2 minutes)

```javascript
// File: tailwind.config.js
// Add this one line after content array:
darkMode: "selector",
```

**Then restart dev server**: `npm run dev` or equivalent

### Fix 2: Layout Restructure (5 minutes)

```tsx
// File: KanbanBoard.tsx

// BEFORE:
<div className="flex items-center justify-between">
  <div>Title</div>
  <div className="flex gap-4">
    <ProjectSelector />  {/* ❌ Remove from here */}
    <ThemeToggle />
  </div>
</div>
<div className="mb-6">
  <h2>Kanban Board</h2>  {/* ❌ Remove this */}
  <p>Task count</p>
</div>

// AFTER:
<div className="flex items-center justify-between">
  <div>Title</div>
  <ThemeToggle />  {/* ✅ Only toggle here */}
</div>
<div className="mb-6">
  <ProjectSelector />  {/* ✅ Moved here */}
  <p>Task count</p>
</div>
```

---

Generated: 2025-10-10
Feature: task_manager_header_redesign
Total Examples: 5
Quality Score: 9/10

**Coverage**: Examples cover all required patterns (Tailwind config, React Context, theme toggle, layout restructure)
**Relevance**: All examples directly applicable to the feature requirements
**Completeness**: Each example is runnable/studyable with full context
**Overall**: High-quality example set with clear guidance on what to change
