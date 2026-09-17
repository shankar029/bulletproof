"""R2: same real byte transport, corrected exclusively owned short temp layout."""

import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path.cwd()
EVIDENCE = ROOT / ".ai/workflow-reliability/evidence"
old = runpy.run_path(str(EVIDENCE / "c2b-state-independent-stream.py"))
save, CAP = old["save"], old["CAP"]


def pins():
    result = old["pins"]()
    expected = json.loads((EVIDENCE / "c2b-state-independent-reconciliation.json").read_bytes())["pins"]
    assert result == expected, "Previously verified source/test/helper drift"
    paths = [
        EVIDENCE / ("c2b-state-independent-" + name) for name in
        ("report.md", "reconciliation.json", "reconcile.py", "state.md")
    ]
    for tag in ("transport01", "workflow01"):
        paths.extend(p for p in (EVIDENCE / ("c2b-state-independent-" + tag)).rglob("*") if p.is_file())
    paths.extend(EVIDENCE / name for name in (
        "c2b-state-workflow01-timeout.json", "c2b-state-gate02-timeout.json",
        "c2b-state-independent-r2-stream.py", "c2b-state-independent-r2-stage.py"))
    result.update({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in paths})
    assert result[".ai/workflow-reliability/evidence/c2b-state-independent-report.md"] == \
        "0f96ab97cc3f37f94c29d5d3b2c7176c35ae4c0acbbdca3d9acbc6c4c22945ff"
    assert result[".ai/workflow-reliability/evidence/c2b-state-independent-reconciliation.json"] == \
        "415880ede79316c95e923a8d272b428e9c2266d34c357cfd89ce4501b6ab1256"
    return result


def main():
    phase, = sys.argv[1:]
    assert phase in ("preflight", "workflow")
    destination = EVIDENCE / ("c2b-state-independent-r2-" + phase + "01")
    destination.mkdir(exist_ok=False)
    before = pins()
    save(destination / "pins-before.json", before)
    preflight = EVIDENCE / "c2b-state-independent-r2-preflight01"
    if phase == "preflight":
        temporary = Path(tempfile.mkdtemp(prefix="bc2-"))
        assert not temporary.resolve().is_relative_to(ROOT)
        assert len(str(temporary)) < 100, "OS-temp root is not short"
        ownership = {"path": str(temporary), "creator_pid": os.getpid(),
                     "st_dev": temporary.stat().st_dev, "st_ino": temporary.stat().st_ino,
                     "created_exclusively_by": "tempfile.mkdtemp"}
        save(destination / "temp-ownership.json", ownership)
        child = [sys.executable, "-u", "-B",
                 ".ai/workflow-reliability/evidence/c2b-state-independent-r2-stage.py",
                 str(temporary), str(destination)]
        inventory = []
    else:
        previous = json.loads((preflight / "result.json").read_bytes())
        assert previous["returncode"] == 0 and previous["pins_unchanged"]
        assert json.loads((preflight / "receipt-stage.json").read_bytes())["status"] == "pass"
        assert before == json.loads((preflight / "pins-before.json").read_bytes())
        ownership = json.loads((preflight / "temp-ownership.json").read_bytes())
        temporary = Path(ownership["path"])
        assert (temporary.stat().st_dev, temporary.stat().st_ino) == (ownership["st_dev"], ownership["st_ino"])
        inventory = list(old["flatten"](unittest.defaultTestLoader.discover(
            str(ROOT / "scripts/tests"), pattern="test_workflow*.py")))
        assert len(inventory) == 100 and len(set(inventory)) == 100
        assert not any("_FailedTest" in name for name in inventory)
        child = [sys.executable, "-u", "-B", "-m", "unittest", "discover",
                 "-s", "scripts/tests", "-p", "test_workflow*.py", "-v"]
    assert not temporary.is_symlink() and not temporary.is_junction() and not list(temporary.iterdir())
    save(destination / "inventory.json", inventory)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TEMP=str(temporary),
               TMP=str(temporary), TMPDIR=str(temporary))
    command = [sys.executable, "-u", "-B", "scripts/run.py", "--idle", "120", "--max", "600", "--", *child]
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            bufsize=0, env=env,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
    save(destination / "launch.json", {
        "command": command, "cwd": str(ROOT), "pid": proc.pid, "capture_pid": os.getpid(),
        "time": time.time(), "cap_bytes": CAP, "temp": str(temporary), "path": env["PATH"],
        "environment_overrides": {key: env[key] for key in
                                  ("PYTHONDONTWRITEBYTECODE", "TEMP", "TMP", "TMPDIR")},
        "encoding": "raw merged CLI bytes; CLI UTF-8 replacement/line forwarding",
    })
    total, chunks, first, last, live, overflow = 0, 0, None, None, False, False
    with (destination / "combined.log").open("xb") as log:
        while chunk := proc.stdout.read(4096):
            now = time.monotonic() - started
            if first is None:
                first, live = now, proc.poll() is None
            last, chunks = now, chunks + 1
            if total + len(chunk) > CAP:
                overflow = True
                old["_kill_tree"](proc)
                break
            total += len(chunk)
            log.write(chunk)
            log.flush()
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
    proc.stdout.close()
    rc = proc.wait()
    after = pins()
    save(destination / "pins-after.json", after)
    remains = [p.relative_to(temporary).as_posix() for p in temporary.rglob("*")]
    removed = False
    if phase == "workflow" and rc == 0 and not overflow and before == after and not remains:
        assert (temporary.stat().st_dev, temporary.stat().st_ino) == (ownership["st_dev"], ownership["st_ino"])
        temporary.rmdir()  # Exact owned empty root only; never recursive or OS-temp parent.
        removed = True
    result = {
        "returncode": rc, "overflow": overflow, "elapsed_seconds": time.monotonic() - started,
        "captured_bytes": total, "chunks_forwarded": chunks,
        "first_chunk_seconds": first, "last_chunk_seconds": last,
        "first_chunk_before_direct_exit": live, "runner_pid": proc.pid,
        "direct_runner_reaped": proc.returncode is not None, "temp": str(temporary),
        "owned_temp_remaining": remains, "owned_empty_root_removed": removed,
        "pins_unchanged": before == after, "inventory_count": len(inventory),
        "limits": "No descendant-death, old cleanup, authenticated actor or recovery claim.",
    }
    save(destination / "result.json", result)
    print(json.dumps(result), flush=True)
    return rc or (3 if overflow or before != after or remains else 0)


if __name__ == "__main__":
    sys.exit(main())
