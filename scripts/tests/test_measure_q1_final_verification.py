"""Independent uncovered R1/R2 boundaries; real owned files and Git, no doubles."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from helpers import GitFixture
from test_measure_inventory import Q1Fixture
import measure


class FinalBoundaryTests(unittest.TestCase):
    def test_new_source_directory_absent_at_base_is_not_an_alias(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        fixture.config["python_source_roots"] = ["new"]
        fixture.save_config()
        fixture.git.write("new/a.py", "import b\n")
        fixture.git.write("new/b.py", "import a\n")
        fixture.build()
        self.assertFalse((Path(fixture.context["base_root"]) / "new").exists())
        cycles = fixture.summary()["metrics"]["cycles"]
        self.assertEqual((cycles["base"], cycles["head"], cycles["comparison"]), (0, 1, "fail"))
        local = {(edge["from"], edge["to"]) for edge in fixture.head["graph"]["edges"]
                 if edge["resolution"] == "local"}
        self.assertTrue({("new/a.py", "new/b.py"), ("new/b.py", "new/a.py")} <= local)

    def test_supplied_missing_file_and_directory_replacement_fail_exact_path_set(self):
        fixture = GitFixture()
        self.addCleanup(fixture.close)
        scratch = tempfile.TemporaryDirectory(prefix="q1-final-tests-")
        self.addCleanup(scratch.cleanup)
        fixture.write(".hidden/contract.txt", b"immutable\n")
        revision = fixture.commit()
        target = Path(scratch.name).resolve() / "base"
        measure.materialize_baseline(fixture.root, target, revision)
        measure.validate_baseline(target, revision)
        path = target / ".hidden/contract.txt"
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Baseline differs"):
            measure.validate_baseline(target, revision)
        path.mkdir()
        with self.assertRaisesRegex(ValueError, "Baseline differs"):
            measure.validate_baseline(target, revision)
        path.rmdir()
        path.write_bytes(b"immutable\n")
        measure.validate_baseline(target, revision)

    def test_unqualified_real_git_launcher_copy_fails_before_execution(self):
        # A genuine installed launcher is not the qualified core/DLL tuple.
        # Selecting its independent copy must not silently admit an unknown build.
        approved = measure.baseline_binding()
        actual = Path(shutil.which("git")).resolve(strict=True)
        self.assertNotEqual(actual, Path(approved["git"]["path"]))
        scratch = tempfile.TemporaryDirectory(prefix="q1-final-tests-")
        self.addCleanup(scratch.cleanup)
        owned = Path(scratch.name).resolve()
        shutil.copy2(actual, owned / "git.exe")
        old_path = os.environ["PATH"]
        try:
            os.environ["PATH"] = str(owned)
            with self.assertRaisesRegex(ValueError, "Baseline Git build is unqualified"):
                measure.baseline_binding()
        finally:
            os.environ["PATH"] = old_path
        self.assertEqual(measure.baseline_binding(), approved)


if __name__ == "__main__":
    unittest.main()
