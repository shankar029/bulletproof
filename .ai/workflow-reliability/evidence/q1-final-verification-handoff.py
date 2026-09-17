"""Last read-only freshness check plus an exclusive-create handoff manifest."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "q1-final-verification-"


def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


freeze = HERE / (PREFIX + "final-freeze.json")
record = json.loads(freeze.read_bytes())
preflight = json.loads((HERE / (PREFIX + "preflight-2.json")).read_bytes())
checks = {**record["frozen_inputs"], **preflight["protected"]}
changed = [name for name, ref in checks.items()
           if not Path(name).is_file() or digest(Path(name)) != ref]
files = [freeze, HERE / (PREFIX + "report.md"), HERE / (PREFIX + "execution-notes.md"),
         HERE / (PREFIX + "capture.py"), HERE / (PREFIX + "finalize.py"), Path(__file__),
         ROOT / "scripts/tests/test_measure_q1_final_verification.py"]
for path in files:
    if path.suffix == ".py":
        compile(path.read_bytes(), str(path), "exec")
        assert all(not line.endswith((" ", "\t")) for line in path.read_text().splitlines())
result = {"status": "VERIFIED-WITH-LIMITATIONS" if not changed else "BLOCKED-FRESHNESS",
          "checked_unique_pins": len(checks), "changed": changed,
          "artifacts": {str(path.relative_to(ROOT)): digest(path) for path in files},
          "tests": {"original_q1": 52, "new_independent": 3, "legacy_probe": 19,
                    "distinct": 74, "failures": 0, "errors": 0, "skipped": 0, "timeouts": 0},
          "separate_code_rereview_required": True, "whole_task_complete": False}
with (HERE / (PREFIX + "handoff.json")).open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2)
assert not changed, changed
print(json.dumps(result, indent=2))
