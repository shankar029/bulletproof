"""Bounded independent C3 replay and immutable before/after evidence."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREFIX = "c3-independent-"


def save(name, value):
    with (OUT / (PREFIX + name + ".json")).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv, label, *, env=None, light=False):
    managed = [sys.executable, "-B", str(ROOT / "scripts/run.py"),
               "--idle", "30" if light else "120", "--max", "60" if light else "1800",
               "--", *argv]
    start = time.monotonic()
    with (OUT / (PREFIX + label + ".log")).open("x", encoding="utf-8") as log:
        child = subprocess.Popen(managed, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                 errors="replace")
        lines = []
        for line in child.stdout:
            lines.append(line)
            log.write(line)
            log.flush()
            print(line, end="", flush=True)
        code = child.wait()
    result = dict(argv=managed, exit=code, elapsed_seconds=time.monotonic() - start,
                  output="".join(lines))
    save(label, result)
    return result


def paths():
    seal = json.loads((OUT / "c3-integration-seal.json").read_text(encoding="utf-8"))
    selected = {ROOT / p for p in seal["owned"]}
    selected.update(ROOT / p for p in seal["historical_unchanged"])
    selected.update(ROOT / p for p in seal["source_anchors"])
    selected.update(OUT.glob("c3-integration-*"))
    for folder in ("scripts", "evals/lib", "evals/agent", "evals/workflow", "benchmark",
                   "install", "launchers", "assets", "references", "docs"):
        for base, dirs, files in os.walk(ROOT / folder):
            dirs[:] = [d for d in dirs if d not in
                       ("node_modules", "__pycache__", ".git", ".pytest_cache")]
            selected.update(Path(base) / f for f in files if not f.endswith((".pyc", ".log")))
    selected.update(ROOT / p for p in ("install.sh", "install.ps1", ".gitignore"))
    for name in ("research.md", "design.html", "design-contracts.json", "plan.html",
                 "tasks.json", "continuation-plan.html"):
        selected.add(OUT.parent / name)
    return sorted(p for p in selected if p.is_file())


def before():
    seal = json.loads((OUT / "c3-integration-seal.json").read_text(encoding="utf-8"))
    current = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths()}
    mismatches = []
    for group in ("owned", "historical_unchanged", "source_anchors", "artifacts"):
        for path, entry in seal[group].items():
            expected = entry if isinstance(entry, str) else entry["sha256"]
            if current.get(path) != expected:
                mismatches.append(dict(group=group, path=path, expected=expected,
                                       actual=current.get(path)))
    assert current["assets/bulletproof-banner.svg"] == seal["unchanged_banner_sha256"]
    save("before", dict(pins=current, owner_seal_mismatches=mismatches,
                        owner_owned_count=len(seal["owned"]),
                        historical_count=len(seal["historical_unchanged"])))
    print(f"Fresh pins: {len(current)}; owner mismatches: {len(mismatches)}", flush=True)
    assert not mismatches, mismatches
    for label, argv in (
        ("git-status-before", ["git", "--no-pager", "status", "--short"]),
        ("git-identity", ["git", "--no-pager", "rev-parse", "HEAD", "--abbrev-ref", "HEAD"]),
        ("git-remotes", ["git", "--no-pager", "remote", "-v"]),
        ("historical-blobs", ["git", "--no-pager", "rev-parse",
                             *[seal["base"] + ":" + p for p in seal["historical_unchanged"]]]),
    ):
        result = command(argv, label, light=True)
        assert result["exit"] == 0
        if label == "historical-blobs":
            assert result["output"].splitlines() == [
                item["git_blob"] for item in seal["historical_unchanged"].values()]


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item.id()


def replay(kind):
    temp = tempfile.mkdtemp(prefix="c3i-", dir=Path.home() / "AppData/Local/Temp")
    env = dict(os.environ, TEMP=temp, TMP=temp, PYTHONDONTWRITEBYTECODE="1",
               PYTHONIOENCODING="utf-8", BULLETPROOF_PYTHON=sys.executable)
    if kind == "cli":
        sys.path.insert(0, str(ROOT / "scripts/tests"))
        all_ids = list(flatten(unittest.TestLoader().discover(str(ROOT / "scripts/tests"))))
        selected = list(flatten(unittest.TestLoader().discover(
            str(ROOT / "scripts/tests"), pattern="test_workflow_cli*.py")))
        save("discovery", dict(all_ids=all_ids, selected=selected,
                               unexecuted=sorted(set(all_ids) - set(selected))))
        assert len(all_ids) == len(set(all_ids))
        assert len(selected) == len(set(selected)) == 33
        assert sum(i.startswith("test_workflow_cli.WorkflowCliTests.") for i in selected) == 30
        assert sum(i.startswith("test_workflow_cli_boundaries.") for i in selected) == 3
        print(f"Independent ordinary discovery: {len(all_ids)} distinct; CLI {len(selected)}",
              flush=True)
        argv = [sys.executable, "-u", "-B", "-m", "unittest", "discover",
                "-s", "scripts/tests", "-p", "test_workflow_cli*.py", "-v"]
    elif kind == "native":
        files = sorted(ROOT.glob("evals/lib/*.test.mjs")) + [
            ROOT / "evals/agent/agent.test.mjs", ROOT / "evals/workflow/failures.test.mjs"]
        argv = ["node", "--test", *map(str, files)]
    else:
        raise ValueError(kind)
    try:
        result = command(argv, kind, env=env)
    finally:
        remaining = [p.name for p in Path(temp).iterdir()]
        if not remaining:
            Path(temp).rmdir()
        save(kind + "-temp", dict(owned_temp=temp, remaining=remaining,
                                 removed_empty_root=not remaining,
                                 old_timeout_cleanup="UNKNOWN; untouched"))
    return result["exit"]


def after():
    previous = json.loads((OUT / "c3-independent-before.json").read_text(encoding="utf-8"))["pins"]
    current = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths()}
    changed = [p for p in previous if previous[p] != current.get(p)]
    added = sorted(set(current) - set(previous))
    save("after", dict(pins=current, changed=changed, added=added))
    print(f"Final pins: {len(current)}; changed {len(changed)}; added {len(added)}", flush=True)
    assert not changed and not added
    assert command(["git", "--no-pager", "status", "--short"],
                   "git-status-after", light=True)["exit"] == 0


def inspect_source():
    old = ast.parse((OUT / "joint-cli-binding-tests.py").read_text(encoding="utf-8"))
    new = ast.parse((ROOT / "scripts/tests/test_workflow_cli_boundaries.py").read_text(encoding="utf-8"))
    methods = lambda tree: {n.name: n for n in ast.walk(tree)
                            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")}
    old_methods, new_methods = methods(old), methods(new)
    assert set(old_methods) == set(new_methods) and len(new_methods) == 3
    comparisons = {}
    for name, node in new_methods.items():
        original = old_methods[name]
        # The only semantic-neutral port difference is moving Path's import to module scope.
        for parent in ast.walk(original):
            if hasattr(parent, "body") and isinstance(parent.body, list):
                parent.body = [n for n in parent.body if not
                               (isinstance(n, ast.ImportFrom) and n.module == "pathlib")]
        comparisons[name] = ast.dump(original, include_attributes=False) == ast.dump(
            node, include_attributes=False)
    assert all(comparisons.values()), comparisons
    anchors = {}
    seal = json.loads((OUT / "c3-integration-seal.json").read_text(encoding="utf-8"))
    for name, data in seal["source_anchors"].items():
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        record = dict(sha256=digest(path))
        if path.suffix == ".py":
            record["definitions"] = {
                n.name: [n.lineno, n.end_lineno] for n in ast.walk(ast.parse(text))
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name in data.get("definitions", {})
            }
        else:
            record["headings"] = [
                {"line": i, "text": line} for i, line in enumerate(text.splitlines(), 1)
                if line.startswith("#")]
        anchors[name] = record
    result = command(["git", "--no-pager", "diff", "--check", "--", *seal["owned"]],
                     "whitespace", light=True)
    assert result["exit"] == 0
    save("source-checks", dict(ports_equivalent_after_Path_import_hoist=comparisons,
                              anchors=anchors,
                              limitation="Static syntax/content checks, not extra executed tests"))
    print("Three historical ports retain identical test ASTs after Path import hoist", flush=True)


def seal():
    before_data = json.loads((OUT / "c3-independent-before.json").read_text(encoding="utf-8"))
    after_data = json.loads((OUT / "c3-independent-after.json").read_text(encoding="utf-8"))
    assert before_data["pins"] == after_data["pins"]
    final = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths()}
    assert final == after_data["pins"], "Input changed after final pin capture"
    artifacts = {p.relative_to(ROOT).as_posix(): digest(p)
                 for p in sorted(OUT.glob("c3-independent-*")) if p.is_file()}
    save("seal", dict(kind="Independent functional Phase 5 proof only; not final quality/release approval",
                      base="dadce66ff7d9a7494db0af5f8124009d7b132cb9",
                      pinned_input_count=len(final), changed_inputs=[],
                      input_pins=final, artifacts=artifacts,
                      owner_owned16_matched=True, historical7_matched=True,
                      self_hash_excluded=True))
    print("Independent seal SHA-256: " + digest(OUT / "c3-independent-seal.json"), flush=True)


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "before":
        before()
    elif action == "after":
        after()
    elif action == "inspect":
        inspect_source()
    elif action == "seal":
        seal()
    else:
        raise SystemExit(replay(action))
