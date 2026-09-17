"""Reconcile captured r3 outcomes, effective modes, source pins and archives."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_bytes())


def identity(path):
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def main():
    preflight = load(HERE / "q1-independent-r3-preflight.json")
    original_changes = [name for name, ref in preflight["preserved_originals"].items()
                        if identity(Path(name)) != ref]
    current = {name: identity(Path(name)) for name in preflight["expected"]}
    freeze_changes = [name for name, ref in preflight["expected"].items() if current[name] != ref]
    runs, pins = {}, {}
    for label in ("q1", "legacy"):
        prefix = str(HERE / ("q1-independent-r3-" + label))
        before = load(Path(prefix + "-inputs-before.json"))
        after = load(Path(prefix + "-inputs-after.json"))
        result = load(Path(prefix + "-result.json"))
        late = load(Path(prefix + "-late-inputs.json"))
        command = load(Path(prefix + "-command.json"))
        changed = [name for name, ref in before.items() if identity(Path(name)) != ref]
        for name, ref in before.items():
            if name in pins and pins[name] != ref:
                raise ValueError("Input differed between replay runs: " + name)
            pins[name] = ref
        runs[label] = {"result": result, "command": command, "pinned_count": len(before),
                       "before_equals_after": before == after, "changed_since_run": changed, "late": late}
    mode_lines = (HERE / "q1-independent-r3-q1.stdout.bin").read_bytes().decode("utf-8").splitlines()
    modes = [json.loads(line) for line in mode_lines if line.startswith('{"case":')]
    indexed = {item["case"]: item for item in modes}
    expected_modes = {"default", "env-on", "env-off", "cli-off", "cli-on",
                      "last-off", "last-on", "ignored-off", "ignored-on", "isolated-off"}
    if len(modes) != 10 or set(indexed) != expected_modes:
        raise ValueError("Incomplete/duplicate actual mode inventory")
    for item in modes:
        observation = item["observation"]
        if item["exit_code"] != 0 or observation["digest"] != observation["after"]:
            raise ValueError("Native mode failed or effective identity changed after raw-setting edits")
        if observation["table"] != observation["table_after"]:
            raise ValueError("Effective table changed after raw-setting edits")
        active = observation["table"].get("__phello__") is not None
        if (observation["native_origin"] == "frozen") != active or observation["local"] == active:
            raise ValueError("Native import does not match the runtime table")
    on = indexed["env-on"]["observation"]
    off = indexed["env-off"]["observation"]
    if on["digest"] == off["digest"] or not set(off["table"]) < set(on["table"]):
        raise ValueError("Effective mode identity not distinguished")
    for name in ("cli-on", "last-on"):
        if indexed[name]["observation"]["digest"] != on["digest"]:
            raise ValueError("On-mode precedence identity mismatch")
    for name in ("cli-off", "last-off"):
        if indexed[name]["observation"]["digest"] != off["digest"]:
            raise ValueError("Off-mode precedence identity mismatch")
    for name in ("ignored-off", "ignored-on", "isolated-off"):
        if indexed[name]["observation"]["digest"] != indexed["default"]["observation"]["digest"]:
            raise ValueError("Ignored environment changed effective identity")
    archives, raw = {}, {}
    command_paths = list(HERE.glob("q1-independent-r3-*-command.json"))
    for directory in HERE.glob("q1-independent-r3-fixtures-*"):
        command_paths.extend(directory.glob("*-command-*.json"))
        for manifest_path in directory.glob("*-fixture-*.json"):
            manifest = load(manifest_path)
            path = directory / manifest["archive"]
            with zipfile.ZipFile(path) as archive:
                actual = {name: {"sha256": hashlib.sha256(archive.read(name)).hexdigest(),
                                 "bytes": len(archive.read(name))} for name in archive.namelist()}
            archives[str(path)] = {**identity(path), "files": len(actual),
                                   "mapping_matches": actual == manifest["files"]}
    for path in command_paths:
        command = load(path)
        streams = {}
        for key, ref in command["raw"].items():
            filename = ref.get("path") or path.parent / (path.stem.replace("-command-", "-") + "." + key + ".bin")
            observed = identity(Path(filename))
            streams[key] = {"path": str(filename), **observed,
                            "matches": observed == {field: ref[field] for field in ("sha256", "bytes")}}
        raw[str(path)] = {"exit_code": command["exit_code"], "streams": streams}
    intact = (not original_changes and not freeze_changes
              and all(value["mapping_matches"] for value in archives.values())
              and all(stream["matches"] for value in raw.values() for stream in value["streams"].values()))
    passed = intact and all(
        value["command"]["exit_code"] == 0 and value["result"]["tests"] > 0
        and not any(value["result"][field] for field in ("failures", "errors", "skipped"))
        and value["before_equals_after"] and not value["changed_since_run"] and not value["late"]
        for value in runs.values())
    record = {
        "verdict": "VERIFIED-WITH-LIMITATIONS" if passed else "NOT-VERIFIED",
        "scope": "Q1 functional correction verification only; separate review and Q2+ remain due",
        "runtime": sys.version, "executable": sys.executable, "runs": runs,
        "unique_pinned_inputs": len(pins), "frozen_inputs": pins,
        "owner_freeze": {"expected": preflight["expected"], "final": current, "changed": freeze_changes},
        "original_count": len(preflight["preserved_originals"]), "original_changes": original_changes,
        "actual_modes": modes, "raw_commands": raw, "fixture_archives": archives,
    }
    with (HERE / "q1-independent-r3-final-freeze.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps({
        "verdict": record["verdict"], "runs": {label: {key: value[key] for key in (
            "result", "pinned_count", "before_equals_after", "changed_since_run", "late")}
            for label, value in runs.items()},
        "unique_pinned_inputs": len(pins), "freeze_changes": freeze_changes,
        "original_count": record["original_count"], "original_changes": original_changes,
        "mode_count": len(modes), "on_census": len(on["table"]), "off_census": len(off["table"]),
        "on_digest": on["digest"], "off_digest": off["digest"],
        "raw_streams": sum(len(value["streams"]) for value in raw.values()),
        "archives": len(archives), "archive_files": sum(value["files"] for value in archives.values()),
        "evidence_intact": intact,
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
