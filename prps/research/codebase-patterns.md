# Codebase Patterns: devcontainer_vibesbox_integration

## Search Summary

### Archon Code Examples Searched
- Query 1: "devcontainer lifecycle" → 5 results found (low relevance)
- Query 2: "docker compose orchestration" → 5 results found (moderate relevance)
- Query 3: "bash automation helpers" → 5 results found (environment setup patterns)
- Query 4: "health check polling" → 5 results found (instrumentation patterns)
- Query 5: "colored terminal output" → 5 results found (output formatting patterns)
- Query 6: "progress indicator spinner" → 5 results found (low relevance)

### Local Codebase Searches
- Pattern 1: `.devcontainer/**/*.sh` → 5 scripts found (postCreate, setup-network, test-docker, test-network, validate-config)
- Pattern 2: `mcp-vibesbox-server/**/*.sh` → 0 scripts found (Docker-based, no shell scripts)
- Pattern 3: `^function |^[a-z_]+\(\)` in `.devcontainer/scripts/*.sh` → 4 helper functions found
- Pattern 4: Docker compose files → Found mcp-vibesbox-server/docker-compose.yml

### Total Patterns Found
- Archon Examples: 30 code examples reviewed
- Local Examples: 6 files analyzed
- Combined Insights: 8 actionable patterns documented

## Similar Implementations Found

### Pattern 1: Helper Function Output Formatting

**Source**: [File: /Users/jon/source/vibes/.devcontainer/scripts/postCreate.sh]

**What It Demonstrates**:
Consistent colored output pattern for status messages with emojis and ANSI color codes.

**Code Structure**:
```
.devcontainer/
├── scripts/
│   ├── postCreate.sh          # Main setup script with helpers
│   ├── test-docker.sh         # Docker validation
│   ├── test-network.sh        # Network connectivity tests
│   └── setup-network.sh       # Network creation/connection
```

**Key Code Pattern**:
```bash
# Helper functions for colored output
info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }

# Usage example
info "Checking vibesbox status..."
success "Container started"
warn "VNC server not ready yet"
error "Failed to connect to Docker daemon"
```

**Naming Convention**:
- Files: snake_case with hyphens (test-docker.sh, setup-network.sh)
- Functions: lowercase, short verbs (info, success, warn, error)
- Variables: UPPERCASE for globals (DOCKER_PATH, CONTAINER_ID)
- Variables: lowercase for locals (server, container_name)

**What to Mimic**:
- Exact color codes and emoji symbols for consistency
- printf formatting pattern (not echo)
- Four-function pattern: info, success, warn, error
- ANSI escape sequences: `\033[36m` (cyan), `\033[32m` (green), `\033[33m` (yellow), `\033[31m` (red)
- Reset code: `\033[0m`

**What to Adapt**:
- Add progress indicator function for long operations
- Consider adding debug() function for verbose output
- May need timeout indicators for health checks

### Pattern 2: Docker State Detection

**Source**: [File: /Users/jon/source/vibes/.devcontainer/scripts/test-docker.sh]

**What It Demonstrates**:
Comprehensive Docker connectivity and permission checking pattern.

**Code Structure**:
```bash
# Test Docker CLI access
if command -v docker &>/dev/null; then
    echo "✅ Docker CLI found: $(which docker)"

    # Test Docker version
    if docker --version &>/dev/null; then
        echo "✅ Docker version: $(docker --version)"
    fi

    # Test Docker daemon connectivity
    if docker info &>/dev/null; then
        echo "✅ Docker daemon accessible"
    else
        echo "❌ Docker daemon not accessible"
    fi
fi

# Test Docker socket permissions
if ls -la /var/run/docker.sock &>/dev/null; then
    echo "✅ Docker socket found"
    if [ -w /var/run/docker.sock ]; then
        echo "✅ Docker socket is writable"
    fi
fi

# Test group membership
if groups | grep -q docker; then
    echo "✅ User is in docker group"
fi
```

**Naming Convention**:
- Test scripts: `test-{component}.sh`
- Boolean checks: `if command -v ... &>/dev/null`
- Error suppression: `&>/dev/null` for silent checks

**What to Mimic**:
- Multi-level validation: CLI → version → daemon → socket → permissions
- Silent checks with `&>/dev/null` followed by verbose output
- Progressive validation (don't check daemon if CLI missing)
- Graceful degradation (continue even if checks fail)

**What to Adapt**:
- Apply same pattern to vibesbox: container existence → running state → VNC port → screenshot
- Return structured data (not just echo) for programmatic use
- Add timeout mechanism for health checks

### Pattern 3: Network Setup & Validation

**Source**: [File: /Users/jon/source/vibes/.devcontainer/scripts/setup-network.sh]

**What It Demonstrates**:
Idempotent network creation and connection pattern with error handling.

**Code Structure**:
```bash
# Check if network exists
if docker network ls | grep -q "vibes-network"; then
    echo "✅ vibes-network already exists"
else
    echo "⚠️  vibes-network not found, creating it..."
    if docker network create vibes-network 2>/dev/null; then
        echo "✅ Created vibes-network"
    else
        echo "❌ Failed to create vibes-network (might already exist)"
    fi
fi

# Try to connect current container to network
CONTAINER_ID=$(hostname)
if docker network connect vibes-network "$CONTAINER_ID" 2>/dev/null; then
    echo "✅ Connected to vibes-network"
else
    echo "⚠️  Could not connect to vibes-network (might already be connected)"
fi
```

**Naming Convention**:
- Setup scripts: `setup-{component}.sh`
- Variables for dynamic values: `CONTAINER_ID`, `NETWORK_NAME`
- Error redirection: `2>/dev/null` for expected errors

**What to Mimic**:
- Idempotent operations (safe to run multiple times)
- Check-before-action pattern
- Graceful handling of "already exists" errors
- Clear success/failure messaging

**What to Adapt**:
- Apply to vibesbox: check container → create/start if needed
- Configurable network name (environment variable)
- Return exit codes for scripting

### Pattern 4: Docker Compose Configuration

**Source**: [File: /Users/jon/source/vibes/mcp/mcp-vibesbox-server/docker-compose.yml]

**What It Demonstrates**:
Complete vibesbox service definition with systemd, VNC, and network configuration.

**Code Structure**:
```yaml
services:
  mcp-vibesbox-server:
    image: vibes/mcp-vibesbox-server:latest
    build: .
    container_name: mcp-vibesbox-server
    restart: unless-stopped
    privileged: true
    security_opt:
      - seccomp:unconfined
    cap_add:
      - SYS_ADMIN
      - SYS_RESOURCE
      - DAC_READ_SEARCH
    stop_signal: SIGRTMIN+3
    tmpfs:
      - /run
      - /run/lock
      - /tmp
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${VIBES_PATH:-/workspace/vibes}:/workspace/vibes:rw
      - mcp-vibesbox-workspace:/workspace
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    ports:
      - "5901:5901"  # VNC server
    command: ["/sbin/init"]

networks:
  default:
    name: vibes-network
    external: true

volumes:
  mcp-vibesbox-workspace:
```

**Naming Convention**:
- Service name: `mcp-vibesbox-server` (matches container name)
- Network name: `vibes-network` (external, pre-existing)
- Volume name: `{service}-workspace` pattern
- Environment variables: `${VAR:-default}` syntax

**What to Mimic**:
- Use environment variables for paths: `${VIBES_PATH:-/workspace/vibes}`
- External network reference: `external: true`
- Container naming convention: match service name
- VNC port: 5901 (standard)

**What to Adapt**:
- Make network name configurable
- Make VNC port configurable
- Support overriding container name

### Pattern 5: Tool Availability Checking

**Source**: [File: /Users/jon/source/vibes/.devcontainer/scripts/postCreate.sh]

**What It Demonstrates**:
Comprehensive tool availability checking with version extraction.

**Code Structure**:
```bash
# Check if tool exists
if command -v docker &>/dev/null; then
  DOCKER_PATH=$(which docker)
  DOCKER_VER=$(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',' || echo 'unknown')
  success "Docker CLI: found at $DOCKER_PATH (v$DOCKER_VER)"
else
  error "Docker CLI: NOT found"
fi

# Check Docker Compose (two possible commands)
if command -v docker-compose &>/dev/null || docker compose version &>/dev/null; then
  success "Docker Compose: available"
else
  warn "Docker Compose: NOT found"
fi
```

**Naming Convention**:
- Path variables: `{TOOL}_PATH`
- Version variables: `{TOOL}_VER`
- Fallback values: `|| echo 'unknown'` or `|| echo 'not found'`

**What to Mimic**:
- `command -v` for existence check (portable)
- `which` for path extraction
- Version parsing with `awk` and `tr`
- Multiple command variants (docker-compose vs docker compose)
- Fallback to 'unknown' on version extraction failure

**What to Adapt**:
- Check for ImageMagick (import command)
- Check for netcat (nc command)
- Verify vibesbox-specific dependencies

### Pattern 6: Container State Inspection

**Source**: [File: /Users/jon/source/vibes/.devcontainer/scripts/test-docker.sh]

**What It Demonstrates**:
Extracting specific information from Docker using format strings.

**Code Structure**:
```bash
if docker info &>/dev/null; then
    echo "✅ Docker daemon accessible"
    echo "  Container runtime: $(docker info --format '{{.ServerVersion}}')"
    echo "  Total containers: $(docker info --format '{{.Containers}}')"
fi
```

**Naming Convention**:
- Format templates: `--format '{{.FieldName}}'`
- Nested fields: `{{.Parent.Child}}`

**What to Mimic**:
- Use `--format` for structured data extraction
- Common docker inspect patterns:
  - `docker inspect --format '{{.State.Running}}' container_name`
  - `docker inspect --format '{{.State.Status}}' container_name`
  - `docker inspect --format '{{.NetworkSettings.Networks}}' container_name`
- Single-line extraction with command substitution

**What to Adapt**:
- Check if vibesbox container exists: `docker ps -a --filter name=mcp-vibesbox-server --format '{{.Names}}'`
- Check running state: `docker inspect --format '{{.State.Running}}' mcp-vibesbox-server`
- Get container uptime: `docker inspect --format '{{.State.StartedAt}}' mcp-vibesbox-server`

### Pattern 7: Network Connectivity Testing

**Source**: [File: /Users/jon/source/vibes/.devcontainer/scripts/test-network.sh]

**What It Demonstrates**:
Systematic network connectivity testing with multiple protocols.

**Code Structure**:
```bash
# Test DNS resolution and ping
MCP_SERVERS=("azure-mcp-server" "terraform-mcp-server" "mcp-vibes-server")

for server in "${MCP_SERVERS[@]}"; do
    if ping -c 1 -W 2 "$server" &>/dev/null; then
        echo "✅ $server - reachable"
    else
        echo "❌ $server - not reachable"
    fi
done

# Test HTTP connectivity
if curl -s -o /dev/null -w "%{http_code}" http://openmemory-ui:3000 | grep -q "200"; then
    echo "✅ openmemory-ui:3000 - HTTP 200"
else
    echo "❌ openmemory-ui:3000 - not responding"
fi
```

**Naming Convention**:
- Arrays: `UPPERCASE_NAMES` for lists
- Loop variable: lowercase `server`, `host`, etc.
- Timeout flags: `-c 1 -W 2` (1 ping, 2 second wait)

**What to Mimic**:
- Ping with timeout: `ping -c 1 -W 2`
- Silent curl: `curl -s -o /dev/null`
- HTTP status code extraction: `-w "%{http_code}"`
- Array iteration for multiple targets

**What to Adapt**:
- VNC port check: `nc -z localhost 5901` (netcat zero-I/O mode)
- Container IP check: `docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container`
- Port listening check: `ss -tlnp | grep :5901` or `lsof -i :5901`

### Pattern 8: Devcontainer Integration Hook

**Source**: [File: /Users/jon/source/vibes/.devcontainer/devcontainer.json]

**What It Demonstrates**:
Standard devcontainer postCreateCommand hook pattern.

**Code Structure**:
```json
{
  "name": "Vibes Development Workspace",
  "dockerComposeFile": "docker-compose.yml",
  "service": "devcontainer",
  "workspaceFolder": "/workspace",
  "postCreateCommand": "bash /usr/local/share/postCreate.sh",
  "remoteUser": "vscode"
}
```

**Naming Convention**:
- Hook: `postCreateCommand` (runs after container created)
- Script location: `/usr/local/share/` (copied in Dockerfile)
- Script name: `postCreate.sh` (matches hook name)

**What to Mimic**:
- Use absolute path for script: `/usr/local/share/ensure-vibesbox.sh`
- Run as remoteUser (vscode) by default
- Non-blocking execution (background with `&` if needed)

**What to Adapt**:
- Chain multiple scripts: `bash /usr/local/share/postCreate.sh && bash /usr/local/share/ensure-vibesbox.sh`
- OR: Integrate vibesbox check into existing postCreate.sh
- Consider separate script for modularity

## Architectural Patterns

### Service Layer Organization

**Pattern Observed**: Scripts are modular and single-purpose, with helper functions defined at the top.

**Example from Codebase**:
```bash
#!/usr/bin/env bash
set -euo pipefail

# ┌───────────────────────────────────────────────────────────────────┐
# │                        Script Title                                │
# └───────────────────────────────────────────────────────────────────┘

#── helper functions ────────────────────────────────────────────────
info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }

#── main logic ──────────────────────────────────────────────────────
info "Starting operation..."
# ... implementation ...
success "Operation complete!"
```

**Application to devcontainer_vibesbox_integration**:
- Create `ensure-vibesbox.sh` with same structure
- Define helpers at top (reuse existing pattern)
- Organize into sections with ASCII art headers
- Keep functions small and testable

### Data Access Patterns

**Pattern Observed**: Use Docker CLI as API, parse output with format strings and awk/grep.

**Example from Codebase**:
```bash
# Direct API calls
CONTAINER_EXISTS=$(docker ps -a --filter name=mcp-vibesbox-server --format '{{.Names}}' 2>/dev/null)
CONTAINER_RUNNING=$(docker inspect --format '{{.State.Running}}' mcp-vibesbox-server 2>/dev/null)

# Parsing with awk
DOCKER_VER=$(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')

# Using grep for boolean checks
if docker network ls | grep -q "vibes-network"; then
    # network exists
fi
```

**Recommendations**:
- Use `docker inspect --format` for structured data
- Use `docker ps --filter` for existence checks
- Parse JSON output with `jq` if complex (optional)
- Suppress errors with `2>/dev/null` for expected failures
- Store results in variables for reuse

### Error Handling Patterns

**Pattern Observed**: Graceful degradation with clear error messages and non-blocking failures.

**Example from Codebase**:
```bash
# Pattern 1: Try operation, warn if fails but continue
if docker network connect vibes-network "$CONTAINER_ID" 2>/dev/null; then
    echo "✅ Connected to vibes-network"
else
    echo "⚠️  Could not connect to vibes-network (might already be connected)"
fi

# Pattern 2: Check before action, provide context
if docker info &>/dev/null; then
    success "Docker daemon accessible"
else
    warn "Docker daemon not accessible"
    warn "This might be expected in some devcontainer setups"
fi

# Pattern 3: Set errexit but disable for expected failures
set -euo pipefail
if some_command 2>/dev/null || true; then
    # won't exit script if command fails
fi
```

**Best Practices Identified**:
- Use `set -euo pipefail` for safety
- Disable errexit selectively with `|| true`
- Provide context in error messages (why it might fail)
- Don't block devcontainer startup on vibesbox failures
- Log errors but continue execution

### Testing Patterns

**Test File Organization**: Test scripts colocated with main scripts in `.devcontainer/scripts/`

**Fixture Patterns**:
```bash
# Test data as arrays
MCP_SERVERS=("azure-mcp-server" "terraform-mcp-server" "mcp-vibes-server")

# Test iteration
for server in "${MCP_SERVERS[@]}"; do
    # run test
done
```

**Test Structure**:
- Naming: test-{component}.sh
- Organization: Same directory as implementation
- Fixtures: Inline arrays or variables at top
- Assertions: Visual output with ✅/❌ emojis

## File Organization

### Typical Structure for Similar Features

```
.devcontainer/
├── devcontainer.json           # Main config (postCreateCommand hook)
├── docker-compose.yml          # Devcontainer service definition
└── scripts/
    ├── postCreate.sh           # Main setup (calls other scripts)
    ├── ensure-vibesbox.sh      # NEW: Vibesbox lifecycle management
    ├── check-vibesbox.sh       # NEW: Health checking logic
    ├── setup-network.sh        # Network setup (existing)
    ├── test-docker.sh          # Docker validation (existing)
    └── test-network.sh         # Network tests (existing)

mcp/mcp-vibesbox-server/
├── docker-compose.yml          # Vibesbox service definition
├── Dockerfile                  # Image build instructions
└── (server code)

# Helper functions exported to user shell
/etc/profile.d/
└── vibesbox-helpers.sh         # NEW: CLI helper functions
```

**Rationale**:
- Scripts in `.devcontainer/scripts/` are copied to `/usr/local/share/` during build
- Helper functions in `/etc/profile.d/` are sourced on shell startup
- Separation of concerns: lifecycle (ensure) vs health (check)
- Existing pattern already established

### Module Naming Conventions

- Main lifecycle script: `ensure-vibesbox.sh`
- Health checking: `check-vibesbox.sh`
- Helper functions: `vibesbox-helpers.sh`
- Test modules: `test-vibesbox.sh`
- Configuration: Environment variables (no separate config file)

**Consistency Check**:
- Follows existing `setup-network.sh`, `test-docker.sh` pattern
- Hyphenated names (not underscores)
- Descriptive verb-noun format
- `.sh` extension explicit

## Integration Points

### Database Integration

**Pattern from Codebase**: N/A - No database in this feature

**Migrations**: N/A
**Models**: N/A
**Queries**: N/A

### API Routes

**Pattern from Codebase**: N/A - Bash scripting, no API routes

### Configuration Management

**Pattern from Codebase**: Environment variables with defaults

**Environment Variables**:
```bash
# From docker-compose.yml
VIBES_PATH=${VIBES_PATH:-/workspace/vibes}

# From scripts
CONTAINER_NAME=${VIBESBOX_CONTAINER_NAME:-mcp-vibesbox-server}
NETWORK_NAME=${VIBESBOX_NETWORK:-vibes-network}
VNC_PORT=${VIBESBOX_VNC_PORT:-5901}
```

**Config Files**: None (pure environment variable approach)

**Secrets**:
- Docker socket access controlled via group membership
- No VNC password by default (localhost only)
- API keys managed separately (ANTHROPIC_API_KEY pattern)

## Code Style & Conventions

### Naming Conventions Summary

| Element | Convention | Example |
|---------|------------|---------|
| Files | kebab-case | ensure-vibesbox.sh |
| Functions | lowercase | info, success, check_container_running |
| Variables (global) | UPPERCASE | CONTAINER_NAME, VIBES_PATH |
| Variables (local) | lowercase | container_id, vnc_port |
| Constants | UPPERCASE | DEFAULT_VNC_PORT=5901 |
| Environment Vars | UPPERCASE_SNAKE_CASE | VIBESBOX_CONTAINER_NAME |

### Documentation Patterns

**Docstring Style**: Inline comments with ASCII art headers

**Example**:
```bash
#!/usr/bin/env bash
set -euo pipefail

# ┌───────────────────────────────────────────────────────────────────┐
# │                    Vibesbox Lifecycle Manager                     │
# └───────────────────────────────────────────────────────────────────┘
#
# Purpose: Auto-detect, start, and verify MCP Vibesbox Server
# Usage: bash ensure-vibesbox.sh
# Environment:
#   VIBESBOX_CONTAINER_NAME - Container name (default: mcp-vibesbox-server)
#   VIBESBOX_NETWORK        - Docker network (default: vibes-network)
#   VIBESBOX_VNC_PORT       - VNC port (default: 5901)
#   VIBESBOX_AUTO_BUILD     - Auto-build without prompt (default: false)
#

#── helper functions ────────────────────────────────────────────────
# ... functions ...

#── main logic ──────────────────────────────────────────────────────
# ... implementation ...
```

### Import Organization

**Pattern Observed**: N/A - Bash scripts don't have imports

**Sourcing Pattern**:
```bash
# Source shared functions (if separated)
if [ -f "/usr/local/share/vibesbox-common.sh" ]; then
    source "/usr/local/share/vibesbox-common.sh"
fi
```

## Recommendations for devcontainer_vibesbox_integration

### Patterns to Follow

1. **Helper Function Output Pattern**: Exact color codes and formatting
   - Source: postCreate.sh
   - Benefit: Consistent UX across all scripts, familiar to users

2. **Multi-Level Validation Pattern**: Progressive checks (CLI → daemon → container → VNC → screenshot)
   - Source: test-docker.sh
   - Benefit: Clear diagnostic information, graceful degradation

3. **Idempotent Operations Pattern**: Check-before-action with safe retry
   - Source: setup-network.sh
   - Benefit: Safe to run multiple times, no side effects

4. **Environment Variable Configuration**: ${VAR:-default} syntax
   - Source: docker-compose.yml
   - Benefit: Flexible, no config file parsing, easy override

5. **Docker Format String Extraction**: Use --format for structured data
   - Source: test-docker.sh
   - Benefit: Reliable parsing, no fragile grep/awk chains

6. **ASCII Art Headers**: Sections clearly marked with box drawing
   - Source: postCreate.sh
   - Benefit: Readable, scannable, professional appearance

### Patterns to Avoid

1. **Anti-pattern**: Blocking operations without timeout
   - Seen in: N/A (not present in codebase - good!)
   - Issue: Would hang devcontainer startup
   - Alternative: All health checks must have timeouts

2. **Anti-pattern**: Hardcoded paths or values
   - Seen in: Avoided in existing scripts
   - Issue: Not flexible, breaks in different environments
   - Alternative: Use environment variables with defaults

3. **Anti-pattern**: Complex error handling with multiple exit codes
   - Seen in: N/A (scripts use simple success/fail)
   - Issue: Would complicate devcontainer integration
   - Alternative: Graceful degradation, warn but continue

### New Patterns Needed

If no similar codebase patterns exist:

1. **Gap**: Health check polling with timeout
   - **What's missing**: No existing pattern for "retry operation for N seconds"
   - **Recommendation**:
     ```bash
     wait_for_condition() {
       local timeout=$1
       local check_command=$2
       local start_time=$(date +%s)

       while true; do
         if eval "$check_command"; then
           return 0
         fi

         local current_time=$(date +%s)
         local elapsed=$((current_time - start_time))

         if [ $elapsed -ge $timeout ]; then
           return 1
         fi

         sleep 2
       done
     }

     # Usage:
     if wait_for_condition 30 "nc -z localhost 5901"; then
       success "VNC server ready"
     else
       warn "VNC server timeout after 30s"
     fi
     ```
   - **Rationale**: VNC startup is async, need polling mechanism
   - **Example**: Standard pattern from DevOps health check scripts

2. **Gap**: Screenshot capability testing
   - **What's missing**: No pattern for testing X11/VNC display functionality
   - **Recommendation**:
     ```bash
     test_screenshot() {
       local display="${1:-:1}"
       local output_file="/tmp/vibesbox-health-check.png"

       # Try to capture screenshot
       if DISPLAY="$display" import -window root "$output_file" 2>/dev/null; then
         # Verify file exists and is not empty
         if [ -s "$output_file" ]; then
           rm -f "$output_file"
           return 0
         fi
       fi
       return 1
     }
     ```
   - **Rationale**: Screenshot is definitive proof GUI automation works
   - **Example**: ImageMagick import command standard for headless testing

3. **Gap**: Progress indicators for long operations
   - **What's missing**: No visual feedback during docker compose build
   - **Recommendation**:
     ```bash
     show_progress() {
       local message="$1"
       local pid=$2

       info "$message"
       while kill -0 $pid 2>/dev/null; do
         printf "."
         sleep 1
       done
       echo ""
     }

     # Usage:
     docker compose build --progress=plain &>/tmp/build.log &
     BUILD_PID=$!
     show_progress "Building vibesbox image" $BUILD_PID
     wait $BUILD_PID
     ```
   - **Rationale**: Build takes 1-3 minutes, user needs feedback
   - **Example**: Common shell progress indicator pattern

4. **Gap**: CLI helper function export
   - **What's missing**: No pattern for making functions available in user shell
   - **Recommendation**:
     ```bash
     # Create /etc/profile.d/vibesbox-helpers.sh
     # Functions defined here are sourced on shell startup

     vibesbox-status() {
       bash /usr/local/share/check-vibesbox.sh
     }

     vibesbox-start() {
       docker compose -f /workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml start
     }

     vibesbox-stop() {
       docker compose -f /workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml stop
     }

     # ... more helpers ...
     ```
   - **Rationale**: Users need CLI access to vibesbox operations
   - **Example**: Standard Linux profile.d pattern for shell customization

## Archon Code Examples Referenced

### Example 1: Environment Configuration Pattern
- **Archon ID**: b8565aff9938938b
- **Relevance**: 6/10
- **Key Takeaway**: Environment variable configuration pattern with validation
- **Location in Archon**: GitHub context-engineering-intro commit

### Example 2: Docker Orchestration Pattern
- **Archon ID**: c0e629a894699314
- **Relevance**: 5/10
- **Key Takeaway**: Instrumentation and monitoring patterns for services
- **Location in Archon**: Pydantic AI documentation

### Example 3: Health Check Pattern
- **Archon ID**: c0e629a894699314
- **Relevance**: 4/10
- **Key Takeaway**: Polling and validation patterns for service health
- **Location in Archon**: Pydantic AI model instrumentation

## Local Files Referenced

### File 1: /Users/jon/source/vibes/.devcontainer/scripts/postCreate.sh
- **Lines**: 1-203
- **Pattern Type**: Helper functions, tool checking, configuration setup
- **Relevance**: Primary pattern source for output formatting and setup flow

### File 2: /Users/jon/source/vibes/.devcontainer/scripts/test-docker.sh
- **Lines**: 1-69
- **Pattern Type**: Multi-level Docker validation and state detection
- **Relevance**: Direct template for vibesbox health checking logic

### File 3: /Users/jon/source/vibes/.devcontainer/scripts/setup-network.sh
- **Lines**: 1-26
- **Pattern Type**: Idempotent network creation and connection
- **Relevance**: Pattern for vibesbox container startup logic

### File 4: /Users/jon/source/vibes/.devcontainer/scripts/test-network.sh
- **Lines**: 1-35
- **Pattern Type**: Network connectivity testing with multiple protocols
- **Relevance**: Pattern for VNC port checking and connectivity validation

### File 5: /Users/jon/source/vibes/mcp/mcp-vibesbox-server/docker-compose.yml
- **Lines**: 1-35
- **Pattern Type**: Complete service definition with systemd, VNC, networking
- **Relevance**: Core configuration to orchestrate in automation scripts

### File 6: /Users/jon/source/vibes/.devcontainer/devcontainer.json
- **Lines**: 1-44
- **Pattern Type**: Devcontainer configuration and hook integration
- **Relevance**: Integration point for vibesbox automation

---
Generated: 2025-10-04
Archon Examples Referenced: 3
Local Files Referenced: 6
Total Patterns Documented: 8
Feature: devcontainer_vibesbox_integration
