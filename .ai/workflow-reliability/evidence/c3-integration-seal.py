"""Pin the C3 handoff and re-anchor source facts without changing shared authority."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = "dadce66ff7d9a7494db0af5f8124009d7b132cb9"
DOCS = [
    "SKILL.md", "README.md", "CONTRIBUTING.md", "docs/user-guide.md", "docs/architecture.md",
    *("references/" + name + ".md" for name in (
        "workspace", "planning", "design-doc", "delegation", "testing-and-e2e", "research",
        "communication", "review-and-pr", "final-report", "workflow-gates")),
]
OWNED = DOCS + ["scripts/tests/test_workflow_cli_boundaries.py"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    argv = [sys.executable, "-B", str(ROOT / "scripts/run.py"), "--idle", "30", "--max", "60",
            "--", "git", *args]
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    return {"argv": argv, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def main():
    records = [
        git("diff", "--check", "--", *OWNED),
        git("diff", "--exit-code", BASE, "--", ".ai/workflow-reliability/evidence"),
        git("diff", "--exit-code", BASE, "--", "assets/bulletproof-banner.svg"),
        git("status", "--short", "--untracked-files=normal"),
    ]
    original_paths = [
        OUT / "joint-cli-binding-tests.py", OUT / "joint-cli-binding-verify.py",
    ]
    original_paths += sorted(OUT.glob("joint-cli-binding*report.md"))
    original_paths += sorted(OUT.glob("joint-cli-binding-code-review*.md"))
    revisions = [f"{BASE}:{p.relative_to(ROOT).as_posix()}" for p in original_paths]
    blobs = git("rev-parse", *revisions)
    records.append(blobs)
    historical = {}
    for path, blob in zip(original_paths, blobs["stdout"].splitlines(), strict=True):
        content = path.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        # Historical task evidence uses -text, so compare exact stored bytes.
        assert actual == blob, f"Historical bytes changed: {path}"
        historical[path.relative_to(ROOT).as_posix()] = {"sha256": digest(path), "git_blob": blob}
    cli = json.loads((OUT / "c3-integration-cli-tests.json").read_text())
    assert cli["successful"] and cli["run"] == 33 and not cli["changed_inputs"]
    assert cli["before"]["scripts/tests/test_workflow_cli_boundaries.py"] == digest(ROOT / OWNED[-1])
    rendering = json.loads((OUT / "c3-integration-r2-docs.json").read_text())
    assert rendering["failure"] is None and len(rendering["results"]) == 12
    assert len(rendering["navigation"]) == 3
    for row in rendering["links"]:
        assert row["sha256"] == digest(ROOT / row["file"]), row["file"]
    native = json.loads((OUT / "c3-integration-native.json").read_text())
    assert native["exit"] == 0 and native["before"] == native["after"]
    for name, expected in native["after"].items():
        assert digest(ROOT / name) == expected, name
    assert not cli["remaining_owned_temp_entries"] and not native["remaining_owned_temp_entries"]
    # Definition ranges are re-derived from current source, not copied old line numbers.
    symbols = {
        "scripts/workflow.py": ["_accept", "_next", "_committed", "_close", "_adopt", "_parser", "main"],
        "scripts/workflow_state.py": [
            "_claim", "validate_contract", "validate_design", "validate_design_binding",
            "load_workspace", "_section_hash", "_validate_claim_files", "bind_inputs",
        ],
        "scripts/workflow_gate.py": ["_receipt", "claims", "evaluate"],
        "scripts/tests/test_workflow_cli_boundaries.py": [
            "test_registered_environment_sets_removes_and_preserves_exact_values",
            "test_close_rejects_real_scoped_membership_and_git_mode_mismatch",
            "test_adoption_cannot_reclassify_an_actual_pending_handoff_as_executable",
        ],
    }
    anchors = {}
    for name, functions in symbols.items():
        path = ROOT / name
        nodes = {node.name: node for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        anchors[name] = {
            "sha256": digest(path),
            "definitions": {f: [nodes[f].lineno, nodes[f].end_lineno] for f in functions},
        }
    for name in DOCS:
        anchors[name] = {
            "sha256": digest(ROOT / name),
            "headings": [{"line": i, "text": line} for i, line in enumerate(
                (ROOT / name).read_text(encoding="utf-8").splitlines(), 1) if line.startswith("#")],
        }
    artifacts = {p.relative_to(ROOT).as_posix(): digest(p)
                 for p in sorted(OUT.glob("c3-integration-*")) if p.is_file()}
    result = {
        "kind": "C3 local frozen handoff; parent independent acceptance pending", "base": BASE,
        "owned": {name: digest(ROOT / name) for name in OWNED},
        "historical_unchanged": historical, "source_anchors": anchors,
        "unchanged_banner_sha256": digest(ROOT / "assets/bulletproof-banner.svg"),
        "artifacts": artifacts, "git_checks": records,
        "final_cli_dependency_changes_since_execution": [
            name for name, expected in cli["after"].items()
            if not (ROOT / name).exists() or digest(ROOT / name) != expected
        ],
        "counts": {"python_discovered": len(cli["ordinary_discovery"]), "python_executed": cli["run"],
                   "python_unexecuted": len(cli["unexecuted"]), "native_entries": 70,
                   "native_python_replays_already_in_cli33": 5, "render_views": 12},
        "limits": "No current root-quality/coverage/mutation or independent/host acceptance. Parent owns state, traceability, review, report and commits.",
    }
    with (OUT / "c3-integration-seal.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"owned_files": len(OWNED), "historical_raw_checks": len(historical),
                      "counts": result["counts"],
                      "changed_cli_dependencies": result["final_cli_dependency_changes_since_execution"]},
                     indent=2))


if __name__ == "__main__":
    main()
