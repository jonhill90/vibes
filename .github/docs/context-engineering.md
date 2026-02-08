# Context Engineering

> Distilled from authoritative sources. Verify against these URLs before relying on local content.

## Sources

- [Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [VS Code: Context Engineering Guide](https://code.visualstudio.com/docs/copilot/guides/context-engineering-guide)
- [OpenAI: Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI: Conversation State Guide](https://platform.openai.com/docs/guides/conversation-state)

---

## Core Idea

Context is a finite resource with diminishing returns. Every token depletes the model's attention budget. Treat it like memory — allocate deliberately, reclaim aggressively.

## Principles

### 1. Just-in-Time Retrieval

Don't pre-load everything. Maintain lightweight identifiers (file paths, URLs, queries) and fetch content when actually needed. Each retrieval should inform the next decision.

- Prefer progressive disclosure over upfront dumps
- Let agents discover relevant context through exploration
- Hybrid: seed with high-level overview, explore for details

### 2. Minimal System Prompts

Organize instructions into distinct sections (XML tags or markdown headers). Strive for minimal yet sufficient — avoid both overly complex hardcoded logic and vague high-level guidance.

- If the agent already does it correctly without the instruction, remove it
- Instructions that are too long get ignored — important rules get lost in noise

### 3. Token-Efficient Tools

Design tools with clear, non-overlapping purposes. Bloated toolsets create ambiguous decision points.

- Minimize functional overlap between tools
- Use descriptive, unambiguous parameter names
- Each tool should have one obvious use case

### 4. Compaction

When approaching context limits, summarize message history. Preserve critical decisions and implementation details. Discard redundant outputs.

- **Claude Code:** `/compact` to summarize, `/clear` between unrelated tasks
- **Copilot:** Use separate chat sessions for different activities (planning vs. coding)
- **Codex CLI:** Keep sessions task-scoped; when context drifts, start a fresh session and carry forward only a brief state summary

### 5. Sub-Agent Isolation

Specialized agents handle focused tasks with clean context windows. They return condensed summaries (1,000-2,000 tokens) instead of exhaustive exploration details.

- Use sub-agents for research — keeps main context clean for implementation
- Each sub-agent gets its own attention budget
- Return findings as summaries, not raw data

### 6. Structured Note-Taking for Long Tasks

For tasks spanning multiple sessions, maintain external memory files. Track progress, decisions, and state across context resets.

- Create a progress file at session start
- Update it after each meaningful step
- Read it at the start of each new session
- Use JSON for structured data the model shouldn't casually edit
- **Initializer/coding agent pattern:** initializer creates `init.sh` + progress file + feature checklist; coding agent reads the onboarding checklist at each session start, then updates progress as it works

### 7. Few-Shot Examples

Provide diverse, canonical examples that portray expected behavior. Examples outperform lengthy explanations for formatting, tone, and edge-case handling.

- Include 2-3 examples covering distinct scenarios (happy path, edge case, error)
- Place examples close to the instruction they illustrate
- Prefer real input/output pairs over synthetic ones

## Anti-Patterns

- **Kitchen sink sessions (context rot)** — mixing unrelated tasks in one context degrades attention across all of them
- **Infinite exploration** — unscoped investigation that reads hundreds of files
- **Excessive correction loops** — failed approaches polluting context (start fresh after 2 failures)
- **Stale skill loading** — loading irrelevant skills causes context rot: diluted attention, wasted tokens, conflated patterns
- **Information dumps** — providing everything upfront instead of progressively

## Guiding Question

> "What is the smallest set of high-signal tokens that maximizes the likelihood of the desired outcome?"
