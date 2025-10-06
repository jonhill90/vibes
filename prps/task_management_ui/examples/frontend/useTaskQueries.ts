// Source: /Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts
// Pattern: TanStack Query hooks with optimistic updates
// Extracted: 2025-10-06
// Relevance: 10/10 - Core data fetching pattern

/**
 * Task Query Hooks - TanStack Query v5 Pattern
 *
 * KEY PATTERNS TO MIMIC:
 * 1. Query key factories for cache management
 * 2. Smart polling with visibility awareness
 * 3. Optimistic updates with rollback on error
 * 4. Dual nature: global and project-scoped tasks
 * 5. Proper invalidation after mutations
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createOptimisticEntity,
  type OptimisticEntity,
  removeDuplicateEntities,
  replaceOptimisticEntity,
} from "@/features/shared/utils/optimistic";
import { DISABLED_QUERY_KEY, STALE_TIMES } from "../../../shared/config/queryPatterns";
import { useSmartPolling } from "../../../shared/hooks";
import { useToast } from "../../../shared/hooks/useToast";
import { taskService } from "../services";
import type { CreateTaskRequest, Task, UpdateTaskRequest } from "../types";

// PATTERN: Query keys factory for tasks - supports dual backend nature
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const, // For /api/tasks
  detail: (id: string) => [...taskKeys.all, "detail", id] as const, // For /api/tasks/{id}
  byProject: (projectId: string) => ["projects", projectId, "tasks"] as const, // For /api/projects/{id}/tasks
  counts: () => [...taskKeys.all, "counts"] as const, // For /api/projects/task-counts
};

// PATTERN: Project-scoped task query with smart polling
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
    staleTime: STALE_TIMES.frequent,
  });
}

// PATTERN: Aggregated query for all projects
export function useTaskCounts() {
  const { refetchInterval: countsRefetchInterval } = useSmartPolling(10_000); // 10s bg polling
  return useQuery<Awaited<ReturnType<typeof taskService.getTaskCountsForAllProjects>>>({
    queryKey: taskKeys.counts(),
    queryFn: () => taskService.getTaskCountsForAllProjects(),
    refetchInterval: countsRefetchInterval,
    staleTime: STALE_TIMES.frequent,
  });
}

// PATTERN: Create mutation with optimistic updates
export function useCreateTask() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation<Task, Error, CreateTaskRequest, { previousTasks?: Task[]; optimisticId: string }>({
    mutationFn: (taskData: CreateTaskRequest) => taskService.createTask(taskData),

    // CRITICAL: onMutate for optimistic updates
    onMutate: async (newTaskData) => {
      // Cancel any outgoing refetches to avoid race conditions
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(newTaskData.project_id) });

      // Snapshot the previous value for rollback
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(newTaskData.project_id));

      // Create optimistic task with stable ID (nanoid)
      const optimisticTask = createOptimisticEntity<Task>({
        project_id: newTaskData.project_id,
        title: newTaskData.title,
        description: newTaskData.description || "",
        status: newTaskData.status ?? "todo",
        assignee: newTaskData.assignee ?? "User",
        feature: newTaskData.feature,
        task_order: newTaskData.task_order ?? 100,
        priority: newTaskData.priority ?? "medium",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // Optimistically add the new task
      queryClient.setQueryData(taskKeys.byProject(newTaskData.project_id), (old: Task[] | undefined) => {
        if (!old) return [optimisticTask];
        return [...old, optimisticTask];
      });

      return { previousTasks, optimisticId: optimisticTask._localId };
    },

    // PATTERN: Rollback on error
    onError: (error, variables, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to create task:", error?.message, {
        project_id: variables?.project_id,
      });

      // Rollback to previous state
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(variables.project_id), context.previousTasks);
      }

      showToast(`Failed to create task: ${errorMessage}`, "error");
    },

    // PATTERN: Replace optimistic with server data
    onSuccess: (serverTask, variables, context) => {
      queryClient.setQueryData(
        taskKeys.byProject(variables.project_id),
        (tasks: (Task & Partial<OptimisticEntity>)[] = []) => {
          const replaced = replaceOptimisticEntity(tasks, context?.optimisticId || "", serverTask);
          return removeDuplicateEntities(replaced); // Dedup by ID
        },
      );

      // Invalidate counts since we have a new task
      queryClient.invalidateQueries({
        queryKey: taskKeys.counts(),
      });

      showToast("Task created successfully", "success");
    },

    // PATTERN: Always refetch to ensure consistency
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(variables.project_id) });
    },
  });
}

// PATTERN: Update mutation with optimistic updates
export function useUpdateTask(projectId: string) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation<Task, Error, { taskId: string; updates: UpdateTaskRequest }, { previousTasks?: Task[] }>({
    mutationFn: ({ taskId, updates }: { taskId: string; updates: UpdateTaskRequest }) =>
      taskService.updateTask(taskId, updates),

    onMutate: async ({ taskId, updates }) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

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
      console.error("Failed to update task:", error?.message, {
        taskId: variables?.taskId,
        changedFields: Object.keys(variables?.updates ?? {}),
      });

      // Rollback
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }

      showToast(`Failed to update task: ${errorMessage}`, "error");

      // Refetch on error
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(projectId) });

      // Only invalidate counts if status was changed
      if (variables.updates?.status) {
        queryClient.invalidateQueries({ queryKey: taskKeys.counts() });
      }
    },

    onSuccess: (data, { updates }) => {
      // Merge server response to keep timestamps and computed fields in sync
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) =>
        old ? old.map((t) => (t.id === data.id ? data : t)) : old,
      );

      // Only invalidate counts if status changed
      if (updates.status) {
        queryClient.invalidateQueries({ queryKey: taskKeys.counts() });
        showToast(`Task moved to ${updates.status}`, "success");
      }
    },
  });
}

// PATTERN: Delete mutation with optimistic removal
export function useDeleteTask(projectId: string) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation<void, Error, string, { previousTasks?: Task[] }>({
    mutationFn: (taskId: string) => taskService.deleteTask(taskId),

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

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
      console.error("Failed to delete task:", error?.message, { taskId });

      // Rollback
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }

      showToast(`Failed to delete task: ${errorMessage}`, "error");
    },

    onSuccess: () => {
      showToast("Task deleted successfully", "success");
    },

    onSettled: () => {
      // Always refetch counts after deletion
      queryClient.invalidateQueries({ queryKey: taskKeys.counts() });
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(projectId) });
    },
  });
}

/**
 * WHAT TO MIMIC:
 *
 * 1. Query Key Factory:
 *    - Hierarchical structure: all → lists/detail/byProject
 *    - Type-safe with const assertions
 *    - Match backend API structure
 *
 * 2. Smart Polling:
 *    - Use useSmartPolling hook for visibility-aware intervals
 *    - Different intervals for different data types
 *    - refetchOnWindowFocus for fresh data on tab switch
 *
 * 3. Optimistic Updates:
 *    - createOptimisticEntity for stable temporary IDs
 *    - Cancel in-flight queries before mutating
 *    - Snapshot previous state for rollback
 *    - Replace optimistic with server data on success
 *
 * 4. Error Handling:
 *    - Rollback to previous state on error
 *    - Show user-friendly toast messages
 *    - Log errors with context for debugging
 *
 * 5. Cache Invalidation:
 *    - Invalidate related queries (counts) after mutations
 *    - Use onSettled for guaranteed refetch
 *    - Selective invalidation based on what changed
 *
 * WHAT TO ADAPT:
 *
 * - Query keys: Adjust to match your API structure
 * - Polling intervals: Tune for your real-time needs
 * - Optimistic entity shape: Match your Task type
 * - Service methods: Point to your API layer
 *
 * WHAT TO SKIP:
 *
 * - Archon-specific utility imports
 * - Project-specific toast styling
 * - Dual nature (global/scoped) if not needed
 */
