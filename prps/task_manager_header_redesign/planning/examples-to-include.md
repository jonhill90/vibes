# Examples Curated: task_manager_header_redesign

## Summary

Extracted **5 code examples** to the examples directory demonstrating the exact patterns needed for fixing the task manager header layout and enabling dark mode toggle functionality.

## Files Created

1. **example_1_tailwind_darkmode_config.js**: Tailwind configuration with darkMode enabled (CRITICAL FIX)
2. **example_2_theme_context_pattern.tsx**: React Context pattern for theme management with localStorage
3. **example_3_theme_toggle_component.tsx**: Theme toggle button component with accessibility
4. **example_4_header_layout_pattern.tsx**: Current header layout showing what needs to change
5. **example_5_alternative_theme_toggle.tsx**: Alternative styling approach (optional inspiration)
6. **README.md**: Comprehensive guide with usage instructions and pattern analysis

## Key Patterns Extracted

### Pattern 1: Tailwind Dark Mode Configuration
**From**: infra/archon/archon-ui-main/tailwind.config.js
**Relevance**: 10/10 - Root cause fix

**What it demonstrates**:
- The `darkMode: "selector"` configuration line that enables class-based dark mode
- This single line is the entire fix needed for the theme toggle to work
- Without it, all `dark:` classes are compiled away by Tailwind

**Critical insight**: The theme toggle button and ThemeContext are already implemented correctly. The ONLY issue is the missing Tailwind configuration.

### Pattern 2: React Context for Theme Management
**From**: infra/task-manager/frontend/src/contexts/ThemeContext.tsx (current code)
**Relevance**: 9/10 - Current implementation (correct)

**What it demonstrates**:
- Two-useEffect pattern: separate initialization from updates
- localStorage persistence with proper type checking
- document.documentElement class manipulation
- Custom hook with guard clause

**Critical insight**: This code is already correct and requires no changes. It's included for reference and to show the PRP implementer that the React side is working.

### Pattern 3: Theme Toggle Component
**From**: infra/task-manager/frontend/src/components/ThemeToggle.tsx (current code)
**Relevance**: 9/10 - Current implementation (correct)

**What it demonstrates**:
- Icon switching based on theme state
- Comprehensive dark mode classes (bg, hover, focus states)
- Accessibility with ARIA labels and titles
- onClick handler properly bound to toggleTheme

**Critical insight**: This component is also already correct. The button works, it calls the right function, it has the right classes. The classes just don't do anything because Tailwind's darkMode isn't configured.

### Pattern 4: Header Layout Structure
**From**: infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx (lines 117-149)
**Relevance**: 10/10 - Exact code to change

**What it demonstrates**:
- Current layout with ProjectSelector in wrong position (header row)
- Target layout with ProjectSelector in sub-header section
- Flex justify-between pattern for left/right positioning
- The specific JSX that needs to be moved

**Critical insight**: Shows the EXACT before/after for the layout fix. Just moving components between divs, no logic changes.

### Pattern 5: Alternative Theme Toggle (Optional)
**From**: infra/archon/archon-ui-main/src/components/ui/ThemeToggle.tsx
**Relevance**: 6/10 - Future inspiration

**What it demonstrates**:
- Configurable accent color system
- Glassmorphism styling with backdrop-blur
- Gradient backgrounds
- More sophisticated visual design

**Critical insight**: Not needed for MVP, but useful reference if design evolves later.

## Recommendations for PRP Assembly

### 1. Reference Examples Directory in PRP "All Needed Context"

Add to PRP's context section:
```markdown
## Code Examples

See `prps/task_manager_header_redesign/examples/` for working implementations:

**CRITICAL - Must Read**:
- `example_1_tailwind_darkmode_config.js` - The root cause fix (10/10 relevance)
- `example_4_header_layout_pattern.tsx` - Exact code to change (10/10 relevance)

**Reference - Current Implementation**:
- `example_2_theme_context_pattern.tsx` - ThemeContext (already correct)
- `example_3_theme_toggle_component.tsx` - ThemeToggle (already correct)

**Optional**:
- `example_5_alternative_theme_toggle.tsx` - Future styling ideas (6/10 relevance)

**Comprehensive Guide**:
- `README.md` - Full pattern analysis with what to mimic/adapt/skip
```

### 2. Include Key Pattern Highlights in "Implementation Blueprint"

From the examples, pull out these code snippets for the PRP:

```javascript
// CRITICAL FIX #1: Tailwind Config
// File: tailwind.config.js
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: "selector",  // ← Add this one line
  theme: { extend: {} },
  plugins: [],
}
```

```tsx
// CRITICAL FIX #2: Layout Restructure
// File: KanbanBoard.tsx

// BEFORE (Current - Wrong):
<div className="flex items-center justify-between">
  <div>Title</div>
  <div className="flex gap-4">
    <ProjectSelector />  {/* ❌ Wrong location */}
    <ThemeToggle />
  </div>
</div>

// AFTER (Target - Correct):
<div className="flex items-center justify-between">
  <div>Title</div>
  <ThemeToggle />  {/* ✅ Only toggle here */}
</div>
<div className="mb-6">
  <ProjectSelector />  {/* ✅ Moved here */}
  <p>Task count</p>
</div>
```

### 3. Direct Implementer to Study README Before Coding

Add to PRP's "Before You Start" section:
```markdown
## Required Reading

1. **Read** `prps/task_manager_header_redesign/examples/README.md` - Full pattern guide
2. **Study** Example 1 (Tailwind config) - Understand the root cause
3. **Study** Example 4 (Header layout) - Identify exact changes needed
4. **Verify** Examples 2-3 match current code - Confirm React side is correct
```

### 4. Use Examples for Validation

Add to PRP's "Validation Steps":
```markdown
## Validation Against Examples

1. **Tailwind Config Validation**:
   ```bash
   cat tailwind.config.js | grep darkMode
   # Expected output: darkMode: "selector",
   ```

2. **Layout Structure Validation**:
   - Header row should have ONLY Title and ThemeToggle
   - Sub-header should have ONLY ProjectSelector and task count
   - "Kanban Board" h2 should be removed

3. **Theme Toggle Functionality**:
   - Click toggle → colors change immediately
   - Refresh page → theme persists
   - Check console: `document.documentElement.classList.contains('dark')`
```

### 5. Clarify "Working vs Broken" Status

Add to PRP's "Context" or "Background" section:
```markdown
## What's Already Working vs What's Broken

**Already Working (No changes needed)**:
- ✅ ThemeContext.tsx - Correctly manages theme state
- ✅ ThemeToggle.tsx - Button properly wired, has correct classes
- ✅ App.tsx - ThemeProvider correctly wraps app

**Broken (Needs fixing)**:
- ❌ tailwind.config.js - Missing `darkMode: "selector"` configuration
- ❌ KanbanBoard.tsx - ProjectSelector in wrong position

**Why Toggle Appears Broken**:
The toggle button WORKS (it calls toggleTheme, which updates state and DOM classes).
The theme context WORKS (it adds/removes 'dark' class on document.documentElement).
But Tailwind doesn't process dark: classes because darkMode config is missing.
Result: Button clicks, state changes, classes apply, but NO VISUAL CHANGE.
```

## Quality Assessment

### Coverage: 10/10
- ✅ Tailwind dark mode configuration (the critical fix)
- ✅ React Context pattern (reference for understanding)
- ✅ Theme toggle component (reference for understanding)
- ✅ Header layout restructure (exact code to change)
- ✅ Alternative styling (future inspiration)

All required patterns are covered with working examples.

### Relevance: 9/10
- Example 1: 10/10 - Root cause fix
- Example 2: 9/10 - Current implementation (correct)
- Example 3: 9/10 - Current implementation (correct)
- Example 4: 10/10 - Exact changes needed
- Example 5: 6/10 - Optional inspiration

Average relevance is very high. All examples directly applicable.

### Completeness: 10/10
- ✅ Each example has source attribution header
- ✅ All examples are actual code (not references)
- ✅ Each example is self-contained
- ✅ Comprehensive README with usage guidance
- ✅ Clear "what to mimic/adapt/skip" sections

Examples are studyable and runnable (or near-runnable).

### Documentation Quality: 10/10
- ✅ README has clear structure with table of contents
- ✅ Each example has dedicated section in README
- ✅ "What to Mimic/Adapt/Skip" for every example
- ✅ Pattern highlights with code snippets
- ✅ "Why This Example" explanations
- ✅ Quick reference section for busy developers

README is comprehensive and actionable.

### Overall: 9.75/10

**Strengths**:
- Exactly addresses the feature requirements
- Identifies root cause (Tailwind config)
- Shows current vs target state clearly
- Comprehensive documentation
- All examples from working code

**Areas for improvement**:
- Could include PostCSS config check (though not needed here)
- Could add example of testing dark mode classes
- Could show before/after screenshots (but examples provide ASCII mockup)

## Search Strategy Used

### Archon Knowledge Base Search

Searched Archon with queries:
- "React theme toggle" - No relevant results
- "Tailwind darkMode class" - No relevant results
- "localStorage persistence" - Generic patterns only
- "React Context provider" - Generic patterns only

**Outcome**: Archon had no specific examples for React theme toggling or Tailwind dark mode. All examples came from local codebase.

### Local Codebase Search

Used Grep and Glob to find:
- Files with `darkMode.*class` pattern
- Files with `localStorage.*theme` pattern
- Files with `ThemeContext` or `ThemeProvider`
- All `tailwind.config.*` files
- Header layout patterns with `flex justify-between`

**Outcome**: Found perfect examples in:
1. Archon's working Tailwind config (has darkMode)
2. Task-manager's broken Tailwind config (missing darkMode)
3. Task-manager's correct ThemeContext
4. Task-manager's correct ThemeToggle
5. Task-manager's KanbanBoard with wrong layout
6. Archon's alternative ThemeToggle for inspiration

### Key Discovery

The feature analysis suspected missing Tailwind config as the root cause. Grep confirmed:
- Task-manager's tailwind.config.js has NO darkMode setting
- Archon's tailwind.config.js HAS `darkMode: "selector"`
- All other code (ThemeContext, ThemeToggle) is identical and correct

This validated the hypothesis and made it easy to extract the exact fix needed.

## File Structure Created

```
prps/task_manager_header_redesign/
├── examples/
│   ├── example_1_tailwind_darkmode_config.js      # Tailwind fix
│   ├── example_2_theme_context_pattern.tsx        # React Context
│   ├── example_3_theme_toggle_component.tsx       # Toggle button
│   ├── example_4_header_layout_pattern.tsx        # Layout changes
│   ├── example_5_alternative_theme_toggle.tsx     # Optional styling
│   └── README.md                                  # Comprehensive guide
└── planning/
    ├── feature-analysis.md
    └── examples-to-include.md                     # This file
```

All files use consistent naming and source attribution.

## Next Steps for Assembler

1. **Read this manifest** to understand what examples are available
2. **Read the examples README** to understand the patterns
3. **Pull key snippets** from examples into PRP "Implementation Blueprint"
4. **Reference examples directory** in PRP "All Needed Context" section
5. **Use pattern highlights** for clear implementation guidance
6. **Add validation steps** using examples as reference

The examples are ready for integration into the final PRP.

---

**Generated**: 2025-10-10
**Feature**: task_manager_header_redesign
**Total Examples**: 5 code files + 1 README
**Quality Score**: 9.75/10
**Completion Status**: ✅ Ready for PRP assembly
