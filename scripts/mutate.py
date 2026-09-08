#!/usr/bin/env python3
"""bulletproof mutation probe.

Answers the one question coverage cannot: *would the tests actually catch this
code being wrong?* It mutates only the lines this change touched, runs the
project's own test command against each mutant, and reports which mutants
survived.

  python mutate.py --slug my-feature --base origin/main
  python mutate.py --slug my-feature --base origin/main --test-cmd "npm test" --max-mutants 30

Design notes:
  * Diff-scoped. Mutating the whole repository is pointless and slow; the
    question is whether *this change* is tested.
  * Language-agnostic. The operators are textual and shared across C-family
    languages, Python, Go, Rust and friends. A project already wired for a real
    mutation runner should use that instead (probe.py prefers it).
  * Honest. Survivors are reported with file, line and the exact edit, so each
    one is either killed with a real assertion or justified as equivalent.
    Nothing here decides that for you.

Exit codes: 0 = completed, 2 = could not run (dirty tree, no tests, red suite).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
            ".cs", ".rb", ".php", ".swift", ".c", ".h", ".cc", ".cpp", ".scala"}

# (pattern, replacement, label) — order matters: longer operators first so that
# ">=" is never partially rewritten by the ">" rule.
OPERATORS = [
    (r">=", "<", "boundary >= -> <"),
    (r"<=", ">", "boundary <= -> >"),
    (r"!=", "==", "equality != -> =="),
    (r"==", "!=", "equality == -> !="),
    (r"&&", "||", "logic && -> ||"),
    (r"\|\|", "&&", "logic || -> &&"),
    (r"\band\b", "or", "logic and -> or"),
    (r"\bor\b", "and", "logic or -> and"),
    (r">", "<", "comparison > -> <"),
    (r"<", ">", "comparison < -> >"),
    (r"(?<![+\-\w])\+(?![+=])", "-", "arithmetic + -> -"),
    (r"(?<![\-+\w])\-(?![\-=>])", "+", "arithmetic - -> +"),
    (r"\bTrue\b", "False", "literal True -> False"),
    (r"\bFalse\b", "True", "literal False -> True"),
    (r"\btrue\b", "false", "literal true -> false"),
    (r"\bfalse\b", "true", "literal false -> true"),
]

COMMENT_PREFIXES = ("#", "//", "*", "/*", '"""', "'''", "--")

# Statement deletion catches what operator swaps cannot: a guard clause, an
# early return, or a side-effecting call that no test actually depends on.
# Restricted to balanced, statement-terminated lines that do not declare a name,
# so a deleted line cannot break syntax or trigger a spurious ReferenceError.
DECLARATION_START = re.compile(
    r"^(const|let|var|function|class|def|import|export|module|package|use|from|public|private|protected)\b")


def deletable(text):
    stripped = text.strip()
    if not stripped.endswith(";") or DECLARATION_START.match(stripped):
        return False
    if stripped.count("(") != stripped.count(")"):
        return False
    return stripped.count("{") == stripped.count("}") and stripped.count("[") == stripped.count("]")

# Mutating a test proves nothing: a surviving mutant in a test file is noise, and
# a killed one only says the suite noticed itself change. Production code only.
TEST_DIR_PARTS = {"test", "tests", "spec", "specs", "__tests__", "testing",
                  "e2e", "fixtures", "mocks", "__mocks__"}
TEST_NAME_HINTS = (".test.", ".spec.", "_test.", "test_", "-test.", ".tests.")

# Never mutate generated, vendored, or agent-workspace files: the project's tests
# do not cover them, so every mutant would "survive" and say nothing.
EXCLUDED_DIRS = {".ai", ".git", ".github", "node_modules", "dist", "build", "out",
                 "target", "vendor", "coverage", "__pycache__", ".venv", "venv",
                 "migrations", "generated", ".next"}


def is_excluded(rel):
    parts = [p.lower() for p in rel.replace("\\", "/").split("/")]
    return any(p in EXCLUDED_DIRS for p in parts)


def is_test_path(rel):
    parts = [p.lower() for p in rel.replace("\\", "/").split("/")]
    if any(p in TEST_DIR_PARTS for p in parts[:-1]):
        return True
    name = parts[-1]
    return any(h in name for h in TEST_NAME_HINTS) or name.startswith("test")

TEST_COMMANDS = [
    ("package.json", ["npm", "test", "--silent"]),
    ("pyproject.toml", ["pytest", "-q", "-x"]),
    ("setup.cfg", ["pytest", "-q", "-x"]),
    ("pytest.ini", ["pytest", "-q", "-x"]),
    ("go.mod", ["go", "test", "./..."]),
    ("Cargo.toml", ["cargo", "test", "--quiet"]),
    ("pom.xml", ["mvn", "-q", "test"]),
    ("build.gradle", ["gradle", "test", "--quiet"]),
]


def run(cmd, cwd=None, timeout=900):
    """Run a command, returning (rc, stdout, stderr). Never raises.

    `timeout` is the absolute ceiling; the command is also killed (whole tree) if
    it goes silent for `idle` seconds — a hang no longer waits out the full
    ceiling, and orphaned children never linger holding a lock. rc 124 = idle or
    ceiling kill, matching GNU `timeout`.
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from run import run_capture
    except Exception:  # noqa: BLE001 — fall back to a total-timeout run
        try:
            p = subprocess.run(cmd, cwd=cwd, timeout=timeout, shell=False,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return (p.returncode, p.stdout.decode("utf-8", "replace"),
                    p.stderr.decode("utf-8", "replace"))
        except FileNotFoundError:
            return 127, "", "not found"
        except subprocess.TimeoutExpired:
            return 124, "", "timeout"
        except Exception as exc:                              # noqa: BLE001
            return 125, "", str(exc)
    idle = min(300.0, float(timeout)) if timeout else 300.0
    return run_capture(cmd, cwd=cwd, idle=idle, max_total=float(timeout or 0))


def resolve(cmd):
    """Resolve argv[0] to a full path so Windows shims are executable."""
    if not cmd:
        return cmd
    path = shutil.which(cmd[0])
    return ([path] + list(cmd[1:])) if path else list(cmd)


def detect_test_cmd(repo):
    for marker, cmd in TEST_COMMANDS:
        if os.path.exists(os.path.join(repo, marker)):
            if marker == "package.json":
                try:
                    with open(os.path.join(repo, "package.json"), encoding="utf-8") as fh:
                        if "test" not in (json.load(fh).get("scripts") or {}):
                            continue
                except Exception:                              # noqa: BLE001
                    continue
            if shutil.which(cmd[0]):
                return cmd
    return None


def changed_lines(repo, base):
    """{path: set(line numbers)} for lines added or modified vs the base."""
    rc, out, _ = run(["git", "diff", "-U0", base + "...HEAD"], cwd=repo)
    if rc != 0:
        rc, out, _ = run(["git", "diff", "-U0", base], cwd=repo)
        if rc != 0:
            return {}
    result = {}
    current = None
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:].strip()
        elif line.startswith("@@") and current:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2) or 1)
                if (os.path.splitext(current)[1].lower() in CODE_EXT
                        and not is_test_path(current) and not is_excluded(current)):
                    result.setdefault(current, set()).update(range(start, start + count))
    return result


def is_mutable(text):
    stripped = text.strip()
    if not stripped or stripped.startswith(COMMENT_PREFIXES):
        return False
    # crude but effective: skip lines that are mostly string literal
    quoted = sum(len(s) for s in re.findall(r"(['\"])(?:\\.|(?!\1).)*\1", stripped))
    return quoted <= len(stripped) * 0.6


STRING_RE = re.compile(r"(['\"`])(?:\\.|(?!\1).)*\1")


def mask_strings(text):
    """Blank out string literals so operators inside prose are never mutated.

    Rewriting "between 1 and 100" to "between 1 or 100" changes a message, not
    behaviour: the mutant survives and teaches nothing. Masking keeps the score
    honest by only mutating code.
    """
    return STRING_RE.sub(lambda m: m.group(0)[0] + "\u0000" * (len(m.group(0)) - 2) + m.group(0)[0], text)


def build_mutants(repo, targets, limit):
    mutants = []
    for rel in sorted(targets):
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines(keepends=True)
        except Exception:                                      # noqa: BLE001
            continue
        for lineno in sorted(targets[rel]):
            if lineno > len(lines):
                continue
            original = lines[lineno - 1]
            if not is_mutable(original):
                continue
            masked = mask_strings(original)
            chosen = None
            for pattern, repl, label in OPERATORS:
                match = re.search(pattern, masked)
                if not match:
                    continue
                mutated = original[:match.start()] + repl + original[match.end():]
                if mutated != original:
                    chosen = (label, mutated)
                break          # one mutant per line keeps the run affordable
            if chosen is None and deletable(original):
                indent = original[:len(original) - len(original.lstrip())]
                chosen = ("statement deleted", indent + "/* mutant: statement removed */\n")
            if chosen is None:
                continue
            label, mutated = chosen
            mutants.append({
                "file": rel, "line": lineno, "op": label,
                "before": original.strip()[:120],
                "after": mutated.strip()[:120],
                "_index": lineno - 1, "_text": mutated,
            })
    # deterministic spread across files rather than exhausting the first one
    mutants.sort(key=lambda m: (m["line"], m["file"]))
    if len(mutants) > limit:
        step = len(mutants) / float(limit)
        mutants = [mutants[int(i * step)] for i in range(limit)]
    return mutants


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--test-cmd", default=None,
                    help="Test command, e.g. \"npm test\". Auto-detected when omitted.")
    ap.add_argument("--max-mutants", type=int, default=20)
    ap.add_argument("--timeout", type=int, default=300, help="Per-mutant test timeout, seconds.")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    rc, top, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    if rc != 0:
        print("mutate: not a git repository", file=sys.stderr)
        return 2
    repo = top.strip()

    rc, dirty, _ = run(["git", "status", "--porcelain"], cwd=repo)
    if dirty.strip():
        print("mutate: working tree is dirty — commit or stash first "
              "(mutants are written in place and restored)", file=sys.stderr)
        return 2

    cmd = resolve(args.test_cmd.split()) if args.test_cmd else detect_test_cmd(repo)
    if not cmd:
        print("mutate: no test command found — pass --test-cmd", file=sys.stderr)
        return 2
    cmd = resolve(cmd)

    rc, merge_base, _ = run(["git", "merge-base", args.base, "HEAD"], cwd=repo)
    base_ref = merge_base.strip() or args.base

    rc, head_sha, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd=repo)
    head_sha = head_sha.strip() if rc == 0 else "unknown"

    print("mutate: verifying the suite is green ...", file=sys.stderr)
    started = time.time()
    rc, _, _ = run(cmd, cwd=repo, timeout=args.timeout)
    if rc != 0:
        print("mutate: the test suite is not green — fix it before measuring mutants",
              file=sys.stderr)
        return 2
    clean_run = max(1.0, time.time() - started)

    targets = changed_lines(repo, base_ref)
    mutants = build_mutants(repo, targets, args.max_mutants)
    if not mutants:
        print("mutate: no mutable changed lines found", file=sys.stderr)
        report = {"slug": args.slug, "head": head_sha, "score_pct": None, "killed": 0,
                  "survived": 0, "total": 0, "note": "no mutable changed lines"}
    else:
        print("mutate: %d mutants across %d files (~%.0fs each)"
              % (len(mutants), len(targets), clean_run), file=sys.stderr)
        killed, survived, errored = 0, [], 0
        per_timeout = max(args.timeout, int(clean_run * 4))
        for i, mut in enumerate(mutants, 1):
            path = os.path.join(repo, mut["file"])
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines(keepends=True)
            backup = lines[mut["_index"]]
            lines[mut["_index"]] = mut["_text"]
            try:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.writelines(lines)
                rc, _, _ = run(cmd, cwd=repo, timeout=per_timeout)
            finally:
                lines[mut["_index"]] = backup
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.writelines(lines)
            if rc == 124:
                errored += 1                      # timeout counts as killed-by-hang
                killed += 1
                mark = "timeout"
            elif rc != 0:
                killed += 1
                mark = "killed"
            else:
                survived.append({k: mut[k] for k in ("file", "line", "op", "before", "after")})
                mark = "SURVIVED"
            print("mutate: [%d/%d] %s:%d %s -> %s"
                  % (i, len(mutants), mut["file"], mut["line"], mut["op"], mark),
                  file=sys.stderr)

        total = len(mutants)
        report = {
            "slug": args.slug,
            "base": base_ref[:12],
            "head": head_sha,
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "test_cmd": " ".join(os.path.basename(cmd[0]) if i == 0 else c
                                 for i, c in enumerate(cmd)),
            "score_pct": round(100.0 * killed / total, 1) if total else None,
            "killed": killed, "survived": len(survived), "total": total,
            "timeouts": errored,
            "survivors": survived,
        }

    out_dir = os.path.join(repo, ".ai", args.slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "mutation.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    print(json.dumps(report, indent=2))
    print("\nmutate: wrote %s" % out_path, file=sys.stderr)
    if report.get("survivors"):
        print("mutate: %d survivor(s) — kill each with a real assertion, or justify it as "
              "equivalent in review.md" % len(report["survivors"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
