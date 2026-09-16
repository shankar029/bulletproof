import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import exclusive_lock, source_snapshot, write_json_atomic
from helpers import GitFixture


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="bulletproof-evidence-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_snapshot_binds_bytes_membership_and_missing_paths(self):
        self.write("src/a.mjs", b"export const a = 1;\n")
        scope = {"files": ["config.json"], "directories": ["src"], "excluded_outputs": []}
        before = source_snapshot(self.root, scope)
        self.assertEqual(before["binding_mode"], "standalone-source")
        self.assertIsNone(before["base"])
        self.assertIsNone(before["head"])
        self.assertEqual(before["files"]["config.json"], {"sha256": None, "mode": "missing"})
        self.assertEqual(before["files"]["src/a.mjs"]["sha256"], hashlib.sha256(b"export const a = 1;\n").hexdigest())
        self.assertEqual(before, source_snapshot(self.root, scope))
        self.write("src/a.mjs", b"export const a = 2;\n")
        changed = source_snapshot(self.root, scope)
        self.assertNotEqual(before["scope_sha256"], changed["scope_sha256"])
        self.write("src/new.cjs", b"module.exports = 3;\n")
        added = source_snapshot(self.root, scope)
        self.assertNotEqual(changed["scope_sha256"], added["scope_sha256"])
        (self.root / "src/a.mjs").unlink()
        removed = source_snapshot(self.root, scope)
        self.assertNotEqual(added["scope_sha256"], removed["scope_sha256"])

    def test_generated_outputs_do_not_hide_contracts(self):
        self.write(".ai/task/contract.json", b'{"revision":1}\n')
        scope = {"files": [], "directories": [".ai/task"], "excluded_outputs": [
            {"path": ".ai/task/evidence", "reason": "Owned generated receipts"}]}
        first = source_snapshot(self.root, scope)
        self.write(".ai/task/evidence/run.json", b'{"result":"pass"}\n')
        self.assertEqual(first, source_snapshot(self.root, scope))
        self.write(".ai/task/contract.json", b'{"revision":2}\n')
        self.assertNotEqual(first["scope_sha256"], source_snapshot(self.root, scope)["scope_sha256"])

    def test_scope_is_canonical_and_preserves_missing_directory_state(self):
        self.write("b.txt", b"b")
        self.write("a.txt", b"a")
        first = source_snapshot(self.root, {"files": ["b.txt", "a.txt"], "directories": ["missing"]})
        second = source_snapshot(self.root, {"files": ["a.txt", "b.txt"], "directories": ["missing"]})
        self.assertEqual(first, second)
        self.assertEqual(list(first["files"]), ["a.txt", "b.txt", "missing"])
        (self.root / "missing").mkdir()
        self.assertNotEqual(first["scope_sha256"], source_snapshot(self.root, first["scope"])["scope_sha256"])

    def test_rejects_traversal_absolute_and_excluded_inputs(self):
        for name in ("../escape", "a/../escape", "/absolute", "C:\\outside", "C:relative", ""):
            with self.subTest(name=name), self.assertRaises(ValueError):
                source_snapshot(self.root, {"files": [name]})
        with self.assertRaises(ValueError):
            source_snapshot(self.root, {"directories": ["."], "excluded_outputs": [{"path": ".", "reason": "Everything"}]})
        with self.assertRaises(ValueError):
            source_snapshot(self.root, {"files": ["a"], "excluded_outputs": [{"path": "a", "reason": "Output"}]})
        with self.assertRaises(ValueError):
            source_snapshot(self.root, {"files": [], "unknown": True})

    def test_atomic_write_preserves_old_bytes_on_replace_failure(self):
        path = self.write("record.json", b'{"old":true}\r\n')
        with patch("evidence.os.replace", side_effect=OSError("replacement denied")):
            with self.assertRaisesRegex(OSError, "replacement denied"):
                write_json_atomic(path, {"new": True})
        self.assertEqual(path.read_bytes(), b'{"old":true}\r\n')
        self.assertEqual([p.name for p in self.root.iterdir()], ["record.json"])
        write_json_atomic(path, {"new": True})
        self.assertEqual(json.loads(path.read_bytes()), {"new": True})

    def test_invalid_json_does_not_touch_destination(self):
        path = self.write("record.json", b"original")
        with self.assertRaises(ValueError):
            write_json_atomic(path, {"value": float("nan")})
        self.assertEqual(path.read_bytes(), b"original")

    def test_lock_collision_does_not_remove_original_owner(self):
        path = self.root / "owner.lock"
        owner = {"token": "first-run", "pid": os.getpid()}
        with exclusive_lock(path, owner):
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                with exclusive_lock(path, {"token": "second-run", "pid": os.getpid()}):
                    self.fail("Competing owner entered the protected operation")
            self.assertEqual(path.read_bytes(), before)
        self.assertFalse(path.exists())

    def test_lock_exception_releases_only_its_own_record(self):
        path = self.root / "owner.lock"
        with self.assertRaisesRegex(RuntimeError, "body failed"):
            with exclusive_lock(path, {"token": "ours", "pid": os.getpid()}):
                raise RuntimeError("body failed")
        self.assertFalse(path.exists())
        with self.assertRaisesRegex(RuntimeError, "ownership changed"):
            with exclusive_lock(path, {"token": "ours", "pid": os.getpid()}):
                path.write_bytes(b'{"token":"another-owner"}')
        self.assertEqual(json.loads(path.read_bytes()), {"token": "another-owner"})
        with self.assertRaises(ValueError):
            with exclusive_lock(self.root / "bad.lock", {}):
                self.fail("Missing unique owner token was accepted")

    def test_owned_git_fixture_preserves_bytes_and_reports_commands(self):
        fixture = GitFixture()
        self.addCleanup(fixture.close)
        path = fixture.write("source.mjs", b"export const value = 1;\r\n")
        commit = fixture.commit()
        self.assertEqual(len(commit), 40)
        self.assertEqual(path.read_bytes(), b"export const value = 1;\r\n")
        code, stdout, stderr = fixture.run(sys.executable, "-B", "-c",
                                          "import sys; print('observed'); sys.exit(7)", expected=7)
        self.assertEqual((code, stdout.strip(), stderr), (7, "observed", ""))
        with self.assertRaises(ValueError):
            fixture.write("../escape", b"outside")

    def test_snapshot_rejects_directory_link_escape(self):
        repo = self.root / "repo"
        repo.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_bytes(b"not an input")
        link = repo / "linked"
        if os.name == "nt":
            from run import run_capture
            script = "New-Item -ItemType Junction -Path '%s' -Target '%s' | Out-Null" % (
                str(link).replace("'", "''"), str(outside).replace("'", "''"))
            result = run_capture(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                                 idle=15, max_total=30)
            self.assertEqual(result[0], 0, result)
        else:
            link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "escapes"):
            source_snapshot(repo, {"files": ["linked/secret.txt"]})
        with self.assertRaisesRegex(ValueError, "escapes"):
            source_snapshot(repo, {"directories": ["."]})


if __name__ == "__main__":
    unittest.main()
