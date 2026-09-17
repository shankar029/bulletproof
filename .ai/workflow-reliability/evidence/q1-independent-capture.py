"""Bounded Q1-only verification capture. Invoke through scripts/run.py."""
import hashlib
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
INPUTS = [
    "scripts/measure.py", "scripts/measure_graph.py", "scripts/probe.py",
    "scripts/mutate.py", "scripts/evidence.py", "scripts/run.py", "scripts/native_result.mjs",
    "scripts/tests/helpers.py", "scripts/tests/test_measure_inventory.py",
    "scripts/tests/test_measure_graph.py", "scripts/tests/test_measure_q1_integration.py",
    "scripts/tests/test_probe.py", "scripts/tests/test_measure_q1_verification.py",
    ".ai/workflow-reliability/measurement-enablement.html",
    ".ai/workflow-reliability/measurement-enablement-contracts.json",
    ".ai/workflow-reliability/evidence/measurement-design-review-r2.md",
    "CONTRIBUTING.md",
]


def hashes(paths):
    return {str(path): {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "bytes": path.stat().st_size}
            for path in sorted(set(paths)) if path.is_file()}


def write(name, value):
    path = OUT / ("q1-independent-" + name + ".json")
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def worker(pattern, label):
    ast.unparse(ast.parse("value = 1"))  # Load the parser's lazy stdlib dependency before pinning.
    sys.path.insert(0, str(ROOT / "scripts/tests"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "scripts/tests"), pattern=pattern)
    paths = {ROOT / name for name in INPUTS if (ROOT / name).is_file()}
    paths.add(Path(__file__).resolve())
    # Pin imported Python code, its runtime binaries, and native fixture executables.
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename and Path(filename).is_file():
            paths.add(Path(filename))
    paths.add(Path(sys.executable))
    paths.update(Path(sys.executable).parent.glob("python*.dll"))
    import shutil
    for executable in ("git", "node"):
        resolved = shutil.which(executable)
        if resolved:
            paths.add(Path(resolved))
    before = hashes(paths)
    write(label + "-inputs-before", before)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    # Include modules loaded lazily; distinguish these from initial pins.
    after = hashes(paths)
    write(label + "-inputs-after", after)
    late = {Path(module.__file__) for module in list(sys.modules.values())
            if getattr(module, "__file__", None) and Path(module.__file__).is_file()} - paths
    write(label + "-late-inputs", hashes(late))
    write(label + "-result", {
        "tests": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "unchanged": before == after,
        "changed": [name for name in before if before[name] != after.get(name)],
    })
    return 0 if result.wasSuccessful() and before == after else 1


def capture(pattern, label):
    command = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", pattern, label]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    started = time.time()
    proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    chunks = {"stdout": [], "stderr": []}

    def pump(stream, key):
        while data := stream.read1(65536):
            chunks[key].append(data)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        stream.close()

    threads = [threading.Thread(target=pump, args=(getattr(proc, key), key)) for key in chunks]
    for thread in threads:
        thread.start()
    code = proc.wait()
    for thread in threads:
        thread.join()
    raw = {}
    for key, pieces in chunks.items():
        data = b"".join(pieces)
        path = OUT / ("q1-independent-" + label + "." + key + ".bin")
        path.write_bytes(data)
        raw[key] = {"path": str(path), "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()}
    write(label + "-command", {"argv": command, "cwd": str(ROOT),
                              "environment_delta": {"PYTHONDONTWRITEBYTECODE": "1"},
                              "exit_code": code, "seconds": time.time() - started,
                              "outer_bounds": {"idle": 120, "max": 1200}, "raw": raw})
    return code


if __name__ == "__main__":
    action, pattern, label = sys.argv[1:]
    sys.exit(worker(pattern, label) if action == "worker" else capture(pattern, label))
