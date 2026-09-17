"""Final round-2 input, raw-log and original-verifier preservation check."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture


def read(path):
    return json.loads(path.read_bytes())


def identity(path):
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


pins, runs = {}, {}
for label in ("q1-final", "legacy-final"):
    before = read(HERE / ("q1-correction-r2-" + label + "-inputs-before.json"))
    after = read(HERE / ("q1-correction-r2-" + label + "-inputs-after.json"))
    result = read(HERE / ("q1-correction-r2-" + label + "-result.json"))
    late = read(HERE / ("q1-correction-r2-" + label + "-late-inputs.json"))
    assert before == after and result["unchanged"], label
    assert not result["failures"] and not result["errors"] and not result["skipped"], result
    assert result["tests"] == {"q1-final": 42, "legacy-final": 19}[label], result
    assert read(HERE / ("q1-correction-r2-" + label + "-command.json"))["exit_code"] == 0, label
    for name, expected in before.items():
        assert identity(Path(name)) == expected, "Changed after final test: " + name
        assert name not in pins or pins[name] == expected, "Final runs used different inputs: " + name
        pins[name] = expected
    for name, expected in late.items():
        assert identity(Path(name)) == expected, "Changed late dependency: " + name
    runs[label] = {"result": result, "pinned_count": len(before), "late_inputs": late}

preserved = read(HERE / "q1-correction-r2-preserved-before.json")
for name, expected in preserved.items():
    assert identity(Path(name)) == expected, "Original verifier input changed: " + name

commands = {}
for path in HERE.glob("q1-correction-r2-*-command.json"):
    value = read(path)
    for ref in value["raw"].values():
        assert identity(Path(ref["path"])) == {"sha256": ref["sha256"], "bytes": ref["bytes"]}, str(path)
    commands[path.name] = value

checked = {}
for relative in ("scripts/measure.py", "scripts/measure_graph.py", "scripts/probe.py",
                 "scripts/tests/test_measure_inventory.py", "scripts/tests/test_measure_graph.py",
                 "scripts/tests/test_measure_q1_integration.py",
                 ".ai/workflow-reliability/evidence/q1-correction-r2-capture.py",
                 ".ai/workflow-reliability/evidence/q1-correction-r2-finalize.py"):
    path = ROOT / relative
    source = path.read_bytes()
    compile(source, str(path), "exec")
    assert all(line == line.rstrip() for line in source.decode("utf-8").splitlines()), relative
    checked[relative] = identity(path)

argv = ["git", "rev-parse", "HEAD"]
code, head, error = run_capture(argv, cwd=ROOT, idle=30, max_total=90)
assert code == 0, error
record = {
    "status": "OWNER_TESTED_PENDING_ORIGINAL_VERIFIER_REPLAY_AND_SEPARATE_REVIEW",
    "git_context": {"argv": argv, "cwd": str(ROOT), "head": head.strip(), "exit_code": code},
    "runs": runs, "frozen_inputs": pins, "preserved_originals": preserved, "commands": commands,
    "compile_and_whitespace": checked,
    "finalizer_argv": [sys.executable, "-B", *sys.argv],
    "limits": "Observed targeted dependencies, not an OS-wide/whole-repository freeze or release proof"}
with (HERE / "q1-correction-r2-final-freeze.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, indent=2)
print(json.dumps({"runs": runs, "frozen_count": len(pins), "preserved_count": len(preserved),
                  "head": head.strip()}, indent=2))
for relative in ("scripts/measure_graph.py", "scripts/measure.py", "scripts/probe.py",
                 "scripts/tests/test_measure_inventory.py", "scripts/tests/test_measure_graph.py",
                 "scripts/tests/test_measure_q1_integration.py", "scripts/tests/test_measure_q1_verification.py",
                 "scripts/tests/test_measure_q1_verification_r2.py"):
    print(relative, identity(ROOT / relative)["sha256"])
