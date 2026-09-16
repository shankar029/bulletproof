"""Bounded F1 revalidation; preserve earlier red and capture probe output externally."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / ".ai/workflow-reliability/evidence"
helpers = runpy.run_path(str(OUT / "i1-independent-runner.py"))
PY, NODE, ENV = helpers["PY"], helpers["NODE"], helpers["ENV"]
save, run = helpers["save"], helpers["run"]
PATHS = [
    "scripts/probe.py", "scripts/mutate.py", "scripts/native_result.mjs",
    "scripts/evidence.py", "scripts/run.py", "scripts/tests/helpers.py",
    "scripts/tests/test_probe.py", "scripts/tests/test_measurement_e2e.py",
    "scripts/tests/test_mutate.py", "scripts/tests/test_evidence.py", "scripts/tests/test_run.py",
    "evals/lib/score.mjs", "evals/lib/score.test.mjs", "evals/lib/native_result.test.mjs",
    "evals/lib/mutate.test.mjs", "evals/agent/agent.test.mjs", "evals/run.mjs",
    "benchmark/projects/csv-stats-cli/bulletproof/cli.test.ts",
    ".ai/workflow-reliability/design.html", ".ai/workflow-reliability/design-contracts.json",
    ".ai/workflow-reliability/.gitattributes",
]


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in PATHS}


def probe_external(label="f1", max_seconds=900):
    before = hashes()
    argv = [PY, "-B", "scripts/run.py", "--idle", "120", "--max", str(max_seconds), "--",
            PY, "-B", "scripts/probe.py", "--slug", "workflow-reliability",
            "--base", "bcc971d3b64559127dfc43eb0bfd4348c42803ca", "--test-cwd", ".", "--",
            NODE, "--test", "evals/lib/mutate.test.mjs", "evals/lib/score.test.mjs",
            "evals/agent/agent.test.mjs", "evals/lib/native_result.test.mjs"]
    display = ROOT / ".ai/workflow-reliability/metrics.json"
    prior_display = display.read_bytes() if display.exists() else None
    runs = OUT / "runs"
    prior_runs = set(runs.iterdir()) if runs.exists() else set()
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    timer = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="i1-independent-raw-") as temporary:
        external = Path(temporary)
        log = external / "probe.log"
        print(json.dumps({"argv": argv, "cwd": str(ROOT), "external_raw_capture": str(log)}), flush=True)
        try:
            proc = subprocess.Popen(argv, cwd=ROOT, env=ENV, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            with log.open("wb") as sink:
                for line in iter(proc.stdout.readline, b""):
                    sink.write(line)
                    if line.startswith(b"probe:"):
                        print(line.decode("utf-8", errors="replace"), end="", flush=True)
            proc.wait(timeout=30)
            proc.stdout.close()
            new_runs = sorted(set(runs.iterdir()) - prior_runs)
            if len(new_runs) != 1:
                raise RuntimeError(f"Expected one owned probe run, observed {new_runs}")
            directory = new_runs[0]
            report = json.loads((directory / "metrics.json").read_bytes())
            sys.path.insert(0, str(ROOT / "scripts"))
            from evidence import source_snapshot
            observed = source_snapshot(ROOT, report["source"]["scope"])
            after = hashes()
            record = {
                "argv": argv, "cwd": str(ROOT), "environment_delta": helpers["ENV_DELTA"],
                "started": start, "finished": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "duration_seconds": round(time.monotonic() - timer, 3), "exit_code": proc.returncode,
                "idle_seconds": 120, "max_seconds": max_seconds, "external_raw_capture": str(log),
                "raw_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
                "run_id": report["run_id"], "before": before, "after": after,
                "source_hashes_unchanged": before == after,
                "fresh_immediately_after_producer": observed["scope_sha256"] == report["source"]["scope_sha256"],
                "report_scope_hash": report["source"]["scope_sha256"],
                "observed_scope_hash": observed["scope_sha256"],
                "measurement_status": report["measurement_status"],
                "completeness": report["completeness"], "verdict": report["verdict"],
                "missing_required": report["missing_required"],
                "capture_note": "No verifier evidence written in repository during collection or immediate freshness check. Subsequent archival is an observed source-membership change, not part of the measured interval.",
            }
            (external / "record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
            # Capture both immutable producer reports externally before restoring
            # the old display alias and archiving into the allowed evidence namespace.
            shutil.copytree(directory, external / "producer")
            if prior_display is None:
                display.unlink(missing_ok=True)
            else:
                display.write_bytes(prior_display)
            destination = OUT / ("i1-independent-" + label + "-probe-run-" + report["run_id"])
            shutil.move(str(directory), str(destination))
            shutil.copyfile(log, OUT / ("i1-independent-" + label + "-probe.log"))
            shutil.copyfile(external / "record.json", OUT / ("i1-independent-" + label + "-probe.json"))
            print(json.dumps({key: record[key] for key in
                              ("run_id", "exit_code", "duration_seconds", "source_hashes_unchanged",
                               "fresh_immediately_after_producer", "measurement_status",
                               "completeness", "verdict")}), flush=True)
        finally:
            if prior_display is None:
                display.unlink(missing_ok=True)
            else:
                display.write_bytes(prior_display)


def main():
    mode = sys.argv[1]
    if mode == "probe":
        probe_external()
        return
    label = "f1-" + mode
    before = hashes()
    save(label + "-before", before)
    if mode in {"measurement", "python", "snapshot-test"}:
        argv = [PY, "-B", "-m", "unittest", "discover", "-s", "scripts/tests"]
        if mode == "measurement":
            argv += ["-p", "test_measurement_e2e.py"]
        elif mode == "snapshot-test":
            argv += ["-p", "test_probe.py", "-k", "snapshot_ignores_own_output_but_not_other_contracts"]
        argv += ["-v"]
    elif mode == "whitespace":
        argv = ["git", "--no-pager", "diff", "--check", "bcc971d3b64559127dfc43eb0bfd4348c42803ca"]
    else:
        raise ValueError(mode)
    result = run(label, argv)
    after = hashes()
    save(label + "-sources", {"before": before, "after": after, "unchanged": before == after,
                             "exit_code": result.returncode})


if __name__ == "__main__":
    main()
