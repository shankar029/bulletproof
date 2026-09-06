#!/usr/bin/env python3
"""bulletproof quality probe.

Runs whatever analysis tools are installed on this machine against the working
tree and against the merge-base, and writes .ai/<slug>/metrics.json with both
values plus the delta. Tools belong to the skill, not to the repository: nothing
is installed into the project and nothing is written outside .ai/<slug>/.

  python probe.py --slug my-feature --base origin/main
  python probe.py --slug my-feature --base origin/main --skip-mutation

Exit codes: 0 = pass, 1 = gate failure, 2 = probe could not run.
Missing tools are reported as "unavailable" -- never as a pass.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

SKIP_DIRS = {".git", ".ai", "node_modules", "dist", "build", "target", "vendor",
             "__pycache__", ".venv", "venv", ".tox", ".next", "coverage", "out"}
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
            ".cs", ".rb", ".php", ".swift", ".c", ".h", ".cc", ".cpp", ".scala"}


# Python-based tools can be reached through the interpreter when pip's script
# directory is not on PATH (common on Windows with `pip install --user`).
PY_MODULE = {"lizard": "lizard", "vulture": "vulture", "semgrep": "semgrep",
             "radon": "radon", "mutmut": "mutmut", "diff-cover": "diff_cover"}


# ---------------------------------------------------------------- helpers
def run(cmd, cwd=None, timeout=900):
    """Run a command, returning (rc, stdout, stderr). Never raises."""
    try:
        p = subprocess.run(cmd, cwd=cwd, timeout=timeout, shell=False,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as exc:                                   # noqa: BLE001
        return 125, "", str(exc)


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
    text = (out or err).strip().splitlines()
    return text[0][:60] if text else "unknown"


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
            deps = dict(data.get("dependencies") or {})
            deps.update(data.get("devDependencies") or {})
            if any(d in deps for d in UI_DEPS):
                return True
        except Exception:                                      # noqa: BLE001
            pass
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
                               "**/node_modules/**,**/.ai/**,**/dist/**"])
        report = os.path.join(out, "jscpd-report.json")
        if not os.path.exists(report):
            return None
        try:
            with open(report, encoding="utf-8") as fh:
                data = json.load(fh)
            return round(float(data["statistics"]["total"]["percentage"]), 2)
        except Exception:                                      # noqa: BLE001
            return None


def m_complexity(root):
    """(max, average) cyclomatic complexity across functions (lizard)."""
    base = argv("lizard")
    if not base:
        return None, None
    rc, out, _ = run(base + [root, "--csv",
                             "-x", "*/node_modules/*", "-x", "*/.ai/*", "-x", "*/dist/*"])
    if rc not in (0, 1) or not out.strip():
        return None, None
    values = []
    for line in out.splitlines():
        parts = line.split(",")
        if len(parts) > 1:
            try:
                values.append(int(parts[1]))                   # CCN column
            except ValueError:
                continue
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
        rc, out, _ = run(base + ["--circular", "--json", t], cwd=root)
        if rc == 127:
            return None
        try:
            total += len(json.loads(out or "[]"))
            seen = True
        except Exception:                                      # noqa: BLE001
            continue
    return total if seen else None


def m_static(root):
    """Count of static-analysis findings (semgrep, default registry rules)."""
    base = argv("semgrep")
    if not base:
        return None
    rc, out, _ = run(base + ["--config", "auto", "--json", "--quiet",
                             "--metrics", "off", root], timeout=1800)
    if rc not in (0, 1) or not out.strip():
        return None
    try:
        return len(json.loads(out).get("results", []))
    except Exception:                                          # noqa: BLE001
        return None


def m_dead(root):
    """Unused exports / dead code count (knip for JS/TS, vulture for Python)."""
    knip = argv("knip")
    if os.path.exists(os.path.join(root, "package.json")) and knip:
        rc, out, _ = run(knip + ["--reporter", "json", "--no-exit-code"], cwd=root)
        try:
            data = json.loads(out)
            return sum(len(v) for v in data.values() if isinstance(v, list))
        except Exception:                                      # noqa: BLE001
            return None
    vult = argv("vulture")
    if vult:
        rc, out, _ = run(vult + [root, "--min-confidence", "80"])
        if rc in (0, 3):
            return len([l for l in out.splitlines() if l.strip()])
    return None


def m_mutation(root, skip):
    """Mutation score from a runner the project is already wired for.

    Returns None when no configured runner exists; probe.py then falls back to
    the skill's diff-scoped engine (scripts/mutate.py), which needs no project
    wiring at all.
    """
    if skip:
        return None
    npx = argv("npx")
    if os.path.exists(os.path.join(root, "stryker.config.json")) and npx:
        rc, out, _ = run(npx + ["stryker", "run", "--reporters", "json"], cwd=root, timeout=3600)
        match = re.search(r"mutation score[^0-9]*([0-9]+\.?[0-9]*)", out, re.I)
        if match:
            return float(match.group(1))
    mut = argv("mutmut")
    if mut and os.path.isdir(os.path.join(root, "tests")):
        rc, out, _ = run(mut + ["run", "--paths-to-mutate", root], cwd=root, timeout=3600)
        rc2, res, _ = run(mut + ["results"], cwd=root, timeout=300)
        killed = len(re.findall(r"killed", res, re.I))
        survived = len(re.findall(r"survived", res, re.I))
        if killed + survived:
            return round(100.0 * killed / (killed + survived), 1)
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


def mutation_entry(repo, slug, base, skip):
    """Mutation score for the change. Diff-scoped, so there is no baseline to
    compare against: it is judged against an absolute floor."""
    if skip:
        return None
    score = m_mutation(repo, skip)
    survivors = None
    if score is None:
        engine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mutate.py")
        if not os.path.exists(engine):
            return None
        print("probe: running diff-scoped mutation engine ...", file=sys.stderr)
        run([sys.executable, engine, "--slug", slug, "--base", base, "--repo", repo],
            cwd=repo, timeout=5400)
        report = os.path.join(repo, ".ai", slug, "mutation.json")
        if not os.path.exists(report):
            return None
        try:
            with open(report, encoding="utf-8") as fh:
                data = json.load(fh)
            score = data.get("score_pct")
            survivors = len(data.get("survivors") or [])
        except Exception:                                      # noqa: BLE001
            return None
    if score is None:
        return None
    entry = {"head": score, "threshold": MUTATION_FLOOR,
             "status": "ok" if score >= MUTATION_FLOOR else "fail"}
    if survivors is not None:
        entry["survivors"] = survivors
        entry["detail"] = ".ai/%s/mutation.json" % slug
    return entry


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
    "cycles": (0, 1),
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
        entry["status"] = "ok"
        return entry, "ok"
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--skip-mutation", action="store_true")
    ap.add_argument("--force-mutation", action="store_true",
                    help="Run mutation even on a UI project, where it is slow.")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    rc, top, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    if rc != 0:
        print("probe: not a git repository", file=sys.stderr)
        return 2
    repo = top.strip()

    rc, head_sha, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd=repo)
    head_sha = head_sha.strip() if rc == 0 else "unknown"

    rc, merge_base, _ = run(["git", "merge-base", args.base, "HEAD"], cwd=repo)
    merge_base = merge_base.strip() if rc == 0 else ""

    print("probe: measuring working tree ...", file=sys.stderr)
    head_metrics = collect(repo, args.skip_mutation)

    ui = is_ui_project(repo)
    base_metrics = {k: None for k in head_metrics}
    base_code_count = 0
    if merge_base:
        with tempfile.TemporaryDirectory() as tmp:
            wt = os.path.join(tmp, "base")
            rc, _, err = run(["git", "worktree", "add", "--detach", wt, merge_base], cwd=repo)
            if rc == 0:
                print("probe: measuring baseline %s ..." % merge_base[:8], file=sys.stderr)
                try:
                    base_code_count = len(code_files(wt))
                    base_metrics = collect(wt, args.skip_mutation)
                finally:
                    run(["git", "worktree", "remove", "--force", wt], cwd=repo)
            else:
                print("probe: baseline worktree failed: %s" % err.strip(), file=sys.stderr)

    # Fewer than three source files at the base means there is nothing to compare
    # against: this is greenfield work, judged against sanity limits instead.
    greenfield = base_code_count < 3
    if greenfield:
        print("probe: baseline has no meaningful code (%d files) — judging greenfield work "
              "against absolute limits, not deltas" % base_code_count, file=sys.stderr)

    metrics = {}
    unavailable = []
    worst = "ok"
    for name in head_metrics:
        entry, status = judge(name, base_metrics.get(name), head_metrics[name], greenfield)
        if entry is None:
            unavailable.append(name)
            continue
        metrics[name] = entry
        if status == "fail":
            worst = "fail"
        elif status == "warn" and worst == "ok":
            worst = "warn"

    files, lines = diff_stats(repo, merge_base or args.base)
    if files is not None:
        metrics["diff_files"] = {"head": files}
        metrics["diff_lines"] = {"head": lines}

    skip_mutation = args.skip_mutation or (ui and not args.force_mutation)
    mutation = mutation_entry(repo, args.slug, merge_base or args.base, skip_mutation)
    if mutation is None:
        unavailable.append("mutation_score_pct")
    else:
        metrics["mutation_score_pct"] = mutation
        if mutation["status"] == "fail":
            worst = "fail"

    report = {
        "slug": args.slug,
        "base": args.base,
        "merge_base": merge_base[:12],
        "head": head_sha,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project": "ui" if ui else "general",
        "baseline": "greenfield" if greenfield else "compared",
        "verdict": "fail" if worst == "fail" else "pass",
        "worst_status": worst,
        "metrics": metrics,
        "unavailable": unavailable,
        "tools": {t: v for t, v in (
            ("jscpd", tool_version("jscpd")),
            ("lizard", tool_version("lizard")),
            ("madge", tool_version("madge")),
            ("semgrep", tool_version("semgrep")),
            ("knip", tool_version("knip")),
            ("vulture", tool_version("vulture")),
        ) if v},
    }

    out_dir = os.path.join(repo, ".ai", args.slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "metrics.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

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
