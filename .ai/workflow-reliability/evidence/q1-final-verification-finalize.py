"""Independently reconcile current inventories, stream bytes, archives and pins."""
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "q1-final-verification-"
sys.path.insert(0, str(ROOT / "scripts"))
import measure
from run import run_capture


def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def read(label):
    return json.loads((HERE / (PREFIX + label + ".json")).read_bytes())


def save(label, data):
    with (HERE / (PREFIX + label + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)


def git_observation(label):
    commands = []
    binding = measure.baseline_binding()
    for executable, args in [
        ("git", ["rev-parse", "HEAD"]),
        ("git", ["branch", "--show-current"]),
        ("git", ["remote", "-v"]),
        ("git", ["diff", "--cached", "--name-only"]),
        ("git", ["diff", "--check", "--", "scripts/measure.py", "scripts/measure_graph.py",
                 "scripts/probe.py", "scripts/tests/test_measure_q1_final_verification.py"]),
        (binding["git"]["path"], ["version", "--build-options"]),
    ]:
        argv = [executable, "--no-pager", *args]
        code, out, err = run_capture(argv, cwd=ROOT, idle=30, max_total=90)
        commands.append({"argv": argv, "cwd": str(ROOT), "idle": 30, "max": 90,
                         "exit_code": code, "stdout_text": out, "stderr_text": err})
        assert code == 0, commands[-1]
    result = {"binding": binding, "commands": commands,
              "note": "Git text is run_capture-decoded; test raw streams are separately byte-preserved."}
    save(label, result)
    assert commands[0]["stdout_text"].strip() == "0b7e1a1f6fd1f807bd254886e2877d605596d96d"
    assert commands[1]["stdout_text"].strip() == "shbs-microsoft-workflow-app-verification"
    assert not commands[3]["stdout_text"]
    assert len(binding["git"]["bundled_dlls"]) == 69
    assert "2.53.0.windows.4" in commands[-1]["stdout_text"]
    print(json.dumps({"git": commands[:2], "dlls": len(binding["git"]["bundled_dlls"])}))
    return result


def finalize():
    start = read("preflight-2")
    pins = {}
    for source in (start["owner_inputs"], start["inputs"]):
        pins.update(source)
    # This status file is explicitly parent-owned, not a measurement runtime input.
    parent_status = str(ROOT / ".ai/workflow-reliability/state.md")
    pins.pop(parent_status, None)
    protected_changed = [name for name, ref in start["protected"].items()
                         if not Path(name).is_file() or digest(Path(name)) != ref]
    results, all_tests, all_temps, all_archives, raw_files = {}, [], set(), [], {}
    late = {}
    for label, expected in (("g", 25), ("i", 30), ("p", 19)):
        result, command = read(label + "-result"), read(label + "-command")
        inv = read(label + "-inventory")
        assert result["tests"] == inv["count"] == expected, (label, result, inv)
        assert result["failures"] == result["errors"] == result["skipped"] == 0, result
        assert result["unchanged"] and not result["changed"]
        assert command["exit_code"] == 0, command
        before, after = read(label + "-inputs-before"), read(label + "-inputs-after")
        assert before == after
        for name, ref in before.items():
            if name in pins:
                assert pins[name] == ref, name
            pins[name] = ref
        late[label] = read(label + "-late-inputs")
        for name, ref in late[label].items():
            pins[name] = ref
        texts = {}
        for stream, raw in command["raw"].items():
            path = Path(raw["path"])
            assert digest(path) == {key: raw[key] for key in ("bytes", "sha256")}
            raw_files[str(path)] = digest(path)
            texts[stream] = path.read_bytes().decode("utf-8")
            all_temps.update(re.findall(r"\[owned-temp\] ([^\r\n]+)", texts[stream]))
        observed_ids = re.findall(r"^test_\w+ \(([^)]+)\) \.\.\.", texts["stderr"], re.MULTILINE)
        assert observed_ids == inv["tests"], (label, observed_ids, inv["tests"])
        assert re.search(r"Ran %d tests in [\d.]+s\s+OK\s*$" % expected, texts["stderr"])
        all_tests.extend(observed_ids)
        results[label] = {"result": result, "inventory": inv, "command": command}
        archives = read(label + "-archives")
        assert not archives["owned_remaining"], archives["owned_remaining"]
        for record in archives["archives"]:
            archive_path = Path(record["archive"])
            with zipfile.ZipFile(archive_path) as archive:
                assert set(archive.namelist()) == set(record["files"])
                for name, ref in record["files"].items():
                    data = archive.read(name)
                    assert {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} == ref
            all_archives.append({"path": str(archive_path), "source": record["source"],
                                 **digest(archive_path), "members": len(record["files"]),
                                 "links_not_followed": record["links_not_followed"]})
    assert len(all_tests) == len(set(all_tests)) == 74
    # The two Q1 patterns are exhaustive and disjoint, not two overlapping counts.
    files = set((ROOT / "scripts/tests").glob("test_measure_*.py"))
    one = set((ROOT / "scripts/tests").glob("test_measure_[gi]*.py"))
    two = set((ROOT / "scripts/tests").glob("test_measure_q1*.py"))
    assert one | two == files and not one & two

    # Independently check native mode observations emitted by this actual worker.
    stdout = Path(results["g"]["command"]["raw"]["stdout"]["path"]).read_text(encoding="utf-8")
    modes = [json.loads(line) for line in stdout.splitlines() if line.startswith('{"case":')]
    indexed = {entry["case"]: entry for entry in modes}
    assert set(indexed) == {"default", "env-on", "env-off", "cli-off", "cli-on",
                            "last-off", "last-on", "ignored-off", "ignored-on", "isolated-off"}
    for entry in modes:
        observation = entry["observation"]
        assert entry["exit_code"] == 0
        assert observation["digest"] == observation["after"]
        assert observation["table"] == observation["table_after"]
        active = observation["table"].get("__phello__") is not None
        assert (observation["native_origin"] == "frozen") == active
        assert observation["local"] == (not active)
    assert indexed["env-on"]["observation"]["digest"] != indexed["env-off"]["observation"]["digest"]
    for keys in (("env-on", "cli-on", "last-on"), ("env-off", "cli-off", "last-off"),
                 ("default", "ignored-off", "ignored-on", "isolated-off")):
        assert len({indexed[key]["observation"]["digest"] for key in keys}) == 1

    qualification = []
    for name in ("q1-review-correction-qualification.json",
                 "q1-resumed-correction-core-qualification.json"):
        path = HERE / name
        record = json.loads(path.read_bytes())
        assert record["status"] == "PASS"
        for command in record["commands"]:
            for raw in command["raw"].values():
                assert digest(Path(raw["path"])) == {k: raw[k] for k in ("bytes", "sha256")}
        qualification.append({"path": str(path), **digest(path),
                              "command_count": len(record["commands"]),
                              "historical_not_reexecuted_here": True})

    # Reconcile original verifier-produced archives and byte captures too.
    fixtures = HERE / (PREFIX + "fixtures-i")
    verifier_archives = []
    for path in fixtures.glob("*-fixture-*.json"):
        record = json.loads(path.read_bytes())
        archive_path = fixtures / record["archive"]
        with zipfile.ZipFile(archive_path) as archive:
            assert set(archive.namelist()) == set(record["files"])
            for name, ref in record["files"].items():
                data = archive.read(name)
                assert {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} == ref
        verifier_archives.append({"path": str(archive_path), **digest(archive_path),
                                  "members": len(record["files"])})
    for path in fixtures.glob("*-command-*.json"):
        record = json.loads(path.read_bytes())
        stem = path.name.replace("-command-", "-").removesuffix(".json")
        for stream, ref in record["raw"].items():
            raw_path = fixtures / (stem + "." + stream + ".bin")
            assert digest(raw_path) == ref
            raw_files[str(raw_path)] = ref

    changed = [name for name, ref in pins.items()
               if not Path(name).is_file() or digest(Path(name)) != ref]
    remaining = sorted(path for path in all_temps if Path(path).exists())
    git = git_observation("git-after")
    assert git["binding"] == read("git-during")["binding"]
    for path in (ROOT / "scripts/tests/test_measure_q1_final_verification.py",
                 HERE / (PREFIX + "capture.py"), Path(__file__)):
        compile(path.read_bytes(), str(path), "exec")
    result = {"status": "VERIFIED-WITH-LIMITATIONS" if not
              (changed or protected_changed or remaining) else "BLOCKED-FRESHNESS",
              "results": results, "distinct_q1_tests": 55, "original_q1_tests": 52,
              "added_tests": 3, "legacy_probe_tests": 19, "total_distinct": 74,
              "frozen_inputs": pins, "input_changes": changed,
              "protected_count": len(start["protected"]), "protected_changes": protected_changed,
              "allowed_parent_state_change": parent_status, "late_imports": late,
              "owned_archives": all_archives, "verifier_archives": verifier_archives,
              "raw_files": raw_files, "actual_modes": modes,
              "qualification": qualification, "git": git,
              "temporary_count": len(all_temps), "temporary_remaining": remaining,
              "file_partition": {"g": sorted(p.name for p in one), "i": sorted(p.name for p in two)},
              "limits": ["Bounded Windows/CPython/Git package proof, not OS-loader closure.",
                         "Historical qualification rehashed, not rerun as a separate qualification suite.",
                         "Five copied controller files do not prove Q4 execution.",
                         "No actual-root quality, mutation, C1 reacceptance, Q2 advancement or release.",
                         "Separate code re-review remains required."]}
    save("final-freeze", result)
    assert not (changed or protected_changed or remaining), result["status"]
    print(json.dumps({"status": result["status"], "tests": 74, "pins": len(pins),
                      "protected": len(start["protected"]), "archives": len(all_archives),
                      "verifier_archives": len(verifier_archives), "raw_files": len(raw_files),
                      "late_imports": late, "owned_temps": len(all_temps)}))


if __name__ == "__main__":
    if sys.argv[1] == "environment":
        git_observation("git-during")
    else:
        finalize()
