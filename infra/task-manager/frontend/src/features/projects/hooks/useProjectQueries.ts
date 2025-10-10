/**
 * Project Query Hooks - TanStack Query v5 Pattern
 *
 * PURPOSE: React hooks for project CRUD with optimistic updates
 *
 * KEY PATTERNS:
 * 1. Query key factories for cache management
 * 2. Smart polling with visibility awareness
 * 3. Conditional queries with DISABLED_QUERY_KEY
 * 4. Proper staleTime configuration
 *
 * TASK 2 STATUS: Query keys and list query only (mutations in Task 3)
 *
 * GOTCHAS ADDRESSED:
 * - Gotcha #5: Query keys follow hierarchical structure
 * - Gotcha #11: Smart polling reduces request volume by ~50%
 * - Use STALE_TIMES.normal (30s) for projects (medium-change data)
 */

import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { DISABLED_QUERY_KEY, STALE_TIMES } from "../../shared/config/queryPatterns";
import { useSmartPolling } from "../../shared/hooks/useSmartPolling";
import {
  createOptimisticEntity,
  type OptimisticEntity,
  removeDuplicateEntities,
  replaceOptimisticEntity,
} from "../../shared/utils/optimistic";
import { projectService } from "../services/projectService";
import type { Project, ProjectCreate } from "../types/project";

// PATTERN: Query keys factory for projects
// Hierarchical structure matches API endpoints
export const projectKeys = {
  all: ["projects"] as const,
  lists: () => [...projectKeys.all, "list"] as const, // For /api/projects
  detail: (id: string) => [...projectKeys.all, "detail", id] as const, // For /api/projects/{id}
};

/**
 * useProjects - Query hook for all projects
 *
 * PATTERN: Smart polling for real-time updates
 * - Polls every 30 seconds when tab is visible (conservative for projects)
 * - Pauses polling when tab is hidden (useSmartPolling)
 * - Refetches when window regains focus (cheap with ETags)
 *
 * @returns Query result with projects, isLoading, error states
 */
export function useProjects() {
  const { refetchInterval } = useSmartPolling(30000); // 30s active polling for project list

  return useQuery<Project[]>({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    refetchInterval, // Smart interval based on page visibility/focus
    refetchOnWindowFocus: true, // Refetch when tab gains focus (ETag makes this cheap)
    staleTime: STALE_TIMES.normal, // 30s - medium-change data
  });
}

/**
 * useProject - Query hook for a single project
 *
 * PATTERN: Conditional query - only runs when id is provided
 * Uses DISABLED_QUERY_KEY when id is undefined to prevent invalid queries
 *
 * @param id - Project ID (optional)
 * @param enabled - Whether to enable the query (default: true)
 * @returns Query result with project, isLoading, error states
 */
export function useProject(id: string | undefined, enabled = true) {
  return useQuery<Project>({
    queryKey: id ? projectKeys.detail(id) : DISABLED_QUERY_KEY,
    queryFn: async () => {
      if (!id) throw new Error("No project ID");
      return projectService.getProject(id);
    },
    enabled: !!id && enabled,
    staleTime: STALE_TIMES.normal, // 30s - medium-change data
  });
}

/**
 * useCreateProject - Mutation hook for creating projects
 *
 * PATTERN: Optimistic updates with rollback on error, race condition prevention
 *
 * FLOW:
 * 1. onMutate: Cancel in-flight queries, snapshot current state, add optimistic project
 * 2. mutationFn: Call API to create project
 * 3. onSuccess: Replace optimistic project with server data
 * 4. onError: Rollback to previous state
 * 5. onSettled: Invalidate queries to refetch (only if last mutation)
 *
 * CRITICAL GOTCHAS:
 * - MUST await cancelQueries to prevent race conditions (Gotcha #1)
 * - Use _localId for stable reference when replacing optimistic entity
 * - Snapshot previous state for rollback on error
 * - Check isMutating to prevent concurrent mutation issues (Gotcha #2)
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation<Project, Error, ProjectCreate, { previousProjects?: Project[]; optimisticId: string }>({
    mutationKey: ["createProject"], // CRITICAL: enables tracking concurrent mutations
    mutationFn: (projectData: ProjectCreate) => projectService.createProject(projectData),

    // CRITICAL: onMutate for optimistic updates
    onMutate: async (newProjectData) => {
      // GOTCHA #1: Cancel any outgoing refetches to avoid race conditions
      // Without this, a background refetch could overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      // Snapshot the previous value for rollback
      const previousProjects = queryClient.getQueryData<Project[]>(projectKeys.lists());

      // Create optimistic project with stable ID (nanoid)
      // PATTERN: Use createOptimisticEntity for _localId and _optimistic flag
      const optimisticProject = createOptimisticEntity<Project>({
        name: newProjectData.name,
        description: newProjectData.description || null,
        id: `temp-${Date.now()}`, // Temporary ID (will be replaced by server)
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // Optimistically add the new project to cache
      queryClient.setQueryData(projectKeys.lists(), (old: Project[] | undefined) => {
        if (!old) return [optimisticProject];
        return [optimisticProject, ...old]; // Add new project at the beginning
      });

      // Return context for onError and onSuccess
      return { previousProjects, optimisticId: optimisticProject._localId };
    },

    // PATTERN: Rollback on error
    onError: (error, variables, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to create project:", errorMessage, {
        name: variables?.name,
      });

      // Rollback to previous state
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }

      // TODO: Show toast notification when useToast is available
      // showToast(`Failed to create project: ${errorMessage}`, "error");
    },

    // PATTERN: Replace optimistic with server data
    onSuccess: (serverProject, variables, context) => {
      queryClient.setQueryData(
        projectKeys.lists(),
        (projects: (Project & Partial<OptimisticEntity>)[] = []) => {
          const replaced = replaceOptimisticEntity(projects, context?.optimisticId || "", serverProject);
          return removeDuplicateEntities(replaced); // Dedup by ID in case server already pushed
        },
      );

      // TODO: Show success toast when useToast is available
      // showToast("Project created successfully", "success");
    },

    // PATTERN: Only invalidate if last mutation (prevents concurrent mutation issues)
    // GOTCHA #2: Check isMutating to prevent race conditions from concurrent creates
    onSettled: () => {
      // Check if other mutations are still running
      const mutationCount = queryClient.isMutating({ mutationKey: ["createProject"] });
      if (mutationCount === 1) {
        // This is the last mutation, safe to invalidate
        queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      }
    },
  });
}

/**
 * useDeleteProject - Mutation hook for deleting projects
 *
 * PATTERN: Optimistic updates with rollback on error
 *
 * FLOW:
 * 1. onMutate: Cancel in-flight queries, snapshot current state, remove project optimistically
 * 2. mutationFn: Call API to delete project
 * 3. onError: Rollback to previous state
 * 4. onSettled: Invalidate queries to refetch (only if last mutation)
 *
 * CRITICAL GOTCHAS:
 * - MUST await cancelQueries to prevent race conditions (Gotcha #1)
 * - Snapshot previous state for rollback on error
 * - Check isMutating to prevent concurrent mutation issues (Gotcha #2)
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string, { previousProjects?: Project[] }>({
    mutationKey: ["deleteProject"], // CRITICAL: enables tracking concurrent mutations
    mutationFn: (projectId: string) => projectService.deleteProject(projectId),

    // CRITICAL: onMutate for optimistic updates
    onMutate: async (projectId) => {
      // GOTCHA #1: Cancel any outgoing refetches to avoid race conditions
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      // Snapshot the previous value for rollback
      const previousProjects = queryClient.getQueryData<Project[]>(projectKeys.lists());

      // Optimistically remove the project from cache
      queryClient.setQueryData(projectKeys.lists(), (old: Project[] | undefined) => {
        if (!old) return [];
        return old.filter((project) => project.id !== projectId);
      });

      // Return context for onError
      return { previousProjects };
    },

    // PATTERN: Rollback on error
    onError: (error, projectId, context) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Failed to delete project:", errorMessage, {
        projectId,
      });

      // Rollback to previous state
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }

      // TODO: Show toast notification when useToast is available
      // showToast(`Failed to delete project: ${errorMessage}`, "error");
    },

    // TODO: Show success toast when useToast is available
    // onSuccess: () => {
    //   showToast("Project deleted successfully", "success");
    // },

    // PATTERN: Only invalidate if last mutation (prevents concurrent mutation issues)
    // GOTCHA #2: Check isMutating to prevent race conditions from concurrent deletes
    onSettled: () => {
      // Check if other mutations are still running
      const mutationCount = queryClient.isMutating({ mutationKey: ["deleteProject"] });
      if (mutationCount === 1) {
        // This is the last mutation, safe to invalidate
        queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      }
    },
  });
}

/**
 * USAGE EXAMPLE:
 *
 * ```tsx
 * // In a component
 * function ProjectSelector() {
 *   const { data: projects, isLoading } = useProjects();
 *
 *   if (isLoading) return <div>Loading...</div>;
 *
 *   return (
 *     <select>
 *       {projects?.map(project => (
 *         <option key={project.id} value={project.id}>
 *           {project.name}
 *         </option>
 *       ))}
 *     </select>
 *   );
 * }
 *
 * // Conditional query for project details
 * function ProjectDetails({ projectId }: { projectId?: string }) {
 *   const { data: project, isLoading } = useProject(projectId);
 *
 *   if (!projectId) return <div>No project selected</div>;
 *   if (isLoading) return <div>Loading...</div>;
 *
 *   return <div>{project?.name}</div>;
 * }
 *
 * // Create project mutation with optimistic updates
 * function CreateProjectForm() {
 *   const createProject = useCreateProject();
 *
 *   const handleCreate = () => {
 *     createProject.mutate({
 *       name: "New project",
 *       description: "Project description",
 *     });
 *   };
 *
 *   return (
 *     <button onClick={handleCreate} disabled={createProject.isPending}>
 *       {createProject.isPending ? "Creating..." : "Create Project"}
 *     </button>
 *   );
 * }
 *
 * // Delete project mutation with optimistic updates
 * function DeleteProjectButton({ projectId }: { projectId: string }) {
 *   const deleteProject = useDeleteProject();
 *
 *   const handleDelete = () => {
 *     if (confirm("Are you sure you want to delete this project?")) {
 *       deleteProject.mutate(projectId);
 *     }
 *   };
 *
 *   return (
 *     <button onClick={handleDelete} disabled={deleteProject.isPending}>
 *       {deleteProject.isPending ? "Deleting..." : "Delete"}
 *     </button>
 *   );
 * }
 * ```
 */
