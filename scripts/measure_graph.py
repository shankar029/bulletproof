"""Source-bound Python literal-import evidence. No discovery or policy composition."""

import ast
import _imp
import hashlib
from importlib.machinery import BuiltinImporter, FrozenImporter
import io
import json
import os
from pathlib import Path
import sys
import time
import tokenize

from evidence import _json_bytes, write_json_atomic

SEMANTICS = "python-literal-import-v3"
RULE_IDS = ["ARCH01", "ARCH02", "ARCH03", "ARCH04", "ARCH05"]
CYCLE_STEPS = 100000
CYCLE_LIMIT = 10000
CYCLE_SECONDS = 5


def digest(value):
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def load_json(content):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    try:
        return json.loads(content, object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              ValueError("Non-finite JSON: " + value)))
    except (TypeError, UnicodeError) as error:
        raise ValueError("Invalid JSON encoding") from error


def relative_name(name, *, directory=False):
    if directory and name == ".":
        return name
    if (not isinstance(name, str) or not name or "\\" in name or ":" in name or
            any(ord(char) < 32 for char in name) or name.startswith("/") or
            any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError("Noncanonical relative path: %r" % name)
    if os.name == "nt" and any(part.endswith((".", " ")) for part in name.split("/")):
        raise ValueError("Aliased relative path: %r" % name)
    return name


def root_path(value):
    root = Path(value)
    if not root.is_absolute() or not root.is_dir() or str(root.resolve()) != str(root):
        raise ValueError("Root must be a canonical existing absolute directory")
    for part in (root, *root.parents):
        if part.is_symlink() or part.is_junction():
            raise ValueError("Linked root is unsupported")
        if part.parent != part and part.name not in os.listdir(part.parent):
            raise ValueError("Aliased root component: " + str(part))
    return root


def input_path(root, name, *, directory=False):
    root = root_path(root)
    relative_name(name, directory=directory)
    path = root / name
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink() or part.is_junction():
            raise ValueError("Linked path is unsupported: " + name)
        if part.exists() and part.name not in os.listdir(part.parent):
            raise ValueError("Aliased path component: " + name)
    if not path.resolve().is_relative_to(root):
        raise ValueError("Path escapes root: " + name)
    return path


def artifact(root, name):
    path = input_path(root, name)
    content = path.read_bytes()
    return {"path": name, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}


def persist(context, name, value):
    path = input_path(context["run_root"], name)
    if path.exists():
        raise ValueError("Refusing to overwrite an artifact: " + name)
    write_json_atomic(path, value)
    return artifact(context["run_root"], name)


def _frozen_import_binding():
    """Observe the complete effective CPython frozen table, without importing it.

    The runtime has already applied environment/CLI precedence, ignore-environment
    flags and build defaults. Raw os.environ/sys._xoptions can be stale or
    overridden; neither is an authoritative description of that effective state.
    """
    census = getattr(_imp, "_frozen_module_names", None)
    if census is None:
        raise ValueError("Cannot bind parser: CPython frozen-module census unavailable")
    names = census()
    if (not isinstance(names, list) or not names or
            any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names)):
        raise ValueError("Cannot bind parser: malformed frozen-module census")
    binding = {}
    for name in sorted(names):
        spec = FrozenImporter.find_spec(name)
        binding[name] = (None if spec is None else
                         {"origin": spec.origin, "package": spec.submodule_search_locations is not None})
    return binding


def parser_digest():
    # Bind actual adapter, Python grammar implementation and runtime identity.
    return digest({"adapter": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "ast": hashlib.sha256(Path(ast.__file__).read_bytes()).hexdigest(),
                   "runtime": sys.version,
                   "import_options": {key: value for key, value in sys._xoptions.items()
                                      if key != "frozen_modules"},
                   "frozen_modules": _frozen_import_binding(),
                   "builtin_modules": sorted(sys.builtin_module_names),
                   "executable": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()})


def syntax_name(revision, path):
    return revision + "/syntax/" + hashlib.sha256(path.encode()).hexdigest() + ".json"


def graph_name(revision):
    return revision + "/graph.json"


def _syntax(content, entry, inventory, parser):
    tree = ast.parse(content, filename=entry["path"])
    compile(tree, entry["path"], "exec")  # Validate contextual errors without execution.
    encoding, _ = tokenize.detect_encoding(io.BytesIO(content).readline)
    text = content.decode(encoding)
    lines = text.splitlines(keepends=True)
    # AST columns are UTF-8 byte offsets, even for a non-UTF8 encoded source.
    raw_encoding = "utf-8" if encoding == "utf-8-sig" else encoding
    prefix = 3 if content.startswith(b"\xef\xbb\xbf") else 0
    starts = [prefix]
    for line in lines:
        starts.append(starts[-1] + len(line.encode(raw_encoding)))

    def span(node):
        def offset(line, column):
            before = lines[line - 1].encode("utf-8")[:column].decode("utf-8")
            return starts[line - 1] + len(before.encode(raw_encoding))
        return {"start_byte": offset(node.lineno, node.col_offset),
                "end_byte": offset(node.end_lineno, node.end_col_offset),
                "start_line": node.lineno, "end_line": node.end_lineno}

    nodes, imports, outside = [], [], []
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            for alias in node.names:
                aliases[alias.asname or alias.name] = (node.module or "") + "." + alias.name
    for node in ast.walk(tree):
        if hasattr(node, "end_lineno") and node.end_lineno is not None:
            nodes.append({"kind": type(node).__name__, "span": span(node)})
        if isinstance(node, ast.Import):
            imports.extend({"specifier": alias.name, "kind": "import", "span": span(node)}
                           for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            # Serialize the grammar, not an opaque live AST, for shared consumers.
            imports.extend({"specifier": "." * node.level + (node.module or "") + ":" + alias.name,
                            "kind": "from", "span": span(node)} for alias in node.names)
        elif isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            first, *tail = name.split(".")
            qualified = ".".join([aliases.get(first, first), *tail])
            builtin = qualified.removeprefix("builtins.")
            kind = None
            if builtin == "__import__" or qualified.startswith("importlib."):
                kind = "computed-import"
            elif builtin in {"eval", "exec", "getattr", "setattr", "globals", "locals"}:
                kind = "reflection"
            elif qualified in {"subprocess.run", "subprocess.Popen", "subprocess.call",
                               "subprocess.check_call", "subprocess.check_output", "os.system", "os.popen"}:
                kind = "runtime-command"
            if kind:
                outside.append({"kind": kind, "span": span(node),
                                "reason": qualified + " is outside the static literal-import model"})
    return {"schema_version": 1, "revision": inventory["revision"],
            "inventory_sha256": inventory["digest"], "path": entry["path"],
            "source_sha256": entry["sha256"], "parser_sha256": parser,
            "semantic_version": SEMANTICS, "nodes": nodes, "literal_imports": imports,
            "outside_model": outside, "diagnostics": []}


def _module_candidates(module, source_roots, paths):
    stem = module.replace(".", "/")
    candidates = set()
    for root in source_roots:
        prefix = "" if root == "." else root + "/"
        for candidate in (prefix + stem + ".py", prefix + stem + "/__init__.py"):
            if candidate in paths:
                candidates.add(candidate)
        namespace = prefix + stem + "/"
        if any(path.startswith(namespace) for path in paths) and prefix + stem + "/__init__.py" not in paths:
            candidates.add(namespace)  # Namespace package; no executable module node.
    return sorted(candidates)


def _resolve(source, item, roots, paths):
    specifier = item["specifier"]
    module, _, child = specifier.partition(":") if item["kind"] == "from" else (specifier, "", "")
    relative = module.startswith(".")
    if not relative:
        # Model the standard runtime finders before filesystem search, without
        # executing source or consulting mutable sys.modules/custom import hooks.
        # stdlib membership alone does NOT imply precedence: ordinary source
        # and extension modules may legitimately be shadowed by source roots.
        top = module.split(".")[0]
        builtin = BuiltinImporter.find_spec(top)
        if builtin is not None:
            if "." in module and builtin.submodule_search_locations is None:
                return [], "Runtime module is not a package"
            return [(specifier, "external")], None
        if FrozenImporter.find_spec(top) is not None:
            # Frozen stdlib modules can publish submodule aliases (os.path).
            # Keep their contents opaque like other external dependencies; do
            # not execute them or mistake a local namesake for their child.
            return [(specifier, "external")], None
    if relative:
        level = len(module) - len(module.lstrip("."))
        parts = source.split("/")[:-1]
        # A declared source root is the top of a package context, not its parent.
        owners = [root for root in roots if root == "." or source.startswith(root + "/")]
        owner = max(owners, key=lambda root: 0 if root == "." else len(root.split("/")), default=".")
        depth = 0 if owner == "." else len(owner.split("/"))
        if len(parts) - depth < level:
            return [], "Relative import escapes package context"
        package = parts[:len(parts) - level + 1]
        suffix = module[level:]
        module = ".".join(package + ([suffix] if suffix else []))
        search_roots = ["."]
    else:
        search_roots = roots
    candidates = _module_candidates(module, search_roots, paths) if module else []
    if len(candidates) > 1:
        return [], "Ambiguous local module"
    targets = []
    if candidates:
        if not candidates[0].endswith("/"):
            targets.append((candidates[0], "local"))
        if child and child != "*":
            children = _module_candidates(module + "." + child, search_roots, paths)
            if len(children) > 1:
                return [], "Ambiguous child module"
            targets.extend((candidate, "local") for candidate in children if not candidate.endswith("/"))
            if not children and candidates[0].endswith("/"):
                return [], "Missing namespace child module"
        # Loading a submodule also executes each concrete parent package.
        bits = module.split(".")
        for index in range(1, len(bits)):
            parents = _module_candidates(".".join(bits[:index]), search_roots, paths)
            if len(parents) > 1:
                return [], "Ambiguous parent package"
            targets.extend((parent, "local") for parent in parents if parent.endswith("/__init__.py"))
        return sorted(set(targets)), None
    top = module.split(".")[0]
    local_top = _module_candidates(top, search_roots, paths)
    if relative or local_top:
        return [], "Missing literal local import"
    # Bare third-party packages are external terminals, not asserted installed.
    return [(specifier, "external")], None


def enumerate_cycles(graph):
    """Canonical elementary directed cycles, SCC-pruned and bounded, never truncated."""
    adjacent = {node: set() for node in graph["nodes"]}
    reverse = {node: set() for node in adjacent}
    for edge in graph["edges"]:
        if edge["resolution"] == "local":
            adjacent[edge["from"]].add(edge["to"])
            reverse[edge["to"]].add(edge["from"])
    seen, order = set(), []
    for start in sorted(adjacent):
        stack = [(start, False)]
        while stack:
            node, done = stack.pop()
            if done:
                order.append(node)
            elif node not in seen:
                seen.add(node)
                stack.append((node, True))
                stack.extend((child, False) for child in sorted(adjacent[node], reverse=True) if child not in seen)
    components = []
    seen.clear()
    for start in reversed(order):
        if start in seen:
            continue
        component, pending = set(), [start]
        seen.add(start)
        while pending:
            node = pending.pop()
            component.add(node)
            for child in reverse[node] - seen:
                seen.add(child)
                pending.append(child)
        components.append(component)
    cycles, steps = [], 0
    deadline = time.monotonic() + CYCLE_SECONDS
    for component in components:
        for start in sorted(component):
            path, visited = [start], {start}
            stack = [iter(sorted(adjacent[start] & component))]
            while stack:
                steps += 1
                if steps > CYCLE_STEPS or time.monotonic() > deadline:
                    raise ValueError("Cycle enumeration budget exceeded")
                child = next(stack[-1], None)
                if child is None:
                    stack.pop()
                    visited.remove(path.pop())
                elif child == start:
                    cycles.append({"id": digest(path), "ordered_nodes": path.copy()})
                    if len(cycles) > CYCLE_LIMIT:
                        raise ValueError("Cycle output budget exceeded")
                elif child > start and child not in visited:
                    visited.add(child)
                    path.append(child)
                    stack.append(iter(sorted(adjacent[child] & component)))
    return sorted(cycles, key=lambda cycle: cycle["ordered_nodes"])


def _graph(inventory, syntax, config):
    paths = {entry["path"] for entry in inventory["entries"]}
    graph = {"schema_version": 1, "inventory_sha256": inventory["digest"],
             "nodes": sorted(paths), "edges": [], "unresolved": [], "outside_model": [], "cycles": []}
    for source, evidence in sorted(syntax.items()):
        for item in evidence["literal_imports"]:
            targets, error = _resolve(source, item, config["python_source_roots"], paths)
            if error:
                graph["unresolved"].append({"from": source, "specifier": item["specifier"],
                                             "span": item["span"], "reason": error})
            for target, resolution in targets:
                edge = {"from": source, "to": target, "kind": "import",
                        "resolution": resolution, "span": item["span"]}
                if edge not in graph["edges"]:
                    graph["edges"].append(edge)
        graph["outside_model"].extend({"path": source, **site} for site in evidence["outside_model"])
    return graph


def _parse(context, inventory, config):
    root = context[inventory["revision"] + "_root"]
    # A root may be newly introduced at head, but an existing root at either
    # revision must use its own canonical inventory spelling.
    for name in config["python_source_roots"]:
        path = input_path(root, name, directory=True)
        if path.exists() and not path.is_dir():
            raise ValueError("Source root is not a directory: " + name)
    parser = parser_digest()
    receipts, syntax = [], {}
    for entry in inventory["entries"]:
        receipt = {"path": entry["path"], "source_sha256": entry["sha256"],
                   "adapter": "python-ast", "run_id": context["run_id"], "revision": inventory["revision"],
                   "inventory_sha256": inventory["digest"], "toolset_sha256": context["toolset_sha256"],
                   "policy_sha256": context["policy_sha256"], "semantic_version": SEMANTICS,
                   "state": "unsupported", "unit_count": None,
                   "reason": "Q1 supports only Python syntax; this language requires a later adapter", "raw": []}
        if entry["language"] == "python":
            try:
                content = input_path(root, entry["path"]).read_bytes()
                if hashlib.sha256(content).hexdigest() != entry["sha256"]:
                    raise ValueError("Source changed since inventory")
                evidence = _syntax(content, entry, inventory, parser)
                syntax[entry["path"]] = evidence
                receipt.update(state="processed", unit_count=len(evidence["literal_imports"]), reason="")
            except (OSError, ValueError, SyntaxError, UnicodeError, LookupError, RecursionError) as error:
                receipt.update(state="failed", reason=str(error))
        receipts.append(receipt)
    graph = _graph(inventory, syntax, config)
    cycle_error = None
    try:
        graph["cycles"] = enumerate_cycles(graph)
    except ValueError as error:
        cycle_error = str(error)
    return receipts, syntax, graph, cycle_error


def _raw(context, inventory, receipts, syntax_refs, graph):
    return {"schema_version": 1, "run_id": context["run_id"], "revision": inventory["revision"],
            "inventory_sha256": inventory["digest"], "source_sha256": inventory["source_sha256"],
            "adapter": "python-ast", "semantic_version": SEMANTICS,
            "toolset_sha256": context["toolset_sha256"], "policy_sha256": context["policy_sha256"],
            "receipts": receipts, "commands": [], "qualified_raw": list(syntax_refs.values()),
            "payload": {"graph": graph}}


def parse_files(context, inventory, config):
    receipts, syntax, graph, _ = _parse(context, inventory, config)
    refs = {name: persist(context, syntax_name(inventory["revision"], name), value)
            for name, value in sorted(syntax.items())}
    for receipt in receipts:
        if receipt["path"] in refs:
            receipt["raw"] = [refs[receipt["path"]]]
    persist(context, graph_name(inventory["revision"]), _raw(context, inventory, receipts, refs, graph))
    return {"inventory": inventory, "receipts": receipts, "syntax_artifacts": refs, "graph": graph}


def _test_path(path):
    parts = path.split("/")
    name = parts[-1]
    return (any(part in {"tests", "test", "__tests__"} for part in parts) or
            name.startswith("test_") or name.endswith("_test.py") or ".test." in name or ".spec." in name)


def evaluate_rules(graph, rules):
    if (not isinstance(rules, list) or len(rules) != 5 or
            sorted(rule.get("id", "") for rule in rules if isinstance(rule, dict)) != RULE_IDS or
            any(set(rule) != {"id", "version", "origin_ref"} or type(rule["version"]) is not int or
                rule["version"] != 1 or not isinstance(rule["origin_ref"], str) or not rule["origin_ref"].strip()
                for rule in rules)):
        raise ValueError("All five compiled architecture rules are required at version 1")
    findings = {}
    local = {node: [] for node in graph["nodes"]}
    for edge in graph["edges"]:
        if edge["resolution"] == "local":
            local[edge["from"]].append(edge)
    roots = [node for node in graph["nodes"] if node in {
        "scripts/probe.py", "scripts/mutate.py", "scripts/unittest_result.py",
        "scripts/evidence.py", "scripts/run.py", "scripts/native_result.mjs", "scripts/measure_js.mjs"} or
        (node.startswith("scripts/measure") and node.endswith(".py") and node.count("/") == 1)]

    def add(rule, path, target, span, message):
        # Edge identity deliberately excludes line numbers: moving the same import is not new.
        parts = [rule, path, target]
        identity = digest(parts)
        findings[identity] = {"id": identity, "rule": rule, "path": path, "span": span,
                              "symbol": target, "message": message, "confidence": None,
                              "identity_parts": parts}

    for root in roots:
        pending, seen = [root], set()
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            for edge in local[node]:
                target = edge["to"]
                if target.startswith("scripts/workflow") and target.endswith(".py"):
                    add("ARCH01", root, target, edge["span"], "Measurement reaches workflow implementation")
                pending.append(target)
    for edge in graph["edges"]:
        source, target = edge["from"], edge["to"]
        is_local = edge["resolution"] == "local"
        foundation = source in {"scripts/evidence.py", "scripts/run.py"}
        bare = target.split(":")[0].split(".")[0]
        if foundation and (is_local or bare not in sys.stdlib_module_names | set(sys.builtin_module_names)):
            add("ARCH02", source, target, edge["span"], "Foundation may import only standard-library modules")
        if (is_local and source.startswith("scripts/") and not _test_path(source) and
                (_test_path(target) or target.split("/")[0] in {"evals", "benchmark", "examples"})):
            add("ARCH03", source, target, edge["span"], "Production imports a test or fixture")
        if (is_local and source.startswith("evals/lib/") and not _test_path(source) and
                target.startswith("scripts/") and target != "scripts/native_result.mjs"):
            add("ARCH04", source, target, edge["span"], "Evaluation imports outside the shared reporter seam")
    for site in graph["outside_model"]:
        if site["path"] in {"scripts/evidence.py", "scripts/run.py"} and site["kind"] != "runtime-command":
            add("ARCH05", site["path"], site["kind"] + ":" + site["reason"], site["span"],
                "Foundation uses dynamic module loading or reflection")
    return sorted(findings.values(), key=lambda finding: finding["id"])


def read_owned(context, artifacts, ref, role, revision):
    if artifacts["root"] != str(root_path(context["run_root"])) or artifacts["run_id"] != context["run_id"]:
        raise ValueError("Artifact manifest root/run mismatch")
    expected = {"artifact": ref, "role": role, "revision": revision}
    if (artifacts["inputs"].count(expected) != 1 or ref["path"] not in artifacts["reserved_outputs"] or
            artifact(context["run_root"], ref["path"]) != ref):
        raise ValueError("Artifact ownership or bytes mismatch")
    return load_json(input_path(context["run_root"], ref["path"]).read_bytes())


def observations(context, parsed, config, cycle_error=None):
    inv, graph = parsed["inventory"], parsed["graph"]
    if cycle_error is None:
        try:
            enumerate_cycles(graph)
        except ValueError as error:
            cycle_error = str(error)
    reasons = [receipt["path"] + ": " + receipt["reason"] for receipt in parsed["receipts"]
               if receipt["state"] != "processed"]
    if inv["enumeration_state"] != "complete":
        reasons.append("Inventory enumeration failed")
    if graph["unresolved"]:
        reasons.append("Unresolved literal local imports")
    if cycle_error:
        reasons.append(cycle_error)
    findings = evaluate_rules(graph, config["architecture_rules"])
    common = {"schema_version": 1, "revision": inv["revision"], "run_id": context["run_id"],
              "source_sha256": inv["source_sha256"], "inventory_sha256": inv["digest"],
              "semantic_version": SEMANTICS, "toolset_sha256": context["toolset_sha256"],
              "policy_sha256": context["policy_sha256"], "receipts": parsed["receipts"],
              "outside_model": graph["outside_model"], "commands": [],
              "raw": [artifact(context["run_root"], graph_name(inv["revision"]))], "reasons": reasons,
              "state": "partial" if reasons else "complete"}
    return [{**common, "metric": "cycles", "value": None if cycle_error else len(graph["cycles"]),
             "findings": []},
            {**common, "metric": "architecture_rules", "value": len(findings), "findings": findings}]


def validate_evidence(context, parsed, config, raw, artifacts):
    """Reparse exact source bytes and compare every receipt/syntax/graph field."""
    inv = parsed["inventory"]
    receipts, syntax, graph, cycle_error = _parse(context, inv, config)
    refs = {}
    for name, value in sorted(syntax.items()):
        ref = artifact(context["run_root"], syntax_name(inv["revision"], name))
        decoded = read_owned(context, artifacts, ref, "syntax", inv["revision"])
        if _json_bytes(decoded) != _json_bytes(value):
            raise ValueError("Syntax evidence disagrees with source")
        refs[name] = ref
    for receipt in receipts:
        if receipt["path"] in refs:
            receipt["raw"] = [refs[receipt["path"]]]
    expected = {"inventory": inv, "receipts": receipts, "syntax_artifacts": refs, "graph": graph}
    if _json_bytes(expected) != _json_bytes(parsed):
        raise ValueError("Parsed inventory/graph disagrees with source")
    expected_raw = _raw(context, inv, receipts, refs, graph)
    if _json_bytes(raw) != _json_bytes(expected_raw):
        raise ValueError("Raw graph disagrees with recomputed source evidence")
    return observations(context, expected, config, cycle_error)
