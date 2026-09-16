"""Public-CLI gaps found by independent I1 verification; no collector substitutes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

from helpers import GitFixture, SCRIPTS
from evidence import source_snapshot
from run import run_capture
import probe as probe_module

ROOT = SCRIPTS.parent
EVIDENCE = ROOT / ".ai/workflow-reliability/evidence"


class MeasurementE2ETests(unittest.TestCase):
    def setUp(self):
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        # Reuse the existing fixture operations, placing only this verifier's
        # scratch in its explicitly allowed worktree evidence namespace.
        self.fixture = GitFixture.__new__(GitFixture)
        self.fixture.directory = tempfile.TemporaryDirectory(
            prefix="i1-independent-fixture-space ", dir=EVIDENCE)
        self.fixture.root = Path(self.fixture.directory.name).resolve()
        self.addCleanup(self.fixture.close)
        self.root = self.fixture.root
        self.commands = []
        self.fixture.run = self.command
        self.command("git", "init", "--quiet")
        self.command("git", "config", "user.name", "Independent verification fixture")
        self.command("git", "config", "user.email", "verifier@example.invalid")
        self.command("git", "config", "core.autocrlf", "false")
        self.fixture.write(".gitignore", ".ai/\n")
        category = ("schema" if "nonobject" in self.id() else
                    "policy" if "measured_failure" in self.id() else "scope")
        self.tag = category + "-" + uuid.uuid4().hex[:12]
        self.addCleanup(self.save_commands)

    def save_commands(self):
        self.artifact("commands", self.commands)

    def artifact(self, suffix, value):
        (EVIDENCE / f"i1-independent-{self.tag}-{suffix}.json").write_text(
            json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    def command(self, *argv, expected=0, timeout=900, cwd=None):
        argv = [str(arg) for arg in argv]
        expanded = [sys.executable, "-B", str(SCRIPTS / "run.py"),
                    "--idle", "120", "--max", "900", "--", *argv]
        env = dict(os.environ)
        env.pop("NODE_TEST_CONTEXT", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        started = time.time()
        result = run_capture(expanded, cwd=str(cwd or self.root), idle=120,
                             max_total=900, env=env)
        self.commands.append({"argv": expanded, "cwd": str(cwd or self.root),
                              "start_unix": started, "duration": time.time() - started,
                              "bounds": {"idle": 120, "max": 900},
                              "environment_delta": {"NODE_TEST_CONTEXT": None,
                                                    "PYTHONDONTWRITEBYTECODE": "1"},
                              "exit_code": result[0], "stdout": result[1], "stderr": result[2]})
        if expected is not None:
            self.assertEqual(result[0], expected, repr(argv) + "\n" + result[1] + result[2])
        return result

    def probe(self, base, slug, *argv):
        self.command(sys.executable, "-B", SCRIPTS / "probe.py", "--slug", slug,
                     "--base", base, *argv, expected=1)
        report = json.loads((self.root / f".ai/{slug}/metrics.json").read_bytes())
        self.artifact(slug + "-metrics", report)
        return report

    def test_public_probe_measured_failure_is_distinct_from_incomplete_proof(self):
        for extension in ("mjs", "cjs"):
            with self.subTest(extension=extension):
                folder = f"packages/{extension} space"
                filename = folder + "/value." + extension
                test = folder + "/math case.test." + extension
                if extension == "mjs":
                    prefix = "export const "
                    imports = ("import {test} from 'node:test';import assert from 'node:assert/strict';"
                               "import {flag} from './value.mjs';")
                else:
                    prefix = "exports."
                    imports = ("const {test}=require('node:test');const assert=require('node:assert/strict');"
                               "const {flag}=require('./value.cjs');")
                self.fixture.write(filename, prefix + "flag = false;\r\n" + prefix + "unused = false;\r\n")
                self.fixture.write(test, imports + "\ntest('required boundary',()=>assert.equal(flag,true));\n")
                base = self.fixture.commit("fixture: independent pre-change")
                original = (prefix + "flag = true;\r\n" + prefix + "unused = true;\r\n").encode()
                self.fixture.write(filename, original)
                self.fixture.commit("fixture: independent changed source")
                report = self.probe(base, extension, "--test-cwd", str(self.root / folder),
                                    "--", shutil.which("node"), "--test", "math case.test." + extension)
                mutation = report["metrics"]["mutation_score_pct"]
                self.assertEqual((mutation["state"], mutation["head"], mutation["comparison"]),
                                 ("measured", 50.0, "fail"), mutation)
                self.assertEqual((report["measurement_status"], report["completeness"], report["verdict"]),
                                 ("fail", "incomplete", "fail"))
                missing = {item["metric"] for item in report["missing_required"]}
                self.assertTrue({"diff_coverage_pct", "architecture_rules"} <= missing)
                self.assertNotIn("mutation_score_pct", missing)
                child_path = self.root / f".ai/{extension}/evidence/runs/{report['run_id']}/mutation.json"
                child = json.loads(child_path.read_bytes())
                self.artifact(extension + "-mutation", child)
                self.assertEqual((child["complete"], child["killed"], child["survived"]), (True, 1, 1))
                self.assertEqual(child["test_run"]["command"]["cwd"], folder)
                self.assertEqual((self.root / filename).read_bytes(), original)
                fresh = source_snapshot(self.root, child["source"]["scope"])["scope_sha256"]
                self.assertEqual(fresh, child["source"]["scope_sha256"])
                self.assertEqual(fresh, child["restored_sha256"])
                self.assertEqual(source_snapshot(self.root, report["source"]["scope"])["scope_sha256"],
                                 report["source"]["scope_sha256"])
                self.artifact(extension + "-restoration", {"source_sha256": hashlib.sha256(original).hexdigest(),
                                                         "restored_scope_sha256": fresh})

    def test_public_probe_observes_unrelated_evidence_not_just_its_own_reports(self):
        self.fixture.write("value.mjs", "export const value = true;\n")
        base = self.fixture.commit("fixture: independent source")
        note = self.fixture.write(".ai/freshness/evidence/contract-note.json", '{"required":true}\n')
        report = self.probe(base, "freshness", "--skip-mutation")
        original_hash = report["source"]["scope_sha256"]
        scope = report["source"]["scope"]
        self.assertEqual(source_snapshot(self.root, scope)["scope_sha256"], original_hash,
                         "Publishing exact owned reports must preserve freshness")
        note.write_text('{"required":false}\n', encoding="utf-8")
        changed_hash = source_snapshot(self.root, scope)["scope_sha256"]
        self.artifact("freshness-observation", {"before": original_hash, "after": changed_hash,
                                              "changed_path": note.relative_to(self.root).as_posix(),
                                              "excluded_outputs": scope["excluded_outputs"]})
        self.assertNotEqual(changed_hash, original_hash,
                            "Unrelated existing evidence is not this invocation's generated report")

    def test_current_mutation_rejects_nonobject_report_bindings(self):
        self.fixture.write("value.mjs", "export const flag = false;\n")
        self.fixture.write("value.test.mjs",
                           "import {test} from 'node:test';import assert from 'node:assert/strict';"
                           "import {flag} from './value.mjs';"
                           "test('required',()=>assert.equal(flag,true));\n")
        base = self.fixture.commit("fixture: schema boundary baseline")
        original = b"export const flag = true;\n"
        self.fixture.write("value.mjs", original)
        self.fixture.commit("fixture: schema boundary changed source")
        selected = {"cwd": str(self.root),
                    "argv": [shutil.which("node"), "--test", "value.test.mjs"]}
        results = []
        cases = [(None, None)] + [(field, value) for field in ("source", "command", "baseline")
                                 for value in (None, 42, [], "invalid", True)]
        cases += [("results", value) for value in (None, [], [{}])]
        cases += [("outcome", value) for value in ("setup-error", "unclassified", "survived")]
        cases += [(field, None) for field in ("missing-results", "wrong-bytes", "wrong-inventory",
                                            "false-survivor", "missing-execution", "boolean-leaf-count",
                                            "boolean-native-schema", "extra-command-argument",
                                            "wrong-test-files")]
        reasons = {"source": "Mutation source binding must be an object",
                   "command": "Mutation command binding is missing",
                   "baseline": "Mutation baseline must be an object",
                   "boolean-native-schema": "Mutation baseline evidence is inconsistent",
                   "extra-command-argument": "Mutation command does not match canonical test selection",
                   "wrong-test-files": "Mutation command does not match canonical test selection"}
        for index, (field, value) in enumerate(cases):
            with self.subTest(field=field, value=value):
                run_id = "schema-" + uuid.uuid4().hex
                report_path = self.root / f".ai/schema/evidence/runs/{run_id}/mutation.json"

                def execute_then_corrupt(command, cwd=None, timeout=900):
                    # This seam executes every real command, including the genuine
                    # producer and native tests. Only its completed on-disk report
                    # is deliberately corrupted; no exit code/output is fabricated.
                    result = self.command(*command, cwd=cwd, expected=None)
                    if str(SCRIPTS / "mutate.py") in command:
                        self.assertEqual(result[0], 0, result[2])
                        report = json.loads(report_path.read_bytes())
                        self.assertEqual((report["complete"], report["killed"], report["survived"]),
                                         (True, 1, 0))
                        if field == "command":
                            report["test_run"]["command"] = value
                        elif field == "outcome":
                            report["results"][0]["outcome"] = value
                        elif field == "missing-results":
                            del report["results"]
                        elif field == "wrong-bytes":
                            report["results"][0]["after_sha256"] = "0" * 64
                        elif field == "wrong-inventory":
                            report["results"][0]["artifacts"]["native"]["tests"][0]["name"] = "not the baseline test"
                        elif field == "false-survivor":
                            report.update(killed=0, survived=1, score_pct=0)
                            report["results"][0]["outcome"] = "survived"
                        elif field == "missing-execution":
                            del report["results"][0]["artifacts"]["execution"]
                        elif field == "boolean-leaf-count":
                            report["baseline"]["leaf_count"] = True
                        elif field == "boolean-native-schema":
                            report["baseline"]["schema_version"] = True
                        elif field == "extra-command-argument":
                            report["test_run"]["command"]["argv"].append("extra.test.mjs")
                        elif field == "wrong-test-files":
                            report["test_run"]["test_files"] = ["extra.test.mjs"]
                        elif field is not None:
                            report[field] = value
                        if field is not None:
                            report_path.write_text(json.dumps(report), encoding="utf-8")
                        self.artifact(f"case-{index}-report", report)
                    return result

                with patch.object(probe_module, "run", side_effect=execute_then_corrupt):
                    entry = probe_module.mutation_entry(self.root, "schema", base, False,
                                                       run_id=run_id, test_run=selected)
                results.append({"field": field, "value": value, "entry": entry})
                self.artifact("results", results)
                if field is None:
                    self.assertEqual((entry["state"], entry["head"], entry["comparison"]),
                                     ("measured", 100.0, "ok"))
                else:
                    self.assertEqual((entry["state"], entry["head"], entry["comparison"]),
                                     ("unavailable", None, "unavailable"))
                    if field in reasons:
                        self.assertIn(reasons[field], entry["reason"])
                self.assertEqual((self.root / "value.mjs").read_bytes(), original)

    def test_explicit_native_discovery_uses_canonical_files(self):
        self.fixture.write("value.mjs", "export const flag = false;\n")
        self.fixture.write("value.test.mjs",
                           "import {test} from 'node:test';import assert from 'node:assert/strict';"
                           "import {flag} from './value.mjs';test('flag',()=>assert.equal(flag,true));\n")
        base = self.fixture.commit("fixture: native discovery baseline")
        self.fixture.write("value.mjs", "export const flag = true;\n")
        self.fixture.commit("fixture: native discovery change")
        report = self.probe(base, "discovery", "--", shutil.which("node"), "--test")
        mutation = report["metrics"]["mutation_score_pct"]
        self.assertEqual((mutation["state"], mutation["head"]), ("measured", 100.0), mutation)
        self.assertEqual(mutation["command"]["argv"][2:], ["--test", "value.test.mjs"])


if __name__ == "__main__":
    unittest.main()
