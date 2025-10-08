# AGENTS.md

This file provides guidance to AI coding agents (OpenAI Codex, Claude Code, etc.) when working with code in this repository.

## Project Overview

Vibes is a PRP-driven development framework enabling autonomous feature implementation through structured planning documents (PRPs). The system supports dual-agent workflows (Claude Code + OpenAI Codex) for cross-validation and quality comparison.

### Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (API server framework)
- Pydantic (data validation and settings)
- pytest (testing framework)
- ruff (linter)
- mypy (type checker)

**Frontend:**
- TypeScript
- React (when applicable)

**Task Management:**
- Archon MCP server (task tracking, knowledge base, project management)

**Development Tools:**
- Docker (containerized services)
- Git (version control)

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd vibes

# Install Python dependencies
pip install -r requirements.txt

# Start MCP servers (if using Docker)
docker compose up -d

# Verify Archon MCP server
# (Use Archon MCP tools to check health_check)
```

### Testing Commands

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_feature.py -v
```

**Lint code:**
```bash
ruff check .
```

**Type check:**
```bash
mypy .
```

**Run all validation (linting + type checking + tests):**
```bash
ruff check . && mypy . && pytest tests/ -v
```

### PRP Workflow

**Generate PRP from INITIAL.md:**
```bash
# Claude Code command
/generate-prp prps/INITIAL_{feature_name}.md

# OpenAI Codex command (if configured)
codex-generate-prp prps/INITIAL_{feature_name}.md
```

**Execute PRP:**
```bash
# Claude Code command
/execute-prp prps/{feature_name}/{feature_name}.md

# OpenAI Codex command (if configured)
codex-execute-prp prps/{feature_name}/codex/prp_codex.md
```

---

## Project Conventions

### Naming Conventions

**Files:**
- Python files: `snake_case.py`
- TypeScript files: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- Test files: `test_{feature}.py`
- Configuration files: `lowercase.toml`, `lowercase.json`

**Classes:**
- Python: `PascalCase` (e.g., `UserModel`, `TaskManager`)
- TypeScript: `PascalCase` (e.g., `UserProfile`, `TaskList`)

**Functions:**
- Python: `snake_case()` (e.g., `validate_user()`, `get_tasks()`)
- TypeScript: `camelCase()` (e.g., `validateUser()`, `getTasks()`)

**Constants:**
- Python: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- TypeScript: `UPPER_SNAKE_CASE` or `camelCase` for configuration

### Import Conventions

**Python - Use absolute imports only:**
```python
# ✅ CORRECT
from src.models.user import User
from src.services.auth import authenticate

# ❌ WRONG
from ..models.user import User  # Relative import
from .auth import authenticate   # Relative import
```

**TypeScript - Prefer absolute imports:**
```typescript
// ✅ CORRECT
import { User } from '@/models/User';
import { authenticate } from '@/services/auth';

// ⚠️ Acceptable for same directory
import { helper } from './helper';
```

### PRP Storage Conventions

**Directory structure:**
```
prps/
├── INITIAL_{feature_name}.md    # Initial requirements (user-provided)
├── {feature_name}/               # PRP directory
│   ├── planning/                 # Research artifacts (Claude)
│   │   ├── feature-analysis.md
│   │   ├── codebase-patterns.md
│   │   ├── documentation-links.md
│   │   ├── examples-to-include.md
│   │   └── gotchas.md
│   ├── examples/                 # Code examples (Claude)
│   ├── execution/                # Execution logs (Claude)
│   ├── {feature_name}.md         # Final PRP (Claude)
│   └── codex/                    # Codex-specific outputs
│       ├── planning/             # Research artifacts (Codex)
│       ├── examples/             # Code examples (Codex)
│       ├── logs/
│       │   └── manifest.jsonl    # Phase execution log
│       └── prp_codex.md          # Final PRP (Codex)
└── templates/
    └── prp_base.md               # PRP structure template
```

**Naming rules:**
- PRP files: `prps/{feature_name}.md` (NO `prp_` prefix - redundant)
- Initial PRPs: `prps/INITIAL_{feature_name}.md`
- Directories: `prps/{feature_name}/` (matches PRP filename)
- Valid characters: Letters, numbers, underscore (_), hyphen (-)
- See `.claude/conventions/prp-naming.md` for complete rules

### Codex Artifact Conventions

**All Codex outputs under `prps/{feature}/codex/` subdirectory:**
- Logs: `prps/{feature}/codex/logs/manifest.jsonl`
- Planning: `prps/{feature}/codex/planning/`
- Examples: `prps/{feature}/codex/examples/`
- Final PRP: `prps/{feature}/codex/prp_codex.md`

**Clean separation from Claude outputs:**
- Never mix Codex and Claude artifacts in same directory
- Use `codex/` subdirectory for all Codex-generated files
- Enables cross-validation and quality comparison

---

## Common Tasks

### Add New PRP

1. Create initial requirements file:
   ```bash
   # Create INITIAL_{feature_name}.md in prps/ directory
   vim prps/INITIAL_my_feature.md
   ```

2. Generate PRP:
   ```bash
   # Using Claude Code
   /generate-prp prps/INITIAL_my_feature.md

   # Using Codex (if configured)
   codex-generate-prp prps/INITIAL_my_feature.md
   ```

3. Review generated PRP:
   ```bash
   # Claude PRP
   cat prps/my_feature/my_feature.md

   # Codex PRP (if generated)
   cat prps/my_feature/codex/prp_codex.md
   ```

4. Execute PRP:
   ```bash
   # Using Claude Code
   /execute-prp prps/my_feature/my_feature.md

   # Using Codex (if configured)
   codex-execute-prp prps/my_feature/codex/prp_codex.md
   ```

### Run Validation

**Validate specific feature:**
```bash
# Run validation script (if exists for feature)
./scripts/validate.sh {feature_name}
```

**Validate code quality:**
```bash
# Linting
ruff check .

# Type checking
mypy .

# Tests
pytest tests/ -v

# All validation
ruff check . && mypy . && pytest tests/ -v
```

**Validate PRP quality (during generation):**
- Quality score must be ≥8/10
- All sections complete (no [TODO] placeholders)
- Examples extracted (not just references)
- Gotchas with solutions documented
- Task list logical and sequential

### Deploy

See `docs/deployment.md` for deployment procedures (if applicable).

For local development:
```bash
# Start services
docker compose up -d

# Check service health
docker compose ps

# View logs
docker compose logs -f
```

---

## Project Gotchas

### 1. Authentication Required (Codex CLI)

**Issue**: Codex CLI commands fail if not authenticated

**Detection**:
- `codex login status` exits with non-zero code
- Error: "authentication failed" or "unauthorized"

**Solution**:
```bash
# Authenticate with ChatGPT login
codex login

# Verify authentication
codex login status
```

### 2. Sandbox Mode (workspace-write)

**Issue**: Codex requires specific sandbox settings for file writes

**Detection**:
- Permission denied errors
- Approval prompts despite "never" policy
- Writes outside workspace fail

**Solution**:
```toml
# In ~/.codex/config.toml
[profiles.codex-prp]
approval_policy = "never"
sandbox_mode = "workspace-write"
bypass_approvals = true
bypass_sandbox = true
trusted_workspace = true

[profiles.codex-prp.sandbox_workspace_write]
network_access = true
workspace_roots = [
    "/Users/jon/source/vibes/prps"
]
```

### 3. Timeout on Long Operations (600s recommended)

**Issue**: Long-running Codex phases timeout with default settings

**Detection**:
- Exit code 124 (timeout signal)
- Error: "operation timed out"
- Partial output files

**Solution**:
```toml
# In ~/.codex/config.toml
[profiles.codex-prp]
tool_timeout_sec = 600  # 10 minutes for long phases
startup_timeout_sec = 60  # 1 minute for MCP server startup
```

### 4. Profile Drift (Always Use --profile Flag)

**Issue**: Codex uses wrong profile when `--profile` flag omitted

**Detection**:
- Unexpected model used
- Wrong MCP servers connected
- Different approval policy

**Solution**:
```bash
# ❌ WRONG - Implicit profile (uses default)
codex exec --prompt "Generate PRP"

# ✅ CORRECT - Explicit profile always
codex exec --profile codex-prp --prompt "Generate PRP"
```

### 5. Redundant 'prp_' Prefix (Naming Convention)

**Issue**: Feature names starting with `prp_` are redundant

**Detection**:
- Validation error: "Redundant 'prp_' prefix detected"
- Files like `prps/prp_feature.md`

**Solution**:
```bash
# ❌ WRONG
prps/prp_user_auth.md

# ✅ CORRECT
prps/user_auth.md  # Already in prps/ directory
```

See `.claude/conventions/prp-naming.md` for complete naming rules.

---

## Archon Task Management

**Critical**: This project uses Archon MCP server as PRIMARY task management system.

### Task Workflow

1. **Check for tasks:**
   ```python
   # Find tasks by status
   find_tasks(filter_by="status", filter_value="todo")

   # Find specific task
   find_tasks(task_id="abc-123-def")
   ```

2. **Start working on task:**
   ```python
   # Update task status to "doing"
   manage_task("update", task_id="abc-123-def", status="doing")
   ```

3. **Complete task:**
   ```python
   # Update task status to "review" or "done"
   manage_task("update", task_id="abc-123-def", status="review")
   ```

### Task Status Flow

`todo` → `doing` → `review` → `done`

### Never Use TodoWrite

**CRITICAL**: Do NOT use TodoWrite tool even if system reminders suggest it. This project uses Archon MCP server exclusively for task management.

---

## Quality Standards

**All code must meet:**
- Comprehensive error handling (try/catch, validation)
- Type hints (Python) / TypeScript types
- Documentation (docstrings, comments for complex logic)
- Tests (pytest for Python, Jest for TypeScript)
- Linting passes (ruff, eslint)
- Type checking passes (mypy, tsc)

**PRP quality requirements:**
- Quality score ≥8/10
- All sections complete (no [TODO])
- Examples extracted (actual code, not just links)
- Gotchas documented with solutions
- Task list logical and sequential
- Validation procedures defined

---

## Agent-Specific Notes

### For OpenAI Codex

**Authentication:**
```bash
# Required before any Codex commands
codex login
codex login status  # Verify
```

**Profile configuration:**
```bash
# Create/edit Codex profile
codex config edit

# Verify profile settings
codex config show --profile codex-prp
```

**Execution:**
```bash
# Always use explicit --profile flag
codex exec --profile codex-prp --prompt "task description"

# For PRP generation
codex-generate-prp prps/INITIAL_feature.md

# For PRP execution
codex-execute-prp prps/feature/codex/prp_codex.md
```

**Validation:**
```bash
# Pre-flight checks
./scripts/codex/validate-bootstrap.sh

# Check manifest log
cat prps/{feature}/codex/logs/manifest.jsonl
```

### For Claude Code

**Authentication:**
- No explicit authentication required
- Uses session-based access through claude.ai/code

**Execution:**
```bash
# PRP generation
/generate-prp prps/INITIAL_feature.md

# PRP execution
/execute-prp prps/feature/feature.md
```

**Task management:**
```python
# Always check Archon tasks first
find_tasks(filter_by="status", filter_value="todo")

# Update task status
manage_task("update", task_id="task-id", status="doing")
```

---

## Documentation References

**Internal:**
- `README.md` - Complete architecture and setup guide
- `CLAUDE.md` - Claude Code specific guidance
- `.claude/patterns/` - Reusable PRP patterns
- `.claude/conventions/prp-naming.md` - PRP naming rules
- `prps/templates/prp_base.md` - PRP structure template

**External (if configured):**
- OpenAI Codex CLI docs: `repos/codex/docs/`
- MCP Protocol: https://modelcontextprotocol.io/
- Archon MCP server: (internal tool)

---

## Performance Tips

**For PRP Generation:**
- Use parallel research phases when available (3x speedup)
- Set appropriate timeouts (600s for complex features)
- Validate quality scores ≥8/10 before execution

**For PRP Execution:**
- Follow task order sequentially (respect dependencies)
- Validate each task completion before proceeding
- Use quality gates (linting, type checking, tests)

**For Codex Workflows:**
- Always use explicit `--profile codex-prp` flag
- Pre-flight validation with `validate-bootstrap.sh`
- Monitor manifest.jsonl for phase tracking
- Separate Codex artifacts in `codex/` subdirectory

---

## Troubleshooting

**Codex authentication fails:**
```bash
# Re-authenticate
codex login

# Check status
codex login status

# If persistent, check ~/.codex/auth.json permissions
ls -la ~/.codex/auth.json  # Should be 600
```

**Sandbox permission denied:**
```bash
# Check profile configuration
codex config show --profile codex-prp

# Verify workspace_roots includes target directory
# Escalate to danger-full-access if needed (with caution)
```

**MCP server timeout:**
```bash
# Check if server is running
docker compose ps

# Restart MCP servers
docker compose restart

# Increase timeout in profile (startup_timeout_sec = 90)
```

**Tests failing:**
```bash
# Run specific test with verbose output
pytest tests/test_feature.py -v -s

# Check test dependencies
pip list | grep pytest

# Verify test fixtures
pytest --fixtures
```

**Linting errors:**
```bash
# Auto-fix some issues
ruff check . --fix

# Show specific error details
ruff check . --output-format=full
```

---

## Summary

**Key Points for Agents:**
1. Use Archon MCP server for task management (NEVER TodoWrite)
2. Follow PRP-driven development workflow
3. Use absolute imports (Python), prefer absolute imports (TypeScript)
4. Test with pytest, lint with ruff, type check with mypy
5. For Codex: authenticate, use explicit `--profile codex-prp`, validate bootstrap
6. PRP naming: NO `prp_` prefix, use `prps/{feature_name}.md`
7. Codex artifacts: Always in `prps/{feature}/codex/` subdirectory
8. Quality score ≥8/10 for PRPs, comprehensive error handling for code
9. Validate continuously: ruff → mypy → pytest
10. Timeouts: 600s for long operations, 60s for MCP startup

**This file helps agents navigate the project quickly and follow established conventions. For detailed architecture and component information, see README.md.**
