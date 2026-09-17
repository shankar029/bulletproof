"""Fresh-context Q1 regression probes; production is never changed."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest

from helpers import SCRIPTS
from test_measure_inventory import Q1Fixture
import measure
import probe


EVIDENCE = SCRIPTS.parent / ".ai/workflow-reliability/evidence"


def save(label, value):
    path = EVIDENCE / ("q1-independent-" + label + ".json")
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def raw_command(label, argv, cwd):
    """Child belongs to the outer run.py process tree; preserve original bytes."""
    proc = subprocess.Popen(argv, cwd=cwd, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    chunks = {"stdout": [], "stderr": []}

    def pump(key):
        stream = getattr(proc, key)
        while data := stream.read1(65536):
            chunks[key].append(data)
        stream.close()

    threads = [threading.Thread(target=pump, args=(key,)) for key in chunks]
    for thread in threads:
        thread.start()
    code = proc.wait(timeout=180)
    for thread in threads:
        thread.join()
    result = {}
    for key, pieces in chunks.items():
        data = b"".join(pieces)
        (EVIDENCE / ("q1-independent-" + label + "." + key + ".bin")).write_bytes(data)
        result[key] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    save(label + "-command", {"argv": argv, "cwd": str(cwd), "exit_code": code,
                             "environment_delta": {"PYTHONDONTWRITEBYTECODE": "1"}, "raw": result,
                             "outer_run_bounds": {"idle": 120, "max": 1200}})
    return code, b"".join(chunks["stdout"]), b"".join(chunks["stderr"])


def preserve_fixture(label, fixture, report=None):
    """Exact non-Git bytes, with deterministic content hashes; no shared-tree walk."""
    destination = EVIDENCE / ("q1-independent-" + label + "-files")
    destination.mkdir(exist_ok=False)
    records = {}
    for base, dirs, files in os.walk(fixture.git.root):
        dirs[:] = [name for name in dirs if name != ".git"]
        for name in files:
            source = Path(base) / name
            relative = source.relative_to(fixture.git.root)
            data = source.read_bytes()
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            records[relative.as_posix()] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    save(label + "-fixture", {"root": str(fixture.git.root), "base": fixture.base_sha,
                              "files": records, "report": report})


class IndependentQ1VerificationTests(unittest.TestCase):
    def fixture(self):
        fixture = Q1Fixture()
        self.addCleanup(fixture.close)
        return fixture

    def cli(self, fixture, label):
        argv = [sys.executable, "-B", str(SCRIPTS / "probe.py"), "--repo", str(fixture.git.root),
                "--slug", label, "--base", fixture.base_sha, "--skip-mutation",
                "--measurement-config", str(fixture.git.root / "measurement.json")]
        code, output, error = raw_command(label, argv, fixture.git.root)
        self.assertEqual(code, 1, error.decode(errors="replace"))
        report = json.loads(output)
        preserve_fixture(label, fixture)
        self.assertEqual(set(report["metrics"]), {
            "duplication_pct", "complexity_max", "complexity_avg", "cycles", "dead_exports",
            "static_findings", "mutation_score_pct", "diff_coverage_pct", "architecture_rules"})
        self.assertEqual((report["completeness"], report["verdict"]), ("incomplete", "fail"))
        return report

    def test_actual_greenfield_requires_complete_two_file_baseline(self):
        fixture = self.fixture()
        (fixture.git.root / "b.py").unlink()
        (fixture.git.root / "c.py").unlink()
        fixture.base_sha = fixture.git.commit("fixture: actual two-code-file baseline")
        fixture.git.write("a.py", "value = 2\n")
        fixture.git.commit("fixture: changed source")
        report = self.cli(fixture, "greenfield")
        base = report["inventories"]["base"]
        self.assertEqual(base["enumeration_state"], "complete")
        self.assertEqual({entry["path"] for entry in base["entries"]}, {"a.py", "test_example.py"})
        self.assertEqual(report["baseline"], "greenfield")
        self.assertEqual(report["metrics"]["cycles"]["state"], "measured")
        self.assertEqual(report["metrics"]["cycles"]["head"], 0)
        self.assertEqual(len(report["missing_required"]), 7)

    def test_public_census_keeps_ignored_untracked_tests_examples_benchmarks(self):
        fixture = self.fixture()
        fixture.git.write(".gitignore", ".ai/\nignored_input.py\n")
        fixture.git.commit("fixture: source ignore rule")
        fixture.git.write("ignored_input.py", "import a\n")
        fixture.git.write("tests/untracked_test.py", "import b\n")
        fixture.git.write("examples/untracked.py", "import c\n")
        fixture.git.write("benchmark/untracked.py", "import a\n")
        report = self.cli(fixture, "untracked-census")
        names = {"ignored_input.py", "tests/untracked_test.py", "examples/untracked.py", "benchmark/untracked.py"}
        entries = {entry["path"] for entry in report["inventories"]["head"]["entries"]}
        receipts = {receipt["path"]: receipt for receipt in report["parsed"]["head"]["receipts"]}
        self.assertTrue(names <= entries)
        for name in names:
            self.assertEqual(receipts[name]["state"], "processed")
            self.assertEqual(report["source"]["files"][name]["sha256"], receipts[name]["source_sha256"])
        self.assertEqual(len(entries), len(receipts))

    def test_builtin_import_uses_actual_python_resolution_not_local_sys_file(self):
        fixture = self.fixture()
        fixture.git.write("sys.py", "import scripts.evidence\n")
        fixture.git.write("scripts/evidence.py", "import sys\n")
        fixture.git.commit("fixture: builtin name and local namesake")
        code, output, error = raw_command(
            "builtin-native",
            [sys.executable, "-B", "-c",
             "import sys, scripts.evidence; print(sys.__spec__.origin); "
             "assert sys.__spec__.origin == 'built-in'; "
             "assert scripts.evidence.sys is sys"],
            fixture.git.root)
        self.assertEqual(code, 0, error.decode(errors="replace"))
        self.assertEqual(output.strip(), b"built-in")
        report = self.cli(fixture, "builtin-resolution")
        local = [(edge["from"], edge["to"]) for edge in report["parsed"]["head"]["graph"]["edges"]
                 if edge["resolution"] == "local"]
        self.assertNotIn(("scripts/evidence.py", "sys.py"), local,
                         "CPython's builtin sys takes precedence over a repository sys.py")
        self.assertEqual(report["metrics"]["cycles"]["head"], 0)
        self.assertEqual(report["metrics"]["architecture_rules"]["head"], 0)

    def test_module_cannot_be_used_as_a_package_but_graph_must_fail_closed(self):
        fixture = self.fixture()
        fixture.git.write("pkg.py", "value = 1\n")
        fixture.git.write("pkg/child.py", "value = 2\n")
        fixture.git.write("a.py", "import pkg.child\n")
        fixture.git.commit("fixture: non-package shadows namespace directory")
        code, output, error = raw_command(
            "nonpackage-native", [sys.executable, "-B", "-c", "import pkg.child"], fixture.git.root)
        self.assertEqual(code, 1)
        self.assertIn(b"'pkg' is not a package", error)
        report = self.cli(fixture, "nonpackage-resolution")
        self.assertTrue(report["parsed"]["head"]["graph"]["unresolved"],
                        "A local module cannot satisfy an import of its nonexistent package child")
        self.assertEqual(report["metrics"]["cycles"]["state"], "unavailable")
        self.assertEqual(report["metrics"]["architecture_rules"]["state"], "unavailable")

    def test_disjoint_roots_must_not_share_mutable_base_head_files(self):
        fixture = self.fixture().materialize()
        fixture.validate()
        base = Path(fixture.context["base_root"]) / "a.py"
        head = Path(fixture.context["head_root"]) / "a.py"
        original = base.read_bytes()
        head.unlink()
        os.link(base, head)
        self.assertTrue(os.path.samefile(base, head))
        rejected = False
        try:
            fixture.validate()
        except ValueError:
            rejected = True
        # Prove mutability aliasing rather than relying only on inode metadata.
        head.write_bytes(original + b"# owned target edit\n")
        shared_write = base.read_bytes() == head.read_bytes() != original
        save("hardlink-counterexample", {
            "base": str(base), "head": str(head), "samefile": os.path.samefile(base, head),
            "shared_write_observed": shared_write, "validator_rejected": rejected,
            "base_before_sha256": hashlib.sha256(original).hexdigest(),
            "base_after_sha256": hashlib.sha256(base.read_bytes()).hexdigest(),
            "head_after_sha256": hashlib.sha256(head.read_bytes()).hexdigest()})
        preserve_fixture("hardlink", fixture)
        self.assertTrue(shared_write)
        self.assertTrue(rejected, "Distinct paths are not distinct mutable source copies")


if __name__ == "__main__":
    unittest.main()
