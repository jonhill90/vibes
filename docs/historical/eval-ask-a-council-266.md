# jonhill90/skills#266 -- ask-a-council-only re-attempt, run once

**Disposition: landed.** Recorded verdict `could_not_measure`
(`docs/eval-status.json`, 2026-08-25) -- not a rescue, a different named
reason than the two prior passes. Do not read this as evidence the skill
should be dropped or rewritten; #266 and its own dispatching brief are
explicit that deletion/deprecation is out of scope on this evidence
either way.

## What #266 asked for

Not all 26 `could_not_measure` skills -- one, `ask-a-council`, with a
scenario built to actually satisfy its own documented trigger: failure
modes plural in *kind* (not merely plural in count), not settleable by a
cheap deterministic check or a single careful read, and a right answer
checkable after the fact without a judgement call.

## Prediction

Full text lives in the private `agent-evals` repo's own prediction file
for this scenario; summarized here since the prediction's *reasoning*,
not its content, is what matters for a public reader.

**Provenance caveat:** the prediction's *content* is consistent with
having been authored before either arm ran and matches the reasoning
below, but its ordering relative to the runs cannot be confirmed from
the repository. `agent-evals` PR #25 is a single squashed commit
(`57fa0cad`) containing `prediction.md`, the fixtures, all three
transcripts, and the results file together, timestamped
2026-08-25T04:53:15Z -- after all three transcripts' own internal
timestamps (04:47:47-04:50:43Z). No transcript reads or references
`prediction.md`, so nothing in the runs themselves proves the file
existed beforehand. That is consistent with an ordinary workflow
(authored earlier, committed in one batch afterward) but is equally
consistent with post-hoc rationalization, and the repository cannot
distinguish the two. The `could_not_measure` verdict below rests in
part on a prediction whose priority relative to the runs is
unverified.

- **WITHOUT** would catch the code-mechanism bug (visible in one read)
  and likely NOT independently cross-reference a quoted citation against
  its own named source -- nothing in a default pass prompts distrust of a
  plausible-sounding paraphrase.
- **WITH** would recognize two different-kind failure surfaces on a
  load-bearing decision and, even without literally convening a multi-
  agent council (correctly, per the skill's own RULE B2 on a small
  artifact), still treat "does the cited premise hold" as its own
  question and go check the source.
- Stated in advance: if both arms independently verify the citation
  anyway, that's a real `could_not_measure` result meaning "this is
  baseline diligence a capable model already does, not something this
  skill's framing changed" -- and that outcome would NOT be grounds to
  keep redesigning the scenario.

## What happened

Both arms found both planted defects, independently, each citing the
specific contradicting evidence. A first WITHOUT attempt was
contaminated -- a project-local `.claude/skills/` directory omitting the
skill did not actually produce a clean control, because this machine's
globally-deployed skill roster stayed visible to headless `claude -p`
regardless of the project path. That was caught by reading the
contaminated run's own `system`/`init` event (it listed `ask-a-council`
in `skills`), discarded rather than scored, and re-run with
`--disable-slash-commands` on the WITHOUT arm -- confirmed clean by
reading that run's own `init` event before scoring anything.

The measured result was closer to, but not identical to, the predicted
non-discriminating branch: both arms caught the citation defect. Going a
step further than the prediction called for, the WITH arm's own reasoning
text (not tool-result noise -- a `grep`/`find` incidentally surfacing the
skill's file path does not count) was checked for any council/lens
language or a `Skill`-tool invocation. Zero. **The skill never entered
that run's reasoning at all.**

## Verdict, and why it's a different reason than v1 or v2

`could_not_measure`, same as the prior two passes, for a third and
distinct reason:

- v1: the reused fabrication-incident case was single-lens-solvable.
- v2: a genuinely two-lens artifact, but both arms found both bugs
  unassisted and WITH correctly *declined to convene* -- the skill
  working as designed, not a discriminating result.
- v3 (this pass): the artifact satisfies #266's own two written criteria
  on paper, and the skill's trigger still never fired -- not a considered
  decline, an absence of engagement. A capable model checked a citation
  against its own cited source, for both arms identically, without this
  skill's presence changing what got read or what the run's own text
  said.

That is new information, not a repeat: satisfying "plural in kind" and
"not cheaply checkable by a single read" on paper is not, by itself,
sufficient to force this skill's mechanism to engage. What remains
untested: whether a genuinely harder-to-hold-in-one-pass artifact would
force it, and whether the skill helps once explicitly invoked rather than
left to trigger on its own.

## Process note for future runs

This pass committed `prediction.md` together with the fixtures,
transcripts, and results file in one squashed commit, which is why its
priority relative to the runs cannot be confirmed above. The fix is
process, not retroactive: commit `prediction.md` on its own, before
running either arm, so the ordering is a fact in git rather than a claim
in prose.

## Where the evidence actually lives

Full prompt, criteria, fixture, prediction, and both arms' transcripts
live in the private `jonhill90/agent-evals` repo (PR #25), under this
skill's own `eval-scenario-v3-citation` scenario and its dated 2026-08-25
results file. Named in plain text per this repository's own guardrail
against linking private material from a public tree -- `agent-evals` is
not clickable from here by design.
