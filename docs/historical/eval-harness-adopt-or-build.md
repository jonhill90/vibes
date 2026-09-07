# Adopt-or-build on the behavioural eval harness (jonhill90/skills#... build-5)

**This check was never run before now.** Jon asked directly whether build-vs-adopt
had ever been done on the behavioural eval harness. `git grep` across `docs/` and
`scripts/` for any prior-art name (in both this repo and `agent-evals`) returns
nothing but the eval log for the `adopt-or-build` *skill itself* — the tool we
spent the most weeks on (`docs/historical/eval-harness-findings.md`'s six-obstacle taxonomy,
the cost-axis rewrite, the longitudinal design) never had its own first step
applied to it. This document is that check, run properly: search before judging,
license first, blast radius per component, a contract over a vendored dependency
where a candidate is thin, and a `devils-advocate` pass on the conclusion before
it ships.

**No implementation in this PR.** This is the decision document plus evidence.

## What "the harness" actually is, read from the tree, not recalled

Four separable components, spread across two repositories:

1. **Scenario format** (`jonhill90/skills`, `skills/<name>/references/eval-scenario/{prompt.md,criteria.md,fixture/}`) — one prompt, one criteria doc, one disposable git-fixture, per skill.
2. **Runner** (`jonhill90/agent-evals`, private, `scripts/eval_skill.py` + `scripts/eval_arm.py`) — `build_fixture()` copies the fixture into a git repo; `eval_arm.py`'s `no-skill:<name>` stash renames the skill's files aside for the "without" arm; `run_agent()` shells out to `claude -p --output-format stream-json --verbose --dangerously-skip-permissions` and parses the NDJSON event stream for tool calls, `num_turns`, and token counts.
3. **Scorer** (`agent-evals`, same file) — a `SCORERS` dispatch table with exactly **one** registered function (`score_research_the_limit`); every other skill's criteria.md is graded by an agent reading the transcript by hand against its own written criteria, not by code. A generic `verdict()` function flags a >1.5x token/turn ratio as `improve` rather than `keep`, independent of any per-skill scorer.
4. **Record** (`jonhill90/skills`, `docs/eval-status.json` + `docs/eval-log/<skill>.jsonl`, managed by `scripts/eval_status.py`) — append-only JSONL per skill, regenerated into one summary JSON. Built this way specifically because three PRs hand-editing one shared record file conflicted the same night (`eval_status.py`'s own docstring, `#239`/`#240`/`#243`).

The brief's own instruction to split rather than answer once is correct on the
evidence: these four have obviously different blast radii, and the search below
treats them separately.

## The requirement the search was run against

Not the standard eval shape (`prompt → output → reference`). Ours is an
**ablation**: run a real coding agent, with real tool access, twice — once with a
skill on the context path, once without — on the identical task, and score the
resulting *trajectory* (tool calls, files touched, ordering), not final text.
`docs/historical/eval-harness-findings.md` additionally establishes, from three independent
escalation trials (`create-skill`, `distill`, `loop-memory`), that the current
instrument's real blind spot is **longitudinal**: a **cross-session** design —
two genuinely separate agent processes, a structural memory wall between them,
failure-inviting pressure introduced partway through session 1 rather than
stated up front, scored on the exact tool call where session 2's behaviour first
diverges. Per the brief: a candidate that makes *that* shape cheap is worth more
than one that only matches today's single-turn design.

## Candidates checked — evidence beside each, license first

Eight tools searched live (WebSearch/WebFetch, not recalled), 2026-08-23. Full
per-candidate citations are in the individual research passes this PR's author
ran; the table below is the load-bearing extract of each.

| Candidate | License | Maintenance | Trajectory-ablation fit | Longitudinal fit |
|---|---|---|---|---|
| **promptfoo** | MIT (confirmed via GitHub API `license.spdx_id`). Acquired by OpenAI 2026-03-09; OpenAI's own announcement states it "will remain open source under the current license." | Very active — last push same day as this check, v0.122.0 (2026-08-04), 24.5k stars. | **Real, documented `trajectory:*` assertion family** (`tool-used`, `tool-sequence`, `tool-args-match`, `goal-success`), explicitly framed for coding-agent comparison ("two agents might produce identical outputs, but one read 3 files and the other read 30"). Requires the agent to emit OTLP spans — no built-in Claude Code adapter found. | Not found. "Simulated User" is multi-turn within one conversation only. |
| **UK AISI `inspect_ai`** | MIT (GitHub API confirmed). | Very active — daily commits, PyPI-shipped (0.3.249), large surrounding ecosystem (`inspect-swe`, `inspect-evals`). | Full ordered tool-call **event transcript** retained per sample, explicitly designed for custom scorers to read it directly. No packaged with/without ablation-pair primitive found — would be built on top of `Task`/scorer primitives. | Not found as a first-class concept; one doc page (`checkpointing.html`) was flagged unconfirmed, not ruled out with full confidence. |
| **Braintrust** | SDK (JS/Ruby/Go) Apache-2.0; the actual eval/comparison **platform is proprietary hosted SaaS**, self-hosting requires an Enterprise contract (independently corroborated via Langfuse's and MLflow's own comparison pages). | Active, ~weekly SDK releases. | Native **experiment-vs-baseline comparison** (closest primitive to a two-arm diff: named baseline, per-test-case score deltas) and tracing of arbitrary tool calls (task is "any logic"). No doc page describes the specific with/without-context ablation pattern as first-class — would be assembled from parts. | Multi-turn = one conversation, one trace. No cross-session concept found. |
| **DeepEval** | Apache-2.0 (LICENSE.md fetched directly). Genuinely self-contained — runs locally, no required backend (Confident AI cloud is optional, unlike Braintrust). | Very active — release 2 days before this check (4.1.10), 17.8k stars. | **Strong, real trajectory metrics** from actual instrumented execution: Tool Correctness, Argument Correctness, Step Efficiency, Plan Adherence, Plan Quality. Docs explicitly state they do **not** address "comparing trajectories across different conditions or ablation studies." | Explicit: "memory management remains your responsibility — DeepEval observes execution but doesn't store conversation state for you." Multi-turn tracing not yet supported at all per its own docs. |
| **OpenAI `evals`** | MIT (code) + a bundle of separate per-dataset licenses for registry data. | Patchy — a roughly year-long commit gap (late-2024 to late-2025), small 2026 burst, and the README now steers users to a hosted dashboard product. | **None.** Standard prompt→completion→grade shape; explicitly "not currently accepting evals with custom code" upstream — the one thing this problem needs. | None found. |
| **LangSmith / `agentevals`** | Client SDK MIT; the **platform is proprietary SaaS**, self-host needs Enterprise + Kubernetes (independently corroborated by Langfuse/MLflow/DataCamp comparison pages). | Active, commercial, shipping features in 2026. | Real, documented trajectory-match evaluators (strict/subset/superset tool-call sequence matching) — the strongest *scoring* primitive of the SaaS-tier candidates. Docs and examples are LangChain-native only; scoring an external CLI agent's real trajectory is inferred from the message-format shape, never demonstrated. | Docs are explicit: "multi-turn" = linear turns within one thread via `thread_id`. No cross-session memory-boundary concept. |
| **ragas** | Apache-2.0 (LICENSE fetched directly). | Was active through early 2026 (v0.4.3, Jan 2026, ~biweekly releases before that) — **but last commit found is 2026-02-24, ~6 months stale as of this check.** Real caution flag, not disqualifying on its own. | RAG-first heritage (confirmed: `retrieved_contexts` is a first-class sample field), has since added `ToolCallAccuracy` (ordered/unordered tool-call comparison against a reference) — a real trajectory signal, but it **scores a trace you already captured**; no with/without-run orchestration. | Multi-turn samples exist; no documented multi-session or pressure-injection support. |
| **`adewale/skill-eval-harness`** (surfaced by the broader sweep, not on the brief's named list) | MIT (LICENSE fetched directly). | **Single maintainer**: 101 of 125 commits by one person (real name, known engineer), 23 AI-assisted, 1 outside contributor at 1 commit. 10 real tagged releases June–July 2026, then **quiet for 3 weeks** as of this check. 67 stars. | **Closest match found, and genuinely real, not aspirational**: verified in source that `claude_cli_invoke` shells out to the real `claude` binary (`claude -p --output-format stream-json --verbose --no-session-persistence`) with an equivalent path for `codex exec`; `events.json`/`trace.jsonl` are the agent's own real event stream, not fabricated; `build_trajectory_diff` computes real per-case deltas (steps/commands/tool_calls/file_reads/file_writes) and **blocks** (never silently drops) a pair missing trace evidence. Rich, real assertion vocabulary confirmed in source: `tool_call`, `command_ran`, `command_not_ran`, `tool_count_le`, `command_order`, `no_repeated_command_loop`, `skill_invoked`, `total_tokens_le`. | Scripted multi-turn within one run exists (`turns`, not universally supported across its own backends). **No multi-session/memory-boundary concept** — grepped the full source and docs for `memory_boundary`/`multi_session`/`cross_session`: zero hits, and every invocation explicitly passes `--no-session-persistence`. |

Also surfaced, checked more briefly, not deep-dived: **`agents-md-evals`** (MIT,
genuine AGENTS.md A/B testing, but scores final output only, no trajectory
signal); **`eval-view`/EvalView** (Apache-2.0, real baseline-vs-current
trajectory snapshot testing, but regression-detection framed, not a
with/without-context ablation mode); **LangChain `agentevals`** (MIT, real
trajectory-match evaluators, but matches against a fixed reference trajectory,
not a second live run). None changes the picture below.

**The single fact that generalizes across all eight:** every candidate's
"multi-turn" means *within one continuous conversation*. Not one documents,
demonstrates, or even gestures at a scenario spanning genuinely separate agent
processes with a structural memory wall and pressure introduced after it. This
is not a gap in the search — four separate research passes looked for it
specifically and it is not there. The exact axis `docs/historical/eval-harness-findings.md`
and `docs/research/eval-longitudinal-design.md` argue is the current instrument's real
blind spot, and that three hand-run trials already validated as worth pursuing,
does not exist anywhere in the market as of this check.

## A ninth candidate, found late: `microsoft/hve-core` and `@microsoft/vally-cli`

Jon pointed at `microsoft/hve-core` — "roughly Microsoft's agent-dotfiles, with
evals in it" — after the eight-candidate search above was already written.
Checked directly (local clone, `b1cae50`, 2026-08-22; the actual runner,
`@microsoft/vally-cli`, installed and inspected separately since it is a real,
independently-published npm package, not vendored code) rather than trusting
either Jon's description or the brief's own summary of it. This is a real hit,
stronger than any of the eight above on the primitive that mattered most, with
one real caveat and one thing the brief worried about that turned out not to
be true.

**License — MIT, confirmed twice.** `hve-core`'s own `LICENSE` (Microsoft
Corporation copyright). Separately and just as importantly: `@microsoft/vally-cli`
**and** its core library `@microsoft/vally` are *each independently* MIT-licensed
per their own `package.json` `license` fields — this is not hve-core
relicensing a private tool, `vally` is a standalone, publicly-published npm
package (14 versions on the registry, current 0.14.0, hve-core pins 0.13.0).

**The direct hit — `evals/baseline-equivalence/`.** Exactly our ablation,
already built and running: identical stimuli run twice, once against an empty
baseline environment and once against an environment that materializes the
target agent/skill, joined by `vally compare --baseline <dir> --treatment
<dir>` into a signed mean score, 95% CI, and win rate. This is not aspirational
README text — `evals/agent-conformance/rai-planner/eval.yaml` was read
directly and confirms the weighted-advisory-scoring claim exactly as
described: `scoring.weights: {prompt: 0.7, wall-time: 0.15,
output-contains: 0.15}`, `threshold: 0.7`, with the file's own comment stating
"the judge alone clears the threshold; the other graders are advisory
budgets." **This is precisely the fix for our own `#267` bug** (the
conjunctive cheaper-AND-correct rule that let a cheaper-but-worse arm block a
real `improve` verdict on `mechanize`) — free to steal regardless of anything
else in this section.

**The executor-coupling worry, checked rather than assumed, and it does not
hold the way it looked.** Every `eval.yaml` found in `hve-core` declares
`executor: copilot-sdk` — real coupling, confirmed. But `vally --help` and
`vally eval --help` (run directly against the installed 0.13.0 package, not
inferred from docs) show `--executor <name>` as a first-class CLI flag, and
the installed package's own `executor/types.d.ts` defines a documented,
public `Executor` interface:

```ts
export interface Executor {
  name: string;
  supportsPreparedWorkspace?: boolean;
  supportsMultiTurn?: boolean;
  supportsTurnCompletion?: boolean;
  supportsSimulation?: boolean;
  supportsAttachments?: boolean;
  supportsEnvVars?: boolean;
  validateConfig?(config: unknown): void;
  execute(stimulus: Stimulus, options: ExecutorOptions): Promise<Trajectory>;
  shutdown(): Promise<void>;
}
```

— plus a real `discovery.js` implementing dynamic plugin loading: `specifier`
(an npm package name or local file path) exporting a `register(registry)`
function, with atomic-commit/staging semantics shared with vally's other
plugin kinds. Only two executors ship today (`copilot-sdk-executor.js`,
1,371 lines; `mock-executor.js`, a 208-line reference implementation for
dry-runs/tests) — no `claude`/`claude-code`/`codex` executor exists yet — but
the extension point is real, documented, and bounded: writing one means
implementing `execute()`/`shutdown()` by shelling out to `claude -p
--output-format stream-json`, almost exactly what our own `eval_skill.py`'s
`run_agent()` and `skill-eval-harness`'s `claude_cli_invoke` already do,
retargeted at vally's `Trajectory` schema instead of our own. **Verdict on the
brief's own fit question: not "study-only in practice."** The coupling is
real work (one new executor plugin, no small task, but bounded and precedented
by the `mock-executor.js` reference shape) — not a hard architectural wall.

**The `turns` question, checked precisely — real, but not the primitive we
actually need.** `Stimulus.turns?: string[]`'s own doc comment: prompts are
delivered "sequentially to the same agent session, **preserving conversation
context**." This is genuine, working multi-turn-with-pressure-introduced-
partway (`StimulusGraderConfig.turn` lets a grader score a specific turn, not
just the final state — real divergence-point-style scoring infrastructure),
and it goes further than every one of the eight candidates in the first
search, none of which had turn-scoped grading. **But it explicitly preserves
context across turns** — it is the same "multi-turn within one continuous
conversation" shape every other candidate had, not `docs/eval-longitudinal-
design.md`'s required structural memory boundary (a genuinely fresh agent
process, given only disk state, no transcript). `turns` cannot supply that
boundary no matter how it is used. **What can, without vally needing to
change at all:** the composition `baseline-equivalence` already uses — two
separate `vally eval` invocations (two genuinely separate agent processes,
zero shared context between them, precisely the boundary the design doc
requires) with session 2's `--work-dir` seeded from session 1's own output
artifacts, joined by `vally compare` — is a thin driver script on top of
primitives vally already has, not a missing feature. This reframes the
longitudinal build: not "build a harness feature vally lacks," but "write the
same two-invocation-plus-compare driver `baseline-equivalence` already
demonstrates, pointed at a session-2-starts-from-session-1's-disk fixture
instead of a baseline-vs-customized one."

**What stays a real cost, not resolved by any of the above:** hve-core's own
orchestration (`scripts/evals/Invoke-BaselineEquivalence.ps1` and siblings) is
genuinely PowerShell — real friction for a bash/Python-first estate, exactly
as the brief flagged. This is separable and does not need adopting: `vally` is
a standalone Node/npm CLI, invokable directly from bash or Python with no
PowerShell in the path; a thin driver in this estate's own idiom (mirroring
what `eval_skill.py` already is) replaces the PowerShell layer, not vally
itself.

**Also present, not deep-dived, worth a name:** `skill-hygiene` (static
`vally lint` over every `SKILL.md`, no executor calls — a cheap structural
check this estate has no equivalent of today) and a documented three-tier
maturity ladder (PR-advisory / nightly-authoritative / a third tier that never
fails a build) that answers, better than anything built here, the "how do we
trust a verdict enough to gate on it" question this loop has never actually
solved (today, nothing gates on any eval verdict at all).

## Recommendation, per component

### 1. Scenario format — replaceable leaf. Keep building; steal the vocabulary.

Our `prompt.md`/`criteria.md`/`fixture/` convention is already cheap and already
working (40 skills' worth of scenarios exist). Nothing found is worth swapping
it for. What **is** worth stealing: `skill-eval-harness`'s assertion vocabulary
(`command_order`, `no_repeated_command_loop`, `tool_count_le`, `skill_invoked`)
as a **contract**, not a dependency — most of `criteria.md`'s current "scored by
`score_X`" language describes exactly this kind of check in ad hoc prose per
skill (`tdd`'s own criteria.md hand-describes a tool-call-order check that a
`command_order` assertion type would express directly and reusably). Being
wrong about this costs a rewrite of one convention file, not a system.

### 2. Runner — reopened by `vally`. Adopt the platform, build one executor plugin.

The original draft recommended stealing `skill-eval-harness`'s adapter
contract without vendoring it (single maintainer, 21K-line file, three weeks
quiet). `vally-cli` changes this component's answer, not just its degree:
it is MIT-licensed *at the actual package level* (not a thin single-maintainer
repo — a Microsoft-published npm package on its 14th release, with `compare`,
`grade`, `oracle`, `experiment`, `serve`, `ingest`, and `lint` all real and
shipping, not just `eval`), it already implements the exact ablation shape
(`baseline-equivalence`) our own `eval_skill.py`+`eval_arm.py` hand-rolled,
and its weighted-advisory scoring already fixes a bug (`#267`) ours still
has. The blocker is real (no Claude/Codex executor ships) but is a documented,
bounded extension point — implement `Executor.execute()`/`shutdown()` against
a public interface, precedented by a 208-line reference implementation
(`mock-executor.js`) — not the closed, single-vendor wall the brief was right
to worry about checking for.

**Recommendation: adopt `vally-cli` as the runner+comparison substrate; build
one `claude-code` (and, later, `codex`) executor plugin against its
documented `Executor` interface.** This is a genuine "adopt," not a
contract-only steal, specifically because the package itself clears every bar
step 4 sets (real license, at the package we'd actually depend on) and the
piece we'd still write (one executor plugin) is bounded, precedented, and
would have to be written *regardless* of which runner we chose — every
candidate researched, including `skill-eval-harness`, required writing or
already had separate per-CLI adapters. Replaces `eval_skill.py`'s
`build_fixture`/`run_agent`/`eval_arm.py`'s stash mechanism; does not require
adopting hve-core's PowerShell orchestration layer, which stays out of scope
(a thin bash/Python driver in this estate's own idiom replaces it, the same
role `eval_skill.py` already plays).

### 3. Scorer — split, and reopened in one place by `vally`.

If component 2's `vally` recommendation is taken, its `scoring.weights`
mechanism (judge grader clears threshold, cost/latency graders stay advisory,
confirmed real in `evals/agent-conformance/rai-planner/eval.yaml`) directly
replaces `eval_skill.py`'s own `verdict()` — and fixes a bug ours has
(`#267`'s conjunctive cheaper-AND-correct rule) that `verdict()` does not.
This is adoption, riding on component 2's adoption, not a separate decision —
the generic efficiency-delta function only stays a "replaceable leaf, fine
as-is" if the runner recommendation above is *not* taken; if it is, `vally`'s
scoring engine comes with it and is strictly better on the one concrete bug
this loop has already found.

Independent of that: DeepEval's and promptfoo's named trajectory metrics
(Tool Correctness, Step Efficiency, Plan Adherence) are still worth stealing
as **vocabulary** for `criteria.md`/`eval.yaml` authors, whichever runner
underlies them — naming, not a library, for the reason the first draft gave.

The **per-skill hand-judgment against criteria.md** — what actually decides
most of the 40 verdicts today, since only one skill has a registered code
scorer — is design, not code, and stays exactly that. No candidate anywhere in
this search replaces a human/agent reading a transcript and applying written
criteria; that is inherent to grading behavioural nuance, not a tooling gap
eight vendors independently failed to fill.

### 4. Record — trust boundary. Build, not negotiable.

`docs/eval-status.json` / `docs/eval-log/*.jsonl` is, in the brief's own words,
"the thing verdicts are read from" — every downstream `keep`/`drop` decision
about what stays in this estate's skill roster reads this record, not the raw
transcripts. Nothing in this search even attempts to be a "verdict ledger" —
every candidate is upstream of this (execution or scoring), none is this. It is
already small, git-native, append-only (specifically to survive the
concurrent-PR conflict this loop already learned the hard way, per
`eval_status.py`'s own docstring), and auditable by anyone who can read JSONL.
Correctly built in-house already; there is no adoption question here.

### 5. The longitudinal gap — still build the boundary; `vally`, if adopted, cuts what has to be built.

Nine candidates now checked, including `vally`. **None documents a genuine
cross-session memory boundary** — `vally`'s own `turns` explicitly preserves
context across turns, the same "multi-turn within one conversation" shape
every other candidate had. This part of the original conclusion is unchanged:
nothing exists to adopt for the boundary itself.

What changes if component 2's recommendation is taken: the boundary does not
need a bespoke runner underneath it. `baseline-equivalence`'s own composition
— two separate `vally eval` invocations (two genuinely independent agent
processes, by construction no shared context, exactly the structural wall
`docs/research/eval-longitudinal-design.md` requires) joined by `vally compare`, with
`--work-dir` for the second invocation seeded from the first's own output
artifacts — supplies the boundary as a thin driver script, not a new harness
feature. This *lowers* the cost of generalizing the design without changing
its evidentiary basis: it is still one hand-run trial (`loop-memory`), and
`devils-advocate` below still applies — run it against one or two more
`clean no-discrimination` skills before treating it as a reusable feature,
whichever runner ends up underneath it.

## Interim conclusion, research pass 1 (pre-`vally` — superseded, see below)

*Kept for the record rather than rewritten over: this was the conclusion
before Jon pointed at `microsoft/hve-core` and it was checked. The final
conclusion, after a second `devils-advocate` pass specifically on adopting
`vally`, is at the bottom of this document.*

1. `skill-eval-harness`'s assertion-type vocabulary for `criteria.md` (scenario
   format) — reimplemented as naming, not code.
2. `skill-eval-harness`'s CLI-adapter module specifically (`claude_cli_invoke`/
   `codex_cli_invoke`/`run_argv_capture`, under 2,000 lines total, under 10% of
   the file, 75 dedicated tests) — **fork or vendor this slice directly**, MIT
   permits it, and it is small and independently tested enough that
   reimplementing it from a pattern would mean re-earning CLI streaming/
   lifecycle edge cases already paid for. Do not adopt the surrounding
   21,034-line file's scoring/grading/reporting bulk — that part stays exactly
   the "read the contract" case the first draft made.
3. DeepEval's/promptfoo's named trajectory-metric vocabulary (Tool Correctness,
   Step Efficiency, Plan Adherence) for scorer terminology — reimplemented as
   naming, not code.

Items 1 and 3 are shapes to read once and rename into our own ~20-40 lines,
matching this skill's own "contract over vendored code" rule. Item 2 is the one
place this pass concluded the opposite — the candidate is thin as a *whole
package* but the specific slice needed is small, bounded, and tested enough
that vendoring beats reimplementing.

The longitudinal design is still where the next real engineering effort
belongs — no candidate, of eight checked, documents cross-session/memory-
boundary support — but **not as a general harness feature yet**. One hand-run
trial (`loop-memory`) supports the design; run it against one or two more of
the remaining `clean no-discrimination` skills (`ask-a-council` or
`sanity-check` first, per `docs/research/eval-longitudinal-design.md`'s own
candidate-selection discipline) before generalizing it into a reusable
`eval_skill.py` feature. Building the general feature on n=1 is the thing this
document's own `devils-advocate` pass correctly caught as too early.

## `devils-advocate` pass 1 (pre-`vally`)

Run as a dedicated opposing pass (per the skill's method: assume the
recommendation above is wrong, argue from there, require evidence, name the
checkable condition for each objection) before this shipped. Full attack below,
then what changed and what didn't.

### Objections that changed the recommendation

**Runner (#2): "steal the contract, don't vendor" was under-verified — the
21,034-line size cited to justify reimplementing from a pattern describes the
whole file, not the piece actually being borrowed.** The attack's own
checkable condition: measure how much of `skill-eval-harness` is CLI-adapter
plumbing versus everything else, and check whether that slice has its own
tests. Checked directly (clone + `wc -l` + `grep` for adapter tests, not
re-asserted from the earlier pass): `claude_cli_invoke` is 308 lines,
`codex_cli_invoke` 1,076, and the full family of `*_cli_invoke`/
`*_judge_invoke` adapter functions plus their shared `run_argv_capture`/
`ProcessInvocationPlan` plumbing totals under **2,000 lines — under 10% of the
file** — with **75 dedicated tests** in `tests/test_runners.py` alone (plus
`test_judging.py` covering the judge-invoke siblings). This is a small,
bounded, independently-tested, MIT-licensed module, not entangled with the
21K-line file's scoring/grading/reporting bulk. **Recommendation sharpened**:
this specific slice is small and tested enough to **fork or vendor directly**
(with attribution, MIT permits it) rather than defaulting to a from-scratch
reimplementation "from the pattern" — reimplementing here would mean re-paying
for CLI streaming/lifecycle edge cases `skill-eval-harness` already has tests
for, for no benefit over taking the module itself. Read `test_runners.py`
first to confirm its assertions match our own subprocess-invocation
assumptions before forking; if they diverge meaningfully, fall back to the
original "read the contract" position for the parts that don't fit.

**Longitudinal (#5): building a general harness feature on an n=1 trial is
thin, even though the diagnostic work the objection asked for already
exists.** The attack's premise — "pull the failure taxonomy behind the 74%
figure before investing in more harness, in case the failure is scenario
design, not harness capability" — is *already answered* in
`docs/historical/eval-harness-findings.md`, more thoroughly than the attack could see
from this document alone: three separate escalation trials each targeted a
different rival hypothesis (`create-skill`: a leaked-fixture fix, ruling out
"just a bad scenario" for that one skill; `distill`: three axes of
single-shot hardening — scale, adversarial pressure, ambiguity — ruling out
"just needs to be harder"; `loop-memory`: the one genuine cross-session trial,
the axis nothing else had tested). So this is not an uninvestigated question.
**But the attack is still right that the evidence for the *specific*
recommendation — generalize the longitudinal design into a reusable harness
feature — is thin**: exactly one hand-run trial supports it, and
`docs/historical/eval-harness-findings.md` says so itself ("does not settle the question
for the remaining six"). **Recommendation sharpened**: do not generalize the
longitudinal design into a reusable `eval_skill.py` feature yet. Run it
hand-scored against one or two more of the six untested `clean
no-discrimination` skills first (`ask-a-council` or `sanity-check` are the
next-best candidates — neither has a self-diagnosed axis prediction pointing
elsewhere the way `tdd`'s does toward scale/ambiguity) — the same discipline
`docs/research/eval-longitudinal-design.md` itself already used to justify picking
`loop-memory` first. Generalizing into a harness feature is the right call
once two or three trials agree, not after one.

### Objection left open, not resolved here

**Whether `inspect_ai`'s checkpointing or Braintrust's experiment-comparison
primitive could substitute for a hand-built cross-session boundary** — the
original research flagged `inspect_ai`'s `checkpointing.html` as
"unconfirmed," not ruled out, and never attempted threading a second,
later-session agent invocation through either tool's session/experiment
concept. This is a real gap in the research, cheap to close (a few hours,
not a rebuild), and not closed in this pass — effort here went to the two
checkable conditions above instead. Flagged honestly as unresolved rather
than quietly dropped: if either primitive turns out to persist real
conversation-shaped state across a process boundary, it would change the
longitudinal recommendation from build-only to a substrate worth building on.

### Objection judged real but conditional, not resolved here

**Record (#4): rejecting a SaaS platform for the ledger doesn't require
rejecting one for a read-only comparison view over the same ledger** — real
if the "eval-status.json is machine JSON, nobody has a dashboard" friction is
actually felt, not hypothetical. Not established either way in this pass.
Worth a one-line check (has anyone actually gone looking for a human-readable
view and hit friction) before treating it as a live gap.

## `devils-advocate` pass 2 — on adopting `vally`

The `vally` finding above (candidate 9, found after pass 1) is a big enough
change to the recommendation that it earned its own dedicated opposing pass,
per the same method as pass 1: assume "adopt `vally`, build one executor
plugin" is wrong, argue from there, require evidence.

### Objections raised, and what direct verification did to each

**Objection: nobody had run `vally eval` end-to-end — every claim rested on
reading source and docs, one level short of "did we try it."** Real when
raised. **Resolved, not left open**: ran it directly after the attack landed
— `vally init`, `vally lint -e eval.yaml`, then `vally eval -e eval.yaml
--executor mock`. All three completed cleanly against the package's own
reference `mock-executor.js`; the run produced a real, well-structured
`results.jsonl` (`trial-result` → `gradeResult` → per-grader `details[]` →
`trajectory`), plus markdown and OpenTelemetry-span artifacts on disk, all at
the paths the CLI itself reported. This is real execution evidence, not
inferred from `.d.ts` files.

**Objection: telemetry/network behavior was unchecked — real governance risk
for a Microsoft tool evaluating an Anthropic-CLI-driven estate.** Partially
resolved. `vally init`'s own first-run output discloses its telemetry scope
directly, unprompted, before any command that would send data: "command name,
version, outcome, duration, persistent device identifier (when available),
and coarse OS/runtime info... **No prompts, datasets, file paths, or
arguments are collected**," opt-out via `VALLY_TELEMETRY_OPTOUT=1` or the
standard `DO_NOT_TRACK=1`. This is first-party disclosure at the point of
use, not a README claim read out of context — real, positive evidence. **Not
fully closed**: this pass did not independently packet-capture a run to
verify the disclosure is exhaustive (no `lsof`/firewall-deny check was run).
Treat the network-safety question as *substantially* de-risked, not fully
closed — a five-minute packet capture is cheap and still worth doing before
any real credential or private-repo content touches a `vally eval` run.

**Objection: the executor-plugin cost is asserted ("bounded, precedented"),
not measured — the one real data point (`copilot-sdk-executor.js`, 1,371
lines) is nearly 4x the entire harness being replaced.** **Not resolved,
correctly still open.** No `claude` executor was prototyped — doing so is
implementation, and this PR's own brief rules that out. This stays the
single largest unresolved risk in the "adopt" recommendation.

**Objection: the `Executor` interface is pre-1.0 and might already be
unstable — adopting infrastructure against a moving target with no upstream
relationship.** **Checked directly, and the objection is confirmed, not
speculative.** Pulled `@microsoft/vally`'s `executor/types.d.ts` across four
published versions (`npm pack` at 0.6.0, 0.10.0, 0.13.0, 0.14.0) and diffed
them: the interface grew from 96 lines (0.6.0) to 224 (0.13.0/0.14.0), with a
genuine structural change, not just additions — 0.6.0's
`FinalizeWorkspaceContext`/`finalizeWorkspace` remote-workspace-sync concept
is gone by 0.14.0, replaced by `ExecutorTurnCompletion`/
`supportsTurnCompletion` for multi-turn support, alongside new capability
flags (`supportsMultiTurn`, `supportsSimulation`, `supportsAttachments`,
`supportsEnvVars`, `validateConfig`) that did not exist at 0.6.0. **This is
real, confirmed pre-1.0 breaking change, not a hypothetical risk** — a
`claude` executor written against 0.13.0 today is written against an
interface that has already reshaped itself at least once. One point in
`vally`'s favor found in the same check: 0.13.0 and 0.14.0 are byte-identical
in this file, suggesting the interface may be settling, not still churning —
but one stable release pair is weak evidence of a trend.

**Objection: "more capable" may not be the right axis — a legible, ~365-line,
stdlib-only harness has a real value the platform migration would spend.**
Not resolved, and not fully attacked either — this is a values call, not a
factual one. What direct evidence *does* support (see below): the one thing
actually wanted from `vally` right now, weighted-advisory scoring, can be
taken as an idea and ported into the existing Python harness for near-zero
cost, without resolving whether the rest of the platform is worth adopting.

### What this pass changes about the recommendation

The interface-instability finding is new, real, and was not in the original
`vally` write-up — surfaced only because a dedicated opposing pass was run
rather than skipped. Combined with the unmeasured executor-plugin cost, the
honest position is no longer an unqualified "adopt `vally`, build the
executor." It is: **adopt the weighted-advisory-scoring contract immediately
— zero dependency, zero platform risk, fixes a confirmed bug (`#267`) today —
and treat full `vally` adoption as a live, promising, but *not yet decided*
candidate, gated on a bounded spike this decision-only PR does not include:
build a minimal `claude` executor, measure its real size against the two
named Python-harness gaps, and packet-capture one run.** This is closer to
the brief's own suggested honest shape than the pre-pass-2 draft was: "the
executor coupling [is not disqualifying, but] we steal the weighted-scoring
model and the two-run/compare contract" now, and revisit the rest once
spiked.

### Objections attempted and discarded (pass 1)

Scenario format (#1) and scorer (#3, as it stood pre-`vally`): the attacker's
own assessment, after trying, was that no genuine case exists against
contract-only borrowing for either — the existing 40-skill convention and the
39/40-skills-have-no-code-scorer reality make vendoring disproportionate for
both. Recorded as attempted and failed, not skipped. (Pass 2, above, reopened
part of #3 specifically — the weighted-scoring piece — once `vally` was
found; the rest of this pass 1 finding stands.)

## Overall — final, after both `devils-advocate` passes

1. **Scenario format** — build, steal `skill-eval-harness`'s assertion
   vocabulary as naming. Unattacked successfully in either pass; unchanged.
2. **Runner** — do not commit to full `vally` adoption in this PR. Immediately
   portable: nothing (the runner itself has no zero-cost win the way scoring
   does). Gated on a bounded spike, explicitly out of this decision-only PR's
   scope: build a minimal `claude` executor against `vally`'s documented
   `Executor` interface, measure its real size, and packet-capture one run —
   before deciding adopt vs. continue the bespoke Python harness. Until that
   spike runs, default to the bespoke harness (`eval_skill.py`/`eval_arm.py`)
   continuing to own this component, adding its own Codex adapter if Codex
   support is needed sooner than the spike.
3. **Scorer** — split, and one piece is a same-day win: port `vally`'s
   weighted-advisory-scoring rule (judge alone clears the threshold; cost/
   latency stay advisory budgets) into `eval_arm.py`'s verdict logic now —
   zero dependency, zero platform risk, and it fixes a bug (`#267`) the
   current conjunctive rule has today. DeepEval's/promptfoo's trajectory-
   metric naming is still worth stealing as vocabulary, independent of
   runner choice.
4. **Record** — build, trust boundary, unattacked successfully in either
   pass. One open, unresolved thread: check (cheaply, doesn't require a
   decision here) whether the "no human-readable view of eval-status.json"
   friction is real before treating a read-only dashboard as a live gap.
5. **Longitudinal gap** — still build the memory boundary; no candidate, of
   nine now checked including `vally`, documents cross-session support.
   Run the existing hand-scored design against one or two more skills before
   generalizing it into a reusable feature (pass 1's finding, unchanged by
   `vally`). If the runner spike above lands on "adopt `vally`," the boundary
   becomes a thin two-invocation-plus-`compare` driver script rather than new
   harness code; if it lands on "keep the bespoke harness," it is the same
   two-invocation composition against `eval_skill.py` instead. Either way,
   the design and its evidence bar are unchanged — only what sits underneath
   the two invocations differs.

**The honest single-sentence answer this document was asked for**: build the
scenario/scorer/record layers (stealing naming from several tools and one
scoring *rule* — not code — from `vally`, ported today for near-zero cost),
keep building the longitudinal boundary by hand a little further before
generalizing it, and treat adopting `vally` as the runner as a real,
evidence-backed, *not-yet-decided* option — the strongest candidate found by
a wide margin, reopened by a genuine `devils-advocate` pass rather than
rubber-stamped, gated on one bounded spike outside this PR's own
no-implementation scope.

## The spike ran — component 2 and 3's gate, closed

The bounded spike this document gated components 2 (runner) and 3 (scorer)
on has run (`spike/vally-spike.md`; the actual code, private, is
`jonhill90/agent-evals#23` — cited by number only, per this repo's own rule
against publishing scenario prompts/criteria/transcripts, none of which are
reproduced here). One question, stated in advance, both outcomes stateable
before starting: **can one `Executor` plugin drive our real Claude arm
under `vally`, and does `vally compare` then produce a usable two-arm
result?**

**Answer: yes**, confirmed with a real run, not asserted. A ~215-line,
zero-dependency `Executor` plugin — porting `eval_skill.py`'s own
`run_agent()` NDJSON parsing to the interface, not rewriting it, exactly as
the spike brief predicted would be the actual asset — drove a real two-arm
run against `research-the-limit` (the one skill with a registered,
mechanical scorer, so its result is directly comparable to the existing
record). Real result: outcome tied, cost noisy with no consistent
direction — **consistent with, not contradicting**, `research-the-limit`'s
own already-recorded public verdict ("outcome axis a wash across all
three [runs]... cost swung in both directions... read as noise",
`skills/research-the-limit/references/eval-result.md`). One `vally`-driven
trial landed inside that same described pattern.

Two real integration gaps were found and fixed along the way, neither a
defect in `vally`, both places the spike's own first assumption was wrong
— full technical account in the private PR, summarized here because the
*shape* of each finding matters for the record even though the fixture
content does not:

1. **Environment inheritance** — spawning `vally` with a hand-picked
   environment subset silently stripped Claude Code's own credential state
   several process layers down, failing every trial with an auth error
   that looked at first like a `vally` or executor problem and was neither.
2. **Fixture delivery** — `--work-dir` does not mean "run in this
   directory" (`vally`'s own pipeline always allocates a fresh temp
   sandbox per trial, unconditionally); the real, declarative path for
   "materialize from a local git repo I already built" is
   `environment.git` (`type: worktree`), which lines up with
   `eval_skill.build_fixture()`'s own output with no redesign needed —
   but only once you know to reach for it instead of the flag that reads
   like it should mean exactly that.

**What this does not resolve, stated as precisely as the first draft
insisted on:** the `Executor` interface's own pre-1.0 version-instability
risk (`devils-advocate` pass 2's own finding, 96→224 lines across four
diffed versions) is untouched by one successful run on `0.13.0` — that risk
still belongs to a full-adoption decision, not to this spike, and one
green run does not retire it. n=1: one skill, one trial per arm, one
machine, one session.

**Components 2 and 3, unblocked:**

- **Component 3 (scorer):** the weighted-advisory scoring rule is no
  longer just described, it is real, tested, additive code —
  `weighted_verdict()` in `eval_skill.py` (`agent-evals#23`), vally's own
  `scoring.weights` shape, offered as an opt-in path alongside `verdict()`
  without touching or risking that function's own existing, deliberately-
  tested n=1-caution behavior. Taken regardless of the spike's outcome,
  per the brief; the spike happened to succeed, and it was taken anyway,
  exactly as instructed.
- **Component 2 (runner):** the spike answers "can this work at all" —
  yes — without resolving "should we commit to it long-term," which was
  never this spike's question. The honest position is unchanged in kind
  from the first draft, sharpened by real evidence instead of a
  read-the-docs estimate: `vally` remains a real, evidence-backed,
  *not-yet-decided* option for the runner. What changed is the confidence
  behind "not-yet-decided" — from "unverified, gated on a spike" to
  "verified to work on one real case, still carrying an unresolved
  version-stability question that a single run cannot answer." Whether
  that's enough to commit to full adoption, versus running the same spike
  against one or two more skills first, is a call for whoever owns this
  decision next — this document's job was answering whether the gate
  could be passed at all, and it can.
