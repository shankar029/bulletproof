"""Owner round-2 capture; reuse immutable verifier dependency pinning."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("q1_capture", HERE / "q1-independent-capture.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def save(label, value):
    with (HERE / ("q1-correction-r2-" + label + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


def preflight():
    paths = []
    for path in HERE.glob("q1-independent-*"):
        paths.extend(path.rglob("*") if path.is_dir() else [path])
    paths += [ROOT / "scripts/tests/test_measure_q1_verification.py",
              ROOT / "scripts/tests/test_measure_q1_verification_r2.py"]
    frozen = json.loads((HERE / "q1-independent-r2-final-freeze.json").read_bytes())
    # Use the known prior owner freeze as the pre-correction source boundary.
    previous = json.loads((HERE / "q1-correction-final-freeze.json").read_bytes())["frozen_inputs"]
    changed = [name for name, ref in previous.items()
               if original.hashes([Path(name)]).get(name) != ref]
    assert not changed, changed
    save("preserved-before", original.hashes(paths))
    save("preflight", {"previous_inputs": previous, "changed": changed,
                      "independent_freeze_sha256": original.hashes(
                          [HERE / "q1-independent-r2-final-freeze.json"]),
                      "independent_status": frozen.get("status")})


def worker(pattern, label):
    original.write = save
    original.INPUTS += [str(Path(__file__).resolve()),
                        "scripts/tests/test_measure_q1_verification_r2.py"]
    original.ast.unparse(original.ast.parse("value = 1"))
    sys.path.insert(0, str(ROOT / "scripts/tests"))
    if "::" in pattern:
        pattern, match = pattern.split("::", 1)
        original.unittest.defaultTestLoader.testNamePatterns = ["*" + match + "*"]
    original.unittest.defaultTestLoader.discover(str(ROOT / "scripts/tests"), pattern=pattern)
    verifier = sys.modules.get("test_measure_q1_verification")
    if verifier is not None:
        output = HERE / ("q1-correction-r2-fixtures-" + label)
        output.mkdir(exist_ok=False)
        verifier.EVIDENCE = output
    for module in list(sys.modules.values()):
        cached = getattr(module, "__cached__", None)
        if cached and Path(cached).is_file():
            original.INPUTS.append(cached)
    return original.worker(pattern, label)


def capture(pattern, label):
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", pattern, label]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", Q1_VERIFICATION_TAG="owner-r2-" + label)
    started = time.monotonic()
    proc = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    chunks = {"stdout": [], "stderr": []}

    def pump(key):
        stream = getattr(proc, key)
        while data := stream.read1(65536):
            chunks[key].append(data)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        stream.close()

    threads = [threading.Thread(target=pump, args=(key,)) for key in chunks]
    for thread in threads:
        thread.start()
    code = proc.wait()
    for thread in threads:
        thread.join()
    raw = {}
    for key, pieces in chunks.items():
        path = HERE / ("q1-correction-r2-" + label + "." + key + ".bin")
        with path.open("xb") as stream:
            stream.write(b"".join(pieces))
        raw[key] = {**original.hashes([path])[str(path)], "path": str(path)}
    save(label + "-command", {
        "argv": argv, "cwd": str(ROOT), "environment_delta": {
            "PYTHONDONTWRITEBYTECODE": "1", "Q1_VERIFICATION_TAG": env["Q1_VERIFICATION_TAG"]},
        "exit_code": code, "seconds": time.monotonic() - started,
        "outer_bounds": {"idle": 120, "max": 900}, "raw": raw})
    return code


if __name__ == "__main__":
    action, *args = sys.argv[1:]
    if action == "preflight":
        preflight()
    else:
        sys.exit(worker(*args) if action == "worker" else capture(*args))
