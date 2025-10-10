/**
 * Task Service - API methods for task CRUD
 *
 * PATTERN: Service layer with typed responses
 * - Returns typed data (not axios response directly)
 * - Supports filtering by project_id, status, assignee
 * - Handles position updates via dedicated endpoint
 */

import apiClient from "../../shared/api/apiClient";
import type { Task, TaskCreate, TaskStatus, TaskUpdate } from "../types/task";

/**
 * Task filters for list endpoint
 */
export interface TaskFilters {
  project_id?: string;
  status?: TaskStatus;
  assignee?: string;
  page?: number;
  per_page?: number;
}

/**
 * Paginated task list response
 */
export interface TaskListResponse {
  tasks: Task[];
  total_count: number;
  page: number;
  per_page: number;
}

/**
 * Single task response
 */
export interface TaskResponse {
  task: Task;
  message?: string;
}

/**
 * Position update request
 */
export interface TaskPositionUpdate {
  status: TaskStatus;
  position: number;
}

/**
 * Task Service - CRUD operations for tasks
 */
class TaskService {
  /**
   * List tasks with optional filters and pagination
   *
   * @param filters - Optional filters (project_id, status, assignee, page, per_page)
   * @returns Promise<Task[]>
   */
  async listTasks(filters?: TaskFilters): Promise<Task[]> {
    const params: Record<string, string | number | undefined> = {};

    if (filters) {
      if (filters.project_id) params.project_id = filters.project_id;
      if (filters.status) params.status = filters.status;
      if (filters.assignee) params.assignee = filters.assignee;
      if (filters.page) params.page = filters.page;
      if (filters.per_page) params.per_page = filters.per_page;
    }

    const response = await apiClient.get<TaskListResponse>("/api/tasks/", { params });
    return response.data.tasks;
  }

  /**
   * Get a single task by ID
   *
   * @param id - Task ID
   * @returns Promise<Task>
   * @throws ApiError if not found (404)
   */
  async getTask(id: string): Promise<Task> {
    const response = await apiClient.get<TaskResponse>(`/api/tasks/${id}`);
    return response.data.task;
  }

  /**
   * Create a new task
   *
   * @param data - Task creation data
   * @returns Promise<Task>
   * @throws ApiError if validation fails (422)
   */
  async createTask(data: TaskCreate): Promise<Task> {
    const response = await apiClient.post<TaskResponse>("/api/tasks/", data);
    return response.data.task;
  }

  /**
   * Update an existing task
   *
   * @param id - Task ID
   * @param data - Task update data (partial)
   * @returns Promise<Task>
   * @throws ApiError if not found (404) or validation fails (422)
   */
  async updateTask(id: string, data: TaskUpdate): Promise<Task> {
    const response = await apiClient.patch<TaskResponse>(`/api/tasks/${id}`, data);
    return response.data.task;
  }

  /**
   * Update task position (status + position)
   *
   * PATTERN: Dedicated endpoint for atomic position updates
   * - Uses PATCH /api/tasks/{id}/position
   * - Backend handles position reordering atomically
   *
   * @param id - Task ID
   * @param status - New status column
   * @param position - New position in column
   * @returns Promise<Task>
   * @throws ApiError if not found (404) or validation fails (422)
   */
  async updateTaskPosition(id: string, status: TaskStatus, position: number): Promise<Task> {
    const response = await apiClient.patch<TaskResponse>(`/api/tasks/${id}/position`, {
      status,
      position,
    });
    return response.data.task;
  }

  /**
   * Delete a task
   *
   * @param id - Task ID
   * @returns Promise<void>
   * @throws ApiError if not found (404)
   */
  async deleteTask(id: string): Promise<void> {
    await apiClient.delete(`/api/tasks/${id}`);
  }

  /**
   * Get tasks by project (convenience method)
   *
   * PATTERN: Matches Archon's getTasksByProject pattern
   * - Used by useProjectTasks hook
   * - Filters by project_id
   *
   * @param projectId - Project ID
   * @returns Promise<Task[]>
   */
  async getTasksByProject(projectId: string): Promise<Task[]> {
    return this.listTasks({ project_id: projectId, per_page: 1000 });
  }
}

// Export singleton instance
export const taskService = new TaskService();
