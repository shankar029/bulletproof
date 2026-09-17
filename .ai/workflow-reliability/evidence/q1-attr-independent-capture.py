"""One bounded focused replay, then integrated C1; exclusive additive artifacts."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "q1-attr-independent-"
spec = importlib.util.spec_from_file_location("transport", HERE / "q1-resumed-correction-capture.py")
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)
transport.__file__ = __file__
transport.prior.__file__ = __file__
transport.prior.PREFIX = PREFIX
EXPECTED = {"a": 28, "w": 83, "e": 10}


def hashes(paths):
    return {str(p.resolve()): {"bytes": p.stat().st_size,
                              "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(set(paths)) if p.is_file()}


def save(name, value):
    with (HERE / (PREFIX + name + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


def read(name):
    return json.loads((HERE / (PREFIX + name + ".json")).read_bytes())


def paths():
    result = list((ROOT / "scripts").glob("*.py"))
    result += list((ROOT / "scripts/tests").glob("*.py"))
    result += [ROOT / "scripts/native_result.mjs", Path(__file__),
               HERE / "q1-resumed-correction-capture.py", HERE / "q1-review-correction-capture.py",
               HERE / "q1-independent-capture.py"]
    result += [p for p in Path(sys.base_prefix).rglob("*") if p.is_file()
               and p.suffix in {".py", ".pyc", ".pyd", ".dll", ".exe", ".zip"}]
    result += [HERE.parent / name for name in ("design-contracts.json", "guard-resolution-contract.json",
               "measurement-enablement-contracts.json", "baseline-materialization-contract.json")]
    owner = json.loads((HERE / "q1-attr-final-freeze.json").read_bytes())
    result += [Path(name) for name in owner["frozen_inputs"]
               if Path(name) != HERE.parent / "state.md"]
    for module in list(sys.modules.values()):
        for attr in ("__file__", "__cached__"):
            name = getattr(module, attr, None)
            if name and Path(name).is_file():
                result.append(Path(name))
    import shutil
    for name in ("git", "node"):
        executable = shutil.which(name)
        if executable:
            result.append(Path(executable))
    return result


def preflight(label):
    owner = json.loads((HERE / "q1-attr-final-freeze.json").read_bytes())
    actual = hashes([Path(p) for p in owner["frozen_inputs"]])
    changes = [p for p, ref in owner["frozen_inputs"].items()
               if actual.get(str(Path(p).resolve())) != ref and Path(p) != HERE.parent / "state.md"]
    protected = hashes([p for p in HERE.rglob("*") if p.is_file()
                        and not p.relative_to(HERE).parts[0].startswith(PREFIX)])
    inputs = hashes(paths())
    save(label, {"owner_changes": changes, "owner_inputs": owner["frozen_inputs"],
                       "inputs": inputs, "protected": protected,
                       "runtime": sys.version, "executable": sys.executable})
    assert not changes, changes
    assert inputs[str(ROOT / "scripts/measure.py")]["sha256"] == (
        "5d6f15a95de50d932953023508dd12ae2f470fd073af91d409ca5a948838b084")
    print(json.dumps({"inputs": len(inputs), "protected": len(protected), "changes": changes}))


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def suite_for(label):
    sys.path.insert(0, str(ROOT / "scripts/tests"))
    loader = unittest.TestLoader()
    if label in {"w", "e"}:
        pattern = "test_workflow_*.py" if label == "w" else "test_evidence.py"
        return loader.discover(str(ROOT / "scripts/tests"), pattern=pattern)
    names = [
        "test_measure_q1_attr", "test_measure_q1_attr_independent",
        "test_measure_q1_resumed.ResumedBoundaryTests.test_external_filter_macro_rejected_before_sentinel_execution",
        "test_measure_q1_resumed.ResumedBoundaryTests.test_neutral_and_versioned_eol_modes_exact_bytes",
        "test_measure_q1_resumed.ResumedBoundaryTests.test_unqualified_attributes_and_git_types_fail_closed",
        "test_measure_q1_integration.Q1IntegrationTests.test_public_python_cli_from_nested_cwd_keeps_all_nine_and_archives_raw",
        "test_probe",
    ]
    return loader.loadTestsFromNames(names)


def worker(_pattern, label):
    if label == "w":
        destination = HERE / (PREFIX + "w-imports.json")
        assert not destination.exists()
        os.environ["C1_VERIFICATION_IMPORT_MANIFEST"] = str(destination)
    suite = suite_for(label)
    inventory = [test.id() for test in cases(suite)]
    save(label + "-inventory", {"tests": inventory, "expected": EXPECTED[label],
                                "pattern_argument": _pattern})
    assert len(inventory) == len(set(inventory)) == EXPECTED[label], inventory
    ast.unparse(ast.parse("value = 1"))
    pinned = paths()
    before = hashes(pinned)
    save(label + "-inputs-before", before)
    records, owned = [], set()
    archive_root = HERE / (PREFIX + "f-" + label)
    archive_root.mkdir(exist_ok=False)

    def audit(event, args):
        if event == "subprocess.Popen":
            print("[native-start] " + repr(args[1]), file=sys.stderr, flush=True)
        elif event == "tempfile.mkdtemp":
            path = Path(args[0]).resolve()
            owned.add(path)
            print("[owned-temp] " + str(path), file=sys.stderr, flush=True)
        elif event == "shutil.rmtree" and label == "a":
            path = Path(args[0]).resolve()
            if path not in owned or not path.exists() or any(r["source"] == str(path) for r in records):
                return
            if not path.name.startswith(("q1-attr-tests-", "q1-attr-independent-tests-",
                                         "q1-resumed-tests-", "bulletproof-git-", "q1-evidence-")):
                return
            if path.name.startswith(("bulletproof-git-policy-", "bulletproof-git-head-", "bulletproof-git-tree-")):
                return
            archive_path = archive_root / ("%03d.zip" % len(records))
            files = {}
            with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
                for base, dirs, names in os.walk(path, followlinks=False):
                    dirs[:] = [name for name in dirs if not (Path(base) / name).is_symlink()
                               and not (Path(base) / name).is_junction()]
                    for name in names:
                        file = Path(base) / name
                        if file.is_symlink():
                            continue
                        data = file.read_bytes()
                        relative = file.relative_to(path).as_posix()
                        archive.writestr(relative, data)
                        files[relative] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            record = {"source": str(path), "archive": str(archive_path), "files": files}
            records.append(record)
            save(label + "-fixture-%03d" % len(records), record)

    sys.addaudithook(audit)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    after = hashes(pinned)
    observed = {}
    for name, module in list(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename and Path(filename).is_file():
            path = Path(filename).resolve()
            observed[name] = {"path": str(path), **hashes([path])[str(path)]}
    late = {r["path"]: {"bytes": r["bytes"], "sha256": r["sha256"]}
            for r in observed.values() if r["path"] not in before}
    save(label + "-inputs-after", after)
    save(label + "-observed-imports", observed)
    save(label + "-late-inputs", late)
    save(label + "-fixtures", records)
    save(label + "-result", {"tests": result.testsRun, "failures": len(result.failures),
                            "errors": len(result.errors), "skipped": len(result.skipped),
                            "unchanged": before == after,
                            "changed": [p for p, ref in before.items() if after.get(p) != ref],
                            "owned_temps": sorted(str(p) for p in owned),
                            "owned_remaining": sorted(str(p) for p in owned if p.exists())})
    return 0 if result.wasSuccessful() and before == after else 1


if __name__ == "__main__":
    action, *args = sys.argv[1:]
    if action == "preflight":
        preflight(args[0] if args else "preflight")
    else:
        sys.exit(worker(*args) if action == "worker" else transport.capture(*args))
