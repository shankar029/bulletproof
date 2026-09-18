"""Stream/capture the two additional discoverable boundary tests."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
argv = [sys.executable, "-B", "-u", str(root / "scripts/run.py"),
        "--idle", "120", "--max", "300", "--",
        sys.executable, "-B", "-u", "-m", "unittest", "discover",
        "-s", "scripts/tests", "-p", "test_measure_js_core_independent.py", "-v"]
env = dict(os.environ, Q2_JS_INDEPENDENT_RECORDS=str(out))
paths = [root / "scripts/tests/test_measure_js_core_independent.py",
         root / "scripts/tests/measure_js_core_independent.test.mjs"]
def pins():
    return [{"path": str(path.relative_to(root)), "bytes": path.stat().st_size,
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]
before = pins()
with (out / "boundary-invocation.json").open("x", encoding="utf-8") as stream:
    json.dump({"argv": argv, "cwd": str(root), "test_pins": before, "environment": {
        name: env.get(name) for name in ("PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING",
                                       "PYTHONPATH", "PATH", "TEMP", "TMP",
                                       "Q2_JS_INDEPENDENT_RECORDS")}}, stream, indent=2)
started = time.monotonic()
with (out / "boundary-unittest.log").open("x", encoding="utf-8") as log:
    process = subprocess.Popen(argv, cwd=root, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                               errors="replace", bufsize=1)
    for line in process.stdout:
        print(line, end="", flush=True)
        log.write(line)
        log.flush()
    code = process.wait()
with (out / "boundary-result.json").open("x", encoding="utf-8") as stream:
    json.dump({"returncode": code, "wall_seconds": time.monotonic() - started,
               "test_pins": pins(), "test_pins_unchanged": before == pins()}, stream, indent=2)
assert before == pins()
raise SystemExit(code)
