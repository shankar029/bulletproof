"""Focused execution of shipped bindings against the already-qualified tools."""

import copy
import json
import os
from pathlib import Path
import shutil
import sys
import unittest

from helpers import SCRIPTS
from test_measure_inventory import Q1Fixture
from test_measure_q2 import EVIDENCE, native_tools
import measure
import measure_graph as graph
import probe
from evidence import source_snapshot


def source_tools(names=("typescript", "lizard", "vulture")):
    roots = graph.load_json((EVIDENCE / "q2-tools-source-roots.json").read_bytes())
    runtime = graph.load_json((EVIDENCE / "q2-tools-runtime-bindings.json").read_bytes())
    values = {
        "typescript": ("5.9.3", "typescript-compiler-5-9-3-v1", "node", "lib/typescript.js"),
        "lizard": ("1.24.0", "lizard-strict-text-1-24-0-v1", "python", "lizard.py"),
        "vulture": ("2.16", "vulture-scan-2-16-v1", "python", "vulture/core.py"),
    }
    result = {}
    for name in names:
        version, api, executor, module = values[name]
        artifacts = ["q2-tools-runtime-bindings.json", "q2-tools-source-roots.json",
                     "q2-tools-source-extracted-pins.json", "q2-tools-source-" + name + "-results.json"]
        if name != "typescript":
            artifacts.append("q2-tools-source-python-provenance-" + name + ".json")
        if name == "lizard":
            artifacts.append("q2-tools-source-lizard-boundaries-results.json")
        result[name] = {
            "executable": str(Path(runtime["executors"][executor]["path"]).resolve()),
            "sha256": runtime["executors"][executor]["sha256"],
            "module_path": str(Path(roots[name]) / module),
            "observed_version": version, "qualified_api": api,
            "configuration": graph.artifact(EVIDENCE, "q2-tools-source-roots.json"),
            "help": graph.artifact(EVIDENCE, "q2-tools-source-" + name + "-help.stdout.log"),
            "qualification": [graph.artifact(EVIDENCE, item) for item in artifacts],
        }
    return result


class SourceBindingTests(unittest.TestCase):
    def fixture(self, names=("typescript", "lizard", "vulture")):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        fixture.config["tools"] = source_tools(names)
        fixture.config["tool_artifact_root"] = str(EVIDENCE)
        fixture.save_config()
        return fixture

    def context(self, fixture, *, revisions=False):
        context = {"run_id": "source-binding-development"}
        for key in ("base_root", "head_root", "controller_root", "run_root"):
            path = fixture.root / key
            if revisions and key in {"base_root", "head_root"}:
                if key == "base_root":
                    probe._copy_subject(fixture.git.root, path, fixture.base_sha)
                else:
                    source = source_snapshot(fixture.git.root, {
                        "directories": ["."], "excluded_outputs": [{"path": ".git", "reason": "Git metadata"}]})
                    probe._copy_subject(fixture.git.root, path, measure.git_head(fixture.git.root), source)
            else:
                path.mkdir()
            context[key] = str(path)
        controller = Path(context["controller_root"])
        for name in ("measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py"):
            shutil.copyfile(SCRIPTS / name, controller / name)
        context["controller_sha256"] = measure.controller_digest(controller)
        context["toolset_sha256"] = measure.toolset_digest(fixture.config)
        measure.stage_tool_inputs(context, fixture.config)
        refs = measure.tool_artifacts(fixture.config)
        manifest = {"run_id": context["run_id"], "root": context["run_root"],
                    "inputs": [{"artifact": ref, "role": "qualification", "revision": None} for ref in refs],
                    "reserved_outputs": [ref["path"] for ref in refs] + ["manifest.json"] + [
                        name for tool in fixture.config["tools"] for revision in ("base", "head")
                        for name in measure.source_binding_paths(tool, revision)]}
        context["output_manifest"] = graph.persist(context, "manifest.json", manifest)
        if os.environ.get("Q2_SOURCE_RECORDS"):
            def preserve():
                records = {}
                for name in manifest["reserved_outputs"]:
                    path = Path(context["run_root"]) / name
                    if "/binding/" in name and path.is_file():
                        records[name] = graph.load_json(path.read_bytes())
                self.capture("raw-" + graph.digest(self._testMethodName)[:12],
                             {"test": self.id(), "artifacts": records})
            self.addCleanup(preserve)
        return context

    def capture(self, label, records):
        destination = os.environ.get("Q2_SOURCE_RECORDS")
        if destination:
            root = graph.root_path(destination)
            with (root / (label + ".json")).open("x", encoding="utf-8") as stream:
                json.dump(records, stream, ensure_ascii=False, indent=2)

    def relocate(self, fixture, names):
        root = fixture.root / "originals"
        root.mkdir()
        for ref in measure.tool_artifacts(fixture.config):
            shutil.copyfile(EVIDENCE / ref["path"], root / ref["path"])
        roots = graph.load_json((root / "q2-tools-source-roots.json").read_bytes())
        original = copy.deepcopy(roots)
        for name in names:
            roots[name] = str(fixture.root / (name + "-package"))
            Path(roots[name]).mkdir()
        pins = graph.load_json((root / "q2-tools-source-extracted-pins.json").read_bytes())
        for pin in pins:
            path = Path(pin["path"])
            for name in names:
                if path.is_relative_to(Path(original[name])):
                    target = Path(roots[name]) / path.relative_to(Path(original[name]))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, target)
        (root / "relocated-roots.json").write_text(json.dumps(roots), encoding="utf-8")
        fixture.config["tool_artifact_root"] = str(root)
        for name, binding in fixture.config["tools"].items():
            binding["module_path"] = str(Path(roots[name]) / Path(
                binding["module_path"]).relative_to(Path(original[name])))
            binding["configuration"] = graph.artifact(root, "relocated-roots.json")
        return roots

    def test_actual_three_tools_at_two_git_revisions_with_import_provenance(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "value = 2\n")
        fixture.git.commit("Actual head for shared source-tool bindings")
        measure.validate_config(fixture.config, fixture.git.root)
        context = self.context(fixture, revisions=True)
        self.assertNotEqual(measure.git_head(context["base_root"]), measure.git_head(context["head_root"]))
        records = []
        for revision in ("base", "head"):
            for tool in ("typescript", "lizard", "vulture"):
                record = measure.inspect_source_binding(context, fixture.config, tool, revision)
                observed = record["observed"]
                command = graph.load_json((Path(context["run_root"]) / record["command"]["path"]).read_bytes())
                self.assertEqual(command["returncode"], 0)
                self.assertEqual(command["stderr"], "")
                self.assertEqual(command["toolset_sha256"], context["toolset_sha256"])
                self.assertTrue(observed["imports"])
                if tool == "typescript":
                    self.assertEqual(observed["runtime"]["arch"], "arm64")
                    self.assertEqual(observed["smoke"]["symbol"], "answer")
                    self.assertEqual(observed["smoke"]["diagnostics"], [])
                    self.assertTrue(any(item["path"].endswith("lib.esnext.full.d.ts")
                                        for item in observed["resources_read"]))
                elif tool == "lizard":
                    self.assertEqual(observed["smoke"]["functions"][0]["cyclomatic_complexity"], 2)
                    self.assertEqual(observed["smoke"]["readers"][".jsx"], "TSXReader")
                    self.assertEqual(observed["runtime"]["pathspec_backend"], "simple")
                else:
                    self.assertEqual(observed["smoke"]["pre_report_exit"], 0)
                    self.assertTrue(any(item["confidence"] == 90 for item in observed["smoke"]["findings"]))
                    self.assertTrue(observed["resources_read"])
                records.append({"revision": revision, **record, "raw_command": command})
                print("Completed actual binding smoke:", revision, tool, flush=True)
        self.capture("two-revisions", records)
        self.assertEqual(measure.toolset_digest(fixture.config, context["run_root"]),
                         context["toolset_sha256"])

    def test_environment_preload_and_python_path_are_not_execution_inputs(self):
        fixture = self.fixture(("typescript", "vulture"))
        context = self.context(fixture)
        evil = fixture.root / "preload.cjs"
        marker = fixture.root / "preload-ran"
        evil.write_text("require('node:fs').writeFileSync(" + json.dumps(str(marker)) + ", 'ran');",
                        encoding="utf-8")
        python_hook = fixture.root / "sitecustomize.py"
        python_marker = fixture.root / "python-hook-ran"
        python_hook.write_text("open(" + repr(str(python_marker)) + ", 'w').write('ran')", encoding="utf-8")
        changed = {"NODE_OPTIONS": "--require " + str(evil), "NODE_PATH": str(fixture.root),
                   "PYTHONPATH": str(fixture.root), "PYTHONSTARTUP": str(python_hook)}
        previous = {name: os.environ.get(name) for name in changed}
        records = []
        try:
            os.environ.update(changed)
            for tool in ("typescript", "vulture"):
                record = measure.inspect_source_binding(context, fixture.config, tool, "head")
                command = graph.load_json((Path(context["run_root"]) / record["command"]["path"]).read_bytes())
                self.assertTrue(set(changed) <= set(command["environment_delta"]["removed_names"]))
                records.append({"tool": tool, "observed": record["observed"], "raw_command": command})
                print("Completed real poisoned-environment binding:", tool, flush=True)
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
        self.assertFalse(marker.exists())
        self.assertFalse(python_marker.exists())
        self.capture("environment", records)

    def test_missing_qualification_module_and_unknown_settings_reject(self):
        fixture = self.fixture(("typescript",))
        binding = fixture.config["tools"]["typescript"]
        saved = copy.deepcopy(binding)
        binding["qualification"] = [ref for ref in binding["qualification"]
                                     if ref["path"] != "q2-tools-source-extracted-pins.json"]
        with self.assertRaisesRegex(ValueError, "complete original"):
            measure.validate_config(fixture.config, fixture.git.root)
        fixture.config["tools"]["typescript"] = copy.deepcopy(saved)
        fixture.config["tools"]["typescript"]["module_path"] = str(fixture.root / "typescript.js")
        with self.assertRaisesRegex(ValueError, "module does not match"):
            measure.validate_config(fixture.config, fixture.git.root)
        fixture.config["tools"]["typescript"] = copy.deepcopy(saved)
        fixture.config["tools"]["typescript"]["configuration"] = graph.artifact(
            EVIDENCE, "q2-tools-source-typescript-results.json")
        with self.assertRaisesRegex(ValueError, "explicit qualified root map"):
            measure.validate_config(fixture.config, fixture.git.root)
        fixture.config["tools"]["typescript"] = copy.deepcopy(saved)
        fixture.config["tools"]["typescript"]["observed_version"] = "7.0.2"
        with self.assertRaisesRegex(ValueError, "qualified version"):
            measure.validate_config(fixture.config, fixture.git.root)

    def test_all_resources_not_just_loaded_module_are_bound(self):
        fixture = self.fixture(("typescript",))
        roots = self.relocate(fixture, ("typescript",))
        context = self.context(fixture)
        record = measure.inspect_source_binding(context, fixture.config, "typescript", "head")
        self.assertEqual(record["observed"]["smoke"]["symbol"], "answer")
        resource = Path(roots["typescript"]) / "lib/lib.es5.d.ts"
        with resource.open("ab") as stream:
            stream.write(b"\n// changed owned test copy\n")
        with self.assertRaisesRegex(ValueError, "resource bytes changed"):
            measure.toolset_digest(fixture.config, context["run_root"])

    def test_unqualified_python_import_rejects_before_module_execution(self):
        fixture = self.fixture(("vulture",))
        roots = self.relocate(fixture, ("lizard", "vulture", "pygments", "pathspec"))
        marker = fixture.root / "unqualified-module-ran"
        module = Path(roots["pathspec"]) / "re2.py"
        module.write_text("open(" + repr(str(marker)) + ", 'w').write('ran')", encoding="utf-8")
        context = self.context(fixture)
        with self.assertRaisesRegex(ValueError, "Unqualified import/resource"):
            measure.inspect_source_binding(context, fixture.config, "vulture", "head")
        self.assertFalse(marker.exists())
        name = measure.source_binding_paths("vulture", "head")[2]
        command = graph.load_json((Path(context["run_root"]) / name).read_bytes())
        self.assertNotEqual(command["returncode"], 0)
        self.assertIn("re2.py", command["stderr"])

    def test_raw_staging_reservation_and_controller_remain_authoritative(self):
        fixture = self.fixture(("typescript",))
        context = self.context(fixture)
        with self.assertRaisesRegex(ValueError, "no explicit binding"):
            measure.inspect_source_binding(context, fixture.config, "vulture", "head")
        manifest = graph.load_json((Path(context["run_root"]) / "manifest.json").read_bytes())
        manifest["reserved_outputs"].remove(measure.source_binding_paths("typescript", "head")[1])
        context["output_manifest"] = graph.persist(context, "without-reservation.json", manifest)
        with self.assertRaisesRegex(ValueError, "predeclared"):
            measure.inspect_source_binding(context, fixture.config, "typescript", "head")
        context["output_manifest"] = graph.artifact(context["run_root"], "manifest.json")
        controller = Path(context["controller_root"]) / "measure.py"
        with controller.open("ab") as stream:
            stream.write(b"\n# changed controller copy\n")
        with self.assertRaisesRegex(ValueError, "controller changed"):
            measure.inspect_source_binding(context, fixture.config, "typescript", "head")

    def test_qualification_ownership_rejects_rehashed_manifests_before_launch(self):
        fixture = self.fixture(("typescript",))
        measure.validate_config(fixture.config, fixture.git.root)
        context = self.context(fixture)
        root = Path(context["run_root"])
        original_ref = context["output_manifest"]
        original = graph.load_json((root / original_ref["path"]).read_bytes())
        selected = original["inputs"][0]["artifact"]["path"]
        extra = graph.persist(context, "r1-extra.json", {"purpose": "unselected input fixture"})
        cases = []

        def altered(label):
            manifest = copy.deepcopy(original)
            cases.append((label, manifest))
            return manifest

        altered("missing-row")["inputs"].pop(0)
        altered("missing-all-rows")["inputs"].clear()
        altered("wrong-role")["inputs"][0]["role"] = "command"
        altered("wrong-revision")["inputs"][0]["revision"] = "head"
        altered("duplicate-row")["inputs"].append(copy.deepcopy(original["inputs"][0]))
        altered("changed-hash")["inputs"][0]["artifact"]["sha256"] = "0" * 64
        altered("changed-length")["inputs"][0]["artifact"]["bytes"] += 1
        row = altered("noninteger-length")["inputs"][0]
        row["artifact"]["bytes"] = float(row["artifact"]["bytes"])
        altered("changed-path")["inputs"][0]["artifact"]["path"] = "r1-other.json"
        altered("extra-row-field")["inputs"][0]["extra"] = True
        altered("missing-input-reservation")["reserved_outputs"].remove(selected)
        altered("duplicate-input-reservation")["reserved_outputs"].append(selected)
        altered("prefix-input-reservation")["reserved_outputs"].append(selected + "/child")
        row = copy.deepcopy(original["inputs"][0])
        row["artifact"]["path"] += "/child"
        altered("prefix-input-row")["inputs"].append(row)
        row = copy.deepcopy(original["inputs"][0])
        row["artifact"]["sha256"] = "0" * 64
        altered("conflicting-input-row")["inputs"].append(row)
        manifest = altered("unselected-qualification")
        manifest["inputs"].append({"artifact": extra, "role": "qualification", "revision": None})
        manifest["reserved_outputs"].append(extra["path"])
        manifest = altered("cross-namespace-prefix")
        manifest["inputs"].append({"artifact": {**extra, "path": "r1-nested"},
                                   "role": "command", "revision": "head"})
        manifest["reserved_outputs"].append("r1-nested/child")
        if os.name == "nt":
            altered("case-collision")["reserved_outputs"].append(selected.upper())
        altered("malformed-input-list")["inputs"] = None
        altered("malformed-reservation-list")["reserved_outputs"] = None

        active, launches, writes = [False], [], []

        def audit(event, args):
            if not active[0]:
                return
            if event == "subprocess.Popen":
                launches.append({"executable": str(args[0]), "argv": args[1], "cwd": str(args[2])})
            elif event == "open" and isinstance(args[0], str) and isinstance(args[2], int):
                path = Path(args[0])
                if path.is_relative_to(root) and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
                    writes.append({"path": str(path), "mode": args[1], "flags": args[2]})

        sys.addaudithook(audit)
        records = []
        try:
            for index, (label, manifest) in enumerate(cases):
                with self.subTest(case=label):
                    name = "r1-manifest-" + str(index) + ".json"
                    if isinstance(manifest["reserved_outputs"], list):
                        manifest["reserved_outputs"].append(name)
                    context["output_manifest"] = graph.persist(context, name, manifest)
                    self.assertEqual(graph.artifact(root, name), context["output_manifest"])
                    self.assertNotEqual(original_ref["sha256"], context["output_manifest"]["sha256"])
                    launches.clear()
                    writes.clear()
                    active[0] = True
                    try:
                        with self.assertRaises(ValueError) as error:
                            measure.inspect_source_binding(context, fixture.config, "typescript", "head")
                    finally:
                        active[0] = False
                    present = [name for name in measure.source_binding_paths("typescript", "head")
                               if (root / name).exists()]
                    records.append({"case": label, "manifest": manifest,
                                    "manifest_ref": context["output_manifest"], "error": str(error.exception),
                                    "launches": list(launches), "writes": list(writes),
                                    "outputs_present": present})
                    self.assertEqual(launches, [])
                    self.assertEqual(writes, [])
                    self.assertEqual(present, [])
                    print("Completed real ownership rejection:", label, flush=True)
            context["output_manifest"] = original_ref
            active[0] = True
            try:
                valid = measure.inspect_source_binding(context, fixture.config, "typescript", "base")
            finally:
                active[0] = False
            self.assertEqual(len(launches), 1)
            self.assertTrue(writes)
            self.assertEqual(valid["observed"]["smoke"]["symbol"], "answer")
            self.capture("r1-valid-control", {"observation": valid, "launches": launches, "writes": writes})
        finally:
            active[0] = False
            self.capture("r1-ownership", records)

    def test_empty_q1_and_native_bindings_still_validate(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        measure.validate_config(fixture.config, fixture.git.root)
        self.assertEqual(measure.toolset_digest(fixture.config),
                         graph.digest({"python_parser": graph.parser_digest()}))
        fixture.config["tools"] = native_tools()
        fixture.config["tool_artifact_root"] = str(EVIDENCE)
        measure.validate_config(fixture.config, fixture.git.root)
        self.assertEqual(set(measure._qualified_inputs(fixture.config)), {"jscpd", "ruff"})


if __name__ == "__main__":
    unittest.main()
