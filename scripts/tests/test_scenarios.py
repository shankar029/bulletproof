"""Behavioral tests for scripts/scenarios.py.

Each test builds a real workspace on disk and asserts the checker's verdict,
because the whole point of the tool is that it inspects files rather than
trusting a claim. Nothing here mocks the filesystem.
"""

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scenarios import check, main, parse_scenarios

HEADER = (
    "| Id | AC | Class | Expected observable | Evidence | Status |\n"
    "|----|----|-------|---------------------|----------|--------|\n"
)


def table(*rows: str) -> str:
    return "# Scenarios\n\n" + HEADER + "".join(rows)


def row(ident, ac="AC1", cls="positive", expected="`HTTP 201`",
        evidence="`evidence/{id}.json`", status=""):
    evidence = evidence.format(id=ident)
    return f"| {ident} | {ac} | {cls} | {expected} | {evidence} | {status} |\n"


class Workspace:
    """A throwaway repo with a .ai/<slug>/ workspace."""

    def __init__(self, slug="demo"):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.slug = slug
        self.slug_dir = self.root / ".ai" / slug
        (self.slug_dir / "evidence").mkdir(parents=True)

    def scenarios(self, text):
        (self.slug_dir / "scenarios.md").write_text(text, encoding="utf-8")

    def artifact(self, name, body="ok", age_seconds=0):
        path = self.slug_dir / "evidence" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        if age_seconds:
            when = time.time() - age_seconds
            os.utime(path, (when, when))
        return path

    def close(self):
        self.dir.cleanup()


class ParseTest(unittest.TestCase):
    def test_reads_rows_by_header_name_not_position(self):
        text = ("| Evidence | Id | Status |\n|---|---|---|\n"
                "| `evidence/S1.json` | S1 | |\n")
        rows = parse_scenarios(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].ident, "S1")
        self.assertEqual(rows[0].evidence, "`evidence/S1.json`")

    def test_ignores_prose_and_non_scenario_rows(self):
        rows = parse_scenarios(table(row("S1"), "| note | x | y | z | w | v |\n"))
        self.assertEqual([r.ident for r in rows], ["S1"])

    def test_returns_nothing_without_the_required_columns(self):
        self.assertEqual(parse_scenarios("| Foo | Bar |\n|---|---|\n| a | b |\n"), [])


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()
        self.addCleanup(self.ws.close)

    def run_check(self, since=None, acs=None, strict=False):
        return check(self.ws.root, self.ws.slug, since, acs, strict)

    def test_passes_when_every_row_has_a_real_artifact(self):
        self.ws.scenarios(table(row("S1"), row("S2")))
        self.ws.artifact("S1.json")
        self.ws.artifact("S2.json")
        report = self.run_check()
        self.assertTrue(report.ok)
        self.assertEqual(report.checked, 2)

    def test_missing_artifact_fails(self):
        self.ws.scenarios(table(row("S1")))
        report = self.run_check()
        self.assertFalse(report.ok)
        self.assertEqual([f.kind for f in report.failures], ["MISSING"])

    def test_zero_byte_artifact_is_missing_evidence_not_weak_evidence(self):
        self.ws.scenarios(table(row("S1")))
        self.ws.artifact("S1.json", body="")
        report = self.run_check()
        self.assertEqual([f.kind for f in report.failures], ["EMPTY"])

    def test_row_without_evidence_or_blocker_is_dropped(self):
        self.ws.scenarios(table(row("S1", evidence="—")))
        report = self.run_check()
        self.assertEqual([f.kind for f in report.failures], ["DROPPED"])

    def test_blocked_with_a_reason_is_an_honest_outcome(self):
        self.ws.scenarios(table(row("S1", evidence="—",
                                    status="BLOCKED: no staging credentials")))
        report = self.run_check()
        self.assertTrue(report.ok)
        self.assertEqual(report.blocked[0]["reason"], "no staging credentials")

    def test_blocked_without_a_reason_fails(self):
        self.ws.scenarios(table(row("S1", evidence="—", status="BLOCKED")))
        report = self.run_check()
        self.assertEqual([f.kind for f in report.failures], ["DROPPED"])

    def test_duplicate_ids_fail(self):
        self.ws.scenarios(table(row("S1"), row("S1")))
        self.ws.artifact("S1.json")
        report = self.run_check()
        self.assertEqual([f.kind for f in report.failures], ["DUPLICATE"])

    def test_ac_scope_skips_rows_outside_the_increment(self):
        self.ws.scenarios(table(row("S1", ac="AC1"), row("S2", ac="AC2")))
        self.ws.artifact("S1.json")
        report = self.run_check(acs={"AC1"})
        self.assertTrue(report.ok)
        self.assertEqual((report.checked, report.skipped), (1, 1))

    def test_directory_artifact_needs_a_non_empty_file(self):
        self.ws.scenarios(table(row("S1", evidence="`evidence/run/`")))
        (self.ws.slug_dir / "evidence" / "run").mkdir()
        (self.ws.slug_dir / "evidence" / "run" / "out.txt").write_text("", encoding="utf-8")
        self.assertEqual([f.kind for f in self.run_check().failures], ["EMPTY"])

    def test_path_escaping_the_workspace_is_refused(self):
        self.ws.scenarios(table(row("S1", evidence="`../../etc/passwd`")))
        self.assertEqual([f.kind for f in self.run_check().failures], ["DROPPED"])

    def test_backslash_traversal_is_refused_too(self):
        self.ws.scenarios(table(row("S1", evidence=r"`..\..\etc\passwd`")))
        self.assertEqual([f.kind for f in self.run_check().failures], ["DROPPED"])

    def test_absolute_path_is_refused(self):
        self.ws.scenarios(table(row("S1", evidence="`C:/Windows/win.ini`")))
        self.assertEqual([f.kind for f in self.run_check().failures], ["DROPPED"])

    def test_strict_fails_when_the_expected_literal_is_absent(self):
        self.ws.scenarios(table(row("S1", expected="`HTTP 201`")))
        self.ws.artifact("S1.json", body='{"status": 500}')
        report = self.run_check(strict=True)
        self.assertEqual([f.kind for f in report.failures], ["UNPROVEN"])

    def test_strict_passes_when_the_literal_is_present(self):
        self.ws.scenarios(table(row("S1", expected="`HTTP 201`")))
        self.ws.artifact("S1.json", body="HTTP 201 OK")
        self.assertTrue(self.run_check(strict=True).ok)

    def test_strict_refuses_to_vouch_for_a_screenshot(self):
        self.ws.scenarios(table(row("S1", expected="`Order placed`",
                                    evidence="`evidence/S1.png`")))
        self.ws.artifact("S1.png", body="not really a png")
        report = self.run_check(strict=True)
        self.assertEqual([f.kind for f in report.failures], ["UNPROVEN"])
        self.assertIn("cannot read", report.failures[0].detail)

    def test_missing_scenarios_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.run_check()

    def test_unparseable_table_raises(self):
        self.ws.scenarios("# Scenarios\n\nNo table here.\n")
        with self.assertRaises(ValueError):
            self.run_check()


class StalenessTest(unittest.TestCase):
    """Staleness needs a real commit to compare against."""

    def setUp(self):
        self.ws = Workspace()
        self.addCleanup(self.ws.close)
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        for args in (["init", "-q"], ["add", "-A"],
                     ["commit", "-qm", "base", "--allow-empty"]):
            subprocess.run(["git", "-C", str(self.ws.root), *args],
                           check=True, env=env, capture_output=True)

    def test_artifact_older_than_the_commit_is_stale(self):
        self.ws.scenarios(table(row("S1")))
        self.ws.artifact("S1.json", age_seconds=86400)
        report = check(self.ws.root, self.ws.slug, "HEAD", None, False)
        self.assertEqual([f.kind for f in report.failures], ["STALE"])

    def test_artifact_captured_after_the_commit_passes(self):
        self.ws.scenarios(table(row("S1")))
        self.ws.artifact("S1.json")
        self.assertTrue(check(self.ws.root, self.ws.slug, "HEAD", None, False).ok)

    def test_staleness_is_skipped_when_since_is_empty(self):
        self.ws.scenarios(table(row("S1")))
        self.ws.artifact("S1.json", age_seconds=86400)
        self.assertTrue(check(self.ws.root, self.ws.slug, None, None, False).ok)


class ExitCodeTest(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()
        self.addCleanup(self.ws.close)

    def cli(self, *extra):
        return main(["--slug", self.ws.slug, "--root", str(self.ws.root),
                     "--since", "", *extra])

    def test_zero_when_proven(self):
        self.ws.scenarios(table(row("S1")))
        self.ws.artifact("S1.json")
        self.assertEqual(self.cli(), 0)

    def test_one_when_a_row_fails(self):
        self.ws.scenarios(table(row("S1")))
        self.assertEqual(self.cli(), 1)

    def test_two_when_the_file_is_absent(self):
        self.assertEqual(self.cli(), 2)


if __name__ == "__main__":
    unittest.main()
