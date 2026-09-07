"""jonhill90/skills#269 review (estate:2): prove skill_read_confirmed by
construction, in both mutation directions, not by reading the function and
trusting it -- this repo's own standing convention for a scorer-adjacent
utility (see test_eval_status.py's own header for the same import shape).

jonhill90/skills#273 review (estate:4): the function is tri-state
(True/False/None), not boolean -- an unparseable/empty/truncated/wrong-file
transcript must return None ("could not determine"), never False, or a
could-not-measure input silently records as a confirmed negative. Both the
original mutation pair and the new tri-state pair are covered below."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "skill_read_confirmed.py"
SPEC = importlib.util.spec_from_file_location("skill_read_confirmed", SCRIPT_PATH)
assert SPEC and SPEC.loader
skill_read_confirmed_mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = skill_read_confirmed_mod
SPEC.loader.exec_module(skill_read_confirmed_mod)
skill_read_confirmed = skill_read_confirmed_mod.skill_read_confirmed


def _assistant_turn(*blocks: dict) -> dict:
    """One JSONL line shaped like a real Claude Code transcript's assistant
    turn -- verified against a live ~/.claude/projects/*.jsonl transcript
    before writing this fixture, not assumed: type "assistant" at the top
    level, message.content a list of blocks."""
    return {"type": "assistant", "message": {"role": "assistant", "content": list(blocks)}}


def _read_block(file_path: str) -> dict:
    return {"type": "tool_use", "name": "Read", "input": {"file_path": file_path}}


def _write_transcript(tmpdir: Path, name: str, lines: list[dict]) -> Path:
    path = tmpdir / name
    path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
    return path


class SkillReadConfirmedTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    # --- the two mandatory mutation-check directions (True/False) ------

    def test_confirmed_true_when_the_read_genuinely_happened(self):
        transcript = _write_transcript(
            self.tmpdir,
            "with-read.jsonl",
            [
                _assistant_turn(
                    {"type": "text", "text": "Let me check the skill first."},
                    _read_block("/home/agent/work/skills/github-cli/SKILL.md"),
                ),
            ],
        )
        self.assertIs(
            skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"),
            True,
            "a transcript with a real Read of the exact skill path must confirm True",
        )

    def test_confirmed_false_when_the_read_never_happened(self):
        # Same shape, same skill, but Arm A went straight to the task --
        # exactly the silent-wiring-failure case this function exists to
        # catch, indistinguishable from a genuine null in prose or in
        # manifest.json's own self-reported actions_log. A REAL, legible
        # transcript with real events -- this must be False, not None.
        transcript = _write_transcript(
            self.tmpdir,
            "without-read.jsonl",
            [
                _assistant_turn(
                    {"type": "text", "text": "I'll just run gh run watch directly."},
                    {"type": "tool_use", "name": "Bash", "input": {"command": "gh run watch 9001 --exit-status"}},
                ),
            ],
        )
        self.assertIs(
            skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"),
            False,
            "a legible transcript with no Read of the skill path must confirm False, not None",
        )

    # --- the new tri-state mutation-check directions (skills#273) ------

    def test_a_genuinely_empty_transcript_returns_unknown_not_false(self):
        """The exact defect skills#273 found: this used to return False
        here, byte-for-byte identical to a real negative result."""
        path = self.tmpdir / "empty.jsonl"
        path.write_text("", encoding="utf-8")
        self.assertIsNone(
            skill_read_confirmed(path, "skills/linear/SKILL.md"),
            "an empty transcript carries no evidence either way -- must be None, never False",
        )

    def test_a_legible_transcript_with_no_read_is_still_false_not_unknown(self):
        """The mutation-check DIRECTION that proves the fix didn't just
        widen everything to None: a real, well-formed transcript that
        genuinely shows no Read must still resolve to False. (Same
        fixture as test_confirmed_false_when_the_read_never_happened,
        asserted again here explicitly alongside the None cases so the
        two directions of the NEW behaviour sit next to each other.)"""
        transcript = _write_transcript(
            self.tmpdir,
            "legible-no-read.jsonl",
            [_assistant_turn({"type": "text", "text": "Proceeding without reading anything."})],
        )
        self.assertIs(skill_read_confirmed(transcript, "skills/linear/SKILL.md"), False)

    def test_unparseable_json_throughout_returns_unknown(self):
        path = self.tmpdir / "garbage.jsonl"
        path.write_text("not json\nalso not json\n{{{broken\n", encoding="utf-8")
        self.assertIsNone(skill_read_confirmed(path, "skills/linear/SKILL.md"))

    def test_wrong_file_shape_returns_unknown_not_false(self):
        """The reviewer's own named scenario: an operator points this at
        $STUB_LOG (or any file that is valid JSON lines but not a Claude
        Code transcript) by mistake. Valid JSON, zero recognisable
        assistant/tool_use events -- must be None, not a confident False."""
        path = self.tmpdir / "stub-log-shaped.jsonl"
        # Plausible $STUB_LOG shape: a flat list of CLI invocations, not a
        # transcript event envelope at all.
        lines = [
            {"argv": ["gh", "run", "watch", "9001", "--exit-status"]},
            {"argv": ["gh", "run", "view", "9001"]},
        ]
        path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
        self.assertIsNone(
            skill_read_confirmed(path, "skills/github-cli/SKILL.md"),
            "a wrong-shaped file (e.g. $STUB_LOG) must return None, never a confident False",
        )

    def test_truncated_transcript_with_no_complete_event_returns_unknown(self):
        path = self.tmpdir / "truncated.jsonl"
        # A capture cut off mid-write -- half a JSON object, no valid line.
        path.write_text('{"type": "assistant", "message": {"content": [{"typ', encoding="utf-8")
        self.assertIsNone(skill_read_confirmed(path, "skills/linear/SKILL.md"))

    # --- must be a REAL Read tool_use, never a stand-in ----------------

    def test_a_bash_cat_of_the_same_file_does_not_count(self):
        """The whole point is refusing self-report-shaped evidence -- a
        Bash command that happens to cat the SKILL.md text is not the
        mechanical signal this function is built to trust, even though a
        naive substring search over the transcript would find the path."""
        transcript = _write_transcript(
            self.tmpdir,
            "bash-cat.jsonl",
            [
                _assistant_turn(
                    _read_block("skills/github-cli/SKILL.md"),
                )
            ],
        )
        # Sanity: the Read-tool version of this exact path DOES confirm --
        # proves the negative case below isn't failing for some unrelated
        # reason (e.g. a broken fixture).
        self.assertIs(skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"), True)

        bash_transcript = _write_transcript(
            self.tmpdir,
            "bash-cat-2.jsonl",
            [
                _assistant_turn(
                    {"type": "tool_use", "name": "Bash", "input": {"command": "cat skills/github-cli/SKILL.md"}},
                )
            ],
        )
        self.assertIs(
            skill_read_confirmed(bash_transcript, "skills/github-cli/SKILL.md"),
            False,
            "a Bash cat of the skill file must not count as a confirmed Read -- and this IS a legible "
            "transcript (a real tool_use event was seen), so the answer is False, not None",
        )

    def test_actions_log_style_self_report_is_never_consulted(self):
        """manifest.json's own actions_log is explicitly untrusted by this
        harness (docs/historical/eval-harness-findings.md) -- confirm this function
        doesn't accidentally read anything shaped like it out of the
        transcript itself."""
        transcript = _write_transcript(
            self.tmpdir,
            "self-report.jsonl",
            [
                _assistant_turn(
                    {"type": "text", "text": "actions_log: [\"read skills/github-cli/SKILL.md\"]"},
                )
            ],
        )
        self.assertIs(skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"), False)

    # --- path-matching, both forms named in the brief -------------------

    def test_relative_skill_path_matches_an_absolute_transcript_path(self):
        transcript = _write_transcript(
            self.tmpdir,
            "abs.jsonl",
            [_assistant_turn(_read_block("/private/var/tmp/eval-run-42/skills/linear/SKILL.md"))],
        )
        self.assertIs(skill_read_confirmed(transcript, "skills/linear/SKILL.md"), True)

    def test_absolute_skill_path_requires_exact_match(self):
        transcript = _write_transcript(
            self.tmpdir,
            "abs-exact.jsonl",
            [_assistant_turn(_read_block("/private/var/tmp/eval-run-42/skills/linear/SKILL.md"))],
        )
        self.assertIs(
            skill_read_confirmed(transcript, "/private/var/tmp/eval-run-42/skills/linear/SKILL.md"), True
        )
        self.assertIs(
            skill_read_confirmed(transcript, "/somewhere/else/skills/linear/SKILL.md"),
            False,
            "an absolute query path must match exactly, not by suffix",
        )

    def test_suffix_match_respects_a_path_boundary(self):
        """'skills/linear/SKILL.md' must not match
        'myskills/linear/SKILL.md' just because one string ends with the
        other -- the boundary must be a real path separator."""
        transcript = _write_transcript(
            self.tmpdir,
            "boundary.jsonl",
            [_assistant_turn(_read_block("/work/myskills/linear/SKILL.md"))],
        )
        self.assertIs(skill_read_confirmed(transcript, "skills/linear/SKILL.md"), False)

    def test_read_of_a_different_skill_does_not_confirm(self):
        transcript = _write_transcript(
            self.tmpdir,
            "wrong-skill.jsonl",
            [_assistant_turn(_read_block("/work/skills/obsidian/SKILL.md"))],
        )
        self.assertIs(skill_read_confirmed(transcript, "skills/linear/SKILL.md"), False)

    # --- fail-closed behaviour -------------------------------------------

    def test_missing_transcript_returns_unknown(self):
        self.assertIsNone(
            skill_read_confirmed(self.tmpdir / "does-not-exist.jsonl", "skills/linear/SKILL.md")
        )

    def test_malformed_lines_are_skipped_not_fatal(self):
        path = self.tmpdir / "malformed.jsonl"
        path.write_text(
            "not json at all\n"
            + json.dumps(_assistant_turn(_read_block("/work/skills/linear/SKILL.md"))),
            encoding="utf-8",
        )
        self.assertIs(skill_read_confirmed(path, "skills/linear/SKILL.md"), True)


class CLITests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cli_exit_codes(self):
        import subprocess

        confirmed = _write_transcript(
            self.tmpdir, "confirmed.jsonl", [_assistant_turn(_read_block("/w/skills/linear/SKILL.md"))]
        )
        rc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(confirmed), "skills/linear/SKILL.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(rc.returncode, 0)
        self.assertEqual(rc.stdout.strip(), "true")

        not_confirmed = _write_transcript(
            self.tmpdir, "not-confirmed.jsonl", [_assistant_turn({"type": "text", "text": "no reads here"})]
        )
        rc2 = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(not_confirmed), "skills/linear/SKILL.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(rc2.returncode, 1)
        self.assertEqual(rc2.stdout.strip(), "false")

        empty = self.tmpdir / "empty-for-cli.jsonl"
        empty.write_text("", encoding="utf-8")
        rc3 = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(empty), "skills/linear/SKILL.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(rc3.returncode, 2, "an empty transcript must exit 2 (unknown), not 1 (false)")
        self.assertEqual(rc3.stdout.strip(), "unknown")

        rc4 = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(self.tmpdir / "nope.jsonl"), "skills/linear/SKILL.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(rc4.returncode, 3, "a missing file is a usage-level error, distinct from exit 2")


if __name__ == "__main__":
    unittest.main()
