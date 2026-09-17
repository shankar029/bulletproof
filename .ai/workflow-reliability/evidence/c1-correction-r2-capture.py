"""Additive C1 r2 evidence capture; excludes unrelated concurrent Q1 tests."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def census():
    paths = set((ROOT / "scripts").glob("*.py"))
    paths.update((ROOT / "scripts/tests").glob("test_workflow*.py"))
    paths.update(ROOT / "scripts/tests" / name for name in (
        "workflow_fixtures.py", "helpers.py", "test_evidence.py"))
    paths.update(p for p in Path(sys.base_prefix).rglob("*")
                 if p.is_file() and p.suffix in (".py", ".pyc", ".pyd", ".dll", ".exe", ".zip"))
    paths.update(ROOT / ".ai/workflow-reliability" / name for name in (
        "design-contracts.json", "guard-resolution-contract.json"))
    paths.update(p for p in HERE.glob("c1-independent-*") if p.is_file())
    paths.add(Path(__file__))
    return {str(p.resolve()): sha(p) for p in sorted(paths)}


def capture(argv, env):
    chunks = [[], []]

    def drain(pipe, destination, output):
        with pipe:
            while data := pipe.read1(4096):
                output.append(data)
                destination.buffer.write(data)
                destination.buffer.flush()

    # argv is itself bounded by run.py; stream progress to the outer idle timer.
    with subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as child:
        threads = [threading.Thread(target=drain, args=args) for args in (
            (child.stdout, sys.stdout, chunks[0]), (child.stderr, sys.stderr, chunks[1]))]
        for thread in threads:
            thread.start()
        code = child.wait()
        for thread in threads:
            thread.join()
    return code, b"".join(chunks[0]), b"".join(chunks[1])


def main():
    label = sys.argv[1]
    patterns = {"red": "test_workflow_core_verification_r2.py",
                "workflow": "test_workflow_*.py", "evidence": "test_evidence.py"}
    pattern = patterns[label]
    base = "c1-correction-r2-" + label
    outputs = {name: HERE / (base + suffix) for name, suffix in (
        ("manifest", ".json"), ("imports", "-imports.json"),
        ("stdout", ".stdout.log"), ("stderr", ".stderr.log"))}
    if any(p.exists() for p in outputs.values()):
        raise FileExistsError("Preserve earlier r2 capture")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               C1_VERIFICATION_IMPORT_MANIFEST=str(outputs["imports"]))
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", "900",
            "--", sys.executable, "-B", "-m", "unittest", "discover",
            "-s", "scripts/tests", "-p", pattern, "-v"]
    before = census()
    started = time.monotonic()
    code, stdout, stderr = capture(argv, env)
    elapsed = time.monotonic() - started
    after = census()
    for stream, content in (("stdout", stdout), ("stderr", stderr)):
        with outputs[stream].open("xb") as file:
            file.write(content)
    imports = json.loads(outputs["imports"].read_text(encoding="utf-8")) if outputs["imports"].exists() else {}
    mismatches = {name: ref for name, ref in imports.items()
                  if before.get(ref["path"]) != ref["sha256"] or after.get(ref["path"]) != ref["sha256"]}
    changed = {name: {"before": before.get(name), "after": after.get(name)}
               for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
    manifest = {"label": label, "argv": argv, "cwd": str(ROOT), "runtime": sys.version,
                "exit_code": code, "elapsed_seconds": elapsed, "before": before, "after": after,
                "changed": changed, "observed_imports": len(imports), "import_mismatches": mismatches,
                "streams": {key: {"path": str(outputs[key]), "sha256": sha(outputs[key]),
                                  "bytes": outputs[key].stat().st_size} for key in ("stdout", "stderr")}}
    with outputs["manifest"].open("x", encoding="utf-8") as file:
        file.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: manifest[key] for key in (
        "label", "exit_code", "elapsed_seconds", "changed", "observed_imports", "import_mismatches")}))
    print("Pinned files:", len(before))
    return code if not changed and not mismatches else 2


if __name__ == "__main__":
    sys.exit(main())
