"""Check actual final captures, preserve history, and freeze this bounded handoff."""
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "q1-resumed-correction-"
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture
import measure
import measure_graph
import probe
import mutate


def hashes(paths):
    return {str(path): {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "bytes": path.stat().st_size}
            for path in sorted(set(paths)) if path.is_file()}


def read(label):
    return json.loads((HERE / (PREFIX + label + ".json")).read_bytes())


initial = read("initial-pins")
owned_source = {str(ROOT / "scripts" / name) for name in ("measure.py", "measure_graph.py", "probe.py")}
protected = {name: ref for name, ref in initial.items() if name not in owned_source}
changed = [name for name, ref in protected.items() if hashes([Path(name)]).get(name) != ref]
assert not changed, changed
labels = ["q1-recovery-graph-inventory", "q1-recovery-integration", "r1", "f3",
          "probe-core-final", "targeted-final"]
pins, results, temporary_paths = {}, {}, set()
for label in labels:
    result, command = read(label + "-result"), read(label + "-command")
    assert result["tests"] > 0 and result["failures"] == result["skipped"] == 0
    if label == "q1-recovery-integration":
        assert result["tests"] == 27 and result["errors"] == 2 and command["exit_code"] == 1
        stderr = Path(command["raw"]["stderr"]["path"]).read_text(encoding="utf-8")
        error_names = re.findall(r"^ERROR: (\S+)", stderr, re.MULTILINE)
        assert error_names == ["test_public_source_root_aliases_rejected",
                               "test_effective_frozen_mode_from_environment_has_distinct_tool_binding"]
        assert stderr.count("FileNotFoundError:") == 2
    else:
        assert result["errors"] == 0 and command["exit_code"] == 0
    assert result["unchanged"] and not result["changed"]
    before, after = read(label + "-inputs-before"), read(label + "-inputs-after")
    assert before == after
    for name, ref in {**before, **read(label + "-late-inputs")}.items():
        if name in pins:
            assert pins[name] == ref, name
        pins[name] = ref
    results[label] = {**result, "seconds": command["seconds"], "argv": command["argv"]}
    for raw in command["raw"].values():
        data = Path(raw["path"]).read_bytes()
        temporary_paths.update(re.findall(r"\[owned-temp\] ([^\r\n]+)", data.decode("utf-8", "replace")))
        assert hashes([Path(raw["path"])])[raw["path"]] == {key: raw[key] for key in ("sha256", "bytes")}
assert all(hashes([Path(name)]).get(name) == ref for name, ref in pins.items())

# Show that the two batches are exhaustive and disjoint without rerunning tests.
all_q1 = set((ROOT / "scripts/tests").glob("test_measure_*.py"))
one = set((ROOT / "scripts/tests").glob("test_measure_[gi]*.py"))
two = set((ROOT / "scripts/tests").glob("test_measure_q1*.py"))
assert one | two == all_q1 and not one & two
for path in [*(ROOT / "scripts").glob("measure*.py"), ROOT / "scripts/probe.py",
             ROOT / "scripts/tests/test_measure_q1_resumed.py"]:
    compile(path.read_bytes(), str(path), "exec")

qualification_checks = []
for path in (HERE / "q1-review-correction-qualification.json",
             HERE / "q1-resumed-correction-core-qualification.json"):
    qualification = json.loads(path.read_bytes())
    assert qualification["status"] == "PASS"
    for command in qualification["commands"]:
        for raw in command["raw"].values():
            assert hashes([Path(raw["path"])])[raw["path"]] == {key: raw[key] for key in ("sha256", "bytes")}
    qualification_checks.append(str(path))

git = []
for args in (["rev-parse", "HEAD"], ["branch", "--show-current"],
             ["diff", "--cached", "--name-only"], ["diff", "--check", "--",
              "scripts/measure.py", "scripts/measure_graph.py", "scripts/probe.py",
              "scripts/tests/test_measure_q1_resumed.py"]):
    code, out, err = run_capture(["git", *args], cwd=ROOT, idle=30, max_total=90)
    git.append({"argv": ["git", *args], "exit": code, "stdout": out, "stderr": err})
    assert code == 0, git[-1]
assert not git[2]["stdout"], "Unexpected staged changes"
assert git[1]["stdout"].strip() not in {"main", "master"}
extras = [Path(__file__), *[ROOT / "scripts" / name for name in
          ("measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py", "mutate.py")]]
extras += [HERE.parent / name for name in ("state.md", "measurement-enablement-contracts.json",
                                          "measurement-enablement.html", "baseline-materialization-contract.json")]
extras += list(HERE.glob(PREFIX + "*"))
pins.update(hashes(extras))
remaining_temporary = sorted(path for path in temporary_paths if Path(path).exists())
assert not remaining_temporary, remaining_temporary
result = {
    "status": "LOCAL_CASE_COVERAGE_COMPLETE_WITH_CAPTURE_LIMITS_AWAITING_INDEPENDENT_REPLAY",
    "results": results, "git": git, "frozen_inputs": pins,
    "source": hashes([Path(name) for name in owned_source]),
    "protected_count": len(protected), "protected_changed": changed,
    "qualified_materializer": measure.baseline_binding(), "qualification_checks": qualification_checks,
    "q1_file_partition": {"graph_inventory": sorted(path.name for path in one),
                          "integration_review": sorted(path.name for path in two)},
    "observed_execution_modules": {module.__name__: str(Path(module.__file__).resolve())
                                   for module in (measure, measure_graph, probe, mutate)},
    "recorded_temporary_count": len(temporary_paths), "recorded_temporary_remaining": remaining_temporary,
    "case_reconciliation": {
        "q1_distinct_passing_cases": 52, "legacy_probe_passing_cases": 19,
        "not_a_single_green_aggregate": True,
        "integration_capture_errors": 2,
        "same_source_short_tag_replays": ["r1", "f3"],
        "duplicate_targeted_runs_not_added": True},
    "limits": ["Prior aggregate run exited 124 without final raw flush/result; see recovery record.",
               "No claim of cleanup for unknown interrupted-run temporary paths.",
               "Qualified Git core/application DLL set only; not an OS loader closure.",
               "No POSIX execution proof, Q4 controller execution, root quality or overall acceptance.",
               "Five-file controller copy is not complete actual probe execution; mutate is separately pinned.",
               "No shared-state/C1/C2/Q2 edits, installations, commits or publication."]}
with (HERE / (PREFIX + "final-freeze.json")).open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2)
print(json.dumps({key: value for key, value in result.items()
                  if key not in {"frozen_inputs", "qualified_materializer"}}, indent=2))
