/**
 * Tests for EmptyProjectState component
 *
 * PURPOSE: Verify empty state onboarding component
 *
 * TEST COVERAGE:
 * - Renders centered layout
 * - Shows "No Projects Yet" message
 * - Displays description text
 * - Shows "Create Your First Project" button
 * - Button triggers onCreateClick callback
 * - Accessible (ARIA labels, keyboard navigation)
 */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { EmptyProjectState } from "../EmptyProjectState";

describe("EmptyProjectState", () => {
  it("should render empty state message", () => {
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    expect(
      screen.getByRole("heading", { name: /no projects yet/i })
    ).toBeInTheDocument();
  });

  it("should render description text", () => {
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    expect(
      screen.getByText(/projects help you organize your tasks/i)
    ).toBeInTheDocument();
  });

  it("should render create button", () => {
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    expect(
      screen.getByRole("button", { name: /create your first project/i })
    ).toBeInTheDocument();
  });

  it("should call onCreateClick when button clicked", async () => {
    const user = userEvent.setup();
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    const button = screen.getByRole("button", {
      name: /create your first project/i,
    });
    await user.click(button);

    expect(mockOnCreateClick).toHaveBeenCalledTimes(1);
  });

  it("should support keyboard navigation", async () => {
    const user = userEvent.setup();
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    const button = screen.getByRole("button", {
      name: /create your first project/i,
    });

    // Focus button
    await user.tab();
    expect(button).toHaveFocus();

    // Press Enter
    await user.keyboard("{Enter}");
    expect(mockOnCreateClick).toHaveBeenCalledTimes(1);

    // Press Space
    await user.keyboard(" ");
    expect(mockOnCreateClick).toHaveBeenCalledTimes(2);
  });

  it("should have accessible ARIA attributes", () => {
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    const main = screen.getByRole("main");
    expect(main).toHaveAttribute("aria-label", "Empty project state");

    const button = screen.getByRole("button", {
      name: /create your first project/i,
    });
    expect(button).toHaveAttribute("aria-label", "Create your first project");
  });

  it("should display icon", () => {
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    // Icon should be present but hidden from screen readers
    const iconContainer = screen
      .getByRole("main")
      .querySelector('[aria-hidden="true"]');
    expect(iconContainer).toBeInTheDocument();
  });

  it("should have centered layout", () => {
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    const container = screen.getByRole("main");
    expect(container).toHaveClass("flex", "flex-col", "items-center", "justify-center");
  });

  it("should handle multiple rapid clicks", async () => {
    const user = userEvent.setup();
    const mockOnCreateClick = vi.fn();

    render(<EmptyProjectState onCreateClick={mockOnCreateClick} />);

    const button = screen.getByRole("button", {
      name: /create your first project/i,
    });

    // Rapid clicks
    await user.tripleClick(button);

    // Should call callback for each click
    expect(mockOnCreateClick).toHaveBeenCalledTimes(3);
  });
});
