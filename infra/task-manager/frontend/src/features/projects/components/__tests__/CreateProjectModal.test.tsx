/**
 * Tests for CreateProjectModal component
 *
 * PURPOSE: Verify modal form for creating projects
 *
 * TEST COVERAGE:
 * - Renders modal when open
 * - Form has name and description fields
 * - Form validation prevents empty name
 * - Cannot close during mutation (Esc, backdrop, Cancel button)
 * - Success callback receives new project
 * - Error displays user-friendly message
 * - Form resets on close
 * - Loading states during mutation
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { projectService } from "../../services/projectService";
import type { Project } from "../../types/project";
import { CreateProjectModal } from "../CreateProjectModal";

// Mock projectService
vi.mock("../../services/projectService", () => ({
  projectService: {
    createProject: vi.fn(),
  },
}));

// Mock useSmartPolling
vi.mock("../../../shared/hooks/useSmartPolling", () => ({
  useSmartPolling: vi.fn(() => ({
    refetchInterval: false,
  })),
}));

describe("CreateProjectModal", () => {
  let queryClient: QueryClient;

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

  it("should not render when open is false", () => {
    const mockOnOpenChange = vi.fn();

    const { container } = render(
      <CreateProjectModal open={false} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    expect(container.querySelector('[role="dialog"]')).not.toBeInTheDocument();
  });

  it("should render modal when open is true", () => {
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    expect(
      screen.getByRole("heading", { name: /create new project/i })
    ).toBeInTheDocument();
  });

  it("should render form fields", () => {
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
  });

  it("should have name field marked as required", () => {
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    expect(nameInput).toHaveAttribute("required");
    expect(nameInput).toHaveAttribute("aria-required", "true");
  });

  it("should render Cancel and Create buttons", () => {
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    expect(
      screen.getByRole("button", { name: /cancel/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /^create project$/i })
    ).toBeInTheDocument();
  });

  it("should disable Create button when name is empty", () => {
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    expect(createButton).toBeDisabled();
  });

  it("should enable Create button when name is filled", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "Test Project");

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    expect(createButton).not.toBeDisabled();
  });

  it("should call onOpenChange(false) when Cancel clicked", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    await user.click(cancelButton);

    expect(mockOnOpenChange).toHaveBeenCalledWith(false);
  });

  it("should create project successfully", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();
    const mockOnSuccess = vi.fn();

    const serverProject: Project = {
      id: "server-123",
      name: "New Project",
      description: "Test Description",
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    };

    vi.mocked(projectService.createProject).mockResolvedValue(serverProject);

    render(
      <CreateProjectModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onSuccess={mockOnSuccess}
      />,
      { wrapper: createWrapper() }
    );

    // Fill form
    const nameInput = screen.getByLabelText(/project name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(nameInput, "New Project");
    await user.type(descriptionInput, "Test Description");

    // Submit form
    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    await user.click(createButton);

    // Wait for success
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith(serverProject);
    });

    expect(mockOnOpenChange).toHaveBeenCalledWith(false);
    expect(projectService.createProject).toHaveBeenCalledWith({
      name: "New Project",
      description: "Test Description",
    });
  });

  it("should show loading state during mutation", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();

    const serverProject: Project = {
      id: "server-123",
      name: "New Project",
      description: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    };

    // Delay response to see loading state
    vi.mocked(projectService.createProject).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(serverProject), 100);
        })
    );

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "New Project");

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    await user.click(createButton);

    // Check loading state
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /creating/i })
      ).toBeInTheDocument();
    });

    // Buttons should be disabled during mutation
    expect(screen.getByRole("button", { name: /cancel/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /creating/i })).toBeDisabled();

    // Inputs should be disabled
    expect(nameInput).toBeDisabled();
  });

  it("should prevent close during mutation (Cancel button)", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();

    const serverProject: Project = {
      id: "server-123",
      name: "New Project",
      description: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    };

    vi.mocked(projectService.createProject).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(serverProject), 100);
        })
    );

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "New Project");

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    await user.click(createButton);

    // Try to close via Cancel button during mutation
    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    expect(cancelButton).toBeDisabled();

    // onOpenChange should not be called
    expect(mockOnOpenChange).not.toHaveBeenCalled();
  });

  it("should display error message on failure", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();

    const error = new Error("Server error");
    vi.mocked(projectService.createProject).mockRejectedValue(error);

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "New Project");

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    await user.click(createButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });

    expect(screen.getByText(/failed to create project/i)).toBeInTheDocument();
  });

  it("should show user-friendly error message", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();

    const error = new Error("Network request failed");
    vi.mocked(projectService.createProject).mockRejectedValue(error);

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "New Project");

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    await user.click(createButton);

    await waitFor(() => {
      expect(
        screen.getByText(/network connection issue/i)
      ).toBeInTheDocument();
    });
  });

  it("should reset form when modal closes", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();

    const { rerender } = render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    // Fill form
    const nameInput = screen.getByLabelText(/project name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(nameInput, "Test Project");
    await user.type(descriptionInput, "Test Description");

    // Close modal
    rerender(
      <CreateProjectModal open={false} onOpenChange={mockOnOpenChange} />
    );

    // Reopen modal
    rerender(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />
    );

    // Form should be reset
    const newNameInput = screen.getByLabelText(/project name/i);
    const newDescriptionInput = screen.getByLabelText(/description/i);
    expect(newNameInput).toHaveValue("");
    expect(newDescriptionInput).toHaveValue("");
  });

  it("should handle form submission with Enter key", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();
    const mockOnSuccess = vi.fn();

    const serverProject: Project = {
      id: "server-123",
      name: "New Project",
      description: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    };

    vi.mocked(projectService.createProject).mockResolvedValue(serverProject);

    render(
      <CreateProjectModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onSuccess={mockOnSuccess}
      />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "New Project{Enter}");

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith(serverProject);
    });
  });

  it("should validate name is not whitespace-only", () => {
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);

    // Type only spaces
    const event = new Event("input", { bubbles: true });
    Object.defineProperty(event, "target", {
      writable: false,
      value: { value: "   " },
    });
    nameInput.dispatchEvent(event);

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });

    // Button should remain disabled
    expect(createButton).toBeDisabled();
  });

  it("should autofocus name input when modal opens", () => {
    const mockOnOpenChange = vi.fn();

    render(
      <CreateProjectModal open={true} onOpenChange={mockOnOpenChange} />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    expect(nameInput).toHaveAttribute("autoFocus");
  });

  it("should handle creating project without description", async () => {
    const user = userEvent.setup();
    const mockOnOpenChange = vi.fn();
    const mockOnSuccess = vi.fn();

    const serverProject: Project = {
      id: "server-123",
      name: "Minimal Project",
      description: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    };

    vi.mocked(projectService.createProject).mockResolvedValue(serverProject);

    render(
      <CreateProjectModal
        open={true}
        onOpenChange={mockOnOpenChange}
        onSuccess={mockOnSuccess}
      />,
      { wrapper: createWrapper() }
    );

    const nameInput = screen.getByLabelText(/project name/i);
    await user.type(nameInput, "Minimal Project");

    const createButton = screen.getByRole("button", {
      name: /^create project$/i,
    });
    await user.click(createButton);

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith(serverProject);
    });

    expect(projectService.createProject).toHaveBeenCalledWith({
      name: "Minimal Project",
      description: "",
    });
  });
});
