"""Independent native serialization gaps, not configured measurement acceptance."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from helpers import SCRIPTS, run_capture
from test_measure_inventory import Q1Fixture
from test_measure_q2 import EVIDENCE
from test_measure_source_bindings import source_tools
import measure
import measure_graph as graph


class IndependentJSSerializationTests(unittest.TestCase):
    def test_merged_declarations_import_equals_and_namespace_reexport(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        fixture.config["tools"] = source_tools(("typescript",))
        fixture.config["tool_artifact_root"] = str(EVIDENCE)
        qualified = measure._qualified_inputs(fixture.config, [fixture.git.root])["typescript"]
        files = {
            "package.json": '{"type":"commonjs"}\n',
            "origin.ts": (
                "export class Parcel { value = 1; }\r\n"
                "export namespace Parcel { export const tag = 'parcel'; }\r\n"
                "export interface Box { left: string; }\r\n"
                "export interface Box { right: number; }\r\n"
            ),
            "barrel.ts": "export * as bundle from './origin.js';\r\n",
            "consumer.ts": (
                "import model = require('./origin.js');\r\n"
                "import Item = model.Parcel;\r\n"
                "import { bundle } from './barrel.js';\r\n"
                "export const instance = new Item();\r\n"
                "export const tag = model.Parcel.tag;\r\n"
                "export const other = bundle.Parcel.tag;\r\n"
                "export const box: model.Box = { left: 'x', right: 1 };\r\n"
            ),
        }
        for name, text in files.items():
            fixture.git.write(name, text)
        fixture.save_config()
        fixture.build()
        root = Path(fixture.context["head_root"])
        inventory = measure.inventory(fixture.context, "head", {}, include_js=True)
        self.assertGreaterEqual(sum(entry["suffix"] == ".py" for entry in inventory["entries"]), 3)
        self.assertNotEqual(fixture.base_sha, measure.git_head(root))
        with tempfile.TemporaryDirectory(prefix="qji-") as temporary:
            scratch = Path(temporary).resolve()
            controller = scratch / "measure_js.mjs"
            shutil.copyfile(SCRIPTS / controller.name, controller)
            config_ref = {"scope": "head-contract", **graph.artifact(root, "measurement.json")}
            request = {
                "controller": str(controller), "controller_sha256": hashlib.sha256(controller.read_bytes()).hexdigest(),
                "binding": qualified["binding"], "source": qualified["source"],
                "root": str(root), "entries": [entry for entry in inventory["entries"] if entry["suffix"] == ".ts"],
                "metadata": [graph.artifact(root, "package.json")], "config_input": config_ref,
                "result": str(scratch / "result.json"),
                "semantic": {
                    "semantic_version": "typescript-shared-v1", "run_id": fixture.context["run_id"],
                    "revision": "head", "git_revision": measure.git_head(root),
                    "inventory_sha256": inventory["digest"], "source_sha256": inventory["source_sha256"],
                    "policy_sha256": fixture.context["policy_sha256"],
                    "toolset_sha256": measure.toolset_digest(fixture.config),
                },
            }
            request_path = scratch / "input.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            removed = sorted(key for key in os.environ if key.upper().startswith(("PYTHON", "NODE_", "TS_NODE_"))
                             or key.upper() == "VSCODE_INSPECTOR_OPTIONS")
            env = {key: value for key, value in os.environ.items() if key not in removed}
            env["Q2_JS_TEST_INPUT"] = str(request_path)
            argv = [qualified["executable"]["path"],
                    str(SCRIPTS / "tests" / "measure_js_serialization_independent.test.mjs")]
            destination = os.environ.get("Q2_JS_RECORDS")
            record = {
                "test": self.id(), "argv": argv, "cwd": str(scratch), "idle_seconds": 30, "max_seconds": 90,
                "environment_removed": removed, "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
                "qualified_inputs_sha256": graph.digest(qualified),
                "controller_sha256": request["controller_sha256"],
                "base_git": fixture.base_sha, "head_git": request["semantic"]["git_revision"],
                "fixture_files": files,
            }
            target = Path(destination) / "independent-native" if destination else None
            if target:
                with target.with_suffix(".invocation.json").open("x", encoding="utf-8") as stream:
                    json.dump(record, stream, ensure_ascii=False, indent=2)
            print("Starting real native merged/import-equals/namespace-reexport proof", flush=True)
            code, stdout, stderr = run_capture(argv, cwd=str(scratch), env=env, idle=30, max_total=90)
            # Preserve returned streams/exit and undecoded result bytes BEFORE parsing.
            # run_capture itself decodes UTF-8 and normalizes CRLF, as in the frozen harness.
            if target:
                with target.with_suffix(".capture.json").open("x", encoding="utf-8") as stream:
                    json.dump({"returncode": code, "stdout": stdout, "stderr": stderr}, stream,
                              ensure_ascii=False, indent=2)
                if Path(request["result"]).exists():
                    with target.with_suffix(".result.bin").open("xb") as stream:
                        stream.write(Path(request["result"]).read_bytes())
            self.assertEqual(code, 0, stdout + stderr)
            self.assertEqual(stderr, "")
            result = graph.load_json(Path(request["result"]).read_bytes())
            self.assertEqual(result["runtime"], {"version": "v24.11.1", "architecture": "arm64"})
            self.assertEqual(result["verified"], ["merged-declarations", "import-equals", "namespace-reexport"])
            self.assertEqual(result["qualified_controller_sha256"], request["controller_sha256"])
            for symbol in result["merged_symbols"]:
                descriptors = [{key: value for key, value in declaration.items()
                                if key not in {"source_sha256", "span"}} for declaration in symbol["declarations"]]
                descriptors.sort(key=graph._json_bytes)
                self.assertEqual(symbol["id"], graph.digest(["js-symbol-v1", descriptors]))
                self.assertEqual(len(symbol["declarations"]), 2)
            self.assertEqual(controller.read_bytes(), (SCRIPTS / "measure_js.mjs").read_bytes())
            print("Completed real native merged/import-equals/namespace-reexport proof", flush=True)


class NativeSerializationReviewRegressions(unittest.TestCase):
    """Focused red handoff for independent review R1/R2; no expected-failure waiver."""

    def run_review_fixture(self, case, source):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        fixture.config["tools"] = source_tools(("typescript",))
        fixture.config["tool_artifact_root"] = str(EVIDENCE)
        qualified = measure._qualified_inputs(fixture.config, [fixture.git.root])["typescript"]
        files = {"package.json": '{"type":"module"}\n',
                 "origin.mjs": "export const value = 1;\n", "use.mjs": source}
        for name, text in files.items():
            fixture.git.write(name, text)
        fixture.save_config()
        fixture.build()
        root = Path(fixture.context["head_root"])
        inventory = measure.inventory(fixture.context, "head", {}, include_js=True)
        with tempfile.TemporaryDirectory(prefix="qjr-") as temporary:
            scratch = Path(temporary).resolve()
            controller = scratch / "measure_js.mjs"
            shutil.copyfile(SCRIPTS / controller.name, controller)
            request = {
                "controller": str(controller), "controller_sha256": hashlib.sha256(controller.read_bytes()).hexdigest(),
                "binding": qualified["binding"], "source": qualified["source"],
                "root": str(root), "entries": [entry for entry in inventory["entries"] if entry["suffix"] == ".mjs"],
                "metadata": [graph.artifact(root, "package.json")],
                "config_input": {"scope": "head-contract", **graph.artifact(root, "measurement.json")},
                "result": str(scratch / "result.json"),
                "semantic": {
                    "semantic_version": "typescript-shared-v1", "run_id": fixture.context["run_id"],
                    "revision": "head", "git_revision": measure.git_head(root),
                    "inventory_sha256": inventory["digest"], "source_sha256": inventory["source_sha256"],
                    "policy_sha256": fixture.context["policy_sha256"],
                    "toolset_sha256": measure.toolset_digest(fixture.config),
                },
            }
            request_path = scratch / "input.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            removed = sorted(key for key in os.environ if key.upper().startswith(("PYTHON", "NODE_", "TS_NODE_"))
                             or key.upper() == "VSCODE_INSPECTOR_OPTIONS")
            env = {key: value for key, value in os.environ.items() if key not in removed}
            env.update(Q2_JS_TEST_INPUT=str(request_path), Q2_JS_TEST_CASE=case)
            argv = [qualified["executable"]["path"],
                    str(SCRIPTS / "tests" / "measure_js_serialization_independent.test.mjs")]
            destination = os.environ.get("Q2_JS_RECORDS")
            target = Path(destination) / case if destination else None
            if target:
                with target.with_suffix(".invocation.json").open("x", encoding="utf-8") as stream:
                    json.dump({"test": self.id(), "argv": argv, "cwd": str(scratch),
                               "idle_seconds": 30, "max_seconds": 90, "environment_removed": removed,
                               "controller_sha256": request["controller_sha256"],
                               "qualified_inputs_sha256": graph.digest(qualified),
                               "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
                               "fixture_files": files, "head_git": request["semantic"]["git_revision"]},
                              stream, ensure_ascii=False, indent=2)
            print("Starting real review regression:", case, flush=True)
            code, stdout, stderr = run_capture(argv, cwd=str(scratch), env=env, idle=30, max_total=90)
            if target:
                with target.with_suffix(".capture.json").open("x", encoding="utf-8") as stream:
                    json.dump({"returncode": code, "stdout": stdout, "stderr": stderr},
                              stream, ensure_ascii=False, indent=2)
                if Path(request["result"]).exists():
                    with target.with_suffix(".result.bin").open("xb") as stream:
                        stream.write(Path(request["result"]).read_bytes())
            self.assertTrue(Path(request["result"]).is_file(), "Native test did not produce actual result evidence")
            result = graph.load_json(Path(request["result"]).read_bytes())
            self.assertEqual(result["case"], case)
            self.assertEqual(result["runtime"], {"version": "v24.11.1", "architecture": "arm64"})
            self.assertEqual(result["controller_sha256"], request["controller_sha256"])
            self.assertIn("tests 1", stdout)
            self.assertEqual(code, 0, stdout + stderr)
            self.assertEqual(stderr, "")

    def test_r1_namespace_destructuring_keeps_export_property_identity(self):
        self.run_review_fixture("review_r1", (
            "import * as ns from './origin.mjs';\n"
            "const { value } = ns;\n"
            'const { "value": local } = ns;\n'
            "export const answers = [value, local];\n"
            "export const control = ns.value;\n"
        ))

    def test_r2_literal_dynamic_import_with_options_keeps_local_target(self):
        self.run_review_fixture("review_r2", (
            "export const plain = () => import('./origin.mjs');\n"
            "export const options = () => import('./origin.mjs', {});\n"
            "/** @param {string} name */\n"
            "export const computed = name => import(name, {});\n"
        ))


if __name__ == "__main__":
    unittest.main()
