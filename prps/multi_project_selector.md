# PRP: Multi-Project Selector for Task Manager UI

**Generated**: 2025-10-10
**Based On**: prps/INITIAL_multi_project_selector.md
**Archon Project**: becada72-a984-4e51-b2b4-eee6edfef03c

---

## Goal

Add project selection capability to task-manager UI, enabling users to switch between multiple projects and view their respective Kanban boards. Transform the single-project hardcoded experience into a multi-project interface with project creation, selection persistence, and intuitive navigation.

**End State**:
- User can select from all available projects via dropdown in header
- Selected project persists across page reloads via localStorage
- User can create new projects via modal form
- Kanban board dynamically loads tasks for selected project
- Empty state guides new users to create their first project
- All existing Kanban functionality works unchanged

## Why

**Current Pain Points**:
- Project ID hardcoded in `KanbanPage.tsx` line 17 - no way to switch projects
- Backend supports multiple projects but frontend is single-project only
- Users cannot create or select projects from the UI
- No state persistence - refresh loses context

**Business Value**:
- Unlocks multi-project use case (primary user need)
- Reduces onboarding friction with project creation flow
- Increases user engagement through project organization
- Enables future collaboration features (project-based permissions)
- Matches user mental model (projects contain tasks)

## What

### Core Features

1. **ProjectSelector Component** (dropdown in header)
   - Display all available projects in accessible dropdown
   - Show currently selected project name
   - Enable quick switching between projects
   - Visual indicator for active project
   - "Create New Project" action at bottom of dropdown

2. **CreateProjectModal Component** (modal dialog)
   - Form with name (required) and description (optional) fields
   - Client-side validation (name minimum 1 character)
   - Integration with existing POST `/api/projects` endpoint
   - Optimistic UI updates with rollback on error
   - Auto-select newly created project on success

3. **State Management** (localStorage + TanStack Query)
   - Persist selectedProjectId in localStorage
   - Default to first project if none selected
   - Validate stored ID against current project list
   - Handle edge cases: no projects, deleted project, corrupted storage

4. **EmptyProjectState Component** (onboarding)
   - Centered message "No projects yet"
   - Call-to-action "Create Your First Project" button
   - Triggers CreateProjectModal on click

### Success Criteria

- [ ] User can see list of all projects in dropdown
- [ ] User can switch between projects seamlessly (< 100ms perceived latency)
- [ ] Selected project persists across page reloads (localStorage)
- [ ] User can create new projects via modal form
- [ ] UI clearly shows which project is active (visual indicator)
- [ ] All existing Kanban board functionality works unchanged
- [ ] Graceful handling of edge cases:
  - [ ] No projects: Show create prompt
  - [ ] Deleted project: Auto-select next available
  - [ ] Network error: Show error message with retry
  - [ ] localStorage quota exceeded: Fallback to in-memory state
- [ ] Accessibility: Keyboard navigation works, ARIA labels present
- [ ] Performance: Project list loads in < 500ms, switching feels instant

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - TanStack Query v5
- url: https://tanstack.com/query/v5/docs/framework/react/overview
  sections:
    - "useQuery Hook" - Object-based API (breaking change from v4)
    - "useMutation Hook" - Optimistic updates and rollback
    - "Query Keys Guide" - Hierarchical key structure for cache management
  why: Core state management library for project data, pagination, and mutations
  critical_gotchas:
    - v5 requires object-based syntax: useQuery({ queryKey, queryFn }) not useQuery(key, fn)
    - isPending replaces isLoading (breaking change)
    - gcTime replaces cacheTime (breaking change)
    - MUST call cancelQueries in onMutate to prevent race conditions
    - MUST include all parameters in query keys or cache will collide

- url: https://tanstack.com/query/v5/docs/framework/react/guides/mutations
  sections:
    - "Mutation Lifecycle" - onMutate, onError, onSuccess, onSettled
    - "Optimistic Updates" - Immediate UI feedback with server sync
  why: Project creation requires optimistic UI with rollback
  critical_gotchas:
    - Always snapshot previous data in onMutate for rollback
    - Use mutation keys to track concurrent mutations
    - Check isMutating() count before invalidating queries

- url: https://tanstack.com/query/v5/docs/framework/react/examples/optimistic-updates-cache
  why: Complete working example of optimistic create pattern
  critical: Shows exact pattern for cancelQueries → snapshot → setQueryData → rollback

# MUST READ - Radix UI Primitives
- url: https://www.radix-ui.com/primitives/docs/components/dialog
  sections:
    - "Dialog Component" - Modal vs non-modal, focus management
    - "Accessibility" - ARIA attributes, keyboard navigation
    - "Portal" - Z-index layering and focus trap escape
  why: CreateProjectModal uses Dialog primitives for accessibility
  critical_gotchas:
    - Dialog focus trap prevents nested Select keyboard nav - use Portal
    - onEscapeKeyDown and onPointerDownOutside needed to prevent close during mutation
    - Must use asChild prop to merge with custom trigger elements

- url: https://www.radix-ui.com/primitives/docs/components/select
  sections:
    - "Select Component" - Controlled state, keyboard navigation
    - "Portal" - Rendering outside Dialog for proper z-index
  why: ProjectSelector dropdown uses Select primitives
  critical_gotchas:
    - Select.Content must use Portal when nested in Dialog.Content
    - Native scrollbar hidden by default - add ScrollUpButton/ScrollDownButton
    - Keyboard nav (Home/End) requires manual implementation

# MUST READ - localStorage Best Practices
- url: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
  sections:
    - "API Reference" - setItem, getItem, removeItem
    - "Exceptions" - SecurityError, QuotaExceededError
  why: Persist selectedProjectId across page reloads
  critical_gotchas:
    - Throws errors in private browsing mode (Safari) and when cookies disabled
    - Quota exceeded has different error codes: 22 (standard), 1014 (Firefox), -2147024882 (IE8)
    - Data persists forever unless manually cleared
    - MUST wrap all access in try-catch with fallback to in-memory state

# ESSENTIAL DOCUMENTATION - React Router v6 (Optional for MVP)
- url: https://reactrouter.com/api/hooks/useParams
  why: Extract projectId from URL for shareable links (Phase 5 enhancement)
  note: Optional - start with localStorage-only, add URL params later

# ESSENTIAL BLOG - TanStack Query Best Practices
- url: https://tkdodo.eu/blog/effective-react-query-keys
  sections:
    - "Query Key Factories" - Hierarchical structure for cache invalidation
    - "Colocate Keys with Queries" - Keep in same feature directory
  why: Written by TanStack Query maintainer - authoritative patterns
  critical: Use query key factory pattern to prevent cache collisions and typos

- url: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query
  sections:
    - "Race Conditions" - cancelQueries prevents overwrite
    - "Concurrent Mutations" - Mutation keys and isMutating()
  why: Critical for preventing race conditions in optimistic updates
  critical: MUST cancel queries before optimistic update or background refetch will overwrite

# ESSENTIAL LOCAL FILES - Examples Directory
- file: prps/multi_project_selector/examples/README.md
  why: Comprehensive 500+ line guide with "What to Mimic/Adapt/Skip" for all patterns
  pattern: Complete implementations extracted from Archon production code

- file: prps/multi_project_selector/examples/example_1_modal_with_form.tsx
  why: Complete NewProjectModal pattern from Archon - nearly identical to CreateProjectModal
  pattern: Dialog + form state + mutation integration + validation + loading states
  critical: Shows isPending check to prevent close during mutation

- file: prps/multi_project_selector/examples/example_2_query_hooks_pattern.ts
  why: Complete useProjectQueries pattern from Archon - exact pattern to follow
  pattern: Query key factory + list query + optimistic create mutation + smart polling
  critical: Shows cancelQueries → snapshot → optimistic update → rollback pattern

- file: prps/multi_project_selector/examples/example_3_select_component.tsx
  why: Radix Select wrapper from Archon with glassmorphism styling
  pattern: Accessible dropdown with Portal, keyboard nav, animations
  critical: Shows Portal usage inside Dialog to escape focus trap

- file: prps/multi_project_selector/examples/example_4_localstorage_persistence.tsx
  why: localStorage persistence pattern from Archon ThemeContext
  pattern: Two useEffect hooks - one for init, one for persistence
  critical: Shows validation on read to handle stale/corrupted data

# ESSENTIAL LOCAL FILES - Codebase Patterns
- file: infra/task-manager/frontend/src/features/tasks/hooks/useTaskQueries.ts
  why: Task-manager already uses this exact TanStack Query pattern - mirror it
  pattern: Query key factory, smart polling, optimistic updates with nanoid
  critical: Follow EXACT same structure for useProjectQueries.ts

- file: infra/task-manager/frontend/src/features/projects/services/projectService.ts
  why: Project service is READY TO USE - no changes needed
  pattern: Typed responses, returns data not axios response objects
  critical: Service already implements all required API calls

- file: infra/task-manager/frontend/src/pages/KanbanPage.tsx
  why: Integration point - remove hardcoded projectId, add ProjectSelector
  pattern: Page-level layout, header structure, dark mode classes
  critical: Line 17 has hardcoded project ID to replace

- file: infra/task-manager/frontend/src/features/shared/config/queryPatterns.ts
  why: Shared query configuration - use STALE_TIMES.normal for project list
  pattern: DISABLED_QUERY_KEY for conditional queries, stale time constants
  critical: Use STALE_TIMES.normal (30s) not hardcoded numbers

- file: infra/task-manager/frontend/src/features/shared/utils/optimistic.ts
  why: Helper functions for optimistic updates with nanoid-based stable IDs
  pattern: createOptimisticEntity, replaceOptimisticEntity, removeDuplicateEntities
  critical: Use these utilities instead of manual optimistic ID generation

- file: infra/task-manager/frontend/src/features/shared/hooks/useSmartPolling.ts
  why: Visibility-aware polling that pauses when tab hidden
  pattern: Smart polling with configurable interval
  critical: Pauses polling when tab hidden - saves ~50% of requests
```

### Current Codebase Tree

```
infra/task-manager/frontend/src/
├── features/
│   ├── projects/
│   │   ├── services/
│   │   │   └── projectService.ts          # READY TO USE - implements all API calls
│   │   └── types/
│   │       └── project.ts                 # Types: Project, ProjectCreate
│   ├── tasks/
│   │   ├── components/
│   │   │   ├── KanbanBoard.tsx           # Accepts projectId prop
│   │   │   ├── KanbanColumn.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   └── TaskDetailModal.tsx       # PATTERN: Modal with form validation
│   │   ├── hooks/
│   │   │   └── useTaskQueries.ts         # PATTERN: Query key factory, optimistic updates
│   │   ├── services/
│   │   │   └── taskService.ts
│   │   └── types/
│   │       └── task.ts
│   └── shared/
│       ├── api/
│       │   └── apiClient.ts              # Configured axios with error handling
│       ├── config/
│       │   ├── queryClient.ts            # TanStack Query client setup
│       │   └── queryPatterns.ts          # STALE_TIMES, DISABLED_QUERY_KEY
│       ├── hooks/
│       │   └── useSmartPolling.ts        # Visibility-aware polling
│       └── utils/
│           └── optimistic.ts             # Optimistic update helpers
├── pages/
│   └── KanbanPage.tsx                    # MODIFY: Line 17 hardcoded project ID
└── App.tsx                               # QueryClientProvider configured

Backend API:
GET    /api/projects/           # List all projects (pagination optional)
POST   /api/projects/           # Create new project
GET    /api/projects/{id}       # Get single project
PATCH  /api/projects/{id}       # Update project
DELETE /api/projects/{id}       # Delete project
```

### Desired Codebase Tree

```
infra/task-manager/frontend/src/features/projects/
├── components/                           # NEW DIRECTORY
│   ├── ProjectSelector.tsx               # NEW - Dropdown with project list
│   ├── CreateProjectModal.tsx            # NEW - Creation modal
│   └── EmptyProjectState.tsx             # NEW - Onboarding component
├── hooks/                                # NEW DIRECTORY
│   └── useProjectQueries.ts              # NEW - Query hooks (mirror useTaskQueries.ts)
├── services/
│   └── projectService.ts                 # EXISTS - no changes needed
├── types/
│   └── project.ts                        # EXISTS - no changes needed
└── utils/                                # NEW DIRECTORY
    └── projectStorage.ts                 # NEW - Type-safe localStorage wrapper

infra/task-manager/frontend/src/pages/
└── KanbanPage.tsx                        # MODIFY - Remove hardcoded ID, add selector

**New Files to Create**:
1. src/features/projects/hooks/useProjectQueries.ts (250 lines)
2. src/features/projects/components/ProjectSelector.tsx (150 lines)
3. src/features/projects/components/CreateProjectModal.tsx (200 lines)
4. src/features/projects/components/EmptyProjectState.tsx (50 lines)
5. src/features/projects/utils/projectStorage.ts (100 lines)

**Files to Modify**:
1. src/pages/KanbanPage.tsx (replace line 17, integrate ProjectSelector)
```

### Known Gotchas & Library Quirks

```typescript
// CRITICAL: TanStack Query v5 Breaking Changes
// ❌ WRONG - v4 syntax no longer works
const { data } = useQuery(['projects'], fetchProjects, { staleTime: 30000 });
const { mutate } = useMutation(createProject, { onSuccess: () => {} });

// ✅ RIGHT - v5 requires object-based syntax
const { data } = useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  staleTime: 30000,
});
const { mutate } = useMutation({
  mutationFn: createProject,
  onSuccess: () => {},
});

// CRITICAL: Race Condition - Optimistic Update Overwritten
// ❌ WRONG - Background refetch will overwrite optimistic update
export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectService.createProject,
    onMutate: async (newProject) => {
      // Missing: await queryClient.cancelQueries()
      queryClient.setQueryData(projectKeys.lists(), (old) => [...old, newProject]);
    },
  });
}

// ✅ RIGHT - Cancel queries to prevent race conditions
export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectService.createProject,
    onMutate: async (newProject) => {
      // CRITICAL: Cancel in-flight queries first
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      const previousProjects = queryClient.getQueryData<Project[]>(projectKeys.lists());
      const optimisticProject = createOptimisticEntity<Project>({
        ...newProject,
        id: `temp-${Date.now()}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) =>
        [optimisticProject, ...old]
      );

      return { previousProjects, optimisticId: optimisticProject._localId };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }
    },
    onSuccess: (serverProject, variables, context) => {
      // Replace optimistic with server data
      queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) =>
        replaceOptimisticEntity(old, context?.optimisticId, serverProject)
      );
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

// CRITICAL: Concurrent Mutations - Multiple Projects Created Simultaneously
// ❌ WRONG - Each mutation invalidates, causing second to be overwritten
onSettled: () => {
  queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
}

// ✅ RIGHT - Only invalidate if last mutation running
export function useCreateProject() {
  return useMutation({
    mutationKey: ['createProject'], // CRITICAL: enables tracking
    mutationFn: projectService.createProject,
    onSettled: () => {
      // Check if other mutations running
      const mutationCount = queryClient.isMutating({ mutationKey: ['createProject'] });
      if (mutationCount === 1) {
        // This is the last mutation, safe to invalidate
        queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      }
    },
  });
}

// CRITICAL: localStorage Quota Exceeded or Security Error
// ❌ WRONG - No error handling, will crash app
const saveSelectedProject = (projectId: string) => {
  localStorage.setItem('selectedProjectId', projectId);
};

// ✅ RIGHT - Comprehensive error handling with fallback
class ProjectStorage {
  private static KEY = 'selectedProjectId';
  private static inMemoryFallback: string | null = null;
  private static isAvailable: boolean | null = null;

  private static checkAvailability(): boolean {
    if (this.isAvailable !== null) return this.isAvailable;

    try {
      const testKey = '__localStorage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      this.isAvailable = true;
      return true;
    } catch (e) {
      console.warn('localStorage not available, using in-memory fallback', e);
      this.isAvailable = false;
      return false;
    }
  }

  static get(): string | null {
    if (!this.checkAvailability()) {
      return this.inMemoryFallback;
    }

    try {
      return localStorage.getItem(this.KEY);
    } catch (e) {
      console.error('Failed to read from localStorage:', e);
      return this.inMemoryFallback;
    }
  }

  static set(projectId: string | null): void {
    this.inMemoryFallback = projectId; // Update in-memory first

    if (!this.checkAvailability()) return;

    try {
      if (projectId === null) {
        localStorage.removeItem(this.KEY);
      } else {
        localStorage.setItem(this.KEY, projectId);
      }
    } catch (e) {
      console.error('Failed to write to localStorage:', e);
      // Fall back to in-memory (already set above)
    }
  }
}

// CRITICAL: Deleted Project Still Selected in localStorage
// ❌ WRONG - No validation of stored project ID
const [selectedProjectId] = useState<string | null>(() => {
  return ProjectStorage.get(); // Might be deleted project!
});

// ✅ RIGHT - Validate stored ID against available projects
const { data: projects } = useProjects();
const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

useEffect(() => {
  if (!projects || projects.length === 0) {
    setSelectedProjectId(null);
    ProjectStorage.clear();
    return;
  }

  const storedId = ProjectStorage.get();
  const storedProjectExists = storedId && projects.some(p => p.id === storedId);

  if (storedProjectExists) {
    setSelectedProjectId(storedId);
  } else {
    // Stored project deleted - auto-select first
    const firstProject = projects[0];
    setSelectedProjectId(firstProject.id);
    ProjectStorage.set(firstProject.id);
  }
}, [projects]);

// CRITICAL: Radix Dialog Focus Trap Conflicts with Nested Select
// ❌ WRONG - Select nested in Dialog without Portal
<Dialog.Root>
  <Dialog.Content>
    <Select.Root>
      <Select.Trigger>Choose template</Select.Trigger>
      <Select.Content>
        {/* Focus trap prevents keyboard navigation here! */}
      </Select.Content>
    </Select.Root>
  </Dialog.Content>
</Dialog.Root>

// ✅ RIGHT - Select.Content uses Portal to escape focus trap
<Dialog.Root>
  <Dialog.Content>
    <Select.Root>
      <Select.Trigger>Choose template</Select.Trigger>
      <Select.Portal> {/* CRITICAL: Renders outside Dialog */}
        <Select.Content>
          {/* Keyboard navigation works now */}
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  </Dialog.Content>
</Dialog.Root>

// CRITICAL: Missing Query Key Dependencies Breaks Caching
// ❌ WRONG - Parameters not in query key
export function useProjects(page: number) {
  return useQuery({
    queryKey: projectKeys.all, // Same key for ALL pages!
    queryFn: () => projectService.listProjects({ page }),
  });
}

// ✅ RIGHT - Parameters included in query key
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  list: (filters?: { page?: number }) =>
    [...projectKeys.lists(), { filters }] as const,
};

export function useProjects(filters?: { page?: number }) {
  return useQuery({
    queryKey: projectKeys.list(filters), // Unique key per page
    queryFn: () => projectService.listProjects(filters),
  });
}

// CRITICAL: Not Preventing Dialog Close During Mutation
// ❌ WRONG - User can close while mutation pending
<Dialog.Root open={open} onOpenChange={onOpenChange}>
  <DialogContent>
    <Button disabled={createProject.isPending}>Create</Button>
  </DialogContent>
</Dialog.Root>

// ✅ RIGHT - Prevent close during mutation
const handleOpenChange = (newOpen: boolean) => {
  if (!newOpen && createProject.isPending) {
    return; // Block close attempt
  }
  onOpenChange(newOpen);
};

<Dialog.Root open={open} onOpenChange={handleOpenChange}>
  <DialogContent
    onEscapeKeyDown={(e) => {
      if (createProject.isPending) e.preventDefault();
    }}
    onPointerDownOutside={(e) => {
      if (createProject.isPending) e.preventDefault();
    }}
  >
    <Button disabled={createProject.isPending}>Create</Button>
  </DialogContent>
</Dialog.Root>

// CRITICAL: Mapping Query Data to Redux/Context Anti-Pattern
// ❌ WRONG - Syncing query data to Redux
const { data } = useProjects();
useEffect(() => {
  if (data) {
    dispatch(setProjects(data)); // Causes double render
  }
}, [data, dispatch]);

// ✅ RIGHT - Use TanStack Query directly (no Redux/Context for server state)
const ProjectSelector = () => {
  const { data: projects } = useProjects(); // Direct usage
  // ...
};

// If multiple components need projects, just call the hook
const AnotherComponent = () => {
  const { data: projects } = useProjects(); // Same cache, no extra request
};
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Read all example files**:
   - Read `prps/multi_project_selector/examples/README.md` cover to cover
   - Study each example file noting key patterns
   - Understand "What to Mimic/Adapt/Skip" for each

2. **Study existing codebase patterns**:
   - Read `src/features/tasks/hooks/useTaskQueries.ts` - EXACT pattern to mirror
   - Read `src/pages/KanbanPage.tsx` - Integration point, understand current layout
   - Read `src/features/shared/config/queryPatterns.ts` - Available utilities

3. **Verify backend integration**:
   - Confirm `src/features/projects/services/projectService.ts` implements all API calls
   - Check `src/features/projects/types/project.ts` for type definitions
   - Test API endpoints manually if needed

4. **Review gotchas document**:
   - Read `prps/multi_project_selector/planning/gotchas.md` - All 14 critical gotchas
   - Focus on race conditions (#1, #2) and localStorage errors (#3, #4)
   - Understand TanStack Query v5 breaking changes (#10)

### Task List (Execute in Order)

```yaml
Task 1: Create localStorage Utility with Error Handling
RESPONSIBILITY: Type-safe localStorage wrapper with quota handling and in-memory fallback
FILES TO CREATE:
  - src/features/projects/utils/projectStorage.ts

PATTERN TO FOLLOW: prps/multi_project_selector/examples/example_4_localstorage_persistence.tsx

SPECIFIC STEPS:
  1. Create ProjectStorage class with static methods get/set/clear
  2. Implement checkAvailability() to detect localStorage errors
  3. Add isQuotaExceeded() to handle cross-browser quota errors (code 22, 1014, -2147024882)
  4. Maintain inMemoryFallback as safety net
  5. Wrap all localStorage access in try-catch
  6. Add console warnings for quota/security errors
  7. Return null gracefully on errors

VALIDATION:
  - [ ] Works in private browsing mode (uses in-memory fallback)
  - [ ] Handles quota exceeded error (clears and retries)
  - [ ] Returns null instead of throwing on security errors
  - [ ] In-memory fallback works when localStorage disabled

REFERENCE: See gotcha #3 (localStorage errors) in gotchas.md for complete implementation

---

Task 2: Create Query Key Factory and List Query Hook
RESPONSIBILITY: Hierarchical query keys and project list query with smart polling
FILES TO CREATE:
  - src/features/projects/hooks/useProjectQueries.ts (partial - keys and list query only)

PATTERN TO FOLLOW:
  - src/features/tasks/hooks/useTaskQueries.ts (EXACT pattern)
  - prps/multi_project_selector/examples/example_2_query_hooks_pattern.ts

SPECIFIC STEPS:
  1. Define projectKeys factory with hierarchical structure:
     - all: ['projects'] as const
     - lists: () => [...projectKeys.all, 'list'] as const
     - detail: (id: string) => [...projectKeys.all, 'detail', id] as const
  2. Import STALE_TIMES and DISABLED_QUERY_KEY from shared/config/queryPatterns
  3. Import useSmartPolling from shared/hooks/useSmartPolling
  4. Create useProjects() hook:
     - Use projectKeys.lists() as queryKey
     - Call projectService.listProjects() as queryFn
     - Add smart polling with 30s interval (conservative for projects)
     - Set staleTime: STALE_TIMES.normal
     - Enable refetchOnWindowFocus: true
  5. Create useProject(id: string | undefined) conditional query:
     - Use projectKeys.detail(id!) when enabled
     - Set enabled: !!id (conditional execution)

VALIDATION:
  - [ ] Query keys follow hierarchical pattern
  - [ ] Smart polling pauses when tab hidden
  - [ ] Conditional query only runs when id provided
  - [ ] Uses shared constants (no magic numbers)
  - [ ] TypeScript strict mode passes

REFERENCE: See gotcha #5 (query key dependencies) and #11 (excessive polling) in gotchas.md

---

Task 3: Create Optimistic Mutation Hook
RESPONSIBILITY: Create project mutation with optimistic updates, rollback, and race condition prevention
FILES TO MODIFY:
  - src/features/projects/hooks/useProjectQueries.ts (add useCreateProject)

PATTERN TO FOLLOW:
  - src/features/tasks/hooks/useTaskQueries.ts (optimistic pattern)
  - prps/multi_project_selector/examples/example_2_query_hooks_pattern.ts

SPECIFIC STEPS:
  1. Import createOptimisticEntity, replaceOptimisticEntity from shared/utils/optimistic
  2. Create useCreateProject() hook with mutationKey: ['createProject']
  3. Implement onMutate with race condition prevention:
     - await queryClient.cancelQueries({ queryKey: projectKeys.lists() })
     - Snapshot previousProjects with getQueryData
     - Create optimisticProject using createOptimisticEntity with temp ID
     - setQueryData to add optimistic project to list
     - Return { previousProjects, optimisticId } as context
  4. Implement onError with rollback:
     - Restore previousProjects from context
  5. Implement onSuccess with optimistic replacement:
     - Use replaceOptimisticEntity to swap temp ID with server ID
  6. Implement onSettled with concurrent mutation check:
     - Check isMutating({ mutationKey: ['createProject'] })
     - Only invalidate if mutationCount === 1 (last mutation)
  7. Export hook

VALIDATION:
  - [ ] cancelQueries called before optimistic update
  - [ ] Rollback on error restores previous state
  - [ ] Optimistic ID replaced with server ID on success
  - [ ] Concurrent mutations handled (double-click test)
  - [ ] TypeScript context types correct

REFERENCE: See gotchas #1 (race conditions), #2 (concurrent mutations) in gotchas.md

---

Task 4: Create EmptyProjectState Component
RESPONSIBILITY: Onboarding component for zero projects scenario
FILES TO CREATE:
  - src/features/projects/components/EmptyProjectState.tsx

PATTERN TO FOLLOW: Standard React component with Tailwind styling

SPECIFIC STEPS:
  1. Create functional component with onCreateClick prop
  2. Add centered flexbox layout (h-full, flex-col, items-center, justify-center)
  3. Add icon (FolderIcon or ProjectIcon from lucide-react)
  4. Add heading "No Projects Yet"
  5. Add description text explaining projects
  6. Add primary CTA button "Create Your First Project"
  7. Add dark mode classes (dark:bg-*, dark:text-*)
  8. Wire onCreateClick to button

VALIDATION:
  - [ ] Renders centered on page
  - [ ] Dark mode styling works
  - [ ] Button triggers onCreateClick callback
  - [ ] Accessible (ARIA labels, keyboard navigation)

REFERENCE: See gotcha #12 (empty state handling) in gotchas.md

---

Task 5: Create CreateProjectModal Component
RESPONSIBILITY: Modal form for creating projects with validation and mutation integration
FILES TO CREATE:
  - src/features/projects/components/CreateProjectModal.tsx

PATTERN TO FOLLOW:
  - prps/multi_project_selector/examples/example_1_modal_with_form.tsx (EXACT pattern)
  - src/features/tasks/components/TaskDetailModal.tsx (validation pattern)

SPECIFIC STEPS:
  1. Import Dialog primitives from @radix-ui/react-dialog
  2. Define props: open, onOpenChange, onSuccess?: (project: Project) => void
  3. Create formData state: { name: string; description: string }
  4. Get createProject mutation from useCreateProject()
  5. Create handleOpenChange to prevent close during mutation:
     - If closing (!newOpen) and isPending, return early
     - Reset formData when closing
     - Call createProject.reset() to clear error state
  6. Create handleSubmit:
     - e.preventDefault()
     - Return early if isPending (prevent double submit)
     - Validate name.trim() not empty
     - Call createProject.mutate with callbacks:
       - onSuccess: reset form, close modal, call props.onSuccess
  7. Render Dialog.Root with controlled open state
  8. Add Dialog.Content with escape/backdrop prevention:
     - onEscapeKeyDown: prevent if isPending
     - onPointerDownOutside: prevent if isPending
  9. Add form with Input (name) and Textarea (description)
  10. Disable inputs during isPending
  11. Show error message if createProject.error
  12. Add footer buttons: Cancel (disabled if isPending), Create (disabled if isPending or empty name)
  13. Show loading text "Creating..." when isPending

VALIDATION:
  - [ ] Cannot close during mutation (Esc, backdrop, Cancel)
  - [ ] Form resets on close
  - [ ] Validation prevents empty name
  - [ ] Error displayed on mutation failure
  - [ ] Success callback called with new project
  - [ ] Loading states clear (disabled inputs, button text)
  - [ ] Keyboard navigation works (Tab, Enter, Esc)

REFERENCE: See gotchas #6 (Dialog focus trap), #9 (prevent close), #13 (form reset) in gotchas.md

---

Task 6: Create ProjectSelector Component
RESPONSIBILITY: Dropdown for selecting projects with visual active indicator
FILES TO CREATE:
  - src/features/projects/components/ProjectSelector.tsx

PATTERN TO FOLLOW:
  - prps/multi_project_selector/examples/example_3_select_component.tsx

SPECIFIC STEPS:
  1. Import Select primitives from @radix-ui/react-select
  2. Define props: selectedProjectId, onProjectChange, onCreateProject
  3. Get projects from useProjects() hook
  4. Handle loading state: return skeleton or "Loading..."
  5. Handle error state: return error message
  6. If no projects, return null (EmptyProjectState shown at page level)
  7. Find current project from selectedProjectId
  8. Render Select.Root with controlled value
  9. Render Select.Trigger showing current project name
  10. Render Select.Portal > Select.Content (CRITICAL for focus trap escape)
  11. Map projects to Select.Item with:
      - key={project.id}
      - value={project.id}
      - Visual indicator if project.id === selectedProjectId (checkmark icon)
      - Highlight background if selected
  12. Add "Create New Project" item at bottom of list
  13. Wire onValueChange to call onProjectChange
  14. Add dark mode styling

VALIDATION:
  - [ ] Shows current project name in trigger
  - [ ] Lists all projects in dropdown
  - [ ] Selected project has visual indicator
  - [ ] "Create New Project" action works
  - [ ] Keyboard navigation works (arrows, Enter, Esc)
  - [ ] Dark mode styling correct
  - [ ] Loading/error states handled

REFERENCE: See gotcha #6 (Dialog focus trap - Select needs Portal) in gotchas.md

---

Task 7: Integrate ProjectSelector into KanbanPage
RESPONSIBILITY: Replace hardcoded project ID with ProjectSelector and state management
FILES TO MODIFY:
  - src/pages/KanbanPage.tsx

PATTERN TO FOLLOW:
  - prps/multi_project_selector/planning/codebase-patterns.md (Page structure)

SPECIFIC STEPS:
  1. Import useProjects from features/projects/hooks/useProjectQueries
  2. Import ProjectSelector from features/projects/components/ProjectSelector
  3. Import CreateProjectModal from features/projects/components/CreateProjectModal
  4. Import EmptyProjectState from features/projects/components/EmptyProjectState
  5. Import ProjectStorage from features/projects/utils/projectStorage
  6. Remove hardcoded projectId constant (line 17)
  7. Add state: selectedProjectId (string | null), createModalOpen (boolean)
  8. Get projects from useProjects()
  9. Add useEffect for initialization and validation:
     - If no projects: setSelectedProjectId(null), clear storage
     - If projects exist: validate stored ID, auto-select first if invalid
     - Handle project deletion: watch for selectedProjectId no longer in list
  10. Add useEffect for persistence:
      - When selectedProjectId changes, save to ProjectStorage
  11. Update render logic:
      - If isLoading: show LoadingSpinner
      - If no projects: show EmptyProjectState with createModalOpen handler
      - If no selectedProjectId: show LoadingSpinner (initializing)
      - Normal case: show header with ProjectSelector + main with KanbanBoard
  12. Update header to include ProjectSelector:
      - Add to left side of header (before or in place of title)
      - Pass selectedProjectId, onProjectChange, onCreateProject
  13. Add CreateProjectModal at bottom of component:
      - Controlled by createModalOpen state
      - onSuccess: auto-select newly created project
  14. Pass selectedProjectId to KanbanBoard component

VALIDATION:
  - [ ] Hardcoded project ID removed
  - [ ] ProjectSelector appears in header
  - [ ] Switching projects updates Kanban board
  - [ ] Selection persists across page reloads
  - [ ] Empty state shows when no projects
  - [ ] New project auto-selected after creation
  - [ ] Deleted project handled gracefully
  - [ ] Dark mode styling maintained

REFERENCE: See gotcha #4 (deleted project validation) in gotchas.md

---

Task 8: Handle Edge Cases and Error States
RESPONSIBILITY: Graceful degradation for all failure modes
FILES TO MODIFY:
  - All components (add error boundaries, fallbacks)

SPECIFIC STEPS:
  1. ProjectStorage: Verify in-memory fallback works (test in private browsing)
  2. useProjects: Add error state handling in components
  3. CreateProjectModal: Show user-friendly error messages (not raw API errors)
  4. ProjectSelector: Handle network errors with retry button
  5. KanbanPage: Add error boundary for catastrophic failures
  6. Test scenarios:
     - Network offline when loading projects
     - API returns 500 error
     - localStorage quota exceeded
     - Corrupted localStorage data
     - Project deleted while viewing it
     - Double-click "Create Project" button

VALIDATION:
  - [ ] Network errors show retry option
  - [ ] localStorage errors fall back to in-memory
  - [ ] Corrupted data cleared and reset
  - [ ] Deleted project auto-switches to next
  - [ ] No unhandled exceptions in console
  - [ ] Error messages are user-friendly

REFERENCE: See all gotchas in gotchas.md, especially #3, #4, #7, #12

---

Task 9: Add Loading States and Skeletons
RESPONSIBILITY: Prevent layout shift and provide visual feedback during async operations
FILES TO MODIFY:
  - ProjectSelector, CreateProjectModal, KanbanPage

SPECIFIC STEPS:
  1. ProjectSelector: Show skeleton while loading projects
  2. CreateProjectModal: Show loading indicator in button
  3. KanbanPage: Show loading spinner during initialization
  4. Ensure loading states maintain layout (no CLS)
  5. Add smooth transitions where appropriate

VALIDATION:
  - [ ] No layout shift during loading
  - [ ] User sees feedback for all async actions
  - [ ] Loading states clear and consistent
  - [ ] Animations smooth (60fps)

---

Task 10: Accessibility Audit
RESPONSIBILITY: Ensure WCAG 2.1 AA compliance
FILES TO MODIFY:
  - All components

SPECIFIC STEPS:
  1. Add ARIA labels to all interactive elements
  2. Test keyboard navigation (Tab, Enter, Esc, Arrow keys)
  3. Verify focus indicators visible
  4. Check color contrast ratios (use browser devtools)
  5. Test screen reader compatibility (VoiceOver/NVDA)
  6. Ensure form labels properly associated
  7. Add focus trap to modal (Dialog handles this)
  8. Add live regions for dynamic content

VALIDATION:
  - [ ] All interactive elements keyboard accessible
  - [ ] Focus visible on all elements
  - [ ] Screen reader announces state changes
  - [ ] Color contrast meets WCAG AA
  - [ ] Form validation errors announced

REFERENCE: Radix UI primitives have built-in accessibility - verify not broken

---

Task 11: Testing
RESPONSIBILITY: Comprehensive test coverage for all components and hooks
FILES TO CREATE:
  - src/features/projects/hooks/__tests__/useProjectQueries.test.ts
  - src/features/projects/components/__tests__/ProjectSelector.test.tsx
  - src/features/projects/components/__tests__/CreateProjectModal.test.tsx
  - src/features/projects/utils/__tests__/projectStorage.test.ts
  - src/pages/__tests__/KanbanPage.test.tsx

PATTERN TO FOLLOW: Existing test patterns from task-manager

SPECIFIC STEPS:
  1. Mock localStorage globally in beforeEach
  2. Create QueryClient wrapper for hook tests
  3. Test useProjectQueries:
     - List query fetches projects
     - Conditional query only runs when ID provided
     - Optimistic update adds project immediately
     - Rollback on error restores previous state
     - Concurrent mutations handled correctly
  4. Test ProjectSelector:
     - Renders project list
     - Selected project has visual indicator
     - Changing selection calls callback
     - "Create New Project" triggers modal
  5. Test CreateProjectModal:
     - Form validation prevents empty name
     - Cannot close during mutation
     - Success callback receives new project
     - Error displays user-friendly message
  6. Test ProjectStorage:
     - Handles quota exceeded error
     - Handles security error (private browsing)
     - Falls back to in-memory when localStorage unavailable
  7. Test KanbanPage:
     - Empty state shows when no projects
     - Validates stored project ID
     - Auto-selects first project if stored ID invalid
     - Persists selection to localStorage

VALIDATION:
  - [ ] All tests pass: npm test
  - [ ] Coverage > 80%
  - [ ] No test flakiness (run 10 times)

REFERENCE: See gotchas.md testing section for mock patterns

---

Task 12: Performance Optimization
RESPONSIBILITY: Minimize re-renders and network requests
FILES TO MODIFY:
  - All hooks and components

SPECIFIC STEPS:
  1. Verify useProjects not called multiple times in same component
  2. Memoize expensive computations with useMemo
  3. Memoize callbacks with useCallback where passed to children
  4. Verify query keys include all dependencies (prevent over-fetching)
  5. Tune staleTime and gcTime for optimal caching
  6. Use React DevTools Profiler to identify excessive re-renders
  7. Consider React.memo for ProjectSelector if re-rendering too often

VALIDATION:
  - [ ] Project list not refetched on every selection change
  - [ ] No unnecessary re-renders in React Profiler
  - [ ] Network tab shows minimal requests
  - [ ] UI feels snappy (< 100ms interaction response)

REFERENCE: See gotcha #8 (mapping query data anti-pattern) in gotchas.md

---

Task 13: Documentation
RESPONSIBILITY: Update README and add inline comments
FILES TO MODIFY:
  - README.md (if exists)
  - Add JSDoc comments to all public functions

SPECIFIC STEPS:
  1. Document new components and hooks with JSDoc
  2. Add inline comments explaining critical patterns:
     - Why cancelQueries is needed
     - Why Portal is used in Select
     - Why localStorage is wrapped in try-catch
  3. Update architecture documentation if it exists
  4. Add migration guide if breaking changes

VALIDATION:
  - [ ] All public APIs have JSDoc comments
  - [ ] Critical patterns explained inline
  - [ ] README updated with new features
```

### Implementation Pseudocode

```typescript
// Task 1: ProjectStorage Utility
class ProjectStorage {
  private static KEY = 'selectedProjectId';
  private static inMemoryFallback: string | null = null;

  static get(): string | null {
    // Try localStorage first, fall back to in-memory
    // Handle all errors gracefully (quota, security, etc.)
    // Return null on any failure
  }

  static set(id: string | null): void {
    // Update in-memory first (always succeeds)
    // Try localStorage with error handling
    // Detect quota exceeded across browsers
    // Fall back silently to in-memory only
  }
}

// Task 2 & 3: useProjectQueries Hook
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  detail: (id: string) => [...projectKeys.all, 'detail', id] as const,
};

export function useProjects() {
  const { refetchInterval } = useSmartPolling(30000); // 30s polling

  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchInterval,
    refetchOnWindowFocus: true,
    staleTime: STALE_TIMES.normal,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['createProject'],
    mutationFn: projectService.createProject,
    onMutate: async (newProject) => {
      // CRITICAL: Prevent race conditions
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      // Snapshot for rollback
      const previousProjects = queryClient.getQueryData(projectKeys.lists());

      // Optimistic update
      const optimisticProject = createOptimisticEntity({ ...newProject, ... });
      queryClient.setQueryData(projectKeys.lists(), (old) => [optimisticProject, ...old]);

      return { previousProjects, optimisticId: optimisticProject._localId };
    },
    onError: (err, vars, context) => {
      // Rollback on error
      queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
    },
    onSuccess: (serverProject, vars, context) => {
      // Replace optimistic with real
      queryClient.setQueryData(projectKeys.lists(), (old) =>
        replaceOptimisticEntity(old, context.optimisticId, serverProject)
      );
    },
    onSettled: () => {
      // Only invalidate if last mutation
      const mutationCount = queryClient.isMutating({ mutationKey: ['createProject'] });
      if (mutationCount === 1) {
        queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      }
    },
  });
}

// Task 5: CreateProjectModal
const CreateProjectModal = ({ open, onOpenChange, onSuccess }) => {
  const [formData, setFormData] = useState({ name: '', description: '' });
  const createProject = useCreateProject();

  const handleOpenChange = (newOpen) => {
    // Prevent close during mutation
    if (!newOpen && createProject.isPending) return;

    // Reset form on close
    if (!newOpen) {
      setFormData({ name: '', description: '' });
      createProject.reset();
    }

    onOpenChange(newOpen);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (createProject.isPending || !formData.name.trim()) return;

    createProject.mutate(formData, {
      onSuccess: (newProject) => {
        setFormData({ name: '', description: '' });
        onOpenChange(false);
        onSuccess?.(newProject);
      },
    });
  };

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <Dialog.Content
        onEscapeKeyDown={(e) => createProject.isPending && e.preventDefault()}
        onPointerDownOutside={(e) => createProject.isPending && e.preventDefault()}
      >
        <form onSubmit={handleSubmit}>
          {/* Form fields disabled during isPending */}
          {/* Show error if createProject.error */}
          {/* Button disabled if isPending or empty name */}
        </form>
      </Dialog.Content>
    </Dialog.Root>
  );
};

// Task 6: ProjectSelector
const ProjectSelector = ({ selectedProjectId, onProjectChange, onCreateProject }) => {
  const { data: projects, isLoading, error } = useProjects();

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage retry />;
  if (!projects || projects.length === 0) return null; // Empty state at page level

  const currentProject = projects.find(p => p.id === selectedProjectId);

  return (
    <Select.Root value={selectedProjectId} onValueChange={onProjectChange}>
      <Select.Trigger>
        <Select.Value>{currentProject?.name || 'Select project...'}</Select.Value>
      </Select.Trigger>
      <Select.Portal> {/* CRITICAL: Escape Dialog focus trap */}
        <Select.Content>
          <Select.Viewport>
            {projects.map(project => (
              <Select.Item
                key={project.id}
                value={project.id}
                className={project.id === selectedProjectId ? 'bg-blue-50' : ''}
              >
                {project.name}
                {project.id === selectedProjectId && <CheckIcon />}
              </Select.Item>
            ))}
            <Select.Separator />
            <Select.Item value="__create__" onSelect={onCreateProject}>
              <PlusIcon /> Create New Project
            </Select.Item>
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
};

// Task 7: KanbanPage Integration
const KanbanPage = () => {
  const { data: projects, isLoading } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  // Initialize and validate selected project
  useEffect(() => {
    if (!projects || projects.length === 0) {
      setSelectedProjectId(null);
      ProjectStorage.clear();
      return;
    }

    const storedId = ProjectStorage.get();
    const storedProjectExists = storedId && projects.some(p => p.id === storedId);

    if (storedProjectExists) {
      setSelectedProjectId(storedId);
    } else {
      // Auto-select first if stored ID invalid
      const firstProject = projects[0];
      setSelectedProjectId(firstProject.id);
      ProjectStorage.set(firstProject.id);
    }
  }, [projects]);

  // Persist changes to localStorage
  useEffect(() => {
    if (selectedProjectId) {
      ProjectStorage.set(selectedProjectId);
    }
  }, [selectedProjectId]);

  if (isLoading) return <LoadingSpinner />;

  if (!projects || projects.length === 0) {
    return (
      <>
        <EmptyProjectState onCreateClick={() => setCreateModalOpen(true)} />
        <CreateProjectModal
          open={createModalOpen}
          onOpenChange={setCreateModalOpen}
          onSuccess={(project) => {
            setSelectedProjectId(project.id);
            setCreateModalOpen(false);
          }}
        />
      </>
    );
  }

  if (!selectedProjectId) return <LoadingSpinner />; // Initializing

  return (
    <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-full px-6 py-4 flex items-center gap-4">
          <ProjectSelector
            selectedProjectId={selectedProjectId}
            onProjectChange={setSelectedProjectId}
            onCreateProject={() => setCreateModalOpen(true)}
          />
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Task Management
          </h1>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        <KanbanBoard projectId={selectedProjectId} />
      </main>

      <CreateProjectModal
        open={createModalOpen}
        onOpenChange={setCreateModalOpen}
        onSuccess={(project) => {
          setSelectedProjectId(project.id);
          setCreateModalOpen(false);
        }}
      />
    </div>
  );
};
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Run these FIRST before proceeding to next task
cd infra/task-manager/frontend

# Type checking
npm run type-check
# Expected: No errors. If errors, READ and fix before proceeding

# Linting
npm run lint
# Expected: No errors. Auto-fix what's possible with --fix

# Fix auto-fixable issues
npm run lint -- --fix

# Verify TypeScript strict mode
tsc --noEmit --strict src/features/projects/**/*.ts src/pages/KanbanPage.tsx
```

### Level 2: Unit Tests

```bash
# Run tests for each new file as you create it
npm test src/features/projects/hooks/__tests__/useProjectQueries.test.ts
npm test src/features/projects/components/__tests__/ProjectSelector.test.tsx
npm test src/features/projects/components/__tests__/CreateProjectModal.test.tsx
npm test src/features/projects/utils/__tests__/projectStorage.test.ts

# Run all tests
npm test

# Expected: All tests pass
# If failing: Read error, understand root cause, fix code, re-run
# NEVER mock to pass - fix the actual issue
```

### Level 3: Integration Tests

```bash
# Start dev server
cd infra/task-manager/frontend
npm run dev

# Open browser to http://localhost:5173
# Manual test checklist:
# - [ ] Project list loads in dropdown
# - [ ] Switching projects updates Kanban board
# - [ ] Selection persists across page reload (F5)
# - [ ] Creating new project works
# - [ ] New project auto-selected after creation
# - [ ] Empty state shows when no projects
# - [ ] "Create Your First Project" button works
# - [ ] Keyboard navigation works (Tab, Enter, Esc, Arrow keys)
# - [ ] Dark mode toggle works
# - [ ] Works in private browsing mode (uses in-memory fallback)

# Test edge cases:
# - [ ] Delete current project in API, reload page - auto-selects next
# - [ ] Double-click "Create Project" - no duplicate projects
# - [ ] Disconnect network - shows error with retry
# - [ ] Fill localStorage to quota - falls back to in-memory
```

### Level 4: Cross-Browser Testing

```bash
# Test in multiple browsers:
# - [ ] Chrome/Edge (localStorage standard)
# - [ ] Firefox (different quota error code)
# - [ ] Safari (private browsing behavior different)

# Test private browsing:
# - [ ] Chrome Incognito
# - [ ] Firefox Private Window
# - [ ] Safari Private Browsing
# Expected: Uses in-memory fallback, no crashes
```

---

## Final Validation Checklist

**Functional Requirements**:
- [ ] All success criteria from "What" section met
- [ ] User can see list of all projects
- [ ] User can switch between projects seamlessly
- [ ] Selected project persists across page reloads
- [ ] User can create new projects via modal
- [ ] UI clearly shows which project is active
- [ ] All existing Kanban functionality works unchanged
- [ ] Empty state shows when no projects
- [ ] Deleted project handled gracefully

**Validation Gates**:
- [ ] All tests pass: `npm test`
- [ ] No linting errors: `npm run lint`
- [ ] No type errors: `npm run type-check`
- [ ] Manual test successful in dev environment
- [ ] Works in Chrome, Firefox, Safari
- [ ] Works in private browsing mode

**Code Quality**:
- [ ] Follows existing codebase patterns (mirrors useTaskQueries.ts)
- [ ] All critical gotchas addressed (race conditions, localStorage errors)
- [ ] Error cases handled gracefully (network failures, quota exceeded)
- [ ] Logs are informative but not verbose
- [ ] TypeScript strict mode passes
- [ ] No console errors or warnings

**Accessibility**:
- [ ] Keyboard navigation works (Tab, Enter, Esc, Arrow keys)
- [ ] ARIA labels present on all interactive elements
- [ ] Focus visible on all elements
- [ ] Screen reader compatible
- [ ] Color contrast meets WCAG AA

**Performance**:
- [ ] Project list loads in < 500ms
- [ ] Project switching feels instant (< 100ms perceived)
- [ ] No excessive re-renders in React Profiler
- [ ] Smart polling pauses when tab hidden
- [ ] Query cache working (no redundant requests)

**Documentation**:
- [ ] All public APIs have JSDoc comments
- [ ] Critical patterns explained inline
- [ ] README updated if applicable

**Critical Gotchas Verified**:
- [ ] cancelQueries called in all mutations (gotcha #1)
- [ ] Optimistic updates have rollback (gotcha #1)
- [ ] Concurrent mutations handled (gotcha #2)
- [ ] localStorage wrapped in try-catch (gotcha #3)
- [ ] Deleted project validation (gotcha #4)
- [ ] Query keys include all parameters (gotcha #5)
- [ ] Select uses Portal inside Dialog (gotcha #6)
- [ ] Cannot close modal during mutation (gotcha #9)
- [ ] TanStack Query v5 object syntax (gotcha #10)
- [ ] No mapping to Redux/Context (gotcha #8)

---

## Anti-Patterns to Avoid

### TanStack Query Anti-Patterns

```typescript
// ❌ Don't use v4 syntax
const { data } = useQuery(['projects'], fetchProjects);

// ❌ Don't forget cancelQueries
onMutate: async () => {
  // Missing: await queryClient.cancelQueries()
}

// ❌ Don't hardcode query keys
queryKey: ['projects', 'list']

// ❌ Don't map query data to Redux/Context
useEffect(() => {
  dispatch(setProjects(data));
}, [data]);

// ❌ Don't use refetch() when query key should change
const { refetch } = useProjects();
useEffect(() => { refetch(); }, [page]);

// ✅ Do use v5 object syntax
const { data } = useQuery({ queryKey: ['projects'], queryFn: fetchProjects });

// ✅ Do cancel queries before optimistic updates
onMutate: async () => {
  await queryClient.cancelQueries({ queryKey: projectKeys.lists() });
}

// ✅ Do use query key factory
queryKey: projectKeys.lists()

// ✅ Do use query data directly
const { data: projects } = useProjects();

// ✅ Do include parameters in query key
const { data } = useProjects({ page }); // Auto-refetches when page changes
```

### Radix UI Anti-Patterns

```typescript
// ❌ Don't nest Select.Content directly in Dialog.Content
<Dialog.Content>
  <Select.Content> {/* Focus trap breaks keyboard nav */}
</Dialog.Content>

// ❌ Don't allow close during mutation
<Dialog.Root open={open} onOpenChange={onOpenChange}>
  {/* User can close while mutation pending */}
</Dialog.Root>

// ✅ Do use Portal for Select inside Dialog
<Dialog.Content>
  <Select.Portal>
    <Select.Content> {/* Escapes focus trap */}
  </Select.Portal>
</Dialog.Content>

// ✅ Do prevent close during mutation
const handleOpenChange = (newOpen) => {
  if (!newOpen && isPending) return;
  onOpenChange(newOpen);
};
```

### localStorage Anti-Patterns

```typescript
// ❌ Don't access localStorage without error handling
localStorage.setItem('key', value); // Will crash in private browsing

// ❌ Don't assume localStorage data is valid
const id = localStorage.getItem('projectId');
setSelectedProjectId(id); // Might be deleted project

// ✅ Do wrap in try-catch with fallback
try {
  localStorage.setItem('key', value);
} catch (e) {
  // Use in-memory fallback
}

// ✅ Do validate before using
const id = localStorage.getItem('projectId');
if (id && projects.some(p => p.id === id)) {
  setSelectedProjectId(id);
}
```

---

## Success Metrics

**User Experience**:
- Project switching completes in < 100ms perceived latency
- Zero data loss across page reloads (localStorage persistence)
- Empty state onboards new users in < 30 seconds
- Error messages are actionable, not technical

**Performance**:
- Project list loads in < 500ms (p95)
- Smart polling reduces request volume by ~50% (tab visibility)
- Query cache hit rate > 80%
- Zero unnecessary re-renders (verified in React Profiler)

**Reliability**:
- Zero crashes from localStorage errors (comprehensive error handling)
- Zero race conditions from concurrent mutations (cancelQueries + mutation keys)
- Zero stale project references (validation on mount and project deletion)
- Works in all browsers including private browsing mode

**Code Quality**:
- Test coverage > 80%
- Zero TypeScript strict mode errors
- Zero linting errors
- All components follow existing patterns

---

## PRP Quality Self-Assessment

**Score: 9.5/10** - Very high confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research docs are thorough and detailed
  - Feature analysis: 620 lines with complete requirements
  - Codebase patterns: 1025 lines with exact patterns to follow
  - Documentation links: 725 lines with all URLs and gotchas
  - Examples: 4 complete working examples + 500-line README
  - Gotchas: 2014 lines covering 14 critical issues with solutions

- ✅ **Clear task breakdown**: 13 tasks with specific steps, patterns, and validation
  - Each task has PATTERN TO FOLLOW with exact file references
  - SPECIFIC STEPS are actionable and ordered logically
  - VALIDATION criteria are measurable and executable
  - Dependencies between tasks are clear

- ✅ **Proven patterns**: Examples extracted from production Archon codebase
  - NewProjectModal pattern (10/10 relevance)
  - useProjectQueries pattern (10/10 relevance)
  - Select component pattern (9/10 relevance)
  - localStorage persistence (8/10 relevance)

- ✅ **Validation strategy**: 4-level validation loop with executable commands
  - Level 1: TypeScript + lint (automated)
  - Level 2: Unit tests (automated)
  - Level 3: Integration tests (manual checklist)
  - Level 4: Cross-browser tests (compatibility)

- ✅ **Error handling**: 14 critical gotchas documented with solutions
  - Race conditions (#1, #2) - cancelQueries pattern
  - localStorage errors (#3, #4) - try-catch with fallback
  - Focus trap (#6) - Portal pattern
  - TanStack Query v5 (#10) - object syntax
  - All gotchas have ❌ WRONG / ✅ RIGHT code examples

**Deduction reasoning** (-0.5 points):
- **Minor gap**: React Router URL params marked as optional (Phase 5 enhancement)
  - Not included in main task list
  - If user wants this in MVP, would need additional tasks
  - Mitigation: Clear guidance in Task 7 notes and optional task structure

- **Minor consideration**: Radix UI component installation not explicitly verified
  - Codebase patterns doc mentions @radix-ui/react-dialog and @radix-ui/react-select
  - Documentation links assume these are installed
  - Mitigation: Task 5 and 6 will fail fast if not installed (TypeScript error)

**Mitigations**:
1. **URL params gap**: Documentation-links.md includes React Router references for future enhancement
2. **Installation verification**: Add Task 0 to verify dependencies before starting
3. **Fast failure**: TypeScript will catch missing Radix UI imports immediately

**Strengths that justify 9.5/10**:
- Examples are production-tested, not synthetic
- Gotchas have real-world detection methods (not just descriptions)
- All patterns cross-referenced between multiple documents
- Validation gates are executable commands, not vague suggestions
- Task list is implementation-ready with file paths and line numbers
- localStorage utility is complete (handles all browser quirks)
- Optimistic update pattern is bulletproof (cancelQueries + rollback)
- Empty state and error handling considered from the start

**Implementer readiness**:
An AI agent or junior developer can implement this feature with minimal questions by:
1. Reading examples/README.md for patterns
2. Following task list in order
3. Running validation gates after each task
4. Referring to gotchas.md when errors occur
5. Using exact file references to mirror existing patterns

This PRP achieves the goal of "comprehensive, well-structured, scores 8+/10, and enables first-pass implementation success."
