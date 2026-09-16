"""Independent I1 command capture. No production edits or publication."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / ".ai/workflow-reliability/evidence"
PY = r"C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe"
NODE = r"C:\Program Files\nodejs\node.exe"
ENV_DELTA = {"PYTHONDONTWRITEBYTECODE": "1", "NODE_TEST_CONTEXT": None, "BP_TEST_PYTHON": PY}
ENV = os.environ.copy()
for key, value in ENV_DELTA.items():
    if value is None:
        ENV.pop(key, None)
    else:
        ENV[key] = value


def save(name, data):
    (OUT / ("i1-independent-" + name + ".json")).write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def run(name, argv, *, max_seconds=900):
    expanded = [PY, "-B", "scripts/run.py", "--idle", "120", "--max", str(max_seconds), "--", *argv]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    timer = time.monotonic()
    print(json.dumps({"name": name, "argv": expanded, "cwd": str(ROOT)}), flush=True)
    proc = subprocess.Popen(expanded, cwd=ROOT, env=ENV, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    chunks = []
    for line in iter(proc.stdout.readline, b""):
        chunks.append(line)
        if name not in {"probe", "probe-frozen", "diff-check"} or line.startswith(b"probe:"):
            print(line.decode("utf-8", errors="replace"), end="", flush=True)
    proc.wait(timeout=30)
    proc.stdout.close()
    result = subprocess.CompletedProcess(expanded, proc.returncode, b"".join(chunks))
    log = OUT / ("i1-independent-" + name + ".log")
    log.write_bytes(result.stdout)
    record = {"name": name, "argv": expanded, "cwd": str(ROOT), "environment_delta": ENV_DELTA,
              "started": started, "finished": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "duration_seconds": round(time.monotonic() - timer, 3), "exit_code": result.returncode,
              "idle_seconds": 120, "max_seconds": max_seconds, "log": str(log.relative_to(ROOT)),
              "log_sha256": hashlib.sha256(result.stdout).hexdigest()}
    save(name, record)
    print(json.dumps(record), flush=True)
    return result


def snapshot(name):
    files = {}
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv"}]
        for filename in names:
            path = Path(base) / filename
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith(".ai/workflow-reliability/evidence/i1-independent-"):
                continue
            data = path.read_bytes()
            files[rel] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    save(name, {"cwd": str(ROOT), "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "scope": "All regular files except .git/node_modules/__pycache__/.venv and own i1-independent evidence",
                "files": files})
    print(f"{name}: {len(files)} files hashed", flush=True)


def preserved_run(name, argv, paths):
    before = {p: p.read_bytes() if p.exists() else None for p in paths}
    try:
        result = run(name, argv)
        for p in paths:
            if p.exists():
                suffix = p.relative_to(ROOT).as_posix().replace("/", "-")
                (OUT / ("i1-independent-" + name + "-" + suffix)).write_bytes(p.read_bytes())
        return result
    finally:
        for p, data in before.items():
            if data is None:
                p.unlink(missing_ok=True)
            else:
                p.write_bytes(data)


def main():
    name = sys.argv[1]
    if name == "reconcile":
        before = json.loads((OUT / "i1-independent-before.json").read_bytes())["files"]
        checkpoint = json.loads((OUT / "i1-independent-checkpoint.json").read_bytes())["files"]
        after = json.loads((OUT / "i1-independent-after.json").read_bytes())["files"]
        def delta(left, right):
            return {p: {"before": left.get(p), "after": right.get(p)}
                    for p in sorted(set(left) | set(right)) if left.get(p) != right.get(p)}
        result = {"initial_to_final": delta(before, after), "checkpoint_to_final": delta(checkpoint, after),
                  "key_source_hashes": {p: after[p] for p in after if
                      p in {"scripts/probe.py", "scripts/mutate.py", "scripts/native_result.mjs",
                            "scripts/evidence.py", "scripts/run.py", "evals/lib/score.mjs",
                            "scripts/tests/test_measurement_e2e.py", "scripts/tests/test_probe.py"}}}
        save("reconciliation", result)
        print(json.dumps(result, indent=2))
    elif name in {"before", "after", "checkpoint", "frozen"}:
        snapshot(name)
    elif name == "environment":
        for label, argv in [
            ("python-version", [PY, "--version"]), ("node-version", [NODE, "--version"]),
            ("git-version", ["git", "--version"]),
            ("git-status-before", ["git", "--no-pager", "status", "--porcelain=v1", "-uall"]),
            ("git-head", ["git", "--no-pager", "log", "-1", "--format=%H %D"]),
            ("git-remotes", ["git", "remote", "-v"]),
            ("git-branches", ["git", "--no-pager", "branch", "--list"]),
        ]:
            run(label, argv)
    elif name == "python":
        run(name, [PY, "-B", "-m", "unittest", "discover", "-s", "scripts/tests", "-v"])
    elif name in {"measurement-e2e", "measurement-e2e-retry"}:
        run(name, [PY, "-B", "-m", "unittest", "discover", "-s", "scripts/tests",
                   "-p", "test_measurement_e2e.py", "-v"])
    elif name == "probe-tests-current":
        run(name, [PY, "-B", "-m", "unittest", "discover", "-s", "scripts/tests",
                   "-p", "test_probe.py", "-v"])
    elif name == "probe-tests-reanchor":
        paths = ["scripts/probe.py", "scripts/tests/test_probe.py"]
        def hashes():
            return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
        before = hashes()
        result = run(name, [PY, "-B", "-m", "unittest", "discover", "-s", "scripts/tests",
                            "-p", "test_probe.py", "-v"])
        after = hashes()
        save(name + "-sources", {"before": before, "after": after,
                                 "unchanged": before == after, "test_exit": result.returncode})
    elif name == "probe-final-schema":
        paths = ["scripts/probe.py", "scripts/tests/test_probe.py",
                 "scripts/tests/test_measurement_e2e.py", "scripts/mutate.py",
                 "scripts/native_result.mjs", "scripts/evidence.py", "scripts/run.py",
                 "evals/lib/score.mjs"]
        def hashes():
            return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
        before = hashes()
        save(name + "-before", before)
        results = {}
        for label, pattern in [("probe-frozen-suite", "test_probe.py"),
                               ("measurement-frozen-suite", "test_measurement_e2e.py")]:
            result = run(label, [PY, "-B", "-m", "unittest", "discover", "-s", "scripts/tests",
                                 "-p", pattern, "-v"])
            results[label] = result.returncode
        after = hashes()
        save(name + "-sources", {"before": before, "after": after,
                                 "unchanged": before == after, "test_exits": results})
    elif name == "native":
        run(name, [NODE, "--test", "evals/lib/mutate.test.mjs", "evals/lib/native_result.test.mjs",
                   "evals/lib/score.test.mjs", "evals/agent/agent.test.mjs"])
    elif name == "eval":
        preserved_run(name, [NODE, "evals/run.mjs"],
                      [ROOT / "evals/report.md", ROOT / "evals/report.json"])
    elif name in {"probe", "probe-frozen"}:
        sys.path.insert(0, str(ROOT / "scripts"))
        from evidence import source_snapshot
        runs = ROOT / ".ai/workflow-reliability/evidence/runs"
        existing = set(runs.iterdir()) if runs.exists() else set()
        try:
            preserved_run(name, [PY, "-B", "scripts/probe.py", "--slug", "workflow-reliability",
                                 "--base", "bcc971d3b64559127dfc43eb0bfd4348c42803ca",
                                 "--test-cwd", ".", "--", NODE, "--test", "evals/lib/mutate.test.mjs",
                                 "evals/lib/score.test.mjs", "evals/agent/agent.test.mjs",
                                 "evals/lib/native_result.test.mjs"],
                          [ROOT / ".ai/workflow-reliability/metrics.json"])
        finally:
            for directory in set(runs.iterdir()) - existing:
                metrics_path = directory / "metrics.json"
                if metrics_path.exists():
                    metrics = json.loads(metrics_path.read_bytes())
                    observed = source_snapshot(ROOT, metrics["source"]["scope"])
                    save(name + "-freshness", {"run_id": metrics["run_id"],
                                            "report_hash": metrics["source"]["scope_sha256"],
                                            "observed_hash": observed["scope_sha256"],
                                            "fresh": observed["scope_sha256"] == metrics["source"]["scope_sha256"],
                                            "note": "After publication and display-alias restoration; before moving owned run into verifier evidence"})
                shutil.move(str(directory), str(OUT / ("i1-independent-probe-run-" + directory.name)))
    elif name == "dry-run":
        run(name, [NODE, "evals/agent/live.mjs", "--task", "paginator", "--dry-run"])
    elif name in {"diff-check", "diff-check-attributes"}:
        run(name, ["git", "--no-pager", "diff", "--check", "bcc971d3b64559127dfc43eb0bfd4348c42803ca"])
    elif name == "diff-check-working":
        run(name, ["git", "--no-pager", "diff", "--check"])
    else:
        raise ValueError(name)


if __name__ == "__main__":
    main()
