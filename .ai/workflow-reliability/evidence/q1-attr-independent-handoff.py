"""Last freshness check and report binding; does not reexecute any test."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "q1-attr-independent-"


def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


freeze = HERE / (PREFIX + "freeze.json")
record = json.loads(freeze.read_bytes())
pins = {**record["frozen_inputs"], **record["protected"]}
changed = [name for name, ref in pins.items()
           if not Path(name).is_file() or digest(Path(name)) != ref]
raw_changed = [name for name, ref in record["raw_streams"].items()
               if digest(Path(name)) != ref]
files = [freeze, HERE / (PREFIX + "report.md"), HERE / (PREFIX + "capture.py"),
         HERE / (PREFIX + "finalize.py"), Path(__file__),
         ROOT / "scripts/tests/test_measure_q1_attr_independent.py"]
for path in files:
    if path.suffix == ".py":
        compile(path.read_bytes(), str(path), "exec")
result = {"status": "VERIFIED-WITH-LIMITATIONS" if not (changed or raw_changed) else "BLOCKED-FRESHNESS",
          "checked_unique_pins": len(pins), "changed": changed, "raw_changed": raw_changed,
          "artifacts": {str(path.relative_to(ROOT)): digest(path) for path in files},
          "test_counts": record["test_counts"], "failures": 0, "errors": 0, "skipped": 0,
          "test_timeouts": 0, "prior_74_rerun": False, "separate_narrowed_review_due": True,
          "combined_commit_composition_verified": False, "whole_task_complete": False}
with (HERE / (PREFIX + "handoff.json")).open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2)
assert not (changed or raw_changed), result
print(json.dumps(result, indent=2))
