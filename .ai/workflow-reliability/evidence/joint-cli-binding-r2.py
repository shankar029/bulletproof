"""Authorized different capture: only actual completion of two exact code objects."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
OLD = HERE / "joint-cli-binding-records"
OUT = HERE / "joint-cli-binding-r2-records"
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("joint_capture_r2_base", HERE / "joint-cli-binding-verify.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
from test_measure_inventory import Q1Fixture


class CompletionTrace:
    """Constant-time identity filter; no global call/spawn/filesystem collection."""
    def __init__(self, directory):
        self.file = (directory / "validation-events.jsonl").open("x", encoding="utf-8")
        self.validate_code = Q1Fixture.validate.__code__
        self.assert_code = unittest.case._AssertRaisesContext.__exit__.__code__
        self.ordinal = 0
        self.active = {}
        self.rows = []
        self.errors = []
        self.method = "preflight"
        self.previous = None

    def callback(self, frame, event, value):
        # All unrelated functions leave after two identity comparisons. No
        # timestamps, allocation, hashing, stream I/O or spawn inspection there.
        code = frame.f_code
        if code is self.validate_code:
            name = "Q1Fixture.validate"
        elif code is self.assert_code:
            name = "_AssertRaisesContext.__exit__"
        else:
            return
        if event not in ("call", "return"):
            return
        try:
            if event == "call":
                self.ordinal += 1
                row = {"event": "entered", "target": name, "ordinal": self.ordinal,
                       "method": self.method, "monotonic": time.monotonic(), "pid": os.getpid()}
                self.active[id(frame)] = row
            else:
                start = self.active.pop(id(frame))
                row = {"event": "returned-control/completed-invocation", "target": name,
                       "ordinal": start["ordinal"], "method": start["method"],
                       "seconds": time.monotonic() - start["monotonic"],
                       "return_value_is_none": value is None,
                       "meaning": "Return event includes exception unwind; not an assertion verdict",
                       "pid": os.getpid()}
                self.rows.append(row)
            line = json.dumps(row, ensure_ascii=False)
            self.file.write(line + "\n")
            self.file.flush()
            # Starts are durable diagnostics, NEVER stdout progress/heartbeats.
            if event == "return":
                print(line, flush=True)
        except Exception as error:
            # Instrumentation must not replace a production result/exception.
            self.errors.append(type(error).__name__ + ": " + str(error))

    def __enter__(self):
        self.previous = sys.getprofile()
        if self.previous is not None:
            raise RuntimeError("Refuse to replace an existing profiler")
        sys.setprofile(self.callback)
        return self

    def __exit__(self, *args):
        sys.setprofile(self.previous)
        self.file.close()


class Result(capture.Progress):
    trace = None

    def startTest(self, test):
        self.trace.method = test.id()
        super().startTest(test)


def plan():
    prior = json.loads((OLD / "inventory-reconciliation.json").read_bytes())
    batches, tests = capture.load_tests()
    discovered = {identity for ids in batches.values() for identity in ids}
    old_discovered = {identity for batch in prior["batches"].values() for identity in batch["discovered"]}
    if discovered != old_discovered:
        raise ValueError("Actual discovery changed; do not assume counts")
    retained = {identity for batch in prior["batches"].values() for identity in batch["passed"]}
    requested = [prior["twice_idle_blocked_method"], *prior["never_started"]]
    if len(requested) != len(set(requested)) or set(requested) & retained:
        raise ValueError("Duplicate/already-passed selectors")
    if set(requested) != discovered - retained - {capture.BLOCKED}:
        raise ValueError("Remaining inventory does not reconcile")
    groups = {"timed-method": requested[:1]}
    for identity in requested[1:]:
        groups.setdefault(identity.split(".")[0], []).append(identity)
    return groups, tests, retained, discovered


def prepare():
    OUT.mkdir(exist_ok=False)
    groups, _tests, retained, discovered = plan()
    capture.save(OUT / "plan.json", {
        "groups": groups, "retained_passed": sorted(retained), "discovered": sorted(discovered),
        "environment_unverified": capture.BLOCKED,
        "trace_scope": ["Q1Fixture.validate.__code__", "unittest.case._AssertRaisesContext.__exit__.__code__"],
        "trace_semantics": "sys.setprofile exact-code identity filter; call/return records only for two targets",
        "bounds": {"idle": 120, "max": 1800}, "native_retained": {"pair": 5, "reporter": 8}})
    previous = json.loads((OLD / "before-pins.json").read_bytes())
    supplemental = json.loads((OLD / "supplemental-observed-inputs.json").read_bytes())["current_only"]
    names = set(previous) | set(supplemental)
    names.update(str(p.resolve()) for p in OLD.rglob("*") if p.is_file())
    names.update(str(p.resolve()) for p in HERE.glob("joint-cli-binding-*") if p.is_file())
    before = capture.pins(sorted(names))
    changed = [name for name in previous if before[name] != previous[name]]
    if changed:
        raise ValueError("Frozen initial inputs changed: " + repr(changed))
    capture.save(OUT / "before-pins.json", before)
    capture.save(OUT / "prospective-runtime-additions.json",
                 {name: before[name] for name in supplemental})
    print(json.dumps({"groups": {k: len(v) for k, v in groups.items()}, "retained": len(retained),
                      "discovered": len(discovered), "pins": len(before),
                      "previous_current_only_now_prospective": len(supplemental)}), flush=True)
    return 0


def worker(group, directory):
    capture.save(directory / "worker.json", {"pid": os.getpid(), "cwd": str(Path.cwd()),
                                            "python": sys.executable, "version": sys.version})
    with CompletionTrace(directory) as trace:
        if group == "preflight":
            fixture = Q1Fixture()
            try:
                fixture.materialize()
                original = fixture.validate()
                if not isinstance(original, list) or not original:
                    raise AssertionError("Real validation did not return its observation list")
                fixture.head["receipts"][0]["unit_count"] = True
                with unittest.TestCase().assertRaises(ValueError):
                    fixture.validate()
                validation_rows = [row for row in trace.rows if row["target"] == "Q1Fixture.validate"]
                if len(validation_rows) != 2 or trace.active or trace.errors:
                    raise AssertionError("Completion observer did not match two actual validations")
                capture.save(directory / "preflight.json", {
                    "actual_fixture_roots": [str(fixture.git.root), str(fixture.root)],
                    "positive_observations": len(original),
                    "validation_completions": validation_rows,
                    "all_target_completions": len(trace.rows),
                    "events_observed_before_preflight_exit": True,
                    "counts_as_additional_test_method": False})
            finally:
                fixture.close()
            return 0
        groups, tests, _retained, _discovered = plan()
        selected = groups[group]
        Result.trace = trace
        started = time.monotonic()
        result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, failfast=True,
                                        resultclass=Result).run(
            unittest.TestSuite(tests[identity] for identity in selected))
        capture.save(directory / "result.json", {
            "selected": selected, "tests_run": result.testsRun, "passed": result.passed,
            "failures": [(test.id(), detail) for test, detail in result.failures],
            "errors": [(test.id(), detail) for test, detail in result.errors],
            "skips": [(test.id(), detail) for test, detail in result.skipped],
            "seconds": time.monotonic() - started,
            "completion_events": len(trace.rows), "trace_errors": trace.errors,
            "incomplete_target_invocations": list(trace.active.values())})
        return 0 if result.wasSuccessful() and not result.skipped and not trace.errors else 1


def batch(group):
    if group != "preflight":
        proof = OUT / "preflight/exit.json"
        if not proof.exists() or json.loads(proof.read_bytes())["returncode"] != 0:
            raise ValueError("Successful actual completion preflight required")
    directory = OUT / group
    directory.mkdir(exist_ok=False)
    short = Path(tempfile.mkdtemp(prefix="jcb2-")).resolve()
    env = os.environ.copy()
    env.update({key: str(short) for key in ("TEMP", "TMP", "TMPDIR")})
    env.update(PYTHONDONTWRITEBYTECODE="1", BULLETPROOF_PYTHON=sys.executable)
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", "1800", "--",
            sys.executable, "-B", "-u", str(Path(__file__)), "worker", group]
    capture.save(directory / "command.json", {
        "argv": argv, "cwd": str(ROOT), "supervisor_pid": os.getpid(),
        "environment": {key: env[key] for key in ("PATH", "TEMP", "TMP", "TMPDIR",
                                                  "PYTHONDONTWRITEBYTECODE", "BULLETPROOF_PYTHON")},
        "short_temp": str(short), "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    start = time.monotonic()
    with (directory / "output.log").open("xb") as output:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        capture.save(directory / "pid.json", {"runner_pid": process.pid, "supervisor_pid": os.getpid()})
        while data := process.stdout.read1(65536):
            output.write(data)
            output.flush()
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        process.stdout.close()
        code = process.wait()
    capture.save(directory / "exit.json", {"returncode": code, "seconds": time.monotonic() - start})
    entries = list(short.iterdir())
    if not entries:
        short.rmdir()
    capture.save(directory / "cleanup.json", {
        "owned_temp": str(short), "remaining": [str(p) for p in entries],
        "removed_empty_only": not entries, "old_temp_trees": "Untouched; cleanup UNKNOWN"})
    return code


def finish():
    before = json.loads((OUT / "before-pins.json").read_bytes())
    after = capture.pins(before)
    changed = [name for name in before if before[name] != after[name]]
    capture.save(OUT / "after-pins.json", after)
    capture.save(OUT / "freshness.json", {"checked": len(before), "changed": changed})
    groups, _tests, retained, discovered = plan()
    added, failures, unfinished = set(), [], {}
    for group, ids in groups.items():
        path = OUT / group / "result.json"
        if not path.exists():
            unfinished[group] = ids
            continue
        result = json.loads(path.read_bytes())
        if added & set(result["passed"]) or retained & set(result["passed"]):
            raise ValueError("Repeated pass IDs cannot increase accounting")
        added.update(result["passed"])
        failures.extend(result["failures"] + result["errors"] + result["skips"])
        if set(result["passed"]) != set(ids):
            unfinished[group] = sorted(set(ids) - set(result["passed"]))
    passed = retained | added
    capture.save(OUT / "inventory-reconciliation.json", {
        "discovered": sorted(discovered), "retained_204_ids": sorted(retained),
        "newly_passed": sorted(added), "total_passed": len(passed),
        "missing": sorted(discovered - passed), "unfinished": unfinished,
        "failures_errors_skips": failures, "environment_unverified": capture.BLOCKED,
        "all_checkpoint_selectors_except_symlink_passed": discovered - passed == {capture.BLOCKED},
        "preflight_added_methods": 0, "native_entries_retained": {"pair": 5, "reporter": 8}})
    files = {}
    for path in sorted(OUT.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            files[path.relative_to(OUT).as_posix()] = {
                "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    capture.save(OUT / "raw-record-index.json", files)
    print(json.dumps({"pins": len(before), "changed": changed, "retained": len(retained),
                      "newly_passed": len(added), "total_passed": len(passed),
                      "discovered": len(discovered), "missing": sorted(discovered - passed)}), flush=True)
    return 1 if changed or failures or unfinished else 0


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "prepare":
        raise SystemExit(prepare())
    if action == "finish":
        raise SystemExit(finish())
    group = sys.argv[2]
    raise SystemExit(worker(group, OUT / group) if action == "worker" else batch(group))
