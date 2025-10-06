// Task types matching backend Pydantic models

export type TaskStatus = "todo" | "doing" | "review" | "done";
export type TaskPriority = "low" | "medium" | "high" | "urgent";

export interface Task {
  id: string;
  project_id: string | null;
  parent_task_id: string | null;
  title: string;
  description: string | null;
  status: TaskStatus;
  assignee: string;
  priority: TaskPriority;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  project_id?: string;
  title: string;
  description?: string;
  status?: TaskStatus;
  assignee?: string;
  priority?: TaskPriority;
  position?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  assignee?: string;
  priority?: TaskPriority;
  position?: number;
}
