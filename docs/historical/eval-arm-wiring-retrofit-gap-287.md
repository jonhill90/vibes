---
type: Diagnosis
description: >-
  Why the "4 undetermined" from skills#287 don't all share one cause, and
  what the real harness gap behind the 3 that do actually is -- not another
  retrofit, a wiring change scoped larger than this lane.
generated:
  at: 2026-08-28
---

# skills#287 Part 2: the four "undetermined" are three, plus one unrelated case

**Disposition: analysis only. Not yet reacted to by Jon as of this
writing** — this document names a gap and a fix; it does not implement the
fix (see "What this lane did not do" below).

## The brief's premise, checked against the files directly

skills#287 says `github-cli`, `linear`, `notify`, and `obsidian` "all
record the same shape: a clean tie the harness cannot attribute, with
`arm_a_skill_read_confirmed: unknown`." Read all four `references/eval-result.md`
files directly rather than trusting that summary:

- `github-cli`, `linear`, `obsidian` — **yes**, all three carry
  `arm_a_skill_read_confirmed: unknown`, in near-identical wording, for the
  same reason: each delivered the skill to its with-skill arm by prompt
  instruction, and `scripts/skill_read_confirmed.py` (skills#273) could not
  confirm compliance because no real trial transcript survives to check
  (searched, per each file's own text — none found).
- `notify` — **no**. Its `eval-result.md` contains no
  `arm_a_skill_read_confirmed` field at all. Its own verdict line reads
  `could_not_measure (two independent passes, different questions)`, and
  its undetermined-ness (per skills#287's own classification comment) comes
  from something structurally different: two scenario passes that tested
  different framings and disagreed on mechanism, not an unconfirmed prompt
  read.

**So the actual count is 3, not 4** (`github-cli`, `linear`, `obsidian`),
and this matches `docs/historical/eval-instrument-diagnosis-2026-08-23.md`'s own
"sixth cause" section exactly — it names `github-cli`, `linear`, `obsidian`,
`tmux` (not `notify`) as the four "arm-wiring cannot be confirmed" records.
`tmux` has since been reclassified as `blindness` and re-run (this lane,
Part 1) rather than staying in this bucket; `notify` was never in it.
skills#287's own tally folded `notify` in under a broader "undetermined"
label that conflates two different causes. Worth correcting before anyone
uses "4" as a work estimate for the fix below — it's 3.

## What was already fixed, and what wasn't

`skills#280`/`#281` (merged, closed) already did the cheap part: ran
`skill_read_confirmed.py` against whatever evidence survived for all four
of the *original* sixth-cause records (`github-cli`, `linear`, `obsidian`,
`tmux`) and populated the field. For three of those four, the honest
answer was `unknown` — not because the tool is broken, but because **no
real transcript exists anymore to run it against**. `tmux`'s own retrofit
found the same `unknown` for both of its passes, for the same reason on
one and a genuinely-unloaded arm on the other (now resolved separately —
see this lane's Part 1 write-up in `skills/tmux/references/eval-result.md`).

That retrofit was always going to be a one-time, partial fix: it can only
confirm a read that a surviving transcript actually shows. Once a
transcript is gone, `unknown` is permanent for that trial, no matter how
many more times someone runs the same script against it.

## The real gap: confirmation is retroactive and transcript-dependent, not run-time

`scripts/skill_read_confirmed.py`'s own docstring is explicit about this:
it is "usage as a CLI, to populate `eval-result.md`'s structured field by
hand" — a tool applied *after* a trial, to whatever transcript happens to
still be on disk. Nothing in the eval harness's own recording path
(`agent-evals`' `scripts/eval_skill.py`, specifically its `verdict()` /
`score_one_skill()` flow) calls this function or requires a `True` result
before accepting a with-skill trial as valid evidence. And nothing in the
protocol (`agent-evals`' `AGENTS.md` workflow step 5, "raw transcripts...
may stay local instead") *requires* a trial's transcript to be retained.
Put together: a trial can be scored, recorded, and have its transcript
discarded, all before anyone asks whether the skill was actually read —
and once that happens, the question becomes permanently unanswerable, as
it now is for `github-cli`, `linear`, `obsidian`.

This is not the coupling `#285` names. `#285` is about a skill needing to
be live-installed (symlinked into `~/.claude/skills/`) before it can be
evaluated at all — a different gap, upstream of this one. Decoupling the
harness from live installation, on its own, would not fix this: even
pointed at an arbitrary skill source, a prompt-delivered trial still has no
run-time check that the arm actually read what it was told to, unless the
harness is *also* changed to check and gate on it. The brief names `#285`
as "the obvious place to look" for Part 2 — reading it directly shows it
answers a different question than the one this gap is actually about.

## What would actually close it (scoped larger than this lane)

Two changes to `agent-evals`' `scripts/eval_skill.py`, neither of which
this lane implements:

1. **Call `skill_read_confirmed()` at record time, not after.** After the
   with-skill arm's run completes and before `verdict()` is computed, run
   the check against that trial's own transcript. If it returns anything
   other than `True`, the trial is `INVALID` (same status `build_fixture`
   already raises for a missing fixture) — never silently scored as a
   clean tie.
2. **Make transcript retention part of the protocol, not a "may stay
   local" option.** At minimum, commit the boolean result of the check
   alongside the result matrix; ideally, retain the transcript itself
   somewhere `agent-evals` controls, so a future retrofit is never blocked
   on "does this file still exist on somebody's laptop."

Both are `agent-evals`-side changes (a private repository this lane's
brief does not name as in scope, and which this worktree — the public
`jonhill90/skills` checkout — has no PR open against). Recommending them
here, with the evidence above, per the brief's own instruction to write up
a gap larger than one lane rather than paper over it.

## What this lane did and did not do

- Did: read all four "undetermined" records directly, rather than trusting
  skills#287's own summary of them, and found the summary overstated by
  one.
- Did: confirm, by reading `docs/historical/eval-instrument-diagnosis-2026-08-23.md`
  and `scripts/skill_read_confirmed.py` directly, exactly why `github-cli`/
  `linear`/`obsidian` still read `unknown` after the retrofit, and that no
  further retrofit pass can change that outcome.
- Did not: re-run `github-cli`, `linear`, or `obsidian`. Per the brief:
  "Fixing the harness is worth more than four re-runs against a harness
  that still cannot attribute" — running a fourth (now third) unconfirmable
  trial against an unfixed harness would reproduce the exact same
  `unknown`, not new evidence.
- Did not: open a PR against `agent-evals`, or implement either change in
  "What would actually close it" above. That is real design and
  implementation work in a different, private repository, out of this
  lane's stated scope.
