"""Real qualified scalar execution and source-bound normalization tests."""

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

from helpers import SCRIPTS
from test_measure_inventory import Q1Fixture
from test_measure_source_bindings import source_tools
import measure
import measure_graph as graph
import measure_scalars as scalars

EVIDENCE = SCRIPTS.parent / ".ai/workflow-reliability/evidence"


def native_bindings():
    historical = graph.load_json((EVIDENCE / "q2-tools-manifest.json").read_bytes())
    bindings = {}
    for name in ("jscpd", "ruff"):
        binding = copy.deepcopy(historical["tools"][name]["binding"])
        for ref in [binding["help"], binding["configuration"], *binding["qualification"]]:
            filename = Path(ref["path"]).name
            actual = graph.artifact(EVIDENCE, filename)
            if (actual["sha256"], actual["bytes"]) != (ref["sha256"], ref["bytes"]):
                raise ValueError("Relocated qualification differs from historical identity")
            ref["path"] = filename
        binding["qualification"].append(graph.artifact(EVIDENCE, "q2-tools-runtime-bindings.json"))
        bindings[name] = binding
    return bindings


class ScalarArithmeticTests(unittest.TestCase):
    def test_duplicate_locations_are_unioned_not_averaged(self):
        import measure_scalars as scalars
        payload = {"files": [
            {"path": "a.py", "source_sha256": "a" * 64, "source_lines": 10, "processed": True},
            {"path": "b.py", "source_sha256": "b" * 64, "source_lines": 20, "processed": True}],
            "clones": [
                {"locations": [{"path": "a.py", "start_line": 1, "end_line": 5},
                               {"path": "b.py", "start_line": 2, "end_line": 6}]},
                {"locations": [{"path": "a.py", "start_line": 3, "end_line": 7},
                               {"path": "b.py", "start_line": 4, "end_line": 8}]}]}
        self.assertEqual(scalars.duplication_value(payload), round(100 * 14 / 30, 2))
        for bad in (True, 0, -1, 11):
            forged = copy.deepcopy(payload)
            forged["clones"][0]["locations"][0]["end_line"] = bad
            with self.subTest(end=bad), self.assertRaises(ValueError):
                scalars.duplication_value(forged)
        payload["clones"] = []
        self.assertEqual(scalars.duplication_value(payload), 0)
        payload["files"] = []
        self.assertIsNone(scalars.duplication_value(payload))

    def test_empty_function_population_is_unavailable(self):
        import measure_scalars as scalars
        self.assertEqual(scalars.complexity_values({"files": []}), (None, None))
        payload = {"files": [
            {"functions": [{"cyclomatic_complexity": 2}, {"cyclomatic_complexity": 5}]},
            {"functions": []}]}
        self.assertEqual(scalars.complexity_values(payload), (5, 3.5))
        payload["files"][0]["functions"][0]["cyclomatic_complexity"] = True
        with self.assertRaises(ValueError):
            scalars.complexity_values(payload)

    def test_ruff_unicode_columns_preserve_crlf_bytes(self):
        import measure_scalars as scalars
        data = 's = "caf\u00e9\U0001f600"; missing_name\r\n'.encode("utf-8")
        span = scalars.source_span(data, 1, 14, 1, 26)
        self.assertEqual(data[span["start_byte"]:span["end_byte"]], b"missing_name")
        for args in ((0, 1, 1, 2), (1, True, 1, 2), (1, 1, 1, 999)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                scalars.source_span(data, *args)

    def test_physical_lines_do_not_split_unicode_separators(self):
        data = 's = "\u2028"\r\n\fmissing_name\r\n'.encode("utf-8")
        span = scalars.source_span(data, 2, 2, 2, 14)
        self.assertEqual(data[span["start_byte"]:span["end_byte"]], b"missing_name")
        span = scalars._line_span(data, 2, 2)
        self.assertEqual(data[span["start_byte"]:span["end_byte"]], b"\fmissing_name")


class ScalarToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {"tools": {**native_bindings(), **source_tools(("lizard", "vulture"))},
                      "tool_artifact_root": str(EVIDENCE)}
        cls.bindings = measure._qualified_inputs(cls.config)
        cls.rules = graph.load_json((EVIDENCE / "q2-tools-ruff-rules.json").read_bytes())["rule_ids"]

    def directory(self):
        temporary = tempfile.TemporaryDirectory(prefix="scalar-")
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name).resolve()

    def capture(self, label, output):
        root = os.environ.get("SCALAR_EVIDENCE")
        if root:
            with (graph.root_path(root) / (self._testMethodName + "-" + label + ".json")).open(
                    "x", encoding="utf-8") as stream:
                json.dump(output, stream, ensure_ascii=True, indent=2)

    def source_run(self, tool, files):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        for name, content in files.items():
            fixture.git.write(name, content)
        fixture.build()
        output = scalars._source_command(
            fixture.context, fixture.head, tool, self.bindings[tool], self.directory())
        self.capture(tool, output)
        self.assertEqual(output["returncode"], 0, output["stderr"])
        self.assertEqual(output["stderr"], "")
        sources = {entry["path"]: (Path(fixture.context["head_root"]) / entry["path"]).read_bytes()
                   for entry, receipt in zip(fixture.head["inventory"]["entries"], fixture.head["receipts"])
                   if receipt["state"] == "processed" and entry["language"] == "python"}
        return output["result"], sources

    def test_lizard_actual_utf8_crlf_nested_and_zero_functions(self):
        result, sources = self.source_run("lizard", {
            "nested.py": ('# caf\u00e9\r\nasync def outer(value):\r\n'
                          '    def inner(item):\r\n        return item if item else 0\r\n'
                          '    return inner(value)\r\n').encode("utf-8"),
            "empty.py": b"", "comment.py": b"# only a comment\r\n"})
        rows = {row["path"]: row for row in result["files"]}
        self.assertEqual(rows["empty.py"]["functions"], [])
        self.assertEqual(rows["comment.py"]["functions"], [])
        self.assertEqual(len(rows["nested.py"]["functions"]), 2)
        self.assertTrue(all(row["reader"] == "PythonReader" for row in rows.values()))
        payload = scalars._complexity_payload(sources, result)
        values = scalars.complexity_values(payload)
        self.assertEqual(values[0], 2)
        self.assertGreater(values[1], 1)
        self.assertTrue(result["imports"])

    def test_lizard_actual_suppression_rejects_not_string_literals(self):
        result, sources = self.source_run("lizard", {
            "generated.py": b"# GENERATED CODE\ndef visible():\n    return 1\n",
            "forgiven.py": b"#lizard forgive\ndef visible():\n    return 1\n",
            "literal.py": b'def ordinary():\n    return "GENERATED CODE"\n'})
        rows = {row["path"]: row for row in result["files"]}
        self.assertEqual(rows["generated.py"]["state"], "failed")
        self.assertEqual(rows["forgiven.py"]["state"], "failed")
        self.assertEqual(rows["literal.py"]["state"], "processed")
        payload = scalars._complexity_payload(sources, result)
        self.assertTrue(next(row for row in payload["files"] if row["path"] == "generated.py")["diagnostics"])

    def test_lizard_strict_decode_failure_retains_other_file_receipts(self):
        result, sources = self.source_run("lizard", {
            "latin.py": b'# coding: latin-1\nname = "caf\xe9"\n',
            "valid.py": b"def branch(value):\n    return value if value else 0\n"})
        rows = {row["path"]: row for row in result["files"]}
        self.assertEqual(rows["latin.py"]["state"], "failed")
        self.assertIn("UnicodeDecodeError", rows["latin.py"]["reason"])
        self.assertEqual(rows["valid.py"]["state"], "processed")
        payload = scalars._complexity_payload(sources, result)
        self.assertTrue(next(row for row in payload["files"] if row["path"] == "latin.py")["diagnostics"])

    def test_vulture_actual_complete_batch_confidence_directives_and_resources(self):
        result, sources = self.source_run("vulture", {
            "unused.py": b"import os\ndef never_called():\n    return 1\n    print('unreachable')\n",
            "used.py": b"import math\nprint(math.sqrt(4))\n",
            "noqa.py": b"import pathlib  # noqa: V104\n", "empty.py": b""})
        findings = scalars._vulture_findings(sources, result)
        self.assertTrue(any(item["symbol"] == "os" and item["confidence"] == 90 for item in findings))
        self.assertTrue(any(item["rule"] == "VULTURE-unreachable_code" for item in findings))
        self.assertFalse(any(item["symbol"] in {"never_called", "pathlib"} for item in findings))
        self.assertEqual({row["path"] for row in result["files"]}, set(sources))
        self.assertTrue(all(row["state"] == "processed" for row in result["files"]))
        self.assertTrue(scalars._python_directives(sources))
        self.assertTrue(result["resources_read"])

    def test_vulture_type_comment_error_preserves_failed_batch_evidence(self):
        result, _ = self.source_run("vulture", {
            "bad_type.py": (b"def duplicate():  # type: () -> int\n"
                            b"    # type: () -> int\n    return 1\n")})
        rows = {row["path"]: row for row in result["files"]}
        self.assertEqual(rows["bad_type.py"]["state"], "failed")
        self.assertNotEqual(rows["bad_type.py"]["after"], 0)
        self.assertIn("type comment", rows["bad_type.py"]["stderr"])
        self.assertEqual(result["resources_read"], [])

    def test_jscpd_actual_clone_union_short_empty_and_comment_census(self):
        code = ("# caf\u00e9\r\ndef calculate(value):\r\n    doubled = value * 2\r\n"
                "    offset = doubled + 10\r\n    divisor = offset / 4\r\n"
                "    remainder = divisor % 3\r\n    if remainder > 2:\r\n"
                "        return remainder - 3\r\n    return offset + 7\r\n").encode("utf-8")
        sources = {"a.py": code, "b.py": code, "short.py": b"value = 1\n",
                   "empty.py": b"", "comment.py": b"# comment only\n"}
        clone_dir, census_dir = self.directory(), self.directory()
        executable = self.bindings["jscpd"]["executable"]["path"]
        clone = scalars._native_command("jscpd", executable, sources, clone_dir)
        census = scalars._native_command("jscpd", executable, sources, census_dir, census=True)
        self.capture("clone", clone)
        self.capture("census", census)
        self.assertEqual(clone["returncode"], 0, clone["stderr"])
        self.assertEqual(census["returncode"], 0, census["stderr"])
        payload = scalars._jscpd_payload(sources, clone["result"], census["result"],
                                        clone_dir / "inputs", census_dir / "inputs")
        self.assertEqual({row["path"] for row in payload["files"]}, set(sources))
        self.assertEqual(len(payload["clones"]), 1)
        self.assertEqual(scalars.duplication_value(payload), 90)
        forged = copy.deepcopy(census["result"])
        forged["summary"]["files"] = [row for row in forged["summary"]["files"]
                                      if not row["path"].endswith("short.py")]
        forged["summary"]["totalFiles"] -= 1
        with self.assertRaisesRegex(ValueError, "omitted"):
            scalars._jscpd_payload(sources, clone["result"], forged,
                                  clone_dir / "inputs", census_dir / "inputs")

    def test_ruff_actual_explicit_files_rules_unicode_and_noqa(self):
        directory = self.directory()
        sources = {"unicode.py": 's = "caf\u00e9\U0001f600"; missing_name\r\n'.encode("utf-8"),
                   "clean.py": b"print('ok')\n", "empty.py": b"",
                   "noqa.py": b"import os  # noqa: F401\n"}
        output = scalars._native_command("ruff", self.bindings["ruff"]["executable"]["path"],
                                          sources, directory, rules=self.rules)
        self.capture("ruff", output)
        self.assertEqual(output["returncode"], 1, output["stderr"])
        findings = scalars._ruff_findings(sources, output["result"], directory / "inputs", self.rules)
        self.assertEqual({finding["rule"] for finding in findings},
                         {"RUFF-E702", "RUFF-B018", "RUFF-F821"})
        span = next(finding["span"] for finding in findings if finding["rule"] == "RUFF-F821")
        self.assertEqual(sources["unicode.py"][span["start_byte"]:span["end_byte"]], b"missing_name")
        self.assertTrue(scalars._python_directives(sources))

    def test_ruff_actual_unicode_separator_and_formfeed_coordinates(self):
        directory = self.directory()
        sources = {"physical.py": 's = "\u2028"\r\n\fmissing_name\r\n'.encode("utf-8")}
        output = scalars._native_command("ruff", self.bindings["ruff"]["executable"]["path"],
                                        sources, directory, rules=self.rules)
        self.capture("ruff", output)
        self.assertEqual(output["returncode"], 1, output["stderr"])
        findings = scalars._ruff_findings(sources, output["result"], directory / "inputs", self.rules)
        span = next(finding["span"] for finding in findings if finding["rule"] == "RUFF-F821")
        self.assertEqual(sources["physical.py"][span["start_byte"]:span["end_byte"]], b"missing_name")


if __name__ == "__main__":
    unittest.main()
