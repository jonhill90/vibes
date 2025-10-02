# RAG Agent - Complete Reference Implementation

This directory contains a complete, production-ready Pydantic AI agent that demonstrates all patterns from the Context Engineering Agent Factory:

- ✅ Planning documents (markdown specs)
- ✅ Python implementation following Pydantic AI patterns
- ✅ Tool implementations with dependencies
- ✅ System prompts and configuration
- ✅ Comprehensive test suite
- ✅ Complete documentation

## What This Agent Does

**Semantic Search Agent**: Intelligent knowledge base search with PostgreSQL/PGVector, featuring automatic strategy selection between semantic and hybrid search.

See [README.md](./README.md) for full usage documentation.

## Reference Implementation Value

This agent serves as a **complete example** of what the Agent Factory produces. It demonstrates:

### 1. Agent Factory Output Structure

```
rag-agent-example/
├── planning/              # ✅ Planning documents (Phase 1-2 output)
│   ├── INITIAL.md        # Requirements from planner
│   ├── prompts.md        # Prompt specs from prompt-engineer
│   ├── tools.md          # Tool specs from tool-integrator
│   └── dependencies.md   # Dependency specs from dependency-manager
├── agent.py              # ✅ Main agent (Phase 3 output)
├── tools.py             # ✅ Tool implementations (Phase 3)
├── prompts.py           # ✅ System prompts (Phase 3)
├── settings.py          # ✅ Configuration (Phase 3)
├── providers.py         # ✅ Model providers (Phase 3)
├── dependencies.py      # ✅ Dependencies class (Phase 3)
├── __init__.py          # ✅ Package init (Phase 3)
├── .env.example         # ✅ Environment template (Phase 3)
├── requirements.txt     # ✅ Python packages (Phase 3)
├── README.md            # ✅ Documentation (Phase 5)
└── tests/               # ✅ Test suite (Phase 4)
    ├── test_agent.py    # Agent behavior tests
    ├── test_tools.py    # Tool unit tests
    └── conftest.py      # Test fixtures
```

### 2. Markdown Communication Protocol

The `planning/` directory shows how markdown files communicate specifications:

**INITIAL.md** (from planner):
- Requirements that all other agents consume
- Defines what the agent must do

**prompts.md** (from prompt-engineer):
- System prompt specifications
- Structured for implementation

**tools.md** (from tool-integrator):
- Tool specifications with signatures
- Implementation guidance

**dependencies.md** (from dependency-manager):
- Environment variables
- Package requirements
- Provider configuration

### 3. Implementation Quality Standards

#### Agent Implementation (agent.py)

```python
# Clean, focused agent definition
from pydantic_ai import Agent
from .dependencies import AgentDependencies
from .prompts import SYSTEM_PROMPT

agent = Agent(
    model="openai:gpt-4-turbo",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDependencies,
    retries=2
)
```

Key patterns:
- Minimal agent.py - just agent definition
- Imports from organized modules
- Type safety with deps_type
- Configuration via settings

#### Tool Implementation (tools.py)

```python
from pydantic_ai import RunContext
from .dependencies import AgentDependencies

@agent.tool
async def semantic_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    match_count: int = 10
) -> str:
    """Execute semantic search using vector similarity."""
    # Implementation with proper error handling
    ...
```

Key patterns:
- Type-safe context usage
- Clear docstrings
- Error handling
- Async operations

#### Dependencies (dependencies.py)

```python
from pydantic import BaseModel, Field

class AgentDependencies(BaseModel):
    database_url: str = Field(..., description="PostgreSQL connection")
    http_client: httpx.AsyncClient
    embedding_model: str = Field(default="text-embedding-3-small")
```

Key patterns:
- Pydantic model for validation
- Type hints throughout
- Field descriptions
- Sensible defaults

#### Settings (settings.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    llm_provider: str = "openai"
    llm_model: str = "gpt-4-turbo"

    class Config:
        env_file = ".env"
```

Key patterns:
- BaseSettings for env vars
- Type validation
- Default values
- .env file loading

### 4. Testing Patterns (tests/)

#### Using TestModel

```python
from pydantic_ai.models.test import TestModel

@pytest.fixture
def test_agent():
    """Agent with TestModel for fast testing."""
    test_model = TestModel()
    return agent.override(model=test_model)

async def test_basic_search(test_agent):
    """Test agent provides search response."""
    deps = AgentDependencies(database_url="test_url", ...)
    result = await test_agent.run("Search for AI concepts", deps=deps)
    assert result.data is not None
```

#### Using FunctionModel

```python
from pydantic_ai.models.function import FunctionModel

def create_search_mock():
    async def mock_search(messages, tools):
        return {"semantic_search": {"query": "AI concepts", "match_count": 10}}
    return mock_search

async def test_tool_calling():
    """Test agent calls search tool."""
    function_model = FunctionModel(create_search_mock())
    test_agent = agent.override(model=function_model)
    # ... test tool invocation
```

### 5. Documentation Standards (README.md, REFERENCE.md)

Complete documentation includes:
- Feature overview
- Prerequisites
- Installation steps
- Configuration guide
- Usage examples
- Development instructions
- Project structure

## Using This as a Template

### Study the Planning Documents First

1. **Read `planning/INITIAL.md`**
   - See how requirements are structured
   - Understand functional vs technical requirements
   - Note success criteria

2. **Read Component Specs**
   - `prompts.md` - How prompts are specified
   - `tools.md` - How tools are designed
   - `dependencies.md` - How dependencies are configured

3. **See Implementation**
   - Compare specs to actual code
   - Note how specs translate to implementation
   - Understand the patterns used

### Adapt for Your Agent

When building similar agents:

1. **Use planning structure**
   - Same INITIAL.md format
   - Same component specification pattern
   - Same success criteria approach

2. **Follow implementation patterns**
   - Organized module structure
   - Type-safe dependencies
   - Clean agent definition
   - Proper error handling

3. **Replicate testing approach**
   - TestModel for fast tests
   - FunctionModel for controlled behavior
   - Comprehensive coverage

## Key Takeaways

### What Makes This a Good Reference

1. **Complete**: All phases of agent factory represented
2. **Realistic**: Actual working agent, not toy example
3. **Well-Documented**: Clear planning and implementation docs
4. **Tested**: Comprehensive test suite included
5. **Production-Ready**: Error handling, configuration, deployment

### What to Learn From This

1. **Planning Precision**: See how detailed specs enable implementation
2. **Clean Architecture**: Organized, modular, maintainable
3. **Type Safety**: Pydantic models throughout
4. **Testing Rigor**: Multiple testing strategies
5. **Documentation**: User and developer docs

### How Agent Factory Would Generate This

If you ran `/create-agent` for a semantic search agent:

**Phase 0**: Clarify requirements (interactive)
→ User describes RAG search needs

**Phase 1**: planner creates `planning/INITIAL.md`
→ Requirements analysis

**Phase 2**: Three parallel agents create component specs
→ `prompts.md`, `tools.md`, `dependencies.md`

**Phase 3**: Main Claude implements Python code
→ All `.py` files, requirements.txt, .env.example

**Phase 4**: validator creates test suite
→ tests/ directory with comprehensive tests

**Phase 5**: Documentation generated
→ README.md with usage instructions

**Result**: This complete agent structure!

## Comparing to Actual Usage

### Original Creation (Cole's Implementation)
This agent was created manually following agent factory patterns.

### Your Creation (Using /create-agent)
Running `/create-agent` with this spec would generate similar structure automatically.

### Key Difference
- Manual: Individual files crafted by developer
- Automated: Coordinated subagents generate all files

### Result Quality
Both approaches produce production-ready agents when patterns are followed correctly.

## Integration with Vibes Agent Factory

### Archon Integration Points

If this agent were created with Archon available:

1. **Planning Phase**
   - RAG queries for Pydantic AI patterns
   - Search for PostgreSQL/PGVector examples
   - Find embedding model best practices

2. **Implementation Phase**
   - RAG for vector database patterns
   - Code examples for async tools
   - Dependency injection patterns

3. **Validation Phase**
   - Search for testing patterns
   - Find async test examples
   - Validate against requirements

### Without Archon

Agent factory still works perfectly:
- WebSearch replaces RAG
- Codebase grep finds patterns
- All core functionality preserved

## Related Resources

- **Agent Factory Orchestrator**: [.claude/orchestrators/agent-factory.md](../../../.claude/orchestrators/agent-factory.md)
- **Subagent Templates**: [prps/templates/subagent_template.md](../../../prps/templates/subagent_template.md)
- **Parallel Pattern**: [prps/templates/parallel_pattern.md](../../../prps/templates/parallel_pattern.md)
- **Simple Examples**: [examples/agent-factory/](../../agent-factory/)

## Quick Commands

```bash
# Study the planning
cat planning/INITIAL.md
cat planning/prompts.md
cat planning/tools.md
cat planning/dependencies.md

# Review implementation
cat agent.py
cat tools.py
cat prompts.py

# Check tests
cat tests/test_agent.py

# Try it out (requires PostgreSQL + PGVector)
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python -m cli
```

---

**This agent demonstrates that the Agent Factory pattern produces real, production-ready agents, not just boilerplate code.**
