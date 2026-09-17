"""One bounded secure acquisition-route follow-up; no production adapters."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit, urlunsplit

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("q2_owned_harness", HERE / "q2-tools-qualify.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
ROOT = q.OWNED / "route-1"


def save(name, value):
    q.save("route-" + name, value)


def command(name, argv, install=False):
    return q.command("route-" + name, argv, cwd=ROOT, install=install)


def initial():
    os.chdir(q.OWNED)
    Path("route-1").mkdir()
    prior = [{"path": str(p), "sha256": q.sha(p), "bytes": p.stat().st_size}
             for p in sorted(HERE.glob("q2-tools-*")) if p.is_file() and not p.name.startswith("q2-tools-route-")]
    candidates = [{"path": str(p), "sha256": q.sha(p), "bytes": p.stat().st_size}
                  for p in q.OWNED.rglob("*") if p.is_file() and
                  p.name.endswith((".whl", ".tgz", ".tar.gz", ".zip"))]
    curl = shutil.which("curl.exe")
    save("initial", {"prior_evidence": prior, "owned_package_candidates": candidates,
                     "curl": curl, "curl_sha256": q.sha(curl), "owned_route_root": str(ROOT)})
    command("curl-version", [curl, "--version"])
    command("curl-help", [curl, "--help", "all"])


def probe():
    curl = json.loads((HERE / "q2-tools-route-initial.json").read_text())["curl"]
    lizard = json.loads((HERE / "q2-tools-metadata-lizard.json").read_text())["selected_metadata"]
    wheel = next(p for p in lizard["urls"] if p["filename"].endswith(".whl"))
    targets = [("npm", "https://registry.npmjs.org/typescript/5.9.3", "typescript-5.9.3-metadata.json", None),
               ("pypi-files", wheel["url"], wheel["filename"], wheel["digests"]["sha256"])]
    observations = {}
    for name, url, filename, expected in targets:
        path = ROOT / filename
        argv = [curl, "--disable", "--tlsv1.2", "--tls-max", "1.2", "--proto", "=https",
                "--proto-redir", "=https", "--retry", "0", "--max-time", "60",
                "--fail-with-body", "--silent", "--show-error", "--output", str(path),
                "--write-out", "http_code=%{http_code};ssl_verify_result=%{ssl_verify_result}\\n", url]
        result = command("probe-" + name, argv)
        record = {"url": url, "exit": result.returncode,
                  "status": result.stdout.decode("utf-8", "replace"),
                  "body_sha256": q.sha(path) if path.exists() else None,
                  "bytes": path.stat().st_size if path.exists() else 0,
                  "expected_sha256": expected}
        if result.returncode == 0:
            if expected:
                assert q.sha(path) == expected, "Package digest mismatch"
            else:
                metadata = json.loads(path.read_bytes())
                assert metadata["version"] == "5.9.3"
                record["metadata"] = {k: metadata.get(k) for k in
                                      ("name", "version", "license", "dist", "dependencies")}
        elif path.exists():
            body = path.read_text(encoding="utf-8", errors="replace")
            record["error_body_excerpt"] = body[:2000]
            if any(word in body.lower() for word in ("organization policy", "corporate policy", "blocked by policy")):
                record["policy_stop"] = True
                observations[name] = record
                save("probes", observations)
                raise RuntimeError("Explicit policy block: stop, no alternate route")
        observations[name] = record
    save("probes", observations)


PROJECTS = {
    "typescript": ("microsoft/TypeScript", "5.9.3"),
    "lizard": ("terryyin/lizard", "1.24.0"),
    "vulture": ("jendrikseipp/vulture", "2.16"),
    "pygments": ("pygments/pygments", "2.21.0"),
    "pathspec": ("cpburnz/python-pathspec", "1.1.1"),
}


def fetch(name, url):
    request = urllib.request.Request(url, headers={"User-Agent": "Q2-bounded-source-feasibility"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
            status, resolved = response.status, response.url
    except urllib.error.HTTPError as error:
        body, status, resolved = error.read(), error.code, error.url
    path = ROOT / (name + ".capture")
    if path.exists():
        raise FileExistsError(path)
    path.write_bytes(body)
    parts = urlsplit(resolved)
    resolved = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    record = {"url": url, "resolved_url": resolved, "http_status": status, "path": str(path),
              "sha256": q.sha(path), "bytes": len(body)}
    save(name, record)
    print(name, status, len(body), flush=True)
    if status in (401, 403, 451) or b"blocked by policy" in body.lower():
        raise RuntimeError("Access/policy denial; no alternate route authorized")
    return status, body, record


def lookup(tool):
    repo, version = PROJECTS[tool]
    status, raw, _ = fetch(tool + "-tags", "https://api.github.com/repos/" + repo + "/tags?per_page=100")
    assert status == 200
    tags = json.loads(raw)
    selected = [v for v in tags if v["name"] in (version, "v" + version)]
    assert len(selected) == 1, "Exact tag unavailable in bounded tag inventory"
    tag = selected[0]
    status, raw, _ = fetch(tool + "-tag-ref", "https://api.github.com/repos/" + repo + "/git/ref/tags/" + tag["name"])
    assert status == 200
    ref = json.loads(raw)
    status, raw, _ = fetch(tool + "-release", "https://api.github.com/repos/" + repo + "/releases/tags/" + tag["name"])
    release = json.loads(raw) if status == 200 else None
    save(tool + "-origin", {"repository": repo, "version": version, "tag": tag["name"],
                            "commit": tag["commit"]["sha"], "ref_object": ref["object"],
                            "release_status": status,
                            "release": {k: release.get(k) for k in ("html_url", "draft", "prerelease", "published_at")} if release else None,
                            "assets": [{k: a.get(k) for k in ("name", "size", "browser_download_url", "digest")}
                                       for a in release["assets"]] if release else [],
                            "proposed_source_archive": "https://api.github.com/repos/" + repo + "/tarball/" + tag["commit"]["sha"]})


def sources(tool):
    origin = json.loads((HERE / ("q2-tools-route-" + tool + "-origin.json")).read_text())
    repo, commit = origin["repository"], origin["commit"]
    selections = {
        "typescript": ["package.json", "herebyfile.mjs", "lib/typescript.js", "lib/typescript.d.ts"],
        "lizard": ["setup.py", "pyproject.toml", "lizard.py", "lizard_ext/version.py",
                   "lizard_languages/__init__.py", "lizard_languages/javascript.py", "lizard_languages/typescript.py",
                   "lizard_languages/python.py", "LICENSE"],
        "vulture": ["pyproject.toml", "setup.cfg", "vulture/core.py", "vulture/config.py", "vulture/version.py",
                    "vulture/__init__.py", "vulture/__main__.py", "LICENSE.txt"],
        "pygments": ["pyproject.toml", "setup.cfg", "pygments/__init__.py", "LICENSE"],
        "pathspec": ["pyproject.toml", "pathspec/__init__.py", "pathspec/_version.py", "LICENSE"],
    }
    records = []
    for path in selections[tool]:
        status, raw, record = fetch(tool + "-source-" + path.replace("/", "-"),
                                    "https://raw.githubusercontent.com/" + repo + "/" + commit + "/" + path)
        record["source_path"] = path
        records.append(record)
    save(tool + "-source-files", records)


def typescript_distribution():
    import io
    import tarfile
    origin = json.loads((HERE / "q2-tools-route-typescript-origin.json").read_text())
    asset = next(a for a in origin["assets"] if a["name"] == "typescript-5.9.3.tgz")
    status, body, record = fetch("typescript-release-package", asset["browser_download_url"])
    assert status == 200
    assert hashlib.sha256(body).hexdigest() == asset["digest"].split(":")[1]
    # Read archive members as data only. No extraction, import, install, or execution.
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        names = {m.name for m in archive.getmembers() if m.isfile()}
        package = json.loads(archive.extractfile("package/package.json").read())
        assert package["version"] == "5.9.3"
        declarations = archive.extractfile("package/lib/typescript.d.ts").read().decode()
        symbols = ("createSourceFile(", "createProgram(", "forEachChild", "getTypeChecker(",
                   "getPreEmitDiagnostics(", "getSymbolAtLocation(", "getAliasedSymbol(")
        snippets = [line.strip() for line in declarations.splitlines() if any(s in line for s in symbols)]
        pins = [{"path": n, "sha256": hashlib.sha256(archive.extractfile(n).read()).hexdigest()}
                for n in sorted(names) if n.startswith(("package/bin/", "package/lib/")) or
                n in ("package/package.json", "package/LICENSE.txt")]
        save("typescript-package-inspection", {
            "status": "INSPECTED_NOT_INSTALLED_OR_EXECUTED",
            "archive": record, "release_digest_matched": True,
            "package": {k: package.get(k) for k in ("name", "version", "license", "main", "bin", "engines", "dependencies")},
            "compiler_api_declarations": snippets, "package_binding_candidates": pins,
            "runtime_files_present": sorted(n for n in names if n.startswith("package/") and
                                             (n.endswith(".js") or n.startswith("package/bin/"))),
            "source_build_required_for_release_package": False,
        })


def supplemental():
    # Remove transient signed download query strings from this follow-up's two
    # generated records; original qualification/TLS evidence is never touched.
    for name in ("typescript-release-package", "typescript-package-inspection"):
        path = HERE / ("q2-tools-route-" + name + ".json")
        value = json.loads(path.read_text())
        target = value.get("archive", value)
        parts = urlsplit(target["resolved_url"])
        target["resolved_url"] = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    extras = {
        "lizard": ["LICENSE.txt", "lizard_ext/html_output.py", "lizard_ext/__init__.py", "CHANGELOG.md"],
        "vulture": ["vulture/utils.py"],
        "pathspec": ["pathspec/_meta.py", "pathspec/patterns/gitwildmatch.py", "pathspec/_backends/__init__.py"],
    }
    for tool, paths in extras.items():
        origin = json.loads((HERE / ("q2-tools-route-" + tool + "-origin.json")).read_text())
        for path in paths:
            fetch(tool + "-extra-" + path.replace("/", "-"),
                  "https://raw.githubusercontent.com/" + origin["repository"] + "/" + origin["commit"] + "/" + path)
    for tool in ("vulture", "pygments"):
        origin = json.loads((HERE / ("q2-tools-route-" + tool + "-origin.json")).read_text())
        status, raw, _ = fetch(tool + "-annotated-tag", origin["ref_object"]["url"])
        assert status == 200 and json.loads(raw)["object"]["sha"] == origin["commit"]


def archive_inspect(tool):
    import ast
    import io
    import tarfile
    origin = json.loads((HERE / ("q2-tools-route-" + tool + "-origin.json")).read_text())
    status, body, record = fetch(tool + "-source-archive", origin["proposed_source_archive"])
    assert status == 200
    roots = {"lizard": ("lizard.py", "lizard_languages/", "lizard_ext/"),
             "vulture": ("vulture/",), "pygments": ("pygments/",), "pathspec": ("pathspec/",)}[tool]
    pins, imports, errors = [], [], []
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            name = member.name.split("/", 1)[-1]
            if not any(name == root or (root.endswith("/") and name.startswith(root)) for root in roots):
                continue
            content = archive.extractfile(member).read()
            pins.append({"path": name, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
            if name.endswith(".py"):
                try:
                    tree = ast.parse(content, filename=name)
                except (SyntaxError, UnicodeError) as error:
                    errors.append({"path": name, "error": str(error)})
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend({"path": name, "line": node.lineno, "module": alias.name}
                                       for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                        imports.append({"path": name, "line": node.lineno, "module": node.module})
    owned = {"lizard", "lizard_ext", "lizard_languages"} if tool == "lizard" else {tool}
    external = [r for r in imports if r["module"].split(".")[0] not in sys.stdlib_module_names | owned]
    pins.sort(key=lambda v: v["path"])
    digest = hashlib.sha256(json.dumps(pins, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    save(tool + "-archive-inspection", {"status": "DATA_ONLY_NOT_PROVISIONED_OR_EXECUTED",
        "origin": origin, "archive": record, "runtime_file_pins": pins, "runtime_tree_sha256": digest,
        "static_external_import_sites": external, "static_parse_errors": errors,
        "limits": "Syntax/import inventory only; conditional/optional imports are not mandatory runtime dependency claims. No package import or install."})
    print(tool, "runtime files", len(pins), "external import sites", len(external), "parse errors", len(errors))


def dependency_details():
    import io
    import tarfile
    wanted = {
        "lizard": {"lizard_ext/htmloutput.py": [(1, 38)], "lizard_languages/erlang.py": [(1, 45)]},
        "pathspec": {"pathspec/_typing.py": [(1, 65)], "pathspec/pathspec.py": [(1, 110)],
                     "pathspec/_backends/agg.py": [(1, 180)]},
        "pygments": {"pygments/__init__.py": [(1, 110)], "pygments/plugin.py": [(1, 65)]},
    }
    for tool, paths in wanted.items():
        archivepath = ROOT / (tool + "-source-archive.capture")
        records = {}
        with tarfile.open(archivepath, mode="r:gz") as archive:
            members = {m.name.split("/", 1)[-1]: m for m in archive.getmembers() if m.isfile()}
            for path, ranges in paths.items():
                if path not in members:
                    records[path] = {"missing": True,
                                     "backend_candidates": [n for n in members if n.startswith("pathspec/_backends/")]}
                    continue
                content = archive.extractfile(members[path]).read()
                lines = content.decode("utf-8").splitlines()
                records[path] = {"sha256": hashlib.sha256(content).hexdigest(),
                                 "excerpts": [{"start": a, "end": b, "text": "\n".join(lines[a-1:b])} for a, b in ranges]}
        save(tool + "-dependency-details", records)
        print(json.dumps(records, ensure_ascii=True))
    ts = json.loads((HERE / "q2-tools-route-typescript-package-inspection.json").read_text())
    checks = []
    for name in ("lib/typescript.js", "lib/typescript.d.ts"):
        expected = next(p["sha256"] for p in ts["package_binding_candidates"] if p["path"] == "package/" + name)
        actual = q.sha(ROOT / ("typescript-source-" + name.replace("/", "-") + ".capture"))
        checks.append({"source_path": name, "package_sha256": expected, "tag_source_sha256": actual, "match": expected == actual})
    save("typescript-tag-package-comparison", checks)


def finish():
    initial = json.loads((HERE / "q2-tools-route-initial.json").read_text())
    preservation = [{"path": item["path"], "sha256": q.sha(item["path"]),
                     "unchanged": q.sha(item["path"]) == item["sha256"]}
                    for item in initial["prior_evidence"]]
    assert all(item["unchanged"] for item in preservation)
    old_manifest = json.loads((HERE / "q2-tools-manifest.json").read_text())
    source_checks = {path: {"sha256": q.sha(q.REPO / path), "unchanged": q.sha(q.REPO / path) == digest}
                     for path, digest in old_manifest["source_pins_rechecked"].items()}
    runtime = json.loads((HERE / "q2-tools-runtime-bindings.json").read_text())
    runtime_checks = {name: {"path": item["path"], "sha256": q.sha(item["path"]),
                             "unchanged": q.sha(item["path"]) == item["sha256"]}
                      for name, item in runtime["executors"].items()}
    assert all(v["unchanged"] for v in source_checks.values())
    assert all(v["unchanged"] for v in runtime_checks.values())
    assert q.sha(initial["curl"]) == initial["curl_sha256"]
    git = r"C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe"
    result = command("head-final", [git, "--no-pager", "-C", q.REPO, "rev-parse", "HEAD"])
    assert result.returncode == 0 and result.stdout.decode().strip() == old_manifest["accepted_head"]
    status = {}
    for tool in PROJECTS:
        origin = json.loads((HERE / ("q2-tools-route-" + tool + "-origin.json")).read_text())
        artifact = ("typescript-release-package" if tool == "typescript" else tool + "-source-archive")
        download = json.loads((HERE / ("q2-tools-route-" + artifact + ".json")).read_text())
        assert q.sha(download["path"]) == download["sha256"]
        status[tool] = {"status": "BLOCKED-PENDING-ROUTE-APPROVAL" if tool in ("typescript", "lizard", "vulture")
                       else "PROPOSED-DEPENDENCY-NOT-PROVISIONED",
                       "origin": origin, "acquired_data_only": download}
    repo_files = [{"path": str(p), "sha256": q.sha(p), "bytes": p.stat().st_size}
                  for p in sorted(HERE.glob("q2-tools-route-*")) if p.is_file()]
    external_files = [{"path": str(p), "sha256": q.sha(p), "bytes": p.stat().st_size}
                      for p in sorted(ROOT.iterdir()) if p.is_file()]
    save("manifest", {"scope": "One bounded acquisition-route follow-up; not CHECK-TOOLS completion",
                      "overall": "BLOCKED-PENDING-ROUTE-APPROVAL",
                      "tools": status, "same_host_tls_attempts": {"registry.npmjs.org": 1, "files.pythonhosted.org": 1},
                      "prior_evidence_preservation": preservation, "source_checks": source_checks,
                      "runtime_checks": runtime_checks, "curl_sha256": initial["curl_sha256"],
                      "evidence": repo_files, "external_data": external_files,
                      "cleanup": {"installs": 0, "package_extractions": 0, "package_executions": 0,
                                  "background_processes_started": 0, "owned_data_retained": str(ROOT)},
                      "capture_limits": "Child curl and final git commands have raw wrapper logs. Outer phase output and helper pre-network indentation failures are in session transcript. HTTP fetch records retain exact URLs/statuses and hashed response bodies; signed redirect queries omitted."})
    print("Preserved", len(preservation), "prior evidence files;", len(repo_files), "new evidence files; six source and four executor pins unchanged")


def verify():
    value = json.loads((HERE / "q2-tools-route-manifest.json").read_text())
    for item in value["evidence"] + value["external_data"] + value["prior_evidence_preservation"]:
        assert q.sha(item["path"]) == item["sha256"]
    print(json.dumps({"verified": True, "prior_evidence": len(value["prior_evidence_preservation"]),
                      "manifest_sha256": q.sha(HERE / "q2-tools-route-manifest.json"),
                      "overall": value["overall"]}))


if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])
