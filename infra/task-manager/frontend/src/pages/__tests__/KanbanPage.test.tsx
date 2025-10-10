/**
 * Tests for KanbanPage component (Integration tests)
 *
 * PURPOSE: Verify page-level integration of project selection and Kanban board
 *
 * TEST COVERAGE:
 * - Shows loading state while fetching projects
 * - Empty state shows when no projects
 * - Validates stored project ID against available projects
 * - Auto-selects first project if stored ID invalid
 * - Persists selection to localStorage
 * - Renders ProjectSelector and KanbanBoard
 * - Create modal integration
 * - Handles deleted project gracefully
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { projectService } from "../features/projects/services/projectService";
import ProjectStorage from "../features/projects/utils/projectStorage";
import type { Project } from "../features/projects/types/project";
import { KanbanPage } from "./KanbanPage";

// Mock ProjectStorage
vi.mock("../features/projects/utils/projectStorage", () => ({
  default: {
    get: vi.fn(),
    set: vi.fn(),
    clear: vi.fn(),
  },
}));

// Mock projectService
vi.mock("../features/projects/services/projectService", () => ({
  projectService: {
    listProjects: vi.fn(),
    createProject: vi.fn(),
  },
}));

// Mock useSmartPolling
vi.mock("../features/shared/hooks/useSmartPolling", () => ({
  useSmartPolling: vi.fn(() => ({
    refetchInterval: false,
  })),
}));

// Mock KanbanBoard component
vi.mock("../features/tasks/components/KanbanBoard", () => ({
  KanbanBoard: ({ projectId }: { projectId: string }) => (
    <div data-testid="kanban-board" data-project-id={projectId}>
      Kanban Board for project {projectId}
    </div>
  ),
}));

// Mock ErrorBoundary
vi.mock("../features/shared/components/ErrorBoundary", () => ({
  ErrorBoundary: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

describe("KanbanPage", () => {
  let queryClient: QueryClient;

  const mockProjects: Project[] = [
    {
      id: "project-1",
      name: "Project Alpha",
      description: "First project",
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    },
    {
      id: "project-2",
      name: "Project Beta",
      description: null,
      created_at: "2025-01-02T00:00:00Z",
      updated_at: "2025-01-02T00:00:00Z",
    },
  ];

  const createWrapper = () => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    return ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Default localStorage mock behavior
    vi.mocked(ProjectStorage.get).mockReturnValue(null);
  });

  it("should show loading state while fetching projects", () => {
    vi.mocked(projectService.listProjects).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<KanbanPage />, { wrapper: createWrapper() });

    expect(screen.getByRole("main", { name: /loading projects/i })).toBeInTheDocument();
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByText(/loading projects/i)).toBeInTheDocument();
  });

  it("should show empty state when no projects", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue([]);

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /no projects yet/i })
      ).toBeInTheDocument();
    });

    expect(
      screen.getByRole("button", { name: /create your first project/i })
    ).toBeInTheDocument();
  });

  it("should clear localStorage when no projects", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue([]);
    vi.mocked(ProjectStorage.get).mockReturnValue("old-project-123");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(ProjectStorage.clear).toHaveBeenCalled();
    });
  });

  it("should auto-select first project when no stored ID", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue(null);

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    });

    expect(ProjectStorage.set).toHaveBeenCalledWith("project-1");
    expect(screen.getByTestId("kanban-board")).toHaveAttribute(
      "data-project-id",
      "project-1"
    );
  });

  it("should use stored project ID if valid", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-2");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    });

    expect(screen.getByTestId("kanban-board")).toHaveAttribute(
      "data-project-id",
      "project-2"
    );
    expect(ProjectStorage.set).not.toHaveBeenCalled(); // Already valid
  });

  it("should auto-select first project if stored ID invalid (deleted project)", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("deleted-project-999");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    });

    // Should auto-select first project
    expect(ProjectStorage.set).toHaveBeenCalledWith("project-1");
    expect(screen.getByTestId("kanban-board")).toHaveAttribute(
      "data-project-id",
      "project-1"
    );
  });

  it("should render ProjectSelector with project list", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-1");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    expect(screen.getByText("Project Alpha")).toBeInTheDocument();
  });

  it("should render KanbanBoard with selected project", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-1");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    });

    expect(screen.getByTestId("kanban-board")).toHaveAttribute(
      "data-project-id",
      "project-1"
    );
  });

  it("should update KanbanBoard when project selection changes", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-1");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    // Open dropdown
    const trigger = screen.getByRole("combobox");
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });

    // Select different project
    const projectBetaOption = screen.getByRole("option", {
      name: /project beta/i,
    });
    await user.click(projectBetaOption);

    // Verify localStorage updated
    await waitFor(() => {
      expect(ProjectStorage.set).toHaveBeenCalledWith("project-2");
    });

    // Verify KanbanBoard updated
    expect(screen.getByTestId("kanban-board")).toHaveAttribute(
      "data-project-id",
      "project-2"
    );
  });

  it("should show create modal when Create New Project clicked in empty state", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue([]);

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /create your first project/i })
      ).toBeInTheDocument();
    });

    const createButton = screen.getByRole("button", {
      name: /create your first project/i,
    });
    await user.click(createButton);

    // Modal should open
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /create new project/i })
      ).toBeInTheDocument();
    });
  });

  it("should show create modal when Create New Project clicked in selector", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-1");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    // Open dropdown
    const trigger = screen.getByRole("combobox");
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });

    // Click "Create New Project"
    const createOption = screen.getByRole("option", {
      name: /create new project/i,
    });
    await user.click(createOption);

    // Modal should open
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /create new project/i })
      ).toBeInTheDocument();
    });
  });

  it("should auto-select newly created project", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue([]);

    const newProject: Project = {
      id: "new-project-123",
      name: "New Project",
      description: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    };

    vi.mocked(projectService.createProject).mockResolvedValue(newProject);

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /create your first project/i })
      ).toBeInTheDocument();
    });

    // Open create modal
    const createButton = screen.getByRole("button", {
      name: /create your first project/i,
    });
    await user.click(createButton);

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /create new project/i })
      ).toBeInTheDocument();
    });

    // Fill form
    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "New Project");

    // Submit
    const submitButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    await user.click(submitButton);

    // Wait for success
    await waitFor(() => {
      expect(ProjectStorage.set).toHaveBeenCalledWith("new-project-123");
    });
  });

  it("should render page header with title", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-1");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /task management/i })
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText(/organize your tasks with drag-and-drop/i)
    ).toBeInTheDocument();
  });

  it("should have accessible ARIA landmarks", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-1");

    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByRole("banner")).toBeInTheDocument();
    });

    expect(screen.getByRole("main", { name: /kanban board/i })).toBeInTheDocument();
  });

  it("should show initializing state before selecting project", async () => {
    vi.mocked(projectService.listProjects).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(mockProjects), 100);
        })
    );
    vi.mocked(ProjectStorage.get).mockReturnValue(null);

    render(<KanbanPage />, { wrapper: createWrapper() });

    // Should show loading initially
    expect(screen.getByRole("main", { name: /loading projects/i })).toBeInTheDocument();

    // Wait for projects to load
    await waitFor(
      () => {
        expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
      },
      { timeout: 150 }
    );
  });

  it("should handle project list refresh", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-1");

    const { rerender } = render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    });

    // Update mock to return updated list (project-1 deleted)
    const updatedProjects = mockProjects.filter((p) => p.id !== "project-1");
    vi.mocked(projectService.listProjects).mockResolvedValue(updatedProjects);

    // Force re-render by invalidating queries
    queryClient.invalidateQueries();

    // Wait for update
    await waitFor(() => {
      // Should auto-select first available project (project-2)
      expect(screen.getByTestId("kanban-board")).toHaveAttribute(
        "data-project-id",
        "project-2"
      );
    });
  });

  it("should persist project selection across component remounts", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);
    vi.mocked(ProjectStorage.get).mockReturnValue("project-2");

    const { unmount, rerender } = render(<KanbanPage />, {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    });

    expect(screen.getByTestId("kanban-board")).toHaveAttribute(
      "data-project-id",
      "project-2"
    );

    // Unmount
    unmount();

    // Remount with new wrapper
    render(<KanbanPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByTestId("kanban-board")).toBeInTheDocument();
    });

    // Should still use stored project ID
    expect(screen.getByTestId("kanban-board")).toHaveAttribute(
      "data-project-id",
      "project-2"
    );
  });
});
