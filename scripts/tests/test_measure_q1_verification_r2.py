"""Correction-only independent boundaries; no production or original-test edits."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import unittest

import test_measure_inventory as inventory_tests
from test_measure_q1_verification import raw_command, preserve_fixture, save
from helpers import SCRIPTS


@contextmanager
def frozen_environment(value):
    previous = os.environ.get("PYTHON_FROZEN_MODULES")
    os.environ["PYTHON_FROZEN_MODULES"] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("PYTHON_FROZEN_MODULES", None)
        else:
            os.environ["PYTHON_FROZEN_MODULES"] = previous


class CorrectionBoundaryTests(unittest.TestCase):
    def fixture(self):
        fixture = inventory_tests.Q1Fixture()
        self.addCleanup(fixture.close)
        return fixture

    def test_effective_frozen_mode_from_environment_has_distinct_tool_binding(self):
        fixture = self.fixture()
        fixture.git.write("__hello__.py", "LOCAL = True\n")
        fixture.git.write("a.py", "import __hello__\n")
        fixture.git.commit("fixture: runtime-frozen name and local source namesake")
        reports = {}
        observations = {}
        for mode in ("on", "off"):
            with frozen_environment(mode):
                prefix = [sys.executable, "-B", "-S"]
                native = prefix + ["-c", "import __hello__; print(__hello__.__spec__.origin)"]
                rc, output, error = raw_command("frozen-env-" + mode + "-native", native, fixture.git.root)
                self.assertEqual(rc, 0, error.decode(errors="replace"))
                origin = output.decode().strip()
                if mode == "on":
                    self.assertEqual(origin, "frozen")
                else:
                    self.assertEqual(Path(origin).resolve(), fixture.git.root / "__hello__.py")
                command = prefix + [str(SCRIPTS / "probe.py"), "--repo", str(fixture.git.root),
                                    "--slug", "frozen-env-" + mode, "--base", fixture.base_sha,
                                    "--skip-mutation", "--measurement-config",
                                    str(fixture.git.root / "measurement.json")]
                rc, output, error = raw_command("frozen-env-" + mode + "-probe", command, fixture.git.root)
                self.assertEqual(rc, 1, error.decode(errors="replace"))
                report = json.loads(output)
                reports[mode] = report
                edges = [edge for edge in report["parsed"]["head"]["graph"]["edges"] if edge["from"] == "a.py"]
                self.assertEqual(len(edges), 1)
                self.assertEqual(edges[0]["resolution"], "external" if mode == "on" else "local")
                self.assertEqual((report["completeness"], report["verdict"]), ("incomplete", "fail"))
                observations[mode] = {
                    "environment_delta": {"PYTHONDONTWRITEBYTECODE": "1", "PYTHON_FROZEN_MODULES": mode},
                    "native_argv": native, "probe_argv": command, "native_origin": origin,
                    "edges": edges, "tools": report["tools"],
                    "receipt_toolsets": sorted({item["toolset_sha256"] for item in report["parsed"]["head"]["receipts"]}),
                }
                preserve_fixture("frozen-env-" + mode, fixture)
        save("effective-frozen-mode-observations", observations)
        self.assertNotEqual(reports["on"]["tools"]["python_parser"],
                            reports["off"]["tools"]["python_parser"],
                            "Different effective frozen-import semantics must not share a parser/tool fingerprint")

    def test_fresh_hidden_noncode_contract_alias_is_rejected(self):
        fixture = self.fixture()
        fixture.git.write(".hidden/normative.txt", "Normative source contract\n")
        fixture.base_sha = fixture.git.commit("fixture: non-code input under excluded analyzer directory")
        fixture.materialize()
        fixture.validate()
        self.assertNotIn(".hidden/normative.txt",
                         {entry["path"] for entry in fixture.head["inventory"]["entries"]})
        left = Path(fixture.context["base_root"]) / ".hidden/normative.txt"
        right = Path(fixture.context["head_root"]) / ".hidden/normative.txt"
        right.unlink()
        os.link(left, right)
        self.assertTrue(os.path.samefile(left, right))
        inventory_tests.InventoryTests().recollect(fixture)
        with self.assertRaisesRegex(ValueError, "Shared mutable file identity") as caught:
            fixture.validate()
        save("hidden-alias-observation", {
            "samefile": os.path.samefile(left, right), "rejection": str(caught.exception),
            "context": fixture.context, "base": fixture.base, "head": fixture.head,
            "manifest": fixture.manifest, "observations": fixture.observations})
        preserve_fixture("hidden-alias", fixture)


if __name__ == "__main__":
    unittest.main()
