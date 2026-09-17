"""Index observed proof and incomplete inventory without manufacturing batch success."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("joint_resume", HERE / "joint-cli-binding-resume.py")
resume = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resume)
capture = resume.capture
OUT = capture.OUT
batches, tests = capture.load_tests()
before = json.loads((OUT / "before-pins.json").read_bytes())
summary, passed = {}, set()
imports, executable_paths, observed_pids = set(), set(), set()
for batch in batches:
    result_path = OUT / batch / "result.json"
    result = json.loads(result_path.read_bytes()) if result_path.exists() else None
    ids = result["passed"] if result else resume.completed(batch)
    if batch == "support":
        recovered = json.loads((OUT / "support-resume/result.json").read_bytes())
        ids += recovered["passed"]
    ids = sorted(set(ids))
    passed.update(ids)
    summary[batch] = {
        "discovered": batches[batch], "passed": ids,
        "not_passed": sorted(set(batches[batch]) - set(ids)),
        "original_result_exists": result is not None,
        "original_exit": json.loads((OUT / batch / "exit.json").read_bytes()),
        "seconds": result["seconds"] if result else None,
        "pass_basis": "result.json, plus support-resume where applicable" if result else
                      "Completed method lines in preserved interrupted stdout; not a completed batch",
    }
    if result:
        imports.update(result.get("runtime_imports", []))
    log = OUT / batch / "capture-invocations.jsonl"
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            argv = row["argv"]
            if isinstance(argv, list) and argv and Path(argv[0]).is_absolute() and Path(argv[0]).is_file():
                executable_paths.add(str(Path(argv[0]).resolve()))
            if row["kind"] == "actual-spawn":
                observed_pids.add(row["pid"])
                observed_pids.add(row["parent_pid"])
unknown = sorted((imports | executable_paths) - set(before))
capture.save(OUT / "supplemental-observed-inputs.json", {
    "limitation": "These actual observed files were not in the initial pin set; current-only hashes are not retroactive start pins.",
    "current_only": {name: {"sha256": hashlib.sha256(Path(name).read_bytes()).hexdigest(),
                          "bytes": Path(name).stat().st_size} for name in unknown},
    "observed_executables": sorted(executable_paths),
    "observed_imports": sorted(imports),
    "known_pids": sorted(observed_pids),
})
all_ids = {identity for ids in batches.values() for identity in ids}
timeout = "test_measure_graph.GraphTests.test_graph_receipt_summary_and_artifact_corruption_rejected"
capture.save(OUT / "inventory-reconciliation.json", {
    "batches": summary, "unique_discovered": len(all_ids), "unique_passed": len(passed),
    "missing": sorted(all_ids - passed), "named_symlink_environment_block": capture.BLOCKED,
    "twice_idle_blocked_method": timeout,
    "never_started": sorted(all_ids - passed - {capture.BLOCKED, timeout}),
    "support_discovery_correction": "One _FailedTest placeholder replaced by three real test IDs; placeholder is not a method.",
    "native": {"entries_passed": 13, "cli_replay_entries": 5, "reporter_regressions": 8,
               "additional_unique_python_behaviors": 0},
    "joint_verdict": "NOT-VERIFIED: selected Q1 regression proof incomplete",
    "production_assertion_failure_observed": False,
})
records = {}
for path in sorted(OUT.rglob("*")):
    if path.is_file():
        data = path.read_bytes()
        records[path.relative_to(OUT).as_posix()] = {
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
capture.save(OUT / "raw-record-index.json", records)
print(json.dumps({
    "discovered": len(all_ids), "passed": len(passed), "missing": len(all_ids - passed),
    "q1_completed": summary["q1"]["passed"], "never_started": len(all_ids - passed - {capture.BLOCKED, timeout}),
    "current_only_input_count": len(unknown), "current_only_inputs": unknown,
    "raw_records_indexed": len(records)}, indent=2))
