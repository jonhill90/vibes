# Should this repository have docs, and what should they say? (#161)

**Disposition, verified 2026-08-16T02:15Z: still an open proposal — no
recorded decision from Jon accepts or rejects any of its four
recommendations.** Checked against the tree as it stands today, item by
item:

1. *"Fix `README.md`'s table now"* — was not done as part of this proposal
   landing (`#164` merged the proposal text only, no `README.md` diff); it
   sat wrong for four more days and is corrected by this same sweep's PR
   (`README.md`, this commit) rather than by a reaction to this document.
2. Per-skill human-facing pages under `docs/` — undecided. `docs/` holds
   only this file and `loop-tick-placement-160.md`; no `docs/<skill-name>.md`
   exists.
3. Consolidating the `AGENTS.md` authoring-bullet duplication with
   `agent-dotfiles`'s own `AGENTS.md` — **not verified from this repository**;
   settling it needs a checkout of `agent-dotfiles` alongside this one, which
   this pass did not have. Flagged unverified rather than assumed either way.
4. A dedicated reader-facing note on user-invoked vs. model-invoked — not
   written. `README.md` now points at this document as the open tracker for
   it (see "Skills in this collection") rather than restating unwritten
   content as done.

The "do not adopt buckets" recommendation is not a thing Jon needed to
decide — it is a description of what already held on 2026-08-12 and still
holds: `skills/` is flat, 25 directories, no `engineering/`/`productivity/`
split. That part of this document reads as correct and current; the four
numbered asks above remain proposal, not settled practice.

Proposal only — no docs are written here, and no files move. Jon reacts to
this; a follow-up PR implements whatever he picks. Same discipline
agent-dotfiles#143 used for the layout question, and it worked.

*Merged 2026-08-12 from two independent answers to the same question, filed
in two repositories by the Director's own duplicate dispatch: this
document (`skills#164`, from `skills#161`) and `agent-dotfiles#182` (from
`agent-dotfiles#177`). This repository's backlog is where `jonhill90/skills`
documentation work belongs — `skills#161` itself records that filing it in
`agent-dotfiles` was the error — so this document survives and absorbs
`#182`'s unique findings: the precise `agent-dotfiles#143` Q3/Q4 distinction
below, the sharper cost argument against moving `create-skill`/SPEC, the
confusable-siblings example, and the against-padding-templates refinement.
`#182`'s engineering/productivity skill-count split (13/7) was checked
against the actual tree and does not match (18/7, unchanged from this
document's original count) — not carried over. `agent-dotfiles#182` is
closed in favour of this document.*

## The concrete reference: `mattpocock/skills`

Jon's own framing: *"i know i was thinking about how matt pocock has docs
in his skills repo and its docs."* Cloned and read directly
(`github.com/mattpocock/skills`, default branch `main`) rather than
summarised from reputation. Its structure, with paths:

```
README.md                          # pitch, install, "why these skills exist"
                                    # essay, and a reference table per bucket
AGENTS.md / CLAUDE.md               # identical — repo contribution rules
CONTEXT.md                          # this repo's OWN domain glossary,
                                    # produced by dogfooding its own
                                    # domain-modeling skill on itself
.agents/
  invocation.md                     # user- vs model-invoked, as a concept
  install-block.md                  # ONE canonical install wording, quoted
                                     # verbatim everywhere else needs it
  writing-docs.md                   # the doc-page template + authoring
                                     # rules for docs/ (page structure,
                                     # tone, linking rules, a "Done when"
                                     # checklist)
  adr/0001-*.md, 0002-*.md          # numbered architecture decisions
docs/
  engineering/<skill-name>.md       # one page per PROMOTED skill only
  productivity/<skill-name>.md      # (mirrors skills/engineering,
                                     #  skills/productivity 1:1)
skills/
  engineering/<name>/SKILL.md       # bucketed, not flat
  engineering/README.md             # bucket-local skill index
  productivity/<name>/SKILL.md
  productivity/README.md
  misc/, in-progress/, deprecated/  # NOT promoted, NOT in docs/, NOT in
                                     # the plugin manifest
.claude-plugin/plugin.json          # Agent-Plugins-adjacent manifest,
  .claude-plugin/marketplace.json   # explicit promoted-skills array
```

Concrete facts, not impressions:

- **35 total `SKILL.md` files, 25 promoted** (`engineering/` +
  `productivity/`) and listed in `plugin.json`'s `skills` array; the
  other 10 sit in `misc/`, `in-progress/`, `deprecated/` and are
  deliberately absent from the README, the plugin manifest, and `docs/`.
- **`docs/` pages exist only for the 25 promoted skills**, one file each,
  averaging ~90 lines (`docs/engineering/tdd.md` is 94 lines). They are
  published externally at `https://aihero.dev/skills-<name>` — the repo
  path is organisation only, not the served URL.
- **A page is not a copy of `SKILL.md`.** `.agents/writing-docs.md`
  states this explicitly and gives the page a fixed section frame —
  *What it does* (leads with the one-sentence job, then the *defining
  constraint* — the fact that makes it behave differently from the
  obvious default), *When to reach for it* (invocation mode + trigger
  boundary), optional *Prerequisites*, a free-form middle in the skill's
  own vocabulary, *Common questions* (sized to evidence actually found —
  the wiki, `gh issue list --search`, `CHANGELOG.md` — never padded),
  *It's working if*, always-present *Where it fits* (role + neighbours +
  a link to the router skill `ask-matt`). The rule that stands out most:
  **"A page carries no install commands"** — the hosting site renders
  the install widget itself, so a hand-written copy in the page would
  drift from it. That single rule is why `.agents/install-block.md`
  exists at all: one canonical block, quoted everywhere, changed once.
- **`README.md` does not restate what `docs/` says.** It carries the
  pitch, the two-philosophy install split (managed plugin vs. editable
  copy), a "why these skills exist" essay anchored to four named failure
  modes, and a flat reference table per bucket linking straight to each
  `SKILL.md` — not to the doc page. The doc pages are a separate,
  externally-hosted layer for someone who found one skill and wants to
  understand it, not someone browsing the whole set.
- **The authoring/contribution rules are `AGENTS.md`+`.agents/*.md`**,
  entirely separate from both `README.md` and `docs/`. `.agents/` covers
  bucket policy, the promoted-skill invariant, invocation classification,
  and the doc-page template itself — none of it consumer-facing.

## What a cold reader of `jonhill90/skills` cannot answer today

Read cold, this repo is 24 skills (flat, no buckets), `AGENTS.md`,
`CLAUDE.md`, `README.md`, `scripts/`, `tests/`. Concretely, today:

1. **`README.md`'s own table is wrong, not just thin.** It is headed
   "Skills in this collection" and lists exactly 13 rows — the 13 skills
   that existed on 2026-08-09 when `docs/` was removed (`069e2c4`). Eleven
   more skills merged 2026-08-11 (`ask-a-council`, `distill`,
   `keep-me-honest`, `loop-contract`, `loop-memory`, `mine-transcripts`,
   `notify`, `prd`, `spec`, `tdd`, `verify-the-instrument`) and the table
   was never touched. A cold reader sees a table that claims completeness
   and is silently 46% short — the identical shape as the roster gap
   agent-dotfiles#181 just fixed, one layer up, in the repo's own README
   instead of a consumer's install manifest.
2. **No skill has a page of its own anywhere.** `SKILL.md` is written for
   the *agent that runs the skill* — dense, imperative, front-loaded with
   trigger conditions. A human deciding whether `wayfinder`-equivalent
   `loop-contract` is the right tool for their situation, versus
   `loop-memory`, has only the one-line README description and the
   `SKILL.md` body itself to go on. There is no document written for a
   human's decision, only for the agent's execution.
3. **Nothing explains the user-invoked/model-invoked split as a concept.**
   `AGENTS.md` has one bullet: *"Classify each skill as model-invoked...
   or user-invoked... Express the classification in `description` trigger
   wording, not in frontmatter fields."* That is instruction for an
   *author*, not orientation for a *reader* — nowhere does this repo say,
   for a reader, "here is what that split means for you and how to tell
   which one you're looking at." (Contrast `mattpocock/skills`, where
   `.agents/invocation.md` is a dedicated concept page and both README
   levels group entries under **User-invoked**/**Model-invoked** headers.)
   Concretely unanswerable today without opening all 24 `SKILL.md` files:
   is `sanity-check` something you type, or something the agent reaches
   for on its own — and how does it differ from `dispatching-subagents`
   and `keep-me-honest`, three names that plausibly overlap in when
   you'd reach for them? `mattpocock/skills` answers exactly this shape
   of question in `## When to reach for it` on every page, in a table
   whenever the answer branches.
4. **No categorisation at all.** `mattpocock/skills` splits 25 promoted
   skills into two buckets your eye can scan; this repo's `skills/` is 24
   directories in one flat alphabetical list, and the README table is
   likewise flat. A reader cannot tell `create-skill` (repo-authoring
   tooling) from `notify` (an outbound-messaging utility) from
   `loop-contract` (a design discipline) except by reading each
   description in full.
5. **The install story is one command with no philosophy attached.**
   `npx skills add jonhill90/skills --skill <name>` is correct and
   sufficient mechanically, but it doesn't say anything about what
   installing means (a copy you own and can edit — this repo has no
   competing "managed bundle" mode, unlike `mattpocock/skills`'s
   plugin-vs-skills.sh split) or how updates are meant to be pulled back
   in later.
6. **No visible decision trail.** `provenance-manifest.md`,
   `SPEC.md` §10.1's evidence bar, and the eleven skills' own individual
   issues (`#129`, `#133`–`#137`, `#146`) are the actual record of *why*
   a skill exists and what it does and does not cover — but all of that
   lives in `agent-dotfiles` or in closed issues here, not anywhere a
   cold reader of *this* repo would find it. A reader cannot currently
   answer "why does `keep-me-honest` exist and how is it different from
   `sanity-check`" without leaving this repository.

## Two audiences, and the real cost of moving one

The issue is right that conflating these is how docs sprawl. They are
genuinely different documents:

| | **Using** a skill | **Authoring** one |
|---|---|---|
| Reader | Someone deciding whether/how to install and invoke a skill | Someone writing a new `SKILL.md` or reviewing one |
| Answers | What it does, when it fires, install command, what it's not for | Frontmatter contract, trigger-wording discipline, the 500-line cap, `references/` layout, what makes a description reliably fire |
| Lives today | Nothing (the gap this issue names) | `AGENTS.md` (this repo) + the `create-skill` skill (this repo) + `agent-dotfiles`' `AGENTS.md` "Skill Authoring and Sourcing" section |

**Correcting the issue's premise on where authoring material lives.**
It is not solely in `agent-dotfiles`. This repo's own `AGENTS.md` already
carries a "Skill Authoring" section (naming rules, the 500-line cap,
frontmatter fields, `jonhill90/skills#142`'s colon-quoting fix), and
`skills/create-skill/SKILL.md` (110 lines) is the portable, general
"how to design a good skill" discipline — installable by anyone, not
`agent-dotfiles`-specific. `agent-dotfiles`' own `AGENTS.md` already says,
in so many words, *"Follow that repository's `AGENTS.md`, not this
section, when writing skill content"* — it explicitly defers here already.

What genuinely is `agent-dotfiles`-only, and does **not** belong in a
move, is *rostering* policy: `default-skills.txt`, the §10.1 evidence
bar, and the cost-gate exception mechanics agent-dotfiles#181 just
extended. That is Jon's personal install-default decision-making, not a
property of the skill or a fact a skill author elsewhere needs. Moving
it here would do more than duplicate — it would invert a dependency
direction `agent-dotfiles`' own `CLAUDE.md` already states explicitly
("skill content is not vendored here … declared as pinned dependencies"):
`agent-dotfiles` depends on `jonhill90/skills` for content, not the
other way around, and rostering logic is meaningless outside
`agent-dotfiles`' own install path. It would also gain nothing
`mattpocock/skills` argues for — his `.agents/` material (his triage
labels, his ADR numbering, his docs-page template) is scoped to *his*
repo's own conventions, not a portable authoring spec, so it is not
evidence for centralizing anything here either.

What is a real, live duplication: the bullet list of `SKILL.md`
mechanics — *"portable frontmatter, 500-line cap, `references/` for
detail, deterministic scripts, imperative instructions, model-invoked vs.
user-invoked framed in `description`"* — is written out **almost
verbatim in both repos' `AGENTS.md`** (this repo's "Skill Authoring"
section, and `agent-dotfiles`' "Skill Authoring and Sourcing" section,
which claims to defer here but restates the same list anyway). **The
cost of fully consolidating it here and trimming `agent-dotfiles`' copy
to a one-line pointer:** one small edit in each of two files, not a
move of any content that does not already live here — cheap, and the
duplication is small enough that this is worth doing regardless of the
larger docs question. **The cost of moving anything bigger** — e.g. if
someone later wants to relocate the evidence-bar mechanics themselves —
would be real: `default-skills.txt`, `validate_apm_skill_roster`, and
now `validate_skill_bench`/`validate_skill_roster_delta` are
`agent-dotfiles`-specific code that has nothing to move to. Recommend:
fix the small duplication now; do not treat it as license to move
anything roster-shaped.

## Resolving the tension, not asserting a side

The issue frames a real tension: *"a standalone public collection
arguably needs MORE explanation of itself, not less."* Two independent
pieces of evidence resolve it, and they reinforce each other.

**First, what `069e2c4` actually removed.** Read against its diff
(`git show 069e2c4~1:docs` from this worktree), `docs/` in this repo
before the split was a byte-identical mirror of `agent-dotfiles`' own
project docs: `PRD.md`, `SPEC.md`, `docs/agent-engineering-lineage.md`,
`docs/evals.md`, `docs/harness-engineering.md`, `docs/memory.md`,
`docs/migration-audit.md`, `docs/provenance-manifest.md`,
`docs/work-tracking.md` — `agent-dotfiles`' *personal harness engineering*
project record, not anything describing what a skill in this collection
does or how to use one. The commit message confirms the intent: *"Strip
agent-dotfiles harness machinery... and private behavioral-eval content
out of the working tree."* It was a repo-split cleanup.

**Second, and more precisely: `agent-dotfiles#143`'s council already
posed and answered a narrower version of this exact question, on
purpose, with a named condition for reversing it.** Read directly
(`agent-dotfiles`' `docs/docs-layout-council-138.md`, Question 3):
*"Should `skills`/`skills-private` have `docs/` at all?"* — answered
**12/12 unanimous, no**, both by arms told the `069e2c4` history and by
arms shown only bare structure (`dir-c`/`dir-d`, no history). Every arm,
informed or blind, converged on the identical reversal condition,
quoted verbatim from the findings doc: *"it flips only if the repos
start accumulating documentation genuinely native to a skill collection
(not harness machinery) that no longer fits in `README.md`/`AGENTS.md`."*

That is the correct scope for this issue, and it is narrower than
"reopen #143": **Q3** (docs at all, for a content repo) and **Q4**
(agent-dotfiles/agent-evals's five-way `architecture/decisions/product`
split) are different questions in the same council, and this proposal
touches only the first. Q3's own stated condition is what licenses
reopening it — Matt Pocock's `mattpocock/skills` is exactly that
evidence: real, external, populated documentation native to a skill
collection, that did not exist as input when Q3 was answered. Q4 stays
untouched and unrelitigated: nothing here proposes subdividing
`jonhill90/skills`' hypothetical `docs/` tree, and Pocock's own `docs/`
is flat-per-bucket, not five-way, so even the reference this proposal
draws on does not point toward Q4's structure.

## The Agent Plugins angle (skills#159), briefly

`skills#159` is adjacent, not the same question: it is about `plugin.json`
making this repo consumable by any Agent-Plugins-conformant client
(spec: `agent-plugins.org/specification`,
`github.com/agentplugins/agent-plugins-spec`), not about explaining the
repo to a human reader. A public repo choosing to *describe* itself to
the outside world (this proposal) and a public repo choosing to
*package* itself for the outside world (#159's manifest) are the same
posture applied to two different files, and `mattpocock/skills` shows
the concrete reason they're worth sequencing together rather than
separately: its `.claude-plugin/plugin.json` `skills` array is exactly
the set that also needs a bucket/category answer, and its own dated ADR
(`.agents/adr/0002-ship-as-a-claude-code-plugin.md`) records *why*
Claude-first — Codex's plugin format rejects an array and accepts only
one path, forcing a real structural choice between promoted-vs-not
buckets — rather than silently picking one harness. If #159's
`plugin.json` and any future bucket/category decision from this issue
both touch "which skills are the curated public-facing set," deciding
them independently risks two different answers to the same underlying
question. Recommend: resolve this issue's categorisation question (if
any) before or alongside #159's manifest, not after — but that is a
sequencing note, not a reason to fold plugin work into this proposal.

## Recommendation

Do not adopt `mattpocock/skills`'s bucket/category split
(`engineering/`, `productivity/`, `misc/`, ...) for `skills/` itself —
that re-opens agent-dotfiles#143 **Q4** by another name, and #143's
finding there was that the disagreement correlated with whether an arm
knew this repo's own history of trying and reversing subdivision once
(2026-07-13), not with genuine merit. Flat stays flat, for `skills/`
and for any `docs/` this issue adds.

What is not foreclosed by #143 — because this proposal reopens **Q3**
only, on the evidence its own stated reversal condition names, and
Q3 never addressed layout in the first place, only existence — and is
worth Jon's decision:

1. **Fix `README.md`'s table now**, regardless of anything else decided
   here: it is not incomplete, it is wrong, and it is a five-minute
   correction. (Flagged, not done, per this issue's "do not write the
   docs" constraint — but it is small enough that it may not deserve its
   own issue either; Jon's call.)
2. **Decide whether per-skill human-facing pages are worth it here at
   all**, given this collection has no external publishing surface like
   `aihero.dev` to host them and no newsletter audience pulling readers
   toward them. If yes, they would live inline (`docs/<skill-name>.md`,
   flat, matching this repo's existing flat `skills/` — no bucket
   mirroring) rather than externally hosted, and should reuse
   `writing-docs.md`'s section frame (*What it does*, *When to reach for
   it*, *Common questions*, *It's working if*) as a **ceiling, not a
   quota**: `writing-docs.md`'s own rule is that *Common questions* is
   "sized to what it found, not padded," and with zero observed reader
   questions behind most of these 24 skills today, a fixed template
   filled in for its own sake would invent content nobody asked for.
   Write *What it does*/*When to reach for it* for every page; add
   *Common questions*/*It's working if* only where a real issue, a
   repeated question, or a changelog entry earns them.
3. **Consolidate the small `AGENTS.md` authoring-bullet duplication**
   described above — cheap, uncontroversial, and worth doing regardless
   of what else is decided.
4. **Add a short, dedicated note on the user-invoked/model-invoked
   split** as a reader-facing concept, not just an author instruction —
   this repo already has the substance; it just orients the wrong
   audience today.

None of this is written in this change. A follow-up PR, scoped to
whichever of the above Jon picks, does the writing.
