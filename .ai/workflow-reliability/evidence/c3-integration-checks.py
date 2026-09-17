"""Local C3 discovery/execution evidence; not independent acceptance or root quality."""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TESTS = ROOT / "scripts/tests"
sys.path.insert(0, str(TESTS))
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def pins():
    files = [ROOT / "scripts/tests/test_workflow_cli_boundaries.py"]
    files += sorted((ROOT / "scripts").glob("*.py"))
    files += sorted(TESTS.glob("*.py"))
    files += [OUT / "joint-cli-binding-tests.py"]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


class EvidenceStream:
    def __init__(self, log):
        self.log = log

    def write(self, text):
        self.log.write(text)
        self.log.flush()
        sys.stdout.write(text)
        sys.stdout.flush()

    def flush(self):
        self.log.flush()
        sys.stdout.flush()


def main():
    all_suite = unittest.TestLoader().discover(str(TESTS))
    all_ids = [test.id() for test in flatten(all_suite)]
    selected = unittest.TestLoader().discover(str(TESTS), pattern="test_workflow_cli*.py")
    selected_ids = [test.id() for test in flatten(selected)]
    assert len(all_ids) == len(set(all_ids)), "Normal discovery duplicated method IDs"
    assert len(selected_ids) == len(set(selected_ids)) == 33
    assert sum(name.startswith("test_workflow_cli_boundaries.") for name in all_ids) == 3
    assert sum(name.startswith("test_workflow_cli.WorkflowCliTests.") for name in all_ids) == 30
    assert set(selected_ids) <= set(all_ids)
    before = pins()
    started = time.monotonic()
    # Short, newly owned OS-temp storage; no old timeout directory is touched.
    temp = tempfile.mkdtemp(prefix="c3-", dir=Path.home() / "AppData/Local/Temp")
    os.environ["TEMP"] = os.environ["TMP"] = temp
    tempfile.tempdir = temp
    result = None
    try:
        with (OUT / "c3-integration-cli-tests.log").open("x", encoding="utf-8") as log:
            stream = EvidenceStream(log)
            stream.write(f"Ordinary discovery: {len(all_ids)}; selected CLI: {len(selected_ids)}\n")
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(selected)
    finally:
        after = pins()
        remaining = [p.name for p in Path(temp).iterdir()]
        if not remaining:
            Path(temp).rmdir()
        record = {
            "kind": "local-development-proof",
            "ordinary_discovery": all_ids,
            "selected": selected_ids,
            "unexecuted": sorted(set(all_ids) - set(selected_ids)),
            "run": result.testsRun if result else None,
            "failures": result.failures if result else [],
            "errors": result.errors if result else [],
            "skipped": result.skipped if result else [],
            "successful": result.wasSuccessful() if result else False,
            "elapsed_seconds": time.monotonic() - started,
            "before": before,
            "after": after,
            "changed_inputs": [name for name in before if before[name] != after.get(name)],
            "owned_temp": temp, "remaining_owned_temp_entries": remaining,
            "limits": [
                "33 methods include the historical three ports, not new independent proof.",
                "Unexecuted normal inventory is explicit; no full-suite or quality claim.",
                "Q2 may change unowned measurement inputs concurrently; joint freeze/acceptance remains parent-owned.",
                "Known symlink WinError1314 case remains environment-unverified; old timeout cleanup UNKNOWN.",
            ],
        }
        with (OUT / "c3-integration-cli-tests.json").open("x", encoding="utf-8") as output:
            json.dump(record, output, indent=2)
            output.write("\n")
    return 0 if result and result.wasSuccessful() and not remaining else 1


if __name__ == "__main__":
    raise SystemExit(main())
