"""Selected real development checks; explicitly not full Q2 or independent proof."""

import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/tests"))
sys.path.insert(0, str(ROOT / "scripts"))

from test_measure_q2 import ToolRootTests


class ProgressResult(unittest.TextTestResult):
    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        self.stream.writeln("completed actual subtest: " + subtest.id())
        self.stream.flush()


def main():
    name = sys.argv[1] if len(sys.argv) == 2 else "q2-adapter-root-development-records"
    if not name.startswith("q2-adapter-") or Path(name).name != name:
        raise ValueError("An additive q2-adapter evidence directory name is required")
    output = Path(__file__).with_name(name)
    output.mkdir(exist_ok=False)
    os.environ["Q2_ADAPTER_RECORDS"] = str(output)
    inputs = ["scripts/measure.py", "scripts/probe.py", "scripts/measure_graph.py",
              "scripts/tests/test_measure_q2.py",
              "scripts/tests/helpers.py", "scripts/tests/test_measure_inventory.py",
              "scripts/tests/test_measure_graph.py", "scripts/tests/test_measure_q1_integration.py",
              ".ai/workflow-reliability/evidence/q2-adapter-root-development.py",
              ".ai/workflow-reliability/evidence/q2-tool-input-root-amendment.json",
              ".ai/workflow-reliability/evidence/q2-tool-input-root-review.md"]

    def pins():
        return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs}

    before = pins()
    blocked = "test_actual_symlink_root_rejects"
    selected = ["test_measure_q2.ToolRootTests." + name
                for name in unittest.defaultTestLoader.getTestCaseNames(ToolRootTests) if name != blocked]
    selected += [
        "test_measure_graph.GraphTests.test_zero_import_receipts_complete_and_source_bytes_are_not_executed",
        "test_measure_q1_integration.Q1IntegrationTests.test_public_python_cli_from_nested_cwd_keeps_all_nine_and_archives_raw",
        "test_measure_q1_integration.Q1IntegrationTests.test_public_mixed_root_marks_every_unsupported_input",
        "test_measure_q1_integration.Q1IntegrationTests.test_public_validator_rejects_metric_comparison_revision_and_verdict_forgery",
    ]
    suite = unittest.defaultTestLoader.loadTestsFromNames(selected)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2,
                                    resultclass=ProgressResult).run(suite)
    after = pins()
    record = {
        "scope": "Selected development checks only, not full suite, Q2, or independent acceptance",
        "selected_methods": selected,
        "tests_run": result.testsRun,
        "failures": [{"id": test.id(), "traceback": detail} for test, detail in result.failures],
        "errors": [{"id": test.id(), "traceback": detail} for test, detail in result.errors],
        "skipped": [{"id": test.id(), "reason": reason} for test, reason in result.skipped],
        "environment_blocked_not_retried": [{
            "id": "test_measure_q2.ToolRootTests." + blocked,
            "observed_error": "Prior actual os.symlink call raised WinError 1314; privilege not held",
            "disposition": "Persistent test remains; not retried and not counted as passed or skipped",
        }],
        "source_before": before, "source_after": after, "source_unchanged": before == after,
        "raw_fixture_records": ["repository.json", "external.json"],
        "qualified_collectors_executed": [],
        "unfinished": ["Source-tool bindings", "JS syntax/symbol/candidates", "Scalar collectors",
                       "Full Q2 raw reconciliation and CHECK-SCALARS/CHECK-GRAPH/CHECK-JS-PARSER/CHECK-RECONCILE"],
    }
    with (output / "result.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps({"selected_tests_run": result.testsRun,
                      "selected_success": result.wasSuccessful(), "source_unchanged": before == after,
                      "environment_blocked": 1, "Q2_complete": False}), flush=True)
    return 0 if result.wasSuccessful() and before == after else 1


if __name__ == "__main__":
    raise SystemExit(main())
