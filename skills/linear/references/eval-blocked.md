# Why this skill is `unevaluated`, not `could_not_measure`

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop (pass 16,
following pass 15's `docs/historical/eval-pass15-remaining-four.md`). Re-verified
live against a fresh checkout rather than cited from that pass.

## What was re-checked live, today

Install-parity: `linear: OK -- installed copy at
/Users/jon/.claude/skills/linear matches skills/linear`. No drift.

The `linear` CLI (`schpet/linear-cli`, v1.9.1) is installed and on
`PATH`. That is not, by itself, evidence a fixture is possible — the
question is whether there is a Linear *workspace* this loop is
sanctioned to write test issues into.

## The sharper evidence pass 15 did not have

The private evals harness's own acceptance spec for this skill (not
publicly available; read for this pass, not reproduced or modified)
states directly:

> **Not exercisable in this repository.** [This estate] tracks work in
> GitHub Issues... run these checks against a repo that actually uses
> Linear.

That is the harness maintainer's own prior conclusion, reached
independently of the skills#230 loop, for the same reason skills#230
would hit: there is no Linear-tracked project in this estate to run a
live check against. `linear`'s five acceptance tasks (list open issues,
create-then-verify an issue, start work and create a branch, update
status and comment, generate a linked PR) all require a real team inside
a real workspace with real issue-identifier routing — "no cross-team
leakage" is explicitly part of the pass criterion, which presupposes
more than one real team to leak across.

## Why this is not simply "make a test workspace"

Unlike `github-cli` (where the blocker is *authorization to script
disposable writes* against an account that already has API access),
`linear` has no workspace at all backing it in this environment —
creating one would mean provisioning a new paid or trial Linear
workspace and a token for it, purely to feed an eval loop, which is a
standing infrastructure decision well outside this pass's scope and not
one with an obvious "safe, disposable, and cheap" shape the way a
throwaway GitHub repo has.

## Relation to #248's "may be structurally unable to discriminate" finding

Not relevant here in the way it is for the habit/consistency skills #248
was written about. That finding was about pairs that *ran* and came
back clean regardless of arm; this skill has never had a pair run at
all, for lack of a workspace to run one against. `linear` is the same
kind of reference-material skill as `github-cli` (CLI syntax over a
specific external tool), not a behavioral-discipline skill, so #248's
mechanism does not apply even hypothetically.

## Conclusion

Confirmed: `linear` stays excluded from the skills#230 with/without
loop. Verdict stays `unevaluated` — no `--record` call was made; this
pass ran no live pair, so `could_not_measure` would misstate what
happened.

**The concrete unblock**, if someone wants to pick this up: provision a
disposable Linear workspace (or a scoped test team inside an existing
one) with its own API token, dedicated to this eval loop only. That is
an explicit infrastructure decision for a human to make, not something
this pass can create unattended.
