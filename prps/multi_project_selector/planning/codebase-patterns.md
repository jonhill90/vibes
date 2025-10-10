# Codebase Patterns: Multi-Project Selector

## Overview

This document identifies existing code patterns in the task-manager frontend that should be followed when implementing the multi-project selector feature. Patterns are extracted from both the local codebase and Archon (parent project), which has mature implementations of similar functionality.

## Architectural Patterns

### Pattern 1: Modal Dialog with Radix UI
**Source**: Archon - `infra/archon/archon-ui-main/src/features/projects/components/NewProjectModal.tsx`
**Relevance**: 10/10

**What it does**: Implements a modal dialog for creating new projects using Radix UI primitives with proper form handling and mutation integration.

**Key Techniques**:
```typescript
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "../../ui/primitives/dialog";
import { useCreateProject } from "../hooks/useProjectQueries";

const NewProjectModal: React.FC<{ open: boolean; onOpenChange: (open: boolean) => void; }> = ({ open, onOpenChange }) => {
  const [formData, setFormData] = useState({ title: "", description: "" });
  const createProjectMutation = useCreateProject();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    createProjectMutation.mutate(formData, {
      onSuccess: () => {
        setFormData({ title: "", description: "" }); // Reset form
        onOpenChange(false); // Close modal
      },
    });
  };

  const handleClose = () => {
    if (!createProjectMutation.isPending) { // Prevent close during mutation
      setFormData({ title: "", description: "" });
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          {/* Form fields with disabled state during mutation */}
          <Input disabled={createProjectMutation.isPending} />
          <Button disabled={createProjectMutation.isPending || !formData.title.trim()}>
            {createProjectMutation.isPending ? "Creating..." : "Create Project"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
};
```

**When to use**:
- Creating the CreateProjectModal component
- Any modal that performs mutations
- Forms with loading states

**How to adapt**:
- Simplify for task-manager (no fancy animations needed)
- Use existing Radix Dialog from package.json (@radix-ui/react-dialog@^1.1.15)
- Follow same pattern for form reset on success
- Same pattern for preventing close during mutation

**Why this pattern**:
- Proven in production (Archon)
- Accessible by default (Radix UI primitives)
- Clean separation of form state and mutation state
- Prevents race conditions with isPending checks

---

### Pattern 2: TanStack Query Hooks with Query Key Factory
**Source**: Task-manager - `infra/task-manager/frontend/src/features/tasks/hooks/useTaskQueries.ts`
**Relevance**: 10/10

**What it does**: Implements query hooks with hierarchical query key factory, smart polling, optimistic updates, and proper cache management.

**Key Techniques**:
```typescript
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DISABLED_QUERY_KEY, STALE_TIMES } from "../../shared/config/queryPatterns";
import { useSmartPolling } from "../../shared/hooks/useSmartPolling";

// Query key factory - hierarchical structure matching API
export const projectKeys = {
  all: ["projects"] as const,
  lists: () => [...projectKeys.all, "list"] as const,
  detail: (id: string) => [...projectKeys.all, "detail", id] as const,
};

// Query hook with smart polling
export function useProjects() {
  const { refetchInterval } = useSmartPolling(2000); // 2s polling

  return useQuery<Project[]>({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchInterval, // Smart polling based on visibility
    refetchOnWindowFocus: true, // Refetch on tab focus (cheap with ETags)
    staleTime: STALE_TIMES.normal, // 30s
  });
}

// Mutation with optimistic updates
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation<Project, Error, ProjectCreate, { previousProjects?: Project[]; optimisticId: string }>({
    mutationFn: (data) => projectService.createProject(data),

    // CRITICAL: onMutate for optimistic updates
    onMutate: async (newData) => {
      // Cancel in-flight queries to prevent race conditions
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      // Snapshot for rollback
      const previousProjects = queryClient.getQueryData<Project[]>(projectKeys.lists());

      // Create optimistic entity with stable ID (nanoid)
      const optimisticProject = createOptimisticEntity<Project>({
        ...newData,
        id: `temp-${Date.now()}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // Optimistically add to cache
      queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) =>
        [...old, optimisticProject]
      );

      return { previousProjects, optimisticId: optimisticProject._localId };
    },

    // Rollback on error
    onError: (error, variables, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }
    },

    // Replace optimistic with server data
    onSuccess: (serverData, variables, context) => {
      queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) =>
        replaceOptimisticEntity(old, context?.optimisticId, serverData)
      );
    },

    // Always refetch to ensure consistency
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}
```

**When to use**:
- Creating `useProjectQueries.ts` hook
- All query and mutation operations for projects
- Cache management for project data

**How to adapt**:
- Create `src/features/projects/hooks/useProjectQueries.ts` (new file)
- Define `projectKeys` factory following exact pattern
- Use existing `STALE_TIMES.normal` for project list
- Follow same optimistic update pattern from tasks

**Why this pattern**:
- Already proven in task-manager codebase
- Eliminates race conditions with cancelQueries
- Provides instant UI feedback with optimistic updates
- Smart polling reduces unnecessary requests
- ETag support reduces bandwidth by ~70%

---

### Pattern 3: Page-Level Component Structure
**Source**: Task-manager - `infra/task-manager/frontend/src/pages/KanbanPage.tsx`
**Relevance**: 9/10

**What it does**: Defines page-level component with header, layout, and feature component integration.

**Key Techniques**:
```typescript
export const KanbanPage = () => {
  const projectId = "hardcoded-uuid"; // TODO: Replace with selector

  return (
    <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
      {/* Page Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-full px-6 py-4">
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Task Management
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Organize your tasks with drag-and-drop Kanban board
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        <KanbanBoard projectId={projectId} />
      </main>
    </div>
  );
};
```

**When to use**:
- Updating KanbanPage.tsx to include ProjectSelector
- Layout structure for header modifications

**How to adapt**:
```typescript
// Updated pattern with ProjectSelector
export const KanbanPage = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  return (
    <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-full px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* NEW: ProjectSelector component here */}
            <ProjectSelector
              selectedProjectId={selectedProjectId}
              onProjectChange={setSelectedProjectId}
            />
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                Task Management
              </h1>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        {selectedProjectId ? (
          <KanbanBoard projectId={selectedProjectId} />
        ) : (
          <EmptyProjectState />
        )}
      </main>
    </div>
  );
};
```

**Why this pattern**:
- Maintains existing layout structure
- Consistent with current page design
- Easy to inject ProjectSelector component
- Dark mode support already in place

---

### Pattern 4: Service Layer with Typed Responses
**Source**: Task-manager - `infra/task-manager/frontend/src/features/projects/services/projectService.ts`
**Relevance**: 10/10

**What it does**: Implements service layer that returns typed data directly (not axios response objects).

**Key Techniques**:
```typescript
import apiClient from "../../shared/api/apiClient";
import type { Project, ProjectCreate } from "../types/project";

class ProjectService {
  /**
   * List all projects with optional pagination
   */
  async listProjects(page = 1, perPage = 100): Promise<Project[]> {
    const response = await apiClient.get<Project[]>("/api/projects", {
      params: { page, per_page: perPage },
    });
    return response.data; // Return data directly, not response
  }

  /**
   * Create a new project
   */
  async createProject(data: ProjectCreate): Promise<Project> {
    const response = await apiClient.post<Project>("/api/projects", data);
    return response.data;
  }

  /**
   * Get a single project by ID
   */
  async getProject(id: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/api/projects/${id}`);
    return response.data;
  }
}

// Export singleton instance
export const projectService = new ProjectService();
```

**When to use**:
- Project service is ALREADY IMPLEMENTED - just need to create query hooks
- No changes needed to service layer

**How to adapt**:
- Service already exists and is complete
- Just import and use in new `useProjectQueries.ts` hook
- Follow same pattern if adding new methods

**Why this pattern**:
- Already follows task-manager conventions
- Type-safe with TypeScript
- Clean API - returns data not response objects
- Error handling at apiClient level

---

### Pattern 5: Modal Form with Validation
**Source**: Task-manager - `infra/task-manager/frontend/src/features/tasks/components/TaskDetailModal.tsx`
**Relevance**: 8/10

**What it does**: Implements form validation, loading states, error handling, and mutation integration in a modal.

**Key Techniques**:
```typescript
export const TaskDetailModal = ({ task, isOpen, onClose }: Props) => {
  const [title, setTitle] = useState("");
  const [validationError, setValidationError] = useState("");

  const updateTask = useUpdateTask(projectId);

  // Validate form before submitting
  const validateForm = (): boolean => {
    if (!title.trim()) {
      setValidationError("Title is required");
      return false;
    }
    if (title.length > 200) {
      setValidationError("Title must be 200 characters or less");
      return false;
    }
    setValidationError("");
    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    updateTask.mutate({ taskId, updates }, {
      onSuccess: () => onClose(),
      onError: (error) => {
        setValidationError(error instanceof Error ? error.message : "Failed to update");
      },
    });
  };

  const isLoading = updateTask.isPending;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        {/* Validation Error Display */}
        {validationError && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p className="text-sm text-red-800 dark:text-red-300">{validationError}</p>
          </div>
        )}

        {/* Form Fields */}
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={isLoading}
        />

        {/* Action Buttons */}
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? "Saving..." : "Save Changes"}
        </Button>
      </DialogContent>
    </Dialog>
  );
};
```

**When to use**:
- CreateProjectModal component
- Form validation logic
- Error display patterns

**How to adapt**:
- Simpler validation for CreateProjectModal (just name required)
- Same loading state pattern
- Same error display pattern
- Follow disabled state pattern during mutations

**Why this pattern**:
- Already proven in task-manager
- Consistent UX with existing modals
- Prevents double submissions with isPending
- Clear error messaging

---

## Naming Conventions

### File Naming
**Pattern**: Feature-based organization with camelCase files

**Task-manager examples**:
- Components: `KanbanPage.tsx`, `TaskDetailModal.tsx`
- Hooks: `useTaskQueries.ts`, `useSmartPolling.ts`
- Services: `projectService.ts`, `taskService.ts`
- Types: `project.ts`, `task.ts`

**Recommendations**:
```
src/features/projects/
├── components/
│   ├── ProjectSelector.tsx       # NEW - dropdown component
│   └── CreateProjectModal.tsx    # NEW - creation modal
├── hooks/
│   └── useProjectQueries.ts      # NEW - query hooks
├── services/
│   └── projectService.ts         # EXISTS - no changes needed
└── types/
    └── project.ts                # EXISTS - no changes needed
```

### Class Naming
**Pattern**: PascalCase for components and types

**Examples from codebase**:
- Components: `KanbanPage`, `TaskDetailModal`, `KanbanBoard`
- Types: `Project`, `ProjectCreate`, `Task`, `TaskStatus`
- Services: `ProjectService`, `TaskService` (class names)

**Recommendations**:
- `ProjectSelector` - dropdown component
- `CreateProjectModal` - modal component
- `EmptyProjectState` - empty state component
- `ProjectSelectorProps` - component props interface

### Function Naming
**Pattern**: camelCase with descriptive verbs

**Hook patterns** (from `useTaskQueries.ts`):
- `useProjects()` - query hook for list
- `useProject(id)` - query hook for single item
- `useCreateProject()` - mutation hook for creation
- `useUpdateProject()` - mutation hook for updates
- `useDeleteProject()` - mutation hook for deletion

**Handler patterns** (from components):
- `handleSave()` - save actions
- `handleClose()` - close actions
- `handleProjectChange(id)` - selection changes
- `handleSubmit(e)` - form submissions

**Recommendations**:
```typescript
// In ProjectSelector.tsx
const handleProjectChange = (projectId: string) => { ... };
const handleCreateClick = () => { ... };

// In CreateProjectModal.tsx
const handleSubmit = (e: React.FormEvent) => { ... };
const handleClose = () => { ... };
```

---

## File Organization

### Directory Structure
**Pattern**: Vertical slice architecture - features own their components, hooks, services, and types

**Current task-manager structure**:
```
src/
├── features/
│   ├── projects/
│   │   ├── services/
│   │   │   └── projectService.ts        # EXISTS
│   │   └── types/
│   │       └── project.ts                # EXISTS
│   ├── tasks/
│   │   ├── components/
│   │   │   ├── KanbanBoard.tsx
│   │   │   ├── KanbanColumn.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   └── TaskDetailModal.tsx
│   │   ├── hooks/
│   │   │   └── useTaskQueries.ts
│   │   ├── services/
│   │   │   └── taskService.ts
│   │   └── types/
│   │       └── task.ts
│   └── shared/
│       ├── api/
│       │   └── apiClient.ts
│       ├── config/
│       │   ├── queryClient.ts
│       │   └── queryPatterns.ts
│       └── hooks/
│           └── useSmartPolling.ts
├── pages/
│   └── KanbanPage.tsx
└── App.tsx
```

**Recommended additions**:
```
src/features/projects/
├── components/                     # NEW DIRECTORY
│   ├── ProjectSelector.tsx         # NEW - dropdown component
│   ├── CreateProjectModal.tsx      # NEW - creation modal
│   └── EmptyProjectState.tsx       # NEW - empty state
├── hooks/                          # NEW DIRECTORY
│   └── useProjectQueries.ts        # NEW - query hooks
├── services/
│   └── projectService.ts           # EXISTS - no changes
└── types/
    └── project.ts                  # EXISTS - no changes
```

**Justification**:
- Follows existing vertical slice pattern
- Projects feature owns all project-related code
- Easy to find related files
- Clear separation of concerns
- Matches Archon's mature structure

---

## Common Utilities to Leverage

### 1. TanStack Query Configuration
**Location**: `src/features/shared/config/queryPatterns.ts`
**Purpose**: Shared query configuration constants

**Usage Example**:
```typescript
import { DISABLED_QUERY_KEY, STALE_TIMES } from "../../shared/config/queryPatterns";

// Use in query hooks
export function useProjects() {
  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    staleTime: STALE_TIMES.normal, // 30 seconds
  });
}

// Conditional queries
export function useProject(id: string | undefined) {
  return useQuery({
    queryKey: id ? projectKeys.detail(id) : DISABLED_QUERY_KEY,
    queryFn: () => id ? projectService.getProject(id) : Promise.reject("No ID"),
    enabled: !!id,
  });
}
```

### 2. Optimistic Update Utilities
**Location**: `src/features/shared/utils/optimistic.ts`
**Purpose**: Helper functions for optimistic updates with nanoid-based stable IDs

**Usage Example**:
```typescript
import { createOptimisticEntity, replaceOptimisticEntity, removeDuplicateEntities } from "../../shared/utils/optimistic";

// In mutation onMutate
const optimisticProject = createOptimisticEntity<Project>({
  name: "New Project",
  description: "Description",
  // ... other fields
});

// In mutation onSuccess
queryClient.setQueryData(projectKeys.lists(), (old: Project[] = []) => {
  const replaced = replaceOptimisticEntity(old, optimisticId, serverProject);
  return removeDuplicateEntities(replaced);
});
```

### 3. Smart Polling Hook
**Location**: `src/features/shared/hooks/useSmartPolling.ts`
**Purpose**: Visibility-aware polling that pauses when tab is hidden

**Usage Example**:
```typescript
import { useSmartPolling } from "../../shared/hooks/useSmartPolling";

export function useProjects() {
  const { refetchInterval } = useSmartPolling(2000); // 2s base interval

  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchInterval, // Adapts to visibility
  });
}
```

### 4. API Client
**Location**: `src/features/shared/api/apiClient.ts`
**Purpose**: Configured axios instance with error handling and ETag support

**Usage Example**:
```typescript
import apiClient from "../../shared/api/apiClient";

// Already used in projectService.ts - no changes needed
async listProjects(): Promise<Project[]> {
  const response = await apiClient.get<Project[]>("/api/projects");
  return response.data;
}
```

### 5. Radix UI Components
**Location**: Installed as dependencies (@radix-ui/react-dialog, @radix-ui/react-select)
**Purpose**: Accessible UI primitives

**Available components**:
- `@radix-ui/react-dialog` - Modal dialogs
- `@radix-ui/react-select` - Dropdown selects

**Usage Example**:
```typescript
// For CreateProjectModal
import * as Dialog from "@radix-ui/react-dialog";

// For ProjectSelector
import * as Select from "@radix-ui/react-select";
```

**Note**: Task-manager already has these installed. May need to create wrapper components similar to Archon's `src/features/ui/primitives/` structure.

---

## Testing Patterns

### Unit Test Structure
**Pattern**: Vitest with React Testing Library (from package.json)

**Example test pattern** (inferred from codebase structure):
```typescript
// src/features/projects/hooks/__tests__/useProjectQueries.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProjects, useCreateProject } from '../useProjectQueries';
import { projectService } from '../../services/projectService';

// Mock service
vi.mock('../../services/projectService', () => ({
  projectService: {
    listProjects: vi.fn(),
    createProject: vi.fn(),
  },
}));

describe('useProjects', () => {
  it('fetches projects successfully', async () => {
    const mockProjects = [{ id: '1', name: 'Test' }];
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const { result } = renderHook(() => useProjects(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={new QueryClient()}>
          {children}
        </QueryClientProvider>
      ),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockProjects);
  });
});
```

**Key techniques**:
- Mock services at module level
- Wrap hooks in QueryClientProvider
- Use waitFor for async assertions
- Test loading, success, and error states

### Integration Test Structure
**Pattern**: Component tests with mocked queries

**Example pattern**:
```typescript
// src/features/projects/components/__tests__/ProjectSelector.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProjectSelector } from '../ProjectSelector';

const mockProjects = [
  { id: '1', name: 'Project 1' },
  { id: '2', name: 'Project 2' },
];

describe('ProjectSelector', () => {
  it('renders project list', async () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <ProjectSelector
          selectedProjectId="1"
          onProjectChange={vi.fn()}
        />
      </QueryClientProvider>
    );

    // Test rendering and interactions
  });
});
```

---

## Anti-Patterns to Avoid

### 1. Hardcoded Query Times
**What it is**: Using magic numbers for stale times instead of shared constants
**Found in**: N/A - codebase follows good patterns
**Why to avoid**:
- Inconsistent caching behavior
- Hard to maintain
- No central configuration

**Example**:
```typescript
// ❌ BAD - hardcoded time
staleTime: 30000,

// ✅ GOOD - use shared constant
staleTime: STALE_TIMES.normal,
```

### 2. Missing Optimistic Update Rollback
**What it is**: Not implementing onError rollback in mutations
**Why to avoid**:
- UI shows incorrect state on error
- Cache becomes stale
- Poor user experience

**Example**:
```typescript
// ❌ BAD - no error handling
onMutate: async (newData) => {
  queryClient.setQueryData(key, (old) => [...old, newData]);
},

// ✅ GOOD - with rollback
onMutate: async (newData) => {
  await queryClient.cancelQueries({ queryKey: key });
  const previousData = queryClient.getQueryData(key);
  queryClient.setQueryData(key, (old) => [...old, optimisticData]);
  return { previousData };
},
onError: (err, variables, context) => {
  if (context?.previousData) {
    queryClient.setQueryData(key, context.previousData);
  }
},
```

### 3. Not Canceling Queries Before Optimistic Updates
**What it is**: Forgetting to call `cancelQueries` in onMutate
**Why to avoid**:
- Race condition: background refetch can overwrite optimistic update
- Inconsistent UI state
- Hard-to-debug issues

**Example**:
```typescript
// ❌ BAD - missing cancelQueries
onMutate: async (newData) => {
  const previous = queryClient.getQueryData(key);
  queryClient.setQueryData(key, newData);
  return { previous };
},

// ✅ GOOD - cancel first
onMutate: async (newData) => {
  await queryClient.cancelQueries({ queryKey: key }); // CRITICAL
  const previous = queryClient.getQueryData(key);
  queryClient.setQueryData(key, newData);
  return { previous };
},
```

### 4. Prop Drilling Instead of Query Hooks
**What it is**: Passing data down through multiple component levels
**Why to avoid**:
- Verbose and hard to maintain
- Couples components together
- TanStack Query already provides data anywhere

**Example**:
```typescript
// ❌ BAD - prop drilling
<Parent projects={projects}>
  <Child projects={projects}>
    <GrandChild projects={projects} />
  </Child>
</Parent>

// ✅ GOOD - use query hook where needed
const GrandChild = () => {
  const { data: projects } = useProjects();
  // ...
};
```

### 5. Not Using Query Key Factories
**What it is**: Hardcoding query keys throughout the codebase
**Why to avoid**:
- Typos lead to cache misses
- Hard to refactor
- No single source of truth

**Example**:
```typescript
// ❌ BAD - hardcoded keys
queryKey: ["projects", "list"],
queryKey: ["projects", "details", id],

// ✅ GOOD - use factory
queryKey: projectKeys.lists(),
queryKey: projectKeys.detail(id),
```

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. **TaskDetailModal** (Edit existing entity)
**Location**: `src/features/tasks/components/TaskDetailModal.tsx`
**Similarity**: Modal dialog with form, validation, and mutations
**Lessons**:
- Clean form state management with useState
- Validation before mutation
- Loading states with isPending
- Error display with styled error box
- Reset form on close/success
**Differences**:
- CreateProjectModal is simpler (creation vs editing)
- No preview mode needed
- Fewer fields (name + description only)

#### 2. **KanbanBoard** (Data display with loading/error states)
**Location**: `src/features/tasks/components/KanbanBoard.tsx`
**Similarity**: Component that fetches data and displays loading/error states
**Lessons**:
- Clear loading state UI with spinner
- Error state UI with clear message
- Empty state handling
- Smart polling integration
**Differences**:
- ProjectSelector is simpler (dropdown vs board)
- No drag-and-drop needed
- Fewer visual elements

#### 3. **KanbanPage** (Page-level integration)
**Location**: `src/pages/KanbanPage.tsx`
**Similarity**: Page component that needs to integrate project selection
**Lessons**:
- Header/main layout structure
- Dark mode Tailwind classes
- Component composition pattern
**Differences**:
- Need to add ProjectSelector to header
- Need to handle null selectedProjectId state

---

## Recommendations for PRP

Based on pattern analysis, the PRP should specify:

### 1. **Follow TanStack Query patterns from useTaskQueries.ts**
- Use same query key factory structure
- Implement optimistic updates with cancelQueries
- Use STALE_TIMES.normal for project list
- Use smart polling for real-time updates

### 2. **Reuse Radix UI Dialog pattern from Archon**
- CreateProjectModal should mirror NewProjectModal.tsx structure
- Use @radix-ui/react-dialog (already installed)
- Follow same form validation pattern
- Same loading state pattern with isPending

### 3. **Mirror TaskDetailModal validation patterns**
- Client-side validation before mutation
- Clear error messaging with styled error box
- Disable form during mutation
- Reset form on success

### 4. **Integrate into KanbanPage following existing structure**
- Add ProjectSelector to header (left of title)
- Use flex layout with gap-4 for spacing
- Maintain dark mode support
- Show EmptyProjectState when no project selected

### 5. **Create useProjectQueries.ts following useTaskQueries.ts exactly**
- Same file structure and exports
- Same optimistic update pattern
- Same query key factory pattern
- Use existing projectService (no changes needed)

### 6. **Avoid anti-patterns identified**
- ALWAYS call cancelQueries in onMutate
- ALWAYS implement onError rollback
- NEVER hardcode stale times
- NEVER use prop drilling
- NEVER skip query key factories

---

## Source References

### From Local Codebase (task-manager)
- `src/pages/KanbanPage.tsx` - Page layout structure (relevance 9/10)
- `src/features/tasks/hooks/useTaskQueries.ts` - Query hook pattern (relevance 10/10)
- `src/features/tasks/components/TaskDetailModal.tsx` - Modal form pattern (relevance 8/10)
- `src/features/tasks/components/KanbanBoard.tsx` - Loading/error states (relevance 7/10)
- `src/features/projects/services/projectService.ts` - Service layer (relevance 10/10)
- `src/features/projects/types/project.ts` - Type definitions (relevance 10/10)
- `src/features/shared/config/queryPatterns.ts` - Query configuration (relevance 10/10)
- `src/features/shared/hooks/useSmartPolling.ts` - Polling utility (relevance 8/10)
- `src/features/shared/utils/optimistic.ts` - Optimistic update utilities (relevance 10/10)
- `src/App.tsx` - QueryClient configuration (relevance 7/10)
- `package.json` - Dependencies (Radix UI, TanStack Query v5) (relevance 10/10)

### From Archon Codebase
- `infra/archon/archon-ui-main/src/features/projects/components/NewProjectModal.tsx` - Modal implementation (relevance 10/10)
- `infra/archon/archon-ui-main/src/features/projects/hooks/useProjectQueries.ts` - Query hooks reference (relevance 10/10)

### Archon Documentation (Contextual Knowledge)
- Archon ARCHITECTURE.md - Vertical slice architecture
- Archon QUERY_PATTERNS.md - TanStack Query patterns
- Archon DATA_FETCHING_ARCHITECTURE.md - Query configuration
- Archon API_NAMING_CONVENTIONS.md - Naming standards

---

## Next Steps for Assembler

When generating the PRP, reference these patterns in:

### "Current Codebase Tree" section:
```
Include:
- src/features/projects/services/projectService.ts (ready to use)
- src/features/projects/types/project.ts (types defined)
- src/features/tasks/hooks/useTaskQueries.ts (pattern to follow)
- src/features/shared/config/queryPatterns.ts (utilities)
- src/features/shared/utils/optimistic.ts (utilities)
- src/pages/KanbanPage.tsx (integration point)
```

### "Implementation Blueprint" section:
```
Include code snippets from:
- Query key factory pattern (from useTaskQueries.ts)
- Optimistic update pattern (from useTaskQueries.ts)
- Modal form pattern (from NewProjectModal.tsx)
- Validation pattern (from TaskDetailModal.tsx)
- Loading states pattern (from KanbanBoard.tsx)
```

### "Known Gotchas" section:
```
Add anti-patterns identified:
- Must call cancelQueries before optimistic updates
- Must implement onError rollback
- Must use query key factories
- Must use STALE_TIMES constants
- Must prevent modal close during mutation
```

### "Desired Codebase Tree" section:
```
Show new files based on file organization:
- src/features/projects/components/ProjectSelector.tsx
- src/features/projects/components/CreateProjectModal.tsx
- src/features/projects/components/EmptyProjectState.tsx
- src/features/projects/hooks/useProjectQueries.ts
```

### Testing Requirements:
```
Reference testing patterns from codebase:
- Mock projectService methods
- Mock STALE_TIMES and DISABLED_QUERY_KEY
- Test with QueryClientProvider wrapper
- Test loading, success, error states
- Test optimistic updates and rollback
```

### Success Criteria Validation:
```
Map to discovered patterns:
- ProjectSelector follows existing component patterns ✓
- CreateProjectModal mirrors Archon NewProjectModal ✓
- useProjectQueries follows useTaskQueries pattern ✓
- Integration with KanbanPage maintains layout ✓
- Dark mode support matches existing pages ✓
```

---

**Pattern Analysis Complete**: All architectural patterns, naming conventions, file organization, utilities, anti-patterns, and integration points have been documented with concrete examples from the codebase. The PRP can now be generated with high confidence based on proven patterns.
