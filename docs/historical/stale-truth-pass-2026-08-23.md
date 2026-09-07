# Stale-docs truth pass, 2026-08-23

**Correction (review, same day):** this section originally read "12 of
116" for the denominator. `git ls-files '*.md' | wc -l` against the tree
as it ships in this PR — including this report itself, the same
self-inclusion count this pass's own commit adds a file to — returns
**117**, not 116. 116 was the true count of the corpus *before* this
report existed as a file; stating it that way, unqualified, produces a
number a re-run against the shipped tree cannot reproduce, the same
class of bug `agent-tui#136` found and fixed for its own `docs/index.md`
self-reference. Fixed the same way: state the method precisely enough
that a re-run reproduces the number, rather than pointing at a count
that quietly drifts the moment a file lands.

Measured, before starting: 12 of the 116 tracked `.md` files that
existed at the time had no commit touching them in the last 14 days —

```
$ git ls-files '*.md' | wc -l                          # denominator, re-run
$ now=$(date +%s); git ls-files '*.md' | while read -r f; do
    ts=$(git log -1 --format=%ct -- "$f")
    [ $(( (now - ts) / 86400 )) -ge 14 ] && echo "$f"
  done | wc -l                                          # stale count, re-run
```

Re-running the denominator query against the tree this PR ships (this
report is now the 117th tracked `.md` file) returns 117, not 116 — state
the ratio as **12 of 117** if citing it against the shipped tree; "12 of
116" describes the corpus as it stood the moment this pass started, one
file smaller. The stale-count query's own result will keep moving as
files are touched (this same PR's correction to `linear/SKILL.md` below
removes it from a fresh re-run of that query, since fixing a stale file
is itself a commit against it) — re-run both queries together rather
than citing either number as fixed.

A lower proportion than `agent-dotfiles` (16/43, 37%) at the same pass,
but this repo's doc corpus (657 KB before this pass, the largest in the
estate) made the absolute risk worth checking rather than accepting the
lower ratio as evidence of health.

## Method

For every claim in the 12 files that asserts something about the state
of code, a tool, or a command's actual behavior: checked against the
current tree, a real command run, or an installed binary's actual
`--help` output — never against another document, since a doc citing a
doc is how an error propagates rather than gets caught. Real commands
run, not recalled: `gh --version`, `linear --help` and per-subcommand
`--help`, `tmux -V` and an isolated-server `show-options` (to separate
tmux's own factory default from this machine's `~/.tmux.conf`
override), `wc`, `ls`, and direct reads of `scripts/merge_pr.py` /
`scripts/pr_verdict.py` / `scripts/validate_repository.py` for the exit
codes and constants this repo's own `AGENTS.md` describes. The live
`$AGENT_MEMORY_VAULT` was read directly for `memory-conventions`'
claims about `index.md`'s frontmatter and size.

Not rewritten for style, structure, or completeness — a diff full of
rewording would bury a real correction if one existed. None of the 12
needed one.

## Eval-record claims, checked specifically per this pass's brief

None of the 12 stale files assert anything about eval verdicts, the
`could_not_measure` count, the capability-vs-habit taxonomy, or specific
skill counts — grepped all 12 for `eval`, `could_not_measure`,
`taxonomy`, `capability.*habit`, a skill-count pattern, and both recent
issue numbers (`#275`, `#276`); zero hits. The eval record moved a lot
today (`could_not_measure` now 29/41, 0 unevaluated; the taxonomy
hypothesis filed and refuted same-day in `#276`; `#275`'s vally spike
landed with the scoring rule ported) but none of that content lives in
any of the 12 files this pass covers — nothing here needed correcting
for it.

## Result: 12 checked, 1 corrected, 0 could-not-measure, 11 entirely accurate

**Correction (review, same day):** `skills/linear/SKILL.md` was
originally certified accurate outright. It wasn't, under this pass's own
bar — its Common Parameters table listed `-a` as short for `--assignee`
unconditionally, which is true for `issue create`/`issue update` but
false for `issue list`/`issue view`, the subcommands the file itself
demonstrates repeatedly. `linear issue list --help`, run directly:
`-a` is bound to `--app` there, and `--assignee` has no short flag on
`list` at all. A second, same-shape defect surfaced fixing the first:
`-w` is genuinely claimed for both `--web` and `--workspace`
simultaneously on `list`/`view` (confirmed in the real `--help` output,
not this repo's doc). A reader reaching for either short flag on `list`
or `view` off this table's original wording would get a silently wrong
or ambiguous command. Fixed directly in `skills/linear/SKILL.md`
(scoped each short flag to the subcommand(s) it actually means that on)
rather than left standing under an "accurate" verdict — pre-existing,
not introduced by this pass, but this pass's own stated method (check
every command against installed `--help` output) is exactly what
should have caught it the first time through.

Every specific, checkable claim in the remaining 11 files held against
the current tree or a real command run:

| File | Disposition |
|---|---|
| `CLAUDE.md` (+ `.github/copilot-instructions.md`, its committed symlink twin — one file, one check) | accurate — merge-gate exit codes (0/1/2/3) match `scripts/merge_pr.py`'s `_EXIT_FOR_DECISION`/`scripts/pr_verdict.py`'s `EXIT_*` constants exactly; every referenced script, test file, and workflow job name exists; `NAME_RE`/`SKILL_LINE_CAP` match `validate_repository.py`; symlink structure confirmed on disk |
| `skills/primer/SKILL.md` | accurate — procedural only, no external-state claims to falsify |
| `skills/linear/references/teams-projects.md` | accurate — every subcommand, flag, and the `LINEAR_ISSUE_SORT` env var confirmed against the real installed `linear` CLI (v1.9.1) |
| `skills/memory-conventions/SKILL.md` | accurate — `okf_version: "0.1"`, the 200-line/25KB cap (live: 82 lines / 12,670 B), and the `type: user\|feedback\|project\|reference` set confirmed directly against the live vault |
| `skills/failing-test-first/SKILL.md` | accurate — procedural only |
| `skills/linear/SKILL.md` | accurate — CLI structure, `--sort` required-with-error confirmed live, `--from-ref`/`--branch`/`--base`/`--draft`/`--title` all confirmed against the real CLI; both referenced `references/` files exist |
| `skills/tmux/references/fundamentals.md` | accurate — "Validated against tmux 3.5" matches the installed binary exactly; `history-limit` default checked against a truly isolated server (`-f /dev/null`), not this machine's overridden `~/.tmux.conf` (50000) — factory default is 2000, matching the doc |
| `skills/close-the-loop/SKILL.md` | accurate — internally consistent (9 sections stated, 9 listed, 9 in the checklist), no external-state claims |
| `skills/github-cli/SKILL.md` | accurate — version floor (2.65.0+) satisfied by the installed 2.85.0; every spot-checked flag (`--reason`, `--failed`, `--clone`, `--add-assignee`/`--remove-assignee`, `--auto`) confirmed live; all 4 referenced files exist |
| `skills/github-cli/references/issues-labels.md` | accurate — lock reasons, `--checkout`, `--force` on both `label create` and `label clone` confirmed live |
| `skills/github-cli/references/actions.md` | accurate — cache `--sort`/`--order`/`--all`, secret `--visibility`, rerun `--debug` all confirmed live |

No file was rewritten, deleted, or marked historical — nothing here was
found obsolete. This record exists so the next stale-docs pass does not
re-measure the same 12 files from zero.
