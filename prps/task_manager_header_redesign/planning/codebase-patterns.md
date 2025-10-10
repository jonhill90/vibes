# Codebase Patterns: Task Manager Header Redesign

## Overview
This document catalogs existing patterns in the task-manager codebase relevant to the header redesign feature. The codebase demonstrates mature React patterns with comprehensive dark mode support, robust localStorage handling, and well-documented gotcha prevention. All patterns analyzed are from the local codebase - Archon search yielded no directly relevant React theme toggle or header layout examples.

## Architectural Patterns

### Pattern 1: React Context for Global State (ThemeContext)
**Source**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/contexts/ThemeContext.tsx`
**Relevance**: 10/10 - Core pattern for theme management

**What it does**: Provides centralized theme state management with localStorage persistence. Automatically applies 'dark' class to document.documentElement and syncs with localStorage on every theme change.

**Key Techniques**:
```typescript
// Pattern: Dual useEffect pattern for initialization and synchronization
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light"); // Default to light mode

  // Effect 1: Initialize from localStorage (runs once)
  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored === "dark" || stored === "light") {
      setTheme(stored);
    }
  }, []);

  // Effect 2: Apply theme to DOM and persist (runs on every theme change)
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

**When to use**:
- Global state that needs persistence (theme, user preferences)
- State shared across multiple unrelated components
- When prop drilling would require 3+ levels of passing

**How to adapt**:
- Already implemented correctly - no changes needed
- Will work immediately after Tailwind darkMode config fix

**Why this pattern**:
- Separation of concerns: Context handles state, localStorage handles persistence
- Dual useEffect prevents flash of wrong theme on page load
- Type-safe with TypeScript Theme union type
- Prevents hydration mismatches with localStorage check

---

### Pattern 2: Type-Safe localStorage Wrapper (ProjectStorage)
**Source**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/utils/projectStorage.ts`
**Relevance**: 8/10 - Same pattern could be applied to theme storage

**What it does**: Wraps localStorage with comprehensive error handling for quota exceeded, private browsing mode, and cookie restrictions. Provides graceful fallback to in-memory storage.

**Key Techniques**:
```typescript
class ProjectStorage {
  private static readonly KEY = 'selectedProjectId';
  private static inMemoryFallback: string | null = null;
  private static isAvailable: boolean | null = null;

  // Cross-browser quota detection
  private static isQuotaExceeded(e: any): boolean {
    if (!e) return false;
    if (e.code) {
      switch (e.code) {
        case 22: return true; // Standard quota exceeded
        case 1014: return e.name === 'NS_ERROR_DOM_QUOTA_REACHED'; // Firefox
      }
    }
    if (e.number === -2147024882) return true; // IE8
    return e.name === 'QuotaExceededError';
  }

  static set(projectId: string | null): void {
    // Always update in-memory first (never fails)
    this.inMemoryFallback = projectId;

    try {
      if (projectId === null) {
        localStorage.removeItem(this.KEY);
      } else {
        localStorage.setItem(this.KEY, projectId);
      }
    } catch (e) {
      if (this.isQuotaExceeded(e)) {
        // Retry after clearing
        localStorage.removeItem(this.KEY);
        if (projectId !== null) {
          localStorage.setItem(this.KEY, projectId);
        }
      }
      // Gracefully fall back to in-memory (already set above)
    }
  }
}
```

**When to use**:
- Production localStorage access (prevents app crashes)
- When localStorage quota limits are a concern
- Supporting private browsing modes (Safari)

**How to adapt**:
- ThemeContext currently uses raw localStorage - could wrap with similar pattern
- For MVP, current implementation is acceptable (theme is single string, unlikely to hit quota)
- Consider adding try-catch in ThemeContext for private browsing support

**Why this pattern**:
- Prevents SecurityError crashes in private browsing
- Handles QuotaExceededError across browsers (error codes vary)
- In-memory fallback ensures feature works even without localStorage
- Automatic retry after clearing maximizes success rate

---

### Pattern 3: Provider Nesting Hierarchy (App.tsx)
**Source**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/App.tsx`
**Relevance**: 9/10 - Shows correct provider ordering

**What it does**: Establishes provider hierarchy with ThemeProvider as outermost wrapper, enabling dark mode for all descendant components including DndProvider and QueryClientProvider.

**Key Techniques**:
```typescript
function App() {
  return (
    // CRITICAL: ThemeProvider wraps app for light/dark mode
    <ThemeProvider>
      {/* DndProvider wraps entire app for drag-and-drop functionality */}
      <DndProvider backend={HTML5Backend}>
        <QueryClientProvider client={queryClient}>
          <KanbanPage />
        </QueryClientProvider>
      </DndProvider>
    </ThemeProvider>
  );
}
```

**Provider Ordering Rules**:
1. **ThemeProvider** (outermost) - Affects all UI, including provider UI
2. **DndProvider** - Needs theme for drag previews
3. **QueryClientProvider** - Data layer, doesn't need theme directly
4. **Application Components** (innermost)

**When to use**:
- Multiple context providers needed
- Order matters for dependency graph
- UI providers should wrap data providers

**How to adapt**:
- Already correctly implemented
- ThemeProvider placement ensures all components get dark mode
- No changes needed for this feature

**Why this pattern**:
- ThemeProvider outermost allows dark mode to style all providers
- Follows React best practice: outer providers = broader scope
- Single source of truth for theme state

---

### Pattern 4: Flex Layout with justify-between (Header Pattern)
**Source**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx:119`
**Relevance**: 10/10 - Exact pattern used in current header

**What it does**: Creates responsive header layout with title on left, controls on right, using Tailwind flex utilities.

**Key Techniques**:
```typescript
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
```

**Tailwind Pattern Breakdown**:
- `mb-6` - Bottom margin for spacing from content below
- `flex items-center justify-between` - Flex row, vertical center, space between
- `gap-4` - Spacing between right-side controls (1rem = 16px)
- `text-gray-900 dark:text-gray-100` - Dark mode color variant

**When to use**:
- Header/toolbar layouts with left-aligned title and right-aligned controls
- Responsive layouts that need consistent spacing
- When avoiding absolute positioning (which breaks responsive)

**How to adapt for this feature**:
1. Keep outer flex container (already correct)
2. Remove ProjectSelector from right side `<div className="flex items-center gap-4">`
3. Leave only ThemeToggle in right side
4. Move ProjectSelector to board sub-header section (replace "Kanban Board" h2)

**Why this pattern**:
- `justify-between` auto-distributes space (no manual spacing needed)
- `items-center` ensures vertical alignment regardless of content height
- Works on all screen sizes without media queries
- Maintains ARIA landmark structure (header contains navigation)

---

### Pattern 5: Component Layout Restructuring (Board Sub-header)
**Source**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx:142-149`
**Relevance**: 10/10 - Exact section to be modified

**What it does**: Displays board title ("Kanban Board") and task count in a sub-header section below main header.

**Current Implementation**:
```typescript
{/* Board Sub-header */}
<div className="mb-6">
  <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
    Kanban Board
  </h2>
  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
    {tasks?.length || 0} tasks total
  </p>
</div>
```

**What needs to change**:
```typescript
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
```

**Key changes**:
1. Remove `<h2>Kanban Board</h2>` (lines 143-145)
2. Replace with `<ProjectSelector />` component
3. Keep task count paragraph (already has dark mode styling)
4. Maintain `mb-6` margin for consistent spacing

**When to use**:
- When replacing a header element with an interactive component
- Need to maintain vertical spacing and dark mode consistency
- Component should feel like a natural header replacement

**How to adapt**:
- Simply swap h2 element for ProjectSelector component
- ProjectSelector already has proper min-width and dark mode styles
- May need to adjust ProjectSelector width if it looks too narrow as a header

**Why this pattern**:
- Maintains visual hierarchy (sub-header below main header)
- Dark mode classes already applied to task count text
- Consistent margin-bottom (mb-6) creates rhythm

---

## Naming Conventions

### File Naming
**Pattern**: `{ComponentName}.tsx` for components, `{featureName}Context.tsx` for contexts
**Examples**:
- `ThemeContext.tsx` - Context provider for theme state
- `ThemeToggle.tsx` - UI component for toggle button
- `KanbanBoard.tsx` - Main board component
- `ProjectSelector.tsx` - Dropdown selector component

**Rules**:
- PascalCase for all React component files
- Suffix with `.tsx` (TypeScript + JSX)
- Context files always end with `Context.tsx`
- Test files: `{ComponentName}.test.tsx` in `__tests__/` subdirectory

### Class Naming (Tailwind)
**Pattern**: Utility-first with dark: prefix for dark mode variants
**Examples**:
```typescript
// Background colors
"bg-gray-200 dark:bg-gray-700"
"bg-white dark:bg-gray-800"

// Text colors
"text-gray-900 dark:text-gray-100"
"text-gray-600 dark:text-gray-400"

// Border colors
"border-gray-300 dark:border-gray-600"

// Focus rings
"focus:ring-blue-500 dark:focus:ring-blue-400"
"focus:ring-offset-2 dark:focus:ring-offset-gray-900"
```

**Dark Mode Color Scale**:
- Light mode: Lower numbers (100-600) for backgrounds, higher (700-900) for text
- Dark mode: Higher numbers (700-900) for backgrounds, lower (100-400) for text
- Maintains contrast ratio for WCAG AA compliance

### Function Naming
**Pattern**: `handle{Action}` for event handlers, `use{Feature}` for hooks
**Examples**:
- `toggleTheme()` - Simple action function
- `handleTaskMove()` - Event handler for drag-and-drop
- `useTheme()` - Custom hook for theme context
- `useProjectTasks()` - Query hook for data fetching

### Variable Naming
**Pattern**: camelCase for variables, SCREAMING_SNAKE_CASE for constants
**Examples**:
```typescript
const theme = "light"; // Variable
const COLUMNS: Array<{ status: TaskStatus; label: string }> = [...]; // Constant array
const KEY = 'selectedProjectId'; // Constant string
```

---

## File Organization

### Directory Structure
```
infra/task-manager/frontend/src/
├── components/                    # Shared components
│   ├── ThemeToggle.tsx           # Global theme toggle button
│   └── __tests__/                # Component tests
├── contexts/                      # Global contexts
│   └── ThemeContext.tsx          # Theme provider and hook
├── features/                      # Feature modules
│   ├── projects/
│   │   ├── components/           # Project-specific components
│   │   │   ├── ProjectSelector.tsx
│   │   │   └── __tests__/
│   │   ├── hooks/                # Project queries and mutations
│   │   ├── services/             # API service layer
│   │   └── utils/                # Project utilities
│   │       └── projectStorage.ts # localStorage wrapper
│   ├── tasks/
│   │   ├── components/
│   │   │   └── KanbanBoard.tsx   # Main board (file to modify)
│   │   └── hooks/
│   └── shared/                   # Shared feature code
│       ├── api/
│       ├── config/
│       └── hooks/
├── pages/                         # Page components
│   └── KanbanPage.tsx            # Main page container
├── App.tsx                        # Root component
├── index.css                      # Global styles + Tailwind
└── main.tsx                       # Entry point
```

**Justification**:
- **Feature-first organization** - Projects and tasks are separate domains
- **Shared components at top level** - ThemeToggle used across features
- **Contexts separate** - Global state lives in dedicated folder
- **Co-location of tests** - Each component has `__tests__/` adjacent
- **Utils next to features** - projectStorage.ts near components that use it

**Pattern Rules**:
1. Shared components (used by 2+ features) go in `/components`
2. Feature-specific components stay in `/features/{feature}/components`
3. Contexts are global by definition, always in `/contexts`
4. Tests co-located with source in `__tests__/` subdirectories

---

## Common Utilities to Leverage

### 1. useTheme Hook
**Location**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/contexts/ThemeContext.tsx:56`
**Purpose**: Access theme state and toggle function from any component
**Usage Example**:
```typescript
import { useTheme } from "../contexts/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      {theme === "light" ? <Moon /> : <Sun />}
    </button>
  );
}
```

**Key Points**:
- Throws error if used outside ThemeProvider (dev-time safety)
- Returns `{ theme: "light" | "dark", toggleTheme: () => void }`
- Automatically triggers re-render when theme changes

---

### 2. ProjectStorage Class
**Location**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/utils/projectStorage.ts`
**Purpose**: Type-safe localStorage wrapper with error handling
**Usage Example**:
```typescript
import ProjectStorage from "../../utils/projectStorage";

// Save selection
ProjectStorage.set("project-123");

// Retrieve (returns string | null)
const projectId = ProjectStorage.get();

// Clear
ProjectStorage.clear();
```

**Key Points**:
- Static class (no instantiation needed)
- Handles quota exceeded, private browsing, cookie restrictions
- In-memory fallback if localStorage unavailable
- Cross-browser error code detection

---

### 3. Tailwind Dark Mode Classes
**Location**: Throughout codebase (163 occurrences across 13 files)
**Purpose**: Consistent dark mode styling pattern
**Usage Example**:
```typescript
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
  <button className="
    bg-gray-200 dark:bg-gray-700
    hover:bg-gray-300 dark:hover:bg-gray-600
    focus:ring-blue-500 dark:focus:ring-blue-400
    transition-colors duration-200
  ">
    Click me
  </button>
</div>
```

**Standard Color Mappings**:
| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Primary BG | `bg-white` | `dark:bg-gray-800` |
| Secondary BG | `bg-gray-100` | `dark:bg-gray-900` |
| Interactive BG | `bg-gray-200` | `dark:bg-gray-700` |
| Primary Text | `text-gray-900` | `dark:text-gray-100` |
| Secondary Text | `text-gray-600` | `dark:text-gray-400` |
| Border | `border-gray-300` | `dark:border-gray-600` |
| Focus Ring | `ring-blue-500` | `dark:ring-blue-400` |

**Transition Pattern**: Always add `transition-colors duration-200` for smooth theme changes

---

### 4. React.memo for Performance
**Location**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/components/ProjectSelector.tsx:48`
**Purpose**: Prevent unnecessary re-renders of expensive components
**Usage Example**:
```typescript
import { memo, useCallback, useMemo } from "react";

export const ProjectSelector = memo(({
  selectedProjectId,
  onProjectChange,
  onCreateProject,
}: ProjectSelectorProps) => {
  // Memoize expensive computations
  const currentProject = useMemo(
    () => projects?.find((p) => p.id === selectedProjectId),
    [projects, selectedProjectId]
  );

  // Memoize callbacks to prevent child re-renders
  const handleValueChange = useCallback((value: string) => {
    if (value === "__create_new_project__") {
      onCreateProject();
    } else {
      onProjectChange(value);
    }
  }, [onCreateProject, onProjectChange]);

  return <Select.Root value={selectedProjectId} onValueChange={handleValueChange}>
    {/* ... */}
  </Select.Root>;
});
```

**When to use**:
- Components that render frequently (e.g., in lists, or with polling data)
- Components with expensive computations
- Always pair with `useCallback` for event handlers
- Always pair with `useMemo` for derived data

---

### 5. useCallback Pattern
**Location**: Found in 3 files (KanbanPage.tsx, ProjectSelector.tsx, TaskListView.tsx)
**Purpose**: Stable function references to prevent child re-renders
**Usage Example**:
```typescript
const handleProjectChange = useCallback((projectId: string) => {
  setSelectedProjectId(projectId);
  ProjectStorage.set(projectId);
}, []); // Empty deps = function never changes

const handleCreateProject = useCallback(() => {
  setCreateModalOpen(true);
}, []);
```

**Rules**:
- Wrap all callbacks passed to memoized children
- Include all external values in deps array
- Empty deps array if function is truly stable
- Don't over-use: only for props passed to memo'd components

---

## Testing Patterns

### Unit Test Structure
**Pattern**: Vitest + React Testing Library with QueryClient wrapper
**Example**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/components/__tests__/ProjectSelector.test.tsx`

**Key techniques**:

#### 1. Test Setup with QueryClient Wrapper
```typescript
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

describe("ProjectSelector", () => {
  let queryClient: QueryClient;

  const createWrapper = () => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },  // No retries in tests
        mutations: { retry: false },
      },
    });

    return ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });
});
```

#### 2. Service Mocking Pattern
```typescript
// Mock at module level
vi.mock("../../services/projectService", () => ({
  projectService: {
    listProjects: vi.fn(),
  },
}));

// Configure in tests
it("should show loading state", () => {
  vi.mocked(projectService.listProjects).mockImplementation(
    () => new Promise(() => {}) // Never resolves
  );

  render(<ProjectSelector />, { wrapper: createWrapper() });

  expect(screen.getByRole("status")).toBeInTheDocument();
});
```

#### 3. User Interaction Testing
```typescript
it("should call onProjectChange when project selected", async () => {
  const user = userEvent.setup();
  const mockOnProjectChange = vi.fn();

  render(<ProjectSelector onProjectChange={mockOnProjectChange} />,
    { wrapper: createWrapper() }
  );

  await waitFor(() => {
    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  // Open dropdown
  const trigger = screen.getByRole("combobox");
  await user.click(trigger);

  // Wait for dropdown to open
  await waitFor(() => {
    expect(screen.getByRole("listbox")).toBeInTheDocument();
  });

  // Select item
  const option = screen.getByRole("option", { name: /project beta/i });
  await user.click(option);

  expect(mockOnProjectChange).toHaveBeenCalledWith("project-2");
});
```

#### 4. Accessibility Testing
```typescript
it("should have accessible ARIA attributes", async () => {
  render(<ProjectSelector />, { wrapper: createWrapper() });

  await waitFor(() => {
    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  const trigger = screen.getByRole("combobox");
  expect(trigger).toHaveAttribute("aria-label", "Select project");
  expect(trigger).toHaveAttribute("aria-haspopup", "listbox");
});

it("should support keyboard navigation", async () => {
  const user = userEvent.setup();

  render(<ProjectSelector />, { wrapper: createWrapper() });

  const trigger = screen.getByRole("combobox");
  trigger.focus();

  // Open with Space
  await user.keyboard(" ");

  // Navigate with arrows
  await user.keyboard("{ArrowDown}");
  await user.keyboard("{Enter}");

  await waitFor(() => {
    expect(mockOnProjectChange).toHaveBeenCalled();
  });
});
```

#### 5. Loading/Error State Testing
```typescript
it("should show error state with retry button", async () => {
  const error = new Error("Network error");
  vi.mocked(projectService.listProjects).mockRejectedValue(error);

  render(<ProjectSelector />, { wrapper: createWrapper() });

  await waitFor(() => {
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
});
```

---

### Integration Test Structure
**Pattern**: Not found in codebase - tests are component-level unit tests
**Recommendation**: For theme toggle integration test, consider:

```typescript
// ThemeToggle.test.tsx (to be created)
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ThemeProvider } from "../contexts/ThemeContext";
import { ThemeToggle } from "../components/ThemeToggle";

describe("ThemeToggle Integration", () => {
  it("should toggle theme and persist to localStorage", async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggleButton = screen.getByRole("button", { name: /switch to dark mode/i });

    // Initial state: light mode
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe("light");

    // Click toggle
    await user.click(toggleButton);

    // Verify dark mode applied
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(localStorage.getItem("theme")).toBe("dark");

    // Click again
    await user.click(toggleButton);

    // Back to light mode
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe("light");
  });
});
```

---

## Anti-Patterns to Avoid

### 1. Missing Tailwind darkMode Configuration
**What it is**: Using dark: class variants without `darkMode: 'class'` in tailwind.config.js
**Why to avoid**: Dark mode classes won't be generated in CSS bundle, toggle appears broken
**Found in**: Current issue - tailwind.config.js line 2-11 missing darkMode setting
**Better approach**:
```javascript
// tailwind.config.js
export default {
  darkMode: 'class', // REQUIRED for dark: variants to work
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Impact**: HIGH - Without this, no dark mode classes are generated, toggle does nothing visually

---

### 2. Raw localStorage Access Without Error Handling
**What it is**: Directly calling `localStorage.setItem()` or `localStorage.getItem()` without try-catch
**Why to avoid**:
- Crashes in private browsing mode (SecurityError)
- Fails when cookies disabled (DOMException)
- QuotaExceededError in restricted environments
**Found in**: ThemeContext.tsx uses raw localStorage (lines 28, 42)
**Better approach**:
```typescript
// Current (risky)
const stored = localStorage.getItem("theme");
localStorage.setItem("theme", theme);

// Better (safe)
try {
  const stored = localStorage.getItem("theme");
  if (stored === "dark" || stored === "light") {
    setTheme(stored);
  }
} catch (e) {
  console.warn("localStorage unavailable:", e);
  // Use default theme
}

try {
  localStorage.setItem("theme", theme);
} catch (e) {
  console.warn("Failed to persist theme:", e);
  // Still works, just doesn't persist
}
```

**Impact**: MEDIUM - App crashes in private browsing or restricted environments. For theme, low risk (single string won't hit quota), but best practice is to wrap all localStorage access.

---

### 3. Calling Mutations When Already Pending
**What it is**: Triggering `mutate()` without checking `isPending` flag
**Why to avoid**: Race conditions, duplicate API calls, optimistic update conflicts
**Found in**: KanbanBoard.tsx addresses this (Gotcha #9, lines 58-61)
**Better approach**:
```typescript
// Anti-pattern
const handleTaskMove = (taskId: string, newStatus: TaskStatus) => {
  updateTaskPosition.mutate({ taskId, status: newStatus }); // May fire twice!
};

// Correct pattern
const handleTaskMove = (taskId: string, newStatus: TaskStatus) => {
  // GOTCHA: Don't call mutation if already pending
  if (updateTaskPosition.isPending) {
    console.warn("Task position update already in progress");
    return;
  }

  updateTaskPosition.mutate({ taskId, status: newStatus });
};
```

**Impact**: MEDIUM - Causes duplicate network requests and potential data corruption if optimistic updates conflict

---

### 4. Missing cancelQueries in onMutate
**What it is**: Performing optimistic updates without canceling in-flight queries
**Why to avoid**: Background refetch can overwrite optimistic update, causing UI flicker
**Found in**: All mutation hooks correctly address this (Gotcha #1 and #4)
**Better approach**:
```typescript
// Anti-pattern
onMutate: async (newData) => {
  const previous = queryClient.getQueryData(queryKey);
  queryClient.setQueryData(queryKey, [...previous, newData]); // Race condition!
  return { previous };
}

// Correct pattern
onMutate: async (newData) => {
  // GOTCHA #4: Cancel any outgoing refetches to avoid race conditions
  await queryClient.cancelQueries({ queryKey });

  const previous = queryClient.getQueryData(queryKey);
  queryClient.setQueryData(queryKey, [...previous, newData]);
  return { previous };
}
```

**Impact**: HIGH - Causes visual glitches, optimistic updates get overwritten, poor UX

---

### 5. Forgetting Dark Mode Variants on Interactive Elements
**What it is**: Applying dark mode to container but not to interactive states (hover, focus)
**Why to avoid**: Focus rings invisible in dark mode, accessibility failure
**Found in**: Codebase correctly applies dark: to all interactive states
**Better approach**:
```typescript
// Anti-pattern (missing dark: on hover and focus)
<button className="
  bg-gray-200 dark:bg-gray-700
  hover:bg-gray-300
  focus:ring-2 focus:ring-blue-500
">

// Correct pattern
<button className="
  bg-gray-200 dark:bg-gray-700
  hover:bg-gray-300 dark:hover:bg-gray-600
  focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400
  focus:ring-offset-2 dark:focus:ring-offset-gray-900
">
```

**Impact**: MEDIUM - Accessibility issue, hover states wrong color, focus rings invisible

---

### 6. Hard-Coding Colors Instead of Tailwind Utilities
**What it is**: Using inline styles or custom CSS for colors instead of Tailwind
**Why to avoid**: Loses dark mode support, inconsistent color palette, maintenance burden
**Better approach**:
```typescript
// Anti-pattern
<div style={{ backgroundColor: '#f3f4f6', color: '#111827' }}>

// Correct pattern
<div className="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

**Impact**: LOW - Mostly cosmetic, but creates inconsistent theming

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. ProjectSelector Component
**Location**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/components/ProjectSelector.tsx`
**Similarity**: Interactive dropdown component with dark mode, currently in header
**Lessons**:
- Uses Radix UI Select for accessibility (same pattern could apply to other dropdowns)
- Comprehensive dark mode styling on all states (trigger, content, items)
- Loading skeleton prevents layout shift (line 78-86)
- Error state with retry button (line 88-104)
- React.memo optimization (line 48)
- useCallback for event handlers (lines 58, 69)

**Differences for current feature**:
- ProjectSelector will move from header to sub-header
- No new component creation needed, just repositioning

---

#### 2. ThemeToggle Button
**Location**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/components/ThemeToggle.tsx`
**Similarity**: Interactive button in header, needs theme awareness
**Lessons**:
- Simple component, single responsibility (just toggles theme)
- Icon changes based on theme state (Moon for light mode, Sun for dark)
- Comprehensive accessibility: aria-label, title attribute, aria-hidden on icons
- Smooth transitions with `transition-colors duration-200`
- Focus ring with dark mode variant

**Differences**:
- Already correctly positioned in header
- No changes needed to component itself

---

#### 3. KanbanBoard Header Layout
**Location**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx:117-149`
**Similarity**: Exact file and section to be modified
**Lessons**:
- Flex layout with justify-between for left/right alignment works well
- Nested divs for grouping related controls (line 131-138)
- Consistent spacing with mb-6 between sections
- Dark mode classes on all text elements

**Differences**:
- Need to move ProjectSelector from line 132-136 to line 142-149 section
- Remove "Kanban Board" h2 header
- Keep task count paragraph

---

#### 4. localStorage Pattern in KanbanPage
**Location**: `/Users/jon/source/vibes/infra/task-manager/frontend/src/pages/KanbanPage.tsx:62`
**Similarity**: Persists user preference (selected project) across sessions
**Lessons**:
- Uses ProjectStorage wrapper for safe localStorage access
- Updates on every change (not just on unmount)
- Validation: checks if stored ID still exists in available projects (Gotcha #4)

**Differences**:
- ThemeContext already handles persistence (no page-level logic needed)
- Theme persistence is simpler (no validation needed, theme is always valid)

---

## Recommendations for PRP

Based on pattern analysis, the PRP should:

1. **Follow Tailwind darkMode Config Fix Pattern**
   - Add `darkMode: 'class'` to tailwind.config.js (line 2)
   - This is the PRIMARY FIX for theme toggle functionality
   - Rebuild required after config change (dev server auto-restarts)

2. **Reuse Existing ThemeContext Pattern**
   - No changes needed to ThemeContext.tsx
   - Already implements correct dual-useEffect pattern
   - localStorage persistence works (just needs Tailwind config fix)

3. **Mirror KanbanBoard Flex Layout Structure**
   - Keep outer header flex container: `<div className="mb-6 flex items-center justify-between">`
   - Remove ProjectSelector from right side (lines 131-138)
   - Keep only ThemeToggle in `<div className="flex items-center gap-4">`

4. **Adapt Board Sub-header Pattern for ProjectSelector**
   - Replace `<h2>Kanban Board</h2>` with `<ProjectSelector />` (line 143-145)
   - Keep existing dark mode classes on task count paragraph
   - Maintain mb-6 margin for consistent vertical rhythm

5. **Avoid Anti-Pattern #1 (Missing Tailwind Config)**
   - Verify `darkMode: 'class'` in tailwind.config.js
   - Rebuild and test theme toggle after config change
   - Check browser DevTools: `document.documentElement.classList` should contain 'dark'

6. **Follow Testing Pattern from ProjectSelector.test.tsx**
   - Create ThemeToggle.test.tsx if needed
   - Test: click toggle → DOM class changes → localStorage updates
   - Test keyboard accessibility (Space/Enter to toggle)
   - Mock localStorage for isolation

7. **Maintain Accessibility Standards**
   - All interactive elements have aria-labels (already present)
   - Keyboard navigation works (Tab, Space, Enter)
   - Focus rings have dark mode variants
   - Color contrast meets WCAG AA (existing palette compliant)

8. **Performance Best Practices**
   - ThemeToggle already optimized (no memo needed, simple component)
   - ProjectSelector already has React.memo wrapper
   - No additional optimization required for this feature

---

## Source References

### From Archon
- **No relevant results** - Archon search for "React theme toggle context" and "Tailwind dark mode config" yielded no direct matches
- Pydantic AI and MCP protocol examples not applicable to this frontend feature
- Recommendation: Rely entirely on local codebase patterns (which are comprehensive)

### From Local Codebase

#### Core Pattern Files
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/contexts/ThemeContext.tsx` - Theme management pattern (Relevance: 10/10)
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/components/ThemeToggle.tsx` - Toggle button pattern (Relevance: 10/10)
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx:117-149` - Layout to modify (Relevance: 10/10)
- `/Users/jon/source/vibes/infra/task-manager/frontend/tailwind.config.js` - Config to fix (Relevance: 10/10)

#### Supporting Patterns
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/App.tsx:33` - Provider nesting (Relevance: 9/10)
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/utils/projectStorage.ts` - localStorage wrapper pattern (Relevance: 8/10)
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/components/ProjectSelector.tsx:48` - React.memo pattern (Relevance: 7/10)
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/index.css:13` - Global dark mode styles (Relevance: 7/10)

#### Test Patterns
- `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/projects/components/__tests__/ProjectSelector.test.tsx` - Component testing pattern (Relevance: 8/10)

#### Gotcha Documentation
- Found 15 files with GOTCHA comments documenting anti-patterns and solutions
- Primary gotchas relevant to this feature:
  - Gotcha #6: Radix Select Portal escapes Dialog (ProjectSelector line 133)
  - Gotcha #9: DndProvider wrapping (App.tsx line 36)
  - Gotcha #10: Polling pauses when tab hidden (queryClient.ts line 48)

---

## Next Steps for Assembler

When generating the PRP, the Assembler should:

### 1. Reference These Patterns in "Current Codebase Tree"
```markdown
## Current Codebase Tree

### Theme System (Already Implemented)
- `/contexts/ThemeContext.tsx` - Theme provider with localStorage persistence
- `/components/ThemeToggle.tsx` - Toggle button (already correct)
- `/App.tsx:33` - ThemeProvider wraps app (already correct)

### Layout to Modify
- `/features/tasks/components/KanbanBoard.tsx:119-149`
  - Line 119-138: Header with title, ProjectSelector, ThemeToggle
  - Line 142-149: Board sub-header with "Kanban Board" h2 (TO BE REPLACED)

### Configuration to Fix
- `/tailwind.config.js:2` - Add `darkMode: 'class'` (CRITICAL)
```

### 2. Include Key Code Snippets in "Implementation Blueprint"

**Step 1: Fix Tailwind Config**
```javascript
// tailwind.config.js
export default {
  darkMode: 'class', // ADD THIS LINE
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Step 2: Restructure KanbanBoard Header**
```typescript
// KanbanBoard.tsx - BEFORE (lines 119-138)
<div className="mb-6 flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
      Task Management
    </h1>
    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
      Organize your tasks with drag-and-drop Kanban board
    </p>
  </div>
  <div className="flex items-center gap-4">
    <ProjectSelector {...props} /> {/* MOVE THIS */}
    <ThemeToggle />
  </div>
</div>

// KanbanBoard.tsx - AFTER
<div className="mb-6 flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
      Task Management
    </h1>
    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
      Organize your tasks with drag-and-drop Kanban board
    </p>
  </div>
  <div className="flex items-center gap-4">
    <ThemeToggle /> {/* ONLY ThemeToggle remains */}
  </div>
</div>
```

**Step 3: Replace Board Sub-header**
```typescript
// KanbanBoard.tsx - BEFORE (lines 142-149)
<div className="mb-6">
  <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
    Kanban Board
  </h2>
  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
    {tasks?.length || 0} tasks total
  </p>
</div>

// KanbanBoard.tsx - AFTER
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
```

### 3. Add Anti-patterns to "Known Gotchas" Section

**Gotcha #1: Missing Tailwind darkMode Config**
- **Symptom**: Theme toggle button clicks, but no visual change occurs
- **Root Cause**: `darkMode: 'class'` missing from tailwind.config.js
- **Detection**: Check generated CSS - no dark: classes present
- **Fix**: Add `darkMode: 'class'` to config, restart dev server
- **Prevention**: Always configure Tailwind dark mode before using dark: variants

**Gotcha #2: Raw localStorage in Private Browsing**
- **Symptom**: App crashes on page load in Safari Private Browsing
- **Root Cause**: SecurityError when accessing localStorage
- **Current Risk**: LOW (ThemeContext uses raw localStorage, but theme is non-critical)
- **Fix**: Wrap localStorage access in try-catch blocks
- **Prevention**: Use ProjectStorage pattern for all localStorage access

**Gotcha #3: Forgetting Dark Mode on Focus Rings**
- **Symptom**: Focus indicators invisible in dark mode
- **Root Cause**: Missing `dark:focus:ring-{color}` and `dark:focus:ring-offset-{color}`
- **Detection**: Tab through UI in dark mode, check if focus visible
- **Fix**: Always pair `focus:ring-{color}` with dark variant
- **Prevention**: Use existing component patterns as reference

### 4. Use File Organization for "Desired Codebase Tree"

**Modified Files**:
```
infra/task-manager/frontend/
├── tailwind.config.js                    # ADD: darkMode: 'class'
└── src/
    └── features/
        └── tasks/
            └── components/
                └── KanbanBoard.tsx       # MODIFY: Lines 119-149
```

**Unchanged Files** (reference for validation):
```
src/
├── contexts/ThemeContext.tsx             # ✅ Already correct
├── components/ThemeToggle.tsx            # ✅ Already correct
├── App.tsx                               # ✅ ThemeProvider wrapping correct
└── features/projects/components/
    └── ProjectSelector.tsx               # ✅ Component works, just reposition
```

### 5. Validation Checklist

**Config Validation**:
- [ ] `darkMode: 'class'` present in tailwind.config.js
- [ ] Dev server restarted after config change
- [ ] Dark mode classes present in generated CSS

**Layout Validation**:
- [ ] "Task Management" title on left (unchanged)
- [ ] ThemeToggle button on right in header
- [ ] ProjectSelector in sub-header (where "Kanban Board" was)
- [ ] Task count below ProjectSelector
- [ ] No layout shift when comparing before/after

**Functionality Validation**:
- [ ] Click theme toggle → `document.documentElement` gains/loses 'dark' class
- [ ] All components change to dark theme colors
- [ ] Refresh page → theme persists from localStorage
- [ ] Private browsing mode: toggle still works (may not persist)

**Accessibility Validation**:
- [ ] Tab through header → all elements reachable
- [ ] Focus visible on all interactive elements (light and dark mode)
- [ ] Space/Enter activates theme toggle
- [ ] Screen reader announces theme changes

---

## Summary

This codebase demonstrates production-ready React patterns with:

- **Comprehensive dark mode support** (163 dark: usages across 13 files)
- **Robust error handling** (ProjectStorage wrapper, gotcha prevention)
- **Performance optimizations** (React.memo, useCallback, useMemo)
- **Accessibility-first design** (ARIA labels, keyboard nav, focus management)
- **Test coverage** (Vitest + RTL with QueryClient mocking)

**Critical Finding**: The theme toggle functionality exists and is correctly implemented. The PRIMARY issue is a missing Tailwind configuration (`darkMode: 'class'`). Once added, the toggle will work immediately.

**Implementation Complexity**: LOW
- 1 line config change (tailwind.config.js)
- 20-30 lines JSX restructuring (KanbanBoard.tsx)
- No new components or logic needed
- Estimated time: 30-60 minutes

**Confidence Level**: VERY HIGH
- All patterns documented and tested in existing code
- Clear before/after examples from similar components
- Single point of failure identified (Tailwind config)
- No ambiguity in requirements
