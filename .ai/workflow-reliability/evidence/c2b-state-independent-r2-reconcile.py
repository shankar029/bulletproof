"""Reconcile only existing r2 execution artifacts; no test execution."""

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
helper = runpy.run_path(str(evidence / "c2b-state-independent-r2-stream.py"))
pins = helper["pins"]()
prior = json.loads((evidence / "c2b-state-independent-reconciliation.json").read_bytes())
for name, digest in prior["pins"].items():
    assert pins[name] == digest
for phase in ("preflight", "workflow"):
    directory = evidence / ("c2b-state-independent-r2-" + phase + "01")
    assert json.loads((directory / "pins-before.json").read_bytes()) == pins
    assert json.loads((directory / "pins-after.json").read_bytes()) == pins
    result = json.loads((directory / "result.json").read_bytes())
    assert result["returncode"] == 0 and not result["overflow"]
    assert result["direct_runner_reaped"] and not result["owned_temp_remaining"]
    assert result["pins_unchanged"] and result["first_chunk_before_direct_exit"]
preflight = evidence / "c2b-state-independent-r2-preflight01"
stage = json.loads((preflight / "receipt-stage.json").read_bytes())
assert stage["status"] == "pass" and stage["actual_receipt_resolved"] == "valid"
assert stage["stage_observations"][0]["source_length"] == 145
for name, digest in stage["observed_repository_imports"].items():
    assert pins[name] == digest
owned = json.loads((preflight / "temp-ownership.json").read_bytes())["path"]
assert not Path(owned).exists()

batches, accepted_ids = {}, set()
for tag in ("c2b-state-independent-transport01", "c2b-state-independent-r2-workflow01"):
    directory = evidence / tag
    inventory = json.loads((directory / "inventory.json").read_bytes())
    text = (directory / "combined.log").read_text(encoding="utf-8")
    records = re.findall(
        r"^test_\w+ \(([^)]+)\) \.\.\.(.*?)(?=^test_|^-{10}|\Z)",
        text, re.M | re.S)
    # The scale test emits real output between its name and final standalone
    # "ok". Account for it rather than guessing success from the suite count.
    positive = [name for name, body in records if body.strip().endswith("ok")]
    assert len(records) == len(positive) == len(inventory)
    assert len(set(positive)) == len(positive) and set(positive) == set(inventory)
    assert not accepted_ids.intersection(positive)
    accepted_ids.update(positive)
    summary = re.search(r"^Ran (\d+) tests in ([\d.]+)s$", text, re.M)
    assert summary and int(summary[1]) == len(inventory)
    assert re.search(r"^OK$", text, re.M)
    assert not re.search(r"^ERROR:|^FAIL:|^FAILED|\.\.\. skipped |\[run\] (idle|max)-timeout", text, re.M)
    for name, digest in json.loads((directory / "pins-before.json").read_bytes()).items():
        assert pins[name] == digest
    result = json.loads((directory / "result.json").read_bytes())
    assert result["returncode"] == 0
    batches[tag] = {
        "method_count": len(positive), "positive_ids": positive,
        "positive_by_module": dict(Counter(p.split(".")[0] for p in positive)),
        "unittest_seconds": float(summary[2]), "result": result,
        "zero_failures_errors_skips_timeouts": True,
    }

git = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"
def read_git(*args):
    return subprocess.check_output(
        [sys.executable, "-u", "-B", "scripts/run.py", "--idle", "120", "--max", "600",
         "--", git, "--no-pager", *args], cwd=root)


head = read_git("rev-parse", "HEAD").decode().strip()
assert head == prior["head"]
original = ast.parse(read_git("show", "HEAD:scripts/workflow_state.py"))
current = ast.parse((root / "scripts/workflow_state.py").read_bytes())
definitions = lambda tree: {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
before, after = definitions(original), definitions(current)
others = set(before) - {"_load_design", "bind_inputs"}
assert all(ast.dump(before[n]) == ast.dump(after[n]) for n in others)
def tail(nodes, name):
    for index, node in enumerate(nodes):
        if (name == "validate_design" and isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name) and node.value.func.id == name):
            return [ast.dump(n) for n in nodes[index:]]
        if (name == "snapshots" and isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)):
            return [ast.dump(n) for n in nodes[index:]]
    raise AssertionError("Missing policy/materialization anchor")


assert tail(before["_load_design"].body, "validate_design") == tail(after["validate_design_binding"].body, "validate_design")
assert tail(before["bind_inputs"].body, "snapshots") == tail(after["bind_inputs"].body, "snapshots")
report = {
    "verdict": "VERIFIED", "scope": "Approved C2b-S state seams only; separate review/CLI/recovery excluded",
    "head": head, "pins": pins, "pin_count": len(pins),
    "pins_before_after_final_identical": True, "prior_29_pins_still_match": True,
    "original_evidence_including_failed_run_preserved": True,
    "accepted_batches": batches, "distinct_accepted_methods": len(accepted_ids),
    "preflight_counted_as_unittest": False,
    "prior_failed_workflow_methods_added_to_total": 0,
    "receipt_stage_preflight": stage,
    "temp_ownership": json.loads((preflight / "temp-ownership.json").read_bytes()),
    "exact_owned_root_absent_after_successful_empty_rmdir": True,
    "validation_policy_ast_equal": True, "materialization_ast_equal": True,
    "other_original_definitions_unchanged": len(others),
    "workflow_cli_absent": not (root / "scripts/workflow.py").exists(),
    "import_scope": "Nine actual repository imports observed in receipt preflight, pinned eight script modules plus fixture. Not a complete dynamic-import/DLL attestation of workflow subprocess.",
    "historical_cleanup": "First buffered capture identity and whole old trees remain UNKNOWN; PID43520 absence is only prior owner evidence.",
}
artifacts = [p for tag in ("preflight", "workflow")
             for p in (evidence / ("c2b-state-independent-r2-" + tag + "01")).rglob("*") if p.is_file()]
artifacts += list(evidence.glob("c2b-state-independent-r2-*.py"))
report["artifact_hashes"] = {
    p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts
}
helper["save"](evidence / "c2b-state-independent-r2-reconciliation.json", report)
print(json.dumps({k: report[k] for k in (
    "verdict", "head", "pin_count", "distinct_accepted_methods", "validation_policy_ast_equal",
    "materialization_ast_equal", "other_original_definitions_unchanged",
    "original_evidence_including_failed_run_preserved",
    "exact_owned_root_absent_after_successful_empty_rmdir")}, indent=2))
for tag, batch in batches.items():
    print(tag, batch["method_count"], batch["positive_by_module"])
