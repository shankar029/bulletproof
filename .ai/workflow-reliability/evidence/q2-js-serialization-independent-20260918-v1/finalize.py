"""Seal only this independent verification's evidence and new tests."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from run import run_capture


def artifact(path):
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def save(name, value):
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


before = json.loads((HERE / "before.json").read_bytes())
after = json.loads((HERE / "after.json").read_bytes())
assert before == after
assert all(row["matches"] for row in after["frozen"])
for row in after["frozen"]:
    assert artifact(ROOT / row["path"]) == {key: row[key] for key in ("path", "sha256", "bytes")}
for row in after["qualification"]:
    observed = artifact(HERE.parent / row["path"])
    assert (observed["sha256"], observed["bytes"]) == (row["sha256"], row["bytes"])

argv = ["git", "rev-parse", "HEAD"]
code, stdout, stderr = run_capture(argv, cwd=str(ROOT), idle=30, max_total=60)
save("final-head.json", {"argv": argv, "cwd": str(ROOT), "returncode": code,
                         "stdout": stdout, "stderr": stderr, "idle_seconds": 30, "max_seconds": 60})
assert code == 0 and stdout.strip() == "8881a7e667695345328852ab39157988f9fd868d"
new_tests = [ROOT / "scripts/tests/test_measure_js_serialization_independent.py",
             ROOT / "scripts/tests/measure_js_serialization_independent.test.mjs"]
for path in new_tests:
    data = path.read_bytes()
    assert data.endswith(b"\n")
    assert all(line.rstrip(b" \t") == line for line in data.splitlines())
tree = ast.parse(new_tests[0].read_text("utf-8"))
classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
assert len(classes) == 1 and ast.unparse(classes[0].bases[0]) == "unittest.TestCase"
assert len([node for node in classes[0].body if isinstance(node, ast.FunctionDef)
            and node.name.startswith("test_")]) == 1

original = json.loads((HERE.parent / "q2-js-serialization-seal.json").read_bytes())
assert artifact(HERE.parent / "q2-js-serialization-seal.json")["sha256"] == before["seal_sha256"]
native = [json.loads(path.read_bytes()) for path in sorted(HERE.glob("test_native_*.json"))]
assert len(native) == 13
for row in native:
    assert (row["returncode"], row["stderr"], row["idle_seconds"], row["max_seconds"]) == (0, "", 30, 90)
    assert row["native"]["runtime"] == {"version": "v24.11.1", "architecture": "arm64"}
new_capture = json.loads((HERE / "independent-native.capture.json").read_bytes())
assert (new_capture["returncode"], new_capture["stderr"]) == (0, "")
qualified = {row["qualified_inputs_sha256"] for row in native}
qualified.add(json.loads((HERE / "independent-native.invocation.json").read_bytes())["qualified_inputs_sha256"])
assert qualified == {"635539f7f194d17ba256f6a774949a12e3191f53796a5e02db17736462b03e88"}
results = []
for label, count, nested, seconds in [("replay", 15, 13, 354.598), ("independent", 1, 1, 31.425)]:
    result = json.loads((HERE / (label + "-result.json")).read_bytes())
    assert result["returncode"] == 0
    lines = (HERE / (label + ".stdout.bin")).read_bytes().decode("utf-8").splitlines()
    assert f"Ran {count} {'test' if count == 1 else 'tests'} in {seconds:.3f}s" in lines
    assert "OK" in lines and not any("skipped=" in line for line in lines)
    results.append({"label": label, "python_methods": count, "passed": count,
                    "nested_native_invocations": nested, "unittest_seconds": seconds, **result})
save("final-checks.json", {"frozen_inputs_matching": len(after["frozen"]),
                         "qualification_refs_unchanged": len(after["qualification"]),
                         "new_test_direct_whitespace_check": "PASS",
                         "new_python_ast_parse": "PASS", "new_discoverable_methods": 1,
                         "no_test_class_inheritance_duplication": True, "results": results})
seal = {
    "status": "BOUNDED_NATIVE_PHASE5_PASS_NOT_COMPLETE_ACCEPTANCE",
    "head": stdout.strip(),
    "original_seal": artifact(HERE.parent / "q2-js-serialization-seal.json"),
    "authorities": original["authorities"],
    "reconciliation": {"before": artifact(HERE / "before.json"), "after": artifact(HERE / "after.json"),
                       "matching_paths": len(after["frozen"]), "qualification_references": 5},
    "invocations": [json.loads((HERE / (label + "-invocation.json")).read_bytes())
                    for label in ("replay", "independent")],
    "results": results,
    "counts_are_not_additive": True,
    "timeouts": 0, "retries": 0, "production_corrections": 0,
    "qualified_inputs_sha256": next(iter(qualified)),
    "new_tests": [artifact(path) for path in new_tests],
    "accepted_ids": {key: "PARTIAL_ONLY" if key != "JS-LIFE-02" else "NOT_IMPLEMENTED_NOT_VERIFIED"
                     for key in original["accepted_checks"]},
    "limits": [
        "Not configured JS measurement, complete Q2 acceptance, Phase 6 or ship proof",
        "Fixed command/manifests/graph/replay/scalars/metrics/recovery/full-quality/live-model NOT IMPLEMENTED/NOT VERIFIED",
        "Nested run_capture text is UTF-8 replacement-decoded/newline-normalized, not original wire bytes",
        "Frozen harness parses native result before storing its record; unchanged",
        "Outer run.py merges its child stderr into stdout; raw wrapper streams preserved before interpretation",
        "No agents, installs, root suite/probe/mutants, live hosts, C4, production changes, commits or pushes",
        "Separate app results and owner/historical runs not counted"
    ],
    "evidence": [artifact(path) for path in sorted(HERE.iterdir()) if path.is_file()],
}
save("seal.json", seal)
print(json.dumps({"sealed_evidence_files": len(seal["evidence"]), "seal": artifact(HERE / "seal.json"),
                  "results": results}, indent=2))
