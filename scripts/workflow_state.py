"""Strict workflow persistence and materialized inputs for the I/O-free gate.

Paths in persisted records are repository-relative. Receipt IDs name immutable
``.ai/<slug>/evidence/receipts/<id>.json`` files. Resolved views are never JSON
records; only their target GuardSnapshot may be written into an event.
"""

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re

from evidence import source_snapshot, write_json_atomic


class SequenceConflict(RuntimeError):
    """The caller's already-held lock did not protect its expected ledger."""


@dataclass(frozen=True)
class ReceiptObservation:
    status: str
    document: dict | None
    observed_sha256: str | None
    artifacts: dict
    reason: str


@dataclass(frozen=True)
class ResolvedLedger:
    document: dict
    receipts: dict[str, ReceiptObservation]


@dataclass(frozen=True)
class BlockedInput:
    reason: str


@dataclass(frozen=True)
class ResolvedInputs:
    target: dict
    targets: dict[str, dict | BlockedInput]


def canonical_hash(value):
    """Match evidence.py's sorted UTF-8 JSON convention, including final LF."""
    content = json.dumps(value, ensure_ascii=False, allow_nan=False,
                         sort_keys=True, separators=(",", ":")) + "\n"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _text(value):
    if not isinstance(value, str) or not value.strip() or "\0" in value:
        raise ValueError("Expected nonempty text")


def _string(value):
    if not isinstance(value, str) or "\0" in value:
        raise ValueError("Expected string")


def _id(value):
    _text(value)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise ValueError("Invalid ID: " + value)


def _slug(value):
    _text(value)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError("Invalid slug")


def _hash(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Expected lowercase SHA-256")


def _commit(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("Expected full commit SHA")


def _integer(value):
    if type(value) is not int:
        raise ValueError("Expected integer, not boolean")


def _natural(value):
    _integer(value)
    if value < 0:
        raise ValueError("Expected nonnegative integer")


def _positive(value):
    _integer(value)
    if value < 1:
        raise ValueError("Expected positive integer")


def _number(value):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError("Expected finite number")


def _duration(value):
    _number(value)
    if value <= 0:
        raise ValueError("Expected positive duration")


def _boolean(value):
    if type(value) is not bool:
        raise ValueError("Expected boolean")


def _enum(*choices):
    def check(value):
        if not isinstance(value, str) or value not in choices:
            raise ValueError("Expected one of " + ", ".join(choices))
    return check


def _nullable(check):
    def validate(value):
        if value is not None:
            check(value)
    return validate


def _list(check, *, nonempty=False, unique=False):
    def validate(value):
        if not isinstance(value, list) or (nonempty and not value):
            raise ValueError("Expected list" + (" with entries" if nonempty else ""))
        for item in value:
            check(item)
        if unique and len({canonical_hash(item) for item in value}) != len(value):
            raise ValueError("Duplicate list entry")
    return validate


def _map(check, key_check=_id):
    def validate(value):
        if not isinstance(value, dict):
            raise ValueError("Expected mapping")
        for key, item in value.items():
            key_check(key)
            check(item)
    return validate


def _record(value, fields, optional=()):
    if not isinstance(value, dict) or set(value) - set(fields) or set(fields) - set(value) - set(optional):
        raise ValueError("Invalid record fields; expected " + ", ".join(fields))
    for key, item in value.items():
        try:
            fields[key](item)
        except ValueError as error:
            raise ValueError("%s: %s" % (key, error)) from error


def _version(version):
    def validate(value):
        _integer(value)
        if value != version:
            raise ValueError("Unknown schema version")
    return validate


def _time(value):
    _text(value)
    if not value.endswith(("Z", "+00:00")):
        raise ValueError("Expected UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Invalid timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("Expected timezone-aware UTC timestamp")


def path_name(value, *, directory=False):
    _text(value)
    name = value.replace("\\", "/")
    if directory and name == ".":
        return name
    if (name.startswith("/") or PureWindowsPath(name).drive or
            any(part in ("", ".", "..") or ":" in part for part in name.split("/"))):
        raise ValueError("Unsafe repository-relative path: " + value)
    return name


def _path(value):
    path_name(value)


def safe_path(root, name):
    """Reject links (including internal links), junctions and traversal before I/O."""
    name = path_name(name, directory=True)
    root = Path(root).resolve(strict=True)
    path = root / name
    resolved = path.resolve()
    if not resolved.is_relative_to(root) or os.path.normcase(str(resolved)) != os.path.normcase(os.path.abspath(path)):
        raise ValueError("Linked or escaping path: " + name)
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink() or parent.is_junction():
            raise ValueError("Linked path: " + name)
    return path


def read_json(path):
    return _decode_json(Path(path).read_bytes())


def _decode_json(content):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(value):
        raise ValueError("Nonfinite JSON number: " + value)

    def number(value):
        parsed = float(value)
        _number(parsed)
        return parsed

    return json.loads(content.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=constant, parse_float=number)


def validate_scope(value):
    _record(value, {"files": _list(_path, unique=True),
                    "directories": _list(lambda v: path_name(v, directory=True), unique=True),
                    "excluded_outputs": _list(_exclusion, unique=True)})
    paths = [path_name(item["path"]) for item in value["excluded_outputs"]]
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate excluded output")
    for key in ("files", "directories"):
        names = [path_name(v, directory=key == "directories") for v in value[key]]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate normalized path")


def _exclusion(value):
    _record(value, {"path": _path, "reason": _text})


def _file(value):
    _record(value, {"sha256": _nullable(_hash), "mode": _enum("file", "executable", "missing")})
    if (value["mode"] == "missing") != (value["sha256"] is None):
        raise ValueError("Missing file/hash mismatch")


def validate_source(value):
    _record(value, {"binding_mode": _enum("standalone-source"), "base": _nullable(_commit),
                    "head": _nullable(_commit), "scope": validate_scope,
                    "files": _map(_file, _path), "scope_sha256": _hash})
    if canonical_hash({"scope": value["scope"], "files": value["files"]}) != value["scope_sha256"]:
        raise ValueError("Source snapshot hash mismatch")


def validate_binding(value):
    _record(value, {"binding_mode": _enum("guarded"), "adopted_contract_sha256": _hash,
                    "components": _map(_hash), "actions": _map(_hash),
                    "checks": _map(_hash), "claims": _map(_hash)})


def validate_snapshot(value):
    _record(value, {"source": validate_source, "contract": validate_binding})


ROLES = ("implementer", "researcher", "verifier", "reviewer", "human")


def validate_producer(value):
    _record(value, {"actor_id": _text, "context_id": _text, "role": _enum(*ROLES),
                    "host": _text, "model": _text})


def validate_command(value):
    _record(value, {"argv": _list(_text, nonempty=True),
                    "cwd": lambda v: path_name(v, directory=True),
                    "runtime": lambda v: _record(v, {"executable": _text, "observed_version": _text}),
                    "idle_seconds": _duration, "max_seconds": _duration,
                    "environment": _map(_nullable(_string), _text)})
    if any(Path(arg.replace("\\", "/")).name == "workflow.py" for arg in value["argv"]):
        raise ValueError("Reentrant workflow commands are not supported")
    if any("*" in arg or "?" in arg for arg in value["argv"]) and "--test" in value["argv"]:
        raise ValueError("Unresolved native test glob")
    if any("=" in key for key in value["environment"]):
        raise ValueError("Invalid environment name")


def validate_target(value):
    _record(value, {"kind": _enum("action", "check", "increment", "ship"), "id": _id})
    if value["kind"] == "ship" and value["id"] != "ship":
        raise ValueError("Ship target ID must be ship")


def target_key(target):
    return target["kind"] + ":" + target["id"]


def target(kind, name):
    return {"kind": kind, "id": name}


def _assertion(value):
    _record(value, {"id": _id, "test_file": _path, "test_name": _text, "source_sha256": _hash,
                    "assertion_lines": _list(_positive, nonempty=True, unique=True), "purpose": _text,
                    "expected_red": lambda v: _record(v, {"operator": _text,
                        "expected_relation": _string, "actual_relation": _string})})


def _increment(value):
    _record(value, {"id": _id, "acs": _list(_id, nonempty=True, unique=True),
                    "components": _list(_id, nonempty=True, unique=True),
                    "requires": _list(validate_target, unique=True),
                    "implementers": _list(validate_producer, nonempty=True, unique=True)})
    if any(p["role"] != "implementer" for p in value["implementers"]):
        raise ValueError("Increment implementers must have implementer role")


def _action(value):
    _record(value, {"id": _id, "increment": _id, "kind": _enum("work", "check", "retire"),
                    "requires": _list(validate_target, unique=True),
                    "command": _nullable(validate_command), "owner": validate_producer,
                    "inputs": validate_scope, "components": _list(_id, unique=True),
                    "claims": _list(_id, unique=True), "declared_changes": _list(_path, unique=True),
                    "retirement": _nullable(lambda v: _record(v, {"legacy_scope": validate_scope,
                        "expected_legacy_presence": _list(_path, nonempty=True, unique=True)}))})
    if (value["kind"] == "retire") != (value["retirement"] is not None):
        raise ValueError("Retirement data is required only for retire actions")
    if value["kind"] != "check" and value["command"] is None:
        raise ValueError("Work requires an executable command")


def _check(value):
    _record(value, {"id": _id, "action_id": _id, "acs": _list(_id, nonempty=True, unique=True),
                    "kind": _enum("test", "behavioral-red", "metrics", "verification",
                                  "review", "compatibility", "research", "human"),
                    "owner_role": _enum(*ROLES), "context_rule": _enum("same-allowed", "independent"),
                    "validity": _enum("current", "before-action"),
                    "assertions": _list(_assertion), "pass_condition": _text,
                    "handoff_steps": _list(_text)})
    if value["kind"] == "behavioral-red" and not value["assertions"]:
        raise ValueError("Behavioral red requires assertion targets")
    if value["kind"] in ("verification", "review"):
        role = "verifier" if value["kind"] == "verification" else "reviewer"
        if value["context_rule"] != "independent" or value["owner_role"] != role:
            raise ValueError("Verification/review require independent assigned roles")


def _artifact_ref(value):
    _record(value, {"path": _path, "sha256": _hash})


def _receipt_ref(value):
    _record(value, {"id": _id, "sha256": _hash})


def _receipt_refs(value):
    _list(_receipt_ref)(value)
    if len({ref["id"] for ref in value}) != len(value):
        raise ValueError("Duplicate receipt reference ID")


def _disposition(value):
    _record(value, {"finding_id": _id, "path": _path, "sha256": _hash})


def _anchor(value):
    _text(value)
    if value.count("#") != 1:
        raise ValueError("Expected report path#heading anchor")
    path, anchor = value.split("#")
    _path(path)
    _id(anchor)


def _json_data(value):
    # Scoped research query details are descriptive data, never executable code.
    if not isinstance(value, dict) or not value:
        raise ValueError("Expected nonempty research scope mapping")
    canonical_hash(value)


def _claim(value):
    _record(value, {"claim_id": _id, "report": _anchor, "claim_sha256": _hash,
                    "epistemic": _enum("FACT", "INFERENCE", "HYPOTHESIS", "UNKNOWN"),
                    "scope": _json_data,
                    "source_refs": _list(lambda v: _record(v, {"path": _path, "sha256": _hash,
                        "lines": _list(_positive, nonempty=True, unique=True), "snippet_ref": _text})),
                    "supersedes": _list(_id, unique=True), "correction_owner": validate_producer,
                    "acceptance_owner": validate_producer, "accepted_receipt": _nullable(_id)})
    if value["correction_owner"]["role"] != "researcher":
        raise ValueError("Research correction requires researcher")


def dependencies(contract, item, *, members=True):
    """The only derived graph: check -> action; action admission != closure."""
    kind, name = item["kind"], item["id"]
    if kind == "ship":
        return [target("increment", key) for key in contract["increments"]]
    if kind == "check":
        return [target("action", contract["checks"][name]["action_id"])]
    if kind == "increment":
        result = list(contract["increments"][name]["requires"])
        if members:
            result += [target("action", a["id"]) for a in contract["actions"].values()
                       if a["increment"] == name]
        return result
    action = contract["actions"][name]
    return list(action["requires"]) + [
        t for t in contract["increments"][action["increment"]]["requires"] if t["kind"] == "increment"]


def dependency_closure(contract, item):
    result, visiting = {}, set()

    def visit(node):
        key = target_key(node)
        if key in visiting:
            raise ValueError("Dependency cycle: " + key)
        if key in result:
            return
        visiting.add(key)
        for dependency in dependencies(contract, node):
            visit(dependency)
        visiting.remove(key)
        result[key] = node
    visit(item)
    return result


def validate_contract(value):
    _record(value, {"schema_version": _version(1), "slug": _slug, "design_revision": _id,
                    "increments": _map(_increment), "actions": _map(_action),
                    "checks": _map(_check), "claims": _map(_claim), "revision_reason": _text})
    if not value["increments"]:
        raise ValueError("Workflow needs increments")
    for table in ("increments", "actions", "checks", "claims"):
        for key, record in value[table].items():
            if record["claim_id" if table == "claims" else "id"] != key:
                raise ValueError("Record ID mismatch")
    check_actions = [c["action_id"] for c in value["checks"].values()]
    actual = [a["id"] for a in value["actions"].values() if a["kind"] == "check"]
    if len(check_actions) != len(set(check_actions)) or set(check_actions) != set(actual):
        raise ValueError("Orphan or duplicate check action")
    for table, kinds in (("increments", ("increment", "check")), ("actions", ("action", "check"))):
        for record in value[table].values():
            for ref in record["requires"]:
                if ref["kind"] not in kinds or ref["id"] not in value[ref["kind"] + "s"]:
                    raise ValueError("Unknown or forbidden requires target")
    for action in value["actions"].values():
        if action["increment"] not in value["increments"]:
            raise ValueError("Unknown action increment")
        increment = value["increments"][action["increment"]]
        if set(action["components"]) - set(increment["components"]):
            raise ValueError("Action component is outside increment")
        if set(action["claims"]) - set(value["claims"]):
            raise ValueError("Unknown research claim")
        if (action["kind"] in ("work", "retire") or action["owner"]["role"] == "implementer") and (
                action["owner"] not in increment["implementers"]):
            raise ValueError("Work owner is not a declared implementer")
        if action["kind"] == "retire" and not any(
                ref["kind"] == "check" and value["checks"][ref["id"]]["kind"] == "compatibility"
                and value["checks"][ref["id"]]["validity"] == "before-action" for ref in action["requires"]):
            raise ValueError("Retirement requires earlier compatibility")
    for check in value["checks"].values():
        action = value["actions"][check["action_id"]]
        if action["owner"]["role"] != check["owner_role"]:
            raise ValueError("Check owner role mismatch")
        if (action["command"] is None) != bool(check["handoff_steps"]):
            raise ValueError("Handoff steps belong only to null-command checks")
        if check["validity"] == "before-action":
            consumers = [a for a in value["actions"].values() if a["kind"] in ("work", "retire")
                         and target("check", check["id"]) in a["requires"]]
            if len(consumers) != 1:
                raise ValueError("Before-action check needs exactly one consumer")
    for increment in value["increments"].values():
        checks = [value["checks"][ref["id"]] for ref in increment["requires"] if ref["kind"] == "check"]
        owned = [c for c in checks if value["actions"][c["action_id"]]["increment"] == increment["id"]]
        if not {"verification", "review", "metrics"} <= {c["kind"] for c in owned}:
            raise ValueError("Missing mandatory closure checks")
        proven = {ac for c in checks if c["kind"] in ("test", "compatibility", "verification") for ac in c["acs"]}
        if set(increment["acs"]) - proven:
            raise ValueError("Missing closure scenario proof")
    for claim in value["claims"].values():
        if set(claim["supersedes"]) - set(value["claims"]):
            raise ValueError("Missing superseded claim history")
    _validate_claim_cycles(value["claims"])
    dependency_closure(value, target("ship", "ship"))


def _validate_claim_cycles(claims):
    done, active = set(), set()

    def visit(name):
        if name in active:
            raise ValueError("Research supersession cycle")
        if name in done:
            return
        active.add(name)
        for old in claims[name]["supersedes"]:
            visit(old)
        active.remove(name)
        done.add(name)
    for name in claims:
        visit(name)


FINDING_VERDICTS = ("VERIFIED", "VERIFIED-WITH-LIMITATIONS", "NOT-VERIFIED", "BLOCKED")


def validate_finding(value):
    _record(value, {"kind": _enum("verification", "review", "research", "human"),
                    "verdict": _enum(*FINDING_VERDICTS),
                    "scenarios": _map(lambda v: _record(v, {"verdict": _enum(*FINDING_VERDICTS),
                        "evidence_refs": _list(_path), "reason": _string})),
                    "findings": _list(lambda v: _record(v, {"id": _id, "location": _text,
                        "observation": _text, "blocking": _boolean, "evidence_refs": _list(_path)})),
                    "source_artifact": _artifact_ref, "disposition_refs": _list(_disposition),
                    "human_confirmation": _enum("confirmed", "unconfirmed", "not-applicable")})
    ids = [f["id"] for f in value["findings"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate finding ID")


def validate_native(value):
    def test(record):
        _record(record, {"file": _text, "line": _positive, "name": _text, "nesting": _natural,
                         "outcome": _enum("pass", "assertion-fail", "setup-error", "cancelled", "skipped", "todo"),
                         "error": lambda v: _record(v, {"name": _string, "code": _string,
                             "cause_code": _string, "message": _string, "assertion_stack": _string,
                             "operator": _nullable(_string), "expected": _string, "actual": _string})},
                optional=("error",))
    _record(value, {"schema_version": _version(1), "complete": _boolean,
                    "tests": _list(test), "leaf_count": _natural,
                    "logs": _list(lambda v: _record(v, {"stream": _enum("stdout", "stderr"), "text": _string}))})
    if value["leaf_count"] != len(value["tests"]):
        raise ValueError("Native leaf count mismatch")
    identities = [(t["file"], t["line"], t["name"], t["nesting"]) for t in value["tests"]]
    if len(set(identities)) != len(identities):
        raise ValueError("Duplicate native test identity")


def _measurement(value):
    _record(value, {"name": _id, "state": _enum("measured", "unavailable"),
                    "base": _nullable(_number), "head": _nullable(_number),
                    "comparison": _enum("ok", "warn", "fail", "unavailable"), "reason": _string,
                    "run_id": _id, "source": validate_source, "command": _nullable(validate_command),
                    "artifacts": _list(lambda v: _record(v, {"path": _path, "sha256": _hash, "bytes": _natural})),
                    "scope_support": _json_data})


def validate_metrics(value):
    def policy(record):
        _record(record, {"schema_version": _version(1), "required": _list(_id, nonempty=True, unique=True),
                         "rules": _map(lambda v: _record(v, {"mode": _enum("compare", "floor", "coverage"),
                             "threshold": _nullable(_number), "origin": _enum("built-in", "repo-source"),
                             "origin_ref": _text})), "sha256": _hash})
        if canonical_hash({key: record[key] for key in ("required", "rules")}) != record["sha256"]:
            raise ValueError("Metric policy hash mismatch")
    _record(value, {"schema_version": _version(2), "run_id": _id, "source": validate_source,
                    "baseline": _enum("compared", "greenfield", "unknown"),
                    "measurement_status": _enum("ok", "warn", "fail", "unavailable"),
                    "completeness": _enum("complete", "incomplete"),
                    "missing_required": _list(lambda v: _record(v, {"metric": _id, "reason": _text,
                        "owner": _text, "command_ref": _nullable(_text), "prerequisite": _text})),
                    "verdict": _enum("pass", "fail"), "metrics": _map(_measurement),
                    "unavailable": _list(_id, unique=True), "worst_status": _enum("ok", "warn", "fail", "unavailable"),
                    "policy": policy, "generated": _time})


def validate_receipt(value):
    def result(record):
        if not isinstance(record, dict):
            raise ValueError("Invalid receipt result")
        if "kind" in record:
            validate_finding(record)
        elif record.get("schema_version") == 2:
            validate_metrics(record)
        else:
            validate_native(record)
    _record(value, {"schema_version": _version(1), "id": _id, "check_id": _id, "run_id": _id,
                    "producer": validate_producer, "recorded_by": validate_producer,
                    "outcome": _enum("pass", "fail", "blocked", "unavailable"),
                    "inputs": validate_snapshot, "prerequisite_receipts": _receipt_refs,
                    "result": result,
                    "artifacts": _list(lambda v: _record(v, {"path": _path, "sha256": _hash,
                        "bytes": _natural, "media_type": _text})),
                    "started_at": _time, "finished_at": _time})
    if datetime.fromisoformat(value["finished_at"]) < datetime.fromisoformat(value["started_at"]):
        raise ValueError("Receipt finishes before it starts")
    paths = [path_name(a["path"]) for a in value["artifacts"]]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate receipt artifact")


def _process(value):
    _record(value, {"phase": _enum("launch-failed", "spawned", "direct-exited"),
                    "pid": _nullable(_positive), "process_group": _nullable(_positive),
                    "start_identity": _nullable(_text), "identity_evidence": _nullable(_artifact_ref),
                    "returncode": _nullable(_integer),
                    "cleanup": _enum("not-attempted", "best-effort-attempted", "unknown"),
                    "error": _nullable(_string)})
    if value["phase"] != "launch-failed" and value["pid"] is None:
        raise ValueError("Observed process requires actual PID")
    if value["phase"] == "spawned" and value["returncode"] is not None:
        raise ValueError("Spawn observation cannot assert a return code")
    if value["phase"] == "direct-exited" and value["returncode"] is None:
        raise ValueError("Direct exit requires observed return code")
    if value["phase"] == "launch-failed" and value["returncode"] == 0:
        raise ValueError("Failed launch cannot have a successful return code")


def validate_event(value):
    _record(value, {"seq": _positive,
                    "kind": _enum("adopted", "admitted", "launch-intent", "process-observed", "completed",
                                  "receipt-accepted", "closed", "interrupted", "recovered"),
                    "target": lambda v: _id(v) if isinstance(v, str) else validate_target(v),
                    "run_id": _id, "inputs": validate_snapshot,
                    "receipt_refs": _receipt_refs, "producer": validate_producer,
                    "outcome": _enum("ready", "awaiting-response", "executed", "pass", "fail",
                                     "blocked", "unavailable", "interrupted"),
                    "process": _nullable(_process), "child_exit": _nullable(_integer),
                    "spawned": _enum("yes", "no", "unknown"),
                    "completion_commit": _nullable(_commit), "time": _time, "reason": _string})
    if (value["kind"] == "adopted") != isinstance(value["target"], str):
        raise ValueError("Only adoption targets a design revision")
    if value["completion_commit"] is not None and value["kind"] != "closed":
        raise ValueError("Completion commit belongs only to closure")
    if (value["kind"] == "process-observed") != (value["process"] is not None):
        raise ValueError("Process observations belong only to process events")
    if value["kind"] == "receipt-accepted" and (
            value["target"]["kind"] != "check" or len(value["receipt_refs"]) != 1):
        raise ValueError("Receipt acceptance must target one check and one receipt")
    if value["kind"] == "closed" and value["target"]["kind"] not in ("increment", "ship"):
        raise ValueError("Only increments/ship can close")
    if value["kind"] == "process-observed":
        expected = "no" if value["process"]["phase"] == "launch-failed" else "yes"
        if value["spawned"] != expected:
            raise ValueError("Spawn state contradicts observed process")


def validate_ledger(value):
    _record(value, {"schema_version": _version(1), "slug": _slug, "events": _list(validate_event)})
    admitted, adopted, accepted, runs, lifecycle = {}, set(), set(), set(), {}
    adoption = None
    for seq, event in enumerate(value["events"], 1):
        if event["seq"] != seq:
            raise ValueError("Ledger sequence is not contiguous")
        kind, run = event["kind"], event["run_id"]
        if kind == "adopted":
            if event["target"] in adopted or run in runs:
                raise ValueError("Duplicate adoption or run ID")
            adopted.add(event["target"])
            runs.add(run)
            adoption = event
        elif kind == "admitted":
            if run in runs:
                raise ValueError("Duplicate admission ID")
            if adoption is None or event["inputs"]["contract"]["adopted_contract_sha256"] != (
                    adoption["inputs"]["contract"]["adopted_contract_sha256"]):
                raise ValueError("Admission is not bound to the then-current adoption")
            admitted[run] = event
            runs.add(run)
            lifecycle[run] = []
        elif kind not in ("closed",):
            if run not in admitted:
                raise ValueError("Event without prior admission")
            prior = lifecycle[run]
            if kind in ("launch-intent", "process-observed", "completed") and event["target"] != admitted[run]["target"]:
                raise ValueError("Lifecycle target differs from admission")
            if datetime.fromisoformat(event["time"]) < datetime.fromisoformat(admitted[run]["time"]):
                raise ValueError("Lifecycle event predates admission")
            if kind == "launch-intent" and (prior or admitted[run]["outcome"] == "awaiting-response"):
                raise ValueError("Duplicate or external-handoff launch intent")
            if kind == "process-observed":
                phase = event["process"]["phase"]
                phases = [p["process"]["phase"] for p in prior if p["kind"] == "process-observed"]
                if not any(p["kind"] == "launch-intent" for p in prior):
                    raise ValueError("Process observation without launch intent")
                if phase in ("spawned", "launch-failed") and phases:
                    raise ValueError("Duplicate/contradictory process spawn")
                if phase == "direct-exited" and phases != ["spawned"]:
                    raise ValueError("Direct exit without exactly one observed spawn")
                if phase == "direct-exited":
                    spawned = next(p["process"] for p in prior if p["kind"] == "process-observed")
                    if any(event["process"][k] != spawned[k] for k in ("pid", "process_group", "start_identity")):
                        raise ValueError("Exited process identity changed")
            if kind == "completed":
                observed = [p["process"] for p in prior if p["kind"] == "process-observed"]
                if any(p["kind"] == "completed" for p in prior) or not observed or observed[-1]["phase"] not in (
                        "direct-exited", "launch-failed"):
                    raise ValueError("Completion lacks terminal process observation")
                if event["child_exit"] != observed[-1]["returncode"]:
                    raise ValueError("Completion exit differs from observation")
                if observed[-1]["phase"] == "launch-failed":
                    if event["spawned"] != "no" or event["outcome"] not in (
                            "fail", "blocked", "unavailable", "interrupted"):
                        raise ValueError("Failed launch cannot establish executed completion")
                elif event["spawned"] != "yes":
                    raise ValueError("Completion spawn state differs from observed child")
            if kind == "receipt-accepted":
                for ref in event["receipt_refs"]:
                    if ref["id"] in accepted:
                        raise ValueError("Receipt accepted more than once")
                    accepted.add(ref["id"])
            prior.append(event)


def _design_review(value):
    _record(value, {"producer": validate_producer, "designer": validate_producer,
                    "candidate_hashes": lambda v: _record(v, {"document": _hash, "components": _map(_hash),
                                                             "workflow_contract": _hash}),
                    "verdict": _enum("APPROVE", "REVISE", "REJECT"), "artifact": _artifact_ref,
                    "disposition_refs": _list(_disposition),
                    "human_approval": _enum("confirmed", "unconfirmed"),
                    "unattended_authorization": _nullable(_artifact_ref)})


def validate_design(value):
    _record(value, {"schema_version": _version(1), "revision": _id, "document": _artifact_ref,
                    "contract": _artifact_ref, "components": _map(_hash), "supersedes": _nullable(_id),
                    "review": _design_review,
                    "history": _list(lambda v: _record(v, {"revision": _id, "document": _artifact_ref,
                                                          "contract": _artifact_ref})),
                    "reason": _text})
    revisions = [entry["revision"] for entry in value["history"]]
    if len(revisions) != len(set(revisions)) or value["revision"] in revisions:
        raise ValueError("Duplicate design revision")
    if value["supersedes"] != (revisions[-1] if revisions else None):
        raise ValueError("Design supersedes/history mismatch")


def _verify_artifact(root, ref):
    path = safe_path(root, ref["path"])
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != ref["sha256"] or ("bytes" in ref and len(content) != ref["bytes"]):
        raise ValueError("Artifact changed: " + ref["path"])
    return content


def validate_design_binding(root: Path, contract: dict, design: dict, ledger: dict) -> dict:
    """Validate an explicit adoption basis without reading or publishing a live pointer."""
    validate_contract(contract)
    validate_ledger(ledger)
    if contract["slug"] != ledger["slug"]:
        raise ValueError("Workspace slug mismatch")
    root = Path(root).resolve(strict=True)
    workspace = ".ai/" + contract["slug"]
    validate_design(design)
    if design["revision"] != contract["design_revision"]:
        raise ValueError("Current design and workflow revision disagree")
    for entry in [*design["history"], design]:
        for key, folder, ext in (("document", "design-history", "html"), ("contract", "contracts", "json")):
            expected = "%s/%s/%s.%s" % (workspace, folder, entry["revision"], ext)
            if path_name(entry[key]["path"]) != expected:
                raise ValueError("Design pointer is not a retained revision path")
            _verify_artifact(root, entry[key])
    review = design["review"]
    for ref in [review["artifact"], *review["disposition_refs"]]:
        _verify_artifact(root, ref)
    if review["verdict"] != "APPROVE" or review["producer"]["role"] != "reviewer":
        raise ValueError("Design lacks approved independent review")
    forbidden = {review["designer"]["context_id"]}
    forbidden.update(p["context_id"] for i in contract["increments"].values() for p in i["implementers"])
    if review["producer"]["context_id"] in forbidden:
        raise ValueError("Design reviewer is not independent")
    if review["human_approval"] == "unconfirmed":
        if review["unattended_authorization"] is None:
            raise ValueError("Unconfirmed design lacks unattended authorization")
        _verify_artifact(root, review["unattended_authorization"])
    expected = {"document": design["document"]["sha256"], "components": design["components"],
                "workflow_contract": canonical_hash(contract)}
    if review["candidate_hashes"] != expected:
        raise ValueError("Design review candidate mismatch")
    normative = _decode_json(_verify_artifact(root, design["contract"]))
    if not isinstance(normative, dict) or {k: canonical_hash(v) for k, v in normative.items()} != design["components"]:
        raise ValueError("Normative component hashes do not match retained contracts")
    if any(set(i["components"]) - set(design["components"]) for i in contract["increments"].values()):
        raise ValueError("Missing normative component")
    adoptions = [e for e in ledger["events"] if e["kind"] == "adopted"]
    if [e["target"] for e in adoptions] != [e["revision"] for e in design["history"]] + [design["revision"]]:
        raise ValueError("Current-design history/adoption mismatch")
    for adoption, entry in zip(adoptions, [*design["history"], design]):
        files = adoption["inputs"]["source"]["files"]
        if any(files.get(entry[k]["path"], {}).get("sha256") != entry[k]["sha256"] for k in ("document", "contract")):
            raise ValueError("Adoption does not bind retained design bytes")
    binding = adoptions[-1]["inputs"]["contract"]
    if binding["adopted_contract_sha256"] != canonical_hash(contract) or binding["components"] != design["components"]:
        raise ValueError("Current pointer/adopted contract mismatch")
    return design


def _load_design(root, contract, ledger):
    design = read_json(safe_path(root, ".ai/%s/current-design.json" % contract["slug"]))
    return validate_design_binding(root, contract, design, ledger)


def _receipt_artifacts(root, receipt):
    refs = list(receipt["artifacts"])
    result = receipt["result"]
    if "source_artifact" in result:
        refs += [result["source_artifact"], *result["disposition_refs"]]
        declared = {a["path"]: a for a in receipt["artifacts"]}
        evidence_paths = [p for s in result["scenarios"].values() for p in s["evidence_refs"]]
        evidence_paths += [p for f in result["findings"] for p in f["evidence_refs"]]
        if any(p not in declared for p in evidence_paths):
            raise ValueError("Finding evidence is not a declared artifact")
    if result.get("schema_version") == 2:
        refs += [a for m in result["metrics"].values() for a in m["artifacts"]]
    observations, errors = {}, []
    for ref in refs:
        path = safe_path(root, ref["path"])
        content = path.read_bytes() if path.is_file() else None
        digest = hashlib.sha256(content).hexdigest() if content is not None else None
        size = len(content) if content is not None else None
        observations[ref["path"]] = {"exists": content is not None, "expected_sha256": ref["sha256"],
                                     "observed_sha256": digest, "bytes": size,
                                     "expected_bytes": ref.get("bytes")}
        if digest != ref["sha256"] or ("bytes" in ref and size != ref["bytes"]):
            errors.append("Missing or changed artifact: " + ref["path"])
    return observations, errors


def resolve_receipts(root, slug, ledger, extra_ids=()):
    observations, active = {}, set()
    references = [r for e in ledger["events"] for r in e["receipt_refs"]]
    references += [{"id": name, "sha256": None} for name in extra_ids]

    def resolve(ref):
        name = ref["id"]
        if name in active:
            raise ValueError("Cyclic receipt prerequisites")
        if name not in observations:
            active.add(name)
            receipt, digest, artifacts = None, None, {}
            try:
                path = safe_path(root, ".ai/%s/evidence/receipts/%s.json" % (slug, name))
                content = path.read_bytes()
                digest = hashlib.sha256(content).hexdigest()
                receipt = _decode_json(content)
                validate_receipt(receipt)
                if receipt["id"] != name:
                    raise ValueError("Receipt filename/ID mismatch")
                artifacts, artifact_errors = _receipt_artifacts(root, receipt)
                for prerequisite in receipt["prerequisite_receipts"]:
                    child = resolve(prerequisite)
                    if child.status != "valid":
                        raise ValueError("Invalid prerequisite receipt: " + prerequisite["id"])
                observations[name] = ReceiptObservation("stale" if artifact_errors else "valid",
                    receipt, digest, artifacts, "; ".join(artifact_errors))
            except FileNotFoundError:
                observations[name] = ReceiptObservation("missing", None, digest, artifacts, "Receipt is missing")
            except (ValueError, OSError, UnicodeError, RecursionError) as error:
                observations[name] = ReceiptObservation("invalid", None, digest, artifacts, str(error))
            finally:
                active.remove(name)
        observation = observations[name]
        if observation.status == "valid" and ref["sha256"] is not None and observation.observed_sha256 != ref["sha256"]:
            observation = ReceiptObservation("stale", observation.document, observation.observed_sha256,
                                             observation.artifacts, "Receipt byte hash changed")
            observations[name] = observation
        return observation
    for ref in references:
        resolve(ref)
    return observations


def load_workspace(root: Path, slug: str):
    """Validate persisted authority and resolve immutable proof. Does not adopt."""
    _slug(slug)
    root = Path(root).resolve(strict=True)
    contract = read_json(safe_path(root, ".ai/%s/workflow.json" % slug))
    validate_contract(contract)
    ledger = read_json(safe_path(root, ".ai/%s/evidence/ledger.json" % slug))
    validate_ledger(ledger)
    if contract["slug"] != slug or ledger["slug"] != slug:
        raise ValueError("Workspace slug mismatch")
    design = _load_design(root, contract, ledger)
    extra = [c["accepted_receipt"] for c in contract["claims"].values() if c["accepted_receipt"] is not None]
    return contract, design, ResolvedLedger(ledger, resolve_receipts(root, slug, ledger, extra))


def _section_hash(content, anchor):
    lines = content.splitlines(keepends=True)
    found = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = match[2]
        explicit = re.search(r"\s+\{#([\w.-]+)\}$", heading)
        name = explicit[1] if explicit else re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
        found.append((index, len(match[1]), name))
    matches = [h for h in found if h[2] == anchor]
    if len(matches) != 1:
        raise ValueError("Missing or ambiguous research heading")
    start, level, _ = matches[0]
    end = next((i for i, depth, _ in found if i > start and depth <= level), len(lines))
    return hashlib.sha256("".join(lines[start:end]).encode("utf-8")).hexdigest()


def _validate_claim_files(root, claim):
    path, anchor = claim["report"].split("#")
    text = safe_path(root, path).read_bytes().decode("utf-8")
    if _section_hash(text, anchor) != claim["claim_sha256"]:
        raise ValueError("Research claim section changed")
    for ref in claim["source_refs"]:
        content = _verify_artifact(root, ref).decode("utf-8")
        if max(ref["lines"]) > len(content.splitlines()):
            raise ValueError("Research source line is out of range")


def _target_actions(contract, item):
    if item["kind"] == "action":
        return [contract["actions"][item["id"]]]
    if item["kind"] == "check":
        return [contract["actions"][contract["checks"][item["id"]]["action_id"]]]
    return [contract["actions"][node["id"]] for node in dependency_closure(contract, item).values()
            if node["kind"] == "action"]


def _snapshot_for(root, contract, design, item):
    actions = _target_actions(contract, item)
    components = {component for action in actions for component in action["components"]}
    if item["kind"] == "increment":
        components.update(contract["increments"][item["id"]]["components"])
    claims = {name for action in actions for name in action["claims"]}
    for name in claims:
        _validate_claim_files(root, contract["claims"][name])
    scope = {"files": [], "directories": [], "excluded_outputs": []}
    for action in actions:
        if action["command"] is not None and not safe_path(root, action["command"]["cwd"]).is_dir():
            raise ValueError("Registered command cwd does not exist")
        scopes = [action["inputs"]]
        if action["retirement"]:
            scopes.append(action["retirement"]["legacy_scope"])
        for own_scope in scopes:
            for key in scope:
                for entry in own_scope[key]:
                    if entry not in scope[key]:
                        scope[key].append(entry)
    # Exclusions are exact generated paths, never directory-prefix blind spots.
    for exclusion in scope["excluded_outputs"]:
        name = path_name(exclusion["path"])
        allowed = ".ai/%s/" % contract["slug"]
        if not name.startswith(allowed) or not (
                name == allowed + "metrics.json" or name == allowed + "evidence/ledger.json" or
                re.fullmatch(re.escape(allowed) + r"evidence/(runs|receipts)/.+\.(json|log|txt)", name)):
            raise ValueError("Exclusion is not an exact owned workflow output")
        if safe_path(root, name).is_dir():
            raise ValueError("Directory output exclusions are forbidden")
    for name in scope["files"] + scope["directories"]:
        safe_path(root, name)
    source = source_snapshot(root, scope)
    action_ids = {action["id"] for action in actions}
    check_ids = {c["id"] for c in contract["checks"].values() if c["action_id"] in action_ids}
    binding = {"binding_mode": "guarded", "adopted_contract_sha256": canonical_hash(contract),
               "components": {k: design["components"][k] for k in sorted(components)},
               "actions": {k: canonical_hash(contract["actions"][k]) for k in sorted(action_ids)},
               "checks": {k: canonical_hash(contract["checks"][k]) for k in sorted(check_ids)},
               "claims": {k: canonical_hash(contract["claims"][k]) for k in sorted(claims)}}
    return {"source": source, "contract": binding}


def bind_inputs(root: Path, contract: dict, target: dict, *,
                design: dict | None = None, ledger: dict | None = None) -> ResolvedInputs:
    """Bind live inputs, or an explicit validated basis for adoption retry only.

    Explicit design and ledger must be supplied together. They do not replace
    persisted authority or authorize ordinary dispatch from a historical prefix.
    """
    if (design is None) != (ledger is None):
        raise ValueError("Explicit design and ledger must be supplied together")
    validate_contract(contract)
    validate_target(target)
    if target["kind"] != "ship" and target["id"] not in contract[target["kind"] + "s"]:
        raise ValueError("Unknown target")
    root = Path(root).resolve(strict=True)
    if design is None:
        ledger = read_json(safe_path(root, ".ai/%s/evidence/ledger.json" % contract["slug"]))
        design = _load_design(root, contract, ledger)
    else:
        design = validate_design_binding(root, contract, design, ledger)
    snapshots = {}
    for key, item in dependency_closure(contract, target).items():
        try:
            snapshots[key] = _snapshot_for(root, contract, design, item)
        except (OSError, ValueError, UnicodeError) as error:
            snapshots[key] = BlockedInput(str(error))
    own = snapshots[target_key(target)]
    if isinstance(own, BlockedInput):
        # The requested snapshot cannot be serialized; caller reports input error.
        raise ValueError(own.reason)
    return ResolvedInputs(own, snapshots)


def append_event(workspace: Path, event: dict, expected_seq: int) -> dict:
    """Append under a caller-held exclusive lock; seq is assigned, not trusted.

    ``event`` has the persisted Event fields except seq. Immutable receipt blobs
    must already exist. Sequence conflicts never overwrite the ledger.
    """
    _natural(expected_seq)
    workspace = Path(workspace)
    if workspace.is_symlink() or workspace.is_junction():
        raise ValueError("Linked workspace")
    workspace = workspace.absolute()
    root = workspace.parent.parent.resolve(strict=True)
    safe_path(root, workspace.relative_to(root).as_posix())
    path = safe_path(root, workspace.relative_to(root).as_posix() + "/evidence/ledger.json")
    ledger = read_json(path)
    validate_ledger(ledger)
    if len(ledger["events"]) != expected_seq:
        raise SequenceConflict("Ledger sequence changed")
    if not isinstance(event, dict) or "seq" in event:
        raise ValueError("Append assigns seq")
    persisted = dict(deepcopy(event), seq=expected_seq + 1)
    candidate = dict(ledger, events=[*ledger["events"], persisted])
    validate_ledger(candidate)
    refs = persisted["receipt_refs"]
    observations = resolve_receipts(root, ledger["slug"], {"events": [{"receipt_refs": refs}]})
    if any(observations[ref["id"]].status != "valid" for ref in refs):
        raise ValueError("Cannot append references to missing or changed receipts")
    write_json_atomic(path, candidate)
    return persisted
