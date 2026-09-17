"""Bounded independent r3 replay; preserve all prior tests and evidence."""
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
FREEZE = HERE / "q1-correction-r2-final-freeze.json"
freeze = json.loads(FREEZE.read_bytes())
spec = importlib.util.spec_from_file_location("original_q1_capture", HERE / "q1-independent-capture.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def save(label, value):
    with (HERE / ("q1-independent-r3-" + label + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


def preflight():
    expected = freeze["frozen_inputs"]
    current = original.hashes([Path(name) for name in expected])
    changed = [name for name in expected if expected[name] != current.get(name)]
    paths = []
    for path in HERE.glob("q1-independent-*"):
        if path.name.startswith("q1-independent-r3-"):
            continue
        paths.extend(path.rglob("*") if path.is_dir() else [path])
    paths.extend(ROOT / "scripts/tests" / name for name in
                 ("test_measure_q1_verification.py", "test_measure_q1_verification_r2.py"))
    preserved = original.hashes(paths)
    save("preflight", {"expected": expected, "observed": current, "changed": changed,
                       "freeze": original.hashes([FREEZE]), "preserved_originals": preserved})
    print(json.dumps({"frozen_inputs": len(expected), "changed": changed,
                      "preserved_files": len(preserved)}))
    return 1 if changed else 0


def worker(pattern, label):
    original.write = save
    original.INPUTS.extend(freeze["frozen_inputs"])
    original.INPUTS.extend([str(FREEZE), str(Path(__file__).resolve()),
                            str(HERE / "q1-correction-r2-result.md")])
    original.ast.unparse(original.ast.parse("value = 1"))
    sys.path.insert(0, str(ROOT / "scripts/tests"))
    original.unittest.defaultTestLoader.discover(str(ROOT / "scripts/tests"), pattern=pattern)
    verifier = sys.modules.get("test_measure_q1_verification")
    if verifier is not None:
        output = HERE / ("q1-independent-r3-fixtures-" + label)
        output.mkdir(exist_ok=False)
        verifier.EVIDENCE = output
    for module in list(sys.modules.values()):
        cached = getattr(module, "__cached__", None)
        if cached and Path(cached).is_file():
            original.INPUTS.append(cached)
    return original.worker(pattern, label)


def capture(pattern, label):
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", pattern, label]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", Q1_VERIFICATION_TAG="independent-r3-" + label)
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
        path = HERE / ("q1-independent-r3-" + label + "." + key + ".bin")
        with path.open("xb") as stream:
            stream.write(b"".join(pieces))
        raw[key] = {**original.hashes([path])[str(path)], "path": str(path)}
    save(label + "-command", {
        "argv": argv, "cwd": str(ROOT), "exit_code": code,
        "seconds": time.monotonic() - started,
        "environment_delta": {"PYTHONDONTWRITEBYTECODE": "1",
                              "Q1_VERIFICATION_TAG": env["Q1_VERIFICATION_TAG"]},
        "outer_bounds": {"idle": 120, "max": 1200}, "raw": raw})
    return code


if __name__ == "__main__":
    action, *args = sys.argv[1:]
    sys.exit(preflight() if action == "preflight" else
             worker(*args) if action == "worker" else capture(*args))
