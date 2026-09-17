"""One owned archive-based C1 composition replay; never edits production."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from datetime import datetime, timezone

ROOT = Path.cwd().resolve()
EVIDENCE = ROOT / ".ai/workflow-reliability/evidence"
TAG = "c1-standalone-preservation"
BASE = "0b7e1a1f6fd1f807bd254886e2877d605596d96d"
OVERLAYS = [
    "scripts/workflow_state.py", "scripts/workflow_gate.py",
    "scripts/tests/workflow_fixtures.py",
    "scripts/tests/test_workflow_state.py", "scripts/tests/test_workflow_gate.py",
    "scripts/tests/test_workflow_core_verification.py",
    "scripts/tests/test_workflow_core_verification_r2.py",
]
MANIFEST = EVIDENCE / (TAG + "-manifest.json")
assert not MANIFEST.exists(), "Refuse to overwrite a prior standalone replay"


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def pin(paths):
    return {str(p): sha(p) for p in sorted(map(str, paths))}


def delta(before, after):
    return [
        {"path": p, "before": before.get(p), "after": after.get(p)}
        for p in sorted(set(before) | set(after))
        if before.get(p) != after.get(p)
    ]


m = {"started_utc": utc(), "baseline_sha": BASE, "controller_cwd": str(ROOT),
     "python": sys.executable, "runs": [], "overlay_paths": OVERLAYS}
owned = None


def save():
    MANIFEST.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")


def execute(name, argv, cwd, env):
    print("START " + name + " " + json.dumps(argv), flush=True)
    run = {"name": name, "argv": argv, "cwd": str(cwd), "started_utc": utc()}
    start = time.monotonic()
    proc = subprocess.Popen(argv, cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    chunks = {"stdout": [], "stderr": []}

    def consume(stream, key):
        while chunk := stream.read1(65536):
            chunks[key].append(chunk)
            sys.stdout.write(chunk.decode("utf-8", errors="replace"))
            sys.stdout.flush()

    threads = [
        threading.Thread(target=consume, args=(proc.stdout, "stdout")),
        threading.Thread(target=consume, args=(proc.stderr, "stderr")),
    ]
    for thread in threads:
        thread.start()
    run["exit_code"] = proc.wait()
    for thread in threads:
        thread.join()
    run["elapsed_seconds"] = round(time.monotonic() - start, 3)
    for key, parts in chunks.items():
        data = b"".join(parts)
        path = EVIDENCE / (TAG + "-" + name + "." + key + ".log")
        assert not path.exists()
        path.write_bytes(data)
        run[key] = {"path": str(path), "sha256": sha(path), "bytes": len(data)}
    text = b"".join(chunks["stdout"]).decode("utf-8", errors="replace")
    if match := re.search(r"Ran (\d+) tests in ([\d.]+)s", text):
        run["unittest_summary"] = {"tests": int(match[1]), "seconds": float(match[2])}
        run["unittest_ok"] = bool(re.search(r"^OK\s*$", text, re.M))
    run["scaling_lines"] = [line for line in text.splitlines() if "C1 R3 scale:" in line]
    m["runs"].append(run)
    save()
    return run, text


# Executed in memory by the candidate interpreter; no candidate file is added.
# The hook records real imports/exec origins and subprocess dispatches. It does
# not replace unittest, product functions, or test results.
HARNESS = r'''
import atexit, hashlib, json, os, runpy, sys
from pathlib import Path
candidate = Path(os.environ["C1_CANDIDATE_ROOT"]).resolve()
managed = Path(sys.base_prefix).resolve()
original = Path(os.environ["C1_FORBIDDEN_ROOT"]).resolve()
destination = Path(os.environ["C1_RUNTIME_INVENTORY"])
exec_files = set()
import_events = set()
children = []
def audit(event, args):
    if event == "exec":
        filename = args[0].co_filename
        if filename and not filename.startswith("<"):
            exec_files.add(str(Path(filename).resolve()))
    elif event == "import" and len(args) > 1 and args[1]:
        import_events.add(str(Path(args[1]).resolve()))
    elif event == "subprocess.Popen":
        children.append({"executable": str(args[0]), "argv": args[1],
                         "cwd": str(args[2]) if args[2] else None})
sys.addaudithook(audit)
sys.argv = ["unittest", "discover", "-s", "scripts/tests", "-p",
            os.environ["C1_TEST_PATTERN"], "-v"]
exit_code = 0
try:
    runpy.run_module("unittest", run_name="__main__", alter_sys=True)
except SystemExit as exc:
    exit_code = exc.code
finally:
    modules = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename and Path(filename).is_file():
            path = Path(filename).resolve()
            modules[name] = {"path": str(path),
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    paths = set(v["path"] for v in modules.values()) | exec_files | import_events
    observed = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
                for p in sorted(paths) if Path(p).is_file()}
    violations = [p for p in paths
                  if not (Path(p).is_relative_to(candidate)
                          or Path(p).is_relative_to(managed))]
    path_violations = [p for p in sys.path
                       if not (Path(p or os.getcwd()).resolve().is_relative_to(candidate)
                               or Path(p or os.getcwd()).resolve().is_relative_to(managed))]
    child_leaks = [child for child in children
                   if str(original).casefold() in
                   json.dumps(child).replace("\\\\", "\\").casefold()]
    payload = {"modules": modules, "observed_files": observed,
               "exec_files": sorted(exec_files), "import_events": sorted(import_events),
               "sys_path": sys.path, "flags": repr(sys.flags),
               "candidate": str(candidate), "managed": str(managed),
               "cwd": os.getcwd(), "subprocess_dispatches": children,
               "origin_violations": violations, "sys_path_violations": path_violations,
               "worktree_child_dispatch_leaks": child_leaks,
               "unittest_exit_code": exit_code}
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if violations or path_violations or child_leaks:
        print("IMPORT ISOLATION FAILURE", violations, path_violations, child_leaks)
        exit_code = 98
raise SystemExit(exit_code)
'''

try:
    r5 = json.loads((EVIDENCE / "c1-independent-r5-manifest.json").read_text())
    protected = set(r5["after"])
    protected.update(str(p.resolve()) for p in EVIDENCE.glob("c1-independent-*") if p.is_file())
    protected.add(str(EVIDENCE / "c1-code-review-r2.md"))
    m["original_before"] = pin(protected)
    m["overlay_sources"] = {}
    for rel in OVERLAYS:
        path = ROOT / rel
        actual = sha(path)
        expected = r5["after"][str(path)]
        assert actual == expected, ("Accepted overlay changed", rel)
        m["overlay_sources"][rel] = {"source": str(path), "sha256": actual,
                                     "bytes": path.stat().st_size}
    discovered = {str(p.relative_to(ROOT)).replace("\\", "/")
                  for p in (ROOT / "scripts/tests").glob("test_workflow_*.py")}
    assert discovered == {p for p in OVERLAYS if "/test_workflow_" in p}, discovered

    owned = Path(tempfile.mkdtemp(prefix="c1-standalone-owned-")).resolve()
    candidate = owned / "candidate"
    candidate.mkdir()
    fixtures = owned / "fixtures"
    fixtures.mkdir()
    audit_dir = owned / "audit"
    audit_dir.mkdir()
    archive = owned / "baseline.tar"
    m["owned_root"] = str(owned)
    m["candidate_root"] = str(candidate)
    m["creation"] = "git archive of exact committed SHA; regular files copied from tar, no links"
    env = os.environ.copy()
    removed = {}
    for key in tuple(env):
        if key in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONINSPECT",
                   "C1_VERIFICATION_IMPORT_MANIFEST") or key.startswith("GIT_"):
            removed[key] = "removed"
            del env[key]
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1",
               TMPDIR=str(fixtures), TEMP=str(fixtures), TMP=str(fixtures))
    m["environment_sanitization"] = removed
    m["test_environment_delta"] = {k: env[k] for k in
                                  ("PYTHONDONTWRITEBYTECODE", "PYTHONNOUSERSITE",
                                   "TMPDIR", "TEMP", "TMP")}
    bootstrap = [sys.executable, "-I", "-B", str(ROOT / "scripts/run.py"),
                 "--idle", "120", "--max", "1200", "--"]
    head, text = execute("baseline", bootstrap + ["git", "rev-parse", "HEAD"], ROOT, env)
    assert head["exit_code"] == 0 and text.strip() == BASE, text
    result, _ = execute("archive", bootstrap + [
        "git", "archive", "--format=tar", "--output=" + str(archive), BASE], ROOT, env)
    assert result["exit_code"] == 0
    m["archive"] = {"sha256": sha(archive), "bytes": archive.stat().st_size}
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            path = (candidate / member.name).resolve()
            assert path.is_relative_to(candidate), member.name
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                assert member.isfile() and not member.issym() and not member.islnk(), member.name
                assert not path.exists(), member.name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(tar.extractfile(member).read())
    m["baseline_tree"] = pin(p.resolve() for p in candidate.rglob("*") if p.is_file())
    for rel in OVERLAYS:
        target = candidate / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / rel).read_bytes())
        assert sha(target) == m["overlay_sources"][rel]["sha256"]
    m["candidate_before"] = pin(p.resolve() for p in candidate.rglob("*") if p.is_file())
    m["composition_delta"] = delta(m["baseline_tree"], m["candidate_before"])
    assert {d["path"] for d in m["composition_delta"]} <= {str(candidate / p) for p in OVERLAYS}
    assert not (candidate / "scripts/measure.py").exists()
    assert not (candidate / "scripts/measure_graph.py").exists()
    assert sha(candidate / "scripts/probe.py") == m["baseline_tree"][str(candidate / "scripts/probe.py")]
    m["candidate_probe_sha256"] = sha(candidate / "scripts/probe.py")
    runtime = Path(sys.base_prefix).resolve()
    runtime_paths = [p for p in r5["after"] if Path(p).is_relative_to(runtime)]
    m["managed_runtime_before"] = pin(runtime_paths)
    m["suite_results"] = []
    for name, pattern, count in (
        ("workflow", "test_workflow_*.py", 83), ("evidence", "test_evidence.py", 10)
    ):
        before = pin(list(m["candidate_before"]) + runtime_paths)
        inventory = audit_dir / (name + "-imports.json")
        child_env = dict(env, C1_CANDIDATE_ROOT=str(candidate),
                         C1_FORBIDDEN_ROOT=str(ROOT), C1_RUNTIME_INVENTORY=str(inventory),
                         C1_TEST_PATTERN=pattern)
        if name == "workflow":
            child_env["C1_VERIFICATION_IMPORT_MANIFEST"] = str(audit_dir / "workflow-middle-imports.json")
        argv = [sys.executable, "-I", "-B", str(candidate / "scripts/run.py"),
                "--idle", "120", "--max", "1200", "--",
                sys.executable, "-I", "-B", "-c", HARNESS]
        result, _ = execute(name, argv, candidate, child_env)
        after = pin(before)
        result["before"] = before
        result["after"] = after
        result["changed_inputs"] = delta(before, after)
        result["environment_delta"] = {k: v for k, v in child_env.items() if k.startswith("C1_")}
        assert inventory.is_file(), "Missing suite import evidence"
        observation = json.loads(inventory.read_text())
        final_inventory = EVIDENCE / (TAG + "-" + name + "-imports.json")
        assert not final_inventory.exists()
        final_inventory.write_bytes(inventory.read_bytes())
        result["import_inventory"] = {"path": str(final_inventory), "sha256": sha(final_inventory)}
        result["import_checks"] = {
            p: {"before": before.get(p), "observed": h, "after": after.get(p),
                "matches": before.get(p) == h == after.get(p)}
            for p, h in observation["observed_files"].items()
        }
        result["isolation_passed"] = not (
            observation["origin_violations"] or observation["sys_path_violations"]
            or observation["worktree_child_dispatch_leaks"]
        )
        m["suite_results"].append({
            "name": name, "tests": result.get("unittest_summary"),
            "exit_code": result["exit_code"],
            "file_backed_modules": len(observation["modules"]),
            "observed_files": len(observation["observed_files"]),
            "isolation_passed": result["isolation_passed"],
        })
        save()
        assert result["exit_code"] == 0 and result.get("unittest_ok"), "Suite failed; no retry"
        assert result["unittest_summary"]["tests"] == count, "Unexpected discovered count"
        assert not result["changed_inputs"], "Runtime changed"
        assert all(c["matches"] for c in result["import_checks"].values()), "Unpinned runtime"
        assert result["isolation_passed"], "Worktree/runtime leakage"
    m["verdict"] = "VERIFIED-WITH-LIMITATIONS"
except BaseException as exc:
    m["verdict"] = "NOT-VERIFIED"
    m["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    print("STANDALONE FAILURE " + repr(exc), flush=True)
finally:
    if "candidate_before" in m:
        m["candidate_after"] = pin(p.resolve() for p in candidate.rglob("*") if p.is_file())
        m["candidate_changes"] = delta(m["candidate_before"], m["candidate_after"])
        if m["candidate_changes"]:
            m["verdict"] = "BLOCKED-FRESHNESS"
    if "managed_runtime_before" in m:
        m["managed_runtime_after"] = pin(runtime_paths)
        m["managed_runtime_changes"] = delta(m["managed_runtime_before"], m["managed_runtime_after"])
        if m["managed_runtime_changes"]:
            m["verdict"] = "BLOCKED-FRESHNESS"
    if "original_before" in m:
        m["original_after"] = pin(m["original_before"])
        m["original_changes"] = delta(m["original_before"], m["original_after"])
        if m["original_changes"]:
            m["verdict"] = "BLOCKED-FRESHNESS"
    if owned is not None:
        assert owned.name.startswith("c1-standalone-owned-") and owned != ROOT
        m["remaining_fixture_paths_before_cleanup"] = [
            str(p.relative_to(owned)) for p in fixtures.rglob("*")
        ]
        try:
            shutil.rmtree(owned)
            m["cleanup"] = {"owned_path": str(owned), "removed": not owned.exists()}
        except OSError as exc:
            m["cleanup"] = {"owned_path": str(owned), "removed": False, "error": str(exc)}
            m["verdict"] = "NOT-VERIFIED"
    m["finished_utc"] = utc()
    save()
    print("STANDALONE SUMMARY " + json.dumps({
        k: m.get(k) for k in ("verdict", "failure", "suite_results", "original_changes",
                             "candidate_changes", "managed_runtime_changes", "cleanup")
    }), flush=True)
