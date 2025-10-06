// Source: /Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/components/KanbanColumn.tsx
// Pattern: react-dnd drag-and-drop with Kanban column
// Extracted: 2025-10-06
// Relevance: 10/10 - Core Kanban UI pattern

/**
 * KanbanColumn Component - Drag-and-Drop Column Pattern
 *
 * KEY PATTERNS TO MIMIC:
 * 1. useDrop hook for column-level drop zones
 * 2. Visual feedback during drag operations (isOver state)
 * 3. Glassmorphism styling with backdrop-blur
 * 4. Status-based color theming
 * 5. TaskCard integration with reordering support
 */

import { useRef } from "react";
import { useDrop } from "react-dnd";
import { cn } from "../../../ui/primitives/styles";
import type { Task } from "../types";
import { getColumnColor, getColumnGlow, ItemTypes } from "../utils/task-styles";
import { TaskCard } from "./TaskCard";

interface KanbanColumnProps {
  status: Task["status"];
  title: string;
  tasks: Task[];
  projectId: string;
  onTaskMove: (taskId: string, newStatus: Task["status"]) => void;
  onTaskReorder: (taskId: string, targetIndex: number, status: Task["status"]) => void;
  onTaskEdit?: (task: Task) => void;
  onTaskDelete?: (task: Task) => void;
  hoveredTaskId: string | null;
  onTaskHover: (taskId: string | null) => void;
}

export const KanbanColumn = ({
  status,
  title,
  tasks,
  projectId,
  onTaskMove,
  onTaskReorder,
  onTaskEdit,
  onTaskDelete,
  hoveredTaskId,
  onTaskHover,
}: KanbanColumnProps) => {
  const ref = useRef<HTMLDivElement>(null);

  // PATTERN: Column-level drop zone with status transition
  const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.TASK, // Only accept TASK drag items
    drop: (item: { id: string; status: Task["status"] }) => {
      // Only trigger move if status changes
      if (item.status !== status) {
        onTaskMove(item.id, status);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(), // Track hover state for visual feedback
    }),
  });

  drop(ref); // Attach drop ref to column

  return (
    <div
      ref={ref}
      className={cn(
        "flex flex-col h-full",
        // Base glassmorphism
        "bg-gradient-to-b from-white/20 to-transparent dark:from-black/30 dark:to-transparent",
        "backdrop-blur-sm",
        "transition-all duration-200",
        // Hover state visual feedback
        isOver && "bg-gradient-to-b from-cyan-500/5 to-purple-500/5 dark:from-cyan-400/10 dark:to-purple-400/10",
        isOver && "border-t-2 border-t-cyan-400/50 dark:border-t-cyan-400/70",
        isOver &&
          "shadow-[inset_0_2px_20px_rgba(34,211,238,0.15)] dark:shadow-[inset_0_2px_30px_rgba(34,211,238,0.25)]",
        isOver && "backdrop-blur-md",
      )}
    >
      {/* Column Header with Glassmorphism */}
      <div
        className={cn(
          "text-center py-3 sticky top-0 z-10",
          "bg-gradient-to-b from-white/80 to-white/60 dark:from-black/80 dark:to-black/60",
          "backdrop-blur-md",
          "border-b border-gray-200/50 dark:border-gray-700/50",
          "relative",
        )}
      >
        <h3 className={cn("font-mono text-sm font-medium", getColumnColor(status))}>{title}</h3>
        {/* Column header glow effect - Tron aesthetic */}
        <div
          className={cn("absolute bottom-0 left-[15%] right-[15%] w-[70%] mx-auto h-[1px]", getColumnGlow(status))}
        />
      </div>

      {/* Tasks Container */}
      <div className="px-2 flex-1 overflow-y-auto space-y-2 py-3 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
        {tasks.length === 0 ? (
          <div className={cn("text-center py-8 text-gray-400 dark:text-gray-600 text-sm", "opacity-60")}>No tasks</div>
        ) : (
          tasks.map((task, index) => (
            <TaskCard
              key={task.id}
              task={task}
              index={index}
              projectId={projectId}
              onTaskReorder={onTaskReorder}
              onEdit={onTaskEdit}
              onDelete={onTaskDelete}
              hoveredTaskId={hoveredTaskId}
              onTaskHover={onTaskHover}
            />
          ))
        )}
      </div>
    </div>
  );
};

/**
 * WHAT TO MIMIC:
 *
 * 1. Drop Zone Setup:
 *    - Use useDrop with accept: ItemTypes.TASK
 *    - Collect isOver state for visual feedback
 *    - Only trigger onTaskMove if status changes
 *
 * 2. Visual Feedback:
 *    - Apply different styles when isOver is true
 *    - Use backdrop-blur for glassmorphism
 *    - Status-based colors via utility functions
 *
 * 3. Task Rendering:
 *    - Map tasks with index for reordering
 *    - Pass hover state management to children
 *    - Support edit and delete callbacks
 *
 * WHAT TO ADAPT:
 *
 * - Color schemes: Adjust getColumnColor/getColumnGlow for your theme
 * - Task status values: Update ItemTypes and status type
 * - Column layout: Modify grid/flex for your design
 *
 * WHAT TO SKIP:
 *
 * - Archon-specific styling utilities (getColumnGlow)
 * - Project-specific task card features
 * - Specific scrollbar styling (optional)
 */
