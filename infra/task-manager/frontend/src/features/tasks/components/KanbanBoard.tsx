/**
 * KanbanBoard - 4-column Kanban layout with drag-and-drop integration
 *
 * PURPOSE: Main Kanban view for task management
 *
 * FEATURES:
 * - 4 columns (todo, doing, review, done)
 * - Drag-and-drop tasks between columns
 * - Optimistic updates with rollback on error
 * - Loading and error states
 *
 * GOTCHAS ADDRESSED:
 * - Check updateTaskPosition.isPending before mutation (Gotcha #9)
 * - Don't call mutation if source and destination are same
 *
 * USAGE:
 * ```tsx
 * <KanbanBoard projectId="project-uuid" />
 * ```
 */

import { useProjectTasks, useUpdateTaskPosition } from "../hooks/useTaskQueries";
import { KanbanColumn } from "./KanbanColumn";
import type { TaskStatus } from "../types/task";
import { groupBy } from "../../shared/utils/groupBy";
import { ProjectSelector } from "../../projects/components/ProjectSelector";
import { ThemeToggle } from "../../../components/ThemeToggle";

interface KanbanBoardProps {
  projectId: string;
  selectedProjectId: string | null;
  onProjectChange: (projectId: string) => void;
  onCreateProject: () => void;
}

// Column configuration
const COLUMNS: Array<{ status: TaskStatus; label: string }> = [
  { status: "todo", label: "To Do" },
  { status: "doing", label: "In Progress" },
  { status: "review", label: "Review" },
  { status: "done", label: "Done" },
];

export const KanbanBoard = ({
  projectId,
  selectedProjectId,
  onProjectChange,
  onCreateProject,
}: KanbanBoardProps) => {
  // Fetch tasks for the project with smart polling
  const { data: tasks, isLoading, error } = useProjectTasks(projectId);

  // Mutation for drag-and-drop position updates
  const updateTaskPosition = useUpdateTaskPosition(projectId);

  // Handler for task movement between columns
  const handleTaskMove = (taskId: string, newStatus: TaskStatus) => {
    // GOTCHA: Don't call mutation if already pending
    if (updateTaskPosition.isPending) {
      console.warn("Task position update already in progress");
      return;
    }

    // Find the task to get current status
    const task = tasks?.find((t) => t.id === taskId);
    if (!task) {
      console.error("Task not found:", taskId);
      return;
    }

    // GOTCHA: Don't call mutation if source and destination are same
    if (task.status === newStatus) {
      console.log("Task already in target status, skipping update");
      return;
    }

    // Calculate new position (append to end of column)
    const tasksInNewStatus = tasksByStatus[newStatus] || [];
    const newPosition = tasksInNewStatus.length;

    // Trigger mutation with optimistic update
    updateTaskPosition.mutate({
      taskId,
      status: newStatus,
      position: newPosition,
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading tasks...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="text-xl font-semibold mb-2">Error loading tasks</p>
          <p className="text-sm">{error instanceof Error ? error.message : "Unknown error"}</p>
        </div>
      </div>
    );
  }

  // Group tasks by status for column rendering
  const tasksByStatus = groupBy(tasks || [], "status");

  return (
    <div className="h-full p-6">
      {/* Board Header with Title and Theme Toggle */}
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

        {/* Right side: Theme Toggle ONLY */}
        <div className="flex items-center gap-4">
          <ThemeToggle />
        </div>
      </div>

      {/* Project Selector Section (replaces "Kanban Board" header) */}
      <div className="mb-6">
        <ProjectSelector
          selectedProjectId={selectedProjectId}
          onProjectChange={onProjectChange}
          onCreateProject={onCreateProject}
        />
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {tasks?.length || 0} tasks total
        </p>
      </div>

      {/* Kanban Columns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-[calc(100%-5rem)]">
        {COLUMNS.map(({ status, label }) => (
          <div key={status} className="flex flex-col">
            {/* Column label */}
            <div className="mb-2">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                {label}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                {tasksByStatus[status]?.length || 0} tasks
              </p>
            </div>

            {/* KanbanColumn with drop zone */}
            <KanbanColumn
              status={status}
              tasks={tasksByStatus[status] || []}
              onTaskMove={handleTaskMove}
            />
          </div>
        ))}
      </div>

      {/* Mutation pending indicator */}
      {updateTaskPosition.isPending && (
        <div className="fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span className="text-sm">Updating task...</span>
          </div>
        </div>
      )}
    </div>
  );
};
