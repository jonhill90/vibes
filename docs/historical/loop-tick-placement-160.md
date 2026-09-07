# Should `loop-tick.md` move from `agent-dotfiles` into this repo? (#160)

**Disposition, verified 2026-08-16T02:15Z: decision landed, but not the one
this document's own recommendation names below.** #160 closed 2026-08-12 with
no comment recorded (`gh issue view 160 --json state,closedAt,comments`);
its "do not move as written" recommendation is the last word this document
argued for. Jon then gave a superseding instruction in #168 (2026-08-13):
*"loop-tick.md moves to jonhill90/skills."* What actually shipped, in #169
(merged 2026-08-13, "fold loop-tick.md's portable principles into the
existing skill"), is not a verbatim move — it folded the *portable
principles* into `supervised-lane-loop/SKILL.md`, the same shape this
document's own "Recommendation" section below proposed as the productive
path. There is no `loop-tick.md` file in this repository today (`find . -iname
'*loop-tick*'` finds only this document). So: the outcome matches this
document's reasoning, arrived at through a different, Jon-directed route
rather than this document's own recommendation being accepted on its face —
read the rest of this document as the argument that was available at the
time, not as unexamined settled practice.

Investigation only, per #160's own instruction — no files move here. Same
discipline agent-dotfiles#143 and #161 used: measure, answer the three named
questions, recommend, and let Jon decide before anything moves.

Read directly: `agent-dotfiles/scripts/supervisor/loop-tick.md`, measured
2026-08-12 at **550 lines** (`wc -l`) — up from the 527 the issue cites when
it was filed, itself a small data point about how often this file changes.
(It read 540 earlier the same night, before `agent-dotfiles#183` merged and
added 10 lines; re-measured against current `origin/main` rather than left
stale.)

## 1. Is it one skill, or a skill plus references?

This repository's own stated cap, from `create-skill/SKILL.md`: "Keep the
main file under 500 lines." `loop-tick.md` at 550 already exceeds that
before any reference material is even split out. The largest skills already
here split main file plus `references/` — `github-cli` (411 lines main),
`tmux` (381), `linear` (355), `close-the-loop` (223), `obsidian` (243),
`supervised-lane-loop` (316, `wc -l` against `origin/main` at `7dce75a`,
this document's own #165 landing that added the state table §2 discusses) —
so size alone says split, not "leave as one file."

But splitting by length is the wrong cut for this file. `references/` in
this repo's existing skills holds *background* material — provider tables,
advanced flag references, less-common procedures a reader skips on a normal
pass. `loop-tick.md` is not that shape: pull any section out — the
lane-health check, the claim/dispatch sequence, the revert-diff reasoning,
the completion-rename waiter — and every one of them is load-bearing
procedure, not background. There is no low-traffic 340 lines to defer behind
a "loaded on demand" reference; nearly the whole file is the thing an agent
needs on every tick. Progressive disclosure does not resolve this file's
size problem, because its size problem is not "too much detail," it is
"too much of it is specific to one estate's toolchain" — which is question 2.

One relevant precedent already in this repo: `tmux/references/
supervisor-lanes.md` covers agent-supervising-agent tmux patterns —
upward prompt flow, a generic watcher loop, `/loop` mechanics. Read in full:
it is deliberately generic (`workflow:agents.{bottom}`, a
`supervisor-watch.sh` that does not exist in `agent-dotfiles`), not this
estate's actual `lanes.sh`/`dispatch.sh`/`claim.sh` machinery or its exact
state names. No overlap, no duplication — it answers "how do I supervise a
pane at all," not "how does this estate's supervisor loop run." Worth
knowing before assuming a `loop-tick.md` move would consolidate with
something already here; it would not.

## 2. Name or contract — the crux, measured

Counted directly against the file, not estimated:

| what | count |
|---|---|
| references to this estate's own `*.sh` scripts by name (`dispatch.sh`, `lanes.sh`, `claim.sh`, `worktree.sh`, `lane-done.sh`, `director-inbox.sh`, `advance-live.sh`, `would-revert.sh`) | **38**, across all 8 |
| issue numbers cited | **38** mentions, **26** unique |
| code fences with literal commands, exact paths, exact flags | **13** |

That is not a file that describes a contract in the abstract and cites tools
as an example. `dispatch.sh 81 dispatch-worktree ~/.local/state/agent-
dotfiles-supervisor/ad81-brief.md jonhill90/agent-dotfiles ~/source/repos/
Personal/agent-dotfiles` is not a pattern, it is this machine's actual path
and this repo's actual name, typed as the thing to run. Counted directly
against `lanes.sh`'s own `state=` assignments, not estimated: it emits
**eleven** states, not eight — `free`, `busy`, `hung`, `dead`, `service`,
`unknown`, `text-blocked`, `menu-blocked`, `unsent`, `scrolled`,
`supervisor`. There is no bare `blocked` state to cite; #159/#161 split it
into `text-blocked` and `menu-blocked` specifically because routing a reply
into a menu-blocked lane as free text was the defect that changed a lane's
`/theme` setting instead of being read as an answer, proven live
(agent-dotfiles#159/#161) — the two halves answer different questions (is it
safe to type into this lane at all) and collapsing them back into one name
would erase exactly the distinction that incident forced. These eleven are
`lanes.sh`'s own literal vocabulary, not a
described interface a differently-named tool could also satisfy. The incident
citations (#73, #81, #89, #99, #102, #108, and 20 more, including #174,
added by `agent-dotfiles#183` since this document's earlier measurement) are `agent-
dotfiles`' own history, load-bearing as the *reason* for each rule, and
meaningless without that repository's issue tracker.

Compare this repo's own `loop-contract/SKILL.md`, which already faces the
identical tension — its evidence also comes entirely from `agent-dotfiles`
(the twelve-field contract, the cron-as-stall-detector rule, the measured
defect behind it) — and resolves it differently: the skill body stays
abstract ("cron is a stall detector, never the driver, wherever a
supervisor/worker pattern already holds the loop's state"), and a single
"Where this came from" section at the end *cites* `agent-dotfiles
docs/SPEC.md §14` and `agent-dotfiles#22` as the evidentiary source, once,
without the skill's operational content depending on that repo's file
layout, script names, or issue numbers to be usable. `loop-tick.md` does
the opposite of that on every page: the citation and the instruction are the
same sentence, 38 and 26 times over.

**This is the crux, and it resolves against the move weakening the coupling
objection.** The tick describes almost everything by name, not by contract.
A future rename of `dispatch.sh`, a renamed lane state, or a retired issue
number would each independently break passages of a moved copy with nothing
short of the current single-repo, single-commit discipline catching it —
which is exactly the failure #158 already measured happening to the skills
that already try to describe this material from a different repo (see the
table below).

**The strongest objection to that recommendation is that same-repo
co-location does not actually earn the "single-commit discipline" claim
above unless it is observed happening, and it needs to be checked, not
assumed: does `lanes.sh` changing and `loop-tick.md` updating really land as
one atomic commit today?** Measured, not asserted: `loop-tick.md`'s own
lane-state table (`agent-dotfiles/scripts/supervisor/loop-tick.md`,
"Dispatch only to lanes it reports `free`") names exactly seven of
`lanes.sh`'s eleven states — `free`, `busy`, `hung`, `dead`, `service`,
`unknown`, and `supervisor` (the last one line above the table, not in it) —
and never mentions `text-blocked`, `menu-blocked`, `unsent`, or `scrolled`
anywhere in the file, confirmed by grepping each literal state name
directly against it. `text-blocked`/`menu-blocked` shipped in #159/#161,
`unsent` in #141 — both well before this measurement — in the same repository,
under the same "code and its own operating instructions share a commit"
theory this document is relying on. **They did not stay in sync even
co-located.** So skills#158 is not only evidence that a *cross-repo* copy
drifts; it is standing evidence, inside `agent-dotfiles` itself, that
proximity alone does not keep a hand-written description of `lanes.sh`
current — nothing forces `loop-tick.md` to change when `lanes.sh` does, same
repo or not, because nothing checks the two against each other. This does
not flip the recommendation: `loop-tick.md` staying in `agent-dotfiles`
is still correct, because a moved copy adds a second, harder desync (a repo
boundary and a versioning lag on top of the same missing enforcement) rather
than fixing the one that already exists. But "one atomic commit" is not by
itself the reason to trust the tick stays current — nothing here currently
guarantees that, in either repo — and a decision-ready answer has to say so
rather than lean on same-repo-ness as if it were self-enforcing. Whatever
`#158`'s "propose how this stops recurring" deliverable lands on (a CI check
diffing `lanes.sh`'s state list against what its own documentation claims,
or a single source both read) is the actual fix for this, and it would need
to run against `loop-tick.md` too, not just against skills in this
repository.

Independently corroborates #158's own claim, extended, with one correction
to #158's own list along the way: #158 names its three newly-undocumented
states as `blocked`, `menu-blocked`, `service`, but `blocked` is itself
stale terminology — #159/#161 (both landed before #158 was filed) already
split it into `text-blocked` and `menu-blocked`, so there is no bare
`blocked` state left to search for. A search against the current name set,
re-run against this repo's present `main`, no longer finds zero: #165
closed #158 the same night by giving `supervised-lane-loop/SKILL.md` a
state table naming `menu-blocked`, `text-blocked`, `dead`, and `service`
explicitly — so `text-blocked`, `menu-blocked`, and `service` now appear in
**one** skill, not zero. That is not a hole in this document's argument;
it is a second, independent demonstration of the same point. Fixing that
one skill's drift took a dedicated, reviewed PR reacting to a filed issue,
not something same-repo proximity did automatically — the exact burden §2
argues a moved `loop-tick.md` would also carry, with nothing here that
would force the fix to happen on its own. The ordinary English word
"blocked" also appears — in `notify`, `loop-contract`, and
`supervised-lane-loop` itself — but never in `lanes.sh`'s literal
state-machine sense elsewhere (a merge being blocked, a
`blocked-needs-human` loop outcome, a channel being blocked for a given
setup). #158's own list needs the same eight-versus-eleven correction this
document's state-name count above makes, and is now closed by #165 rather
than open.

## 3. What breaks on day one

`SUPERVISOR_TICK` is real and does exactly what the issue suspects.
`agent-dotfiles/scripts/supervisor/watchdog.sh:51`:

```bash
TICK="${SUPERVISOR_TICK:-$HERE/loop-tick.md}"
```

and its only use, `watchdog.sh:568`, embeds it as a plain string in the
`/loop` prompt text: `"Follow $TICK exactly."`. `watchdog.sh` never reads,
parses, or executes the file — it only tells the supervisor pane where to
`Read` it. So redirecting where the tick lives is genuinely a one-line
environment-variable change with **zero** code change to `watchdog.sh`,
confirmed by reading the only two lines that touch it. The issue's intuition
is correct on this narrow point.

What is not free is what `SUPERVISOR_TICK` would need to point *at*, and
this repository's own policy makes that a real decision, not a formality.
Checked directly against `agent-dotfiles/settings/default-skills.txt`:
every skill in `[benched]` — eleven of them, including recent ones like
`loop-contract` and `keep-me-honest` — is withheld from the installed
roster by explicit policy, quoting the file itself: *"nothing joins the
roster on evidence credit until it clears failed x2 baseline, passed x3
with the model pinned, and a counter-scenario at x2."* A newly-authored
`loop-tick` skill would start there. That means a plain `git mv` into this
repo, even after `agent-dotfiles`' pinned `apm.yml` ref is bumped to the new
commit and `apm install -g` / `scripts/sync.py apply` actually run, would
**not** put the file anywhere `SUPERVISOR_TICK` could point to via the
normal installed-skill path (`~/.claude/skills/<name>/SKILL.md`,
`~/.agents/skills/<name>/SKILL.md` — both confirmed to exist on this
machine today, for the currently-rostered skills only) unless the estate's
own operating loop is treated as an explicit exception to its own evidence
bar, or someone hand-installs it outside the roster.

The alternative — point `SUPERVISOR_TICK` at a raw checkout path in a
sibling `Skills` clone, the same way `watchdog.sh` already resolves its own
`$HERE` — sidesteps all of that and is genuinely trivial. But it also
skips the entire mechanism "being a skill" is for: it is not `npx skills`-
installable, it pins nothing, and no other consumer benefits, because a
hardcoded local clone path is not a portable install. Either path is
workable; which one is intended is a decision this issue's answer needs to
name, not something a move can leave implicit — the roster path has a real
governance cost this repo already imposes on itself, and the checkout path
opts out of the reason this repo exists.

## A fourth question neither side of #160 named: does this content belong here at all?

This repository's own `AGENTS.md`, verbatim: *"Nothing here depends on any
particular harness, personal dotfiles, or private evaluation tooling"* and
*"Personal harness configuration ... lives in Jon's separate
`agent-dotfiles` repository, which consumes this collection rather than
vendoring it."* `README.md`, verbatim, says the same thing without naming
either the owner or the repository: *"Personal harness configuration —
canonical instructions, hooks, agents, settings, MCP declarations,
install/sync tooling — lives in a separate personal harness repository
that consumes this collection; it is not vendored here."*

`loop-tick.md`, as written today, is exactly that — personal harness
configuration for one specific estate. It names Jon by name, the Director by
name, four specific repositories by name, eight of this estate's own scripts
by name, and 26 of that estate's own issue numbers. It is not "instructions
an agent loads on demand" in the portable sense the rest of this repository
means by that phrase; it is agent-dotfiles' own operations manual, written
in markdown instead of bash only because prose was the right tool for that
content, not because it is meant to travel.

This repo has already drawn this exact line once and gotten it right:
`loop-contract` extracts the portable *shape* of a supervisor loop
(twelve-field contract, autonomy staging, treat-payloads-as-untrusted) and
leaves the estate-specific evidence as a citation. `loop-tick.md` is the
other half of that same tension — the concrete instance the contract is
distilled *from* — and the concrete instance is exactly what this
repository's own scope section says stays where the code is.

## Recommendation

**Do not move `loop-tick.md` as written.** Question 2's measurement resolves
the crux against the move — the coupling objection is not weakened, it is
confirmed, at 38 script-name references and 26 unique issue citations. Moving
it unmodified would also cross this repository's own stated scope boundary,
independent of the coupling question.

The productive path is the one `loop-contract` already demonstrates working:
extract the portable *principles* `loop-tick.md`'s incidents taught — a
tri-state (or richer) lane-health check before dispatching to anything, never
trust an unresolved empty target, claims expire with the process rather than
a clock, verify a "would this revert" claim by attempting the merge rather
than reading a diff, a completion signal tied to the one event that cannot
fire early — written generically, the way `loop-contract` and `tmux/
references/supervisor-lanes.md` already are, citing `agent-dotfiles` once as
where the evidence came from. The concrete, executable tick — script names,
exact paths, the 26-incident history that justifies each rule — stays
versioned with the code in `agent-dotfiles`, where that coupling is real and
currently load-bearing.

If that extraction happens, question 3 still needs an explicit answer before
anything is wired: whether `SUPERVISOR_TICK` should point at an installed,
rostered skill (real portability, real governance cost — the new skill starts
benched under this repo's own evidence-bar policy) or a raw sibling-checkout
path (trivial, but not portable to any other consumer). This document does
not pick one.

None of this is written here. A follow-up issue, scoped to whichever
principles are worth extracting, does the actual authoring — in this
repository, following `create-skill`'s own contract, not as a copy of
`loop-tick.md`.
