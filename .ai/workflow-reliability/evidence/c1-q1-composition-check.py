"""Check a private prospective index against the independently tested bytes."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture

EXPECTED_HEAD = "0b7e1a1f6fd1f807bd254886e2877d605596d96d"
OVERLAY = (
    "scripts/probe.py",
    "scripts/measure.py",
    "scripts/measure_graph.py",
    "scripts/workflow_gate.py",
    "scripts/workflow_state.py",
    "scripts/tests/workflow_fixtures.py",
    "scripts/tests/test_workflow_state.py",
    "scripts/tests/test_workflow_gate.py",
    "scripts/tests/test_workflow_core_verification.py",
    "scripts/tests/test_workflow_core_verification_r2.py",
    "scripts/tests/test_measure_graph.py",
    "scripts/tests/test_measure_inventory.py",
    "scripts/tests/test_measure_q1_attr.py",
    "scripts/tests/test_measure_q1_attr_independent.py",
    "scripts/tests/test_measure_q1_final_verification.py",
    "scripts/tests/test_measure_q1_integration.py",
    "scripts/tests/test_measure_q1_resumed.py",
    "scripts/tests/test_measure_q1_review.py",
    "scripts/tests/test_measure_q1_verification.py",
    "scripts/tests/test_measure_q1_verification_r2.py",
    "references/quality-metrics.md",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, env=None):
    rc, out, err = run_capture(
        ["git", "--no-pager", *args], cwd=str(ROOT),
        idle=30, max_total=90, env=env,
    )
    if rc:
        raise RuntimeError(f"git {args!r}: exit {rc}\n{out}\n{err}")
    return out.strip()


def main():
    if git("rev-parse", "HEAD") != EXPECTED_HEAD:
        raise RuntimeError("HEAD changed; requalify the prospective composition")
    real_index = git("ls-files", "--stage", "-z")
    if git("diff", "--cached", "--name-only"):
        raise RuntimeError("Real index must be empty of staged changes")
    unknown = set(git("ls-files", "--others", "--exclude-standard", "--", "scripts").splitlines())
    if unknown - set(OVERLAY):
        raise RuntimeError(f"Unexpected untracked source: {sorted(unknown - set(OVERLAY))}")
    changed = set(git("diff", "--name-only", "--", "scripts").splitlines())
    if changed - set(OVERLAY):
        raise RuntimeError(f"Unexpected source change: {sorted(changed - set(OVERLAY))}")
    before = {name: digest((ROOT / name).read_bytes()) for name in OVERLAY}
    evidence = Path(__file__).resolve().parent
    imports_file = evidence / "q1-attr-independent-w-imports.json"
    imports_bytes = imports_file.read_bytes()
    imports = json.loads(imports_bytes)
    matched = {}
    with tempfile.TemporaryDirectory(prefix="bp-composition-") as temporary:
        owned = Path(temporary)
        env = dict(os.environ, GIT_INDEX_FILE=str(owned / "index"))
        git("read-tree", EXPECTED_HEAD, env=env)
        git("add", "--", *OVERLAY, env=env)
        tree = git("write-tree", env=env)
        archive = owned / "candidate.tar"
        git("archive", "--format=tar", f"--output={archive}", tree, env=env)
        with tarfile.open(archive) as candidate:
            names = {entry.name for entry in candidate.getmembers() if entry.isfile()}
            script_names = {name for name in names if name.startswith("scripts/")}
            for name in sorted(script_names | set(OVERLAY)):
                data = candidate.extractfile(name).read()
                actual = (ROOT / name).read_bytes()
                if data != actual:
                    raise RuntimeError(f"Candidate differs from working bytes: {name}")
                matched[name] = digest(data)
            imported = {}
            for module, observation in imports.items():
                path = Path(observation["path"])
                if not path.is_relative_to(ROOT / "scripts"):
                    continue
                name = path.relative_to(ROOT).as_posix()
                if matched.get(name) != observation["sha256"]:
                    raise RuntimeError(f"Candidate differs from verified import: {module}")
                imported[module] = name
            for module in ("workflow_gate", "workflow_state", "measure", "measure_graph",
                           "probe", "mutate", "evidence", "run"):
                if module not in imported:
                    raise RuntimeError(f"Missing verified dependency import: {module}")
    if git("ls-files", "--stage", "-z") != real_index:
        raise RuntimeError("Real index changed")
    if before != {name: digest((ROOT / name).read_bytes()) for name in OVERLAY}:
        raise RuntimeError("Overlay changed during comparison")
    if imports_file.read_bytes() != imports_bytes:
        raise RuntimeError("Independent import evidence changed")
    result = {
        "verdict": "EXACT_SOURCE_COMPOSITION_MATCH",
        "head": EXPECTED_HEAD,
        "prospective_tree": tree,
        "overlay": before,
        "candidate_scripts_and_overlay": matched,
        "independent_imports": imported,
        "independent_import_manifest_sha256": digest(imports_bytes),
        "real_index_unchanged": True,
        "temporary_directory_removed": not owned.exists(),
        "limits": "Byte/composition check only; no additional tests or complete quality claim. "
                  "Evidence and status documents are not part of this source-only candidate tree.",
    }
    output = evidence / "c1-q1-composition-result.json"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(f"PASS: {len(matched)} candidate files match; "
          f"{len(imported)} independent script imports match; real index unchanged.")


if __name__ == "__main__":
    main()
