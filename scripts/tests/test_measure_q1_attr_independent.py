"""Independent missing conservative text-state boundary; real Git only."""
from pathlib import Path
import tempfile
import unittest

from helpers import GitFixture
import measure


class IndependentAttributeTests(unittest.TestCase):
    def test_disabled_text_rejects_but_reset_text_is_genuinely_absent(self):
        fixture = GitFixture()
        self.addCleanup(fixture.close)
        temporary = tempfile.TemporaryDirectory(prefix="q1-attr-independent-tests-")
        self.addCleanup(temporary.cleanup)
        owned = Path(temporary.name).resolve()
        fixture.write("a.py", b"pass\n")
        fixture.write(".gitattributes", "*.py -text\n")
        revision = fixture.commit("ambiguous present text")
        for boundary, action in (
                ("materializer", lambda: measure.materialize_baseline(fixture.root, owned / "negative", revision)),
                ("validator", lambda: measure.validate_baseline(fixture.root, revision))):
            with self.subTest(boundary=boundary), self.assertRaisesRegex(
                    ValueError, "unsupported attribute text=unset.*ambiguous"):
                action()
        self.assertFalse((owned / "negative/a.py").exists())
        fixture.write(".gitattributes", "*.py -text\n*.py !text\n")
        revision = fixture.commit("genuinely reset text")
        target = owned / "positive"
        measure.materialize_baseline(fixture.root, target, revision)
        measure.validate_baseline(target, revision)
        self.assertEqual((target / "a.py").read_bytes(), b"pass\n")


if __name__ == "__main__":
    unittest.main()
