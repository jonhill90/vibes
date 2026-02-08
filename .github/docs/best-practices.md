# Agent Best Practices

> Distilled from authoritative sources. Verify against these URLs before relying on local content.

## Sources

- [Claude Code: Best Practices](https://code.claude.com/docs/en/best-practices)
- [VS Code: Prompt Engineering Guide](https://code.visualstudio.com/docs/copilot/guides/prompt-engineering-guide)
- [microsoft/skills](https://github.com/microsoft/skills) — context rot warning

---

## 1. Give Agents a Way to Verify

The single highest-leverage thing you can do. Provide tests, screenshots, expected outputs, or validation commands so the agent can check its own work.

- Without verification criteria, the human becomes the only feedback loop
- Include specific test cases, not just "write tests"
- UI changes: paste screenshots, have the agent compare before/after

## 2. Explore First, Then Plan, Then Code

Separate research from implementation. Jumping straight to code solves the wrong problem.

1. **Explore** — read files, understand the current state
2. **Plan** — create a detailed implementation approach, surface tradeoffs
3. **Implement** — code against the plan, verify as you go
4. **Commit** — descriptive message, clean diff

Skip planning for trivial changes. Plan when uncertain about approach, touching multiple files, or unfamiliar with the code.

## 3. Specific Prompts Beat Vague Ones

Reference specific files, mention constraints, point to example patterns.

| Vague | Specific |
|-------|----------|
| "add tests for foo.py" | "write a test for foo.py covering the edge case where the user is logged out. avoid mocks." |
| "fix the login bug" | "users report login fails after session timeout. check src/auth/, especially token refresh." |
| "make the dashboard look better" | "[paste screenshot] implement this design. take a screenshot and compare." |

Vague prompts are fine for exploration. Be specific when you know what you want.

## 4. Load Skills Selectively

**Loading all skills causes context rot: diluted attention, wasted tokens, conflated patterns.** Only load skills essential for the current task.

- Each skill consumes context window space
- Irrelevant skills create ambiguous activation triggers
- Prefer on-demand loading over preloading everything

## 5. Keep AGENTS.md / CLAUDE.md Lean

These files load every session. Only include things that apply broadly.

| Include | Exclude |
|---------|---------|
| Commands the agent can't guess | Anything inferrable from code |
| Style rules that differ from defaults | Standard language conventions |
| Testing instructions and runners | Detailed API docs (link instead) |
| Repo conventions (branches, PRs) | Information that changes frequently |
| Common gotchas | Self-evident practices |

If the agent keeps ignoring a rule, the file is probably too long and the rule is getting lost. Prune ruthlessly.

## 6. Course-Correct Early

Tight feedback loops produce better results than letting the agent run unchecked.

- Stop the agent as soon as you see it going off track
- After 2 failed corrections in one session, start fresh with a better prompt
- **Claude Code:** `Esc` to stop, `/rewind` to restore, `/clear` to reset
- **Copilot:** Start a new chat session, reference files with `#`

## 7. Use Sub-Agents for Research

Investigation reads lots of files, all consuming context. Delegate research to sub-agents that report back summaries, keeping your main session clean for implementation.

- **Writer/Reviewer pattern:** run parallel sessions — one writes implementation, another reviews with fresh context. The reviewer catches issues the writer's accumulated context blinds it to.

## 8. Feed Rich Context

Go beyond plain text prompts. Pipe files, paste images, and reference paths directly.

- `@path/to/file` — reference files inline (CLAUDE.md also imports other files this way)
- `cat log.txt | claude` — pipe content directly into the session
- Paste screenshots for UI tasks — the agent can compare before/after
- Allowlist URLs with `/permissions` so agents can fetch live docs

## 9. Let the Agent Interview You

For large or ambiguous features, prompt the agent to ask clarifying questions before it plans. This front-loads requirements gathering and prevents wasted implementation cycles.

- "Interview me about the requirements before writing any code"
- Works best when combined with Section 2 (Explore, Plan, Code)
