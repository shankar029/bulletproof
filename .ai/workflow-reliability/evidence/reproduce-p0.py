"""Capture actual pre-fix failures in an owned disposable repository."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
root = Path.cwd()
sys.path.insert(0, str(root / "scripts"))
import mutate
import probe
from run import run_capture

records = []


def command(args, cwd, expected=0):
    code, stdout, stderr = run_capture(args, cwd=str(cwd), idle=30, max_total=90)
    records.append({"argv": args, "cwd": str(cwd), "code": code,
                    "stdout": stdout, "stderr": stderr})
    if expected is not None:
        assert code == expected, records[-1]
    return code, stdout, stderr


with tempfile.TemporaryDirectory(prefix="p0-reproduction-", dir=Path(__file__).parent) as scratch:
    owned = Path(scratch)
    project = owned / "project"
    project.mkdir()
    (project / "src").mkdir()
    (project / "test").mkdir()
    (project / ".gitignore").write_text(".ai/\n", encoding="utf-8")
    (project / "package.json").write_text('{"type":"module"}\n', encoding="utf-8")
    for extension in ("js", "mjs", "cjs"):
        text = "module.exports.value = 1;\n" if extension == "cjs" else "export const value = 1;\n"
        (project / "src" / ("value." + extension)).write_text(text, encoding="utf-8")
    (project / "test" / "check.test.mjs").write_text(
        "import test from 'node:test';\nimport assert from 'node:assert/strict';\n"
        "import { value } from '../src/value.js';\n"
        "test('value is one', () => assert.equal(value, 1));\n", encoding="utf-8")
    command(["git", "init", "--quiet"], project)
    command(["git", "config", "user.name", "Owned test fixture"], project)
    command(["git", "config", "user.email", "fixture@example.invalid"], project)
    command(["git", "add", "."], project)
    command(["git", "commit", "--quiet", "-m", "Seed fixture"], project)
    _, base, _ = command(["git", "rev-parse", "HEAD"], project)
    base = base.strip()
    for extension in ("js", "mjs", "cjs"):
        path = project / "src" / ("value." + extension)
        extra = "module.exports.positive = x => x > 0;\n" if extension == "cjs" else "export const positive = x => x > 0;\n"
        path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")
    command(["git", "add", "."], project)
    command(["git", "commit", "--quiet", "-m", "Add executable changes"], project)

    targets = mutate.changed_lines(str(project), base)
    assert "src/value.js" in targets and "src/value.mjs" not in targets and "src/value.cjs" not in targets, targets
    discovered = probe.code_files(str(project))
    assert not any(str(path).endswith((".mjs", ".cjs")) for path in discovered)
    candidates = mutate.build_mutants(str(project), targets, 1)
    assert len(candidates) == 1, candidates
    mutation = candidates[0]
    original = (project / mutation["file"]).read_text(encoding="utf-8").splitlines(keepends=True)
    original[mutation["_index"]] = mutation["_text"]
    invalid = owned / "invalid.mjs"
    invalid.write_text("".join(original), encoding="utf-8")
    _, _, syntax_error = command(["node", "--check", str(invalid)], project, expected=1)
    assert "SyntaxError" in syntax_error
    command([sys.executable, str(root / "scripts" / "mutate.py"), "--repo", str(project),
             "--base", base, "--slug", "invalid-kill", "--max-mutants", "1",
             "--test-cmd", "node --test --test-reporter=tap test/check.test.mjs"], project)
    invalid_report = json.loads((project / ".ai" / "invalid-kill" / "mutation.json").read_text())
    assert invalid_report["score_pct"] == 100 and invalid_report["killed"] == 1, invalid_report

    command([sys.executable, str(root / "scripts" / "probe.py"), "--base", "HEAD",
             "--slug", "incomplete-pass", "--skip-mutation"], project)
    incomplete = json.loads((project / ".ai" / "incomplete-pass" / "metrics.json").read_text())
    assert incomplete["verdict"] == "pass" and "mutation_score_pct" in incomplete["unavailable"], incomplete

    (project / "uncommitted.txt").write_text("Invalidate clean-run prerequisites.\n", encoding="utf-8")
    stale_path = project / ".ai" / "stale" / "mutation.json"
    stale_path.parent.mkdir(parents=True)
    stale_path.write_text(json.dumps({"head": "obsolete", "score_pct": 100, "survivors": []}), encoding="utf-8")
    stale_result = probe.mutation_entry(str(project), "stale", base, False)
    assert stale_result["head"] == 100 and stale_result["status"] == "ok", stale_result
    result = {
        "kind": "Observed pre-fix counterexamples, not passing new-feature tests",
        "sourceHashes": {name: hashlib.sha256((root / "scripts" / name).read_bytes()).hexdigest()
                         for name in ("probe.py", "mutate.py", "run.py")},
        "missingExtensions": {"changedTargets": {path: sorted(lines) for path, lines in targets.items()},
                              "requiredButAbsent": [".mjs", ".cjs"]},
        "syntaxCountedAsKill": invalid_report,
        "incompleteReportedPass": incomplete,
        "staleReportAcceptedAfterDirtyRunFailure": stale_result,
        "commands": records,
    }
    output = root / ".ai" / "workflow-reliability" / "evidence" / "p0-reproductions.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("Reproduced all four pre-fix defects; evidence saved, owned fixture removed.")
