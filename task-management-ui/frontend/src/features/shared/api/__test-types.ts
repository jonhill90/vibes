/**
 * Type validation test file
 * This file validates that service methods return correct types
 */

import type { Project, ProjectCreate } from "../../projects/types/project";
import type { Task, TaskCreate } from "../../tasks/types/task";
import { projectService } from "../../projects/services/projectService";
import { taskService } from "../../tasks/services/taskService";

// Test Project Service Types
async function testProjectService() {
  // listProjects should return Promise<Project[]>
  const projects: Project[] = await projectService.listProjects();
  const _projectsWithPagination: Project[] = await projectService.listProjects(1, 10);

  // getProject should return Promise<Project>
  const project: Project = await projectService.getProject("test-id");

  // createProject should accept ProjectCreate and return Promise<Project>
  const createData: ProjectCreate = { name: "Test Project" };
  const created: Project = await projectService.createProject(createData);

  // updateProject should accept partial data and return Promise<Project>
  const updated: Project = await projectService.updateProject("id", { name: "Updated" });

  // deleteProject should return Promise<void>
  const _deleted: void = await projectService.deleteProject("id");

  // Verify Project type structure
  const _id: string = project.id;
  const _name: string = project.name;
  const _description: string | null = project.description;
  const _createdAt: string = project.created_at;
  const _updatedAt: string = project.updated_at;

  console.log("Project service types validated");
}

// Test Task Service Types
async function testTaskService() {
  // listTasks should return Promise<Task[]>
  const tasks: Task[] = await taskService.listTasks();
  const _filteredTasks: Task[] = await taskService.listTasks({
    project_id: "test",
    status: "todo",
    page: 1,
    per_page: 10,
  });

  // getTask should return Promise<Task>
  const task: Task = await taskService.getTask("test-id");

  // createTask should accept TaskCreate and return Promise<Task>
  const createData: TaskCreate = {
    title: "Test Task",
    status: "todo",
    priority: "medium",
  };
  const created: Task = await taskService.createTask(createData);

  // updateTask should accept partial data and return Promise<Task>
  const updated: Task = await taskService.updateTask("id", { title: "Updated" });

  // updateTaskPosition should return Promise<Task>
  const moved: Task = await taskService.updateTaskPosition("id", "doing", 2);

  // deleteTask should return Promise<void>
  const _deleted: void = await taskService.deleteTask("id");

  // getTasksByProject should return Promise<Task[]>
  const projectTasks: Task[] = await taskService.getTasksByProject("project-id");

  // Verify Task type structure
  const _id: string = task.id;
  const _projectId: string | null = task.project_id;
  const _title: string = task.title;
  const _description: string | null = task.description;
  const _status: "todo" | "doing" | "review" | "done" = task.status;
  const _assignee: string = task.assignee;
  const _priority: "low" | "medium" | "high" | "urgent" = task.priority;
  const _position: number = task.position;
  const _createdAt: string = task.created_at;
  const _updatedAt: string = task.updated_at;

  console.log("Task service types validated");
}

// Run validation
testProjectService().catch(console.error);
testTaskService().catch(console.error);
