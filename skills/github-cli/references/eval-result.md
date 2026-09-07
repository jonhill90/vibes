# Eval result

**Verdict: could_not_measure (a reliable skill-attributable difference could not be established)**

Closes this skill's prior `unevaluated` status with a real pair of live
trials against a narrower claim than the original blocker — whether an
arm reaches for a documented-correct invocation shape, tested against a
fixture stub that never contacts a real account, across a baseline
framing and a one-off-pressure framing. Both trials found identical
behavior in both arms. A later correction to this file's own record
established that a clean tie of this shape cannot currently be told apart
from an unconfirmed wiring problem in the arm meant to have the skill,
because nothing in this measurement design independently confirms the
skill's own content was actually read. The verdict stands, but covers
both readings equally rather than confirming either.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at
`skills/github-cli/eval-scenario-count/` (moved there by the
landing PR jonhill90/agent-evals#22). This citation is for internal
cross-check only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of
this public repo cannot open it.

**arm_a_skill_read_confirmed: unknown** (skills#280, retroactive pass,
`scripts/skill_read_confirmed.py`). This scenario delivered the skill to
Arm A by prompt instruction, the exact class the standing requirement in
`docs/historical/eval-harness-findings.md` covers. `skills#273`'s own PR body
already recorded that retrofit here was skipped because "their real
transcripts weren't available in this environment" — re-checked now
rather than inherited: searched `~/.claude/projects/**/*.jsonl` for any
session naming or containing this skill's PR #269 trial; none exists.
The blocker has not expired — there is still no real transcript for this
tool to run against, so this is recorded as `unknown`, not forced to
`false`. This does not change the `could_not_measure` verdict above,
which already treats both readings as equally unresolved.
