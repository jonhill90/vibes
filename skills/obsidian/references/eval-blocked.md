# Why this skill is `unevaluated`, not `could_not_measure`

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop (pass 16,
following pass 15's `docs/historical/eval-pass15-remaining-four.md`). Re-verified
live against a fresh checkout rather than cited from that pass.

## What was re-checked live, today

Install-parity: `obsidian: OK -- installed copy at
/Users/jon/.claude/skills/obsidian matches skills/obsidian`. No drift.

`Obsidian.app` is installed on this machine (`/Applications/Obsidian.app`,
bundling `obsidian-cli`), and this environment carries a live,
in-use vault (`AGENT_MEMORY_VAULT`, the personal agent memory vault
described in the owner's own global instructions). That vault is not a
fixture — it is the real memory backend read at the start of every
session across every harness on this machine. This corrects the same
imprecision noted in `github-cli`'s write-up: the obstacle is not
"nothing is running," it is that the one thing running is live,
personal, and non-disposable.

## The sharper evidence pass 15 did not have

The private evals harness's own acceptance spec for this skill (not
publicly available; read for this pass, not reproduced or modified)
confirms the same shape pass 15 inferred from
`SKILL.md` alone: the five acceptance checks (create/read/search/append/
target-a-named-vault) were verified **once, by hand, against a specific
Obsidian version** ("Checks 1-4 verified hands-on 2026-07-12 on
1.12.7") — not against a scripted, repeatable, disposable vault. It also
notes explicitly that this estate's actual memory contract runs through
*direct file operations on the vault directory*, not through this
skill or CLI at all — so even a successful eval of this skill would say
nothing about the memory path every other loop actually depends on.

## Why this is not simply "point it at a scratch vault"

Two separate obstacles, not one:

1. **The CLI drives whichever vault the running `Obsidian.app` instance
   currently has open**, per the skill's own acceptance check 5 ("fail
   loudly and fast when the app is not running -- never hang or write
   to the wrong vault"). Switching the live app to a scratch vault to
   run an eval pair would mean closing the operator's actual open vault
   mid-session — an outward, disruptive action on a real running
   application this pass has no standing to take unattended.
2. Even a vault switch that could be scripted safely would need the app
   to already be running and pointed at the right vault *before* the
   eval starts, which this loop cannot arrange from inside a sandboxed
   subagent — it would require driving the operator's own desktop
   session, a different class of action than every other skill this
   loop has evaluated so far (all of which run headless).

## Relation to #248's "may be structurally unable to discriminate" finding

Not relevant here for the same reason it is not relevant to
`github-cli`/`linear`: #248 diagnosed pairs that *ran* and came back
indistinguishable; this skill has never had a pair run, for lack of a
disposable vault to run one against. `obsidian` is reference material
over a specific external tool, not a behavioral-discipline skill, so
#248's mechanism would only become a live question once a fixture makes
a pair possible.

## Conclusion

Confirmed: `obsidian` stays excluded from the skills#230 with/without
loop. Verdict stays `unevaluated` — no `--record` call was made; no live
pair ran.

**The concrete unblock**, if someone wants to pick this up: a second,
disposable Obsidian vault directory (no app UI needed — `obsidian-cli`
can be pointed at a vault path directly per its own `vault=<name>`
argument) seeded with throwaway notes, with the app already running
against it before the eval starts. That still requires a human to
launch and hold open a second vault instance; it is not something this
loop can arrange for itself.
