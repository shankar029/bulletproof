"""Narrow follow-up: qualify strict text API without unsafe file auto-decoding."""
import contextlib
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
bootstrap = HERE / "q2-tools-source-python.py"
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
namespace = runpy.run_path(str(bootstrap), run_name="qualification_bootstrap")
namespace["dependencies"]()
roots = namespace["SOURCE_ROOTS"]
external = namespace["EXTERNAL"]
directory = external / "lizard fixtures with spaces"
old = json.loads((HERE / "q2-tools-source-lizard-results.json").read_text())
assert [i for i, passed in enumerate(old["assertions"]) if not passed] == [39]
invalid = directory / "invalid utf8.py"
raw = invalid.read_bytes()
try:
    raw.decode("utf-8")
except UnicodeDecodeError as exc:
    strict_failure = {"type": type(exc).__name__, "message": str(exc), "start": exc.start, "end": exc.end}
else:
    raise AssertionError("Invalid UTF-8 must not enter the text API")
import lizard
from lizard_languages import get_reader_for
analyzer = lizard.FileAnalyzer(lizard.get_extensions([]))
good = directory / "branch caf\u00e9.py"
before = hashlib.sha256(good.read_bytes()).hexdigest()
code = good.read_bytes().decode("utf-8")
out, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    good_info = analyzer.analyze_source_code(str(good), code)
assert len(good_info.function_list) == 1 and good_info.function_list[0].cyclomatic_complexity == 2
assert not out.getvalue() and not err.getvalue()
assert before == hashlib.sha256(good.read_bytes()).hexdigest()
assert get_reader_for("input.unsupported") is None
assert old["rows"][-1]["stderr"].find("RecursionError") >= 0
assert list(importlib.metadata.distributions()) == []
loaded = []
base = Path(sys.base_prefix).resolve()
for name, module in sorted(sys.modules.items()):
    filename = getattr(module, "__file__", None)
    if not filename:
        continue
    path = Path(filename).resolve()
    approved = path == Path(__file__).resolve() or any(path.is_relative_to(root) for root in roots)
    standard = path.is_relative_to(base) and "site-packages" not in path.parts
    assert approved or standard, "Unexpected imported dependency: " + name
    loaded.append({"module": name, "path": str(path),
                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None})
result = {
    "original_result": {"path": str(HERE / "q2-tools-source-lizard-results.json"),
                       "sha256": hashlib.sha256((HERE / "q2-tools-source-lizard-results.json").read_bytes()).hexdigest()},
    "reconciled_failure": {"original_index": 39,
        "original_assumption": "The file API emits a UnicodeDecodeError diagnostic",
        "observed": "auto_read retries utf8 with errors=ignore; empty stderr is not success proof",
        "selected_api": "FileAnalyzer.analyze_source_code with strict decoded input; file __call__ not qualified",
        "strict_decode_rejection": strict_failure,
        "raw_sha256": hashlib.sha256(raw).hexdigest()},
    "valid_text_control": {"path": str(good), "sha256": before, "functions": 1, "complexity": 2,
                           "stderr": err.getvalue(), "stdout": out.getvalue()},
    "all_other_original_assertions_passed": True,
    "actual_imports": loaded, "isolated": True, "ambient_distributions": [],
    "status": "QUALIFIED for selected strict text API only; unsafe convenience file API excluded",
    "production_changes": False,
}
target = HERE / "q2-tools-source-lizard-boundaries-results.json"
with target.open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2)
print(json.dumps({"strict_decode": "REJECTED before lizard", "valid_text_functions": 1,
                  "previous_cases": len(old["rows"]), "status": result["status"]}))
