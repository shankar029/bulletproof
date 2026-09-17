"""Freeze only the final narrow attribute-gate correction and its real evidence."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import measure
from run import run_capture


def ref(path):
    data = Path(path).read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def read(label):
    return json.loads((HERE / ("q1-attr-" + label + ".json")).read_bytes())


before = read("before")
source = ROOT / "scripts/measure.py"
protected = {name: value for name, value in before.items() if name != str(source)}
changed = [name for name, value in protected.items() if not Path(name).is_file() or ref(name) != value]
assert not changed, changed
old = None
archive_ref = None
for archive_path in (HERE / "q1-resumed-correction-fixtures-q1-recovery-integration").glob("*.zip"):
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            if name.endswith("/controller/measure.py"):
                data = archive.read(name)
                if hashlib.sha256(data).hexdigest() == before[str(source)]["sha256"]:
                    old, archive_ref = data, {"archive": str(archive_path), "member": name}
                    break
    if old is not None:
        break
assert old is not None, "No matching frozen predecessor bytes"
diff = "".join(difflib.unified_diff(old.decode().splitlines(True),
                                   source.read_bytes().decode().splitlines(True),
                                   fromfile="reviewed/measure.py", tofile="corrected/measure.py"))
with (HERE / "q1-attr-measure.diff").open("x", encoding="utf-8") as stream:
    stream.write(diff)

results, pins, temporary_paths = {}, {}, set()
for label in ("red", "green", "macro", "eol", "unsupported", "probe", "cli"):
    result, command = read(label + "-result"), read(label + "-command")
    assert result["unchanged"] and not result["changed"]
    assert result["errors"] == result["skipped"] == 0
    if label == "red":
        assert result["tests"] == 4 and result["failures"] == 6 and command["exit_code"] == 1
    else:
        assert result["tests"] > 0 and result["failures"] == 0 and command["exit_code"] == 0
        observed = {**read(label + "-inputs-before"), **read(label + "-late-inputs")}
        assert read(label + "-inputs-before") == read(label + "-inputs-after")
        for name, value in observed.items():
            assert ref(name) == value, name
            pins[name] = value
    results[label] = {**result, "command": command}
    for raw in command["raw"].values():
        assert ref(raw["path"]) == {key: raw[key] for key in ("sha256", "bytes")}
        text = Path(raw["path"]).read_text(encoding="utf-8")
        temporary_paths.update(re.findall(r"\[owned-temp\] ([^\r\n]+)", text))
qualification = read("qualification")
assert qualification["binding_unchanged"] and qualification["no_checkout_files"]
assert measure.baseline_binding() == qualification["binding"]
for command in qualification["commands"]:
    for raw in command["raw"].values():
        assert ref(raw["path"]) == {key: raw[key] for key in ("sha256", "bytes")}
remaining = sorted(name for name in temporary_paths if Path(name).exists())
assert not remaining, remaining
for path in (source, ROOT / "scripts/tests/test_measure_q1_attr.py"):
    compile(path.read_bytes(), str(path), "exec")
git = []
for args in (["rev-parse", "HEAD"], ["branch", "--show-current"], ["diff", "--cached", "--name-only"]):
    code, out, error = run_capture(["git", *args], cwd=ROOT, idle=30, max_total=90)
    assert code == 0, (args, code, error)
    git.append({"argv": ["git", *args], "exit": code, "stdout": out, "stderr": error})
assert not git[-1]["stdout"], "Index is not empty"
for path in [*HERE.glob("q1-attr-*"), ROOT / "scripts/tests/test_measure_q1_attr.py"]:
    if path.is_file():
        pins[str(path)] = ref(path)
result = {"status": "LOCAL_GREEN_AWAITING_NARROW_INDEPENDENT_REPLAY_AND_REVIEW",
          "results": results, "git": git, "frozen_inputs": pins,
          "source": {str(path): ref(path) for path in
                     (source, ROOT / "scripts/measure_graph.py", ROOT / "scripts/probe.py",
                      ROOT / "scripts/tests/test_measure_q1_attr.py")},
          "protected_count": len(protected), "protected_changed": changed,
          "predecessor_source": archive_ref, "production_diff": ref(HERE / "q1-attr-measure.diff"),
          "recorded_temporary_count": len(temporary_paths), "remaining_temporary_paths": remaining,
          "qualification": ref(HERE / "q1-attr-qualification.json"),
          "limits": ["Ambiguous present state-marker values fail explicitly, including -filter.",
                     "No execution escape or false overall green was demonstrated.",
                     "Prior independent 74-test and C1 93-test results were not rerun or reclassified.",
                     "No full Q1/root-quality rerun, shared-state changes, commits, publication or nested agents."]}
with (HERE / "q1-attr-final-freeze.json").open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2)
print(json.dumps({"status": result["status"], "source": result["source"],
                  "tests": {label: {key: value[key] for key in ("tests", "failures", "errors")}
                            for label, value in results.items()},
                  "frozen_count": len(pins), "protected_count": len(protected),
                  "recorded_temporary_count": len(temporary_paths), "git": git}, indent=2))
