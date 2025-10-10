/**
 * DeleteProjectDialog - Confirmation dialog for deleting projects
 *
 * PURPOSE: Modal dialog to confirm project deletion with destructive action pattern
 *
 * FEATURES:
 * - Clear warning about data loss
 * - Prevent accidental deletion
 * - Cannot close during mutation
 * - Accessible with ARIA labels
 *
 * PATTERN: Follows Radix UI AlertDialog pattern for destructive actions
 *
 * GOTCHAS ADDRESSED:
 * - Gotcha #9: Prevent close during mutation (handleOpenChange, onEscapeKeyDown, onPointerDownOutside)
 */

import * as AlertDialog from "@radix-ui/react-alert-dialog";
import { AlertTriangle } from "lucide-react";
import { useDeleteProject } from "../hooks/useProjectQueries";
import type { Project } from "../types/project";

interface DeleteProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  project: Project | null;
  onSuccess?: () => void;
}

export const DeleteProjectDialog = ({
  open,
  onOpenChange,
  project,
  onSuccess,
}: DeleteProjectDialogProps) => {
  const deleteProject = useDeleteProject();

  console.log('[DeleteProjectDialog] Render:', { open, projectName: project?.name });

  // CRITICAL: Prevent close during mutation (Gotcha #9)
  const handleOpenChange = (newOpen: boolean) => {
    // If user is trying to close (!newOpen) and mutation is pending, block it
    if (!newOpen && deleteProject.isPending) {
      return; // Block close attempt
    }

    onOpenChange(newOpen);
  };

  const handleDelete = () => {
    if (!project) return;

    // Call mutation with callbacks
    deleteProject.mutate(project.id, {
      onSuccess: () => {
        // Close dialog
        onOpenChange(false);

        // Call optional success callback
        onSuccess?.();
      },
    });
  };

  if (!project) return null;

  return (
    <AlertDialog.Root open={open} onOpenChange={handleOpenChange}>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="fixed inset-0 bg-black/50 z-40 transition-opacity data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />

        <AlertDialog.Content
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
            if (deleteProject.isPending) e.preventDefault();
          }}
          onPointerDownOutside={(e) => {
            if (deleteProject.isPending) e.preventDefault();
          }}
        >
          {/* Header with warning icon */}
          <div className="flex items-start gap-3 mb-4">
            <div className="flex-shrink-0 w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" aria-hidden="true" />
            </div>
            <div className="flex-1">
              <AlertDialog.Title className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
                Delete Project
              </AlertDialog.Title>
              <AlertDialog.Description className="text-sm text-gray-600 dark:text-gray-400">
                Are you sure you want to delete <strong className="font-medium text-gray-900 dark:text-gray-100">{project.name}</strong>?
                This action cannot be undone and will permanently delete all tasks associated with this project.
              </AlertDialog.Description>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex justify-end gap-2">
            <AlertDialog.Cancel asChild>
              <button
                type="button"
                disabled={deleteProject.isPending}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                         text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800
                         disabled:opacity-50 disabled:cursor-not-allowed
                         focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900
                         transition-colors"
                aria-label="Cancel deletion"
              >
                Cancel
              </button>
            </AlertDialog.Cancel>

            <AlertDialog.Action asChild>
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleteProject.isPending}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700
                         disabled:opacity-50 disabled:cursor-not-allowed
                         focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900
                         flex items-center gap-2 transition-colors"
                aria-label={deleteProject.isPending ? "Deleting project" : "Confirm deletion"}
              >
                {deleteProject.isPending ? (
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
                    <span aria-live="polite">Deleting...</span>
                  </>
                ) : (
                  "Delete Project"
                )}
              </button>
            </AlertDialog.Action>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
};
