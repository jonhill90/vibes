// Source: infra/archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts
// Lines: 1-220 (full file, key sections highlighted)
// Pattern: TanStack Query mutations with optimistic updates
// Extracted: 2025-10-10
// Relevance: 10/10 - Shows that NO CHANGES needed to mutation hooks (taskColor passes through)

/**
 * TanStack Query Mutation Pattern - OPTIMISTIC UPDATES WITH NANOID
 *
 * CRITICAL INSIGHT: You DON'T need to change these mutation hooks!
 * The backend flexible schema accepts new fields automatically.
 * TaskColor will pass through existing create/update mutations.
 *
 * This example shows:
 * 1. Query key factories
 * 2. Optimistic update pattern with createOptimisticEntity
 * 3. Rollback on error
 * 4. Replace optimistic with server data on success
 * 5. Query invalidation patterns
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

// KEY PATTERN #1: Query Keys Factory
// Each feature owns its query keys
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  detail: (id: string) => [...taskKeys.all, "detail", id] as const,
  byProject: (projectId: string) => ["projects", projectId, "tasks"] as const,
  counts: () => [...taskKeys.all, "counts"] as const,
};

// KEY PATTERN #2: Query Hook with Smart Polling
export function useProjectTasks(projectId: string | undefined, enabled = true) {
  const { refetchInterval } = useSmartPolling(2000); // 2s active polling

  return useQuery<Task[]>({
    queryKey: projectId ? taskKeys.byProject(projectId) : DISABLED_QUERY_KEY,
    queryFn: async () => {
      if (!projectId) throw new Error("No project ID");
      return taskService.getTasksByProject(projectId);
    },
    enabled: !!projectId && enabled,
    refetchInterval, // Smart interval based on page visibility/focus
    refetchOnWindowFocus: true,
    staleTime: STALE_TIMES.frequent,
  });
}

// KEY PATTERN #3: Create Mutation with Optimistic Updates
export function useCreateTask() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation<Task, Error, CreateTaskRequest, { previousTasks?: Task[]; optimisticId: string }>({
    mutationFn: (taskData: CreateTaskRequest) => taskService.createTask(taskData),

    // CRITICAL: onMutate runs BEFORE mutation
    onMutate: async (newTaskData) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(newTaskData.project_id) });

      // Snapshot for rollback
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(newTaskData.project_id));

      // KEY PATTERN: Create optimistic task with stable ID
      const optimisticTask = createOptimisticEntity<Task>({
        project_id: newTaskData.project_id,
        title: newTaskData.title,
        description: newTaskData.description || "",
        status: newTaskData.status ?? "todo",
        assignee: newTaskData.assignee ?? "User",
        feature: newTaskData.feature,
        task_order: newTaskData.task_order ?? 100,
        priority: newTaskData.priority ?? "medium",
        // CRITICAL: taskColor would be included here automatically!
        // taskColor: newTaskData.taskColor, // No need to add - spread includes all fields
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // Optimistically add to cache
      queryClient.setQueryData(taskKeys.byProject(newTaskData.project_id), (old: Task[] | undefined) => {
        if (!old) return [optimisticTask];
        return [...old, optimisticTask];
      });

      return { previousTasks, optimisticId: optimisticTask._localId };
    },

    // CRITICAL: onError rolls back optimistic update
    onError: (error, variables, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to create task:", error?.message, {
        project_id: variables?.project_id,
      });

      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(variables.project_id), context.previousTasks);
      }

      showToast(`Failed to create task: ${errorMessage}`, "error");
    },

    // CRITICAL: onSuccess replaces optimistic with server data
    onSuccess: (serverTask, variables, context) => {
      // Replace optimistic with server data
      queryClient.setQueryData(
        taskKeys.byProject(variables.project_id),
        (tasks: (Task & Partial<OptimisticEntity>)[] = []) => {
          const replaced = replaceOptimisticEntity(tasks, context?.optimisticId || "", serverTask);
          return removeDuplicateEntities(replaced);
        },
      );

      // Invalidate counts (new task affects counts)
      queryClient.invalidateQueries({
        queryKey: taskKeys.counts(),
      });

      showToast("Task created successfully", "success");
    },

    onSettled: (_data, _error, variables) => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(variables.project_id) });
    },
  });
}

// KEY PATTERN #4: Update Mutation with Optimistic Updates
export function useUpdateTask(projectId: string) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation<Task, Error, { taskId: string; updates: UpdateTaskRequest }, { previousTasks?: Task[] }>({
    mutationFn: ({ taskId, updates }: { taskId: string; updates: UpdateTaskRequest }) =>
      taskService.updateTask(taskId, updates),

    onMutate: async ({ taskId, updates }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

      // Snapshot for rollback
      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(projectId));

      // Optimistically update
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) => {
        if (!old) return old;
        // KEY PATTERN: Spread updates into existing task
        // taskColor would be included automatically in updates!
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

      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }

      showToast(`Failed to update task: ${errorMessage}`, "error");

      // Refetch on error to ensure consistency
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

// KEY PATTERN #5: Delete Mutation
export function useDeleteTask(projectId: string) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation<void, Error, string, { previousTasks?: Task[] }>({
    mutationFn: (taskId: string) => taskService.deleteTask(taskId),

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

      const previousTasks = queryClient.getQueryData<Task[]>(taskKeys.byProject(projectId));

      // Optimistically remove
      queryClient.setQueryData<Task[]>(taskKeys.byProject(projectId), (old) => {
        if (!old) return old;
        return old.filter((task) => task.id !== taskId);
      });

      return { previousTasks };
    },

    onError: (error, taskId, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to delete task:", error?.message, { taskId });

      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.byProject(projectId), context.previousTasks);
      }

      showToast(`Failed to delete task: ${errorMessage}`, "error");
    },

    onSuccess: () => {
      showToast("Task deleted successfully", "success");
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.counts() });
      queryClient.invalidateQueries({ queryKey: taskKeys.byProject(projectId) });
    },
  });
}

// CRITICAL INSIGHTS FOR TASKCOLOR:
//
// 1. NO CHANGES NEEDED TO THESE HOOKS:
//    - Backend accepts taskColor automatically
//    - Flexible JSON schema in database
//    - Pydantic models allow extra fields
//    - Just add to type definitions!
//
// 2. How TaskColor Will Pass Through:
//    - Add taskColor?: string to Task type
//    - Add to CreateTaskRequest type
//    - Add to UpdateTaskRequest type
//    - Mutations automatically include it
//
// 3. Optimistic Update Behavior:
//    - createOptimisticEntity includes all fields
//    - No need to manually add taskColor
//    - Spread operator handles it
//
// 4. Server Response:
//    - Server returns taskColor in response
//    - onSuccess merges server data
//    - Cache updated with real data
//
// 5. Validation:
//    - No backend validation for optional color
//    - Frontend validates hex format
//    - Invalid colors simply won't display
//
// WHAT YOU ACTUALLY NEED TO DO:
//
// 1. Type Definitions (task.ts):
//    ```typescript
//    export interface Task {
//      // ... existing fields ...
//      taskColor?: string; // NEW: hex color like "#ef4444"
//    }
//
//    export interface CreateTaskRequest {
//      // ... existing fields ...
//      taskColor?: string; // NEW
//    }
//
//    export interface UpdateTaskRequest {
//      // ... existing fields ...
//      taskColor?: string; // NEW
//    }
//    ```
//
// 2. That's It!
//    - No changes to useTaskQueries.ts
//    - No changes to taskService.ts
//    - No changes to backend API
//    - No database migration
//
// 3. Usage in Components:
//    ```typescript
//    // In TaskEditModal
//    setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null));
//
//    // Save automatically includes taskColor
//    saveTask(localTask); // taskColor is in the payload!
//    ```
//
// 4. Testing:
//    - Test optimistic creation with taskColor
//    - Test optimistic update of taskColor
//    - Test clearing taskColor (set to undefined)
//    - Verify rollback on error
