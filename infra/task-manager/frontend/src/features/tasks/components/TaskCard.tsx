import { useDrag } from "react-dnd";
import type { Task } from "../types/task";
import { ItemTypes, type TaskDragItem } from "./KanbanColumn";

interface TaskCardProps {
  task: Task;
  onUpdate?: (taskId: string, updates: Partial<Task>) => void;
}

/**
 * TaskCard - Draggable task card component
 * Implements react-dnd drag functionality for Kanban board
 */
export const TaskCard = ({ task, onUpdate }: TaskCardProps) => {
  // CRITICAL: Explicit type parameters for useDrag (Gotcha #9)
  // useDrag<DragItem, DropResult, CollectedProps>
  const [{ isDragging }, drag] = useDrag<TaskDragItem, void, { isDragging: boolean }>({
    type: ItemTypes.TASK,
    item: { id: task.id, status: task.status },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  // Priority badge color mapping
  const getPriorityColor = (priority: Task["priority"]) => {
    switch (priority) {
      case "urgent":
        return "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400";
      case "high":
        return "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400";
      case "medium":
        return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400";
      case "low":
        return "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400";
      default:
        return "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400";
    }
  };

  return (
    <div
      ref={drag}
      className="p-4 bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 cursor-move transition-opacity duration-200"
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      <h4 className="font-medium text-gray-900 dark:text-gray-100">{task.title}</h4>
      {task.description && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{task.description}</p>
      )}
      <div className="mt-2 flex items-center gap-2">
        <span className={`text-xs px-2 py-1 rounded font-medium ${getPriorityColor(task.priority)}`}>
          {task.priority}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-500">{task.assignee}</span>
      </div>
    </div>
  );
};
