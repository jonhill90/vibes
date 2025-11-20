# Create Agent

Interactively create new domain expert or specialized agent with guided workflow.

## Usage

```
/create-agent [domain-name]
```

## Arguments

- `domain-name` (optional): Pre-specify the domain (e.g., "kubernetes", "docker", "aws")
  - If provided: Skip domain clarification, jump to responsibilities
  - If omitted: Interactive workflow prompts for all details

## Overview

This command guides you through creating a specialized domain expert agent using a 4-phase interactive workflow inspired by the agent-factory pattern. The workflow ensures all required agent fields are properly configured, skills are composed, and tool scoping follows security best practices.

## Interactive Workflow

### Phase 0: Clarification

The command asks 4 key questions to understand your agent requirements:

**1. Domain/Role** (if not provided as argument)
```
What domain/role is this agent for?
Examples: kubernetes-operator, docker-specialist, aws-architect, postgres-dba
Format: {domain}-{role} (lowercase, hyphens)
```

**2. Primary Responsibilities**
```
What are this agent's primary responsibilities? (2-3 sentences)
Be specific about what tasks this agent handles.

Example: "Manages PostgreSQL database operations including schema migrations,
query optimization, and backup/restore procedures. Implements best practices
for indexing and transaction management."
```

**3. Tool Requirements**
```
Which tools does this agent need? (Select from list)
[ ] Read - Read files
[ ] Write - Create new files
[ ] Edit - Modify existing files
[ ] Grep - Search file contents
[ ] Glob - Find files by pattern
[ ] Bash - Execute shell commands
[ ] WebSearch - Search documentation

Recommendation: Start minimal, add tools as needed
Security: Never include Task tool (sub-agents cannot spawn sub-agents)
```

**4. Skills to Compose**
```
Which existing skills should this agent use? (Check available skills)

Available skills from .claude/skills/:
[ ] task-management - Task decomposition and parallel execution
[ ] terraform-basics - Terraform IaC patterns
[ ] azure-basics - Azure cloud services

You can select multiple skills (comma-separated) or none.
```

### Phase 1: Generation

Based on your answers, the command generates a complete agent definition with:

**Frontmatter Structure:**
```yaml
---
name: {domain}-{role}
description: "{domain_title} specialist. USE PROACTIVELY for {use_cases}. Examples: {examples}"
tools: [minimal_tool_list]
skills: [selected_skills]
allowed_commands: [domain_specific_commands]
blocked_commands: [rm, dd, mkfs, curl, wget]
color: {visual_identifier}
---
```

**Key Generation Features:**
- **Specific Description**: Auto-generates use cases and examples from domain knowledge
- **Tool Scoping**: Minimal necessary tools (principle of least privilege)
- **Allowed Commands**: Domain-specific tool allowlist (e.g., `kubectl`, `docker`, `aws`)
- **Blocked Commands**: Standard dangerous commands always blocked
- **Skills Integration**: References to existing skills for domain knowledge
- **System Prompt**: Domain-specific prompt template with best practices

**Example Generated Content:**
```markdown
---
name: kubernetes-operator
description: "Kubernetes cluster operations specialist. USE PROACTIVELY for kubectl commands, manifest creation, deployment management, pod debugging. Examples: creating deployments, scaling replicas, troubleshooting pod failures."
tools: Read, Write, Edit, Grep, Glob, Bash
skills: [task-management]
allowed_commands: [kubectl, helm, k9s, kubectx]
blocked_commands: [kubectl delete namespace, kubectl delete pv, rm, dd]
color: blue
---

You are a Kubernetes specialist focusing on cluster operations, workload management, and troubleshooting.

**Core Expertise**:
- Kubernetes manifest creation and validation (Deployments, Services, ConfigMaps, Secrets)
- kubectl command patterns and best practices
- Pod debugging and log analysis
- Resource scaling and updates
- Helm chart deployment

**When to Use This Agent**:
- Creating or modifying Kubernetes manifests (.yaml files in k8s/ or deployments/)
- Troubleshooting pod failures or service issues
- Scaling deployments or managing replica counts
- Implementing Kubernetes best practices (resource limits, health checks, labels)

**Expected Outputs**:
- Valid Kubernetes YAML manifests
- kubectl commands for deployment/troubleshooting
- Debugging analysis and remediation steps
- Scaling and update strategies

**Best Practices**:
- Always specify resource requests/limits
- Use health checks (readiness/liveness probes)
- Apply labels and annotations consistently
- Namespace isolation for multi-tenant clusters
- Validate manifests before applying (kubectl --dry-run)
```

### Phase 2: Validation

The command automatically validates the generated agent definition:

**Required Fields Check:**
- ✓ `name` field present and valid format ({domain}-{role})
- ✓ `description` field present and specific (not vague)
- ✓ `tools` field explicitly defined (no tool inheritance risk)
- ✓ Task tool NOT included (prevents sub-agent recursion)

**Skills Validation:**
- ✓ All referenced skills exist in `.claude/skills/`
- ✓ Skill names match directory names exactly

**Tool Scoping Validation:**
- ✓ Minimal tool list for domain (least privilege)
- ✓ Dangerous commands in blocked list
- ✓ Domain-specific commands in allowed list
- ✓ No over-permissioned access (no ALL_TOOLS)

**Naming Convention Validation:**
- ✓ Filename matches pattern: `{domain}-{role}.md`
- ✓ Only valid characters (lowercase, hyphens)
- ✓ No redundant prefixes (no "agent-" prefix)

**Output:**
```
Validation Results:
✓ Required fields present
✓ Tool scoping appropriate
✓ Skills exist and valid
✓ Naming conventions followed
✓ No security risks detected

Agent definition ready to write.
```

### Phase 3: Testing

After creating the agent file, the command provides:

**Test Invocation Example:**
```bash
# Test your new agent in isolation
# Create a simple test task file
echo "Create a simple Kubernetes deployment for nginx" > /tmp/test-k8s-agent.md

# Invoke the agent via Claude Code
# (In Claude Code chat)
"Use kubernetes-operator agent to implement /tmp/test-k8s-agent.md"
```

**Example Usage Scenarios:**
```markdown
Use kubernetes-operator when:
1. Creating Kubernetes manifests (deployment.yaml, service.yaml)
2. Debugging pod failures (kubectl logs, kubectl describe)
3. Scaling applications (kubectl scale)
4. Implementing K8s best practices (resource limits, health checks)

Don't use for:
- Non-Kubernetes infrastructure (use terraform-expert)
- Cloud provider APIs (use aws-engineer or azure-engineer)
- General file operations (use main Claude Code instance)
```

**Validation Checklist:**
```
Manual Testing Steps:
1. [ ] Invoke agent with simple task
2. [ ] Verify agent loads specified skills
3. [ ] Confirm tool scoping works (can't access blocked tools)
4. [ ] Check output quality (domain expertise evident)
5. [ ] Test integration with existing agents (if applicable)
```

## Output Files

### Created File: `.claude/agents/{domain}-{role}.md`

Example path: `.claude/agents/kubernetes-operator.md`

The agent definition is written to the `.claude/agents/` directory with:
- Complete YAML frontmatter
- Domain-specific system prompt
- Best practices documentation
- Usage guidelines

## Advanced Features

### Custom Tool Scoping

You can customize tool scoping after generation by editing the agent file:

```yaml
# Read-only agent (validation specialist)
tools: Read, Grep, Glob

# Infrastructure agent (needs Bash for commands)
tools: Read, Write, Edit, Bash
allowed_commands: [terraform, kubectl, docker]
blocked_commands: [terraform destroy, kubectl delete, rm, dd]

# Research agent (needs WebSearch)
tools: Read, Write, WebSearch
```

### Skills Composition

Skills provide domain knowledge without duplicating documentation:

```yaml
# Compose multiple skills for comprehensive expertise
skills: [task-management, terraform-basics, azure-basics]

# This agent can:
# - Decompose features into tasks (task-management skill)
# - Write Terraform configs (terraform-basics skill)
# - Use Azure APIs (azure-basics skill)
```

### Description Optimization

The description field drives auto-delegation, so it should:
- **Be specific**: Include concrete examples and use cases
- **Use keywords**: Terms users might say ("kubectl", "deployment", "pod")
- **Avoid vagueness**: Not "helps with containers" but "manages Kubernetes workloads"

**Good Examples:**
```yaml
description: "PostgreSQL database specialist. USE PROACTIVELY for schema migrations, query optimization, backup/restore. Examples: creating indexes, analyzing slow queries, pg_dump operations."

description: "Docker containerization expert. USE PROACTIVELY for Dockerfile creation, image optimization, container debugging. Examples: multi-stage builds, reducing image size, fixing container startup issues."
```

**Bad Examples:**
```yaml
description: "Database agent"  # Too vague, no examples
description: "Helps with containers and stuff"  # Vague, no specifics
description: "Generic developer agent"  # Not specialized
```

## Command-Line Examples

### Example 1: Interactive (No Arguments)
```bash
/create-agent
```
Output: Full interactive workflow with all 4 clarification questions

### Example 2: Pre-Specify Domain
```bash
/create-agent postgres-dba
```
Output: Skips domain question, asks for responsibilities, tools, skills

### Example 3: Quick Domain Expert
```bash
/create-agent redis-specialist
```
Output: Interactive prompts for Redis-specific configuration

## Integration with Agent Architecture

This command is **Method 1** of the Agent Generation System. Other methods:

- **Method 2: Agent-Factory Workflow** - Autonomous planner → specialists → validator
- **Method 3: Skill-Based Auto-Invoked** - Detects need and generates agent automatically
- **Method 4: Template-Based Profiles** - Pre-defined domain templates

Use `/create-agent` when:
- Creating your first agent for a domain
- Need interactive guidance (less familiar with agent patterns)
- Want to explore tool/skill options before committing

Use other methods when:
- Creating multiple similar agents (use templates)
- Fully autonomous generation needed (use agent-factory)
- Agent generation as part of larger workflow (use auto-invoked)

## Security Considerations

### Tool Scoping (Critical)

**Always explicitly define tools field** - Omitting it grants access to ALL MCP tools (security risk):

```yaml
# ❌ WRONG - No tools field (inherits ALL tools)
---
name: validator
# Missing tools = ACCESS TO ALL MCP TOOLS!
---

# ✅ RIGHT - Explicit minimal tools
---
name: validator
tools: Read, Grep, Glob
---
```

### Sub-Agent Recursion Prevention

**Never add Task tool to domain experts** - Sub-agents cannot spawn other sub-agents:

```yaml
# ❌ WRONG - Task tool will fail
---
name: orchestrator
tools: Read, Write, Task
---

# ✅ RIGHT - No Task tool for sub-agents
---
name: analyst
tools: Read, Write, Grep
# Outputs analysis for main agent to orchestrate
---
```

### Command Blocking

**Always block dangerous commands**:

```yaml
blocked_commands:
  - rm  # File deletion
  - dd  # Disk write
  - mkfs  # Filesystem format
  - curl  # Unvalidated external calls
  - wget  # Unvalidated downloads
  - terraform destroy  # Infrastructure deletion
  - kubectl delete namespace  # Cluster-wide deletion
```

## Related Commands

- `/list-agents` - View all available agents (future)
- `/test-agent` - Validate agent in isolation (future)
- `/generate-prp` - Create PRP (may recommend domain experts)
- `/execute-prp` - Execute PRP with auto-selected domain experts

## Workflow Integration

Typical agent creation workflow:

1. **Identify need**: "I need a Kubernetes expert agent"
2. **Create agent**: `/create-agent kubernetes-operator`
3. **Test agent**: Try simple task to validate
4. **Refine**: Edit agent file to adjust tools/skills
5. **Use in PRP**: Execute-PRP auto-selects agent for K8s tasks

## Implementation Notes

### Phase 0 Implementation (Clarification)

The command uses a conversational approach:

```python
# Pseudo-code for interactive workflow
def phase_0_clarification(domain_arg=None):
    # 1. Domain/Role
    if domain_arg:
        domain_role = domain_arg
    else:
        domain_role = prompt_user("What domain/role is this agent for?")

    validate_naming(domain_role)  # {domain}-{role} format

    # 2. Responsibilities
    responsibilities = prompt_user(
        "What are this agent's primary responsibilities? (2-3 sentences)"
    )

    # 3. Tools
    available_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "WebSearch"]
    selected_tools = prompt_multi_select(
        "Which tools does this agent need?",
        options=available_tools
    )

    # 4. Skills
    available_skills = list_skills_directory()
    selected_skills = prompt_multi_select(
        "Which existing skills should this agent use?",
        options=available_skills
    )

    return {
        "domain_role": domain_role,
        "responsibilities": responsibilities,
        "tools": selected_tools,
        "skills": selected_skills
    }
```

### Phase 1 Implementation (Generation)

Generate agent definition from clarifications:

```python
def phase_1_generation(clarifications):
    domain_role = clarifications["domain_role"]
    domain = domain_role.split("-")[0]

    # Generate specific description with examples
    description = generate_description(
        domain=domain,
        responsibilities=clarifications["responsibilities"]
    )

    # Determine allowed/blocked commands based on domain
    allowed_commands = get_domain_commands(domain)
    blocked_commands = get_standard_blocks() + get_domain_blocks(domain)

    # Choose color based on domain category
    color = assign_color_by_domain(domain)

    # Generate system prompt
    system_prompt = generate_domain_prompt(
        domain=domain,
        responsibilities=clarifications["responsibilities"]
    )

    # Assemble frontmatter
    frontmatter = f"""---
name: {domain_role}
description: "{description}"
tools: {", ".join(clarifications["tools"])}
skills: [{", ".join(clarifications["skills"])}]
allowed_commands: [{", ".join(allowed_commands)}]
blocked_commands: [{", ".join(blocked_commands)}]
color: {color}
---

{system_prompt}
"""

    return frontmatter
```

### Phase 2 Implementation (Validation)

Validate generated agent before writing:

```python
def phase_2_validation(frontmatter, clarifications):
    validations = []

    # Required fields
    validations.append(check_required_fields(frontmatter))

    # Tool scoping
    validations.append(check_tools_field_exists(frontmatter))
    validations.append(check_no_task_tool(frontmatter))

    # Skills validation
    for skill in clarifications["skills"]:
        validations.append(skill_exists(f".claude/skills/{skill}"))

    # Naming conventions
    validations.append(validate_naming_format(clarifications["domain_role"]))

    return all(validations)
```

### Phase 3 Implementation (Testing)

Provide testing guidance:

```python
def phase_3_testing(domain_role):
    agent_path = f".claude/agents/{domain_role}.md"

    test_command = f'''# Test your agent
echo "Simple test task for {domain_role}" > /tmp/test-{domain_role}.md

# In Claude Code chat:
"Use {domain_role} agent to implement /tmp/test-{domain_role}.md"
'''

    usage_examples = generate_usage_examples(domain_role)

    return {
        "test_command": test_command,
        "usage_examples": usage_examples,
        "agent_path": agent_path
    }
```

## Troubleshooting

### Agent Not Auto-Delegating

**Problem**: Claude Code doesn't automatically use your agent

**Solutions**:
1. Make description more specific with keywords
2. Add concrete examples to description field
3. Use "USE PROACTIVELY" in description
4. Explicitly invoke: "Use {agent-name} for this task"

### Tool Permission Errors

**Problem**: Agent can't access needed tools

**Solutions**:
1. Check tools field includes required tools
2. Verify allowed_commands includes needed commands
3. Check blocked_commands doesn't block needed tools
4. Test in isolation to verify tool access

### Skills Not Loading

**Problem**: Agent doesn't seem to use skill knowledge

**Solutions**:
1. Verify skill exists in `.claude/skills/{skill-name}/`
2. Check skill name spelling matches directory exactly
3. Ensure skill has valid SKILL.md frontmatter
4. Test skill activation independently

### Validation Failures

**Problem**: Phase 2 validation fails

**Solutions**:
1. Check domain-role format: `{domain}-{role}` (lowercase, hyphens)
2. Verify all referenced skills exist
3. Ensure tools field is explicitly defined
4. Remove Task tool if present (sub-agent limitation)

## Best Practices

1. **Start Simple**: Minimal tools, 1-2 skills, focused domain
2. **Test Early**: Validate agent works before using in complex workflows
3. **Iterate**: Add tools/skills as needed, don't over-engineer upfront
4. **Document**: Update system prompt with domain-specific gotchas
5. **Compose**: Reuse existing skills instead of duplicating knowledge

## Examples

### Example 1: Database Specialist

```bash
/create-agent postgres-dba
```

**Clarification Responses:**
- Responsibilities: "Manages PostgreSQL operations including schema migrations, query optimization, backup/restore procedures."
- Tools: Read, Write, Edit, Bash
- Skills: task-management

**Generated Agent:**
```yaml
---
name: postgres-dba
description: "PostgreSQL database specialist. USE PROACTIVELY for schema migrations, query optimization, backup/restore, indexing. Examples: CREATE INDEX, EXPLAIN ANALYZE, pg_dump, psql commands."
tools: Read, Write, Edit, Bash
skills: [task-management]
allowed_commands: [psql, pg_dump, pg_restore, createdb, dropdb]
blocked_commands: [dropdb production, rm, dd, curl]
color: green
---
```

### Example 2: Container Expert

```bash
/create-agent docker-specialist
```

**Clarification Responses:**
- Responsibilities: "Builds and optimizes Docker images, debugs container issues, implements multi-stage builds."
- Tools: Read, Write, Edit, Bash
- Skills: None

**Generated Agent:**
```yaml
---
name: docker-specialist
description: "Docker containerization expert. USE PROACTIVELY for Dockerfile creation, image optimization, container debugging. Examples: multi-stage builds, reducing image size, debugging startup failures."
tools: Read, Write, Edit, Bash
skills: []
allowed_commands: [docker, docker-compose]
blocked_commands: [docker system prune -a, rm, dd]
color: cyan
---
```

## Related Documentation

- **Skills System**: `.claude/skills/README.md` - Creating reusable skills
- **Agent Patterns**: `prps/agent_architecture_modernization/examples/` - Example agents
- **Tool Scoping**: Claude Code sub-agents documentation - Security best practices
- **Domain Experts**: `prps/agent_architecture_modernization.md` - Architecture overview

---

**Command Version**: 1.0.0
**Compatible With**: Claude Code 1.0+
**Last Updated**: 2025-11-20
