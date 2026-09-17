"""Additive qualification reconciliation and preservation attestation."""
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("source_harness", HERE / "q2-tools-source-helper.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
q = harness.q


def boundary():
    harness.command("lizard-boundaries", [q.PYTHON, "-I", "-S", "-B",
                    HERE / "q2-tools-source-lizard-boundaries.py"], install=True)


def context():
    git = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"
    harness.command("tracked-context", [git, "--no-pager", "-C", q.REPO,
                                      "status", "--short", "--untracked-files=no"])
    harness.command("head-context", [git, "--no-pager", "-C", q.REPO, "rev-parse", "HEAD"])


def encoding_probe():
    code = (
        "import json,locale,pathlib,sys;"
        "p=pathlib.Path(sys.argv[1]);"
        "a=json.loads(p.read_text())['files'][0]['path'];"
        "b=json.loads(p.read_text(encoding='utf-8'))['files'][0]['path'];"
        "print(json.dumps({'preferred_encoding':locale.getencoding(),"
        "'default_path':a,'default_exists':pathlib.Path(a).exists(),"
        "'utf8_path':b,'utf8_exists':pathlib.Path(b).exists()},ensure_ascii=True));"
        "assert pathlib.Path(b).exists()"
    )
    harness.command("encoding-probe", [q.PYTHON, "-I", "-S", "-B", "-c", code,
                                      HERE / "q2-tools-source-typescript-results.json"])


def summary():
    roots = json.loads((HERE / "q2-tools-source-roots.json").read_text(encoding="utf-8"))
    liz = json.loads((HERE / "q2-tools-source-lizard-results.json").read_text(encoding="utf-8"))
    vult = json.loads((HERE / "q2-tools-source-vulture-results.json").read_text(encoding="utf-8"))
    ts = json.loads((HERE / "q2-tools-source-typescript-results.json").read_text(encoding="utf-8"))
    values = {
        "lizard_rows": [{"name": Path(row["path"]).name, "reader": row["reader"],
                         "functions": [{"name": f["name"], "ccn": f["cyclomatic_complexity"],
                                        "start": f["start_line"], "end": f["end_line"]}
                                       for f in row["file_info"]["functions"]],
                         "stderr": row["stderr"]} for row in liz["rows"]],
        "vulture_rows": [{"case": row["case"], "confidence80_count": len(row.get("findings80", [])),
                          "findings": row.get("findings80"), "pre_report_exit": row.get("pre_report_exit"),
                          "post_report_exit": row.get("post_report_exit"), "error": row.get("system_exit", row.get("stderr"))}
                         for row in vult["rows"]],
        "tool_sources": {},
        "typescript": {"files": len(ts["files"]), "cases": len(ts["checks"]),
                       "shape_cases": len(ts["shapeFiles"]), "positive_codes": [d["code"] for d in ts["positives"]],
                       "compiler_js_sha256": q.sha(Path(roots["typescript"]) / "lib" / "typescript.js")},
    }
    for name, relative in (("lizard", "lizard.py"), ("vulture", "vulture/core.py"),
                           ("pygments", "pygments/__init__.py"), ("pathspec", "pathspec/__init__.py")):
        path = Path(roots[name]) / relative
        values["tool_sources"][name] = {"path": str(path), "sha256": q.sha(path)}
    harness.save("summary", values)
    print(json.dumps({"tool_sources": values["tool_sources"], "typescript": values["typescript"],
                      "lizard_cases": len(values["lizard_rows"]), "vulture_cases": len(values["vulture_rows"])}, indent=2))


def finish():
    previous = json.loads((HERE / "q2-tools-source-prior-pins.json").read_text(encoding="utf-8"))
    extracted = json.loads((HERE / "q2-tools-source-extracted-pins.json").read_text(encoding="utf-8"))
    required = json.loads((HERE / "q2-tools-source-required-pins.json").read_text(encoding="utf-8"))
    for item in previous + extracted + required["contracts"]:
        assert q.sha(Path(item["path"])) == item["sha256"], item["path"]
    for item in list(required["executors"].values()) + [required["python_dll"]]:
        assert q.sha(Path(item["path"])) == item["sha256"], item["path"]
    route = json.loads((HERE / "q2-tools-route-manifest.json").read_text(encoding="utf-8"))
    for tool in route["tools"].values():
        item = tool["acquired_data_only"]
        assert q.sha(Path(item["path"])) == item["sha256"]
    native = json.loads((HERE / "q2-tools-runtime-bindings.json").read_text(encoding="utf-8"))["executors"]
    native = {name: native[name] for name in ("jscpd", "ruff")}
    for item in native.values():
        assert q.sha(Path(item["path"])) == item["sha256"]
    imported = []
    for path in HERE.glob("q2-tools-source-python-provenance-*.json"):
        imported.extend(json.loads(path.read_text(encoding="utf-8"))["imported_files"])
    imported.extend(json.loads((HERE / "q2-tools-source-lizard-boundaries-results.json").read_text(encoding="utf-8"))["actual_imports"])
    for item in imported:
        if item["sha256"] and not Path(item["path"]).is_relative_to(HERE):
            assert q.sha(Path(item["path"])) == item["sha256"], item["path"]
    liz = json.loads((HERE / "q2-tools-source-lizard-results.json").read_text(encoding="utf-8"))
    assert [i for i, passed in enumerate(liz["assertions"]) if not passed] == [39]
    boundary_result = json.loads((HERE / "q2-tools-source-lizard-boundaries-results.json").read_text(encoding="utf-8"))
    assert boundary_result["all_other_original_assertions_passed"]
    vult = json.loads((HERE / "q2-tools-source-vulture-results.json").read_text(encoding="utf-8"))
    assert all(vult["assertions"])
    ts = json.loads((HERE / "q2-tools-source-typescript-results.json").read_text(encoding="utf-8"))
    assert ts["version"] == "5.9.3"
    for row in ts["files"] + vult["files"]:
        assert q.sha(Path(row["path"])) == row["sha256"]
    for row in liz["rows"]:
        if row["source_sha256"]:
            assert q.sha(Path(row["path"])) == row["source_sha256"]
    roots = json.loads((HERE / "q2-tools-source-roots.json").read_text(encoding="utf-8"))
    unexpected = [str(p) for root in roots.values() for p in Path(root).rglob("*.pyc")]
    assert not unexpected
    fixture_pins = [{"path": str(p), "sha256": q.sha(p), "bytes": p.stat().st_size}
                    for name in ("typescript", "lizard", "vulture")
                    for p in sorted((harness.ROOT / (name + " fixtures with spaces")).iterdir()) if p.is_file()]
    artifacts = [{"path": str(p), "sha256": q.sha(p), "bytes": p.stat().st_size}
                 for p in sorted(HERE.glob("q2-tools-source-*")) if p.is_file()]
    manifest = {
        "status": "CHECK-TOOLS qualified; Q2 implementation and quality not completed",
        "human_approval": "unconfirmed; parent provenance-route approval is recorded user-authorized autonomy",
        "prior_evidence_verified": len(previous), "extracted_files_verified": len(extracted),
        "required_pins": required, "source_archives": {name: value["acquired_data_only"] for name, value in route["tools"].items()},
        "source_roots": roots, "artifacts": artifacts,
        "synthetic_fixtures": fixture_pins,
        "retained_native_tools_rehashed_not_rerun": native,
        "runtime_import_records_rehashed": len(imported),
        "stage_bootstrap_hashes": "Version/help used the initial bootstrap stage; subsequent API stage added fixture functions. Per-execution provenance records preserve stage hashes; only approved external module bytes are asserted unchanged.",
        "preserved_original_failure": "lizard API run exit1: incorrect decode-diagnostic expectation. Strict text API boundary separately qualified; raw result unchanged.",
        "scope": "No production adapter/integration, repository tests/docs/shared-state, install/build/dependency/OS/network changes in this phase",
        "concurrent_writer": "Parent C2 workflow_state.py deliberately excluded from pin assertions",
        "coverage": "7.16.1 deferred to Q3", "cleanup": "No live child processes, no bytecode; owned tools/fixtures retained as bound evidence",
    }
    harness.save("manifest", manifest)
    print(json.dumps({"prior_preserved": len(previous), "extracted_unchanged": len(extracted),
                      "artifacts": len(artifacts), "manifest_sha256": q.sha(HERE / "q2-tools-source-manifest.json")}))


def verify():
    manifest = json.loads((HERE / "q2-tools-source-manifest.json").read_text(encoding="utf-8"))
    for item in manifest["artifacts"] + manifest["synthetic_fixtures"]:
        assert q.sha(Path(item["path"])) == item["sha256"], item["path"]
    print(json.dumps({"verified": True, "artifacts": len(manifest["artifacts"]),
                      "fixtures": len(manifest["synthetic_fixtures"]),
                      "manifest_sha256": q.sha(HERE / "q2-tools-source-manifest.json")}))


if __name__ == "__main__":
    globals()[sys.argv[1]]()
