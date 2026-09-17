"""One bounded capture-only correction: repository import root, no global profiler."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unittest

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("joint_capture", HERE / "joint-cli-binding-verify.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


def completed(batch):
    text = (capture.OUT / batch / "output.log").read_text(encoding="utf-8")
    entries = list(re.finditer(r"^test_\w+ \(([\w.]+)\) \.\.\. ", text, re.M))
    return [match.group(1) for index, match in enumerate(entries)
            if text[match.end():entries[index + 1].start() if index + 1 < len(entries) else len(text)].rstrip().endswith("ok")]


def main():
    batch = sys.argv[2]
    directory = capture.OUT / (batch + "-resume")
    batches, tests = capture.load_tests()
    if batch == "support":
        selected = [name for name in batches[batch] if name.startswith("test_run_c2a_verification.")]
    else:
        selected = [name for name in batches[batch] if name not in completed(batch)]
    if sys.argv[1] == "worker":
        os.environ["Q2_SOURCE_RECORDS"] = str(directory)
        os.environ["Q2_ADAPTER_RECORDS"] = str(directory)
        capture.save(directory / "selection.json", {
            "corrected_discovery": batches[batch], "retained_completed": completed(batch),
            "selected": selected, "reason": "Fix repository import path; remove expensive global profile capture"})
        started = time.monotonic()
        result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, failfast=True,
                                        resultclass=capture.Progress).run(
            unittest.TestSuite(tests[name] for name in selected))
        capture.save(directory / "result.json", {
            "selected": selected, "tests_run": result.testsRun, "passed": result.passed,
            "failures": [(t.id(), detail) for t, detail in result.failures],
            "errors": [(t.id(), detail) for t, detail in result.errors],
            "skips": [(t.id(), detail) for t, detail in result.skipped],
            "seconds": time.monotonic() - started})
        return 0 if result.wasSuccessful() and not result.skipped else 1
    directory.mkdir(exist_ok=False)
    settings = json.loads((capture.OUT / "environment.json").read_bytes())
    env = os.environ.copy()
    env.update({key: settings["short_temp"] for key in ("TEMP", "TMP", "TMPDIR")})
    env.update(PYTHONDONTWRITEBYTECODE="1", BULLETPROOF_PYTHON=sys.executable)
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", "1800", "--",
            sys.executable, "-B", "-u", str(Path(__file__)), "worker", batch]
    capture.save(directory / "command.json", {
        "argv": argv, "cwd": str(ROOT),
        "environment": {k: env[k] for k in ("PATH", "TEMP", "TMP", "TMPDIR",
                                            "PYTHONDONTWRITEBYTECODE", "BULLETPROOF_PYTHON")},
        "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "retained_completed": completed(batch), "selected": selected})
    start = time.monotonic()
    with (directory / "output.log").open("xb") as output:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        capture.save(directory / "pid.json", {"runner_pid": process.pid, "supervisor_pid": os.getpid()})
        while data := process.stdout.read1(65536):
            output.write(data)
            output.flush()
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        process.stdout.close()
        code = process.wait()
    capture.save(directory / "exit.json", {"returncode": code, "seconds": time.monotonic() - start})
    return code


if __name__ == "__main__":
    raise SystemExit(main())
