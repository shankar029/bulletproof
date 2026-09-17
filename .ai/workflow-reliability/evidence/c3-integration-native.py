"""Replay existing contributor native inventory with actual streamed output."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
files = sorted(ROOT.glob("evals/lib/*.test.mjs")) + [
    ROOT / "evals/agent/agent.test.mjs", ROOT / "evals/workflow/failures.test.mjs",
]
argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", "1800",
        "--", "node", "--test", *map(str, files)]
environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", BULLETPROOF_PYTHON=sys.executable)
temp = tempfile.mkdtemp(prefix="c3n-", dir=Path.home() / "AppData/Local/Temp")
environment["TEMP"] = environment["TMP"] = temp
before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
started = time.monotonic()
code = None
try:
    with (OUT / "c3-integration-native.log").open("x", encoding="utf-8") as log:
        child = subprocess.Popen(argv, cwd=ROOT, env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, encoding="utf-8", errors="replace")
        for line in child.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log.write(line)
            log.flush()
        code = child.wait()
finally:
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    remaining = [p.name for p in Path(temp).iterdir()]
    if not remaining:
        Path(temp).rmdir()
    with (OUT / "c3-integration-native.json").open("x", encoding="utf-8") as stream:
        json.dump({
            "kind": "local-development-replay", "argv": argv, "exit": code,
            "elapsed_seconds": time.monotonic() - started, "before": before, "after": after,
            "owned_temp": temp, "remaining_owned_temp_entries": remaining,
            "limits": "Five workflow entries replay Python cases already in CLI33; not additional independent runtime features.",
        }, stream, indent=2)
        stream.write("\n")
raise SystemExit(code if code is not None else 1)
