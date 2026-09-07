# Does a counting measurement generalize beyond progressive-disclosure? (skills#266)

Answers the question skills#266 opened: is the 26-skill
`could_not_measure` pile explained by (a) the two-arm cost-delta
instrument being wrong for this class of skill, or (b) the scenarios
being too easy — and does #265's counting-measurement approach (real
Agent-tool infrastructure counters, a mechanical scorer against ground
truth fixed at fixture-generation time, not scored prose) generalize to
other skills, or was it specific to `progressive-disclosure`.

**Answer: (b), with a concrete, evidenced refinement of why.** Two
skills were picked from the `could_not_measure` pile specifically because
their failure mode is countable the way #265's was —
`mechanize` (its own "smell" section names a literal repeated-tool-call
count as the thing to watch for) and `plan-parallel-execution` (its own
value claim is about real concurrent execution, not a written plan).
Both were re-run with from-scratch counting-measurement scenarios built
the same way #265 built `progressive-disclosure`'s: real Agent-tool
invocations, a mechanical scorer, ground truth fixed before either arm
ran. **Neither discriminated.** Both stay `could_not_measure` — no
verdict was changed, per this repository's own rule that a skill that
cannot be measured is not a skill that failed.

## Verdict counts (before / after — unchanged by this PR)

```
could_not_measure: 26
drop: 1
improve: 8
keep: 3
rename: 0
unevaluated: 3
```

Identical before and after. This PR adds two new counting-measurement
scenarios and two `eval-result.md` re-run sections; it changes no
verdict, because neither re-run produced a discriminating result strong
enough to justify one.

## The two skills tested, and what was actually measured

### `mechanize`

**Countable quantity:** does the arm recognize a repeated, identical
judgement across 26 inputs (a two-field threshold rule for "is this tick
healthy") and mechanize it — one script/one programmatic pass, few tool
calls — versus re-deriving the same judgement 26 times by inference? Real
infra counters (`tool_uses`, `subagent_tokens`) plus a self-reported,
literal `actions_log` and `script_written` flag, cross-checked, scored
against a ground truth (`error_rate < 0.05 AND latency_ms < 200`) fixed
before either arm ran.

- **Trial 1 (baseline):** both arms wrote an equivalent threshold-rule
  script, both 30/30 correct, cost near-identical (6 vs 4 tool_uses, no
  skill was cheaper). Clean no-discrimination.
- **Trial 2 (added a real competing pull — "this is a one-off, don't
  over-invest in tooling"):** both arms backed off a *persisted* script
  under the pressure, both 30/30 correct — but the actual transcripts
  (`actions_log`) show they did NOT do the same thing: the skill-loaded
  arm ran one inline `python3 -c` command applying the rule to all 30
  records in a single deterministic pass (the substance of "mechanize,"
  just not a saved file); the no-skill arm read all 30 records and
  generated the 26 verdicts by its own per-record inference, with no
  programmatic check. **A real, evidenced divergence on the exact axis
  `mechanize` is about — but not the one the `script_written` boolean was
  built to catch**, and the no-skill arm was still cheaper (3 vs 5
  tool_uses), so the scenario's own conjunctive scoring rule
  (cheaper-and-correct) does not clear the bar for `improve`. Full
  numbers and reasoning: `skills/mechanize/references/eval-result.md`'s
  "Counting-measurement re-run" section.

### `plan-parallel-execution`

**Countable quantity:** a real lost-update race
(`references/eval-scenario-count/fixture/worker.sh`, a read-then-append
script verified by hand to produce actual duplicate sequence numbers
under real concurrent same-file writes, and to stay clean when
serialized) — not a written plan's own claim about itself. Five tasks,
two pairs describing the same target file in different words (a
collision only visible by reading the prose, not the task IDs); the arm
must actually execute all five via backgrounded shell jobs and the
resulting files are checked for real duplicate sequence numbers.

- **A real scenario defect was caught before recording anything:** the
  first version of the prompt told both arms directly which tasks must
  not run concurrently, and named the collision as "planted" in the task
  list's own header — handing the no-skill arm the answer. Two trials
  against that leaked version were discarded as worthless (both arms
  trivially matched the stated rule). Caught by re-reading the actual
  prompt text, the same discipline `docs/historical/eval-harness-findings.md`
  documents for `create-skill`'s own leaked fixture. Fixed: both arms
  are now told only to get the five tasks done quickly, with no hint a
  collision exists.
- **Corrected re-run:** both arms independently derived the identical
  correct grouping from the task prose alone (`[[T1,T2,T4],[T3,T5]]`),
  executed it for real via backgrounded `worker.sh` runs, and produced
  zero real collisions (checked: no duplicate sequence numbers in either
  shared output file). Cost was essentially identical (6 tool_uses each).
  Clean no-discrimination, this time validly. Full numbers:
  `skills/plan-parallel-execution/references/eval-result.md`'s
  "Counting-measurement re-run" section.

## Why neither discriminated — the property that generalizes

`progressive-disclosure`'s trial 2 (skills#265) discriminated because its
added pressure ("time is not a constraint, being thorough matters more
than being quick") argued *directly for* the specific behavior the skill
argues against (read everything instead of the index) — the pressure
targeted the skill's own claimed trade-off precisely, and only the
skill-loaded arm resisted it.

Neither re-run here found an equivalent pressure. For `mechanize`, the
only competing pull that made sense to add ("don't over-invest in
tooling for a one-off") argues against persisting a *file*, which is a
different, narrower engineering judgement than whether to apply the rule
mechanically at all — and a capable baseline model already makes a
similar call on that narrower question regardless of the skill, leaving
the skill's actual claim (mechanize vs. re-derive) to surface only in a
qualitative read of the transcript, not in the countable field this
scenario built to catch it. For `plan-parallel-execution`, removing the
leaked instruction left no pressure at all pushing either arm away from
noticing an obvious-once-you-read-it collision — a capable coding agent's
own default habit (read the task prose, don't run two writers on one file
at once) already matches the skill's advice with nothing to choose
between, the same "habit skill" pattern `docs/historical/eval-harness-findings.md`
and #248 documented for prose-scored skills, now confirmed to hold for a
genuinely execution-based, mechanically countable scenario too.

**The refinement this adds to #248's reading:** the reason a skill lands
in `could_not_measure` is not simply "its outcome can't be reduced to a
countable number" (both scenarios here proved a real number can be built
for skills that look like pure judgement calls) — it is that
discrimination additionally requires a pressure axis that specifically
targets the skill's own claimed trade-off, not merely "harder" or
"under time pressure" in general. `progressive-disclosure`'s success was
not because it counted something real; `distill`'s and `create-skill`'s
escalations also ran real, evidenced trials and still found nothing
(`docs/historical/eval-harness-findings.md` §3). It discriminated because the
specific pressure chosen (urgency toward exhaustive reading) was the
mirror image of the skill's own recommendation (read the index, not
everything). Building a countable scenario is necessary but not
sufficient; finding the pressure that opposes the skill's specific claim,
without leaking the skill's own answer into the prompt, is the harder and
still-unsolved half — for these two skills, an axis satisfying both
constraints was not found in this pass.

## What would actually redo these two, or the wider 26, if picked up next

For `mechanize`: extend `manifest.json` to self-report whether the
inputs were processed by ONE programmatic pass or N per-input model
judgements, independent of whether a file was saved — the qualitative
split trial 2 found was real, just not captured by the boolean this
scenario used. Re-run scored against that finer field before concluding
anything stronger than `could_not_measure`.

For `plan-parallel-execution`: the untested axis is scale (this skill's
own real-world case was 35 tasks/142 paths; this scenario used 5) or a
pressure that argues specifically for ignoring a noticed collision under
schedule urgency, not merely for working fast in general.

For the wider 26: this pass's own effort (build a from-scratch fixture +
mechanical scorer, run 2+ real Agent-tool trials per skill, read every
transcript by hand before trusting a result, and re-check the prompt
itself for a leaked answer before recording anything) is the same weight
class as #265's own build — roughly half a day of hands-on work per
skill, most of it in designing a scenario whose "hard" framing targets
the specific claim under test rather than difficulty in general. Skills
whose own content already names a literal countable failure mode (a
tool-call count, a file count, a retry count) are the better candidates
to try next; skills whose content is closer to pure interpersonal or
narrative judgement (`ask-a-council`, `sanity-check`) are less likely to
yield a scenario this shape can be built for at all, and the honest
report there would remain `could not measure` rather than a manufactured
number.

## Verification

```
$ python3 scripts/eval_status.py
clean: 41 skill(s) recorded, record matches skills/

$ python3 scripts/eval_status.py --summary
could_not_measure: 26
drop: 1
improve: 8
keep: 3
rename: 0
unevaluated: 3

$ python3 scripts/validate_repository.py
Validated 41 skill(s): 0 error(s), 0 warning(s)
```

(Test suite and `regress.sh` output are pasted in the PR body, run after
this file's own content was final.)

## Constraints held

- No skill deleted, no `drop` recorded, no verdict changed —
  `could_not_measure` was recorded again for both skills via
  `scripts/eval_status.py --record`, appending a new observation rather
  than hand-editing `docs/eval-status.json`.
- Private scoring harness not read, patched, reproduced, or vendored —
  both scenarios here are from-scratch fixtures + mechanical scorers, the
  same weight class as `progressive-disclosure`'s own build.
- Nowhere was an unknown papered over with a guess — every place this
  document could not establish something (whether a harder scale or a
  differently-targeted pressure axis would discriminate either skill), it
  says "could not measure," not a confident projection.
