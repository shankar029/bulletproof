#!/usr/bin/env python3
"""bulletproof mutation probe.

Answers the one question coverage cannot: *would the tests actually catch this
code being wrong?* It mutates only the lines this change touched, runs the
project's own test command against each mutant, and reports which mutants
survived.

  python mutate.py --slug my-feature --base origin/main
  python mutate.py --slug my-feature --base origin/main -- node --test "math case.test.mjs"

Design notes:
  * Diff-scoped. Mutating the whole repository is pointless and slow; the
    question is whether *this change* is tested.
  * Conservative. Textual candidate discovery spans languages; classified proof
    currently requires native Node >=22 and JavaScript-family inputs. Other
    commands may run, but exit codes alone never count as assertion evidence.
  * Honest. Survivors are reported with file, line and the exact edit, so each
    one is either killed with a real assertion or justified as equivalent.
    Nothing here decides that for you.

Exit codes: 0 = complete classified measurement (threshold belongs to probe),
2 = incomplete/unavailable/invalid invocation. Reports are fresh per-run artifacts
under .ai/<slug>/evidence/runs/<run-id>/mutation.json, never reused latest scores.
"""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone

from evidence import exclusive_lock, source_snapshot, write_json_atomic
from run import run_capture

CODE_EXT = {".py", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
            ".cs", ".rb", ".php", ".swift", ".c", ".h", ".cc", ".cpp", ".scala"}
JS_EXT = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}
DEFAULT_MAX_MUTANTS = 20

# (pattern, replacement, label) — order matters: longer operators first so that
# ">=" is never partially rewritten by the ">" rule.
OPERATORS = [
    (r"(?<![!<>=])===(?!=)", "!==", "equality === -> !=="),
    (r"(?<![!<>=])!==(?!=)", "===", "equality !== -> ==="),
    (r"(?<![<>=])>=(?![=>])", "<", "boundary >= -> <"),
    (r"(?<![<>=])<=(?![=>])", ">", "boundary <= -> >"),
    (r"(?<![!<>=])!=(?!=)", "==", "equality != -> =="),
    (r"(?<![!<>=])==(?!=|>)", "!=", "equality == -> !="),
    (r"&&(?!=)", "||", "logic && -> ||"),
    (r"\|\|(?!=)", "&&", "logic || -> &&"),
    (r"\band\b", "or", "logic and -> or"),
    (r"\bor\b", "and", "logic or -> and"),
    (r"(?<![=<>-])>(?![=>])", "<", "comparison > -> <"),
    (r"(?<![=<>])<(?![=<])", ">", "comparison < -> >"),
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
    if (not stripped.endswith(";") or DECLARATION_START.match(stripped)
            or re.match(r"^(?:exports[.\[]|module\.exports\b)", stripped)):
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


def run(cmd, cwd=None, timeout=900, *, env=None):
    """Run a command, returning (rc, stdout, stderr). Never raises.

    `timeout` is the absolute ceiling; the command is also killed (whole tree) if
    it goes silent for `idle` seconds — a hang no longer waits out the full
    ceiling. Best-effort PID-scoped tree cleanup uses run_capture; rc 124 is an
    idle kill, 125 a maximum-time kill, and neither is a mutation kill.
    """
    idle = min(300.0, float(timeout)) if timeout else 300.0
    return run_capture(cmd, cwd=cwd, idle=idle, max_total=float(timeout or 0), env=env)


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
    files = native_test_files(Path(repo))
    return ["node", "--test", *files] if files and shutil.which("node") else None


def native_test_files(cwd):
    """Bounded discovery, never recurse into a benchmark arm/nested package."""
    return sorted(str(p.relative_to(cwd)) for directory in (cwd, cwd / "test", cwd / "tests")
                  if directory.is_dir() and (directory == cwd or not (directory / "package.json").exists())
                  for p in directory.iterdir()
                  if p.is_file() and re.search(r"\.test\.(?:js|mjs|cjs)$", p.name))


def select_test_run(repo_root: Path, test_cwd: Path, argv: list[str] | None):
    if not test_cwd.is_dir() or not test_cwd.is_relative_to(repo_root):
        raise ValueError("Test cwd must be a directory inside the Git root")
    selected = resolve(argv or detect_test_cmd(str(test_cwd)))
    if not selected:
        raise ValueError("No test command found; use -- COMMAND ARG...")
    native = Path(selected[0]).stem.lower() == "node" and "--test" in selected
    test_files = []
    version = None
    if native:
        if any(a.startswith("--test-reporter") for a in selected):
            raise ValueError("Conflicting reporter configuration; remove --test-reporter options")
        rc, output, _ = run([selected[0], "--version"], timeout=30)
        if rc or not re.fullmatch(r"v(\d+)\.\d+\.\d+\s*", output) or int(output[1:].split(".")[0]) < 22:
            raise ValueError("Native structured results require Node >=22")
        version = output.strip()
        # Keep caller parameters unchanged; never confuse a regex parameter or preload
        # script with a test path. Unknown positional forms fail closed.
        takes_value = {"--test-name-pattern", "--test-skip-pattern", "--test-timeout",
                       "--test-concurrency", "--test-shard", "--import", "--require", "-r",
                       "--loader", "--experimental-loader", "--conditions", "-C"}
        consume_value = False
        positional_only = False
        for argument in selected[1:]:
            if consume_value:
                consume_value = False
            elif argument == "--":
                positional_only = True
            elif not positional_only and argument in takes_value:
                consume_value = True
            elif not positional_only and argument.startswith("-"):
                continue
            else:
                candidate = (test_cwd / argument).resolve(strict=True)
                if not candidate.is_relative_to(repo_root) or not candidate.is_file():
                    raise ValueError("Native argv requires concrete in-repository test files: " + argument)
                test_files.append(argument)
        if consume_value:
            raise ValueError("Missing native option parameter")
        if not test_files:
            discovered = native_test_files(test_cwd)
            if not discovered:
                raise ValueError("No explicit native test files; pass concrete file argv")
            selected.extend(discovered)
            test_files = discovered
        selected.insert(1, "--test-reporter=" + Path(__file__).with_name("native_result.mjs").resolve().as_uri())
    return {
        "command": {"argv": selected, "cwd": test_cwd.relative_to(repo_root).as_posix(),
                    "runtime": {"executable": selected[0], "observed_version": version},
                    "idle_seconds": 300.0, "max_seconds": 300.0,
                    "environment": {"NODE_TEST_CONTEXT": None} if native else {}},
        "runner": "node-native" if native else "process",
        "test_files": [str((test_cwd / name).relative_to(repo_root).as_posix()) for name in test_files],
        "assertions": [],
    }


def changed_lines(repo, base):
    """{path: set(line numbers)} for lines added or modified vs the base."""
    rc, out, error = run(["git", "-c", "core.quotePath=false", "diff", "--no-ext-diff",
                         "--no-renames", "-U0", base, "HEAD"], cwd=repo)
    if rc != 0:
        raise ValueError("Cannot resolve changed lines: " + error)
    result = {}
    current = None
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:].rstrip("\t")
            if current.startswith('"'):
                current = json.loads(current)
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


def build_mutants(repo, targets, limit, *, unsupported=None):
    mutants = []
    for rel in sorted(targets):
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8", newline="") as fh:
                lines = fh.read().splitlines(keepends=True)
        except (OSError, UnicodeError):
            if unsupported is not None:
                unsupported.append({"file": rel, "reason": "unreadable UTF-8 input"})
            continue
        # Without a parser, multiline comments/templates/regex literals are ambiguous.
        # Skip conservatively and expose the unsupported scope, rather than count junk.
        js = Path(rel).suffix.lower() in JS_EXT
        ambiguous = js and any(token in "".join(lines) for token in ("/*", "*/", "`"))
        for lineno in sorted(targets[rel]):
            if lineno > len(lines):
                continue
            original = lines[lineno - 1]
            if not is_mutable(original):
                continue
            masked = mask_strings(original)
            if ambiguous or (js and "/" in masked.replace("//", "")):
                if unsupported is not None:
                    unsupported.append({"file": rel, "line": lineno,
                                        "reason": "ambiguous comment/template/regex or division syntax"})
                continue
            masked = masked.split("//", 1)[0] if js else masked
            chosen = None
            for pattern, repl, label in OPERATORS:
                if js and label.startswith(("logic and ", "logic or ", "literal True ", "literal False ")):
                    continue
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


def parse_native(text):
    """Validate the shared reporter protocol, without scraping TAP or log text."""
    try:
        value = json.loads(text)
        outcomes = {"pass", "assertion-fail", "setup-error", "cancelled", "skipped", "todo"}
        if (type(value["schema_version"]) is not int or value["schema_version"] != 1
                or not isinstance(value["complete"], bool)
                or not isinstance(value["tests"], list)
                or type(value["leaf_count"]) is not int
                or value["leaf_count"] != len(value["tests"])
                or not isinstance(value["logs"], list)):
            return None
        for test in value["tests"]:
            if (not isinstance(test["file"], str) or not test["file"]
                    or not isinstance(test["name"], str) or type(test["line"]) is not int
                    or test["line"] < 1 or type(test["nesting"]) is not int
                    or test["nesting"] < 0 or test["outcome"] not in outcomes):
                return None
            if test["outcome"] == "assertion-fail":
                error = test["error"]
                if (error["name"] != "AssertionError" or error["cause_code"] != "ERR_ASSERTION"
                        or not error["operator"] or not error["assertion_stack"]):
                    return None
        return value
    except (ValueError, KeyError, TypeError):
        return None


def classify_native(result, rc, baseline=None):
    if rc in (124, 125):
        return "timeout"
    if not result or not result["complete"] or not result["leaf_count"]:
        return "unclassified"
    outcomes = [t["outcome"] for t in result["tests"]]
    if any(o in ("setup-error", "cancelled") for o in outcomes):
        return "setup-error"
    if any(o in ("skipped", "todo") for o in outcomes):
        return "unclassified"
    if baseline:
        def inventory(value):
            return sorted((t["file"], t["line"], t["name"], t["nesting"]) for t in value["tests"])
        if inventory(baseline) != inventory(result):
            return "unclassified"
    if rc != 0 and "assertion-fail" in outcomes:
        return "killed-assertion"
    if rc == 0 and all(o == "pass" for o in outcomes):
        return "survived"
    return "unclassified"


def validate_mutation_results(report, repo):
    """Reconcile a complete report with canonical candidates and native evidence."""
    def check_capture(value):
        if (not isinstance(value, dict) or type(value.get("returncode")) is not int or
                not isinstance(value.get("stdout"), str) or not isinstance(value.get("stderr"), str)):
            raise ValueError("Mutation process evidence is incomplete")

    results = report.get("results")
    unsupported = []
    targets = changed_lines(str(repo), report["source"]["base"])
    if any(Path(path).suffix.lower() not in JS_EXT for path in targets):
        raise ValueError("Mutation changed scope includes unsupported languages")
    candidates = build_mutants(str(repo), targets, DEFAULT_MAX_MUTANTS, unsupported=unsupported)
    if unsupported or not isinstance(results, list) or not results or len(results) != len(candidates):
        raise ValueError("Mutation results do not match the complete candidate inventory")
    baseline = report["baseline"]
    raw_baseline = report["baseline_artifacts"]
    check_capture(raw_baseline)
    if (parse_native(json.dumps(baseline)) is None or raw_baseline["returncode"] != 0 or
            parse_native(raw_baseline["stdout"]) != baseline or
            classify_native(baseline, raw_baseline["returncode"]) != "survived"):
        raise ValueError("Mutation baseline evidence is inconsistent")
    killed = survived = 0
    for result, candidate in zip(results, candidates):
        if not isinstance(result, dict) or result.get("outcome") not in {"killed-assertion", "survived"}:
            raise ValueError("Mutation results contain missing or ungraded outcomes")
        if type(result.get("line")) is not int or (result.get("file"), result.get("line"), result.get("operator")) != (
                candidate["file"], candidate["line"], candidate["op"]):
            raise ValueError("Mutation result identity differs from its canonical candidate")
        original = (repo / candidate["file"]).read_bytes()
        if (result.get("before_sha256") != _sha(original) or
                result.get("after_sha256") != _sha(_mutant_bytes(original, candidate))):
            raise ValueError("Mutation result bytes do not match its candidate")
        artifacts = result["artifacts"]
        syntax = artifacts["syntax"]
        execution = artifacts["execution"]
        check_capture(syntax)
        check_capture(execution)
        native = parse_native(execution["stdout"])
        if (type(syntax["returncode"]) is not int or syntax["returncode"] != 0 or
                type(execution["returncode"]) is not int or
                native != parse_native(json.dumps(artifacts["native"])) or
                classify_native(native, execution["returncode"], baseline) != result["outcome"]):
            raise ValueError("Mutation result classification disagrees with its native evidence")
        killed += result["outcome"] == "killed-assertion"
        survived += result["outcome"] == "survived"
    expected = {"total": len(results), "killed": killed, "survived": survived, "ungraded": 0}
    if any(type(report.get(key)) is not int or report[key] != value for key, value in expected.items()):
        raise ValueError("Mutation counters disagree with classified results")
    score = round(100.0 * killed / len(results), 1)
    if type(report.get("score_pct")) not in (int, float) or report["score_pct"] != score:
        raise ValueError("Mutation score disagrees with classified results")


def _git(repo, *argv):
    rc, output, error = run(["git", *argv], cwd=repo, timeout=30)
    if rc:
        raise ValueError("Git command failed: " + error)
    return output.strip()


def _safe_component(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise ValueError("slug/run-id must be a single safe path component")
    return value


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _mutant_bytes(original, mutant):
    lines = original.decode("utf-8").splitlines(keepends=True)
    lines[mutant["_index"]] = mutant["_text"]
    return "".join(lines).encode("utf-8")


def _reserve_report(path, run_id):
    """Claim only our output, not the run directory shared with probe."""
    content = json.dumps({"run_id": run_id, "complete": False,
                          "reason": "Mutation in progress", "token": uuid.uuid4().hex}).encode("utf-8")
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        identity = os.fstat(stream.fileno())
    return identity, content


def _publish_report(path, report, reservation):
    identity, content = reservation
    current = path.stat()
    if ((current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino)
            or path.read_bytes() != content):
        raise RuntimeError("Mutation report ownership changed; refusing overwrite")
    write_json_atomic(path, report)


def _clean_tree(repo, owned_outputs):
    rc, status, error = run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                            cwd=repo, timeout=30)
    if rc:
        raise ValueError("Cannot check source cleanliness: " + error)
    for entry in status.split("\0"):
        if entry and entry[3:].replace("\\", "/") not in owned_outputs:
            raise ValueError("Working tree is dirty; commit/stash source inputs first: " + entry)


def _execute_test(test_run, repo, timeout):
    env = os.environ.copy()
    if test_run["runner"] == "node-native":
        env.pop("NODE_TEST_CONTEXT", None)
        if "--test-reporter" in env.get("NODE_OPTIONS", ""):
            raise ValueError("Conflicting reporter in NODE_OPTIONS")
    rc, out, err = run(test_run["command"]["argv"],
                       cwd=repo / test_run["command"]["cwd"], timeout=timeout, env=env)
    native = parse_native(out) if test_run["runner"] == "node-native" else None
    return rc, native, {"returncode": rc, "stdout": out, "stderr": err}


def _measure(repo, args, report, report_path):
    owned_output = report_path.relative_to(repo).as_posix()
    outputs = [
        {"path": owned_output, "reason": "Exact fresh invocation-owned mutation report"},
        {"path": report_path.with_name("metrics.json").relative_to(repo).as_posix(),
         "reason": "Exact same-run metrics report published by the invoking probe"},
        {"path": ".ai/%s/metrics.json" % args.slug,
         "reason": "Generated metrics display alias owned by the invoking probe"},
    ]
    _clean_tree(repo, {item["path"] for item in outputs})
    base = _git(repo, "merge-base", args.base, "HEAD")
    head = _git(repo, "rev-parse", "HEAD")
    scope = {"directories": ["."], "files": [], "excluded_outputs": [
        {"path": ".git", "reason": "Git administrative metadata, not source inputs"},
        *outputs,
    ]}
    source = source_snapshot(repo, scope)
    source.update(base=base, head=head)
    report["source"] = source
    test_cwd = Path(args.test_cwd or args.repo).resolve(strict=True)
    argv = args.command[1:] if args.command[:1] == ["--"] else args.command
    if args.test_cmd:
        if argv:
            raise ValueError("--test-cmd and remainder argv are mutually exclusive")
        if any(c in args.test_cmd for c in "'\"\\"):
            raise ValueError("Ambiguous legacy quoting/escaping; use -- COMMAND ARG... instead")
        argv = args.test_cmd.split()
    test_run = select_test_run(repo, test_cwd, argv or None)
    test_run["command"].update(idle_seconds=min(300, args.timeout), max_seconds=args.timeout)
    report["test_run"] = test_run
    unsupported = []
    targets = changed_lines(str(repo), base)
    # Language coverage is a property of the changed scope, not of the sampled
    # candidates. A limit (or an operator-free Python line) cannot hide a gap.
    unsupported.extend({"file": rel, "reason": "Unsupported changed language for native assertion proof"}
                       for rel, lines in sorted(targets.items())
                       if lines and Path(rel).suffix.lower() not in JS_EXT)
    mutants = build_mutants(str(repo), targets, args.max_mutants, unsupported=unsupported)
    report["unsupported_scope"] = unsupported
    for mutant in mutants:
        original = (repo / mutant["file"]).read_bytes()
        report["results"].append({
            "file": mutant["file"], "line": mutant["line"], "operator": mutant["op"],
            "before_sha256": _sha(original), "after_sha256": _sha(_mutant_bytes(original, mutant)),
            "outcome": "unclassified",
            "artifacts": {"reason": "Not executed; a green classified baseline is required"},
        })
    report["reason"] = "Baseline is unavailable"
    rc, baseline, artifacts = _execute_test(test_run, repo, args.timeout)
    report["baseline"] = baseline
    report["baseline_artifacts"] = artifacts
    if test_run["runner"] != "node-native":
        report["reason"] = "Unsupported custom runner; process exit codes are not assertion evidence"
        return
    if classify_native(baseline, rc) != "survived":
        report["reason"] = "Baseline requires positive, complete, non-skipped passing leaf inventory"
        return
    if not mutants:
        report["reason"] = "No mutable changed lines; no graded mutation measurement"
        return
    for mutant, result in zip(mutants, report["results"]):
        if source_snapshot(repo, scope)["scope_sha256"] != source["scope_sha256"]:
            report["reason"] = "Source changed during measurement; recovery required"
            return
        path = repo / mutant["file"]
        original = path.read_bytes()
        edited = _mutant_bytes(original, mutant)
        result.update(before_sha256=_sha(original), after_sha256=_sha(edited))
        if path.suffix.lower() not in JS_EXT:
            result["artifacts"] = {"reason": "Unsupported mutation language for native assertion proof"}
            continue
        # Verify immediately before taking ownership of this edit. This is detection,
        # not a filesystem sandbox: arbitrary child/agent writes are outside our control.
        if path.read_bytes() != original:
            raise RuntimeError("Competing source edit before mutation")
        path.write_bytes(edited)
        try:
            env = os.environ.copy()
            env.pop("NODE_TEST_CONTEXT", None)
            syntax_rc, syntax_out, syntax_err = run(
                [test_run["command"]["argv"][0], str(Path(__file__).with_name("native_result.mjs")),
                 "--check", str(path)],
                cwd=test_cwd, timeout=args.timeout, env=env)
            result["artifacts"] = {"syntax": {"returncode": syntax_rc, "stdout": syntax_out,
                                              "stderr": syntax_err}}
            if syntax_rc:
                result["outcome"] = ("timeout" if syntax_rc in (124, 125) else
                                     "invalid-syntax" if syntax_rc == 1 else "unclassified")
            else:
                rc, native, execution = _execute_test(test_run, repo, args.timeout)
                result["artifacts"].update(execution=execution, native=native)
                result["outcome"] = classify_native(native, rc, baseline)
        finally:
            if path.read_bytes() == edited:
                path.write_bytes(original)
            else:
                # Keep both the intervening edit and recoverable original bytes.
                result["outcome"] = "unclassified"
                result["artifacts"]["original_base64"] = base64.b64encode(original).decode("ascii")
                raise RuntimeError("Competing edit preserved; recovery required for " + mutant["file"])
        print("mutate: %s:%s -> %s" % (mutant["file"], mutant["line"], result["outcome"]), file=sys.stderr)
    report["reason"] = "Measurement completed"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--test-cmd", default=None,
                    help="Test command, e.g. \"npm test\". Auto-detected when omitted.")
    ap.add_argument("--max-mutants", type=int, default=DEFAULT_MAX_MUTANTS)
    ap.add_argument("--timeout", type=int, default=300, help="Per-mutant test timeout, seconds.")
    ap.add_argument("--test-cwd")
    ap.add_argument("--run-id")
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    report = {"schema_version": 2, "run_id": args.run_id or uuid.uuid4().hex, "source": None,
              "test_run": None, "baseline": None, "results": [], "score_pct": None,
              "complete": False, "reason": "Not measured", "restored_sha256": None,
              "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "killed": 0, "survived": 0, "total": 0, "ungraded": 0}
    try:
        if args.max_mutants <= 0 or args.timeout <= 0:
            raise ValueError("--max-mutants and --timeout must be positive")
        _safe_component(args.slug)
        _safe_component(report["run_id"])
        repo = Path(_git(Path(args.repo).resolve(strict=True), "rev-parse", "--show-toplevel")).resolve()
        out_path = repo / ".ai" / args.slug / "evidence" / "runs" / report["run_id"] / "mutation.json"
        if out_path.resolve() != out_path:
            raise ValueError("Linked output paths are unsupported")
        # Probe may already own this run directory. Only the mutation report is
        # exclusive: an old report or interrupted reservation must never be reused.
        out_path.parent.mkdir(parents=True, exist_ok=True)
        reservation = _reserve_report(out_path, report["run_id"])
    except (OSError, ValueError) as error:
        print("mutate: " + str(error), file=sys.stderr)
        return 2
    try:
        lock_path = Path(_git(repo, "rev-parse", "--git-path", "bulletproof-mutation.lock"))
        if not lock_path.is_absolute():
            lock_path = repo / lock_path
        with exclusive_lock(lock_path, {"token": uuid.uuid4().hex, "run_id": report["run_id"]}):
            try:
                _measure(repo, args, report, out_path)
            finally:
                if report["source"]:
                    report["restored_sha256"] = source_snapshot(repo, report["source"]["scope"])["scope_sha256"]
    except (OSError, ValueError, RuntimeError) as error:
        report["reason"] = str(error)
    report["total"] = len(report["results"])
    report["killed"] = sum(r["outcome"] == "killed-assertion" for r in report["results"])
    report["survived"] = sum(r["outcome"] == "survived" for r in report["results"])
    graded = report["killed"] + report["survived"]
    report["ungraded"] = report["total"] - graded
    report["score_pct"] = round(100.0 * report["killed"] / graded, 1) if graded else None
    report["complete"] = bool(
        graded and not report["ungraded"] and not report.get("unsupported_scope")
        and report["reason"] == "Measurement completed"
        and report["source"]["scope_sha256"] == report["restored_sha256"])
    if report["reason"] == "Measurement completed" and not report["complete"]:
        report["reason"] = "Incomplete: ungraded/unsupported scope or source restoration mismatch"
    try:
        _publish_report(out_path, report, reservation)
    except (OSError, RuntimeError) as error:
        print("mutate: could not write fresh report: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    print("mutate: wrote %s" % out_path, file=sys.stderr)
    return 0 if report["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
