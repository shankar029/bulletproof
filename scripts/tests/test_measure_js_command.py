"""Real fixed-command producer checks, not measurement/replay acceptance."""

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import uuid

from helpers import SCRIPTS, run_capture
from test_measure_inventory import Q1Fixture
from test_measure_q2 import EVIDENCE
from test_measure_source_bindings import source_tools
import measure
import measure_graph as graph


class JSCommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = Q1Fixture()
        cls.addClassCleanup(fixture.close)
        fixture.config["tools"] = source_tools(("typescript",))
        fixture.config["tool_artifact_root"] = str(EVIDENCE)
        fixture.git.write("source.mjs", "import { writeFileSync } from 'node:fs';\n"
                          "writeFileSync('executed-subject.txt', 'unexpected');\n"
                          "export const flag = true;\n")
        fixture.save_config()
        fixture.build()
        shutil.copyfile(SCRIPTS / "measure_js.mjs",
                        Path(fixture.context["controller_root"]) / "measure_js.mjs")
        fixture.context["controller_sha256"] = measure.controller_digest(
            fixture.context["controller_root"], include_js=True)
        fixture.context["toolset_sha256"] = measure.toolset_digest(fixture.config)
        cls.fixture = fixture
        cls.qualified = measure._qualified_inputs(fixture.config)["typescript"]
        print("Prepared real JS command subjects and qualified TypeScript", flush=True)

    def request(self, revision="head"):
        context = copy.deepcopy(self.fixture.context)
        context["run_root"] = tempfile.mkdtemp(prefix="command-", dir=self.fixture.root)
        measure.stage_tool_inputs(context, self.fixture.config)
        inventory = measure.inventory(context, revision, {}, include_js=True)
        refs = measure.tool_artifacts(self.fixture.config)
        reserved = [ref["path"] for ref in refs] + [
            "js-preflight.json", "js-produced.json", "manifest.json"]
        for side in ("base", "head"):
            reserved += [f"{side}/js/{name}.json" for name in ("request", "command", "result", "symbols")]
        preflight = {"run_id": context["run_id"], "root": context["run_root"],
                     "inputs": [{"artifact": ref, "role": "qualification", "revision": None}
                                for ref in refs], "reserved_outputs": sorted(reserved)}
        context["output_manifest"] = graph.persist(context, "js-preflight.json", preflight)
        qualified = self.qualified
        resources = [{"path": Path(pin["path"]).relative_to(
            qualified["source"]["roots"]["typescript"]).as_posix(),
            "qualified_path": pin["path"], "sha256": pin["sha256"], "bytes": pin["bytes"]}
            for pin in qualified["source"]["resources"]]
        parser = graph.digest({
            "semantic_version": "typescript-shared-v1",
            "adapter_sha256": hashlib.sha256((SCRIPTS / "measure_js.mjs").read_bytes()).hexdigest(),
            "compiler_version": "5.9.3", "module_path": qualified["binding"]["module_path"],
            "resources": sorted(resources, key=lambda item: item["path"]),
            "runtime": {"executable": qualified["binding"]["executable"],
                        "sha256": qualified["binding"]["sha256"],
                        "version": "v24.11.1", "architecture": "arm64"},
            "options": qualified["source"]["settings"]})
        binding = {"semantic_version": "typescript-shared-v1", "run_id": context["run_id"],
                   "revision": revision, "git_revision": context["source"][revision],
                   "inventory_sha256": inventory["digest"], "source_sha256": inventory["source_sha256"],
                   "parser_sha256": parser, "toolset_sha256": context["toolset_sha256"],
                   "settings_sha256": graph.digest({
                       "compiler_options": qualified["source"]["settings"],
                       "semantic_version": "typescript-shared-v1", "js_entrypoints": []}),
                   "policy_sha256": context["policy_sha256"]}
        inputs = [{"scope": "subject", **{key: entry[key] for key in ("path", "sha256", "bytes")}}
                  for entry in inventory["entries"] if entry["suffix"] in measure.JS_EXT]
        inputs += [{"scope": "head-contract", **ref} for ref in context["contract_artifacts"]]
        inputs += [{"scope": "tool-resource", **{key: entry[key] for key in ("path", "sha256", "bytes")}}
                   for entry in resources]
        return {"schema_version": 1, "binding": binding, "execution_id": uuid.uuid4().hex,
                "purpose": "produce", "context": context, "inventory": inventory,
                "config": copy.deepcopy(self.fixture.config), "pre_manifest": context["output_manifest"],
                "inputs": sorted(inputs, key=lambda item: (item["scope"], item["path"])),
                "outputs": {name: f"{revision}/js/{name}.json" for name in ("result", "symbols")}}

    def execute(self, request, *, raw=None):
        context = request["context"]
        request_name = request["binding"]["revision"] + "/js/request.json"
        graph.persist(context, request_name, request)
        request_path = Path(context["run_root"]) / request_name
        if raw is not None:
            request_path.write_bytes(raw(request_path.read_bytes()))
        env = {key: value for key, value in os.environ.items()
               if not key.upper().startswith(("PYTHON", "NODE_", "TS_NODE_"))
               and key.upper() != "VSCODE_INSPECTOR_OPTIONS"}
        argv = [self.qualified["executable"]["path"],
                str(Path(context["controller_root"]) / "measure_js.mjs"), str(request_path)]
        print("Executing fixed JS command:", self._testMethodName, request["binding"]["revision"], flush=True)
        code, stdout, stderr = run_capture(argv, cwd=context[request["binding"]["revision"] + "_root"],
                                           env=env, idle=30, max_total=90)
        evidence = os.environ.get("Q2_JS_COMMAND_RECORDS")
        if evidence:
            outputs = {}
            for name in ("result", "symbols"):
                produced = Path(context["run_root"]) / f"{request['binding']['revision']}/js/{name}.json"
                if produced.is_file():
                    destination = Path(evidence) / f"{request['execution_id']}-{name}.json"
                    with destination.open("xb") as stream:
                        stream.write(produced.read_bytes())
                    outputs[name] = graph.artifact(evidence, destination.name)
            with (Path(evidence) / (request["execution_id"] + ".json")).open("x", encoding="utf-8") as stream:
                json.dump({"test": self.id(), "request": request, "argv": argv, "returncode": code,
                           "stdout": stdout, "stderr": stderr, "idle_seconds": 30, "max_seconds": 90,
                           "outputs": outputs},
                          stream, ensure_ascii=False, indent=2)
        return code, stdout, stderr

    def test_fixed_command_produces_source_bound_and_empty_censuses(self):
        for revision in ("base", "head"):
            with self.subTest(revision=revision):
                request = self.request(revision)
                code, stdout, stderr = self.execute(request)
                self.assertEqual((code, stderr), (0, ""), stdout + stderr)
                root = Path(request["context"]["run_root"])
                result = graph.load_json((root / request["outputs"]["result"]).read_bytes())
                symbols = graph.load_json((root / request["outputs"]["symbols"]).read_bytes())
                self.assertEqual(result["state"], "produced")
                self.assertEqual(result["binding"], request["binding"])
                self.assertEqual(result["execution_id"], request["execution_id"])
                self.assertEqual(result["symbols"], graph.artifact(root, request["outputs"]["symbols"]))
                self.assertEqual(result["request"], graph.artifact(root, f"{revision}/js/request.json"))
                self.assertEqual(result["reasons"], [])
                self.assertEqual(symbols["binding"], request["binding"])
                self.assertEqual([row["path"] for row in symbols["files"]],
                                 [] if revision == "base" else ["source.mjs"])
                self.assertEqual([row["path"] for row in result["syntax"]],
                                 [] if revision == "base" else ["source.mjs"])
                self.assertEqual(len(result["provenance"]["controller_files"]), 6)
                self.assertFalse((root / revision / "syntax").exists())
                self.assertFalse((Path(request["context"][revision + "_root"]) / "executed-subject.txt").exists())

    def test_rejects_incomplete_inputs_and_changed_config(self):
        for mutation in ("missing-input", "config"):
            with self.subTest(mutation=mutation):
                request = self.request()
                if mutation == "missing-input":
                    request["inputs"].pop()
                else:
                    request["config"]["mutation_cap"] = 19
                code, stdout, stderr = self.execute(request)
                self.assertEqual(code, 2, stdout + stderr)
                self.assertIn("Incomplete or unexpected admitted JS inputs" if mutation == "missing-input"
                              else "Request configuration differs from source contract", stderr)
                self.assertFalse((Path(request["context"]["run_root"]) / request["outputs"]["result"]).exists())

    def test_rejects_unknown_fields_purpose_and_duplicate_json(self):
        for mutation in ("extra-field", "purpose", "duplicate"):
            with self.subTest(mutation=mutation):
                request = self.request()
                if mutation == "extra-field":
                    request["argv"] = ["unapproved"]
                elif mutation == "purpose":
                    request["purpose"] = "trust"
                raw = (lambda data: b'{"schema_version":1,' + data[1:]) if mutation == "duplicate" else None
                code, stdout, stderr = self.execute(request, raw=raw)
                self.assertEqual(code, 2, stdout + stderr)
                self.assertIn({"extra-field": "Invalid JSRequestV1 fields",
                               "purpose": "Invalid JS request version, purpose or execution ID",
                               "duplicate": "Duplicate JSON key: schema_version"}[mutation], stderr)
                self.assertFalse((Path(request["context"]["run_root"]) / request["outputs"]["result"]).exists())

    def test_refuses_output_escape_and_existing_output(self):
        for mutation in ("escape", "existing"):
            with self.subTest(mutation=mutation):
                request = self.request()
                root = Path(request["context"]["run_root"])
                if mutation == "escape":
                    request["outputs"]["result"] = "../escaped.json"
                else:
                    target = root / request["outputs"]["symbols"]
                    target.parent.mkdir(parents=True)
                    target.write_bytes(b"retain me")
                code, stdout, stderr = self.execute(request)
                self.assertEqual(code, 2, stdout + stderr)
                self.assertIn("Invalid fixed JS output path" if mutation == "escape"
                              else "Refusing to overwrite JS output: symbols", stderr)
                self.assertFalse((root / "head/js/result.json").exists())
                if mutation == "existing":
                    self.assertEqual(target.read_bytes(), b"retain me")

    def test_rejects_rehashed_manifest_and_stale_controller(self):
        for mutation in ("manifest", "controller"):
            with self.subTest(mutation=mutation):
                request = self.request()
                context = request["context"]
                controller = Path(context["controller_root"]) / "run.py"
                original = controller.read_bytes()
                try:
                    if mutation == "manifest":
                        manifest_path = Path(context["run_root"]) / "js-preflight.json"
                        manifest = graph.load_json(manifest_path.read_bytes())
                        manifest["inputs"].pop()
                        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                        ref = graph.artifact(context["run_root"], "js-preflight.json")
                        context["output_manifest"] = request["pre_manifest"] = ref
                    else:
                        controller.write_bytes(original + b"\n")
                    code, stdout, stderr = self.execute(request)
                    self.assertEqual(code, 2, stdout + stderr)
                    self.assertIn("Invalid preflight ownership" if mutation == "manifest"
                                  else "Controller bytes changed", stderr)
                    self.assertFalse((Path(context["run_root"]) / request["outputs"]["result"]).exists())
                finally:
                    controller.write_bytes(original)
