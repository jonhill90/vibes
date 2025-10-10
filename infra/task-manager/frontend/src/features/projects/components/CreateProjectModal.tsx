/**
 * CreateProjectModal - Modal form for creating new projects
 *
 * PURPOSE: Modal dialog with form for creating projects with validation and mutation integration
 *
 * FEATURES:
 * - Form fields: name (required), description (optional)
 * - Client-side validation (name minimum 1 character)
 * - Integration with useCreateProject mutation
 * - Optimistic UI updates with rollback on error
 * - Cannot close during mutation (Esc, backdrop, Cancel button)
 * - Form resets on close
 * - Loading states during mutation
 *
 * PATTERN: Follows example_1_modal_with_form.tsx from Archon NewProjectModal
 *
 * GOTCHAS ADDRESSED:
 * - Gotcha #9: Prevent close during mutation (handleOpenChange, onEscapeKeyDown, onPointerDownOutside)
 * - Gotcha #13: Form resets on close (handleOpenChange resets formData)
 * - Form validation prevents empty name (handleSubmit validation)
 * - Loading states clear (disabled inputs, button text "Creating...")
 */

import * as Dialog from "@radix-ui/react-dialog";
import { useState } from "react";
import { useCreateProject } from "../hooks/useProjectQueries";
import type { Project, ProjectCreate } from "../types/project";

interface CreateProjectModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: (project: Project) => void;
}

/**
 * Convert error to user-friendly message
 * TASK 8: Show user-friendly error messages (not raw API errors)
 */
function getUserFriendlyErrorMessage(error: Error | unknown): string {
  if (!error) return "An unexpected error occurred. Please try again.";

  const errorMessage = error instanceof Error ? error.message : String(error);

  // Network errors
  if (errorMessage.toLowerCase().includes("network") ||
      errorMessage.toLowerCase().includes("fetch")) {
    return "Network connection issue. Please check your internet connection and try again.";
  }

  // Validation errors
  if (errorMessage.toLowerCase().includes("validation") ||
      errorMessage.toLowerCase().includes("invalid")) {
    return "Please check your input and try again.";
  }

  // Timeout errors
  if (errorMessage.toLowerCase().includes("timeout")) {
    return "Request took too long. Please try again.";
  }

  // Server errors
  if (errorMessage.toLowerCase().includes("500") ||
      errorMessage.toLowerCase().includes("server")) {
    return "Server is experiencing issues. Please try again in a moment.";
  }

  // Permission errors
  if (errorMessage.toLowerCase().includes("403") ||
      errorMessage.toLowerCase().includes("unauthorized") ||
      errorMessage.toLowerCase().includes("forbidden")) {
    return "You don't have permission to perform this action.";
  }

  // Duplicate/conflict errors
  if (errorMessage.toLowerCase().includes("409") ||
      errorMessage.toLowerCase().includes("duplicate") ||
      errorMessage.toLowerCase().includes("already exists")) {
    return "A project with this name already exists.";
  }

  // Default: Show sanitized error or generic message
  return errorMessage.length > 100
    ? "An error occurred. Please try again or contact support if the issue persists."
    : errorMessage;
}

export const CreateProjectModal = ({ open, onOpenChange, onSuccess }: CreateProjectModalProps) => {
  // Form state
  const [formData, setFormData] = useState<ProjectCreate>({
    name: "",
    description: "",
  });

  // Get createProject mutation from useCreateProject
  const createProject = useCreateProject();

  // CRITICAL: Prevent close during mutation (Gotcha #9)
  const handleOpenChange = (newOpen: boolean) => {
    // If user is trying to close (!newOpen) and mutation is pending, block it
    if (!newOpen && createProject.isPending) {
      return; // Block close attempt
    }

    // If closing, reset form and clear error state
    if (!newOpen) {
      setFormData({ name: "", description: "" });
      createProject.reset(); // Clear error state from previous attempts
    }

    onOpenChange(newOpen);
  };

  // Form submit handler
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // CRITICAL: Prevent double submit during mutation
    if (createProject.isPending) return;

    // CRITICAL: Validate name not empty
    if (!formData.name.trim()) return;

    // Call mutation with callbacks
    createProject.mutate(formData, {
      onSuccess: (newProject) => {
        // Reset form
        setFormData({ name: "", description: "" });

        // Close modal
        onOpenChange(false);

        // Call optional success callback
        onSuccess?.(newProject);
      },
      // onError is handled in the mutation hook, but we could add UI feedback here
    });
  };

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40 transition-opacity data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />

        <Dialog.Content
          className="fixed left-[50%] top-[50%] z-50 translate-x-[-50%] translate-y-[-50%]
                     bg-white dark:bg-gray-900 rounded-lg shadow-xl
                     w-full max-w-md p-6
                     data-[state=open]:animate-in data-[state=closed]:animate-out
                     data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0
                     data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95
                     data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%]
                     data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]"
          // CRITICAL: Prevent close during mutation (Gotcha #9)
          onEscapeKeyDown={(e) => {
            if (createProject.isPending) e.preventDefault();
          }}
          onPointerDownOutside={(e) => {
            if (createProject.isPending) e.preventDefault();
          }}
        >
          <form onSubmit={handleSubmit}>
            {/* Header */}
            <Dialog.Title className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Create New Project
            </Dialog.Title>
            <Dialog.Description className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Start a new project to organize your tasks.
            </Dialog.Description>

            {/* Form Fields */}
            <div className="space-y-4 mb-6">
              {/* Name Field */}
              <div>
                <label
                  htmlFor="project-name"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                >
                  Project Name <span className="text-red-500">*</span>
                </label>
                <input
                  id="project-name"
                  type="text"
                  placeholder="Enter project name..."
                  value={formData.name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                  disabled={createProject.isPending}
                  autoFocus
                  required
                  aria-required="true"
                  aria-invalid={!formData.name.trim() && formData.name.length > 0 ? "true" : "false"}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed
                           transition-all"
                />
              </div>

              {/* Description Field */}
              <div>
                <label
                  htmlFor="project-description"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                >
                  Description
                </label>
                <textarea
                  id="project-description"
                  placeholder="Enter project description..."
                  rows={4}
                  value={formData.description}
                  onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                  disabled={createProject.isPending}
                  aria-describedby="description-hint"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed
                           resize-none transition-all"
                />
                <p id="description-hint" className="sr-only">Optional field for project description</p>
              </div>
            </div>

            {/* Error Message - User-friendly (Task 8: Gotcha #7) */}
            {createProject.error && (
              <div
                className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md"
                role="alert"
                aria-live="assertive"
              >
                <p className="text-sm text-red-800 dark:text-red-300 font-medium mb-1">
                  Failed to create project
                </p>
                <p className="text-xs text-red-700 dark:text-red-400">
                  {getUserFriendlyErrorMessage(createProject.error)}
                </p>
              </div>
            )}

            {/* Footer - Action Buttons */}
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => handleOpenChange(false)}
                disabled={createProject.isPending}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                         text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800
                         disabled:opacity-50 disabled:cursor-not-allowed
                         focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900
                         transition-colors"
                aria-label="Cancel and close modal"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createProject.isPending || !formData.name.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700
                         disabled:opacity-50 disabled:cursor-not-allowed
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900
                         flex items-center gap-2 transition-colors"
                aria-label={createProject.isPending ? "Creating project" : "Create project"}
              >
                {createProject.isPending ? (
                  <>
                    <svg
                      className="animate-spin h-4 w-4"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      role="status"
                      aria-label="Loading"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    <span aria-live="polite">Creating...</span>
                  </>
                ) : (
                  "Create Project"
                )}
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
