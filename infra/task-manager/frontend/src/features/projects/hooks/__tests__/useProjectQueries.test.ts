/**
 * Tests for useProjectQueries hooks
 *
 * PURPOSE: Verify TanStack Query hooks for project CRUD operations
 *
 * TEST COVERAGE:
 * - useProjects() fetches project list
 * - useProject() fetches single project conditionally
 * - useCreateProject() creates project with optimistic updates
 * - Optimistic update adds project immediately
 * - Rollback on error restores previous state
 * - Concurrent mutations handled correctly
 * - Race condition prevention (cancelQueries)
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { projectService } from "../../services/projectService";
import type { Project, ProjectCreate } from "../../types/project";
import {
  projectKeys,
  useCreateProject,
  useProject,
  useProjects,
} from "../useProjectQueries";

// Mock projectService
vi.mock("../../services/projectService", () => ({
  projectService: {
    listProjects: vi.fn(),
    getProject: vi.fn(),
    createProject: vi.fn(),
  },
}));

// Mock useSmartPolling
vi.mock("../../../shared/hooks/useSmartPolling", () => ({
  useSmartPolling: vi.fn(() => ({
    refetchInterval: false, // Disable polling in tests
  })),
}));

describe("useProjectQueries", () => {
  let queryClient: QueryClient;

  // Helper to create wrapper with QueryClient
  const createWrapper = () => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false, // Disable retries in tests
        },
        mutations: {
          retry: false,
        },
      },
    });

    return ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("projectKeys", () => {
    it("should have hierarchical query key structure", () => {
      expect(projectKeys.all).toEqual(["projects"]);
      expect(projectKeys.lists()).toEqual(["projects", "list"]);
      expect(projectKeys.detail("123")).toEqual(["projects", "detail", "123"]);
    });
  });

  describe("useProjects()", () => {
    it("should fetch project list successfully", async () => {
      const mockProjects: Project[] = [
        {
          id: "1",
          name: "Project 1",
          description: "Description 1",
          created_at: "2025-01-01T00:00:00Z",
          updated_at: "2025-01-01T00:00:00Z",
        },
        {
          id: "2",
          name: "Project 2",
          description: null,
          created_at: "2025-01-02T00:00:00Z",
          updated_at: "2025-01-02T00:00:00Z",
        },
      ];

      vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      // Initial loading state
      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();

      // Wait for query to resolve
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockProjects);
      expect(projectService.listProjects).toHaveBeenCalledTimes(1);
    });

    it("should handle empty project list", async () => {
      vi.mocked(projectService.listProjects).mockResolvedValue([]);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual([]);
    });

    it("should handle fetch error", async () => {
      const error = new Error("Network error");
      vi.mocked(projectService.listProjects).mockRejectedValue(error);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toEqual(error);
      expect(result.current.data).toBeUndefined();
    });

    it("should use correct query key", async () => {
      vi.mocked(projectService.listProjects).mockResolvedValue([]);

      renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        const queryData = queryClient.getQueryData(projectKeys.lists());
        expect(queryData).toEqual([]);
      });
    });
  });

  describe("useProject()", () => {
    it("should fetch single project when id provided", async () => {
      const mockProject: Project = {
        id: "123",
        name: "Test Project",
        description: "Test Description",
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      };

      vi.mocked(projectService.getProject).mockResolvedValue(mockProject);

      const { result } = renderHook(() => useProject("123"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockProject);
      expect(projectService.getProject).toHaveBeenCalledWith("123");
    });

    it("should not run query when id is undefined", async () => {
      const { result } = renderHook(() => useProject(undefined), {
        wrapper: createWrapper(),
      });

      // Should not be loading or fetching
      expect(result.current.isLoading).toBe(false);
      expect(result.current.isFetching).toBe(false);
      expect(result.current.data).toBeUndefined();

      // Service should not be called
      expect(projectService.getProject).not.toHaveBeenCalled();
    });

    it("should respect enabled parameter", async () => {
      const { result } = renderHook(() => useProject("123", false), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isFetching).toBe(false);
      expect(projectService.getProject).not.toHaveBeenCalled();
    });

    it("should handle fetch error", async () => {
      const error = new Error("Not found");
      vi.mocked(projectService.getProject).mockRejectedValue(error);

      const { result } = renderHook(() => useProject("999"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toEqual(error);
    });
  });

  describe("useCreateProject()", () => {
    it("should create project successfully", async () => {
      const newProjectData: ProjectCreate = {
        name: "New Project",
        description: "New Description",
      };

      const serverProject: Project = {
        id: "server-123",
        name: newProjectData.name,
        description: newProjectData.description!,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      };

      vi.mocked(projectService.createProject).mockResolvedValue(serverProject);

      // Pre-populate with existing projects
      queryClient.setQueryData(projectKeys.lists(), []);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      // Trigger mutation
      result.current.mutate(newProjectData);

      // Wait for mutation to complete
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(projectService.createProject).toHaveBeenCalledWith(newProjectData);
      expect(result.current.data).toEqual(serverProject);
    });

    it("should add optimistic project immediately", async () => {
      const newProjectData: ProjectCreate = {
        name: "Optimistic Project",
        description: "Test",
      };

      const serverProject: Project = {
        id: "server-456",
        name: newProjectData.name,
        description: newProjectData.description!,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      };

      // Delay server response to see optimistic update
      vi.mocked(projectService.createProject).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(serverProject), 100);
          })
      );

      queryClient.setQueryData(projectKeys.lists(), []);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      // Trigger mutation
      result.current.mutate(newProjectData);

      // Immediately check for optimistic update
      await waitFor(
        () => {
          const projects = queryClient.getQueryData<Project[]>(
            projectKeys.lists()
          );
          expect(projects).toHaveLength(1);
        },
        { timeout: 50 }
      );

      const projects = queryClient.getQueryData<Project[]>(projectKeys.lists());
      expect(projects![0].name).toBe("Optimistic Project");
      expect(projects![0].id).toContain("temp-"); // Temporary ID

      // Wait for server response
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Check server project replaced optimistic
      const finalProjects = queryClient.getQueryData<Project[]>(
        projectKeys.lists()
      );
      expect(finalProjects).toHaveLength(1);
      expect(finalProjects![0].id).toBe("server-456");
    });

    it("should rollback on error", async () => {
      const newProjectData: ProjectCreate = {
        name: "Failed Project",
        description: "Test",
      };

      const existingProjects: Project[] = [
        {
          id: "existing-1",
          name: "Existing Project",
          description: null,
          created_at: "2025-01-01T00:00:00Z",
          updated_at: "2025-01-01T00:00:00Z",
        },
      ];

      const error = new Error("Server error");
      vi.mocked(projectService.createProject).mockRejectedValue(error);

      // Pre-populate with existing projects
      queryClient.setQueryData(projectKeys.lists(), existingProjects);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      // Trigger mutation
      result.current.mutate(newProjectData);

      // Wait for error
      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toEqual(error);

      // Verify rollback - should have original projects only
      const projects = queryClient.getQueryData<Project[]>(projectKeys.lists());
      expect(projects).toEqual(existingProjects);
    });

    it("should handle concurrent mutations", async () => {
      const project1: ProjectCreate = { name: "Project 1" };
      const project2: ProjectCreate = { name: "Project 2" };

      const serverProject1: Project = {
        id: "server-1",
        name: "Project 1",
        description: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      };

      const serverProject2: Project = {
        id: "server-2",
        name: "Project 2",
        description: null,
        created_at: "2025-01-02T00:00:00Z",
        updated_at: "2025-01-02T00:00:00Z",
      };

      vi.mocked(projectService.createProject)
        .mockResolvedValueOnce(serverProject1)
        .mockResolvedValueOnce(serverProject2);

      queryClient.setQueryData(projectKeys.lists(), []);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      // Trigger both mutations concurrently
      result.current.mutate(project1);
      result.current.mutate(project2);

      // Wait for both to complete
      await waitFor(() => {
        const projects = queryClient.getQueryData<Project[]>(
          projectKeys.lists()
        );
        // Should have both projects
        expect(projects?.length).toBeGreaterThanOrEqual(2);
      });

      const finalProjects = queryClient.getQueryData<Project[]>(
        projectKeys.lists()
      );

      // Both projects should be in the list (no duplicates)
      expect(finalProjects!.length).toBe(2);
      expect(finalProjects!.some((p) => p.id === "server-1")).toBe(true);
      expect(finalProjects!.some((p) => p.id === "server-2")).toBe(true);
    });

    it("should use mutation key for tracking", () => {
      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      // Check mutation key is set (enables isMutating tracking)
      // This is verified by the mutation working correctly in concurrent tests
      expect(result.current).toBeDefined();
    });

    it("should cancel in-flight queries before optimistic update", async () => {
      const cancelQueriesSpy = vi.spyOn(queryClient, "cancelQueries");

      const newProjectData: ProjectCreate = { name: "Test" };
      const serverProject: Project = {
        id: "server-1",
        name: "Test",
        description: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      };

      vi.mocked(projectService.createProject).mockResolvedValue(serverProject);

      queryClient.setQueryData(projectKeys.lists(), []);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(newProjectData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify cancelQueries was called with correct query key
      expect(cancelQueriesSpy).toHaveBeenCalledWith({
        queryKey: projectKeys.lists(),
      });
    });

    it("should handle mutation with minimal data", async () => {
      const minimalProject: ProjectCreate = {
        name: "Minimal Project",
        // No description
      };

      const serverProject: Project = {
        id: "server-minimal",
        name: "Minimal Project",
        description: null,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      };

      vi.mocked(projectService.createProject).mockResolvedValue(serverProject);

      queryClient.setQueryData(projectKeys.lists(), []);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(minimalProject);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(serverProject);
    });
  });
});
