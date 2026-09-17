"""Reconcile this independent replay without overwriting any earlier evidence."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(path):
    return json.loads(path.read_bytes())


def identity(path):
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def main():
    preflight = load(HERE / "q1-independent-r2-preflight.json")
    originals = preflight["preserved_originals"]
    original_changes = [name for name, value in originals.items() if identity(Path(name)) != value]
    expected = preflight["expected"]
    current = {name: identity(Path(name)) for name in expected}
    freeze_changes = [name for name in expected if expected[name] != current[name]]
    pins, runs = {}, {}
    for label in ("q1", "legacy", "boundaries"):
        prefix = HERE / ("q1-independent-r2-" + label)
        before = load(Path(str(prefix) + "-inputs-before.json"))
        after = load(Path(str(prefix) + "-inputs-after.json"))
        result = load(Path(str(prefix) + "-result.json"))
        late = load(Path(str(prefix) + "-late-inputs.json"))
        command = load(Path(str(prefix) + "-command.json"))
        changed = [name for name, value in before.items() if identity(Path(name)) != value]
        for name, value in before.items():
            if name in pins and pins[name] != value:
                raise ValueError("Different pinned input across replay runs: " + name)
            pins[name] = value
        runs[label] = {"result": result, "command": command, "pinned_count": len(before),
                       "before_equals_after": before == after, "changed_since_run": changed, "late": late}
    artifacts, raw = {}, {}
    command_paths = list(HERE.glob("q1-independent-r2-*-command.json"))
    for directory in HERE.glob("q1-independent-r2-fixtures-*"):
        command_paths.extend(directory.glob("*-command-*.json"))
        for path in directory.glob("*-fixture-*.json"):
            manifest = load(path)
            archive_path = directory / manifest["archive"]
            with zipfile.ZipFile(archive_path) as archive:
                actual = {name: {"sha256": hashlib.sha256(archive.read(name)).hexdigest(),
                                 "bytes": len(archive.read(name))} for name in archive.namelist()}
            artifacts[str(archive_path)] = {
                **identity(archive_path), "files": len(actual), "mapping_matches": actual == manifest["files"]}
    for path in command_paths:
        command = load(path)
        refs = {}
        for stream, ref in command["raw"].items():
            filename = ref.get("path")
            if filename is None:
                filename = path.parent / (path.stem.replace("-command-", "-") + "." + stream + ".bin")
            actual = identity(Path(filename))
            refs[stream] = {"path": str(filename), **actual,
                            "matches": actual == {key: ref[key] for key in ("sha256", "bytes")}}
        raw[str(path)] = {"exit_code": command["exit_code"], "streams": refs}
    record = {
        "verdict": "NOT-VERIFIED", "runtime": sys.version, "executable": sys.executable,
        "runs": runs, "frozen_inputs": pins, "unique_pinned_inputs": len(pins),
        "owner_freeze": {"expected": expected, "final": current, "changed": freeze_changes},
        "preserved_originals_count": len(originals), "preserved_originals_changed": original_changes,
        "raw_commands": raw, "fixture_archives": artifacts,
        "limits": "Relevant captured inputs only; no unrelated C1/parent or OS-wide stability claim.",
    }
    with (HERE / "q1-independent-r2-final-freeze.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps({
        "runs": {label: {key: value[key] for key in (
            "result", "pinned_count", "before_equals_after", "changed_since_run", "late")}
                 for label, value in runs.items()},
        "unique_pinned_inputs": len(pins), "owner_freeze_changes": freeze_changes,
        "original_count": len(originals), "original_changes": original_changes,
        "raw_streams": sum(len(value["streams"]) for value in raw.values()),
        "raw_match": all(stream["matches"] for value in raw.values() for stream in value["streams"].values()),
        "archives": len(artifacts), "archive_files": sum(value["files"] for value in artifacts.values()),
        "archive_match": all(value["mapping_matches"] for value in artifacts.values()),
    }, indent=2))


if __name__ == "__main__":
    main()
