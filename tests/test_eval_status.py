from __future__ import annotations

import datetime
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "eval_status.py"
SPEC = importlib.util.spec_from_file_location("eval_status", SCRIPT_PATH)
assert SPEC and SPEC.loader
eval_status = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = eval_status
SPEC.loader.exec_module(eval_status)


def unevaluated(name: str) -> dict:
    return {"verdict": "unevaluated", "date": None, "evidence": None}


def evaluated(verdict: str, date: str = "2026-08-22", evidence: str = "README.md") -> dict:
    # README.md always exists in this repo -- a real, checkable evidence
    # path any test can use without writing its own fixture file for it.
    return {"verdict": verdict, "date": date, "evidence": evidence}


class TestCheck(unittest.TestCase):
    def test_clean_record_has_no_findings(self):
        record = {"a": unevaluated("a"), "b": evaluated("keep")}
        findings = eval_status.check(record, {"a", "b"})
        self.assertEqual(findings, [])

    def test_skill_dir_with_no_entry_is_a_finding(self):
        record = {"a": unevaluated("a")}
        findings = eval_status.check(record, {"a", "b"})
        self.assertTrue(any("b" in f and "no entry" in f for f in findings))

    def test_entry_with_no_skill_dir_is_stale(self):
        record = {"a": unevaluated("a"), "ghost": unevaluated("ghost")}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("ghost" in f and "stale" in f for f in findings))

    def test_unknown_verdict_is_a_finding(self):
        record = {"a": {"verdict": "maybe", "date": None, "evidence": None}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("maybe" in f for f in findings))

    def test_unevaluated_with_date_set_is_a_finding(self):
        """unevaluated must mean NO eval ran -- date/evidence set alongside
        it is a contradiction, not a richer record."""
        record = {"a": {"verdict": "unevaluated", "date": "2026-08-22", "evidence": None}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("unevaluated but date/evidence is set" in f for f in findings))

    def test_evaluated_verdict_missing_date_is_a_finding(self):
        record = {"a": {"verdict": "keep", "date": None, "evidence": "README.md"}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("date is not set" in f for f in findings))

    def test_evaluated_verdict_missing_evidence_is_a_finding(self):
        record = {"a": {"verdict": "keep", "date": "2026-08-22", "evidence": None}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("evidence is not set" in f for f in findings))

    def test_evidence_path_that_does_not_exist_is_a_finding(self):
        record = {"a": evaluated("keep", evidence="skills/nonexistent/references/eval-result.md")}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("does not exist in this repo" in f for f in findings))

    def test_could_not_measure_is_a_valid_verdict_not_unevaluated(self):
        """could_not_measure means an eval ran and produced no reliable
        signal -- a different, real state from unevaluated (no eval ran at
        all). Both must be representable and neither should collapse into
        the other."""
        record = {"a": evaluated("could_not_measure")}
        findings = eval_status.check(record, {"a"})
        self.assertEqual(findings, [])


class TestLoadRecordAndDiscovery(unittest.TestCase):
    def test_load_record_missing_file_raises(self):
        with self.assertRaises(eval_status.RecordError):
            eval_status.load_record(Path("/nonexistent/eval-status.json"))

    def test_load_record_malformed_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            with self.assertRaises(eval_status.RecordError):
                eval_status.load_record(path)

    def test_load_record_missing_skills_key_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"nope": {}}), encoding="utf-8")
            with self.assertRaises(eval_status.RecordError):
                eval_status.load_record(path)

    def test_discover_skill_names_missing_dir_raises(self):
        with self.assertRaises(eval_status.RecordError):
            eval_status.discover_skill_names(Path("/nonexistent/skills"))

    def test_discover_skill_names_finds_directories_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real-skill").mkdir()
            (root / "not-a-skill.txt").write_text("x", encoding="utf-8")
            names = eval_status.discover_skill_names(root)
            self.assertEqual(names, {"real-skill"})


class TestMainCLI(unittest.TestCase):
    def test_unevaluated_flag_lists_only_unevaluated_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "a").mkdir(parents=True)
            (root / "skills" / "z").mkdir(parents=True)
            (root / "docs").mkdir()
            record_path = root / "docs" / "eval-status.json"
            record_path.write_text(json.dumps({"skills": {
                "a": {"verdict": "unevaluated", "date": None, "evidence": None},
                "z": {"verdict": "keep", "date": "2026-08-22", "evidence": None},
            }}), encoding="utf-8")

            orig_record, orig_root = eval_status.RECORD_PATH, eval_status.SKILLS_ROOT
            eval_status.RECORD_PATH = record_path
            eval_status.SKILLS_ROOT = root / "skills"
            try:
                import io
                from contextlib import redirect_stdout
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = eval_status.main(["--unevaluated"])
                self.assertEqual(rc, 0)
                self.assertEqual(buf.getvalue().splitlines(), ["a"])
            finally:
                eval_status.RECORD_PATH, eval_status.SKILLS_ROOT = orig_record, orig_root

    def test_real_record_is_clean(self):
        """The actual docs/eval-status.json this repo ships must pass its
        own check -- the property this script exists to guarantee, checked
        against the real file, not only a synthetic fixture."""
        rc = eval_status.main([])
        self.assertEqual(rc, 0)


class TestDumpRecord(unittest.TestCase):
    def test_dump_record_is_a_noop_round_trip_on_the_real_file(self):
        """--record's whole safety case rests on dump_record reproducing
        this file's existing one-line-per-skill shape exactly -- a
        formatter that reindented the whole file on every write would
        turn a one-skill change into an unreviewable whole-file diff.
        Checked against the REAL shipped file, not a synthetic one."""
        doc = eval_status.load_full_doc(eval_status.RECORD_PATH)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "roundtrip.json"
            eval_status.dump_record(doc, out)
            self.assertEqual(out.read_text(encoding="utf-8"),
                              eval_status.RECORD_PATH.read_text(encoding="utf-8"))

    def test_dump_record_sorts_and_updates_one_entry(self):
        doc = {"$comment": "c", "skills": {
            "z": {"verdict": "unevaluated", "date": None, "evidence": None},
            "a": {"verdict": "keep", "date": "2026-01-01", "evidence": "README.md"},
        }}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.json"
            eval_status.dump_record(doc, out)
            text = out.read_text(encoding="utf-8")
            # "a" sorts before "z"
            self.assertLess(text.index('"a":'), text.index('"z":'))
            reloaded = eval_status.load_full_doc(out)
            self.assertEqual(reloaded, doc)


class EvalLogSandboxTestCase(unittest.TestCase):
    """Shared sandbox for every test touching docs/eval-log/ and/or
    --record: a throwaway copy of the record, skills tree and log
    directory, never the real shipped ones, with eval_status's module
    globals restored afterward."""

    def _sandbox(self):
        tmp = Path(tempfile.mkdtemp())
        skill_md = "---\nname: a-skill\n---\nbody\n"
        (tmp / "skills" / "a-skill" / "references").mkdir(parents=True)
        (tmp / "skills" / "a-skill" / "references" / "eval-result.md").write_text(
            "evidence\n", encoding="utf-8")
        (tmp / "skills" / "a-skill" / "SKILL.md").write_text(skill_md, encoding="utf-8")
        (tmp / "docs").mkdir()
        (tmp / "docs" / "eval-status.json").write_text(json.dumps({
            "$comment": "c",
            "skills": {"a-skill": {"verdict": "unevaluated", "date": None, "evidence": None}},
        }), encoding="utf-8")
        # A matching "installed" copy of a-skill -- these tests exercise the
        # REAL install-check pass-through path (a fixture that genuinely
        # matches), never quietly bypass it just because the record itself
        # is sandboxed. See test_record_refuses_when_skill_not_installed/
        # test_record_refuses_when_installed_copy_diverges below for the
        # failure paths, and test_record_skip_install_check_override for the
        # explicit-override path.
        claude_skills = tmp / "claude-skills"
        claude_skills.mkdir(parents=True)
        shutil.copytree(tmp / "skills" / "a-skill", claude_skills / "a-skill")
        return tmp, claude_skills

    def setUp(self):
        self.orig_repo = eval_status.REPO
        self.orig_record = eval_status.RECORD_PATH
        self.orig_skills = eval_status.SKILLS_ROOT
        self.orig_log_dir = eval_status.EVAL_LOG_DIR
        self.orig_claude_skills = eval_status.CLAUDE_SKILLS_DIR
        self.tmp, self.claude_skills = self._sandbox()
        eval_status.REPO = self.tmp
        eval_status.RECORD_PATH = self.tmp / "docs" / "eval-status.json"
        eval_status.SKILLS_ROOT = self.tmp / "skills"
        eval_status.EVAL_LOG_DIR = self.tmp / "docs" / "eval-log"
        eval_status.CLAUDE_SKILLS_DIR = self.claude_skills

    def tearDown(self):
        eval_status.REPO = self.orig_repo
        eval_status.RECORD_PATH = self.orig_record
        eval_status.SKILLS_ROOT = self.orig_skills
        eval_status.EVAL_LOG_DIR = self.orig_log_dir
        eval_status.CLAUDE_SKILLS_DIR = self.orig_claude_skills
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestObservationLog(EvalLogSandboxTestCase):
    """append_observation/read_observations/latest_observation --
    docs/eval-log/'s own read/write primitives, independent of --record's
    CLI-level validation."""

    def test_read_observations_missing_log_is_empty_not_an_error(self):
        self.assertEqual(eval_status.read_observations("a-skill"), [])

    def test_append_then_read_round_trips(self):
        entry = {"verdict": "keep", "date": "2026-08-22", "evidence": "README.md", "source": "PR #244"}
        eval_status.append_observation("a-skill", entry)
        self.assertEqual(eval_status.read_observations("a-skill"), [entry])

    def test_append_never_overwrites_an_earlier_observation(self):
        """The property that makes two independent evaluations of the same
        skill both survive: appending a second observation must leave the
        first one, byte for byte, still readable back."""
        first = {"verdict": "could_not_measure", "date": "2026-08-20", "evidence": "README.md", "source": "PR #239"}
        second = {"verdict": "improve", "date": "2026-08-22", "evidence": "README.md", "source": "PR #244"}
        eval_status.append_observation("a-skill", first)
        eval_status.append_observation("a-skill", second)

        observations = eval_status.read_observations("a-skill")
        self.assertEqual(len(observations), 2)
        self.assertEqual(observations[0], first)
        self.assertEqual(observations[1], second)
        # both distinguishable by source, not merged into one.
        self.assertEqual({o["source"] for o in observations}, {"PR #239", "PR #244"})

    def test_latest_observation_of_empty_is_none(self):
        self.assertIsNone(eval_status.latest_observation([]))

    def test_latest_observation_picks_the_newest_date_not_the_last_line(self):
        """Two passes appending near-simultaneously can land in either
        order once git merges their branches -- latest_observation must
        pick by DATE, not by file position, so this is safe regardless of
        merge order."""
        observations = [
            {"verdict": "improve", "date": "2026-08-22", "evidence": "e", "source": "newer, appended first"},
            {"verdict": "keep", "date": "2026-08-15", "evidence": "e", "source": "older, appended second"},
        ]
        latest = eval_status.latest_observation(observations)
        self.assertEqual(latest["date"], "2026-08-22")

    def test_regenerate_record_uses_latest_per_skill(self):
        eval_status.append_observation("a-skill", {
            "verdict": "could_not_measure", "date": "2026-08-15", "evidence": "README.md", "source": "PR #239"})
        eval_status.append_observation("a-skill", {
            "verdict": "keep", "date": "2026-08-22", "evidence": "README.md", "source": "PR #244"})
        (self.tmp / "skills" / "b-skill").mkdir()

        doc = eval_status.regenerate_record("the comment", {"a-skill", "b-skill"})
        self.assertEqual(doc["$comment"], "the comment")
        self.assertEqual(doc["skills"]["a-skill"], {
            "verdict": "keep", "date": "2026-08-22", "evidence": "README.md"})
        # never evaluated -- unevaluated default, no "source" key leaked
        # from the log shape into the generated record's own schema.
        self.assertEqual(doc["skills"]["b-skill"], {
            "verdict": "unevaluated", "date": None, "evidence": None})
        self.assertNotIn("source", doc["skills"]["a-skill"])


class TestRecordCLI(EvalLogSandboxTestCase):
    """--record is the one supported write path for docs/eval-log/ and,
    through regeneration, docs/eval-status.json (estate-loop/agent-b2.md's
    own rule: "never by hand")."""

    def test_record_writes_a_valid_entry(self):
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #244",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"], {
            "verdict": "keep", "date": "2026-08-22",
            "evidence": "skills/a-skill/references/eval-result.md",
        })
        # the log itself carries the attribution the generated record does not.
        observations = eval_status.read_observations("a-skill")
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["source"], "PR #244")
        # what it just wrote must itself pass this script's own check.
        self.assertEqual(eval_status.main([]), 0)

    def test_record_defaults_date_to_today(self):
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "improve",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--source", "PR #244",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["date"], datetime.date.today().isoformat())

    def test_record_refuses_nonexistent_skill(self):
        rc = eval_status.main([
            "--record", "no-such-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--source", "PR #244",
        ])
        self.assertEqual(rc, 2)
        # nothing written -- the record is untouched.
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertNotIn("no-such-skill", record)

    def test_record_refuses_unevaluated_as_a_verdict_to_record(self):
        """unevaluated is the record's own default for a never-touched
        entry, not something --record should ever be asked to write --
        see do_record's own docstring for why."""
        with self.assertRaises(SystemExit):
            # argparse itself refuses: "unevaluated" is not in --verdict's
            # choices (RECORDABLE_VERDICTS excludes it).
            eval_status.main([
                "--record", "a-skill", "--verdict", "unevaluated",
                "--evidence", "skills/a-skill/references/eval-result.md",
                "--source", "PR #244",
            ])

    def test_record_refuses_missing_evidence_file(self):
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/does-not-exist.md",
            "--source", "PR #244",
        ])
        self.assertEqual(rc, 2)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["verdict"], "unevaluated")

    def test_record_refuses_missing_source(self):
        """source is the one field this shape adds over the old
        single-record entry -- never optional, since an unattributed
        observation is exactly the ambiguity this fix exists to remove."""
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(eval_status.read_observations("a-skill"), [])

    def test_record_requires_verdict(self):
        rc = eval_status.main([
            "--record", "a-skill",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--source", "PR #244",
        ])
        self.assertEqual(rc, 2)

    def test_record_preserves_other_skills_own_logs(self):
        # b-skill already has a real observation of its own, recorded the
        # same way -- proves recording "a-skill" doesn't touch it.
        (self.tmp / "skills" / "b-skill").mkdir()
        eval_status.append_observation("b-skill", {
            "verdict": "keep", "date": "2020-01-01", "evidence": "README.md", "source": "PR #1"})
        eval_status.dump_record(
            eval_status.regenerate_record("c", {"a-skill", "b-skill"}), eval_status.RECORD_PATH)

        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "drop",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #244",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["b-skill"]["verdict"], "keep")
        self.assertEqual(record["a-skill"]["verdict"], "drop")
        # b-skill's own log is untouched -- still exactly its one entry.
        self.assertEqual(len(eval_status.read_observations("b-skill")), 1)

    def test_record_twice_on_the_same_skill_keeps_both_observations(self):
        """The requirement this whole fix exists for: two evaluations of
        the same skill both survive and stay attributed to their pass,
        rather than the second silently overwriting the first."""
        rc1 = eval_status.main([
            "--record", "a-skill", "--verdict", "could_not_measure",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-20", "--source", "PR #239",
        ])
        rc2 = eval_status.main([
            "--record", "a-skill", "--verdict", "improve",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #244",
        ])
        self.assertEqual((rc1, rc2), (0, 0))

        observations = eval_status.read_observations("a-skill")
        self.assertEqual(len(observations), 2)
        self.assertEqual([o["source"] for o in observations], ["PR #239", "PR #244"])
        self.assertEqual([o["verdict"] for o in observations], ["could_not_measure", "improve"])

        # the generated record shows the LATEST -- current-status readers
        # (check(), --summary, --unevaluated) see one verdict per skill,
        # unchanged contract.
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["verdict"], "improve")

    def test_record_refuses_when_skill_not_installed(self):
        """#230's own mechanical check: a skill missing from the shared
        skills path must block --record, not just get a note in a doc a
        human can skip. --source is present and valid here so the refusal
        can only be coming from the install check, not the (separate,
        already-covered) missing-source path."""
        shutil.rmtree(self.claude_skills / "a-skill")

        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--source", "PR #244",
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(eval_status.read_observations("a-skill"), [])
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["verdict"], "unevaluated")

    def test_record_refuses_when_installed_copy_diverges(self):
        """A present-but-drifted installed copy is a different failure than
        MISSING and must be named as such, not merged into one message."""
        (self.claude_skills / "a-skill" / "SKILL.md").write_text(
            "---\nname: a-skill\n---\ndrifted body\n", encoding="utf-8")

        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--source", "PR #244",
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(eval_status.read_observations("a-skill"), [])
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["verdict"], "unevaluated")

    def test_record_claude_skills_dir_override_redirects_the_check(self):
        """jonhill90/skills#285: --claude-skills-dir must actually redirect
        the install-parity gate, not merely be accepted and ignored.
        Mutation, both directions, in one test: a scratch install the
        DEFAULT claude-skills dir does not have at all is accepted when
        pointed at directly; a scratch install missing the skill is
        refused even though the DEFAULT dir (self.claude_skills, from
        _sandbox) has a perfectly good matching copy the whole time. If
        the override were ignored and --record silently fell back to
        CLAUDE_SKILLS_DIR, both assertions below would still pass by
        accident -- the second one is what rules that out."""
        scratch = self.tmp / "scratch-install"
        scratch.mkdir()
        shutil.copytree(self.tmp / "skills" / "a-skill", scratch / "a-skill")

        rc_accept = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-28", "--source", "PR #285-test",
            "--claude-skills-dir", str(scratch),
        ])
        self.assertEqual(rc_accept, 0,
                          "a scratch install that genuinely matches must be accepted "
                          "when --claude-skills-dir points directly at it")

        empty_scratch = self.tmp / "empty-scratch"
        empty_scratch.mkdir()
        rc_reject = eval_status.main([
            "--record", "a-skill", "--verdict", "improve",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-28", "--source", "PR #285-test-2",
            "--claude-skills-dir", str(empty_scratch),
        ])
        self.assertEqual(rc_reject, 2,
                          "must refuse against a scratch dir missing the skill even "
                          "though the DEFAULT claude-skills dir (self.claude_skills) "
                          "has a matching copy the whole time -- proves the override "
                          "actually redirected the check rather than being ignored")
        # the accepted call recorded one observation; the refused call added none.
        observations = eval_status.read_observations("a-skill")
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["source"], "PR #285-test")

    def test_record_without_override_still_checks_the_default_dir(self):
        """Regression: omitting --claude-skills-dir must keep checking
        CLAUDE_SKILLS_DIR exactly as before this flag existed -- the
        'do not break the installed path' requirement, checked directly
        against do_record's own None-default branch."""
        shutil.rmtree(self.claude_skills / "a-skill")
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--source", "PR #244",
        ])
        self.assertEqual(rc, 2)
        self.assertEqual(eval_status.read_observations("a-skill"), [])

    def test_record_skip_install_check_override(self):
        """--skip-install-check is the loud, named escape hatch -- it must
        still let a legitimate --record through even when the sandboxed
        installed copy doesn't match (there is no real ~/.claude/skills
        entry for this test's own fake skill on CI machines)."""
        shutil.rmtree(self.claude_skills / "a-skill")

        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #244",
            "--skip-install-check", "sandboxed test fixture, not a real install",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["verdict"], "keep")
        observations = eval_status.read_observations("a-skill")
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["source"], "PR #244")

    def test_record_writes_arm_a_skill_read_confirmed_true_false_unknown(self):
        """jonhill90/skills#300: the sanctioned writer must be able to
        attach the tri-state, and each of the three values must survive
        into the appended entry exactly -- the property #299 established
        by hand must now also hold through --record."""
        for i, value in enumerate(("true", "false", "unknown")):
            rc = eval_status.main([
                "--record", "a-skill", "--verdict", "could_not_measure",
                "--evidence", "skills/a-skill/references/eval-result.md",
                "--date", f"2026-08-2{i}", "--source", f"PR #300-{value}",
                "--arm-a-skill-read-confirmed", value,
            ])
            self.assertEqual(rc, 0)

        observations = eval_status.read_observations("a-skill")
        self.assertEqual(len(observations), 3)
        self.assertEqual(
            [o["arm_a_skill_read_confirmed"] for o in observations],
            ["true", "false", "unknown"],
        )

    def test_record_without_the_flag_omits_the_key_entirely(self):
        """The design decision this PR makes explicit: an unrecorded field
        ('this pass did not measure it') must stay distinguishable from a
        recorded 'unknown' ('this pass measured it and could not tell').
        Defaulting to 'unknown', or to 'false', would each collapse that
        distinction -- this proves the chosen behaviour: the key is simply
        absent from the entry, not present with either default value."""
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #244",
        ])
        self.assertEqual(rc, 0)
        observations = eval_status.read_observations("a-skill")
        self.assertEqual(len(observations), 1)
        self.assertNotIn("arm_a_skill_read_confirmed", observations[0])

    def test_record_rejects_a_bad_arm_a_skill_read_confirmed_value(self):
        """A bad value must be refused, never silently written -- the same
        bar --verdict and --evidence already hold to."""
        with self.assertRaises(SystemExit):
            # argparse itself refuses: "maybe" is not in the flag's choices.
            eval_status.main([
                "--record", "a-skill", "--verdict", "keep",
                "--evidence", "skills/a-skill/references/eval-result.md",
                "--source", "PR #244",
                "--arm-a-skill-read-confirmed", "maybe",
            ])
        self.assertEqual(eval_status.read_observations("a-skill"), [])

    def test_record_arm_a_skill_read_confirmed_does_not_reach_the_generated_record(self):
        """docs/eval-status.json keeps its exact pre-existing shape (this
        module's own top-of-file doc comment) -- the tri-state lives only
        in the log, the same way 'source' already does, never in the
        regenerated per-skill entry."""
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "could_not_measure",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #244",
            "--arm-a-skill-read-confirmed", "unknown",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertNotIn("arm_a_skill_read_confirmed", record["a-skill"])
        self.assertEqual(record["a-skill"], {
            "verdict": "could_not_measure", "date": "2026-08-22",
            "evidence": "skills/a-skill/references/eval-result.md",
        })


class TestHistoryCLI(EvalLogSandboxTestCase):
    def test_history_nonexistent_skill(self):
        rc = eval_status.main(["--history", "no-such-skill"])
        self.assertEqual(rc, 2)

    def test_history_never_evaluated_skill(self):
        rc = eval_status.main(["--history", "a-skill"])
        self.assertEqual(rc, 0)

    def test_history_prints_every_observation(self):
        eval_status.main([
            "--record", "a-skill", "--verdict", "could_not_measure",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-20", "--source", "PR #239",
        ])
        eval_status.main([
            "--record", "a-skill", "--verdict", "improve",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #244",
        ])
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = eval_status.main(["--history", "a-skill"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("PR #239", out)
        self.assertIn("PR #244", out)
        self.assertIn("could_not_measure", out)
        self.assertIn("improve", out)


class TestLogDrift(EvalLogSandboxTestCase):
    """find_log_drift -- the guard agent-b3.md's PR comment on #245
    required: PR #245's own migration seeded docs/eval-log/ from a
    pre-#243 copy of docs/eval-status.json, so tdd.jsonl was never
    created. GitHub still reported the PR MERGEABLE, because the git
    merge happened to land the correct TEXT in docs/eval-status.json
    without the log entry that is supposed to back it -- nothing existing
    (check() alone) compared the generated record against its own source
    of truth. These tests reproduce that exact shape against a sandbox,
    not the real tdd -- the real-tdd mutation check (empty the real file,
    confirm scripts/eval_status.py fails; restore it, confirm clean) is
    run once, live, and reported in the PR body, not re-run on every test
    invocation against the shipped file."""

    def _record_a_skill(self):
        eval_status.main([
            "--record", "a-skill", "--verdict", "could_not_measure",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22", "--source", "PR #239",
        ])

    def test_clean_when_record_matches_the_log(self):
        self._record_a_skill()
        record = eval_status.load_record(eval_status.RECORD_PATH)
        findings = eval_status.find_log_drift(record, {"a-skill"})
        self.assertEqual(findings, [])

    def test_flags_a_real_verdict_backed_by_an_empty_log(self):
        """The exact #245 shape: record() then wipe the log underneath
        it, simulating a merge that regenerated the file from a stale
        log."""
        self._record_a_skill()
        (self.tmp / "docs" / "eval-log" / "a-skill.jsonl").write_text("", encoding="utf-8")

        record = eval_status.load_record(eval_status.RECORD_PATH)
        findings = eval_status.find_log_drift(record, {"a-skill"})
        self.assertEqual(len(findings), 1)
        self.assertIn("a-skill", findings[0])
        self.assertIn("NO observations", findings[0])

    def test_flags_a_record_that_disagrees_with_the_logs_latest(self):
        """The more general form: both have data, but they disagree --
        not just the empty-log case."""
        self._record_a_skill()
        doc = eval_status.load_full_doc(eval_status.RECORD_PATH)
        doc["skills"]["a-skill"]["verdict"] = "improve"  # hand-corrupt the record only
        eval_status.dump_record(doc, eval_status.RECORD_PATH)

        record = eval_status.load_record(eval_status.RECORD_PATH)
        findings = eval_status.find_log_drift(record, {"a-skill"})
        self.assertEqual(len(findings), 1)
        self.assertIn("a-skill", findings[0])

    def test_main_default_path_fails_on_drift_and_passes_once_reseeded(self):
        """End to end, through scripts/eval_status.py's own default
        (no-flag) path -- the exact command the PR's own verification
        bar names ("scripts/eval_status.py reports clean"). Mutation
        checked in both directions in the SAME test, not asserted only
        one way."""
        self._record_a_skill()
        self.assertEqual(eval_status.main([]), 0)

        log_path = self.tmp / "docs" / "eval-log" / "a-skill.jsonl"
        original = log_path.read_text(encoding="utf-8")
        log_path.write_text("", encoding="utf-8")
        self.assertEqual(eval_status.main([]), 1, "guard did not fire with the log emptied")

        log_path.write_text(original, encoding="utf-8")
        self.assertEqual(eval_status.main([]), 0, "guard did not clear once the log was restored")


class TestConflictDemonstration(unittest.TestCase):
    """agent-b3.md's own bar: demonstrate the conflict is gone by
    construction, not by argument. Runs a REAL git init/commit/branch/merge
    sequence -- not a mock, not an assertion that it "should" work.
    Skips if git is not on PATH rather than failing an environment that
    lacks it."""

    def setUp(self):
        self.git = shutil.which("git")
        if not self.git:
            self.skipTest("git not on PATH")

    def _env(self):
        # CI runners have no global git identity configured at all (unlike
        # a dev machine's own ~/.gitconfig) -- every git subprocess this
        # class runs, including the merge commits, needs this env or the
        # commit/merge itself fails with "empty ident name" before ever
        # reaching the merge=union behaviour under test. Found by CI
        # itself failing on the two `subprocess.run(...)` merge calls
        # below, which had not been routed through this env (only _run
        # had it) -- fixed by giving both the same one source of truth.
        return {**os.environ,
                "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@test",
                "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@test"}

    def _run(self, repo, *args):
        result = subprocess.run(
            [self.git, *args], cwd=repo, capture_output=True, text=True, env=self._env(),
        )
        self.assertEqual(result.returncode, 0, f"git {args}: {result.stderr}")
        return result.stdout

    def _init_repo(self):
        """A throwaway repo carrying the REAL shipped .gitattributes (not
        a re-typed copy that could silently drift from what actually
        ships) -- the union merge driver it declares is what this whole
        test class exists to prove is load-bearing, not decoration."""
        repo = Path(tempfile.mkdtemp())
        self._run(repo, "init", "-q", "-b", "main")
        (repo / "state" / "eval-log").mkdir(parents=True)
        real_gitattributes = REPO_ROOT / ".gitattributes"
        (repo / ".gitattributes").write_text(
            real_gitattributes.read_text(encoding="utf-8"), encoding="utf-8")
        self._run(repo, "add", "-A")
        self._run(repo, "commit", "-q", "-m", "base: .gitattributes")
        return repo

    def _write_observation(self, repo, skill, entry):
        # git does not track empty directories -- a checkout onto a branch
        # that never committed anything under docs/eval-log/ can leave it
        # missing on disk, so this recreates it every time rather than
        # trusting _init_repo's own mkdir to have survived a branch switch.
        path = repo / "state" / "eval-log" / f"{skill}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    def test_two_disjoint_skills_merge_without_conflict(self):
        """Lane A evaluates skill-x, lane B evaluates skill-y, on branches
        off the same base -- disjoint files, must merge with zero
        conflict, exactly the collision the old single
        docs/eval-status.json produced three times in one night
        (#239/#240/#243)."""
        repo = self._init_repo()
        self.addCleanup(shutil.rmtree, repo, ignore_errors=True)
        base_x = repo / "state" / "eval-log" / "skill-x.jsonl"
        base_y = repo / "state" / "eval-log" / "skill-y.jsonl"

        self._run(repo, "checkout", "-q", "-b", "lane-a")
        self._write_observation(repo, "skill-x", {
            "verdict": "keep", "date": "2026-08-22", "evidence": "e", "source": "PR #239 (lane A)"})
        self._run(repo, "add", "-A")
        self._run(repo, "commit", "-q", "-m", "lane A: skill-x evaluated")

        self._run(repo, "checkout", "-q", "main")
        self._run(repo, "checkout", "-q", "-b", "lane-b")
        self._write_observation(repo, "skill-y", {
            "verdict": "improve", "date": "2026-08-22", "evidence": "e", "source": "PR #240 (lane B)"})
        self._run(repo, "add", "-A")
        self._run(repo, "commit", "-q", "-m", "lane B: skill-y evaluated")

        self._run(repo, "checkout", "-q", "main")
        self._run(repo, "merge", "-q", "--no-edit", "lane-a")
        result = subprocess.run(
            [self.git, "merge", "--no-edit", "lane-b"], cwd=repo, capture_output=True, text=True, env=self._env())
        self.assertEqual(result.returncode, 0,
                          f"merging lane-b after lane-a FAILED -- the exact collision this fix "
                          f"exists to prevent:\n{result.stderr}")

        x_obs = [json.loads(line) for line in base_x.read_text(encoding="utf-8").splitlines() if line]
        y_obs = [json.loads(line) for line in base_y.read_text(encoding="utf-8").splitlines() if line]
        self.assertEqual(x_obs[-1]["source"], "PR #239 (lane A)")
        self.assertEqual(y_obs[-1]["source"], "PR #240 (lane B)")

    def test_two_evaluations_of_the_same_skill_both_survive_a_merge(self):
        """Lane A and lane B BOTH evaluate skill-z independently, off the
        same base -- both observations must survive the merge, distinct
        and attributed, not one silently discarding the other.

        FOUND, NOT ASSUMED, while writing this test: git's DEFAULT text
        merge does NOT resolve two pure appends to the end of the same
        file automatically -- both sides' hunks anchor on the same
        trailing context line, so git reports a real content conflict
        even though the two changes are logically disjoint (verified by
        running exactly this sequence with .gitattributes deleted: exit
        1, `<<<<<<< HEAD` markers). Reported rather than worked around by
        loosening this test (agent-b3.md's own bar) -- the actual fix is
        `merge=union` in .gitattributes (docs/eval-log/*.jsonl), git's own
        built-in driver for "keep every line either side added." This
        test exercises the REAL shipped .gitattributes (via _init_repo)
        and must see zero conflict, both observations present, in commit
        order."""
        repo = self._init_repo()
        self.addCleanup(shutil.rmtree, repo, ignore_errors=True)
        log = repo / "state" / "eval-log" / "skill-z.jsonl"

        self._run(repo, "checkout", "-q", "-b", "lane-a")
        self._write_observation(repo, "skill-z", {
            "verdict": "could_not_measure", "date": "2026-08-20", "evidence": "e", "source": "PR #239 (lane A)"})
        self._run(repo, "add", "-A")
        self._run(repo, "commit", "-q", "-m", "lane A: skill-z, first independent evaluation")

        self._run(repo, "checkout", "-q", "main")
        self._run(repo, "checkout", "-q", "-b", "lane-b")
        self._write_observation(repo, "skill-z", {
            "verdict": "improve", "date": "2026-08-22", "evidence": "e", "source": "PR #244 (lane B)"})
        self._run(repo, "add", "-A")
        self._run(repo, "commit", "-q", "-m", "lane B: skill-z, second independent evaluation")

        self._run(repo, "checkout", "-q", "main")
        self._run(repo, "merge", "-q", "--no-edit", "lane-a")
        result = subprocess.run(
            [self.git, "merge", "--no-edit", "lane-b"], cwd=repo, capture_output=True, text=True, env=self._env())
        self.assertEqual(
            result.returncode, 0,
            f"same-skill concurrent append did NOT merge cleanly -- the .gitattributes "
            f"merge=union driver did not take effect:\n{result.stderr}",
        )

        observations = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line]
        sources = [o["source"] for o in observations]
        self.assertEqual(
            sources, ["PR #239 (lane A)", "PR #244 (lane B)"],
            f"expected BOTH independent evaluations to survive the merge, in order, got: {observations}",
        )


if __name__ == "__main__":
    unittest.main()
