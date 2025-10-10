/**
 * Tests for ProjectSelector component
 *
 * PURPOSE: Verify project dropdown selector
 *
 * TEST COVERAGE:
 * - Renders project list in dropdown
 * - Shows loading state while fetching
 * - Shows error state with retry button
 * - Selected project has visual indicator (checkmark)
 * - Changing selection calls callback
 * - "Create New Project" triggers callback
 * - Returns null when no projects (empty state at page level)
 * - Accessible (keyboard navigation)
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { projectService } from "../../services/projectService";
import type { Project } from "../../types/project";
import { ProjectSelector } from "../ProjectSelector";

// Mock projectService
vi.mock("../../services/projectService", () => ({
  projectService: {
    listProjects: vi.fn(),
  },
}));

// Mock useSmartPolling
vi.mock("../../../shared/hooks/useSmartPolling", () => ({
  useSmartPolling: vi.fn(() => ({
    refetchInterval: false,
  })),
}));

describe("ProjectSelector", () => {
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
    {
      id: "project-3",
      name: "Project Gamma",
      description: "Third project",
      created_at: "2025-01-03T00:00:00Z",
      updated_at: "2025-01-03T00:00:00Z",
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
  });

  it("should show loading state while fetching projects", () => {
    vi.mocked(projectService.listProjects).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId={null}
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByLabelText(/loading projects/i)).toBeInTheDocument();
  });

  it("should show error state with retry button", async () => {
    const error = new Error("Network error");
    vi.mocked(projectService.listProjects).mockRejectedValue(error);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId={null}
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });

    expect(screen.getByText(/failed to load projects/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /retry/i })
    ).toBeInTheDocument();
  });

  it("should retry fetching when retry button clicked", async () => {
    const user = userEvent.setup();
    const error = new Error("Network error");

    vi.mocked(projectService.listProjects)
      .mockRejectedValueOnce(error)
      .mockResolvedValueOnce(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId={null}
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });

    const retryButton = screen.getByRole("button", { name: /retry/i });
    await user.click(retryButton);

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    expect(projectService.listProjects).toHaveBeenCalledTimes(2);
  });

  it("should return null when no projects", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue([]);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    const { container } = render(
      <ProjectSelector
        selectedProjectId={null}
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it("should render project selector with trigger button", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    expect(screen.getByText("Project Alpha")).toBeInTheDocument();
  });

  it("should show placeholder when no project selected", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId={null}
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText(/select project/i)).toBeInTheDocument();
    });
  });

  it("should call onProjectChange when project selected", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    // Open dropdown
    const trigger = screen.getByRole("combobox");
    await user.click(trigger);

    // Wait for dropdown to open and select item
    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });

    const projectBetaOption = screen.getByRole("option", {
      name: /select project: project beta/i,
    });
    await user.click(projectBetaOption);

    expect(mockOnProjectChange).toHaveBeenCalledWith("project-2");
  });

  it("should call onCreateProject when Create New Project clicked", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

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

    expect(mockOnCreateProject).toHaveBeenCalledTimes(1);
    expect(mockOnProjectChange).not.toHaveBeenCalled();
  });

  it("should show checkmark indicator for selected project", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-2"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    // Open dropdown
    const trigger = screen.getByRole("combobox");
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });

    // Selected project should have data-state=checked
    const selectedOption = screen.getByRole("option", {
      name: /select project: project beta/i,
    });
    expect(selectedOption).toHaveAttribute("data-state", "checked");
  });

  it("should support keyboard navigation", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    // Focus trigger
    const trigger = screen.getByRole("combobox");
    trigger.focus();
    expect(trigger).toHaveFocus();

    // Open with Space key
    await user.keyboard(" ");

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });

    // Navigate with arrow keys
    await user.keyboard("{ArrowDown}");
    await user.keyboard("{ArrowDown}");

    // Select with Enter
    await user.keyboard("{Enter}");

    // Should have selected project-2
    await waitFor(() => {
      expect(mockOnProjectChange).toHaveBeenCalledWith("project-2");
    });
  });

  it("should render all projects in dropdown", async () => {
    const user = userEvent.setup();
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    // Open dropdown
    const trigger = screen.getByRole("combobox");
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });

    // All projects should be present
    expect(
      screen.getByRole("option", { name: /project alpha/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /project beta/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /project gamma/i })
    ).toBeInTheDocument();
  });

  it("should have accessible ARIA attributes", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    const trigger = screen.getByRole("combobox");
    expect(trigger).toHaveAttribute("aria-label", "Select project");
    expect(trigger).toHaveAttribute("aria-haspopup", "listbox");
  });

  it("should memoize to prevent unnecessary re-renders", async () => {
    vi.mocked(projectService.listProjects).mockResolvedValue(mockProjects);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    const { rerender } = render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    // Rerender with same props
    rerender(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />
    );

    // Component should not re-fetch
    expect(projectService.listProjects).toHaveBeenCalledTimes(1);
  });

  it("should handle single project", async () => {
    const singleProject: Project[] = [mockProjects[0]];
    vi.mocked(projectService.listProjects).mockResolvedValue(singleProject);

    const mockOnProjectChange = vi.fn();
    const mockOnCreateProject = vi.fn();

    render(
      <ProjectSelector
        selectedProjectId="project-1"
        onProjectChange={mockOnProjectChange}
        onCreateProject={mockOnCreateProject}
      />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    expect(screen.getByText("Project Alpha")).toBeInTheDocument();
  });
});
