"""Read-only final reconciliation plus one additive manifest."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("independent_capture", HERE / "c2a-independent-capture.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    target = HERE / "c2a-independent-final.json"
    if target.exists():
        raise SystemExit("refusing to overwrite final manifest")
    current = capture.pins()
    original_mismatch = [path for path, value in capture.FROZEN.items() if current[path] != value]
    reconciliation = {}
    for tag in ("runner", "callers", "probe", "evidence", "boundaries", "boundaries2", "diffcheck"):
        path = HERE / f"c2a-independent-{tag}.json"
        record = json.loads(path.read_bytes())
        difference = [key for key, value in record["after"].items() if current[key] != value]
        expected = [] if tag in ("boundaries2", "diffcheck") else [
            str(ROOT / "scripts/tests/test_run_c2a_verification.py")]
        if difference != expected or record["before"] != record["after"]:
            raise SystemExit(f"unexpected freshness mismatch in {tag}: {difference}")
        reconciliation[tag] = {"sha256": digest(path), "exit": record["exit"],
                               "counts": record["test_counts"],
                               "later_changes": difference}
    if original_mismatch:
        raise SystemExit(f"owner freeze changed: {original_mismatch}")
    syntax = []
    for path in (ROOT / "scripts/tests/test_run_c2a_verification.py",
                 HERE / "c2a-independent-capture.py", Path(__file__).resolve()):
        text = path.read_text(encoding="utf-8")
        ast.parse(text, filename=str(path))
        if any(line.rstrip() != line for line in text.splitlines()):
            raise SystemExit(f"trailing whitespace: {path}")
        syntax.append(str(path))
    git = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"
    commands = []
    for args in (["rev-parse", "HEAD"], ["branch", "--show-current"], ["remote", "-v"],
                 ["status", "--short", "--untracked-files=all", "--",
                  "scripts", ".ai/workflow-reliability/evidence/c2a-*"]):
        argv = [git, "--no-pager", *args]
        code, stdout, stderr = capture.run_capture(argv, cwd=str(ROOT), idle=30, max_total=60)
        commands.append({"argv": argv, "cwd": str(ROOT), "idle": 30, "max_total": 60,
                         "exit": code, "stdout": stdout, "stderr": stderr})
        if code:
            raise SystemExit(f"Git observation failed: {commands[-1]}")
    after = capture.pins()
    if current != after:
        raise SystemExit("source drift during finalization")
    artifacts = {str(path): digest(path) for path in sorted(HERE.glob("c2a-independent-*"))
                 if path.is_file()}
    runtime_audit_source = Path(sys.executable).parent / "Lib/subprocess.py"
    result = {
        "verdict": "VERIFIED", "scope": "Windows C2a observer only; not C2/full quality",
        "unique_positive_methods": 51, "owner_pins_unchanged": len(capture.FROZEN),
        "before": current, "after": after, "reconciliation": reconciliation,
        "artifacts": artifacts, "commands": commands, "syntax_whitespace_checked": syntax,
        "runtime_audit_source_final_pin": {str(runtime_audit_source): digest(runtime_audit_source)},
        "limits": "Bounded input/executable pins, not complete machine/import/dependency attestation.",
    }
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"verdict": result["verdict"], "positive_methods": 51,
                      "pins_unchanged": len(current), "owner_pins_unchanged": len(capture.FROZEN),
                      "evidence": str(target), "sha256": digest(target),
                      "report_sha256": artifacts[str(HERE / "c2a-independent-report.md")]},
                     indent=2), flush=True)


if __name__ == "__main__":
    main()
