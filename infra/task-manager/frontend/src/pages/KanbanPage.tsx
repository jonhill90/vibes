/**
 * KanbanPage - Page wrapper for Kanban board view with multi-project support
 *
 * PURPOSE: Provides project selection and board rendering
 *
 * PATTERN: Page-level component with state management and localStorage persistence
 *
 * FEATURES:
 * - Multi-project support via ProjectSelector dropdown
 * - Selection persists across page reloads via localStorage
 * - Empty state guides users to create their first project
 * - Automatic validation of stored project ID
 * - Handles deleted projects gracefully
 *
 * GOTCHAS ADDRESSED:
 * - Gotcha #4: Validates stored project ID against available projects
 * - Auto-selects first project if stored ID is invalid (deleted project case)
 * - Clears storage when no projects exist
 */

import { useCallback, useEffect, useState } from "react";
import { KanbanBoard } from "../features/tasks/components/KanbanBoard";
import { CreateProjectModal } from "../features/projects/components/CreateProjectModal";
import { EmptyProjectState } from "../features/projects/components/EmptyProjectState";
import { ProjectSelector } from "../features/projects/components/ProjectSelector";
import { useProjects } from "../features/projects/hooks/useProjectQueries";
import ProjectStorage from "../features/projects/utils/projectStorage";
import { ErrorBoundary } from "../features/shared/components/ErrorBoundary";

export const KanbanPage = () => {
  // State: Selected project ID and modal open state
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  // Get projects from query hook
  const { data: projects, isLoading } = useProjects();

  // CRITICAL: Initialize and validate selected project
  // Handles cases: no projects, deleted project, first load
  useEffect(() => {
    if (!projects || projects.length === 0) {
      // No projects: clear selection and storage
      setSelectedProjectId(null);
      ProjectStorage.clear();
      return;
    }

    const storedId = ProjectStorage.get();
    const storedProjectExists = storedId && projects.some((p) => p.id === storedId);

    if (storedProjectExists) {
      // Stored project exists: use it
      setSelectedProjectId(storedId);
    } else {
      // Stored project deleted or doesn't exist: auto-select first project
      const firstProject = projects[0];
      setSelectedProjectId(firstProject.id);
      ProjectStorage.set(firstProject.id);
    }
  }, [projects]);

  // CRITICAL: Persist changes to localStorage
  // When selectedProjectId changes, save to storage
  useEffect(() => {
    if (selectedProjectId) {
      ProjectStorage.set(selectedProjectId);
    }
  }, [selectedProjectId]);

  // PERFORMANCE: Memoize callback to prevent ProjectSelector re-renders (Task 12)
  const handleCreateProjectClick = useCallback(() => {
    setCreateModalOpen(true);
  }, []);

  // PERFORMANCE: Memoize callback for create modal success (Task 12)
  const handleProjectCreated = useCallback((project: { id: string }) => {
    setSelectedProjectId(project.id);
    setCreateModalOpen(false);
  }, []);

  // Loading state: show spinner while fetching projects
  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 transition-opacity duration-200" role="main" aria-label="Loading projects">
        <div className="flex flex-col items-center gap-3">
          <div
            className="w-8 h-8 border-4 border-blue-200 dark:border-blue-900 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"
            role="status"
            aria-label="Loading"
          />
          <div className="text-sm text-gray-600 dark:text-gray-400" aria-live="polite">Loading projects...</div>
        </div>
      </div>
    );
  }

  // Empty state: no projects - show onboarding
  if (!projects || projects.length === 0) {
    return (
      <>
        <EmptyProjectState onCreateClick={handleCreateProjectClick} />
        <CreateProjectModal
          open={createModalOpen}
          onOpenChange={setCreateModalOpen}
          onSuccess={handleProjectCreated}
        />
      </>
    );
  }

  // Initializing state: projects loaded but selection not yet initialized
  if (!selectedProjectId) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 transition-opacity duration-200" role="main" aria-label="Initializing">
        <div className="flex flex-col items-center gap-3">
          <div
            className="w-8 h-8 border-4 border-blue-200 dark:border-blue-900 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"
            role="status"
            aria-label="Loading"
          />
          <div className="text-sm text-gray-600 dark:text-gray-400" aria-live="polite">Initializing...</div>
        </div>
      </div>
    );
  }

  // Normal case: show header with ProjectSelector + main with KanbanBoard
  return (
    <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900 transition-opacity duration-200 animate-in fade-in">
      {/* Page Header with ProjectSelector */}
      <header className="bg-white dark:bg-gray-800 shadow-sm" role="banner">
        <div className="max-w-full px-6 py-4 flex items-center gap-4">
          {/* Project Selector Dropdown */}
          <nav aria-label="Project navigation">
            <ProjectSelector
              selectedProjectId={selectedProjectId}
              onProjectChange={setSelectedProjectId}
              onCreateProject={handleCreateProjectClick}
            />
          </nav>

          {/* Title Section */}
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              Task Management
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Organize your tasks with drag-and-drop Kanban board
            </p>
          </div>
        </div>
      </header>

      {/* Main Content - Kanban Board wrapped in ErrorBoundary (TASK 8: Catastrophic failures) */}
      <main className="flex-1 overflow-hidden" role="main" aria-label="Kanban board">
        <ErrorBoundary>
          <KanbanBoard projectId={selectedProjectId} />
        </ErrorBoundary>
      </main>

      {/* Create Project Modal */}
      <CreateProjectModal
        open={createModalOpen}
        onOpenChange={setCreateModalOpen}
        onSuccess={handleProjectCreated}
      />
    </div>
  );
};
