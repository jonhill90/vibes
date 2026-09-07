#!/usr/bin/env python3
"""Did a trial's Arm A genuinely read the skill it was prompt-instructed to
read — mechanically, from the real transcript, never from self-report
(jonhill90/skills#269 review, estate:2; tri-state fix, skills#273 review,
estate:4).

Why this exists: the #265-#269 eval lineage delivers skill content to
Arm A via a prompt instruction ("Arm A only: read skills/<name>/SKILL.md
before starting"), deliberately NOT via the Skill tool, to dodge a
DIFFERENT already-known failure mode (`docs/historical/eval-harness-findings.md`'s
"Cause D" — the with-skill arm silently never receiving the skill via
Skill/ToolSearch discovery). But nothing logged whether the model
actually complied with that instruction: `$STUB_LOG` records only the
fake CLI's own calls, and `manifest.json`'s `actions_log` is
self-reported by the arm — this harness's own standing convention
(mirrored here, not reinvented: see `mechanize`'s and
`progressive-disclosure`'s own eval-result.md files) treats a
self-reported log as informational, never as evidence a scored axis can
rely on. A genuine null (skill read, no measurable divergence) and a
silent wiring failure (skill never read, both arms ran unprompted) were
therefore indistinguishable from the committed record — and that bites
hardest on `could_not_measure`, the majority verdict across this
population (29 of 41 skills, `eval_status.py --summary`, 2026-08-23).

WHAT THIS DOES, and no more (deliberately not a general observability
framework — one function, one field): scans a trial's real transcript for
a genuine `Read` tool_use block whose input path resolves to the given
skill's `SKILL.md`. It does not inspect whether the read succeeded (a
file-not-found error is still evidence the model attempted compliance, a
different and rarer failure than total omission, and out of this
function's narrow scope) and it does not read `manifest.json`'s
`actions_log` at all — the self-report this function exists to stop
being the only evidence.

TRI-STATE, not boolean (skills#273 review): the first version of this
function collapsed "the transcript is well-formed and genuinely shows no
Read" and "the transcript could not be read at all" into the same
`False` — an unparseable, truncated, empty, or wrong-file transcript
(an operator accidentally pointing this at `$STUB_LOG`, say, which has
none of this shape) returned `False`, byte-for-byte identical to a real
negative result. That silently re-created, one level down, the exact
`could_not_measure`-vs-`confirmed-absent` conflation this whole function
exists to close. Fixed by tracking whether at least one recognisable
`assistant`-turn or `tool_use` event was ever seen in the transcript —
if none was, the file was not legible as a real transcript at all and
the answer is `None` ("could not determine"), never `False`. Only once
a real, parseable transcript has been confirmed present does "no
matching Read found in it" mean `False`.

TRANSCRIPT SHAPE, verified against a real Claude Code transcript before
assuming one (`~/.claude/projects/**/*.jsonl`, and identical in shape to
a headless `claude -p --output-format stream-json` capture — both emit
the same per-turn event envelope): one JSON object per line, top-level
`type: "assistant"` for a model turn, `message.content` a list of blocks,
a tool invocation appearing as `{"type": "tool_use", "name": "Read",
"input": {"file_path": "<absolute path>"}}`. `file_path` is always
absolute in a real transcript — this function's own path-matching
handles a relative `skill_path` argument (the common case: callers pass
the repo-relative form, e.g. `skills/github-cli/SKILL.md`) by suffix
match on a `/` boundary, and an absolute `skill_path` by exact match, per
that same observed shape.

Usage as a library:
    from skill_read_confirmed import skill_read_confirmed
    confirmed = skill_read_confirmed("path/to/trial.transcript.jsonl",
                                      "skills/github-cli/SKILL.md")
    # confirmed is True, False, or None ("could not determine")

Usage as a CLI, to populate eval-result.md's structured field by hand
(this harness's own passes are hand-run, not auto-wired — see
`docs/historical/eval-harness-findings.md`'s own "hand-scored, not a general harness
feature" precedent for the longitudinal design):
    $ python3 scripts/skill_read_confirmed.py <transcript.jsonl> <skill_path>
    true
    $ echo $?
    0   # 0 = true, 1 = false, 2 = could not determine (no recognisable
        #     assistant/tool_use event in the transcript at all --
        #     record this as unresolved, never as a confirmed false)
        # 3 = usage error, or the transcript file itself could not be
        #     opened at all (distinct from 2: this is "we never even
        #     got to look," not "we looked and it wasn't a transcript")

Python 3 stdlib only, matching every other script in this directory
(`eval_status.py`, `pr_verdict.py`, `check_skill_install.py`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path, PurePosixPath


def skill_read_confirmed(transcript_path: str | Path, skill_path: str) -> bool | None:
    """Return True/False/None for whether `transcript_path` (a real Claude
    Code transcript -- a saved session `.jsonl` or a headless
    `stream-json` capture, both the same event shape) contains a genuine
    `Read` tool_use block whose `input.file_path` resolves to
    `skill_path`.

    - True: a matching Read was found.
    - False: the transcript is legible (at least one recognisable
      `assistant`-turn or `tool_use` event was seen) and no matching Read
      was found in it -- a real negative, not a parsing gap.
    - None: COULD NOT DETERMINE. The transcript could not be opened, was
      empty, or contained not one recognisable `assistant`/`tool_use`
      event -- unparseable JSON throughout, a truncated capture, or the
      wrong file entirely (e.g. `$STUB_LOG`, which has none of this
      shape). This must never be read as, or recorded as, `False` --
      that is the exact conflation this tri-state exists to prevent
      (skills#273 review).

    The one thing this function refuses to be lenient about, in any of
    the three outcomes, is what counts as evidence: only a real
    `tool_use` block named exactly `Read` counts toward `True`, never a
    `Bash` call that happens to `cat`/`head` the same file, and this
    function never reads `manifest.json`'s self-reported `actions_log` at
    all -- both would reintroduce the class of evidence this function
    exists to stop trusting.
    """
    try:
        text = Path(transcript_path).read_text(encoding="utf-8")
    except OSError:
        return None

    skill_path = skill_path.strip()
    is_absolute_query = skill_path.startswith("/")
    skill_path_norm = PurePosixPath(skill_path).as_posix()

    saw_recognizable_event = False

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "assistant":
            saw_recognizable_event = True
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            saw_recognizable_event = True
            if block.get("name") != "Read":
                continue
            tool_input = block.get("input")
            if not isinstance(tool_input, dict):
                continue
            file_path = tool_input.get("file_path")
            if not isinstance(file_path, str) or not file_path:
                continue
            candidate = PurePosixPath(file_path).as_posix()
            if is_absolute_query:
                if candidate == skill_path_norm:
                    return True
            else:
                if candidate == skill_path_norm or candidate.endswith("/" + skill_path_norm):
                    return True

    if not saw_recognizable_event:
        return None
    return False


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <transcript.jsonl> <skill_path>", file=sys.stderr)
        return 3
    transcript_path, skill_path = argv[1], argv[2]
    if not Path(transcript_path).is_file():
        print(f"skill_read_confirmed: no such file: {transcript_path}", file=sys.stderr)
        return 3
    confirmed = skill_read_confirmed(transcript_path, skill_path)
    if confirmed is None:
        print("unknown", file=sys.stdout)
        print(
            "skill_read_confirmed: no recognisable assistant/tool_use event in "
            f"{transcript_path} -- could not determine, do not record as false",
            file=sys.stderr,
        )
        return 2
    print("true" if confirmed else "false")
    return 0 if confirmed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
