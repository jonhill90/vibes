/**
 * KanbanPage - Page wrapper for Kanban board view
 *
 * PURPOSE: Provides project selection and board rendering
 *
 * PATTERN: Page-level component that wraps feature component
 *
 * TODO: Add project selection dropdown when multi-project support is added
 * For now, uses hardcoded project ID for MVP
 */

import { KanbanBoard } from "../features/tasks/components/KanbanBoard";

export const KanbanPage = () => {
  // TODO: Replace with actual project selection logic
  // For MVP, use hardcoded project ID or get from URL params
  const projectId = "default-project-id";

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
