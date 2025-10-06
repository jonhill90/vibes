# Task Management UI

A self-hosted, containerized task management system with dual interfaces: a web UI for human oversight and an MCP server for AI assistant integration.

## Overview

This system provides a structured 4-state workflow (`todo` → `doing` → `review` → `done`) with project organization and drag-and-drop Kanban board capabilities. External AI assistants like Claude Code can manage tasks via the Model Context Protocol (MCP) server while humans monitor progress through the web interface.

**Architecture**:
- **Backend**: FastAPI + SQLAlchemy with async PostgreSQL support
- **Frontend**: React + TypeScript with TanStack Query and react-dnd
- **Database**: PostgreSQL 16 with auto-updating timestamps and composite indexes
- **Deployment**: Docker Compose with health checks and hot reload support
- **MCP Server**: Consolidated tools pattern for AI assistant integration

**Key Features**:
- Kanban board view with drag-and-drop task management
- List view with filtering, sorting, and inline editing
- Project/workspace organization for task grouping
- Real-time UI updates via smart HTTP polling (pauses when tab hidden)
- MCP server for AI assistant task management
- Data persistence across container restarts

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker**: Version 20.10 or higher ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0 or higher (included with Docker Desktop)

To verify your installation:
```bash
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Clone and Configure

```bash
# Navigate to the task-management-ui directory
cd task-management-ui

# Copy environment template
cp .env.example .env

# (Optional) Edit .env to customize ports, passwords, etc.
# nano .env
```

### 2. Start Services

```bash
# Build and start all services (database, backend, frontend)
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d
```

**First-time startup takes 2-3 minutes**:
1. PostgreSQL initializes database (10-15 seconds)
2. Backend waits for database health check, runs migrations (20-30 seconds)
3. Frontend builds and starts development server (60-90 seconds)

### 3. Access the Application

Once all health checks pass:

- **Web UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MCP Server**: `http://localhost:8051/mcp` (via `npx mcp-remote`)

### 4. Verify MCP Integration

Test the MCP server from Claude Code or another AI assistant:

```bash
# Connect to MCP server
npx mcp-remote http://localhost:8051/mcp

# Example MCP commands (in Claude Code):
# - find_tasks(filter_by="status", filter_value="todo")
# - manage_task("create", title="Test task", description="Testing MCP")
# - manage_task("update", task_id="<uuid>", status="doing")
```

---

## MCP Server Usage

The MCP server provides four consolidated tools for AI assistants to manage tasks and projects:

### 1. `find_tasks` - List, search, or get tasks

```python
# List all tasks
find_tasks()

# Get a specific task
find_tasks(task_id="550e8400-e29b-41d4-a716-446655440000")

# Filter by status
find_tasks(filter_by="status", filter_value="todo")

# Filter by project
find_tasks(filter_by="project", filter_value="<project-uuid>")

# Search by keyword
find_tasks(query="bug fix")

# Pagination
find_tasks(page=2, per_page=20)
```

**Parameters**:
- `query` (str, optional): Keyword search in title/description
- `task_id` (str, optional): UUID of specific task
- `filter_by` (str, optional): Field to filter by (`status`, `project`, `assignee`, `priority`)
- `filter_value` (str, optional): Value to match for filter
- `project_id` (str, optional): UUID of project to filter by
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 50)

### 2. `manage_task` - Create, update, or delete tasks

```python
# Create a new task
manage_task(
    action="create",
    title="Implement authentication",
    description="Add JWT-based authentication to API",
    status="todo",
    priority="high",
    assignee="AI Assistant"
)

# Update task status
manage_task(
    action="update",
    task_id="<uuid>",
    status="doing"
)

# Update multiple fields
manage_task(
    action="update",
    task_id="<uuid>",
    title="Implement OAuth authentication",
    priority="critical",
    status="review"
)

# Delete a task
manage_task(
    action="delete",
    task_id="<uuid>"
)
```

**Parameters**:
- `action` (str, required): `"create"`, `"update"`, or `"delete"`
- `task_id` (str, required for update/delete): UUID of task
- `project_id` (str, optional): UUID of project for task
- `title` (str, optional): Task title
- `description` (str, optional): Task description (supports Markdown)
- `status` (str, optional): `"todo"`, `"doing"`, `"review"`, or `"done"`
- `priority` (str, optional): `"low"`, `"medium"`, `"high"`, or `"critical"`
- `assignee` (str, optional): Name of task assignee
- `position` (float, optional): Manual ordering within status column

### 3. `find_projects` - List or get projects

```python
# List all projects
find_projects()

# Get a specific project
find_projects(project_id="<uuid>")

# Search by keyword
find_projects(query="authentication")
```

### 4. `manage_project` - Create, update, or delete projects

```python
# Create a project
manage_project(
    action="create",
    name="Authentication System",
    description="OAuth and JWT implementation"
)

# Update project
manage_project(
    action="update",
    project_id="<uuid>",
    name="Authentication & Authorization System"
)

# Delete project
manage_project(
    action="delete",
    project_id="<uuid>"
)
```

---

## Development Workflow

### Hot Reload

All services support hot reload during development:

- **Backend**: Changes to Python files trigger automatic reload (FastAPI `--reload`)
- **Frontend**: Vite detects file changes and hot-reloads the browser
- **Database**: Schema changes require manual migration (see below)

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Run Database Migrations

```bash
# Access backend container
docker exec -it taskmanager-backend bash

# Generate migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Exit container
exit
```

### Run Tests

```bash
# Backend tests (pytest)
docker exec -it taskmanager-backend pytest

# Frontend tests (vitest, when configured)
docker exec -it taskmanager-frontend npm test
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop services (preserves data)
docker-compose down

# Stop and remove volumes (deletes ALL data)
docker-compose down -v
```

### Rebuild After Changes

```bash
# Rebuild specific service
docker-compose up --build backend

# Rebuild all services
docker-compose up --build
```

---

## Environment Configuration

The `.env` file controls all service configuration. Key variables:

### Database Configuration
- `POSTGRES_DB`: Database name (default: `taskmanager`)
- `POSTGRES_USER`: Database username (default: `taskuser`)
- `POSTGRES_PASSWORD`: Database password (**change in production!**)
- `DATABASE_URL`: Full connection string (use `db` as hostname in Docker)
- `DB_PORT`: Exposed database port (default: `5432`)

### Backend Configuration
- `API_PORT`: FastAPI server port (default: `8000`)
- `MCP_PORT`: MCP server port (default: `8051`)
- `CORS_ORIGINS`: Allowed frontend URLs (comma-separated)
- `LOG_LEVEL`: Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)

### Frontend Configuration
- `FRONTEND_PORT`: React development server port (default: `3000`)
- `VITE_API_URL`: Backend API URL (use `http://localhost:8000` for browser access)

### General Configuration
- `ENVIRONMENT`: Deployment mode (`development`, `staging`, `production`)

**Example .env for local development**:
```env
POSTGRES_DB=taskmanager
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpass123
DATABASE_URL=postgresql+asyncpg://taskuser:taskpass123@db:5432/taskmanager
API_PORT=8000
MCP_PORT=8051
FRONTEND_PORT=3000
VITE_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## Troubleshooting

### Services Won't Start

**Symptom**: `docker-compose up` fails with health check errors

**Solutions**:
1. Check if ports are already in use:
   ```bash
   lsof -i :3000  # Frontend
   lsof -i :8000  # Backend API
   lsof -i :8051  # MCP server
   lsof -i :5432  # Database
   ```
2. Change ports in `.env` file if needed
3. Remove old containers and volumes:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

### Database Connection Errors

**Symptom**: Backend logs show "could not connect to server"

**Solutions**:
1. Wait 30 seconds for database initialization (first-time startup)
2. Check database health:
   ```bash
   docker-compose logs db
   docker exec -it taskmanager-db pg_isready -U taskuser -d taskmanager
   ```
3. Verify `DATABASE_URL` in `.env` uses `db` as hostname (not `localhost`)

### Frontend Can't Connect to Backend

**Symptom**: Web UI shows "Network Error" or API calls fail

**Solutions**:
1. Verify `VITE_API_URL=http://localhost:8000` in `.env`
2. Check backend health:
   ```bash
   curl http://localhost:8000/health
   ```
3. Verify CORS configuration in `.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000
   ```
4. Check browser console for CORS errors

### MCP Server Not Responding

**Symptom**: `npx mcp-remote http://localhost:8051/mcp` fails

**Solutions**:
1. Verify MCP port in `.env`:
   ```env
   MCP_PORT=8051
   ```
2. Check backend logs for MCP server startup:
   ```bash
   docker-compose logs backend | grep MCP
   ```
3. Test MCP health endpoint:
   ```bash
   curl http://localhost:8051/health
   ```

### Hot Reload Not Working

**Symptom**: Code changes don't trigger automatic reload

**Solutions**:
1. Verify volume mounts in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./backend:/app
     - ./frontend:/app
   ```
2. Restart the specific service:
   ```bash
   docker-compose restart backend
   docker-compose restart frontend
   ```
3. Check for file permission issues (especially on Windows/WSL)

### Data Not Persisting

**Symptom**: Tasks disappear after `docker-compose down`

**Solutions**:
1. Verify named volume in `docker-compose.yml`:
   ```yaml
   volumes:
     taskmanager-db-data:
       driver: local
   ```
2. Don't use `-v` flag when stopping:
   ```bash
   docker-compose down    # Preserves data
   # NOT: docker-compose down -v  # Deletes data
   ```
3. Check volume exists:
   ```bash
   docker volume ls | grep taskmanager-db-data
   ```

### Permission Errors (Linux/WSL)

**Symptom**: "Permission denied" errors in logs

**Solutions**:
1. Check file ownership:
   ```bash
   ls -la backend/ frontend/
   ```
2. Fix permissions:
   ```bash
   sudo chown -R $USER:$USER backend/ frontend/
   ```
3. For PostgreSQL data volume, use named volume (not bind mount)

### Slow Performance

**Symptom**: API calls take > 1 second

**Solutions**:
1. Check database indexes:
   ```sql
   -- Connect to database
   docker exec -it taskmanager-db psql -U taskuser -d taskmanager

   -- Verify indexes exist
   \d tasks
   ```
2. Enable query logging in `.env`:
   ```env
   LOG_LEVEL=DEBUG
   ```
3. Check Docker resource limits (Docker Desktop → Settings → Resources)

---

## Production Deployment

**IMPORTANT**: Before deploying to production:

1. **Update `.env` security settings**:
   ```env
   POSTGRES_PASSWORD=<strong-random-password>
   ENVIRONMENT=production
   LOG_LEVEL=WARNING
   ```

2. **Restrict CORS origins**:
   ```env
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Use HTTPS for API URL**:
   ```env
   VITE_API_URL=https://api.yourdomain.com
   ```

4. **Configure database backups**:
   ```bash
   # Backup database
   docker exec taskmanager-db pg_dump -U taskuser taskmanager > backup.sql

   # Restore database
   cat backup.sql | docker exec -i taskmanager-db psql -U taskuser taskmanager
   ```

5. **Use production-ready frontend build**:
   - Update `frontend/Dockerfile` to use `npm run build` instead of `npm run dev`
   - Serve static files via Nginx or CDN

6. **Enable HTTPS**:
   - Add reverse proxy (Nginx, Caddy, Traefik)
   - Configure SSL certificates (Let's Encrypt)

7. **Monitor logs and health checks**:
   - Set up log aggregation (ELK, Splunk, CloudWatch)
   - Configure uptime monitoring for health endpoints

---

## Architecture Details

### Database Schema

**Tasks Table**:
- `id` (UUID, primary key)
- `title` (VARCHAR 255, required)
- `description` (TEXT, optional)
- `status` (ENUM: todo, doing, review, done)
- `priority` (ENUM: low, medium, high, critical)
- `assignee` (VARCHAR 100, optional)
- `position` (FLOAT, for drag-and-drop ordering)
- `project_id` (UUID, foreign key to projects, optional)
- `created_at` (TIMESTAMP, auto-generated)
- `updated_at` (TIMESTAMP, auto-updated)

**Indexes**:
- Composite index on `(status, position)` for Kanban queries
- Index on `project_id` for project filtering
- Partial index on active tasks (`WHERE status IN ('todo', 'doing', 'review')`)

**Projects Table**:
- `id` (UUID, primary key)
- `name` (VARCHAR 255, required)
- `description` (TEXT, optional)
- `created_at` (TIMESTAMP, auto-generated)
- `updated_at` (TIMESTAMP, auto-updated)

### API Endpoints

**Task Endpoints**:
- `GET /tasks` - List tasks (with filters, pagination)
- `GET /tasks/{task_id}` - Get task details
- `POST /tasks` - Create task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task

**Project Endpoints**:
- `GET /projects` - List projects
- `GET /projects/{project_id}` - Get project details
- `POST /projects` - Create project
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project

**Health Endpoints**:
- `GET /health` - Backend health check
- `GET /health/db` - Database connectivity check

### MCP Server Implementation

The MCP server runs alongside the FastAPI backend on port 8051. It provides consolidated tools following the Archon pattern:
- **Consolidated tools**: `find_tasks`, `manage_task`, `find_projects`, `manage_project`
- **Response optimization**: Descriptions truncated to 1000 chars, arrays replaced with counts
- **AI-friendly errors**: Structured responses with suggestions

---

## Contributing

### Code Style
- **Backend**: Follow PEP 8, use type hints, run `ruff` for linting
- **Frontend**: Follow Airbnb style guide, enable TypeScript strict mode
- **Commits**: Use conventional commits format (`feat:`, `fix:`, `docs:`, etc.)

### Testing
- **Backend**: Write pytest tests for all endpoints and services
- **Frontend**: Write Vitest tests for components and hooks
- **Integration**: Test MCP tools with real AI assistant (Claude Code)

### Pull Requests
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Run linters and tests
5. Submit PR with detailed description

---

## License

This project is part of the vibes ecosystem. See top-level LICENSE file for details.

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [vibes/issues](https://github.com/yourusername/vibes/issues)
- **Documentation**: See `/Users/jon/source/vibes/README.md` for overall architecture
- **MCP Specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
