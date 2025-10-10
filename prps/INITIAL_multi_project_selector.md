# INITIAL: Multi-Project Selector for Task Manager UI

## Overview
Add project selection capability to the task-manager UI, allowing users to switch between multiple projects and view their respective Kanban boards.

## Current State
- Single hardcoded project ID in `KanbanPage.tsx` (line 17)
- Backend fully supports multiple projects via `/api/projects` endpoints
- Frontend has no UI for project selection or management
- Project service and hooks exist but are unused

## Desired Functionality

### User Stories
1. As a user, I want to see a list of my projects so I can select which one to view
2. As a user, I want to switch between projects without losing my place
3. As a user, I want to create new projects from the UI
4. As a user, I want to see which project I'm currently viewing

### Key Features
- **Project Dropdown/Selector** in the header
  - List all available projects
  - Show current project name
  - Quick switch between projects

- **Project Management**
  - Create new project (modal/form)
  - Edit project details (optional for MVP)
  - Delete project (optional for MVP)

- **State Management**
  - Persist selected project (localStorage)
  - Default to first project if none selected
  - Handle empty state (no projects)

- **URL Integration** (optional)
  - Project ID in URL params (`/board/:projectId`)
  - Shareable project links
  - Browser back/forward support

## Technical Considerations

### Existing Backend APIs
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}` - Get single project
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Existing Frontend Code
- `src/features/projects/services/projectService.ts` - Already exists
- `src/features/projects/hooks/useProjectQueries.ts` - Already exists (likely)
- `src/features/projects/types/project.ts` - Already exists

### Components Needed
1. **ProjectSelector** - Dropdown/select component
2. **CreateProjectModal** - Form for new projects
3. **ProjectContext** (optional) - Global project state

### Files to Modify
- `src/pages/KanbanPage.tsx` - Remove hardcoded ID, add selector
- Header component - Add project selector to header

## Constraints
- Must maintain existing Kanban board functionality
- Should not break current single-project workflow
- Must handle edge cases (no projects, deleted projects)
- Keep UI simple and intuitive

## Questions for Implementation
1. Should project selection use URL params or just local state?
2. Do we want project management (create/edit/delete) in this feature or separate?
3. What should happen when there are no projects? (Create first project prompt?)
4. Should we show task count per project in the selector?

## Success Criteria
- [ ] User can see list of all projects
- [ ] User can switch between projects
- [ ] Selected project persists across page reloads
- [ ] User can create new projects
- [ ] UI clearly shows which project is active
- [ ] All existing Kanban functionality works unchanged

## Notes
- Backend is ready, this is purely frontend work
- Existing project services/hooks should be used
- Consider UX for users with many projects (search/filter?)
