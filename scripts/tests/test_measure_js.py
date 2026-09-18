"""Real native parser-core proof; not configured JS measurement acceptance."""

import copy
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
import probe


class SharedJSCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = Q1Fixture()
        cls.addClassCleanup(fixture.close)
        fixture.config["tools"] = source_tools(("typescript",))
        fixture.config["tool_artifact_root"] = str(EVIDENCE)
        fixture.save_config()
        measure.validate_config(fixture.config, fixture.git.root)
        cls.config = fixture.config
        cls.qualified = measure._qualified_inputs(cls.config, [SCRIPTS.parent])["typescript"]
        print("Validated existing TypeScript binding for native core tests", flush=True)

    def fixture(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        return fixture

    def native(self, case, revisions=None, root_sources=None, semantic=None):
        with tempfile.TemporaryDirectory(prefix="qj-") as temporary:
            root = Path(temporary).resolve()
            controller = root / "measure_js.mjs"
            shutil.copyfile(SCRIPTS / controller.name, controller)
            controller_hash = hashlib.sha256(controller.read_bytes()).hexdigest()
            result = root / "result.json"
            request = {
                "binding": self.qualified["binding"], "source": self.qualified["source"],
                "scratch": str(root), "controller": str(controller),
                "controller_sha256": controller_hash, "result": str(result), "revisions": revisions,
                "root_sources": root_sources,
                "semantic": semantic,
            }
            request_path = root / "input.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            removed = sorted(key for key in os.environ if key.upper().startswith(("PYTHON", "NODE_", "TS_NODE_"))
                             or key.upper() == "VSCODE_INSPECTOR_OPTIONS")
            env = {key: value for key, value in os.environ.items() if key not in removed}
            env.update(Q2_JS_TEST_INPUT=str(request_path), Q2_JS_TEST_CASE=case)
            argv = [self.qualified["executable"]["path"], str(SCRIPTS / "tests" / "measure_js.test.mjs")]
            print("Starting real native core case:", case, flush=True)
            code, stdout, stderr = run_capture(argv, cwd=str(root), env=env, idle=30, max_total=90)
            record = {
                "test": self.id(), "case": case, "argv": argv, "cwd": str(root),
                "idle_seconds": 30, "max_seconds": 90, "environment_removed": removed,
                "returncode": code, "stdout": stdout, "stderr": stderr,
                "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
                "qualified_inputs_sha256": graph.digest(self.qualified),
                "controller_sha256": controller_hash,
                "executing_sources": [graph.artifact(SCRIPTS, name) for name in (
                    "measure_js.mjs", "measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py",
                    "tests/test_measure_js.py", "tests/measure_js.test.mjs", "tests/helpers.py",
                    "tests/test_measure_inventory.py", "tests/test_measure_source_bindings.py", "tests/test_measure_q2.py")],
                "native": graph.load_json(result.read_bytes()) if result.exists() else None,
            }
            destination = os.environ.get("Q2_JS_RECORDS")
            if destination:
                target = graph.root_path(destination) / (self._testMethodName + ".json")
                with target.open("x", encoding="utf-8") as stream:
                    json.dump(record, stream, ensure_ascii=False, indent=2)
            self.assertEqual(code, 0, stdout + stderr)
            self.assertEqual(stderr, "")
            self.assertEqual(record["native"]["runtime"], {"version": "v24.11.1", "architecture": "arm64"})
            self.assertEqual(record["native"]["case"], case)
            for proof in record["native"]["proofs"]:
                for candidate in proof.get("population", {}).get("eligible", []):
                    identity = {key: candidate[key] for key in
                                ("path", "span", "operator", "before_sha256", "after_sha256")}
                    self.assertEqual(candidate["id"], graph.digest(identity))
                    original = (Path(revisions[1]["root"]) / candidate["path"]).read_bytes()
                    span = candidate["span"]
                    self.assertEqual(original[span["start_byte"]:span["end_byte"]].decode("utf-8"),
                                     candidate["before_text"])
                    edited = (original[:span["start_byte"]] + candidate["after_text"].encode("utf-8")
                              + original[span["end_byte"]:])
                    self.assertEqual(hashlib.sha256(original).hexdigest(), candidate["before_sha256"])
                    self.assertEqual(hashlib.sha256(edited).hexdigest(), candidate["after_sha256"])
            self.assertEqual(hashlib.sha256(controller.read_bytes()).hexdigest(), controller_hash)
            self.assertEqual(controller.read_bytes(), (SCRIPTS / controller.name).read_bytes())
            self.assertEqual(measure._qualified_inputs(self.config, [root])["typescript"], self.qualified)
            print("Completed real native core case:", case, flush=True)

    def semantic_fixture(self, case, *, actual_sources=False):
        fixture = self.fixture()
        fixture.config["tools"] = copy.deepcopy(self.config["tools"])
        fixture.config["tool_artifact_root"] = self.config["tool_artifact_root"]
        fixture.git.write("origin.ts", "export const café = 1;\r\nexport function identity(x: number) { return x; }\r\n")
        fixture.git.write("barrel.ts", "export { café as renamed } from './origin.js';\nexport * from './cycle.js';\n")
        fixture.git.write("cycle.ts", "export { renamed } from './barrel.js';\n")
        fixture.git.write("base-only.cjs", "")
        fixture.git.write("package.json", json.dumps({"type": "module", "exports": {
            ".": "./origin.ts", "./conditional": {"import": "./origin.ts"}}, "bin": "./consumer.mjs"}))
        fixture.git.write("consumer.mjs", "import { renamed } from './barrel.js'; export const answer = renamed;\n")
        fixture.config["js_entrypoints"] = [
            {"path": "origin.ts", "origin_ref": "fixture-explicit", "public_exports": ["café"]},
            {"path": "head-only.ts", "origin_ref": "fixture-head-only", "public_exports": ["head"]}]
        fixture.config["suites"].append({
            "id": "native-fixture", "runner": "node-native", "argv": [self.qualified["executable"]["path"],
            "--test", "case.test.mjs"], "cwd": ".", "test_files": ["case.test.mjs"],
            "idle_seconds": 30, "max_seconds": 90})
        fixture.git.write("case.test.mjs", "import test from 'node:test'; import assert from 'node:assert/strict';\n"
                          "import { café } from './origin.ts'; test('café', () => assert.equal(café, 1));\n")
        fixture.save_config()
        fixture.base_sha = fixture.git.commit("Semantic fixture immutable base")
        fixture.git.write("origin.ts", "// Unrelated leading comment\r\n" +
                          "export const café = 1;\r\nexport function identity(x: number) { return x; }\r\n"
                          "export const extra = 2;\r\n")
        (fixture.git.root / "base-only.cjs").unlink()
        fixture.git.write("head-only.ts", "export const head = true;\n")
        fixture.git.write("plain.js", "/** true === false */\r\nexport const n = 1 + 2;\r\n")
        fixture.git.write("widget.jsx", "export const view = () => <span>{1 + 2}</span>;\r\n")
        fixture.git.write("view.tsx", "export const view = (n: number) => <span>{n >= 2}</span>;\r\n")
        fixture.git.write("calls.cjs", "const local = require('./consumer.mjs');\n"
                          "function inner(require) { return require('./not-an-import.js'); }\n"
                          "const computed = require(local.path);\nexports.local = local;\n")
        fixture.git.write("references.ts", "import * as ns from './origin.js';\n"
                          "import { café as value } from './origin.js';\n"
                          "import type { Missing } from './absent.js';\n"
                          "import { execFile } from 'node:child_process';\n"
                          "export const object = { value };\nexport const lookup = ns['café'];\n"
                          "export const dynamic = (key: string) => ns[key];\n"
                          "export const external = () => execFile('tool');\n"
                          "// @ts-expect-error deliberate static fixture error\nexport const ignored: number = 'bad';\n"
                          "// @ts-ignore deliberate second static fixture error\nexport const ignored2: number = 'bad';\n")
        fixture.git.write("runtime.mjs", "import * as child from 'node:child_process';\n"
                          "export const run = () => child.spawn('tool');\n"
                          "export const shadowed = (Function) => Function('not-runtime-code');\n")
        fixture.git.write("pragmas.js", "// @ts-nocheck\nexport const x = 1;\n")
        fixture.git.write("checked.js", "// @ts-check\nexport const x = 1;\n")
        fixture.git.write("types.d.ts", "export const declaration: true;\n")
        fixture.git.write("shapes.ts", "\ufeff// true === false and 😀\r\n"
                          "type Flags = true | false;\r\n"
                          "type Fn = (x: true) => false;\r\n"
                          "export const regex = /true===false/;\r\n"
                          "export const template = `true === false ${1 + 2}`;\r\n"
                          "export const arrow = (x: number) => x >= 1;\r\n"
                          "export const precedence = 1 + 2 === 3;\r\n"
                          "export const positive = +1;\r\n"
                          "export const quotient = 8 / 2;\r\n"
                          "export function first() {\r\n  return 7;\r\n}\r\n"
                          "export function branch(x: boolean) { if (x) console.log('😀'); }\r\n"
                          "export const bool = true;\r\n"
                          "'use strict';\r\n"
                          "declare const ambient: true;\r\n")
        fixture.git.write("invalid.ts", "export function ( {\n")
        fixture.git.write("bad-utf8.js", b"\xff")
        fixture.git.write("empty.js", "")
        if case == "review_corrections":
            fixture.git.write("selections.ts", "import * as ns from './origin.js';\n"
                              "export const { café } = ns;\n"
                              'export const { "café": quoted } = ns;\n'
                              "export const { café: renamed } = ns;\n"
                              'export const { ["café"]: literal } = ns;\n'
                              "export function choose(key: keyof typeof ns) {\n"
                              "  const { [key]: chosen, ...rest } = ns; return { chosen, rest };\n}\n"
                              "export function indexed(input: Record<string, number>) {\n"
                              "  const { unresolved } = input; return unresolved;\n}\n"
                              "export const plain = () => import('./origin.js');\n"
                              "export const options = () => import('./origin.js', {});\n"
                              "export const computed = (name: string) => import(name, {});\n")
            fixture.git.write("require-arity.cjs", "const plain = require('./consumer.mjs');\n"
                              "const options = require('./consumer.mjs', {});\n"
                              "function shadow(require) { return require('./not-an-import.js', {}); }\n"
                              "exports.values = [plain, options, shadow];\n")
        if actual_sources:
            for name in ("evals/lib/score.mjs", "scripts/native_result.mjs"):
                fixture.git.write(name, (SCRIPTS.parent / name).read_bytes())
        fixture.build()
        self.semantic_native(case, fixture)

    def semantic_native(self, case, fixture):
        changes = {name: sorted(lines) for name, lines in probe.changed_lines(
            fixture.git.root, fixture.base_sha).items()}
        revisions = []
        for revision in ("base", "head"):
            inventory = measure.inventory(fixture.context, revision, changes if revision == "head" else {},
                                          include_js=True)
            root = Path(fixture.context[revision + "_root"])
            self.assertGreaterEqual(len(inventory["entries"]), 3)
            revisions.append({"name": revision, "git": measure.git_head(root), "root": str(root),
                              "inventory": inventory,
                              "entries": [entry for entry in inventory["entries"] if entry["suffix"] in measure.JS_EXT],
                              "metadata": [graph.artifact(root, "package.json")] if (root / "package.json").is_file() else []})
        root = Path(fixture.context["head_root"])
        ref = graph.artifact(root, "measurement.json")
        self.native(case, revisions, semantic={
            "config_input": {"scope": "head-contract", **ref}, "config_root": str(root),
            "run_id": fixture.context["run_id"], "policy_sha256": fixture.context["policy_sha256"],
            "toolset_sha256": measure.toolset_digest(fixture.config),
            "legacy_inventory": measure.inventory(fixture.context, "head", changes),
        })

    def test_native_serialized_source_records_and_origins(self):
        self.semantic_fixture("serialized_records")

    def test_native_review_corrections_uncertainty_and_require_arity(self):
        self.semantic_fixture("review_corrections")

    def test_native_candidates_from_shared_syntax(self):
        self.semantic_fixture("candidate_records")

    def test_native_serialized_freshness_and_identity(self):
        self.semantic_fixture("serialized_freshness")

    def test_native_candidates_on_actual_controller_sources(self):
        self.semantic_fixture("actual_source_candidates", actual_sources=True)

    def test_native_serialized_zero_js_inputs(self):
        fixture = self.fixture()
        fixture.config["tools"] = copy.deepcopy(self.config["tools"])
        fixture.config["tool_artifact_root"] = self.config["tool_artifact_root"]
        fixture.save_config()
        fixture.git.write("a.py", "value = 2\n")
        fixture.build()
        self.semantic_native("serialized_empty", fixture)

    def test_native_parser_digest_independent_copy(self):
        self.native("parser_copy_binding")

    def test_native_byte_boundaries(self):
        self.native("byte_boundaries")

    def test_native_six_suffix_census(self):
        self.native("six_suffixes")

    def test_native_syntax_shapes(self):
        self.native("syntax_shapes")

    def test_native_diagnostics_and_checker_alias(self):
        self.native("diagnostics_and_symbols")

    def test_native_errors_and_empty_program(self):
        self.native("errors_and_empty_program")

    def test_native_actual_root_syntax_without_execution(self):
        entries = [graph.artifact(SCRIPTS.parent, name) for name in
                   ("evals/lib/score.mjs", "scripts/native_result.mjs")]
        self.native("actual_root_syntax", root_sources={"root": str(SCRIPTS.parent), "entries": entries})

    def test_native_two_git_revision_census(self):
        fixture = self.fixture()
        fixture.git.write("base-only.js", "export const old = 1;\n")
        fixture.git.write("shared.ts", "export const current: number = 1;\n")
        fixture.git.write("view.jsx", "export const view = () => null;\n")
        fixture.git.write("package.json", '{"type":"module"}\n')
        fixture.base_sha = fixture.git.commit("Native parser base")
        (fixture.git.root / "base-only.js").unlink()
        fixture.git.write("shared.ts", "export const current: number = 'changed';\n")
        fixture.git.write("package.json", '{"type":"commonjs"}\n')
        fixture.build()
        revisions = []
        include_js = "typescript" in self.config["tools"]
        for revision in ("base", "head"):
            inventory = measure.inventory(fixture.context, revision, {}, include_js=include_js)
            self.assertGreaterEqual(len(inventory["entries"]), 3)
            root = Path(fixture.context[revision + "_root"])
            revisions.append({"name": revision, "git": measure.git_head(root), "root": str(root),
                              "entries": [entry for entry in inventory["entries"] if entry["suffix"] in measure.JS_EXT],
                              "metadata": [graph.artifact(root, "package.json")]})
        self.native("two_revisions", revisions)

    def test_inventory_keywords_preserve_legacy_and_pending_entries(self):
        fixture = self.fixture()
        fixture.git.write("view.jsx", "export const view = () => null;\n")
        fixture.git.write("view.tsx", "export const view = () => null;\n")
        fixture.base_sha = fixture.git.commit("Both JSX dialects at base")
        fixture.git.write("a.py", "value = 2\n")
        fixture.build()
        include_js = "typescript" in self.config["tools"]
        for revision in ("base", "head"):
            legacy = measure.inventory(fixture.context, revision, {})
            disabled = measure.inventory(fixture.context, revision, {}, include_js=False)
            enabled = measure.inventory(fixture.context, revision, {}, include_js=include_js)
            self.assertEqual(graph._json_bytes(legacy), graph._json_bytes(disabled))
            expected = copy.deepcopy(legacy)
            for entry in expected["entries"]:
                if entry["suffix"] in {".jsx", ".tsx"}:
                    self.assertEqual(entry["language"], "unsupported")
                    self.assertEqual(entry["parse_state"], "unsupported")
                    self.assertEqual(entry["reason"], "No declared language adapter")
                    entry.update(language="javascript" if entry["suffix"] == ".jsx" else "typescript",
                                 parse_state="pending", reason="")
            expected.pop("digest")
            expected["digest"] = graph.digest(expected)
            self.assertEqual(enabled, expected)
            self.assertNotEqual(enabled["digest"], legacy["digest"])
            left = measure._walk(fixture.context[revision + "_root"])
            right = measure._walk(fixture.context[revision + "_root"], include_js=True)
            self.assertEqual([item["path"] for item in left[0]], [item["path"] for item in right[0]])
            self.assertEqual(left[1:], right[1:])
        fixture.validate()
        fixture.head["inventory"] = measure.inventory(
            fixture.context, "head", fixture.head["inventory"]["changed_production"], include_js=True)
        with self.assertRaisesRegex(ValueError, "Inventory is missing"):
            fixture.validate()
        for value in (None, 0, 1, "false"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "bool"):
                    measure.inventory(fixture.context, "base", {}, include_js=value)
                with self.assertRaisesRegex(ValueError, "bool"):
                    measure._walk(fixture.context["base_root"], include_js=value)

    def test_controller_digest_and_no_inventory_mode_salt(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "value = 2\n")
        fixture.build()
        self.assertEqual(measure.inventory(fixture.context, "head", {}),
                         measure.inventory(fixture.context, "head", {}, include_js=True))
        root = Path(fixture.context["controller_root"])
        names = ("measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py")
        expected = graph.digest({name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names})
        self.assertEqual(measure.controller_digest(root), expected)
        self.assertEqual(measure.controller_digest(root, include_js=False), expected)
        with self.assertRaises(FileNotFoundError):
            measure.controller_digest(root, include_js=True)
        shutil.copyfile(SCRIPTS / "measure_js.mjs", root / "measure_js.mjs")
        extended = graph.digest({name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                 for name in names + ("measure_js.mjs",)})
        self.assertEqual(measure.controller_digest(root, include_js=True), extended)
        (root / "measure_js.mjs").write_bytes((root / "measure_js.mjs").read_bytes() + b"\n")
        self.assertNotEqual(measure.controller_digest(root, include_js=True), extended)
        self.assertEqual(measure.controller_digest(root), expected)
        (root / "measure_js.mjs").unlink()
        os.link(root / "measure.py", root / "measure_js.mjs")
        with self.assertRaisesRegex(ValueError, "regular-file"):
            measure.controller_digest(root, include_js=True)
        for value in (0, 1, None, "true"):
            with self.assertRaisesRegex(ValueError, "bool"):
                measure.controller_digest(root, include_js=value)


if __name__ == "__main__":
    unittest.main()
