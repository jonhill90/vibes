# Feature Analysis: Task Manager Header Redesign

## INITIAL.md Summary
The task manager UI requires a header layout redesign to fix positioning issues and implement a working dark/light mode toggle. The project dropdown needs to replace the "Kanban Board" header text (currently mispositioned in upper right), and the theme toggle needs to be debugged and positioned in the upper right corner with persistent localStorage settings.

## Core Requirements

### Explicit Requirements
1. **Replace "Kanban Board" header with Project Selector dropdown**
   - Current state: "Kanban Board" text appears as h2 header above columns (line 143-145 in KanbanBoard.tsx)
   - Desired state: Project selector dropdown replaces this header entirely
   - Location: Should appear where "Kanban Board" currently is (above column layout, below main title)

2. **Keep "Task Management" title on the left**
   - Already implemented correctly (line 122-127 in KanbanBoard.tsx)
   - Should remain as main page title

3. **Add Working Dark/Light Mode Toggle**
   - Position: Upper right corner
   - Default: Light mode
   - Must persist preference across sessions via localStorage
   - Currently implemented but non-functional (button doesn't respond to clicks)

4. **Fix Layout to Match User Mockup**
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

### Implicit Requirements
1. **Responsive Design**: Layout should work on mobile/tablet (already uses Tailwind breakpoints)
2. **Accessibility**: Maintain ARIA labels and keyboard navigation
3. **Smooth Transitions**: Theme toggle should have smooth visual transitions (already implemented with Tailwind duration-200)
4. **No Layout Shift**: Changes should not cause jarring layout shifts
5. **Maintain Dark Mode Styling**: All components must have dark: variants for proper theme support
6. **Error Handling**: Gracefully handle localStorage unavailable scenarios

## Technical Components

### Data Models
**No new data models required** - Using existing:
- `Theme` type: `"light" | "dark"` (ThemeContext.tsx line 14)
- localStorage key: `"theme"` (ThemeContext.tsx line 42)
- Project data models already exist in ProjectSelector

### External Integrations
**Already Integrated**:
- **Radix UI Select**: `@radix-ui/react-select` - Accessible dropdown primitives (ProjectSelector.tsx line 37)
- **Lucide React**: Icon library for Sun/Moon icons (ThemeToggle.tsx line 12)
- **Tailwind CSS**: Utility-first CSS with dark mode support via `darkMode: 'class'` (needs verification in tailwind.config.js)
- **localStorage API**: Browser API for theme persistence

**Missing from tailwind.config.js**:
- `darkMode: 'class'` configuration (currently not set - line 2-11 shows basic config)
- This is CRITICAL for dark mode to work

### Core Logic

#### 1. Theme Toggle Fix (Primary Issue)
**Current Implementation Analysis**:
- ThemeContext.tsx (lines 1-63): Context provider correctly implemented
  - `toggleTheme` function exists (line 45-47)
  - localStorage persistence exists (line 42)
  - Document class toggle exists (line 38-41)
- ThemeToggle.tsx (lines 1-33): Button component correctly structured
  - `onClick={toggleTheme}` exists (line 20)
  - Correct hook usage: `const { theme, toggleTheme } = useTheme()` (line 16)

**Root Cause Analysis**:
1. **Missing Tailwind darkMode config** - Without `darkMode: 'class'` in tailwind.config.js, dark: variants won't work
2. **Possible ThemeProvider not wrapping components** - Need to verify App.tsx wrapping (already verified - line 33 wraps app)
3. **Event handler conflict** - onClick might be blocked by parent element or CSS

**Solution Path**:
- Add `darkMode: 'class'` to tailwind.config.js
- Verify no pointer-events: none blocking clicks
- Test toggleTheme function directly in console
- Check for conflicting event handlers in parent components

#### 2. Layout Restructure
**Current Structure** (KanbanBoard.tsx lines 117-149):
```
<div className="h-full p-6">
  {/* Header - Title + ProjectSelector + ThemeToggle */}
  <div className="mb-6 flex items-center justify-between">
    <div>
      <h1>Task Management</h1>
      <p>subtitle</p>
    </div>
    <div className="flex items-center gap-4">
      <ProjectSelector />
      <ThemeToggle />
    </div>
  </div>

  {/* Board Sub-header with "Kanban Board" */}
  <div className="mb-6">
    <h2>Kanban Board</h2>  {/* THIS NEEDS TO BE REPLACED */}
    <p>0 tasks total</p>
  </div>

  {/* Columns */}
</div>
```

**Desired Structure**:
```
<div className="h-full p-6">
  {/* Header - Title + ThemeToggle ONLY */}
  <div className="mb-6 flex items-center justify-between">
    <div>
      <h1>Task Management</h1>
      <p>subtitle</p>
    </div>
    <div>
      <ThemeToggle />  {/* REMOVE ProjectSelector from here */}
    </div>
  </div>

  {/* Project Selector Section (replaces "Kanban Board" header) */}
  <div className="mb-6">
    <ProjectSelector />  {/* MOVE HERE */}
    <p>0 tasks total</p>
  </div>

  {/* Columns */}
</div>
```

#### 3. ProjectSelector Styling Adjustments
**Current**: Compact dropdown button (min-w-[200px])
**Needed**: May need to be styled as full-width or larger to "replace" header presence

### UI/CLI Requirements

#### Component Hierarchy Changes
```
KanbanBoard
├── Header Row (justify-between)
│   ├── Left: Title + Subtitle
│   └── Right: ThemeToggle (ONLY)
│
├── Project Section (NEW SECTION)
│   ├── ProjectSelector (MOVED from Header)
│   └── Task count
│
└── Columns Grid
    ├── Todo
    ├── Doing
    ├── Review
    └── Done
```

#### Accessibility Requirements (Maintain Existing)
- All interactive elements have aria-labels
- Keyboard navigation works (Tab, Enter, Arrow keys)
- Screen reader announcements for theme changes
- Focus visible states on all buttons
- Color contrast meets WCAG AA standards

## Similar Implementations Found in Archon

### 1. No Direct Header Redesign PRPs Found
- **Relevance**: N/A
- **Archon ID**: None found
- **Key Patterns**: N/A
- **Gotchas**: N/A

**Note**: Archon search for "React header layout theme toggle" yielded no relevant PRPs or projects. This appears to be a unique implementation for this codebase.

### 2. General React Patterns (From Archon Knowledge Base)
- **Relevance**: 3/10 (General guidance only)
- **Source**: General React/AI agent documentation
- **Key Patterns**:
  - Component composition and layout restructuring
  - Event handler debugging approaches
- **Gotchas**: None specific to this use case

### 3. Existing Codebase Patterns (Self-Reference)
- **Relevance**: 10/10
- **Source**: Current task-manager codebase
- **Key Patterns**:
  - Radix UI Select pattern already implemented correctly (ProjectSelector.tsx)
  - Theme context pattern follows React best practices
  - Tailwind dark mode class strategy (needs config fix)
  - Memoization with React.memo for performance (ProjectSelector line 48)
- **Gotchas from Existing Code**:
  - Gotcha #6 addressed: Select.Portal escapes Dialog focus trap (ProjectSelector line 133)
  - Gotcha #9 addressed: DndProvider wraps app (App.tsx line 36)
  - Performance optimization with useCallback (ProjectSelector lines 58, 69)

## Recommended Technology Stack

**No new technologies needed** - Using existing stack:

### Framework & Libraries
- **React 18**: Component library (already in use)
- **TypeScript**: Type safety (already in use)
- **Tailwind CSS 3.x**: Utility-first styling (already in use)
  - **REQUIRED FIX**: Add `darkMode: 'class'` to tailwind.config.js
- **Radix UI Select**: Accessible dropdown (already in use)
- **Lucide React**: Icon library (already in use)

### State Management
- **React Context API**: ThemeContext for global theme state (already implemented)
- **localStorage**: Browser API for persistence (already implemented)

### Testing (Existing Patterns)
- **Vitest**: Component testing (based on existing test files)
- **React Testing Library**: Component interaction testing
- **Test files to update**:
  - `KanbanBoard.test.tsx` (verify layout changes)
  - `ThemeToggle.test.tsx` (may need creation for click testing)

### Build & Development
- **Vite**: Build tool (inferred from React + TypeScript setup)
- **PostCSS**: Tailwind processing (required for Tailwind)

## Assumptions Made

### 1. **Tailwind Configuration Issue is Root Cause**
- **Assumption**: Missing `darkMode: 'class'` in tailwind.config.js is why theme toggle doesn't work
- **Reasoning**:
  - Current config (lines 2-11) shows no darkMode setting
  - ThemeContext adds/removes 'dark' class correctly (line 38-41)
  - Dark variants exist throughout codebase (e.g., `dark:bg-gray-900`)
  - Tailwind requires explicit `darkMode: 'class'` to enable class-based dark mode
- **Source**: Tailwind CSS documentation and codebase analysis
- **Validation**: Add config, rebuild, test toggle

### 2. **No Server-Side Changes Required**
- **Assumption**: This is purely a frontend layout/styling fix
- **Reasoning**:
  - No new API endpoints needed
  - No database schema changes
  - All required data already fetched (projects, tasks, theme preference)
- **Source**: INITIAL.md scope and codebase analysis
- **Risk Level**: Low

### 3. **Project Selector Component Can Be Reused As-Is**
- **Assumption**: ProjectSelector component needs no logic changes, only repositioning
- **Reasoning**:
  - Component is well-implemented with proper accessibility
  - Already has dark mode styling
  - Only needs to be moved in JSX and potentially restyled (width/layout)
- **Source**: ProjectSelector.tsx analysis (lines 1-178)
- **Risk Level**: Low

### 4. **No Breaking Changes to Component Props**
- **Assumption**: KanbanBoard props can remain unchanged
- **Reasoning**:
  - Layout changes are internal to KanbanBoard component
  - Props interface already includes all needed callbacks
  - Parent component (KanbanPage) doesn't need modifications
- **Source**: KanbanBoard.tsx interface (lines 29-34)
- **Risk Level**: Very Low

### 5. **User's Mockup is Accurate Representation**
- **Assumption**: ASCII mockup in INITIAL.md shows exact desired layout
- **Reasoning**:
  - User explicitly provided mockup
  - Mockup clearly shows ProjectSelector replacing "Kanban Board" header
  - Layout is simple and unambiguous
- **Source**: INITIAL.md lines 26-39
- **Confidence**: High

### 6. **localStorage is Available in Target Browsers**
- **Assumption**: Target users have browsers with localStorage support
- **Reasoning**:
  - localStorage is universally supported (IE8+)
  - Existing code already uses localStorage without fallback
  - Modern React app assumes modern browser
- **Source**: ThemeContext.tsx line 28, 42
- **Risk Level**: Very Low (can add try-catch if needed)

### 7. **Theme Toggle Should Work After Tailwind Fix**
- **Assumption**: No other JavaScript bugs exist beyond Tailwind configuration
- **Reasoning**:
  - ThemeToggle component is correctly implemented
  - onClick handler properly wired
  - Context provider correctly wraps app
  - Only missing piece is Tailwind darkMode config
- **Source**: ThemeToggle.tsx and ThemeContext.tsx analysis
- **Validation Strategy**: If toggle still doesn't work after Tailwind fix, debug event propagation

## Success Criteria

### Functional Requirements
1. ✅ **Project Dropdown Placement**: ProjectSelector appears where "Kanban Board" text previously was (below main title, above columns)
2. ✅ **Title Remains Left-Aligned**: "Task Management" title stays in current position
3. ✅ **Theme Toggle Positioned Upper Right**: Toggle button appears in header right corner
4. ✅ **Theme Toggle Functionality**: Clicking toggle switches between light and dark modes
5. ✅ **Theme Persistence**: Selected theme persists across browser sessions (localStorage)
6. ✅ **Dark Mode Applies**: All components correctly display with dark theme classes when dark mode active

### Visual/Layout Requirements
7. ✅ **Matches Mockup**: Layout exactly matches user's provided ASCII mockup
8. ✅ **No Layout Shift**: Changes don't cause jarring visual shifts or flashing
9. ✅ **Responsive Design**: Layout works on mobile, tablet, and desktop viewports
10. ✅ **Smooth Transitions**: Theme changes have smooth fade transitions (already exist via Tailwind)

### Technical Requirements
11. ✅ **No Console Errors**: No JavaScript errors in browser console
12. ✅ **Accessibility Maintained**: All ARIA labels, keyboard navigation work correctly
13. ✅ **Dark Mode Classes**: All dark: variants apply correctly when theme is "dark"
14. ✅ **localStorage Works**: Theme preference saves and loads correctly

### Testing Requirements
15. ✅ **Manual Testing**: Click theme toggle → mode changes → refresh page → mode persists
16. ✅ **Component Tests Pass**: Updated/created tests pass for modified components
17. ✅ **Cross-Browser**: Works in Chrome, Firefox, Safari, Edge

## Known Issues & Gotchas

### Issue 1: Theme Toggle Doesn't Respond to Clicks
- **Status**: PRIMARY BUG TO FIX
- **Root Cause**: Missing `darkMode: 'class'` in tailwind.config.js
- **Impact**: Dark mode classes don't apply, toggle appears to do nothing
- **Fix**: Add `darkMode: 'class'` to tailwind.config.js and rebuild
- **Validation**: Click toggle → verify document.documentElement gets 'dark' class → verify dark: styles apply

### Issue 2: Project Dropdown in Wrong Position
- **Status**: LAYOUT ISSUE
- **Current Position**: Upper right corner with ThemeToggle (line 131-138 in KanbanBoard.tsx)
- **Desired Position**: Replace "Kanban Board" header (should be at line 142-149 area)
- **Fix**: Move ProjectSelector from header flex to board sub-header section
- **Impact**: Low risk - pure JSX restructuring

### Issue 3: "Kanban Board" Header Still Visible
- **Status**: NEEDS REMOVAL
- **Location**: KanbanBoard.tsx lines 142-149
- **Fix**: Remove or replace this section with ProjectSelector
- **Impact**: May need to keep task count display (line 147-148)

### Potential Gotcha: ThemeContext Not Initialized Properly
- **Likelihood**: Low (verified App.tsx wraps ThemeProvider)
- **Check**: Ensure ThemeProvider is outermost wrapper (currently is - App.tsx line 33)
- **Symptom**: useTheme() throws "must be used within ThemeProvider" error
- **Current Status**: Correctly implemented

### Potential Gotcha: Event Bubbling Issues
- **Likelihood**: Low
- **Symptom**: onClick on ThemeToggle button gets intercepted by parent
- **Debug**: Add console.log to toggleTheme function to verify it's called
- **Mitigation**: Use event.stopPropagation() if needed (unlikely)

### Potential Gotcha: CSS Specificity Conflicts
- **Likelihood**: Low
- **Symptom**: Dark mode classes exist but don't apply due to specificity
- **Debug**: Inspect element → verify dark: classes are in DOM → check computed styles
- **Mitigation**: Use !important (last resort) or increase specificity

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus Areas**:
1. **Verify Tailwind darkMode strategy** across all CSS files
2. **Find all dark: variant usages** to ensure consistency
3. **Locate any custom CSS** that might override Tailwind dark mode
4. **Search for existing theme toggle tests** if any exist
5. **Find similar layout restructuring PRPs** in project history (check git log for header/layout commits)

**Search Patterns**:
```bash
# Find dark mode Tailwind classes
grep -r "dark:" src/

# Find tailwind config files
find . -name "tailwind.config.*"

# Find theme-related tests
grep -r "theme" src/**/*.test.tsx

# Find localStorage usage patterns
grep -r "localStorage" src/
```

### Documentation Hunter
**Find Documentation For**:
1. **Tailwind CSS Dark Mode**: Official docs for `darkMode: 'class'` configuration
   - URL: https://tailwindcss.com/docs/dark-mode
2. **Radix UI Select**: Styling and layout customization
   - URL: https://www.radix-ui.com/primitives/docs/components/select
3. **React Context Best Practices**: Theme context patterns
   - URL: https://react.dev/reference/react/useContext
4. **localStorage API**: Error handling and fallbacks
   - URL: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

**Extract Sections On**:
- Class-based dark mode implementation
- localStorage quota exceeded errors
- Radix Select Portal behavior (already documented in code - Gotcha #6)

### Example Curator
**Extract Examples Showing**:
1. **Tailwind darkMode config** examples from similar projects
2. **React theme toggle** implementations with localStorage
3. **Layout restructuring** patterns (moving components between sections)
4. **Radix UI Select** custom styling examples
5. **Debug onClick handlers** that don't fire (event propagation)

**Priority Examples**:
- Complete tailwind.config.js with dark mode
- Theme toggle with persistence pattern
- Header layout with flex positioning

### Gotcha Detective
**Investigate These Problem Areas**:
1. **Tailwind Dark Mode Not Working**
   - Missing darkMode config
   - Build not recompiling after config change
   - PostCSS not processing dark: variants

2. **onClick Not Firing**
   - Parent element blocking clicks (pointer-events)
   - Event handler not properly bound
   - Component re-rendering removing handler

3. **Layout Shift During Restructure**
   - Flexbox sizing issues
   - Missing min-height/max-height constraints
   - Transition timing causing flash

4. **localStorage Edge Cases**
   - QuotaExceededError (unlikely for single theme value)
   - localStorage disabled in private browsing
   - Cross-domain localStorage access

5. **Dark Mode Classes Not Applying**
   - CSS specificity conflicts
   - Tailwind purging classes incorrectly
   - Missing dark: prefix on some elements

## File Change Summary

### Files to Modify (Confirmed)
1. **tailwind.config.js** (CRITICAL FIX)
   - Add `darkMode: 'class'` configuration
   - Current: Missing darkMode setting
   - Impact: HIGH - Enables dark mode functionality

2. **infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx**
   - Move ProjectSelector from header (lines 131-138) to board section
   - Remove "Kanban Board" h2 header (lines 143-145)
   - Adjust layout structure and spacing
   - Impact: MEDIUM - Layout changes only

### Files to Potentially Create
1. **infra/task-manager/frontend/src/components/__tests__/ThemeToggle.test.tsx**
   - Test onClick behavior
   - Test theme persistence
   - Test icon switching
   - Priority: MEDIUM (may already exist)

### Files to Update Tests
1. **infra/task-manager/frontend/src/features/tasks/components/__tests__/KanbanBoard.test.tsx** (if exists)
   - Update snapshot tests for new layout
   - Verify ProjectSelector in correct position
   - Priority: LOW (validation only)

### Files Already Correct (No Changes)
1. **ThemeContext.tsx** - Implementation is correct
2. **ThemeToggle.tsx** - Component is correct
3. **App.tsx** - ThemeProvider wrapping is correct
4. **ProjectSelector.tsx** - Component works as-is

## Risk Assessment

### High Risk Items
1. **Tailwind Build Process**: If darkMode config doesn't trigger rebuild, may need manual rebuild or dev server restart
   - Mitigation: Document restart requirement in PRP

### Medium Risk Items
1. **Layout Breaking on Mobile**: Repositioning ProjectSelector might break responsive layout
   - Mitigation: Test on multiple viewport sizes
2. **Unforeseen onClick Bug**: If Tailwind fix doesn't resolve toggle issue, deeper debugging needed
   - Mitigation: Add console logging, check event propagation

### Low Risk Items
1. **Component Re-renders**: Layout changes are simple JSX moves
2. **Prop Interface Changes**: No props need to change
3. **Breaking Changes**: All changes are isolated to KanbanBoard component

## Validation Gates

### Gate 1: Tailwind Configuration
```bash
# Verify darkMode config exists
cat tailwind.config.js | grep darkMode

# Expected: darkMode: 'class',
```

### Gate 2: Build Success
```bash
# Rebuild Tailwind with new config
npm run dev  # or yarn dev / bun dev

# Verify no build errors
# Verify dark: classes in generated CSS
```

### Gate 3: Theme Toggle Functionality
```javascript
// Open browser console
document.documentElement.classList.contains('dark')  // Should toggle on click

// Click toggle button
// Run again - should return opposite value
```

### Gate 4: Visual Verification
1. Open app in browser
2. Verify layout matches mockup:
   - "Task Management" title on left
   - Theme toggle on right (same row as title)
   - Project dropdown below title (NOT in header row)
   - "Kanban Board" header removed
   - Task count below project dropdown
3. Click theme toggle → all components change to dark theme
4. Refresh page → theme persists

### Gate 5: Accessibility Check
```bash
# Run accessibility audit
npm run test:a11y  # if exists

# Manual check:
# - Tab through all elements
# - Verify focus visible states
# - Test screen reader announcements
```

## Implementation Complexity Estimate

### Complexity: LOW-MEDIUM
- **Tailwind Config**: 1 line change (darkMode: 'class')
- **Layout Restructure**: 20-30 lines of JSX movement in KanbanBoard.tsx
- **Testing**: Update existing tests, possibly add theme toggle test
- **Total Effort**: 1-2 hours for experienced React developer

### Confidence Level: HIGH
- Clear requirements from INITIAL.md
- Well-understood problem (config + layout)
- No API or backend changes
- Existing patterns to follow

## Architecture Decision Records

### ADR 1: Use Tailwind Class-Based Dark Mode
- **Decision**: Use `darkMode: 'class'` instead of media query
- **Rationale**: Allows user control via toggle (vs system preference)
- **Trade-offs**: Doesn't auto-sync with OS dark mode (acceptable per requirements)
- **Status**: Required fix

### ADR 2: Keep ProjectSelector Component Unchanged
- **Decision**: Don't modify ProjectSelector logic, only reposition
- **Rationale**: Component is well-implemented and tested
- **Trade-offs**: May need width/styling adjustments for new position
- **Status**: Recommended approach

### ADR 3: localStorage for Theme Persistence
- **Decision**: Use localStorage instead of cookies or server-side storage
- **Rationale**: Simple, fast, no server round-trip, already implemented
- **Trade-offs**: Not synced across devices (acceptable for MVP)
- **Status**: Already implemented correctly

### ADR 4: Single-Level Layout Restructure
- **Decision**: Move components within KanbanBoard, don't create new components
- **Rationale**: Keeps changes minimal, easier to review
- **Trade-offs**: Could extract to separate HeaderSection component later
- **Status**: Recommended for this iteration

## Performance Considerations

### Already Optimized (No Changes Needed)
1. **React.memo on ProjectSelector** (line 48) - Prevents unnecessary re-renders
2. **useCallback for event handlers** - Stable references
3. **useMemo for currentProject lookup** - Cached computation
4. **Tailwind JIT mode** - Fast build times

### Potential Optimizations (Future)
1. **Lazy load theme preference** - Currently loads synchronously (acceptable)
2. **Debounce theme toggle** - Prevent rapid clicking issues (unlikely needed)
3. **CSS containment** - Use `contain: layout paint` for theme transitions (micro-optimization)

## Browser Compatibility

### Target Browsers (Inferred)
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (iOS 12.2+)
- Internet Explorer: ❌ Not supported (React 18 requires modern browsers)

### Critical APIs Used
- **localStorage**: IE8+ (✅ Universal support)
- **CSS Grid**: IE11+ with -ms prefix (✅ Modern browsers)
- **Flexbox**: IE11+ with bugs (✅ Modern browsers)
- **Tailwind dark: variants**: Any browser supporting class-based CSS (✅ Universal)

## Monitoring & Validation

### Post-Deployment Checks
1. **Console Errors**: Monitor for any JavaScript errors related to theme
2. **localStorage Usage**: Verify theme key is set correctly
3. **User Feedback**: Confirm layout matches expectations
4. **Accessibility Audit**: Run automated and manual checks

### Rollback Plan
- **Low Risk**: Changes are purely frontend and non-breaking
- **Rollback Method**: Git revert commit
- **No Data Migration**: No database or API changes to revert

---

## Summary for PRP Assembly

This feature requires:
1. **One critical configuration fix**: Add `darkMode: 'class'` to tailwind.config.js
2. **One layout restructure**: Move ProjectSelector and remove "Kanban Board" header in KanbanBoard.tsx
3. **Validation**: Test theme toggle functionality and layout match to mockup

The implementation is straightforward with low risk and high confidence. All required components and patterns already exist in the codebase. The main issue is a missing Tailwind configuration that prevents dark mode from functioning.

**Estimated Completion Time**: 1-2 hours
**Risk Level**: Low
**Complexity**: Low-Medium
**Dependencies**: None (all required code exists)
