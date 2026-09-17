"""Correction-only raw capture; reuse the untouched verifier's dependency pinning."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("q1_original_capture", HERE / "q1-independent-capture.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
original.INPUTS.append(str(Path(__file__).resolve()))


def save(name, value):
    path = HERE / ("q1-correction-" + name + ".json")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


original.write = save


def worker(pattern, label):
    if "::" in pattern:
        pattern, selected = pattern.split("::", 1)
        original.unittest.defaultTestLoader.testNamePatterns = ["*" + selected + "*"]
    original.ast.unparse(original.ast.parse("value = 1"))
    sys.path.insert(0, str(original.ROOT / "scripts/tests"))
    original.unittest.defaultTestLoader.discover(str(original.ROOT / "scripts/tests"), pattern=pattern)
    # -B prevents writes, not reads, of existing bytecode caches. Pin those too.
    for module in list(sys.modules.values()):
        cached = getattr(module, "__cached__", None)
        if cached and Path(cached).is_file():
            original.INPUTS.append(cached)
    return original.worker(pattern, label)


def capture(pattern, label):
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", pattern, label]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    # Original verifier tests may create new tagged counterexample artifacts,
    # never overwrite their original evidence. Their test code stays untouched.
    env["Q1_VERIFICATION_TAG"] = "owner-correction-" + label
    started = time.monotonic()
    proc = subprocess.Popen(argv, cwd=original.ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pieces = {"stdout": [], "stderr": []}

    def pump(key):
        stream = getattr(proc, key)
        while chunk := stream.read1(65536):
            pieces[key].append(chunk)
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
        stream.close()

    threads = [threading.Thread(target=pump, args=(key,)) for key in pieces]
    for thread in threads:
        thread.start()
    code = proc.wait()
    for thread in threads:
        thread.join()
    raw = {}
    for key, chunks in pieces.items():
        path = HERE / ("q1-correction-" + label + "." + key + ".bin")
        with path.open("xb") as stream:
            stream.write(b"".join(chunks))
        raw[key] = original.hashes([path])[str(path)]
        raw[key]["path"] = str(path)
    save(label + "-command", {
        "argv": argv, "cwd": str(original.ROOT), "exit_code": code,
        "environment_delta": {"PYTHONDONTWRITEBYTECODE": "1",
                              "Q1_VERIFICATION_TAG": env["Q1_VERIFICATION_TAG"]},
        "seconds": time.monotonic() - started, "outer_bounds": {"idle": 120, "max": 900}, "raw": raw})
    return code


if __name__ == "__main__":
    action, pattern, label = sys.argv[1:]
    if action == "pin":
        paths = list(HERE.glob("q1-independent-*")) + [
            original.ROOT / "scripts/tests/test_measure_q1_verification.py"]
        save(label, original.hashes(paths))
    else:
        sys.exit(worker(pattern, label) if action == "worker" else capture(pattern, label))
