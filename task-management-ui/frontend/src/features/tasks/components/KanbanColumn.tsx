import { useRef } from "react";
import { useDrop } from "react-dnd";
import type { Task, TaskStatus } from "../types/task";
import { TaskCard } from "./TaskCard";

// ItemTypes constant - used across drag-and-drop components
export const ItemTypes = {
  TASK: "task",
} as const;

// TaskDragItem interface - data transferred during drag operation
export interface TaskDragItem {
  id: string;
  status: TaskStatus;
}

interface KanbanColumnProps {
  status: TaskStatus;
  tasks: Task[];
  onTaskMove: (taskId: string, newStatus: TaskStatus) => void;
}

export const KanbanColumn = ({ status, tasks, onTaskMove }: KanbanColumnProps) => {
  const ref = useRef<HTMLDivElement>(null);

  // CRITICAL: Explicit type parameters for useDrop (Gotcha #9)
  // useDrop<DragItem, DropResult, CollectedProps>
  const [{ isOver }, drop] = useDrop<TaskDragItem, void, { isOver: boolean }>({
    accept: ItemTypes.TASK, // Use constant, not magic string
    drop: (item: TaskDragItem) => {
      // Only trigger move if status changed
      if (item.status !== status) {
        onTaskMove(item.id, status);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(), // Visual feedback state
    }),
  });

  // Attach drop ref to column container
  drop(ref);

  return (
    <div
      ref={ref}
      className={`
        flex flex-col h-full min-h-[400px] p-4 rounded-lg
        transition-all duration-200
        ${
          isOver
            ? "bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-400 dark:border-blue-500"
            : "bg-gray-50 dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700"
        }
      `}
    >
      {/* Column Header */}
      <h3 className="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-300 capitalize">
        {status}
      </h3>

      {/* Tasks Container */}
      <div className="space-y-2 flex-1">
        {tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-400 dark:text-gray-600 text-sm">
            No tasks
          </div>
        ) : (
          tasks.map((task) => <TaskCard key={task.id} task={task} />)
        )}
      </div>
    </div>
  );
};
