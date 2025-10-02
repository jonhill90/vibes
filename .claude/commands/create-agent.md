# Create Agent

Invokes the agent factory workflow to create a complete, production-ready Pydantic AI agent autonomously.

## Usage

Simply describe the agent you want to build at a high level. The factory will handle the rest.

**Examples**:
- "Build an agent that can search the web"
- "Create an agent for PostgreSQL queries"
- "I need an agent that can summarize documents"
- "Make a Pydantic AI agent that integrates with Asana"

## How It Works

This command triggers the complete agent factory orchestration defined in `.claude/orchestrators/agent-factory.md`:

### Phase 0: Clarification (Interactive)
- Asks 2-3 targeted questions about your needs
- Waits for your responses
- Determines agent folder name
- Checks Archon availability

### Phase 1: Requirements Planning (Autonomous)
- Invokes `pydantic-ai-planner` subagent
- Creates comprehensive INITIAL.md with requirements
- Output: `agents/[name]/planning/INITIAL.md`

### Phase 2: Parallel Component Design (Autonomous)
- Invokes 3 subagents **simultaneously**:
  - `pydantic-ai-prompt-engineer` → creates prompts.md
  - `pydantic-ai-tool-integrator` → creates tools.md
  - `pydantic-ai-dependency-manager` → creates dependencies.md
- All work in parallel for speed

### Phase 3: Implementation (Autonomous)
- Main Claude Code reads all planning files
- Implements complete Python agent
- Creates all necessary files (agent.py, tools.py, etc.)

### Phase 4: Validation (Autonomous)
- Invokes `pydantic-ai-validator` subagent
- Creates comprehensive test suite
- Generates VALIDATION_REPORT.md

### Phase 5: Delivery (Autonomous)
- Generates final README with usage instructions
- Provides setup and deployment guidance
- Reports completion to user

## What You Get

A complete agent in `agents/[agent_name]/` with:

```
agents/your_agent/
├── planning/              # Planning documents
│   ├── INITIAL.md        # Requirements
│   ├── prompts.md        # Prompt specifications
│   ├── tools.md          # Tool specifications
│   └── dependencies.md   # Dependency specifications
├── agent.py              # Main implementation
├── settings.py           # Configuration
├── providers.py          # Model providers
├── dependencies.py       # Dependencies
├── tools.py             # Tool implementations
├── prompts.py           # System prompts
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

## Archon Integration

If Archon MCP is available:
- Creates a project for your agent
- Tracks progress through 7 tasks (one per phase)
- Uses RAG for documentation lookup during implementation
- Provides project link for tracking

If Archon is unavailable:
- Workflow still executes completely
- All core functionality preserved

## Time Estimate

- **Simple agents**: 10-15 minutes
- **Complex agents**: 15-25 minutes

Most time is spent in autonomous execution - you only interact during Phase 0 clarification.

## Tips for Best Results

1. **Be specific about functionality**: "search the web and summarize results" is better than "search agent"

2. **Mention APIs if you have preferences**: "use Brave API for search" helps the planner

3. **Specify output format if important**: "return structured JSON" vs "return plain text"

4. **Keep it simple initially**: The factory creates MVP agents - you can enhance later

## Troubleshooting

**If the workflow doesn't start:**
- Make sure your request matches a trigger pattern (e.g., "Build an agent...")
- Try being more explicit: "I want to create a Pydantic AI agent that..."

**If a phase fails:**
- The system will attempt automatic recovery
- If recovery fails, you'll be asked for guidance
- Partial implementations are documented in the README

**If you want to start over:**
- Simply request a new agent
- Each agent gets its own directory, no conflicts

## Advanced Usage

You can also invoke specific subagents manually:
- `/task pydantic-ai-planner` - Just requirements planning
- "Run the validator on my agent" - Just validation
- "Have the tool integrator add web search" - Specific enhancement

## Next Steps After Creation

1. **Review the agent**: Check `agents/[name]/README.md`
2. **Set up environment**: Copy `.env.example` to `.env` and add API keys
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run tests**: `pytest agents/[name]/tests/`
5. **Try the agent**: Follow usage examples in README

## Philosophy

The agent factory follows these principles:
- **MVP first**: Start simple, make it work, then iterate
- **Autonomous execution**: Minimal user interaction after clarification
- **Comprehensive testing**: Every agent includes tests
- **Production-ready**: Complete with docs, configs, and error handling

Ready to build your agent? Just describe what you need!
