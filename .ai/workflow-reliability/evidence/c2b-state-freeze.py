"""Read-only source/record reconciliation; does not execute tests or review code."""

import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = EVIDENCE / "c2b-state-freeze.json"
    if output.exists():
        raise SystemExit("Refusing to overwrite prior freeze")
    baseline = EVIDENCE / "c2b-state-red01/inputs/scripts/workflow_state.py"
    current = ROOT / "scripts/workflow_state.py"
    old = {n.name: n for n in ast.parse(baseline.read_bytes()).body
           if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    new = {n.name: n for n in ast.parse(current.read_bytes()).body
           if isinstance(n, (ast.FunctionDef, ast.ClassDef))}

    def normalized(nodes):
        return [ast.dump(node, include_attributes=False) for node in nodes]

    assert normalized(old["_load_design"].body[2:]) == normalized(new["validate_design_binding"].body[6:])
    untouched = set(old) - {"_load_design", "bind_inputs"}
    assert all(ast.dump(old[name]) == ast.dump(new[name]) for name in untouched)
    assert set(new) - set(old) == {"validate_design_binding"}
    old_loop = next(i for i, n in enumerate(old["bind_inputs"].body)
                    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                    and n.targets[0].id == "snapshots")
    new_loop = next(i for i, n in enumerate(new["bind_inputs"].body)
                    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                    and n.targets[0].id == "snapshots")
    assert normalized(old["bind_inputs"].body[old_loop:]) == normalized(new["bind_inputs"].body[new_loop:])
    batches = {}
    for tag in ("seams01", "evidence01", "state02", "core02", "chronology02"):
        directory = EVIDENCE / ("c2b-state-" + tag)
        record = json.loads((directory / "result.json").read_bytes())
        stderr = (directory / "stderr.txt").read_text(encoding="utf-8")
        count = int(re.search(r"Ran (\d+) tests? in ", stderr)[1])
        assert record["exit"] == 0 and record["unchanged"] and stderr.rstrip().endswith("OK")
        batches[tag] = {"count": count, "result_sha256": digest(directory / "result.json"),
                        "stdout_sha256": digest(directory / "stdout.txt"),
                        "stderr_sha256": digest(directory / "stderr.txt")}
    latest = json.loads((EVIDENCE / "c2b-state-state02/result.json").read_bytes())
    current_pins = {}
    for name, expected in latest["after"].items():
        path = (Path(latest["python_executable"]) if name == "runtime:python" else
                Path(latest["git_executable"]) if name == "runtime:git" else ROOT / name)
        observed = digest(path)
        assert observed == expected, name
        current_pins[name] = observed
    for tag in ("workflow01", "gate02"):
        assert not (EVIDENCE / ("c2b-state-" + tag) / "result.json").exists()
    artifacts = [EVIDENCE / "c2b-state-handoff.md", EVIDENCE / "c2b-state-capture.py",
                 EVIDENCE / "c2b-state-workflow01-timeout.json", EVIDENCE / "c2b-state-gate02-timeout.json",
                 Path(__file__)]
    for tag in ("red01", "seams01", "workflow01", "evidence01",
                "state02", "gate02", "core02", "chronology02"):
        artifacts.extend(p for p in (EVIDENCE / ("c2b-state-" + tag)).rglob("*") if p.is_file())
    result = {
        "outcome": "local implementation frozen; gate regression blocked by second capture timeout",
        "generated": datetime.now(timezone.utc).isoformat(),
        "new_methods": 16, "distinct_successful_methods": sum(b["count"] for b in batches.values()),
        "successful_batches": batches, "failed_attempts": ["red01: two missing-API errors",
                                                          "workflow01: outer idle124", "gate02: outer idle124"],
        "original_validation_ast_preserved": True,
        "snapshot_loop_ast_preserved": True,
        "other_original_definitions_unchanged": len(untouched),
        "current_pins": current_pins,
        "artifact_hashes": {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(artifacts)},
        "limits": [
            "Structural extraction check supplements tests; not independent review.",
            "Successful local batches are not independent verification.",
            "No full gate-regression count established; no CLI, recovery or quality proof.",
            "Bounded source/runtime pins, not exhaustive import/host attestation.",
            "Timeout cleanup lacks whole-tree-death and complete temporary-fixture-removal proof.",
        ],
    }
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"file": str(output), "sha256": digest(output),
                      "passing_methods": result["distinct_successful_methods"],
                      "current_pins": len(current_pins)}))


if __name__ == "__main__":
    main()
