#!/usr/bin/env python3
"""bulletproof quality probe.

Runs whatever analysis tools are installed on this machine against the working
tree and against the merge-base, and writes .ai/<slug>/metrics.json with both
values plus the delta. Tools belong to the skill, not to the repository: nothing
is installed into the project and nothing is written outside .ai/<slug>/.

  python probe.py --slug my-feature --base origin/main
  python probe.py --slug my-feature --base origin/main --skip-mutation

Exit codes: 0 = complete passing proof, 1 = failure or incomplete proof,
2 = invalid invocation. Missing required measurements never produce a pass.
"""

import argparse
from contextvars import ContextVar
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from evidence import source_snapshot, write_json_atomic
from mutate import DEFAULT_MAX_MUTANTS, select_test_run, validate_mutation_results
from run import run_capture

SKIP_DIRS = {".git", ".ai", "node_modules", "dist", "build", "target", "vendor",
             "__pycache__", ".venv", "venv", ".tox", ".next", "coverage", "out"}
CODE_EXT = {".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
            ".cs", ".rb", ".php", ".swift", ".c", ".h", ".cc", ".cpp", ".scala"}
JS_EXT = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
TRACE = ContextVar("probe_commands", default=None)


# Python-based tools can be reached through the interpreter when pip's script
# directory is not on PATH (common on Windows with `pip install --user`).
PY_MODULE = {"lizard": "lizard", "vulture": "vulture", "semgrep": "semgrep",
             "radon": "radon", "mutmut": "mutmut", "diff-cover": "diff_cover"}


# ---------------------------------------------------------------- helpers
def run(cmd, cwd=None, timeout=900):
    """Run a command, returning (rc, stdout, stderr), with bounded capture.

    `timeout` is the absolute ceiling; the command is also killed (whole tree) if
    it goes silent for `idle` seconds — so a hung child dies in minutes instead of
    stalling out the full ceiling, and no orphaned test/mutation process keeps a
    lock. rc 124 = idle timeout; 125 = absolute timeout or launch error.
    """
    idle = min(300.0, float(timeout)) if timeout else 300.0
    result = run_capture(cmd, cwd=cwd, idle=idle, max_total=float(timeout or 0))
    trace = TRACE.get()
    if trace is not None:
        trace.append({"argv": [str(value) for value in cmd], "cwd": str(Path(cwd or ".").resolve()),
                      "idle_seconds": idle, "max_seconds": timeout, "code": result[0],
                      "stdout": result[1], "stderr": result[2]})
    return result


def argv(tool):
    """Return the argv prefix that actually launches `tool`, or None.

    Resolves the full path so Windows .CMD/.EXE shims are executable without a
    shell, and falls back to `python -m <module>` for pip-installed tools whose
    script directory is not on PATH.
    """
    path = shutil.which(tool)
    if path:
        return [path]
    module = PY_MODULE.get(tool)
    if module:
        rc, _, _ = run([sys.executable, "-m", module, "--version"], timeout=60)
        if rc == 0:
            return [sys.executable, "-m", module]
    return None


def have(tool):
    return argv(tool) is not None


def tool_version(tool, flag="--version"):
    base = argv(tool)
    if not base:
        return None
    rc, out, err = run(base + [flag], timeout=60)
    if rc != 0:
        return None
    text = (out or err).strip().splitlines()
    return text[0][:60] if text else "unknown"


def _attach_result(value):
    trace = TRACE.get()
    if trace:
        trace[-1]["result_report"] = value


def code_files(root):
    found = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if os.path.splitext(f)[1].lower() in CODE_EXT:
                found.append(os.path.join(base, f))
    return found


UI_DEPS = ("react", "vue", "svelte", "@angular/core", "solid-js", "preact")
UI_EXT = {".tsx", ".jsx", ".vue", ".svelte"}


def is_ui_project(root):
    """A front-end project: its suite is slow per mutant and its duplication is
    dominated by style files, so the probe treats it differently."""
    pkg = os.path.join(root, "package.json")
    if os.path.exists(pkg):
        try:
            with open(pkg, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError("Manifest must be a JSON object")
            deps = dict(data.get("dependencies") or {})
            deps.update(data.get("devDependencies") or {})
            if any(d in deps for d in UI_DEPS):
                return True
        except (OSError, ValueError, TypeError) as error:
            raise ValueError("Cannot inspect UI manifest %s: %s" % (pkg, error)) from error
    return any(os.path.splitext(p)[1].lower() in UI_EXT for p in code_files(root))


# ---------------------------------------------------------------- metrics
def m_duplication(root):
    """Percentage of duplicated lines (jscpd)."""
    base = argv("jscpd")
    if not base:
        return None
    with tempfile.TemporaryDirectory() as out:
        rc, _, _ = run(base + [root, "--reporters", "json", "--output", out,
                               "--silent", "--min-tokens", "40", "--min-lines", "5",
                               "--ignore",
                               "**/node_modules/**,**/.ai/**,**/dist/**"], cwd=root)
        report = os.path.join(out, "jscpd-report.json")
        if rc != 0 or not os.path.exists(report):
            return None
        try:
            with open(report, encoding="utf-8") as fh:
                data = json.load(fh)
            _attach_result(data)
            value = data["statistics"]["total"]["percentage"]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                return None
            return round(value, 2) if 0 <= value <= 100 else None
        except (OSError, ValueError, TypeError, KeyError):
            return None


def m_complexity(root):
    """(max, average) cyclomatic complexity across functions (lizard)."""
    base = argv("lizard")
    if not base:
        return None, None
    rc, out, err = run(base + [root, "--csv",
                             "-x", "*/node_modules/*", "-x", "*/.ai/*", "-x", "*/dist/*"], cwd=root)
    if rc != 0 or not out.strip() or err.strip():
        return None, None
    values = []
    try:
        for index, parts in enumerate(csv.reader(io.StringIO(out))):
            if index == 0 and len(parts) > 1 and parts[1].strip().upper() == "CCN":
                continue
            if len(parts) < 2 or not parts[1].strip().isdigit():
                return None, None
            values.append(int(parts[1]))
    except csv.Error:
        return None, None
    if not values:
        return None, None
    return max(values), round(sum(values) / len(values), 2)


def m_cycles(root):
    """Number of circular dependencies (madge)."""
    base = argv("madge")
    if not base:
        return None
    targets = [d for d in ("src", "lib", "app") if os.path.isdir(os.path.join(root, d))]
    if not targets:
        targets = ["."]
    total = 0
    seen = False
    for t in targets:
        rc, out, err = run(base + ["--extensions", "js,jsx,ts,tsx,mjs,cjs", "--circular", "--json", t], cwd=root)
        if rc != 0 or not out.strip() or err.strip():
            return None
        try:
            cycles = json.loads(out)
            if not isinstance(cycles, list) or any(
                    not isinstance(cycle, list) or not cycle or
                    any(not isinstance(path, str) or not path for path in cycle) for cycle in cycles):
                return None
            total += len(cycles)
            seen = True
        except ValueError:
            return None
    return total if seen else None


def m_static(root):
    """Count of static-analysis findings (semgrep, default registry rules)."""
    base = argv("semgrep")
    if not base:
        return None
    rc, out, _ = run(base + ["--config", "auto", "--json", "--quiet",
                             "--metrics", "off", root], cwd=root, timeout=1800)
    if rc != 0 or not out.strip():
        return None
    try:
        report = json.loads(out)
        _attach_result(report)
        if not isinstance(report, dict) or not isinstance(report.get("results"), list) or report.get("errors"):
            return None
        return len(report["results"])
    except (ValueError, TypeError):
        return None


def m_dead(root):
    """Unused exports / dead code count (knip for JS/TS, vulture for Python)."""
    knip = argv("knip")
    if os.path.exists(os.path.join(root, "package.json")) and knip:
        rc, out, _ = run(knip + ["--reporter", "json", "--no-exit-code"], cwd=root)
        if rc != 0 or not out.strip():
            return None
        try:
            data = json.loads(out)
            if not isinstance(data, dict) or not data or any(not isinstance(value, list) for value in data.values()):
                return None
            return sum(len(v) for v in data.values() if isinstance(v, list))
        except (ValueError, TypeError):
            return None
    vult = argv("vulture")
    if vult:
        rc, out, _ = run(vult + [root, "--min-confidence", "80"], cwd=root)
        if rc in (0, 3):
            return len([l for l in out.splitlines() if l.strip()])
    return None


def diff_stats(repo, base):
    """Files and lines changed between the base and the *working tree*, so the
    probe reflects work in progress as well as commits."""
    rc, out, _ = run(["git", "diff", "--numstat", base], cwd=repo)
    if rc != 0:
        rc, out, _ = run(["git", "diff", "--numstat", base + "...HEAD"], cwd=repo)
        if rc != 0:
            return None, None
    files = 0
    lines = 0
    for row in out.splitlines():
        cols = row.split("\t")
        if len(cols) == 3:
            files += 1
            for n in cols[:2]:
                if n.isdigit():
                    lines += int(n)
    return files, lines


# ---------------------------------------------------------------- probe
def collect(root, skip_mutation):
    cx_max, cx_avg = m_complexity(root)
    return {
        "duplication_pct": m_duplication(root),
        "complexity_max": cx_max,
        "complexity_avg": cx_avg,
        "cycles": m_cycles(root),
        "dead_exports": m_dead(root),
        "static_findings": m_static(root),
    }


MUTATION_FLOOR = 60.0


def mutation_entry(repo, slug, base, skip, *, run_id, test_run=None):
    """Consume only successful, restored native proof from this invocation."""
    missing = {"state": "unavailable", "head": None, "base": None,
               "comparison": "unavailable", "status": "unavailable", "run_id": run_id,
               "reason": "Mutation was explicitly skipped; required proof is still missing"}
    if skip:
        return missing
    selected = test_run or {}
    engine = Path(__file__).with_name("mutate.py")
    command = [sys.executable, "-B", str(engine), "--slug", slug, "--base", base,
               "--repo", str(repo), "--run-id", run_id, "--test-cwd", selected.get("cwd", "."),
               "--max-mutants", str(DEFAULT_MAX_MUTANTS)]
    if selected.get("argv"):
        command += ["--", *selected["argv"]]
    print("probe: running current-invocation native mutation ...", file=sys.stderr)
    code, _, error = run(command, cwd=repo, timeout=5400)
    path = Path(repo) / ".ai" / slug / "evidence" / "runs" / run_id / "mutation.json"
    if code != 0:
        missing["reason"] = "Current mutation invocation failed or was incomplete (exit %s): %s" % (code, error[-1000:].strip())
        if path.is_file():
            try:
                diagnostic = json.loads(path.read_text(encoding="utf-8"))
                if (isinstance(diagnostic, dict) and diagnostic.get("schema_version") == 2 and
                        diagnostic.get("run_id") == run_id and isinstance(diagnostic.get("reason"), str)):
                    missing["reason"] = "Current mutation incomplete (exit %s): %s" % (code, diagnostic["reason"])
            except (OSError, ValueError) as failure:
                missing["reason"] += "; current diagnostic unreadable: %s" % failure
        return missing
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema_version") != 2 or data.get("run_id") != run_id:
            raise ValueError("Mutation report is not bound to this versioned invocation")
        if data.get("complete") is not True or data.get("ungraded") != 0 or data.get("unsupported_scope"):
            raise ValueError("Mutation report contains incomplete or ungraded proof")
        source = data["source"]
        if not isinstance(source, dict):
            raise ValueError("Mutation source binding must be an object")
        observed = source_snapshot(Path(repo), source["scope"])
        if source.get("binding_mode") != "standalone-source" or observed["scope_sha256"] != source.get("scope_sha256"):
            raise ValueError("Mutation source scope is stale")
        if observed["files"] != source.get("files"):
            raise ValueError("Mutation source inventory does not match its hash")
        code, current_head, _ = run(["git", "rev-parse", "HEAD"], cwd=repo)
        if code != 0 or current_head.strip() != source.get("head") or source.get("base") != base:
            raise ValueError("Mutation Git provenance does not match the requested revision")
        if data.get("restored_sha256") != source["scope_sha256"]:
            raise ValueError("Mutation restoration was not verified")
        counts = [data[key] for key in ("killed", "survived", "total")]
        if any(type(value) is not int or value < 0 for value in counts) or counts[2] <= 0 or sum(counts[:2]) != counts[2]:
            raise ValueError("Mutation counts are incomplete")
        score = data["score_pct"]
        if not _number(score) or not 0 <= score <= 100 or abs(score - 100 * counts[0] / counts[2]) > 0.11:
            raise ValueError("Mutation score does not match its classified outcomes")
        test_command = data["test_run"]["command"]
        if not isinstance(test_command, dict) or not isinstance(test_command.get("argv"), list) or not test_command["argv"]:
            raise ValueError("Mutation command binding is missing")
        expected_cwd = Path(selected.get("cwd", repo)).resolve().relative_to(Path(repo).resolve()).as_posix()
        if test_command.get("cwd") != expected_cwd or data["test_run"].get("runner") != "node-native":
            raise ValueError("Mutation runner or working directory does not match")
        canonical = select_test_run(Path(repo).resolve(), Path(selected.get("cwd", repo)).resolve(),
                                    selected.get("argv") or None)
        if test_command != canonical["command"] or data["test_run"].get("test_files") != canonical["test_files"]:
            raise ValueError("Mutation command does not match canonical test selection")
        baseline = data["baseline"]
        if not isinstance(baseline, dict):
            raise ValueError("Mutation baseline must be an object")
        tests = baseline.get("tests", [])
        if (baseline.get("complete") is not True or not isinstance(tests, list) or not tests or
                baseline.get("leaf_count") != len(tests) or
                any(not isinstance(test, dict) or test.get("outcome") != "pass" for test in tests)):
            raise ValueError("Mutation baseline lacks a complete passing test inventory")
        validate_mutation_results(data, Path(repo))
    except (OSError, ValueError, TypeError, KeyError) as failure:
        missing["reason"] = "Current mutation proof rejected: %s" % failure
        return missing
    status = "ok" if score >= MUTATION_FLOOR else "fail"
    return {"state": "measured", "head": score, "base": None, "comparison": status,
            "status": status, "threshold": MUTATION_FLOOR, "run_id": run_id, "source": source,
            "command": test_command, "reason": "", "survivors": counts[1],
            "artifacts": [_artifact(path, Path(repo))],
            "scope_support": {"measured_paths": sorted(source["files"]), "unsupported_paths": []}}


# lower is better for these; higher is better for the rest
LOWER_BETTER = {"duplication_pct", "complexity_max", "complexity_avg",
                "cycles", "dead_exports", "static_findings"}
ABSOLUTE_ZERO = {"cycles"}          # any increase fails outright
TOLERANCE = {"complexity_max": 2, "complexity_avg": 0.3, "duplication_pct": 0.5}

# Greenfield work has no baseline to regress against: the first commit of real
# code would "regress" every metric from zero. Judge it against sanity limits
# instead, and say so in the report rather than failing the gate for existing.
GREENFIELD_LIMITS = {                      # metric: (warn above, fail above)
    "duplication_pct": (5.0, 12.0),
    "complexity_max": (15, 25),
    "complexity_avg": (4.0, 8.0),
    "cycles": (0, 0),
    "dead_exports": (10, 40),
    "static_findings": (10, 40),
}


def judge(name, base, head, greenfield=False):
    if head is None:
        return None, "unavailable"
    entry = {"base": base, "head": head}
    if greenfield:
        entry["baseline"] = "greenfield"
        warn_at, fail_at = GREENFIELD_LIMITS.get(name, (None, None))
        if fail_at is not None and head > fail_at:
            status = "fail"
        elif warn_at is not None and head > warn_at:
            status = "warn"
        else:
            status = "ok"
        entry["status"] = status
        if fail_at is not None:
            entry["limit"] = fail_at
        return entry, status
    if base is None:
        entry["status"] = "unavailable"
        return entry, "unavailable"
    delta = round(head - base, 2)
    entry["delta"] = delta
    if name in LOWER_BETTER:
        if delta <= 0:
            status = "ok"
        elif name in ABSOLUTE_ZERO:
            status = "fail"
        elif delta <= TOLERANCE.get(name, 0):
            status = "warn"
        else:
            status = "fail"
    else:
        status = "ok" if delta >= 0 else ("warn" if delta > -5 else "fail")
    entry["status"] = status
    return entry, status


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def default_policy():
    return {"required": [*sorted(LOWER_BETTER), "mutation_score_pct",
                         "diff_coverage_pct", "architecture_rules"],
            "rules": {"mutation_score_pct": {"threshold": MUTATION_FLOOR},
                      "greenfield": GREENFIELD_LIMITS.copy(), "tolerance": TOLERANCE.copy()},
            "origins": ["built-in quality metrics; required coverage and architecture proof"]}


def assess_report(metrics, policy):
    if not isinstance(policy.get("required"), list) or not policy["required"]:
        raise ValueError("Policy requires at least one measurement")
    statuses = []
    missing = []
    for name, entry in metrics.items():
        if entry.get("head") is not None and not _number(entry["head"]):
            raise ValueError("Non-finite or non-numeric measurement: " + name)
        if entry.get("state") == "measured" and entry.get("head") is None:
            raise ValueError("Measured value missing: " + name)
        if entry.get("state") == "measured" and entry.get("comparison") in {"ok", "warn", "fail"}:
            statuses.append(entry["comparison"])
    for name in policy["required"]:
        entry = metrics.get(name, {})
        if entry.get("state") != "measured" or entry.get("comparison") not in {"ok", "warn", "fail"}:
            missing.append({"metric": name, "reason": entry.get("reason") or "Required measurement missing",
                            "prerequisite": "Produce a fresh complete supported measurement and comparison"})
    measured = next((status for status in ("fail", "warn", "ok") if status in statuses), "unavailable")
    return {"measurement_status": measured, "completeness": "incomplete" if missing else "complete",
            "missing_required": missing, "verdict": "fail" if missing or measured == "fail" else "pass",
            "worst_status": measured}


def _artifact(path, root):
    return {"path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _snapshot(repo, slug, run_id=None):
    exclusions = [{"path": ".git", "reason": "Git metadata, not analyzer input"}]
    outputs = [".ai/%s/metrics.json" % slug]
    if run_id is not None:
        outputs += [".ai/%s/evidence/runs/%s/%s.json" % (slug, run_id, kind)
                    for kind in ("metrics", "mutation")]
    exclusions += [{"path": path, "reason": "Exact current measurement output"} for path in outputs]
    return source_snapshot(repo, {"directories": ["."], "excluded_outputs": exclusions})


def _scope_support(name, root, commands):
    paths = {Path(path).relative_to(root).as_posix() for path in code_files(root)}
    supported = set()
    if name in {"complexity_max", "complexity_avg"}:
        for command in commands:
            if "--csv" not in command["argv"] or command["code"] != 0:
                continue
            for row in csv.reader(io.StringIO(command["stdout"])):
                if len(row) >= 11 and row[1].strip().isdigit():
                    path = Path(row[6])
                    absolute = path if path.is_absolute() else Path(root) / path
                    if absolute.is_relative_to(root):
                        supported.add(absolute.relative_to(root).as_posix())
    elif name == "cycles":
        supported = {path for path in paths if Path(path).suffix.lower() in JS_EXT}
        # Madge's original src/lib/app selection does not cover other roots.
        targets = [path for path in ("src", "lib", "app") if (Path(root) / path).is_dir()]
        if targets:
            supported = {path for path in supported if any(path.startswith(target + "/") for target in targets)}
    elif name == "dead_exports":
        native = any("knip" in " ".join(command["argv"]) and command["code"] == 0 for command in commands)
        supported = {path for path in paths if Path(path).suffix.lower() in (JS_EXT if native else {".py"})}
    elif name == "static_findings":
        for command in commands:
            report = command.get("result_report", {})
            if isinstance(report, dict):
                inventory = report.get("paths", {})
                if not isinstance(inventory, dict) or not isinstance(inventory.get("scanned", []), list):
                    continue
                for path in inventory.get("scanned", []):
                    if isinstance(path, str):
                        absolute = Path(path) if Path(path).is_absolute() else Path(root) / path
                        if absolute.is_relative_to(root):
                            supported.add(absolute.relative_to(root).as_posix())
    # Duplication output needs a verified inventory adapter before it is complete proof.
    return {"measured_paths": sorted(paths & supported), "unsupported_paths": sorted(paths - supported)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--skip-mutation", action="store_true")
    ap.add_argument("--force-mutation", action="store_true",
                    help="Run mutation even on a UI project, where it is slow.")
    ap.add_argument("--test-cwd")
    ap.add_argument("--require-metric", action="append", default=[])
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    if args.command == ["--"]:
        ap.error("Expected a test command after --")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        ap.error("--slug must contain lowercase alphanumeric words separated by hyphens")
    if any(not re.fullmatch(r"[a-z][a-z0-9_]*", name) for name in args.require_metric):
        ap.error("Invalid required metric name")
    trace = []
    token = TRACE.set(trace)
    try:
        return _execute(args, trace)
    except (OSError, ValueError) as error:
        print("probe: unable to run: %s" % error, file=sys.stderr)
        return 2
    finally:
        TRACE.reset(token)


def _execute(args, trace):
    repo = os.path.abspath(args.repo)
    test_cwd = os.path.abspath(args.test_cwd or repo)
    rc, top, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    if rc != 0:
        print("probe: not a git repository", file=sys.stderr)
        return 2
    repo = top.strip()

    repo = Path(repo)
    if not Path(test_cwd).is_dir() or not Path(test_cwd).resolve().is_relative_to(repo.resolve()):
        raise ValueError("Test cwd must be an existing directory inside the repository")
    run_id = uuid.uuid4().hex
    run_dir = repo / ".ai" / args.slug / "evidence" / "runs" / run_id
    source_snapshot(repo, {"files": [path.relative_to(repo).as_posix() for path in
                                   (run_dir / "metrics.json", repo / ".ai" / args.slug / "metrics.json")]})
    run_dir.mkdir(parents=True, exist_ok=False)
    source = _snapshot(repo, args.slug, run_id)
    rc, head_sha, _ = run(["git", "rev-parse", "HEAD"], cwd=repo)
    head_sha = head_sha.strip() if rc == 0 else "unknown"

    rc, merge_base, _ = run(["git", "merge-base", args.base, "HEAD"], cwd=repo)
    merge_base = merge_base.strip() if rc == 0 else ""

    print("probe: measuring working tree ...", file=sys.stderr)
    start = len(trace)
    head_metrics = collect(str(repo), args.skip_mutation)
    head_commands = trace[start:]

    ui = is_ui_project(repo)
    base_metrics = {k: None for k in head_metrics}
    base_code_count = None
    base_support = {}
    if merge_base:
        with tempfile.TemporaryDirectory() as tmp:
            wt = os.path.join(tmp, "base")
            rc, _, err = run(["git", "worktree", "add", "--detach", wt, merge_base], cwd=repo)
            if rc == 0:
                print("probe: measuring baseline %s ..." % merge_base[:8], file=sys.stderr)
                try:
                    base_code_count = len(code_files(wt))
                    start = len(trace)
                    base_metrics = collect(wt, args.skip_mutation)
                    base_support = {name: _scope_support(name, Path(wt), trace[start:]) for name in base_metrics}
                finally:
                    removed, _, error = run(["git", "worktree", "remove", "--force", wt], cwd=repo)
                    if removed != 0:
                        raise OSError("Could not remove owned baseline worktree: " + error)
            else:
                print("probe: baseline worktree failed: %s" % err.strip(), file=sys.stderr)

    # Fewer than three source files at the base means there is nothing to compare
    # against: this is greenfield work, judged against sanity limits instead.
    greenfield = base_code_count is not None and base_code_count < 3
    if greenfield:
        print("probe: baseline has no meaningful code (%d files) — judging greenfield work "
              "against absolute limits, not deltas" % base_code_count, file=sys.stderr)

    metrics = {}
    for name in head_metrics:
        entry, status = judge(name, base_metrics.get(name), head_metrics[name], greenfield)
        support = _scope_support(name, repo, head_commands)
        partial = bool(support["unsupported_paths"]) or not support["measured_paths"]
        partial_base = not greenfield and bool(base_support.get(name, {}).get("unsupported_paths"))
        reason = ("Collector unavailable, failed or malformed" if entry is None else
                  "Collector does not establish complete file coverage" if partial or partial_base else
                  "Baseline comparison unavailable" if status == "unavailable" else "")
        metrics[name] = {**(entry or {"head": None, "base": base_metrics.get(name)}),
                         "state": "unavailable" if entry is None or partial or partial_base else "measured",
                         "comparison": status, "reason": reason, "scope_support": support,
                         "run_id": run_id, "source": source}

    files, lines = diff_stats(repo, merge_base or args.base)
    if files is not None:
        metrics["diff_files"] = {"head": files}
        metrics["diff_lines"] = {"head": lines}

    skip_mutation = args.skip_mutation or (ui and not args.force_mutation)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    metrics["mutation_score_pct"] = mutation_entry(
        repo, args.slug, merge_base or args.base, skip_mutation, run_id=run_id,
        test_run={"cwd": test_cwd, "argv": command})
    policy = default_policy()
    policy["required"] = sorted(set(policy["required"]) | set(args.require_metric))
    for name in policy["required"]:
        if name not in metrics:
            metrics[name] = {"state": "unavailable", "head": None, "comparison": "unavailable",
                             "reason": "No supported collector implemented", "run_id": run_id}
    tools = {tool: version for tool in ("jscpd", "lizard", "madge", "semgrep", "knip", "vulture")
             if (version := tool_version(tool))}
    if _snapshot(repo, args.slug, run_id)["scope_sha256"] != source["scope_sha256"]:
        for entry in metrics.values():
            entry.update(state="unavailable", reason="Observed source changed during collection")
    verdict = assess_report(metrics, policy)
    unavailable = [name for name, entry in metrics.items() if entry.get("state") == "unavailable"
                   or entry.get("comparison") == "unavailable"]
    source.update(base=merge_base or None, head=head_sha if head_sha != "unknown" else None)

    report = {
        "schema_version": 2, "run_id": run_id, "source": source,
        "policy": policy,
        "policy_sha256": hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "commands": trace,
        "slug": args.slug,
        "base": args.base,
        "merge_base": merge_base[:12],
        "head": head_sha,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project": "ui" if ui else "general",
        "baseline": "unknown" if base_code_count is None else "greenfield" if greenfield else "compared",
        **verdict,
        "metrics": metrics,
        "unavailable": unavailable,
        "tools": tools,
    }

    out_path = repo / ".ai" / args.slug / "metrics.json"
    write_json_atomic(run_dir / "metrics.json", report)
    write_json_atomic(out_path, report)

    print(json.dumps(report, indent=2))
    print("\nprobe: wrote %s" % out_path, file=sys.stderr)
    if ui and skip_mutation and not args.skip_mutation:
        print("probe: mutation skipped — UI project (the whole component suite reruns per "
              "mutant). Use --force-mutation to run it anyway, and say so in the evidence.",
              file=sys.stderr)
    if unavailable:
        print("probe: unavailable (install the tool or report honestly): %s"
              % ", ".join(unavailable), file=sys.stderr)
    return 1 if report["verdict"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
