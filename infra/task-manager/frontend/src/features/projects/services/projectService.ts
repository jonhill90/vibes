/**
 * Project Service - API methods for project CRUD
 *
 * PATTERN: Service layer with typed responses
 * - Returns typed data (not axios response directly)
 * - Handles errors at API client level
 * - Uses types from features/projects/types
 */

import apiClient from "../../shared/api/apiClient";
import type { Project, ProjectCreate } from "../types/project";

/**
 * Project Update type - all fields optional
 */
export interface ProjectUpdate {
  name?: string;
  description?: string;
}

/**
 * Project Service - CRUD operations for projects
 */
class ProjectService {
  /**
   * List all projects with optional pagination
   *
   * @param page - Page number (default 1)
   * @param perPage - Items per page (default 100)
   * @returns Promise<Project[]>
   */
  async listProjects(page = 1, perPage = 100): Promise<Project[]> {
    const response = await apiClient.get<{ projects: Project[] }>("/api/projects", {
      params: { page, per_page: perPage },
    });
    return response.data.projects;
  }

  /**
   * Get a single project by ID
   *
   * @param id - Project ID
   * @returns Promise<Project>
   * @throws ApiError if not found (404)
   */
  async getProject(id: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/api/projects/${id}`);
    return response.data;
  }

  /**
   * Create a new project
   *
   * @param data - Project creation data
   * @returns Promise<Project>
   * @throws ApiError if validation fails (422)
   */
  async createProject(data: ProjectCreate): Promise<Project> {
    const response = await apiClient.post<Project>("/api/projects", data);
    return response.data;
  }

  /**
   * Update an existing project
   *
   * @param id - Project ID
   * @param data - Project update data (partial)
   * @returns Promise<Project>
   * @throws ApiError if not found (404) or validation fails (422)
   */
  async updateProject(id: string, data: ProjectUpdate): Promise<Project> {
    const response = await apiClient.patch<Project>(`/api/projects/${id}`, data);
    return response.data;
  }

  /**
   * Delete a project
   *
   * @param id - Project ID
   * @returns Promise<void>
   * @throws ApiError if not found (404)
   */
  async deleteProject(id: string): Promise<void> {
    await apiClient.delete(`/api/projects/${id}`);
  }
}

// Export singleton instance
export const projectService = new ProjectService();
