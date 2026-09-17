"""Capture bounded local commands without replacing previous evidence."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.tag.isalnum() or not args.command:
        parser.error("Expected unique alphanumeric tag and command argv")
    command = args.command[1:] if args.command[0] == "--" else args.command
    destination = Path(__file__).with_name("c2b-state-" + args.tag)
    destination.mkdir()
    names = sorted(
        [p.relative_to(ROOT).as_posix() for p in (ROOT / "scripts").glob("*.py")] +
        [p.relative_to(ROOT).as_posix() for p in (ROOT / "scripts/tests").glob("test_workflow*.py")] +
        ["scripts/tests/helpers.py", "scripts/tests/workflow_fixtures.py",
         "scripts/tests/test_evidence.py",
         ".ai/workflow-reliability/c2-recovery-contract.json",
         ".ai/workflow-reliability/c2-recovery-design.html",
         ".ai/workflow-reliability/evidence/c2-recovery-design-review-r2.md",
         ".ai/workflow-reliability/evidence/c2-recovery-r2-disposition.md",
         ".ai/workflow-reliability/design-contracts.json",
         ".ai/workflow-reliability/guard-resolution-contract.json",
         ".ai/workflow-reliability/evidence/c2b-state-capture.py"])
    paths = {name: ROOT / name for name in names}
    paths["runtime:python"] = Path(sys.executable)
    paths["runtime:git"] = Path(shutil_which_git())

    def hashes():
        return {name: hashlib.sha256(path.read_bytes()).hexdigest()
                for name, path in paths.items()}

    before = hashes()
    for name in names:
        copy = destination / "inputs" / name
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(paths[name].read_bytes())
    started = datetime.now(timezone.utc).isoformat()
    launch = {"argv": command, "cwd": str(ROOT), "capture_argv": sys.orig_argv,
              "started": started, "idle": 120, "max": 600, "before": before}
    (destination / "launch.json").write_text(
        json.dumps(launch, indent=2) + "\n", encoding="utf-8", newline="\n")

    def observe(event):
        with (destination / "lifecycle.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(event) + "\n")
            stream.flush()
        print(json.dumps({"child_observation": event}), flush=True)

    rc, stdout, stderr = run_capture(command, cwd=str(ROOT), idle=120, max_total=600, observe=observe)
    (destination / "stdout.txt").write_text(stdout, encoding="utf-8", newline="\n")
    (destination / "stderr.txt").write_text(stderr, encoding="utf-8", newline="\n")
    after = hashes()
    result = {
        "argv": command, "cwd": str(ROOT), "capture_argv": sys.orig_argv,
        "idle": 120, "max": 600, "started": started,
        "finished": datetime.now(timezone.utc).isoformat(), "exit": rc,
        "python": sys.version, "python_executable": sys.executable,
        "git_executable": str(paths["runtime:git"]),
        "PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE"),
        "before": before, "after": after, "unchanged": before == after,
        "stdout_sha256": hashlib.sha256((destination / "stdout.txt").read_bytes()).hexdigest(),
        "stderr_sha256": hashlib.sha256((destination / "stderr.txt").read_bytes()).hexdigest(),
    }
    (destination / "result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(stdout, end="")
    print(stderr, end="", file=sys.stderr)
    print(json.dumps({"record": str(destination / "result.json"), "exit": rc,
                      "pins": len(before), "unchanged": before == after}))
    return rc if before == after else 2


def shutil_which_git():
    import shutil
    path = shutil.which("git")
    if path is None:
        raise RuntimeError("Qualified Git missing from PATH")
    return path


if __name__ == "__main__":
    raise SystemExit(main())
