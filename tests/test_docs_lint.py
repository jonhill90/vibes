"""Tests for scripts/docs_lint.py. Every fixture is a throwaway tempdir
git repo -- this suite never touches this repo's own docs/ tree."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).with_name("..") / "scripts" / "docs_lint.py"
P = (Path(__file__).parent.parent / "scripts" / "docs_lint.py").resolve()
spec = importlib.util.spec_from_file_location("docs_lint", P)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)


def git_add(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)


class UnclassifiedRootFiles(unittest.TestCase):
    def test_classified_tree_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs" / "canonical").mkdir(parents=True)
            (root / "docs" / "canonical" / "a.md").write_text("A\n")
            self.assertEqual(m.check_unclassified_root_files(root), [])

    def test_loose_root_file_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "docs" / "loose.md").write_text("stray\n")
            violations = m.check_unclassified_root_files(root)
            self.assertEqual(len(violations), 1)
            self.assertIn("docs/loose.md", violations[0])

    def test_allowlisted_root_file_is_not_a_violation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "docs" / "README.md").write_text("index\n")
            self.assertEqual(m.check_unclassified_root_files(root), [])

    def test_unrecognized_subdirectory_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs" / "eval-log").mkdir(parents=True)
            violations = m.check_unclassified_root_files(root)
            self.assertEqual(len(violations), 1)
            self.assertIn("docs/eval-log/", violations[0])

    def test_tombstone_stub_is_not_a_violation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "docs" / "moved.md").write_text(
                m.TOMBSTONE_MARKER + "\n\nMoved to docs/historical/moved.md.\n")
            self.assertEqual(m.check_unclassified_root_files(root), [])

    def test_symlink_at_root_is_not_a_rule_1_violation(self):
        # Rule 1 defers to rule 2 for symlink legitimacy -- it only
        # confirms a symlink isn't flagged as plain unclassified content.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "state").mkdir()
            (root / "state" / "real.json").write_text("{}")
            (root / "docs" / "real.json").symlink_to("../state/real.json")
            self.assertEqual(m.check_unclassified_root_files(root), [])


class NoStateFilesInDocs(unittest.TestCase):
    def test_clean_tree_has_no_violations(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs" / "canonical").mkdir(parents=True)
            (root / "docs" / "canonical" / "a.md").write_text("A\n")
            self.assertEqual(m.check_no_state_files_in_docs(root), [])

    def test_real_json_file_in_docs_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs" / "canonical").mkdir(parents=True)
            (root / "docs" / "canonical" / "state.json").write_text("{}")
            violations = m.check_no_state_files_in_docs(root)
            self.assertEqual(len(violations), 1)
            self.assertIn("state.json", violations[0])

    def test_jsonl_anywhere_under_docs_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs" / "eval-log").mkdir(parents=True)
            (root / "docs" / "eval-log" / "x.jsonl").write_text("")
            violations = m.check_no_state_files_in_docs(root)
            self.assertEqual(len(violations), 1)

    def test_symlink_pointing_outside_docs_is_exempt(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "state").mkdir()
            (root / "state" / "real.json").write_text("{}")
            (root / "docs" / "real.json").symlink_to("../state/real.json")
            self.assertEqual(m.check_no_state_files_in_docs(root), [])

    def test_symlink_pointing_back_inside_docs_is_not_exempt(self):
        # The loophole this test closes: a symlink is only a legitimate
        # compat pointer if it actually leaves docs/ -- one that just
        # points at ANOTHER file inside docs/ is state-in-docs wearing a
        # symlink, not a real redirect to state/.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs" / "canonical").mkdir(parents=True)
            (root / "docs" / "canonical" / "real.json").write_text("{}")
            (root / "docs" / "fake.json").symlink_to("canonical/real.json")
            violations = m.check_no_state_files_in_docs(root)
            # Two violations here: canonical/real.json is itself a genuine
            # state file in docs/ (caught on its own merits), and
            # fake.json is a symlink that fails the "must resolve outside
            # docs/" exemption -- both real, both expected, not double-
            # counting one problem.
            self.assertEqual(len(violations), 2)
            self.assertTrue(any("resolves inside docs/" in v for v in violations))

    def test_broken_symlink_is_not_exempt(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "docs" / "dangling.json").symlink_to("../state/does-not-exist.json")
            violations = m.check_no_state_files_in_docs(root)
            self.assertEqual(len(violations), 1)
            self.assertIn("broken symlink", violations[0])


class ZeroDuplicateChecksums(unittest.TestCase):
    def test_unique_files_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git_repo(root)
            (root / "a.md").write_text("alpha\n")
            (root / "b.md").write_text("beta\n")
            git_add(root)
            self.assertEqual(m.check_zero_duplicate_checksums(root), [])

    def test_byte_identical_tracked_files_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git_repo(root)
            (root / "a.md").write_text("same content\n")
            (root / "b.md").write_text("same content\n")
            git_add(root)
            violations = m.check_zero_duplicate_checksums(root)
            self.assertEqual(len(violations), 1)
            self.assertIn("a.md", violations[0])
            self.assertIn("b.md", violations[0])

    def test_symlink_alias_is_not_a_duplicate(self):
        # CLAUDE.md -> AGENTS.md, this repo's own real shape -- an alias
        # to one file must never be reported as a second independent copy.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git_repo(root)
            (root / "AGENTS.md").write_text("shared content\n")
            (root / "CLAUDE.md").symlink_to("AGENTS.md")
            git_add(root)
            self.assertEqual(m.check_zero_duplicate_checksums(root), [])

    def test_untracked_duplicate_is_not_checked(self):
        # Scope is the committed/staged tree (what CI sees), same as
        # git ls-files reports -- an untracked scratch file is not yet
        # part of the repo this rule protects.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git_repo(root)
            (root / "a.md").write_text("same\n")
            git_add(root)
            (root / "b.md").write_text("same\n")  # never git add'ed
            self.assertEqual(m.check_zero_duplicate_checksums(root), [])


class Run(unittest.TestCase):
    def test_clean_repo_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git_repo(root)
            (root / "docs" / "canonical").mkdir(parents=True)
            (root / "docs" / "canonical" / "a.md").write_text("A\n")
            git_add(root)
            code, lines = m.run(root)
            self.assertEqual(code, 0)
            self.assertTrue(any("all three rules hold" in l for l in lines))

    def test_violations_across_all_three_rules_are_all_reported_together(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git_repo(root)
            (root / "docs").mkdir()
            (root / "docs" / "loose.md").write_text("dup\n")
            (root / "docs" / "state.json").write_text("{}")
            (root / "other-dup.md").write_text("dup\n")
            git_add(root)
            code, lines = m.run(root)
            self.assertEqual(code, 1)
            joined = "\n".join(lines)
            self.assertIn("unclassified root file", joined)
            self.assertIn("state file under docs/", joined)
            self.assertIn("full-text duplicate", joined)


if __name__ == "__main__":
    unittest.main()
