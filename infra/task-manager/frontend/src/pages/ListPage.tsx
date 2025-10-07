/**
 * ListPage - Task list view page with filtering and sorting
 *
 * PURPOSE: Main page component for table/list view of tasks
 *
 * KEY PATTERNS:
 * 1. Uses TaskListView component for display
 * 2. Integrates TaskDetailModal for task details
 * 3. URL-based filtering and sorting state
 */

import { useState } from "react";
import { useParams } from "react-router-dom";
import { TaskListView } from "../features/tasks/components/TaskListView";
import type { Task } from "../features/tasks/types/task";

export const ListPage = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  if (!projectId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-500 dark:text-gray-400">No project selected</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Task List</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          View and manage tasks in a filterable table
        </p>
      </div>

      <TaskListView projectId={projectId} onTaskClick={setSelectedTask} />

      {/* Task Detail Modal - Will be implemented in Task 18 */}
      {selectedTask && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setSelectedTask(null)}
        >
          <div
            className="bg-white dark:bg-gray-900 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                {selectedTask.title}
              </h2>
              <button
                onClick={() => setSelectedTask(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <div className="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                  {selectedTask.description || "No description"}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Status
                  </label>
                  <div className="text-gray-900 dark:text-gray-100 capitalize">
                    {selectedTask.status}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Priority
                  </label>
                  <div className="text-gray-900 dark:text-gray-100 capitalize">
                    {selectedTask.priority}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Assignee
                  </label>
                  <div className="text-gray-900 dark:text-gray-100">
                    {selectedTask.assignee}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Created
                  </label>
                  <div className="text-gray-900 dark:text-gray-100">
                    {new Date(selectedTask.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
