---
name: "Agent Factory Lite Workflow"
description: "Simplified 3-phase agent creation workflow for learning orchestration patterns"
---

# Agent Factory Lite - Simplified Orchestration

A minimal workflow demonstrating the core agent factory pattern with 3 phases: Planning → Parallel Design → Implementation.

**Purpose**: Educational example showing orchestration fundamentals without production complexity.

---

## 🎯 Trigger Recognition

Recognize this workflow when user requests a simple agent:

- "Build a simple [type] agent"
- "Create a basic agent for [task]"
- "Make a minimal agent that [function]"

**Note**: This lite version is for demonstration. Use the full agent factory for production agents.

---

## 🔄 3-Phase Workflow

### Phase 1: Requirements Planning

**Mode**: AUTONOMOUS
**Subagent**: `lite-planner`
**Duration**: ~2 minutes

**Actions**:
```
1. Invoke lite-planner subagent
2. Planner analyzes user request
3. Creates simple_agent/requirements.md
4. Wait for completion
```

**Output**: `simple_agent/requirements.md`

**Content**:
- What the agent does
- Required tools (1-2 tools max)
- Basic configuration
- Success criteria

**Quality Gate**:
- ✅ Clear agent purpose defined
- ✅ Tool needs identified
- ✅ Output format specified

---

### Phase 2: Parallel Design ⚡

**Mode**: PARALLEL - 2 subagents simultaneously
**Duration**: ~2 minutes

**CRITICAL: Parallel Invocation Pattern**

⚠️ Invoke BOTH subagents in SINGLE message:

```markdown
Phase 2: Designing components in parallel...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design tools</description>
    <prompt>
You are lite-tool-designer.

Input: simple_agent/requirements.md
Output: simple_agent/tools.md

Design 1-2 simple tools based on requirements.
    </prompt>
    <subagent_type>lite-tool-designer</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design prompt</description>
    <prompt>
You are lite-prompt-designer.

Input: simple_agent/requirements.md
Output: simple_agent/prompts.md

Create a simple system prompt (50-100 words).
    </prompt>
    <subagent_type>lite-prompt-designer</subagent_type>
  </parameters>
</tool_use>
```

#### 2A: Tool Design

**Subagent**: `lite-tool-designer`
**Input**: `simple_agent/requirements.md`
**Output**: `simple_agent/tools.md`
**Content**: 1-2 tool specifications with function signatures

#### 2B: Prompt Design

**Subagent**: `lite-prompt-designer`
**Input**: `simple_agent/requirements.md`
**Output**: `simple_agent/prompts.md`
**Content**: Simple system prompt (50-100 words)

**Phase 2 Complete When**: Both subagents finish

**Why Parallel?**:
- Tasks are independent (both read same input)
- No file conflicts (different outputs)
- 2x speedup (both run simultaneously)

---

### Phase 3: Implementation

**Actor**: Main Claude Code
**Mode**: AUTONOMOUS
**Duration**: ~3 minutes

**Actions**:
```
1. Read all 3 markdown files:
   - simple_agent/requirements.md
   - simple_agent/tools.md
   - simple_agent/prompts.md

2. Implement agent in Python:
   - Create simple_agent/agent.py
   - Implement tools from tools.md
   - Use prompt from prompts.md

3. Add basic configuration:
   - simple_agent/.env.example
   - simple_agent/README.md

4. Report completion
```

**Output Files**:
- `simple_agent/agent.py` - Complete agent implementation
- `simple_agent/.env.example` - Environment variables template
- `simple_agent/README.md` - Basic usage instructions

**Quality Gate**:
- ✅ Agent implements all requirements
- ✅ Tools match specifications
- ✅ Prompt integrated correctly
- ✅ README explains usage

---

## 📁 Expected Output Structure

```
simple_agent/
├── requirements.md    # Phase 1 output
├── tools.md          # Phase 2A output
├── prompts.md        # Phase 2B output
├── agent.py          # Phase 3 output
├── .env.example      # Phase 3 output
└── README.md         # Phase 3 output
```

---

## 🛡️ Quality Standards

### Every Agent Must Have:
1. **Clear purpose** - Defined in requirements.md
2. **Working tools** - Implemented from tools.md
3. **Effective prompt** - From prompts.md
4. **Basic documentation** - README with usage

### Simplified vs Production:
- ❌ No comprehensive testing (lite version)
- ❌ No extensive validation (lite version)
- ❌ No advanced error handling (lite version)
- ✅ Focus on core pattern learning

---

## 🚨 Critical Rules

### ALWAYS:
- ✅ Run Phase 1 before Phase 2 (dependencies)
- ✅ Run Phase 2 agents in parallel (performance)
- ✅ Run Phase 3 after Phase 2 (dependencies)
- ✅ Use markdown for communication

### NEVER:
- ❌ Skip sequential dependencies
- ❌ Run parallel agents sequentially
- ❌ Assume file contents without reading

---

## 🎯 Example Execution

### User Request

```
User: "Build a simple weather agent"
```

### Phase 1: Requirements

```markdown
Invoking lite-planner to analyze requirements...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Analyze weather agent requirements</description>
    <prompt>
You are lite-planner.

User wants: "simple weather agent"

Output: simple_agent/requirements.md

Create simple requirements:
- Agent purpose (get weather forecasts)
- Required tools (get_weather tool)
- Configuration (API key needed)
- Success criteria (returns weather data)

Keep it minimal - 1-2 paragraphs per section.
    </prompt>
    <subagent_type>lite-planner</subagent_type>
  </parameters>
</tool_use>
```

**Output**: `simple_agent/requirements.md`

```markdown
# Weather Agent Requirements

## Purpose
Get weather forecasts for user-specified locations.

## Required Tools
- get_weather(location: str) -> weather data

## Configuration
- WEATHER_API_KEY environment variable

## Success Criteria
- Returns current weather for valid locations
- Handles invalid locations gracefully
```

### Phase 2: Parallel Design

```markdown
Designing tools and prompt in parallel...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design weather tool</description>
    <prompt>
You are lite-tool-designer.

Input: simple_agent/requirements.md
Output: simple_agent/tools.md

Design get_weather tool:
- Function signature
- Implementation notes
- Error handling

Keep it simple.
    </prompt>
    <subagent_type>lite-tool-designer</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design system prompt</description>
    <prompt>
You are lite-prompt-designer.

Input: simple_agent/requirements.md
Output: simple_agent/prompts.md

Create system prompt for weather agent:
- 50-100 words
- Helpful and informative
- Explains agent capabilities

Keep it simple.
    </prompt>
    <subagent_type>lite-prompt-designer</subagent_type>
  </parameters>
</tool_use>
```

**Outputs**:

`simple_agent/tools.md`:
```markdown
# Weather Tools

## get_weather

```python
async def get_weather(location: str) -> str:
    # Call weather API
    # Return formatted weather data
```

Returns current weather for location.
```

`simple_agent/prompts.md`:
```markdown
# Weather Agent Prompt

You are a helpful weather assistant. You can get current weather forecasts for any location. When users ask about weather, use your get_weather tool and present the information clearly.
```

### Phase 3: Implementation

```markdown
Implementing weather agent from design documents...

[Read requirements.md, tools.md, prompts.md]

Creating agent.py with:
- Agent definition using prompt from prompts.md
- get_weather tool implementation from tools.md
- Configuration from requirements.md

Creating .env.example and README.md...
```

**Output**: `simple_agent/agent.py`

```python
from pydantic_ai import Agent, RunContext
import httpx

SYSTEM_PROMPT = """
You are a helpful weather assistant. You can get current weather
forecasts for any location. When users ask about weather, use your
get_weather tool and present the information clearly.
"""

agent = Agent(
    model="openai:gpt-4",
    system_prompt=SYSTEM_PROMPT
)

@agent.tool
async def get_weather(ctx: RunContext, location: str) -> str:
    """Get current weather for a location."""
    api_key = os.getenv("WEATHER_API_KEY")
    async with httpx.AsyncClient() as client:
        # Implementation
        ...
    return weather_data
```

**Output**: `simple_agent/README.md`

```markdown
# Weather Agent

Simple weather forecast agent.

## Setup
1. `cp .env.example .env`
2. Add WEATHER_API_KEY
3. `python agent.py`

## Usage
Ask: "What's the weather in London?"
```

### Completion

```markdown
✅ Weather agent complete!

Location: simple_agent/
- requirements.md ✓
- tools.md ✓
- prompts.md ✓
- agent.py ✓
- README.md ✓
```

---

## 🔍 Learning Points

### 1. Phase Dependencies

```
Phase 1 must complete first
    ↓
Phase 2 reads Phase 1 output
    ↓
Phase 3 reads Phase 2 outputs
```

### 2. Parallel Execution

```
Phase 2A: tool-designer   ─┐
Phase 2B: prompt-designer ─┴─ Run simultaneously
```

**Key**: Single message with multiple Task tool calls

### 3. Markdown Communication

```
planner writes requirements.md
    ↓
Both designers read requirements.md
    ↓
Implementation reads all markdown files
```

---

## 🔧 Adapting This Pattern

### Add More Parallel Agents in Phase 2

```markdown
<tool_use> tool-designer </tool_use>
<tool_use> prompt-designer </tool_use>
<tool_use> config-designer </tool_use>  <!-- Add third agent -->
```

### Add a Validation Phase

```markdown
Phase 4: Validation
└─> validator checks agent.py against requirements.md
```

### Add Interactive Clarification

```markdown
Phase 0: Clarification
└─> Ask user questions
└─> Wait for responses
└─> Then proceed to Phase 1
```

---

## 📚 Next Steps

1. **Understand this lite version completely**
2. **Try modifying the workflow** (add phases, change agents)
3. **Study the [full agent factory](../../../.claude/orchestrators/agent-factory.md)**
4. **Build your own workflow** using [templates](../../../prps/templates/)

---

**This lite version teaches the pattern. The full agent factory applies it to production agent generation.**
