# Eval result

**Verdict: scenario_inadequate (still) -- third pass, third reason**

jonhill90/skills#266 asked for one new scenario, designed specifically to
satisfy this skill's own documented trigger (failure modes plural in
*kind*, not cheaply checkable by a single careful read, checkable ground
truth) rather than re-running the prior scenario. It was: a readiness
memo recommending a script for production, citing a chat log as evidence
that a known concurrency risk had been retired; the log actually says the
opposite for this script's own job class, and the script separately has a
real, findable retry-logic bug. Predicted, then run once as a real
with/without pair (`claude -p`, project-local skill vs.
`--disable-slash-commands`), with a first contaminated control attempt
caught and discarded before scoring (this machine's globally-deployed
skill roster leaked into what was meant to be a clean "without" arm; see
the evidence file for how that was caught and re-run).

**Provenance caveat:** the prediction's ordering relative to the runs is
not independently verifiable from the repository -- `agent-evals` PR #25
bundled `prediction.md`, fixtures, transcripts, and results into one
squashed commit that postdates all three transcripts' internal
timestamps. See `docs/historical/eval-ask-a-council-266.md` for the full accounting.
The verdict below does not depend on prediction timing (it rests on the
WITHOUT-arm contamination catch and the both-arms-caught-the-citation
finding, both independently verified against the transcripts), but the
prediction's own priority claim is unverified.

Both arms found both planted defects, independently, each quoting the
specific contradicting log lines. Checking the WITH arm's own reasoning
text (not tool-result noise) for council/lens language, or a Skill-tool
call: zero. **The skill was present but never entered the run's
reasoning at all** -- not v2's "correctly declined to convene after
considering it," but "never reached for." A capable model asked "is this
ready to ship," with the contradicting source sitting next to the claim
that cites it, checked it unprompted, identically with or without this
skill on the path.

Evidence for this pass lives outside this repository, in the private
`jonhill90/agent-evals` repo (PR #25): the `eval-scenario-v3-citation`
directory under this skill's own scenario tree there (prompt, criteria,
fixture, prediction, both arms' transcripts) and its dated results file
(prediction, method, contaminated-control account, verdict reasoning).
This citation is for internal cross-check only -- `agent-evals` is a
private repository (its evidence is not publicly available), so a reader
of this public repo cannot open it.

Prior passes, kept for the reasoning trail rather than overwritten:

- **v1** (2026-08-22): reused the fabrication-incident case from this
  skill's own SKILL.md verbatim. Single-lens-solvable by both arms.
- **v2** (2026-08-22): a genuinely two-lens artifact (`monitor.py`, a
  mechanism bug plus a legibility bug). Both arms found both unassisted;
  WITH correctly declined to convene, per the skill's own RULE B2 --
  correct application, not a discriminating result.
- **v3** (2026-08-25, this pass): satisfied both of #266's written
  criteria on paper and still didn't discriminate, for a reason neither
  prior pass named -- the skill's trigger was never staged at all on an
  artifact a capable model could hold in one pass.

What v3 adds: satisfying "plural in kind" and "not cheaply checkable by a
single read" is not, by itself, sufficient to force this skill's
mechanism to engage. Untested: whether a genuinely harder-to-hold-in-one-
pass artifact would; whether the skill helps once explicitly invoked
rather than left to trigger on its own.
