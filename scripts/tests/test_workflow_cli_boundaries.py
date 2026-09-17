"""Ordinary discovery of three historically independent CLI boundary cases.

Ported from workflow-reliability evidence without modifying the original proof.
Synthetic role metadata; real public CLI, Git and subprocesses via CliFixture.
No inherited WorkflowCliTests methods or additional independent-proof claim.
"""

import json
import os
from pathlib import Path
import sys
import unittest

from test_workflow_cli import CliFixture


class WorkflowCliBoundaryTests(unittest.TestCase):
    def fixture(self):
        fixture = CliFixture()
        self.addCleanup(fixture.close)
        return fixture

    def test_registered_environment_sets_removes_and_preserves_exact_values(self):
        f = self.fixture()
        names = ("JOINT_BINDING_SET", "JOINT_BINDING_REMOVE", "JOINT_BINDING_KEEP")
        previous = {name: os.environ.get(name) for name in names}
        try:
            os.environ.update(dict(zip(names, ("old", "remove me", "inherited value"))))
            action = f.contract["actions"]["A-work"]
            action["command"]["environment"] = {names[0]: "exact spaced = value", names[1]: None}
            action["command"]["argv"] = [
                sys.executable, "-B", "-c",
                "import json,os; print(json.dumps({k:os.environ.get(k) for k in " + repr(names) + "}))",
            ]
            f.adopt()
            result = f.cli("next", "--action", "A-work")[1]
            actual = json.loads(Path(result["stdout"]).read_text())
            self.assertEqual(actual, dict(zip(names, ("exact spaced = value", None, "inherited value"))))
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_close_rejects_real_scoped_membership_and_git_mode_mismatch(self):
        for scenario in ("membership", "mode"):
            with self.subTest(scenario=scenario):
                f = self.fixture()
                f.adopt()
                commit = f.commit()
                if scenario == "membership":
                    (f.root / "src/A.py").unlink()
                    expected = "Committed source membership"
                else:
                    f.run("git", "update-index", "--chmod=+x", "src/A.py")
                    f.run("git", "commit", "--quiet", "-m", "fixture: executable mode")
                    commit = f.run("git", "rev-parse", "HEAD")[1].strip()
                    self.assertIn("100755", f.run("git", "ls-tree", "HEAD", "src/A.py")[1])
                    expected = "Committed bytes/mode"
                result = f.cli("close", "--increment", "A", "--commit", commit, expected=1)[1]
                self.assertIn(expected, result["reason"])
                self.assertFalse(any(e["kind"] == "closed" for e in f.ledger()["events"]))

    def test_adoption_cannot_reclassify_an_actual_pending_handoff_as_executable(self):
        f = self.fixture()
        f.handoff()
        f.adopt()
        f.cli("next", "--action", "A-work")
        f.cli("next", "--action", "A-review-run")
        before = f.ledger()
        f.revision()
        f.contract["actions"]["A-review-run"]["command"] = {
            **f.contract["actions"]["A-work"]["command"],
            "argv": [sys.executable, "-B", "-c", "raise SystemExit(41)"],
        }
        f.contract["checks"]["A-review"]["handoff_steps"] = []
        result = f.adopt(expected=3)[1]
        self.assertIn("reclassifies", result["reason"])
        self.assertEqual(f.ledger(), before)


if __name__ == "__main__":
    unittest.main()
