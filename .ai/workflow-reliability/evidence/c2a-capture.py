"""Bounded C2a command capture; no workflow admission or acceptance claim."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture

INPUTS = [
    "scripts/run.py", "scripts/tests/test_run.py", "scripts/probe.py",
    "scripts/mutate.py", "scripts/measure.py", "scripts/measure_graph.py",
    "scripts/evidence.py", "scripts/tests/helpers.py",
    ".ai/workflow-reliability/design.html",
    ".ai/workflow-reliability/design-contracts.json",
    ".ai/workflow-reliability/continuation-plan.html",
    ".ai/workflow-reliability/evidence/continuation-plan-review.md",
    ".ai/workflow-reliability/evidence/c2a-capture.py",
    ".ai/workflow-reliability/evidence/c2a-callers.py",
]


def pins():
    paths = [ROOT / value for value in INPUTS]
    paths += [Path(sys.executable)]
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


if __name__ == "__main__":
    tag, *argv = sys.argv[1:]
    if not tag.isalnum() or not argv:
        raise SystemExit("usage: c2a-capture.py ALNUM_TAG COMMAND ARG...")
    dest = Path(__file__).with_name(f"c2a-{tag}.json")
    if dest.exists():
        raise SystemExit(f"refusing to overwrite {dest}")
    before = pins()
    result = run_capture(argv, cwd=str(ROOT), idle=60, max_total=180)
    record = {
        "argv": argv, "cwd": str(ROOT), "idle": 60, "max_total": 180,
        "runtime": sys.version, "executable": sys.executable,
        "PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE"),
        "before": before, "after": pins(),
        "exit": result[0], "stdout": result[1], "stderr": result[2],
    }
    dest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2), flush=True)
    raise SystemExit(result[0])
