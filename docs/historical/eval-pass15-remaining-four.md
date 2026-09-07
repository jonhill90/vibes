# Eval loop pass 15: the remaining four are excluded, not unattempted

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop. This pass
picked zero new skills to run. That is the finding, not a skipped step
-- here is the evidence for why, re-derived independently today rather
than taken on citation from the prior pass that first flagged it.

## The number that motivated this pass

`scripts/eval_status.py --unevaluated`, run fresh on `origin/main`
(`2ebf4d2`, PR #249 merged): exactly four skills remain --
`github-cli`, `linear`, `obsidian`, `tmux`. `--summary` on the same
checkout: `keep 3 · improve 6 · could_not_measure 27 · unevaluated 4`
(40 total). Thirty-six of forty skills carry a recorded verdict. Pass
13's own write-up (`skills/prd/references/eval-result.md`) already
named these same four as the full remaining set and noted they were
"poorly suited to this methodology" without recording why in the
machine record or in `docs/historical/eval-harness-findings.md` -- a grep for
`poorly suited`, `pure command-reference`, and `live-external-tool`
across `docs/` returns nothing before this file. That finding lived
only in loop-memory carried between passes, unwritten. This pass
verifies it against live evidence instead of re-citing it, and writes
it down so the next pass doesn't have to re-derive it a third time.

## Two distinct obstacles, not one

### `github-cli`, `linear`, `obsidian`: no install drift, a live-fixture gap instead

```
$ python3 -c "
import sys; from pathlib import Path
sys.path.insert(0, 'scripts')
import check_skill_install
d = check_skill_install.default_claude_skills_dir()
for s in ['github-cli','linear','obsidian','tmux']:
    print(s, check_skill_install.check_installed(s, d, Path('.')))
"
github-cli InstallCheck(skill='github-cli', status='ok', message='github-cli: OK -- installed copy at /Users/jon/.claude/skills/github-cli matches skills/github-cli', only_in_installed=[], only_in_repo=[], differing=[])
linear InstallCheck(skill='linear', status='ok', message='linear: OK -- installed copy at /Users/jon/.claude/skills/linear matches skills/linear', only_in_installed=[], only_in_repo=[], differing=[])
obsidian InstallCheck(skill='obsidian', status='ok', message='obsidian: OK -- installed copy at /Users/jon/.claude/skills/obsidian matches skills/obsidian', only_in_installed=[], only_in_repo=[], differing=[])
```

All three pass the harness's own install-parity gate (#246) cleanly --
so the block is not stale content. It's what these three skills *are*:
each is CLI reference documentation for a specific external tool
(`gh`, `schpet/linear-cli`, the bundled Obsidian CLI) whose correct
operation is scored against real external state -- a GitHub repo/issue
thread with appropriately scoped write access, a real Linear workspace
plus API token, a running `Obsidian.app` with an actual vault
(`obsidian`'s own SKILL.md: "requires it to be already running...
does not auto-launch"). A with/without scenario that doesn't actually
call the live tool only tests whether the model already knows correct
CLI flag syntax from training data -- which is not the judgement call
these skills exist to improve; their content is reference material,
not a discipline. This harness has no sanctioned way to provision that
live state repeatably and safely inside a scripted eval run. That is a
scenario-design gap, not a per-skill defect, and it does not resolve by
picking a harder scenario the way the nine `could_not_measure` skills
in `docs/historical/eval-harness-findings.md` §3 might.

### `tmux`: mechanically blocked right now, independent of scenario design

```
tmux InstallCheck(skill='tmux', status='divergent', message='tmux: DIVERGENT -- 2 file(s) with different content (installed=/Users/jon/.claude/skills/tmux, repo=skills/tmux)', only_in_installed=[], only_in_repo=[], differing=['SKILL.md', 'references/supervisor-lanes.md'])
```

(same invocation as above, `tmux` row.)

`--record`'s own install-parity check (#246) refuses to record an
observation while the installed copy and the repo checkout disagree --
confirmed live today, not inferred. This is a different, and
separately fixable, obstacle from the other three: it is not a
methodology question, it is stale local install state. Resyncing
`~/.claude/skills/tmux` from this repo (or reconciling whichever side
is correct) is a real, scoped fix -- not attempted here, because it
means overwriting a user-global file outside this repo's worktree, and
this pass's brief was to evaluate skills, not to make unreviewed
changes to `~/.claude/skills` on the operator's behalf.

## Conclusion: the active-candidate queue is empty

Continuing this loop's current methodology -- `--unevaluated`, pick 3
not already claimed, run live with/without pairs -- has nothing left
to pick. 36 of 40 skills have a recorded verdict; the remaining 4 are
excluded for the reasons above, independently reconfirmed today, not
merely unattempted. Two concrete unblocks exist, both out of scope for
this pass:

1. **`tmux`**: resync the installed copy against the repo (or vice
   versa), which is a one-line mechanical fix once someone decides
   which side is correct. Once install-parity holds, `tmux` re-enters
   the normal candidate pool.
2. **`github-cli` / `linear` / `obsidian`**: either design a
   live-fixture-safe scenario (a sandboxed GitHub repo the harness may
   write to, a disposable Linear workspace, a throwaway Obsidian vault
   with the app pre-launched) or accept these three are out of this
   harness's reach and record that as a stated methodology limitation
   in `docs/historical/eval-harness-findings.md`, not as a per-skill verdict.

## What I did NOT do

- Did not run a live with/without pair for any of the four -- none
  currently passes this harness's own gate for one (three lack a safe
  live fixture, one fails install-parity).
- Did not call `scripts/eval_status.py --record` for any of the four.
  `could_not_measure` means "ran a pair and got no discriminating
  signal" -- that did not happen here, and recording it as if it had
  would misstate what this pass actually found.
- Did not modify `~/.claude/skills/tmux` to force install-parity. That
  is a global, outside-this-repo change and needs an explicit decision
  about which copy is authoritative, not a side effect of an eval pass.
- Did not propose `drop` for any skill. Nothing here is evidence a
  skill does nothing -- it is evidence the harness cannot currently
  reach it.
- Did not open or comment on jonhill90/skills#230 beyond what this PR
  itself represents; a maintainer comment recommending the loop's next
  concrete step (the two unblocks above) is left to the PR description.
