"""Actual receipt-stage layout preflight; observes but never replaces file I/O."""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


root = Path.cwd()
sys.path.insert(0, str(root / "scripts/tests"))
sys.path.insert(0, str(root / "scripts"))
from workflow_fixtures import WorkflowFixture
from workflow_state import read_json
import workflow_gate


owned, destination = map(Path, sys.argv[1:])
assert Path(tempfile.gettempdir()).resolve() == owned.resolve()
assert owned.is_dir() and not list(owned.iterdir())
stages = []


def observe(event, args):
    if event == "os.rename":
        source, target = Path(args[0]), Path(args[1])
        if source.suffix == ".stage" and target.parent.name == "receipts":
            assert source.is_relative_to(owned)
            actual = source.read_bytes()
            observation = {
                "source": str(source), "destination": str(target),
                "source_length": len(str(source)), "destination_length": len(str(target)),
                "staged_bytes": len(actual), "sha256": hashlib.sha256(actual).hexdigest(),
                "phase": "actual-stage-exists-before-replace",
            }
            stages.append(observation)
            print(json.dumps(observation), flush=True)


sys.addaudithook(observe)
fixture = WorkflowFixture()
try:
    assert fixture.root.is_relative_to(owned)
    fixture.work("A-work")
    reference = fixture.receipt("A-test")
    path = fixture.workspace / ("evidence/receipts/" + reference["id"] + ".json")
    content = path.read_bytes()
    assert reference["sha256"] == hashlib.sha256(content).hexdigest()
    assert len(stages) == 1 and stages[0]["sha256"] == reference["sha256"]
    assert Path(stages[0]["destination"]) == path
    assert not Path(stages[0]["source"]).exists()
    document = read_json(path)
    assert document["id"] == reference["id"]
    _, _, resolved = fixture.load()
    assert resolved.receipts[reference["id"]].status == "valid"
    result = {
        "status": "pass", "temp": str(owned), "fixture": str(fixture.root),
        "stage_observations": stages, "receipt": reference,
        "actual_receipt_resolved": "valid",
        "limits": "Real filesystem receipt staging; synthetic protocol proof/identities, not actor or recovery proof.",
    }
finally:
    fixture.close()
result["owned_temp_remaining"] = [str(p) for p in owned.iterdir()]
assert not result["owned_temp_remaining"]
result["observed_repository_imports"] = {
    Path(module.__file__).resolve().relative_to(root).as_posix():
        hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
    for module in list(sys.modules.values())
    if getattr(module, "__file__", None)
    and Path(module.__file__).resolve().is_relative_to(root / "scripts")
}
with (destination / "receipt-stage.json").open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps(result), flush=True)
