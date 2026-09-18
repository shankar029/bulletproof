"""Qualified native execution through ownership, graph projection and fresh replay."""

import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from helpers import SCRIPTS, run_capture
from test_measure_inventory import Q1Fixture
from test_measure_q2 import EVIDENCE
from test_measure_source_bindings import source_tools
import measure
import measure_graph as graph
import probe


class JSFixture(Q1Fixture):
    def __init__(self, *, empty=False, entrypoints=False, crlf=False):
        super().__init__()
        self.config["tools"] = source_tools(("typescript",))
        self.config["tool_artifact_root"] = str(EVIDENCE)
        self.save_config()
        if not empty:
            self.git.write("old/deleted.mjs", "export const gone = true;\n")
            self.git.write("old/package.json", '{"type":"module"}\n')
            self.git.write("deleted.py", "value = 1\n")
            self.git.write("package.json", '{"type":"module"}\n')
            self.base_sha = self.git.commit("fixture: JS base")
            (self.git.root / "old/deleted.mjs").unlink()
            (self.git.root / "deleted.py").unlink()
            self.git.write("old/package.json", '{"type":"commonjs"}\n')
            self.git.write("lib/value.ts", "export const value: number = 1;\n")
            self.git.write("main.mjs", "import { value as renamed } from './lib/value.js';\n"
                           "import { writeFileSync } from 'node:fs';\n"
                           "writeFileSync('subject-executed.txt', 'bad');\nexport { renamed };\n")
            self.git.write("common.cjs", "module.exports = 1;\n")
            self.git.write("plain.js", "// functionless\n")
            self.git.write("empty.jsx", "")
            self.git.write("view.tsx", "export const view = <div />;\n")
        if crlf:
            self.git.write("lib/value.ts", "export const value: number = 1;\r\n")
            self.git.write("plain.js", "import * as ns from './lib/value.js';\r\nexport const other = ns.value;\r\n")
        if entrypoints:
            self.config["js_entrypoints"] = [{"path": "main.mjs", "origin_ref": "approval.txt",
                                              "public_exports": ["renamed"]}]
            self.config["suites"].append({
                "id": "native-root", "runner": "node-native",
                "argv": [self.config["tools"]["typescript"]["executable"], "--test", "main.mjs"],
                "cwd": ".", "test_files": ["main.mjs"], "idle_seconds": 30, "max_seconds": 90})
            self.git.write("package.json", '{"type":"module","exports":"./main.mjs"}\n')
            self.save_config()
        self.build(collect=False)
        shutil.copyfile(SCRIPTS / "measure_js.mjs", Path(self.context["controller_root"]) / "measure_js.mjs")
        self.context["controller_sha256"] = measure.controller_digest(self.context["controller_root"], include_js=True)
        self.context["toolset_sha256"] = measure.toolset_digest(self.config)

    def produce(self):
        measure.stage_tool_inputs(self.context, self.config)
        changes = {name: sorted(lines) for name, lines in probe.changed_lines(self.git.root, self.base_sha).items()}
        inventories = [measure.inventory(self.context, side, change, include_js=True)
                       for side, change in (("base", {}), ("head", changes))]
        measure.prepare_js_manifest(self.context, inventories, self.config)
        for inv in inventories:
            measure.execute_js(self.context, inv, self.config)
        measure.finish_js_manifest(self.context, inventories, self.config)
        self.base, self.head = [graph.parse_files(self.context, inv, self.config) for inv in inventories]
        self.manifest = measure.make_manifest(self.context, self.base, self.head)
        self.context["output_manifest"] = graph.persist(self.context, "manifest.json", self.manifest)
        self.observations = [item for pair in measure.collect_pair(
            self.context, self.config, self.base, self.head).values() for item in pair]
        return self


class JSIntegrationTests(unittest.TestCase):
    def test_real_mixed_production_and_accepting_replay(self):
        fixture = JSFixture(entrypoints=True, crlf=True)
        self.addCleanup(fixture.close)
        fixture.produce()
        before = graph.digest([fixture.base, fixture.head])
        self.assertEqual(fixture.validate(), sorted(fixture.observations, key=lambda row: (
            row["metric"], row["revision"])))
        self.assertEqual(graph.digest([fixture.base, fixture.head]), before)
        self.assertTrue(any(edge["from"] == "main.mjs" and edge["to"] == "lib/value.ts"
                            for edge in fixture.head["graph"]["edges"]))
        self.assertIn("old/deleted.mjs", fixture.base["graph"]["nodes"])
        self.assertNotIn("old/deleted.mjs", fixture.head["graph"]["nodes"])
        self.assertTrue(all(row["state"] == "processed" for row in fixture.head["receipts"]))
        self.assertFalse((Path(fixture.context["head_root"]) / "subject-executed.txt").exists())
        for side in ("base", "head"):
            request = graph._js_json(fixture.context, f"{side}/js/request.json")[1]
            self.assertEqual(request["purpose"], "produce")
            self.assertIn({"scope": "subject", **graph.artifact(fixture.context[side + "_root"], "package.json")},
                          request["inputs"])
            roots = graph._js_json(fixture.context, f"{side}/js/symbols.json")[1]["entrypoints"]
            entry = next(row for row in roots if row["path"] == "main.mjs")
            self.assertEqual(entry["state"], "absent-at-revision" if side == "base" else "active")
            self.assertIn("renamed", entry["public_exports"])
            self.assertEqual({row["kind"] for row in entry["origins"]},
                             {"config", "suite"} if side == "base" else {"config", "suite", "package"})
        self.assertEqual([row["artifact"]["path"] for row in fixture.manifest["inputs"] if row["role"] == "manifest"],
                         ["js-preflight.json", "js-produced.json"])
        with self.assertRaisesRegex(ValueError, "measure.validate_observations"):
            graph.validate_evidence(fixture.context, fixture.head, fixture.config, {}, fixture.manifest)
        _, _, result, symbols, _, _ = graph._js_transport(fixture.context, fixture.head["inventory"], fixture.config)
        declarations = [declaration for symbol in symbols["symbols"] for declaration in symbol["declarations"]
                        if declaration["path"] == "lib/value.ts" and declaration["kind"] == "SourceFile"]
        self.assertTrue(declarations, "The real compiler must exercise a CRLF-terminated whole-file declaration")
        declarations[0]["span"]["end_line"] += 1
        entries = {row["path"]: row for row in fixture.head["inventory"]["entries"] if row["suffix"] in measure.JS_EXT}
        with self.assertRaisesRegex(ValueError, "span line coordinates"):
            graph._js_symbol_shapes(symbols, entries, fixture.context, "head", result["syntax"])

    def test_zero_js_still_executes_and_replays(self):
        fixture = JSFixture(empty=True)
        self.addCleanup(fixture.close)
        fixture.produce()
        fixture.validate()
        for side in ("base", "head"):
            transport = graph._js_transport(fixture.context, getattr(fixture, side)["inventory"], fixture.config)
            self.assertEqual(transport[1]["returncode"], 0)
            self.assertEqual(transport[3]["files"], [])
            self.assertTrue(transport[1]["stdout"])

    def test_inventory_mode_remains_explicit_and_immutable(self):
        fixture = JSFixture()
        self.addCleanup(fixture.close)
        default = measure.inventory(fixture.context, "head", {})
        self.assertEqual(default, measure.inventory(fixture.context, "head", {}, include_js=False))
        enabled = measure.inventory(fixture.context, "head", {}, include_js=True)
        self.assertEqual([row["path"] for row in default["entries"]], [row["path"] for row in enabled["entries"]])
        self.assertNotEqual(default["digest"], enabled["digest"])
        measure.stage_tool_inputs(fixture.context, fixture.config)
        with self.assertRaisesRegex(ValueError, "JS source inventory"):
            measure.prepare_js_manifest(fixture.context, [
                measure.inventory(fixture.context, "base", {}, include_js=True), default], fixture.config)
        for invalid in (1, None, "true"):
            with self.assertRaisesRegex(ValueError, "bool"):
                measure.inventory(fixture.context, "head", {}, include_js=invalid)

    def test_public_probe_archives_only_materialized_owned_records(self):
        fixture = JSFixture()
        self.addCleanup(fixture.close)
        fixture.git.write("package.json", '{"type":"module","exports":"./missing.mjs"}\n')
        fixture.git.commit("fixture: native producer cannot resolve declared package root")
        code, stdout, stderr = run_capture(
            [sys.executable, "-B", str(SCRIPTS / "probe.py"), "--repo", str(fixture.git.root),
             "--base", fixture.base_sha, "--slug", "js-public", "--measurement-config",
             str(fixture.git.root / "measurement.json")], idle=120, max_total=900)
        self.assertEqual(code, 1, stderr)
        report = graph.load_json(stdout)
        self.assertEqual(report["verdict"], "fail")
        self.assertEqual(report["metrics"]["cycles"]["state"], "unavailable")
        self.assertEqual(report["metrics"]["diff_coverage_pct"]["state"], "unavailable")
        archive = fixture.git.root / ".ai/js-public/evidence/runs" / report["run_id"] / "measurement"
        manifest = report["artifact_manifest"]
        expected = sorted([row["artifact"]["path"] for row in manifest["inputs"]] + ["manifest.json"])
        self.assertEqual(sorted(path.relative_to(archive).as_posix() for path in archive.rglob("*") if path.is_file()),
                         expected)
        for row in manifest["inputs"]:
            self.assertEqual(graph.artifact(archive, row["artifact"]["path"]), row["artifact"])
        self.assertIn(graph.syntax_name("base", "old/deleted.mjs"), manifest["reserved_outputs"])
        self.assertIn(graph.syntax_name("base", "deleted.py"), manifest["reserved_outputs"])
        capture = graph.load_json((archive / "head/js/command.json").read_bytes())
        self.assertEqual(capture["returncode"], 2)
        self.assertIsNone(capture["result"])
        self.assertIsNone(capture["symbols"])
        for receipt in report["parsed"]["head"]["receipts"]:
            if Path(receipt["path"]).suffix in measure.JS_EXT:
                self.assertEqual((receipt["state"], receipt["unit_count"], receipt["reason"]),
                                 ("failed", None, "js-command-nonzero 2"))
                self.assertNotIn(graph.syntax_name("head", receipt["path"]), expected)


class JSOutputPolicyTests(unittest.TestCase):
    def test_actual_failed_children_are_opaque_and_zero_invalid_children_reject(self):
        # These deliberately different fixture commands test output admission,
        # not the fixed-producer invocation checks or positive semantic acceptance.
        node = source_tools(("typescript",))["typescript"]["executable"]
        cases = [
            ("absent", "", 7, "", False, False),
            ("symbols-only", "fs.writeFileSync('head/js/symbols.json', Buffer.from([255]));", 7, "", False, True),
            ("truncated", "fs.writeFileSync('head/js/result.json', '{');", 7, "", True, False),
            ("valid-looking", "fs.writeFileSync('head/js/result.json', '{\"state\":\"produced\"}');"
             "fs.writeFileSync('head/js/symbols.json', '{}');", 7, "", True, True),
            ("zero-absent", "", 0, "", False, False),
            ("zero-invalid", "fs.writeFileSync('head/js/result.json', '{');"
             "fs.writeFileSync('head/js/symbols.json', '{}');", 0, "", True, True),
            ("zero-stderr", "", 0, " ", False, False),
        ]
        for name, source, status, error, has_result, has_symbols in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory(prefix="jso-") as temporary:
                root = Path(temporary).resolve()
                (root / "head/js").mkdir(parents=True)
                argv = [node, "--input-type=module", "-e",
                        "import fs from 'node:fs';" + source + "process.stderr.write(" + json.dumps(error) +
                        ");process.exitCode=" + str(status)]
                code, stdout, stderr = run_capture(argv, cwd=root, idle=30, max_total=90)
                self.assertEqual((code, stderr), (status, error), stdout + stderr)
                context = {"run_root": str(root)}
                command = {"returncode": code, "stdout": stdout, "stderr": stderr}
                for slot, present in (("result", has_result), ("symbols", has_symbols)):
                    command[slot] = graph.artifact(root, f"head/js/{slot}.json") if present else None
                before = {slot: (root / f"head/js/{slot}.json").read_bytes()
                          for slot in ("result", "symbols") if command[slot] is not None}
                if code:
                    self.assertEqual(graph._js_output_records(context, {"revision": "head"}, {}, command), (None, None))
                else:
                    with self.assertRaises(ValueError):
                        graph._js_output_records(context, {"revision": "head"}, {}, command)
                self.assertEqual(before, {slot: (root / f"head/js/{slot}.json").read_bytes() for slot in before})

    def test_actual_bounded_timeout_is_failed_output_not_a_cleanup_claim(self):
        node = source_tools(("typescript",))["typescript"]["executable"]
        with tempfile.TemporaryDirectory(prefix="jst-") as temporary:
            code, stdout, stderr = run_capture([node, "-e", "setInterval(()=>{},1000)"],
                                               cwd=temporary, idle=1, max_total=5)
            self.assertEqual(code, 124, stdout + stderr)
            command = {"returncode": code, "stdout": stdout, "stderr": stderr, "result": None, "symbols": None}
            self.assertEqual(graph._js_output_records({"run_root": str(Path(temporary).resolve())},
                                                      {"revision": "head"}, {}, command), (None, None))


class JSOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = JSFixture()
        cls.addClassCleanup(cls.fixture.close)
        cls.fixture.produce()
        cls.raw = Path(cls.fixture.context["run_root"])
        cls.originals = {path.relative_to(cls.raw).as_posix(): path.read_bytes()
                         for path in cls.raw.rglob("*") if path.is_file()}
        cls.objects = copy.deepcopy({key: getattr(cls.fixture, key) for key in (
            "context", "base", "head", "manifest", "observations")})

    def tearDown(self):
        for name, content in self.originals.items():
            (self.raw / name).write_bytes(content)
        for key, value in self.objects.items():
            setattr(self.fixture, key, copy.deepcopy(value))

    def write(self, name, value):
        (self.raw / name).write_bytes(graph._json_bytes(value))
        return graph.artifact(self.raw, name)

    def rebind(self):
        fixture = self.fixture
        for side in ("base", "head"):
            request_ref, request = graph._js_json(fixture.context, f"{side}/js/request.json")
            _, command = graph._js_json(fixture.context, f"{side}/js/command.json")
            _, result = graph._js_json(fixture.context, f"{side}/js/result.json")
            result["request"] = command["request"] = request_ref
            result["symbols"] = command["symbols"] = graph.artifact(self.raw, f"{side}/js/symbols.json")
            command["result"] = self.write(f"{side}/js/result.json", result)
            self.write(f"{side}/js/command.json", command)
        inventories = [fixture.base["inventory"], fixture.head["inventory"]]
        produced = graph._js_manifest(fixture.context, fixture.config, inventories, phase="js-produced.json")
        fixture.context["output_manifest"] = self.write("js-produced.json", produced)
        for parsed in (fixture.base, fixture.head):
            for ref in parsed["syntax_artifacts"].values():
                (self.raw / ref["path"]).unlink()
            (self.raw / graph.graph_name(parsed["inventory"]["revision"])).unlink()
        fixture.base, fixture.head = [graph.parse_files(fixture.context, inv, fixture.config) for inv in inventories]
        fixture.manifest = measure.make_manifest(fixture.context, fixture.base, fixture.head)
        fixture.context["output_manifest"] = self.write("manifest.json", fixture.manifest)
        fixture.observations = [item for pair in measure.collect_pair(
            fixture.context, fixture.config, fixture.base, fixture.head).values() for item in pair]

    def test_rehashed_predecessor_ownership_and_reservations_reject(self):
        for mutation in ("missing", "wrong-role", "duplicate", "forward", "reservation"):
            with self.subTest(mutation=mutation):
                self.tearDown()
                fixture = self.fixture
                _, produced = graph._js_json(fixture.context, "js-produced.json")
                if mutation == "missing":
                    produced["inputs"].pop()
                elif mutation == "wrong-role":
                    produced["inputs"][0]["role"] = "qualification"
                elif mutation == "duplicate":
                    produced["inputs"].append(produced["inputs"][0])
                elif mutation == "forward":
                    produced["inputs"].append({"artifact": fixture.context["output_manifest"],
                                               "role": "manifest", "revision": None})
                else:
                    produced["reserved_outputs"].pop()
                changed = self.write("js-produced.json", produced)
                for row in fixture.manifest["inputs"]:
                    if row["artifact"]["path"] == "js-produced.json":
                        row["artifact"] = changed
                fixture.context["output_manifest"] = self.write("manifest.json", fixture.manifest)
                with self.assertRaises(ValueError):
                    graph.parse_files(fixture.context, fixture.head["inventory"], fixture.config)

    def test_rehashed_production_purpose_swap_rejects_before_replay(self):
        fixture = self.fixture
        _, request = graph._js_json(fixture.context, "head/js/request.json")
        request["purpose"] = "validate"
        self.write("head/js/request.json", request)
        self.rebind()
        with self.assertRaisesRegex(ValueError, "purpose"):
            fixture.validate()

    def test_rehashed_alias_edit_rejected_by_fresh_accepting_replay(self):
        fixture = self.fixture
        _, symbols = graph._js_json(fixture.context, "head/js/symbols.json")
        self.assertTrue(symbols["aliases"])
        symbols["aliases"][0]["name"] += "_forged"
        self.write("head/js/symbols.json", symbols)
        self.rebind()
        with self.assertRaisesRegex(ValueError, "JS replay symbol semantics"):
            fixture.validate()

    def test_source_controller_and_request_input_changes_reject(self):
        fixture = self.fixture
        for name in ("plain.js", "package.json", "measurement.json"):
            with self.subTest(source=name):
                path = Path(fixture.context["head_root"]) / name
                before = path.read_bytes()
                try:
                    path.write_bytes(before + b" ")
                    with self.assertRaises(ValueError):
                        measure._check_js_sources(fixture.context, [fixture.head["inventory"]], fixture.config)
                finally:
                    path.write_bytes(before)
        controller = Path(fixture.context["controller_root"]) / "measure_js.mjs"
        before = controller.read_bytes()
        try:
            controller.write_bytes(before + b"\n")
            with self.assertRaisesRegex(ValueError, "controller"):
                measure._check_js_sources(fixture.context, [fixture.head["inventory"]], fixture.config)
        finally:
            controller.write_bytes(before)
        _, request = graph._js_json(fixture.context, "head/js/request.json")
        request["inputs"].pop()
        self.write("head/js/request.json", request)
        with self.assertRaises(ValueError):
            graph._js_transport(fixture.context, fixture.head["inventory"], fixture.config)

    def test_actual_nonzero_child_retains_real_produced_records_only_as_failure_bytes(self):
        fixture = self.fixture
        _, _, result, symbols, _, _ = graph._js_transport(fixture.context, fixture.head["inventory"], fixture.config)
        self.assertEqual(result["state"], "produced")
        self.assertTrue(symbols["files"])
        with tempfile.TemporaryDirectory(prefix="jsopaque-") as temporary:
            root = Path(temporary).resolve()
            (root / "head/js").mkdir(parents=True)
            code, stdout, stderr = run_capture([
                fixture.config["tools"]["typescript"]["executable"], "--input-type=module", "-e",
                "import fs from 'node:fs';"
                "for(const slot of ['result','symbols']) fs.copyFileSync("
                + json.dumps(str(self.raw)) + "+'/head/js/'+slot+'.json','head/js/'+slot+'.json');"
                "process.exitCode=7;"], cwd=root, idle=30, max_total=90)
            self.assertEqual((code, stderr), (7, ""), stdout + stderr)
            command = {"returncode": code, "stdout": stdout, "stderr": stderr,
                       **{slot: graph.artifact(root, f"head/js/{slot}.json") for slot in ("result", "symbols")}}
            self.assertEqual(graph._js_output_records({**fixture.context, "run_root": str(root)},
                                                      fixture.head["inventory"], {}, command), (None, None))
            for slot in ("result", "symbols"):
                self.assertEqual((root / f"head/js/{slot}.json").read_bytes(),
                                 (self.raw / f"head/js/{slot}.json").read_bytes())
