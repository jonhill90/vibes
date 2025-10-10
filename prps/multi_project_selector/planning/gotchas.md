# Known Gotchas: Multi-Project Selector

## Overview

This document identifies critical gotchas, common mistakes, security vulnerabilities, and performance pitfalls when implementing a multi-project selector using TanStack Query v5, Radix UI Dialog/Select, localStorage persistence, and React Router integration. Every gotcha includes detection methods and concrete solutions.

**Research Sources**: TanStack Query v5 documentation, TkDodo's React Query blog (maintainer), web research on localStorage security, Radix UI GitHub issues, and codebase pattern analysis.

---

## Critical Gotchas

### 1. Race Condition: Optimistic Update Overwritten by Background Refetch

**Severity**: Critical
**Category**: Data Integrity / User Experience
**Affects**: TanStack Query optimistic updates in `useCreateProject`
**Source**: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query

**What it is**:
When creating a project with optimistic updates, a background refetch (triggered by window focus or polling) can overwrite the optimistic data before the mutation completes, causing the newly created project to disappear from the UI temporarily.

**Why it's a problem**:
- User sees project appear, then disappear, then reappear (UI flicker)
- Confusing UX that looks like a bug
- Can cause race conditions if user tries to select the project immediately
- Breaks trust in the application's reliability

**How to detect it**:
- Open browser DevTools Network tab
- Create a new project
- Immediately switch browser tabs to trigger refetch on focus
- Watch for project disappearing from dropdown
- Check console for query invalidation/refetch logs

**How to avoid/fix**:
```typescript
// ❌ WRONG - No query cancellation, vulnerable to race conditions
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.createProject,
    onMutate: async (newProject) => {
      // Missing: await queryClient.cancelQueries()
      const optimistic = { ...newProject, id: `temp-${Date.now()}` };
      queryClient.setQueryData(projectKeys.lists(), (old: Project[]) =>
        [...old, optimistic]
      );
    },
  });
}

// ✅ RIGHT - Cancel queries to prevent race conditions
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.createProject,
    onMutate: async (newProject) => {
      // CRITICAL: Cancel any in-flight queries that might overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      // Snapshot for rollback
      const previousProjects = queryClient.getQueryData<Project[]>(projectKeys.lists());

      // Create optimistic entity with temporary ID
      const optimisticProject = {
        ...newProject,
        id: `temp-${Date.now()}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      // Update cache optimistically
      queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) =>
        [optimisticProject, ...old]
      );

      return { previousProjects, optimisticId: optimisticProject.id };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }
    },
    onSuccess: (serverProject, variables, context) => {
      // Replace optimistic with real data
      queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) =>
        old.map(p => p.id === context?.optimisticId ? serverProject : p)
      );
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

// Why this works:
// 1. cancelQueries() stops any background refetches from overwriting optimistic data
// 2. Context system allows rollback on error
// 3. onSuccess replaces temporary ID with server-generated ID
// 4. onSettled ensures final consistency with server state
```

**Testing for this gotcha**:
```typescript
// Test to verify race condition handling
it('should not lose optimistic update when query refetches', async () => {
  const queryClient = new QueryClient();
  const { result } = renderHook(() => useCreateProject(), {
    wrapper: createWrapper(queryClient),
  });

  // Trigger mutation
  act(() => {
    result.current.mutate({ name: 'New Project' });
  });

  // Simulate background refetch (race condition scenario)
  act(() => {
    queryClient.refetchQueries({ queryKey: projectKeys.lists() });
  });

  // Optimistic update should still be present
  const projects = queryClient.getQueryData<Project[]>(projectKeys.lists());
  expect(projects).toContainEqual(
    expect.objectContaining({ name: 'New Project' })
  );
});
```

---

### 2. Concurrent Mutations: Multiple Projects Created Simultaneously

**Severity**: Critical
**Category**: Data Integrity / Cache Corruption
**Affects**: Optimistic updates when creating multiple projects rapidly
**Source**: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query

**What it is**:
When a user creates multiple projects in rapid succession (e.g., double-clicking "Create" button), the first mutation's invalidation can overwrite the second mutation's optimistic update, causing the second project to disappear until its mutation completes.

**Why it's a problem**:
- Second project disappears from UI (looks like it failed)
- Cache becomes temporarily inconsistent
- User might create duplicate projects thinking first one failed
- Confusing user experience

**How to detect it**:
- Double-click "Create Project" button quickly
- Watch network tab - both POST requests fire
- Second project appears, then disappears, then reappears
- Console shows two mutations running concurrently

**How to avoid/fix**:
```typescript
// ❌ WRONG - Each mutation invalidates, causing race conditions
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.createProject,
    onSettled: () => {
      // This runs for BOTH mutations, causing second to be overwritten
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

// ✅ RIGHT - Only invalidate when no other mutations are running
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectService.createProject,
    mutationKey: ['createProject'], // CRITICAL: mutation key for tracking
    onMutate: async (newProject) => {
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });
      const previousProjects = queryClient.getQueryData<Project[]>(projectKeys.lists());

      const optimisticProject = {
        ...newProject,
        id: `temp-${Date.now()}-${Math.random()}`, // Unique temp ID
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) =>
        [optimisticProject, ...old]
      );

      return { previousProjects, optimisticId: optimisticProject.id };
    },
    onError: (error, variables, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }
    },
    onSettled: () => {
      // CRITICAL: Only invalidate if this is the last mutation running
      const mutationCount = queryClient.isMutating({ mutationKey: ['createProject'] });
      if (mutationCount === 1) {
        // This is the last mutation, safe to invalidate
        queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      }
      // If mutationCount > 1, another mutation is running - let it handle invalidation
    },
  });
}

// Bonus: Prevent double-click in CreateProjectModal
const CreateProjectModal = ({ open, onOpenChange }) => {
  const createProject = useCreateProject();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Prevent double submission
    if (createProject.isPending) return;

    createProject.mutate(formData, {
      onSuccess: () => {
        setFormData({ name: "", description: "" });
        onOpenChange(false);
      },
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <Button
        type="submit"
        disabled={createProject.isPending || !formData.name.trim()}
      >
        {createProject.isPending ? "Creating..." : "Create Project"}
      </Button>
    </form>
  );
};

// Why this works:
// 1. mutationKey allows tracking how many mutations are active
// 2. isMutating() returns count of active mutations with that key
// 3. Only last mutation triggers invalidation, avoiding overwrites
// 4. UI prevents double-clicks with isPending check
```

---

### 3. localStorage Quota Exceeded or Security Error

**Severity**: Critical
**Category**: Security / Data Persistence Failure
**Affects**: Project selection persistence in localStorage
**Source**: http://crocodillon.com/blog/always-catch-localstorage-security-and-quota-exceeded-errors

**What it is**:
localStorage can throw errors in multiple scenarios: quota exceeded (5-10MB limit), private browsing mode, cookies disabled, or SecurityError. These errors are uncaught and will crash the application.

**Why it's a problem**:
- Application crashes when trying to persist selected project
- User loses project selection on page reload
- No fallback mechanism for in-memory state
- Different error codes across browsers (code 22, 1014, -2147024882)

**How to detect it**:
- Open browser in private/incognito mode
- Disable cookies in browser settings
- Fill localStorage with large data to exceed quota
- Try to select a project
- Watch console for DOMException errors

**How to avoid/fix**:
```typescript
// ❌ WRONG - No error handling, will crash app
const saveSelectedProject = (projectId: string) => {
  localStorage.setItem('selectedProjectId', projectId);
};

const getSelectedProject = (): string | null => {
  return localStorage.getItem('selectedProjectId');
};

// ✅ RIGHT - Comprehensive error handling with fallback
// utils/projectStorage.ts
class ProjectStorage {
  private static KEY = 'selectedProjectId';
  private static inMemoryFallback: string | null = null;
  private static isAvailable: boolean | null = null;

  /**
   * Check if localStorage is available
   * Handles security errors, private browsing, disabled cookies
   */
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

  /**
   * Cross-browser quota exceeded detection
   */
  private static isQuotaExceeded(e: any): boolean {
    if (!e) return false;

    // Check for error code (most browsers)
    if (e.code) {
      switch (e.code) {
        case 22: // Standard quota exceeded
          return true;
        case 1014: // Firefox
          return e.name === 'NS_ERROR_DOM_QUOTA_REACHED';
      }
    }

    // Internet Explorer 8
    if (e.number === -2147024882) {
      return true;
    }

    // Check error name (some browsers)
    return e.name === 'QuotaExceededError';
  }

  /**
   * Get selected project ID with error handling
   */
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

  /**
   * Set selected project ID with quota handling
   */
  static set(projectId: string | null): void {
    // Update in-memory fallback first
    this.inMemoryFallback = projectId;

    if (!this.checkAvailability()) {
      return; // Gracefully degrade to in-memory only
    }

    try {
      if (projectId === null) {
        localStorage.removeItem(this.KEY);
      } else {
        localStorage.setItem(this.KEY, projectId);
      }
    } catch (e) {
      if (this.isQuotaExceeded(e)) {
        console.error('localStorage quota exceeded, clearing old data');
        // Try to free up space by clearing our data
        try {
          localStorage.removeItem(this.KEY);
          localStorage.setItem(this.KEY, projectId);
        } catch (retryError) {
          console.error('Failed to save even after clearing:', retryError);
          // Fall back to in-memory (already set above)
        }
      } else {
        console.error('Failed to write to localStorage:', e);
        // Fall back to in-memory (already set above)
      }
    }
  }

  /**
   * Clear stored project ID
   */
  static clear(): void {
    this.inMemoryFallback = null;

    if (!this.checkAvailability()) return;

    try {
      localStorage.removeItem(this.KEY);
    } catch (e) {
      console.error('Failed to clear localStorage:', e);
    }
  }
}

export default ProjectStorage;

// Usage in component
const ProjectSelector = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(() => {
    // Initialize from storage (safe with error handling)
    return ProjectStorage.get();
  });

  const handleProjectChange = (projectId: string) => {
    setSelectedProjectId(projectId);
    ProjectStorage.set(projectId); // Safe - won't crash if it fails
  };

  return (/* ... */);
};

// Why this works:
// 1. Availability check prevents errors on every access
// 2. Cross-browser quota detection handles different error codes
// 3. In-memory fallback ensures app never crashes
// 4. Automatic retry after clearing space
// 5. Graceful degradation - feature still works without persistence
```

**Testing for this gotcha**:
```typescript
describe('ProjectStorage', () => {
  it('should handle quota exceeded error', () => {
    // Mock localStorage to throw quota error
    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      .mockImplementation(() => {
        const error: any = new Error('QuotaExceededError');
        error.code = 22;
        throw error;
      });

    // Should not throw, should use in-memory fallback
    expect(() => {
      ProjectStorage.set('project-123');
    }).not.toThrow();

    // Should still return value from in-memory fallback
    expect(ProjectStorage.get()).toBe('project-123');

    setItemSpy.mockRestore();
  });

  it('should handle security error in private browsing', () => {
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem')
      .mockImplementation(() => {
        throw new Error('SecurityError');
      });

    // Should not throw, should return null
    expect(() => {
      ProjectStorage.get();
    }).not.toThrow();

    expect(ProjectStorage.get()).toBeNull();

    getItemSpy.mockRestore();
  });
});
```

---

### 4. Deleted Project Still Selected in localStorage

**Severity**: High
**Category**: Data Integrity / User Experience
**Affects**: localStorage persistence when project is deleted
**Source**: Codebase analysis + localStorage research

**What it is**:
User selects a project, project is deleted (by them or someone else), localStorage still contains the deleted project ID. On page reload, app tries to load non-existent project, causing errors or empty state.

**Why it's a problem**:
- Kanban board shows "Project not found" error
- User confused why their selection doesn't work
- localStorage becomes stale and unreliable
- No automatic cleanup of invalid references

**How to detect it**:
- Select a project
- Delete that project (via API or another browser tab)
- Reload the page
- localStorage has stale project ID
- App either crashes or shows empty/error state

**How to avoid/fix**:
```typescript
// ❌ WRONG - No validation of stored project ID
const KanbanPage = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(() => {
    return ProjectStorage.get(); // Might be deleted project!
  });

  return <KanbanBoard projectId={selectedProjectId} />;
};

// ✅ RIGHT - Validate stored ID against available projects
const KanbanPage = () => {
  const { data: projects, isLoading } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  // Initialize and validate selected project on mount and when projects change
  useEffect(() => {
    if (!projects || projects.length === 0) {
      setSelectedProjectId(null);
      ProjectStorage.clear();
      return;
    }

    // Try to restore from localStorage
    const storedId = ProjectStorage.get();

    // Validate stored ID exists in current project list
    const storedProjectExists = storedId && projects.some(p => p.id === storedId);

    if (storedProjectExists) {
      setSelectedProjectId(storedId);
    } else {
      // Stored project was deleted or doesn't exist
      // Auto-select first available project
      const firstProject = projects[0];
      setSelectedProjectId(firstProject.id);
      ProjectStorage.set(firstProject.id);

      if (storedId) {
        console.warn(`Previously selected project ${storedId} no longer exists, selecting ${firstProject.id}`);
      }
    }
  }, [projects]);

  // Persist changes to localStorage
  useEffect(() => {
    if (selectedProjectId) {
      ProjectStorage.set(selectedProjectId);
    }
  }, [selectedProjectId]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!projects || projects.length === 0) {
    return <EmptyProjectState />;
  }

  if (!selectedProjectId) {
    return <LoadingSpinner />; // Initializing selection
  }

  return (
    <div className="h-screen flex flex-col">
      <header>
        <ProjectSelector
          selectedProjectId={selectedProjectId}
          onProjectChange={setSelectedProjectId}
        />
      </header>
      <main className="flex-1">
        <KanbanBoard projectId={selectedProjectId} />
      </main>
    </div>
  );
};

// Why this works:
// 1. Validates stored ID against current project list
// 2. Auto-selects first project if stored ID is invalid
// 3. Clears storage when no projects exist
// 4. Warns developer when cleanup happens
// 5. Handles edge case of projects loading asynchronously
```

**Edge case: Project deleted while viewing it**:
```typescript
// Handle project deletion in real-time
const KanbanPage = () => {
  const { data: projects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  // Watch for selected project being deleted
  useEffect(() => {
    if (!selectedProjectId || !projects) return;

    // Check if currently selected project still exists
    const selectedProjectExists = projects.some(p => p.id === selectedProjectId);

    if (!selectedProjectExists) {
      // Project was deleted! Select next available or clear
      if (projects.length > 0) {
        const nextProject = projects[0];
        setSelectedProjectId(nextProject.id);
        ProjectStorage.set(nextProject.id);

        // Optional: Show toast notification
        toast.info(`Project was deleted. Switched to ${nextProject.name}`);
      } else {
        setSelectedProjectId(null);
        ProjectStorage.clear();

        toast.info('All projects deleted');
      }
    }
  }, [selectedProjectId, projects]);

  return (/* ... */);
};

// Why this works:
// 1. Continuously validates selected project exists
// 2. Auto-switches to next available project
// 3. User feedback via toast notification
// 4. Handles edge case of last project being deleted
```

---

## High Priority Gotchas

### 5. Missing Query Key Dependencies Breaks Caching

**Severity**: High
**Category**: Performance / Cache Misuse
**Affects**: Project queries with filters or parameters
**Source**: https://www.buncolak.com/posts/avoiding-common-mistakes-with-tanstack-query-part-1/

**What it is**:
Not including function parameters in query keys causes all variations of the query to share the same cache entry, leading to incorrect data display and cache pollution.

**Why it's a problem**:
- Different queries share same cache (e.g., page 1 and page 2 both cached as "projects")
- Cache becomes corrupted with mixed data
- Refetch doesn't work properly because key doesn't change
- Defeats purpose of TanStack Query's intelligent caching

**How to detect it**:
- Open React DevTools Query panel
- Change filter/parameter (e.g., page number)
- Watch query key - if it doesn't change, this gotcha is present
- Old data shows briefly before refetch
- Cache entries don't increase when params change

**How to avoid/fix**:
```typescript
// ❌ WRONG - Parameters not in query key
export function useProjects(page: number, search?: string) {
  return useQuery({
    queryKey: projectKeys.all, // Same key for ALL variations!
    queryFn: () => projectService.listProjects({ page, search }),
  });
}

// Multiple calls create cache collisions:
useProjects(1, 'test'); // Caches as ['projects']
useProjects(2, 'foo');  // Overwrites cache at ['projects']!

// ❌ ALSO WRONG - Using refetch() to update
const ProjectList = () => {
  const [page, setPage] = useState(1);
  const { data, refetch } = useProjects(page); // Key doesn't include page!

  const nextPage = () => {
    setPage(p => p + 1);
    refetch(); // Race condition - might use stale page value
  };
};

// ✅ RIGHT - Parameters included in query key
// Query key factory with parameters
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  list: (filters?: { page?: number; search?: string }) =>
    [...projectKeys.lists(), { filters }] as const,
  details: () => [...projectKeys.all, 'detail'] as const,
  detail: (id: string) => [...projectKeys.details(), id] as const,
};

export function useProjects(filters?: { page?: number; search?: string }) {
  return useQuery({
    queryKey: projectKeys.list(filters), // Unique key per combination
    queryFn: () => projectService.listProjects(filters),
    staleTime: STALE_TIMES.normal,
  });
}

// Usage - automatic cache management
const ProjectList = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  // Query automatically refetches when page or search changes
  const { data, isLoading } = useProjects({ page, search });

  const nextPage = () => setPage(p => p + 1); // No manual refetch needed!

  return (/* ... */);
};

// Each combination gets its own cache entry:
// ['projects', 'list', { filters: { page: 1, search: 'test' } }]
// ['projects', 'list', { filters: { page: 2, search: 'test' } }]
// ['projects', 'list', { filters: { page: 1, search: 'foo' } }]

// Why this works:
// 1. Each parameter combination gets unique cache entry
// 2. Changing parameters triggers automatic refetch
// 3. No manual refetch() calls needed
// 4. Can invalidate by partial key matching
// 5. TanStack Query manages cache lifecycle automatically
```

**Invalidation with hierarchical keys**:
```typescript
// Invalidate all project queries
queryClient.invalidateQueries({ queryKey: projectKeys.all });

// Invalidate only list queries (all pages/searches)
queryClient.invalidateQueries({ queryKey: projectKeys.lists() });

// Invalidate specific filter combination
queryClient.invalidateQueries({
  queryKey: projectKeys.list({ page: 1, search: 'test' })
});

// Invalidate specific project detail
queryClient.invalidateQueries({ queryKey: projectKeys.detail('project-123') });
```

---

### 6. Radix Dialog Focus Trap Conflicts with Nested Select

**Severity**: High
**Category**: User Experience / Accessibility
**Affects**: Radix UI Dialog with nested Select component
**Source**: https://github.com/radix-ui/primitives/issues/2275

**What it is**:
When a Radix Select component is nested inside a Radix Dialog (modal mode), the Dialog's focus trap prevents keyboard navigation within the Select dropdown. Arrow keys and typing affect the Dialog instead of the Select.

**Why it's a problem**:
- Users cannot navigate Select with keyboard (breaks accessibility)
- Arrow keys scroll the Dialog instead of changing selection
- Tab key exits Select instead of cycling through options
- Violates WCAG accessibility guidelines
- Poor UX for keyboard-only users

**How to detect it**:
- Open CreateProjectModal
- Add a Select field (e.g., project template selector)
- Tab to Select and press Enter to open dropdown
- Try using arrow keys or typing to filter
- Focus remains trapped in Dialog, Select is unusable

**How to avoid/fix**:
```typescript
// ❌ WRONG - Select nested in modal Dialog without portal
import * as Dialog from '@radix-ui/react-dialog';
import * as Select from '@radix-ui/react-select';

const CreateProjectModal = () => {
  return (
    <Dialog.Root>
      <Dialog.Content> {/* modal={true} by default */}
        <Select.Root>
          <Select.Trigger>Choose template</Select.Trigger>
          <Select.Content>
            {/* Focus trap prevents keyboard nav here! */}
            <Select.Item value="blank">Blank</Select.Item>
            <Select.Item value="kanban">Kanban</Select.Item>
          </Select.Content>
        </Select.Root>
      </Dialog.Content>
    </Dialog.Root>
  );
};

// ✅ RIGHT - Select.Content uses Portal to escape focus trap
import * as Dialog from '@radix-ui/react-dialog';
import * as Select from '@radix-ui/react-select';

const CreateProjectModal = () => {
  return (
    <Dialog.Root>
      <Dialog.Content>
        <form onSubmit={handleSubmit}>
          <Select.Root value={template} onValueChange={setTemplate}>
            <Select.Trigger className="w-full">
              <Select.Value placeholder="Choose template" />
            </Select.Trigger>

            {/* CRITICAL: Portal renders outside Dialog focus trap */}
            <Select.Portal>
              <Select.Content>
                <Select.Viewport>
                  <Select.Item value="blank">
                    <Select.ItemText>Blank Project</Select.ItemText>
                  </Select.Item>
                  <Select.Item value="kanban">
                    <Select.ItemText>Kanban Board</Select.ItemText>
                  </Select.Item>
                </Select.Viewport>
              </Select.Content>
            </Select.Portal>
          </Select.Root>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  );
};

// Why this works:
// 1. Portal renders Select.Content outside Dialog DOM hierarchy
// 2. Select.Content escapes Dialog's focus trap
// 3. Keyboard navigation works normally in Select
// 4. Tab cycling, arrow keys, typing all function correctly
// 5. Maintains proper z-index layering (Portal handles this)

// Alternative: Use Dialog modal={false} if you don't need focus trap
const NonModalDialog = () => {
  return (
    <Dialog.Root modal={false}> {/* No focus trap */}
      <Dialog.Content>
        <Select.Root>
          {/* Works without Portal, but loses modal behavior */}
        </Select.Root>
      </Dialog.Content>
    </Dialog.Root>
  );
};
```

**Testing for this gotcha**:
```typescript
// Integration test
it('should allow keyboard navigation in Select within Dialog', async () => {
  const { getByRole } = render(<CreateProjectModal open={true} />);

  // Open Select
  const selectTrigger = getByRole('combobox');
  await userEvent.click(selectTrigger);

  // Try arrow key navigation
  await userEvent.keyboard('{ArrowDown}');

  // First item should be focused (not Dialog scrolling)
  const firstOption = getByRole('option', { name: 'Blank Project' });
  expect(firstOption).toHaveFocus();

  // Arrow down again
  await userEvent.keyboard('{ArrowDown}');
  const secondOption = getByRole('option', { name: 'Kanban Board' });
  expect(secondOption).toHaveFocus();
});
```

---

### 7. React Router Stale Params with Multiple State Updates

**Severity**: High
**Category**: State Synchronization / URL Integrity
**Affects**: React Router integration with project selection
**Source**: https://github.com/remix-run/react-router/issues/9757

**What it is**:
When using `setSearchParams` to sync project selection to URL, calling it multiple times synchronously causes it to use stale `location.search` values. Only the last call takes effect, losing intermediate state changes.

**Why it's a problem**:
- URL doesn't reflect actual selected project
- Browser history becomes corrupted
- Back/forward navigation breaks
- Shareable links point to wrong project
- Race conditions when multiple components update URL

**How to detect it**:
- Implement URL params for project selection
- Rapidly switch between projects
- Check browser URL - it skips intermediate selections
- Press back button - doesn't navigate to previous project
- Console shows stale searchParams warnings

**How to avoid/fix**:
```typescript
// ❌ WRONG - Multiple setSearchParams calls use stale location.search
import { useSearchParams } from 'react-router-dom';

const ProjectSelector = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const handleProjectChange = (projectId: string) => {
    // Both calls read stale searchParams!
    setSearchParams({ project: projectId });
    setSearchParams({ project: projectId, view: 'board' }); // Only this one applies
  };
};

// ❌ ALSO WRONG - Using searchParams in useEffect dependency array
const KanbanPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const projectId = searchParams.get('project');
  const [localState, setLocalState] = useState(projectId);

  // Circular dependency - causes infinite loop
  useEffect(() => {
    if (localState !== projectId) {
      setSearchParams({ project: localState }); // Triggers re-render
    }
  }, [searchParams, localState]); // searchParams changes, loops forever
};

// ✅ RIGHT - Use updater function pattern to avoid stale reads
import { useSearchParams, useNavigate } from 'react-router-dom';

const ProjectSelector = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const handleProjectChange = (projectId: string) => {
    // Use updater function to get current params
    setSearchParams(prev => {
      const next = new URLSearchParams(prev);
      next.set('project', projectId);
      return next;
    }, { replace: true }); // replace: true avoids polluting history
  };
};

// ✅ BETTER - Use navigate() for more control
import { useNavigate, useParams } from 'react-router-dom';

const ProjectSelector = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();

  const handleProjectChange = (newProjectId: string) => {
    // Navigate to new project URL
    navigate(`/board/${newProjectId}`, {
      replace: true, // Replace current history entry
    });
  };
};

// ✅ BEST - URL as single source of truth (no local state)
const KanbanPage = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: projects } = useProjects();
  const navigate = useNavigate();

  // Validate project exists, redirect if not
  useEffect(() => {
    if (!projectId && projects && projects.length > 0) {
      // No project selected, redirect to first project
      navigate(`/board/${projects[0].id}`, { replace: true });
    } else if (projectId && projects && !projects.some(p => p.id === projectId)) {
      // Invalid project ID, redirect to first project
      navigate(`/board/${projects[0].id}`, { replace: true });
    }
  }, [projectId, projects, navigate]);

  if (!projectId) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <ProjectSelector
        selectedProjectId={projectId}
        onProjectChange={(id) => navigate(`/board/${id}`, { replace: true })}
      />
      <KanbanBoard projectId={projectId} />
    </div>
  );
};

// Why this works:
// 1. URL params are single source of truth (no state duplication)
// 2. navigate() doesn't suffer from stale closure issues
// 3. replace: true avoids cluttering browser history
// 4. Validation ensures URL always points to valid project
// 5. Works correctly with browser back/forward buttons
```

**Combining URL params with localStorage**:
```typescript
// Hybrid approach: URL for shareability, localStorage for default
const KanbanPage = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: projects } = useProjects();
  const navigate = useNavigate();

  useEffect(() => {
    if (!projectId && projects && projects.length > 0) {
      // No project in URL - check localStorage
      const storedId = ProjectStorage.get();
      const storedProjectExists = storedId && projects.some(p => p.id === storedId);

      const defaultProject = storedProjectExists ? storedId : projects[0].id;
      navigate(`/board/${defaultProject}`, { replace: true });
    }
  }, [projectId, projects, navigate]);

  // Persist URL project to localStorage for next visit
  useEffect(() => {
    if (projectId) {
      ProjectStorage.set(projectId);
    }
  }, [projectId]);

  return (/* ... */);
};

// Why this works:
// 1. URL is primary source of truth for current page
// 2. localStorage provides default when no URL param
// 3. localStorage gets updated when URL changes
// 4. Shareable links work (URL has project ID)
// 5. Direct navigation to / redirects to last viewed project
```

---

### 8. Mapping Query Data to External State (Redux/Context Anti-Pattern)

**Severity**: High
**Category**: Performance / Architecture
**Affects**: Project data management
**Source**: https://www.buncolak.com/posts/avoiding-common-mistakes-with-tanstack-query-part-1/

**What it is**:
Using `useEffect` to copy TanStack Query data into Redux, Context, or local state creates duplicate state management, causing unnecessary re-renders and cache synchronization issues.

**Why it's a problem**:
- Double renders: query updates → dispatch → component re-renders
- Cache and state get out of sync
- Defeats TanStack Query's caching benefits
- Adds complexity for no gain
- Harder to debug state issues

**How to detect it**:
- Search codebase for `useEffect` with query data in dependencies
- Check for `dispatch(setProjects(data))` patterns
- Look for `context.setProjects(data)` in query callbacks
- React DevTools Profiler shows double renders on data fetch
- Redux DevTools shows actions fired from query updates

**How to avoid/fix**:
```typescript
// ❌ WRONG - Mapping query data to Redux
import { useProjects } from '../hooks/useProjectQueries';
import { setProjects, setLoading } from '../store/projectSlice';

const ProjectSelector = () => {
  const dispatch = useDispatch();
  const projects = useSelector(state => state.projects.items); // Duplicate state!

  const { data, isLoading } = useProjects();

  // Anti-pattern: Syncing query data to Redux
  useEffect(() => {
    if (data) {
      dispatch(setProjects(data)); // Triggers re-render
    }
  }, [data, dispatch]); // Causes double render

  useEffect(() => {
    dispatch(setLoading(isLoading));
  }, [isLoading, dispatch]); // Another double render

  return (/* ... */);
};

// ❌ ALSO WRONG - Mapping to Context
const ProjectContext = createContext<Project[]>([]);

const ProjectProvider = ({ children }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const { data } = useProjects();

  useEffect(() => {
    if (data) {
      setProjects(data); // Duplicate state management
    }
  }, [data]);

  return (
    <ProjectContext.Provider value={projects}>
      {children}
    </ProjectContext.Provider>
  );
};

// ✅ RIGHT - Use TanStack Query directly
const ProjectSelector = () => {
  // No Redux, no Context, just query hook
  const { data: projects, isLoading, error } = useProjects();

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!projects) return null;

  return (
    <Select>
      {projects.map(project => (
        <SelectItem key={project.id} value={project.id}>
          {project.name}
        </SelectItem>
      ))}
    </Select>
  );
};

// Why this works:
// 1. Single source of truth (TanStack Query cache)
// 2. No duplicate state to keep in sync
// 3. Single render when data changes
// 4. Built-in loading/error states
// 5. Automatic cache management

// If multiple components need projects, just call the hook
const AnotherComponent = () => {
  const { data: projects } = useProjects(); // Same cache, no extra request
  // ...
};

// ✅ For global state that ISN'T server data, use React Context
const SelectionContext = createContext<{
  selectedProjectId: string | null;
  setSelectedProjectId: (id: string) => void;
}>(null);

const SelectionProvider = ({ children }) => {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  return (
    <SelectionContext.Provider value={{ selectedProjectId, setSelectedProjectId }}>
      {children}
    </SelectionContext.Provider>
  );
};

// Use Context for client state, TanStack Query for server state
const KanbanPage = () => {
  const { selectedProjectId, setSelectedProjectId } = useContext(SelectionContext);
  const { data: projects } = useProjects(); // Server state from query

  return (/* ... */);
};

// Why this works:
// 1. Clear separation: server state (TanStack Query) vs client state (Context)
// 2. Each tool used for its strength
// 3. No duplicate data storage
// 4. Easier to reason about data flow
```

---

## Medium Priority Gotchas

### 9. Not Preventing Dialog Close During Mutation

**Severity**: Medium
**Category**: User Experience / Data Integrity
**Affects**: CreateProjectModal
**Source**: Archon codebase patterns

**What it is**:
User can close the CreateProjectModal while a project creation mutation is in progress (clicking backdrop, pressing Esc, clicking Cancel), potentially losing the created project or leaving optimistic update orphaned.

**Why it's confusing**:
- Mutation completes in background but user doesn't see result
- Optimistic update shows project, then it disappears when modal closes
- User unsure if project was created
- Can lead to duplicate projects if user retries

**How to handle it**:
```typescript
// ❌ WRONG - User can close during mutation
const CreateProjectModal = ({ open, onOpenChange }) => {
  const createProject = useCreateProject();

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      {/* User can close while createProject.isPending! */}
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <Button disabled={createProject.isPending}>
            {createProject.isPending ? 'Creating...' : 'Create'}
          </Button>
        </form>
      </DialogContent>
    </Dialog.Root>
  );
};

// ✅ RIGHT - Prevent close during mutation
const CreateProjectModal = ({ open, onOpenChange }) => {
  const createProject = useCreateProject();
  const [formData, setFormData] = useState({ name: '', description: '' });

  const handleOpenChange = (newOpen: boolean) => {
    // Prevent closing if mutation is pending
    if (!newOpen && createProject.isPending) {
      return; // Block close attempt
    }

    // Safe to close - reset form
    if (!newOpen) {
      setFormData({ name: '', description: '' });
      createProject.reset(); // Clear any error state
    }

    onOpenChange(newOpen);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    createProject.mutate(formData, {
      onSuccess: (newProject) => {
        setFormData({ name: '', description: '' });
        onOpenChange(false); // Close after success
        // Optional: Auto-select newly created project
        onProjectCreated?.(newProject);
      },
    });
  };

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        onEscapeKeyDown={(e) => {
          // Block Esc key during mutation
          if (createProject.isPending) {
            e.preventDefault();
          }
        }}
        onPointerDownOutside={(e) => {
          // Block backdrop click during mutation
          if (createProject.isPending) {
            e.preventDefault();
          }
        }}
      >
        <form onSubmit={handleSubmit}>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            disabled={createProject.isPending}
            placeholder="Project name"
          />
          <Textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            disabled={createProject.isPending}
            placeholder="Description (optional)"
          />

          {createProject.error && (
            <div className="text-red-600 text-sm">
              Error: {createProject.error.message}
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={createProject.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createProject.isPending || !formData.name.trim()}
            >
              {createProject.isPending ? 'Creating...' : 'Create Project'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog.Root>
  );
};

// Why this works:
// 1. handleOpenChange checks isPending before allowing close
// 2. onEscapeKeyDown and onPointerDownOutside prevent accidental close
// 3. Form inputs disabled during mutation (visual feedback)
// 4. Cancel button disabled during mutation
// 5. Form resets only after successful close
```

---

### 10. Incorrect Usage of TanStack Query v5 API (Breaking Changes)

**Severity**: Medium
**Category**: API Compatibility / Migration
**Affects**: Query hooks (if migrating from v4)
**Source**: https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5

**What it is**:
TanStack Query v5 removed multi-argument overloads in favor of object-based syntax only. Using old v4 patterns causes TypeScript errors and runtime failures.

**Why it's a problem**:
- Migration from v4 breaks unexpectedly
- TypeScript shows confusing error messages
- Runtime errors if types not checked
- Documentation examples might use old API

**How to detect it**:
- TypeScript errors when calling `useQuery(key, fn, options)`
- Error: "Argument of type is not assignable to parameter"
- Code works in v4 but breaks in v5
- Console shows "useQuery is not defined" or similar

**How to avoid/fix**:
```typescript
// ❌ WRONG - v4 multi-argument syntax (no longer supported)
const { data } = useQuery(['projects'], fetchProjects, {
  staleTime: 30000,
});

const { mutate } = useMutation(createProject, {
  onSuccess: () => {/* ... */},
});

// ✅ RIGHT - v5 object-based syntax
const { data } = useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  staleTime: 30000,
});

const { mutate } = useMutation({
  mutationFn: createProject,
  onSuccess: () => {/* ... */},
});

// Other v5 breaking changes to watch for:

// ❌ WRONG - v4 used isLoading
if (query.isLoading) { /* ... */ }

// ✅ RIGHT - v5 uses isPending (more accurate name)
if (query.isPending) { /* ... */ }

// ❌ WRONG - v4 used cacheTime
useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  cacheTime: 5 * 60 * 1000,
});

// ✅ RIGHT - v5 uses gcTime (garbage collection time)
useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  gcTime: 5 * 60 * 1000,
});

// ❌ WRONG - v4 useQueries had different syntax
const queries = useQueries([
  { queryKey: ['project', '1'], queryFn: () => fetchProject('1') },
  { queryKey: ['project', '2'], queryFn: () => fetchProject('2') },
]);

// ✅ RIGHT - v5 useQueries requires queries array
const queries = useQueries({
  queries: [
    { queryKey: ['project', '1'], queryFn: () => fetchProject('1') },
    { queryKey: ['project', '2'], queryFn: () => fetchProject('2') },
  ],
});

// Migration checklist:
// 1. Update all useQuery/useMutation to object syntax
// 2. Replace isLoading with isPending
// 3. Replace cacheTime with gcTime
// 4. Wrap useQueries arrays in { queries: [...] }
// 5. Check for removed options (like useErrorBoundary)
```

---

### 11. Smart Polling Causing Excessive Requests

**Severity**: Medium
**Category**: Performance / API Load
**Affects**: Project list query with smart polling
**Source**: Task-manager useSmartPolling pattern

**What it is**:
Enabling smart polling for project list without considering frequency can cause excessive API requests, especially with multiple browser tabs open or frequent tab switching.

**Why it's a problem**:
- High server load from unnecessary requests
- Increased API costs
- Battery drain on mobile devices
- Network bandwidth waste
- Each tab runs its own polling interval

**How to detect it**:
- Open Network tab, filter by project API endpoint
- See requests every 2 seconds continuously
- Open multiple browser tabs - requests multiply
- Server logs show high request volume
- API rate limits may trigger

**How to avoid/fix**:
```typescript
// ❌ WRONG - Aggressive polling without consideration
export function useProjects() {
  const { refetchInterval } = useSmartPolling(2000); // Every 2 seconds!

  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchInterval, // Polls aggressively
  });
}

// ✅ RIGHT - Conservative polling with visibility awareness
export function useProjects() {
  // Smart polling pauses when tab hidden, resumes when visible
  // 30 seconds is reasonable for project list (changes infrequently)
  const { refetchInterval } = useSmartPolling(30000); // 30 seconds

  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchInterval, // Only polls when tab visible
    refetchOnWindowFocus: true, // Refetch when tab regains focus (free with ETags)
    staleTime: STALE_TIMES.normal, // 30 seconds - prevent over-fetching
  });
}

// ✅ BETTER - No polling, just refetch on focus
export function useProjects() {
  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchOnWindowFocus: true, // Refetch when user returns to tab
    staleTime: STALE_TIMES.normal, // Cache for 30 seconds
    // No polling - projects don't change that frequently
  });
}

// ✅ BEST - Conditional polling only when needed
export function useProjects(options?: { enableRealtime?: boolean }) {
  const { refetchInterval } = useSmartPolling(options?.enableRealtime ? 10000 : false);

  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchInterval, // Only polls if real-time mode enabled
    refetchOnWindowFocus: true,
    staleTime: STALE_TIMES.normal,
  });
}

// Usage
const ProjectSelector = () => {
  // Default: no polling, just refetch on focus
  const { data: projects } = useProjects();

  // For collaboration features: enable real-time updates
  const { data: projects } = useProjects({ enableRealtime: true });
};

// Why this works:
// 1. Smart polling pauses when tab hidden (saves requests)
// 2. Conservative interval (30s vs 2s = 93% fewer requests)
// 3. refetchOnWindowFocus catches changes when user returns
// 4. staleTime prevents redundant requests
// 5. Real-time mode optional for when needed
```

**Calculate request load**:
```typescript
// ❌ Aggressive polling (2s interval, 24/7)
// Requests per hour per tab: 3600 / 2 = 1800 requests
// 5 tabs open: 9000 requests/hour
// Daily: 216,000 requests per user!

// ✅ Conservative (30s interval, smart pausing)
// Active use (8 hours): 3600 * 8 / 30 = 960 requests
// Paused when hidden: ~50% reduction = 480 requests
// Daily: 480 requests per user (450x reduction!)
```

---

### 12. No Empty State for Zero Projects

**Severity**: Medium
**Category**: User Experience
**Affects**: Initial app state, all projects deleted scenario
**Source**: Feature analysis

**What it is**:
When no projects exist (new user or all deleted), app shows blank screen or loading spinner forever instead of guiding user to create first project.

**Why it's confusing**:
- New users don't know what to do
- Looks broken, not intentional
- No clear path forward
- Lost opportunity to onboard users

**How to handle**:
```typescript
// ❌ WRONG - No handling of empty state
const KanbanPage = () => {
  const { data: projects, isLoading } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  if (isLoading) return <LoadingSpinner />;

  // If no projects, this renders blank screen!
  return <KanbanBoard projectId={selectedProjectId} />;
};

// ✅ RIGHT - Dedicated empty state with call-to-action
const EmptyProjectState = ({ onCreateClick }: { onCreateClick: () => void }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
      <div className="mb-4">
        <FolderIcon className="w-16 h-16 text-gray-400" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        No Projects Yet
      </h2>
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
        Get started by creating your first project. Projects help you organize tasks
        and collaborate with your team.
      </p>
      <Button onClick={onCreateClick} size="lg">
        <PlusIcon className="w-5 h-5 mr-2" />
        Create Your First Project
      </Button>
    </div>
  );
};

const KanbanPage = () => {
  const { data: projects, isLoading } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Handle empty state
  if (!projects || projects.length === 0) {
    return (
      <>
        <EmptyProjectState onCreateClick={() => setCreateModalOpen(true)} />
        <CreateProjectModal
          open={createModalOpen}
          onOpenChange={setCreateModalOpen}
          onSuccess={(project) => {
            setSelectedProjectId(project.id); // Auto-select new project
            setCreateModalOpen(false);
          }}
        />
      </>
    );
  }

  return (/* normal UI */);
};

// Why this works:
// 1. Clear messaging about what's missing
// 2. Obvious call-to-action button
// 3. Educational content (explains what projects are)
// 4. Smooth transition from empty → first project
// 5. Auto-selects newly created project
```

---

## Low Priority Gotchas

### 13. Form State Not Reset Between Modal Opens

**Severity**: Low
**Category**: User Experience
**Affects**: CreateProjectModal
**Source**: Archon NewProjectModal pattern

**What it is**:
User opens modal, types project name, closes without submitting, reopens modal - previous input still shows instead of clean slate.

**Why it's confusing**:
- User expects fresh start each time
- Old error messages persist
- Can lead to accidental duplicate projects

**How to handle**:
```typescript
// ❌ WRONG - Form state persists across opens
const CreateProjectModal = ({ open, onOpenChange }) => {
  const [formData, setFormData] = useState({ name: '', description: '' });
  const createProject = useCreateProject();

  // Form state never resets!
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <Input value={formData.name} onChange={...} />
      </DialogContent>
    </Dialog.Root>
  );
};

// ✅ RIGHT - Reset form when modal closes
const CreateProjectModal = ({ open, onOpenChange }) => {
  const [formData, setFormData] = useState({ name: '', description: '' });
  const createProject = useCreateProject();

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      // Reset form when closing
      setFormData({ name: '', description: '' });
      createProject.reset(); // Clear mutation state
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      {/* ... */}
    </Dialog.Root>
  );
};
```

---

### 14. No Visual Feedback for Active Project in Selector

**Severity**: Low
**Category**: User Experience
**Affects**: ProjectSelector dropdown
**Source**: UX best practices

**What it is**:
Dropdown doesn't visually indicate which project is currently selected, making it hard to know current context.

**How to fix**:
```typescript
// ✅ Visual indicator for selected project
<SelectItem
  value={project.id}
  className={cn(
    "relative",
    project.id === selectedProjectId && "bg-blue-50 dark:bg-blue-900/20"
  )}
>
  {project.name}
  {project.id === selectedProjectId && (
    <CheckIcon className="absolute right-2 w-4 h-4 text-blue-600" />
  )}
</SelectItem>
```

---

## Library-Specific Quirks

### TanStack Query v5

**Version-Specific Issues**:
- **v5.x**: Breaking changes from v4 - object-based API only, `isPending` instead of `isLoading`, `gcTime` instead of `cacheTime`
- **v5.0-v5.20**: Some TypeScript inference issues with query keys (fixed in v5.21+)

**Common Mistakes**:
1. **Not using query key factories**: Leads to cache collisions and typos
2. **Forgetting cancelQueries in onMutate**: Race conditions with optimistic updates
3. **Over-invalidating**: Invalidating too broadly wastes network requests
4. **Mapping to Redux/Context**: Defeats purpose of TanStack Query

**Best Practices**:
- **Use hierarchical query keys**: `['projects', 'list', { filters }]` allows partial invalidation
- **Conservative stale times**: 30 seconds for lists, 5 minutes for details
- **Enable refetchOnWindowFocus**: Free with ETags, catches external changes
- **Use mutation keys**: Track concurrent mutations to prevent race conditions

---

### Radix UI Primitives

**Dialog Gotchas**:
1. **Focus trap in modal mode**: Can break nested Select - use Portal
2. **Can't customize close behavior**: Must use onEscapeKeyDown/onPointerDownOutside
3. **Auto-focus on first focusable element**: May not be desired - use autoFocus attribute

**Select Gotchas**:
1. **No native scrollbar**: Must use ScrollUpButton/ScrollDownButton components
2. **Portal required for proper z-index**: Especially inside Dialog
3. **Keyboard navigation quirks**: Home/End keys don't work by default

**Best Practices**:
- **Always use Portal for nested components**: Prevents focus trap issues
- **Provide aria-label attributes**: Improves accessibility
- **Test keyboard navigation**: Tab, Enter, Esc, Arrow keys should all work
- **Consider mobile**: Touch interactions differ from desktop

---

### localStorage API

**Browser Compatibility Issues**:
- **Quota limits vary**: 5MB (most browsers), 10MB (some), unlimited (old IE)
- **Error codes differ**: Code 22 (standard), 1014 (Firefox), -2147024882 (IE8)
- **Private browsing**: Safari throws on access, Chrome throws on write
- **Disabled cookies**: Some browsers disable localStorage when cookies disabled

**Security Considerations**:
- **Not encrypted**: Sensitive data visible in browser DevTools
- **Accessible to all scripts**: XSS attacks can steal data
- **No expiration**: Data persists until manually cleared
- **Protocol-specific**: HTTP and HTTPS have separate storage

**Best Practices**:
- **Always use try-catch**: Wrap all localStorage access
- **Validate on read**: Stored data might be corrupted or outdated
- **Don't store secrets**: Use secure, httpOnly cookies instead
- **Provide in-memory fallback**: App should work without localStorage

---

## Performance Gotchas

### 1. Excessive Re-renders from Query Subscriptions

**Impact**: UI jank, CPU usage
**Affects**: Components using useProjects in multiple places

**The problem**:
```typescript
// Each call to useProjects subscribes to cache updates
const ProjectSelector = () => {
  const { data: projects } = useProjects(); // Subscribes
  const { data: projectsAgain } = useProjects(); // Another subscription!

  // Every cache update causes 2 re-renders
};
```

**The solution**:
```typescript
// Call hook once, pass data down if needed
const ProjectSelector = () => {
  const { data: projects } = useProjects();

  return <ProjectDropdown projects={projects} />;
};

// Or use select to derive data without re-rendering
const { data: projectCount } = useProjects({
  select: (data) => data.length, // Only re-render if length changes
});
```

---

### 2. Large localStorage Writes Block Main Thread

**Impact**: UI freezes during project selection
**Affects**: localStorage.setItem calls

**The problem**:
localStorage is synchronous - large writes block JavaScript execution.

**The solution**:
```typescript
// Debounce writes to avoid blocking on every keystroke
const debouncedSave = debounce((id: string) => {
  ProjectStorage.set(id);
}, 500);

const handleProjectChange = (id: string) => {
  setSelectedProjectId(id); // Instant UI update
  debouncedSave(id); // Deferred persistence
};
```

---

## Security Gotchas

### 1. XSS Vulnerability in Project Names

**Severity**: High
**Type**: Cross-Site Scripting
**Affects**: Project name display
**CVE**: N/A (application-level)

**Vulnerability**:
If project names are rendered without escaping, malicious project names like `<script>alert('xss')</script>` could execute.

**Secure Implementation**:
```typescript
// ✅ React escapes by default
<SelectItem value={project.id}>
  {project.name} {/* Automatically escaped */}
</SelectItem>

// ❌ NEVER use dangerouslySetInnerHTML with user input
<div dangerouslySetInnerHTML={{ __html: project.name }} /> // VULNERABLE!
```

---

## Testing Gotchas

**Common Test Pitfalls**:

1. **Not mocking localStorage in tests**:
```typescript
// Setup global localStorage mock
beforeEach(() => {
  const store: Record<string, string> = {};
  const mockLocalStorage = {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { Object.keys(store).forEach(k => delete store[k]); }),
  };
  global.localStorage = mockLocalStorage as any;
});
```

2. **Not waiting for async query updates**:
```typescript
// ❌ WRONG
it('creates project', () => {
  const { result } = renderHook(() => useCreateProject());
  result.current.mutate({ name: 'Test' });
  expect(result.current.isSuccess).toBe(true); // Fails - async!
});

// ✅ RIGHT
it('creates project', async () => {
  const { result } = renderHook(() => useCreateProject());
  result.current.mutate({ name: 'Test' });
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
});
```

---

## Deployment Gotchas

**Environment-Specific Issues**:

- **Development**: Hot reload can cause query cache corruption - restart dev server
- **Staging**: Shared backend with production - test data pollution risk
- **Production**: CDN caching can serve stale HTML with outdated query keys

**Configuration Issues**:
```bash
# ❌ WRONG - Hardcoded API URL
const API_URL = 'http://localhost:8000';

# ✅ RIGHT - Environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## Anti-Patterns to Avoid

### 1. Polling Instead of Using Query Keys

**What it is**:
Using `refetch()` or polling to update data when parameters change, instead of including parameters in query key.

**Why it's bad**:
- Defeats TanStack Query's cache
- Creates race conditions
- Wastes network requests
- Harder to debug

**Better pattern**:
```typescript
// ❌ Anti-pattern
const [page, setPage] = useState(1);
const { data, refetch } = useProjects();
useEffect(() => { refetch(); }, [page]);

// ✅ Correct pattern
const { data } = useProjects({ page }); // Auto-refetches when page changes
```

---

### 2. Optimistic Update Without Rollback

**What it is**:
Implementing optimistic UI updates but not handling the error case to roll back changes.

**Why it's bad**:
- UI shows incorrect state when mutation fails
- Cache becomes corrupted
- User sees project that doesn't exist
- Confusing error messages

**Better pattern**:
Always implement onError with context-based rollback (see Gotcha #1).

---

### 3. Storing Derived Data in localStorage

**What it is**:
Storing computed values (e.g., project count, sorted lists) instead of just the selected project ID.

**Why it's bad**:
- Data gets stale quickly
- Increases storage usage
- Synchronization complexity
- Can exceed quota faster

**Better pattern**:
Only store minimal state (selected project ID), derive everything else from queries.

---

## Gotcha Checklist for Implementation

Before marking PRP complete, verify these gotchas are addressed:

- [ ] **Race conditions**: `cancelQueries()` called in all mutations
- [ ] **Optimistic rollback**: `onError` restores previous state
- [ ] **localStorage errors**: Try-catch with quota detection
- [ ] **Stale project ID**: Validation against current project list
- [ ] **Query key dependencies**: All parameters included in query keys
- [ ] **Focus trap**: Select uses Portal inside Dialog
- [ ] **Concurrent mutations**: Mutation keys and `isMutating()` check
- [ ] **Empty state**: Handled gracefully with call-to-action
- [ ] **Form reset**: Modal clears state on close
- [ ] **Close prevention**: Can't close modal during mutation
- [ ] **TanStack Query v5 API**: Object-based syntax throughout
- [ ] **No Redux mapping**: Query data used directly
- [ ] **Conservative polling**: 30s+ interval or disabled
- [ ] **URL validation**: Stale params handled in React Router integration

---

## Sources Referenced

### From Web Research
- **TanStack Query Gotchas**: https://www.buncolak.com/posts/avoiding-common-mistakes-with-tanstack-query-part-1/
- **Optimistic Updates**: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query
- **localStorage Errors**: http://crocodillon.com/blog/always-catch-localstorage-security-and-quota-exceeded-errors
- **Radix UI Issues**: https://github.com/radix-ui/primitives/issues/2275
- **React Router Stale Params**: https://github.com/remix-run/react-router/issues/9757
- **TanStack Query v5 Migration**: https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5

### From Codebase Analysis
- Task-manager `useTaskQueries.ts` - Query patterns
- Task-manager `useSmartPolling.ts` - Polling implementation
- Archon `NewProjectModal.tsx` - Modal patterns
- Archon `useProjectQueries.ts` - Optimistic updates

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include critical gotchas** in "Known Gotchas & Library Quirks" section
2. **Reference solutions** in "Implementation Blueprint" with code examples
3. **Add detection tests** to validation gates for each gotcha
4. **Highlight v5 breaking changes** in documentation references
5. **Warn about race conditions** prominently - this is the #1 bug source
6. **Include localStorage fallback** as non-negotiable requirement
7. **Mandate query key factories** - show exact pattern to follow
8. **Require mutation keys** for all mutations that might run concurrently

## Confidence Assessment

**Gotcha Coverage**: 9/10
- **Security**: High confidence - covered XSS, localStorage security, quota errors
- **Performance**: High confidence - covered polling, re-renders, cache patterns
- **Common Mistakes**: Very high confidence - drew from TanStack maintainer blog + research
- **Race Conditions**: Very high confidence - detailed patterns from expert sources
- **Browser Compatibility**: High confidence - cross-browser localStorage handling

**Gaps**:
- Network failure scenarios (offline mode) - not extensively covered
- Concurrent editing (multiple users editing same project) - out of scope for MVP
- Performance with 100+ projects - not researched (unlikely in MVP)

**Overall Confidence**: 9/10 - Comprehensive coverage of high-probability gotchas with concrete solutions.
