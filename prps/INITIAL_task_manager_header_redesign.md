# INITIAL: Task Manager Header Redesign

## Problem Statement
The task manager UI needs a redesigned header layout with the following changes:

1. **Replace "Kanban Board" header with Project Selector dropdown**
   - Current: "Kanban Board" text appears as a header above the columns
   - Desired: Project selector dropdown should replace this header entirely
   - The dropdown should appear where "Kanban Board" currently is (above the column layout)

2. **Move "Task Management" title to the left**
   - Keep it as the main page title on the left side

3. **Add Dark/Light Mode Toggle**
   - Position: Upper right corner
   - Default: Light mode
   - Should persist preference across sessions
   - Currently implemented but not working

## Current Layout Issues
Based on the user's mockup image:
- Project dropdown is currently in wrong position (upper right instead of replacing "Kanban Board" header)
- "Kanban Board" text should be removed/replaced by the dropdown
- Theme toggle exists but doesn't function

## Desired Layout (from user's mockup)
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

## Technical Context
- Files already modified:
  - `/Users/jon/source/vibes/infra/task-manager/frontend/src/contexts/ThemeContext.tsx` (created)
  - `/Users/jon/source/vibes/infra/task-manager/frontend/src/components/ThemeToggle.tsx` (created)
  - `/Users/jon/source/vibes/infra/task-manager/frontend/src/App.tsx` (ThemeProvider added)
  - `/Users/jon/source/vibes/infra/task-manager/frontend/src/pages/KanbanPage.tsx` (modified)
  - `/Users/jon/source/vibes/infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx` (modified)

- Theme toggle created but not functioning
- Project selector moved to wrong position

## Success Criteria
1. Project dropdown appears where "Kanban Board" header currently is
2. "Task Management" title remains on left side
3. Theme toggle in upper right corner works correctly
4. Theme preference persists in localStorage
5. Layout matches user's mockup image exactly
6. Dark mode properly toggles all component styles

## Known Issues
1. Theme toggle button doesn't respond to clicks
2. Project dropdown in wrong position (needs to replace "Kanban Board" header)
3. Possible issue: ThemeContext may not be properly initialized or connected

## Additional Notes
- User provided a mockup image showing exact desired layout
- Current implementation is partially complete but incorrectly positioned
- Need to ensure theme toggle actually works (may be event handler issue)
