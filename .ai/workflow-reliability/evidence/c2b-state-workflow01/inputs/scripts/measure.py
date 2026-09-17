"""Canonical code census and Q1 measurement composition; never imports probe/guard."""

import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile

from evidence import _json_bytes, source_snapshot
import measure_graph as graph
from run import run_capture

SKIP_DIRS = {".git", ".ai", "node_modules", "dist", "build", "target", "vendor",
             "__pycache__", ".venv", "venv", ".tox", ".next", "coverage", "out"}
CODE_EXT = {".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
            ".cs", ".rb", ".php", ".swift", ".c", ".h", ".cc", ".cpp", ".scala"}
JS_EXT = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
LOWER_BETTER = {"duplication_pct", "complexity_max", "complexity_avg",
                "cycles", "dead_exports", "static_findings"}
REQUIRED = [*sorted(LOWER_BETTER), "mutation_score_pct", "diff_coverage_pct", "architecture_rules"]
MUTATION_FLOOR = 60.0
TOLERANCE = {"complexity_max": 2, "complexity_avg": 0.3, "duplication_pct": 0.5}
GREENFIELD_LIMITS = {"duplication_pct": (5.0, 12.0), "complexity_max": (15, 25),
                    "complexity_avg": (4.0, 8.0), "cycles": (0, 0),
                    "dead_exports": (10, 40), "static_findings": (10, 40),
                    "architecture_rules": (0, 0)}
BASELINE_POLICY = "isolated-versioned-attribute-checkout-v1"
# Actual command/attribute/sentinel qualification is preserved in the Q1 evidence.
# Different builds need qualification, not a guessed compatibility claim.
QUALIFIED_BASELINE_GIT = {
    ("a612b966632d6d5c31829f45c62e7a161f428c79d8c2d15c56d7a005820dadb0",
     "22a15e7333438dac6993ec3af1a4ee99a48f4555aa7acd0734f23bc77f92d7eb"): "2.53.0.windows.4",
}


def _git_environment(empty):
    # Git's GIT_CONFIG_* injection and repository/index/object overrides must not
    # select the authority for the independent tree. No supplied config is edited.
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_ATTR_NOSYSTEM="1", GIT_NO_REPLACE_OBJECTS="1", GIT_TERMINAL_PROMPT="0",
               HOME=str(empty), USERPROFILE=str(empty), XDG_CONFIG_HOME=str(empty))
    return env


def baseline_binding():
    executable = shutil.which("git")
    if not executable:
        raise ValueError("Baseline Git executable unavailable")
    executable = Path(executable).resolve(strict=True)
    if executable.parent.name == "cmd":
        # Qualified distribution's cmd/git.exe is a launcher. Invoke and bind the
        # actual core directly, including its bundled application DLL inputs.
        executable = executable.parents[1] / "clangarm64/bin/git.exe"
    sha256 = hashlib.sha256(executable.read_bytes()).hexdigest()
    dlls = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(executable.parent.glob("*.dll"))}
    qualification = (sha256, graph.digest(dlls))
    if qualification not in QUALIFIED_BASELINE_GIT:
        raise ValueError("Baseline Git build is unqualified: " + str(executable) + " sha256=" + sha256)
    return {"policy": BASELINE_POLICY, "git": {"path": str(executable),
            "sha256": sha256, "version": QUALIFIED_BASELINE_GIT[qualification], "bundled_dlls": dlls},
            "mode_projection": "regular-file-only-windows" if os.name == "nt" else "posix-executable"}


def _tree_modes(tree):
    modes, folded = {}, set()
    for record in tree.split("\0"):
        if not record:
            continue
        metadata, name = record.split("\t", 1)
        mode, kind, _oid = metadata.split(" ")
        graph.relative_name(name)
        key = name.casefold() if os.name == "nt" else name
        if key in folded:
            raise ValueError("Baseline ambiguous tree path: " + name)
        folded.add(key)
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("Baseline unsupported tree type/mode: %s %s %s" % (name, kind, mode))
        modes[name] = mode
    return modes


def baseline_tree(root, revision):
    """Bind immutable Git modes separately from platform worktree observations."""
    binding = baseline_binding()
    with tempfile.TemporaryDirectory(prefix="bulletproof-git-tree-") as temporary:
        code, tree, error = run_capture(
            [binding["git"]["path"], "ls-tree", "-r", "-z", "--full-tree", revision],
            cwd=root, env=_git_environment(Path(temporary).resolve()), idle=30, max_total=90)
        if code:
            raise ValueError("Baseline cannot read immutable tree modes: " + error)
    return {"binding": binding, "tree_modes": _tree_modes(tree)}


def materialize_baseline(repo, target, revision):
    """Materialize only the immutable tree under qualified built-in attributes.

    clone --no-checkout and read-tree do not run checkout filters. Ask Git's
    cached attribute interpreter (including macros/nested precedence) before the
    first capable operation, checkout-index. Never consult the caller's index.
    The caller owns target; temporary configuration resources belong to this call.
    """
    repo = graph.root_path(repo)
    target = Path(target)
    if target.exists() or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision):
        raise ValueError("Baseline requires a fresh owned destination and immutable Git ID")
    binding = baseline_binding()
    with tempfile.TemporaryDirectory(prefix="bulletproof-git-policy-") as temporary:
        empty = Path(temporary).resolve()
        env = _git_environment(empty)
        options = [binding["git"]["path"], "-c", "core.autocrlf=false", "-c", "core.eol=lf",
                   "-c", "core.attributesFile=" + os.devnull, "-c", "core.hooksPath=" + str(empty)]

        def git(args, cwd):
            code, output, error = run_capture(options + args, cwd=cwd, env=env, idle=30, max_total=90)
            if code:
                raise ValueError("Baseline Git operation failed (%s): %s" % (args[0], error))
            return output

        git(["clone", "--quiet", "--no-hardlinks", "--no-checkout",
             "--template=" + str(empty), str(repo), str(target)], target.parent)
        git(["update-ref", "--no-deref", "HEAD", revision], target)
        tree = git(["ls-tree", "-r", "-z", "--full-tree", revision], target)
        modes = _tree_modes(tree)
        git(["read-tree", revision], target)
        names = sorted(modes)
        # Bound Windows argv length, not the census: every path is checked.
        batch, size = [], 0

        def attributes(paths):
            raw = git(["check-attr", "--cached", "--all", "-z", "--", *paths], target).split("\0")
            if raw.pop() != "" or len(raw) % 3:
                raise ValueError("Baseline incomplete attribute census")
            seen = set()
            for offset in range(0, len(raw), 3):
                name, attr, value = raw[offset:offset + 3]
                if name not in paths or (name, attr) in seen:
                    raise ValueError("Baseline attribute census mismatch")
                seen.add((name, attr))
                if attr not in {"filter", "ident", "working-tree-encoding", "text", "eol", "crlf"}:
                    continue
                # --all omits genuinely unspecified attributes. Present textual
                # state markers can instead be literal values (e.g. filter=unset).
                allowed = set()
                if attr == "text":
                    allowed = {"set", "auto"}
                elif attr == "eol":
                    allowed = {"lf", "crlf"}
                if value not in allowed:
                    reason = " (ambiguous present declaration)" if value in {"unset", "unspecified"} else ""
                    raise ValueError("Baseline unsupported attribute %s=%s: %s%s" % (attr, value, name, reason))

        for name in names:
            if batch and size + len(name) > 6000:
                attributes(batch)
                batch, size = [], 0
            batch.append(name)
            size += len(name) + 3
        if batch:
            attributes(batch)
        git(["checkout-index", "--all", "--force"], target)
        if baseline_binding() != binding:
            raise ValueError("Baseline Git identity changed during materialization")
        actual = _baseline_files(target)
        if set(actual) != set(modes):
            raise ValueError("Baseline materialization path set differs from immutable tree")
        for name, mode in modes.items():
            if os.name != "nt" and actual[name]["executable"] != (mode == "100755"):
                raise ValueError("Baseline materialization executable mode mismatch: " + name)
        return {"binding": binding, "tree_modes": modes}


def _baseline_files(root):
    """All subject files, including non-code and analyzer-excluded inputs."""
    result = {}

    def fail(error):
        raise error

    for directory, dirs, files in os.walk(root, onerror=fail, followlinks=False):
        if Path(directory) == root:
            dirs[:] = [name for name in dirs if name != ".git"]
            files = [name for name in files if name != ".git"]
        for name in sorted(dirs + files):
            relative = (Path(directory) / name).relative_to(root).as_posix()
            path = graph.input_path(root, relative)
            mode = path.stat().st_mode
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode):
                raise ValueError("Baseline unsupported non-regular input: " + relative)
            result[relative] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                "executable": bool(mode & 0o111) if os.name != "nt" else None}
    return result


def validate_baseline(root, revision):
    try:
        with tempfile.TemporaryDirectory(prefix="bulletproof-expected-base-") as temporary:
            expected = Path(temporary).resolve() / "tree"
            materialize_baseline(root, expected, revision)
            actual, immutable = _baseline_files(Path(root)), _baseline_files(expected)
            if actual != immutable:
                different = sorted(name for name in actual.keys() | immutable.keys()
                                   if actual.get(name) != immutable.get(name))
                raise ValueError("Baseline differs from immutable materialization: " + repr(different))
    except OSError as error:
        raise ValueError("Baseline cannot be established: " + str(error)) from error


def _walk(root):
    root = graph.root_path(Path(root).absolute())
    entries, exclusions, errors, folded = [], [], [], {}

    def error(directory, entry, operation, reason):
        errors.append({"directory": directory, "entry": entry, "operation": operation, "reason": str(reason)})

    def walk_error(failure):
        directory = Path(failure.filename or root).absolute().relative_to(root).as_posix()
        error(directory, None, "walk", failure)

    for base, dirs, files in os.walk(root, onerror=walk_error, followlinks=False):
        relative_dir = Path(base).relative_to(root).as_posix()
        kept = []
        for name in sorted(dirs + files):
            relative = (Path(base) / name).relative_to(root).as_posix()
            is_directory = name in dirs
            if is_directory and (name in SKIP_DIRS or name.startswith(".")):
                exclusions.append({"path": relative, "kind": "directory",
                                   "reason": "Deliberate code_files directory exclusion",
                                   "origin_ref": "measure.code_files/v1"})
                continue
            try:
                graph.relative_name(relative)
                key = relative.casefold() if os.name == "nt" else relative
                if key in folded and folded[key] != relative:
                    raise ValueError("Case-fold path collision: " + folded[key])
                folded[key] = relative
                path = graph.input_path(root, relative)
                if is_directory:
                    path.stat()
                    kept.append(name)
                    continue
                suffix = path.suffix.lower()
                if suffix not in CODE_EXT:
                    continue
                if not path.is_file():
                    raise OSError("Code input is not a regular file")
                path.stat()
            except (OSError, ValueError) as failure:
                error(relative_dir, relative, "stat", failure)
                continue
            try:
                content = path.read_bytes()
            except OSError as failure:
                error(relative_dir, relative, "read", failure)
                continue
            language = ("python" if suffix == ".py" else "javascript" if suffix in {".js", ".mjs", ".cjs"}
                        else "typescript" if suffix == ".ts" else "unsupported")
            entries.append({"path": relative, "sha256": hashlib.sha256(content).hexdigest(),
                            "bytes": len(content), "language": language, "suffix": suffix,
                            "role": "test" if graph._test_path(relative) else "production",
                            "parser": None, "parse_state": "unsupported" if language == "unsupported" else "pending",
                            "reason": "No declared language adapter" if language == "unsupported" else "",
                            "diagnostics": []})
        dirs[:] = sorted(kept)
    return sorted(entries, key=lambda item: item["path"]), sorted(exclusions, key=lambda item: item["path"]), errors


def code_files(root):
    entries, _, errors = _walk(root)
    if errors:
        raise OSError("Code enumeration failed: " + repr(errors))
    return [str(Path(root).absolute() / entry["path"]) for entry in entries]


def git_head(root):
    with tempfile.TemporaryDirectory(prefix="bulletproof-git-head-") as temporary:
        code, out, error = run_capture([baseline_binding()["git"]["path"], "rev-parse", "HEAD"], cwd=root,
                                       env=_git_environment(Path(temporary).resolve()),
                                       idle=30, max_total=90)
    if code or not re.fullmatch(r"[0-9a-f]{40,64}", out.strip()):
        raise ValueError("Cannot bind Git revision: " + error)
    return out.strip()


def inventory(context, revision, changed_production):
    if revision not in {"base", "head"}:
        raise ValueError("Explicit base/head revision required")
    root = graph.root_path(context[revision + "_root"])
    if git_head(root) != context["source"][revision]:
        raise ValueError("Git revision/root mismatch")
    if not isinstance(changed_production, dict) or (revision == "base" and changed_production):
        raise ValueError("Only head may have changed production lines")
    entries, exclusions, errors = _walk(root)
    by_path = {entry["path"]: entry for entry in entries}
    for name, lines in changed_production.items():
        graph.relative_name(name)
        if (name not in by_path or by_path[name]["role"] != "production" or
                not isinstance(lines, list) or any(type(line) is not int or line < 1 for line in lines) or
                lines != sorted(set(lines))):
            raise ValueError("Changed-production map does not bind canonical inputs")
    # The broad source observation includes ignored normative contracts, not just code.
    # If bytes cannot be observed, keep the existing run source binding only as a
    # diagnostic identity, and explicitly fail enumeration (never compare this census).
    try:
        observed = source_snapshot(root, context["source"]["scope"])
        source_hash = observed["scope_sha256"]
    except (OSError, ValueError) as failure:
        source_hash = context["source"]["scope_sha256"]
        errors.append({"directory": ".", "entry": None, "operation": "read",
                       "reason": "Broad source observation unavailable: " + str(failure)})
    result = {"schema_version": 1, "revision": revision, "source_sha256": source_hash,
              "entries": entries, "changed_production": dict(sorted(changed_production.items())),
              "scope_exclusions": exclusions, "enumeration_state": "failed" if errors else "complete",
              "enumeration_errors": errors}
    result["digest"] = graph.digest(result)
    return result


def default_policy():
    # Keep legacy compatibility entry points; evidence validation is a separate boundary.
    return {"required": REQUIRED.copy(),
            "rules": {"mutation_score_pct": {"threshold": MUTATION_FLOOR},
                      "greenfield": GREENFIELD_LIMITS.copy(), "tolerance": TOLERANCE.copy()},
            "origins": ["built-in quality metrics; required coverage and architecture proof"]}


def judge(name, base, head, greenfield=False):
    if head is None:
        return None, "unavailable"
    entry = {"base": base, "head": head}
    if greenfield:
        entry["baseline"] = "greenfield"
        warn_at, fail_at = GREENFIELD_LIMITS.get(name, (None, None))
        status = "fail" if fail_at is not None and head > fail_at else (
            "warn" if warn_at is not None and head > warn_at else "ok")
        if fail_at is not None:
            entry["limit"] = fail_at
    elif base is None:
        status = "unavailable"
    else:
        delta = round(head - base, 2)
        entry["delta"] = delta
        if name in LOWER_BETTER | {"architecture_rules"}:
            status = "ok" if delta <= 0 else (
                "warn" if name not in {"cycles", "architecture_rules"} and delta <= TOLERANCE.get(name, 0) else "fail")
        else:
            status = "ok" if delta >= 0 else ("warn" if delta > -5 else "fail")
    entry["status"] = status
    return entry, status


def assess_report(metrics, policy):
    import math
    if not isinstance(policy.get("required"), list) or not policy["required"]:
        raise ValueError("Policy requires at least one measurement")
    statuses, missing = [], []
    for name, entry in metrics.items():
        value = entry.get("head")
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
            raise ValueError("Non-finite or non-numeric measurement: " + name)
        if entry.get("state") == "measured" and value is None:
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


def unavailable(context, parsed, metric):
    inv = parsed["inventory"]
    return {"schema_version": 1, "metric": metric, "revision": inv["revision"], "run_id": context["run_id"],
            "source_sha256": inv["source_sha256"], "inventory_sha256": inv["digest"],
            "semantic_version": "q1-missing-adapter-v1", "toolset_sha256": context["toolset_sha256"],
            "policy_sha256": context["policy_sha256"], "state": "unavailable", "value": None,
            "receipts": [], "findings": [], "outside_model": [], "commands": [], "raw": [],
            "reasons": ["No qualified Q1 adapter for " + metric]}


def collect_pair(context, config, base, head):
    result = {}
    for parsed in (base, head):
        items = graph.observations(context, parsed, config)
        items += [unavailable(context, parsed, name) for name in sorted(LOWER_BETTER - {"cycles"})]
        for item in items:
            result.setdefault(item["metric"], []).append(item)
    return {name: tuple(pair) for name, pair in sorted(result.items())}


def config_policy(config):
    policy = default_policy()
    policy["rules"]["coverage"] = {
        "changed_executable_line_floor_pct": 100, "changed_decision_outcome_floor_pct": 100}
    policy["approval_artifact"] = config["approval_artifact"]
    policy["semantic_profile"] = config["semantic_profile"]
    policy["baseline_materialization"] = baseline_binding()
    return policy


def validate_config(config, root):
    fields = {"schema_version", "semantic_profile", "tools", "python_source_roots", "js_entrypoints",
              "suites", "coverage_policy", "architecture_rules", "mutation_cap",
              "mutation_max_seconds", "approval_artifact"}
    if not isinstance(config, dict) or set(config) != fields:
        raise ValueError("Invalid MeasurementConfig fields")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1 or config["semantic_profile"] != "workflow-reliability-q-v1":
        raise ValueError("Unsupported measurement config version/profile")
    if config["tools"] != {} or config["js_entrypoints"] != []:
        raise ValueError("Q1 does not qualify tool bindings or JS entrypoints")
    roots = config["python_source_roots"]
    if not isinstance(roots, list) or not roots or len(set(roots)) != len(roots):
        raise ValueError("Source roots must be a nonempty unique list")
    if os.name == "nt" and len({name.casefold() for name in roots}) != len(roots):
        raise ValueError("Case-fold source root collision")
    for name in roots:
        if not graph.input_path(root, name, directory=True).is_dir():
            raise ValueError("Source root is not a real directory")
    graph.evaluate_rules({"nodes": [], "edges": [], "outside_model": []}, config["architecture_rules"])
    coverage = config["coverage_policy"]
    if not isinstance(coverage, dict) or set(coverage) != {
            "changed_executable_line_floor_pct", "changed_decision_outcome_floor_pct", "approval_artifact"}:
        raise ValueError("Invalid coverage policy")
    for key in ("changed_executable_line_floor_pct", "changed_decision_outcome_floor_pct"):
        if type(coverage[key]) not in (int, float) or coverage[key] != 100:
            raise ValueError("Coverage floors must remain 100")
    for ref in (config["approval_artifact"], coverage["approval_artifact"]):
        if not isinstance(ref, dict) or _json_bytes(graph.artifact(root, ref["path"])) != _json_bytes(ref):
            raise ValueError("Approval artifact does not match source")
    if type(config["mutation_cap"]) is not int or config["mutation_cap"] != 20:
        raise ValueError("Q requires the unchanged 20-candidate cap")
    import math
    budget = config["mutation_max_seconds"]
    if type(budget) not in (int, float) or not math.isfinite(budget) or budget <= 0:
        raise ValueError("Invalid mutation budget")
    suites = config["suites"]
    if not isinstance(suites, list) or not suites:
        raise ValueError("Explicit suites are required (not executed by the Q1 graph adapter)")
    ids = set()
    for suite in suites:
        if not isinstance(suite, dict) or set(suite) != {
                "id", "runner", "argv", "cwd", "test_files", "idle_seconds", "max_seconds"}:
            raise ValueError("Invalid suite fields")
        if not isinstance(suite["id"], str) or not re.fullmatch(r"[!-~]+", suite["id"]) or suite["id"] in ids:
            raise ValueError("Suite IDs must be unique ASCII identifiers")
        ids.add(suite["id"])
        if suite["runner"] not in {"python-unittest", "node-native"}:
            raise ValueError("Unsupported suite runner")
        if (not isinstance(suite["argv"], list) or not suite["argv"] or
                any(not isinstance(arg, str) or not arg or "\0" in arg for arg in suite["argv"])):
            raise ValueError("Suite requires concrete argv")
        if not graph.input_path(root, suite["cwd"], directory=True).is_dir():
            raise ValueError("Invalid suite cwd")
        files = suite["test_files"]
        if not isinstance(files, list) or not files or len(set(files)) != len(files):
            raise ValueError("Suite requires unique test files")
        for name in files:
            if not graph.input_path(root, name).is_file():
                raise ValueError("Missing test input")
        for key in ("idle_seconds", "max_seconds"):
            value = suite[key]
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError("Invalid suite bounds")
    return config


def make_manifest(context, base, head):
    inputs = []
    for parsed in (base, head):
        revision = parsed["inventory"]["revision"]
        inputs += [{"artifact": ref, "role": "syntax", "revision": revision}
                   for ref in parsed["syntax_artifacts"].values()]
        inputs.append({"artifact": graph.artifact(context["run_root"], graph.graph_name(revision)),
                       "role": "graph", "revision": revision})
    inputs.sort(key=lambda item: item["artifact"]["path"])
    return {"run_id": context["run_id"], "root": str(graph.root_path(context["run_root"])),
            "inputs": inputs, "reserved_outputs": [item["artifact"]["path"] for item in inputs] + ["manifest.json"]}


def _validate_root_independence(roots):
    """Reject cross-root mutable aliases, not merely equal bytes or path ancestry.

    Include non-code contracts and owned artifacts. Git metadata is not a subject
    input. Identity observation is not a lock against subsequent filesystem edits.
    """
    identities = {}

    def walk_error(error):
        raise error

    try:
        for owner, root in enumerate(roots):
            for directory, dirs, files in os.walk(root, onerror=walk_error, followlinks=False):
                if Path(directory) == root and owner < 3:
                    dirs[:] = [name for name in dirs if name != ".git"]
                    files = [name for name in files if name != ".git"]
                for name in sorted(dirs + files):
                    relative = (Path(directory) / name).relative_to(root).as_posix()
                    path = graph.input_path(root, relative)
                    info = path.stat()
                    if stat.S_ISDIR(info.st_mode):
                        continue
                    if not stat.S_ISREG(info.st_mode) or not info.st_ino:
                        raise ValueError("Cannot establish independent regular-file identity: " + str(path))
                    identity = (info.st_dev, info.st_ino)
                    previous = identities.get(identity)
                    if previous is not None and previous[0] != owner:
                        raise ValueError("Shared mutable file identity across Context roots: %s and %s"
                                         % (previous[1], path))
                    identities[identity] = (owner, path)
    except OSError as error:
        raise ValueError("Cannot establish Context source independence: " + str(error)) from error


def validate_observations(context, base, head, config, policy, artifacts, observations):
    if not isinstance(context, dict) or set(context) != {
            "schema_version", "run_id", "source", "base_root", "head_root", "controller_root",
            "run_root", "controller_sha256", "policy_sha256", "toolset_sha256",
            "output_manifest", "contract_artifacts"}:
        raise ValueError("Invalid Context fields")
    if context["schema_version"] != 1 or type(context["schema_version"]) is not int:
        raise ValueError("Unsupported Context version")
    if not isinstance(context["run_id"], str) or not re.fullmatch(r"[!-~]+", context["run_id"]):
        raise ValueError("Invalid Context run identity")
    roots = [graph.root_path(context[key]) for key in ("base_root", "head_root", "controller_root", "run_root")]
    if any(a.is_relative_to(b) or b.is_relative_to(a) for i, a in enumerate(roots) for b in roots[i + 1:]):
        raise ValueError("Context roots must be distinct and disjoint")
    _validate_root_independence(roots)
    validate_config(config, context["head_root"])
    refs = context["contract_artifacts"]
    if not isinstance(refs, list) or not refs or len({ref["path"] for ref in refs}) != len(refs):
        raise ValueError("Context requires unique source contract artifacts")
    config_matches = 0
    for ref in refs:
        if (_json_bytes(graph.artifact(context["head_root"], ref["path"])) != _json_bytes(ref) or
                context["source"]["files"].get(ref["path"], {}).get("sha256") != ref["sha256"]):
            raise ValueError("Contract artifact is not bound to observed source")
        try:
            decoded = graph.load_json(graph.input_path(context["head_root"], ref["path"]).read_bytes())
        except ValueError:
            continue  # An approval may be prose, not JSON.
        if _json_bytes(decoded) == _json_bytes(config):
            config_matches += 1
    if config_matches != 1 or config["approval_artifact"] not in refs:
        raise ValueError("Config bytes and approval must match their source artifacts")
    if (_json_bytes(policy) != _json_bytes(config_policy(config)) or
            context["policy_sha256"] != graph.digest(policy) or
            context["toolset_sha256"] != graph.digest({"python_parser": graph.parser_digest()}) or
            context["controller_sha256"] != controller_digest(context["controller_root"]) or
            context["controller_sha256"] != controller_digest(Path(__file__).resolve().parent)):
        raise ValueError("Policy/tool/controller binding mismatch")
    if context["source"]["head"] != git_head(context["head_root"]) or context["source"]["base"] != git_head(context["base_root"]):
        raise ValueError("Context Git identity mismatch")
    validate_baseline(context["base_root"], context["source"]["base"])
    observed = source_snapshot(context["head_root"], context["source"]["scope"])
    observed.update(base=context["source"]["base"], head=context["source"]["head"])
    if _json_bytes(observed) != _json_bytes(context["source"]):
        raise ValueError("Head source observation is stale")
    if _json_bytes(artifacts) != _json_bytes(make_manifest(context, base, head)):
        raise ValueError("Unexpected manifest inputs/ownership")
    ref = context["output_manifest"]
    if (ref != graph.artifact(context["run_root"], "manifest.json") or
            _json_bytes(graph.load_json(graph.input_path(context["run_root"], ref["path"]).read_bytes())) != _json_bytes(artifacts)):
        raise ValueError("Manifest identity mismatch")
    derived = []
    for revision, parsed in (("base", base), ("head", head)):
        inv = parsed["inventory"]
        if inv["revision"] != revision or _json_bytes(inventory(context, revision, inv["changed_production"])) != _json_bytes(inv):
            raise ValueError("Inventory is missing, stale or bound to the wrong revision")
        raw_ref = graph.artifact(context["run_root"], graph.graph_name(revision))
        raw = graph.read_owned(context, artifacts, raw_ref, "graph", revision)
        derived += graph.validate_evidence(context, parsed, config, raw, artifacts)
        derived += [unavailable(context, parsed, name) for name in sorted(LOWER_BETTER - {"cycles"})]
    derived.sort(key=lambda item: (item["metric"], item["revision"]))
    if _json_bytes(sorted(observations, key=lambda item: (item["metric"], item["revision"]))) != _json_bytes(derived):
        raise ValueError("Observations disagree with producer-owned raw recomputation")
    _validate_root_independence(roots)
    return derived


def controller_digest(root):
    return graph.digest({name: hashlib.sha256(graph.input_path(root, name).read_bytes()).hexdigest()
                         for name in ("measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py")})


def assess_observations(observations, mutation, policy, base_inventory):
    if policy["required"] != REQUIRED:
        raise ValueError("All nine required metrics must be retained")
    indexed = {(item["metric"], item["revision"]): item for item in observations}
    if len(indexed) != len(observations):
        raise ValueError("Duplicate observations")
    metrics = {}
    greenfield = base_inventory["enumeration_state"] == "complete" and len(base_inventory["entries"]) < 3
    for name in sorted(LOWER_BETTER | {"architecture_rules"}):
        base, head = indexed[name, "base"], indexed[name, "head"]
        entry, status = judge(name, base["value"], head["value"], greenfield)
        complete = base["state"] == head["state"] == "complete"
        reason = "; ".join(dict.fromkeys(base["reasons"] + head["reasons"]))
        metrics[name] = {**(entry or {"head": None, "base": base["value"]}),
                         "state": "measured" if complete else "unavailable",
                         "comparison": status if complete else "unavailable",
                         "status": status if complete else "unavailable", "reason": reason}
        if name in {"cycles", "architecture_rules"}:
            def identities(item):
                if name == "architecture_rules":
                    return {finding["id"] for finding in item["findings"]}
                raw = item.get("cycle_ids")
                if raw is None:
                    raise ValueError("Cycle identities must be supplied from validated graph")
                return set(raw)
            new = sorted(identities(head) - identities(base))
            metrics[name]["new_ids"] = new
            if complete and new:
                metrics[name].update(comparison="fail", status="fail")
    metrics["mutation_score_pct"] = mutation
    metrics["diff_coverage_pct"] = {"state": "unavailable", "head": None, "base": None,
                                   "comparison": "unavailable", "status": "unavailable",
                                   "reason": "No qualified Q1 coverage adapter"}
    return {"metrics": metrics, **assess_report(metrics, policy)}


def with_cycle_ids(observations, base, head):
    # Identities are internal assessment inputs, not an extension of Observation.
    parsed = {"base": base, "head": head}
    return [{**item, "cycle_ids": [cycle["id"] for cycle in parsed[item["revision"]]["graph"]["cycles"]]}
            if item["metric"] == "cycles" else item for item in observations]
