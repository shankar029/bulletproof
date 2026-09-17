"""Finalize only bounded C2a pins and read-only Git observations."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("c2a_capture", HERE / "c2a-capture.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
from run import run_capture

GIT = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"
BASE = "5dabb4ca27a440ad370fbcb1be1739ed52e38ab7"


def git(*args):
    argv = [GIT, "--no-pager", *args]
    result = run_capture(argv, cwd=str(ROOT), idle=30, max_total=60)
    commands.append({"argv": argv, "cwd": str(ROOT), "idle": 30, "max_total": 60,
                     "exit": result[0], "stdout": result[1], "stderr": result[2]})
    if result[0] != 0:
        raise RuntimeError(commands[-1])
    return result[1]


def functions(source):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}


if __name__ == "__main__":
    dest = HERE / "c2a-freeze.json"
    if dest.exists():
        raise SystemExit("refusing to overwrite freeze")
    commands = []
    head = git("rev-parse", "HEAD").strip()
    assert head == BASE, head
    branch = git("branch", "--show-current").strip()
    status = git("status", "--short", "--untracked-files=all")
    git("remote", "-v")
    original = git("show", f"{BASE}:scripts/run.py")
    current = (ROOT / "scripts/run.py").read_text(encoding="utf-8")
    before_functions, after_functions = functions(original), functions(current)
    unchanged = {name: before_functions[name] == after_functions[name]
                 for name in ("_kill_tree", "_popen", "main")}
    assert all(unchanged.values()), unchanged
    git("diff", "--", "scripts/run.py", "scripts/tests/test_run.py")
    pins = capture.pins()
    pins[str(Path(GIT))] = hashlib.sha256(Path(GIT).read_bytes()).hexdigest()
    for path in HERE.glob("c2a-*"):
        if path.is_file():
            pins[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    green = json.loads((HERE / "c2a-green1.json").read_bytes())
    changed = {path: {"green": value, "now": pins.get(path)}
               for path, value in green["after"].items() if pins.get(path) != value}
    assert set(changed) == {str(HERE / "c2a-capture.py")}, changed
    callers = json.loads((HERE / "c2a-callers1.json").read_bytes())
    assert all(pins[path] == value for path, value in callers["after"].items())
    record = {"head": head, "branch": branch, "status": status, "pins": pins,
              "commands": commands, "unchanged_function_asts": unchanged,
              "green1_disclosed_helper_delta": changed,
              "callers1_pins_unchanged": True,
              "limits": "bounded snapshot only; parent state/report excluded; no rerun or independent acceptance"}
    dest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"head": head, "branch": branch, "status": status,
                      "pin_count": len(pins), "unchanged_functions": unchanged,
                      "green1_disclosed_helper_delta": changed,
                      "callers1_pins_unchanged": True}, indent=2))
