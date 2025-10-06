-- Source: /Users/jon/source/vibes/repos/Archon/migration/complete_setup.sql
-- Lines: 822-840
-- Pattern: PostgreSQL task table with JSONB fields
-- Extracted: 2025-10-06
-- Relevance: 9/10 - Database schema reference

-- PATTERN: Task Table Schema with Position Tracking
-- Key features:
-- 1. UUID primary keys for distributed systems
-- 2. Foreign key relationships with CASCADE
-- 3. JSONB fields for flexible metadata (sources, code_examples)
-- 4. task_order for drag-and-drop positioning
-- 5. Soft delete with archived fields
-- 6. Timestamps with automatic NOW() defaults

CREATE TABLE IF NOT EXISTS archon_tasks (
  -- Primary key and relationships
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
  parent_task_id UUID REFERENCES archon_tasks(id) ON DELETE CASCADE, -- For hierarchical tasks

  -- Core task fields
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  status task_status DEFAULT 'todo', -- Custom enum type: todo, doing, review, done
  assignee TEXT DEFAULT 'User' CHECK (assignee IS NOT NULL AND assignee != ''),
  task_order INTEGER DEFAULT 0, -- CRITICAL: For drag-and-drop position within status column
  priority task_priority DEFAULT 'medium' NOT NULL, -- Custom enum: low, medium, high, critical
  feature TEXT, -- Optional feature label for grouping

  -- PATTERN: JSONB fields for flexible metadata
  sources JSONB DEFAULT '[]'::jsonb, -- Array of source references
  code_examples JSONB DEFAULT '[]'::jsonb, -- Array of code example references

  -- PATTERN: Soft delete fields
  archived BOOLEAN DEFAULT false,
  archived_at TIMESTAMPTZ NULL,
  archived_by TEXT NULL,

  -- PATTERN: Automatic timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PATTERN: Custom enum types for type safety
CREATE TYPE task_status AS ENUM ('todo', 'doing', 'review', 'done');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'critical');

-- PATTERN: Indexes for performance
-- Index on project_id for filtering tasks by project
CREATE INDEX idx_tasks_project_id ON archon_tasks(project_id);

-- Index on status for filtering by workflow state
CREATE INDEX idx_tasks_status ON archon_tasks(status);

-- Index on assignee for filtering tasks by person/agent
CREATE INDEX idx_tasks_assignee ON archon_tasks(assignee);

-- CRITICAL: Composite index for ordered retrieval within status column
-- Used for Kanban board queries: WHERE status = ? ORDER BY task_order
CREATE INDEX idx_tasks_status_position ON archon_tasks(status, task_order);

-- Index on archived flag for filtering out soft-deleted tasks
CREATE INDEX idx_tasks_archived ON archon_tasks(archived) WHERE archived IS NOT NULL;

-- PATTERN: GIN index for JSONB fields (if doing searches)
-- CREATE INDEX idx_tasks_sources_gin ON archon_tasks USING GIN (sources);
-- CREATE INDEX idx_tasks_code_examples_gin ON archon_tasks USING GIN (code_examples);

-- PATTERN: Trigger for automatic updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_archon_tasks_updated_at
    BEFORE UPDATE ON archon_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

/**
 * WHAT TO MIMIC:
 *
 * 1. Position Tracking:
 *    - task_order INTEGER for manual ordering
 *    - Composite index (status, task_order) for efficient queries
 *    - Used for drag-and-drop position within each column
 *
 * 2. JSONB Fields:
 *    - Flexible storage for arrays (sources, code_examples)
 *    - Default to empty array '[]'::jsonb
 *    - Optional GIN indexes for searching JSONB content
 *
 * 3. Soft Delete:
 *    - archived BOOLEAN flag
 *    - archived_at timestamp for audit
 *    - archived_by for tracking who archived
 *    - Index with WHERE clause for performance
 *
 * 4. Enums:
 *    - Custom types for status and priority
 *    - Type safety at database level
 *    - Prevents invalid values
 *
 * 5. Timestamps:
 *    - created_at and updated_at with NOW() defaults
 *    - Trigger for automatic updated_at on UPDATE
 *
 * WHAT TO ADAPT:
 *
 * - Enum values: Change status/priority values for your workflow
 * - JSONB fields: Adjust to your metadata needs
 * - Indexes: Add/remove based on query patterns
 * - Foreign keys: Update table references for your schema
 *
 * WHAT TO SKIP:
 *
 * - parent_task_id if not supporting hierarchical tasks
 * - archived fields if using hard delete
 * - JSONB fields if storing metadata separately
 *
 * POSITION REORDERING PATTERN:
 *
 * When moving a task to a new position:
 * 1. Get all tasks with position >= new position
 * 2. Increment their position by 1
 * 3. Insert new task at desired position
 *
 * See task_service.py create_task() for implementation.
 */
