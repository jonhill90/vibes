#!/usr/bin/env python3
"""Read and check state/eval-status.json — jonhill90/skills#230's own
machine-readable record of which skills have been run through the
keep/improve/rename/drop harness (agent-evals, private, not published
here) and what each run found.

Why this exists: #231 and #232 each recorded a verdict as prose in a
per-skill `references/eval-result.md` file. Prose answers "what did THIS
skill's eval find" one file at a time; it does not answer "which of the
40 skills still need a first pass" without reading all 40 SKILL.md
directories and checking each one by hand — the exact kind of question
that should be a command, not something an agent re-derives every pass
(jonhill90/skills#230's own follow-on: "a tool beats an agent every
time"). This script is that command.

This is deliberately NOT a harness, a scorer, or a runner — it owns one
thing: keeping the record consistent with the skills that actually exist,
and answering "which are unevaluated" in one call. Running an eval and
writing its result is still a human/agent judgement call per skill (this
script has no opinion on verdicts); recording that a record exists and is
internally consistent is not.

Exit codes:
  0  record is consistent with skills/ -- every skill has exactly one
     entry, every entry points at a real skill, and the typed-absence
     rule (unevaluated <-> date/evidence both null; anything else <->
     both set, evidence pointing at a real file) holds for every entry.
  1  drift found -- printed as findings, one per line.
  2  could not check at all -- state/eval-status.json missing or not
     valid JSON, or skills/ not found. Never read as "consistent."

--record (jonhill90/skills#230, estate-loop/agent-b2.md's own rule: "Update
state/eval-status.json through scripts/eval_status.py, never by hand"): the
one write path this record has. Every prior pass hand-edited the JSON
directly -- fine for a handful of entries, but a hand edit cannot be
stopped from writing a malformed one (a verdict this file wouldn't accept,
an evidence path that doesn't exist, a stray date on "unevaluated"). This
validates the SAME rules `check()` above enforces before it ever touches
the file, so a --record call can never produce a record its own `check()`
would then reject. See do_record's own docstring for the exact contract.

STORAGE, since agent-b3.md's own fix (three PRs -- #239, #240, #243 --
conflicted on this one shared file the same night): state/eval-status.json
is no longer hand-authored data. It is GENERATED, by this script, from
state/eval-log/<skill>.jsonl -- one APPEND-ONLY file per skill, one JSON
line per observation ({"verdict", "date", "evidence", "source"}, "source"
naming the pass/PR that produced it, the attribution the single-record
shape had no room for). A pass that evaluates skill X now touches only
state/eval-log/X.jsonl -- two passes over disjoint skills touch disjoint
files and cannot conflict at the git level at all; two independent
evaluations of the SAME skill both survive as separate lines in that
skill's own log, distinguishable by --history, rather than the second one
silently overwriting the first the way a single-record entry always did.
state/eval-status.json itself keeps its EXACT pre-existing shape ($comment
+ one current entry per skill, no "source" field) for every reader that
already depends on it (`check()`, --summary, --unevaluated, downstream
tooling) -- it is regenerated to show each skill's LATEST observation
(by date, ties broken by log order) every time --record runs, via the
same dump_record() this file has always used, so its own byte-for-byte
round-trip property is unchanged. See regenerate_record()'s own docstring
for exactly how "latest" is chosen.

--record also runs `check_skill_install.check_installed` (jonhill90/skills#230,
#244's full-population diagnosis: 4 of 20 could_not_measure results were a
skill that was never actually on the machine's shared skills path, found
by hand, one at a time, four separate times) before it will write a
verdict, and refuses -- naming the skill and whether the installed copy is
MISSING or DIVERGENT from this repo's own copy -- unless the caller passes
--skip-install-check with a reason. See check_skill_install.py's own doc
comment for what the check does and does not cover.

--claude-skills-dir (jonhill90/skills#285): --record's install check
defaults to comparing against the one shared `~/.claude/skills` path every
running agent on the host reads from. This flag points that comparison at
a different directory instead (a scratch checkout, a project-local skills
dir) -- see do_record's own docstring for the exact contract. #285 asks a
larger question this flag does not answer: whether the with/without
evaluation ARMS themselves (not this record-time gate) should be able to
point at an arbitrary skill source. That harness is `agent-evals`, private
and out of this repository's scope (see this file's own top line) -- this
flag only narrows the ONE coupling this repository's own code enforces:
that recording a verdict requires the skill to already be live on the
single shared path.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_skill_install  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
# P12 (run/iteration-queue.md): relocated from docs/eval-status.json and
# docs/eval-log/ -- state, not documentation. docs/eval-status.json is
# kept as a symlink to state/eval-status.json for agent-estate's TUI,
# which hardcodes that exact relative path as a Go constant
# (src/tui/cmd/estate/skills.go's skillsEvalStatusRelPath) -- this
# module writes the real file at its new canonical location; the
# symlink makes the old path keep resolving for that external reader
# without this repo hand-editing a sibling repo's source in this PR.
RECORD_PATH = REPO / "state" / "eval-status.json"
SKILLS_ROOT = REPO / "skills"
EVAL_LOG_DIR = REPO / "state" / "eval-log"
# Same pattern as REPO/RECORD_PATH/SKILLS_ROOT/EVAL_LOG_DIR above: a
# module-level default, monkeypatchable by tests that sandbox the whole
# record in a tmp dir (see tests/test_eval_status.py's own
# TestRecordCLI.setUp) so those tests keep exercising the REAL
# install-check pass-through path against a fixture, never quietly
# skipping the check just because the test itself is sandboxed.
CLAUDE_SKILLS_DIR = check_skill_install.default_claude_skills_dir()

VERDICTS = {"keep", "improve", "rename", "drop", "could_not_measure", "unevaluated"}
RECORDABLE_VERDICTS = VERDICTS - {"unevaluated"}
ARM_A_SKILL_READ_CONFIRMED_VALUES = {"true", "false", "unknown"}


class RecordError(RuntimeError):
    """The record itself could not be read at all -- exit 2, never 0 or 1."""


def load_full_doc(path: Path) -> dict:
    """The whole parsed state/eval-status.json -- $comment and all. Kept
    separate from load_record (below, which most callers want: just the
    skills mapping) because --record needs to rewrite the file and must
    not lose the $comment or any other top-level key while doing it."""
    if not path.is_file():
        raise RecordError(f"no record at {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise RecordError(f"{path} is not valid JSON: {exc}") from exc
    if "skills" not in doc or not isinstance(doc["skills"], dict):
        raise RecordError(f"{path} has no top-level \"skills\" object")
    return doc


def load_record(path: Path) -> dict:
    return load_full_doc(path)["skills"]


def dump_record(doc: dict, path: Path) -> None:
    """Writes doc back in the exact one-line-per-skill shape the file has
    always shipped in (sorted keys, compact per-entry JSON) -- NOT
    json.dump(doc, indent=2), which would reformat every line and turn a
    one-skill change into a whole-file diff. Verified byte-identical on a
    no-op round trip of the real file (tests/test_eval_status.py's own
    test_dump_record_is_a_noop_round_trip_on_the_real_file)."""
    lines = ["{", f'  "$comment": {json.dumps(doc["$comment"])},', '  "skills": {']
    names = sorted(doc["skills"].keys())
    for i, name in enumerate(names):
        comma = "," if i < len(names) - 1 else ""
        lines.append(f"    {json.dumps(name)}: {json.dumps(doc['skills'][name])}{comma}")
    lines.append("  }")
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def log_path(skill: str) -> Path:
    """state/eval-log/<skill>.jsonl -- the ONE file a pass evaluating
    `skill` ever writes to. Two passes over disjoint skills touch two
    disjoint files here and cannot conflict at the git level; this is the
    property that makes this storage shape the fix for the file-per-PR
    conflict agent-b3.md's own brief measured (three PRs, one night, all
    on the old single state/eval-status.json)."""
    return EVAL_LOG_DIR / f"{skill}.jsonl"


def read_observations(skill: str) -> list[dict]:
    """Every observation ever recorded for `skill`, in the order its own
    log file has them (append order) -- oldest first. A skill with no log
    file yet (never evaluated) returns [], not an error: absence is a
    typed value here the same way "unevaluated" already is in the
    generated record (this module's own top-of-file doc comment)."""
    path = log_path(skill)
    if not path.is_file():
        return []
    observations = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        observations.append(json.loads(line))
    return observations


def append_observation(skill: str, entry: dict) -> None:
    """Appends entry as one JSON line to skill's own log file -- the ONLY
    write this module performs against state/eval-log/. Never rewrites or
    reorders a line already there: two independent evaluations of the
    same skill both survive as two separate lines, not one overwriting
    the other, which is exactly what the single-record shape could not
    do (agent-b3.md's own brief: "independent second evaluations are the
    most valuable thing the loop produces and are currently the ones most
    at risk of being merged away")."""
    EVAL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    with log_path(skill).open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def latest_observation(observations: list[dict]) -> dict | None:
    """The most recently DATED observation, not simply the last line in
    the file -- two passes appending to the same skill's log on separate
    branches can land in either order once git merges them (both are pure
    additions at end-of-file; nothing here assumes one branch's commit
    lands before the other's), so trusting file order alone could let a
    genuinely older evaluation win a comparison it should have lost.
    Ties (identical date) keep log order, on the assumption that within
    one calendar day, appended-later means observed-later. None for an
    empty list -- "never evaluated," not a KeyError waiting to happen."""
    if not observations:
        return None
    return max(enumerate(observations), key=lambda pair: (pair[1]["date"], pair[0]))[1]


def regenerate_record(comment: str, skill_names: set[str]) -> dict:
    """Rebuilds the FULL state/eval-status.json doc ($comment + skills)
    from every skill's own log file under state/eval-log/ -- the
    "mechanical, not manual" regeneration agent-b3.md's own brief
    requires. Each skill's entry is its LATEST observation's own
    verdict/date/evidence, in the EXACT shape the record has always had
    (no "source" key here -- source lives only in the log; adding it to
    the generated record would change a schema every existing reader,
    including dump_record's own round-trip test, depends on). A skill
    with no observations at all gets the same "unevaluated" default the
    hand-authored record always used."""
    skills: dict[str, dict] = {}
    for name in sorted(skill_names):
        latest = latest_observation(read_observations(name))
        if latest is None:
            skills[name] = {"verdict": "unevaluated", "date": None, "evidence": None}
        else:
            skills[name] = {
                "verdict": latest["verdict"],
                "date": latest["date"],
                "evidence": latest["evidence"],
            }
    return {"$comment": comment, "skills": skills}


def do_record(skill: str, verdict: str | None, evidence: str | None, date: str | None,
              source: str | None, skip_install_check: str | None = None,
              claude_skills_dir: Path | None = None,
              arm_a_skill_read_confirmed: str | None = None) -> int:
    """Appends ONE observation to state/eval-log/<skill>.jsonl, then
    regenerates state/eval-status.json from every skill's own log -- the
    one path --record exposes, and the one this script wants every future
    pass to use instead of a hand edit (see this module's own docstring).
    Writing only ever APPENDS to skill's own log file; an earlier
    observation for the same skill is never touched, so two independent
    evaluations of one skill both survive as separate lines, distinct
    from and never overwriting each other (--history reads them back).

    Refuses (exit 2, prints why) rather than writing anything when:
      - `skill` has no skills/<name>/ directory -- never record a verdict
        for something that doesn't exist.
      - `verdict` is not one of RECORDABLE_VERDICTS -- "unevaluated" is
        not recordable THROUGH this flag; it is the record's own default
        for an entry no log has an observation for yet, never something
        to write back (recording "unevaluated" on purpose is
        indistinguishable from never having called this at all, so there
        is nothing for this path to do for it).
      - `evidence` is missing, or does not point at a real file in this
        repo -- the same "date/evidence load-bearing, not decoration"
        rule `check()` already enforces; recording an entry `check()`
        would then flag as drift is exactly what this flag exists to stop.
      - `source` is missing -- the one field this shape adds over the old
        single-record entry, and the one that makes "which pass produced
        this" decidable from the file itself rather than from memory
        (agent-b3.md's own bar). Never optional: an unattributed
        observation is exactly the ambiguity this fix exists to remove.
      - the skill under test is not correctly installed on
        ~/.claude/skills right now (jonhill90/skills#230, #244's own
        full-population diagnosis: four independent passes each lost a
        real pair to exactly this, discovered by hand each time, because
        nothing MECHANICAL stood between a broken install and a recorded
        verdict). `check_skill_install.check_installed` names MISSING vs
        DIVERGENT specifically rather than one "bad install" message --
        see that module's own doc comment for why the distinction
        matters. `skip_install_check`, if given a non-empty reason,
        overrides this refusal (the check may not apply -- e.g. this
        machine's own install state is known to differ from whatever
        machine actually ran the eval) but prints a loud stderr warning
        naming the reason; the override is never silent.

    `claude_skills_dir` (jonhill90/skills#285): the directory the install
    check compares `skills/<skill>/` against, defaulting to the module-level
    CLAUDE_SKILLS_DIR (`~/.claude/skills`, the one path shared by every
    running agent on this host) when None -- existing callers that never
    pass this argument get byte-identical behavior. Passing a different
    directory lets a verdict be recorded from an install visible only to
    this evaluation (a scratch checkout of a specific commit, a
    project-local skills dir) WITHOUT ever symlinking a not-yet-merged or
    not-yet-trusted skill into the one path every other agent on the host
    reads -- the coupling #285 names ("evaluating a candidate skill makes
    it live for every running agent on the host as a side effect of
    measuring it"), narrowed to the one place this repository's own code
    enforces it. This does not touch how the with/without evaluation ARMS
    themselves get skill content -- that harness (`agent-evals`, private,
    see this module's own top-of-file doc comment) is out of this
    repository's scope; this only changes what --record's own pre-write
    gate checks against. The visibility guarantee is unchanged either way:
    `check_skill_install.check_installed` still runs, still returns
    OK/MISSING/DIVERGENT, and its message still names the exact directory
    it checked -- pointing it elsewhere does not make the check optional
    or silent, only redirects what it verifies against.

    `date` defaults to today (real wall-clock date; this is an ordinary
    script run by a human/agent, not a Workflow script, so datetime.date.
    today() is the right tool) -- overridable for tests and for a
    deliberate backdate, never read by production callers.

    `arm_a_skill_read_confirmed` (jonhill90/skills#300): the tri-state
    `skill_read_confirmed.py` produces for an arm-wiring-shaped pass --
    "true", "false", or "unknown" (an unscannable input must never be
    collapsed into a confident "false"; see that module's own doc comment).
    Rejected (exit 2) if given anything outside
    ARM_A_SKILL_READ_CONFIRMED_VALUES, the same "reject a bad value rather
    than silently write it" rule --verdict/--evidence already enforce.
    None (the flag omitted) means the key is left OUT of the appended
    entry entirely -- "this pass did not measure it" must stay
    distinguishable from "this pass measured it and could not tell"
    (unknown), which a default of "unknown" or "false" would each collapse
    in a different direction. Existing records written before #300 have no
    such key at all and must keep loading -- this flag does not touch
    read_observations/latest_observation/check(), none of which requires
    the key to be present.
    """
    if not (SKILLS_ROOT / skill).is_dir():
        print(f"--record {skill}: no skills/{skill}/ directory -- refusing to "
              "record a verdict for a skill that doesn't exist", file=sys.stderr)
        return 2
    if verdict is None:
        print(f"--record {skill}: --verdict is required "
              f"(one of {sorted(RECORDABLE_VERDICTS)})", file=sys.stderr)
        return 2
    if verdict not in RECORDABLE_VERDICTS:
        print(f"--record --verdict {verdict!r}: not one of {sorted(RECORDABLE_VERDICTS)} "
              "(unevaluated is not recordable through this flag -- see --help)",
              file=sys.stderr)
        return 2
    if not evidence:
        print(f"--record {skill}: --verdict {verdict!r} requires --evidence "
              "(a repo-relative path)", file=sys.stderr)
        return 2
    if not (REPO / evidence).is_file():
        print(f"--record {skill}: evidence path {evidence!r} does not exist "
              "in this repo -- write the file first", file=sys.stderr)
        return 2
    if not source:
        print(f"--record {skill}: --source is required -- name the pass/PR "
              "this observation came from (e.g. \"PR #244\")", file=sys.stderr)
        return 2
    if (arm_a_skill_read_confirmed is not None
            and arm_a_skill_read_confirmed not in ARM_A_SKILL_READ_CONFIRMED_VALUES):
        print(f"--record {skill}: --arm-a-skill-read-confirmed "
              f"{arm_a_skill_read_confirmed!r} is not one of "
              f"{sorted(ARM_A_SKILL_READ_CONFIRMED_VALUES)}", file=sys.stderr)
        return 2

    if skip_install_check:
        print(f"--record {skill}: install check SKIPPED -- {skip_install_check}",
              file=sys.stderr)
    else:
        target_dir = claude_skills_dir if claude_skills_dir is not None else CLAUDE_SKILLS_DIR
        install = check_skill_install.check_installed(skill, target_dir, REPO)
        if install.status != check_skill_install.OK:
            print(f"--record {skill}: refusing -- {install.message}", file=sys.stderr)
            print("  (pass --skip-install-check \"<reason>\" to override; "
                  "never silent -- the reason is printed here)", file=sys.stderr)
            return 2

    try:
        comment = load_full_doc(RECORD_PATH)["$comment"]
        skill_names = discover_skill_names(SKILLS_ROOT)
    except RecordError as exc:
        print(f"COULD-NOT-CHECK: {exc}", file=sys.stderr)
        return 2

    resolved_date = date or datetime.date.today().isoformat()
    entry = {
        "verdict": verdict,
        "date": resolved_date,
        "evidence": evidence,
        "source": source,
    }
    if arm_a_skill_read_confirmed is not None:
        entry["arm_a_skill_read_confirmed"] = arm_a_skill_read_confirmed
    append_observation(skill, entry)
    dump_record(regenerate_record(comment, skill_names), RECORD_PATH)
    suffix = (f", arm_a_skill_read_confirmed={arm_a_skill_read_confirmed!r}"
              if arm_a_skill_read_confirmed is not None else "")
    print(f"recorded {skill}: {verdict} ({resolved_date}, {evidence}, "
          f"source={source!r}{suffix})")
    return 0


def do_history(skill: str) -> int:
    """Prints every observation ever recorded for `skill`, oldest first --
    the demonstration that two independent evaluations of the same skill
    both survive and stay distinguishable (agent-b3.md's own bar), not
    just an assertion that the log format allows it."""
    if not (SKILLS_ROOT / skill).is_dir():
        print(f"--history {skill}: no skills/{skill}/ directory", file=sys.stderr)
        return 2
    observations = read_observations(skill)
    if not observations:
        print(f"{skill}: no observations recorded")
        return 0
    for obs in observations:
        print(f"{obs['date']}  {obs['verdict']:<18} source={obs['source']!r}  evidence={obs['evidence']}")
    return 0


def discover_skill_names(skills_root: Path) -> set[str]:
    if not skills_root.is_dir():
        raise RecordError(f"no skills/ directory at {skills_root}")
    return {p.name for p in skills_root.iterdir() if p.is_dir()}


def check(record: dict, skill_names: set[str]) -> list[str]:
    """Returns a list of finding strings; empty means clean."""
    findings = []

    recorded_names = set(record.keys())
    for missing in sorted(skill_names - recorded_names):
        findings.append(f"{missing}: has a skills/ directory but no entry in the record")
    for stale in sorted(recorded_names - skill_names):
        findings.append(f"{stale}: has a record entry but no skills/ directory -- stale")

    for name in sorted(recorded_names & skill_names):
        entry = record[name]
        if not isinstance(entry, dict):
            findings.append(f"{name}: entry is not an object")
            continue

        verdict = entry.get("verdict")
        date = entry.get("date")
        evidence = entry.get("evidence")

        if verdict not in VERDICTS:
            findings.append(f"{name}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
            continue

        if verdict == "unevaluated":
            if date is not None or evidence is not None:
                findings.append(
                    f"{name}: verdict is unevaluated but date/evidence is set "
                    f"(date={date!r}, evidence={evidence!r}) -- "
                    "unevaluated must mean no eval has run at all"
                )
            continue

        # Anything other than unevaluated is a claim an eval actually ran --
        # date and evidence are both load-bearing, not decoration, the same
        # "absence is a typed value" rule this collection uses everywhere
        # else (AGENTS.md).
        if not date:
            findings.append(f"{name}: verdict is {verdict!r} but date is not set")
        if not evidence:
            findings.append(f"{name}: verdict is {verdict!r} but evidence is not set")
        elif not (REPO / evidence).is_file():
            findings.append(f"{name}: evidence path {evidence!r} does not exist in this repo")

    return findings


def find_log_drift(record: dict, skill_names: set[str]) -> list[str]:
    """Catches the exact failure agent-b3.md's PR comment measured live on
    PR #245: a git merge can leave state/eval-status.json's TEXT looking
    correct (because the merge happened to land in a region neither side
    touched) while the skill's own state/eval-log/<skill>.jsonl -- the
    actual source of truth this record is regenerated from -- was never
    updated to match. GitHub reported that PR MERGEABLE; nothing in
    check() caught the drift, because check() only validates the record
    against ITSELF (internally consistent) and against skills/ (every
    skill has an entry), never against the logs it is supposed to be
    GENERATED from. This closes that gap: for every skill, the record's
    own verdict/date/evidence must equal that skill's log's own latest
    observation, exactly. A skill whose record claims a real verdict but
    whose log has zero observations is the specific shape the #245
    incident took (regenerate_record() would silently produce
    "unevaluated" the next time anyone actually ran it); a skill whose
    record and log both have data but DISAGREE is the more general form
    of the same defect.

    Deliberately a SEPARATE function from check(), not folded into it:
    check()'s own test suite (TestCheck) exercises it against synthetic
    records for skill names that do not exist in the real
    state/eval-log/ -- folding a hard dependency on the real log directory
    into check() itself would make every one of those tests fail for a
    reason unrelated to what they test. main()'s default (no-flag) path
    calls both, against the real record and the real logs."""
    findings = []
    for name in sorted(skill_names):
        entry = record.get(name)
        if not isinstance(entry, dict):
            continue  # already flagged above (missing entry / not an object)
        verdict, date, evidence = entry.get("verdict"), entry.get("date"), entry.get("evidence")
        latest = latest_observation(read_observations(name))

        if latest is None:
            if verdict not in (None, "unevaluated"):
                findings.append(
                    f"{name}: record shows verdict {verdict!r} but state/eval-log/{name}.jsonl "
                    "has NO observations -- the generated record does not match its own source "
                    "of truth (a merge likely landed a regenerated file without the log entry "
                    "that backs it -- re-run --record, or regenerate from the logs, before this "
                    "commit ships)"
                )
            continue

        if (verdict, date, evidence) != (latest["verdict"], latest["date"], latest["evidence"]):
            findings.append(
                f"{name}: record shows {verdict!r}/{date!r}/{evidence!r} but "
                f"state/eval-log/{name}.jsonl's own latest observation is "
                f"{latest['verdict']!r}/{latest['date']!r}/{latest['evidence']!r} -- "
                "regenerate state/eval-status.json from the logs"
            )
    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--unevaluated", action="store_true",
                     help="print unevaluated skill names, one per line, sorted, and exit "
                          "(0 if the record itself is readable, regardless of how many "
                          "are unevaluated -- an empty list is a real, checkable answer)")
    ap.add_argument("--summary", action="store_true",
                     help="print a count per verdict and exit")
    ap.add_argument("--record", metavar="SKILL",
                     help="append an observation for SKILL to state/eval-log/SKILL.jsonl "
                          "and regenerate state/eval-status.json -- the only supported "
                          "write path for either, requires --verdict, --evidence and --source")
    ap.add_argument("--verdict", choices=sorted(RECORDABLE_VERDICTS),
                     help="verdict to record (with --record)")
    ap.add_argument("--evidence",
                     help="repo-relative path to the evidence file (with --record)")
    ap.add_argument("--date",
                     help="YYYY-MM-DD to record (with --record; default: today)")
    ap.add_argument("--source",
                     help="which pass/PR produced this observation, e.g. \"PR #244\" "
                          "(with --record; required -- see do_record's own docstring)")
    ap.add_argument("--arm-a-skill-read-confirmed",
                     choices=sorted(ARM_A_SKILL_READ_CONFIRMED_VALUES),
                     help="the arm-A skill_read_confirmed.py tri-state for this observation "
                          "(with --record; optional -- omitting this flag omits the key from "
                          "the appended entry entirely, distinct from recording 'unknown'; "
                          "see do_record's own docstring)")
    ap.add_argument("--history", metavar="SKILL",
                     help="print every observation ever recorded for SKILL, oldest "
                          "first, and exit")
    ap.add_argument("--skip-install-check", metavar="REASON",
                     help="override --record's own install-parity check (with --record) -- "
                          "requires a non-empty REASON, printed to stderr, never silent; "
                          "see check_skill_install.py for what this check verifies and why")
    ap.add_argument("--claude-skills-dir", metavar="DIR",
                     help="check --record's install-parity gate against DIR instead of the "
                          "shared ~/.claude/skills (jonhill90/skills#285) -- lets a verdict be "
                          "recorded from an install visible only to this evaluation (e.g. a "
                          "scratch checkout of a specific commit) without symlinking a "
                          "not-yet-merged skill into the one path every other agent on the "
                          "host reads; omit for the unchanged default behavior")
    args = ap.parse_args(argv)

    if args.record:
        return do_record(args.record, args.verdict, args.evidence, args.date, args.source,
                          skip_install_check=args.skip_install_check,
                          claude_skills_dir=Path(args.claude_skills_dir)
                          if args.claude_skills_dir else None,
                          arm_a_skill_read_confirmed=args.arm_a_skill_read_confirmed)

    if args.history:
        return do_history(args.history)

    try:
        record = load_record(RECORD_PATH)
        skill_names = discover_skill_names(SKILLS_ROOT)
    except RecordError as exc:
        print(f"COULD-NOT-CHECK: {exc}", file=sys.stderr)
        return 2

    if args.unevaluated:
        for name in sorted(n for n, e in record.items()
                            if isinstance(e, dict) and e.get("verdict") == "unevaluated"):
            print(name)
        return 0

    if args.summary:
        counts: dict[str, int] = {}
        for entry in record.values():
            if isinstance(entry, dict):
                counts[entry.get("verdict", "?")] = counts.get(entry.get("verdict", "?"), 0) + 1
        for verdict in sorted(VERDICTS):
            print(f"{verdict}: {counts.get(verdict, 0)}")
        return 0

    findings = check(record, skill_names) + find_log_drift(record, skill_names)
    if not findings:
        print(f"clean: {len(record)} skill(s) recorded, record matches skills/")
        return 0
    for finding in findings:
        print(finding, file=sys.stderr)
    print(f"{len(findings)} finding(s)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
