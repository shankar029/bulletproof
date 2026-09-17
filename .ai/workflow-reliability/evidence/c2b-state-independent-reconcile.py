"""Read-only reconciliation of the stopped run; never executes tests."""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys


root = Path.cwd()
evidence = root / ".ai/workflow-reliability/evidence"
capture = runpy.run_path(str(evidence / "c2b-state-independent-stream.py"))
current = capture["pins"]()
git = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"


def read_git(*args):
    return subprocess.check_output(
        [sys.executable, "-u", "-B", "scripts/run.py", "--idle", "120", "--max", "600",
         "--", git, "--no-pager", *args], cwd=root)


head = read_git("rev-parse", "HEAD").decode().strip()
assert head == "d971634219a633cc4401fb7dcba9685e672978aa"
old = ast.parse(read_git("show", "HEAD:scripts/workflow_state.py"))
new = ast.parse((root / "scripts/workflow_state.py").read_bytes())
old_defs = {n.name: n for n in old.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
new_defs = {n.name: n for n in new.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
unchanged = [name for name in old_defs if name not in ("_load_design", "bind_inputs")]
assert all(ast.dump(old_defs[n]) == ast.dump(new_defs[n]) for n in unchanged)
original_body = old_defs["_load_design"].body
extracted = new_defs["validate_design_binding"].body
# Compare from validate_design(design) through return; workspace/live-read
# preparation is the approved delta, not part of the extracted policy.
def policy(nodes):
    start = next(i for i, n in enumerate(nodes)
                 if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                 and isinstance(n.value.func, ast.Name) and n.value.func.id == "validate_design")
    return [ast.dump(n) for n in nodes[start:]]


assert policy(original_body) == policy(extracted)


def materialization(function):
    start = next(i for i, n in enumerate(function.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "snapshots" for t in n.targets))
    return [ast.dump(n) for n in function.body[start:]]


assert materialization(old_defs["bind_inputs"]) == materialization(new_defs["bind_inputs"])
summaries = {}
all_ids, all_passes = set(), set()
for tag in ("transport01", "workflow01"):
    directory = evidence / ("c2b-state-independent-" + tag)
    inventory = json.loads((directory / "inventory.json").read_bytes())
    text = (directory / "combined.log").read_text(encoding="utf-8")
    passed = re.findall(r"^test_\w+ \(([^)]+)\) \.\.\. ok$", text, re.M)
    error_ids = re.findall(r"^ERROR: test_\w+ \(([^)]+)\)", text, re.M)
    exceptions = re.findall(r"^(\w+(?:Error|Exception)): (.*)$", text, re.M)
    summary = re.search(r"^Ran (\d+) tests in ([\d.]+)s$", text, re.M)
    assert summary and int(summary[1]) == len(inventory)
    assert not all_ids.intersection(inventory)
    all_ids.update(inventory)
    all_passes.update(passed)
    assert len(set(passed)) == len(passed) and set(passed) <= set(inventory)
    assert set(passed).isdisjoint(error_ids)
    assert set(passed) | set(error_ids) == set(inventory)
    before = json.loads((directory / "pins-before.json").read_bytes())
    after = json.loads((directory / "pins-after.json").read_bytes())
    assert before == after == current
    summaries[tag] = {
        "methods": len(inventory), "positive_methods": len(passed),
        "positive_by_module": dict(Counter(p.split(".")[0] for p in passed)),
        "errored_methods": len(set(error_ids)), "error_records": len(error_ids),
        "exceptions": dict(Counter(e[0] for e in exceptions)),
        "failed_assertion_records": len(re.findall(r"^FAIL: ", text, re.M)),
        "skipped_records": len(re.findall(r"\.\.\. skipped ", text)),
        "unittest_seconds": float(summary[2]),
        "positive_ids": passed, "errored_ids": sorted(set(error_ids)),
        "result": json.loads((directory / "result.json").read_bytes()),
    }
    if exceptions:
        paths = [ast.literal_eval(message.split(": ", 1)[1]) for _, message in exceptions
                 if message.startswith("[Errno 2] No such file or directory: ")]
        summaries[tag]["failing_path_lengths"] = dict(Counter(map(len, paths)))
        summaries[tag]["first_failing_path"] = paths[0]
        summaries[tag]["all_errors_are_missing_receipt_stage"] = all(
            "\\receipts\\." in path and path.endswith(".stage") for path in paths)

inputs = {}
for name, module in sorted(sys.modules.copy().items()):
    file = getattr(module, "__file__", None)
    if file:
        path = Path(file).resolve()
        if path.is_relative_to(root / "scripts") and path.is_file():
            inputs[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
report = {
    "verdict": "BLOCKED", "head": head, "pins": current, "pin_count": len(current),
    "all_29_before_after_final_match": True,
    "original_validation_policy_ast_equal": True,
    "original_materialization_ast_equal": True,
    "other_unchanged_definitions": len(unchanged),
    "runtime_imports_in_reconciliation_only": inputs,
    "workflow_cli_absent": not (root / "scripts/workflow.py").exists(),
    "batches": summaries, "distinct_attempted_methods": len(all_ids),
    "distinct_positive_methods": len(all_passes),
    "cleanup_limit": "Both owned temp roots empty; direct CLI runner processes reaped. No whole-tree claim.",
    "historical_cleanup": "First capture identity absent, old PID43520 later absent per owner; whole trees unverified.",
}
report["artifacts"] = {
    p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in evidence.glob("c2b-state-independent-*") if p.is_file()
}
for tag in ("transport01", "workflow01"):
    report["artifacts"].update({
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (evidence / ("c2b-state-independent-" + tag)).rglob("*") if p.is_file()
    })
capture["save"](evidence / "c2b-state-independent-reconciliation.json", report)
print(json.dumps({k: report[k] for k in (
    "verdict", "head", "pin_count", "distinct_attempted_methods", "distinct_positive_methods",
    "original_validation_policy_ast_equal", "original_materialization_ast_equal",
    "other_unchanged_definitions")}, indent=2))
for tag, summary in summaries.items():
    print(tag, json.dumps({k: v for k, v in summary.items()
                           if k not in ("positive_ids", "errored_ids", "result")}, indent=2))
