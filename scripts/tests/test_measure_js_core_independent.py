"""Independent gaps at the frozen native-core boundary, not JS integration proof."""
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


class IndependentJSCoreBoundaryTests(unittest.TestCase):
    def capture(self, record):
        destination = os.environ.get("Q2_JS_INDEPENDENT_RECORDS")
        if destination:
            with (Path(destination) / (self._testMethodName + ".json")).open("x", encoding="utf-8") as stream:
                json.dump(record, stream, ensure_ascii=False, indent=2)

    def invoke(self, temporary, argv, **record):
        removed = sorted(name for name in os.environ if
                         name.upper().startswith(("PYTHON", "NODE_", "TS_NODE_")) or
                         name.upper() == "VSCODE_INSPECTOR_OPTIONS")
        env = {name: value for name, value in os.environ.items() if name not in removed}
        code, stdout, stderr = run_capture(argv, cwd=str(temporary), env=env, idle=30, max_total=90)
        result = {"test": self.id(), "argv": argv, "cwd": str(temporary),
                  "idle_seconds": 30, "max_seconds": 90, "environment_removed": removed,
                  "returncode": code, "stdout": stdout, "stderr": stderr, **record}
        self.capture(result)
        return result

    def test_missing_metadata_unadmitted_source_and_forged_handle(self):
        config = {"tools": source_tools(("typescript",)), "tool_artifact_root": str(EVIDENCE)}
        qualified = measure._qualified_inputs(config, [SCRIPTS.parent])["typescript"]
        with tempfile.TemporaryDirectory(prefix="ji-") as directory:
            root = Path(directory).resolve()
            controller = root / "measure_js.mjs"
            shutil.copyfile(SCRIPTS / controller.name, controller)
            self.assertFalse(os.path.samefile(controller, SCRIPTS / controller.name))
            request = {"binding": qualified["binding"], "source": qualified["source"],
                       "controller": str(controller), "scratch": str(root)}
            request_path = root / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            argv = [qualified["executable"]["path"],
                    str(SCRIPTS / "tests/measure_js_core_independent.test.mjs"), str(request_path)]
            print("Starting independent native boundary invocation", flush=True)
            result = self.invoke(root, argv, request=request,
                                 controller_sha256=hashlib.sha256(controller.read_bytes()).hexdigest())
            self.assertEqual(result["returncode"], 0, result["stdout"] + result["stderr"])
            self.assertEqual(result["stderr"], "")
            observed = json.loads(result["stdout"])
            self.assertEqual(set(observed), {"missing_metadata", "unadmitted_source",
                                            "forged_handle", "hardlinked_source"})
            self.assertEqual(observed["missing_metadata"]["cause"], "ENOENT")
            self.assertEqual(observed["unadmitted_source"], [2307])
            self.assertFalse(observed["forged_handle"]["callback_called"])
            self.assertIn("independent regular file", observed["hardlinked_source"])
            self.assertEqual(controller.read_bytes(), (SCRIPTS / controller.name).read_bytes())

    def test_unqualified_config_and_missing_request_reject_integration(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        measure.validate_config(fixture.config, fixture.git.root)
        fixture.config["js_entrypoints"] = ["a.js"]
        with self.assertRaisesRegex(ValueError, "JS entrypoints require qualified TypeScript") as error:
            measure.validate_config(fixture.config, fixture.git.root)
        node = source_tools(("typescript",))["typescript"]["executable"]
        with tempfile.TemporaryDirectory(prefix="ji-") as directory:
            root = Path(directory).resolve()
            controller = root / "measure_js.mjs"
            shutil.copyfile(SCRIPTS / controller.name, controller)
            result = self.invoke(root, [node, str(controller)], config_error=str(error.exception))
            self.assertEqual(result["returncode"], 2, result)
            self.assertEqual(result["stdout"], "")
            self.assertIn("Expected one absolute JSRequestV1 path", result["stderr"])
            self.assertEqual(sorted(item.name for item in root.iterdir()), ["measure_js.mjs"])
            self.assertEqual(controller.read_bytes(), (SCRIPTS / controller.name).read_bytes())


if __name__ == "__main__":
    unittest.main()
