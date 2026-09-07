# The cost axis a counting-measurement scenario scores must be work, not tool calls (jonhill90/skills#267)

Fixes a blind spot #267 (skills#266's counting-measurement recount)
recorded but its own scoring rule could not see: `mechanize` trial 2
found a real, transcript-visible divergence on the exact axis the skill
exists to test, and the scenario's conjunctive scoring rule
("cheaper AND correct," cost read off raw `tool_uses`) missed it anyway.
This file states the general principle first, independent of that one
case, before either re-run below is used to check it.

## The principle

A counting-measurement scenario's cost axis has to count the same thing
the skill under test claims to change. Two scenarios can both be
"countable" and still need different cost signals, because the unit of
work a skill claims to reduce is not always one tool call:

- **When a fixture affords no way to batch multiple units of required
  work into a single tool call** — each unit must materialize as its own
  action (`progressive-disclosure`: each fact read is one file-open;
  `plan-parallel-execution`: each dispatched batch is one turn, and
  batching itself is the thing being measured) — raw tool-call/turn
  counts and work-item counts are the same number. Scoring cost by raw
  count is correct here; there is nothing for it to conflate.
- **When a fixture affords batching** — one tool call can mechanically
  resolve many units of work at once (`mechanize`: one script or one
  inline command applied to all N records) as an alternative to N
  separate acts of per-item judgement folded into however many tool
  calls the model happens to use to emit them — raw tool-call counts
  stop tracking the thing the skill claims to change. A model can
  perform N independent inferences while making fewer tool calls than a
  model that performs one mechanical pass plus a few file operations, if
  the N inferences are emitted inline (e.g., in the same message that
  writes the output file) rather than as N separate tool invocations.
  Counting tool calls here counts how the answer was packaged, not how
  much judgement went into producing it.

**The fix:** a scenario whose fixture affords batching must have its own
manifest self-report a work-item count — how many of the required units
of output were produced by per-item model inference versus by one
application of a mechanical rule — and that count, not raw
`tool_uses`/`actions_log` length, is the primary cost signal. Raw counts
remain valid as a secondary/tiebreak signal, and as a plausibility
cross-check against the self-reported count (the same role
`actions_log` already played against `script_written`), but they no
longer decide "cheaper" on their own.

This does not change scoring for scenarios where batching isn't
possible — see the non-regression check below — because raw counts
were never conflating anything there in the first place. The failure is
specific to fixtures where one action can stand in for many units of
work.

## Applying it: `mechanize` (re-run below)

`mechanize`'s own claim is about the number of times a judgement is
independently re-derived by inference versus produced by one mechanical
pass. Its manifest now reports `inference_judgements`: the count of the
30 required verdicts produced by the model's own per-record reasoning,
as opposed to by executing code that applied one rule to all of them at
once. `script_written=false` (backing off a persisted file under
one-off pressure) no longer reads as "no mechanization happened" if
`inference_judgements` is still low — a single inline command counts as
mechanizing even when nothing is saved to disk.

## Applying it: `plan-parallel-execution` (re-run below, unchanged)

This scenario's existing cost signal, `turns_used`, already counts
batches, not raw actions — dispatching three independent tasks in one
backgrounded turn already reads as cheap regardless of how many
individual `worker.sh` invocations that turn contains. Batching is
already the unit being measured; there is no tool-call-vs-work-item gap
for this fix to close here. No scoring change is made to this
scenario's `criteria.md` or `check_answer.py` — it is re-run only to
confirm the fix introduced for `mechanize` does not disturb a scenario
that was already scoring the right unit.

## Non-regression check: `progressive-disclosure` trial 2 (already recorded, not touched while writing this fix)

Picked because it is the one already-recorded `improve` verdict in this
repository built the same way (`skills#265`, real Agent-tool counters,
mechanical scorer) — the closest existing case to what this fix changes,
and the one most likely to be disturbed by it if the principle above were
wrong. Its own `eval-result.md` and `criteria.md` were not opened while
writing the principle or the `mechanize` fix above; the numbers below are
its already-published trial 2 table, unmodified.

| | tokens | tool_uses (raw count) | files opened (item-level count) | correct |
|---|---:|---:|---:|---|
| A (skill) | 38,742 | 4 | 2 (`index.md`, `fact-073.md`) | yes |
| B (no skill) | 39,195 | 13 | 10 (never opened `index.md`) | yes |

This fixture affords no batching: opening a fact file is one file-open
per fact, with no mechanical-pass alternative that resolves several
facts' worth of reading in a single action the way `mechanize`'s fixture
allows a script to resolve 26 records in one pass. Per the principle
above, `tool_uses` and item-level work coincide here, and
`progressive-disclosure`'s own `criteria.md` already used the finer
signal (`files_opened`) as its deciding observable, not raw `tool_uses`,
for exactly this reason — the two happen to agree in this case (2 < 10,
same as 4 < 13) but the scenario was already scored by the item-level
count, not the tool-call count, before this fix existed.

**Applying the new rule changes nothing:** cost still reads 2 vs 10
files opened, both correct, A cheaper → `improve`, unchanged. The fix
does not flip an already-correct verdict.

## What this does not prove

Fixing `mechanize`'s cost axis and re-confirming `plan-parallel-execution`
is unaffected validates the principle against exactly three data points
(both re-runs below, plus one non-regression check against an existing
recorded verdict). It does not prove the instrument now generalizes to
the other `could_not_measure` skills — most of them have not been
checked for whether their own fixtures afford batching at all, and
`mechanize` and `plan-parallel-execution` were themselves picked in
#266 because their failure mode was already unusually countable. That
remains open.
