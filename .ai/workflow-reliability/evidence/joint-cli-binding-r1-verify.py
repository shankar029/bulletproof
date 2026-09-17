"""Independent affected replay using the owner's unchanged test bodies and capture."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "joint-cli-binding-r1-records"
RESULTS = HERE / "joint-cli-binding-r1-results"
OWNER = HERE / "q2-binding-r1-verify.py"
EXPECTED = {
    str(ROOT / "scripts/measure.py"): "1cd5e00bd054a83ea338f7aab6150de6988443d6a12435cdfad30e72ee78dfd1",
    str(ROOT / "scripts/tests/test_measure_source_bindings.py"): "bcc36f23061dd5b4db2dfcb161c0202bbe95db1fb930b1c6ef79fe8c9b95d1b3",
}
SELECTED = [
    "test_measure_source_bindings",
    "test_measure_q2.ToolRootTests.test_empty_mode_and_conditional_root_validation",
    "test_measure_q2.ToolRootTests.test_duplicate_prefix_reserved_namespace_and_hardlinks_reject",
]


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)


def pin(path):
    data = Path(path).read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def load(path):
    return json.loads(path.read_bytes())


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def without_function(data, name):
    lines = data.splitlines(keepends=True)
    nodes = sorted((node for node in ast.walk(ast.parse(data))
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))), key=lambda n: n.lineno)
    node = next(node for node in nodes if node.name == name)
    end = node.end_lineno
    while end < len(lines) and not lines[end].strip():
        end += 1
    return b"".join(lines[:node.lineno - 1] + lines[end:])


def method_ids(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from method_ids(item)
        else:
            yield item.id()


def prepare(resume=False):
    if resume:
        assert OUT.is_dir() and not (OUT / "before-pins.json").exists()
    else:
        OUT.mkdir(exist_ok=False)
    assert not RESULTS.exists()
    old = load(HERE / "joint-cli-binding-r2-records/before-pins.json")
    current = {name: pin(name) for name in old}
    changed = {name: {"before": old[name], "current": row}
               for name, row in current.items() if row != old[name]}
    assert set(changed) == set(EXPECTED), changed
    assert all(current[name]["sha256"] == sha for name, sha in EXPECTED.items())

    source = (ROOT / "scripts/measure.py").read_bytes()
    prior = without_function(source, "_validate_binding_ownership")
    call = b"    _validate_binding_ownership(manifest, config)\r\n"
    assert prior.count(call) == 1
    prior = prior.replace(call, b"", 1)
    assert hashlib.sha256(prior).hexdigest() == old[str(ROOT / "scripts/measure.py")]["sha256"]
    test = (ROOT / "scripts/tests/test_measure_source_bindings.py").read_bytes()
    old_test = without_function(test, "test_qualification_ownership_rejects_rehashed_manifests_before_launch")
    assert old_test.count(b"import sys\r\n") == 1
    old_test = old_test.replace(b"import sys\r\n", b"", 1)
    assert hashlib.sha256(old_test).hexdigest() == old[
        str(ROOT / "scripts/tests/test_measure_source_bindings.py")]["sha256"]
    diff = ""
    for label, before, after in (("scripts/measure.py", prior, source),
                                 ("scripts/tests/test_measure_source_bindings.py", old_test, test)):
        diff += "".join(difflib.unified_diff(before.decode().splitlines(True),
                       after.decode().splitlines(True), "reviewed/" + label, "current/" + label))
    narrow = {
        "changed_previous_pins": changed, "measure_raw_reconstructed": hashlib.sha256(prior).hexdigest(),
        "tests_raw_reconstructed": hashlib.sha256(old_test).hexdigest(),
        "method": "Remove only new helper/call; remove only new test/sys import; exact raw-byte comparison",
    }
    if resume:
        assert load(OUT / "narrow-change.json") == narrow
        assert (OUT / "r1-only.diff").read_bytes() == diff.replace("\n", os.linesep).encode("utf-8")
    else:
        with (OUT / "r1-only.diff").open("x", encoding="utf-8") as stream:
            stream.write(diff)
        save(OUT / "narrow-change.json", narrow)

    repro_path = HERE / "q2-binding-r1-repro/reproduction.json"
    assert pin(repro_path)["sha256"] == "a74b337ca26cb7ca7991f53069c60abca01afec6b26e1b262beb82fef9e0d46f"
    repro = load(repro_path)
    broken = repro["malformed_manifest"]
    ref = repro["context"]["output_manifest"]
    raw = json_bytes(broken)
    assert ref["sha256"] == hashlib.sha256(raw).hexdigest() and ref["bytes"] == len(raw)
    assert repro["removed_row"] in repro["original_manifest"]["inputs"]
    assert repro["removed_row"] not in broken["inputs"]
    assert repro["removed_row"]["artifact"]["path"] in broken["reserved_outputs"]
    assert len(repro["audited_launches"]) == 1 and repro["command"]["returncode"] == 0
    audited_argv = repro["audited_launches"][0]["argv"]
    expected_argv = repro["command"]["argv"]
    assert audited_argv == (subprocess.list2cmdline(expected_argv)
                            if isinstance(audited_argv, str) else expected_argv)
    assert repro["observed"]["observed"]["smoke"]["symbol"] == "answer"
    raw_record = load(HERE / "q2-binding-r1-repro/raw-b9f2a02c67e7.json")
    checked = []
    for kind in ("request", "result", "command"):
        artifact = repro["observed"][kind]
        value = raw_record["artifacts"][artifact["path"]]
        data = json_bytes(value)
        # The Node result is ordinary JSON.stringify, not the controller serializer.
        if kind == "result":
            data = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        assert hashlib.sha256(data).hexdigest() == artifact["sha256"], kind
        assert len(data) == artifact["bytes"], kind
        checked.append(artifact)
    save(OUT / "historical-counterexample-check.json", {
        "source": str(repro_path), "pin": pin(repro_path), "manifest_ref": ref,
        "checked_artifacts": checked, "audited_launches": repro["audited_launches"],
        "returncode": repro["command"]["returncode"], "symbol": "answer",
        "limitation": "Independent reconciliation of owner-recorded execution, not rerunning unfixed code",
    })

    sys.path[:0] = [str(ROOT / "scripts/tests"), str(ROOT / "scripts"), str(ROOT)]
    ids = list(method_ids(unittest.defaultTestLoader.loadTestsFromNames(SELECTED)))
    assert len(ids) == len(set(ids)) == 10 and not any("_FailedTest" in item for item in ids)
    save(OUT / "plan.json", {"selected": SELECTED, "method_ids": ids,
        "idle_seconds": 120, "max_seconds": 1800, "historical_262_refreshed": False,
        "capture": "Existing resource/subtest progress; no profiler; prefix-only adapter plus failfast",
        "symlink": "Retained WinError 1314; not selected or retried"})
    paths = set(current)
    paths.update(str(path.resolve()) for path in HERE.glob("q2-binding-r1-*") if path.is_file())
    for directory in ("q2-binding-r1-repro", "q2-binding-r1-final"):
        paths.update(str(path.resolve()) for path in (HERE / directory).iterdir() if path.is_file())
    paths.update(str(path.resolve()) for path in HERE.glob("joint-cli-binding-r2-*") if path.is_file())
    paths.add(str(Path(__file__).resolve()))
    paths.add(str(HERE / "joint-cli-binding-code-review.md"))
    paths.update(str(path.resolve()) for path in (Path(sys.base_prefix) / "Lib").rglob("*.py"))
    paths.update(str(path.resolve()) for path in (Path(sys.base_prefix) / "DLLs").glob("*.pyd"))
    before = {name: pin(name) for name in sorted(paths)}
    save(OUT / "before-pins.json", before)
    save(OUT / "added-pin-paths.json", sorted(paths - set(old)))
    print(json.dumps({"prepared": True, "pins": len(before), "methods": ids}), flush=True)


def worker():
    source = OWNER.read_text(encoding="utf-8")
    adaptations = {
        'name.startswith("q2-binding-r1-")': 'name.startswith("joint-cli-binding-r1-")',
        "verbosity=2, resultclass=Result": "verbosity=2, resultclass=Result, failfast=True",
    }
    for before, after in adaptations.items():
        assert source.count(before) == 1
        source = source.replace(before, after, 1)
    save(OUT / "capture-adaptation.json", {"owner_pin": pin(OWNER), "replacements": adaptations,
        "executed_capture_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "test_bodies_changed": False, "production_changed": False})
    save(OUT / "worker.json", {"pid": os.getpid(), "ppid": os.getppid(), "executable": sys.executable,
        "cwd": os.getcwd(), "argv": sys.argv, "temp": tempfile.gettempdir(),
        "profile_installed": sys.getprofile() is not None})
    namespace = {"__file__": str(OWNER), "__name__": "independent_r1_owner_capture"}
    exec(compile(source, str(OWNER), "exec"), namespace)
    sys.argv = [str(OWNER), RESULTS.name]
    try:
        return namespace["main"]()
    finally:
        modules = {}
        for name, module in tuple(sys.modules.items()):
            path = getattr(module, "__file__", None)
            if path and Path(path).is_file():
                path = Path(path).resolve()
                if path.suffix == ".pyc":
                    import importlib.util
                    path = Path(importlib.util.source_from_cache(str(path)))
                modules[name] = str(path)
        save(OUT / "loaded-module-paths.json", modules)


def execute():
    before = load(OUT / "before-pins.json")
    assert all(pin(name) == row for name, row in before.items()), "Pins changed since preparation"
    scratch = Path(tempfile.mkdtemp(prefix="jcbr1-")).resolve()
    env = dict(os.environ, TEMP=str(scratch), TMP=str(scratch), PYTHONDONTWRITEBYTECODE="1",
               BULLETPROOF_PYTHON=sys.executable)
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", "1800",
            "--", sys.executable, "-B", "-u", str(Path(__file__).resolve()), "worker"]
    save(OUT / "command.json", {"argv": argv, "cwd": str(ROOT), "supervisor_pid": os.getpid(),
        "environment": {key: env.get(key) for key in (
            "PATH", "TEMP", "TMP", "PYTHONDONTWRITEBYTECODE", "BULLETPROOF_PYTHON",
            "PYTHONPATH", "PYTHONHOME", "NODE_OPTIONS", "NODE_PATH")},
        "other_environment": "Inherited unchanged; not dumped (may contain credentials)",
        "short_temp_owner": "Created exclusively by this execution; no old roots accessed"})
    started = time.monotonic()
    with (OUT / "stdout-stderr.log").open("xb") as stream:
        proc = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        save(OUT / "runner.json", {"pid": proc.pid, "started_monotonic": started})
        for line in iter(proc.stdout.readline, b""):
            stream.write(line)
            stream.flush()
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
        proc.stdout.close()
        code = proc.wait()
    save(OUT / "exit.json", {"returncode": code, "seconds": time.monotonic() - started})
    entries = [str(path) for path in scratch.iterdir()]
    if not entries:
        scratch.rmdir()
    save(OUT / "cleanup.json", {"root": str(scratch), "entries": entries,
        "removed_empty_nonrecursively": not entries, "old_cleanup": "UNKNOWN; untouched",
        "process_tree_death": "Not established by empty-directory cleanup"})
    print(json.dumps({"returncode": code, "new_temp_removed": not entries}), flush=True)
    return code


def finish():
    before = load(OUT / "before-pins.json")
    after = {name: pin(name) for name in before}
    save(OUT / "after-pins.json", after)
    changed = [name for name in before if before[name] != after[name]]
    module_paths = load(OUT / "loaded-module-paths.json")
    unpinned = sorted(set(module_paths.values()) - set(before))
    save(OUT / "freshness.json", {"checked": len(before), "changed": changed,
        "loaded_controller_modules": len(module_paths), "unpinned_module_files": unpinned,
        "limit": "Observed controller modules and qualified runtime/resource candidates, not full loaded-DLL attestation"})
    result = load(RESULTS / "result.json")
    ids = load(OUT / "plan.json")["method_ids"]
    assert result["tests_run"] == 10 and sorted(result["passed_ids"]) == sorted(ids)
    assert not result["failures"] and not result["errors"] and not result["skipped"]
    assert result["same_bytes"] and not changed and not unpinned
    ownership = load(RESULTS / "r1-ownership.json")
    assert len(ownership) == 20
    for row in ownership:
        data = json_bytes(row["manifest"])
        assert row["manifest_ref"]["sha256"] == hashlib.sha256(data).hexdigest()
        assert row["manifest_ref"]["bytes"] == len(data)
        assert row["error"] and not row["launches"] and not row["writes"] and not row["outputs_present"]
    control = load(RESULTS / "r1-valid-control.json")
    assert len(control["launches"]) == 1 and len(control["writes"]) == 2
    assert control["observation"]["observed"]["smoke"]["symbol"] == "answer"
    revisions = load(RESULTS / "two-revisions.json")
    assert {(item["revision"], item["observed"]["tool"]) for item in revisions} == {
        (revision, tool) for revision in ("base", "head") for tool in ("typescript", "lizard", "vulture")}
    assert len({item["raw_command"]["toolset_sha256"] for item in revisions}) == 1
    assert all(item["raw_command"]["returncode"] == 0 for item in revisions)
    save(OUT / "reconciliation.json", {
        "verdict": "VERIFIED-WITH-LIMITATIONS", "fresh_methods": 10, "passed_ids": result["passed_ids"],
        "seconds": result["seconds"], "malformed_manifests": len(ownership),
        "cases": [row["case"] for row in ownership], "negative_audit_launches": 0,
        "negative_audit_write_opens": 0, "negative_outputs": 0,
        "valid_control_launches": len(control["launches"]), "valid_control_write_opens": len(control["writes"]),
        "two_revision_smokes": len(revisions), "unchanged_pins": len(before),
        "historical_262_refreshed": False, "native_13_rerun": False,
        "symlink": "Retained named WinError 1314 environment-unverified case",
        "parent_acceptance_and_same_reviewer_rereview": "PENDING"})
    files = [path for directory in (OUT, RESULTS) for path in directory.iterdir() if path.is_file()]
    save(OUT / "raw-record-index.json", {str(path.relative_to(ROOT)): pin(path) for path in sorted(files)})
    print(json.dumps(load(OUT / "reconciliation.json")), flush=True)


if __name__ == "__main__":
    action = {"prepare": prepare, "prepare-resume": lambda: prepare(resume=True),
              "worker": worker, "execute": execute, "finish": finish}[sys.argv[1]]
    raise SystemExit(action() or 0)
