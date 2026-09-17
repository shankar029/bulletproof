"""Owned bounded byte forwarding around the real CLI runner, not run_capture."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest


ROOT = Path.cwd()
EVIDENCE = ROOT / ".ai/workflow-reliability/evidence"
CAP = 4 * 1024 * 1024
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/tests"))
from run import _kill_tree


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def pins():
    freeze = json.loads((EVIDENCE / "c2b-state-freeze.json").read_bytes())
    paths = dict(freeze["current_pins"])
    paths[".ai/workflow-reliability/evidence/c2b-state-freeze.json"] = None
    paths[".ai/workflow-reliability/evidence/c2b-state-handoff.md"] = None
    paths[Path(__file__).relative_to(ROOT).as_posix()] = None
    paths["scripts/tests/test_workflow_adoption_verification.py"] = None
    result = {}
    for name, expected in paths.items():
        path = (Path(sys.executable) if name == "runtime:python" else
                Path(r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe")
                if name == "runtime:git" else ROOT / name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected is not None and expected != digest:
            raise RuntimeError("Frozen input drift: " + name)
        result[name] = digest
    return result


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item.id()


def main():
    tag, pattern = sys.argv[1:]
    if not tag.isalnum() or pattern not in ("test_evidence.py", "test_workflow*.py"):
        raise ValueError("Only uniquely tagged approved suites")
    destination = EVIDENCE / ("c2b-state-independent-" + tag)
    destination.mkdir(exist_ok=False)
    before = pins()
    save(destination / "pins-before.json", before)
    inventory = list(flatten(unittest.defaultTestLoader.discover(
        str(ROOT / "scripts/tests"), pattern=pattern)))
    if any("_FailedTest" in name for name in inventory) or len(set(inventory)) != len(inventory):
        raise RuntimeError("Discovery error or duplicate test IDs")
    save(destination / "inventory.json", inventory)
    temporary = destination / "owned-temp"
    temporary.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary))
    command = [sys.executable, "-u", "-B", "scripts/run.py", "--idle", "120", "--max", "600",
               "--", sys.executable, "-u", "-B", "-m", "unittest", "discover",
               "-s", "scripts/tests", "-p", pattern, "-v"]
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            bufsize=0, env=env,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
    save(destination / "launch.json", {
        "command": command, "cwd": str(ROOT), "pid": proc.pid, "capture_pid": os.getpid(),
        "time": time.time(), "cap_bytes": CAP, "temp": str(temporary),
        "encoding": "raw merged CLI bytes; CLI UTF-8 replacement/line forwarding",
        "environment_overrides": {key: env[key] for key in
                                  ("PYTHONDONTWRITEBYTECODE", "TEMP", "TMP", "TMPDIR")},
        "path": env["PATH"],
    })
    total, chunks, first, last, first_before_exit, overflow = 0, 0, None, None, False, False
    try:
        with (destination / "combined.log").open("xb") as log:
            while chunk := proc.stdout.read(4096):
                now = time.monotonic() - started
                if first is None:
                    first, first_before_exit = now, proc.poll() is None
                last, chunks = now, chunks + 1
                if total + len(chunk) > CAP:
                    overflow = True
                    _kill_tree(proc)
                    break
                total += len(chunk)
                log.write(chunk)
                log.flush()
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
    finally:
        proc.stdout.close()
        if proc.poll() is None and overflow:
            _kill_tree(proc)
    rc = proc.wait()
    after = pins()
    save(destination / "pins-after.json", after)
    remains = [p.relative_to(temporary).as_posix() for p in temporary.rglob("*")]
    result = {
        "returncode": rc, "overflow": overflow, "elapsed_seconds": time.monotonic() - started,
        "captured_bytes": total, "chunks_forwarded": chunks,
        "first_chunk_seconds": first, "last_chunk_seconds": last,
        "first_chunk_before_direct_exit": first_before_exit,
        "runner_pid": proc.pid, "direct_runner_reaped": proc.returncode is not None,
        "owned_temp_remaining": remains, "pins_unchanged": before == after,
        "inventory_count": len(inventory),
        "limits": "No descendant-death claim; no historical cleanup or actor/recovery proof.",
    }
    save(destination / "result.json", result)
    print(json.dumps(result), flush=True)
    return rc or (3 if overflow or before != after or remains else 0)


if __name__ == "__main__":
    sys.exit(main())
