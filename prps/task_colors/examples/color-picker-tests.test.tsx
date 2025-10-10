// Source: infra/archon/archon-ui-main/src/features/projects/components/tests/ProjectCard.test.tsx
// Lines: 1-140
// Pattern: Testing interactive components with Vitest + React Testing Library
// Extracted: 2025-10-10
// Relevance: 7/10 - Shows testing patterns for interactive UI components

/**
 * Component Testing Pattern - VITEST + REACT TESTING LIBRARY
 *
 * This shows the EXACT pattern for testing:
 * 1. Component rendering with props
 * 2. User interactions (click, hover)
 * 3. Conditional styling
 * 4. Event handler verification
 * 5. Visual state changes
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "../../../testing/test-utils";
import type { Project } from "../../types";
import { ProjectCard } from "../ProjectCard";

describe("ProjectCard", () => {
  // KEY PATTERN #1: Mock Data Setup
  const mockProject: Project = {
    id: "project-1",
    title: "Test Project",
    description: "Test Description",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
    pinned: false,
    features: [],
    docs: [],
  };

  const mockTaskCounts = {
    todo: 5,
    doing: 3,
    review: 2,
    done: 10,
  };

  // KEY PATTERN #2: Mock Handlers with vi.fn()
  const mockHandlers = {
    onSelect: vi.fn(),
    onPin: vi.fn(),
    onDelete: vi.fn(),
  };

  // KEY PATTERN #3: Reset Mocks Before Each Test
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // KEY PATTERN #4: Basic Rendering Test
  it("should render project title", () => {
    render(<ProjectCard project={mockProject} isSelected={false} taskCounts={mockTaskCounts} {...mockHandlers} />);

    expect(screen.getByText("Test Project")).toBeInTheDocument();
  });

  // KEY PATTERN #5: Testing User Interactions
  it("should call onSelect when clicked", () => {
    const { container } = render(
      <ProjectCard project={mockProject} isSelected={false} taskCounts={mockTaskCounts} {...mockHandlers} />,
    );

    const card = container.firstChild as HTMLElement;
    fireEvent.click(card);

    expect(mockHandlers.onSelect).toHaveBeenCalledWith(mockProject);
    expect(mockHandlers.onSelect).toHaveBeenCalledTimes(1);
  });

  // KEY PATTERN #6: Testing Conditional Styling
  it("should apply selected styles when isSelected is true", () => {
    const { container } = render(
      <ProjectCard project={mockProject} isSelected={true} taskCounts={mockTaskCounts} {...mockHandlers} />,
    );

    const card = container.firstChild;
    expect(card).toBeInTheDocument();
    // Check for selected-specific classes
    expect((card as HTMLElement)?.className || "").toContain("scale-[1.02]");
    expect((card as HTMLElement)?.className || "").toContain("border-purple");
  });

  // KEY PATTERN #7: Testing Dynamic Props
  it("should apply pinned styles when project is pinned", () => {
    const pinnedProject = { ...mockProject, pinned: true };

    const { container } = render(
      <ProjectCard project={pinnedProject} isSelected={false} taskCounts={mockTaskCounts} {...mockHandlers} />,
    );

    const card = container.firstChild;
    expect(card).toBeInTheDocument();
    expect((card as HTMLElement)?.className || "").toContain("from-purple");
    expect((card as HTMLElement)?.className || "").toContain("border-purple-500");
  });

  // KEY PATTERN #8: Testing Conditional Rendering
  it("should render aurora glow effect when selected", () => {
    const { container } = render(
      <ProjectCard project={mockProject} isSelected={true} taskCounts={mockTaskCounts} {...mockHandlers} />,
    );

    // Check for specific element with selector
    const glowEffect = container.querySelector(".animate-\\[pulse_8s_ease-in-out_infinite\\]");
    expect(glowEffect).toBeInTheDocument();
  });

  it("should not render aurora glow effect when not selected", () => {
    const { container } = render(
      <ProjectCard project={mockProject} isSelected={false} taskCounts={mockTaskCounts} {...mockHandlers} />,
    );

    const glowEffect = container.querySelector(".animate-\\[pulse_8s_ease-in-out_infinite\\]");
    expect(glowEffect).not.toBeInTheDocument();
  });

  // KEY PATTERN #9: Edge Case Testing
  it("should handle very long project titles", () => {
    const longTitleProject = {
      ...mockProject,
      title:
        "This is an extremely long project title that should be truncated properly to avoid breaking the layout",
    };

    render(<ProjectCard project={longTitleProject} isSelected={false} taskCounts={mockTaskCounts} {...mockHandlers} />);

    const title = screen.getByText(/This is an extremely long project title/);
    expect(title).toBeInTheDocument();
    expect(title.className).toContain("line-clamp-2");
  });
});

// EXAMPLE TEST SUITE FOR TASKCOLORPICKER:
//
// describe("TaskColorPicker", () => {
//   const mockHandlers = {
//     onChange: vi.fn(),
//   };
//
//   beforeEach(() => {
//     vi.clearAllMocks();
//   });
//
//   // Test 1: Rendering with no color selected
//   it("should render with placeholder when no color selected", () => {
//     render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
//     expect(screen.getByRole("button")).toBeInTheDocument();
//   });
//
//   // Test 2: Rendering with color selected
//   it("should show color indicator when color is selected", () => {
//     const { container } = render(
//       <TaskColorPicker value="#ef4444" onChange={mockHandlers.onChange} />
//     );
//
//     // Check for inline style with color
//     const button = screen.getByRole("button");
//     expect(button).toBeInTheDocument();
//     // Check for color swatch inside button
//   });
//
//   // Test 3: Opening popover
//   it("should open popover when clicked", async () => {
//     render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
//
//     const trigger = screen.getByRole("button");
//     fireEvent.click(trigger);
//
//     // Wait for popover content to appear
//     await waitFor(() => {
//       expect(screen.getByText("Clear Color")).toBeInTheDocument();
//     });
//   });
//
//   // Test 4: Selecting preset color
//   it("should call onChange when preset color clicked", async () => {
//     render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
//
//     // Open popover
//     const trigger = screen.getByRole("button");
//     fireEvent.click(trigger);
//
//     // Click red preset
//     const redSwatch = await screen.findByLabelText("Red");
//     fireEvent.click(redSwatch);
//
//     expect(mockHandlers.onChange).toHaveBeenCalledWith("#ef4444");
//     expect(mockHandlers.onChange).toHaveBeenCalledTimes(1);
//   });
//
//   // Test 5: Clearing color
//   it("should call onChange with undefined when clear clicked", async () => {
//     render(<TaskColorPicker value="#ef4444" onChange={mockHandlers.onChange} />);
//
//     // Open popover
//     const trigger = screen.getByRole("button");
//     fireEvent.click(trigger);
//
//     // Click clear button
//     const clearButton = await screen.findByText("Clear Color");
//     fireEvent.click(clearButton);
//
//     expect(mockHandlers.onChange).toHaveBeenCalledWith(undefined);
//   });
//
//   // Test 6: Custom color input
//   it("should update color when custom input changes", async () => {
//     render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
//
//     // Open popover
//     const trigger = screen.getByRole("button");
//     fireEvent.click(trigger);
//
//     // Change custom color input
//     const colorInput = await screen.findByLabelText("Custom Color");
//     fireEvent.change(colorInput, { target: { value: "#123456" } });
//
//     expect(mockHandlers.onChange).toHaveBeenCalledWith("#123456");
//   });
//
//   // Test 7: Keyboard navigation
//   it("should close popover when Escape pressed", async () => {
//     render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
//
//     // Open popover
//     const trigger = screen.getByRole("button");
//     fireEvent.click(trigger);
//
//     // Wait for popover
//     await waitFor(() => {
//       expect(screen.getByText("Clear Color")).toBeInTheDocument();
//     });
//
//     // Press Escape
//     fireEvent.keyDown(trigger, { key: "Escape" });
//
//     // Popover should close
//     await waitFor(() => {
//       expect(screen.queryByText("Clear Color")).not.toBeInTheDocument();
//     });
//   });
//
//   // Test 8: Disabled state
//   it("should not open when disabled", () => {
//     render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} disabled />);
//
//     const trigger = screen.getByRole("button");
//     expect(trigger).toBeDisabled();
//
//     fireEvent.click(trigger);
//
//     // Popover should not appear
//     expect(screen.queryByText("Clear Color")).not.toBeInTheDocument();
//   });
//
//   // Test 9: All preset colors visible
//   it("should display all 8 preset colors", async () => {
//     render(<TaskColorPicker value={undefined} onChange={mockHandlers.onChange} />);
//
//     // Open popover
//     const trigger = screen.getByRole("button");
//     fireEvent.click(trigger);
//
//     // Check for all 8 color swatches
//     await waitFor(() => {
//       const swatches = screen.getAllByRole("button", { name: /color/i });
//       expect(swatches.length).toBeGreaterThanOrEqual(8);
//     });
//   });
// });

// CRITICAL TESTING PATTERNS:
//
// 1. Test File Structure:
//    - describe() for component
//    - it() for each test case
//    - beforeEach() for setup
//    - Mock handlers with vi.fn()
//
// 2. Rendering Pattern:
//    - render() from test-utils
//    - screen.getByText() for queries
//    - container.querySelector() for CSS selectors
//
// 3. User Interactions:
//    - fireEvent.click() for clicks
//    - fireEvent.keyDown() for keyboard
//    - fireEvent.change() for inputs
//
// 4. Async Testing:
//    - waitFor() for delayed updates
//    - findBy queries (async)
//    - await for promises
//
// 5. Assertions:
//    - toBeInTheDocument()
//    - toHaveBeenCalledWith()
//    - toHaveBeenCalledTimes()
//    - toContain() for strings/arrays
//
// 6. What to Test for TaskColorPicker:
//    - Rendering with/without color
//    - Opening/closing popover
//    - Selecting preset colors
//    - Custom color input
//    - Clearing color
//    - Keyboard navigation
//    - Disabled state
//    - All presets visible
//    - Inline styles applied
//
// 7. What NOT to Test:
//    - Radix UI internals
//    - Browser color picker UI
//    - CSS transitions/animations
//    - Exact pixel positions
