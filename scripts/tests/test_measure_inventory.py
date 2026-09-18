import copy
import ctypes
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from helpers import GitFixture, SCRIPTS
import measure
import measure_graph as graph
import probe
from evidence import source_snapshot


class Q1Fixture:
    """Actual source revisions, private subjects and real producer artifacts."""

    def __init__(self):
        self.git = GitFixture()
        self.scratch = tempfile.TemporaryDirectory(prefix="q1-evidence-")
        self.root = Path(self.scratch.name).resolve()
        for name in ("a.py", "b.py", "c.py"):
            self.git.write(name, "value = 1\n")
        self.git.write("test_example.py", "import unittest\nclass Example(unittest.TestCase):\n"
                       "    def test_value(self):\n        self.assertEqual(1 + 1, 2)\n")
        self.git.write("approval.txt", "Real fixture approval of the compiled Q1 graph policy.\n")
        self.git.write(".gitignore", ".ai/\n")
        approval = graph.artifact(self.git.root, "approval.txt")
        self.config = {
            "schema_version": 1, "semantic_profile": "workflow-reliability-q-v1", "tools": {},
            "python_source_roots": ["."], "js_entrypoints": [],
            "suites": [{"id": "fixture-tests", "runner": "python-unittest",
                        "argv": [sys.executable, "-B", "-m", "unittest", "test_example"],
                        "cwd": ".", "test_files": ["test_example.py"], "idle_seconds": 30, "max_seconds": 90}],
            "coverage_policy": {"changed_executable_line_floor_pct": 100,
                                "changed_decision_outcome_floor_pct": 100, "approval_artifact": approval},
            "architecture_rules": [{"id": name, "version": 1, "origin_ref": "approval.txt"} for name in graph.RULE_IDS],
            "mutation_cap": 20, "mutation_max_seconds": 90, "approval_artifact": approval}
        self.save_config()
        self.base_sha = self.git.commit()

    def save_config(self):
        self.git.write("measurement.json", json.dumps(self.config))

    def build(self, *, collect=True):
        self.git.commit("fixture: head")
        return self.materialize(collect=collect)

    def materialize(self, *, collect=True):
        base, head = self.root / "base", self.root / "head"
        source = source_snapshot(self.git.root, {"directories": ["."],
                                 "excluded_outputs": [{"path": ".git", "reason": "Git metadata"}]})
        source.update(base=self.base_sha, head=measure.git_head(self.git.root))
        probe._copy_subject(self.git.root, base, source["base"])
        probe._copy_subject(self.git.root, head, source["head"], source)
        controller, raw = self.root / "controller", self.root / "raw"
        controller.mkdir()
        raw.mkdir()
        for name in ("measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py"):
            shutil.copy2(SCRIPTS / name, controller / name)
        self.policy = measure.config_policy(self.config)
        self.context = {
            "schema_version": 1, "run_id": "fixture-run", "source": source,
            "base_root": str(base), "head_root": str(head), "controller_root": str(controller),
            "run_root": str(raw), "controller_sha256": measure.controller_digest(controller),
            "policy_sha256": graph.digest(self.policy),
            "toolset_sha256": graph.digest({"python_parser": graph.parser_digest()}),
            "contract_artifacts": [self.config["approval_artifact"],
                                   graph.artifact(self.git.root, "measurement.json")]}
        if not collect:
            return self
        changes = {name: sorted(lines) for name, lines in probe.changed_lines(self.git.root, self.base_sha).items()}
        self.base = graph.parse_files(self.context, measure.inventory(self.context, "base", {}), self.config)
        self.head = graph.parse_files(self.context, measure.inventory(self.context, "head", changes), self.config)
        pairs = measure.collect_pair(self.context, self.config, self.base, self.head)
        self.observations = [item for pair in pairs.values() for item in pair]
        self.manifest = measure.make_manifest(self.context, self.base, self.head)
        self.context["output_manifest"] = graph.persist(self.context, "manifest.json", self.manifest)
        return self

    def validate(self):
        return measure.validate_observations(self.context, self.base, self.head, self.config,
                                             self.policy, self.manifest, self.observations)

    def summary(self):
        return measure.assess_observations(measure.with_cycle_ids(self.validate(), self.base, self.head),
                                           probe._configured_mutation(), self.policy, self.base["inventory"])

    def close(self):
        self.git.close()
        self.scratch.cleanup()


class InventoryTests(unittest.TestCase):
    def fixture(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        return fixture

    def recollect(self, fixture):
        """Real fresh evidence, so an alias test cannot pass by detecting staleness."""
        source = source_snapshot(Path(fixture.context["head_root"]), fixture.context["source"]["scope"])
        source.update(base=fixture.context["source"]["base"], head=fixture.context["source"]["head"])
        fixture.context["source"] = source
        raw = Path(tempfile.mkdtemp(prefix="fresh-", dir=fixture.root))
        fixture.context["run_root"] = str(raw)
        fixture.context["controller_sha256"] = measure.controller_digest(fixture.context["controller_root"])
        fixture.base = graph.parse_files(fixture.context, measure.inventory(fixture.context, "base", {}), fixture.config)
        fixture.head = graph.parse_files(fixture.context, measure.inventory(fixture.context, "head", {}), fixture.config)
        pairs = measure.collect_pair(fixture.context, fixture.config, fixture.base, fixture.head)
        fixture.observations = [item for pair in pairs.values() for item in pair]
        fixture.manifest = measure.make_manifest(fixture.context, fixture.base, fixture.head)
        fixture.context["output_manifest"] = graph.persist(fixture.context, "manifest.json", fixture.manifest)

    def test_fresh_cross_root_aliases_reject_different_names_and_noncode_inputs(self):
        for left, right, source_name, target_name in (
                ("base_root", "head_root", "a.py", "b.py"),
                ("base_root", "head_root", "approval.txt", "other-contract.txt"),
                ("base_root", "controller_root", "controller-copy.txt", "measure.py"),
                ("head_root", "controller_root", "controller-copy.txt", "measure.py")):
            with self.subTest(roots=(left, right), paths=(source_name, target_name)):
                fixture = self.fixture()
                fixture.git.write("controller-copy.txt", (SCRIPTS / "measure.py").read_bytes())
                fixture.base_sha = fixture.git.commit("fixture: source independent of controller")
                fixture.materialize()
                fixture.validate()
                source = Path(fixture.context[left]) / source_name
                target = Path(fixture.context[right]) / target_name
                target.unlink(missing_ok=True)
                os.link(source, target)
                self.assertTrue(os.path.samefile(source, target))
                self.recollect(fixture)
                with self.assertRaisesRegex(ValueError, "Shared mutable file identity"):
                    fixture.validate()
                before = source.read_bytes()
                target.write_bytes(before + b"\n# prove shared storage\n")
                self.assertEqual(source.read_bytes(), target.read_bytes())
                self.assertNotEqual(source.read_bytes(), before)

    def test_independent_equal_content_copies_survive_owned_head_write(self):
        fixture = self.fixture()
        fixture.git.write("controller-copy.txt", (SCRIPTS / "measure.py").read_bytes())
        fixture.base_sha = fixture.git.commit("fixture: equal bytes in independent copies")
        fixture.materialize()
        fixture.validate()
        base = Path(fixture.context["base_root"]) / "controller-copy.txt"
        head = Path(fixture.context["head_root"]) / "controller-copy.txt"
        controller = Path(fixture.context["controller_root"]) / "measure.py"
        original = base.read_bytes()
        self.assertEqual(original, head.read_bytes())
        self.assertEqual(original, controller.read_bytes())
        for one, other in ((base, head), (base, controller), (head, controller)):
            self.assertFalse(os.path.samefile(one, other))
        head.write_bytes(b"Owned head edit\n")
        self.assertEqual(base.read_bytes(), original)
        self.assertEqual(controller.read_bytes(), original)

    def test_owned_artifacts_cannot_alias_a_source_input(self):
        fixture = self.fixture().materialize()
        source = Path(fixture.context["head_root"]) / "a.py"
        target = Path(fixture.context["run_root"]) / "unregistered-alias.txt"
        os.link(source, target)
        with self.assertRaisesRegex(ValueError, "Shared mutable file identity"):
            fixture.validate()

    def test_one_discovery_owner_and_standalone_imports(self):
        self.assertIs(probe.code_files, measure.code_files)
        self.assertIs(probe.CODE_EXT, measure.CODE_EXT)
        fixture = self.fixture()
        for module in ("measure", "measure_graph", "probe"):
            fixture.git.run(sys.executable, "-B", "-c",
                            "import sys;sys.path.insert(0,%r);import %s" % (str(SCRIPTS), module))
        self.assertNotIn("import probe", (SCRIPTS / "measure.py").read_text())

    def test_inventory_retains_all_code_and_deliberate_exclusions(self):
        fixture = self.fixture()
        for name in ("nested/pkg/__init__.py", "nested/pkg/module.py", "module.mjs", "module.cjs",
                     "unsupported.go", "examples/example.py", "ignored.py"):
            fixture.git.write(name, "")
        fixture.git.write(".gitignore", ".ai/\nignored.py\n")
        fixture.git.run("git", "add", "--force", "ignored.py")
        fixture.git.write(".hidden/excluded.py", "")
        fixture.git.write("node_modules/excluded.py", "")
        fixture.build()
        before = copy.deepcopy(fixture.head["inventory"])
        self.assertEqual(before, measure.inventory(fixture.context, "head", before["changed_production"]))
        entries = {entry["path"]: entry for entry in before["entries"]}
        self.assertTrue({"module.mjs", "module.cjs", "unsupported.go", "ignored.py",
                         "examples/example.py", "nested/pkg/module.py"} <= entries.keys())
        self.assertEqual(entries["unsupported.go"]["parse_state"], "unsupported")
        self.assertEqual(entries["module.mjs"]["parse_state"], "pending")
        self.assertIsNone(entries["a.py"]["parser"])
        self.assertEqual(len(fixture.head["receipts"]), len(entries))
        excluded = {item["path"] for item in before["scope_exclusions"]}
        self.assertTrue({".git", ".hidden", "node_modules"} <= excluded)
        self.assertFalse(any("excluded.py" in name for name in entries))
        fixture.validate()

    def test_paths_reject_traversal_root_file_aliases_and_absolute_names(self):
        fixture = self.fixture()
        self.assertEqual(graph.input_path(fixture.git.root, ".", directory=True), fixture.git.root)
        for name in (".", "../a.py", "a/../b.py", "/a.py", "C:/a.py", "a//b.py", "./a.py", "a\\b.py"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                graph.input_path(fixture.git.root, name)
        bad = copy.deepcopy(fixture.config)
        bad["python_source_roots"] = ["missing"]
        with self.assertRaises(ValueError):
            measure.validate_config(bad, fixture.git.root)
        for change in (
                lambda c: c["coverage_policy"].update(changed_executable_line_floor_pct=True),
                lambda c: c.update(mutation_cap=1),
                lambda c: c["architecture_rules"].pop(),
                lambda c: c.update(extra=True),
                lambda c: c["approval_artifact"].update(path="."),
                lambda c: c["suites"][0].update(cwd="../")):
            bad = copy.deepcopy(fixture.config)
            change(bad)
            with self.subTest(config=bad), self.assertRaises((ValueError, OSError)):
                measure.validate_config(bad, fixture.git.root)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            graph.load_json('{"value":1,"value":2}')
        if os.name == "nt":
            (fixture.git.root / "nested").mkdir()
            bad = copy.deepcopy(fixture.config)
            bad["python_source_roots"] = ["nested", "NESTED"]
            with self.assertRaisesRegex(ValueError, "collision"):
                measure.validate_config(bad, fixture.git.root)

    def test_omitted_entry_digest_revision_and_changed_map_are_rejected(self):
        fixture = self.fixture().materialize()
        fixture.validate()
        original = copy.deepcopy(fixture.head)
        for modify in (
                lambda p: p["inventory"]["entries"].pop(),
                lambda p: p["inventory"].update(revision="base"),
                lambda p: p["receipts"].pop(),
                lambda p: p["receipts"][0].update(revision="base"),
                lambda p: p["inventory"].update(extra=True)):
            fixture.head = copy.deepcopy(original)
            modify(fixture.head)
            inv = fixture.head["inventory"]
            inv["digest"] = graph.digest({key: value for key, value in inv.items() if key != "digest"})
            with self.assertRaises(ValueError):
                fixture.validate()
        fixture.head = original
        for revision, changes in (("other", {}), ("base", {"a.py": [1]}),
                                  ("head", {"../a.py": [1]}), ("head", {"a.py": [True]})):
            with self.assertRaises(ValueError):
                measure.inventory(fixture.context, revision, changes)
        fixture.context["source"]["head"] = "0" * 40
        with self.assertRaises(ValueError):
            fixture.validate()

    def test_deleted_renamed_and_untracked_inputs_change_inventory(self):
        fixture = self.fixture().materialize()
        root = Path(fixture.context["head_root"])
        original = fixture.head["inventory"]
        (root / "a.py").rename(root / "renamed.py")
        (root / "new.py").write_text("# untracked\n")
        current = measure.inventory(fixture.context, "head", {})
        names = {entry["path"] for entry in current["entries"]}
        self.assertNotIn("a.py", names)
        self.assertTrue({"renamed.py", "new.py"} <= names)
        self.assertNotEqual(original["digest"], current["digest"])
        with self.assertRaisesRegex(ValueError, "stale"):
            fixture.validate()

    def test_real_link_is_failed_not_a_shortened_success(self):
        fixture = self.fixture().materialize()
        root = Path(fixture.context["head_root"])
        destination = fixture.root / "outside"
        destination.mkdir()
        (destination / "outside.py").write_text("pass\n")
        link = root / "linked"
        if os.name == "nt":
            fixture.git.run(os.environ["ComSpec"], "/c", "mklink", "/J", str(link), str(destination))
        else:
            link.symlink_to(destination, target_is_directory=True)
        self.addCleanup(lambda: os.rmdir(link) if os.name == "nt" else link.unlink())
        inv = measure.inventory(fixture.context, "head", {})
        self.assertEqual(inv["enumeration_state"], "failed")
        self.assertTrue(any(item["entry"] == "linked" for item in inv["enumeration_errors"]))
        with self.assertRaises(OSError):
            measure.code_files(root)

    def test_real_read_and_walk_errors_are_enumerated(self):
        fixture = self.fixture().materialize()
        root = Path(fixture.context["head_root"])
        if os.name != "nt":
            # Real broken link is a portable stat/traversal failure; Windows below
            # additionally proves mandatory-sharing I/O and directory-list errors.
            (root / "broken.py").symlink_to(root / "missing.py")
            inv = measure.inventory(fixture.context, "head", {})
            self.assertEqual(inv["enumeration_state"], "failed")
            self.assertTrue(inv["enumeration_errors"])
            return
        create = ctypes.windll.kernel32.CreateFileW
        create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
                           ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
        create.restype = ctypes.c_void_p
        close = ctypes.windll.kernel32.CloseHandle
        close.argtypes = [ctypes.c_void_p]
        directory = root / "locked"
        directory.mkdir()
        (directory / "file.py").write_text("pass\n")
        for path, flags, expected in ((root / "a.py", 0x80, "read"), (directory, 0x02000000, "walk")):
            handle = create(str(path), 0x80000000, 0, None, 3, flags, None)
            self.assertNotEqual(handle, ctypes.c_void_p(-1).value)
            try:
                inv = measure.inventory(fixture.context, "head", {})
                self.assertEqual(inv["enumeration_state"], "failed")
                self.assertIn(expected, {item["operation"] for item in inv["enumeration_errors"]})
                with self.assertRaises(OSError):
                    measure.code_files(root)
            finally:
                self.assertTrue(close(handle))


if __name__ == "__main__":
    unittest.main()
