# docs/ — taxonomy index

Not a skill inventory (`SKILLS-INDEX.md` was deleted for exactly that
anti-pattern, #303 — never resurrected under any name, here or elsewhere).
This is a one-page signpost for the classified documentation tree
itself, enforced by `scripts/docs_lint.py`:

- **`canonical/`** — current, standing reference material. Actively
  true today, not a record of a past event.
- **`historical/`** — dated investigation/decision records. Correctly
  kept, not archived by accident; each states its own disposition.
- **`research/`** — open proposals, not yet decided one way or the
  other.

State (generated JSON/JSONL) lives under `state/` at the repo root, not
here — documentation and data are different trees. `docs/eval-status.json`
is the one exception you'll see in a directory listing: a symlink, not a
file, kept so `jonhill90/agent-estate`'s TUI (which hardcodes that exact
relative path as a Go constant) keeps resolving without this repo
hand-editing a sibling repo's source. The real, generated file lives at
`state/eval-status.json`.
