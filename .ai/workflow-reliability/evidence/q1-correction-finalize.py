"""Verify raw captures, preserved originals and final pinned input identity."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_bytes())


def identity(path):
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


labels = sys.argv[1:]
if not labels:
    raise ValueError("Supply exact final test labels")
pins, runs = {}, {}
for label in labels:
    before = read(HERE / ("q1-correction-" + label + "-inputs-before.json"))
    after = read(HERE / ("q1-correction-" + label + "-inputs-after.json"))
    result = read(HERE / ("q1-correction-" + label + "-result.json"))
    assert before == after and result["unchanged"], label + ": pinned inputs changed during tests"
    assert not result["failures"] and not result["errors"] and not result["skipped"], label
    for name, expected in before.items():
        assert identity(Path(name)) == expected, "Changed since final test: " + name
        assert name not in pins or pins[name] == expected, "Different final run input: " + name
        pins[name] = expected
    late = read(HERE / ("q1-correction-" + label + "-late-inputs.json"))
    for name, expected in late.items():
        assert identity(Path(name)) == expected, "Changed late input: " + name
    runs[label] = {"result": result, "pinned_count": len(before), "late_inputs": late}

preserved = read(HERE / "q1-correction-preserved-before.json")
for name, expected in preserved.items():
    assert identity(Path(name)) == expected, "Original verifier input changed: " + name
raws = {}
for path in HERE.glob("q1-correction-*-command.json"):
    command = read(path)
    for stream, ref in command["raw"].items():
        actual = identity(Path(ref["path"]))
        assert actual == {"sha256": ref["sha256"], "bytes": ref["bytes"]}, str(path)
    raws[path.name] = command

record = {"runs": runs, "frozen_inputs": pins, "preserved_originals": preserved, "raw_commands": raws,
          "scope": "Observed targeted runtime inputs, not OS-wide or whole-repository isolation",
          "status": "OWNER_CORRECTION_TESTED_PENDING_ORIGINAL_VERIFIER_REPLAY_AND_REVIEW"}
with (HERE / "q1-correction-final-freeze.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, indent=2)
print(json.dumps({"runs": runs, "frozen_count": len(pins), "preserved_count": len(preserved)}, indent=2))
for name, ref in pins.items():
    if name.endswith(("scripts\\measure.py", "scripts\\measure_graph.py", "scripts\\probe.py",
                      "scripts\\tests\\test_measure_inventory.py", "scripts\\tests\\test_measure_graph.py",
                      "scripts\\tests\\test_measure_q1_verification.py")):
        print(name, ref["sha256"])
