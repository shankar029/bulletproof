"""Read-only reconciliation of Q1 inputs/raw archives; writes only its own manifest."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def record(path):
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def main():
    runs = {}
    pins = {}
    for label in ("existing-q1", "legacy-probe", "adversarial", "adversarial-r2", "adversarial-r3"):
        before = json.loads((OUT / f"q1-independent-{label}-inputs-before.json").read_bytes())
        after = json.loads((OUT / f"q1-independent-{label}-inputs-after.json").read_bytes())
        late = json.loads((OUT / f"q1-independent-{label}-late-inputs.json").read_bytes())
        command = json.loads((OUT / f"q1-independent-{label}-command.json").read_bytes())
        current = {name: record(Path(name)) for name in before}
        runs[label] = {
            "result": json.loads((OUT / f"q1-independent-{label}-result.json").read_bytes()),
            "pinned_files": len(before), "late_files": len(late), "before_equals_after": before == after,
            "changed_since_run": [name for name in before if before[name] != current[name]],
            "raw_hashes_match": all(record(Path(raw["path"])) == {k: raw[k] for k in ("sha256", "bytes")}
                                    for raw in command["raw"].values()),
            "command": command,
        }
        pins.update(before)
        pins.update(late)
    frozen = {}
    for name, before in pins.items():
        path = Path(name)
        if path.name in {"test_measure_q1_verification.py", "q1-independent-capture.py"}:
            continue
        frozen[name] = {"before": before, "final": record(path)}
    archives = {}
    for manifest_path in sorted(OUT.glob("q1-independent-*-fixture-r3.json")):
        manifest = json.loads(manifest_path.read_bytes())
        path = OUT / manifest["archive"]
        with zipfile.ZipFile(path) as archive:
            actual = {name: {"sha256": hashlib.sha256(archive.read(name)).hexdigest(),
                             "bytes": len(archive.read(name))} for name in archive.namelist()}
        archives[path.name] = {"manifest": manifest_path.name, **record(path),
                               "file_count": len(actual), "mapping_matches": actual == manifest["files"]}
    report = {
        "verdict": "NOT-VERIFIED", "runtime": sys.version, "executable": sys.executable,
        "runs": runs, "frozen_input_count": len(frozen),
        "frozen_inputs_unchanged": all(item["before"] == item["final"] for item in frozen.values()),
        "frozen_inputs": frozen, "archives": archives,
        "current_verifier": {str(ROOT / name): record(ROOT / name) for name in (
            "scripts/tests/test_measure_q1_verification.py",
            ".ai/workflow-reliability/evidence/q1-independent-capture.py")},
        "limits": [
            "Only explicitly pinned measurement/test/runtime inputs, not a whole-tree stability claim.",
            "The first runs discovered _ast_unparse lazily; it is pre-pinned in final r3.",
            "Verifier test edits between completed r1/r2/r3 runs are intentional and preserved.",
            "No external analyzer, full repository, changed-line mutation, Q2+, review or release acceptance.",
        ],
    }
    (OUT / "q1-independent-final-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in {"frozen_inputs", "runs"}}, indent=2))
    for label, result in runs.items():
        print(label, json.dumps({key: result[key] for key in
              ("result", "pinned_files", "late_files", "changed_since_run", "raw_hashes_match")}))


if __name__ == "__main__":
    main()
