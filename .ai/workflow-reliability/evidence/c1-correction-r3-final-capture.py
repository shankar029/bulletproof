"""Final bounded replay, retaining the initial correction capture unchanged."""

import json
import os
from pathlib import Path
import runpy
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORIGINAL = runpy.run_path(str(HERE / "c1-correction-r3-capture.py"))


def census():
    result = ORIGINAL["census"]()
    result[str(Path(__file__).resolve())] = ORIGINAL["sha"](Path(__file__))
    return result


def main():
    label = sys.argv[1]
    pattern = {"workflow": "test_workflow_*.py", "evidence": "test_evidence.py"}[label]
    base = "c1-correction-r3-final-" + label
    outputs = {name: HERE / (base + suffix) for name, suffix in (
        ("manifest", ".json"), ("imports", "-imports.json"),
        ("stdout", ".stdout.log"), ("stderr", ".stderr.log"))}
    if any(p.exists() for p in outputs.values()):
        raise FileExistsError("Preserve earlier final replay")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               C1_VERIFICATION_IMPORT_MANIFEST=str(outputs["imports"]))
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "120", "--max", "900",
            "--", sys.executable, "-B", "-m", "unittest", "discover",
            "-s", "scripts/tests", "-p", pattern, "-v"]
    before = census()
    started = time.monotonic()
    code, stdout, stderr = ORIGINAL["capture"](argv, env)
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
                "streams": {key: {"path": str(outputs[key]), "sha256": ORIGINAL["sha"](outputs[key]),
                                  "bytes": outputs[key].stat().st_size} for key in ("stdout", "stderr")}}
    with outputs["manifest"].open("x", encoding="utf-8") as file:
        file.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: manifest[key] for key in (
        "label", "exit_code", "elapsed_seconds", "changed", "observed_imports", "import_mismatches")}))
    print("Pinned files:", len(before))
    return code if not changed and not mismatches else 2


if __name__ == "__main__":
    sys.exit(main())
