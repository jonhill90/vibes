/**
 * Task Query Hooks - TanStack Query v5 Pattern
 *
 * PURPOSE: React hooks for task CRUD with optimistic updates
 *
 * KEY PATTERNS:
 * 1. Query key factories for cache management
 * 2. Smart polling with visibility awareness
 * 3. Optimistic updates with rollback on error
 * 4. Proper invalidation after mutations
 *
 * GOTCHAS ADDRESSED:
 * - Gotcha #4: ALWAYS await queryClient.cancelQueries() in onMutate
 * - Use _localId for stable optimistic entity references
 * - Check isPending before triggering mutations (via UI)
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createOptimisticEntity,
  type OptimisticEntity,
  removeDuplicateEntities,
  replaceOptimisticEntity,
} from "../../shared/utils/optimistic";
import { DISABLED_QUERY_KEY, STALE_TIMES } from "../../shared/config/queryPatterns";
import { useSmartPolling } from "../../shared/hooks/useSmartPolling";
import { taskService } from "../services/taskService";
import type { Task, TaskCreate, TaskUpdate } from "../types/task";

// PATTERN: Query keys factory for tasks
// Hierarchical structure matches API endpoints
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const, // For /api/tasks
  detail: (id: string) => [...taskKeys.all, "detail", id] as const, // For /api/tasks/{id}
  byProject: (projectId: string) => ["projects", projectId, "tasks"] as const, // For project-scoped tasks
};

/**
 * useProjectTasks - Query hook for tasks scoped to a project
 *
 * PATTERN: Smart polling for real-time updates
 * - Polls every 2 seconds when tab is visible
 * - Pauses polling when tab is hidden (useSmartPolling)
 * - Refetches when window regains focus (cheap with ETags)
 *
 * @param projectId - Project ID to filter tasks
 * @param enabled - Whether to enable the query (default: true)
 * @returns Query result with tasks, isLoading, error states
 */
export function useProjectTasks(projectId: string | undefined, enabled = true) {
  const { refetchInterval } = useSmartPolling(2000); // 2s active polling for real-time updates

  return useQuery<Task[]>({
    queryKey: projectId ? taskKeys.byProject(projectId) : DISABLED_QUERY_KEY,
    queryFn: async () => {
      if (!projectId) throw new Error("No project ID");
      return taskService.getTasksByProject(projectId);
    },
    enabled: !!projectId && enabled,
    refetchInterval, // Smart interval based on page visibility/focus
    refetchOnWindowFocus: true, // Refetch when tab gains focus (ETag makes this cheap)
    staleTime: STALE_TIMES.frequent, // 5s - high-change data
  });
}

/**
 * useTask - Query hook for a single task
 *
 * @param taskId - Task ID
 * @param enabled - Whether to enable the query (default: true)
 * @returns Query result with task, isLoading, error states
 */
export function useTask(taskId: string | undefined, enabled = true) {
  return useQuery<Task>({
    queryKey: taskId ? taskKeys.detail(taskId) : DISABLED_QUERY_KEY,
    queryFn: async () => {
      if (!taskId) throw new Error("No task ID");
      return taskService.getTask(taskId);
    },
    enabled: !!taskId && enabled,
    staleTime: STALE_TIMES.normal, // 30s - medium-change data
  });
}

/**
 * useCreateTask - Mutation hook for creating tasks
 *
 * PATTERN: Optimistic updates with rollback on error
 *
 * FLOW:
 * 1. onMutate: Cancel in-flight queries, snapshot current state, add optimistic task
 * 2. mutationFn: Call API to create task
 * 3. onSuccess: Replace optimistic task with server data
 * 4. onError: Rollback to previous state
 * 5. onSettled: Invalidate queries to refetch
 *
 * CRITICAL GOTCHAS:
 * - MUST await cancelQueries to prevent race conditions (Gotcha #4)
 * - Use _localId for stable reference when replacing optimistic entity
 * - Snapshot previous state for rollback on error
 */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation<Task, Error, TaskCreate, { previousTasks?: Task[]; optimisticId: string }>({
    mutationFn: (taskData: TaskCreate) => taskService.createTask(taskData),

    // CRITICAL: onMutate for optimistic updates
    onMutate: async (newTaskData) => {
      // GOTCHA #4: Cancel any outgoing refetches to avoid race conditions
      // Without this, a background refetch could overwrite our optimistic update
      if (newTaskData.project_id) {
        await queryClient.cancelQueries({ queryKey: taskKeys.byProject(newTaskData.project_id) });
      }

      // Snapshot the previous value for rollback
      const previousTasks = newTaskData.project_id
        ? queryClient.getQueryData<Task[]>(taskKeys.byProject(newTaskData.project_id))
        : undefined;

      // Create optimistic task with stable ID (nanoid)
      // PATTERN: Use createOptimisticEntity for _localId and _optimistic flag
      const optimisticTask = createOptimisticEntity<Task>({
        project_id: newTaskData.project_id || null,
        parent_task_id: null,
        title: newTaskData.title,
        description: newTaskData.description || null,
        status: newTaskData.status ?? "todo",
        assignee: newTaskData.assignee ?? "Unassigned",
        priority: newTaskData.priority ?? "medium",
        position: newTaskData.position ?? 0,
        id: `temp-${Date.now()}`, // Temporary ID (will be replaced by server)
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // Optimistically add the new task to cache
      if (newTaskData.project_id) {
        queryClient.setQueryData(taskKeys.byProject(newTaskData.project_id), (old: Task[] | undefined) => {
          if (!old) return [optimisticTask];
          return [...old, optimisticTask];
        });
      }

      // Return context for onError and onSuccess
      return { previousTasks, optimisticId: optimisticTask._localId };
    },

    // PATTERN: Rollback on error
    onError: (error, variables, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to create task:", errorMessage, {
        project_id: variables?.project_id,
      });

      // Rollback to previous state
      if (context?.previousTasks && variables.project_id) {
        queryClient.setQueryData(taskKeys.byProject(variables.project_id), context.previousTasks);
      }

      // TODO: Show toast notification when useToast is available
      // showToast(`Failed to create task: ${errorMessage}`, "error");
    },

    // PATTERN: Replace optimistic with server data
    onSuccess: (serverTask, variables, context) => {
      if (variables.project_id) {
        queryClient.setQueryData(
          taskKeys.byProject(variables.project_id),
          (tasks: (Task & Partial<OptimisticEntity>)[] = []) => {
            const replaced = replaceOptimisticEntity(tasks, context?.optimisticId || "", serverTask);
            return removeDuplicateEntities(replaced); // Dedup by ID in case server already pushed
          },
        );
      }

      // TODO: Show success toast when useToast is available
      // showToast("Task created successfully", "success");
    },

    // PATTERN: Always refetch to ensure consistency
    onSettled: (_data, _error, variables) => {
      if (variables.project_id) {
        queryClient.invalidateQueries({ queryKey: taskKeys.byProject(variables.project_id) });
      }
    },
  });
}

/**
 * useUpdateTask - Mutation hook for updating tasks
 *
 * PATTERN: Same optimistic update pattern as create
 *
 * @param projectId - Project ID for cache invalidation
 */
export function useUpdateTask(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<Task, Error, { taskId: string; updates: TaskUpdate }, { previousTasks?: Task[] }>({
    mutationFn: ({ taskId, updates }: { taskId: string; updates: TaskUpdate }) =>
      taskService.updateTask(taskId, updates),

    onMutate: async ({ taskId, updates }) => {
      // Cancel in-flight queries
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

      // Snapshot previous state
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(projectId));

      // Optimistically update
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) => {
        if (!old) return old;
        return old.map((task) => (task.id === taskId ? { ...task, ...updates } : task));
      });

      return { previousTasks };
    },

    onError: (error, variables, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to update task:", errorMessage, {
        taskId: variables?.taskId,
        changedFields: Object.keys(variables?.updates ?? {}),
      });

      // Rollback
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }

      // TODO: Toast notification
      // showToast(`Failed to update task: ${errorMessage}`, "error");

      // Refetch on error to get correct state
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(projectId) });
    },

    onSuccess: (serverTask, { updates }) => {
      // Merge server response to keep timestamps and computed fields in sync
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) =>
        old ? old.map((t) => (t.id === serverTask.id ? serverTask : t)) : old,
      );

      // Show status change feedback
      if (updates.status) {
        // TODO: Toast notification
        // showToast(`Task moved to ${updates.status}`, "success");
      }
    },
  });
}

/**
 * useUpdateTaskPosition - Mutation hook for drag-and-drop position updates
 *
 * PATTERN: Dedicated mutation for atomic position updates
 * - Uses dedicated backend endpoint: PATCH /api/tasks/{id}/position
 * - Backend handles position reordering atomically
 *
 * @param projectId - Project ID for cache invalidation
 */
export function useUpdateTaskPosition(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<
    Task,
    Error,
    { taskId: string; status: Task["status"]; position: number },
    { previousTasks?: Task[] }
  >({
    mutationFn: ({ taskId, status, position }) => taskService.updateTaskPosition(taskId, status, position),

    onMutate: async ({ taskId, status, position }) => {
      // Cancel in-flight queries
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

      // Snapshot previous state
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(projectId));

      // Optimistically update position
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) => {
        if (!old) return old;
        return old.map((task) => (task.id === taskId ? { ...task, status, position } : task));
      });

      return { previousTasks };
    },

    onError: (error, variables, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to update task position:", errorMessage, {
        taskId: variables?.taskId,
        status: variables?.status,
        position: variables?.position,
      });

      // Rollback
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }

      // TODO: Toast notification
      // showToast(`Failed to move task: ${errorMessage}`, "error");
    },

    onSuccess: (serverTask) => {
      // Replace with server data to ensure consistency
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) =>
        old ? old.map((t) => (t.id === serverTask.id ? serverTask : t)) : old,
      );
    },

    onSettled: () => {
      // Always refetch to ensure correct ordering
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(projectId) });
    },
  });
}

/**
 * useDeleteTask - Mutation hook for deleting tasks
 *
 * PATTERN: Optimistic removal with rollback
 *
 * @param projectId - Project ID for cache invalidation
 */
export function useDeleteTask(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string, { previousTasks?: Task[] }>({
    mutationFn: (taskId: string) => taskService.deleteTask(taskId),

    onMutate: async (taskId) => {
      // Cancel in-flight queries
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

      // Snapshot previous state
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(projectId));

      // Optimistically remove the task
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) => {
        if (!old) return old;
        return old.filter((task) => task.id !== taskId);
      });

      return { previousTasks };
    },

    onError: (error, taskId, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to delete task:", errorMessage, { taskId });

      // Rollback
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }

      // TODO: Toast notification
      // showToast(`Failed to delete task: ${errorMessage}`, "error");
    },

    onSuccess: () => {
      // TODO: Toast notification
      // showToast("Task deleted successfully", "success");
    },

    onSettled: () => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(projectId) });
    },
  });
}

/**
 * USAGE EXAMPLE:
 *
 * ```tsx
 * // In a component
 * function TaskList({ projectId }: { projectId: string }) {
 *   const { data: tasks, isLoading } = useProjectTasks(projectId);
 *   const createTask = useCreateTask();
 *
 *   const handleCreate = () => {
 *     createTask.mutate({
 *       project_id: projectId,
 *       title: "New task",
 *       status: "todo",
 *     });
 *   };
 *
 *   if (isLoading) return <div>Loading...</div>;
 *
 *   return (
 *     <div>
 *       {tasks?.map(task => (
 *         <div key={task.id}>{task.title}</div>
 *       ))}
 *       <button onClick={handleCreate}>Add Task</button>
 *     </div>
 *   );
 * }
 * ```
 */
