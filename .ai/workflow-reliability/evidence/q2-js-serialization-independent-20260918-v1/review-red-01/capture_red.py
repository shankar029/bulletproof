"""Capture the two focused review regressions, never replay the frozen suite."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

root = Path.cwd()
home = Path(__file__).resolve().parent
here = home / "corrected" if "--corrected" in sys.argv else home
python = r"C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe"
argv = [python, "-B", "-u", r"scripts\run.py", "--idle", "120", "--max", "900", "--",
        python, "-B", "-u", "-m", "unittest", "discover", "-s", r"scripts\tests",
        "-p", "test_measure_js_serialization_independent.py", "-k", "ReviewRegressions", "-v"]
env = dict(os.environ)
env["PATH"] = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd" + os.pathsep + env["PATH"]
env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", Q2_JS_RECORDS=str(here))


def save(name, value):
    with (here / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


def artifact(path):
    data = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


before = json.loads((home / "before.json").read_bytes())["frozen_reconciliation"]
for row in before["frozen"]:
    assert artifact(root / row["path"]) == {key: row[key] for key in ("path", "sha256", "bytes")}
save("invocation.json", {
    "argv": argv, "cwd": str(root), "outer_idle_seconds": 120, "outer_max_seconds": 900,
    "native_idle_seconds": 30, "native_max_seconds": 90,
    "environment": {key: env[key] for key in ("PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "Q2_JS_RECORDS")},
    "path_prefix": env["PATH"].split(os.pathsep)[0],
    "test_inputs": [artifact(root / "scripts/tests" / name) for name in
                    ("test_measure_js_serialization_independent.py", "measure_js_serialization_independent.test.mjs")],
})
started = time.monotonic()
with (here / "stdout.bin").open("xb") as out, (here / "stderr.bin").open("xb") as err:
    process = subprocess.Popen(argv, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
save("exit.json", {"returncode": code, "elapsed_seconds": time.monotonic() - started,
                   "stdout": artifact(here / "stdout.bin"), "stderr": artifact(here / "stderr.bin")})
print("Focused review invocation exit:", code, flush=True)
sys.exit(code)
