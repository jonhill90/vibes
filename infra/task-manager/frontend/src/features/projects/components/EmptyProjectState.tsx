/**
 * EmptyProjectState - Onboarding component for zero projects scenario
 *
 * PURPOSE: Guide new users to create their first project
 *
 * FEATURES:
 * - Centered layout with clear messaging
 * - Primary CTA button to trigger project creation
 * - Dark mode support
 *
 * USAGE:
 * ```tsx
 * <EmptyProjectState onCreateClick={() => setCreateModalOpen(true)} />
 * ```
 */

import { FolderPlus } from "lucide-react";

interface EmptyProjectStateProps {
  onCreateClick: () => void;
}

export const EmptyProjectState = ({
  onCreateClick,
}: EmptyProjectStateProps) => {
  return (
    <div
      className="h-full flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-900 px-4"
      role="main"
      aria-label="Empty project state"
    >
      <div className="text-center max-w-md">
        {/* Icon */}
        <div className="mb-6 flex justify-center" aria-hidden="true">
          <div className="rounded-full bg-blue-100 dark:bg-blue-900/30 p-4">
            <FolderPlus
              className="w-12 h-12 text-blue-600 dark:text-blue-400"
              strokeWidth={1.5}
            />
          </div>
        </div>

        {/* Heading */}
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3">
          No Projects Yet
        </h2>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 mb-8 leading-relaxed">
          Projects help you organize your tasks. Create your first project to
          get started with task management.
        </p>

        {/* CTA Button */}
        <button
          onClick={onCreateClick}
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
          aria-label="Create your first project"
        >
          <FolderPlus className="w-5 h-5" aria-hidden="true" />
          Create Your First Project
        </button>
      </div>
    </div>
  );
};
