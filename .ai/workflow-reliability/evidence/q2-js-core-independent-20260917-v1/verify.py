"""Independent frozen-checkpoint capture. Never changes source or owner evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
EVIDENCE = OUT.parent
sys.path[:0] = [str(ROOT / "scripts/tests"), str(ROOT / "scripts")]
from run import run_capture
import measure
from test_measure_source_bindings import source_tools

SEAL_HASH = "7befec79cce53797b158d62f80f412b2efdf05080c1e7c28a8b2cd48f9e1f0fa"


def save(name, value):
    with (OUT / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def pin(path):
    path = Path(path)
    data = path.read_bytes()
    info = path.stat()
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data), "dev": info.st_dev, "ino": info.st_ino,
            "nlink": info.st_nlink}


def command(argv):
    code, stdout, stderr = run_capture(argv, cwd=str(ROOT), idle=30, max_total=90)
    assert code == 0, (argv, code, stdout, stderr)
    return {"argv": argv, "returncode": code, "stdout": stdout, "stderr": stderr}


def snapshot(label):
    seal_path = EVIDENCE / "q2-js-seal.json"
    assert pin(seal_path)["sha256"] == SEAL_HASH
    seal = json.loads(seal_path.read_bytes())
    frozen = []
    for ref in seal["owned_files"] + seal["unchanged_inputs"]:
        actual = pin(ROOT / ref["path"])
        assert (actual["sha256"], actual["bytes"]) == (ref["sha256"], ref["bytes"]), ref
        frozen.append(actual)
    print("Matched 28 owner artifacts and 10 unchanged input pins", flush=True)
    config = {"tools": source_tools(), "tool_artifact_root": str(EVIDENCE)}
    qualified = measure._qualified_inputs(config, [ROOT])
    baseline = measure.baseline_binding()
    paths = {str(ROOT / ref["path"]) for ref in seal["owned_files"] + seal["unchanged_inputs"]}
    paths.add(str(seal_path))
    paths.update(str(EVIDENCE / ref["path"]) for ref in measure.tool_artifacts(config))
    for description in qualified.values():
        paths.add(description["executable"]["path"])
        paths.update(item["path"] for item in description["dependencies"])
        paths.update(item["path"] for item in description["source"]["resources"])
        paths.update(item["path"] for item in description["source"]["runtime_imports"])
    git = Path(baseline["git"]["path"])
    paths.add(str(git))
    paths.update(str(git.parent / name) for name in baseline["git"]["bundled_dlls"])
    paths.add(str(Path(os.environ["Q2_IV_GIT"]) / "git.exe"))
    paths.update(str(ROOT / name) for name in (
        "scripts/tests/helpers.py", "scripts/tests/test_measure_inventory.py",
        "scripts/tests/test_measure_graph.py", "scripts/tests/test_measure_q2.py",
        "scripts/native_result.mjs", "evals/lib/score.mjs", "CONTRIBUTING.md",
        ".ai/workflow-reliability/evidence/q2-js-execution-rationale.md"))
    pins = [pin(path) for path in sorted(paths)]
    head = command([str(git), "--no-pager", "rev-parse", "HEAD"])
    assert head["stdout"].strip() == seal["head"]
    status = command([str(git), "--no-pager", "status", "--porcelain", "--untracked-files=all"])
    result = {"label": label, "seal_sha256": SEAL_HASH, "head": head,
              "git_status": status, "frozen": frozen, "pins": pins,
              "qualified": qualified, "baseline": baseline,
              "python": {"executable": sys.executable, "version": sys.version},
              "environment": {k: os.environ.get(k) for k in (
                  "PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "PYTHONPATH",
                  "TEMP", "TMP", "Q2_JS_RECORDS", "Q2_SOURCE_RECORDS")}}
    save(label + ".json", result)
    if label == "after":
        before = json.loads((OUT / "before.json").read_bytes())
        assert before["pins"] == pins, "Before/after input bytes or physical identities differ"
        assert before["qualified"] == qualified
        assert before["baseline"] == baseline
    print(label, "reconciled", len(pins), "distinct file pins", flush=True)


def replay():
    seal = json.loads((EVIDENCE / "q2-js-seal.json").read_bytes())
    methods = seal["validation"]["unittest_methods"]
    assert len(methods) == 15 and len(set(methods)) == 15
    # Explicit method names avoid accidentally including a later added method.
    argv = [sys.executable, "-B", "-u", str(ROOT / "scripts/run.py"),
            "--idle", "120", "--max", "1800", "--",
            sys.executable, "-B", "-u", "-m", "unittest", "-v", *methods]
    env = dict(os.environ)
    env["Q2_JS_RECORDS"] = str(OUT)
    env["Q2_SOURCE_RECORDS"] = str(OUT)
    save("invocation.json", {"argv": argv, "cwd": str(ROOT), "methods": methods,
                            "environment": {k: env.get(k) for k in (
                                "PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING",
                                "PYTHONPATH", "PATH", "TEMP", "TMP",
                                "Q2_JS_RECORDS", "Q2_SOURCE_RECORDS")},
                            "child_limits": {"idle": 30, "max": 90},
                            "outer_limits": {"idle": 120, "max": 1800}})
    started = time.monotonic()
    with (OUT / "unittest.log").open("x", encoding="utf-8") as log:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                   errors="replace", bufsize=1)
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log.write(line)
            log.flush()
        code = process.wait()
    save("replay-result.json", {"returncode": code, "wall_seconds": time.monotonic() - started})
    raise SystemExit(code)


if __name__ == "__main__":
    {"before": lambda: snapshot("before"), "after": lambda: snapshot("after"),
     "replay": replay}[sys.argv[1]]()
