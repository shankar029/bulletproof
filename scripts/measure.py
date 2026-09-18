"""Canonical code census and Q1 measurement composition; never imports probe/guard."""

import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import uuid

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


def _walk(root, *, include_js=False):
    if type(include_js) is not bool:
        raise ValueError("include_js must be a bool")
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
            if include_js and suffix in {".jsx", ".tsx"}:
                language = "javascript" if suffix == ".jsx" else "typescript"
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


def inventory(context, revision, changed_production, *, include_js=False):
    if type(include_js) is not bool:
        raise ValueError("include_js must be a bool")
    if revision not in {"base", "head"}:
        raise ValueError("Explicit base/head revision required")
    root = graph.root_path(context[revision + "_root"])
    if git_head(root) != context["source"][revision]:
        raise ValueError("Git revision/root mismatch")
    if not isinstance(changed_production, dict) or (revision == "base" and changed_production):
        raise ValueError("Only head may have changed production lines")
    entries, exclusions, errors = _walk(root, include_js=include_js)
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


def _regular_file(path, *, independent=True):
    """Observe a canonical, independent regular file; never normalize an alias."""
    path = Path(path)
    if not path.is_absolute():
        raise ValueError("Expected an absolute input file")
    path = graph.input_path(path.parent, path.name)
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or not info.st_ino or (independent and info.st_nlink != 1) or
            getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
        raise ValueError("Input requires independent regular-file identity: " + str(path))
    content = path.read_bytes()
    after = path.stat()
    if (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_nlink, info.st_mode) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_nlink, after.st_mode):
        raise ValueError("Input changed while reading: " + str(path))
    return content, (info.st_dev, info.st_ino)


def _artifact_bytes(root, ref):
    if (not isinstance(ref, dict) or set(ref) != {"path", "sha256", "bytes"} or
            not isinstance(ref["sha256"], str) or not re.fullmatch("[0-9a-f]{64}", ref["sha256"]) or
            type(ref["bytes"]) is not int or ref["bytes"] < 0):
        raise ValueError("Invalid tool Artifact")
    path = graph.input_path(root, ref["path"])
    data, identity = _regular_file(path)
    if len(data) != ref["bytes"] or hashlib.sha256(data).hexdigest() != ref["sha256"]:
        raise ValueError("Tool artifact bytes mismatch: " + ref["path"])
    return data, identity


def _path_partition(names):
    folded = {}
    for name in names:
        graph.relative_name(name)
        key = name.casefold() if os.name == "nt" else name
        if key in folded:
            raise ValueError("Duplicate/colliding artifact path: " + name)
        folded[key] = name
    for key in folded:
        parts = key.split("/")
        for end in range(1, len(parts)):
            ancestor = "/".join(parts[:end])
            if ancestor in folded:
                raise ValueError("Artifact file/directory prefix collision: " + folded[ancestor])


def tool_artifacts(config):
    """Unique selected originals; sharing between tools is explicit, not discovery."""
    tools = config["tools"]
    if not isinstance(tools, dict):
        raise ValueError("tools must be a mapping")
    if bool(tools) != ("tool_artifact_root" in config):
        raise ValueError("tool_artifact_root is required exactly when tools is nonempty")
    if not tools:
        return []
    if not isinstance(config["tool_artifact_root"], str) or not config["tool_artifact_root"]:
        raise ValueError("tool_artifact_root must be a nonempty absolute directory string")
    root = graph.root_path(config["tool_artifact_root"])
    selected, identities = {}, {}
    for tool, binding in sorted(tools.items()):
        if tool not in {"typescript", "lizard", "vulture", "ruff", "jscpd"}:
            raise ValueError("Unqualified tool ID: " + str(tool))
        if not isinstance(binding, dict) or set(binding) != {
                "executable", "module_path", "observed_version", "sha256", "qualified_api",
                "help", "configuration", "qualification"}:
            raise ValueError("Invalid ToolBinding fields")
        qualifications = binding["qualification"]
        if not isinstance(qualifications, list) or not qualifications:
            raise ValueError("Tool requires explicit qualification artifacts")
        _path_partition([ref["path"] for ref in qualifications])
        for ref in [binding["help"], binding["configuration"], *qualifications]:
            _data, identity = _artifact_bytes(root, ref)
            name = ref["path"]
            if name.split("/")[0].casefold() in {"base", "head", "manifest.json"}:
                raise ValueError("Qualification occupies generated artifact namespace: " + name)
            if name in selected and selected[name] != ref:
                raise ValueError("Conflicting tool artifact declaration")
            if identity in identities and identities[identity] != name:
                raise ValueError("Aliased original artifacts")
            identities[identity] = name
            selected[name] = ref
    _path_partition(selected)
    return [selected[name] for name in sorted(selected)]


def _external_pin(path, expected, subject_roots, *, independent=True):
    data, identity = _regular_file(path, independent=independent)
    if any(Path(path).is_relative_to(Path(root)) for root in subject_roots):
        raise ValueError("Tool code/resources must remain external: " + str(path))
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError("Qualified external input changed: " + str(path))
    return {"path": str(path), "sha256": actual, "bytes": len(data)}, identity


_SOURCE_ROOTS_HASH = "7b096834fba95bef4984701376be69f72f37b2549777b5b2eb03715d1f141bde"
_SOURCE_FILES_HASH = "23c3bfa261c02c797d847c134c0131ccebae9ff704cb419d3b0d07c861b4a5af"
_SOURCE_PROFILES = {
    "typescript": {
        "version": "5.9.3", "api": "typescript-compiler-5-9-3-v1", "executor": "node",
        "module": "lib/typescript.js", "roots": ("typescript",),
        "help": "f2e3e3a9ad5608d2818b0356c935a3c45458958d2d70ec3ed715eefc3af5f256",
        "result": "c162d0ce8e34c343442fdb646f40db4674c1fa51098e5af5302222986b5d2b86",
        "provenance": None,
    },
    "lizard": {
        "version": "1.24.0", "api": "lizard-strict-text-1-24-0-v1", "executor": "python",
        "module": "lizard.py", "roots": ("lizard", "vulture", "pygments", "pathspec"),
        "help": "bea971f58be9f6a52a0582add89d18b38746027d9b2bd50a8d5c8f565f0424cc",
        "result": "2ef3cd40316b0b553546366cffc60c9d8c0eb892f835dd164feffb5637a49b32",
        "provenance": "c2f9b6235d514d3729e20973256e264b3c9449abba174a3a9a8b7079e43a3c8e",
    },
    "vulture": {
        "version": "2.16", "api": "vulture-scan-2-16-v1", "executor": "python",
        "module": "vulture/core.py", "roots": ("lizard", "vulture", "pygments", "pathspec"),
        "help": "77b2eeb271a10f1262d835bf1181a43900a94fa6c334bc5b027ed704e6bfb48c",
        "result": "43a02a543dce248e4393a84235fbb899a879afdb2907ed7c07bd852c1b9d6e6d",
        "provenance": "7cbbe382094ab6e892843a8891c8fedb34267a38fff012474b80b8f996096407",
    },
}


def _resource_pin(root, relative, expected, directories):
    # Cache directory checks only within this one rehash operation. Re-walking
    # all ancestors for every packaged file makes exhaustive binding impractical.
    graph.relative_name(relative)
    path = root / relative
    current = root
    for part in Path(relative).parts[:-1]:
        current = current / part
        if current not in directories:
            graph.input_path(root, current.relative_to(root).as_posix(), directory=True)
            if not current.is_dir():
                raise ValueError("Missing qualified resource directory: " + str(current))
            directories[current] = set(os.listdir(current))
    if current not in directories:
        directories[current] = set(os.listdir(current))
    if path.name not in directories[current]:
        raise ValueError("Missing/aliased qualified resource: " + str(path))
    before = path.lstat()
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not before.st_ino or
            getattr(before, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
        raise ValueError("Qualified resource is not an independent regular file: " + str(path))
    data = path.read_bytes()
    after = path.lstat()
    if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_nlink) !=
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_nlink) or
            len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]):
        raise ValueError("Qualified resource bytes changed: " + str(path))
    return {"path": str(path), "sha256": expected["sha256"], "bytes": len(data)}


def _source_inputs(tool, binding, decoded, subject_roots, resource_cache):
    profile = _SOURCE_PROFILES[tool]
    required = {_SOURCE_ROOTS_HASH, _SOURCE_FILES_HASH, profile["result"]}
    if profile["provenance"]:
        required.add(profile["provenance"])
    if tool == "lizard":
        required.add("ec56aff06fb3d8e3b3c7ceb114827a8c8a55533e5868e086f1e2bdd57193d2b6")
    if not required <= {ref["sha256"] for ref in binding["qualification"]}:
        raise ValueError("Source tool requires complete original qualification/resource provenance")
    roots = decoded.get(binding["configuration"]["sha256"])
    names = {"typescript", "lizard", "vulture", "pygments", "pathspec"}
    if not isinstance(roots, dict) or set(roots) != names:
        raise ValueError("Source-tool settings must be the explicit qualified root map")
    for name, root in roots.items():
        if not isinstance(root, str):
            raise ValueError("Source-tool root must be an absolute directory string")
        graph.root_path(root)
        if any(Path(root).is_relative_to(Path(subject)) or Path(subject).is_relative_to(Path(root))
               for subject in subject_roots):
            raise ValueError("Source-tool packages must be external and disjoint")
    if binding["module_path"] != str(Path(roots[tool]) / profile["module"]):
        raise ValueError("Source module does not match its explicit qualified root")
    original_roots = decoded[_SOURCE_ROOTS_HASH]
    resources, directories = [], {}
    for expected in decoded[_SOURCE_FILES_HASH]:
        owners = [name for name in names if Path(expected["path"]).is_relative_to(Path(original_roots[name]))]
        if len(owners) != 1:
            raise ValueError("Qualified resource has ambiguous package ownership")
        name = owners[0]
        if name not in profile["roots"]:
            continue
        relative = Path(expected["path"]).relative_to(Path(original_roots[name])).as_posix()
        path = Path(roots[name]) / relative
        key = (str(path), expected["sha256"], expected["bytes"])
        if key not in resource_cache:
            resource_cache[key] = _resource_pin(Path(roots[name]), relative, expected, directories)
            if len(resource_cache) % 500 == 0:
                print("measure: rehashed qualified resource files:", len(resource_cache),
                      file=sys.stderr, flush=True)
        resources.append(resource_cache[key])
    runtime_imports = []
    if profile["provenance"]:
        for item in decoded[profile["provenance"]]["imported_files"]:
            if item["role"] == "managed-runtime":
                pin, _identity = _external_pin(item["path"], item["sha256"], subject_roots)
                if pin not in runtime_imports:
                    runtime_imports.append(pin)
    settings = ({
        "noEmit": True, "allowJs": True, "checkJs": True, "strict": True,
        "noUnusedLocals": True, "noUnusedParameters": True, "allowUnreachableCode": False,
        "target": 99, "module": 199, "moduleResolution": 99, "jsx": 1,
        "types": [], "typeRoots": [],
    } if tool == "typescript" else {
        "python_flags": ["-I", "-S", "-B"], "pathspec_backend": "simple",
        "versions": {"lizard": "1.24.0", "vulture": "2.16", "pygments": "2.21.0", "pathspec": "1.1.1"},
        "optional_absent": ["re2", "hyperscan", "typing_extensions", "colorama", "jinja2", "tomli"],
        "lizard_extensions": [], "vulture_min_confidence": 80,
    })
    if tool == "typescript" and decoded[profile["result"]]["options"] != settings:
        raise ValueError("Compiler settings disagree with original qualification")
    return {"roots": {name: roots[name] for name in profile["roots"]},
            "resources": resources, "runtime_imports": runtime_imports, "settings": settings}


def _qualified_inputs(config, subject_roots=()):
    """Rehash the exact qualified distribution, never an ambient package search."""
    if not config["tools"]:
        return {}
    original = config["tool_artifact_root"]
    selected = tool_artifacts(config)
    decoded = {}
    for ref in selected:
        data, _identity = _artifact_bytes(original, ref)
        try:
            decoded[ref["sha256"]] = graph.load_json(data)
        except ValueError:
            pass  # Opaque help/logs remain byte artifacts, not JSON documents.
    runtime_hash = "1f38647736643a54273217524f452724f4daf5437c7fa8cb8c6a78c4479ce91b"
    runtime = decoded.get(runtime_hash)
    if runtime is None:
        raise ValueError("Qualified runtime provenance artifact is required")
    profiles = {
        "jscpd": ("5.2.1", "jscpd-json-5-2-1-v1", "jscpd", None,
                  "0dbe0b069783f1e52548d3aec354bf9b2d14ac5326e5e8378865f7ea75440b61",
                  "af06c28dec96da6ca3d3f269b6a51faeead044f95049284d2aecca02a9671279"),
        "ruff": ("0.16.8", "ruff-json-0-16-8-v1", "ruff", None,
                 "424b5c047de648dcf5f4cb18c0cf1c2f7992ab79002b1afa27cd2cfd29550851",
                 "97e2c89b81d40d6c8377471e63b2eb912137edb9fc70169e225413fc6a1cbc1a"),
    }
    inputs, resource_cache = {}, {}
    for tool, binding in sorted(config["tools"].items()):
        source = None
        if tool in _SOURCE_PROFILES:
            profile = _SOURCE_PROFILES[tool]
            version, api, executor = profile["version"], profile["api"], profile["executor"]
            help_hash = profile["help"]
            source = _source_inputs(tool, binding, decoded, subject_roots, resource_cache)
        else:
            version, api, executor, module, help_hash, configuration_hash = profiles[tool]
            if binding["module_path"] != module or binding["configuration"]["sha256"] != configuration_hash:
                raise ValueError("Tool differs from qualified version/API/settings: " + tool)
        expected = runtime["executors"][executor]
        if (binding["observed_version"] != version or binding["qualified_api"] != api or
                binding["sha256"] != expected["sha256"] or binding["help"]["sha256"] != help_hash):
            raise ValueError("Tool differs from qualified version/API/settings: " + tool)
        if source is None:
            required = {
                "jscpd": "c78a1d173941fbafc7561526cefa8e40220719cd564dc45f0c33095568dda4af",
                "ruff": "32c16a8fc7737241427aa7ef9701fbbc6d63219299b0d15a7301f29463bc81bb",
            }[tool]
            if required not in {ref["sha256"] for ref in binding["qualification"]}:
                raise ValueError("Tool requires original actual qualification output")
        pin, _identity = _external_pin(binding["executable"], expected["sha256"], subject_roots)
        dependencies = []
        for item in expected["pe"]["declared_imports"]:
            path = item["resolved_existing_candidate"]
            if path is not None:
                # Qualified PE records retain loader-style uppercase spellings.
                # Windows-serviced DLLs have native WinSxS hardlinks; they are
                # pinned external inputs, never original/staged artifact copies.
                # Canonicalize this qualified locator, not a user Artifact path.
                canonical = Path(path).resolve(strict=True)
                dependency, _identity = _external_pin(
                    canonical, item["sha256"], subject_roots, independent=False)
                if dependency not in dependencies:
                    dependencies.append(dependency)
        inputs[tool] = {"executable": pin, "dependencies": dependencies,
                        "binding": binding}
        if source is not None:
            if executor == "python":
                dll = runtime["python_dll"]
                dll_pin, _identity = _external_pin(dll["path"], dll["sha256"], subject_roots)
                dependencies.append(dll_pin)
            inputs[tool]["source"] = source
    return inputs


def toolset_digest(config, run_root=None, subject_roots=()):
    parser = {"python_parser": graph.parser_digest()}
    refs = tool_artifacts(config)
    if not refs:
        return graph.digest(parser)
    bindings = _qualified_inputs(config, subject_roots)
    original_identities = {_artifact_bytes(config["tool_artifact_root"], ref)[1] for ref in refs}
    if run_root is not None:
        for ref in refs:
            _data, identity = _artifact_bytes(run_root, ref)
            if identity in original_identities:
                raise ValueError("Staged artifact aliases original")
    return graph.digest({**parser, "config": config, "originals_and_copies": refs,
                         "qualified_inputs": bindings})


def stage_tool_inputs(context, config):
    """Exclusive opaque-byte copies; JSON serialization would corrupt qualification logs."""
    refs = tool_artifacts(config)
    if not refs:
        return
    original = graph.root_path(config["tool_artifact_root"])
    for key in ("base_root", "head_root", "controller_root", "run_root"):
        if original.is_relative_to(graph.root_path(context[key])):
            raise ValueError("Original tool root is inside a generated Context root")
    for ref in refs:
        data, _identity = _artifact_bytes(original, ref)
        destination = graph.input_path(context["run_root"], ref["path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination = graph.input_path(context["run_root"], ref["path"])
        with destination.open("xb") as stream:
            stream.write(data)
        _artifact_bytes(context["run_root"], ref)
    if toolset_digest(config, context["run_root"], [context[key] for key in (
            "base_root", "head_root", "controller_root", "run_root")]) != context["toolset_sha256"]:
        raise ValueError("Tool binding changed during staging")


_PYTHON_BINDING_PROBE = r'''
import ast, contextlib, hashlib, importlib, importlib.metadata, io, json, sys
from importlib.machinery import BuiltinImporter, FrozenImporter, PathFinder
from pathlib import Path
request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
source = request["source"]
base = Path(sys.base_prefix).resolve()
if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
    raise ValueError("Source tools require -I -S -B")
if not all(Path(p).resolve().is_relative_to(base) for p in sys.path):
    raise ValueError("Unexpected interpreter startup path")
allowed = {str(Path(p["path"]).resolve()): p["sha256"]
           for p in source["resources"] + source["runtime_imports"]}
def checked(filename):
    path = Path(filename).resolve()
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if allowed.get(str(path)) != digest:
        raise ImportError("Unqualified import/resource: " + str(path))
    return str(path), digest
rejected = []
class PinnedFinder:
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)
        if spec and spec.origin not in (None, "built-in", "frozen"):
            try:
                checked(spec.origin)
            except (OSError, ImportError):
                rejected.append(fullname)
                raise
        return spec
sys.meta_path[:] = [BuiltinImporter, FrozenImporter, PinnedFinder]
sys.path[:0] = list(source["roots"].values())
if list(importlib.metadata.distributions()):
    raise ValueError("Installed distributions/plugins are outside the qualified source mode")
import lizard, vulture, pygments, pathspec
from lizard_languages import get_reader_for
from pathspec._backends import agg
from pygments import plugin
versions = {"lizard": lizard.version, "vulture": vulture.__version__,
            "pygments": pygments.__version__, "pathspec": pathspec.__version__}
if versions != source["settings"]["versions"] or agg._BEST_BACKEND != "simple":
    raise ValueError("Unqualified package version/backend")
if list(plugin.iter_entry_points(plugin.LEXER_ENTRY_POINT)):
    raise ValueError("Unqualified Pygments entry-point plugin")
for name in source["settings"]["optional_absent"]:
    if importlib.util.find_spec(name) is not None:
        raise ValueError("Unqualified optional dependency: " + name)
if not pathspec.PathSpec.from_lines("gitwildmatch", ["*.py"]).match_file("binding.py"):
    raise ValueError("Qualified pathspec simple backend did not execute")
out, err, reads = io.StringIO(), io.StringIO(), []
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    if request["tool"] == "lizard":
        readers = {suffix: get_reader_for("binding" + suffix).__name__
                   for suffix in (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx")}
        text = b"def binding(value):\n    if value:\n        return 1\n    return 0\n".decode("utf-8")
        ast.parse(text)
        info = lizard.FileAnalyzer(lizard.get_extensions([])).analyze_source_code("binding.py", text)
        smoke = {"readers": readers, "functions": [
            {"name": f.name, "start_line": f.start_line, "end_line": f.end_line,
             "cyclomatic_complexity": f.cyclomatic_complexity} for f in info.function_list]}
    elif request["tool"] == "vulture":
        api = vulture.Vulture()
        api.scan("import ast\n", filename="binding.py")
        resource = Path(source["roots"]["vulture"]) / "vulture/whitelists/ast_whitelist.py"
        filename, digest = checked(resource)
        reads.append({"path": filename, "sha256": digest})
        api.scan(resource.read_bytes().decode("utf-8"), filename="whitelists/ast_whitelist.py")
        before_report = int(api.exit_code)
        findings = [{"name": f.name, "typ": f.typ, "confidence": f.confidence,
                     "filename": str(f.filename), "first_lineno": f.first_lineno,
                     "last_lineno": f.last_lineno, "message": f.message}
                    for f in api.get_unused_code(min_confidence=80)]
        smoke = {"pre_report_exit": before_report, "findings": findings}
        if before_report != 0:
            raise ValueError("Vulture scan failed before report")
    else:
        raise ValueError("Unsupported source binding probe")
if out.getvalue() or err.getvalue() or rejected:
    raise ValueError("Source API diagnostics: " + out.getvalue() + err.getvalue() + repr(rejected))
imports = []
for name, module in sorted(sys.modules.items()):
    filename = getattr(module, "__file__", None)
    if filename:
        path, digest = checked(filename)
        imports.append({"module": name, "path": path, "sha256": digest})
payload = {"tool": request["tool"], "settings": source["settings"], "imports": imports,
           "resources_read": reads, "smoke": smoke,
           "runtime": {"executable": str(Path(sys.executable).resolve()), "version": sys.version,
                       "isolated": sys.flags.isolated, "no_site": sys.flags.no_site,
                       "no_bytecode": sys.dont_write_bytecode, "sys_path": sys.path,
                       "versions": versions, "pathspec_backend": agg._BEST_BACKEND}}
with Path(request["result_path"]).open("x", encoding="utf-8") as stream:
    json.dump(payload, stream, ensure_ascii=False)
print("Executed qualified source binding: " + request["tool"], flush=True)
'''

_NODE_BINDING_PROBE = r'''
'use strict';
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const request = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const key = file => process.platform === 'win32' ? path.resolve(file).toLowerCase() : path.resolve(file);
const allowed = new Map(request.source.resources.map(p => [key(p.path), p]));
function checked(file) {
  const pin = allowed.get(key(file));
  if (!pin) throw new Error('Unqualified compiler resource: ' + file);
  const bytes = fs.readFileSync(file);
  if (hash(bytes) !== pin.sha256) throw new Error('Changed compiler resource: ' + file);
  return bytes;
}
checked(request.module_path);
const ts = require(request.module_path);
if (ts.version !== '5.9.3') throw new Error('Unexpected compiler version');
const virtual = path.join(path.dirname(request.result_path), 'binding.ts');
const text = 'export const answer: number = 42;\n';
const options = request.source.settings, reads = new Map();
const host = ts.createCompilerHost(options);
host.readFile = file => {
  if (key(file) === key(virtual)) return text;
  if (!allowed.has(key(file))) return undefined;
  const bytes = checked(file), pin = allowed.get(key(file));
  reads.set(pin.path, {path: pin.path, sha256: hash(bytes)});
  return new TextDecoder('utf-8', {fatal:true}).decode(bytes);
};
host.fileExists = file => key(file) === key(virtual) || allowed.has(key(file));
host.directoryExists = dir => key(dir) === key(path.dirname(virtual)) ||
  request.source.resources.some(p => key(p.path).startsWith(key(dir) + path.sep));
host.writeFile = () => {throw new Error('Unexpected compiler output');};
const program = ts.createProgram([virtual], options, host);
const diagnostics = ts.getPreEmitDiagnostics(program).map(d => ({
  code:d.code, message:ts.flattenDiagnosticMessageText(d.messageText, '\n')}));
if (diagnostics.length) throw new Error(JSON.stringify(diagnostics));
const sf = program.getSourceFile(virtual);
if (!sf) throw new Error('Missing compiler input');
const checker = program.getTypeChecker();
const symbol = checker.getSymbolAtLocation(sf.statements[0].declarationList.declarations[0].name);
const syntax = ts.createSourceFile(virtual, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
let nodes = 0;
function visit(node) { nodes++; ts.forEachChild(node, visit); }
visit(syntax);
const imports = Object.keys(require.cache).sort().map(file => {
  const bytes = checked(file), pin = allowed.get(key(file));
  return {module:path.basename(file), path:pin.path, sha256:hash(bytes)};
});
const payload = {tool:'typescript', settings:options, imports, resources_read:[...reads.values()],
  smoke:{symbol:symbol?.getName(), nodes, diagnostics},
  runtime:{executable:fs.realpathSync(process.execPath), version:process.version, arch:process.arch,
           compiler_version:ts.version, exec_argv:process.execArgv}};
fs.writeFileSync(request.result_path, JSON.stringify(payload), {flag:'wx', encoding:'utf8'});
console.log('Executed qualified source binding: typescript');
'''


def source_binding_paths(tool, revision):
    if tool not in _SOURCE_PROFILES or revision not in {"base", "head"}:
        raise ValueError("Explicit source tool and base/head revision required")
    prefix = revision + "/binding/" + tool + "/"
    return [prefix + name + ".json" for name in ("request", "result", "command")]


def _validate_binding_ownership(manifest, config):
    if (not isinstance(manifest, dict) or not isinstance(manifest.get("inputs"), list) or
            not isinstance(manifest.get("reserved_outputs"), list)):
        raise ValueError("Invalid binding ownership manifest")
    reserved = manifest["reserved_outputs"]
    _path_partition(reserved)
    rows = manifest["inputs"]
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {"artifact", "role", "revision"} or
                not isinstance(row["artifact"], dict) or
                set(row["artifact"]) != {"path", "sha256", "bytes"}):
            raise ValueError("Invalid binding ownership row")
    paths = [row["artifact"]["path"] for row in rows]
    _path_partition(paths)
    _path_partition(set(paths) | set(reserved))
    declared = {row["artifact"]["path"]: row for row in rows}
    expected = {ref["path"]: ref for ref in tool_artifacts(config)}
    for name, artifact in expected.items():
        row = {"artifact": artifact, "role": "qualification", "revision": None}
        if name not in reserved or _json_bytes(declared.get(name)) != _json_bytes(row):
            raise ValueError("Qualification ownership must match selected input: " + name)
    if any(row["role"] == "qualification" and row["artifact"]["path"] not in expected for row in rows):
        raise ValueError("Unselected qualification ownership declaration")


def inspect_source_binding(context, config, tool, revision):
    """Fixed API smoke/provenance, not a metric collector or arbitrary command hook."""
    names = source_binding_paths(tool, revision)
    if tool not in config["tools"]:
        raise ValueError("Source tool has no explicit binding: " + tool)
    root = graph.root_path(context["run_root"])
    ref = context["output_manifest"]
    manifest = graph.load_json(_artifact_bytes(root, ref)[0])
    _validate_binding_ownership(manifest, config)
    if (manifest["run_id"] != context["run_id"] or manifest["root"] != str(root) or
            any(manifest["reserved_outputs"].count(name) != 1 for name in names)):
        raise ValueError("Binding execution requires exact predeclared artifact ownership")
    for name in names:
        if graph.input_path(root, name).exists():
            raise ValueError("Binding output already exists: " + name)
    roots = [context[key] for key in ("base_root", "head_root", "controller_root", "run_root")]
    if (controller_digest(context["controller_root"]) != context["controller_sha256"] or
            controller_digest(Path(__file__).resolve().parent) != context["controller_sha256"] or
            toolset_digest(config, root, roots) != context["toolset_sha256"]):
        raise ValueError("Source binding/controller changed before execution")
    binding = _qualified_inputs(config, roots)[tool]
    request = {"tool": tool, "source": binding["source"],
               "module_path": binding["binding"]["module_path"],
               "result_path": str(root / names[1])}
    request_ref = graph.persist(context, names[0], request)
    python = tool != "typescript"
    argv = [binding["executable"]["path"], *(
        ["-I", "-S", "-B", "-c", _PYTHON_BINDING_PROBE] if python
        else ["-e", _NODE_BINDING_PROBE]), str(root / names[0])]
    removed = sorted(key for key in os.environ if key.upper().startswith(("PYTHON", "NODE_", "TS_NODE_"))
                     or key.upper() == "VSCODE_INSPECTOR_OPTIONS")
    env = {key: value for key, value in os.environ.items() if key not in removed}
    code, stdout, stderr = run_capture(argv, cwd=context[revision + "_root"], env=env,
                                       idle=30, max_total=90)
    command_ref = graph.persist(context, names[2], {
        "argv": argv, "cwd": str(context[revision + "_root"]), "idle_seconds": 30, "max_seconds": 90,
        "environment_delta": {"removed_names": removed}, "returncode": code,
        "stdout": stdout, "stderr": stderr,
        "capture_semantics": "run_capture UTF-8 replacement-decoded, newline-normalized separate streams",
        "toolset_sha256": context["toolset_sha256"], "controller_sha256": context["controller_sha256"],
    })
    if code != 0 or stderr:
        raise ValueError("Source binding inspection failed; retained command: " + command_ref["path"] + ": " + stderr)
    result_ref = graph.artifact(root, names[1])
    observed = graph.load_json(_artifact_bytes(root, result_ref)[0])
    if (set(observed) != {"tool", "settings", "runtime", "imports", "resources_read", "smoke"} or
            observed["tool"] != tool or observed["settings"] != binding["source"]["settings"]):
        raise ValueError("Invalid source-binding observation")
    allowed = {item["path"]: item["sha256"] for item in
               binding["source"]["resources"] + binding["source"]["runtime_imports"]}
    for item in observed["imports"] + observed["resources_read"]:
        if allowed.get(item["path"]) != item["sha256"]:
            raise ValueError("Observed unqualified source import/resource")
    runtime = observed["runtime"]
    if runtime["executable"] != binding["executable"]["path"]:
        raise ValueError("Source binding executed a different interpreter")
    if python:
        if (not runtime["version"].startswith("3.14.2 ") or runtime["isolated"] != 1 or
                runtime["no_site"] != 1 or runtime["no_bytecode"] is not True or
                runtime["versions"] != binding["source"]["settings"]["versions"] or
                runtime["pathspec_backend"] != "simple"):
            raise ValueError("Unqualified Python runtime/settings")
    elif runtime["version"] != "v24.11.1" or runtime["arch"] != "arm64" or runtime["compiler_version"] != "5.9.3":
        raise ValueError("Unqualified Node/compiler runtime")
    if (toolset_digest(config, root, roots) != context["toolset_sha256"] or
            controller_digest(context["controller_root"]) != context["controller_sha256"] or
            controller_digest(Path(__file__).resolve().parent) != context["controller_sha256"]):
        raise ValueError("Source binding/controller changed during execution")
    for artifact in (ref, request_ref, result_ref, command_ref):
        _artifact_bytes(root, artifact)
    return {"request": request_ref, "result": result_ref, "command": command_ref, "observed": observed}


def check_tool_outputs(config, repo, outputs, source_inputs=()):
    """Before snapshot exclusions, prove exact outputs cannot hide original inputs."""
    refs = tool_artifacts(config)
    paths = [graph.input_path(repo, name) for name in outputs]
    _path_partition(outputs)
    inputs = [Path(path) for path in source_inputs]
    if refs:
        inputs += [graph.input_path(config["tool_artifact_root"], ref["path"]) for ref in refs]
        for binding in _qualified_inputs(config, [repo]).values():
            inputs += [Path(binding["executable"]["path"])]
            inputs += [Path(item["path"]) for item in binding["dependencies"]]
            if "source" in binding:
                inputs += [Path(item["path"]) for item in binding["source"]["resources"]]
                inputs += [Path(item["path"]) for item in binding["source"]["runtime_imports"]]
    for output in paths:
        for source in inputs:
            if (source.is_relative_to(output) or output.is_relative_to(source) or
                    (source.exists() and output.exists() and os.path.samefile(source, output))):
                raise ValueError("Tool/source input overlaps reserved output: " + str(source))
    return refs


def _context_config(context):
    configs = []
    for ref in context["contract_artifacts"]:
        try:
            value = graph.load_json(graph.input_path(context["head_root"], ref["path"]).read_bytes())
        except ValueError:
            continue
        if isinstance(value, dict) and value.get("semantic_profile") == "workflow-reliability-q-v1":
            configs.append(value)
    if len(configs) != 1:
        raise ValueError("Context must bind exactly one measurement configuration")
    return configs[0]


def validate_config(config, root):
    fields = {"schema_version", "semantic_profile", "tools", "python_source_roots", "js_entrypoints",
              "suites", "coverage_policy", "architecture_rules", "mutation_cap",
              "mutation_max_seconds", "approval_artifact"}
    if not isinstance(config, dict) or set(config) - {"tool_artifact_root"} != fields:
        raise ValueError("Invalid MeasurementConfig fields")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1 or config["semantic_profile"] != "workflow-reliability-q-v1":
        raise ValueError("Unsupported measurement config version/profile")
    tool_artifacts(config)
    _qualified_inputs(config, [root])
    entrypoints = config["js_entrypoints"]
    if not isinstance(entrypoints, list):
        raise ValueError("JS entrypoints must be a list")
    if entrypoints and "typescript" not in config["tools"]:
        raise ValueError("JS entrypoints require qualified TypeScript")
    _path_partition([entry["path"] for entry in entrypoints])
    for entry in entrypoints:
        graph._fields(entry, "path origin_ref public_exports", "JS entrypoint")
        if (Path(entry["path"]).suffix.lower() not in JS_EXT or
                not isinstance(entry["origin_ref"], str) or not entry["origin_ref"].strip() or
                not graph.input_path(root, entry["path"]).is_file()):
            raise ValueError("JS entrypoint must bind an existing source and origin")
        exports = entry["public_exports"]
        if (not isinstance(exports, list) or any(not isinstance(name, str) or not name for name in exports) or
                exports != sorted(set(exports))):
            raise ValueError("JS entrypoint exports must be sorted unique names")
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


def _js_metadata_names(paths, config):
    names = set()
    for name in [*paths, *(entry["path"] for entry in config["js_entrypoints"])]:
        graph.relative_name(name)
        parent = Path(name).parent
        while True:
            names.add((parent / "package.json").as_posix())
            if parent == Path("."):
                break
            parent = parent.parent
    return sorted(names)


def _js_description(context, inv, config):
    qualified = _qualified_inputs(config, [context[key] for key in (
        "base_root", "head_root", "controller_root", "run_root")])["typescript"]
    source = qualified["source"]
    resources = [{"path": Path(pin["path"]).relative_to(source["roots"]["typescript"]).as_posix(),
                  "qualified_path": pin["path"], "sha256": pin["sha256"], "bytes": pin["bytes"]}
                 for pin in source["resources"]]
    parser = graph.digest({
        "semantic_version": graph.JS_SEMANTICS,
        "adapter_sha256": graph.artifact(context["controller_root"], "measure_js.mjs")["sha256"],
        "compiler_version": "5.9.3", "module_path": qualified["binding"]["module_path"],
        "resources": sorted(resources, key=lambda row: row["path"]),
        "runtime": {"executable": qualified["binding"]["executable"], "sha256": qualified["binding"]["sha256"],
                    "version": "v24.11.1", "architecture": "arm64"}, "options": source["settings"]})
    binding = {"semantic_version": graph.JS_SEMANTICS, "run_id": context["run_id"], "revision": inv["revision"],
               "git_revision": context["source"][inv["revision"]], "inventory_sha256": inv["digest"],
               "source_sha256": inv["source_sha256"], "parser_sha256": parser,
               "toolset_sha256": context["toolset_sha256"], "policy_sha256": context["policy_sha256"],
               "settings_sha256": graph.digest({"compiler_options": source["settings"],
                                                "semantic_version": graph.JS_SEMANTICS,
                                                "js_entrypoints": config["js_entrypoints"]})}
    entries = [entry for entry in inv["entries"] if entry["suffix"] in JS_EXT]
    inputs = [{"scope": "subject", **{key: entry[key] for key in ("path", "sha256", "bytes")}}
              for entry in entries]
    root = context[inv["revision"] + "_root"]
    for name in _js_metadata_names([entry["path"] for entry in entries], config):
        path = graph.input_path(root, name)
        if path.exists():
            data, _ = _regular_file(path)
            inputs.append({"scope": "subject", "path": name,
                           "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    inputs += [{"scope": "head-contract", **ref} for ref in context["contract_artifacts"]]
    inputs += [{"scope": "tool-resource", **{key: ref[key] for key in ("path", "sha256", "bytes")}}
               for ref in resources]
    inputs.sort(key=lambda row: (row["scope"], row["path"]))
    if len({(row["scope"], row["path"]) for row in inputs}) != len(inputs):
        raise ValueError("Duplicate admitted JS input")
    for row in inputs:
        input_root = {"subject": root, "head-contract": context["head_root"],
                      "tool-resource": source["roots"]["typescript"]}[row["scope"]]
        _artifact_bytes(input_root, {key: row[key] for key in ("path", "sha256", "bytes")})
        if row["scope"] == "head-contract" and context["source"]["files"].get(row["path"], {}).get(
                "sha256") != row["sha256"]:
            raise ValueError("JS contract is not source-bound")
    return binding, inputs


def _check_js_sources(context, inventories, config):
    validate_config(config, context["head_root"])
    if "typescript" not in config["tools"]:
        raise ValueError("Validated TypeScript mode required")
    graph._same(_context_config(context), config, "Source JS configuration")
    roots = [graph.root_path(context[key]) for key in ("base_root", "head_root", "controller_root", "run_root")]
    if any(a.is_relative_to(b) or b.is_relative_to(a) for i, a in enumerate(roots) for b in roots[i + 1:]):
        raise ValueError("JS Context roots must be disjoint")
    _validate_root_independence(roots)
    for inv in inventories:
        graph._same(inventory(context, inv["revision"], inv["changed_production"], include_js=True),
                    inv, "JS source inventory")
    observed = source_snapshot(context["head_root"], context["source"]["scope"])
    observed.update(base=context["source"]["base"], head=context["source"]["head"])
    graph._same(observed, context["source"], "JS source Snapshot")
    for ref in context["contract_artifacts"]:
        _artifact_bytes(context["head_root"], ref)
    if (toolset_digest(config, context["run_root"], roots) != context["toolset_sha256"] or
            controller_digest(context["controller_root"], include_js=True) != context["controller_sha256"] or
            controller_digest(Path(__file__).resolve().parent, include_js=True) != context["controller_sha256"] or
            graph.digest(config_policy(config)) != context["policy_sha256"]):
        raise ValueError("JS tool/controller/policy binding mismatch")


def prepare_js_manifest(context, inventories, config):
    _check_js_sources(context, inventories, config)
    validate_baseline(context["base_root"], context["source"]["base"])
    manifest = graph._js_manifest(context, config, inventories, phase="js-preflight.json")
    ref = graph.persist(context, "js-preflight.json", manifest)
    context["output_manifest"] = ref
    return ref


def _check_js_attempt(context, inv, config, purpose):
    request, _, _, _, _, _ = graph._js_transport(context, inv, config, purpose=purpose)
    binding, inputs = _js_description(context, inv, config)
    graph._same(request["binding"], binding, "JS derived parser binding")
    graph._same(request["inputs"], inputs, "JS derived input admission")


def finish_js_manifest(context, inventories, config):
    _check_js_sources(context, inventories, config)
    for inv in inventories:
        # Both attempts must share their compiled caller purpose. Accepting
        # validation additionally requires the original/replay ordered pair.
        purpose = graph._js_json(context, graph._js_name(inv["revision"], "request"))[1]["purpose"]
        _check_js_attempt(context, inv, config, purpose)
    purposes = {graph._js_json(context, graph._js_name(inv["revision"], "request"))[1]["purpose"]
                for inv in inventories}
    if len(purposes) != 1:
        raise ValueError("Mixed JS execution purposes")
    manifest = graph._js_manifest(context, config, inventories, phase="js-produced.json")
    ref = graph.persist(context, "js-produced.json", manifest)
    context["output_manifest"] = ref
    return ref


def execute_js(context, inventory, config):
    _execute_js(context, inventory, config, purpose="produce")


def _execute_js(context, inv, config, *, purpose):
    if purpose not in {"produce", "validate"}:
        raise ValueError("Invalid private JS execution purpose")
    _check_js_sources(context, [inv], config)
    other = "head" if inv["revision"] == "base" else "base"
    inventories = sorted([inv, inventory(context, other, {}, include_js=True)], key=lambda item: item["revision"])
    if context["output_manifest"]["path"] != "js-preflight.json":
        raise ValueError("JS execution requires active preflight")
    graph._js_manifest(context, config, inventories)
    binding, inputs = _js_description(context, inv, config)
    for slot in ("request", "command", "result", "symbols"):
        if graph.input_path(context["run_root"], graph._js_name(inv["revision"], slot)).exists():
            raise ValueError("JS execution slots must be fresh")
    request = {"schema_version": 1, "binding": binding, "execution_id": uuid.uuid4().hex, "purpose": purpose,
               "context": dict(context), "inventory": inv, "config": config,
               "pre_manifest": context["output_manifest"], "inputs": inputs,
               "outputs": {slot: graph._js_name(inv["revision"], slot) for slot in ("result", "symbols")}}
    ref = graph.persist(context, graph._js_name(inv["revision"], "request"), request)
    argv = [config["tools"]["typescript"]["executable"],
            str(Path(context["controller_root"]) / "measure_js.mjs"), str(Path(context["run_root"]) / ref["path"])]
    env = {name: value for name, value in os.environ.items() if not (
        name.upper().startswith(("PYTHON", "NODE_", "TS_NODE_")) or name.upper() == "VSCODE_INSPECTOR_OPTIONS")}
    removed = sorted(set(os.environ) - set(env))
    _check_js_sources(context, [inv], config)
    graph._js_manifest(context, config, inventories)
    graph._same(graph.load_json(_artifact_bytes(context["run_root"], ref)[0]), request, "JS persisted request")
    print("measure: executing JS " + purpose + " " + inv["revision"] + " " + request["execution_id"],
          file=sys.stderr, flush=True)
    code, stdout, stderr = run_capture(argv, cwd=context[inv["revision"] + "_root"], env=env,
                                       idle=30, max_total=90)
    outputs = {}
    for slot in ("result", "symbols"):
        path = graph.input_path(context["run_root"], request["outputs"][slot])
        outputs[slot] = graph.artifact(context["run_root"], request["outputs"][slot]) if path.exists() else None
        if outputs[slot] is not None:
            _artifact_bytes(context["run_root"], outputs[slot])
    command = {"schema_version": 1, "binding": binding, "execution_id": request["execution_id"],
               "request": ref, "pre_manifest": context["output_manifest"], "argv": argv,
               "cwd": context[inv["revision"] + "_root"], "idle_seconds": 30, "max_seconds": 90,
               "environment_delta": {"removed_names": removed}, "returncode": code,
               "stdout": stdout, "stderr": stderr,
               "capture_semantics": "run_capture UTF-8 replacement-decoded, newline-normalized separate streams",
               **outputs}
    graph.persist(context, graph._js_name(inv["revision"], "command"), command)
    print("measure: captured JS " + purpose + " " + inv["revision"] + " " + request["execution_id"] + " exit " + str(code),
          file=sys.stderr, flush=True)
    _check_js_sources(context, [inv], config)
    graph._js_manifest(context, config, inventories)
    _check_js_attempt(context, inv, config, purpose)


def _validate_js_replay(context, base, head, config):
    inventories = [parsed["inventory"] for parsed in (base, head)]
    _check_js_sources(context, inventories, config)
    for inv in inventories:
        _check_js_attempt(context, inv, config, "produce")
    with tempfile.TemporaryDirectory(prefix="jsv-") as temporary:
        replay = {**context, "run_root": str(Path(temporary).resolve())}
        stage_tool_inputs(replay, config)
        prepare_js_manifest(replay, inventories, config)
        for inv in inventories:
            _execute_js(replay, inv, config, purpose="validate")
        finish_js_manifest(replay, inventories, config)
        parsed = [graph.parse_files(replay, inv, config) for inv in inventories]
        manifest = make_manifest(replay, *parsed)
        replay["output_manifest"] = graph.persist(replay, "manifest.json", manifest)
        for original, fresh in zip((base, head), parsed):
            graph._compare_js_replay(context, original, replay, fresh, config)
        _check_js_sources(context, inventories, config)
        _check_js_sources(replay, inventories, config)
        graph._js_manifest(context, config, inventories)
        graph._js_manifest(replay, config, inventories)
        for inv in inventories:
            _check_js_attempt(context, inv, config, "produce")
            _check_js_attempt(replay, inv, config, "validate")


def make_manifest(context, base, head):
    config = _context_config(context)
    if "typescript" in config["tools"]:
        return graph._js_manifest(context, config, [base["inventory"], head["inventory"]], phase="manifest.json")
    inputs = [{"artifact": ref, "role": "qualification", "revision": None}
              for ref in tool_artifacts(config)]
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
    include_js = "typescript" in config["tools"]
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
            context["toolset_sha256"] != toolset_digest(config, context["run_root"], roots) or
            context["controller_sha256"] != controller_digest(context["controller_root"], include_js=include_js) or
            context["controller_sha256"] != controller_digest(Path(__file__).resolve().parent, include_js=include_js)):
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
    if include_js:
        _validate_js_replay(context, base, head, config)
    for revision, parsed in (("base", base), ("head", head)):
        inv = parsed["inventory"]
        if inv["revision"] != revision or _json_bytes(inventory(
                context, revision, inv["changed_production"], include_js=include_js)) != _json_bytes(inv):
            raise ValueError("Inventory is missing, stale or bound to the wrong revision")
        raw_ref = graph.artifact(context["run_root"], graph.graph_name(revision))
        raw = graph.read_owned(context, artifacts, raw_ref, "graph", revision)
        derived += (graph.observations(context, parsed, config) if include_js else
                    graph.validate_evidence(context, parsed, config, raw, artifacts))
        derived += [unavailable(context, parsed, name) for name in sorted(LOWER_BETTER - {"cycles"})]
    derived.sort(key=lambda item: (item["metric"], item["revision"]))
    if _json_bytes(sorted(observations, key=lambda item: (item["metric"], item["revision"]))) != _json_bytes(derived):
        raise ValueError("Observations disagree with producer-owned raw recomputation")
    _validate_root_independence(roots)
    if context["toolset_sha256"] != toolset_digest(config, context["run_root"], roots):
        raise ValueError("Tool inputs changed during producer validation")
    return derived


def controller_digest(root, *, include_js=False):
    if type(include_js) is not bool:
        raise ValueError("include_js must be a bool")
    names = ("measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py")
    if include_js:
        names += ("measure_js.mjs",)
    pins = {}
    for name in names:
        path = graph.input_path(root, name)
        content = _regular_file(path)[0] if include_js else path.read_bytes()
        pins[name] = hashlib.sha256(content).hexdigest()
    return graph.digest(pins)


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
