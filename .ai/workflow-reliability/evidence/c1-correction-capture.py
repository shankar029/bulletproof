"""Bounded C1 correction evidence capture; not workflow proof or quality tooling."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def census():
    paths = {p.resolve() for p in (ROOT / "scripts").rglob("*.py")}
    paths.update(p.resolve() for p in Path(sys.base_prefix).rglob("*")
                 if p.is_file() and p.suffix in (".py", ".pyc", ".pyd", ".dll", ".exe", ".zip"))
    paths.update(ROOT / name for name in (
        ".ai/workflow-reliability/design-contracts.json",
        ".ai/workflow-reliability/guard-resolution-contract.json",
        ".ai/workflow-reliability/evidence/c1-boundary-review.md",
        ".ai/workflow-reliability/evidence/c1-independent-verification.md",
    ))
    paths.add(Path(__file__).resolve())
    return {str(path): sha(path) for path in sorted(paths)}


def main():
    label, pattern = sys.argv[1:]
    if label not in ("red", "workflow", "evidence") or pattern not in (
            "test_workflow_core_verification.py", "test_workflow_*.py", "test_evidence.py"):
        raise ValueError("Unregistered capture selection")
    prefix = HERE / ("c1-correction-" + label)
    manifest_path = prefix.with_suffix(".json")
    if manifest_path.exists():
        raise FileExistsError("Preserve earlier correction capture: " + str(manifest_path))
    imports_path = HERE / ("c1-correction-" + label + "-imports.json")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               C1_VERIFICATION_IMPORT_MANIFEST=str(imports_path))
    before = census()
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", "900",
            "--", sys.executable, "-B", "-m", "unittest", "discover",
            "-s", "scripts/tests", "-p", pattern, "-v"]
    start = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = time.monotonic() - start
    after = census()
    stdout_path = HERE / ("c1-correction-" + label + ".stdout.log")
    stderr_path = HERE / ("c1-correction-" + label + ".stderr.log")
    stdout_path.write_bytes(result.stdout)
    stderr_path.write_bytes(result.stderr)
    imports = json.loads(imports_path.read_text(encoding="utf-8")) if imports_path.exists() else {}
    import_mismatches = {
        name: observation for name, observation in imports.items()
        if before.get(observation["path"]) != observation["sha256"]
        or after.get(observation["path"]) != observation["sha256"]
    }
    changed = {p: {"before": before.get(p), "after": after.get(p)}
               for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    manifest = {
        "label": label, "argv": argv, "cwd": str(ROOT), "python": sys.version,
        "exit_code": result.returncode, "elapsed_seconds": elapsed,
        "before": before, "after": after, "changed": changed,
        "observed_imports": len(imports), "import_mismatches": import_mismatches,
        "stdout": {"path": str(stdout_path), "sha256": sha(stdout_path)},
        "stderr": {"path": str(stderr_path), "sha256": sha(stderr_path)},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result.stdout.decode("utf-8", errors="replace"))
    print(result.stderr.decode("utf-8", errors="replace"))
    print(json.dumps({k: manifest[k] for k in (
        "label", "exit_code", "elapsed_seconds", "changed", "observed_imports", "import_mismatches")}))
    print("Pinned files:", len(before))
    return result.returncode if not changed and not import_mismatches else 2


if __name__ == "__main__":
    sys.exit(main())
