"""Additive bounded verification capture. Never overwrites prior evidence."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture

FREEZE = EVIDENCE / "c2a-freeze.json"
FROZEN = json.loads(FREEZE.read_bytes())["pins"]
EXTRA = [
    FREEZE, Path(__file__).resolve(),
    ROOT / "scripts/tests/test_run_c2a_verification.py",
    ROOT / "scripts/tests/test_probe.py", ROOT / "scripts/tests/test_evidence.py",
    ROOT / "scripts/native_result.mjs",
]
EXTRA += list((ROOT / "scripts").glob("*.py"))
EXTRA += list(Path(sys.executable).parent.glob("python*.dll"))
for tool in ("git", "node", "powershell.exe", "taskkill"):
    located = shutil.which(tool)
    if located:
        EXTRA.append(Path(located).resolve())


def pins():
    paths = sorted(set(FROZEN) | {str(path) for path in EXTRA})
    return {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in paths}


def main():
    tag, idle, maximum, *argv = sys.argv[1:]
    if not tag.isalnum() or not argv:
        raise SystemExit("usage: TAG IDLE MAX ARGV...")
    target = EVIDENCE / f"c2a-independent-{tag}.json"
    if target.exists():
        raise SystemExit(f"refusing to overwrite {target}")
    before = pins()
    mismatch = [path for path, digest in FROZEN.items() if before[path] != digest]
    if mismatch:
        raise SystemExit(f"owner freeze mismatch before execution: {mismatch}")
    started = time.time()
    result = run_capture(argv, cwd=str(ROOT), idle=float(idle), max_total=float(maximum))
    after = pins()
    changed = [path for path in before if before[path] != after[path]]
    inventory = re.findall(r"Ran (\d+) tests? in ", result[2])
    record = {
        "argv": argv, "cwd": str(ROOT), "idle": float(idle), "max_total": float(maximum),
        "runtime": sys.version, "executable": sys.executable,
        "env": {"PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE"),
                "PATH": os.environ.get("PATH")},
        "elapsed_seconds": time.time() - started,
        "exit": result[0], "stdout": result[1], "stderr": result[2],
        "test_counts": [int(count) for count in inventory],
        "before": before, "after": after, "changed": changed,
    }
    with target.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    print(result[1], end="", flush=True)
    print(result[2], end="", file=sys.stderr, flush=True)
    print(json.dumps({"evidence": str(target), "exit": result[0], "test_counts": inventory,
                      "pin_count": len(before), "changed": changed}), flush=True)
    return 1 if changed else result[0]


if __name__ == "__main__":
    raise SystemExit(main())
