"""Qualified scalar adapters over the shared, immutable parsed inventory."""

import hashlib
import io
import json
import os
from pathlib import Path
import re
import tokenize

import measure_graph as graph
from run import run_capture

SEMANTICS = {
    "duplication_pct": "jscpd-union-lines-v1",
    "complexity_max": "lizard-lexical-functions-v1",
    "complexity_avg": "lizard-lexical-functions-v1",
    "dead_exports": "mixed-static-unused-v1",
    "static_findings": "mixed-static-diagnostics-v1",
}


def _count(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("Invalid scalar count")
    return value


def duplication_value(payload):
    files = {}
    for item in payload["files"]:
        if item["path"] in files or type(item["processed"]) is not bool:
            raise ValueError("Duplicate or invalid duplication file")
        files[item["path"]] = _count(item["source_lines"])
    covered = set()
    for clone in payload["clones"]:
        if len(clone["locations"]) < 2:
            raise ValueError("Clone requires at least two locations")
        for location in clone["locations"]:
            start = _count(location["start_line"], 1)
            end = _count(location["end_line"], 1)
            if location["path"] not in files or not start <= end <= files[location["path"]]:
                raise ValueError("Clone location outside analyzer census")
            covered.update((location["path"], line) for line in range(start, end + 1))
    denominator = sum(files.values())
    return round(100 * len(covered) / denominator, 2) if denominator else None


def complexity_values(payload):
    values = [_count(function["cyclomatic_complexity"], 1)
              for item in payload["files"] for function in item["functions"]]
    return (max(values), round(sum(values) / len(values), 2)) if values else (None, None)


def source_span(content, start_line, start_column, end_line, end_column):
    """Ruff uses one-based Unicode codepoint columns, not UTF-8 byte columns."""
    for value in (start_line, start_column, end_line, end_column):
        _count(value, 1)
    lines = _physical_lines(content)
    if not start_line <= end_line <= len(lines):
        raise ValueError("Finding line outside source")

    def offset(line, column):
        text = lines[line - 1]
        if column > len(text.rstrip("\r\n")) + 1:
            raise ValueError("Finding column outside source")
        return sum(len(item.encode("utf-8")) for item in lines[:line - 1]) + len(
            text[:column - 1].encode("utf-8"))

    start, end = offset(start_line, start_column), offset(end_line, end_column)
    if start >= end:
        raise ValueError("Finding requires a nonempty source span")
    return {"start_byte": start, "end_byte": end,
            "start_line": start_line, "end_line": end_line}


def _line_span(content, first, last):
    lines = _physical_lines(content)
    _count(first, 1)
    _count(last, 1)
    if not first <= last <= len(lines):
        raise ValueError("Function/finding line outside source")
    end_column = len(lines[last - 1].rstrip("\r\n")) + 1
    return source_span(content, first, 1, last, end_column)


def _physical_lines(content):
    lines = re.split(r"(?<=\n)|(?<=\r)(?!\n)", content.decode("utf-8"))
    return lines[:-1] if lines[-1] == "" else lines


def _binding_artifact(context, config, tool, field):
    ref = config["tools"][tool][field]
    for root in (config["tool_artifact_root"], context["run_root"]):
        if graph.artifact(root, ref["path"]) != ref:
            raise ValueError("Scalar tool artifact changed")
    return graph.load_json(graph.input_path(context["run_root"], ref["path"]).read_bytes())


def _environment():
    removed = sorted(name for name in os.environ if name.upper().startswith(
        ("PYTHON", "NODE_", "TS_NODE_", "RUFF_", "JSCPD_")) or
        name.upper() == "VSCODE_INSPECTOR_OPTIONS")
    return {name: value for name, value in os.environ.items() if name not in removed}, removed


# Runs in a fresh isolated interpreter; no subject code is imported or executed.
SOURCE_WORKER = r'''
import contextlib, hashlib, importlib, importlib.metadata, io, json, sys
from importlib.machinery import BuiltinImporter, FrozenImporter, PathFinder
from pathlib import Path
request = json.loads(Path(sys.argv[1]).read_bytes())
source = request["source"]
base = Path(sys.base_prefix).resolve()
if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
    raise ValueError("Scalar source tools require -I -S -B")
if not all(Path(p).resolve().is_relative_to(base) for p in sys.path):
    raise ValueError("Unexpected interpreter startup path")
allowed = {str(Path(p["path"]).resolve()): p["sha256"]
           for p in source["resources"] + source["runtime_imports"]}
def checked(filename):
    path = Path(filename).resolve()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if allowed.get(str(path)) != digest:
        raise ImportError("Unqualified import/resource: " + str(path))
    return str(path), digest
class PinnedFinder:
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)
        if spec and spec.origin not in (None, "built-in", "frozen"):
            checked(spec.origin)
        return spec
sys.meta_path[:] = [BuiltinImporter, FrozenImporter, PinnedFinder]
sys.path[:0] = list(source["roots"].values())
if list(importlib.metadata.distributions()):
    raise ValueError("Unqualified installed distribution/plugin")
import lizard, vulture, pygments, pathspec
from lizard_languages import get_reader_for, PythonReader, JavaScriptReader, TypeScriptReader, TSXReader
from pathspec._backends import agg
from pygments import plugin
versions = {"lizard": lizard.version, "vulture": vulture.__version__,
            "pygments": pygments.__version__, "pathspec": pathspec.__version__}
if versions != source["settings"]["versions"] or agg._BEST_BACKEND != "simple":
    raise ValueError("Unqualified versions/backend")
if list(plugin.iter_entry_points(plugin.LEXER_ENTRY_POINT)):
    raise ValueError("Unqualified lexer plugin")
for name in source["settings"]["optional_absent"]:
    if importlib.util.find_spec(name) is not None:
        raise ValueError("Unqualified optional dependency: " + name)
rows, resources = [], []
analyzer = lizard.FileAnalyzer(lizard.get_extensions([]))
scanner = vulture.Vulture()
readers = {".py": PythonReader, ".js": JavaScriptReader, ".mjs": JavaScriptReader,
           ".cjs": JavaScriptReader, ".ts": TypeScriptReader, ".jsx": TSXReader, ".tsx": TSXReader}
for entry in request["files"]:
    path = Path(request["root"]) / entry["path"]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise ValueError("Scalar source changed: " + entry["path"])
    out, err = io.StringIO(), io.StringIO()
    row = {"path": entry["path"], "source_sha256": entry["sha256"],
           "state": "processed", "reason": "", "stdout": "", "stderr": ""}
    try:
        text = raw.decode("utf-8")
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if request["tool"] == "lizard":
                suffix = Path(entry["path"]).suffix
                alias = str(Path(entry["path"]).with_suffix(".js")) if suffix in (".mjs", ".cjs") else entry["path"]
                reader = readers.get(suffix)
                if reader is None or get_reader_for(alias) is not reader:
                    raise ValueError("No qualified explicit lizard reader")
                row.update(alias=alias, reader=reader.__name__, functions=[])
                # Inspect the actual reader's comments, not string literals.
                lexer = reader(lizard.FileInfoBuilder(alias))
                comments = [lexer.get_comment_from_token(token) for token in lexer.generate_tokens(text)]
                if any(comment is not None and ("GENERATED CODE" in comment or
                       comment.strip().startswith("#lizard forgive")) for comment in comments):
                    raise ValueError("Lizard suppression directive")
                info = analyzer.analyze_source_code(alias, text)
                row["functions"] = [
                    {"name": f.name, "long_name": f.long_name, "start_line": f.start_line,
                     "end_line": f.end_line, "cyclomatic_complexity": f.cyclomatic_complexity,
                     "forgiven_metrics": sorted(f.forgiven_metrics)} for f in info.function_list]
                if any(f["forgiven_metrics"] for f in row["functions"]):
                    raise ValueError("Lizard suppressed function metrics")
            elif request["tool"] == "vulture":
                before = int(scanner.exit_code)
                scanner.scan(text, filename=entry["path"])
                row.update(before=before, after=int(scanner.exit_code))
                if scanner.exit_code != 0:
                    raise ValueError("Vulture scan failed before reporting")
            else:
                raise ValueError("Unknown scalar source tool")
        if out.getvalue() or err.getvalue():
            raise ValueError("Scalar analyzer emitted diagnostics")
    except (ValueError, SyntaxError, IndexError, RecursionError) as error:
        row.update(state="failed", reason=type(error).__name__ + ": " + str(error))
    row.update(stdout=out.getvalue(), stderr=err.getvalue())
    rows.append(row)
    print("Consumed scalar source: " + request["tool"] + " " + entry["path"], flush=True)
findings = []
if request["tool"] == "vulture" and all(row["state"] == "processed" for row in rows):
    # Match scavenge's built-in resource heuristics without recursive discovery.
    for name in sorted({item.name for item in scanner.defined_imports}):
        relative = "whitelists/" + name + "_whitelist.py"
        resource = Path(source["roots"]["vulture"]) / "vulture" / relative
        if not resource.is_file():
            continue
        filename, digest = checked(resource)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            scanner.scan(resource.read_bytes().decode("utf-8"), filename=relative)
        resources.append({"path": filename, "sha256": digest,
                          "stdout": out.getvalue(), "stderr": err.getvalue(),
                          "exit_code": int(scanner.exit_code)})
        if out.getvalue() or err.getvalue() or scanner.exit_code != 0:
            raise ValueError("Vulture built-in resource failed")
if request["tool"] == "vulture":
    findings = [{field: str(getattr(item, field)) if field == "filename" else getattr(item, field)
                 for field in vulture.core.Item.__slots__}
                for item in scanner.get_unused_code(min_confidence=80)]
imports = []
for name, module in sorted(sys.modules.items()):
    filename = getattr(module, "__file__", None)
    if filename:
        path, digest = checked(filename)
        imports.append({"module": name, "path": path, "sha256": digest})
payload = {"tool": request["tool"], "files": rows, "findings": findings,
           "resources_read": resources, "imports": imports, "versions": versions}
with Path(request["result_path"]).open("x", encoding="utf-8") as stream:
    json.dump(payload, stream, ensure_ascii=True)
'''


def _source_command(context, parsed, tool, binding, directory):
    """Execute one qualified source batch; binding is rehashed by the composition owner."""
    inv = parsed["inventory"]
    if ([entry["path"] for entry in inv["entries"]] !=
            [receipt["path"] for receipt in parsed["receipts"]]):
        raise ValueError("Scalar parse receipt partition differs from inventory")
    files = [entry for entry, receipt in zip(inv["entries"], parsed["receipts"], strict=True)
             if receipt["state"] == "processed" and
             (entry["language"] == "python" or tool == "lizard" and
              entry["suffix"] in {".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx"})]
    request = {"tool": tool, "source": binding["source"], "files": files,
               "root": context[inv["revision"] + "_root"],
               "result_path": str(directory / "result.json")}
    request_path = directory / "request.json"
    with request_path.open("xb") as stream:
        stream.write(json.dumps(request, ensure_ascii=True).encode("utf-8"))
    argv = [binding["executable"]["path"], "-I", "-S", "-B", "-c", SOURCE_WORKER, str(request_path)]
    env, removed = _environment()
    rc, stdout, stderr = run_capture(argv, cwd=request["root"], env=env, idle=120, max_total=900)
    result = (graph.load_json((directory / "result.json").read_bytes())
              if (directory / "result.json").is_file() else None)
    return {"request": request, "argv": argv, "cwd": request["root"],
            "idle_seconds": 120, "max_seconds": 900,
            "environment_delta": {"removed_names": removed},
            "returncode": rc, "stdout": stdout, "stderr": stderr, "result": result}


def _native_command(tool, executable, sources, directory, *, census=False, rules=None):
    """Stage exact bytes away from ambient configuration and implicit directory scanning."""
    stage = directory / "inputs"
    stage.mkdir()
    paths = []
    for name, content in sorted(sources.items()):
        path = graph.input_path(stage, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
        paths.append(str(path))
    if not paths:
        raise ValueError("Empty native input list must not trigger directory discovery")
    if tool == "jscpd":
        config = directory / "jscpd.json"
        with config.open("x", encoding="utf-8") as stream:
            json.dump({"minTokens": 1 if census else 40, "minLines": 1 if census else 5,
                       "mode": "mild", "reporters": ["json"], "noGitignore": True}, stream)
        argv = [executable, "--config", str(config), "--min-tokens", "1" if census else "40",
                "--min-lines", "1" if census else "5", "--mode", "mild", "--reporters", "json",
                "--summary", "--summary-top", str(max(1, len(paths))), "--no-gitignore",
                "--no-colors", "--no-tips", "--workers", "1", "--absolute",
                "--max-size", "18446744073709551615", "--formats-exts",
                "javascript:js,mjs,cjs;typescript:ts;tsx:tsx;jsx:jsx",
                "--output", str(directory / "report"), *paths]
    elif tool == "ruff":
        if not rules or len(rules) != len(set(rules)):
            raise ValueError("Ruff requires the exact resolved rule list")
        argv = [executable, "check", "--isolated", "--no-cache", "--no-fix", "--no-preview",
                "--no-respect-gitignore", "--no-force-exclude", "--target-version", "py314",
                "--select", ",".join(rules), "--output-format", "json", *paths]
    else:
        raise ValueError("Unknown native scalar tool")
    env, removed = _environment()
    rc, stdout, stderr = run_capture(argv, cwd=directory, env=env, idle=120, max_total=900)
    result = None
    decode_error = None
    try:
        if tool == "ruff" and rc in (0, 1):
            result = graph.load_json(stdout)
        elif tool == "jscpd" and (directory / "report/jscpd-report.json").is_file():
            result = graph.load_json((directory / "report/jscpd-report.json").read_bytes())
    except ValueError as error:
        decode_error = str(error)
    for name, content in sources.items():
        if graph.input_path(stage, name).read_bytes() != content:
            raise ValueError("Scalar tool modified staged input")
    return {"argv": argv, "cwd": str(directory), "idle_seconds": 120, "max_seconds": 900,
            "environment_delta": {"removed_names": removed}, "returncode": rc,
            "stdout": stdout, "stderr": stderr, "result": result, "decode_error": decode_error}


def _reported_path(value, stage, sources):
    if not isinstance(value, str):
        raise ValueError("Invalid analyzer source path")
    path = Path(value.removeprefix("\\\\?\\"))
    if not path.is_absolute() or not path.is_relative_to(stage):
        raise ValueError("Analyzer path outside exact stage")
    name = path.relative_to(stage).as_posix()
    if name not in sources or graph.input_path(stage, name) != path:
        raise ValueError("Analyzer path absent from inventory")
    return name


def _jscpd_payload(sources, clones, census, clone_stage, census_stage):
    files = {}
    for row in census["summary"]["files"]:
        name = _reported_path(row["path"], census_stage, sources)
        if name in files or _count(row["bytes"]) != len(sources[name]):
            raise ValueError("Duplicate or byte-mismatched analyzer census")
        _count(row["tokens"], 1)
        files[name] = {"path": name, "source_sha256": hashlib.sha256(sources[name]).hexdigest(),
                       "source_lines": _count(row["lines"]), "processed": True}
    if _count(census["summary"]["totalFiles"]) != len(files):
        raise ValueError("Truncated analyzer census")
    for name, content in sources.items():
        if name not in files:
            # Nonempty/comment-only omissions need shared zero-token proof at
            # composition; this decoder never invents a successful scan.
            if content:
                raise ValueError("Nonempty source omitted by analyzer census: " + name)
            files[name] = {"path": name, "source_sha256": hashlib.sha256(content).hexdigest(),
                           "source_lines": 0, "processed": True}
    locations = []
    for clone in clones["duplicates"]:
        if clone["kind"] != "exact":
            raise ValueError("Unexpected nonexact clone")
        pair = []
        for field in ("firstFile", "secondFile"):
            row = clone[field]
            name = _reported_path(row["name"], clone_stage, sources)
            pair.append({"path": name, "start_line": _count(row["start"], 1),
                         "end_line": _count(row["end"], 1)})
        locations.append({"locations": pair})
    payload = {"files": [files[name] for name in sorted(files)], "clones": locations}
    duplication_value(payload)
    return payload


def _complexity_payload(sources, output):
    files = []
    for row in output["files"]:
        name = row["path"]
        if name not in sources or row["source_sha256"] != hashlib.sha256(sources[name]).hexdigest():
            raise ValueError("Lizard source binding mismatch")
        functions = []
        diagnostics = [value for value in (row["reason"], row["stdout"], row["stderr"]) if value]
        if row["state"] == "processed":
            for ordinal, function in enumerate(row["functions"]):
                if function["forgiven_metrics"]:
                    raise ValueError("Suppressed complexity cannot be accepted")
                span = _line_span(sources[name], function["start_line"], function["end_line"])
                functions.append({"id": graph.digest([name, function["long_name"], span, ordinal]),
                                  "span": span,
                                  "cyclomatic_complexity": _count(function["cyclomatic_complexity"], 1)})
        files.append({"path": name, "source_sha256": row["source_sha256"],
                      "functions": functions, "diagnostics": diagnostics})
    if sorted(item["path"] for item in files) != sorted(sources):
        raise ValueError("Lizard output partition mismatch")
    return {"files": files}


def _finding(rule, path, span, symbol, message, confidence, sources, occurrences):
    content = sources[path]
    # Token text and an occurrence ordinal, not line numbers alone, bind identity.
    snippet = content[span["start_byte"]:span["end_byte"]].decode("utf-8")
    context = " ".join(snippet.split())
    key = (rule, path, symbol or "", context)
    ordinal = occurrences.get(key, 0)
    occurrences[key] = ordinal + 1
    parts = [*key, str(ordinal)]
    return {"id": graph.digest(parts), "rule": rule, "path": path, "span": span,
            "symbol": symbol, "message": message, "confidence": confidence, "identity_parts": parts}


def _vulture_findings(sources, output):
    findings, occurrences = [], {}
    for item in output["findings"]:
        path = Path(item["filename"]).as_posix()
        if path not in sources:
            raise ValueError("Vulture finding outside explicit Python inputs")
        confidence = _count(item["confidence"], 80)
        if confidence > 100:
            raise ValueError("Invalid Vulture confidence")
        span = _line_span(sources[path], item["first_lineno"], item["last_lineno"])
        findings.append(_finding("VULTURE-" + item["typ"], path, span, item["name"],
                                 item["message"], confidence, sources, occurrences))
    return sorted(findings, key=lambda finding: finding["id"])


def _ruff_findings(sources, output, stage, rules):
    findings, occurrences = [], {}
    for item in output:
        code = item["code"]
        if code not in rules and code != "invalid-syntax":
            raise ValueError("Unqualified Ruff rule")
        path = _reported_path(item["filename"], stage, sources)
        span = source_span(sources[path], item["location"]["row"], item["location"]["column"],
                           item["end_location"]["row"], item["end_location"]["column"])
        findings.append(_finding("RUFF-" + code, path, span, None, item["message"], None,
                                 sources, occurrences))
    return sorted(findings, key=lambda finding: finding["id"])


def _python_directives(sources):
    diagnostics = []
    for path, content in sorted(sources.items()):
        if not path.endswith(".py"):
            continue
        for token in tokenize.tokenize(io.BytesIO(content).readline):
            if token.type == tokenize.COMMENT and any(
                    marker in token.string.lower() for marker in ("noqa", "ruff:", "lizard")):
                diagnostics.append(path + ":" + str(token.start[0]) + ": " + token.string)
    return diagnostics
