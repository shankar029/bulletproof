"""Real qualified-tool inputs, independent byte copies and public probe fixtures."""

import copy
import json
import os
from pathlib import Path
import shutil
import sys
import unittest

from helpers import SCRIPTS
from test_measure_inventory import Q1Fixture
import measure
import measure_graph as graph


EVIDENCE = SCRIPTS.parent / ".ai/workflow-reliability/evidence"


def native_tools():
    manifest = graph.load_json((EVIDENCE / "q2-tools-manifest.json").read_bytes())
    result = {}
    for name in ("ruff", "jscpd"):
        binding = copy.deepcopy(manifest["tools"][name]["binding"])
        for ref in [binding["help"], binding["configuration"], *binding["qualification"]]:
            ref["path"] = Path(ref["path"]).relative_to(EVIDENCE).as_posix()
        binding["qualification"].append(graph.artifact(EVIDENCE, "q2-tools-runtime-bindings.json"))
        result[name] = binding
    return result


class ToolRootTests(unittest.TestCase):
    def fixture(self, *, repository_originals=False):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        fixture.config["tools"] = native_tools()
        root = EVIDENCE
        if repository_originals:
            root = fixture.git.root / ".ai/tool-evidence"
            root.mkdir(parents=True)
            names = set()
            for tool in fixture.config["tools"].values():
                names.update(ref["path"] for ref in [tool["help"], tool["configuration"],
                                                    *tool["qualification"]])
            for name in names:
                shutil.copyfile(EVIDENCE / name, root / name)
            (root / "not-selected.txt").write_text("Must not be staged", encoding="utf-8")
        fixture.config["tool_artifact_root"] = str(root)
        fixture.save_config()
        return fixture

    def context(self, fixture):
        result = {}
        for key in ("base_root", "head_root", "controller_root", "run_root"):
            path = fixture.root / key
            path.mkdir()
            result[key] = str(path)
        result["toolset_sha256"] = measure.toolset_digest(fixture.config)
        return result

    def test_empty_mode_and_conditional_root_validation(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        measure.validate_config(fixture.config, fixture.git.root)
        self.assertEqual(measure.toolset_digest(fixture.config),
                         graph.digest({"python_parser": graph.parser_digest()}))
        fixture.config["tool_artifact_root"] = str(EVIDENCE)
        with self.assertRaisesRegex(ValueError, "exactly"):
            measure.validate_config(fixture.config, fixture.git.root)
        fixture.config.pop("tool_artifact_root")
        fixture.config["tools"] = native_tools()
        with self.assertRaisesRegex(ValueError, "exactly"):
            measure.validate_config(fixture.config, fixture.git.root)
        for value in ("", None, True, 1, EVIDENCE):
            fixture.config["tool_artifact_root"] = value
            with self.subTest(root=value), self.assertRaisesRegex(ValueError, "directory string"):
                measure.validate_config(fixture.config, fixture.git.root)

    def test_actual_opaque_bytes_shared_artifact_and_external_resources(self):
        fixture = self.fixture(repository_originals=True)
        measure.validate_config(fixture.config, fixture.git.root)
        context = self.context(fixture)
        before = {ref["path"]: graph.artifact(fixture.config["tool_artifact_root"], ref["path"])
                  for ref in measure.tool_artifacts(fixture.config)}
        measure.stage_tool_inputs(context, fixture.config)
        self.assertEqual(measure.toolset_digest(fixture.config, context["run_root"]),
                         context["toolset_sha256"])
        self.assertFalse((Path(context["run_root"]) / "not-selected.txt").exists())
        self.assertEqual(len([name for name in before if name == "q2-tools-runtime-bindings.json"]), 1)
        for name, ref in before.items():
            original = Path(fixture.config["tool_artifact_root"]) / name
            staged = Path(context["run_root"]) / name
            self.assertEqual(original.read_bytes(), staged.read_bytes())
            self.assertFalse(os.path.samefile(original, staged))
            self.assertEqual(graph.artifact(fixture.config["tool_artifact_root"], name), ref)
        with self.assertRaises(FileExistsError):
            measure.stage_tool_inputs(context, fixture.config)

    def test_missing_changed_original_and_copy_have_no_fallback(self):
        fixture = self.fixture(repository_originals=True)
        context = self.context(fixture)
        measure.stage_tool_inputs(context, fixture.config)
        name = fixture.config["tools"]["ruff"]["help"]["path"]
        original = Path(fixture.config["tool_artifact_root"]) / name
        staged = Path(context["run_root"]) / name
        content = original.read_bytes()
        original.unlink()
        with self.assertRaises(OSError):
            measure.toolset_digest(fixture.config, context["run_root"])
        original.write_bytes(content)
        staged.write_bytes(content + b"\nchanged")
        with self.assertRaisesRegex(ValueError, "bytes mismatch"):
            measure.toolset_digest(fixture.config, context["run_root"])
        staged.write_bytes(content)
        original.write_bytes(content + b"\nchanged")
        with self.assertRaisesRegex(ValueError, "bytes mismatch"):
            measure.toolset_digest(fixture.config, context["run_root"])

    def test_duplicate_prefix_reserved_namespace_and_hardlinks_reject(self):
        fixture = self.fixture(repository_originals=True)
        binding = fixture.config["tools"]["ruff"]
        binding["qualification"].append(copy.deepcopy(binding["qualification"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            measure.tool_artifacts(fixture.config)
        binding["qualification"].pop()
        for names in (["a", "a/b"], ["a", "a-b", "a/b"], ["manifest.json", "manifest.json"],
                      ["A.json", "a.json"] if os.name == "nt" else ["same", "same"]):
            with self.subTest(names=names), self.assertRaises(ValueError):
                measure._path_partition(names)
        root = Path(fixture.config["tool_artifact_root"])
        original = root / binding["help"]["path"]
        os.link(original, root / "alias.log")
        self.assertTrue(os.path.samefile(original, root / "alias.log"))
        with self.assertRaisesRegex(ValueError, "independent regular"):
            measure.tool_artifacts(fixture.config)

    def test_overlap_before_snapshot_exclusions_and_ancestor_allowed(self):
        fixture = self.fixture(repository_originals=True)
        original = Path(fixture.config["tool_artifact_root"]) / fixture.config["tools"]["ruff"]["help"]["path"]
        output = original.relative_to(fixture.git.root).as_posix()
        with self.assertRaisesRegex(ValueError, "overlaps"):
            measure.check_tool_outputs(fixture.config, fixture.git.root, [output])
        with self.assertRaisesRegex(ValueError, "overlaps"):
            measure.check_tool_outputs(fixture.config, fixture.git.root, [".ai/tool-evidence"])
        refs = measure.check_tool_outputs(fixture.config, fixture.git.root,
                                          [".ai/tool-evidence/runs/new/measurement/manifest.json"])
        self.assertTrue(refs)

    def test_strict_artifact_shapes_namespace_and_forged_help_hash(self):
        fixture = self.fixture(repository_originals=True)
        baseline = copy.deepcopy(fixture.config)
        for name in ("../escape", "/absolute", "C:/drive", "back\\slash",
                     ".", "x//y", "trailing. ", "base/forbidden.json", "manifest.json"):
            fixture.config = copy.deepcopy(baseline)
            ref = fixture.config["tools"]["ruff"]["help"]
            ref["path"] = name
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                measure.validate_config(fixture.config, fixture.git.root)
        for key, value in (("bytes", True), ("bytes", -1), ("sha256", "X" * 64),
                           ("extra", "unknown")):
            fixture.config = copy.deepcopy(baseline)
            fixture.config["tools"]["ruff"]["help"][key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                measure.validate_config(fixture.config, fixture.git.root)
        fixture.config = copy.deepcopy(baseline)
        root = Path(fixture.config["tool_artifact_root"])
        name = fixture.config["tools"]["ruff"]["help"]["path"]
        (root / name).write_bytes((root / name).read_bytes() + b"\nforged but rehashed")
        fixture.config["tools"]["ruff"]["help"] = graph.artifact(root, name)
        with self.assertRaisesRegex(ValueError, "qualified version"):
            measure.validate_config(fixture.config, fixture.git.root)

    def test_actual_executable_copy_is_external_and_tamper_rejects(self):
        fixture = self.fixture()
        binary = fixture.root / "ruff.exe"
        shutil.copyfile(fixture.config["tools"]["ruff"]["executable"], binary)
        fixture.config["tools"]["ruff"]["executable"] = str(binary)
        measure.validate_config(fixture.config, fixture.git.root)
        with binary.open("ab") as stream:
            stream.write(b"changed pinned executable")
        with self.assertRaisesRegex(ValueError, "external input changed"):
            measure.validate_config(fixture.config, fixture.git.root)

    def test_actual_junction_root_rejects(self):
        fixture = self.fixture(repository_originals=True)
        original = Path(fixture.config["tool_artifact_root"])
        junction = fixture.root / "junction"
        if os.name == "nt":
            fixture.git.run("cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(original))
            self.assertTrue(junction.is_junction())
        else:
            junction.symlink_to(original, target_is_directory=True)
            self.assertTrue(junction.is_symlink())
        fixture.config["tool_artifact_root"] = str(junction)
        with self.assertRaises(ValueError):
            measure.validate_config(fixture.config, fixture.git.root)
        junction.unlink() if os.name != "nt" else junction.rmdir()

    def test_actual_symlink_root_rejects(self):
        fixture = self.fixture(repository_originals=True)
        original = Path(fixture.config["tool_artifact_root"])
        link = fixture.root / "symlink"
        link.symlink_to(original, target_is_directory=True)
        self.assertTrue(link.is_symlink())
        fixture.config["tool_artifact_root"] = str(link)
        with self.assertRaises(ValueError):
            measure.validate_config(fixture.config, fixture.git.root)
        link.unlink()

    def test_rehashed_copy_and_changed_root_cannot_keep_context_binding(self):
        fixture = self.fixture(repository_originals=True)
        context = self.context(fixture)
        measure.stage_tool_inputs(context, fixture.config)
        old_digest = context["toolset_sha256"]
        root = Path(fixture.config["tool_artifact_root"])
        relocated = fixture.root / "other-originals"
        relocated.mkdir()
        for ref in measure.tool_artifacts(fixture.config):
            shutil.copyfile(root / ref["path"], relocated / ref["path"])
        fixture.config["tool_artifact_root"] = str(relocated)
        self.assertNotEqual(measure.toolset_digest(fixture.config, context["run_root"]), old_digest)
        # Updating a copy hash and its config declaration is not qualified help.
        name = fixture.config["tools"]["ruff"]["help"]["path"]
        staged = Path(context["run_root"]) / name
        data = staged.read_bytes() + b"\nmodified"
        staged.write_bytes(data)
        (relocated / name).write_bytes(data)
        fixture.config["tools"]["ruff"]["help"] = graph.artifact(relocated, name)
        with self.assertRaisesRegex(ValueError, "qualified version"):
            measure.toolset_digest(fixture.config, context["run_root"])

    def test_real_two_revision_probe_with_repository_and_external_originals(self):
        for repository_originals in (True, False):
            with self.subTest(repository_originals=repository_originals):
                fixture = self.fixture(repository_originals=repository_originals)
                fixture.git.write("a.py", "import b\n")
                fixture.git.commit("actual head with source-bound qualified tool originals")
                fixture.git.run(sys.executable, "-B", str(SCRIPTS / "probe.py"),
                                "--repo", str(fixture.git.root), "--slug", "tool-root",
                                "--base", fixture.base_sha, "--skip-mutation",
                                "--measurement-config", str(fixture.git.root / "measurement.json"),
                                expected=1, timeout=180)
                report = graph.load_json((fixture.git.root / ".ai/tool-root/metrics.json").read_bytes())
                self.assertEqual(report["completeness"], "incomplete")
                self.assertEqual(set(report["metrics"]), set(measure.REQUIRED))
                self.assertGreaterEqual(len(report["inventories"]["base"]["entries"]), 3)
                rows = [row for row in report["artifact_manifest"]["inputs"] if row["role"] == "qualification"]
                self.assertEqual(len(rows), len(measure.tool_artifacts(fixture.config)))
                self.assertTrue(all(row["revision"] is None for row in rows))
                archive = fixture.git.root / ".ai/tool-root/evidence/runs" / report["run_id"] / "measurement"
                for row in rows:
                    self.assertEqual(graph.artifact(archive, row["artifact"]["path"]), row["artifact"])
                if repository_originals:
                    name = ".ai/tool-evidence/" + fixture.config["tools"]["ruff"]["help"]["path"]
                    self.assertIn(name, report["source"]["files"])
                destination = os.environ.get("Q2_ADAPTER_RECORDS")
                if destination:
                    name = "repository" if repository_originals else "external"
                    root = graph.root_path(destination)
                    raw = {revision: graph.load_json((archive / revision / "graph.json").read_bytes())
                           for revision in ("base", "head")}
                    with (root / (name + ".json")).open("x", encoding="utf-8") as stream:
                        json.dump({"scope": "Actual fixture report/graph records, not portable live Context",
                                   "report": report, "raw_graph": raw}, stream, ensure_ascii=False, indent=2)
                print("Q2 actual two-revision fixture verified; repository originals =",
                      repository_originals, "; qualification artifacts =", len(rows), flush=True)


if __name__ == "__main__":
    unittest.main()
