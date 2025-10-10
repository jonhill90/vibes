# Documentation Resources: Multi-Project Selector

## Overview
Comprehensive documentation for implementing a multi-project selector using Radix UI primitives, TanStack Query v5 for state management, React Router for URL params, and localStorage for persistence. All documentation sources verified as current and official (2025).

## Primary Framework Documentation

### Radix UI Primitives
**Official Docs**: https://www.radix-ui.com/primitives
**Version**: Latest (React 18+)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:
1. **Dialog Component**: https://www.radix-ui.com/primitives/docs/components/dialog
   - **Why**: Essential for CreateProjectModal implementation
   - **Key Concepts**: Modal vs non-modal, focus management, accessibility, Portal rendering
   - **Installation**: `npm install @radix-ui/react-dialog`

2. **Select Component**: https://www.radix-ui.com/primitives/docs/components/select
   - **Why**: Core component for ProjectSelector dropdown
   - **Key Concepts**: Controlled/uncontrolled state, keyboard navigation, WAI-ARIA compliance
   - **Installation**: `npm install @radix-ui/react-select`

**Code Examples from Docs**:
```jsx
// Dialog Example
<Dialog.Root>
  <Dialog.Trigger>Open Dialog</Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Dialog Title</Dialog.Title>
      <Dialog.Description>Dialog description</Dialog.Description>
      <Dialog.Close>Close</Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

// Select Example
<Select.Root>
  <Select.Trigger>
    <Select.Value placeholder="Select a project…" />
    <Select.Icon><ChevronDownIcon /></Select.Icon>
  </Select.Trigger>
  <Select.Portal>
    <Select.Content>
      <Select.Viewport>
        <Select.Item value="project-1">Project 1</Select.Item>
        <Select.Item value="project-2">Project 2</Select.Item>
      </Select.Viewport>
    </Select.Content>
  </Select.Portal>
</Select.Root>
```

**Gotchas from Documentation**:
- Dialog automatically manages focus trap in modal mode (can't tab outside)
- Select native scrollbar is hidden by default (need ScrollUpButton/ScrollDownButton)
- Both components require Portal for proper z-index stacking
- Use `asChild` prop to merge component with custom child elements
- Esc key automatically closes Dialog (can be disabled with `onEscapeKeyDown`)

---

### TanStack Query v5
**Official Docs**: https://tanstack.com/query/v5/docs/framework/react/overview
**Version**: v5 (requires React 18+)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:
1. **useQuery Hook**: https://tanstack.com/query/v5/docs/framework/react/reference/useQuery
   - **Why**: Fetching project list from API
   - **Key Concepts**: Object-based API, queryKey structure, staleTime/gcTime, conditional queries
   - **Breaking Change from v4**: `useQuery(key, fn, options)` → `useQuery({ queryKey, queryFn, ...options })`

2. **useMutation Hook**: https://tanstack.com/query/v5/docs/react/reference/useMutation
   - **Why**: Creating new projects with optimistic updates
   - **Key Concepts**: mutationFn, onMutate (optimistic), onError (rollback), onSuccess (invalidation)
   - **Breaking Change from v4**: `useMutation(fn, options)` → `useMutation({ mutationFn, ...options })`

3. **Query Keys Guide**: https://tanstack.com/query/v5/docs/framework/react/guides/query-keys
   - **Why**: Proper cache management and invalidation
   - **Key Concepts**: Array-based keys, hierarchical structure, query filters for fuzzy matching
   - **Best Practice**: Use query key factory pattern per feature

4. **Mutations Guide**: https://tanstack.com/query/v5/docs/framework/react/guides/mutations
   - **Why**: Understanding mutation lifecycle and side effects
   - **Key Concepts**: Mutation states (idle, pending, error, success), invalidation patterns

**Code Examples from Docs**:
```typescript
// useQuery with v5 API
const { data, isPending, isError, error } = useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  staleTime: 30000, // 30 seconds
})

// Conditional query (only run if enabled)
const { data: project } = useQuery({
  queryKey: ['projects', projectId],
  queryFn: () => fetchProject(projectId),
  enabled: !!projectId, // Only fetch if projectId exists
})

// useMutation with optimistic updates
const { mutate, isPending } = useMutation({
  mutationFn: createProject,
  onMutate: async (newProject) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['projects'] })

    // Snapshot previous value
    const previousProjects = queryClient.getQueryData(['projects'])

    // Optimistically update
    queryClient.setQueryData(['projects'], (old) => [...old, newProject])

    // Return context with snapshot
    return { previousProjects }
  },
  onError: (err, newProject, context) => {
    // Rollback on error
    queryClient.setQueryData(['projects'], context.previousProjects)
  },
  onSuccess: () => {
    // Invalidate to refetch
    queryClient.invalidateQueries({ queryKey: ['projects'] })
  },
})
```

**Gotchas from Documentation**:
- v5 requires React 18+ (uses useSyncExternalStore)
- `isPending` replaces `isLoading` (breaking change)
- `gcTime` replaces `cacheTime` (breaking change)
- Always cancel queries in onMutate to prevent race conditions
- Query keys are hashed deterministically (object order doesn't matter, array order does)
- Use `queryClient.setQueryData` for optimistic updates, not direct state mutation

---

## Library Documentation

### 1. React Router v6
**Official Docs**: https://reactrouter.com
**Purpose**: URL-based project selection (optional for MVP)
**Archon Source**: Not in Archon
**Relevance**: 7/10 (optional feature)

**Key Pages**:
- **useParams Hook**: https://reactrouter.com/api/hooks/useParams
  - **Use Case**: Extract projectId from URL (`/board/:projectId`)
  - **Example**:
  ```typescript
  import { useParams } from "react-router";

  function KanbanPage() {
    const { projectId } = useParams();
    // Use projectId to fetch project data
  }
  ```

- **useNavigate Hook**: https://reactrouter.com/api/hooks/useNavigate
  - **Use Case**: Programmatically navigate to project URLs
  - **Example**:
  ```typescript
  import { useNavigate } from "react-router";

  function ProjectSelector() {
    const navigate = useNavigate();

    const handleProjectChange = (projectId: string) => {
      navigate(`/board/${projectId}`, {
        replace: true // Replace instead of push to history
      });
    };
  }
  ```

**API Reference**:
- **useParams()**: Returns object of URL parameters
  - **Signature**: `const params = useParams()`
  - **Returns**: `Params<string>` object
  - **Example**: For route `/posts/:postId`, returns `{ postId: "123" }`

- **useNavigate()**: Returns navigation function
  - **Signature**: `const navigate = useNavigate()`
  - **Returns**: `NavigateFunction`
  - **Options**: `{ replace: boolean, state: any }`

---

### 2. Browser localStorage API
**Official Docs**: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
**Purpose**: Persist selected project across page reloads
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Pages**:
- **localStorage API**: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
  - **Use Case**: Store selectedProjectId in browser
  - **Core Methods**: `setItem()`, `getItem()`, `removeItem()`, `clear()`
  - **Data Format**: Key-value pairs (both strings)

**API Reference**:
- **setItem(key, value)**: Store data
  - **Signature**: `localStorage.setItem(key: string, value: string): void`
  - **Example**:
  ```typescript
  const state = { selectedProjectId: "abc123", lastUpdated: new Date().toISOString() };
  localStorage.setItem("projectSelection", JSON.stringify(state));
  ```

- **getItem(key)**: Retrieve data
  - **Signature**: `localStorage.getItem(key: string): string | null`
  - **Returns**: Value or null if not found
  - **Example**:
  ```typescript
  const data = localStorage.getItem("projectSelection");
  const state = data ? JSON.parse(data) : null;
  ```

- **removeItem(key)**: Delete data
  - **Signature**: `localStorage.removeItem(key: string): void`
  - **Example**: `localStorage.removeItem("projectSelection")`

**Type-Safe localStorage Pattern**:
```typescript
// Type-safe localStorage utility
interface ProjectSelectionState {
  selectedProjectId: string | null;
  lastUpdated: string;
}

class ProjectStorage {
  private static KEY = "projectSelection";

  static get(): ProjectSelectionState | null {
    try {
      const data = localStorage.getItem(this.KEY);
      if (!data) return null;

      const parsed = JSON.parse(data);
      // Validate structure
      if (typeof parsed.selectedProjectId !== 'string') return null;

      return parsed as ProjectSelectionState;
    } catch (error) {
      console.error("Failed to parse localStorage:", error);
      return null;
    }
  }

  static set(state: ProjectSelectionState): void {
    try {
      localStorage.setItem(this.KEY, JSON.stringify(state));
    } catch (error) {
      // Handle quota exceeded
      console.error("Failed to save to localStorage:", error);
    }
  }

  static remove(): void {
    localStorage.removeItem(this.KEY);
  }
}
```

**Gotchas from Documentation**:
- Data persists until explicitly removed (survives browser restart)
- Storage limit typically 5-10MB per origin
- Throws `SecurityError` if cookies blocked or private browsing
- Keys and values stored as UTF-16 strings (use JSON.stringify/parse for objects)
- Protocol-specific (HTTP vs HTTPS have separate storage)
- Synchronous API (can block main thread with large data)
- No server-side rendering support (check `typeof window !== 'undefined'`)

---

## Integration Guides

### TanStack Query + React Router
**Guide URL**: https://tanstack.com/query/v5/docs/framework/react/guides/queries
**Source Type**: Official
**Quality**: 10/10
**Archon Source**: Not in Archon

**What it covers**:
- Using URL params as part of query keys
- Synchronizing query state with URL
- Invalidating queries on route changes

**Code examples**:
```typescript
// Sync query with URL params
function KanbanPage() {
  const { projectId } = useParams();

  const { data: project } = useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => fetchProject(projectId),
    enabled: !!projectId,
  });

  // projectId change automatically triggers new query
}
```

**Applicable patterns**:
- Use URL params in queryKey for automatic refetching on navigation
- Combine localStorage (persistence) + URL (shareability) + React Query (caching)

---

### Optimistic Updates with Rollback
**Resource**: https://tanstack.com/query/v5/docs/framework/react/examples/optimistic-updates-cache
**Type**: Official Example
**Relevance**: 10/10

**Key Practices**:
1. **Cancel Queries Before Optimistic Update**: Prevent race conditions
   ```typescript
   await queryClient.cancelQueries({ queryKey: ['projects'] })
   ```

2. **Snapshot Previous State**: Enable rollback on error
   ```typescript
   const previousProjects = queryClient.getQueryData(['projects'])
   return { previousProjects } // Return as context
   ```

3. **Optimistically Update Cache**: Immediate UI feedback
   ```typescript
   queryClient.setQueryData(['projects'], (old) => [...old, newProject])
   ```

4. **Rollback on Error**: Restore previous state
   ```typescript
   onError: (err, variables, context) => {
     queryClient.setQueryData(['projects'], context.previousProjects)
   }
   ```

5. **Refetch on Settle**: Sync with server truth
   ```typescript
   onSettled: () => {
     queryClient.invalidateQueries({ queryKey: ['projects'] })
   }
   ```

---

## Best Practices Documentation

### Query Key Factory Pattern
**Resource**: https://tkdodo.eu/blog/effective-react-query-keys
**Type**: Community Best Practice (TanStack recommended)
**Relevance**: 10/10

**Key Practices**:
1. **Hierarchical Key Structure**: From generic to specific
   ```typescript
   const projectKeys = {
     all: ['projects'] as const,
     lists: () => [...projectKeys.all, 'list'] as const,
     list: (filters?: string) => [...projectKeys.lists(), { filters }] as const,
     details: () => [...projectKeys.all, 'detail'] as const,
     detail: (id: string) => [...projectKeys.details(), id] as const,
   }
   ```

2. **Colocate Keys with Queries**: Keep in same feature directory
   ```
   features/projects/
     ├── hooks/
     │   ├── useProjectQueries.ts  // Uses projectKeys
     │   └── projectKeys.ts         // Key factory
     ├── components/
     └── services/
   ```

3. **Flexible Invalidation**: Use partial key matching
   ```typescript
   // Invalidate all project queries
   queryClient.invalidateQueries({ queryKey: projectKeys.all })

   // Invalidate only list queries
   queryClient.invalidateQueries({ queryKey: projectKeys.lists() })

   // Invalidate specific project
   queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) })
   ```

**Example**:
```typescript
// features/projects/hooks/projectKeys.ts
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  list: (filters?: ProjectFilters) => [...projectKeys.lists(), { filters }] as const,
  details: () => [...projectKeys.all, 'detail'] as const,
  detail: (id: string) => [...projectKeys.details(), id] as const,
}

// features/projects/hooks/useProjectQueries.ts
export function useProjects(filters?: ProjectFilters) {
  return useQuery({
    queryKey: projectKeys.list(filters),
    queryFn: () => projectService.listProjects(filters),
    staleTime: 30000, // 30 seconds
  })
}

export function useProject(id: string | null) {
  return useQuery({
    queryKey: projectKeys.detail(id!),
    queryFn: () => projectService.getProject(id!),
    enabled: !!id,
  })
}

export function useCreateProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: projectService.createProject,
    onMutate: async (newProject) => {
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() })
      const previous = queryClient.getQueryData(projectKeys.list())

      // Optimistic update with temporary ID
      queryClient.setQueryData(projectKeys.list(), (old: Project[]) => [
        ...old,
        { ...newProject, id: `temp-${Date.now()}` }
      ])

      return { previous }
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(projectKeys.list(), context.previous)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() })
    },
  })
}
```

---

### Type-Safe localStorage
**Resource**: https://dev.to/yutakusuno/ts-consider-type-safe-localstorage-2p9m
**Type**: Community Tutorial
**Relevance**: 9/10

**Key Practices**:
1. **Generic Storage Class**: Type-safe get/set methods
   ```typescript
   class TypedStorage<T> {
     constructor(private key: string) {}

     get(): T | null {
       const data = localStorage.getItem(this.key);
       if (!data) return null;
       try {
         return JSON.parse(data) as T;
       } catch {
         return null;
       }
     }

     set(value: T): void {
       localStorage.setItem(this.key, JSON.stringify(value));
     }

     remove(): void {
       localStorage.removeItem(this.key);
     }
   }
   ```

2. **Validation Before Use**: Ensure data integrity
   ```typescript
   function isValidProjectState(data: unknown): data is ProjectSelectionState {
     return (
       typeof data === 'object' &&
       data !== null &&
       'selectedProjectId' in data &&
       (typeof data.selectedProjectId === 'string' || data.selectedProjectId === null)
     );
   }

   const storage = new TypedStorage<ProjectSelectionState>('projectSelection');
   const state = storage.get();
   if (state && isValidProjectState(state)) {
     // Use validated state
   }
   ```

3. **Error Handling**: Graceful degradation
   ```typescript
   try {
     storage.set(newState);
   } catch (error) {
     if (error instanceof DOMException && error.name === 'QuotaExceededError') {
       console.warn('localStorage quota exceeded');
       // Fallback: use in-memory state only
     }
   }
   ```

---

## Testing Documentation

### Vitest + React Testing Library
**Official Docs**: https://vitest.dev
**Archon Source**: Not in Archon

**Relevant Sections**:
- **Mocking localStorage**: https://vitest.dev/guide/mocking.html
  - **How to use**: Create localStorage mock before tests
  - **Pattern**:
  ```typescript
  beforeEach(() => {
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };
    global.localStorage = localStorageMock as any;
  });
  ```

- **Testing TanStack Query**: https://tanstack.com/query/v5/docs/framework/react/guides/testing
  - **Pattern**: Wrap tests with QueryClientProvider
  ```typescript
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  render(
    <QueryClientProvider client={queryClient}>
      <ProjectSelector />
    </QueryClientProvider>
  );
  ```

**Test Examples**:
```typescript
// Component test for ProjectSelector
describe('ProjectSelector', () => {
  it('loads and displays projects', async () => {
    const { getByText } = render(<ProjectSelector />);
    await waitFor(() => {
      expect(getByText('Project 1')).toBeInTheDocument();
    });
  });

  it('persists selection to localStorage', async () => {
    const { getByText } = render(<ProjectSelector />);
    fireEvent.click(getByText('Project 1'));

    expect(localStorage.setItem).toHaveBeenCalledWith(
      'projectSelection',
      expect.stringContaining('project-1')
    );
  });
});

// Hook test for useProjectQueries
describe('useProjectQueries', () => {
  it('optimistically updates on create', async () => {
    const { result } = renderHook(() => useCreateProject(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({ name: 'New Project' });
    });

    // Verify optimistic update
    expect(queryClient.getQueryData(['projects'])).toContainEqual(
      expect.objectContaining({ name: 'New Project' })
    );
  });
});
```

---

## Additional Resources

### Tutorials with Code
1. **TanStack Query v5 Migration Guide**: https://tanstack.com/query/v5/docs/framework/react/guides/migrating-to-v5
   - **Format**: Official Guide
   - **Quality**: 10/10
   - **What makes it useful**: Complete list of breaking changes with code examples

2. **Radix UI Getting Started**: https://www.radix-ui.com/primitives/docs/overview/getting-started
   - **Format**: Official Tutorial
   - **Quality**: 10/10
   - **What makes it useful**: Setup guide, styling patterns, accessibility tips

3. **React Router v6 Tutorial**: https://reactrouter.com/en/main/start/tutorial
   - **Format**: Official Interactive Tutorial
   - **Quality**: 10/10
   - **What makes it useful**: Step-by-step route setup with modern patterns

### API References
1. **Radix UI Dialog API**: https://www.radix-ui.com/primitives/docs/components/dialog#api-reference
   - **Coverage**: All Dialog component props, data attributes, accessibility
   - **Examples**: Yes, with TypeScript types

2. **TanStack Query API**: https://tanstack.com/query/v5/docs/framework/react/reference/useQuery
   - **Coverage**: Complete hook signatures, options, return values
   - **Examples**: Yes, extensive with TypeScript

3. **localStorage MDN**: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
   - **Coverage**: Complete API, browser compatibility, security
   - **Examples**: Yes, vanilla JavaScript

### Community Resources
1. **Query Key Factory Library**: https://github.com/lukemorales/query-key-factory
   - **Type**: GitHub repo (npm package)
   - **Why included**: Type-safe query key management (recommended by TanStack)

2. **TkDodo's React Query Blog**: https://tkdodo.eu/blog/practical-react-query
   - **Type**: Blog series (TanStack Query maintainer)
   - **Why included**: Real-world patterns and best practices from core team

3. **Type-Safe localStorage Library**: https://github.com/solydhq/typed-local-store
   - **Type**: GitHub repo (npm package)
   - **Why included**: Ready-to-use type-safe localStorage wrapper

---

## Documentation Gaps

**Not found in Archon or Web**:
- None for this feature - all technologies have excellent official documentation

**Outdated or Incomplete**:
- Some Stack Overflow answers still reference TanStack Query v4 API (filter for v5)
- Radix UI Themes docs separate from Primitives (we need Primitives)

**Recommendations**:
- Bookmark official docs pages (all are current and comprehensive)
- Follow TanStack Query v5 migration guide carefully (breaking changes from v4)
- Use TkDodo blog for advanced patterns (maintainer insights)

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Framework Docs:
  - Radix UI Dialog: https://www.radix-ui.com/primitives/docs/components/dialog
  - Radix UI Select: https://www.radix-ui.com/primitives/docs/components/select
  - TanStack Query v5: https://tanstack.com/query/v5/docs/framework/react/overview

Library Docs:
  - useQuery: https://tanstack.com/query/v5/docs/framework/react/reference/useQuery
  - useMutation: https://tanstack.com/query/v5/docs/react/reference/useMutation
  - React Router useParams: https://reactrouter.com/api/hooks/useParams
  - React Router useNavigate: https://reactrouter.com/api/hooks/useNavigate
  - localStorage API: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

Integration Guides:
  - Query Keys Guide: https://tanstack.com/query/v5/docs/framework/react/guides/query-keys
  - Mutations Guide: https://tanstack.com/query/v5/docs/framework/react/guides/mutations
  - Optimistic Updates Example: https://tanstack.com/query/v5/docs/framework/react/examples/optimistic-updates-cache

Testing Docs:
  - TanStack Query Testing: https://tanstack.com/query/v5/docs/framework/react/guides/testing
  - Vitest Mocking: https://vitest.dev/guide/mocking.html

Tutorials:
  - Effective Query Keys: https://tkdodo.eu/blog/effective-react-query-keys
  - Type-Safe localStorage: https://dev.to/yutakusuno/ts-consider-type-safe-localstorage-2p9m
  - TanStack Query v5 Migration: https://tanstack.com/query/v5/docs/framework/react/guides/migrating-to-v5
```

## Recommendations for PRP Assembly

When generating the PRP:
1. **Include these URLs** in "Documentation & References" section
2. **Extract code examples** shown above into PRP context (especially query key factory, optimistic updates, localStorage wrapper)
3. **Highlight gotchas** from documentation in "Known Gotchas" section:
   - TanStack Query v5 breaking changes (isPending vs isLoading, object-based API)
   - Radix Dialog focus trap in modal mode
   - localStorage quota limits and error handling
   - Query key hierarchical structure for efficient invalidation
4. **Reference specific sections** in implementation tasks:
   - "See Radix Dialog docs for focus management: [URL]"
   - "Follow TanStack optimistic update pattern: [URL]"
   - "Implement query key factory per Effective Query Keys: [URL]"
5. **Note installation requirements**:
   - `@radix-ui/react-dialog`
   - `@radix-ui/react-select`
   - TanStack Query already installed (verify v5)
   - React Router already installed (verify v6)

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:
- https://tanstack.com/query/v5/docs/framework/react/overview - TanStack Query is critical for modern React state management
- https://www.radix-ui.com/primitives - Radix UI primitives are industry standard for accessible React components
- https://reactrouter.com - React Router v6 is the de facto routing library
- https://tkdodo.eu/blog/practical-react-query - TkDodo's blog is essential reading for TanStack Query (written by maintainer)

**Why these are valuable for future PRPs**:
- TanStack Query patterns (query keys, optimistic updates) reusable across all data-fetching features
- Radix UI components reusable for any UI feature needing accessible primitives
- React Router patterns apply to all routing/navigation features
- These represent current best practices as of 2025

[Ingesting these would significantly improve Archon's coverage of modern React development patterns]
