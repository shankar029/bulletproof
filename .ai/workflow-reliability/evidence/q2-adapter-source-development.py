"""Progress-visible focused source-binding development, never a Q2 quality gate."""

import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/tests"))
sys.path.insert(0, str(ROOT / "scripts"))


class ProgressResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_ids = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_ids.append(test.id())

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        self.stream.writeln("Completed actual subtest: " + subtest.id())
        self.stream.flush()


def main():
    name = sys.argv[1]
    if not name.startswith("q2-adapter-") or Path(name).name != name:
        raise ValueError("A fresh additive q2-adapter evidence directory is required")
    output = Path(__file__).with_name(name)
    output.mkdir(exist_ok=False)
    os.environ["Q2_SOURCE_RECORDS"] = str(output)
    inputs = ["scripts/measure.py", "scripts/probe.py", "scripts/measure_graph.py",
              "scripts/run.py", "scripts/evidence.py", "scripts/tests/helpers.py",
              "scripts/tests/test_measure_source_bindings.py", "scripts/tests/test_measure_q2.py",
              "scripts/tests/test_measure_inventory.py", "scripts/tests/test_measure_graph.py",
              ".ai/workflow-reliability/evidence/q2-adapter-source-development.py",
              ".ai/workflow-reliability/evidence/q2-tool-input-root-amendment.json",
              ".ai/workflow-reliability/evidence/q2-tool-input-root-review.md"]

    def pins():
        return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs}

    before = pins()
    selected = sys.argv[2:] or [
        "test_measure_source_bindings",
        "test_measure_q2.ToolRootTests.test_empty_mode_and_conditional_root_validation",
        "test_measure_q2.ToolRootTests.test_duplicate_prefix_reserved_namespace_and_hardlinks_reject",
        "test_measure_graph.GraphTests.test_zero_import_receipts_complete_and_source_bytes_are_not_executed",
    ]
    suite = unittest.defaultTestLoader.loadTestsFromNames(selected)
    started = time.monotonic()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2,
                                    resultclass=ProgressResult).run(suite)
    after = pins()
    record = {
        "scope": "Source-binding execution and focused compatibility only; not collectors or all Q2",
        "selected": selected, "tests_run": result.testsRun,
        "passed_ids": result.passed_ids, "seconds": time.monotonic() - started,
        "failures": [{"id": test.id(), "traceback": detail} for test, detail in result.failures],
        "errors": [{"id": test.id(), "traceback": detail} for test, detail in result.errors],
        "skipped": [{"id": test.id(), "reason": detail} for test, detail in result.skipped],
        "before": before, "after": after, "same_bytes": before == after,
        "prior_symlink_creation": "WinError 1314; persistent case remains blocked, not retried or counted",
        "full_Q2_complete": False,
    }
    with (output / "result.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps({"tests_run": result.testsRun, "selected_success": result.wasSuccessful(),
                      "same_bytes": before == after, "full_Q2_complete": False}), flush=True)
    return 0 if result.wasSuccessful() and before == after else 1


if __name__ == "__main__":
    raise SystemExit(main())
