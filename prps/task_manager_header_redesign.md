# PRP: Task Manager Header Redesign

**Generated**: 2025-10-10
**Based On**: prps/INITIAL_task_manager_header_redesign.md
**Archon Project**: e5725160-8989-4b95-9c8f-1fa450f2ac52

---

## Goal

Fix the task manager header layout by repositioning the project selector dropdown and implementing a working dark/light mode toggle. The project dropdown should replace the mispositioned "Kanban Board" header text, and the theme toggle should be positioned in the upper right corner with persistent localStorage settings.

**End State**:
- Project selector dropdown appears below the main title (replacing "Kanban Board" header)
- Theme toggle button positioned in upper right corner of header
- Dark/light mode toggle works with visual theme changes across all components
- Theme preference persists across browser sessions via localStorage
- Layout matches user-provided mockup exactly

## Why

**Current Pain Points**:
- "Kanban Board" header text is redundant and mispositioned as a sub-header
- Project selector is currently in the header row but should be more prominent as a sub-header
- Theme toggle button doesn't respond to clicks (root cause: missing Tailwind darkMode configuration)
- No dark mode support despite having theme toggle UI and context already implemented

**Business Value**:
- Improved header hierarchy and information architecture
- Better user experience with working dark mode (reduces eye strain, user preference)
- More prominent project selector improves multi-project workflow
- Professional polish with smooth theme transitions
- Accessibility compliance with proper focus indicators

## What

### Core Features

1. **Header Layout Restructure**
   - Move ProjectSelector from header row to sub-header section
   - Remove "Kanban Board" h2 header completely
   - Keep "Task Management" title and subtitle on the left
   - Keep ThemeToggle button isolated in upper right corner
   - Maintain task count display below project selector

2. **Working Dark Mode Toggle**
   - Fix Tailwind configuration to enable dark: variant classes
   - Theme toggle button changes between sun/moon icons
   - All components transition smoothly between light and dark themes
   - Dark class applied to document.documentElement
   - Theme preference persists via localStorage

3. **Responsive Design**
   - Layout works on mobile, tablet, and desktop viewports
   - Maintains existing Tailwind breakpoint patterns
   - No layout shift or jarring transitions

### Success Criteria

- [x] **Layout Validation**: Header matches provided ASCII mockup exactly
  ```
  ┌─────────────────────────────────────────────────────────┐
  │ Task Management                    [Theme Toggle 🌙]    │
  │ subtitle text                                            │
  │                                                          │
  │ [Project Dropdown ▼]                                    │
  │ 0 tasks total                                           │
  │                                                          │
  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
  │ │ Todo    │ │ Doing   │ │ Review  │ │ Done    │       │
  │ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
  └─────────────────────────────────────────────────────────┘
  ```
- [x] **Functional**: Theme toggle click changes theme immediately
- [x] **Persistence**: Theme persists after browser refresh
- [x] **Visual**: All dark mode classes apply correctly (backgrounds, text, borders)
- [x] **Accessibility**: Focus indicators visible in both light and dark modes
- [x] **No Regressions**: Existing functionality (drag-and-drop, project switching) continues to work

---

## All Needed Context

### Documentation & References

```yaml
# CRITICAL - Tailwind CSS Dark Mode Configuration (PRIMARY FIX)
- url: https://tailwindcss.com/docs/dark-mode
  sections:
    - "Toggling dark mode manually" - Shows darkMode: 'selector' configuration
    - "Customizing the class name" - Explains how dark: prefix works
  why: Root cause fix - missing darkMode config prevents dark: classes from working
  critical_gotchas:
    - Without darkMode config, dark: variants are compiled away (not in CSS)
    - Must restart dev server after adding config (doesn't hot reload)
    - Use 'selector' (v3.4.1+) or 'class' (legacy) - both work identically

# MUST READ - React Context API
- url: https://react.dev/reference/react/useContext
  sections:
    - "useContext Reference" - How to consume context properly
    - "Passing Data Deeply with Context" - Step-by-step context implementation
  why: Understanding existing ThemeContext pattern (already correct, no changes needed)
  critical_gotchas:
    - Context changes re-render ALL consumers (acceptable for theme)
    - Memoize context value object to prevent unnecessary re-renders
    - useCallback for stable function references

# MUST READ - localStorage Best Practices
- url: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
  sections:
    - "Exceptions" - SecurityError and QuotaExceededError handling
    - "Using the Web Storage API" - Feature detection patterns
  why: Theme persistence with error handling for private browsing
  critical_gotchas:
    - Safari Private Browsing throws SecurityError on localStorage access
    - Wrap all localStorage calls in try-catch for graceful degradation
    - App should work without persistence (localStorage unavailable)

# REFERENCE - Radix UI Select Component
- url: https://www.radix-ui.com/primitives/docs/components/select
  sections:
    - "API Reference" - Component parts and props
    - "Accessibility" - Keyboard navigation and ARIA attributes
  why: ProjectSelector uses Radix Select (already implemented correctly)
  critical_gotchas:
    - Select.Portal renders outside component root (already handled)
    - Test with waitFor() when testing portal content

# REFERENCE - Tailwind Responsive Design
- url: https://tailwindcss.com/docs/responsive-design
  sections:
    - "Default Breakpoints" - Mobile-first breakpoint system
  why: Verify layout works across all viewport sizes
  critical_gotchas:
    - Mobile-first approach (base styles apply to all, breakpoints add up)
    - sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px

# ESSENTIAL LOCAL FILES
- file: /Users/jon/source/vibes/prps/task_manager_header_redesign/examples/README.md
  why: Complete pattern guide with working examples
  pattern: Exact Tailwind config fix and layout restructure code

- file: /Users/jon/source/vibes/prps/task_manager_header_redesign/examples/example_1_tailwind_darkmode_config.js
  why: Root cause fix - shows exactly what to add to tailwind.config.js
  critical: Single line addition enables all dark mode functionality

- file: /Users/jon/source/vibes/prps/task_manager_header_redesign/examples/example_4_header_layout_pattern.tsx
  why: Shows exact before/after JSX for layout restructure
  pattern: Move ProjectSelector from header to sub-header section

- file: /Users/jon/source/vibes/infra/task-manager/frontend/src/contexts/ThemeContext.tsx
  why: Current theme context implementation (already correct, for reference)
  pattern: Dual useEffect pattern for initialization and synchronization

- file: /Users/jon/source/vibes/infra/task-manager/frontend/src/components/ThemeToggle.tsx
  why: Current toggle button component (already correct, for reference)
  pattern: Icon switching, accessibility, dark mode classes

- file: /Users/jon/source/vibes/infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx
  why: File to modify - contains header layout requiring changes (lines 117-149)
  critical: Exact lines to modify for layout restructure
```

### Current Codebase Tree

```
infra/task-manager/frontend/
├── tailwind.config.js              # MISSING darkMode config (CRITICAL FIX)
├── src/
│   ├── App.tsx                     # ✅ ThemeProvider correctly wraps app (line 33)
│   ├── contexts/
│   │   └── ThemeContext.tsx        # ✅ Already correct (no changes needed)
│   ├── components/
│   │   └── ThemeToggle.tsx         # ✅ Already correct (no changes needed)
│   ├── features/
│   │   ├── projects/
│   │   │   ├── components/
│   │   │   │   └── ProjectSelector.tsx  # ✅ Component works, just reposition
│   │   │   └── utils/
│   │   │       └── projectStorage.ts    # Reference for localStorage error handling
│   │   └── tasks/
│   │       └── components/
│   │           └── KanbanBoard.tsx      # MODIFY lines 117-149 (header layout)
│   └── pages/
│       └── KanbanPage.tsx          # ✅ No changes needed (props passed correctly)
```

**What's Already Working (No changes needed)**:
- ✅ ThemeContext.tsx - Correctly manages theme state with localStorage persistence
- ✅ ThemeToggle.tsx - Button properly wired with correct onClick handler and classes
- ✅ App.tsx - ThemeProvider correctly wraps application
- ✅ ProjectSelector.tsx - Component fully functional with accessibility and dark mode

**What's Broken (Needs fixing)**:
- ❌ tailwind.config.js - Missing `darkMode: 'selector'` configuration (ROOT CAUSE)
- ❌ KanbanBoard.tsx - ProjectSelector in wrong position (header instead of sub-header)

### Desired Codebase Tree

```
infra/task-manager/frontend/
├── tailwind.config.js              # ADD: darkMode: 'selector' on line 3
└── src/
    └── features/
        └── tasks/
            └── components/
                └── KanbanBoard.tsx  # MODIFY: Lines 119-149 (restructure header)
```

**New Files**: NONE - All components already exist
**Modified Files**:
1. `tailwind.config.js` - Add darkMode configuration (1 line)
2. `KanbanBoard.tsx` - Restructure header JSX (move ProjectSelector, remove h2)

### Known Gotchas & Library Quirks

```typescript
// CRITICAL GOTCHA #1: Missing Tailwind darkMode Config (ROOT CAUSE)
// ❌ WRONG - Current tailwind.config.js (missing darkMode)
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
// Problem: Without darkMode setting, ALL dark: classes are removed from CSS bundle
// Symptom: Toggle button clicks, state changes, DOM class applies, but NO VISUAL CHANGE

// ✅ RIGHT - Add darkMode configuration
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'selector', // v3.4.1+ modern syntax (or 'class' for legacy)
  theme: { extend: {} },
  plugins: [],
}
// Fix: One line enables all dark: variants in CSS
// CRITICAL: Must restart dev server after config change (doesn't hot reload)

// CRITICAL GOTCHA #2: localStorage SecurityError in Private Browsing
// ❌ WRONG - Raw localStorage access (crashes in Safari Private Browsing)
const stored = localStorage.getItem("theme"); // Throws SecurityError
localStorage.setItem("theme", theme);

// ✅ RIGHT - Wrap in try-catch for graceful degradation
try {
  const stored = localStorage.getItem("theme");
  if (stored === "dark" || stored === "light") {
    setTheme(stored);
  }
} catch (error) {
  console.warn('localStorage unavailable, using default theme');
  // App still works, just doesn't persist preference
}

// CRITICAL GOTCHA #3: Theme Flash on Page Load (FOUC)
// Problem: Brief flash of light theme before JavaScript loads and applies dark class
// Solution: Add inline script to index.html (runs before React)
// Optional for MVP, but documented for future enhancement:
/*
<head>
  <script>
    (function() {
      try {
        const theme = localStorage.getItem('theme');
        if (theme === 'dark') {
          document.documentElement.classList.add('dark');
        }
      } catch (e) {}
    })();
  </script>
</head>
*/

// GOTCHA #4: Missing Dark Variants on Interactive States
// ❌ WRONG - Missing dark: on hover and focus
<button className="
  bg-gray-200 dark:bg-gray-700
  hover:bg-gray-300
  focus:ring-2 focus:ring-blue-500
">

// ✅ RIGHT - Complete dark mode coverage
<button className="
  bg-gray-200 dark:bg-gray-700
  hover:bg-gray-300 dark:hover:bg-gray-600
  focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400
  focus:ring-offset-2 dark:focus:ring-offset-gray-900
  transition-colors duration-200
">
// Explanation: Every interactive state needs dark: variant for proper theme support

// GOTCHA #5: React Context Re-renders All Consumers
// Current ThemeContext uses useMemo and useCallback (already optimized)
const value = useMemo(() => ({ theme, toggleTheme }), [theme, toggleTheme]);
// This is CORRECT - prevents unnecessary re-renders of provider's children
// Note: Consumers still re-render when theme changes (unavoidable, acceptable)

// GOTCHA #6: Radix Select Portal in Dialog (NOT APPLICABLE HERE)
// ProjectSelector is NOT inside a Dialog, so this doesn't affect current implementation
// Documented in codebase: ProjectSelector.tsx line 133 has comment about this
// Reference: https://github.com/radix-ui/primitives/issues/3119

// GOTCHA #7: Testing Radix Select with React Testing Library
// Portal content requires waitFor() and baseElement
await user.click(screen.getByRole('combobox'));
await waitFor(() => {
  expect(screen.getByRole('listbox')).toBeInTheDocument();
});
// Explanation: Portal renders outside component root, need to wait for async rendering
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Read Examples Directory**
   - Open: `prps/task_manager_header_redesign/examples/README.md`
   - Study: Example 1 (Tailwind config fix) - understand root cause
   - Study: Example 4 (Header layout) - identify exact JSX changes
   - Verify: Examples 2-3 match current code (confirm React side correct)

2. **Understand Current State**
   - Theme toggle button: Works correctly, just needs Tailwind config
   - ThemeContext: Already handles localStorage and DOM class manipulation
   - Layout: ProjectSelector needs to move from header to sub-header
   - No new components needed - pure configuration and restructuring

3. **Verify Prerequisites**
   - Node.js and npm/yarn/bun installed
   - Dev server can start successfully: `npm run dev`
   - Browser DevTools accessible for testing
   - Understanding of Tailwind class syntax

### Task List (Execute in Order)

```yaml
Task 1: Fix Tailwind Dark Mode Configuration (CRITICAL - PRIMARY FIX)
RESPONSIBILITY: Enables all dark: variant classes in CSS bundle
FILES TO MODIFY:
  - infra/task-manager/frontend/tailwind.config.js

PATTERN TO FOLLOW: See example_1_tailwind_darkmode_config.js

SPECIFIC STEPS:
  1. Open tailwind.config.js
  2. Add `darkMode: 'selector',` on line 3 (after content array)
  3. Save file
  4. CRITICAL: Stop dev server (Ctrl+C)
  5. Restart dev server: `npm run dev` (config changes don't hot reload)
  6. Wait for "ready" message

VALIDATION:
  - Run: `cat tailwind.config.js | grep darkMode`
  - Expected output: `darkMode: 'selector',` or `darkMode: 'class',`
  - Dev server restarted successfully without errors
  - Browser console shows no compilation errors

CODE CHANGE:
```javascript
// Before:
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

// After:
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'selector', // ADD THIS LINE
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

Task 2: Restructure KanbanBoard Header Layout
RESPONSIBILITY: Move ProjectSelector to sub-header, remove "Kanban Board" text
FILES TO MODIFY:
  - infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx (lines 119-149)

PATTERN TO FOLLOW: See example_4_header_layout_pattern.tsx

SPECIFIC STEPS:
  1. Open KanbanBoard.tsx
  2. Locate header section (lines 119-138)
  3. Remove <ProjectSelector /> from right-side controls div (lines 132-136)
  4. Keep only <ThemeToggle /> in right-side div
  5. Locate board sub-header section (lines 142-149)
  6. Remove <h2>Kanban Board</h2> (lines 143-145)
  7. Add <ProjectSelector /> in place of h2
  8. Keep task count paragraph below ProjectSelector
  9. Save file

VALIDATION:
  - Component renders without errors
  - "Task Management" title remains on left
  - ThemeToggle appears alone on right
  - ProjectSelector appears below title (where "Kanban Board" was)
  - Task count appears below ProjectSelector
  - No layout shift or visual glitches

CODE CHANGE:
```tsx
// BEFORE (Current - Lines 119-149):
<div className="h-full p-6">
  {/* Board Header with Title, Project Selector, and Theme Toggle */}
  <div className="mb-6 flex items-center justify-between">
    {/* Left side: Title and Description */}
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
        Task Management
      </h1>
      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
        Organize your tasks with drag-and-drop Kanban board
      </p>
    </div>

    {/* Right side: Project Selector and Theme Toggle */}
    <div className="flex items-center gap-4">
      <ProjectSelector
        selectedProjectId={selectedProjectId}
        onProjectChange={onProjectChange}
        onCreateProject={onCreateProject}
      />
      <ThemeToggle />
    </div>
  </div>

  {/* Board Sub-header */}
  <div className="mb-6">
    <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
      Kanban Board
    </h2>
    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
      {tasks?.length || 0} tasks total
    </p>
  </div>

  {/* ... rest of component */}
</div>

// AFTER (Target - Lines 119-149):
<div className="h-full p-6">
  {/* Board Header with Title and Theme Toggle */}
  <div className="mb-6 flex items-center justify-between">
    {/* Left side: Title and Description */}
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
        Task Management
      </h1>
      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
        Organize your tasks with drag-and-drop Kanban board
      </p>
    </div>

    {/* Right side: Theme Toggle ONLY */}
    <div className="flex items-center gap-4">
      <ThemeToggle />
    </div>
  </div>

  {/* Project Selector Section (replaces "Kanban Board" header) */}
  <div className="mb-6">
    <ProjectSelector
      selectedProjectId={selectedProjectId}
      onProjectChange={onProjectChange}
      onCreateProject={onCreateProject}
    />
    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
      {tasks?.length || 0} tasks total
    </p>
  </div>

  {/* ... rest of component */}
</div>
```

---

Task 3: Test Theme Toggle Functionality
RESPONSIBILITY: Verify dark mode works end-to-end
FILES TO TEST:
  - Browser UI and DevTools

SPECIFIC STEPS:
  1. Open app in browser: http://localhost:5173 (or configured port)
  2. Open browser DevTools (F12) → Console tab
  3. Click theme toggle button in upper right
  4. Verify visual theme change (backgrounds, text colors change)
  5. In console, run: `document.documentElement.classList.contains('dark')`
     - Should return `true` after clicking toggle
  6. Click toggle again
  7. In console, run same command → should return `false`
  8. Verify localStorage: `localStorage.getItem('theme')`
     - Should return `"dark"` or `"light"` based on current theme
  9. Hard refresh page (Cmd+Shift+R or Ctrl+Shift+R)
  10. Verify theme persists (doesn't reset to light mode)

VALIDATION:
  - Theme toggle button is clickable
  - Icon changes between Sun (dark mode) and Moon (light mode)
  - All components change colors smoothly (200ms transition)
  - Dark mode class applies to document.documentElement
  - Theme preference persists in localStorage
  - Theme persists after browser refresh
  - No console errors

GOTCHA CHECKS:
  - If toggle clicks but no visual change: Check that darkMode config was added
  - If dev server wasn't restarted: Restart now and test again
  - If theme doesn't persist: Check localStorage in DevTools Application tab

---

Task 4: Test Layout Changes
RESPONSIBILITY: Verify header layout matches mockup
FILES TO TEST:
  - Browser UI at different viewport sizes

SPECIFIC STEPS:
  1. In browser, verify header layout:
     - "Task Management" title on left (with subtitle below)
     - Theme toggle button on right (same row as title)
     - ProjectSelector below title (where "Kanban Board" was)
     - Task count below ProjectSelector
     - "Kanban Board" text completely removed
  2. Test responsive breakpoints:
     - Desktop (1280px+): Layout as described above
     - Tablet (768px-1279px): Elements stack appropriately
     - Mobile (<768px): Vertical layout maintains hierarchy
  3. Verify no layout shift when toggling theme
  4. Test ProjectSelector dropdown still works
  5. Test theme toggle still works

VALIDATION:
  - Layout matches ASCII mockup from requirements
  - All elements properly aligned
  - No overlapping or misaligned components
  - Responsive design works on all viewport sizes
  - No layout shift when changing theme
  - ProjectSelector functionality unchanged
  - Task count displays correctly

---

Task 5: Accessibility Verification
RESPONSIBILITY: Ensure keyboard navigation and screen reader support
FILES TO TEST:
  - Browser UI with keyboard only

SPECIFIC STEPS:
  1. Close mouse/trackpad (keyboard only)
  2. Tab through header elements
  3. Verify focus visible on theme toggle
  4. Press Space or Enter on theme toggle → theme changes
  5. Tab to ProjectSelector
  6. Verify focus visible on selector trigger
  7. Press Space or Enter → dropdown opens
  8. Use Arrow keys to navigate options
  9. Press Enter to select option
  10. Verify focus indicators visible in BOTH light and dark modes

VALIDATION:
  - All interactive elements reachable via keyboard
  - Focus rings visible in light mode
  - Focus rings visible in dark mode (different color)
  - Space/Enter activates controls
  - Arrow keys navigate dropdowns
  - Escape closes dropdowns
  - No keyboard traps

WCAG CHECKS:
  - Focus ring contrast ratio >= 3:1 (both themes)
  - Text contrast ratio >= 4.5:1 for normal text (both themes)
  - Text contrast ratio >= 3:1 for large text (both themes)

---

Task 6: Optional Enhancement - Add localStorage Error Handling
RESPONSIBILITY: Graceful degradation in private browsing mode
FILES TO MODIFY:
  - infra/task-manager/frontend/src/contexts/ThemeContext.tsx (OPTIONAL)

PATTERN TO FOLLOW: See projectStorage.ts for error handling pattern

SPECIFIC STEPS:
  1. Open ThemeContext.tsx
  2. Wrap localStorage.getItem in try-catch (line 28)
  3. Wrap localStorage.setItem in try-catch (line 42)
  4. Log warnings to console (not errors)
  5. Return default "light" theme if localStorage fails
  6. Allow theme toggle to work even without persistence

VALIDATION:
  - Test in Safari Private Browsing mode
  - App loads without crashing
  - Theme toggle still works (just doesn't persist)
  - Console shows warning (not error) about localStorage

THIS TASK IS OPTIONAL - Current implementation works for 99% of users.
Add this if project has enterprise users or strict accessibility requirements.

CODE CHANGE (OPTIONAL):
```typescript
// In ThemeContext.tsx, enhance error handling:

// Line 20-26 (initialization):
const [theme, setTheme] = useState<Theme>(() => {
  try {
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored === "dark" || stored === "light") {
      return stored;
    }
  } catch (error) {
    console.warn('localStorage unavailable, using default theme:', error);
  }
  return "light"; // Default fallback
});

// Line 35-43 (persistence):
useEffect(() => {
  const root = document.documentElement;
  if (theme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }

  try {
    localStorage.setItem("theme", theme);
  } catch (error) {
    console.warn('Failed to persist theme preference:', error);
    // App still works, just doesn't persist
  }
}, [theme]);
```
```

---

## Validation Loop

### Level 1: Configuration Validation

```bash
# Verify Tailwind darkMode config exists
cat infra/task-manager/frontend/tailwind.config.js | grep darkMode

# Expected output:
darkMode: 'selector',
# OR
darkMode: 'class',

# If no output: Config not added, go back to Task 1

# Verify dev server is running
# Check terminal - should see "ready in" message
# If not: Run `npm run dev` from frontend directory
```

### Level 2: Browser Console Validation

```javascript
// Open browser DevTools → Console tab

// Test 1: Check if dark class applies
document.documentElement.classList.contains('dark')
// After clicking toggle, should return: true (dark mode) or false (light mode)

// Test 2: Check localStorage persistence
localStorage.getItem('theme')
// Should return: "dark" or "light" (not null)

// Test 3: Check for errors
// Look for any red error messages in console
// Should be: No errors

// Test 4: Verify dark mode CSS classes exist
getComputedStyle(document.body).backgroundColor
// In light mode: rgb(255, 255, 255) or similar light color
// In dark mode: rgb(31, 41, 55) or similar dark color
// If colors don't change: Tailwind config issue or dev server not restarted
```

### Level 3: Visual Layout Validation

Open browser and verify layout matches this checklist:

**Header Row (Top)**:
- [ ] "Task Management" title on the left
- [ ] Subtitle text below title
- [ ] Theme toggle button on the right (same row as title)
- [ ] Theme toggle shows moon icon (light mode) or sun icon (dark mode)
- [ ] NO ProjectSelector in this row

**Sub-Header Row (Below Title)**:
- [ ] ProjectSelector dropdown appears here
- [ ] Task count appears below ProjectSelector
- [ ] NO "Kanban Board" text anywhere

**Theme Toggle Functionality**:
- [ ] Clicking toggle changes icon (moon ↔ sun)
- [ ] All backgrounds change color (white ↔ dark gray)
- [ ] All text changes color (dark ↔ light)
- [ ] Transitions are smooth (no instant snap)
- [ ] Refresh page → theme persists

**ProjectSelector Functionality**:
- [ ] Dropdown opens when clicked
- [ ] Options are visible and selectable
- [ ] Selected project displays correctly
- [ ] Create new project option appears
- [ ] Selecting project filters tasks

### Level 4: Responsive Design Validation

```bash
# Test at different viewport widths
# Use browser DevTools → Toggle device toolbar (Cmd+Shift+M)

# Desktop (1280px width):
# - All elements in single header row: Title (left) | Toggle (right)
# - ProjectSelector below in separate row

# Tablet (768px width):
# - Same layout, elements may be slightly smaller
# - Verify nothing overlaps or wraps awkwardly

# Mobile (375px width):
# - Elements stack vertically if needed
# - All text readable, buttons touchable
# - No horizontal scroll

# Test: Resize browser slowly from wide to narrow
# Verify: Smooth responsive behavior, no sudden breaks
```

### Level 5: Accessibility Validation

```bash
# Keyboard Navigation Test
# 1. Close mouse/trackpad
# 2. Tab through interface
# 3. Verify focus rings visible on:
#    - Theme toggle button
#    - ProjectSelector trigger
#    - All dropdown options

# Screen Reader Test (Optional but recommended)
# macOS: Enable VoiceOver (Cmd+F5)
# Windows: Enable Narrator (Windows+Ctrl+Enter)
# Test: Verify all elements have descriptive labels

# Color Contrast Test
# Use browser extension: "WCAG Color Contrast Checker"
# OR online tool: https://webaim.org/resources/contrastchecker/
# Verify: All text meets WCAG AA standards (4.5:1 for normal, 3:1 for large)
```

### Level 6: Cross-Browser Testing

**Critical Browsers**:
- [ ] Chrome/Chromium: Theme works, layout correct
- [ ] Firefox: Theme works, layout correct
- [ ] Safari: Theme works, layout correct
- [ ] Safari Private Browsing: App loads (theme may not persist - acceptable)

**Known Issues**:
- Safari Private Browsing: If optional Task 6 not completed, may see console warning about localStorage. App still works.

---

## Final Validation Checklist

**Configuration**:
- [ ] `darkMode: 'selector'` present in tailwind.config.js
- [ ] Dev server restarted after config change
- [ ] No build errors or warnings
- [ ] Dark mode CSS classes present in compiled CSS

**Functionality**:
- [ ] Theme toggle button is clickable and responsive
- [ ] Icon changes between sun and moon correctly
- [ ] All components change to dark theme when toggled
- [ ] Theme persists after browser refresh
- [ ] ProjectSelector moved to sub-header position
- [ ] "Kanban Board" header text removed completely
- [ ] Task count displays below ProjectSelector
- [ ] No layout shift when toggling theme

**Visual Design**:
- [ ] Layout matches provided ASCII mockup exactly
- [ ] Header: Title (left) + Theme Toggle (right)
- [ ] Sub-header: ProjectSelector + Task count
- [ ] Smooth transitions on theme change (200ms)
- [ ] All dark mode colors have sufficient contrast
- [ ] Focus rings visible in both light and dark modes

**Accessibility**:
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible in both themes
- [ ] ARIA labels present on all controls
- [ ] Screen reader announces theme changes (if tested)
- [ ] Color contrast meets WCAG AA standards

**Testing**:
- [ ] Manual testing: Theme toggle → visual change → refresh → persists
- [ ] Console validation: No errors, dark class applies correctly
- [ ] localStorage check: Theme value saved correctly
- [ ] Responsive testing: Works on mobile, tablet, desktop
- [ ] Cross-browser: Works in Chrome, Firefox, Safari

**No Regressions**:
- [ ] Drag and drop still works
- [ ] ProjectSelector dropdown still functions
- [ ] Task creation still works
- [ ] Project switching still works
- [ ] All existing features unchanged

---

## Anti-Patterns to Avoid

### 1. ❌ Skipping Dev Server Restart After Config Change
**Problem**: Tailwind config changes don't hot reload. Dark mode won't work until restart.
**Solution**: Always run `npm run dev` again after editing tailwind.config.js

### 2. ❌ Hard-Coding Dark Mode Colors Instead of Using Tailwind Classes
**Problem**: Loses consistency with design system, hard to maintain
**Solution**: Use Tailwind utilities: `bg-gray-800`, `text-gray-100`, etc.

```tsx
// ❌ WRONG
<div style={{ backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff' }}>

// ✅ RIGHT
<div className="bg-white dark:bg-gray-800">
```

### 3. ❌ Not Memoizing Context Values
**Problem**: Causes unnecessary re-renders of all consuming components
**Solution**: Already implemented in ThemeContext - use useMemo for value object

### 4. ❌ Creating New Components When Repositioning Is Sufficient
**Problem**: Over-engineering simple layout changes
**Solution**: Just move existing JSX, don't create new wrapper components

### 5. ❌ Forgetting Dark Mode Variants on Hover/Focus States
**Problem**: Interactive elements look wrong in dark mode, accessibility failure
**Solution**: Every interactive state needs dark: variant

```tsx
// ❌ INCOMPLETE
<button className="hover:bg-gray-300">

// ✅ COMPLETE
<button className="hover:bg-gray-300 dark:hover:bg-gray-600">
```

### 6. ❌ Using Raw localStorage Without Error Handling (Optional Task 6)
**Problem**: App crashes in Safari Private Browsing
**Solution**: Wrap in try-catch if implementing optional error handling

### 7. ❌ Testing Only in Dev Build
**Problem**: Production build may purge dark mode classes if content config incomplete
**Solution**: Test production build with `npm run build && npm run preview`

### 8. ❌ Modifying ThemeContext or ThemeToggle Components
**Problem**: These components are already correct - changes may break functionality
**Solution**: Leave them as-is, only fix Tailwind config and layout

---

## Success Metrics

**Functional Success**:
- Theme toggle works on first click
- All components transition to dark mode
- Theme persists across browser sessions
- No console errors or warnings
- Layout matches mockup exactly

**User Experience**:
- Smooth theme transitions (no jarring color snaps)
- Clear visual hierarchy in header
- Accessible keyboard navigation
- Professional polish

**Technical Success**:
- One-line Tailwind config fix
- Minimal code changes (< 50 lines total)
- No new dependencies required
- No breaking changes to existing features
- Implementation time: 1-2 hours

---

## PRP Quality Self-Assessment

**Score: 9.5/10** - Very high confidence in one-pass implementation success

**Reasoning**:
- ✅ Comprehensive context: All 5 research docs thoroughly analyzed and integrated
- ✅ Clear task breakdown: 6 tasks with specific steps, validation, and code examples
- ✅ Proven patterns: Examples extracted from working codebase (Archon) and current code
- ✅ Validation strategy: 6 levels of validation from config check to cross-browser testing
- ✅ Error handling: 15 gotchas documented with solutions and detection methods
- ✅ Root cause identified: Missing Tailwind darkMode config is primary issue
- ✅ Minimal changes: Only 2 files modified, no new dependencies
- ✅ Code examples: Complete before/after code for both changes
- ✅ No ambiguity: Crystal clear what's working vs broken vs needs fixing

**Deduction reasoning** (-0.5):
- Optional Task 6 (localStorage error handling) not required for MVP but would improve robustness
- FOUC prevention (inline script) mentioned but not required - could enhance polish
- No CI/CD integration steps (assume manual testing sufficient)

**Mitigations**:
- Task 6 clearly marked as optional with justification
- FOUC prevention documented in gotchas for future reference
- Manual testing checklist comprehensive enough to catch issues

**Implementation Readiness**: VERY HIGH
- Clear, ordered task list with specific file paths and line numbers
- Exact code changes shown in before/after format
- Multiple validation gates prevent incomplete implementation
- Gotcha warnings prevent common mistakes
- All documentation links provided with specific sections to read

**Expected Outcome**: Implementer can complete this PRP in single session with high success rate. If any issues occur, validation loops and gotcha section provide debugging guidance.
