"""Owned CHECK-TOOLS evidence harness; not a production measurement adapter."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).parent
PYTHON = Path(r"C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe")
RUNNER = REPO / "scripts" / "run.py"
ARTIFACTS = Path(r"C:\Users\shbs\.copilot\session-state\c154cbfc-3b1d-4163-b8dd-5f0b43af3095\files")
OWNED = ARTIFACTS / "q2-tools-20260917"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def save(name, value):
    path = EVIDENCE / ("q2-tools-" + name + ".json")
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(name, argv, cwd=None, install=False):
    cwd = Path(cwd or OWNED)
    wrapper = [str(PYTHON), "-B", str(RUNNER), "--idle", "120" if install else "30",
               "--max", "1200" if install else "90", "--", *map(str, argv)]
    result = subprocess.run(wrapper, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=os.environ.copy())
    captures = {}
    for stream in ("stdout", "stderr"):
        content = getattr(result, stream)
        path = EVIDENCE / ("q2-tools-" + name + "." + stream + ".log")
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(content)
        captures[stream] = {"path": str(path), "sha256": sha(path), "bytes": len(content)}
    record = {"argv": list(map(str, argv)), "wrapper_argv": wrapper, "cwd": str(cwd),
              "exit": result.returncode, "captures": captures,
              "capture_semantics": "Raw wrapper bytes; run.py CLI merges child stderr into stdout and normalizes newlines",
              "environment_delta": {"PYTHONDONTWRITEBYTECODE": "1"}}
    save(name, record)
    print(name, result.returncode, result.stdout.decode("utf-8", "replace")[:160], flush=True)
    return result


def metadata(name, url):
    request = urllib.request.Request(url, headers={"User-Agent": "Q2-tool-qualification"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
    except Exception as error:
        save(name + "-urllib-failure", {"url": url, "error": str(error)})
        curl = shutil.which("curl.exe")
        destination = OWNED / (name + ".json")
        result = command(name + "-curl", [curl, "--fail", "--location", "--silent", "--show-error",
                                          "--max-time", "60", "--output", destination, url])
        if result.returncode:
            return None
        body = destination.read_bytes()
    value = json.loads(body)
    if "info" in value and "urls" in value:
        selected = {"info": {k: value["info"].get(k) for k in
                            ("name", "version", "license", "license_expression", "requires_dist", "requires_python", "project_urls")},
                    "urls": [{k: item.get(k) for k in ("filename", "url", "digests", "yanked", "upload_time_iso_8601")}
                             for item in value["urls"]]}
    elif "assets" in value:
        selected = {k: value.get(k) for k in ("tag_name", "html_url", "published_at", "draft", "prerelease")}
        selected["assets"] = [{k: item.get(k) for k in ("name", "browser_download_url", "digest", "size")}
                              for item in value["assets"]]
    else:
        selected = {k: value.get(k) for k in ("name", "version", "license", "main", "engines", "dependencies",
                                             "optionalDependencies", "bin", "dist")}
    save(name, {"url": url, "response_sha256": hashlib.sha256(body).hexdigest(), "selected_metadata": selected})
    print(name, "metadata received", flush=True)
    return value


def upstream():
    metadata("metadata-typescript", "https://registry.npmjs.org/typescript/5.9.3")
    metadata("metadata-lizard", "https://pypi.org/pypi/lizard/1.24.0/json")
    metadata("metadata-vulture", "https://pypi.org/pypi/vulture/2.16/json")
    metadata("metadata-ruff", "https://pypi.org/pypi/ruff/json")
    metadata("metadata-jscpd", "https://api.github.com/repos/kucherenko/jscpd/releases/latest")


def download(name, url, filename, expected=None):
    os.chdir(OWNED)
    path = Path(filename)
    if path.exists():
        raise FileExistsError(path)
    request = urllib.request.Request(url, headers={"User-Agent": "Q2-tool-qualification"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            path.write_bytes(response.read())
    except Exception as error:
        save(name + "-urllib-failure", {"url": url, "error": str(error)})
        result = command(name + "-curl", [shutil.which("curl.exe"), "--fail", "--location", "--silent",
                                          "--show-error", "--max-time", "60", "--output", path.resolve(), url])
        if result.returncode:
            return None
    actual = sha(path)
    save(name, {"url": url, "path": str(path.resolve()), "sha256": actual,
                "expected_sha256": expected, "bytes": path.stat().st_size})
    if expected and actual != expected:
        raise ValueError("Digest mismatch")
    print(name, actual, flush=True)
    return path.resolve()


def provision():
    os.chdir(OWNED)
    Path("scratch").mkdir(exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = str(OWNED / "scratch")
    packages = []
    for name in ("pygments", "pathspec"):
        if not (EVIDENCE / ("q2-tools-metadata-" + name + ".json")).exists():
            value = metadata("metadata-" + name, "https://pypi.org/pypi/" + name + "/json")
            assert value
    for name in ("lizard", "vulture", "ruff", "pygments", "pathspec"):
        value = json.loads((EVIDENCE / ("q2-tools-metadata-" + name + ".json")).read_text())["selected_metadata"]
        wheels = [v for v in value["urls"] if v["filename"].endswith(".whl") and not v["yanked"]
                  and ("none-any" in v["filename"] or "win_amd64" in v["filename"])]
        assert len(wheels) == 1, wheels
        wheel = wheels[0]
        packages.append(download("download-" + name, wheel["url"], wheel["filename"], wheel["digests"]["sha256"]))
    if all(packages):
        command("venv-create", [PYTHON, "-B", "-m", "venv", "--without-pip", OWNED / "venv"], install=True)
        uv = json.loads((EVIDENCE / "q2-tools-locations.json").read_text())["path_candidates"]["uv"]
        result = command("venv-install", [uv, "--no-config", "--offline", "--cache-dir", OWNED / "uv-cache",
                          "pip", "install", "--python", OWNED / "venv" / "Scripts" / "python.exe",
                          "--no-python-downloads", "--no-index", "--no-deps", "--no-build", *packages], install=True)
        assert result.returncode == 0
    release = json.loads((EVIDENCE / "q2-tools-metadata-jscpd.json").read_text())["selected_metadata"]
    assert release["tag_name"] == "v5.2.1" and not release["draft"] and not release["prerelease"]
    asset = next(a for a in release["assets"] if a["name"] == "jscpd-windows-x64-msvc.tar.gz")
    archive = download("download-jscpd", asset["browser_download_url"], asset["name"], asset["digest"].split(":")[1])
    if archive:
        Path("jscpd").mkdir()
        with tarfile.open(archive) as bundle:
            bundle.extractall("jscpd", filter="data")
    download("jscpd-license", "https://raw.githubusercontent.com/kucherenko/jscpd/v5.2.1/LICENSE", "jscpd-LICENSE")
    for module in (("lizard", "vulture") if all(packages) else ()):
        command(module + "-version", [OWNED / "venv" / "Scripts" / "python.exe", "-B", "-m", module, "--version"])
        command(module + "-help", [OWNED / "venv" / "Scripts" / "python.exe", "-B", "-m", module, "--help"])
    executables = {}
    if all(packages):
        executables["ruff"] = OWNED / "venv" / "Scripts" / "ruff.exe"
    if archive:
        executables["jscpd"] = next((OWNED / "jscpd").rglob("jscpd.exe"))
    save("executables", {key: {"path": str(path), "sha256": sha(path)} for key, path in executables.items()})
    for name, exe in executables.items():
        command(name + "-version", [exe, "--version"])
        command(name + "-help", [exe, "--help"])
    if "jscpd" in executables:
        command("jscpd-list", [executables["jscpd"], "--list"])
    if "ruff" in executables:
        command("ruff-check-help", [executables["ruff"], "check", "--help"])
        command("ruff-rule-help", [executables["ruff"], "rule", "--help"])


def ruff_release():
    release = metadata("metadata-ruff-github", "https://api.github.com/repos/astral-sh/ruff/releases/tags/0.16.8")
    assert release and not release["draft"] and not release["prerelease"]
    asset = next(a for a in release["assets"] if a["name"] == "ruff-x86_64-pc-windows-msvc.zip")
    archive = download("download-ruff-github", asset["browser_download_url"], asset["name"],
                       asset["digest"].split(":")[1])
    if not archive:
        return
    import zipfile
    os.chdir(OWNED)
    Path("ruff-native").mkdir()
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall("ruff-native")
    exe = next((OWNED / "ruff-native").rglob("ruff.exe"))
    save("ruff-executable", {"path": str(exe), "sha256": sha(exe)})
    command("ruff-version", [exe, "--version"])
    command("ruff-help", [exe, "--help"])
    command("ruff-check-help", [exe, "check", "--help"])
    command("ruff-rule-help", [exe, "rule", "--help"])
    download("ruff-license", "https://raw.githubusercontent.com/astral-sh/ruff/0.16.8/LICENSE", "ruff-LICENSE")


def jscpd_fixture():
    os.chdir(OWNED)
    Path("fixtures with spaces").mkdir()
    fixtures = Path("fixtures with spaces")
    paths = []
    js = """// café 😀 CRLF fixture
export function calculation(value) {
  const doubled = value * 2;
  const offset = doubled + 10;
  if (offset > 20) {
    return offset - 3;
  }
  return offset + 7;
}
"""
    py = """# café 😀 CRLF fixture
def calculation(value):
    doubled = value * 2
    offset = doubled + 10
    if offset > 20:
        return offset - 3
    return offset + 7
"""
    for suffix in (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"):
        source = py if suffix == ".py" else js
        if suffix == ".cjs":
            source = source.replace("export function", "function")
        for label, text in (("clone a", source), ("clone b", source),
                            ("short café", "x = 47\n" if suffix == ".py" else "const unique = 47;\n"),
                            ("empty", ""), ("comment", "# only café\n" if suffix == ".py" else "// only café\n")):
            path = fixtures / (label + suffix)
            path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
            paths.append(path.resolve())
    config = Path("jscpd-config.json")
    config.write_text('{"minTokens":40,"minLines":5,"mode":"mild","reporters":["json"],"noGitignore":true}', encoding="utf-8")
    save("jscpd-inputs", {"files": [{"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in paths],
                          "config": {"path": str(config.resolve()), "sha256": sha(config), "bytes": config.read_text()}})
    exe = json.loads((EVIDENCE / "q2-tools-executables.json").read_text())["jscpd"]["path"]
    common = [exe, "--config", config.resolve(), "--min-tokens", "40", "--min-lines", "5", "--mode", "mild",
              "--reporters", "json", "--summary", "--summary-top", "256", "--no-gitignore", "--no-colors",
              "--no-tips", "--formats-exts", "javascript:js,mjs,cjs;typescript:ts;tsx:tsx;jsx:jsx",
              "--workers", "1", "--absolute"]
    command("jscpd-debug", [*common, "--debug", *paths])
    command("jscpd-positive", [*common, "--output", OWNED / "clone report", *paths], install=True)
    command("jscpd-census", [*common, "--min-tokens", "1", "--min-lines", "1",
                            "--output", OWNED / "census report", *paths], install=True)
    for label in ("short café", "empty", "comment"):
        selected = [p for p in paths if p.stem == label]
        command("jscpd-" + label.split()[0], [*common, "--min-tokens", "1", "--min-lines", "1",
                    "--output", OWNED / (label + " report"), *selected], install=True)
    Path("zero input").mkdir()
    command("jscpd-zero", [*common, "--output", OWNED / "zero report", OWNED / "zero input"])
    command("jscpd-missing", [*common, "--output", OWNED / "missing report", OWNED / "absent.py"])
    for directory in OWNED.glob("* report"):
        for path in directory.glob("*.json"):
            save("jscpd-raw-" + directory.name.replace(" ", "-"), {
                "path": str(path), "sha256": sha(path), "raw": json.loads(path.read_bytes())})


def jscpd_census_recovery():
    os.chdir(OWNED)
    exe = json.loads((EVIDENCE / "q2-tools-executables.json").read_text())["jscpd"]["path"]
    paths = [Path(v["path"]) for v in json.loads((EVIDENCE / "q2-tools-jscpd-inputs.json").read_text())["files"]]
    common = [exe, "--config", OWNED / "jscpd-config.json", "--min-tokens", "1", "--min-lines", "1",
              "--mode", "mild", "--reporters", "json", "--summary", "--summary-top", "256",
              "--no-gitignore", "--no-colors", "--no-tips", "--workers", "1", "--absolute",
              "--formats-exts", "javascript:js,mjs,cjs;typescript:ts;tsx:tsx;jsx:jsx"]
    for label, selected in [("census", paths)] + [(label.split()[0], [p for p in paths if p.stem == label])
                                                 for label in ("short café", "empty", "comment")]:
        output = OWNED / (label + " r2 report")
        command("jscpd-" + label + "-r2", [*common, "--output", output, *selected], install=True)
        path = output / "jscpd-report.json"
        if path.exists():
            raw = json.loads(path.read_bytes())
            save("jscpd-raw-" + label + "-r2", {"path": str(path), "sha256": sha(path), "raw": raw})
    overview = {}
    for output in OWNED.glob("* report"):
        path = output / "jscpd-report.json"
        if path.exists():
            raw = json.loads(path.read_bytes())
            overview[output.name] = {"keys": list(raw), "statistics": raw.get("statistics"),
                                     "summary": raw.get("summary"), "clone_count": len(raw.get("duplicates", []))}
    save("jscpd-schema-overview", overview)
    print(json.dumps(overview, ensure_ascii=True)[:1800])


def ruff_settings():
    os.chdir(OWNED)
    Path("ruff fixtures").mkdir()
    fixtures = Path("ruff fixtures")
    cases = {
        "clean café.py": "# UTF-8 café 😀\nvalue = 42\nprint(value)\n",
        "findings.py": "import os\nassert True\n\ndef example(items=[]):\n    return items\n\nif True: print('hello')\n",
        "empty.py": "",
        "comment.py": "# just café\n",
        "syntax.py": "def broken(:\n",
        "py314.py": 'name = "world"\nmessage = t"Hello {name}"\nprint(message)\n',
        "nested.py": "async def outer(value):\n    def inner(item):\n        return item + 1\n    return inner(value)\n",
        "directive.py": "import os  # noqa: F401\n",
    }
    for name, content in cases.items():
        (fixtures / name).write_bytes(content.replace("\n", "\r\n").encode("utf-8"))
    exe = json.loads((EVIDENCE / "q2-tools-ruff-executable.json").read_text())["path"]
    common = [exe, "check", "--isolated", "--no-cache", "--no-fix", "--no-preview",
              "--no-respect-gitignore", "--no-force-exclude", "--target-version", "py314",
              "--select", "E,F,B,S", "--output-format", "json"]
    save("ruff-inputs", {"files": [{"path": str(p.resolve()), "sha256": sha(p)} for p in fixtures.glob("*.py")],
                          "config_argv": common[2:]})
    command("ruff-settings", [*common, "--show-settings", (fixtures / "clean café.py").resolve()])
    for rule in ("E701", "F401", "B006", "S101"):
        command("ruff-rule-" + rule, [exe, "rule", "--isolated", "--output-format", "json", rule])


def ruff_qualify():
    import re
    os.chdir(OWNED)
    exe = json.loads((EVIDENCE / "q2-tools-ruff-executable.json").read_text())["path"]
    settings = (EVIDENCE / "q2-tools-ruff-settings.stdout.log").read_text(encoding="utf-8")
    enabled = settings.split("linter.rules.enabled = [", 1)[1].split("]", 1)[0]
    rules = sorted(re.findall(r"\(([EFBS]\d+)\)", enabled))
    assert len(rules) == len(set(rules)) and len(rules) > 100
    save("ruff-rules", {"rule_ids": rules, "count": len(rules),
                        "selection": "E,F,B,S; no-preview; py314",
                        "settings_sha256": sha(EVIDENCE / "q2-tools-ruff-settings.stdout.log")})
    common = [exe, "check", "--isolated", "--no-cache", "--no-fix", "--no-preview",
              "--no-respect-gitignore", "--no-force-exclude", "--target-version", "py314",
              "--select", ",".join(rules), "--output-format", "json"]
    files = json.loads((EVIDENCE / "q2-tools-ruff-inputs.json").read_text())["files"]
    cases = {}
    for item in files:
        path = Path(item["path"])
        result = command("ruff-case-" + path.stem.split()[0], [*common, path], install=True)
        records = json.loads(result.stdout)
        assert sha(path) == item["sha256"], "Tool edited input"
        cases[path.name] = {"exit": result.returncode, "count": len(records),
                            "codes": [r["code"] for r in records],
                            "record_keys": sorted(records[0]) if records else [],
                            "source_unchanged": True}
    missing = command("ruff-missing", [*common, OWNED / "missing.py"])
    Path("ruff zero").mkdir()
    zero = command("ruff-zero", [*common, OWNED / "ruff zero"])
    command("ruff-files", [*common, "--show-files", *[v["path"] for v in files]])
    command("ruff-settings-exact", [*common, "--show-settings", files[0]["path"]])
    assert cases["clean café.py"]["exit"] == 0 and cases["clean café.py"]["count"] == 0
    assert set(cases["findings.py"]["codes"]) == {"B006", "E701", "F401", "S101"}
    assert cases["syntax.py"]["exit"] == 1 and "invalid-syntax" in cases["syntax.py"]["codes"]
    assert all(cases[name]["count"] == 0 for name in ("empty.py", "comment.py", "py314.py", "nested.py"))
    assert cases["directive.py"]["count"] == 0
    assert missing.returncode == 1 and "E902" in missing.stdout.decode()
    assert zero.returncode == 0
    exact = (EVIDENCE / "q2-tools-ruff-settings-exact.stdout.log").read_text(encoding="utf-8")
    assert sorted(re.findall(r"\(([EFBS]\d+)\)", exact.split("linter.rules.enabled = [", 1)[1].split("]", 1)[0])) == rules
    save("ruff-results", {"cases": cases, "missing": {"exit": missing.returncode, "json": json.loads(missing.stdout)},
                          "zero": {"exit": zero.returncode, "raw": zero.stdout.decode()},
                          "rules": len(rules), "exact_rules_match_family_resolution": True,
                          "cache_directories": [str(p) for p in OWNED.rglob(".ruff_cache")]})


def source_docs():
    download("jscpd-doc", "https://raw.githubusercontent.com/kucherenko/jscpd/v5.2.1/docs/rust.md", "jscpd-rust.md")
    download("typescript-upstream-package", "https://raw.githubusercontent.com/microsoft/TypeScript/v5.9.3/package.json",
             "typescript-package.json")
    for module in ("lizard", "vulture"):
        for arg in ("--version", "--help"):
            command("unavailable-" + module + "-" + arg[2:], [PYTHON, "-B", "-m", module, arg])


def jscpd_source_index():
    url = "https://api.github.com/repos/kucherenko/jscpd/git/trees/v5.2.1?recursive=1"
    with urllib.request.urlopen(url, timeout=45) as response:
        raw = response.read()
    tree = json.loads(raw)
    paths = [v["path"] for v in tree["tree"] if v["path"].endswith(".rs")
             and any(s in v["path"] for s in ("cli", "config", "walker", "summary", "lib.rs"))]
    save("jscpd-source-index", {"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "paths": paths})
    print("\n".join(paths))


def jscpd_source():
    for name, source in {
            "cli": "rust/crates/cpd/src/cli.rs",
            "runner": "rust/crates/cpd/src/lib.rs",
            "walker": "rust/crates/cpd-finder/src/walker.rs",
            "summary": "rust/crates/cpd-core/src/summary.rs"}.items():
        download("jscpd-source-" + name, "https://raw.githubusercontent.com/kucherenko/jscpd/v5.2.1/" + source,
                 "jscpd-" + name + ".rs")


def jscpd_final_cases():
    os.chdir(OWNED)
    exe = json.loads((EVIDENCE / "q2-tools-executables.json").read_text())["jscpd"]["path"]
    Path("jscpd final fixtures").mkdir()
    fixture = Path("jscpd final fixtures")
    common = [exe, "--config", OWNED / "jscpd-config.json", "--min-tokens", "40", "--min-lines", "5",
              "--mode", "mild", "--reporters", "json", "--summary", "--summary-top", "256", "--no-gitignore",
              "--no-colors", "--no-tips", "--workers", "1", "--absolute",
              "--max-size", "18446744073709551615",
              "--formats-exts", "javascript:js,mjs,cjs;typescript:ts;tsx:tsx;jsx:jsx"]
    cases = {}
    sources = []
    for suffix in (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"):
        py = """# café 😀
def calculate(value):
    doubled = value * 2
    offset = doubled + 10
    divisor = offset / 4
    remainder = divisor % 3
    if remainder > 2:
        return remainder - 3
    return offset + 7
"""
        js = """// café 😀
function calculate(value) {
  const doubled = value * 2;
  const offset = doubled + 10;
  const divisor = offset / 4;
  const remainder = divisor % 3;
  if (remainder > 2) {
    return remainder - 3;
  }
  return offset + 7;
}
"""
        text = py if suffix == ".py" else js
        first, second = fixture / ("café first" + suffix), fixture / ("café second" + suffix)
        for path in (first, second):
            path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
            sources.append({"path": str(path.resolve()), "sha256": sha(path)})
        for label, paths in (("no-clone", [first.resolve()]), ("clone", [first.resolve(), second.resolve()])):
            name = label + "-" + suffix[1:]
            output = OWNED / ("final " + name)
            result = command("jscpd-final-" + name, [*common, "--output", output, *paths], install=True)
            assert result.returncode == 0
            path = output / "jscpd-report.json"
            raw = json.loads(path.read_bytes())
            save("jscpd-final-raw-" + name, {"path": str(path), "sha256": sha(path), "raw": raw})
            rows = raw["summary"]["files"]
            assert raw["summary"]["totalFiles"] == len(paths) == len(rows)
            normalized = {Path(row["path"].removeprefix("\\\\?\\")).resolve() for row in rows}
            assert normalized == set(paths)
            assert all(row["tokens"] >= 40 for row in rows)
            assert bool(raw["duplicates"]) == (label == "clone")
            cases[name] = {"files": len(rows), "clones": len(raw["duplicates"]),
                            "source_lines": [row["lines"] for row in rows],
                            "tokens": [row["tokens"] for row in rows],
                            "formats": [row["format"] for row in rows]}
    command("jscpd-final-debug", [*common, "--debug", first.resolve()])
    invalid = fixture / "invalid utf8.py"
    invalid.write_bytes(b"\xff\xfe\xff")
    bad = command("jscpd-invalid-encoding", [*common, "--output", OWNED / "invalid encoding report", invalid.resolve()])
    raw = json.loads((OWNED / "census r2 report" / "jscpd-report.json").read_bytes())
    rows = raw["summary"]["files"]
    inputs = json.loads((EVIDENCE / "q2-tools-jscpd-inputs.json").read_text())["files"]
    nonempty = {v["path"] for v in inputs if v["bytes"]}
    observed = {row["path"].removeprefix("\\\\?\\") for row in rows}
    assert observed == nonempty and len(rows) == raw["summary"]["totalFiles"] == 28
    assert all(sha(v["path"]) == v["sha256"] for v in inputs + sources)
    save("jscpd-results", {"cases": cases, "initial_census": {"input_files": 35, "summary_files": len(rows),
                          "nonempty_inputs_match": True, "omitted_empty": [v["path"] for v in inputs if not v["bytes"]]},
                          "sources": sources, "invalid_encoding_exit": bad.returncode,
                          "all_fixture_hashes_unchanged": True,
                          "max_size": "u64::MAX: representable file metadata length cannot exceed this; not a size exclusion"})


def finish_bindings():
    import platform
    import struct
    os.chdir(OWNED)
    bins = {
        "jscpd": Path(json.loads((EVIDENCE / "q2-tools-executables.json").read_text())["jscpd"]["path"]),
        "ruff": Path(json.loads((EVIDENCE / "q2-tools-ruff-executable.json").read_text())["path"]),
        "python": PYTHON,
        "node": Path(json.loads((EVIDENCE / "q2-tools-locations.json").read_text())["path_candidates"]["node"]),
    }

    def imports(path):
        data = path.read_bytes()
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        assert data[pe:pe + 4] == b"PE\0\0"
        machine, sections = struct.unpack_from("<HH", data, pe + 4)
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        opt = pe + 24
        assert struct.unpack_from("<H", data, opt)[0] == 0x20B
        table = opt + optional_size

        def offset(rva):
            for i in range(sections):
                row = table + i * 40
                size, address, rawsize, rawptr = struct.unpack_from("<IIII", data, row + 8)
                if address <= rva < address + max(size, rawsize):
                    return rawptr + rva - address
            raise ValueError("Unmapped PE RVA")

        directory = struct.unpack_from("<I", data, opt + 112 + 8)[0]
        names = []
        row = offset(directory)
        while any(data[row:row + 20]):
            name = offset(struct.unpack_from("<I", data, row + 12)[0])
            names.append(data[name:data.index(b"\0", name)].decode("ascii"))
            row += 20
        dependencies = []
        for name in sorted(set(names), key=str.casefold):
            candidates = [path.parent / name, Path(os.environ["SystemRoot"]) / "System32" / name]
            actual = next((p for p in candidates if p.is_file()), None)
            dependencies.append({"name": name, "resolved_existing_candidate": str(actual) if actual else None,
                                 "sha256": sha(actual) if actual else None})
        return {"machine": hex(machine), "declared_imports": dependencies,
                "limit": "PE import table and existing file candidates only; not a loaded-module or API-set forwarding attestation."}

    records = {name: {"path": str(path), "sha256": sha(path), "pe": imports(path)}
               for name, path in bins.items()}
    save("runtime-bindings", {"executors": records, "os": platform.platform(), "python": sys.version,
                              "runner": {"path": str(RUNNER), "sha256": sha(RUNNER)},
                              "python_dll": {"path": str(PYTHON.parent / "python314.dll"),
                                             "sha256": sha(PYTHON.parent / "python314.dll")}})
    source = json.loads((OWNED / "typescript-package.json").read_text())
    save("typescript-source-identity", {k: source.get(k) for k in ("name", "version", "license", "main", "engines")})
    # Capture the negative native report rather than treating exit 0 as consumption.
    invalid = OWNED / "invalid encoding report" / "jscpd-report.json"
    save("jscpd-invalid-raw", {"path": str(invalid), "sha256": sha(invalid), "raw": json.loads(invalid.read_bytes())})
    debug = (EVIDENCE / "q2-tools-jscpd-final-debug.stdout.log").read_text(encoding="utf-8")
    merged = json.loads(debug[debug.index("{"):])
    assert merged["max_size"] == 18446744073709551615
    assert not merged["cross_formats"] and not merged["ignore"] and not merged["ignore_patterns"]
    assert merged["max_gap_lines"] == 0 and merged["similarity"] == 1.0
    save("jscpd-resolved-config", {"settings": merged,
                                  "sha256": sha(EVIDENCE / "q2-tools-jscpd-final-debug.stdout.log")})
    rules = json.loads((EVIDENCE / "q2-tools-ruff-rules.json").read_text())["rule_ids"]
    files = json.loads((EVIDENCE / "q2-tools-ruff-inputs.json").read_text())["files"]
    listed = (EVIDENCE / "q2-tools-ruff-files.stdout.log").read_text(encoding="utf-8").splitlines()
    assert {v for v in listed if v} == {v["path"] for v in files}
    assert all(sha(v["path"]) == v["sha256"] for v in files)
    previous = json.loads((EVIDENCE / "q2-tools-locations.json").read_text())["source_pins"]
    current = {name: sha(REPO / name) for name in previous}
    assert current == previous
    save("boundary", {"source_pins": current, "all_initial_pins_unchanged": True,
                      "ruff_explicit_census": len(files), "ruff_resolved_rules": len(rules),
                      "toolchain_installs": "Two standalone official native releases extracted; no venv created and no Python wheels installed",
                      "coverage": "7.16.1 DEFERRED to Q3; neither provisioned nor executed",
                      "cleanup": {"scratch_empty": not any((OWNED / "scratch").iterdir()),
                                  "ruff_cache": [str(p) for p in OWNED.rglob(".ruff_cache")],
                                  "background_processes_started": 0,
                                  "retained": str(OWNED)}})
    git = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"
    command("head-after", [git, "--no-pager", "rev-parse", "HEAD"], REPO)
    command("status-after", [git, "--no-pager", "status", "--short"], REPO)


def shape_cases():
    os.chdir(OWNED)
    fixture = Path("shape fixtures")
    fixture.mkdir()
    shape = """// café 😀
export const calculate = async (value) => {
  const matcher = /a[b-c]+/;
  function inner(item) {
    return item > 3 ? item + 4 : item - 2;
  }
  const message = `café ${inner(value)}`;
  const division = value / 2;
  return matcher.test(message) && division > 3 ? message : "none";
};
"""
    variants = {
        ".js": shape,
        ".mjs": shape,
        ".cjs": shape.replace("export const", "const") + "module.exports = { calculate };\n",
        ".ts": "interface Input { size: number; }\n" + shape.replace("(value) =>", "(value: number): Promise<string> =>"),
        ".jsx": shape + 'export const View = ({title}) => <section><h1>{title}</h1></section>;\n',
        ".tsx": shape.replace("(value) =>", "(value: number): Promise<string> =>") +
                'export const View = ({title}: {title: string}) => <section><h1>{title}</h1></section>;\n',
        ".py": """# café 😀
async def outer(value):
    def inner(item):
        return item + 4 if item > 3 else item - 2
    message = f"café {inner(value)}"
    division = value / 2
    transformer = lambda item: item * 2
    return message if transformer(division) > 3 else "none"
""",
    }
    exe = json.loads((EVIDENCE / "q2-tools-executables.json").read_text())["jscpd"]["path"]
    common = [exe, "--config", OWNED / "jscpd-config.json", "--min-tokens", "40", "--min-lines", "5",
              "--mode", "mild", "--reporters", "json", "--summary", "--summary-top", "32",
              "--no-gitignore", "--no-colors", "--no-tips", "--workers", "1", "--absolute",
              "--max-size", "18446744073709551615",
              "--formats-exts", "javascript:js,mjs,cjs;typescript:ts;tsx:tsx;jsx:jsx"]
    cases = {}
    for suffix, content in variants.items():
        paths = [(fixture / (name + suffix)).resolve() for name in ("shape a", "shape b")]
        for path in paths:
            path.write_bytes(content.replace("\n", "\r\n").encode("utf-8"))
        output = OWNED / ("shape report " + suffix[1:])
        result = command("jscpd-shape-" + suffix[1:], [*common, "--output", output, *paths], install=True)
        assert result.returncode == 0
        rawpath = output / "jscpd-report.json"
        raw = json.loads(rawpath.read_bytes())
        assert len(raw["summary"]["files"]) == 2 and len(raw["duplicates"]) > 0
        save("jscpd-shape-raw-" + suffix[1:], {"path": str(rawpath), "sha256": sha(rawpath), "raw": raw})
        cases[suffix] = {"files": [{"path": str(path), "sha256": sha(path)} for path in paths],
                         "clones": len(raw["duplicates"]), "census": raw["summary"]["files"]}
    save("jscpd-shape-results", cases)
    path = (fixture / "unicode positions.py").resolve()
    text = 'text = "😀é"; missing_name\n'
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    ruff = json.loads((EVIDENCE / "q2-tools-ruff-executable.json").read_text())["path"]
    rules = json.loads((EVIDENCE / "q2-tools-ruff-rules.json").read_text())["rule_ids"]
    argv = [ruff, "check", "--isolated", "--no-cache", "--no-fix", "--no-preview",
            "--no-respect-gitignore", "--no-force-exclude", "--target-version", "py314",
            "--select", ",".join(rules), "--output-format", "json", path]
    before = sha(path)
    result = command("ruff-unicode-positions", argv)
    raw = json.loads(result.stdout)
    missing = next(v for v in raw if v["code"] == "F821")
    actual_column = missing["location"]["column"]
    candidates = {"unicode_codepoints_1based": text.index("missing_name") + 1,
                  "utf8_bytes_1based": len(text[:text.index("missing_name")].encode("utf-8")) + 1,
                  "utf16_units_1based": len(text[:text.index("missing_name")].encode("utf-16-le")) // 2 + 1}
    assert result.returncode == 1 and sha(path) == before
    save("ruff-column-semantics", {"path": str(path), "sha256": before, "raw": raw,
                                  "observed_column": actual_column, "candidate_columns": candidates,
                                  "matched_models": [k for k, v in candidates.items() if v == actual_column]})


def manifest():
    os.chdir(OWNED)
    scratch = Path("scratch")
    if scratch.exists():
        scratch.rmdir()
    originals = json.loads((EVIDENCE / "q2-tools-locations.json").read_text())["source_pins"]
    assert all(sha(REPO / name) == digest for name, digest in originals.items())
    runtime = json.loads((EVIDENCE / "q2-tools-runtime-bindings.json").read_text())
    assert all(sha(record["path"]) == record["sha256"] for record in runtime["executors"].values())
    jscpd = json.loads((EVIDENCE / "q2-tools-jscpd-results.json").read_text())
    ruff = json.loads((EVIDENCE / "q2-tools-ruff-results.json").read_text())
    shapes = json.loads((EVIDENCE / "q2-tools-jscpd-shape-results.json").read_text())
    assert all(sha(item["path"]) == item["sha256"] for case in shapes.values() for item in case["files"])

    def ref(name):
        path = EVIDENCE / ("q2-tools-" + name)
        return {"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}

    def binding(tool, version, help_file, config, qualifications):
        record = runtime["executors"][tool]
        return {"executable": record["path"], "module_path": None, "observed_version": version,
                "sha256": record["sha256"], "qualified_api": tool + "-json-" + version.replace(".", "-") + "-v1",
                "help": ref(help_file), "configuration": ref(config),
                "qualification": [ref(path) for path in qualifications]}

    status = {
        "jscpd": {"status": "QUALIFIED", "binding": binding("jscpd", "5.2.1", "jscpd-help.stdout.log",
                   "jscpd-resolved-config.json", ["jscpd-results.json", "jscpd-shape-results.json", "jscpd-invalid-raw.json"]),
                  "license": "MIT", "package": ref("download-jscpd.json"),
                  "positive_pair_runs": 7 + len(shapes), "zero_clone_single_file_runs": 7,
                  "census": jscpd["initial_census"],
                  "conditions": ["Exact complete census plus approved shared parser receipts for empty files",
                                 "Reject nonempty census omission, decoding failure and tool errors",
                                 "Use final nonexcluding max-size bound, exact settings and clone-window separation"]},
        "ruff": {"status": "QUALIFIED", "binding": binding("ruff", "0.16.8", "ruff-check-help.stdout.log",
                 "ruff-rules.json", ["ruff-results.json", "ruff-settings-exact.stdout.log", "ruff-column-semantics.json"]),
                 "license": "MIT", "package": ref("download-ruff-github.json"),
                 "rules": ruff["rules"], "case_count": len(ruff["cases"]),
                 "positive_findings": 4, "additional_unicode_findings": 3,
                 "configuration_argv": ref("ruff-inputs.json"),
                 "conditions": ["Exact explicit file census and unchanged inputs",
                                "E902 and invalid-syntax never ordinary successful AST-dependent measurements",
                                "Inventory existing suppression directives"]},
        "typescript": {"status": "BLOCKED", "blocker": "TS-PACKAGE-TLS", "version": "5.9.3",
                       "license": "Apache-2.0", "binding": None,
                       "source_identity": ref("typescript-source-identity.json"),
                       "evidence": [ref("missing-typescript.json"), ref("metadata-typescript-curl.json")]},
        "lizard": {"status": "BLOCKED", "blocker": "LIZARD-WHEEL-TLS", "version": "1.24.0",
                   "license": "MIT", "binding": None, "positive_cases": 0,
                   "evidence": [ref("metadata-lizard.json"), ref("missing-lizard.json"), ref("download-lizard-curl.json")]},
        "vulture": {"status": "BLOCKED", "blocker": "VULTURE-WHEEL-TLS", "version": "2.16",
                    "license": "MIT", "binding": None, "positive_cases": 0,
                    "evidence": [ref("metadata-vulture.json"), ref("missing-vulture.json"), ref("download-vulture-curl.json")]},
        "coverage": {"status": "DEFERRED", "version": "7.16.1", "owner": "Q3", "binding": None},
    }
    records = []
    for path in sorted(EVIDENCE.glob("q2-tools-*")):
        if path.is_file():
            records.append({"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size})
    save("manifest", {
        "scope": "CHECK-TOOLS only; not Q2 completion or measurement proof",
        "accepted_head": "d971634219a633cc4401fb7dcba9685e672978aa",
        "overall": "BLOCKED", "owned_external_root": str(OWNED),
        "tools": status, "evidence": records,
        "source_pins_rechecked": originals,
        "runner_argv": [str(PYTHON), "-B", str(RUNNER), "--idle", "{30|120}",
                        "--max", "{90|1200}", "--", "{exact argv in each command record}"],
        "captures": "Raw wrapper streams; native run.py CLI merges child stderr and normalizes newlines. Native report hashes are separate.",
        "cleanup": {"empty_scratch_removed": True, "native_tools_and_fixtures_retained": True,
                    "venv_created": False, "background_processes_started": 0},
    })
    print("Manifest frozen:", len(records), "artifacts,", sum(r["bytes"] for r in records), "bytes")
    print("QUALIFIED jscpd 5.2.1 / Ruff 0.16.8; BLOCKED TypeScript/lizard/Vulture; DEFERRED coverage")


def verify_manifest():
    value = json.loads((EVIDENCE / "q2-tools-manifest.json").read_text())
    assert all(sha(item["path"]) == item["sha256"] for item in value["evidence"])
    assert all(sha(REPO / path) == digest for path, digest in value["source_pins_rechecked"].items())
    for tool in value["tools"].values():
        if tool.get("binding"):
            assert sha(tool["binding"]["executable"]) == tool["binding"]["sha256"]
    print(json.dumps({"verified_artifacts": len(value["evidence"]), "unchanged_source_pins": 6,
                      "overall": value["overall"], "manifest_sha256": sha(EVIDENCE / "q2-tools-manifest.json")}))


def inspect():
    os.chdir(ARTIFACTS)
    OWNED.name and Path(OWNED.name).mkdir(exist_ok=False)
    candidates = {}
    for name in ("node", "npm.cmd", "uv", "jscpd", "ruff", "lizard", "vulture"):
        candidates[name] = shutil.which(name)
    save("locations", {"python": str(PYTHON), "owned": str(OWNED), "path_candidates": candidates,
                       "source_pins": {str(p.relative_to(REPO)): sha(p) for p in [
                           RUNNER, REPO / "scripts" / "measure.py", REPO / "scripts" / "measure_graph.py",
                           REPO / "scripts" / "probe.py",
                           REPO / ".ai" / "workflow-reliability" / "measurement-enablement-contracts.json",
                           REPO / ".ai" / "workflow-reliability" / "evidence" / "measurement-design-review-r2.md"]}})
    command("python-version", [PYTHON, "-B", "--version"])
    for module in ("lizard", "vulture", "ruff"):
        command("missing-" + module, [PYTHON, "-B", "-c", "__import__(" + repr(module) + ")"])
    node = candidates["node"]
    if node:
        command("node-version", [node, "--version"])
        command("missing-typescript", [node, "-e", "require('typescript/lib/typescript.js')"])
    command("missing-jscpd", [str(OWNED / "jscpd.exe"), "--version"])
    if candidates["uv"]:
        command("uv-version", [candidates["uv"], "--version"])
        command("uv-pip-help", [candidates["uv"], "pip", "install", "--help"])
    git = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"
    command("head", [git, "--no-pager", "rev-parse", "HEAD"], REPO)
    command("status-before", [git, "--no-pager", "status", "--short"], REPO)


if __name__ == "__main__":
    globals()[sys.argv[1]]()
