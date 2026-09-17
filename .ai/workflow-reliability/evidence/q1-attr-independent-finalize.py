"""Fresh bounded result reconciliation, not an implementation or code review."""
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "q1-attr-independent-"
sys.path.insert(0, str(ROOT / "scripts"))
import measure
from run import run_capture


def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def read(label):
    return json.loads((HERE / (PREFIX + label + ".json")).read_bytes())


def save(label, value):
    with (HERE / (PREFIX + label + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


preflight = read("preflight-2")
pins = dict(preflight["inputs"])
changed = {}
results, inventory, raw_streams, archives = {}, [], {}, []
all_temps = set()
for label, count in (("a", 28), ("w", 83), ("e", 10)):
    result, command, inv = read(label + "-result"), read(label + "-command"), read(label + "-inventory")
    assert result["tests"] == len(inv["tests"]) == count
    assert result["failures"] == result["errors"] == result["skipped"] == 0, result
    assert command["exit_code"] == 0 and result["unchanged"] and not result["changed"], result
    assert not result["owned_remaining"], result["owned_remaining"]
    before, after = read(label + "-inputs-before"), read(label + "-inputs-after")
    assert before == after
    for path, ref in before.items():
        if path in pins:
            assert pins[path] == ref, path
        pins[path] = ref
    observed = read(label + "-observed-imports")
    for name, record in observed.items():
        assert record["path"] in before, (label, "late import", name, record)
        assert before[record["path"]] == {k: record[k] for k in ("bytes", "sha256")}, (label, name)
    assert not read(label + "-late-inputs")
    texts = {}
    for stream, raw in command["raw"].items():
        path = Path(raw["path"])
        assert digest(path) == {key: raw[key] for key in ("bytes", "sha256")}
        raw_streams[str(path)] = digest(path)
        texts[stream] = path.read_bytes().decode("utf-8")
    actual_ids = re.findall(r"^test_\w+ \(([^)]+)\) \.\.\.", texts["stderr"], re.MULTILINE)
    assert actual_ids == inv["tests"], (label, actual_ids, inv["tests"])
    duration = re.search(r"Ran %d tests in ([\d.]+)s\s+OK\s*$" % count, texts["stderr"])
    assert duration, label
    inventory += actual_ids
    results[label] = {"result": result, "command": command, "inventory": inv,
                      "unittest_seconds": float(duration[1]), "input_count": len(before),
                      "observed_modules": len(observed)}
    all_temps.update(result["owned_temps"])
    for record in read(label + "-fixtures"):
        path = Path(record["archive"])
        with zipfile.ZipFile(path) as archive:
            assert set(archive.namelist()) == set(record["files"])
            for name, ref in record["files"].items():
                data = archive.read(name)
                assert {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} == ref
        archives.append({"path": str(path), **digest(path), "members": len(record["files"]),
                         "source": record["source"]})
assert len(inventory) == len(set(inventory)) == 121

# Compare optional C1 in-suite observations to all three surrounding snapshots.
c1_imports = read("w-imports")
for name, record in c1_imports.items():
    assert pins[record["path"]]["sha256"] == record["sha256"], (name, record)
for module in ("workflow_gate", "workflow_state", "measure", "measure_graph", "probe", "mutate", "evidence", "run"):
    record = read("w-observed-imports")[module]
    assert Path(record["path"]) == ROOT / "scripts" / (module + ".py")
    assert digest(Path(record["path"]))["sha256"] == record["sha256"]

stdout = Path(results["a"]["command"]["raw"]["stdout"]["path"]).read_text(encoding="utf-8")
drivers = [json.loads(line) for line in stdout.splitlines() if line.startswith('{"driver":')]
assert {record["driver"] for record in drivers} == {"unset", "unspecified"} and len(drivers) == 2
for record in drivers:
    assert record["isolated_sentinel_absent"] and record["positive_sentinel"] == "executed"
    assert set(record["errors"]) == {"materializer", "validator"}
    for error in record["errors"].values():
        assert "unsupported attribute filter=" + record["driver"] in error
        assert "ambiguous present declaration" in error
scales = re.findall(r"C1 R3 scale: increments=(\d+) evaluators=(\d+) proof_misses=(\d+) unique=(\d+)",
                    Path(results["w"]["command"]["raw"]["stdout"]["path"]).read_text(encoding="utf-8"))
assert scales == [("3", "4", "87", "87"), ("5", "6", "195", "195"), ("8", "9", "432", "432")]

# Independently prove the only production delta against the actual archived bytes.
owner = json.loads((HERE / "q1-attr-final-freeze.json").read_bytes())
old_ref = owner["predecessor_source"]
with zipfile.ZipFile(old_ref["archive"]) as archive:
    old_bytes = archive.read(old_ref["member"])
assert hashlib.sha256(old_bytes).hexdigest() == "753fca9e03c7961dab474fcc3536a53c1b48b55dd0382c9cf3cd4ec248e2d859"
current = (ROOT / "scripts/measure.py").read_bytes()
assert hashlib.sha256(current).hexdigest() == "5d6f15a95de50d932953023508dd12ae2f470fd073af91d409ca5a948838b084"
delta = "".join(difflib.unified_diff(old_bytes.decode().splitlines(keepends=True),
                                   current.decode().splitlines(keepends=True),
                                   fromfile="reviewed/measure.py", tofile="corrected/measure.py"))
# The owner's text-mode Windows writer expanded every LF, including the LF in
# source CRLF lines. Verify that exact artifact encoding, not normalized source.
assert delta.replace("\n", "\r\n").encode() == (HERE / "q1-attr-measure.diff").read_bytes()
assert delta.count("\n@@ ") == 1

binding = measure.baseline_binding()
qualification = json.loads((HERE / "q1-attr-qualification.json").read_bytes())
assert binding == qualification["binding"] and qualification["binding_unchanged"]
for command in qualification["commands"]:
    for raw in command["raw"].values():
        assert digest(Path(raw["path"])) == {k: raw[k] for k in ("bytes", "sha256")}
assert len(binding["git"]["bundled_dlls"]) == 69
core = Path(binding["git"]["path"])
assert pins[str(core)]["sha256"] == binding["git"]["sha256"]
for name, sha in binding["git"]["bundled_dlls"].items():
    assert pins[str(core.parent / name)]["sha256"] == sha

git = []
for executable, args in (
        ("git", ["rev-parse", "HEAD"]),
        ("git", ["branch", "--show-current"]),
        ("git", ["diff", "--cached", "--name-only"]),
        ("git", ["diff", "--check", "--", "scripts/measure.py",
                 "scripts/tests/test_measure_q1_attr_independent.py"]),
        (str(core), ["version", "--build-options"])):
    argv = [executable, "--no-pager", *args]
    code, out, err = run_capture(argv, cwd=ROOT, idle=30, max_total=90)
    git.append({"argv": argv, "cwd": str(ROOT), "idle": 30, "max": 90, "exit_code": code,
                "stdout_text": out, "stderr_text": err})
    assert code == 0, git[-1]
assert git[0]["stdout_text"].strip() == "0b7e1a1f6fd1f807bd254886e2877d605596d96d"
assert git[1]["stdout_text"].strip() == "shbs-microsoft-workflow-app-verification"
assert not git[2]["stdout_text"]
assert "git version 2.53.0.windows.4" in git[-1]["stdout_text"]

for path, ref in {**preflight["protected"], **pins}.items():
    if not Path(path).is_file() or digest(Path(path)) != ref:
        changed[path] = ref
remaining = sorted(p for p in all_temps if Path(p).exists())
for path in (Path(__file__), HERE / (PREFIX + "capture.py"),
             ROOT / "scripts/tests/test_measure_q1_attr_independent.py"):
    compile(path.read_bytes(), str(path), "exec")
    assert all(not line.endswith((" ", "\t")) for line in path.read_text().splitlines())
result = {"status": "VERIFIED-WITH-LIMITATIONS" if not (changed or remaining) else "BLOCKED-FRESHNESS",
          "results": results, "frozen_inputs": pins, "protected": preflight["protected"],
          "changed": changed, "remaining_temps": remaining, "temporary_count": len(all_temps),
          "raw_streams": raw_streams, "fixture_archives": archives, "literal_driver_observations": drivers,
          "c1_in_suite_import_count": len(c1_imports), "c1_scale_observations": scales,
          "git": git, "binding": binding,
          "qualification": {"path": str(HERE / "q1-attr-qualification.json"),
                            **digest(HERE / "q1-attr-qualification.json"),
                            "raw_commands_rehashed_not_reexecuted": len(qualification["commands"])},
          "verified_production_diff": {"path": str(HERE / "q1-attr-measure.diff"),
                                      **digest(HERE / "q1-attr-measure.diff"), "hunks": 1},
          "prior_74_reexecuted": False, "test_counts": {"focused": 28, "workflow": 83, "evidence": 10},
          "limits": ["Qualified Windows Git package and managed CPython only; not OS-loader closure.",
                     "C1 fixtures are protocol data, not real root quality receipts or live dispatch.",
                     "No Q4 execution, complete root quality, combined candidate-tree proof or publication.",
                     "Separate narrowed code re-review and parent preservation disposition remain due."]}
save("freeze", result)
assert not changed and not remaining, (changed, remaining)
print(json.dumps({"status": result["status"], "counts": result["test_counts"],
                  "pins": len(pins), "protected": len(preflight["protected"]),
                  "unique": len(set(pins) | set(preflight["protected"])),
                  "c1_imports": len(c1_imports), "archives": len(archives),
                  "temps": len(all_temps), "raw_streams": len(raw_streams)}, indent=2))
