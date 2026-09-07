---
type: Diagnosis
description: Why 29 of 41 skill evals read could_not_measure, grouped by cause with a count, and the single cheapest concrete fix -- not another eval pass.
generated:
  at: 2026-08-23T20:15:00-04:00
---

# Why 29 of 41 evals are `could_not_measure` — grouped by cause, not by theory

`python3 scripts/eval_status.py --summary`, measured directly: `could_not_measure: 29`,
`unevaluated: 0`. This document reads all 29 of the individual
`references/eval-result.md` records directly, groups them by the reason
the record itself gives for the verdict, and names one concrete next
action — it does not re-run anything or re-derive causes this repo
already diagnosed.

**Two things already settled, not re-opened here:**
`skills#276` filed and refuted a taxonomy hypothesis the same day it was
raised — the 29 are not unevaluable by category. `skills#230` ("26 of 35
never evaluated") is closed; every one of the 41 skills has now run at
least once (`unevaluated: 0`, confirmed above) — the coverage framing is
stale, the instrument is the live question.

## Build on `docs/historical/eval-harness-findings.md`, don't repeat it

That document already read 25 of what is now 29 `could_not_measure`
records and built a five-cause taxonomy with per-skill membership:
**Clean no-discrimination (9), Scorer/regex misread (6), Fixture/
installation defect (4), Cost-signal noise (4), Scenario design defect
(2)** — 25 skills, unchanged here. It also already named the class of
defect the four newest records (below) turn out to hit — "Cause D," a
tool skill with real system access whose scenario has no fixture-sandbox
boundary — before any of the four had actually run. Confirming its
prediction, not repeating its analysis.

What that document explicitly does not cover: three skills evaluated
after it was written (`github-cli`, `linear`, `obsidian`, closing their
prior `unevaluated` status via PR #269) plus `tmux`'s own pass. 25 + 4 =
29 — the entire gap between that document's count and today's is exactly
these four, and all four land in one new, sixth cause.

## The sixth cause: arm-wiring cannot be confirmed — 4 of 29 (14%)

`github-cli`, `linear`, `obsidian`, `tmux` each deliver the skill to Arm A
by prompt instruction ("read `SKILL.md` before starting"), not the `Skill`
tool — deliberately, to dodge Cause D. Each of their own `eval-result.md`
records says the same thing in its own words: *"a clean tie of this shape
cannot currently be told apart from an unconfirmed wiring problem in the
arm meant to have the skill, because nothing in this measurement design
independently confirms the skill's own content was actually read."*
`tmux`'s first pass goes further — it discovered mid-run that the arm
meant to have the skill **could not load its content at all**, and
correctly discarded that pair rather than record it as a tie.

**This is not a new problem — it already has a shipped fix that these
four records could not have used.** `skills#269`'s review found exactly
this gap and `skills#273` closed it the same day:
`scripts/skill_read_confirmed.py`'s `skill_read_confirmed(transcript_path,
skill_path)` scans a trial's real transcript for a genuine `Read`
tool-use block against the skill path, tri-state (`true`/`false`/
`unknown`, never collapsing a `could_not_measure`-shaped input into a
confident negative), and `docs/historical/eval-harness-findings.md`'s own "Standing
requirement" section already mandates a populated
`arm_a_skill_read_confirmed` field on exactly this shape of record.

**Checked directly, not assumed: none of the four log entries carry that
field.** `docs/eval-log/{github-cli,linear,obsidian,tmux}.jsonl` — read
all four — none has an `arm_a_skill_read_confirmed` key at all.
`github-cli`/`linear`/`obsidian` (`PR #269`, merged
`2026-08-23T16:15:53Z`) ran **46 minutes before** `skill_read_confirmed.py`
existed (`skills#273`, merged `2026-08-23T17:01:07Z`) — they could not
have populated a field that did not yet exist. `tmux`'s two log entries
predate it too. This is not a records-management oversight; it is four
records whose evaluations genuinely finished before their own repo's
required check was built.

**Could not measure directly**: whether the four skills' real transcripts
still exist to run `skill_read_confirmed.py` against without a fresh
trial — those transcripts, if retained at all, live in the private
`jonhill90/agent-evals` repo, which this pass has no access to. Stating
the gap rather than guessing whether it's cheap or expensive to close.

## The single biggest cause, with a count

**Clean no-discrimination remains the largest bucket: 9 of 29 (31%)** —
unchanged in membership from `docs/historical/eval-harness-findings.md` (`ask-a-
council`, `dispatching-subagents`, `distill`, `sanity-check`, `tdd`,
`create-skill`, `loop-memory`, `memory-conventions`, `spec`), still ahead
of scorer/regex misread (6) and the newly-named arm-wiring cause (4).
Three of these nine have since been directly escalated (`create-skill`'s
fixture rebuilt clean, `distill` hardened on scale/pressure/ambiguity,
`loop-memory` run longitudinally across a real session boundary) and
**none discriminated** — the strongest evidence this repo has that for
this specific skill class (habit/consistency skills, not capability
skills), a single-turn present/absent comparison is measuring the
dimension these skills are least likely to fail on. That argument, and
what would actually test the dimension they're built for, is already
made in full in `docs/historical/eval-harness-findings.md` §"What would actually
measure these skills?" — not repeated here.

## What would fix it — two different fixes, for two different causes

**1. Cheapest, most concrete, do this first: retrofit
`arm_a_skill_read_confirmed` onto the four arm-wiring records.** The tool
already exists and does not need to be built. For each of `github-cli`,
`linear`, `obsidian`, `tmux`: locate the trial's real transcript (in
`agent-evals`, if retained) and run `skill_read_confirmed.py` against it;
if a transcript no longer exists, a single fresh bounded trial per skill
— not a new harness, not a new scenario, the existing one — closes the
same gap. This resolves a real, currently-open ambiguity in four already-
written verdicts, for less cost than any new eval pass, and is the one
recommendation in this document that requires no design decision — the
standard was already set by this repo's own `docs/historical/eval-harness-findings.md`,
the tool that meets it already merged, only the application to these four
records is outstanding.

**2. Separately tracked, larger, not a design decision this document
makes: `vally`'s scoring model.** `skills#267` proved the current
conjunctive cheaper-AND-correct rule cannot register a real divergence —
`mechanize` trial 2 found the skill-loaded arm did the disciplined thing
and the rule had no way to score it. `vally`'s `scoring.weights` model
(model-judge grader clears the threshold; cost and latency stay
*advisory*, never required to also move) fixes exactly that conjunction.
The bounded spike this was gated on has already run and closed — reported
separately, with evidence, in a comment on the merged
`jonhill90/skills#275` (not re-derived here): the spike succeeded (a real
`Executor` plugin drove a real two-arm run under `vally 0.13.0`), the
scoring-rule port itself (`weighted_verdict()`) already shipped in that
same PR, additive to `eval_skill.py`'s existing `verdict()`. What remains
undecided is full `vally` *runner* adoption, which `#275` itself states
plainly is a separate, larger, not-yet-decided call — not blocked on
anything this document found.

## Recommended next action, and why it beats the alternatives

**Retrofit `arm_a_skill_read_confirmed` on the four arm-wiring records
(github-cli, linear, obsidian, tmux) before running anything new.**

Not "run more evals": the harness working as designed on a genuine tie is
already 9 of 29 records (31%, the largest bucket) — more passes on
unescalated scenarios mostly manufacture more of the same, correctly-
measured non-signal, which is exactly what this brief was written to stop
paying for. Not "harden the nine clean-tie skills' scenarios": that is
real, valuable work `docs/historical/eval-harness-findings.md` already scoped
concretely (§4, three axes named), but it is scenario-design work for a
skill class already well-understood, not a diagnosis gap. Not "adopt
`vally`'s runner": that decision is explicitly not blocked on anything in
this document and belongs to whoever owns that separate, larger call. The
arm-wiring retrofit is the one action that is cheap (a tool that already
exists, applied to four already-written records), concrete (closes a
named, checkable gap — a missing field — not a design question), and
actually changes what four existing verdicts mean rather than adding a
thirtieth `could_not_measure` to a pile that is already dominated by
correctly-measured non-signal.
