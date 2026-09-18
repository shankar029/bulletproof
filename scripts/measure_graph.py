"""Source-bound Python literal-import evidence. No discovery or policy composition."""

import ast
import _imp
from bisect import bisect_right
import hashlib
from importlib.machinery import BuiltinImporter, FrozenImporter
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import tokenize

from evidence import _json_bytes, write_json_atomic

SEMANTICS = "python-literal-import-v3"
RULE_IDS = ["ARCH01", "ARCH02", "ARCH03", "ARCH04", "ARCH05"]
CYCLE_STEPS = 100000
CYCLE_LIMIT = 10000
CYCLE_SECONDS = 5
JS_EXT = frozenset({".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"})
JS_SEMANTICS = "typescript-shared-v1"
MIXED_SEMANTICS = "mixed-literal-import-graph-v1"
JS_CONTROLLERS = ("evidence.py", "measure.py", "measure_graph.py", "measure_js.mjs", "probe.py", "run.py")


def _fields(value, names, label):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ValueError("Invalid " + label + " fields")


def _same(left, right, label):
    if (left != right if isinstance(left, bytes) or isinstance(right, bytes)
            else _json_bytes(left) != _json_bytes(right)):
        raise ValueError(label + " mismatch")


def _js_name(revision, slot):
    if revision not in {"base", "head"} or slot not in {"request", "command", "result", "symbols"}:
        raise ValueError("Invalid JS locator")
    return revision + "/js/" + slot + ".json"


def _js_bytes(context, ref):
    _fields(ref, "path sha256 bytes", "JS Artifact")
    if (type(ref["bytes"]) is not int or ref["bytes"] < 0 or
            not isinstance(ref["sha256"], str) or not re.fullmatch("[0-9a-f]{64}", ref["sha256"])):
        raise ValueError("Invalid JS Artifact pin")
    path = input_path(context["run_root"], ref["path"])
    before = path.stat()
    if (not stat.S_ISREG(before.st_mode) or not before.st_ino or before.st_nlink != 1 or
            getattr(before, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
        raise ValueError("JS artifact requires independent regular-file identity")
    data = path.read_bytes()
    after = path.stat()
    keys = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_nlink", "st_mode")
    if any(getattr(before, key) != getattr(after, key) for key in keys):
        raise ValueError("JS artifact changed while reading")
    if len(data) != ref["bytes"] or hashlib.sha256(data).hexdigest() != ref["sha256"]:
        raise ValueError("JS artifact bytes mismatch: " + ref["path"])
    return data


def _js_json(context, name):
    ref = artifact(context["run_root"], name)
    return ref, load_json(_js_bytes(context, ref))


def _js_qualifications(config):
    refs = {}
    for binding in config["tools"].values():
        for ref in [binding["help"], binding["configuration"], *binding["qualification"]]:
            if ref["path"] in refs:
                _same(refs[ref["path"]], ref, "Qualification declaration")
            refs[ref["path"]] = ref
    return [refs[name] for name in sorted(refs)]


def _js_reservations(inventories, config):
    names = [ref["path"] for ref in _js_qualifications(config)]
    names += ["js-preflight.json", "js-produced.json", "manifest.json"]
    if [inv["revision"] for inv in inventories] != ["base", "head"]:
        raise ValueError("Both ordered JS inventories are required")
    for inv in inventories:
        names += [_js_name(inv["revision"], slot) for slot in ("request", "command", "result", "symbols")]
        names.append(graph_name(inv["revision"]))
        names += [syntax_name(inv["revision"], entry["path"]) for entry in inv["entries"]
                  if entry["language"] == "python" or entry["suffix"] in JS_EXT]
    folded = set()
    for name in names:
        relative_name(name)
        key = name.casefold() if os.name == "nt" else name
        if key in folded:
            raise ValueError("Duplicate JS reservation")
        folded.add(key)
    if any("/".join(name.split("/")[:end]) in folded
           for name in folded for end in range(1, len(name.split("/")))):
        raise ValueError("JS reservation prefix collision")
    return sorted(names)


def _js_output_action(command):
    if type(command["returncode"]) is not int or not isinstance(command["stderr"], str):
        raise ValueError("Invalid JS command outcome")
    return ("nonzero-opaque" if command["returncode"] != 0 else
            "zero-stderr-invalid" if command["stderr"] != "" else "zero-strict")


def _js_transport(context, inv, config, *, purpose=None):
    """Check fixed own-run transport. This is not accepting semantic replay."""
    revision = inv["revision"]
    request_ref, request = _js_json(context, _js_name(revision, "request"))
    command_ref, command = _js_json(context, _js_name(revision, "command"))
    _fields(request, "schema_version binding execution_id purpose context inventory config pre_manifest inputs outputs",
            "JSRequestV1")
    _fields(command, "schema_version binding execution_id request pre_manifest argv cwd idle_seconds max_seconds "
            "environment_delta returncode stdout stderr capture_semantics result symbols", "JSCommandV1")
    for value in (request, command):
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            raise ValueError("Invalid JS transport version")
    if (request["purpose"] not in {"produce", "validate"} or
            (purpose is not None and request["purpose"] != purpose) or
            not isinstance(request["execution_id"], str) or
            not re.fullmatch("[0-9a-f]{32}", request["execution_id"])):
        raise ValueError("JS execution purpose/identity mismatch")
    pre_ref = artifact(context["run_root"], "js-preflight.json")
    expected_context = {**context, "output_manifest": pre_ref}
    _same(request["context"], expected_context, "JS request Context")
    _same(request["inventory"], inv, "JS request Inventory")
    _same(request["config"], config, "JS request config")
    _same(request["pre_manifest"], pre_ref, "JS request preflight")
    _same(command["pre_manifest"], pre_ref, "JS capture preflight")
    _same(command["request"], request_ref, "JS capture request")
    _same(command["binding"], request["binding"], "JS capture binding")
    _same(command["execution_id"], request["execution_id"], "JS capture execution")
    binding = request["binding"]
    _fields(binding, "semantic_version run_id revision git_revision inventory_sha256 source_sha256 "
            "parser_sha256 toolset_sha256 settings_sha256 policy_sha256", "JSBinding")
    for key, expected in {
            "semantic_version": JS_SEMANTICS, "run_id": context["run_id"], "revision": revision,
            "git_revision": context["source"][revision], "inventory_sha256": inv["digest"],
            "source_sha256": inv["source_sha256"], "toolset_sha256": context["toolset_sha256"],
            "policy_sha256": context["policy_sha256"]}.items():
        _same(binding[key], expected, "JS " + key)
    for key in ("parser_sha256", "settings_sha256"):
        if not isinstance(binding[key], str) or not re.fullmatch("[0-9a-f]{64}", binding[key]):
            raise ValueError("Invalid JS digest")
    if not isinstance(request["inputs"], list):
        raise ValueError("Invalid JS input list")
    for row in request["inputs"]:
        _fields(row, "scope path sha256 bytes", "JSInput")
        if row["scope"] not in {"subject", "head-contract", "tool-resource"}:
            raise ValueError("Invalid JS input scope")
        relative_name(row["path"])
        if (type(row["bytes"]) is not int or row["bytes"] < 0 or
                not isinstance(row["sha256"], str) or not re.fullmatch("[0-9a-f]{64}", row["sha256"])):
            raise ValueError("Invalid JS input pin")
    if (request["inputs"] != sorted(request["inputs"], key=lambda row: (row["scope"], row["path"])) or
            len({(row["scope"], row["path"]) for row in request["inputs"]}) != len(request["inputs"])):
        raise ValueError("Unordered/duplicate JS input")
    expected_argv = [config["tools"]["typescript"]["executable"],
                     str(Path(context["controller_root"]) / "measure_js.mjs"),
                     str(Path(context["run_root"]) / request_ref["path"])]
    _same(command["argv"], expected_argv, "JS actual argv")
    _same(command["cwd"], context[revision + "_root"], "JS actual cwd")
    if (type(command["idle_seconds"]) not in (int, float) or command["idle_seconds"] != 30 or
            type(command["max_seconds"]) not in (int, float) or command["max_seconds"] != 90 or
            not isinstance(command["stdout"], str) or command["capture_semantics"] !=
            "run_capture UTF-8 replacement-decoded, newline-normalized separate streams"):
        raise ValueError("Invalid JS capture contract")
    _fields(command["environment_delta"], "removed_names", "JS environment")
    removed = command["environment_delta"]["removed_names"]
    if (not isinstance(removed, list) or any(not isinstance(name, str) or not name for name in removed) or
            removed != sorted(set(removed)) or any(not (
                name.upper().startswith(("PYTHON", "NODE_", "TS_NODE_")) or
                name.upper() == "VSCODE_INSPECTOR_OPTIONS") for name in removed)):
        raise ValueError("Invalid JS environment removal")
    _same(request["outputs"], {slot: _js_name(revision, slot) for slot in ("result", "symbols")},
          "JS fixed outputs")
    result, symbols = _js_output_records(context, inv, request, command)
    return request, command, result, symbols, request_ref, command_ref


def _js_output_records(context, inv, request, command):
    """The same finite output admission for captured attempts and owned reads."""
    for slot in ("result", "symbols"):
        name = _js_name(inv["revision"], slot)
        path = input_path(context["run_root"], name)
        actual = artifact(context["run_root"], name) if path.exists() else None
        _same(command[slot], actual, "JS output presence/pin")
        if actual is not None:
            _js_bytes(context, actual)
    action = _js_output_action(command)
    if action == "zero-stderr-invalid":
        raise ValueError("Zero JS exit with stderr is invalid proof")
    result = symbols = None
    if action == "zero-strict":
        if command["result"] is None or command["symbols"] is None:
            raise ValueError("Zero JS exit requires result and symbols")
        result = load_json(_js_bytes(context, command["result"]))
        symbols = load_json(_js_bytes(context, command["symbols"]))
        _js_produced(context, inv, request, command, result, symbols)
    return result, symbols


def _is_js_config(context, ref, config):
    try:
        value = load_json(input_path(context["head_root"], ref["path"]).read_bytes())
    except ValueError:
        return False
    return _json_bytes(value) == _json_bytes(config)


def _js_produced(context, inv, request, command, result, symbols):
    _fields(result, "schema_version binding execution_id request state symbols provenance syntax reasons", "JSResultV1")
    _fields(symbols, "schema_version binding inputs files symbols exports aliases references module_references "
            "entrypoints outside_model directives diagnostics", "JSSymbolEvidenceV1")
    for value in (result, symbols):
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            raise ValueError("Invalid JS output version")
        _same(value["binding"], request["binding"], "JS output binding")
    for key in ("execution_id", "request", "symbols"):
        _same(result[key], command[key], "JS result " + key)
    if result["state"] != "produced" or result["reasons"] != []:
        raise ValueError("Zero JS exit requires produced state and empty reasons")
    configuration_paths = [ref["path"] for ref in context["contract_artifacts"]
                           if _is_js_config(context, ref, request["config"])]
    _same(symbols["inputs"], [row for row in request["inputs"] if row["scope"] != "head-contract" or
                             row["path"] in configuration_paths], "JS admitted symbol inputs")
    entries = [entry for entry in inv["entries"] if entry["suffix"] in JS_EXT]
    if not isinstance(symbols["files"], list) or [row.get("path") for row in symbols["files"]] != [
            entry["path"] for entry in entries]:
        raise ValueError("JS census differs from inventory")
    processed = []
    for entry, row in zip(entries, symbols["files"]):
        _fields(row, "path source_sha256 observed_sha256 suffix state reason token_count function_count diagnostic_ids",
                "JSCensus")
        if (entry["language"] != ("typescript" if entry["suffix"] in {".ts", ".tsx"} else "javascript") or
                entry["parse_state"] != "pending" or entry["parser"] is not None or
                entry["reason"] != "" or entry["diagnostics"] != []):
            raise ValueError("JS inventory classification mismatch")
        if (row["source_sha256"] != entry["sha256"] or row["suffix"] != entry["suffix"] or
                row["observed_sha256"] not in (None, entry["sha256"]) or
                row["state"] not in {"processed", "failed", "unsupported"} or not isinstance(row["reason"], str)):
            raise ValueError("Invalid JS census binding/state")
        if row["state"] == "processed":
            if (row["observed_sha256"] != entry["sha256"] or row["reason"] != "" or
                    any(type(row[key]) is not int or row[key] < 0 for key in ("token_count", "function_count"))):
                raise ValueError("Invalid processed JS census")
            processed.append(entry["path"])
        elif not row["reason"] or row["token_count"] is not None or row["function_count"] is not None:
            raise ValueError("Invalid failed JS census")
        diagnostics = row["diagnostic_ids"]
        if (not isinstance(diagnostics, list) or diagnostics != sorted(set(diagnostics)) or
                any(identity not in [item["id"] for item in symbols["diagnostics"]] for identity in diagnostics)):
            raise ValueError("Invalid JS census diagnostics")
    if not isinstance(result["syntax"], list) or [item.get("path") for item in result["syntax"]] != processed:
        raise ValueError("JS syntax partition differs from processed census")
    by_path = {entry["path"]: entry for entry in entries}
    for syntax in result["syntax"]:
        _fields(syntax, "schema_version revision inventory_sha256 path source_sha256 parser_sha256 semantic_version "
                "nodes literal_imports outside_model diagnostics", "SyntaxEvidence")
        expected = {"schema_version": 1, "revision": inv["revision"], "inventory_sha256": inv["digest"],
                    "source_sha256": by_path[syntax["path"]]["sha256"],
                    "parser_sha256": request["binding"]["parser_sha256"], "semantic_version": JS_SEMANTICS}
        _same({key: syntax[key] for key in expected}, expected, "JS syntax binding")
        for key in ("nodes", "literal_imports", "outside_model", "diagnostics"):
            if not isinstance(syntax[key], list):
                raise ValueError("Invalid JS syntax collection")
    provenance = result["provenance"]
    _fields(provenance, "runtime adapter_sha256 controller_files loaded_modules reads", "JSProvenance")
    runtime = {"executable": request["config"]["tools"]["typescript"]["executable"],
               "version": "v24.11.1", "architecture": "arm64", "typescript_version": "5.9.3", "exec_argv": []}
    _same(provenance["runtime"], runtime, "JS qualified runtime")
    controllers = [artifact(context["controller_root"], name) for name in JS_CONTROLLERS]
    _same(provenance["controller_files"], controllers, "JS controller provenance")
    _same(provenance["adapter_sha256"],
          next(ref["sha256"] for ref in controllers if ref["path"] == "measure_js.mjs"), "JS adapter provenance")
    _same(provenance["reads"], request["inputs"], "JS input read provenance")
    modules = provenance["loaded_modules"]
    if (not isinstance(modules, list) or not modules or
            any(row not in request["inputs"] or row["scope"] != "tool-resource" for row in modules) or
            modules != sorted(modules, key=lambda item: (item["scope"], item["path"])) or
            len({row["path"] for row in modules}) != len(modules)):
        raise ValueError("Invalid JS loaded-module provenance")
    _js_symbol_shapes(symbols, by_path, context, inv["revision"], result["syntax"])


def _js_symbol_shapes(symbols, entries, context, revision, syntax):
    """Finite record shapes; source semantics are established only by fresh replay."""
    schemas = {
        "symbols": "id name flags declarations", "exports": "path span name kind type_only target",
        "aliases": "path span name kind target", "references": "path span kind target",
        "module_references": "path span specifier kind resolution targets external reason",
        "entrypoints": "path source_sha256 state public_exports origins",
        "outside_model": "path span kind reason", "directives": "path span kind text",
        "diagnostics": "id code category source message location related"}
    for name, fields in schemas.items():
        records = symbols[name]
        if not isinstance(records, list) or len({digest(row) for row in records}) != len(records):
            raise ValueError("Invalid/duplicate JS " + name)
        for row in records:
            _fields(row, fields, "JS " + name)
    ids = [row["id"] for row in symbols["symbols"]]
    if ids != sorted(set(ids)):
        raise ValueError("Invalid JS symbol IDs")
    sources = {}
    root = context[revision + "_root"]

    def text(value):
        if not isinstance(value, str):
            raise ValueError("Expected JS string")

    def count(value):
        if type(value) is not int or value < 0:
            raise ValueError("Expected JS nonnegative count")

    admitted_subjects = {row["path"]: row for row in symbols["inputs"] if row["scope"] == "subject"}

    def span(name, value, *, metadata=False):
        _fields(value, "start_byte end_byte start_line end_line", "JS Span")
        source_entries = admitted_subjects if metadata else entries
        if name not in source_entries or any(type(number) is not int for number in value.values()):
            raise ValueError("Invalid JS span source/count")
        if name not in sources:
            data = input_path(root, name).read_bytes()
            if hashlib.sha256(data).hexdigest() != source_entries[name]["sha256"]:
                raise ValueError("JS span source changed")
            line_starts = [0, *(match.end() for match in re.finditer(
                r"\r\n|[\r\n\u2028\u2029]", data.decode("utf-8")))]
            sources[name] = data, line_starts
        data, line_starts = sources[name]
        start, end = value["start_byte"], value["end_byte"]
        if not 0 <= start < end <= len(data) or not 1 <= value["start_line"] <= value["end_line"]:
            raise ValueError("Invalid JS span bounds")
        start_character = len(data[:start].decode("utf-8"))
        end_character = len(data[:end].decode("utf-8")) - 1
        data[start:end].decode("utf-8")
        if (value["start_line"] != bisect_right(line_starts, start_character) or
                value["end_line"] != bisect_right(line_starts, end_character)):
            raise ValueError("Invalid JS span line coordinates")

    def resolution(value):
        _fields(value, "state symbol_ids external reason", "JSResolution")
        state, local = value["state"], value["symbol_ids"]
        if (state not in {"local", "external", "unresolved", "dynamic"} or
                not isinstance(local, list) or local != sorted(set(local)) or
                any(identity not in ids for identity in local) or not isinstance(value["reason"], str)):
            raise ValueError("Invalid JS resolution")
        if state == "local":
            if not local or value["external"] is not None:
                raise ValueError("Invalid local JS resolution")
        elif local or (state == "external" and not isinstance(value["external"], str)) or (
                state in {"unresolved", "dynamic"} and (value["external"] is not None or not value["reason"])):
            raise ValueError("Invalid nonlocal JS resolution")

    for symbol in symbols["symbols"]:
        text(symbol["name"])
        count(symbol["flags"])
        if not isinstance(symbol["declarations"], list) or not symbol["declarations"]:
            raise ValueError("JS symbol requires declarations")
        descriptors = []
        for declaration in symbol["declarations"]:
            _fields(declaration, "path source_sha256 span kind lexical_scope name token_context occurrence", "JSDeclaration")
            span(declaration["path"], declaration["span"])
            if declaration["source_sha256"] != entries[declaration["path"]]["sha256"]:
                raise ValueError("JS declaration source mismatch")
            text(declaration["kind"])
            text(declaration["name"])
            count(declaration["occurrence"])
            if not isinstance(declaration["lexical_scope"], list) or not isinstance(declaration["token_context"], list):
                raise ValueError("Invalid JS declaration context")
            for name in declaration["lexical_scope"]:
                text(name)
            for token in declaration["token_context"]:
                _fields(token, "kind text", "JS token")
                text(token["kind"])
                text(token["text"])
            descriptors.append({key: declaration[key] for key in (
                "path", "kind", "lexical_scope", "name", "token_context", "occurrence")})
        _same(symbol["id"], digest(["js-symbol-v1", sorted(descriptors, key=_json_bytes)]),
              "JS source-backed symbol ID")
    for name in ("exports", "aliases", "references", "module_references", "outside_model", "directives"):
        for row in symbols[name]:
            span(row["path"], row["span"], metadata=name == "outside_model")
            if "target" in row:
                resolution(row["target"])
    enums = {"exports": {"declaration", "default", "reexport", "star", "commonjs"},
             "aliases": {"import", "reexport", "namespace", "import-equals"},
             "references": {"identifier", "property", "shorthand", "type", "alias", "export", "namespace-element"},
             "outside_model": {"computed-import", "reflection", "runtime-command"},
             "directives": {"ts-ignore", "ts-expect-error", "ts-nocheck", "ts-check", "other-suppression"}}
    for name, kinds in enums.items():
        for row in symbols[name]:
            if row["kind"] not in kinds:
                raise ValueError("Invalid JS " + name + " kind")
            for key in ("name", "text", "reason"):
                if key in row:
                    text(row[key])
            if name == "exports" and type(row["type_only"]) is not bool:
                raise ValueError("Invalid JS type-only export")
    for item in syntax:
        if any(not isinstance(value, str) for value in item["diagnostics"]):
            raise ValueError("Invalid JS syntax diagnostic strings")
        for key, fields in (("nodes", "kind span"), ("literal_imports", "specifier kind span"),
                            ("outside_model", "kind span reason")):
            for row in item[key]:
                _fields(row, fields, "JS syntax " + key)
                span(item["path"], row["span"])
                for field in fields.split():
                    if field != "span":
                        text(row[field])
    for row in symbols["module_references"]:
        if (row["kind"] not in {"import", "reexport", "require", "type-import"} or
                row["resolution"] not in {"local", "external", "unresolved", "dynamic"} or
                not isinstance(row["targets"], list) or row["targets"] != sorted(set(row["targets"])) or
                any(name not in entries for name in row["targets"]) or not isinstance(row["reason"], str)):
            raise ValueError("Invalid JS module reference")
        if ((row["resolution"] == "local") != bool(row["targets"]) or
                (row["resolution"] == "external") != (isinstance(row["external"], str) and bool(row["external"]))):
            raise ValueError("Invalid JS module resolution")
        if row["resolution"] == "dynamic":
            if row["specifier"] is not None or row["external"] is not None or not row["reason"]:
                raise ValueError("Invalid dynamic JS module")
        elif not isinstance(row["specifier"], str) or not row["specifier"]:
            raise ValueError("Invalid literal JS module")
        if row["resolution"] != "external" and row["external"] is not None:
            raise ValueError("Invalid JS external module target")
    inputs = {(row["scope"], row["path"]): row for row in symbols["inputs"]}

    def message(value):
        _fields(value, "text category code next", "JSMessage")
        text(value["text"])
        count(value["code"])
        if type(value["category"]) is not int or value["category"] not in {0, 1, 2, 3} or not isinstance(value["next"], list):
            raise ValueError("Invalid JS diagnostic message")
        for child in value["next"]:
            message(child)

    def location(value):
        _fields(value, "file utf16_start utf16_length byte_range", "JSLocation")
        if value["file"] is None:
            if any(item is not None for item in value.values()):
                raise ValueError("Invalid source-less JS location")
            return
        ref = value["file"]
        _fields(ref, "scope path sha256 bytes", "JS diagnostic input")
        if ref["scope"] not in {"subject", "tool-resource"} or inputs.get((ref["scope"], ref["path"])) != ref:
            raise ValueError("Unadmitted JS diagnostic input")
        count(value["utf16_start"])
        count(value["utf16_length"])
        byte_range = value["byte_range"]
        _fields(byte_range, "start_byte end_byte start_line end_line", "JSRange")
        for number in byte_range.values():
            count(number)
        if not (byte_range["start_byte"] <= byte_range["end_byte"] <= ref["bytes"] and
                1 <= byte_range["start_line"] <= byte_range["end_line"]):
            raise ValueError("Invalid JS diagnostic range")

    diagnostic_ids = [row["id"] for row in symbols["diagnostics"]]
    if diagnostic_ids != sorted(set(diagnostic_ids)):
        raise ValueError("Unordered JS diagnostics")
    for diagnostic in symbols["diagnostics"]:
        count(diagnostic["code"])
        if type(diagnostic["category"]) is not int or diagnostic["category"] not in {0, 1, 2, 3}:
            raise ValueError("Invalid JS diagnostic category")
        if diagnostic["source"] is not None:
            text(diagnostic["source"])
        message(diagnostic["message"])
        location(diagnostic["location"])
        if not isinstance(diagnostic["related"], list):
            raise ValueError("Invalid JS related diagnostics")
        for related in diagnostic["related"]:
            _fields(related, "code category message location", "JS related diagnostic")
            count(related["code"])
            if type(related["category"]) is not int or related["category"] not in {0, 1, 2, 3}:
                raise ValueError("Invalid JS related category")
            message(related["message"])
            location(related["location"])
        _same(diagnostic["id"], digest({key: value for key, value in diagnostic.items() if key != "id"}),
              "JS diagnostic ID")
    for row in symbols["entrypoints"]:
        relative_name(row["path"])
        if row["state"] not in {"active", "absent-at-revision"} or not isinstance(row["origins"], list) or not row["origins"]:
            raise ValueError("Invalid JS entrypoint")
        if row["state"] == "active":
            if row["path"] not in entries or row["source_sha256"] != entries[row["path"]]["sha256"]:
                raise ValueError("Invalid active JS entrypoint")
        elif row["path"] in entries or row["source_sha256"] is not None:
            raise ValueError("Invalid absent JS entrypoint")
        if not isinstance(row["public_exports"], list) or row["public_exports"] != sorted(set(row["public_exports"])):
            raise ValueError("Invalid public JS exports")
        for origin in row["origins"]:
            _fields(origin, "kind input pointer origin_ref", "JS entrypoint origin")
            if origin["kind"] not in {"package", "suite", "config"} or origin["input"] not in symbols["inputs"]:
                raise ValueError("Unadmitted JS entrypoint origin")
            text(origin["pointer"])
            text(origin["origin_ref"])


def _js_manifest(context, config, inventories=None, *, phase=None):
    """Reconstruct each finite predecessor, never follow a supplied manifest chain."""
    active = phase or context["output_manifest"]["path"]
    if active not in {"js-preflight.json", "js-produced.json", "manifest.json"}:
        raise ValueError("Invalid active JS manifest")
    if inventories is None:
        inventories = [_js_json(context, _js_name(rev, "request"))[1]["inventory"] for rev in ("base", "head")]
    reserved = _js_reservations(inventories, config)
    rows = [{"artifact": ref, "role": "qualification", "revision": None}
            for ref in _js_qualifications(config)]
    for row in rows:
        _js_bytes(context, row["artifact"])

    def document():
        return {"run_id": context["run_id"], "root": str(root_path(context["run_root"])),
                "inputs": sorted(rows, key=lambda row: row["artifact"]["path"]), "reserved_outputs": reserved}

    def predecessor(name):
        ref, value = _js_json(context, name)
        _same(value, document(), "JS predecessor " + name)
        _same(_js_bytes(context, ref), _json_bytes(value), "Canonical JS manifest bytes")
        rows.append({"artifact": ref, "role": "manifest", "revision": None})

    if active != "js-preflight.json":
        predecessor("js-preflight.json")
        transports = []
        for inv in inventories:
            transport = _js_transport(context, inv, config)
            transports.append(transport)
            _, command, _, _, request_ref, command_ref = transport
            rows += [{"artifact": ref, "role": "command", "revision": inv["revision"]}
                     for ref in (request_ref, command_ref)]
            rows += [{"artifact": command[slot], "role": "syntax", "revision": inv["revision"]}
                     for slot in ("result", "symbols") if command[slot] is not None]
        if active == "manifest.json":
            predecessor("js-produced.json")
            python_parser = parser_digest()
            for inv, transport in zip(inventories, transports):
                result = transport[2]
                syntax_paths = [item["path"] for item in result["syntax"]] if result is not None else []
                for entry in inv["entries"]:
                    if entry["language"] != "python":
                        continue
                    try:
                        _syntax(input_path(context[inv["revision"] + "_root"], entry["path"]).read_bytes(),
                                entry, inv, python_parser)
                        syntax_paths.append(entry["path"])
                    except (OSError, ValueError, SyntaxError, UnicodeError, LookupError, RecursionError):
                        continue
                rows += [{"artifact": artifact(context["run_root"], syntax_name(inv["revision"], name)),
                          "role": "syntax", "revision": inv["revision"]} for name in sorted(syntax_paths)]
                rows.append({"artifact": artifact(context["run_root"], graph_name(inv["revision"])),
                             "role": "graph", "revision": inv["revision"]})
    expected = document()
    if phase is None:
        ref = context["output_manifest"]
        _same(ref, artifact(context["run_root"], active), "Active JS manifest")
        _same(load_json(_js_bytes(context, ref)), expected, "JS manifest ownership")
        _same(_js_bytes(context, ref), _json_bytes(expected), "Canonical active JS manifest")
    owned = {row["artifact"]["path"] for row in rows}
    for row in rows:
        if row["artifact"]["path"] not in reserved:
            raise ValueError("Unreserved JS ownership")
        _js_bytes(context, row["artifact"])
    if active == "manifest.json":
        for name in reserved:
            if name != active and name not in owned and input_path(context["run_root"], name).exists():
                raise ValueError("Populated absent JS output slot")
        for directory, dirs, files in os.walk(context["run_root"], followlinks=False):
            for name in dirs + files:
                relative = (Path(directory) / name).relative_to(context["run_root"]).as_posix()
                input_path(context["run_root"], relative)
                if name in files and relative not in owned | {active}:
                    raise ValueError("Unplanned JS output: " + relative)
    return expected


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


def _graph(inventory, syntax, config, js_modules=()):
    paths = {entry["path"] for entry in inventory["entries"]}
    graph = {"schema_version": 1, "inventory_sha256": inventory["digest"],
             "nodes": sorted(paths), "edges": [], "unresolved": [], "outside_model": [], "cycles": []}
    for source, evidence in sorted(syntax.items()):
        for item in evidence["literal_imports"]:
            if evidence["semantic_version"] == JS_SEMANTICS:
                matches = [row for row in js_modules if row["path"] == source and
                           all(row[key] == item[key] for key in ("span", "kind", "specifier"))]
                if len(matches) != 1:
                    raise ValueError("JS literal import lacks exactly one module reference")
                row = matches[0]
                targets = ([(name, "local") for name in row["targets"]] if row["resolution"] == "local"
                           else [(row["external"], "external")] if row["resolution"] == "external" else [])
                error = row["reason"] if row["resolution"] in {"unresolved", "dynamic"} else None
                if not targets and not error:
                    raise ValueError("Invalid JS literal module resolution")
            else:
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
    js = None
    if "typescript" in config["tools"]:
        if context["output_manifest"]["path"] not in {"js-produced.json", "manifest.json"}:
            raise ValueError("JS graph requires produced ownership")
        _js_manifest(context, config)
        js = _js_transport(context, inventory, config)
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
        elif js is not None and entry["suffix"] in JS_EXT:
            _, command, result, symbols, _, command_ref = js
            if (entry["language"] != ("typescript" if entry["suffix"] in {".ts", ".tsx"} else "javascript") or
                    entry["parse_state"] != "pending"):
                raise ValueError("JS inventory classification mismatch")
            receipt.update(adapter="typescript-compiler", semantic_version=JS_SEMANTICS)
            refs = [command[slot] for slot in ("result", "symbols") if command[slot] is not None]
            if _js_output_action(command) == "nonzero-opaque":
                receipt.update(state="failed", reason="js-command-nonzero " + str(command["returncode"]),
                               raw=[command_ref, *refs])
            else:
                row = next(row for row in symbols["files"] if row["path"] == entry["path"])
                receipt.update(state=row["state"], reason=row["reason"], raw=refs)
                if row["state"] == "processed":
                    value = next(value for value in result["syntax"] if value["path"] == entry["path"])
                    syntax[entry["path"]] = value
                    receipt["unit_count"] = len(value["literal_imports"])
        receipts.append(receipt)
    graph = _graph(inventory, syntax, config, js[3]["module_references"] if js and js[3] is not None else ())
    if js and js[3] is not None:
        for site in js[3]["outside_model"]:
            if site not in graph["outside_model"]:
                graph["outside_model"].append(site)
    cycle_error = None
    try:
        graph["cycles"] = enumerate_cycles(graph)
    except ValueError as error:
        cycle_error = str(error)
    return receipts, syntax, graph, cycle_error


def _raw(context, inventory, receipts, syntax_refs, graph, config=None):
    commands, qualified = [], list(syntax_refs.values())
    enabled = config is not None and "typescript" in config["tools"]
    if enabled:
        _, command, _, _, _, command_ref = _js_transport(context, inventory, config)
        commands = [command_ref]
        qualified += [command[slot] for slot in ("result", "symbols") if command[slot] is not None]
    return {"schema_version": 1, "run_id": context["run_id"], "revision": inventory["revision"],
            "inventory_sha256": inventory["digest"], "source_sha256": inventory["source_sha256"],
            "adapter": "python-ast-typescript" if enabled else "python-ast",
            "semantic_version": MIXED_SEMANTICS if enabled else SEMANTICS,
            "toolset_sha256": context["toolset_sha256"], "policy_sha256": context["policy_sha256"],
            "receipts": receipts, "commands": commands, "qualified_raw": qualified,
            "payload": {"graph": graph}}


def parse_files(context, inventory, config):
    receipts, syntax, graph, _ = _parse(context, inventory, config)
    refs = {name: persist(context, syntax_name(inventory["revision"], name), value)
            for name, value in sorted(syntax.items())}
    for receipt in receipts:
        if receipt["path"] in refs:
            receipt["raw"] = [refs[receipt["path"]], *receipt["raw"]]
    persist(context, graph_name(inventory["revision"]), _raw(context, inventory, receipts, refs, graph, config))
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
    commands = []
    enabled = "typescript" in config["tools"]
    if enabled:
        _, command, _, _, _, command_ref = _js_transport(context, inv, config)
        commands = [command_ref]
        if _js_output_action(command) == "nonzero-opaque":
            reasons.append("js-command-nonzero " + str(command["returncode"]))
    if inv["enumeration_state"] != "complete":
        reasons.append("Inventory enumeration failed")
    if graph["unresolved"]:
        reasons.append("Unresolved literal local imports")
    if cycle_error:
        reasons.append(cycle_error)
    findings = evaluate_rules(graph, config["architecture_rules"])
    common = {"schema_version": 1, "revision": inv["revision"], "run_id": context["run_id"],
              "source_sha256": inv["source_sha256"], "inventory_sha256": inv["digest"],
              "semantic_version": MIXED_SEMANTICS if enabled else SEMANTICS,
              "toolset_sha256": context["toolset_sha256"],
              "policy_sha256": context["policy_sha256"], "receipts": parsed["receipts"],
              "outside_model": graph["outside_model"], "commands": commands,
              "raw": [artifact(context["run_root"], graph_name(inv["revision"]))], "reasons": reasons,
              "state": "partial" if reasons else "complete"}
    return [{**common, "metric": "cycles", "value": None if cycle_error else len(graph["cycles"]),
             "findings": []},
            {**common, "metric": "architecture_rules", "value": len(findings), "findings": findings}]


def validate_evidence(context, parsed, config, raw, artifacts):
    """Reparse exact source bytes and compare every receipt/syntax/graph field."""
    if "typescript" in config["tools"]:
        raise ValueError("JS semantic acceptance requires measure.validate_observations")
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


def _checked_js_parsed(context, parsed, config):
    manifest = _js_manifest(context, config)
    inv = parsed["inventory"]
    receipts, syntax, graph_value, _ = _parse(context, inv, config)
    refs = {}
    for name, value in sorted(syntax.items()):
        ref = artifact(context["run_root"], syntax_name(inv["revision"], name))
        _same(read_owned(context, manifest, ref, "syntax", inv["revision"]), value, "JS/Python syntax")
        refs[name] = ref
    for receipt in receipts:
        if receipt["path"] in refs:
            receipt["raw"] = [refs[receipt["path"]], *receipt["raw"]]
    _same(parsed, {"inventory": inv, "receipts": receipts, "syntax_artifacts": refs, "graph": graph_value},
          "Reconstructed JS parsed inventory")
    raw_ref = artifact(context["run_root"], graph_name(inv["revision"]))
    _same(read_owned(context, manifest, raw_ref, "graph", inv["revision"]),
          _raw(context, inv, receipts, refs, graph_value, config), "Reconstructed mixed raw")
    return syntax


def _compare_js_replay(original_context, original_parsed, replay_context, replay_parsed, config):
    original = _js_transport(original_context, original_parsed["inventory"], config, purpose="produce")
    replay = _js_transport(replay_context, replay_parsed["inventory"], config, purpose="validate")
    if (original_context["run_root"] == replay_context["run_root"] or
            original[0]["execution_id"] == replay[0]["execution_id"]):
        raise ValueError("Fresh independently allocated JS replay required")
    for key in ("binding", "inventory", "config", "inputs"):
        _same(original[0][key], replay[0][key], "JS replay " + key)
    action = _js_output_action(original[1])
    _same(action, _js_output_action(replay[1]), "JS replay outcome")
    if action == "nonzero-opaque":
        def failure(command):
            return {"reason_code": "js-command-nonzero", "returncode": command["returncode"],
                    "stderr_present": command["stderr"] != "", "result_present": command["result"] is not None,
                    "symbols_present": command["symbols"] is not None}
        _same(failure(original[1]), failure(replay[1]), "JS failed replay operands")
    else:
        _same(original[3], replay[3], "JS replay symbol semantics")
        for key in ("binding", "state", "provenance", "syntax", "reasons"):
            _same(original[2][key], replay[2][key], "JS replay result " + key)
    _same(_checked_js_parsed(original_context, original_parsed, config),
          _checked_js_parsed(replay_context, replay_parsed, config), "JS replay syntax semantics")
    _same(original_parsed["graph"], replay_parsed["graph"], "JS replay graph")
    _same([{key: value for key, value in row.items() if key != "raw"} for row in original_parsed["receipts"]],
          [{key: value for key, value in row.items() if key != "raw"} for row in replay_parsed["receipts"]],
          "JS replay receipt semantics")
    original_obs, replay_obs = (observations(context, parsed, config) for context, parsed in (
        (original_context, original_parsed), (replay_context, replay_parsed)))
    for left, right in zip(original_obs, replay_obs):
        _same({key: value for key, value in left.items() if key not in {"commands", "raw", "receipts"}},
              {key: value for key, value in right.items() if key not in {"commands", "raw", "receipts"}},
              "JS replay observation semantics")
