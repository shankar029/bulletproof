"""Exclusive independent correction proof; source/tests remain read-only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
OWNER = HERE.parent / "q2-js-serialization-corrections-01"
SEAL_HASH = "c138dec76b7abc47b334caf5e77e99236154583bf745573312c8b5d44a04fa5b"
PYTHON = r"C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe"


def artifact(path):
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def reconcile(label):
    seal_ref = artifact(OWNER / "seal.json")
    assert seal_ref["sha256"] == SEAL_HASH, "Correction seal changed"
    seal = json.loads((OWNER / "seal.json").read_bytes())
    refs = {}
    groups = ["changed_source_files", "unchanged_independent_tests", "historical_references", "owned_evidence"]
    for group in groups:
        for ref in seal[group]:
            if ref["path"] in refs:
                assert refs[ref["path"]] == ref
            refs[ref["path"]] = ref
    # Read the preservation catalogue only after checking its new seal pin.
    catalogue_ref = seal["preservation"]["after"]
    assert artifact(ROOT / catalogue_ref["path"]) == catalogue_ref
    catalogue = json.loads((ROOT / catalogue_ref["path"]).read_bytes())
    assert len(catalogue) == 199
    for ref in catalogue:
        if ref["path"] in refs:
            assert refs[ref["path"]] == ref
        refs[ref["path"]] = ref
    rows = [artifact(ROOT / name) for name in sorted(refs)]
    mismatches = [row for row in rows if row != refs[row["path"]]]
    snapshot = artifact(HERE.parent / "q2-js-serialization-pre-fix.mjs.snapshot")
    assert snapshot["sha256"] == "35acb58ccd11dce9daa601e640c47b763e8625c84919158610cf33107f4b46bc"
    sys.path.insert(0, str(ROOT / "scripts"))
    from run import run_capture
    argv = ["git", "rev-parse", "HEAD"]
    code, stdout, stderr = run_capture(argv, cwd=str(ROOT), idle=30, max_total=60)
    # Retain return/streams before using HEAD content.
    save(HERE / (label + ".json"), {
        "owner_seal": seal_ref, "catalogue": catalogue_ref, "catalogue_paths": len(catalogue),
        "reconciled_unique_paths": len(rows), "mismatches": mismatches,
        "observed_catalogue_sha256": hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "current_code_and_tests": [row for row in rows if row["path"].startswith("scripts/")],
        "pre_fix_source_snapshot": snapshot,
        "head_observation": {"argv": argv, "cwd": str(ROOT), "returncode": code,
                             "stdout": stdout, "stderr": stderr, "idle_seconds": 30, "max_seconds": 60},
    })
    assert not mismatches, mismatches
    assert code == 0 and stdout.strip() == seal["head"], "HEAD mismatch"
    print(f"{label}: {len(rows)} unique correction/catalogue pins match; retained red-source hash matches", flush=True)


def execute(label):
    selection = {
        "independent": ["-p", "test_measure_js_serialization_independent.py", "-v"],
        "owner": ["-p", "test_measure_js.py", "-k", "review_corrections",
                  "-k", "serialized_source_records", "-k", "serialized_freshness",
                  "-k", "candidates_from_shared_syntax", "-v"],
        "owner-candidate-retry": ["-p", "test_measure_js.py", "-k", "candidates_from_shared_syntax", "-v"],
    }[label]
    folder = HERE / label
    folder.mkdir(exist_ok=False)
    argv = [PYTHON, "-B", "-u", r"scripts\run.py", "--idle", "120", "--max", "900", "--",
            PYTHON, "-B", "-u", "-m", "unittest", "discover", "-s", r"scripts\tests", *selection]
    env = dict(os.environ)
    env["PATH"] = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd" + os.pathsep + env["PATH"]
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", Q2_JS_RECORDS=str(folder))
    save(folder / "invocation.json", {
        "argv": argv, "cwd": str(ROOT), "outer_idle_seconds": 120, "outer_max_seconds": 900,
        "native_idle_seconds": 30, "native_max_seconds": 90,
        "environment": {key: env[key] for key in ("PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "Q2_JS_RECORDS")},
        "path_prefix": env["PATH"].split(os.pathsep)[0],
    })
    started = time.monotonic()
    with (folder / "stdout.bin").open("xb") as out, (folder / "stderr.bin").open("xb") as err:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def pump(source, target, console):
            while block := source.read1(4096):
                target.write(block)
                target.flush()
                console.buffer.write(block)
                console.flush()

        threads = [threading.Thread(target=pump, args=(process.stdout, out, sys.stdout)),
                   threading.Thread(target=pump, args=(process.stderr, err, sys.stderr))]
        for thread in threads:
            thread.start()
        code = process.wait()
        for thread in threads:
            thread.join()
    save(folder / "exit.json", {"returncode": code, "elapsed_seconds": time.monotonic() - started,
                               "stdout": artifact(folder / "stdout.bin"), "stderr": artifact(folder / "stderr.bin")})
    print(f"{label}: exit {code}; raw streams persisted before interpretation", flush=True)
    return code


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode in ("independent", "owner", "owner-candidate-retry"):
        reconcile("before" if mode == "independent" else "before-" + mode)
        sys.exit(execute(mode))
    else:
        reconcile(mode)
