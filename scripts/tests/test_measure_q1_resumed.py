"""Real Git/path controls for the resumed R1/R2 correction (owner tests only)."""
import os
from pathlib import Path
import tempfile
import unittest

from helpers import GitFixture
import measure
import measure_graph as graph
import probe


class ResumedBoundaryTests(unittest.TestCase):
    def fixture(self):
        fixture = GitFixture()
        self.addCleanup(fixture.close)
        scratch = tempfile.TemporaryDirectory(prefix="q1-resumed-tests-")
        self.addCleanup(scratch.cleanup)
        return fixture, Path(scratch.name).resolve()

    def test_shared_paths_reject_alias_components_and_preserve_directory_dot(self):
        fixture, owned = self.fixture()
        fixture.write("Canonical/nested/input.py", "pass\n")
        self.assertEqual(graph.input_path(fixture.root, ".", directory=True), fixture.root)
        with self.assertRaises(ValueError):
            graph.input_path(fixture.root, ".")
        self.assertEqual(graph.input_path(fixture.root, "Canonical/nested/input.py").read_bytes(), b"pass\n")
        if os.name == "nt":
            for name in ("Canonical./nested/input.py", "Canonical /nested/input.py",
                         "canonical/nested/input.py", "Canonical/nested/input.py.",
                         "Canonical/nested/input.py ", "Canonical./new/file.py"):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Alias"):
                    graph.input_path(fixture.root, name)
            for name in ("Canonical.", "Canonical ", "canonical"):
                with self.subTest(root=name), self.assertRaises(ValueError):
                    graph.root_path(fixture.root / name)
        self.assertEqual(graph.input_path(owned, "new/path.py"), owned / "new/path.py")

    def test_hidden_index_controls_and_full_noncode_scope(self):
        fixture, owned = self.fixture()
        for name in ("a.py", "contract.txt", ".hidden/excluded.py", "node_modules/input.txt"):
            fixture.write(name, "original\n")
        revision = fixture.commit()
        target = owned / "base"
        record = measure.materialize_baseline(fixture.root, target, revision)
        self.assertEqual(set(record["tree_modes"]),
                         {"a.py", "contract.txt", ".hidden/excluded.py", "node_modules/input.txt"})
        measure.validate_baseline(target, revision)
        for flag in ("--assume-unchanged", "--skip-worktree"):
            fixture.run("git", "update-index", flag, "contract.txt", cwd=target)
            (target / "contract.txt").write_bytes(b"hidden\n")
            self.assertEqual(fixture.run("git", "status", "--porcelain", cwd=target)[1], "")
            with self.assertRaisesRegex(ValueError, "Baseline differs"):
                measure.validate_baseline(target, revision)
            (target / "contract.txt").write_bytes(b"original\n")
            fixture.run("git", "update-index", "--no-assume-unchanged", "--no-skip-worktree",
                        "contract.txt", cwd=target)
        # Alter the index's blob too; it is still not the selected immutable tree.
        (target / "a.py").write_bytes(b"staged\n")
        fixture.run("git", "add", "a.py", cwd=target)
        with self.assertRaisesRegex(ValueError, "Baseline differs"):
            measure.validate_baseline(target, revision)
        (target / "a.py").write_bytes(b"original\n")
        # Even a disagreeing index cannot reject equal actual bytes.
        measure.validate_baseline(target, revision)
        for name in (".hidden/excluded.py", "node_modules/input.txt", "extra.txt"):
            path = target / name
            before = path.read_bytes() if path.exists() else None
            path.write_bytes(b"not in immutable baseline\n")
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Baseline differs"):
                measure.validate_baseline(target, revision)
            if before is None:
                path.unlink()
            else:
                path.write_bytes(before)

    def test_neutral_and_versioned_eol_modes_exact_bytes(self):
        fixture, owned = self.fixture()
        fixture.write(".gitattributes", "*.txt text eol=crlf\nnested/*.txt text eol=lf\n")
        fixture.write("nested/.gitattributes", "again.txt text eol=crlf\n")
        for name in ("neutral.py", "windows.txt", "nested/unix.txt", "nested/again.txt"):
            fixture.write(name, b"first\nsecond\n")
        fixture.run("git", "add", "--all")
        fixture.run("git", "update-index", "--chmod=+x", "neutral.py")
        fixture.run("git", "commit", "--quiet", "-m", "versioned materialization")
        revision = measure.git_head(fixture.root)
        target = owned / "base"
        record = measure.materialize_baseline(fixture.root, target, revision)
        self.assertEqual(record["tree_modes"]["neutral.py"], "100755")
        self.assertEqual(record["binding"]["mode_projection"],
                         "regular-file-only-windows" if os.name == "nt" else "posix-executable")
        for name in ("windows.txt", "nested/again.txt"):
            self.assertEqual((target / name).read_bytes(), b"first\r\nsecond\r\n")
        for name in ("neutral.py", "nested/unix.txt"):
            self.assertEqual((target / name).read_bytes(), b"first\nsecond\n")
        measure.validate_baseline(target, revision)
        (target / "windows.txt").write_bytes(b"first\nsecond\n")
        with self.assertRaisesRegex(ValueError, "Baseline differs"):
            measure.validate_baseline(target, revision)
        (target / "windows.txt").write_bytes(b"first\r\nsecond\r\n")
        if os.name != "nt":
            (target / "neutral.py").chmod(0o644)
            with self.assertRaisesRegex(ValueError, "Baseline differs"):
                measure.validate_baseline(target, revision)

    def test_ambient_index_info_attributes_and_replacements_do_not_define_tree(self):
        fixture, owned = self.fixture()
        fixture.write("a.py", b"original\n")
        revision = fixture.commit()
        fixture.write("a.py", b"replacement\n")
        replacement = fixture.commit("replacement tree")
        fixture.run("git", "replace", revision, replacement)
        fixture.write(".git/info/attributes", "* text eol=crlf\n")
        fixture.run("git", "config", "core.autocrlf", "true")
        fake_index = owned / "caller-index"
        ambient = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.eol",
                   "GIT_CONFIG_VALUE_0": "crlf", "GIT_INDEX_FILE": str(fake_index),
                   "GIT_WORK_TREE": str(owned), "GIT_CONFIG_PARAMETERS": "'core.autocrlf=true'"}
        previous = {key: os.environ.get(key) for key in ambient}
        try:
            os.environ.update(ambient)
            target = owned / "base"
            measure.materialize_baseline(fixture.root, target, revision)
            self.assertEqual((target / "a.py").read_bytes(), b"original\n")
            measure.validate_baseline(target, revision)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        self.assertFalse(fake_index.exists())
        self.assertEqual(fixture.run("git", "config", "core.autocrlf")[1].strip(), "true")
        self.assertEqual((fixture.root / ".git/info/attributes").read_bytes(), b"* text eol=crlf\n")

    def test_external_filter_macro_rejected_before_sentinel_execution(self):
        fixture, owned = self.fixture()
        fixture.write(".gitattributes", "[attr]danger filter=tripwire\n*.py danger\n")
        fixture.write("a.py", b"pass\n")
        revision = fixture.commit()
        sentinel = owned / "EXECUTED"
        program = owned / "driver.py"
        program.write_text("import pathlib,sys\npathlib.Path(sys.argv[1]).write_text('executed')\n"
                           "sys.stdout.buffer.write(sys.stdin.buffer.read())\n", encoding="utf-8")
        import sys
        driver = '"%s" -B "%s" "%s"' % (Path(sys.executable).as_posix(),
                                         program.as_posix(), sentinel.as_posix())
        fixture.run("git", "config", "filter.tripwire.smudge", driver)
        for target, copy in ((owned / "direct", measure.materialize_baseline),
                             (owned / "cli-path", probe._copy_subject)):
            with self.assertRaisesRegex(ValueError, "unsupported attribute filter=tripwire"):
                copy(fixture.root, target, revision)
            self.assertFalse(sentinel.exists())
            self.assertFalse((target / "a.py").exists(), "Rejection precedes checkout-index")
        # Actual positive control proves the sentinel driver is runnable.
        positive = owned / "direct"
        fixture.run("git", "config", "filter.tripwire.smudge", driver, cwd=positive)
        fixture.run("git", "checkout-index", "--all", "--force", cwd=positive)
        self.assertEqual(sentinel.read_text(), "executed")

    def test_unqualified_attributes_and_git_types_fail_closed(self):
        fixture, owned = self.fixture()
        fixture.write("a.py", b"pass\n")
        for index, attribute in enumerate(("ident", "working-tree-encoding=UTF-16", "crlf")):
            # Commit plain bytes before adding attributes to avoid a clean transform.
            fixture.run("git", "add", "a.py")
            fixture.write(".gitattributes", "*.py " + attribute + "\n")
            fixture.run("git", "add", ".gitattributes")
            fixture.run("git", "commit", "--quiet", "-m", "unsupported " + attribute)
            revision = measure.git_head(fixture.root)
            with self.subTest(attribute=attribute), self.assertRaisesRegex(ValueError, "unsupported attribute"):
                measure.materialize_baseline(fixture.root, owned / str(index), revision)
            (fixture.root / ".gitattributes").unlink()
        fixture.run("git", "add", "--all")
        revision = fixture.commit("plain files")
        blob = fixture.run("git", "rev-parse", revision + ":a.py")[1].strip()
        for index, mode, oid in ((3, "120000", blob), (4, "160000", revision)):
            fixture.run("git", "update-index", "--add", "--cacheinfo", mode, oid, "unsupported")
            fixture.run("git", "commit", "--quiet", "-m", "unsupported mode " + mode)
            selected = measure.git_head(fixture.root)
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "unsupported tree type/mode"):
                measure.materialize_baseline(fixture.root, owned / str(index), selected)

    def test_base_source_root_cannot_alias_its_inventory_spelling(self):
        from test_measure_inventory import Q1Fixture
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        fixture.git.write("Scripts/local.py", "import peer\n")
        fixture.git.write("Scripts/peer.py", "import local\n")
        fixture.base_sha = fixture.git.commit("baseline uppercase source root")
        fixture.git.run("git", "mv", "Scripts", "temporary")
        fixture.git.run("git", "mv", "temporary", "scripts")
        fixture.config["python_source_roots"] = ["scripts"]
        fixture.save_config()
        if os.name == "nt":
            with self.assertRaisesRegex(ValueError, "Aliased"):
                fixture.build()
        else:
            # On a case-sensitive filesystem the old path does not alias scripts.
            fixture.build()
            self.assertEqual(fixture.summary()["metrics"]["cycles"]["head"], 1)

    def test_materializer_identity_and_tree_modes_are_validated(self):
        import copy
        from test_measure_inventory import Q1Fixture
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        fixture.git.write("a.py", "import b\n")
        fixture.build()
        report = probe._configured_report(fixture.context, fixture.base, fixture.head, fixture.config,
                                          fixture.manifest, fixture.observations, "binding", fixture.base_sha, [])
        proof = report["tools"]["baseline_materialization"]
        self.assertEqual(proof["tree_modes"]["a.py"], "100644")
        self.assertEqual(proof["binding"]["git"]["version"], "2.53.0.windows.4")
        self.assertTrue(proof["binding"]["git"]["bundled_dlls"])
        probe.validate_measurement_report(report, fixture.context, fixture.base, fixture.head,
                                          fixture.config, fixture.policy, fixture.manifest)
        forged = copy.deepcopy(report)
        forged["tools"]["baseline_materialization"]["tree_modes"]["a.py"] = "100755"
        with self.assertRaisesRegex(ValueError, "tools"):
            probe.validate_measurement_report(forged, fixture.context, fixture.base, fixture.head,
                                              fixture.config, fixture.policy, fixture.manifest)
        forged_policy = copy.deepcopy(fixture.policy)
        forged_policy["baseline_materialization"]["git"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "binding"):
            measure.validate_observations(fixture.context, fixture.base, fixture.head, fixture.config,
                                           forged_policy, fixture.manifest, fixture.observations)


if __name__ == "__main__":
    unittest.main()
