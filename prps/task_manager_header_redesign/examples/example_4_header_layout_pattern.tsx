// Source: infra/task-manager/frontend/src/features/tasks/components/KanbanBoard.tsx
// Lines: 117-149
// Pattern: Header layout with flex positioning (CURRENT - needs restructure)
// Extracted: 2025-10-10
// Relevance: 10/10 - Shows EXACT structure that needs to change

/**
 * CURRENT LAYOUT (Incorrect):
 *
 * Row 1: [Title + Description] -------------- [ProjectSelector] [ThemeToggle]
 * Row 2: [Kanban Board Header]
 *        [Task count]
 *
 * DESIRED LAYOUT (Correct):
 *
 * Row 1: [Title + Description] ---------------------------- [ThemeToggle]
 * Row 2: [ProjectSelector]
 *        [Task count]
 */

// CURRENT IMPLEMENTATION (lines 117-149 from KanbanBoard.tsx)
// This shows what needs to change

return (
  <div className="h-full p-6">
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
      {/* ❌ PROBLEM: ProjectSelector should NOT be here */}
      <div className="flex items-center gap-4">
        <ProjectSelector
          selectedProjectId={selectedProjectId}
          onProjectChange={onProjectChange}
          onCreateProject={onCreateProject}
        />
        <ThemeToggle />
      </div>
    </div>

    {/* Board Sub-header */}
    {/* ✅ SOLUTION: ProjectSelector should replace "Kanban Board" header here */}
    <div className="mb-6">
      <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
        Kanban Board  {/* ❌ REMOVE THIS */}
      </h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
        {tasks?.length || 0} tasks total
      </p>
    </div>

    {/* Kanban Columns Grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-[calc(100%-5rem)]">
      {/* ... columns ... */}
    </div>
  </div>
);
