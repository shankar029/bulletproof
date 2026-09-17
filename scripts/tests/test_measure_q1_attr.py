"""Literal attribute values must not masquerade as Git's textual state markers."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from helpers import GitFixture
import measure


class AttributeAdmissionTests(unittest.TestCase):
    def fixture(self):
        fixture = GitFixture()
        self.addCleanup(fixture.close)
        temporary = tempfile.TemporaryDirectory(prefix="q1-attr-tests-")
        self.addCleanup(temporary.cleanup)
        return fixture, Path(temporary.name).resolve()

    def named_driver(self, name):
        fixture, owned = self.fixture()
        fixture.write(".gitattributes", "*.py filter=" + name + "\n")
        fixture.write("a.py", "pass\n")
        revision = fixture.commit("literal filter state-marker collision")
        sentinel = owned / "EXECUTED"
        program = owned / "driver.py"
        program.write_text("import pathlib,sys\npathlib.Path(sys.argv[1]).write_text('executed')\n"
                           "sys.stdout.buffer.write(sys.stdin.buffer.read())\n", encoding="utf-8")
        driver = '"%s" -B "%s" "%s"' % (Path(sys.executable).as_posix(),
                                         program.as_posix(), sentinel.as_posix())
        fixture.run("git", "config", "filter." + name + ".smudge", driver)
        target = owned / "base"
        errors = {}
        for boundary, action in (
                ("materializer", lambda: measure.materialize_baseline(fixture.root, target, revision)),
                ("validator", lambda: measure.validate_baseline(fixture.root, revision))):
            try:
                action()
                errors[boundary] = None
            except ValueError as error:
                errors[boundary] = str(error)
            self.assertFalse(sentinel.exists(), "Isolation must prevent filter execution")
        # The owned target has a cached index even when the gate rejects. Prove
        # that the exact string is a real driver name, not a disabled state.
        fixture.run("git", "config", "filter." + name + ".smudge", driver, cwd=target)
        fixture.run("git", "checkout-index", "--all", "--force", cwd=target)
        self.assertEqual(sentinel.read_text(), "executed")
        print(json.dumps({"driver": name, "errors": errors, "isolated_sentinel_absent": True,
                          "positive_sentinel": sentinel.read_text()}), flush=True)
        for boundary, error in errors.items():
            with self.subTest(boundary=boundary):
                self.assertIsNotNone(error, "Declared named external filter was admitted")
                self.assertIn("unsupported attribute filter=" + name, error)

    def test_literal_unset_driver_rejected_at_both_boundaries(self):
        self.named_driver("unset")

    def test_literal_unspecified_driver_rejected_at_both_boundaries(self):
        self.named_driver("unspecified")

    def test_absent_and_reset_filter_preserve_normal_baseline(self):
        for attributes in ("a.py diff=python\n", "a.py filter=earlier\na.py !filter\n"):
            with self.subTest(attributes=attributes):
                fixture, owned = self.fixture()
                fixture.write(".gitattributes", attributes)
                fixture.write("a.py", b"pass\n")
                revision = fixture.commit("no effective filter")
                target = owned / "base"
                measure.materialize_baseline(fixture.root, target, revision)
                measure.validate_baseline(target, revision)
                self.assertEqual((target / "a.py").read_bytes(), b"pass\n")

    def test_disabled_filter_is_explicitly_unsupported_when_ambiguous(self):
        fixture, owned = self.fixture()
        fixture.write(".gitattributes", "*.py -filter\n")
        fixture.write("a.py", "pass\n")
        revision = fixture.commit("disabled filter textual ambiguity")
        for boundary, action in (
                ("materializer", lambda: measure.materialize_baseline(fixture.root, owned / "base", revision)),
                ("validator", lambda: measure.validate_baseline(fixture.root, revision))):
            with self.subTest(boundary=boundary), self.assertRaisesRegex(
                    ValueError, "unsupported attribute filter=unset.*ambiguous"):
                action()


if __name__ == "__main__":
    unittest.main()
