"""Final read-only source checks plus additive handoff fingerprints."""

import ast
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    manifest = json.loads((HERE / "c1-correction-r3-final-workflow.json").read_text(encoding="utf-8"))
    red = json.loads((HERE / "c1-correction-r3-red.json").read_text(encoding="utf-8"))
    current = {path: sha(Path(path)) for path in manifest["after"]}
    changed = {path: {"tested": digest, "current": current[path]}
               for path, digest in manifest["after"].items() if current[path] != digest}
    red_delta = {path: {"red": red["before"].get(path), "final": manifest["after"].get(path)}
                 for path in red["before"].keys() | manifest["after"].keys()
                 if red["before"].get(path) != manifest["after"].get(path)}
    changed_sources = ("scripts/workflow_gate.py", "scripts/tests/test_workflow_gate.py")
    for name in changed_sources:
        data = (ROOT / name).read_bytes()
        text = data.decode("utf-8")
        tree = ast.parse(text, filename=name)
        compile(tree, name, "exec")
        assert data.endswith(b"\n") and all(line == line.rstrip() for line in text.splitlines()), name
        imported = {a.asname or a.name.split(".")[0] for n in ast.walk(tree)
                    if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        assert imported <= used, (name, imported - used)
    files = [*changed_sources, "scripts/workflow_state.py", "scripts/tests/test_workflow_state.py",
             "scripts/tests/workflow_fixtures.py", "scripts/tests/test_workflow_core_verification.py",
             "scripts/tests/test_workflow_core_verification_r2.py", "scripts/measure.py",
             "scripts/measure_graph.py", "scripts/probe.py", ".ai/workflow-reliability/evidence/c1-code-review.md"]
    result = {
        "argv": [sys.executable, "-B", str(Path(__file__).resolve())], "cwd": str(ROOT),
        "pins_rechecked": len(current), "changed_since_test": changed,
        "red_to_final_delta": red_delta, "source_hashes": {name: sha(ROOT / name) for name in files},
        "protected_independent_artifacts": sum(Path(p).name.startswith("c1-independent-") for p in current),
        "source_checks": "AST/compile/import-use/final-LF/trailing-whitespace passed on the two changed C1 files",
        "limits": "Stable interval only; final dependency freeze and independent acceptance remain parent-owned.",
    }
    with (HERE / "c1-correction-r3-handoff.json").open("x", encoding="utf-8") as file:
        file.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
