-- Task Management UI - Database Schema
-- PostgreSQL 16 setup with proper indexes and constraints
-- Generated: 2025-10-06

-- Enable UUID extension for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- PATTERN: Custom enum types for type safety at database level
-- Prevents invalid values and provides clear contract
CREATE TYPE task_status AS ENUM ('todo', 'doing', 'review', 'done');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');

-- PROJECTS TABLE
-- Purpose: Organize tasks into projects/workspaces
CREATE TABLE IF NOT EXISTS projects (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core fields
    name TEXT NOT NULL,
    description TEXT,

    -- Timestamps (TIMESTAMPTZ includes timezone)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for sorting projects by creation date
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- TASKS TABLE
-- Purpose: Task items with 4-state workflow and position tracking
CREATE TABLE IF NOT EXISTS tasks (
    -- Primary key and relationships
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,

    -- Core task fields
    title TEXT NOT NULL,
    description TEXT,
    status task_status NOT NULL DEFAULT 'todo',
    assignee TEXT DEFAULT 'User',
    priority task_priority DEFAULT 'medium' NOT NULL,

    -- CRITICAL: Position for drag-and-drop ordering within status column
    -- Used for Kanban board queries: WHERE status = ? ORDER BY position
    position INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CRITICAL GOTCHA #7: PostgreSQL does NOT auto-index foreign keys
-- Must manually create indexes on ALL foreign key columns for performance

-- Index on project_id for filtering tasks by project
-- Query pattern: SELECT * FROM tasks WHERE project_id = ?
CREATE INDEX idx_tasks_project_id ON tasks(project_id);

-- Index on parent_task_id for hierarchical queries
-- Partial index: Only index non-null values to save space
-- Query pattern: SELECT * FROM tasks WHERE parent_task_id = ?
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id)
    WHERE parent_task_id IS NOT NULL;

-- Index on status for filtering by workflow state
-- Query pattern: SELECT * FROM tasks WHERE status = ?
CREATE INDEX idx_tasks_status ON tasks(status);

-- Index on assignee for filtering tasks by person
-- Query pattern: SELECT * FROM tasks WHERE assignee = ?
CREATE INDEX idx_tasks_assignee ON tasks(assignee);

-- CRITICAL: Composite index for Kanban board ordering
-- Query pattern: SELECT * FROM tasks WHERE status = ? ORDER BY position
-- This index enables efficient retrieval of tasks in display order
CREATE INDEX idx_tasks_status_position ON tasks(status, position);

-- Partial index for active tasks only
-- Query pattern: SELECT * FROM tasks WHERE status IN ('todo', 'doing', 'review')
-- Excludes 'done' tasks to save index space for common queries
CREATE INDEX idx_tasks_active ON tasks(project_id, status)
    WHERE status IN ('todo', 'doing', 'review');

-- AUTO-UPDATE TIMESTAMP TRIGGERS
-- Pattern: Automatically update updated_at column on any UPDATE

-- Trigger function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for tasks table
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for projects table
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

/**
 * SCHEMA DESIGN NOTES:
 *
 * 1. UUID Primary Keys:
 *    - Uses gen_random_uuid() for distributed-safe IDs
 *    - No auto-increment sequences
 *
 * 2. Foreign Keys:
 *    - project_id: CASCADE delete (delete tasks when project deleted)
 *    - parent_task_id: SET NULL (preserve child tasks if parent deleted)
 *
 * 3. Position Tracking:
 *    - INTEGER field for manual ordering
 *    - Composite index (status, position) for Kanban queries
 *    - Position reordering requires transaction (see task_service.py)
 *
 * 4. Enum Types:
 *    - task_status: 4-state workflow (todo → doing → review → done)
 *    - task_priority: 4 levels (low, medium, high, urgent)
 *
 * 5. Text Fields:
 *    - TEXT (not VARCHAR) for flexibility
 *    - No length limits at database level
 *
 * 6. Timestamps:
 *    - TIMESTAMPTZ (with timezone) not TIMESTAMP
 *    - Auto-update via triggers
 *
 * 7. Indexes:
 *    - Single column indexes on all foreign keys
 *    - Composite index (status, position) for Kanban
 *    - Partial index for active tasks
 *
 * CRITICAL GOTCHAS ADDRESSED:
 *
 * - Gotcha #7: All foreign keys have explicit indexes
 * - Gotcha #2: Position updates must use transactions with row locking
 *   (Implementation in task_service.py, not schema)
 * - Use TEXT not VARCHAR for flexibility
 * - Use TIMESTAMPTZ (with timezone) not TIMESTAMP
 * - Lock rows in consistent order (ORDER BY id) to prevent deadlocks
 *   (Implementation in task_service.py)
 *
 * QUERY PATTERNS OPTIMIZED:
 *
 * 1. Kanban Board:
 *    SELECT * FROM tasks
 *    WHERE project_id = ? AND status = ?
 *    ORDER BY position
 *    → Uses idx_tasks_status_position
 *
 * 2. Active Tasks:
 *    SELECT * FROM tasks
 *    WHERE project_id = ? AND status IN ('todo', 'doing', 'review')
 *    → Uses idx_tasks_active
 *
 * 3. Project Tasks:
 *    SELECT * FROM tasks WHERE project_id = ?
 *    → Uses idx_tasks_project_id
 *
 * 4. Task Hierarchy:
 *    SELECT * FROM tasks WHERE parent_task_id = ?
 *    → Uses idx_tasks_parent_id
 */
