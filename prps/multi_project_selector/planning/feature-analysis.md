# Feature Analysis: Multi-Project Selector for Task Manager UI

## INITIAL.md Summary

Add project selection capability to the task-manager UI, enabling users to switch between multiple projects and view their respective Kanban boards. The backend fully supports multiple projects via `/api/projects` endpoints, but the frontend currently has a hardcoded project ID in `KanbanPage.tsx`. This feature will add a project dropdown/selector in the header, a create project modal, and state persistence via localStorage, transforming the single-project UI into a multi-project experience.

## Core Requirements

### Explicit Requirements (from INITIAL.md)

1. **Project Selector Component**
   - Display list of all available projects
   - Show currently selected project name
   - Enable quick switching between projects
   - Placed in header area

2. **Project Creation**
   - Modal/form for creating new projects
   - Name and description fields
   - Integration with existing POST `/api/projects` endpoint

3. **State Management**
   - Persist selected project in localStorage
   - Default to first project if none selected
   - Handle empty state (no projects exist)

4. **URL Integration (Optional for MVP)**
   - Project ID in URL params (`/board/:projectId`)
   - Shareable project links
   - Browser back/forward support

5. **Existing Functionality**
   - Maintain all current Kanban board features
   - No breaking changes to task management
   - Graceful handling of edge cases (deleted projects, no projects)

### Implicit Requirements (inferred from feature type and codebase)

1. **React Query Integration**
   - Use existing `projectService` and create `useProjectQueries` hook
   - Follow TanStack Query patterns from Archon codebase
   - Implement query key factory pattern
   - Smart polling for project list (if needed)

2. **Optimistic Updates**
   - Instant UI feedback when creating projects
   - Nanoid-based optimistic IDs
   - Rollback on error

3. **Component Architecture**
   - Follow vertical slice pattern from Archon
   - Components in `features/projects/components/`
   - Hooks in `features/projects/hooks/`
   - Reuse existing services

4. **UI/UX Standards**
   - Loading states for async operations
   - Error handling with user feedback
   - Accessible dropdown component
   - Visual indicator for active project
   - Empty state messaging

5. **Type Safety**
   - TypeScript strict mode
   - Use existing `Project` and `ProjectCreate` types
   - No type assertions or any usage

6. **Testing Requirements**
   - Component tests for ProjectSelector
   - Component tests for CreateProjectModal
   - Hook tests for useProjectQueries
   - Integration tests for state persistence

## Technical Components

### Data Models

**Already Exist** (from `features/projects/types/project.ts`):
```typescript
interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

interface ProjectCreate {
  name: string;
  description?: string;
}
```

**New Types Needed**:
```typescript
// For localStorage persistence
interface ProjectSelectionState {
  selectedProjectId: string | null;
  lastUpdated: string; // ISO timestamp
}

// For component props
interface ProjectSelectorProps {
  selectedProjectId: string | null;
  onProjectChange: (projectId: string) => void;
  onCreateProject: () => void;
}

interface CreateProjectModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: (project: Project) => void;
}
```

### External Integrations

**Existing Backend APIs** (already implemented):
- `GET /api/projects/` - List all projects (pagination optional)
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}` - Get single project
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

**Existing Frontend Services** (already implemented):
- `projectService.listProjects()` - Fetch all projects
- `projectService.createProject(data)` - Create new project
- `projectService.getProject(id)` - Get project by ID

**New Integrations Needed**:
- React Router (if URL params implemented)
- localStorage API for persistence
- Browser History API (if URL params implemented)

### Core Logic

**Project Selection Flow**:
1. On page load:
   - Check localStorage for `selectedProjectId`
   - If URL param exists (optional), use that
   - If neither, fetch projects and select first
   - If no projects exist, show empty state
2. On project change:
   - Update localStorage
   - Update URL param (optional)
   - Trigger Kanban board refetch with new projectId
3. On project creation:
   - Optimistically add to list
   - Auto-select newly created project
   - Update localStorage and URL

**State Synchronization**:
- localStorage as source of truth for persistence
- React state for UI reactivity
- TanStack Query cache for project data
- URL params (optional) for shareability

**Edge Case Handling**:
- No projects: Show "Create your first project" prompt
- Deleted project: Fallback to first available project
- localStorage corruption: Reset to default behavior
- Network errors: Show error state, retry capability

### UI/CLI Requirements

**ProjectSelector Component** (dropdown):
- Trigger button showing current project name
- Dropdown menu listing all projects
- Search/filter capability (if >10 projects)
- "Create New Project" action at bottom
- Loading skeleton while fetching
- Empty state message

**CreateProjectModal Component** (modal):
- Modal dialog (shadcn/ui Dialog pattern)
- Form with name (required) and description (optional)
- Client-side validation (name min 1 char)
- Submit button with loading state
- Cancel button
- Error display for API failures
- Auto-close on success

**KanbanPage Header Enhancement**:
- Replace static title with ProjectSelector
- Project name as main heading
- Breadcrumb-style navigation (optional)
- "New Project" button visibility

**Empty State Component**:
- Centered message "No projects yet"
- Call-to-action button "Create Your First Project"
- Optional illustration/icon
- Trigger CreateProjectModal on click

## Similar Implementations Found in Archon

### 1. Archon's NewProjectModal Component
- **Relevance**: 9/10
- **File**: `infra/archon/archon-ui-main/src/features/projects/components/NewProjectModal.tsx`
- **Key Patterns to Reuse**:
  - Dialog component from Radix UI primitives
  - Form state management with useState
  - Mutation hook pattern (`useCreateProject`)
  - Optimistic UI with loading states
  - Auto-focus on modal open
  - onSuccess callback pattern
  - Form validation (disable submit if empty)
- **Gotchas**:
  - Must handle isPending state to prevent double submissions
  - Need to reset form state on close
  - Error handling should be user-friendly

### 2. Archon's ProjectHeader Component
- **Relevance**: 7/10
- **File**: `infra/archon/archon-ui-main/src/features/projects/components/ProjectHeader.tsx`
- **Key Patterns to Reuse**:
  - Header layout with title and action button
  - Animation variants with framer-motion (optional)
  - Button placement and styling patterns
  - Icon usage (Plus icon for create)
- **Gotchas**:
  - Keep header minimal for task-manager (simpler than Archon)
  - Animation should not delay interactivity

### 3. Task-Manager's Existing Project Service
- **Relevance**: 10/10
- **File**: `infra/task-manager/frontend/src/features/projects/services/projectService.ts`
- **Key Patterns to Reuse**:
  - Already implements all required API calls
  - Typed responses (no axios response wrapping)
  - Error handling at API client level
  - Pagination support (page, perPage)
- **Implementation Notes**:
  - Service is ready to use as-is
  - Just need to create query hooks wrapper

### 4. Archon's TanStack Query Patterns
- **Relevance**: 10/10
- **Files**:
  - `infra/archon/archon-ui-main/src/features/projects/hooks/useProjectQueries.ts`
  - `infra/archon/archon-ui-main/src/features/shared/config/queryPatterns.ts`
- **Key Patterns to Reuse**:
  - Query key factory pattern (`projectKeys`)
  - DISABLED_QUERY_KEY for conditional queries
  - STALE_TIMES constants for cache configuration
  - Mutation with optimistic updates
  - Smart polling integration (if real-time needed)
- **Gotchas**:
  - Must create projectKeys factory in task-manager
  - Follow exact pattern to ensure type safety
  - Test query key consistency

## Recommended Technology Stack

### Based on Existing Codebase (task-manager/frontend)

**Core Framework**: React 18 with TypeScript 5
- Already in use
- Strict mode enabled
- No changes needed

**State Management**: TanStack Query v5
- Already configured in codebase
- Follow Archon query patterns
- No additional state library needed (no Redux/Zustand)

**UI Components**:
- HTML select or custom dropdown (evaluate existing components)
- Modal component (check if shadcn/ui Dialog exists, else create)
- May need to install Radix UI primitives if not present

**Routing** (if URL params implemented):
- React Router (check existing setup)
- URL params pattern: `/board/:projectId`
- Fallback to localStorage-only if router not configured

**Storage**: Browser localStorage API
- Native API, no library needed
- JSON serialization for state object
- Error handling for quota exceeded

**Testing**:
- Vitest (already in use)
- React Testing Library
- MSW for API mocking (if configured)

**Styling**:
- Tailwind CSS (already in use)
- Follow existing class patterns from KanbanPage
- Dark mode support (if already implemented)

## Assumptions Made

### 1. **React Router is Available**
- **Assumption**: The app uses React Router for routing
- **Reasoning**: KanbanPage exists at a route, implies router setup
- **Source**: Industry best practice for React SPAs
- **Fallback**: If not available, use localStorage-only approach (simpler MVP)

### 2. **UI Component Library Exists**
- **Assumption**: Task-manager has basic UI components or can adopt Radix UI
- **Reasoning**: Modern React apps typically have a component library
- **Source**: Archon uses Radix UI primitives, proven pattern
- **Action**: Verify existing components, install Radix Dialog if needed

### 3. **Project List is Manageable Size**
- **Assumption**: Users will have <50 projects initially
- **Reasoning**: Task management tools typically have limited project counts
- **Source**: Domain knowledge of task management UX
- **Action**: Add search/filter later if needed (YAGNI for MVP)

### 4. **Single User Context**
- **Assumption**: Each browser session represents single user
- **Reasoning**: localStorage is per-browser, no multi-user shown in code
- **Source**: Existing KanbanPage has hardcoded project, implies single-user
- **Note**: Multi-user would require backend user context

### 5. **Existing KanbanBoard Accepts projectId Prop**
- **Assumption**: KanbanBoard component already accepts projectId parameter
- **Reasoning**: Line 17 of KanbanPage shows `const projectId = "..."`
- **Source**: Direct observation from INITIAL.md
- **Validation**: Verify KanbanBoard component signature before implementation

### 6. **Dark Mode Already Implemented**
- **Assumption**: App has dark mode support (className="dark:...")
- **Reasoning**: KanbanPage uses dark mode Tailwind classes
- **Source**: Lines 20-30 of KanbanPage.tsx
- **Action**: Use dark: variants in new components

### 7. **No Project Permissions/Security**
- **Assumption**: All projects visible to all users (beta/MVP)
- **Reasoning**: No auth logic in existing projectService
- **Source**: Backend API has no auth checks shown
- **Note**: Add later if multi-user support needed

### 8. **Network-First Data Fetching**
- **Assumption**: Always fetch fresh project list on page load
- **Reasoning**: Projects don't change frequently, but critical to show accurate list
- **Source**: TanStack Query best practices - STALE_TIMES.normal (30s)
- **Action**: Use normal stale time, smart polling if real-time needed

## Success Criteria

Based on INITIAL.md requirements:

### Must Have (MVP)
- [ ] User can see list of all projects in dropdown
- [ ] User can switch between projects seamlessly
- [ ] Selected project persists across page reloads (localStorage)
- [ ] User can create new projects via modal form
- [ ] UI clearly shows which project is active
- [ ] All existing Kanban functionality works unchanged
- [ ] Graceful handling of edge cases:
  - [ ] No projects: Show create prompt
  - [ ] Deleted project: Auto-select next available
  - [ ] Network error: Show error message with retry

### Should Have (Post-MVP)
- [ ] URL integration with project ID parameter
- [ ] Browser back/forward support
- [ ] Shareable project links
- [ ] Project search/filter (if >10 projects)
- [ ] Edit project details from selector
- [ ] Delete project from selector

### Performance Criteria
- [ ] Project list loads in <500ms
- [ ] Project switch feels instant (<100ms perceived)
- [ ] Modal open/close is smooth (60fps)
- [ ] No unnecessary re-renders on project change
- [ ] LocalStorage operations are non-blocking

### Quality Criteria
- [ ] TypeScript strict mode passes
- [ ] All components have unit tests
- [ ] Hooks have integration tests
- [ ] Accessibility standards met (ARIA labels, keyboard nav)
- [ ] Works in Chrome, Firefox, Safari
- [ ] Mobile-responsive design

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus Areas**:
1. **Verify existing components**:
   - Check if Radix UI Dialog exists in `components/ui/`
   - Verify KanbanBoard component prop signature
   - Find any existing dropdown components to reuse
   - Locate existing modal patterns

2. **Routing investigation**:
   - Confirm React Router setup in `App.tsx`
   - Document current routing structure
   - Determine if route params already used

3. **TanStack Query setup**:
   - Verify queryClient configuration
   - Check if queryPatterns.ts exists (create if not)
   - Document existing query key patterns

4. **Testing infrastructure**:
   - Verify Vitest configuration
   - Check for existing test utilities
   - Locate test examples to follow

**Output**: Document existing patterns, identify gaps, recommend approach

### Documentation Hunter
**Focus Areas**:
1. **React Router documentation** (if using URL params):
   - useParams hook
   - useNavigate hook
   - Route parameter patterns

2. **Radix UI Dialog documentation**:
   - Dialog, DialogContent, DialogHeader, DialogFooter
   - Accessibility features
   - Animation patterns

3. **TanStack Query v5 documentation**:
   - useQuery with conditional execution
   - useMutation with optimistic updates
   - Query invalidation patterns
   - Query key factories

4. **LocalStorage best practices**:
   - Error handling (quota exceeded)
   - JSON serialization
   - Security considerations

**Output**: Curated documentation links and code snippets

### Example Curator
**Focus Areas**:
1. **Extract Archon NewProjectModal pattern**:
   - Complete component implementation
   - Form validation logic
   - Mutation hook integration
   - Error handling

2. **Extract Archon useProjectQueries pattern**:
   - Query key factory
   - List query with stale time
   - Create mutation with optimistic update
   - Testing examples

3. **Find dropdown/select examples**:
   - Accessible select patterns
   - Custom dropdown implementations
   - Search-enabled select (for future)

4. **LocalStorage persistence examples**:
   - State sync patterns
   - Error recovery
   - Type-safe serialization

**Output**: Working code examples ready to adapt

### Gotcha Detective
**Focus Areas**:
1. **Project deletion scenarios**:
   - What happens if selected project is deleted?
   - Race conditions between delete and select
   - Stale localStorage references

2. **Network failure handling**:
   - Project list fetch fails on load
   - Create project API fails mid-operation
   - Optimistic update rollback behavior

3. **Browser compatibility**:
   - LocalStorage quota limits
   - JSON.parse errors with corrupted data
   - URL encoding issues with project names

4. **React Query cache invalidation**:
   - When to invalidate project list
   - Avoid over-invalidation
   - Cache stale time tuning

5. **Component lifecycle issues**:
   - Modal close/open race conditions
   - Form state persistence between opens
   - Memory leaks with event listeners

**Output**: Documented edge cases, prevention strategies, test scenarios

## Risk Assessment

### High Risk
1. **URL routing not configured**
   - **Mitigation**: Start with localStorage-only, add URL params as v2
   - **Impact**: Medium (shareable links nice-to-have)

2. **KanbanBoard component not flexible**
   - **Mitigation**: Early verification, refactor if needed
   - **Impact**: High (core functionality)

3. **Missing UI component library**
   - **Mitigation**: Install Radix UI primitives, proven in Archon
   - **Impact**: Low (well-documented, easy install)

### Medium Risk
1. **Performance with many projects**
   - **Mitigation**: Virtual scrolling or search/filter later
   - **Impact**: Low (unlikely in beta)

2. **localStorage quota exceeded**
   - **Mitigation**: Error handling, fallback to in-memory
   - **Impact**: Low (minimal data stored)

3. **TanStack Query not configured**
   - **Mitigation**: Copy Archon configuration, well-documented
   - **Impact**: Medium (foundational requirement)

### Low Risk
1. **Dark mode styling inconsistencies**
   - **Mitigation**: Follow existing Tailwind patterns
   - **Impact**: Low (cosmetic)

2. **Testing setup incomplete**
   - **Mitigation**: Reference Archon test patterns
   - **Impact**: Low (can add tests iteratively)

## Open Questions for Implementation

### For Codebase Researcher to Answer
1. Does React Router exist in task-manager frontend?
2. What UI component library is currently used?
3. Is TanStack Query already configured with queryClient?
4. What is the exact prop signature of KanbanBoard component?
5. Are there existing test utilities and patterns to follow?

### For Technical Decision
1. **URL params vs localStorage-only for MVP?**
   - Recommendation: Start localStorage-only, add URL params in v2
   - Reason: Faster MVP, URL params require router setup

2. **Create new dropdown vs use native select?**
   - Recommendation: Use Radix Select if <10 projects, custom dropdown if more
   - Reason: Native select limited, Radix accessible and styled

3. **Where to place ProjectSelector in layout?**
   - Recommendation: Inside KanbanPage header, left of title
   - Reason: Contextual to page, doesn't require layout changes

4. **Auto-select first project or show empty state?**
   - Recommendation: Auto-select if projects exist, empty state if none
   - Reason: Reduces clicks, clear path forward

### For UX Decision
1. **Show project count in selector?**
   - Recommendation: Not for MVP, add later if useful
   - Reason: YAGNI, clutters UI

2. **Allow project management in selector dropdown?**
   - Recommendation: Create only, edit/delete separate
   - Reason: Keep selector focused, avoid complex nested UI

3. **Confirmation on project switch?**
   - Recommendation: No confirmation, instant switch
   - Reason: Non-destructive action, localStorage persists state

## Implementation Phases

### Phase 1: Foundation (Day 1)
1. Create `useProjectQueries.ts` hook with query key factory
2. Implement `useProjects()` list query
3. Implement `useCreateProject()` mutation
4. Add localStorage utility functions
5. Write hook tests

### Phase 2: UI Components (Day 2)
1. Create `CreateProjectModal.tsx` component
2. Create `ProjectSelector.tsx` dropdown component
3. Create `EmptyProjectState.tsx` component
4. Write component tests

### Phase 3: Integration (Day 3)
1. Update `KanbanPage.tsx` to use ProjectSelector
2. Implement localStorage persistence
3. Handle edge cases (no projects, deleted project)
4. Integration testing

### Phase 4: Polish (Day 4)
1. Loading states and error handling
2. Accessibility improvements (ARIA labels, keyboard nav)
3. Dark mode verification
4. Performance optimization

### Phase 5: Optional URL Params (Future)
1. Add React Router params to KanbanPage route
2. Sync URL with selectedProjectId state
3. Handle browser back/forward
4. Update tests

## Validation Gates

### Before Starting Implementation
- [ ] Verify KanbanBoard accepts projectId prop
- [ ] Confirm React Query is configured
- [ ] Identify or install Dialog component
- [ ] Review Archon examples fully

### Before Each Phase
- [ ] Previous phase tests passing
- [ ] TypeScript compilation succeeds
- [ ] No console errors or warnings
- [ ] Code review completed

### Before Merge
- [ ] All success criteria met
- [ ] Test coverage >80%
- [ ] Accessibility audit passed
- [ ] Performance benchmarks met
- [ ] Documentation updated

---

**Analysis Complete**: This comprehensive feature analysis provides all necessary context for downstream PRP generation agents to create a production-ready implementation plan. All assumptions documented, risks identified, and success criteria defined.
