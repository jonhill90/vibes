/**
 * ProjectSelector - Dropdown component for selecting projects
 *
 * PURPOSE: Accessible project selection with visual active indicator
 *
 * FEATURES:
 * - Radix UI Select primitives for accessibility
 * - Shows current project name in trigger
 * - Visual checkmark indicator for selected project
 * - "Create New Project" action at bottom of dropdown
 * - Portal rendering to escape Dialog focus traps (Gotcha #6)
 * - Dark mode support with consistent styling
 * - Loading and error states
 *
 * PATTERN: Based on example_3_select_component.tsx from Archon
 *
 * GOTCHAS ADDRESSED:
 * - Gotcha #6: Select.Content uses Portal to escape Dialog focus trap
 * - Loading/error states handled gracefully
 * - No projects returns null (EmptyProjectState shown at page level)
 *
 * PERFORMANCE OPTIMIZATIONS:
 * - useCallback memoization for event handlers
 * - useMemo for currentProject lookup
 * - React.memo wrapper prevents unnecessary re-renders
 *
 * USAGE:
 * ```tsx
 * <ProjectSelector
 *   selectedProjectId={selectedProjectId}
 *   onProjectChange={setSelectedProjectId}
 *   onCreateProject={() => setCreateModalOpen(true)}
 * />
 * ```
 */

import * as Select from "@radix-ui/react-select";
import { Check, ChevronDown, FolderPlus, Trash2 } from "lucide-react";
import { memo, useCallback, useMemo, useState } from "react";
import { useProjects } from "../hooks/useProjectQueries";
import { DeleteProjectDialog } from "./DeleteProjectDialog";
import type { Project } from "../types/project";

interface ProjectSelectorProps {
  selectedProjectId: string | null;
  onProjectChange: (projectId: string) => void;
  onCreateProject: () => void;
  onProjectDeleted?: () => void;
}

export const ProjectSelector = memo(({
  selectedProjectId,
  onProjectChange,
  onCreateProject,
  onProjectDeleted,
}: ProjectSelectorProps) => {
  const { data: projects, isLoading, error, refetch } = useProjects();

  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);

  // CRITICAL: All hooks must be at top level before any early returns

  // TASK 8: Memoize retry handler (Network error with retry button)
  const handleRetry = useCallback(() => {
    refetch();
  }, [refetch]);

  // PERFORMANCE: Memoize currentProject lookup to avoid recalculation on every render
  const currentProject = useMemo(
    () => projects?.find((p) => p.id === selectedProjectId),
    [projects, selectedProjectId]
  );

  // PERFORMANCE: Memoize callback to prevent child re-renders
  const handleValueChange = useCallback((value: string) => {
    if (value === "__create_new_project__") {
      onCreateProject();
    } else {
      onProjectChange(value);
    }
  }, [onCreateProject, onProjectChange]);

  // Delete button handler
  const handleDeleteClick = useCallback((project: Project, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent select item from triggering
    setProjectToDelete(project);
    setDeleteDialogOpen(true);
  }, []);

  // Delete success handler
  const handleDeleteSuccess = useCallback(() => {
    setProjectToDelete(null);
    setDeleteDialogOpen(false);
    onProjectDeleted?.();
  }, [onProjectDeleted]);

  // Loading state: show skeleton (prevents layout shift - Task 9)
  if (isLoading) {
    return (
      <div
        className="w-48 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse transition-opacity duration-200"
        role="status"
        aria-label="Loading projects"
      />
    );
  }

  // Error state: show error message with retry button (TASK 8: Gotcha #12)
  if (error) {
    return (
      <div className="flex items-center gap-2" role="alert" aria-live="assertive">
        <div className="text-sm text-red-600 dark:text-red-400">
          Failed to load projects
        </div>
        <button
          onClick={handleRetry}
          className="px-3 py-1 text-xs font-medium text-white bg-red-600 dark:bg-red-500 hover:bg-red-700 dark:hover:bg-red-600 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
          aria-label="Retry loading projects"
        >
          Retry
        </button>
      </div>
    );
  }

  // No projects: return null (EmptyProjectState shown at page level per PRP)
  if (!projects || projects.length === 0) {
    return null;
  }

  return (
    <>
    <Select.Root
      value={selectedProjectId || undefined}
      onValueChange={handleValueChange}
    >
      <Select.Trigger
        className="inline-flex items-center justify-between gap-2 px-4 py-2 rounded-lg min-w-[200px] bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-colors duration-200"
        aria-label="Select project"
        aria-haspopup="listbox"
      >
        <Select.Value
          placeholder="Select project..."
          className="text-gray-900 dark:text-gray-100"
        >
          {currentProject?.name || "Select project..."}
        </Select.Value>
        <Select.Icon>
          <ChevronDown className="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" />
        </Select.Icon>
      </Select.Trigger>

      {/* CRITICAL: Portal to escape Dialog focus trap (Gotcha #6) */}
      <Select.Portal>
        <Select.Content
          className="overflow-hidden rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 shadow-lg z-50"
          position="popper"
          sideOffset={5}
          role="listbox"
        >
          <Select.Viewport className="p-1">
            {/* Project items */}
            {projects.map((project) => (
              <Select.Item
                key={project.id}
                value={project.id}
                className="relative flex items-center justify-between px-8 py-2 pr-2 text-sm rounded-md cursor-pointer outline-none transition-colors duration-150 text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-blue-900/30 focus:bg-blue-50 dark:focus:bg-blue-900/30 focus:ring-2 focus:ring-inset focus:ring-blue-500 dark:focus:ring-blue-400 data-[state=checked]:bg-blue-100 dark:data-[state=checked]:bg-blue-900/50 data-[state=checked]:text-blue-700 dark:data-[state=checked]:text-blue-300 data-[state=checked]:font-medium"
                aria-label={`Select project: ${project.name}`}
              >
                {/* Checkmark indicator for selected project */}
                <Select.ItemIndicator className="absolute left-2 flex h-4 w-4 items-center justify-center">
                  <Check className="h-4 w-4" aria-hidden="true" />
                </Select.ItemIndicator>

                <Select.ItemText className="flex-1">{project.name}</Select.ItemText>

                {/* Delete button */}
                <button
                  onClick={(e) => handleDeleteClick(project, e)}
                  className="flex-shrink-0 p-1.5 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 dark:focus:ring-red-400"
                  aria-label={`Delete project: ${project.name}`}
                  title="Delete project"
                  type="button"
                >
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                </button>
              </Select.Item>
            ))}

            {/* Separator */}
            <Select.Separator className="h-px bg-gray-200 dark:bg-gray-700 my-1" role="separator" />

            {/* Create New Project action */}
            <Select.Item
              value="__create_new_project__"
              className="relative flex items-center gap-2 px-8 py-2 text-sm rounded-md cursor-pointer outline-none transition-colors duration-150 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 focus:bg-blue-50 dark:focus:bg-blue-900/30 focus:ring-2 focus:ring-inset focus:ring-blue-500 dark:focus:ring-blue-400 font-medium"
              aria-label="Create new project"
            >
              <FolderPlus className="h-4 w-4 absolute left-2" aria-hidden="true" />
              <Select.ItemText className="ml-6">
                Create New Project
              </Select.ItemText>
            </Select.Item>
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>

    {/* Delete confirmation dialog */}
    <DeleteProjectDialog
      open={deleteDialogOpen}
      onOpenChange={setDeleteDialogOpen}
      project={projectToDelete}
      onSuccess={handleDeleteSuccess}
    />
  </>
  );
});
