# Longitudinal eval design (2026-08-23)

`docs/historical/eval-harness-findings.md` §4 recommended, but never built, a
longitudinal alternative to this loop's two-arm single-turn design: a
longer simulated session with the failure-inviting pressure introduced
partway through rather than stated up front, scored on WHEN the arms
diverge rather than only whether the final outcome differs. This document
is that design, made concrete, plus one real trial against the strongest
candidate skill. It answers jonhill90/skills#230's own next-step question
directly; it is not a fresh eval pass under the old design (none was run
to produce this document -- see "What this document does NOT do" below).

## Why this exists now, and why not sooner

Two of the nine `clean no-discrimination` skills already got the cheaper
escalation first: `create-skill` (a leaked-fixture fix, re-run once,
single-shot) and `distill` (three axes -- scale, adversarial pressure,
ambiguity -- each hardened independently, still single-shot, still one
session). Neither discriminated. `docs/historical/eval-harness-findings.md`'s own
reading of that result is exact and worth repeating rather than
re-deriving: two directly-tested cases is not a proof, but it is a real
chance for "wrong instrument" to have been wrong, and it survived. The
longitudinal alternative was recommended, not run, specifically because
harder-single-shot and longer-session are different axes -- `distill`'s
own escalation already tested "harder," not "longer," and its own
write-up says so explicitly. This document is the "longer" axis, owed
since #248 first named it.

## What a longitudinal scenario actually needs, concretely

Four questions, answered specifically rather than left as a shape:

### 1. Session length

Not "many turns" in the abstract -- **at least two genuinely separate
sessions, with a hard memory boundary between them, each session long
enough that a real mid-session interrupt is plausible.** Two sessions is
the minimum that can show "session 2 repeats what session 1 already paid
to learn"; one long session with no boundary tests persistence-within-a-
context, which the base model already does well (this is exactly what
`loop-memory`'s own pass-12 single-session result showed -- both arms
wrote *something* usable before stopping). The boundary, not the total
turn count, is what makes this a different instrument than "harder
single-shot." Depth beyond two sessions (three, four, a real N-session
loop) strengthens the evidence but is not required to get a first real
signal -- start at two, extend only if two doesn't fire cleanly.

### 2. Where and how pressure gets introduced

Two separate design choices, easy to conflate:

- **The memory-loss boundary itself** is not "pressure" -- it is the
  mechanism being tested, and it must be structural, not a role-play
  instruction. A second subagent invocation with a fresh context is
  memory loss. A single subagent told "pretend you don't remember" is
  not -- it still has the tokens in context and can act on them whether
  or not the roleplay is convincing. Every longitudinal scenario needs a
  REAL boundary: a new agent process, given only what the fixture's
  filesystem state shows, never the prior transcript.
- **The failure-inviting pressure** (the thing #248's own language names
  explicitly) is a separate ingredient: an opportunity to repeat a
  specific, identifiable mistake, placed AFTER the memory boundary, not
  announced before it. If session 1 is told "watch out for X" up front,
  session 1 handles X carefully by construction and there is nothing
  for the skill's own record-keeping discipline to have prevented --
  this collapses back into a single-shot design wearing two sessions'
  clothing. The pressure has to be discoverED by doing the work, in both
  sessions independently, so that whether session 2 repeats it is a real
  test of whether session 1's OWN record of it transferred.

### 3. Divergence-point scoring, concretely

"Scored on WHEN the arms diverge" cashes out, per candidate skill, into
three concrete questions, in order:

1. Did the failure-inviting event actually occur in session 1, for both
   arms? (If not, the scenario didn't fire -- this is a design-validity
   check, not a result, and has to be checked BEFORE reading anything
   into the outcome. See `criteria.md`'s "What would make this scenario
   invalid.")
2. Did session 1 externalize the specific failure in a form session 2
   could find (not just "done" or "in progress," but the symptom and
   what would catch it again)?
3. Does session 2 avoid repeating the SAME specific mistake on its FIRST
   attempt, and can the exact tool call where its behavior first differs
   from the other arm's be named and quoted?

Question 3, not the aggregate pass/fail of either session, is the
divergence point. A design that can only say "arm A did better overall"
without naming the specific moment is still closer to the old single-shot
instrument's "final outcome differs" scoring than to what #248 asked for.

### 4. What this looks like for one candidate skill: `loop-memory`

Worked out in full in `skills/loop-memory/references/eval-scenario/`
(`prompt.md`, `criteria.md`, `fixture/`): a 12-item config migration,
split 4 seeded-done / 4 session-1 / 4 session-2, with one item per
session containing an unannounced parsing gotcha (a literal `#` inside a
config value, which a naive "strip from first `#`" transform truncates).
Session 1 gets the compaction-imminent interrupt mid-batch, after the
gotcha item, matching pressure-after-not-before from §2. Session 2 is a
structurally fresh subagent given only the fixture's disk state. The
scored question: does session 2's migration of ITS gotcha item come out
right on the first attempt, and if the with-skill arm gets it right where
the without-skill arm doesn't, can the specific tool call (reading a
known-failures note before writing the file) be named.

## Candidate selection: why `loop-memory`, not one of the other six

Seven of the nine `clean no-discrimination` skills have had no escalation
at all yet: `ask-a-council`, `dispatching-subagents`, `sanity-check`,
`tdd`, `loop-memory`, `memory-conventions`, `spec`. Per #248's own
escalation discipline (pick the strongest case for the RIVAL hypothesis,
not the easiest confirmation -- the reasoning that picked `distill`
because its own write-up already named scale as its untested axis), the
right candidate for a LONGITUDINAL trial specifically is the one whose
own content and own prior result most directly predict this axis would
matter, not just any remaining skill:

- **`loop-memory`'s own pass-12 write-up already names this exact gap in
  its own words**: "this skill's marginal value... would show up on a
  *longer* loop with actual repeated failures or a real crash/restart,
  not a single-turn stop-and-summarize... a scenario built around a
  genuine multi-run crash-and-resume, or one where a known failure needs
  to be caught by a regression file rather than merely alluded to in a
  handoff note, would be a stronger test." That is this document's design,
  almost verbatim -- `docs/historical/eval-harness-findings.md` §4 separately points
  at the same skill's own pass-12 scenario as "close to the right shape."
  No other one of the seven has this direct a textual prediction from its
  own prior result about what a longitudinal version should look like.
- **`loop-memory`'s subject matter IS cross-session memory** -- its
  entire content (`references/files.md`'s five-file taxonomy, "known
  failures become a regression set," the handoff/watermark discipline) is
  a claim about what happens across a memory-loss boundary specifically,
  not a general claim about care or judgment. A skill whose content is
  literally "what to do when the next instance has no memory of this one"
  is the skill most likely to show a real gap on an instrument that
  finally tests that boundary for real -- and, symmetrically, if it does
  NOT discriminate even here, that is unusually strong evidence for
  "wrong instrument," not just "wrong scenario," because the axis being
  added is the skill's own stated reason to exist.
- Ruled out, briefly: `tdd`'s own write-up flags "scale or ambiguity,"
  not cross-session memory, as its untested axis -- a longitudinal
  design isn't the escalation ITS OWN result asked for.
  `ask-a-council`/`dispatching-subagents`/`sanity-check`/`spec` have no
  comparable self-diagnosis pointing at this axis specifically, and
  `memory-conventions` is the vault-scoped sibling this skill's own
  SKILL.md explicitly distinguishes itself from (durable user facts vs.
  one loop's run state) -- picking it instead would test near-identical
  ground with a less direct self-prediction backing the choice.

## Second trial: `keep-me-honest`, once the runner/scorer gate closed

`skills#271`'s own `devils-advocate` pass gated the runner (component 2)
and scorer (component 3) recommendations on a bounded `vally` spike; that
spike ran (`skills#275`) and closed the gate. `keep-me-honest` is picked
for a different reason than `loop-memory` was — it is NOT one of the nine
`clean no-discrimination` skills `docs/historical/eval-harness-findings.md` §2 names
(its own existing `could_not_measure` verdict comes from that file's §4
cost-signal-noise bucket instead, a wash on both axes across two prior
pairs). The pick is direct from the skill's own content: `keep-me-honest`'s
SKILL.md names its trigger as a SECOND round of pushback against a
restated claim, and no existing scenario for this skill runs longer than
one message, so that trigger has never actually been staged — the same
"generalize the design to the skill whose own content most directly
predicts this axis matters" reasoning `loop-memory`'s own selection used,
applied to a different skill for a different, skill-specific reason
rather than to another member of the same nine-skill pool.

Worked out in full in `skills/keep-me-honest/eval-scenario/` (`prompt.md`,
`criteria.md`, `RESULT.md`, `fixture/`, private repo, cited by number
only): round one (the skill's own already-documented single-session case)
happens in session 1; round two is the identical false claim, restated,
delivered to a session-2 subagent with no memory round one happened.
Scoring model per skills#275's own "take the scoring rule regardless"
instruction — a correctness read decides, cost/latency reported but
advisory only.

**Result: `could_not_measure`, clean no-discrimination, design fired
cleanly** — both arms independently re-verified the underlying claim via
the fixture's own mechanical check and held their position in session 2,
with or without the skill. Read plainly, not treated as a miss: this
skill's check ("does my CURRENT observation conflict") doesn't need
cross-session memory to fire, unlike `loop-memory`'s file-taxonomy
mechanism — a real, useful negative result about where this skill's own
value actually sits, not a defect in the instrument. One design-validity
correction made before any scored run: the original design assumed an arm
would check in before continuing past a discovered conflict; the first
attempt showed a capable agent doesn't necessarily do that unprompted, so
a checkpoint instruction was added to both arms' session-1 prompt,
identically, before either scored run — see `RESULT.md`'s own
"design-validity note," kept visible rather than folded into "as
designed."

## What this document does NOT do

- Does not evaluate any skill under the OLD two-arm single-shot design.
  Nothing here is pass 16 of that design; see agent3's own brief for why
  that would be the expensive kind of busy work.
- Does not build a general-purpose longitudinal harness (no new flag on
  `scripts/eval_skill.py`, no `score_*` function, no schema change to
  `docs/eval-status.json`). Two scenarios now, both hand-run and
  hand-scored, the same weight class as `loop-memory`'s own original
  pass-12 scenario and `distill`'s escalation, all run without harness
  changes. Generalizing this into reusable tooling is future work if a
  trial's result justifies the investment -- building the tooling before
  knowing whether the design even fires would be backwards.
- Does not commit to running this against the other six untested
  `clean no-discrimination` skills (`ask-a-council`, `dispatching-
  subagents`, `sanity-check`, `tdd`, `memory-conventions`, `spec` --
  unchanged by this trial; `loop-memory` is the only one of that
  nine-skill pool tried so far). `keep-me-honest` was a deliberate
  off-pool pick for a skill-specific reason (see above), not a second
  draw from the same six. Two data points total, held to the same
  "could not settle it for the other N" honesty
  `docs/historical/eval-harness-findings.md` already applies to the single-shot
  escalations.
