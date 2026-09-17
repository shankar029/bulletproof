"""Owner regressions for the independent Q1 review's canonical-source findings."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from helpers import SCRIPTS
from test_measure_inventory import Q1Fixture
import test_measure_q1_verification as capture
import measure
import measure_graph as graph
import probe


class ReviewBoundaryTests(unittest.TestCase):
    def fixture(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        return fixture

    def recollect(self, fixture):
        """Keep committed changed lines; rederive every producer artifact freshly."""
        raw = Path(tempfile.mkdtemp(prefix="review-fresh-", dir=fixture.root))
        fixture.context["run_root"] = str(raw)
        changes = {name: sorted(lines) for name, lines in
                   probe.changed_lines(Path(fixture.context["head_root"]), fixture.base_sha).items()}
        fixture.base = graph.parse_files(
            fixture.context, measure.inventory(fixture.context, "base", {}), fixture.config)
        fixture.head = graph.parse_files(
            fixture.context, measure.inventory(fixture.context, "head", changes), fixture.config)
        pairs = measure.collect_pair(fixture.context, fixture.config, fixture.base, fixture.head)
        fixture.observations = [item for pair in pairs.values() for item in pair]
        fixture.manifest = measure.make_manifest(fixture.context, fixture.base, fixture.head)
        fixture.context["output_manifest"] = graph.persist(fixture.context, "manifest.json", fixture.manifest)
        return probe._configured_report(fixture.context, fixture.base, fixture.head, fixture.config,
                                        fixture.manifest, fixture.observations, "review", fixture.base_sha, [])

    def validate(self, fixture, report):
        probe.validate_measurement_report(report, fixture.context, fixture.base, fixture.head,
                                          fixture.config, fixture.policy, fixture.manifest)

    def test_public_source_root_aliases_rejected(self):
        fixture = self.fixture()
        fixture.git.write("scripts/a.py", "import b\nVALUE = 1\n")
        fixture.git.write("scripts/b.py", "import a\nVALUE = 2\n")
        fixture.git.commit("fixture: canonical directory cycle")
        observations = []
        for root, label in (("scripts", "canonical"), ("scripts.", "dot-alias"), ("scripts ", "space-alias")):
            # The reviewer demonstrated native resolution for the dot alias.
            # A final-component Win32 directory alias need not behave identically
            # when importlib appends child paths (notably the trailing-space form).
            if os.name == "nt" and root != "scripts ":
                native = ("import sys,json; sys.path.insert(0,%r); import a,b; "
                          "print(json.dumps({'a':a.__file__,'b':b.__file__,'cross':a.b is b and b.a is a}))") % root
                code, output, error = capture.raw_command(
                    "review-native-" + label, [sys.executable, "-B", "-S", "-c", native], fixture.git.root)
                self.assertEqual(code, 0, error)
                self.assertTrue(json.loads(output)["cross"])
            fixture.config["python_source_roots"] = [root]
            fixture.save_config()
            argv = [sys.executable, "-B", str(SCRIPTS / "probe.py"), "--repo", str(fixture.git.root),
                    "--slug", label, "--base", fixture.base_sha, "--skip-mutation",
                    "--measurement-config", str(fixture.git.root / "measurement.json")]
            code, output, error = capture.raw_command("review-cli-" + label, argv, fixture.git.root)
            report = json.loads(output) if code == 1 else None
            observations.append({"root": root, "exit": code, "report": report,
                                 "stderr": error.decode(errors="replace")})
        capture.save("review-path-alias-observations", observations)
        capture.preserve_fixture("review-path-alias", fixture)
        canonical = observations[0]["report"]
        self.assertEqual((canonical["metrics"]["cycles"]["head"],
                          canonical["metrics"]["cycles"]["comparison"]), (1, "fail"))
        self.assertEqual(len(canonical["missing_required"]), 7)
        for observed in observations[1:]:
            with self.subTest(root=observed["root"]):
                self.assertEqual(observed["exit"], 2, "An aliased root must not yield measured external edges")

    def test_fresh_assume_unchanged_baseline_is_rejected(self):
        fixture = self.fixture()
        fixture.git.write("a.py", "import b\n")
        fixture.git.write("b.py", "import a\n")
        fixture.build()
        genuine = fixture.summary()["metrics"]["cycles"]
        self.assertEqual((genuine["base"], genuine["head"], genuine["comparison"]), (0, 1, "fail"))
        base, head = (Path(fixture.context[key]) for key in ("base_root", "head_root"))
        fixture.git.run("git", "update-index", "--assume-unchanged", "a.py", "b.py", cwd=base)
        for name in ("a.py", "b.py"):
            (base / name).write_bytes((head / name).read_bytes())
        status = fixture.git.run("git", "status", "--porcelain", "--untracked-files=all",
                                 "--ignored=matching", cwd=base)[1]
        self.assertEqual(status, "")
        committed = fixture.git.run("git", "show", fixture.base_sha + ":a.py", cwd=base)[1]
        self.assertNotEqual(committed.encode(), (base / "a.py").read_bytes())
        report = self.recollect(fixture)
        capture.save("review-hidden-baseline", {"genuine": genuine, "fresh": report,
                                                "committed": committed, "status": status,
                                                "actual": (base / "a.py").read_text()})
        capture.preserve_fixture("review-hidden-baseline", fixture, report)
        self.assertEqual((report["metrics"]["cycles"]["base"], report["metrics"]["cycles"]["head"]), (1, 1))
        with self.assertRaisesRegex(ValueError, "Baseline"):
            self.validate(fixture, report)


if __name__ == "__main__":
    unittest.main()
