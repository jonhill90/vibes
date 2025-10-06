"""Create initial tables for task management

Revision ID: 001
Revises:
Create Date: 2025-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create initial schema with projects and tasks tables.

    CRITICAL: This migration includes:
    - Custom enum types for type safety
    - All foreign key indexes (Gotcha #7)
    - Composite index for Kanban ordering
    - Auto-update timestamp triggers
    """

    # Enable UUID extension
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Create custom enum types
    op.execute("""
        CREATE TYPE task_status AS ENUM ('todo', 'doing', 'review', 'done')
    """)

    op.execute("""
        CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent')
    """)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('NOW()'))
    )

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('todo', 'doing', 'review', 'done',
                                    name='task_status'), nullable=False,
                  server_default='todo'),
        sa.Column('assignee', sa.Text(), server_default='User'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent',
                                      name='task_priority'), nullable=False,
                  server_default='medium'),
        sa.Column('position', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'],
                                ondelete='SET NULL')
    )

    # CRITICAL: Create indexes on ALL foreign keys (Gotcha #7)
    # PostgreSQL does NOT auto-index foreign keys

    # Projects indexes
    op.create_index('idx_projects_created_at', 'projects',
                    ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # Tasks indexes
    op.create_index('idx_tasks_project_id', 'tasks', ['project_id'])

    # Partial index for parent_task_id (only non-null values)
    op.create_index('idx_tasks_parent_id', 'tasks', ['parent_task_id'],
                    postgresql_where=sa.text('parent_task_id IS NOT NULL'))

    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_assignee', 'tasks', ['assignee'])

    # CRITICAL: Composite index for Kanban ordering
    # Enables efficient queries: WHERE status = ? ORDER BY position
    op.create_index('idx_tasks_status_position', 'tasks',
                    ['status', 'position'])

    # Partial index for active tasks (exclude 'done')
    op.create_index('idx_tasks_active', 'tasks', ['project_id', 'status'],
                    postgresql_where=sa.text(
                        "status IN ('todo', 'doing', 'review')"
                    ))

    # Create auto-update timestamp trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create triggers for auto-updating updated_at
    op.execute("""
        CREATE TRIGGER update_tasks_updated_at
            BEFORE UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_projects_updated_at
            BEFORE UPDATE ON projects
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """
    Drop all tables and custom types.

    IMPORTANT: Order matters - drop triggers first, then tables, then types.
    """

    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks")
    op.execute("DROP TRIGGER IF EXISTS update_projects_updated_at ON projects")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables (CASCADE handles foreign keys)
    op.drop_table('tasks')
    op.drop_table('projects')

    # Drop custom enum types
    op.execute("DROP TYPE IF EXISTS task_priority")
    op.execute("DROP TYPE IF EXISTS task_status")

    # Note: Not dropping pgcrypto extension as it may be used by other schemas
