/**
 * TaskDetailModal - Full task editing modal with markdown preview
 *
 * PURPOSE: Edit task details in a modal dialog with all fields
 *
 * FEATURES:
 * - Form fields: title, description, status, priority, assignee
 * - Markdown preview for description
 * - Delete button with confirmation
 * - Optimistic updates via useUpdateTask/useDeleteTask
 * - Loading states during mutations
 * - Form validation before submit
 *
 * GOTCHAS ADDRESSED:
 * - Validate form before submitting
 * - Show loading state during mutation
 * - Close modal on successful save
 * - Prevent accidental deletion with confirmation
 */

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { Task, TaskStatus, TaskPriority } from "../types/task";
import { useUpdateTask, useDeleteTask } from "../hooks/useTaskQueries";

interface TaskDetailModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
}

const STATUSES: { value: TaskStatus; label: string }[] = [
  { value: "todo", label: "To Do" },
  { value: "doing", label: "Doing" },
  { value: "review", label: "Review" },
  { value: "done", label: "Done" },
];

const PRIORITIES: { value: TaskPriority; label: string }[] = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "urgent", label: "Urgent" },
];

export const TaskDetailModal = ({ task, isOpen, onClose, projectId }: TaskDetailModalProps) => {
  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<TaskStatus>("todo");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [assignee, setAssignee] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [validationError, setValidationError] = useState("");

  // Mutations
  const updateTask = useUpdateTask(projectId);
  const deleteTask = useDeleteTask(projectId);

  // Initialize form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
      setStatus(task.status);
      setPriority(task.priority);
      setAssignee(task.assignee);
      setValidationError("");
      setShowDeleteConfirm(false);
    }
  }, [task]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setShowPreview(false);
      setShowDeleteConfirm(false);
      setValidationError("");
    }
  }, [isOpen]);

  // PATTERN: Validate form before submitting (Gotcha #18)
  const validateForm = (): boolean => {
    if (!title.trim()) {
      setValidationError("Title is required");
      return false;
    }
    if (title.length > 200) {
      setValidationError("Title must be 200 characters or less");
      return false;
    }
    if (description.length > 10000) {
      setValidationError("Description must be 10,000 characters or less");
      return false;
    }
    setValidationError("");
    return true;
  };

  const handleSave = async () => {
    if (!task) return;

    // Validate before submitting
    if (!validateForm()) return;

    // Build updates object (only changed fields)
    const updates: Record<string, string | number> = {};
    if (title !== task.title) updates.title = title;
    if (description !== (task.description || "")) updates.description = description;
    if (status !== task.status) updates.status = status;
    if (priority !== task.priority) updates.priority = priority;
    if (assignee !== task.assignee) updates.assignee = assignee;

    // Only update if something changed
    if (Object.keys(updates).length === 0) {
      onClose();
      return;
    }

    // PATTERN: Show loading state during mutation (Gotcha #18)
    updateTask.mutate(
      { taskId: task.id, updates },
      {
        onSuccess: () => {
          // PATTERN: Close modal on successful save
          onClose();
        },
        onError: (error) => {
          setValidationError(error instanceof Error ? error.message : "Failed to update task");
        },
      },
    );
  };

  const handleDelete = () => {
    if (!task) return;

    deleteTask.mutate(task.id, {
      onSuccess: () => {
        onClose();
      },
      onError: (error) => {
        setValidationError(error instanceof Error ? error.message : "Failed to delete task");
        setShowDeleteConfirm(false);
      },
    });
  };

  // Don't render if not open or no task
  if (!isOpen || !task) return null;

  const isLoading = updateTask.isPending || deleteTask.isPending;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 z-40 transition-opacity"
        onClick={isLoading ? undefined : onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Edit Task</h2>
            <button
              onClick={onClose}
              disabled={isLoading}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-50"
              aria-label="Close modal"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content - Scrollable */}
          <div className="px-6 py-4 overflow-y-auto flex-1">
            {/* Validation Error */}
            {validationError && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                <p className="text-sm text-red-800 dark:text-red-300">{validationError}</p>
              </div>
            )}

            {/* Title Field */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                         bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent
                         disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="Enter task title"
              />
            </div>

            {/* Description Field with Preview Toggle */}
            <div className="mb-4">
              <div className="flex justify-between items-center mb-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Description
                </label>
                <button
                  type="button"
                  onClick={() => setShowPreview(!showPreview)}
                  disabled={isLoading}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50"
                >
                  {showPreview ? "Edit" : "Preview"}
                </button>
              </div>

              {showPreview ? (
                // Markdown Preview
                <div className="w-full min-h-[150px] px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                              bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 prose prose-sm dark:prose-invert max-w-none">
                  {description ? (
                    <ReactMarkdown>{description}</ReactMarkdown>
                  ) : (
                    <p className="text-gray-400 dark:text-gray-600 italic">No description</p>
                  )}
                </div>
              ) : (
                // Textarea Editor
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={isLoading}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed resize-y"
                  placeholder="Enter task description (Markdown supported)"
                />
              )}
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Markdown formatting supported
              </p>
            </div>

            {/* Status and Priority Row */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              {/* Status Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Status
                </label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as TaskStatus)}
                  disabled={isLoading}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {STATUSES.map((s) => (
                    <option key={s.value} value={s.value}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Priority Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Priority
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as TaskPriority)}
                  disabled={isLoading}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {PRIORITIES.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Assignee Field */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Assignee
              </label>
              <input
                type="text"
                value={assignee}
                onChange={(e) => setAssignee(e.target.value)}
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                         bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent
                         disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="Enter assignee name"
              />
            </div>

            {/* Metadata Display */}
            <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Created:</span>
                  <span className="ml-2 text-gray-700 dark:text-gray-300">
                    {new Date(task.created_at).toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Updated:</span>
                  <span className="ml-2 text-gray-700 dark:text-gray-300">
                    {new Date(task.updated_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Footer - Action Buttons */}
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-between">
            {/* Delete Button with Confirmation */}
            <div>
              {showDeleteConfirm ? (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Are you sure?</span>
                  <button
                    onClick={handleDelete}
                    disabled={isLoading}
                    className="px-3 py-1.5 bg-red-600 text-white rounded-md hover:bg-red-700
                             disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                  >
                    {deleteTask.isPending ? "Deleting..." : "Yes, Delete"}
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    disabled={isLoading}
                    className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md
                             text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800
                             disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={isLoading}
                  className="px-4 py-2 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400
                           rounded-md hover:bg-red-50 dark:hover:bg-red-900/20
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Delete Task
                </button>
              )}
            </div>

            {/* Save/Cancel Buttons */}
            <div className="flex gap-2">
              <button
                onClick={onClose}
                disabled={isLoading}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md
                         text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700
                         disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {updateTask.isPending ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Saving...
                  </>
                ) : (
                  "Save Changes"
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
