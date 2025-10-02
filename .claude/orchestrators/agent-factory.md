---
name: "Agent Factory Orchestration Workflow"
description: "Complete 5-phase workflow for autonomous AI agent development using specialized subagents, parallel execution, and Archon integration"
---

# 🏭 Pydantic AI Agent Factory - Orchestration Workflow

This orchestrator defines the complete workflow for transforming high-level user requests into fully-functional, tested Pydantic AI agents through coordinated subagent execution.

**Core Philosophy**: Transform "I want an agent that can search the web" into a production-ready Pydantic AI agent. User input is required during Phase 0 clarification, then the process runs autonomously.

---

## 🎯 Trigger Recognition

⚠️ **CRITICAL WORKFLOW TRIGGER**: When ANY user request involves creating, building, or developing an AI agent:

1. **IMMEDIATELY** recognize this as an agent factory request
2. **MUST** follow Phase 0 first - ask clarifying questions
3. **WAIT** for user responses
4. **THEN** check Archon and proceed with workflow

**Factory Workflow Recognition Patterns**:
- "Build an AI agent that..."
- "Create an agent for..."
- "I need an AI assistant that can..."
- "Make a Pydantic AI agent..."
- "I want to build a Pydantic AI agent..."
- Any request mentioning agent/AI/LLM + functionality

---

## 🔄 Complete 5-Phase Workflow

### Phase 0: Request Recognition & Clarification

**Mode**: INTERACTIVE - Main Claude Code
**Duration**: 1-2 minutes (wait for user)

**Actions**:
```
1. Acknowledge agent creation request
2. Ask 2-3 targeted clarifying questions:
   - Primary functionality and use case
   - Preferred APIs or integrations (if applicable)
   - Output format preferences

3. ⚠️ CRITICAL: STOP AND WAIT for user responses
   - Do NOT make assumptions
   - Do NOT create folders or invoke subagents yet
   - WAIT for explicit user input

4. After user responds:
   - DETERMINE AGENT FOLDER NAME (snake_case: web_search_agent, asana_manager)
   - Check Archon availability: mcp__archon__health_check()
   - If Archon available: Create project and tasks
   - Create agents/[AGENT_FOLDER_NAME]/ directory
```

**Archon Integration** (if available):
```python
# Create Archon project for this agent
project = mcp__archon__manage_project(
    action="create",
    title=f"{agent_name} Development",
    description=f"Agent factory workflow for {agent_name}"
)

# Create tasks for all phases
tasks = [
    {"title": "Requirements Analysis", "assignee": "pydantic-ai-planner", "task_order": 100},
    {"title": "System Prompt Design", "assignee": "pydantic-ai-prompt-engineer", "task_order": 90},
    {"title": "Tool Development Planning", "assignee": "pydantic-ai-tool-integrator", "task_order": 88},
    {"title": "Dependency Configuration", "assignee": "pydantic-ai-dependency-manager", "task_order": 86},
    {"title": "Agent Implementation", "assignee": "Claude Code", "task_order": 80},
    {"title": "Validation & Testing", "assignee": "pydantic-ai-validator", "task_order": 70},
    {"title": "Documentation & Delivery", "assignee": "Claude Code", "task_order": 60}
]

for task in tasks:
    mcp__archon__manage_task(action="create", project_id=project_id, **task)
```

---

### Phase 1: Requirements Documentation 🎯

**Subagent**: `pydantic-ai-planner`
**Mode**: AUTONOMOUS - Works without user interaction
**Philosophy**: SIMPLE, FOCUSED requirements - MVP mindset
**Duration**: 2-3 minutes

**Actions**:
```
1. If Archon available: Update Task 1 to status="doing"

2. Invoke pydantic-ai-planner subagent with:
   - User's original request
   - User's clarification responses
   - EXACT folder name for output
   - Archon project ID (if available)

3. Planner creates: agents/[folder]/planning/INITIAL.md
   ⚠️ CRITICAL: Output to planning/ subdirectory

4. If Archon available: Update Task 1 to status="done"
```

**Quality Gate - INITIAL.md must include**:
- ✅ Agent classification and type
- ✅ Functional requirements (2-3 core features max)
- ✅ Technical requirements
- ✅ External dependencies
- ✅ Success criteria

---

### Phase 2: Parallel Component Development ⚡

**Mode**: PARALLEL - THREE subagents work simultaneously
**Philosophy**: Speed through parallel execution
**Duration**: 3-5 minutes

**CRITICAL: Parallel Invocation Pattern**

⚠️ **YOU MUST invoke all THREE subagents in a SINGLE message with multiple Task tool uses**:

```
❌ WRONG (Sequential):
1. Invoke prompt-engineer, wait for completion
2. Then invoke tool-integrator, wait for completion
3. Then invoke dependency-manager, wait for completion

✅ RIGHT (Parallel):
Send ONE message containing THREE Task tool invocations

Steps:
1. If Archon available: Update Tasks 2, 3, 4 to "doing"
2. Invoke ALL THREE subagents in parallel (single message):
   - pydantic-ai-prompt-engineer
   - pydantic-ai-tool-integrator
   - pydantic-ai-dependency-manager
3. Wait for all three to complete
4. If Archon available: Update Tasks 2, 3, 4 to "done"
```

#### 2A: System Prompt Engineering

**Subagent**: `pydantic-ai-prompt-engineer`
**Input**: planning/INITIAL.md + EXACT folder name
**Output**: agents/[folder]/planning/prompts.md
**Content**: One simple static system prompt (100-300 words)

#### 2B: Tool Development Planning

**Subagent**: `pydantic-ai-tool-integrator`
**Input**: planning/INITIAL.md + EXACT folder name
**Output**: agents/[folder]/planning/tools.md
**Content**: 2-3 essential tool specifications only

#### 2C: Dependency Configuration

**Subagent**: `pydantic-ai-dependency-manager`
**Input**: planning/INITIAL.md + EXACT folder name
**Output**: agents/[folder]/planning/dependencies.md
**Content**: Essential env vars, single model provider, minimal packages

**Phase 2 Complete When**: All three subagents report completion

---

### Phase 3: Agent Implementation 🔨

**Actor**: Main Claude Code (NOT a subagent)
**Mode**: AUTONOMOUS
**Duration**: 5-10 minutes

**Actions**:
```
1. If Archon available: Update Task 5 "Agent Implementation" to status="doing"

2. READ all 4 planning markdown files:
   - agents/[folder]/planning/INITIAL.md
   - agents/[folder]/planning/prompts.md
   - agents/[folder]/planning/tools.md
   - agents/[folder]/planning/dependencies.md

3. If Archon available: Use RAG for Pydantic AI patterns
   - mcp__archon__rag_search_knowledge_base(query="pydantic ai patterns")
   - mcp__archon__rag_search_code_examples(query="agent implementation")

4. IMPLEMENT the actual Python code:
   - Convert prompt specs → prompts.py
   - Convert tool specs → tools.py
   - Convert dependency specs → settings.py, providers.py, dependencies.py
   - Create agent.py (main agent)
   - Create __init__.py
   - Create requirements.txt
   - Create .env.example
   - Create CLI (if needed)

5. Structure final project:
   agents/[agent_name]/
   ├── planning/           # Markdown specs (already created)
   ├── agent.py           # Main agent
   ├── settings.py        # Configuration
   ├── providers.py       # Model providers
   ├── dependencies.py    # Dependencies
   ├── tools.py          # Tool implementations
   ├── prompts.py        # System prompts
   ├── __init__.py       # Package init
   ├── requirements.txt  # Python deps
   ├── .env.example      # Environment template
   └── README.md         # Usage documentation

6. If Archon available: Update Task 5 to status="done"
```

---

### Phase 4: Validation & Testing ✅

**Subagent**: `pydantic-ai-validator`
**Mode**: AUTONOMOUS
**Duration**: 3-5 minutes

**Actions**:
```
1. If Archon available: Update Task 6 "Validation & Testing" to status="doing"

2. Invoke pydantic-ai-validator subagent with:
   - Agent folder path
   - Archon project ID (if available)

3. Validator creates comprehensive test suite:
   agents/[agent_name]/tests/
   ├── test_agent.py
   ├── test_tools.py
   ├── test_integration.py
   ├── test_validation.py
   ├── conftest.py
   └── VALIDATION_REPORT.md

4. If Archon available: Update Task 6 to status="done"
```

**Success Criteria**:
- All requirements from INITIAL.md validated
- Core functionality tested
- Error handling verified
- Performance acceptable

---

### Phase 5: Delivery & Documentation 📦

**Actor**: Main Claude Code
**Mode**: AUTONOMOUS
**Duration**: 2-3 minutes

**Actions**:
```
1. If Archon available: Update Task 7 "Documentation & Delivery" to status="doing"

2. Generate comprehensive README.md:
   - Installation instructions
   - Usage examples
   - API documentation
   - Environment setup
   - Deployment guide

3. Create usage examples (if not already present)

4. If Archon available:
   - Update Task 7 to status="done"
   - Add final notes to project about agent capabilities
   - Provide user with Archon project link

5. Provide user with summary:
   - Agent location
   - Quick start instructions
   - Next steps
```

---

## 📁 Expected Output Structure

Every successful agent factory run produces:

```
agents/[agent_name]/
├── planning/              # Planning documents (markdown)
│   ├── INITIAL.md        # Requirements (from planner)
│   ├── prompts.md        # Prompt specs (from prompt-engineer)
│   ├── tools.md          # Tool specs (from tool-integrator)
│   └── dependencies.md   # Dependency specs (from dependency-manager)
├── agent.py              # Main implementation
├── settings.py           # Configuration
├── providers.py          # Model providers
├── dependencies.py       # Dependencies
├── tools.py             # Tools
├── prompts.py           # Prompts
├── __init__.py          # Package init
├── requirements.txt     # Python packages
├── .env.example         # Environment template
├── README.md            # Documentation
└── tests/               # Test suite
    ├── test_agent.py
    ├── test_tools.py
    ├── conftest.py
    └── VALIDATION_REPORT.md
```

---

## 🛡️ Quality Assurance

### Every Agent MUST Have:
1. **Comprehensive tests** using TestModel/FunctionModel
2. **Error handling** for all external operations
3. **Security measures** for API keys and inputs
4. **Documentation** for usage and deployment
5. **Environment template** (.env.example)

### Pre-Delivery Checklist:
- [ ] All requirements from INITIAL.md implemented
- [ ] Tests created and documented
- [ ] API keys properly managed
- [ ] Error scenarios handled
- [ ] Documentation complete
- [ ] Usage examples provided

---

## 🚨 Critical Rules

### ALWAYS:
- ✅ Use python-dotenv for environment management
- ✅ Create .env.example with all required vars
- ✅ Follow Pydantic AI patterns
- ✅ Create comprehensive tests
- ✅ Validate against requirements

### NEVER:
- ❌ Skip Phase 0 clarification
- ❌ Invoke subagents sequentially when parallel execution is needed
- ❌ Create planning files outside planning/ subdirectory
- ❌ Hardcode API keys or secrets
- ❌ Skip testing phase
- ❌ Ignore error handling

---

## 🔧 Error Handling

If any phase fails:
```
1. Log error with full context
2. If Archon available: Add note to failed task
3. Attempt automatic recovery if possible
4. If recovery fails: Ask user for guidance
5. Continue with partial implementation if possible
6. Document limitations in README
```

### Graceful Degradation:
- If Archon unavailable: Proceed without task tracking
- If subagent fails: Attempt manual implementation
- If validation fails: Document known issues

---

## 📊 Success Metrics

- **Time to Completion**: Target <20 minutes for standard agents
- **Phases Complete**: All 5 phases must complete successfully
- **Validation**: 100% of requirements tested
- **User Intervention**: Minimize to initial clarification only

---

## 🎯 Invocation Examples

### Example 1: Simple Web Search Agent

**User**: "Build an agent that can search the web"

**Phase 0 - Clarification**:
```
I'll help you build a web search AI agent. Let me ask a few quick questions:

1. What will the agent primarily search for?
2. Should it summarize results or return raw data?
3. Any preference for search API? (Brave, Google, Bing)

[WAIT FOR USER RESPONSE]
```

**After user responds**:
```
Perfect! Creating your web_search_agent...

📋 Phase 1: Requirements Analysis...
[Invoke pydantic-ai-planner]

⚙️ Phase 2: Building Components (parallel)...
[Invoke 3 subagents in SINGLE message]

🔨 Phase 3: Implementing Agent...
[Main implementation]

✅ Phase 4: Running Validation...
[Invoke pydantic-ai-validator]

📦 Phase 5: Finalizing Documentation...
[Complete README and examples]

🎉 Agent Complete!
Location: agents/web_search_agent/
```

### Example 2: Database Query Agent

**User**: "Create an agent for PostgreSQL queries with explanations"

**Phase 0 - Clarification**:
```
I'll create a PostgreSQL query agent. Quick questions:

1. What query types? (SELECT only, or also INSERT/UPDATE/DELETE?)
2. Single database or multiple connections?
3. How detailed should explanations be?

[WAIT FOR USER RESPONSE]
```

[Process continues autonomously through all 5 phases]

---

## 🔍 Monitoring & Status Updates

Provide clear progress indicators:
```
✅ Phase 0: Clarification Complete
✅ Phase 1: Requirements Complete (INITIAL.md created)
⏳ Phase 2: Building Components (3 subagents working in parallel...)
  ✅ Prompts: Complete
  ✅ Tools: Complete
  ✅ Dependencies: Complete
⏳ Phase 3: Implementation in progress...
⏳ Phase 4: Validation pending...
⏳ Phase 5: Documentation pending...
```

---

## 📝 Archon Integration Details

When Archon is available, this workflow:
1. Creates a project for the agent
2. Creates 7 tasks (one per phase/subphase)
3. Updates task status as phases progress
4. Uses RAG for documentation lookup during implementation
5. Stores final notes about agent capabilities

When Archon is unavailable:
- Workflow still executes completely
- No task tracking (acceptable)
- No RAG assistance (use WebSearch instead)
- All core functionality preserved

---

## 🎨 Advanced Features

### Debug Mode
Enable with: "Build agent in debug mode"
- Verbose logging from all subagents
- Intermediate outputs preserved
- Step-by-step confirmation
- Performance metrics

### Custom Workflows
Users can request:
- Specific subagent configurations
- Alternative phase sequences
- Integration with existing code
- Custom validation criteria

---

This orchestrator ensures consistent, high-quality agent generation through a proven 5-phase workflow with specialized subagents, parallel execution, and comprehensive validation.
