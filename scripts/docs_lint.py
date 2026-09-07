#!/usr/bin/env python3
"""Enforce the docs standard (P12 item 2, run/iteration-queue.md): three
rules, all hard failures, none advisory. Classification (which doc is
canonical/historical/research) is a human judgment call, made once per
file and recorded by where the file lives; this script never re-decides
that. It only enforces the structural invariants that judgment call
depends on staying true:

  1. No unclassified root file directly under docs/ -- every doc lives in
     docs/canonical/, docs/historical/, or docs/research/, or is named on
     the ROOT_ALLOWLIST below with a stated reason. An allowlist entry is
     a genuine entry point (something a reader expects to find directly
     under docs/, not a doc someone forgot to sort), never a place to
     dump a new file to dodge classification. Two more shapes are
     recognized at the root without an allowlist entry per file: a
     TOMBSTONE (its first line is exactly TOMBSTONE_MARKER below -- a
     3-line stub left behind when a load-bearing path moved, not new
     content) and a SYMLINK (a compat pointer for an external consumer
     that hardcodes the old path -- rule 2 below independently verifies
     it actually points outside docs/, so rule 1 does not re-litigate
     that; a symlink pointing back INSIDE docs/ is still caught, by rule
     2, not silently allowed here).
  2. No state file (.json/.jsonl) anywhere under docs/, recursively --
     generated/derived state does not belong in a documentation tree.
     The one exception is a SYMLINK whose target resolves OUTSIDE docs/
     entirely: that is a compatibility pointer for an external consumer
     that hardcodes the old path (e.g. a sibling repo's own constant),
     not state living in docs/ a second time. A symlink whose target
     still resolves inside docs/, or a broken symlink, is not exempt --
     both would be exactly the "state file in docs/" shape in disguise.
  3. Zero full-text duplicates by checksum, across every tracked .md and
     .py file in the repo (not scoped to docs/ alone -- a duplicate is a
     duplicate wherever it sits, and P11's own refutation of the prior
     "duplicates" claim already used this same scope). Scoped to files
     `git ls-files` reports (the committed/staged tree), same as CI sees
     it -- an untracked scratch file is not yet part of the repo this
     rule protects.

Every check function below takes `repo` (the root to check) as its own
parameter, never reads a module-level default internally -- the same
shape `scripts/reconcile_skills.py`'s own functions use, and for the same
reason: `tests/test_docs_lint.py` points these at a throwaway fixture
directory, never this repository's own tree, so a broken rule can be
proven broken without ever touching real content.

Exit 0 = all three rules hold. Exit 1 = at least one violation, printed
with the specific path so a fix is mechanical, not a re-investigation.
This script does not repair anything.

Run: python3 scripts/docs_lint.py
"""
from __future__ import annotations
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Genuine entry points a reader expects directly under docs/, never a
# classification dodge. Each entry needs a reason here before it's added.
ROOT_ALLOWLIST = {
    "README.md": "the docs/ taxonomy index itself -- explains canonical/"
                  "historical/research and where to look; a directory of "
                  "classified docs still needs one signpost that isn't "
                  "itself classified into one of the three buckets it "
                  "describes.",
}

CLASSIFIED_SUBDIRS = {"canonical", "historical", "research"}
TOMBSTONE_MARKER = "# Moved (P12, run/iteration-queue.md)"


def check_unclassified_root_files(repo: Path) -> list[str]:
    """Rule 1: every direct child of docs/ is either a classified
    subdirectory, or a file named on ROOT_ALLOWLIST. Nothing else."""
    docs = repo / "docs"
    violations = []
    if not docs.is_dir():
        return violations
    for entry in sorted(docs.iterdir()):
        if entry.is_dir():
            if entry.name not in CLASSIFIED_SUBDIRS:
                violations.append(
                    f"docs/{entry.name}/: unrecognized top-level directory "
                    f"(expected one of {sorted(CLASSIFIED_SUBDIRS)})")
            continue
        if entry.name in ROOT_ALLOWLIST:
            continue
        if entry.is_symlink():
            continue  # rule 2 verifies the target is a real compat pointer
        try:
            first_line = entry.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        except (OSError, IndexError):
            first_line = ""
        if first_line == TOMBSTONE_MARKER:
            continue
        violations.append(
            f"docs/{entry.name}: unclassified root file -- move it "
            f"into docs/canonical/, docs/historical/, or docs/research/, "
            f"or add it to ROOT_ALLOWLIST in this script with a reason")
    return violations


def check_no_state_files_in_docs(repo: Path) -> list[str]:
    """Rule 2: no .json/.jsonl anywhere under docs/, recursively, unless
    it is a symlink whose target resolves outside docs/ entirely."""
    docs = repo / "docs"
    violations = []
    if not docs.is_dir():
        return violations
    docs_resolved = docs.resolve()
    for p in sorted(docs.rglob("*")):
        if p.suffix not in (".json", ".jsonl"):
            continue
        rel = p.relative_to(repo)
        if p.is_symlink():
            try:
                target = p.resolve(strict=True)
            except OSError:
                violations.append(
                    f"{rel}: broken symlink -- a dangling "
                    f"compat pointer is not a valid exception")
                continue
            try:
                target.relative_to(docs_resolved)
                still_in_docs = True
            except ValueError:
                still_in_docs = False
            if still_in_docs:
                violations.append(
                    f"{rel}: symlink target still resolves "
                    f"inside docs/ -- not a real compat pointer, this is a "
                    f"state file in docs/ wearing a symlink")
            continue
        violations.append(
            f"{rel}: state file under docs/ -- relocate it "
            f"(state/ or wherever the repo keeps generated data), state "
            f"does not belong in a documentation tree")
    return violations


def check_zero_duplicate_checksums(repo: Path) -> list[str]:
    """Rule 3: no two tracked .md/.py files share a sha256 of their full
    byte content. Scope is the whole repo, not just docs/ -- matches the
    scope P11's own duplicate-refutation used."""
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "*.md", "*.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    by_hash: dict[str, list[str]] = {}
    for rel in out.splitlines():
        if not rel.strip():
            continue
        path = repo / rel
        if path.is_symlink() or not path.is_file():
            # A symlink (e.g. CLAUDE.md -> AGENTS.md, the multi-harness
            # entry-point convention) is an ALIAS to one real file, not an
            # independent copy that can drift -- comparing its resolved
            # bytes against its own target would always "find" a
            # duplicate that isn't one. Only real, independent files can
            # be a genuine full-text duplicate.
            continue
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        by_hash.setdefault(h, []).append(rel)
    violations = []
    for h, paths in sorted(by_hash.items()):
        if len(paths) > 1:
            violations.append(
                f"full-text duplicate (sha256 {h[:12]}): {', '.join(sorted(paths))}")
    return violations


def run(repo: Path) -> tuple[int, list[str]]:
    """Runs all three checks against repo, returns (exit_code, printed
    lines) -- factored out of main() so tests exercise the same code path
    the CLI does, not a re-implementation of it."""
    checks = [
        ("no unclassified root files under docs/", check_unclassified_root_files),
        ("no state files under docs/", check_no_state_files_in_docs),
        ("zero full-text duplicates by checksum", check_zero_duplicate_checksums),
    ]
    lines = []
    total = 0
    for label, fn in checks:
        violations = fn(repo)
        if violations:
            lines.append(f"FAIL -- {label} ({len(violations)}):")
            for v in violations:
                lines.append(f"  - {v}")
        else:
            lines.append(f"ok   -- {label}")
        total += len(violations)
    lines.append("")
    if total:
        lines.append(f"docs-lint: {total} violation(s). Fix them; this script does not repair anything.")
        return 1, lines
    lines.append("docs-lint: all three rules hold.")
    return 0, lines


def main() -> int:
    code, lines = run(REPO)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
