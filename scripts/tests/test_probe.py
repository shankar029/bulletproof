import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe
from helpers import GitFixture, SCRIPTS


class ExistingProbeBehaviorTests(unittest.TestCase):
    def test_esm_and_cjs_are_counted_as_code(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("a.mjs", "b.cjs", "c.py"):
                (Path(directory) / name).write_text("value = 1", encoding="utf-8")
            self.assertEqual({Path(path).suffix for path in probe.code_files(directory)}, {".mjs", ".cjs", ".py"})

    def test_missing_baseline_is_not_a_passing_comparison(self):
        entry, status = probe.judge("complexity_max", None, 3)
        self.assertEqual(status, "unavailable")
        self.assertEqual(entry["head"], 3)

    def test_one_greenfield_cycle_fails(self):
        self.assertEqual(probe.judge("cycles", 0, 1, greenfield=True)[1], "fail")

    def test_failed_or_empty_cycle_command_is_not_zero(self):
        for outcome in ((7, "", "failed"), (0, "", ""), (0, "{}", "")):
            with self.subTest(outcome=outcome), patch.object(probe, "argv", return_value=["madge"]), \
                    patch.object(probe, "run", return_value=outcome):
                self.assertIsNone(probe.m_cycles("."))

    def test_missing_static_results_are_not_zero(self):
        with patch.object(probe, "argv", return_value=["semgrep"]), \
                patch.object(probe, "run", return_value=(0, "{}", "")):
            self.assertIsNone(probe.m_static("."))


class ProbePolicyTests(unittest.TestCase):
    def measured(self, comparison="ok"):
        return {"state": "measured", "head": 0, "comparison": comparison, "reason": ""}

    def test_policy_distinguishes_missing_proof_from_measured_failure(self):
        policy = {"required": ["cycles", "static_findings"], "rules": {}}
        cases = [
            ({}, "unavailable", "incomplete", "fail"),
            ({"cycles": self.measured()}, "ok", "incomplete", "fail"),
            ({"cycles": self.measured("fail")}, "fail", "incomplete", "fail"),
            ({"cycles": self.measured(), "static_findings": self.measured()}, "ok", "complete", "pass"),
            ({"cycles": self.measured("warn"), "static_findings": self.measured()}, "warn", "complete", "pass"),
        ]
        for values, measured, completeness, verdict in cases:
            with self.subTest(values=values):
                result = probe.assess_report(values, policy)
                self.assertEqual((result["measurement_status"], result["completeness"], result["verdict"]),
                                 (measured, completeness, verdict))
                self.assertEqual(bool(result["missing_required"]), completeness == "incomplete")

    def test_partial_scope_and_missing_comparison_cannot_complete(self):
        for entry in (
                {"state": "unavailable", "head": 0, "comparison": "ok", "reason": "Unsupported Python scope"},
                {"state": "measured", "head": 0, "comparison": "unavailable", "reason": "Missing baseline"}):
            result = probe.assess_report({"cycles": entry}, {"required": ["cycles"], "rules": {}})
            self.assertEqual(result["verdict"], "fail")
            self.assertEqual(result["missing_required"][0]["reason"], entry["reason"])

    def test_nonfinite_and_boolean_measurements_are_rejected(self):
        for value in (float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                probe.assess_report({"cycles": {**self.measured(), "head": value}},
                                    {"required": ["cycles"], "rules": {}})

    def test_measured_without_value_and_empty_policy_are_invalid(self):
        with self.assertRaises(ValueError):
            probe.assess_report({"cycles": {**self.measured(), "head": None}}, {"required": ["cycles"]})
        with self.assertRaises(ValueError):
            probe.assess_report({}, {"required": []})

    def test_language_support_does_not_claim_python_cycles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.py").write_text("pass\n")
            (root / "b.mjs").write_text("export const b = 1;\n")
            scope = probe._scope_support("cycles", root, [])
            self.assertEqual(scope["measured_paths"], ["b.mjs"])
            self.assertEqual(scope["unsupported_paths"], ["a.py"])

    def test_complexity_inventory_preserves_quoted_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "code, space.py"
            path.write_text("def f(): return 1\n")
            rows = '1,1,5,0,1,"f@1-1@code, space.py","code, space.py","f","f()",1,1\n'
            command = {"argv": ["lizard", "--csv"], "code": 0, "stdout": rows}
            support = probe._scope_support("complexity_max", root, [command])
            self.assertEqual(support, {"measured_paths": ["code, space.py"], "unsupported_paths": []})

    def test_malformed_static_inventory_is_unsupported_not_a_crash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.py").write_text("value = 1\n")
            for inventory in (None, 42, [], {"scanned": None}):
                with self.subTest(inventory=inventory):
                    support = probe._scope_support("static_findings", root, [{"result_report": {"paths": inventory}}])
                    self.assertEqual(support["unsupported_paths"], ["source.py"])

    def test_snapshot_ignores_own_output_but_not_other_contracts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / ".ai/observed/evidence"
            output.mkdir(parents=True)
            contract = root / ".ai/other/workflow.json"
            contract.parent.mkdir()
            contract.write_text("{}")
            original = probe._snapshot(root, "observed", "current")
            current = output / "runs/current"
            current.mkdir(parents=True)
            (current / "metrics.json").write_text("{}")
            (current / "mutation.json").write_text("{}")
            self.assertEqual(probe._snapshot(root, "observed", "current")["scope_sha256"], original["scope_sha256"])
            (output / "log.txt").write_text("new output")
            self.assertNotEqual(probe._snapshot(root, "observed", "current")["scope_sha256"], original["scope_sha256"])
            before_contract = probe._snapshot(root, "observed", "current")
            contract.write_text('{"changed":true}')
            self.assertNotEqual(probe._snapshot(root, "observed", "current")["scope_sha256"],
                                before_contract["scope_sha256"])
            baseline = probe._snapshot(root, "observed", "current")
            (root / "build").mkdir()
            (root / "build/input.py").write_text("value = 1")
            self.assertNotEqual(probe._snapshot(root, "observed", "current")["scope_sha256"], baseline["scope_sha256"],
                                "An analyzer may consume build files; directory names are not proof of exclusion")

    def test_default_policy_cannot_omit_unimplemented_required_collectors(self):
        policy = probe.default_policy()
        self.assertIn("diff_coverage_pct", policy["required"])
        self.assertIn("architecture_rules", policy["required"])
        self.assertIn("mutation_score_pct", policy["required"])
        self.assertEqual(policy["rules"]["mutation_score_pct"]["threshold"], 60)
        self.assertEqual(policy, probe.default_policy())

    def test_partial_complexity_csv_is_not_a_complete_measurement(self):
        with patch.object(probe, "argv", return_value=["lizard"]), \
                patch.object(probe, "run", return_value=(0, "NLOC,CCN\n1,2\nbroken\n", "")):
            self.assertEqual(probe.m_complexity("."), (None, None))


class ProbeCliTests(unittest.TestCase):
    def setUp(self):
        self.fixture = GitFixture()
        self.addCleanup(self.fixture.close)
        self.fixture.write("source.mjs", "export const value = 1;\n")
        self.fixture.write(".gitignore", ".ai/\n")
        self.base = self.fixture.commit()

    def test_unavailable_default_cli_fails_without_workflow_artifacts(self):
        result = self.fixture.run(sys.executable, "-B", str(SCRIPTS / "probe.py"),
                                  "--slug", "observed", "--base", self.base, "--skip-mutation",
                                  expected=1, timeout=180)
        report = json.loads((self.fixture.root / ".ai/observed/metrics.json").read_bytes())
        self.assertEqual(report["schema_version"], 2)
        self.assertEqual(report["verdict"], "fail")
        self.assertEqual(report["completeness"], "incomplete")
        self.assertIn("mutation_score_pct", report["unavailable"])
        self.assertFalse((self.fixture.root / ".ai/observed/workflow.json").exists())
        self.assertEqual(report["source"]["binding_mode"], "standalone-source")
        self.assertTrue(report["run_id"])
        self.assertIn(report["run_id"], result[1])
        immutable = self.fixture.root / ".ai/observed/evidence/runs" / report["run_id"] / "metrics.json"
        self.assertEqual(json.loads(immutable.read_bytes()), report)

    def test_invalid_baseline_never_becomes_greenfield(self):
        self.fixture.run(sys.executable, "-B", str(SCRIPTS / "probe.py"), "--slug", "unknown-base",
                         "--base", "missing-reference", "--skip-mutation", expected=1, timeout=180)
        report = json.loads((self.fixture.root / ".ai/unknown-base/metrics.json").read_bytes())
        self.assertEqual(report["baseline"], "unknown")
        self.assertEqual(report["verdict"], "fail")

    def test_stale_score_is_not_used_after_current_mutation_failure(self):
        self.fixture.write("uncommitted.mjs", "export const changed = true;\n")
        self.fixture.write(".ai/stale/mutation.json", json.dumps({
            "score_pct": 100, "head": "obsolete", "survivors": []}))
        self.fixture.run(sys.executable, "-B", str(SCRIPTS / "probe.py"), "--slug", "stale",
                         "--base", self.base, "--", "node", "--test", "missing.test.mjs",
                         expected=1, timeout=180)
        report = json.loads((self.fixture.root / ".ai/stale/metrics.json").read_bytes())
        self.assertEqual(report["verdict"], "fail")
        self.assertEqual(report["metrics"]["mutation_score_pct"]["state"], "unavailable")
        self.assertNotEqual(report["metrics"]["mutation_score_pct"].get("head"), 100)

    def test_current_native_mutation_is_measured_even_when_other_proof_is_missing(self):
        self.fixture.write("source.mjs", "export function eligible(n) { return n >= 2; }\n")
        self.fixture.write("source.test.mjs", """
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { eligible } from './source.mjs';
test('boundary', () => { assert.equal(eligible(1), false); assert.equal(eligible(2), true); });
""")
        self.fixture.commit()
        self.fixture.run(sys.executable, "-B", str(SCRIPTS / "probe.py"), "--slug", "fresh",
                         "--base", self.base, "--", "node", "--test", "source.test.mjs",
                         expected=1, timeout=180)
        report = json.loads((self.fixture.root / ".ai/fresh/metrics.json").read_bytes())
        mutation = report["metrics"]["mutation_score_pct"]
        self.assertEqual(mutation["state"], "measured", mutation.get("reason"))
        self.assertEqual(mutation["head"], 100)
        self.assertEqual(mutation["run_id"], report["run_id"])
        self.assertEqual(report["completeness"], "incomplete")
        observed = probe.source_snapshot(self.fixture.root, mutation["source"]["scope"])
        self.assertEqual(observed["scope_sha256"], mutation["source"]["scope_sha256"],
                         "Writing parent reports must not immediately stale child proof")


if __name__ == "__main__":
    unittest.main()
