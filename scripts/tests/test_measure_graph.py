import copy
import json
import os
from pathlib import Path
import sys
import unittest

from test_measure_inventory import Q1Fixture
import measure
import measure_graph as graph
from evidence import write_json_atomic
from helpers import SCRIPTS, run_capture


class GraphTests(unittest.TestCase):
    def fixture(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        return fixture

    def test_effective_frozen_binding_respects_startup_precedence_and_consistency(self):
        fixture = self.fixture()
        fixture.git.write("__phello__/__init__.py", "")
        fixture.git.write("__phello__/spam.py", "LOCAL = True\n")
        fixture.git.commit("fixture: independently shadowable frozen package")
        child = (
            "import sys; sys.path.insert(0,%r); import measure_graph as g; "
            "import importlib,json,os; sys.path.insert(0,%r); "
            "table=g._frozen_import_binding(); before=g.parser_digest(); "
            "module=importlib.import_module('__phello__.spam'); "
            "os.environ['PYTHON_FROZEN_MODULES']='off' if table.get('__phello__') else 'on'; "
            "sys._xoptions['frozen_modules']=os.environ['PYTHON_FROZEN_MODULES']; "
            "print(json.dumps({'table':table,'digest':before,'after':g.parser_digest(),"
            "'table_after':g._frozen_import_binding(),'native_origin':module.__spec__.origin,"
            "'local':getattr(module,'LOCAL',False)}))"
        ) % (str(SCRIPTS), str(fixture.git.root))
        cases = [
            ("default", None, [], None),
            ("env-on", "on", [], True),
            ("env-off", "off", [], False),
            ("cli-off", "on", ["-X", "frozen_modules=off"], False),
            ("cli-on", "off", ["-X", "frozen_modules=on"], True),
            ("last-off", "on", ["-X", "frozen_modules=on", "-X", "frozen_modules=off"], False),
            ("last-on", "off", ["-X", "frozen_modules=off", "-X", "frozen_modules=on"], True),
            ("ignored-off", "off", ["-E"], None),
            ("ignored-on", "on", ["-E"], None),
            ("isolated-off", "off", ["-I"], None),
        ]
        results = {}
        for label, setting, options, expected in cases:
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            env.pop("PYTHON_FROZEN_MODULES", None)
            if setting is not None:
                env["PYTHON_FROZEN_MODULES"] = setting
            argv = [sys.executable, "-B", "-S", *options, "-c", child]
            code, output, error = run_capture(argv, cwd=fixture.git.root, idle=30, max_total=90, env=env)
            self.assertEqual(code, 0, error)
            result = json.loads(output)
            print(json.dumps({"case": label, "argv": argv,
                              "environment_delta": {"PYTHON_FROZEN_MODULES": setting,
                                                    "PYTHONDONTWRITEBYTECODE": "1"},
                              "exit_code": code, "observation": result}))
            results[label] = result
            with self.subTest(mode=label):
                active = result["table"].get("__phello__") is not None
                if expected is not None:
                    self.assertEqual(active, expected)
                self.assertEqual(result["native_origin"] == "frozen", active)
                self.assertEqual(result["local"], not active)
                self.assertEqual(result["digest"], result["after"],
                                 "Changing raw settings after startup must not rewrite effective import identity")
                self.assertEqual(result["table"], result["table_after"])
        on, off = results["env-on"], results["env-off"]
        self.assertLess(set(off["table"]), set(on["table"]),
                        "Disabled optional modules are absent from the runtime's available-name census")
        self.assertGreater(len(on["table"]), 2, "Bind the census, not one fixture sentinel")
        self.assertNotEqual(on["digest"], off["digest"])
        self.assertNotEqual(on["table"], off["table"])
        for label in ("cli-on", "last-on"):
            self.assertEqual(results[label]["digest"], on["digest"])
        for label in ("cli-off", "last-off"):
            self.assertEqual(results[label]["digest"], off["digest"])
        for label in ("ignored-off", "ignored-on", "isolated-off"):
            self.assertEqual(results[label]["digest"], results["default"]["digest"])

    def test_runtime_precedence_preserves_shadowable_and_relative_names(self):
        fixture = self.fixture()
        for name in ("sys", "time", "os"):
            fixture.git.write(name + ".py", "import scripts.evidence\n")
        fixture.git.write("scripts/evidence.py", "import sys\nfrom time import monotonic\nimport os.path\n")
        fixture.git.write("fractions.py", "LOCAL = True\n")
        fixture.git.write("pkg/__init__.py", "")
        fixture.git.write("pkg/sys.py", "LOCAL = True\n")
        fixture.git.write("pkg/inner.py", "from . import sys\n")
        fixture.git.write("a.py", "import fractions\nfrom pkg import inner\n")
        fixture.build()
        _, output, _ = fixture.git.run(
            sys.executable, "-B", "-S", "-c",
            "import sys,time,os,a,json; "
            "assert a.fractions.LOCAL; assert a.inner.sys.LOCAL; "
            "print(json.dumps([sys.__spec__.origin,time.__spec__.origin,os.__spec__.origin]))")
        self.assertEqual(json.loads(output), ["built-in", "built-in", "frozen"])
        fixture.validate()
        self.assertFalse(fixture.head["graph"]["unresolved"])
        local = {(edge["from"], edge["to"]) for edge in fixture.head["graph"]["edges"]
                 if edge["resolution"] == "local"}
        self.assertFalse({("scripts/evidence.py", name + ".py") for name in ("sys", "time", "os")} & local)
        self.assertIn(("a.py", "fractions.py"), local)
        self.assertIn(("pkg/inner.py", "pkg/sys.py"), local)
        self.assertEqual(fixture.summary()["metrics"]["cycles"]["head"], 0)
        self.assertEqual(fixture.summary()["metrics"]["architecture_rules"]["head"], 0)

    def test_runtime_nonpackage_child_is_unresolved_not_a_local_namesake(self):
        fixture = self.fixture()
        fixture.git.write("time/child.py", "LOCAL = True\n")
        fixture.git.write("a.py", "import time.child\n")
        fixture.build()
        _, _, error = fixture.git.run(sys.executable, "-B", "-S", "-c", "import a", expected=1)
        self.assertIn("'time' is not a package", error)
        self.assertIn("Runtime module is not a package",
                      {item["reason"] for item in fixture.head["graph"]["unresolved"]})
        self.assertEqual(fixture.summary()["metrics"]["cycles"]["state"], "unavailable")

    def test_zero_import_receipts_complete_and_source_bytes_are_not_executed(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "raise RuntimeError('must never execute source')\n")
        fixture.git.write("b.py", b"# coding: utf-8\r\nlabel = '\xc3\xa9'\r\n")
        fixture.git.write("c.py", "")
        fixture.build()
        fixture.validate()
        receipts = {receipt["path"]: receipt for receipt in fixture.head["receipts"]}
        for name in ("a.py", "b.py", "c.py"):
            self.assertEqual(receipts[name]["unit_count"], 0)
            self.assertEqual(receipts[name]["state"], "processed")
            self.assertEqual(len(receipts[name]["raw"]), 1)
        summary = fixture.summary()
        self.assertEqual(summary["metrics"]["cycles"]["head"], 0)
        self.assertEqual(summary["metrics"]["cycles"]["state"], "measured")
        self.assertEqual(summary["completeness"], "incomplete")
        self.assertEqual(len(summary["missing_required"]), 7)

    def test_absolute_relative_conditional_local_and_external_imports(self):
        fixture = self.fixture()
        fixture.git.write("pkg/__init__.py", "")
        fixture.git.write("pkg/child.py", "if True:\n    import a\n\ndef f():\n    from . import sibling\n")
        fixture.git.write("pkg/sibling.py", "import os\nimport imaginary_external\n")
        fixture.git.write("a.py", "from pkg import child\n")
        fixture.build()
        fixture.validate()
        edges = {(item["from"], item["to"], item["resolution"]) for item in fixture.head["graph"]["edges"]}
        self.assertTrue({("a.py", "pkg/child.py", "local"),
                         ("a.py", "pkg/__init__.py", "local"),
                         ("pkg/child.py", "pkg/sibling.py", "local"),
                         ("pkg/child.py", "a.py", "local"),
                         ("pkg/sibling.py", "os", "external"),
                         ("pkg/sibling.py", "imaginary_external", "external")} <= edges)
        self.assertFalse(fixture.head["graph"]["unresolved"])
        self.assertGreater(fixture.summary()["metrics"]["cycles"]["head"], 0)

    def test_replaced_cycle_fails_at_equal_count_and_line_moves_preserve_identity(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "import b\n")
        fixture.git.write("b.py", "import a\n")
        fixture.base_sha = fixture.git.commit("fixture: old cycle")
        fixture.git.write("a.py", "\nimport c\n")
        fixture.git.write("b.py", "value = 1\n")
        fixture.git.write("c.py", "import a\n")
        fixture.build()
        metric = fixture.summary()["metrics"]["cycles"]
        self.assertEqual((metric["base"], metric["head"]), (1, 1))
        self.assertEqual(metric["comparison"], "fail")
        self.assertEqual(len(metric["new_ids"]), 1)
        original = copy.deepcopy(fixture.head["graph"])
        for edge in original["edges"]:
            edge["span"]["start_line"] += 10
        self.assertEqual(graph.enumerate_cycles(original), fixture.head["graph"]["cycles"])

    def test_elementary_cycles_include_self_loops_and_direction(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "import a\nimport b\nimport c\n")
        fixture.git.write("b.py", "import a\nimport c\n")
        fixture.git.write("c.py", "import a\nimport b\n")
        fixture.build()
        cycles = fixture.head["graph"]["cycles"]
        self.assertEqual(len(cycles), 6)  # three pairs, two directed triangles and self.
        self.assertIn(["a.py"], [cycle["ordered_nodes"] for cycle in cycles])
        self.assertIn(["a.py", "b.py", "c.py"], [cycle["ordered_nodes"] for cycle in cycles])
        self.assertIn(["a.py", "c.py", "b.py"], [cycle["ordered_nodes"] for cycle in cycles])

    def test_missing_ambiguous_and_escaping_imports_are_incomplete(self):
        fixture = self.fixture()
        fixture.config["python_source_roots"] = [".", "scripts"]
        fixture.save_config()
        fixture.git.write("scripts/a.py", "")
        fixture.git.write("b.py", "import a\nfrom pkg import missing\n")
        fixture.git.write("pkg/child.py", "from ... import missing\n")
        fixture.build()
        reasons = {item["reason"] for item in fixture.head["graph"]["unresolved"]}
        self.assertIn("Ambiguous local module", reasons)
        self.assertIn("Missing namespace child module", reasons)
        self.assertIn("Relative import escapes package context", reasons)
        self.assertEqual(fixture.summary()["metrics"]["cycles"]["state"], "unavailable")

    def test_invalid_python_and_mixed_languages_remain_explicit(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "return 1\n")  # AST parse alone would accept this.
        fixture.git.write("other.mjs", "export const value = 1;\n")
        fixture.git.write("other.go", "package main\n")
        fixture.build()
        fixture.validate()
        receipts = {item["path"]: item for item in fixture.head["receipts"]}
        self.assertEqual(receipts["a.py"]["state"], "failed")
        self.assertEqual(receipts["other.mjs"]["state"], "unsupported")
        self.assertEqual(receipts["other.go"]["state"], "unsupported")
        self.assertEqual(len(receipts), len(fixture.head["inventory"]["entries"]))
        self.assertEqual(fixture.summary()["metrics"]["architecture_rules"]["comparison"], "unavailable")

    def test_compiled_architecture_rules_and_dynamic_disclosure(self):
        fixture = self.fixture()
        fixture.git.write("scripts/evidence.py", "import a\nimport imaginary_external\n"
                          "from importlib import import_module as load\nload('a')\n")
        fixture.git.write("scripts/run.py", "import subprocess\nsubprocess.run(['unknown'])\n")
        fixture.git.write("scripts/probe.py", "import scripts.bridge\nimport tests.helper\n")
        fixture.git.write("scripts/bridge.py", "import scripts.workflow_state\n")
        fixture.git.write("scripts/workflow_state.py", "")
        fixture.git.write("tests/helper.py", "")
        fixture.git.write("evals/lib/client.py", "import scripts.bridge\n")
        fixture.build()
        findings = graph.evaluate_rules(fixture.head["graph"], fixture.config["architecture_rules"])
        self.assertEqual({item["rule"] for item in findings}, set(graph.RULE_IDS))
        sites = fixture.head["graph"]["outside_model"]
        self.assertEqual({site["kind"] for site in sites}, {"computed-import", "runtime-command"})
        self.assertFalse(any(item["rule"] == "ARCH05" and item["path"] == "scripts/run.py" for item in findings))
        self.assertEqual(fixture.summary()["metrics"]["architecture_rules"]["comparison"], "fail")

    def test_replaced_architecture_identity_fails_even_when_total_falls(self):
        fixture = self.fixture()
        fixture.git.write("scripts/evidence.py", "import alpha_external\nimport beta_external\n")
        fixture.base_sha = fixture.git.commit("fixture: old violations")
        fixture.git.write("scripts/evidence.py", "import new_external\n")
        fixture.build()
        metric = fixture.summary()["metrics"]["architecture_rules"]
        self.assertEqual((metric["base"], metric["head"]), (2, 1))
        self.assertEqual(metric["comparison"], "fail")
        self.assertEqual(len(metric["new_ids"]), 1)

    def test_graph_receipt_summary_and_artifact_corruption_rejected(self):
        fixture = self.fixture().materialize()
        fixture.validate()
        original_head = copy.deepcopy(fixture.head)
        for modify in (
                lambda p: p["graph"]["nodes"].pop(),
                lambda p: p["graph"]["cycles"].append({"id": "0" * 64, "ordered_nodes": ["a.py"]}),
                lambda p: p["receipts"][0].update(source_sha256="0" * 64),
                lambda p: p["receipts"][0].update(unit_count=True),
                lambda p: p["receipts"][0].update(toolset_sha256="0" * 64),
                lambda p: p["receipts"][0].update(policy_sha256="0" * 64),
                lambda p: p["receipts"][0].update(run_id="other")):
            fixture.head = copy.deepcopy(original_head)
            modify(fixture.head)
            with self.assertRaises(ValueError):
                fixture.validate()
        fixture.head = original_head
        original_observations = copy.deepcopy(fixture.observations)
        for key, value in (("value", 123), ("state", "complete"), ("extra", 0)):
            fixture.observations = copy.deepcopy(original_observations)
            # An actually unavailable scalar must never be made measured.
            item = next(item for item in fixture.observations if item["metric"] == "complexity_max")
            item[key] = value
            with self.assertRaises(ValueError):
                fixture.validate()
        fixture.observations = original_observations
        ref = fixture.head["syntax_artifacts"]["a.py"]
        path = Path(fixture.context["run_root"]) / ref["path"]
        raw = json.loads(path.read_bytes())
        raw["literal_imports"] = [{"specifier": "forged", "kind": "import", "span": {
            "start_byte": 0, "end_byte": 1, "start_line": 1, "end_line": 1}}]
        write_json_atomic(path, raw)
        new_ref = graph.artifact(fixture.context["run_root"], ref["path"])
        fixture.head["syntax_artifacts"]["a.py"] = new_ref
        fixture.manifest = measure.make_manifest(fixture.context, fixture.base, fixture.head)
        write_json_atomic(Path(fixture.context["run_root"]) / "manifest.json", fixture.manifest)
        fixture.context["output_manifest"] = graph.artifact(fixture.context["run_root"], "manifest.json")
        with self.assertRaisesRegex(ValueError, "Syntax evidence"):
            fixture.validate()

    def test_rehashed_graph_payload_is_not_accepted_as_authoritative(self):
        fixture = self.fixture().materialize()
        path = Path(fixture.context["run_root"]) / "head/graph.json"
        raw = json.loads(path.read_bytes())
        raw["payload"]["graph"]["cycles"] = [{"id": "f" * 64, "ordered_nodes": ["a.py"]}]
        write_json_atomic(path, raw)
        fixture.manifest = measure.make_manifest(fixture.context, fixture.base, fixture.head)
        write_json_atomic(Path(fixture.context["run_root"]) / "manifest.json", fixture.manifest)
        fixture.context["output_manifest"] = graph.artifact(fixture.context["run_root"], "manifest.json")
        with self.assertRaisesRegex(ValueError, "Raw graph"):
            fixture.validate()

    def test_cycle_budget_is_unavailable_not_a_truncated_zero(self):
        fixture = self.fixture()
        names = ["dense%d" % index for index in range(9)]
        for name in names:
            fixture.git.write(name + ".py", "".join("import " + other + "\n" for other in names))
        fixture.build()
        summary = fixture.summary()
        self.assertEqual(summary["metrics"]["cycles"]["state"], "unavailable")
        self.assertIsNone(summary["metrics"]["cycles"]["head"])
        self.assertIn("budget exceeded", summary["metrics"]["cycles"]["reason"])
        self.assertEqual(summary["verdict"], "fail")

    def test_aliased_builtin_loader_and_importlib_calls_are_disclosed(self):
        fixture = self.fixture()
        fixture.git.write("scripts/evidence.py", "from builtins import __import__ as load\n"
                          "import importlib as loader\nload('a')\nloader.reload(loader)\n")
        fixture.build()
        sites = fixture.head["graph"]["outside_model"]
        self.assertEqual(len(sites), 2)
        self.assertEqual({site["kind"] for site in sites}, {"computed-import"})
        self.assertEqual(fixture.summary()["metrics"]["architecture_rules"]["comparison"], "fail")


if __name__ == "__main__":
    unittest.main()
