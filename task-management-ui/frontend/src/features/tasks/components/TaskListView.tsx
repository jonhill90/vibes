/**
 * TaskListView - Filterable table view with sorting and inline editing
 *
 * PURPOSE: Display tasks in a table format with filtering, sorting, and pagination
 *
 * KEY PATTERNS:
 * 1. URL query params for filter state (not local state) - enables shareable URLs
 * 2. Debounced filter changes to reduce API calls
 * 3. Inline status editing with optimistic updates
 * 4. Click row to open task detail modal
 *
 * GOTCHAS ADDRESSED:
 * - Use URL query params for filters (Gotcha from PRP)
 * - Debounce filter changes to reduce API calls
 */

import { useState, useMemo, useCallback, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import type { Task, TaskStatus, TaskPriority } from "../types/task";
import { useProjectTasks, useUpdateTask } from "../hooks/useTaskQueries";

interface TaskListViewProps {
  projectId: string;
  onTaskClick?: (task: Task) => void;
}

type SortField = "created_at" | "updated_at" | "title" | "status" | "priority";
type SortOrder = "asc" | "desc";

export const TaskListView = ({ projectId, onTaskClick }: TaskListViewProps) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: tasks = [], isLoading } = useProjectTasks(projectId);
  const updateTask = useUpdateTask(projectId);

  // CRITICAL: Use URL query params for filter state (enables shareable URLs)
  const statusFilter = searchParams.get("status") as TaskStatus | null;
  const assigneeFilter = searchParams.get("assignee");
  const priorityFilter = searchParams.get("priority") as TaskPriority | null;
  const sortField = (searchParams.get("sort") as SortField) || "created_at";
  const sortOrder = (searchParams.get("order") as SortOrder) || "desc";
  const page = parseInt(searchParams.get("page") || "1", 10);
  const perPage = 20;

  // Debounce filter changes
  const [debouncedFilters, setDebouncedFilters] = useState({
    status: statusFilter,
    assignee: assigneeFilter,
    priority: priorityFilter,
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters({
        status: statusFilter,
        assignee: assigneeFilter,
        priority: priorityFilter,
      });
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [statusFilter, assigneeFilter, priorityFilter]);

  // Filter and sort tasks
  const filteredAndSortedTasks = useMemo(() => {
    let filtered = tasks;

    // Apply filters
    if (debouncedFilters.status) {
      filtered = filtered.filter((task) => task.status === debouncedFilters.status);
    }
    if (debouncedFilters.assignee) {
      filtered = filtered.filter((task) =>
        task.assignee.toLowerCase().includes(debouncedFilters.assignee!.toLowerCase()),
      );
    }
    if (debouncedFilters.priority) {
      filtered = filtered.filter((task) => task.priority === debouncedFilters.priority);
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      let aVal: string | number = "";
      let bVal: string | number = "";

      switch (sortField) {
        case "created_at":
        case "updated_at":
          aVal = new Date(a[sortField]).getTime();
          bVal = new Date(b[sortField]).getTime();
          break;
        case "title":
          aVal = a.title.toLowerCase();
          bVal = b.title.toLowerCase();
          break;
        case "status":
          aVal = a.status;
          bVal = b.status;
          break;
        case "priority":
          // Priority order: urgent > high > medium > low
          const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
          aVal = priorityOrder[a.priority];
          bVal = priorityOrder[b.priority];
          break;
      }

      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [tasks, debouncedFilters, sortField, sortOrder]);

  // Pagination
  const paginatedTasks = useMemo(() => {
    const startIndex = (page - 1) * perPage;
    return filteredAndSortedTasks.slice(startIndex, startIndex + perPage);
  }, [filteredAndSortedTasks, page]);

  const totalPages = Math.ceil(filteredAndSortedTasks.length / perPage);

  // Get unique assignees for filter dropdown
  const uniqueAssignees = useMemo(() => {
    const assignees = new Set(tasks.map((task) => task.assignee));
    return Array.from(assignees).sort();
  }, [tasks]);

  // Update search params helper
  const updateSearchParams = useCallback(
    (updates: Record<string, string | null>) => {
      const newParams = new URLSearchParams(searchParams);
      Object.entries(updates).forEach(([key, value]) => {
        if (value === null || value === "") {
          newParams.delete(key);
        } else {
          newParams.set(key, value);
        }
      });
      setSearchParams(newParams);
    },
    [searchParams, setSearchParams],
  );

  // Handle inline status change
  const handleStatusChange = useCallback(
    (taskId: string, newStatus: TaskStatus) => {
      updateTask.mutate({ taskId, updates: { status: newStatus } });
    },
    [updateTask],
  );

  // Handle sort column click
  const handleSort = useCallback(
    (field: SortField) => {
      const newOrder = field === sortField && sortOrder === "asc" ? "desc" : "asc";
      updateSearchParams({ sort: field, order: newOrder });
    },
    [sortField, sortOrder, updateSearchParams],
  );

  // Priority badge color mapping
  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case "urgent":
        return "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400";
      case "high":
        return "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400";
      case "medium":
        return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400";
      case "low":
        return "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400";
    }
  };

  // Status badge color mapping
  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case "todo":
        return "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-400";
      case "doing":
        return "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400";
      case "review":
        return "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400";
      case "done":
        return "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 dark:text-gray-400">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Controls */}
      <div className="flex flex-wrap gap-4 p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Status
          </label>
          <select
            value={statusFilter || ""}
            onChange={(e) => updateSearchParams({ status: e.target.value || null, page: "1" })}
            className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="doing">Doing</option>
            <option value="review">Review</option>
            <option value="done">Done</option>
          </select>
        </div>

        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Assignee
          </label>
          <select
            value={assigneeFilter || ""}
            onChange={(e) => updateSearchParams({ assignee: e.target.value || null, page: "1" })}
            className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Assignees</option>
            {uniqueAssignees.map((assignee) => (
              <option key={assignee} value={assignee}>
                {assignee}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Priority
          </label>
          <select
            value={priorityFilter || ""}
            onChange={(e) => updateSearchParams({ priority: e.target.value || null, page: "1" })}
            className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Priorities</option>
            <option value="urgent">Urgent</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => handleSort("title")}
                >
                  <div className="flex items-center gap-1">
                    Title
                    {sortField === "title" && (
                      <span className="text-blue-500">{sortOrder === "asc" ? "↑" : "↓"}</span>
                    )}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => handleSort("status")}
                >
                  <div className="flex items-center gap-1">
                    Status
                    {sortField === "status" && (
                      <span className="text-blue-500">{sortOrder === "asc" ? "↑" : "↓"}</span>
                    )}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => handleSort("priority")}
                >
                  <div className="flex items-center gap-1">
                    Priority
                    {sortField === "priority" && (
                      <span className="text-blue-500">{sortOrder === "asc" ? "↑" : "↓"}</span>
                    )}
                  </div>
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Assignee
                </th>
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => handleSort("created_at")}
                >
                  <div className="flex items-center gap-1">
                    Created
                    {sortField === "created_at" && (
                      <span className="text-blue-500">{sortOrder === "asc" ? "↑" : "↓"}</span>
                    )}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => handleSort("updated_at")}
                >
                  <div className="flex items-center gap-1">
                    Updated
                    {sortField === "updated_at" && (
                      <span className="text-blue-500">{sortOrder === "asc" ? "↑" : "↓"}</span>
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {paginatedTasks.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    No tasks found
                  </td>
                </tr>
              ) : (
                paginatedTasks.map((task) => (
                  <tr
                    key={task.id}
                    onClick={() => onTaskClick?.(task)}
                    className="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {task.title}
                      </div>
                      {task.description && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-xs">
                          {task.description}
                        </div>
                      )}
                    </td>
                    <td
                      className="px-4 py-3"
                      onClick={(e) => e.stopPropagation()} // Prevent row click when changing status
                    >
                      <select
                        value={task.status}
                        onChange={(e) => handleStatusChange(task.id, e.target.value as TaskStatus)}
                        className={`text-xs px-2 py-1 rounded font-medium ${getStatusColor(task.status)} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        disabled={updateTask.isPending}
                      >
                        <option value="todo">To Do</option>
                        <option value="doing">Doing</option>
                        <option value="review">Review</option>
                        <option value="done">Done</option>
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-1 rounded font-medium ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">
                      {task.assignee}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500 dark:text-gray-400">
                      {new Date(task.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500 dark:text-gray-400">
                      {new Date(task.updated_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            Showing {(page - 1) * perPage + 1} to {Math.min(page * perPage, filteredAndSortedTasks.length)} of{" "}
            {filteredAndSortedTasks.length} tasks
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => updateSearchParams({ page: String(page - 1) })}
              disabled={page === 1}
              className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <div className="flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                <button
                  key={pageNum}
                  onClick={() => updateSearchParams({ page: String(pageNum) })}
                  className={`px-3 py-1 text-sm font-medium rounded-md ${
                    pageNum === page
                      ? "bg-blue-500 text-white"
                      : "text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                  }`}
                >
                  {pageNum}
                </button>
              ))}
            </div>
            <button
              onClick={() => updateSearchParams({ page: String(page + 1) })}
              disabled={page === totalPages}
              className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
