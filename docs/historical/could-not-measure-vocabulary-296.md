# `could_not_measure` vocabulary split (jonhill90/skills#296)

**Disposition: landed.** This PR relabels each of the 26 `Verdict:
could_not_measure` tokens by reading its own body, splits them into three
tokens, and updates `scripts/eval_tally.py` as the single place that counts
verdicts. No skill's keep/improve/drop judgement changed.

## Part 1 — classification

`#296`'s own regex-over-the-verdict-line count is the shortcut it warns
against. Each of the 26 `could_not_measure` bodies was read in full; the
sentence below is the one that decided its category, quoted from the file
itself (pre-relabel wording, so it reads as it did when read).

| skill | category | deciding sentence (from the file's own body) |
|---|---|---|
| ask-a-council | scenario_inadequate | "satisfying 'plural in kind' and 'not cheaply checkable by a single read' is not, by itself, sufficient to force this skill's mechanism to engage." |
| close-the-loop | no_effect_observed | "A wash once measured properly: both arms read the governing rules document, both named the missing inputs as blocking rather than guessing, neither invented a plausible-looking answer." |
| create-skill | no_effect_observed | "A with/without comparison against this skill's own placement-judgement trigger reached the same correct conclusion in both arms ... with comparable cost either way." |
| decide-by-variant | no_effect_observed | "Two samples pointing in different directions is exactly the noise this loop's own repetition bar exists to catch." (measured twice; the reproducible reading is null, not a discriminating effect) |
| determine-intent | no_effect_observed | "An identical-outcome pair with no meaningful cost delta once the deliverable was hand-checked directly — a wash on both axes." |
| determine-signals | no_effect_observed | "Both arms consistently reached the correct conclusion... A cost signal that does not survive one replication is treated as noise, not a finding." |
| devils-advocate | no_effect_observed | "Both pairs reached the same correct, specific outcome in every arm... Recorded as a wash on both axes once measured properly." |
| dispatching-subagents | no_effect_observed | "Both arms solved it the same, correct way — a real result about this model on this task." |
| distill | no_effect_observed | "A baseline with/without comparison found both arms correctly surfacing a retracted figure and its replacement, with no meaningful cost delta... none discriminated either." |
| durable-fact-before-label | no_effect_observed | "No discrimination — the skill was genuinely visible this time... and the base model already applies this ordering by default." |
| failing-test-first | no_effect_observed | "identical, correct outcomes in both arms of their own comparison: this model writes the reproduction before the fix ... whether or not the skill is installed." |
| github-cli | could_not_measure (blind) | "a clean tie of this shape cannot currently be told apart from an unconfirmed wiring problem in the arm meant to have the skill, because nothing in this measurement design independently confirms the skill's own content was actually read." |
| keep-me-honest | no_effect_observed | "both arms independently re-verified the underlying claim and held their position in the fresh, memory-cut session, with or without the skill's own guidance." |
| linear | could_not_measure (blind) | same unconfirmed-read wiring problem as github-cli, stated verbatim for this skill. |
| loop-memory | no_effect_observed | "the specific failure this skill exists to prevent didn't occur in either arm... It still didn't discriminate." |
| mechanize | scenario_inadequate | "a fresh live re-run under the corrected schema again showed no clean divergence — this fixture does not reliably produce one." |
| memory-conventions | no_effect_observed | "The base model already handles the specific concept-matching case this scenario tested." |
| notify | scenario_inadequate | "one is a scenario-design finding rather than a behavioral one" — the first of its two passes never entered the skill's trigger at all; see note below. |
| obsidian | could_not_measure (blind) | same unconfirmed-read wiring problem as github-cli/linear, stated verbatim for this skill. |
| plan-parallel-execution | no_effect_observed | "No discrimination — the skill was genuinely visible this time, and the base model already performs this skill's own manifest-first discipline by default." |
| sanity-check | no_effect_observed | "A real result about this model on this specific kind of check — a source exists and checking it is one cheap command." |
| spec | no_effect_observed | "The base model already knows the shape of a good technical spec without this skill's explicit section list, on this scenario." |
| spec-driven-development | no_effect_observed | "No discrimination — the skill was genuinely visible this time, and the base model already front-loads a falsifiable criterion and a mutation check." |
| supervised-lane-loop | no_effect_observed | "both found both arms correctly performing this skill's own core discipline ... with no observable difference from the skill's presence." |
| tdd | no_effect_observed | "found both arms independently writing the test before the implementation, unprompted in the no-skill arm's case, at comparable cost." |
| test-in-the-consumer-context | no_effect_observed | "No discrimination — the skill was genuinely visible this time, and the base model already insists on testing in the real consumer's context by default." |

Tally: **3 could_not_measure, 20 no_effect_observed, 3 scenario_inadequate**
(= 26).

### Items that didn't fit cleanly

- **`notify`** is genuinely mixed, and its own body says so: two passes
  tested "structurally different framings," and only one of them actually
  entered this skill's trigger at all — the other pass's arms never
  consulted the skill in either condition, so the with/without conditions
  "never differed on the intended axis." That first pass is a pure
  scenario-design failure (`scenario_inadequate`); the second pass is a
  clean null result under a narrower framing. One `Verdict:` line can only
  carry one token, so it is filed under `scenario_inadequate` — the
  dominant caveat its own text names — with this note as the honest
  qualifier rather than silently picking a side.
- **`github-cli` / `linear` / `obsidian`** are a blindness variant distinct
  from the install-path gap `#282`/`#291` fixed: the skill was delivered to
  the "with" arm by prompt instruction, but nothing in the measurement
  independently confirms it was actually read (`arm_a_skill_read_confirmed:
  unknown` in each file, per `#280`). A clean tie under that condition
  cannot be told apart from the skill never having been exercised at all —
  which is exactly the "harness could not see or exercise the skill"
  definition of `could_not_measure`, just via unconfirmed exposure rather
  than a missing install.

## Part 2 — the vocabulary

Three tokens, kept close to `#296`'s own candidates:

- **`could_not_measure`** — kept, narrowed to genuinely blind cases: the
  harness could not confirm the skill was ever exercised. A fixed
  instrument (install-path confirmed, or read-confirmation added) can
  still produce a real verdict on re-run.
- **`no_effect_observed`** — a clean measurement with a null result. This
  reads as a finding, not a failure: on the scenario tested, the base
  model already does what the skill asks for. It is explicit in
  `scripts/eval_tally.py`'s updated docstring that this is **not** grounds
  to drop a skill — a null result on one scenario is evidence about that
  scenario, not about the skill's value on a harder one (`#296`'s own
  constraint, and the repo's standing "never delete for low usage or a
  null result" rule).
- **`scenario_inadequate`** — the scenario itself never discriminated, and
  re-running it will not change that; a different scenario is needed, or
  an honest statement that the skill's effect is not A/B-measurable on a
  single task. Distinct from `could_not_measure`: nothing stopped the
  harness from exercising the skill, the exercise just never engaged the
  mechanism being tested.

Rejected: a fourth token for the `notify`/blind-variant edge cases. Adding
a token per irregularity would recreate the problem `#296` is fixing —
today's `could_not_measure` already means at least three things; a
five- or six-way split earns diminishing clarity for a one-off shape.
Documenting the exception in prose (this file, and the per-skill body) is
cheaper and more honest than inventing a token nothing else will ever use.

## Before / after tally

Before (`#294`'s figure, unchanged in code until this PR):

```
26 could_not_measure
11 improve
 3 keep
 1 drop           (= 41)
```

After (`python3 scripts/eval_tally.py`, measured on this branch):

```
could_not_measure: 3
drop: 1
improve: 11
keep: 3
no_effect_observed: 20
scenario_inadequate: 3
total: 41
```

## What did not change

- No `Verdict:` token outside the 26 `could_not_measure` files was
  touched — `improve` (11), `keep` (3), and `drop` (1) are untouched.
- `docs/eval-status.json` and `docs/eval-log/*.jsonl` still record
  `could_not_measure` for these 23 relabeled skills. That is deliberate,
  not an oversight: `#296` names `scripts/eval_tally.py` as "the single
  place counting," and `eval_status.py`'s own `VERDICTS` enum is a
  separate historical/consistency record (which skills have been run
  through the harness at all) that this brief does not ask to extend.
  Reconciling that enum with the new tokens, if wanted, is separate
  follow-on work.
- No eval was re-run and no skill's `keep`/`improve`/`drop` judgement
  changed — this only relabels *why* a `could_not_measure` was
  `could_not_measure`.

## Verification

```
python3 scripts/eval_tally.py            # exit 0, sums to 41
python3 scripts/validate_repository.py   # 41 skills, 0 errors
python3 -m unittest discover -s tests -v # 202 tests, OK
npx skills add . --list                  # lists all 41 skills, exit 0
```

Mutation-checked the duplicate-verdict guard `#295` added, since this PR
touches every file it guards: added a second `**Verdict: keep**` line to
`skills/close-the-loop/references/eval-result.md`, confirmed
`validate_repository.py` went red (exit 1, "2 \"Verdict:\" lines found"),
removed it, confirmed green (exit 0) and the tree restored to only the
intended single-token relabel.
