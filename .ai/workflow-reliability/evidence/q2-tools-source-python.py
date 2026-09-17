"""Isolated, source-bound qualification bootstrap; no ambient package paths."""
import ast
import contextlib
import hashlib
import importlib
import importlib.metadata
import inspect
import io
import json
from pathlib import Path
import runpy
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOTS = json.loads((HERE / "q2-tools-source-roots.json").read_text())
EXTERNAL = Path(ROOTS["lizard"]).parents[1]
SOURCE_ROOTS = [Path(ROOTS[n]).resolve() for n in ("lizard", "vulture", "pygments", "pathspec")]
BASE = Path(sys.base_prefix).resolve()
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
assert all(Path(p).resolve().is_relative_to(BASE) for p in sys.path)
sys.path[:0] = [str(p) for p in SOURCE_ROOTS]
for stream in (sys.stdout, sys.stderr):
    stream.reconfigure(encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    path = HERE / ("q2-tools-source-" + name + ".json")
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def provenance(label):
    distributions = list(importlib.metadata.distributions())
    assert not distributions, "Ambient plugin/distribution discovery"
    records = []
    for name, module in sorted(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if not filename:
            continue
        path = Path(filename).resolve()
        if path == Path(__file__).resolve():
            role = "qualification-bootstrap"
        elif any(path.is_relative_to(root) for root in SOURCE_ROOTS):
            role = "approved-source"
        elif path.is_relative_to(BASE) and "site-packages" not in path.parts:
            role = "managed-runtime"
        else:
            raise AssertionError("Unexpected imported module: " + name + " " + str(path))
        records.append({"module": name, "path": str(path), "role": role,
                        "sha256": sha(path) if path.is_file() else None})
    save("python-provenance-" + label, {"argv": sys.argv, "executable": sys.executable,
         "version": sys.version, "sys_path": sys.path, "isolated": sys.flags.isolated,
         "no_site": sys.flags.no_site, "no_bytecode": sys.dont_write_bytecode,
         "imported_files": records, "installed_distributions": []})


def dependencies():
    import lizard
    import pygments
    import pathspec
    from pathspec._backends import agg
    from pygments import plugin
    import vulture
    assert lizard.version == "1.24.0"
    assert pygments.__version__ == "2.21.0"
    assert pathspec.__version__ == "1.1.1"
    assert vulture.__version__ == "2.16"
    assert agg._BEST_BACKEND == "simple"
    assert list(plugin.iter_entry_points(plugin.LEXER_ENTRY_POINT)) == []
    absent = ("re2", "hyperscan", "typing_extensions", "colorama", "jinja2", "tomli")
    assert all(importlib.util.find_spec(name) is None for name in absent)
    assert pathspec.PathSpec.from_lines("gitwildmatch", ["*.py"]).match_file("example.py")
    return {"lizard": lizard.version, "vulture": vulture.__version__,
            "pygments": pygments.__version__, "pathspec": pathspec.__version__,
            "pathspec_backend": agg._BEST_BACKEND, "pygments_lexer_plugins": [],
            "optional_modules_confirmed_absent": absent}


def cli(tool, args):
    dependencies()
    sys.argv = [tool, *args]
    runpy.run_module(tool, run_name="__main__", alter_sys=True)


def fixture(directory, name, text):
    path = directory / name
    with path.open("xb") as stream:
        stream.write(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    return path


def lizard():
    deps = dependencies()
    import lizard as api
    from lizard_languages import get_reader_for
    directory = EXTERNAL / "lizard fixtures with spaces"
    directory.mkdir()
    analyzer = api.FileAnalyzer(api.get_extensions([]))
    rows = []
    expectations = []
    py = ("# caf\u00e9 \U0001f600\n"
          "def branch(value):\n    if value > 0:\n        return value + 1\n    return value - 1\n")
    js = "// caf\u00e9 \U0001f600\nfunction branch(value) {\n if (value > 0) return value + 1;\n return value - 1;\n}\n"

    def analyze(path, alias=None, file_api=False):
        out, err = io.StringIO(), io.StringIO()
        name = str(alias or path)
        reader = get_reader_for(name)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            info = analyzer(str(path)) if file_api else analyzer.analyze_source_code(
                name, path.read_bytes().decode("utf-8"))
        functions = [{**vars(f), "forgiven_metrics": sorted(f.forgiven_metrics),
                      "parameter_count": f.parameter_count, "length": f.length} for f in info.function_list]
        row = {"path": str(path), "source_sha256": sha(path) if path.exists() else None,
               "input_alias": name, "reader": reader.__name__ if reader else None,
               "file_info": {"filename": info.filename, "nloc": info.nloc, "token_count": info.token_count,
                             "functions": functions},
               "stdout": out.getvalue(), "stderr": err.getvalue(), "file_api": file_api}
        rows.append(row)
        return row

    for suffix in (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"):
        typed = suffix in (".ts", ".tsx")
        code = py if suffix == ".py" else js.replace("branch(value)", "branch(value: number)") if typed else js
        path = fixture(directory, "branch caf\u00e9" + suffix, code)
        alias = path.with_suffix(".js") if suffix in (".mjs", ".cjs") else None
        row = analyze(path, alias)
        expectations.append(len(row["file_info"]["functions"]) == 1
                            and row["file_info"]["functions"][0]["cyclomatic_complexity"] == 2
                            and not row["stderr"] and row["reader"] is not None)
        if alias:
            native = analyze(path)
            expectations.append(native["reader"] == "JavaScriptReader"
                                and native["file_info"]["functions"][0]["cyclomatic_complexity"] == 2)
        for kind, text in (("empty", ""), ("comments", "# comment\n" if suffix == ".py" else "// comment\n"),
                           ("functionless", "value = 17\n" if suffix == ".py" else "const value = 17;\n")):
            zero = analyze(fixture(directory, kind + suffix, text))
            expectations.append(zero["file_info"]["functions"] == [] and not zero["stderr"])
        shape = ("async def outer(value):\n"
                 "    def inner(item):\n        return item if item > 0 else -item\n"
                 "    return inner(value)\n" if suffix == ".py" else
                 ("const outer = async (value: number) => {\n" if typed else "const outer = async (value) => {\n")
                 + " function inner(item) { return item > 0 ? item : -item; }\n"
                 + " const pattern = /a[b-c]+/;\n const text = `value ${inner(value)}`;\n"
                 + " return pattern.test(text) && value / 2 > 1 ? text : 'none';\n};\n"
                 + ("const view = <section onClick={() => outer(1)}>ok</section>;\n" if suffix in (".tsx", ".jsx") else ""))
        shaped = analyze(fixture(directory, "nested arrow async" + suffix, shape))
        expectations.append(len(shaped["file_info"]["functions"]) >= 2 and not shaped["stderr"])
    unknown = analyze(fixture(directory, "unknown.unsupported", js))
    expectations.append(unknown["reader"] is None)
    missing = analyze(directory / "absent.py", file_api=True)
    expectations.append(bool(missing["stderr"]) and missing["file_info"]["functions"] == [])
    invalid = directory / "invalid utf8.py"
    invalid.write_bytes(b"\xff\xfe\xff")
    decode = analyze(invalid, file_api=True)
    expectations.append(bool(decode["stderr"]))
    malformed_path = fixture(directory, "invalid syntax.py", "def broken(:\n  return 1\n")
    malformed = analyze(malformed_path)
    try:
        ast.parse(malformed_path.read_bytes())
    except SyntaxError as exc:
        malformed["independent_syntax_error"] = str(exc)
    expectations.append("independent_syntax_error" in malformed)
    generated = analyze(fixture(directory, "generated.py", "# GENERATED CODE\n" + py))
    suppressed = analyze(fixture(directory, "forgiven.py", "#lizard forgive\n" + py))
    expectations.append(generated["file_info"]["functions"] == [])
    suppressed["directive_requires_rejection"] = True
    stress = fixture(directory, "deep recursion.js", "function nested() {\n" * 1200 + "return 1;\n" + "}\n" * 1200)
    recursion = analyze(stress)
    expectations.append("RecursionError" in recursion["stderr"])
    expectations.append(all(sha(r["path"]) == r["source_sha256"] for r in rows if r["source_sha256"]))
    result = {"dependencies": deps, "api": "FileAnalyzer(get_extensions([])).analyze_source_code",
              "processors": [p.__name__ for p in analyzer.processors], "rows": rows,
              "assertions": expectations, "zero_files": {"explicit_input_count": 0, "calls": 0},
              "limits": ["Lexical cyclomatic model, not syntax validation or cognitive complexity",
                         "Reject missing reader, error diagnostics, GENERATED CODE/forgive; syntax parser precedes analyzer",
                         "Use successful explicit per-file calls for census, never function-list count",
                         "mjs/cjs aliases are memory-only; native mappings tested separately"]}
    save("lizard-results", result)
    print(json.dumps({"tool": "lizard", "cases": len(rows), "checks": len(expectations),
                      "failed_checks": [i for i, passed in enumerate(expectations) if not passed],
                      "recursion_stderr": recursion["stderr"]}))
    assert all(expectations)


def vulture():
    deps = dependencies()
    from vulture.core import Vulture, Item
    from vulture.utils import ExitCode
    import pkgutil
    directory = EXTERNAL / "vulture fixtures with spaces"
    directory.mkdir()
    rows, expectations = [], []
    specifications = {
        "positive caf\u00e9.py": "# caf\u00e9 \U0001f600\nimport os\ndef calculate(value):\n    return value\n    print('unreachable')\n",
        "negative.py": "import math\ndef calculate(value):\n    return math.sqrt(value)\nprint(calculate(4))\n",
        "empty.py": "",
        "comments.py": "# caf\u00e9 \U0001f600\n",
        "functionless.py": "value = 1\nprint(value)\n",
        "nested async.py": "async def outer(value):\n    def inner(item):\n        return item\n        print('unreachable')\n    return inner(value)\nprint(outer)\n",
        "template314.py": "value = 'caf\u00e9'\ntemplate = t'hello {value}'\nprint(template)\n",
        "noqa.py": "import os  # noqa: V104\n",
        "reflection.py": "def dynamic_target():\n    return 1\nname = 'dynamic_' + 'target'\nglobals()[name]()\n",
        "whitelist.py": "import collections\nprint(collections)\n",
        "invalid syntax.py": "def broken(:\n  return 1\n",
        "invalid nul.py": "value = \x00\n",
    }
    paths = {name: fixture(directory, name, text) for name, text in specifications.items()}

    def items(scanner, confidence):
        return [{**{field: str(getattr(item, field)) if field == "filename" else getattr(item, field)
                    for field in Item.__slots__}, "size": item.size}
                for item in scanner.get_unused_code(min_confidence=confidence)]

    def scan(name, selected, scavenge=False):
        scanner = Vulture()
        out, err = io.StringIO(), io.StringIO()
        receipts = []
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if scavenge:
                try:
                    scanner.scavenge([str(p) for p in selected])
                except SystemExit as exc:
                    row = {"case": name, "api": "scavenge", "inputs": [str(p) for p in selected],
                           "system_exit": exc.code, "stdout": out.getvalue(), "stderr": err.getvalue(),
                           "classification": "infrastructure-error; no successful census"}
                    rows.append(row)
                    return row
            else:
                for path in selected:
                    before = scanner.exit_code
                    scanner.scan(path.read_bytes().decode("utf-8"), filename=str(path))
                    receipts.append({"path": str(path), "sha256": sha(path), "before": int(before),
                                     "after": int(scanner.exit_code)})
            pre_report = scanner.exit_code
            findings = items(scanner, 80)
            all_findings = items(scanner, 0)
            returned = scanner.report(min_confidence=80)
        row = {"case": name, "api": "scavenge" if scavenge else "scan",
               "inputs": [str(p) for p in selected], "receipts": receipts,
               "findings80": findings, "all_confidences": all_findings,
               "pre_report_exit": int(pre_report), "report_return": int(returned),
               "post_report_exit": int(scanner.exit_code), "stdout": out.getvalue(), "stderr": err.getvalue()}
        rows.append(row)
        return row

    for name, path in paths.items():
        row = scan(name, [path])
        if name in ("positive caf\u00e9.py", "nested async.py"):
            expectations.append(len(row["findings80"]) >= (2 if name.startswith("positive") else 1))
        elif name.startswith("invalid"):
            expectations.append(row["pre_report_exit"] == int(ExitCode.InvalidInput) and bool(row["stderr"]))
        else:
            expectations.append(row["pre_report_exit"] == int(ExitCode.NoDeadCode))
        if name in ("negative.py", "empty.py", "comments.py", "functionless.py", "template314.py", "noqa.py"):
            expectations.append(row["findings80"] == [] and not row["stderr"])
    empty = scan("zero files", [])
    expectations.append(empty["findings80"] == [] and empty["inputs"] == [])
    mixed = scan("invalid plus positive", [paths["invalid syntax.py"], paths["positive caf\u00e9.py"]])
    expectations.append(mixed["pre_report_exit"] == int(ExitCode.InvalidInput)
                        and mixed["post_report_exit"] == int(ExitCode.DeadCode) and bool(mixed["stderr"]))
    whitelist = scan("resource scavenge", [paths["whitelist.py"]], scavenge=True)
    resource = pkgutil.get_data("vulture", "whitelists/collections_whitelist.py")
    expectations.append(resource is not None and not whitelist["stderr"])
    bad_bytes = directory / "bad encoding.py"
    bad_bytes.write_bytes(b"\xff\xfe\xff")
    bad = scan("invalid encoding", [bad_bytes], scavenge=True)
    expectations.append(bad["pre_report_exit"] == int(ExitCode.InvalidInput) and bool(bad["stderr"]))
    missing = scan("missing", [directory / "missing.py"], scavenge=True)
    expectations.append("could not be found" in missing["system_exit"])
    snapshots = [{"path": str(p), "sha256": sha(p)} for p in paths.values()]
    save("vulture-results", {"dependencies": deps, "rows": rows, "assertions": expectations,
         "files": snapshots, "whitelist_resource_sha256": hashlib.sha256(resource).hexdigest(),
         "item_slots": list(Item.__slots__), "exit_codes": {name: int(value) for name, value in ExitCode.__members__.items()},
         "limits": ["confidence80 explicit, static model only; unreferenced function confidence60 is excluded",
                    "report overwrites invalid-input status with DeadCode; retain pre-report diagnostics/status",
                    "scan returns None; explicit successful scan receipts provide census, not findings count",
                    "noqa affects findings; retain directive inventory; no dynamic target resolution"]})
    print(json.dumps({"tool": "vulture", "cases": len(rows), "checks": len(expectations),
                      "positive_count": len(rows[0]["findings80"]),
                      "failed_checks": [i for i, passed in enumerate(expectations) if not passed]}))
    assert all(expectations)


if __name__ == "__main__":
    mode, *args = sys.argv[1:]
    label = "-".join([mode, *args]).replace("--", "")
    try:
        globals()[mode](*args) if mode != "cli" else cli(args[0], args[1:])
    finally:
        provenance(label)
