"""Fresh verification of review R1/R2; reuse capture mechanics, never old outcomes."""
import hashlib
import json
import datetime
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / ".ai/workflow-reliability/evidence"
capture = runpy.run_path(str(OUT / "i1-independent-f1-revalidate.py"))
PY, run, save, hashes = (capture[key] for key in ("PY", "run", "save", "hashes"))


def node_evidence():
    reference = json.loads((OUT / "i1-independent-before.json").read_bytes())["files"]
    suffixes = {".mjs", ".cjs", ".js", ".ts", ".tsx", ".jsx", ".json", ".html", ".css"}
    paths = sorted(p for p in reference
                   if (p.startswith(("evals/", "benchmark/")) and Path(p).suffix in suffixes
                       and p != "evals/report.json") or p == "scripts/native_result.mjs")
    current = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    changed = [p for p in paths if current[p] != reference[p]["sha256"]]
    logs = {}
    for label in ("native", "eval"):
        record = json.loads((OUT / f"i1-independent-{label}.json").read_bytes())
        observed = hashlib.sha256((ROOT / record["log"]).read_bytes()).hexdigest()
        logs[label] = {"observed": observed, "recorded": record["log_sha256"],
                       "matches": observed == record["log_sha256"]}
    return {"reference": "i1-independent-before.json", "files": current,
            "file_count": len(paths), "changed": changed, "log_hashes": logs,
            "note": "Hashes preserve prior actual Node/corpus executions; no new execution is claimed."}


def main():
    mode = sys.argv[1]
    label = "review-fixes-" + mode
    if mode == "probe":
        capture["probe_external"]("review-fixes", 1500)
        return
    if mode == "node-evidence":
        record = node_evidence()
        save(label, record)
        print(json.dumps({k: v for k, v in record.items() if k != "files"}, indent=2))
        return
    if mode == "final":
        current = hashes()
        stable = {}
        for name in ("python", "boundary"):
            record = json.loads((OUT / f"i1-independent-review-fixes-{name}-sources.json").read_bytes())
            stable[name] = record["before"] == record["after"] == current
        probe = json.loads((OUT / "i1-independent-review-fixes-probe.json").read_bytes())
        stable["probe"] = probe["before"] == probe["after"] == current
        retained = node_evidence()
        sources = {**retained["files"], **current}
        observed = {}
        for name, argv in (
            ("python-version", [PY, "--version"]),
            ("node-version", [capture["NODE"], "--version"]),
            ("git-version", ["git", "--version"]),
            ("head", ["git", "rev-parse", "HEAD"]),
            ("branch", ["git", "branch", "--show-current"]),
            ("final-whitespace", ["git", "--no-pager", "diff", "--check",
                                  "bcc971d3b64559127dfc43eb0bfd4348c42803ca"]),
        ):
            result = run("review-fixes-" + name, argv, max_seconds=1500)
            observed[name] = {"exit_code": result.returncode,
                              "output": result.stdout.decode("utf-8", errors="replace").strip()}
        start = json.loads((OUT / "i1-independent-review-fixes-python.json").read_bytes())["started"]
        cutoff = datetime.datetime.fromisoformat(start).timestamp()
        case_files = []
        for path in OUT.glob("i1-independent-schema-*-results.json"):
            if path.stat().st_mtime >= cutoff:
                cases = json.loads(path.read_bytes())
                case_files.append({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                   "count": len(cases),
                                   "measured": sum(c["entry"]["state"] == "measured" for c in cases),
                                   "unavailable": sum(c["entry"]["state"] == "unavailable" for c in cases)})
        history = {}
        for name in ("measurement-e2e-retry", "native", "eval"):
            metadata = json.loads((OUT / f"i1-independent-{name}.json").read_bytes())
            digest = hashlib.sha256((ROOT / metadata["log"]).read_bytes()).hexdigest()
            history[name] = {"sha256": digest, "matches_original_record": digest == metadata["log_sha256"]}
        record = {"cwd": str(ROOT), "source_count": len(sources), "sources": sources,
                  "unchanged_across_executions": stable, "retained_node": retained,
                  "observed": observed, "case_files": case_files, "preserved_history": history,
                  "review_sha256": hashlib.sha256((OUT / "i1-code-review-r1.md").read_bytes()).hexdigest(),
                  "metadata": {p: hashlib.sha256((ROOT / ".ai/workflow-reliability" / p).read_bytes()).hexdigest()
                               for p in ("state.md", "tasks.json", "traceability.md", "design-contracts.json")},
                  "quality_probe_run_id": probe["run_id"], "quality_verdict": probe["verdict"]}
        save("review-fixes-final-manifest", record)
        print(json.dumps({k: v for k, v in record.items() if k not in {"sources", "retained_node"}}, indent=2))
        assert all(stable.values()) and not retained["changed"]
        assert all(v["matches"] for v in retained["log_hashes"].values())
        assert all(v["matches_original_record"] for v in history.values())
        assert len(case_files) == 2 and all((c["count"], c["measured"], c["unavailable"]) == (31, 1, 30)
                                            for c in case_files)
        assert all(v["exit_code"] == 0 for v in observed.values())
        return
    before = hashes()
    save(label + "-before", before)
    if mode in {"python", "boundary"}:
        argv = [PY, "-B", "-m", "unittest", "discover", "-s", "scripts/tests"]
        if mode == "boundary":
            argv += ["-p", "test_measurement_e2e.py"]
        argv += ["-v"]
    elif mode == "whitespace":
        argv = ["git", "--no-pager", "diff", "--check", "bcc971d3b64559127dfc43eb0bfd4348c42803ca"]
    else:
        raise ValueError(mode)
    result = run(label, argv, max_seconds=1500)
    after = hashes()
    save(label + "-sources", {"before": before, "after": after, "unchanged": before == after,
                             "exit_code": result.returncode})


if __name__ == "__main__":
    main()
