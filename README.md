# skills

Jon Hill's public collection of portable [Agent
Skills](https://agentskills.io/specification) — self-contained,
model- and harness-agnostic instructions an AI coding agent loads on
demand. Every skill here is individually installable; nothing in this
repository is specific to any one harness, and nothing here depends on
private tooling or evidence.

## Install

Browse the collection:

```bash
npx skills add jonhill90/skills --list
```

Install one or more specific skills into the current project:

```bash
npx skills add jonhill90/skills --skill tmux --skill github-cli
```

`npx skills` pins installs by content hash in `skills-lock.json`, so a
project's skill set stays reproducible. See the [skills
CLI](https://www.npmjs.com/package/skills) for the full command
reference.

### As an Agent Plugin

This repository is also an [Agent Plugins
1.0.0](https://agent-plugins.org/specification) plugin: `plugin.json` at the
root, 40 skills at `skills/<name>/SKILL.md` (measured `ls -d skills/*/ | wc -l`,
verified 2026-08-23), which is the standard's own discovery convention.
Any conformant client can consume the collection whole, with no bespoke
tooling.

That is a portability claim, not a local one. Claude Code reads its own
manifest at `.claude-plugin/plugin.json` and does not look for this file, so
adding it changed nothing for Claude Code users today. `npx skills` above
remains the way to install individual skills, and nothing here replaces it.

## Skills in this collection

<!-- generated-skills:start -->

Generated from 41 current skill bundles and the dated environment observation; do not hand-edit.
Regenerate with `python3 scripts/reconcile_skills.py`; verify with `--check`.
The [machine-readable manifest](docs/skills-reconciliation.json) names evidence and static audit locations.
Installed observations: 2026-09-07; refresh explicitly, never interpret this as a live roster.
`claude-user` in the manifest means the user-level Claude skills directory; host paths are omitted.
Packaging PASS = no local coupling detected; FAIL = local/CLI assumptions require review. Web execution is unrun.
Eval status reports existing evidence, not quality approval; missing external coverage remains unknown.

| Skill | Scope | Installed observation | Upload audit | Eval evidence |
|---|---|---|---|---|
| [`adopt-or-build`](skills/adopt-or-build/) | public | linked-to-canonical | FAIL | [has-evals](skills/adopt-or-build/references/eval-result.md) |
| [`ask-a-council`](skills/ask-a-council/) | public | linked-to-canonical | PASS | [has-evals](skills/ask-a-council/references/eval-result.md) |
| [`close-the-loop`](skills/close-the-loop/) | public | linked-to-canonical | PASS | [has-evals](skills/close-the-loop/references/eval-result.md) |
| [`create-skill`](skills/create-skill/) | public | linked-to-canonical | FAIL | [has-evals](skills/create-skill/references/eval-result.md) |
| [`decide-by-variant`](skills/decide-by-variant/) | public | linked-to-canonical | PASS | [has-evals](skills/decide-by-variant/references/eval-result.md) |
| [`derive-independently-then-compare`](skills/derive-independently-then-compare/) | public | linked-to-canonical | PASS | [has-evals](skills/derive-independently-then-compare/references/eval-result.md) |
| [`determine-intent`](skills/determine-intent/) | public | linked-to-canonical | PASS | [has-evals](skills/determine-intent/references/eval-result.md) |
| [`determine-signals`](skills/determine-signals/) | public | linked-to-canonical | PASS | [has-evals](skills/determine-signals/references/eval-result.md) |
| [`devils-advocate`](skills/devils-advocate/) | public | linked-to-canonical | PASS | [has-evals](skills/devils-advocate/references/eval-result.md) |
| [`dispatch-brief`](skills/dispatch-brief/) | public | linked-to-canonical | PASS | [has-evals](skills/dispatch-brief/references/eval-result.md) |
| [`dispatching-subagents`](skills/dispatching-subagents/) | public | linked-to-canonical | PASS | [has-evals](skills/dispatching-subagents/references/eval-result.md) |
| [`distill`](skills/distill/) | public | linked-to-canonical | PASS | [has-evals](skills/distill/references/eval-result.md) |
| [`durable-fact-before-label`](skills/durable-fact-before-label/) | public | linked-to-canonical | PASS | [has-evals](skills/durable-fact-before-label/references/eval-result.md) |
| [`failing-test-first`](skills/failing-test-first/) | public | linked-to-canonical | PASS | [has-evals](skills/failing-test-first/references/eval-result.md) |
| [`github-cli`](skills/github-cli/) | public | linked-to-canonical | FAIL | [could-not-measure](skills/github-cli/references/eval-result.md) |
| [`keep-me-honest`](skills/keep-me-honest/) | public | linked-to-canonical | PASS | [has-evals](skills/keep-me-honest/references/eval-result.md) |
| [`linear`](skills/linear/) | public | linked-to-canonical | FAIL | [could-not-measure](skills/linear/references/eval-result.md) |
| [`loop-contract`](skills/loop-contract/) | public | linked-to-canonical | PASS | [has-evals](skills/loop-contract/references/eval-result.md) |
| [`loop-memory`](skills/loop-memory/) | public | linked-to-canonical | FAIL | [has-evals](skills/loop-memory/references/eval-result.md) |
| [`mechanize`](skills/mechanize/) | public | linked-to-canonical | PASS | [has-evals](skills/mechanize/references/eval-result.md) |
| [`memory-conventions`](skills/memory-conventions/) | public | linked-to-canonical | FAIL | [has-evals](skills/memory-conventions/references/eval-result.md) |
| [`mine-transcripts`](skills/mine-transcripts/) | public | linked-to-canonical | FAIL | [has-evals](skills/mine-transcripts/references/eval-result.md) |
| [`notify`](skills/notify/) | public | linked-to-canonical | FAIL | [has-evals](skills/notify/references/eval-result.md) |
| [`obsidian`](skills/obsidian/) | public | linked-to-canonical | FAIL | [could-not-measure](skills/obsidian/references/eval-result.md) |
| [`plan-parallel-execution`](skills/plan-parallel-execution/) | public | linked-to-canonical | PASS | [has-evals](skills/plan-parallel-execution/references/eval-result.md) |
| [`prd`](skills/prd/) | public | linked-to-canonical | PASS | [has-evals](skills/prd/references/eval-result.md) |
| [`primer`](skills/primer/) | public | linked-to-canonical | FAIL | [has-evals](skills/primer/references/eval-result.md) |
| [`progressive-disclosure`](skills/progressive-disclosure/) | public | linked-to-canonical | PASS | [has-evals](skills/progressive-disclosure/references/eval-result.md) |
| [`prompt-corpus`](skills/prompt-corpus/) | public | linked-to-canonical | FAIL | [has-evals](skills/prompt-corpus/references/eval-result.md) |
| [`refuse-invented-identity`](skills/refuse-invented-identity/) | public | linked-to-canonical | PASS | [has-evals](skills/refuse-invented-identity/references/eval-result.md) |
| [`research-the-limit`](skills/research-the-limit/) | public | linked-to-canonical | PASS | [has-evals](skills/research-the-limit/references/eval-result.md) |
| [`safe-deletion`](skills/safe-deletion/) | public | linked-to-canonical | PASS | [has-evals](skills/safe-deletion/references/eval-result.md) |
| [`sanity-check`](skills/sanity-check/) | public | linked-to-canonical | PASS | [has-evals](skills/sanity-check/references/eval-result.md) |
| [`spec`](skills/spec/) | public | linked-to-canonical | PASS | [has-evals](skills/spec/references/eval-result.md) |
| [`spec-driven-development`](skills/spec-driven-development/) | public | linked-to-canonical | PASS | [has-evals](skills/spec-driven-development/references/eval-result.md) |
| [`supervised-lane-loop`](skills/supervised-lane-loop/) | public | linked-to-canonical | FAIL | [has-evals](skills/supervised-lane-loop/references/eval-result.md) |
| [`tdd`](skills/tdd/) | public | linked-to-canonical | PASS | [has-evals](skills/tdd/references/eval-result.md) |
| [`test-in-the-consumer-context`](skills/test-in-the-consumer-context/) | public | linked-to-canonical | PASS | [has-evals](skills/test-in-the-consumer-context/references/eval-result.md) |
| [`tmux`](skills/tmux/) | public | divergent-or-unresolved-install | FAIL | [has-evals](skills/tmux/references/eval-result.md) |
| [`verify-the-instrument`](skills/verify-the-instrument/) | public | linked-to-canonical | PASS | [has-evals](skills/verify-the-instrument/references/eval-result.md) |
| [`wire-it-when-you-write-it`](skills/wire-it-when-you-write-it/) | public | linked-to-canonical | PASS | [has-evals](skills/wire-it-when-you-write-it/references/eval-result.md) |

Private skills observed: 1; installed outside this public collection: 2. Private identities are excluded. Installer-attributed third-party entries: 1; unresolved installed homes: 0.

<!-- generated-skills:end -->

## Where a skill belongs

Most skills should **not** live in this repository. Decide placement
first:

| Situation | Where it goes |
|---|---|
| Useful across many unrelated projects, every day | a public collection like this one |
| Only true in one repository | that repo's own `.claude/skills/` or `.agents/skills/` |
| Needed once, or maintained by someone else | nothing installed — `npx skills use <package>@<skill>` |

## Authoring contract

Each skill lives at `skills/<name>/SKILL.md`:

```text
skills/example-skill/
├── SKILL.md
├── scripts/       Optional deterministic, tested helpers
├── references/    Optional detail loaded on demand
└── assets/        Optional output resources
```

Portable frontmatter is `name` and `description` (plus optional
`license`, `compatibility`, `metadata`, `allowed-tools`). The directory
name must match `name`. Keep `SKILL.md` under 500 lines and move detail
into directly linked `references/`. Full conventions: [AGENTS.md](AGENTS.md).

## Validate

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
```

CI runs both on every pull request and on pushes to `main`.

## Content boundaries

- This repository holds only portable skill content and the minimal
  validation/tests/CI needed to keep it correct.
- Personal harness configuration — canonical instructions, hooks,
  agents, settings, MCP declarations, install/sync tooling — lives in a
  separate personal harness repository that consumes this collection; it
  is not vendored here.
- Behavioral evaluation methodology, scenarios, transcripts, and results
  are private and are not published in this repository. Where a skill
  references past evidence, it states what happened and when without a
  link to private material.
- Employer-owned or project-specific material is never copied here.

See [AGENTS.md](AGENTS.md) for contribution rules.
