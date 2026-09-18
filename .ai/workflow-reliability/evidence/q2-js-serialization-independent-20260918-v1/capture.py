"""Owned Phase 5 capture; no production or qualification changes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
SEAL = EVIDENCE / "q2-js-serialization-seal.json"
EXPECTED = "c43769d83411dd41063be59a77e87918991673f360ec8b759f1a22558bc528da"
PYTHON = r"C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, value):
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def snapshot(label):
    assert sha(SEAL.read_bytes()) == EXPECTED, "Frozen seal mismatch"
    seal = json.loads(SEAL.read_bytes())
    refs = {row["path"]: row for row in seal["authorities"] + seal["owned_files"]}
    original = json.loads((EVIDENCE / "q2-js-serialization-final-02" /
                           "test_native_byte_boundaries.json").read_bytes())
    for row in original["executing_sources"]:
        name = "scripts/" + row["path"]
        refs[name] = {**row, "path": name}
    rows = []
    for name, ref in sorted(refs.items()):
        data = (ROOT / name).read_bytes()
        rows.append({"path": name, "sha256": sha(data), "bytes": len(data),
                     "matches": sha(data) == ref["sha256"] and len(data) == ref["bytes"]})
    # Immutable archives are referenced, never recopied or requalified.
    qualification = []
    for name in ["q2-tools-runtime-bindings.json", "q2-tools-source-roots.json",
                 "q2-tools-source-extracted-pins.json", "q2-tools-source-typescript-results.json",
                 "q2-tools-source-typescript-help.stdout.log"]:
        data = (EVIDENCE / name).read_bytes()
        qualification.append({"path": name, "sha256": sha(data), "bytes": len(data)})
    save(label + ".json", {"seal_sha256": EXPECTED, "frozen": rows, "qualification": qualification})
    assert all(row["matches"] for row in rows), "Frozen input changed"
    if label != "before":
        before = json.loads((HERE / "before.json").read_bytes())
        assert before["qualification"] == qualification, "Qualification archive changed"
    print(f"{label}: {len(rows)} sealed/transitively sealed inputs match; 5 qualification refs hashed", flush=True)


def execute(label, pattern):
    env = dict(os.environ)
    env["PATH"] = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd" + os.pathsep + env["PATH"]
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", Q2_JS_RECORDS=str(HERE))
    argv = [PYTHON, "-B", "-u", r"scripts\run.py", "--idle", "120", "--max", "900", "--",
            PYTHON, "-B", "-u", "-m", "unittest", "discover", "-s", r"scripts\tests",
            "-p", pattern, "-v"]
    save(label + "-invocation.json", {"argv": argv, "cwd": str(ROOT),
         "environment": {key: env[key] for key in ("PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "Q2_JS_RECORDS")},
         "path_prefix": env["PATH"].split(os.pathsep)[0], "idle_seconds": 120, "max_seconds": 900,
         "nested_idle_seconds": 30, "nested_max_seconds": 90})
    started = time.monotonic()
    with (HERE / (label + ".stdout.bin")).open("xb") as out, (HERE / (label + ".stderr.bin")).open("xb") as err:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def pump(source, target, console):
            while block := source.read(4096):
                target.write(block)
                target.flush()
                console.buffer.write(block)
                console.flush()

        threads = [threading.Thread(target=pump, args=(process.stdout, out, sys.stdout)),
                   threading.Thread(target=pump, args=(process.stderr, err, sys.stderr))]
        for thread in threads:
            thread.start()
        code = process.wait()
        for thread in threads:
            thread.join()
    # Persist raw streams and exit result before any output interpretation.
    save(label + "-result.json", {"returncode": code, "elapsed_seconds": time.monotonic() - started,
         "stdout_sha256": sha((HERE / (label + ".stdout.bin")).read_bytes()),
         "stderr_sha256": sha((HERE / (label + ".stderr.bin")).read_bytes())})
    print(f"{label}: returncode={code}", flush=True)
    return code


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "replay":
        snapshot("before")
        sys.exit(execute("replay", "test_measure_js.py"))
    elif mode == "independent":
        sys.exit(execute("independent", "test_measure_js_serialization_independent.py"))
    else:
        snapshot(mode)
