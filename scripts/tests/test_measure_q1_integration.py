import copy
import json
from pathlib import Path
import sys
import unittest

from helpers import SCRIPTS
from test_measure_inventory import Q1Fixture
from evidence import source_snapshot
import measure
import measure_graph as graph
import probe


class Q1IntegrationTests(unittest.TestCase):
    def fixture(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        return fixture

    def invoke(self, fixture, slug="q1", cwd=None):
        result = fixture.git.run(
            sys.executable, "-B", str(SCRIPTS / "probe.py"), "--repo", str(fixture.git.root),
            "--slug", slug, "--base", fixture.base_sha, "--skip-mutation",
            "--measurement-config", str(fixture.git.root / "measurement.json"),
            expected=1, timeout=180, cwd=cwd)
        report = json.loads((fixture.git.root / ".ai" / slug / "metrics.json").read_bytes())
        self.assertIn(report["run_id"], result[1])
        self.assertEqual(report["verdict"], "fail")
        self.assertEqual(report["completeness"], "incomplete")
        self.assertEqual(set(report["metrics"]), set(measure.REQUIRED))
        return report

    def test_public_python_cli_from_nested_cwd_keeps_all_nine_and_archives_raw(self):
        fixture = self.fixture()
        nested = fixture.git.root / "nested"
        nested.mkdir()
        fixture.git.write("a.py", "import b\n")
        fixture.git.write("b.py", "import a\n")
        fixture.git.commit("fixture: actual cycle")
        report = self.invoke(fixture, cwd=nested)
        self.assertEqual(report["metrics"]["cycles"]["head"], 1)
        self.assertEqual(report["metrics"]["cycles"]["comparison"], "fail")
        self.assertEqual(report["metrics"]["architecture_rules"]["head"], 0)
        self.assertEqual(report["metrics"]["architecture_rules"]["state"], "measured")
        self.assertEqual(len(report["missing_required"]), 7)
        self.assertEqual(report["baseline"], "compared")
        self.assertTrue(all(item["state"] == "processed" for item in report["parsed"]["head"]["receipts"]))
        archive = fixture.git.root / ".ai/q1/evidence/runs" / report["run_id"] / "measurement"
        for owned in report["artifact_manifest"]["inputs"]:
            self.assertEqual(graph.artifact(archive, owned["artifact"]["path"]), owned["artifact"])
        observed = source_snapshot(fixture.git.root, report["source"]["scope"])
        self.assertEqual(observed["scope_sha256"], report["source"]["scope_sha256"],
                         "Publishing exact raw artifacts must not immediately stale the report")
        fixture.git.write(".ai/q1/evidence/unrelated.txt", "not a reserved output")
        self.assertNotEqual(source_snapshot(fixture.git.root, report["source"]["scope"])["scope_sha256"],
                            report["source"]["scope_sha256"])
        self.assertFalse((fixture.git.root / ".ai/q1/workflow.json").exists())

    def test_public_mixed_root_marks_every_unsupported_input(self):
        fixture = self.fixture()
        fixture.git.write("module.mjs", "export const value = 1;\n")
        fixture.git.write("module.cjs", "module.exports = 1;\n")
        fixture.git.commit("fixture: mixed inputs")
        report = self.invoke(fixture, "mixed")
        self.assertEqual(report["metrics"]["cycles"]["state"], "unavailable")
        self.assertEqual(report["metrics"]["architecture_rules"]["comparison"], "unavailable")
        receipts = {item["path"]: item["state"] for item in report["parsed"]["head"]["receipts"]}
        self.assertEqual(receipts["module.mjs"], "unsupported")
        self.assertEqual(receipts["module.cjs"], "unsupported")
        self.assertEqual(len(report["missing_required"]), 9)

    def test_public_cycle_replacement_compares_identity_not_count(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "import b\n")
        fixture.git.write("b.py", "import a\n")
        fixture.base_sha = fixture.git.commit("fixture: original cycle")
        fixture.git.write("a.py", "import c\n")
        fixture.git.write("b.py", "")
        fixture.git.write("c.py", "import a\n")
        fixture.git.commit("fixture: different cycle")
        report = self.invoke(fixture, "replaced")
        self.assertEqual(report["metrics"]["cycles"]["base"], 1)
        self.assertEqual(report["metrics"]["cycles"]["head"], 1)
        self.assertEqual(report["metrics"]["cycles"]["comparison"], "fail")
        self.assertEqual(len(report["metrics"]["cycles"]["new_ids"]), 1)

    def test_public_malformed_config_and_invalid_policy_are_exit_two(self):
        fixture = self.fixture()
        for content in ('{"schema_version":1,"schema_version":1}', '{"schema_version":true}',
                        json.dumps({**fixture.config, "python_source_roots": ["../"]}),
                        json.dumps({**fixture.config, "mutation_cap": 0})):
            fixture.git.write("measurement.json", content)
            _, _, error = fixture.git.run(
                sys.executable, "-B", str(SCRIPTS / "probe.py"), "--repo", str(fixture.git.root),
                "--slug", "invalid", "--base", fixture.base_sha, "--measurement-config",
                str(fixture.git.root / "measurement.json"), expected=2, timeout=90)
            self.assertIn("unable to run", error)
            self.assertFalse((fixture.git.root / ".ai/invalid/metrics.json").exists())

    def test_public_validator_rejects_metric_comparison_revision_and_verdict_forgery(self):
        fixture = self.fixture().materialize()
        report = probe._configured_report(fixture.context, fixture.base, fixture.head, fixture.config,
                                          fixture.manifest, fixture.observations, "q1", fixture.base_sha, [])

        def validate(candidate):
            probe.validate_measurement_report(candidate, fixture.context, fixture.base, fixture.head,
                                              fixture.config, fixture.policy, fixture.manifest)
        validate(report)
        cases = [
            lambda r: r.update(verdict="pass"),
            lambda r: r.update(completeness="complete"),
            lambda r: r.update(measurement_status="fail"),
            lambda r: r.update(missing_required=[]),
            lambda r: r["metrics"]["cycles"].update(head=100),
            lambda r: r["metrics"]["cycles"].update(comparison="fail"),
            lambda r: r["metrics"]["cycles"].update(new_ids=["0" * 64]),
            lambda r: r["metrics"]["architecture_rules"].update(head=100),
            lambda r: r["metrics"]["mutation_score_pct"].update(state="measured", head=100, comparison="ok"),
            lambda r: r["metrics"].pop("diff_coverage_pct"),
            lambda r: r["policy"]["required"].remove("diff_coverage_pct"),
            lambda r: r["parsed"]["head"]["receipts"][0].update(revision="base"),
            lambda r: r["parsed"]["head"]["inventory"]["entries"].pop(),
            lambda r: r.update(head="0" * 40),
            lambda r: r["source"].update(scope_sha256="0" * 64),
            lambda r: r.update(extra="unrecognized"),
        ]
        for index, modify in enumerate(cases):
            candidate = copy.deepcopy(report)
            modify(candidate)
            with self.subTest(corruption=index), self.assertRaises(ValueError):
                validate(candidate)
        validate(report)

    def test_policy_root_and_stale_controller_inputs_are_rejected(self):
        fixture = self.fixture().materialize()
        report = probe._configured_report(fixture.context, fixture.base, fixture.head, fixture.config,
                                          fixture.manifest, fixture.observations, "q1", fixture.base_sha, [])
        for key, value in (("run_root", fixture.context["head_root"]),
                           ("toolset_sha256", "f" * 64), ("policy_sha256", "0" * 64),
                           ("base_root", fixture.context["head_root"])):
            context = {**fixture.context, key: value}
            with self.subTest(field=key), self.assertRaises(ValueError):
                probe.validate_measurement_report(report, context, fixture.base, fixture.head, fixture.config,
                                                  fixture.policy, fixture.manifest)
        controller = Path(fixture.context["controller_root"]) / "measure.py"
        controller.write_bytes(controller.read_bytes() + b"\n# edited controller\n")
        fixture.context["controller_sha256"] = measure.controller_digest(fixture.context["controller_root"])
        with self.assertRaisesRegex(ValueError, "controller"):
            fixture.validate()

    def test_config_bytes_and_source_binding_mode_cannot_be_substituted(self):
        fixture = self.fixture().materialize()
        fixture.validate()
        config = copy.deepcopy(fixture.config)
        # Both orders are valid resolutions, but this is not the source config.
        fixture.config["architecture_rules"].reverse()
        with self.subTest(binding="config bytes"), self.assertRaises(ValueError):
            fixture.validate()
        fixture.config = config
        fixture.context["source"]["binding_mode"] = "fabricated"
        with self.subTest(binding="source mode"), self.assertRaises(ValueError):
            fixture.validate()

    def test_config_cannot_be_hidden_in_the_report_output_slot(self):
        fixture = self.fixture()
        path = fixture.git.write(".ai/overlap/metrics.json", json.dumps(fixture.config))
        before = path.read_bytes()
        _, _, error = fixture.git.run(
            sys.executable, "-B", str(SCRIPTS / "probe.py"), "--repo", str(fixture.git.root),
            "--slug", "overlap", "--base", fixture.base_sha, "--measurement-config", str(path),
            "--skip-mutation", expected=2, timeout=90)
        self.assertIn("overlaps", error)
        self.assertEqual(path.read_bytes(), before)

    def test_changed_map_and_manifest_ownership_corruption_are_rejected(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "value = 2\n")
        fixture.build()
        report = probe._configured_report(fixture.context, fixture.base, fixture.head, fixture.config,
                                          fixture.manifest, fixture.observations, "q1", fixture.base_sha, [])
        fixture.head["inventory"]["changed_production"] = {}
        with self.assertRaisesRegex(ValueError, "committed diff"):
            probe.validate_measurement_report(report, fixture.context, fixture.base, fixture.head, fixture.config,
                                              fixture.policy, fixture.manifest)
        fixture.head["inventory"]["changed_production"] = {"a.py": [1]}
        for modify in (lambda m: m["inputs"].pop(),
                       lambda m: m["inputs"].append(copy.deepcopy(m["inputs"][0])),
                       lambda m: m.update(root=fixture.context["head_root"]),
                       lambda m: m["reserved_outputs"].append("../outside.json")):
            manifest = copy.deepcopy(fixture.manifest)
            modify(manifest)
            with self.assertRaises(ValueError):
                probe.validate_measurement_report(report, fixture.context, fixture.base, fixture.head, fixture.config,
                                                  fixture.policy, manifest)


if __name__ == "__main__":
    unittest.main()
