# Why this skill is `unevaluated`, not `could_not_measure`

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop (pass 16,
following pass 15's `docs/historical/eval-pass15-remaining-four.md`). This file
re-verifies that pass's finding live against a fresh checkout rather
than citing it, and narrows it to `github-cli` specifically now that
`tmux` (the other member of pass 15's "remaining four") has since been
resynced and evaluated (`could_not_measure`, PR #253).

## What was re-checked live, today

Install-parity (the harness's own pre-flight gate, #246):

```
github-cli InstallCheck(skill='github-cli', status='ok', message='github-cli: OK
-- installed copy at /Users/jon/.claude/skills/github-cli matches skills/github-cli',
only_in_installed=[], only_in_repo=[], differing=[])
```

No install drift. The block is not stale content, same conclusion pass
15 reached.

`gh auth status` on this machine: authenticated to `github.com` as
`jonhill90`, token scopes `gist, read:org, repo, workflow` — this
corrects one imprecision in pass 15's account, which described the
obstacle as a "live-external-tool-state gap" in a way that could be
misread as "no credentials available." Credentials exist and are live.
**The obstacle is not missing authentication — it is that this skill's
own acceptance criteria (the private evals harness's own acceptance
spec for this skill, not publicly available; read for this pass, not
reproduced or modified) test against *real* PRs, issues, workflow runs,
and review comments in a *real* repository** ("Open a PR from the
current branch," "Create an issue... then close it," "Add an inline
review comment to a PR diff"). Nothing in that acceptance spec, or
anywhere else checked for this pass, defines a disposable, throwaway
GitHub repo the skills#230 with/without loop is sanctioned to create,
populate, and delete on every run.

## Why a fixture is not simply "spin up a scratch repo"

A scripted eval pair would need to, unattended, on every pass: create a
real repository under the `jonhill90` account, open/close real issues
and PRs against it, and tear it down afterward. That is technically
buildable — the authenticated token has `repo` scope — but it is a
standing decision about writing to a real GitHub account
programmatically and unattended, not a scenario-design choice this pass
is positioned to make on its own. It also does not fit this skill's
actual acceptance surface cleanly: several of the five acceptance
checks (workflow runs, review comments on a PR diff) presuppose a repo
with real history and CI wiring, which a repo created fresh for one eval
run would not have — a fixture built just to pass could end up testing
the fixture-builder's scaffolding rather than the skill.

## Relation to #248's "may be structurally unable to discriminate" finding

#248 found the loop's with/without design structurally weak for
*habit/consistency* skills (the model already does the disciplined
thing regardless of whether the skill is loaded). That finding does not
bear on this skill the same way: `github-cli` is CLI-syntax reference
material, not a behavioral discipline — pass 15 already drew this
distinction ("their content is reference material, not a discipline")
and this pass's evidence does not change it. The obstacle here is a
different kind entirely: the loop cannot even *run* a pair, discriminating
or not, without a sanctioned fixture. #248's finding would become
relevant only after that fixture exists and a pair actually runs.

## Conclusion

Confirmed, not refuted: `github-cli` stays genuinely excluded from the
skills#230 with/without loop, for a more specific reason than pass 15
had evidence for (a scenario-authorization gap, not a missing-credential
one). Verdict stays `unevaluated` — no `--record` call was made for this
skill; `could_not_measure` would misstate that a pair ran and returned
no signal, which did not happen here.

**The concrete unblock**, if someone wants to pick this up: an explicit,
reviewed decision to let the loop create/destroy a specifically-named
scratch repo (e.g. `jonhill90/skills-eval-scratch`) for this purpose
only, with the create/populate/delete sequence itself scripted and
reviewed once, not improvised per pass. Until that decision is made,
re-attempting this skill without a fixture will reproduce the same
block.
