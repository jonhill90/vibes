# Eval result

**Verdict: improve (n=1, third pass, jonhill90/skills#287 — was
could_not_measure across the first two)**

Re-run for jonhill90/skills#287 after diagnosing why the first two passes
couldn't measure (below): this pass fixed both named causes before scoring,
not after. Skill delivery to the with-skill arm was mechanically confirmed —
a real `Read` tool-use against `skills/tmux/SKILL.md` in a legible
transcript, not inferred or self-reported — and the host was checked for
leftover tmux sessions immediately before and after each arm; none were
found either time, so Cause D's contamination did not recur.

A same-scenario attempt relying on the harness's native skill discovery was
tried first and reproduced the first pass's own original defect exactly:
the with-skill arm never actually consulted the skill at all (no `Skill`
tool-use, no `SKILL.md` read, in an otherwise legible transcript) despite
the skill being on the skills path. Discarded rather than scored, for the
same reason the first pass discarded its own unloaded arm. Delivering the
skill by explicit prompt instruction instead — the same delivery
`github-cli`/`linear`/`obsidian` use to dodge this exact failure — produced
a valid pair.

Both arms solved the task: the fixture's own self-contained test exited `0`
for both, and neither fix hardcoded any of the test's own fixture-specific
names (secondary observable, satisfied by both). The two arms diverged on
cost, not correctness: with the skill confirmed read, 12 turns and roughly
457k tokens; without it (skill stashed via an isolated-home shadow, never
touching the shared, real `~/.claude`), 10 turns and roughly 302k tokens —
about 1.5x. Same outcome at different cost is exactly the shape this
harness's own scoring rule (`eval_skill.py`'s `verdict()`) reads as
`improve`, not `keep`, at `n=1` — a signal to replicate, not a keep/drop
call by itself.

Evidence for this pass is from a fresh, local run performed for
jonhill90/skills#287; it was not committed to the private
`jonhill90/agent-evals` repo, so there is nothing further to cite here
beyond this summary.

**arm_a_skill_read_confirmed: true** (this pass's scored with-skill arm,
prompt-instruction delivery, mechanically confirmed via a real `Read` of
`skills/tmux/SKILL.md`). The discarded native-discovery attempt would have
read `false` by the same check — not recorded as a scored trial, since it
was never used for the verdict above.

## Prior passes (superseded by the above, kept for the record)

**Previous verdict: could_not_measure (two independent passes, n=1 each)**

Two independently-run passes, both dated the same day, both landed on
`could_not_measure`, for two different reasons — neither resolved by the
other. The first ran a live with/without pair against this skill's own
documented empty-lookup-target failure mode and found no leak in either
arm, but discovered mid-pass that the arm meant to have the skill
couldn't actually load its content — not a valid comparison, so the
clean result is read as the base model's own default caution, not a
skill effect. The second built a mechanical fixture, scored on exit code,
that took three iterations to get right before it reliably distinguished
a known-broken implementation from a corrected one — but after both arms
completed, a real, unanticipated side effect was found on the host
(leftover sessions matching this skill's own documented multi-agent
layout, not created by anything the fixture itself spawns), which
undermines confidence the comparison ran in a controlled environment.
Recorded honestly as `could_not_measure` rather than the clean pass the
raw scored result would otherwise suggest.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at `skills/tmux/eval-scenario/`
(moved there by the landing PR jonhill90/agent-evals#22). This citation
is for internal cross-check only — `agent-evals` is a private repository (its evidence is not publicly available),
so a reader of this public repo cannot open it.

**arm_a_skill_read_confirmed: unknown, for both passes** (skills#280,
retroactive pass, `scripts/skill_read_confirmed.py`). The two passes
resolve differently, neither to a confirmed value:

- **First pass (pass 16, "estate-loop agent4"):** no real transcript for
  this trial exists in this environment — searched
  `~/.claude/projects/**/*.jsonl`, found none. Genuinely unconfirmable,
  same as the other three skills in this retrofit.
- **Second pass (pass 14, the Cause D leftover-sessions pass):** the real
  trial transcript pair *was* found locally
  (`~/.claude/projects/-private-var-folders...-eval-skill-tmux-0fslup0f-tmux-with/`
  and its `-without` sibling) and matches this exact scenario byte for
  byte against this skill's own private-repo `eval-scenario/prompt.md`
  and fixture files (cited above). But `tmux`'s scenario (per its own
  `criteria.md`:
  "runs this scenario twice — once with `tmux` on the skills path, once
  ... stashed") delivers the skill via the harness's native Skill-tool
  discovery, not the prompt-instruction pattern
  (`skill_read_confirmed.py`'s own docstring, and the standing
  requirement in `docs/historical/eval-harness-findings.md`) that this field and
  tool exist to check. Running the tool against the real transcript
  (`python3 scripts/skill_read_confirmed.py <transcript> skills/tmux/SKILL.md`)
  returns `false` — legible transcript, no `Read` tool_use targeting
  `SKILL.md` — but the same transcript's own `Skill` tool_use block and
  the injected `Base directory for this skill: .../skills/tmux` content
  show the skill genuinely was delivered, by the other channel. Recording
  the tool's literal `false` here would misstate a confirmed-successful
  delivery as an unconfirmed read; recording `unknown` reflects that this
  scenario falls outside what the tool is built to measure, not that
  delivery failed. This pass's own already-documented finding (Cause D:
  the leftover `eval-with`/`eval-without` tmux sessions) is the real,
  separate defect this trial surfaced, and stands unchanged.
