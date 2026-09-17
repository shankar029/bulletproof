"""Additive, streamed frozen-checkpoint verification. No production modifications."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).parent
OUT = EVIDENCE / "joint-cli-binding-records"
sys.path[:0] = [str(ROOT / "scripts/tests"), str(ROOT / "scripts")]
BLOCKED = "test_measure_q2.ToolRootTests.test_actual_symlink_root_rejects"


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def load_tests():
    spec = importlib.util.spec_from_file_location("joint_cli_binding_tests", EVIDENCE / "joint-cli-binding-tests.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    patterns = {
        "cli": ["test_workflow_cli"],
        "independent": ["joint_cli_binding_tests"],
        "workflow": [p.stem for p in (ROOT / "scripts/tests").glob("test_workflow*.py")
                     if p.stem != "test_workflow_cli"],
        "support": ["test_evidence", "test_run", "test_run_c2a_verification"],
        "root": ["test_measure_q2"],
        "source": ["test_measure_source_bindings"],
        "q1": [p.stem for p in (ROOT / "scripts/tests").glob("test_measure*.py")
               if p.stem not in {"test_measure_q2", "test_measure_source_bindings"}],
        "probe": ["test_probe"],
    }
    seen, batches, tests = set(), {}, {}
    def flatten(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from flatten(item)
            else:
                yield item
    for batch, modules in patterns.items():
        ids = []
        for test in flatten(unittest.defaultTestLoader.loadTestsFromNames(sorted(modules))):
            identity = test.id()
            if identity not in seen:
                seen.add(identity)
                tests[identity] = test
                ids.append(identity)
        batches[batch] = sorted(ids)
    return batches, tests


def pin_paths():
    from test_measure_q2 import native_tools
    from test_measure_source_bindings import source_tools
    paths = {p.resolve() for p in (ROOT / "scripts").rglob("*")
             if p.is_file() and p.suffix in {".py", ".mjs", ".json"} and "__pycache__" not in p.parts}
    paths.update((ROOT / "evals/lib").glob("*.mjs"))
    paths.update((ROOT / "evals/workflow").glob("*.mjs"))
    for name in ("design.html", "design-contracts.json", "c2-recovery-contract.json",
                 "measurement-enablement-contracts.json", "guard-resolution-contract.json",
                 "baseline-materialization-contract.json"):
        paths.add(EVIDENCE.parent / name)
    for name in ("q2-tool-input-root-amendment.json", "q2-tool-input-root-review.md",
                 "c2-recovery-design-review-r2.md", "q2-tools-manifest.json",
                 "q2-adapter-source-development.py", "q2-adapter-root-development.py"):
        paths.add(EVIDENCE / name)
    paths.add(ROOT / "references/workflow-gates.md")
    paths.update([Path(__file__), EVIDENCE / "joint-cli-binding-tests.py"])
    for binding in {**native_tools(), **source_tools()}.values():
        paths.add(Path(binding["executable"]).resolve())
        for ref in [binding["help"], binding["configuration"], *binding["qualification"]]:
            paths.add(EVIDENCE / ref["path"])
    # Exact indexed resource set; no qualification fixture rerun or raw index dump.
    resource_index = json.loads((EVIDENCE / "q2-tools-source-extracted-pins.json").read_bytes())
    paths.update(Path(row["path"]) for row in resource_index)
    for tool in ("lizard", "vulture"):
        provenance = json.loads((EVIDENCE / ("q2-tools-source-python-provenance-" + tool + ".json")).read_bytes())
        paths.update(Path(row["path"]) for row in provenance["imported_files"])
    runtime = json.loads((EVIDENCE / "q2-tools-runtime-bindings.json").read_bytes())
    paths.add(Path(runtime["python_dll"]["path"]))
    for executor in runtime["executors"].values():
        paths.add(Path(executor["path"]).resolve())
        for row in executor["pe"]["declared_imports"]:
            if row["resolved_existing_candidate"]:
                paths.add(Path(row["resolved_existing_candidate"]).resolve())
    paths.update(Path(sys.base_prefix).rglob("*.py"))
    paths.update(Path(sys.base_prefix).glob("*.dll"))
    paths.add(Path(sys.executable))
    paths.add(Path(shutil.which("git")).resolve())
    paths.add(Path(shutil.which("node")).resolve())
    return sorted({str(p.resolve()) for p in paths})


def pins(paths):
    result = {}
    for index, name in enumerate(paths, 1):
        path = Path(name)
        content = path.read_bytes()
        result[name] = {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
        if index % 500 == 0:
            print("Completed actual input rehashes:", index, flush=True)
    return result


class Progress(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        self.stream.writeln("Completed actual subtest: " + subtest.id())
        self.stream.flush()


def worker(batch):
    batches, tests = load_tests()
    selected = [name for name in batches[batch] if name != BLOCKED]
    directory = OUT / batch
    os.environ["C2_CLI_TRANSCRIPT"] = str(directory / "cli-invocations.jsonl")
    os.environ["Q2_SOURCE_RECORDS"] = str(directory)
    os.environ["Q2_ADAPTER_RECORDS"] = str(directory)
    import run
    # Passive Python profiling observes real Popen returns and capture results.
    # It replaces no producer, runner, callback or subprocess implementation.
    with (directory / "capture-invocations.jsonl").open("x", encoding="utf-8") as raw:
        def profile(frame, event, arg):
            if event != "return":
                return
            if frame.f_code is run._popen.__code__ and arg is not None:
                row = {"kind": "actual-spawn", "pid": arg.pid, "argv": frame.f_locals["cmd"],
                       "cwd": str(frame.f_locals.get("cwd")), "parent_pid": os.getpid()}
            elif frame.f_code is run.run_capture.__code__ and isinstance(arg, tuple):
                row = {"kind": "actual-capture", "argv": frame.f_locals["cmd"],
                       "cwd": str(frame.f_locals.get("cwd")), "result": arg,
                       "idle": frame.f_locals["idle"], "max": frame.f_locals["max_total"]}
            else:
                return
            raw.write(json.dumps(row, ensure_ascii=False) + "\n")
            raw.flush()
        sys.setprofile(profile)
        started = time.monotonic()
        try:
            result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, failfast=True,
                                            resultclass=Progress).run(
                unittest.TestSuite(tests[name] for name in selected))
        finally:
            sys.setprofile(None)
    save(directory / "result.json", {
        "selected": selected, "tests_run": result.testsRun, "passed": result.passed,
        "failures": [(t.id(), detail) for t, detail in result.failures],
        "errors": [(t.id(), detail) for t, detail in result.errors],
        "skips": [(t.id(), detail) for t, detail in result.skipped],
        "seconds": time.monotonic() - started,
        "environment_unverified": [BLOCKED] if batch == "root" else [],
        "runtime_imports": sorted({str(Path(m.__file__).resolve()) for m in sys.modules.values()
                                   if getattr(m, "__file__", None) and Path(m.__file__).is_file()}),
    })
    return 0 if result.wasSuccessful() and not result.skipped else 1


def main():
    action = sys.argv[1]
    if action == "prepare":
        OUT.mkdir(exist_ok=False)
        short = tempfile.mkdtemp(prefix="jcb-")
        save(OUT / "environment.json", {
            "short_temp": short, "python": sys.executable, "version": sys.version,
            "git": shutil.which("git"), "node": shutil.which("node"), "cwd": str(ROOT),
            "base_head": "ee6e0e34e78b70fcb672074af0a76f51fe937e1a",
            "blocked": {"id": BLOCKED, "error": "Prior actual WinError 1314; retained, not retried or skipped"},
        })
        batches, _tests = load_tests()
        save(OUT / "inventory.json", batches)
        from evidence import write_json_atomic
        with tempfile.TemporaryDirectory(prefix="receipt-", dir=short) as transport:
            destination = Path(transport) / ".ai/demo/evidence/receipts" / ("receipt-" + "a" * 32 + ".json")
            payload = {"transport_only": True, "actual_bytes": "Unicode receipt transport 日本"}
            write_json_atomic(destination, payload)
            assert json.loads(destination.read_bytes()) == payload
            save(OUT / "receipt-transport.json", {
                "path": str(destination), "length": len(str(destination)),
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "roundtrip_equal": True, "not_a_receipt_acceptance_claim": True})
        save(OUT / "before-pins.json", pins(pin_paths()))
        print(json.dumps({name: len(ids) for name, ids in batches.items()}), flush=True)
        return 0
    if action == "worker":
        return worker(sys.argv[2])
    if action == "finish":
        before = json.loads((OUT / "before-pins.json").read_bytes())
        after = pins(before)
        changes = [name for name in before if before[name] != after[name]]
        save(OUT / "after-pins.json", after)
        save(OUT / "freshness.json", {"checked": len(before), "changed": changes})
        short = Path(json.loads((OUT / "environment.json").read_bytes())["short_temp"])
        entries = list(short.iterdir())
        if not entries:
            short.rmdir()
        save(OUT / "cleanup.json", {"owned_temp": str(short), "remaining": [str(p) for p in entries],
                                    "removed_empty_only": not entries,
                                    "historical_whole_tree_cleanup": "UNKNOWN"})
        print(json.dumps({"pins": len(before), "changed": changes, "remaining_temp_entries": len(entries)}))
        return 1 if changes else 0
    if action != "batch":
        raise ValueError("Use prepare, batch, worker or finish")
    batch = sys.argv[2]
    directory = OUT / batch
    directory.mkdir(exist_ok=False)
    settings = json.loads((OUT / "environment.json").read_bytes())
    env = os.environ.copy()
    env.update({key: settings["short_temp"] for key in ("TEMP", "TMP", "TMPDIR")})
    env.update(PYTHONDONTWRITEBYTECODE="1", BULLETPROOF_PYTHON=sys.executable)
    env["C2_CLI_TRANSCRIPT"] = str(directory / "cli-invocations.jsonl")
    maximum = "1800" if batch in {"root", "source", "q1"} else "600"
    inner = ([shutil.which("node"), "--test", "evals/workflow/failures.test.mjs",
              "evals/lib/native_result.test.mjs"] if batch == "native" else
             [sys.executable, "-B", "-u", str(Path(__file__)), "worker", batch])
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", maximum, "--", *inner]
    save(directory / "command.json", {
        "argv": argv, "cwd": str(ROOT), "supervisor_pid": os.getpid(),
        "environment": {k: env[k] for k in ("PATH", "TEMP", "TMP", "TMPDIR", "PYTHONDONTWRITEBYTECODE",
                                            "BULLETPROOF_PYTHON", "C2_CLI_TRANSCRIPT")},
        "capture": "Streaming raw merged stdout/stderr bytes; no shell redirection or buffered outer capture",
    })
    start = time.monotonic()
    with (directory / "output.log").open("xb") as output:
        proc = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        save(directory / "pid.json", {"runner_pid": proc.pid, "supervisor_pid": os.getpid()})
        while data := proc.stdout.read1(65536):
            output.write(data)
            output.flush()
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        proc.stdout.close()
        code = proc.wait()
    save(directory / "exit.json", {"returncode": code, "seconds": time.monotonic() - start})
    return code


if __name__ == "__main__":
    raise SystemExit(main())
