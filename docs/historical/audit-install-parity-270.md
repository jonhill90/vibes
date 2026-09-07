# Audit: is every recorded eval's "with skill" arm actually installed? (skills#270)

Settles the central, mechanically-checkable question `docs/eval-harness-
findings.md` raised but did not re-verify: of the skills recorded in
`docs/eval-status.json`, which ones' recorded verdict rests on a live pair
where the skill was never actually installed on this machine's shared
skills path (`~/.claude/skills/`) at all — meaning the "with skill" arm was
silently *also* a without-the-skill run, and the recorded verdict is not a
measurement of anything.

**No eval was re-run and no verdict was changed by this audit.** The
deliverable is the list below.

## Method

`scripts/check_skill_install.py <skill>` already exists for exactly this
(built for #246, used by `eval_status.py --record`'s own pre-flight gate)
and answers with three states, never two: `OK` (content parity), `DIVERGENT`
(installed but some files differ or are missing), `MISSING` (not on the
shared skills path at all). Ran it against **all 41 authored skills**, not
a hand-picked subset, and cross-checked with `scripts/check_installed_skills.py`
(the estate's own roster-wide tool) and a plain `comm` diff — all three
methods agree exactly.

```
$ python3 scripts/check_installed_skills.py
NOT INSTALLED (7):
  dispatch-brief
  durable-fact-before-label
  plan-parallel-execution
  progressive-disclosure
  spec-driven-development
  test-in-the-consumer-context
  wire-it-when-you-write-it

authored=41 installed=35 benched=0
```

## The "5 out of 40" claim, checked rather than trusted

`durable-fact-before-label`'s, `spec-driven-development`'s,
`wire-it-when-you-write-it`'s, and `dispatch-brief`'s own `eval-result.md`
files each independently cite the same figure: *"`~/.claude/skills/`
symlinks 35 of this repo's 40 skills; this is one of the 5 that isn't."*
Four of the five are named explicitly across those four files; the fifth
is never named in any of them. Cross-referencing `docs/eval-harness-
findings.md`'s own "Fixture/installation defect" bucket (`durable-fact-
before-label`, `spec-driven-development`, `test-in-the-consumer-context`,
`wire-it-when-you-write-it`) against the four self-reporting files' own
union (those three plus `dispatch-brief`, which the harness-findings table
doesn't cover because `dispatch-brief` landed `keep`, not
`could_not_measure`) reconstructs the 5th: **`test-in-the-consumer-context`**.
So the historical claim reconstructs as: `{durable-fact-before-label,
spec-driven-development, wire-it-when-you-write-it, dispatch-brief,
test-in-the-consumer-context}` — **confirmed accurate for 2026-08-22**, the
date all four self-reporting files were recorded.

**It is stale today.** The current, mechanically-verified list is **7,
not 5**, and the denominator is 41, not 40 — `plan-parallel-execution` and
`progressive-disclosure` are the two new entries. Both are newer skills
(`plan-parallel-execution`'s `SKILL.md` landed 2026-08-20, #220;
`progressive-disclosure`'s landed 2026-08-23, #265) that were apparently
never symlinked in to begin with, not skills that regressed out of an
install. The doc's own "5 of 40" framing needs updating for currency —
not done here, since this PR's own scope is the audit, not editing that
file.

## Per-skill: does the recorded verdict rest on a genuinely-broken pair?

| Skill | Current state | Verdict on record | Rests on a broken pair? |
|---|---|---|---|
| `durable-fact-before-label` | MISSING | `could_not_measure` | **No.** Its own `eval-result.md` documents finding the gap on the FIRST live attempt (a 1-turn, 0-token "without" arm), discarding that pair entirely, symlinking the skill in, re-running both arms properly, then removing the symlink again. The recorded verdict is from the corrected re-run. |
| `spec-driven-development` | MISSING | `could_not_measure` | **No.** Same pattern, explicitly documented: "Symlinked it in for this pass's real run, then removed the symlink again afterward." |
| `wire-it-when-you-write-it` | MISSING | `could_not_measure` | **No.** Same pattern: "The first live attempt was discarded entirely once this was found... Symlinked the skill in for one real pair, then removed the symlink again afterward." |
| `dispatch-brief` | MISSING | `keep` | **No.** Same pattern, and this is the highest-stakes case on this list because `keep` is a real, standing record, not a null result: "Discovered before trusting the first run's own 'with' arm: symlinked the skill in for the duration of this pass's real runs, then removed the symlink again afterward." Both of its two independent scenario passes (seventh, eighth) used the corrected, symlinked-in run. |
| `test-in-the-consumer-context` | MISSING | `could_not_measure` | **Cannot fully confirm from the written record, but likely valid.** Its own `eval-result.md` documents a DIFFERENT, already-caught-and-fixed defect (a fixture env-var, `INTERACTIVE_SESSION`, never threaded into the harness subprocess) and never mentions an install-path check for itself. It was recorded the same "sixth pass," same session, as `durable-fact-before-label` (both files say "Tracked in docs/eval-status.json alongside this pass's other two results"), and that sibling's own write-up states the symlink state was checked and "confirmed restored... the same 35 skills" for the whole session, not just for itself — circumstantial but real corroboration. Recommend an explicit confirmation pass rather than treating this as settled by inference. |
| `plan-parallel-execution` | MISSING | `could_not_measure` | **Mixed — but the CURRENT verdict does not need a re-run.** Three independent measurements exist: a "seventh pass" and "eighth pass" (both pre-#265-style, using the private agent-evals harness's own `installed`/`no-skill:<name>` arm mechanism) plus a later counting-measurement recount (skills#266/#267, `references/eval-scenario-count/`). The two older passes' own write-ups **never mention an install-path check for this skill specifically** — unlike their siblings above, neither documents finding or fixing a gap, and the note that PR #240 had to resolve a numbering conflict between the two sections ("both originally called themselves seventh pass") confirms they were dispatched by two *different, concurrent* lanes, not the same session as `dispatch-brief`'s batch, so I cannot extend that batch's documented fix to cover these two by inference either. **However**, the counting-measurement recount is independently confirmed clean *of install-absence specifically*: `references/eval-scenario-count/prompt.md`'s own "Arm A only" instruction reads `skills/plan-parallel-execution/SKILL.md` **directly from the repo checkout**, never through `~/.claude/skills`. All three measurements agree (`could_not_measure`), so the recorded verdict is adequately supported by the one confirmed-clean-of-this-failure-mode measurement alone, even setting the two unconfirmed older passes aside. **That immunity does not extend to a separate question — see the caveat below.** |
| `progressive-disclosure` | MISSING | `improve` | **No, to install-absence specifically — see the caveat below.** Only one scenario exists for this skill (`references/eval-scenario/`, the counting-measurement kind from #265, the skill's own origin PR), and its `prompt.md`'s "Arm A only" instruction reads `skills/progressive-disclosure/SKILL.md` directly from the repo checkout, the same as `plan-parallel-execution`'s and `mechanize`'s counting-measurement scenarios. Never depends on `~/.claude/skills` at all. This is the `improve` verdict skills#268's scorer fix work was built around — confirmed unaffected by THIS audit's own failure mode; the separate prompt-delivery question below is not settled by this row. |

## The general rule this reconstructs, and why it matters for future passes

**Counting-measurement scenarios (#265/#266/#267/#268's style —
`progressive-disclosure`, `mechanize`, `plan-parallel-execution`'s
recount, and this reviewer's own #269 three: `github-cli`, `linear`,
`obsidian`) are structurally immune to this failure mode by construction**
— every one of their `prompt.md` files instructs Arm A to read
`skills/<name>/SKILL.md` from an explicit, absolute or repo-relative path
in the checkout the trial is actually running in, never through
`~/.claude/skills`. Checked directly for all six by grepping every
`eval-scenario*/prompt.md`'s "Arm A only" line. Install-path presence or
staleness cannot affect any verdict produced this way.

**The older, private-agent-evals-harness passes (`keep/improve/rename/drop`,
pre-#265) are the ones actually exposed to this risk** — the four that
document finding and fixing it did so because their harness's own
`with`/`no-skill:<name>` arm mechanism depends on the shared install path
being correct, not because of anything specific to those four skills.

**Caveat, added on cross-lane review (estate:4): "structurally immune" above
is scoped to install-absence only, and does not settle a separate question
for `progressive-disclosure` or `plan-parallel-execution`'s counting-
measurement recount.** Both deliver the skill to Arm A the same way —
a prompt instruction telling Arm A to read `skills/<name>/SKILL.md` in the
repo checkout — and that is exactly the delivery mechanism this reviewer's
own #269 write-up (`skills/github-cli/references/eval-result.md`, "Known
harness limitation") found is never logged anywhere a scorer reads: neither
scenario's fixture records whether that `Read` call actually happened and
returned real content, the same way `$STUB_LOG` never would have. Being
immune to install-absence (what this audit checks) and sitting inside the
prompt-delivery-never-confirmed blindness (what #269 found, after this
audit's own scenarios were designed) are two different, independent
properties — this audit settles the first for both skills and does not
settle, and did not previously say it left unsettled, the second. Using the
same register already used above for `test-in-the-consumer-context`: this
is not evidence either verdict is wrong, and neither is being called
"invalid and must be re-run" on the strength of this caveat alone — it is
named because claiming "structurally immune" without this scope would
overstate what was actually checked, which is the same defect this audit
exists to catch elsewhere in the record.

## Also found, related but distinct — installed-but-STALE, not missing

Running the same tool against all 41 skills surfaced a second, different
risk this audit was not asked to settle but is worth naming: **15 of the
34 currently-installed skills are `DIVERGENT`** (installed, but some files
differ from or are missing versus the current repo) — mostly harmless
(`references/eval-result.md`/`eval-scenario/*` files added to the repo
after the install snapshot was taken, since these are real directory
copies, not symlinks, and never auto-update). Four of the fifteen have a
**`SKILL.md` content mismatch specifically** — `dispatching-subagents`,
`safe-deletion`, `sanity-check`, `supervised-lane-loop` — meaning the
actual installed behavioral content differs from what's committed today.
This is a materially different risk from MISSING (the arm still received
*some* version of the skill; the question is whether it was the current
one, not whether it was absent), and none of these four skills' own
`eval-result.md` files document a repo-vs-install parity check for
themselves the way the MISSING-skill write-ups do for the install-gap.
`safe-deletion` is the one worth a human's attention specifically: its
recorded verdict is `improve`, a real behavioral change on the record, and
its `SKILL.md` is one of the four with a content mismatch. Not settled
here — flagged for whoever picks it up next, per this audit's own scope
(install *presence*, not install *currency*).

## Answer to the central question

**Zero recorded verdicts are confirmed to rest on a pair where the skill
was genuinely absent from both arms.** Every skill currently missing from
`~/.claude/skills/` either (a) explicitly documents catching the gap,
discarding the broken first attempt, and re-running correctly (`durable-
fact-before-label`, `spec-driven-development`, `wire-it-when-you-write-it`,
`dispatch-brief`), or (b) is immune **to install-absence specifically**
because its scenario reads `SKILL.md` directly from the repo checkout
regardless of install state (`progressive-disclosure`, and
`plan-parallel-execution`'s one confirmed-clean measurement of three) —
that immunity does not extend to whether the resulting `Read` call was
itself confirmed to happen, a separate, unsettled question named in the
caveat under "The general rule this reconstructs" above. **No verdict in
this list needs to be re-run on the install-absence evidence this audit
actually checked** — this audit does not, on its own, settle the
prompt-delivery question for `progressive-disclosure` or
`plan-parallel-execution` either.

Two items are downgraded from "confirmed clean" to "likely clean, not
independently confirmable from the written record" rather than either
"confirmed" or "must re-run," because asserting either would overstate
what the record actually shows:

- `test-in-the-consumer-context`'s own `could_not_measure` — recommend a
  human or a future pass explicitly re-verify (or re-run) rather than
  relying on this audit's circumstantial same-session inference.
- `plan-parallel-execution`'s two OLDER (`seventh pass`/`eighth pass`)
  sections specifically — their own numbers are unconfirmed on this axis,
  though the skill's overall recorded verdict does not depend on them
  alone given the independently-clean counting-measurement recount.

Neither of these two is being called "invalid and must be re-run" — the
evidence for a broken pair is absent, not present, for both. They are
named because the brief for this audit asked for exactly this level of
honesty about what could and could not be confirmed, not because either
is known to be wrong.

## Constraints held

- No eval re-run.
- No verdict in `docs/eval-status.json` changed.
- No skill retired, downgraded, or deleted; nothing here proposes acting
  on low usage — only an eval decides that, and this PR is not an eval.

## Verification

```
$ python3 scripts/eval_status.py
clean: 41 skill(s) recorded, record matches skills/

$ python3 scripts/eval_status.py --summary
could_not_measure: 29
drop: 1
improve: 8
keep: 3
rename: 0
unevaluated: 0
```

(Unchanged from `origin/main` — this PR adds one audit document and
touches nothing else. Note: this branch originally predated #269's merge,
carrying `origin/main`'s then-current 26/3; #269 has since merged
(`b3cb430`) and this branch merged that update in so its own citation to
`github-cli`'s `eval-result.md` resolves for anyone checking out this PR
alone, which is why the counts above now read 29/0. This audit's own
findings are unaffected either way, since #269's three skills, `github-cli`/
`linear`/`obsidian`, are separately confirmed structurally immune to this
failure mode in the "general rule" section above.)
