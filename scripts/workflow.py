#!/usr/bin/env python3
"""Cooperative five-verb workflow boundary; recovery and metric attachment are deferred."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid

from evidence import exclusive_lock, source_snapshot, write_json_atomic
from mutate import parse_native
from run import run_capture
import workflow_state as state
from workflow_gate import evaluate


METRIC_BLOCK = ("METRIC_ATTACHMENT_UNAVAILABLE: the producer bridge for admission ID, "
                "registered argv, source projection and raw validation is not qualified; "
                "no metric receipt can be accepted. Required quality remains blocked.")


class Refusal(Exception):
    def __init__(self, code, reason, details=None):
        super().__init__(reason)
        self.code, self.details = code, details


def _now():
    return datetime.now(timezone.utc).isoformat()


def _bytes(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _emit(value):
    print(json.dumps(value, ensure_ascii=False, allow_nan=False), flush=True)


def _exclusive(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def _artifact(root, path, media_type="text/plain"):
    content = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content), "media_type": media_type}


def _event(kind, node, run, inputs, producer, *, refs=(), outcome="ready",
           spawned="no", process=None, child_exit=None, commit=None, reason=""):
    return {"kind": kind, "target": node, "run_id": run, "inputs": inputs,
            "receipt_refs": list(refs), "producer": producer, "outcome": outcome,
            "process": process, "child_exit": child_exit, "spawned": spawned,
            "completion_commit": commit, "time": _now(), "reason": reason}


def _append(workspace, ledger, event):
    saved = state.append_event(workspace, event, len(ledger["events"]))
    ledger["events"].append(saved)
    return saved


def _decision(root, contract, ledger, node):
    inputs = state.bind_inputs(root, contract, node)
    lock_name = ".ai/%s/evidence/workflow.lock" % contract["slug"]
    for snapshot in inputs.targets.values():
        if isinstance(snapshot, state.BlockedInput):
            continue
        scope = snapshot["source"]["scope"]
        if lock_name in scope["files"] or any(
                directory == "." or lock_name.startswith(directory + "/") for directory in scope["directories"]):
            raise ValueError("Declared input scope covers the transient workflow lock")
    return evaluate(contract, ledger, inputs, node)


def _lifetime(readiness):
    if any(b["code"] == "RECOVERY_UNVERIFIED" for b in readiness["blockers"]):
        raise Refusal(3, "RECOVERY_UNVERIFIED: unresolved admission; recovery is unavailable", readiness)


def _ready(readiness):
    _lifetime(readiness)
    if readiness["status"] == "blocked":
        raise Refusal(1, "Required proof is not ready", readiness)


def _action(contract, node):
    if node["kind"] == "action":
        return contract["actions"][node["id"]]
    if node["kind"] == "check":
        return contract["actions"][contract["checks"][node["id"]]["action_id"]]
    return None


def _prerequisites(contract, ledger, node):
    """Project exact receipt references from prerequisites already proved by evaluate."""
    events = ledger["events"]
    refs = {}

    def latest(kind, target):
        return next(e for e in reversed(events) if e["kind"] == kind and e["target"] == target)

    def collect(dep):
        if dep["kind"] in ("check", "increment"):
            event = latest("receipt-accepted" if dep["kind"] == "check" else "closed", dep)
            for ref in event["receipt_refs"]:
                refs[ref["id"]] = ref
        else:
            action = _action(contract, dep)
            for child in state.dependencies(contract, dep):
                collect(child)
            check = next((c for c in contract["checks"].values()
                          if c["action_id"] == action["id"]), None)
            if check and check["kind"] == "behavioral-red":
                event = latest("receipt-accepted", state.target("check", check["id"]))
                for ref in event["receipt_refs"]:
                    refs[ref["id"]] = ref

    for dep in state.dependencies(contract, node):
        collect(dep)
    return sorted(refs.values(), key=lambda ref: ref["id"])


def _native_projection(root, action, text):
    command = action["command"]
    reporter = Path(__file__).with_name("native_result.mjs").resolve()
    flags = {"--test-reporter=" + str(reporter), "--test-reporter=" + reporter.as_uri()}
    argv = command["argv"]
    if Path(argv[0]).name.lower() not in ("node", "node.exe") or "--test" not in argv or not any(arg in flags for arg in argv):
        raise Refusal(1, "Native proof requires the registered direct Node test command and native_result reporter")
    value = parse_native(text)
    if value is None:
        raise Refusal(1, "Missing or malformed native producer output")
    state.validate_native(value)
    result = deepcopy(value)
    for test in result["tests"]:
        path = Path(test["file"])
        if not path.is_absolute():
            path = state.safe_path(root, command["cwd"]) / path
        try:
            relative = path.resolve(strict=True).relative_to(root).as_posix()
        except (ValueError, FileNotFoundError) as error:
            raise Refusal(1, "Native test file is outside the observed repository") from error
        state.safe_path(root, relative)
        test["file"] = relative
    return result


def _project_result(root, action, check, stdout_path):
    if check["kind"] == "metrics":
        raise Refusal(1, METRIC_BLOCK)
    if check["kind"] in ("test", "behavioral-red", "compatibility"):
        return _native_projection(root, action, stdout_path.read_text(encoding="utf-8"))
    value = state.read_json(stdout_path)
    state.validate_finding(value)
    if value["kind"] != check["kind"]:
        raise Refusal(1, "Finding kind differs from the registered producer")
    return value


def _accept(root, slug, receipt, content):
    contract, design, resolved = state.load_workspace(root, slug)
    state.validate_receipt(receipt)
    check = contract["checks"].get(receipt["check_id"])
    if check is None:
        raise ValueError("Unknown receipt check")
    if check["kind"] == "metrics":
        raise Refusal(1, METRIC_BLOCK)
    node = state.target("check", check["id"])
    readiness = _decision(root, contract, resolved, node)
    _lifetime(readiness)
    action = contract["actions"][check["action_id"]]
    if receipt["recorded_by"] != design["review"]["designer"]:
        raise Refusal(1, "recorded_by must identify the current declared designer/recorder; producer is unchanged")
    admission = next((e for e in resolved.document["events"] if e["kind"] == "admitted"
                      and e["run_id"] == receipt["run_id"]), None)
    if admission is None or _action(contract, admission["target"]) != action:
        raise Refusal(1, "Receipt has no matching admitted producer")
    if receipt["producer"] != action["owner"]:
        raise Refusal(1, "Receipt producer differs from registered owner")
    if action["command"] is not None:
        raw = state.safe_path(root, ".ai/%s/evidence/runs/%s/stdout.txt" % (slug, receipt["run_id"]))
        projected = _project_result(root, action, check, raw)
        if receipt["result"] != projected:
            raise Refusal(1, "Receipt differs from actual admitted producer output")
        if "tests" in projected and any(t["file"] not in receipt["inputs"]["source"]["files"]
                                       for t in projected["tests"]):
            raise Refusal(1, "Native producer executed a test outside the admitted file inventory")
        artifact = _artifact(root, raw)
        if not any(all(a[key] == artifact[key] for key in ("path", "sha256", "bytes"))
                   for a in receipt["artifacts"]):
            raise Refusal(1, "Receipt must bind the admitted raw stdout artifact")
    workspace = state.safe_path(root, ".ai/" + slug)
    path = state.safe_path(root, ".ai/%s/evidence/receipts/%s.json" % (slug, receipt["id"]))
    if path.exists():
        if path.read_bytes() != content:
            raise Refusal(3, "Immutable receipt ID already contains different bytes")
        if any(ref["id"] == receipt["id"] for e in resolved.document["events"] for ref in e["receipt_refs"]):
            raise Refusal(3, "Receipt has already been referenced")
    else:
        _exclusive(path, content)
    ref = {"id": receipt["id"], "sha256": hashlib.sha256(content).hexdigest()}
    observations = state.resolve_receipts(root, slug, resolved.document, [receipt["id"]])
    observation = observations[receipt["id"]]
    if observation.status != "valid":
        raise Refusal(1, "Receipt artifacts or prerequisites are invalid: " + observation.reason)
    # Immutable orphan blobs are not authority. Accept only after evaluating the
    # proposed append with the same materialized gate used by every consumer.
    event = _event("receipt-accepted", node, receipt["run_id"], readiness["inputs"],
                   design["review"]["designer"], refs=[ref], outcome=receipt["outcome"])
    candidate = dict(resolved.document, events=[*resolved.document["events"],
                                               dict(event, seq=len(resolved.document["events"]) + 1)])
    checked = evaluate(contract, state.ResolvedLedger(candidate, observations),
                       state.bind_inputs(root, contract, node), node)
    if checked["status"] != "complete":
        raise Refusal(1, "Returned producer proof does not satisfy the current check", checked)
    # Re-read bindings and artifact bytes immediately before the final append.
    fresh_contract, _, fresh = state.load_workspace(root, slug)
    fresh_inputs = state.bind_inputs(root, fresh_contract, node)
    fresh_observations = state.resolve_receipts(root, slug, fresh.document, [receipt["id"]])
    if fresh.document != resolved.document or fresh_contract != contract or (
            fresh_observations != observations or fresh_inputs.target != readiness["inputs"]):
        raise Refusal(3, "Receipt inputs changed before acceptance")
    _append(workspace, resolved.document, event)
    return {"outcome": "accepted", "receipt": ref, "readiness": checked}


def _next(root, slug, action_id, run):
    contract, design, resolved = state.load_workspace(root, slug)
    node = state.target("action", action_id)
    readiness = _decision(root, contract, resolved, node)
    _ready(readiness)
    if readiness["status"] == "complete":
        return 0, readiness
    action = contract["actions"][action_id]
    check = next((c for c in contract["checks"].values() if c["action_id"] == action_id), None)
    workspace = state.safe_path(root, ".ai/" + slug)
    run_dir = state.safe_path(root, ".ai/%s/evidence/runs/%s" % (slug, run))
    run_dir.mkdir(parents=True)
    refs = _prerequisites(contract, resolved.document, node)
    command = action["command"]
    admission = _append(workspace, resolved.document, _event(
        "admitted", node, run, readiness["inputs"], action["owner"], refs=refs,
        outcome="awaiting-response" if command is None else "ready",
        spawned="no" if command is None else "unknown"))
    if command is None:
        return 0, {"outcome": "awaiting-response", "run_id": run, "admission": admission,
                   "check_id": check["id"], "handoff_steps": check["handoff_steps"]}
    _append(workspace, resolved.document, _event(
        "launch-intent", node, run, readiness["inputs"], action["owner"], refs=refs, spawned="unknown"))
    observations, observer_failed = [], []

    def observe(value):
        try:
            _append(workspace, resolved.document, _event(
                "process-observed", node, run, readiness["inputs"], action["owner"], refs=refs,
                process=value, spawned="no" if value["phase"] == "launch-failed" else "yes",
                child_exit=value["returncode"]))
            observations.append(value)
        except Exception:
            observer_failed.append(True)
            raise

    env = os.environ.copy()
    for key, value in command["environment"].items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    rc, stdout, stderr = run_capture(command["argv"], cwd=str(state.safe_path(root, command["cwd"])),
                                   idle=command["idle_seconds"], max_total=command["max_seconds"],
                                   env=env, observe=observe)
    for name, text in (("stdout.txt", stdout), ("stderr.txt", stderr)):
        _exclusive(run_dir / name, text.encode("utf-8"))
    summary = {"run_id": run, "wrapper_exit": rc, "stdout": str(run_dir / "stdout.txt"),
               "stderr": str(run_dir / "stderr.txt")}
    if (observer_failed or not observations or
            observations[-1]["phase"] not in ("launch-failed", "direct-exited") or
            any(o["cleanup"] != "not-attempted" or
                (o["phase"] == "direct-exited" and o["error"]) for o in observations)):
        return rc if rc else 3, dict(summary, outcome="RECOVERY_UNVERIFIED", spawned="unknown",
                                    reason="Capture/observer uncertainty; no completion recorded, no recovery available")
    terminal = observations[-1]
    spawned = terminal["phase"] != "launch-failed"
    inputs = state.bind_inputs(root, contract, node).target
    _append(workspace, resolved.document, _event(
        "completed", node, run, inputs, action["owner"], refs=refs,
        outcome="executed" if spawned and rc == 0 else "fail",
        spawned="yes" if spawned else "no", child_exit=terminal["returncode"]))
    summary.update(outcome="executed" if spawned and rc == 0 else "fail",
                   spawned="yes" if spawned else "no", child_exit=terminal["returncode"])
    if check is None or not spawned:
        return rc, summary
    if check["kind"] == "metrics":
        return rc if rc else 1, dict(summary, reason=METRIC_BLOCK)
    try:
        result = _project_result(root, action, check, run_dir / "stdout.txt")
        artifacts = [_artifact(root, run_dir / name) for name in ("stdout.txt", "stderr.txt")]
        if "source_artifact" in result:
            names = {result["source_artifact"]["path"]}
            names.update(ref["path"] for ref in result["disposition_refs"])
            names.update(path for scenario in result["scenarios"].values() for path in scenario["evidence_refs"])
            names.update(path for finding in result["findings"] for path in finding["evidence_refs"])
            artifacts.extend(_artifact(root, state.safe_path(root, name)) for name in sorted(names))
        receipt = {"schema_version": 1, "id": "receipt-" + run, "check_id": check["id"],
                   "run_id": run, "producer": action["owner"], "recorded_by": design["review"]["designer"],
                   "outcome": "pass", "inputs": readiness["inputs"], "prerequisite_receipts": refs,
                   "result": result, "artifacts": artifacts,
                   "started_at": admission["time"], "finished_at": _now()}
        accepted = _accept(root, slug, receipt, _bytes(receipt))
        return rc, dict(summary, proof=accepted)
    except (ValueError, OSError, Refusal) as error:
        return rc if rc else 1, dict(summary, proof="blocked", reason=str(error))


def _git(root, *argv):
    rc, stdout, stderr = run_capture(["git", *argv], cwd=str(root), idle=120, max_total=600)
    if rc:
        raise Refusal(2, "Git command failed: " + stderr, {"argv": ["git", *argv], "exit": rc, "stdout": stdout})
    return stdout


def _committed(root, source, commit):
    entries = {}
    for record in _git(root, "ls-tree", "-r", "-z", commit).split("\0"):
        if record:
            metadata, name = record.split("\t", 1)
            mode, kind, oid = metadata.split()
            entries[name] = (mode, kind, oid)
    scope = source["scope"]

    def included(name):
        return (name in scope["files"] or any(d == "." or name.startswith(d + "/") for d in scope["directories"])) and not any(
            name == e["path"] or name.startswith(e["path"] + "/") for e in scope["excluded_outputs"])

    expected = {name for name, entry in source["files"].items() if entry["mode"] != "missing"}
    if {name for name in entries if included(name)} != expected:
        raise Refusal(1, "Committed source membership differs from proven scope")
    for name in expected:
        mode, kind, oid = entries[name]
        content = state.safe_path(root, name).read_bytes()
        if (kind != "blob" or mode not in ("100644", "100755") or
                ("executable" if mode == "100755" else "file") != source["files"][name]["mode"] or
                hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest() != oid or
                hashlib.sha256(content).hexdigest() != source["files"][name]["sha256"]):
            raise Refusal(1, "Committed bytes/mode differ from proven source: " + name)


def _close(root, slug, increment, commit):
    contract, design, ledger = state.load_workspace(root, slug)
    node = state.target("increment", increment) if increment else state.target("ship", "ship")
    readiness = _decision(root, contract, ledger, node)
    _lifetime(readiness)
    head = _git(root, "rev-parse", "--verify", "HEAD^{commit}").strip()
    branch = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD").strip()
    remote_defaults = _git(root, "for-each-ref", "--format=%(symref)", "refs/remotes").splitlines()
    protected = {"main", "master", "trunk"} | {
        ref.split("/", 3)[3] for ref in remote_defaults if ref.startswith("refs/remotes/") and ref.count("/") >= 3}
    if branch in protected:
        raise Refusal(1, "Closure requires a feature branch")
    if increment and (not re.fullmatch(r"[0-9a-f]{40}", commit) or commit != head):
        raise Refusal(1, "Completion commit must be the full current feature HEAD")
    _committed(root, readiness["inputs"]["source"], head)
    _ready(readiness)
    # The unqualified bridge cannot be bypassed by placing metric receipts on disk.
    raise Refusal(1, METRIC_BLOCK, readiness)


def _read_optional(root, name):
    path = state.safe_path(root, name)
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _decode(content):
    return state._decode_json(content)


def _retain(path, content):
    if path.exists():
        if path.read_bytes() != content:
            raise Refusal(3, "Conflicting immutable retained design: " + str(path))
    else:
        _exclusive(path, content)


def _old_preflight(root, contract, design, ledger):
    node = state.target("ship", "ship")
    inputs = state.bind_inputs(root, contract, node, design=design, ledger=ledger)
    extras = [c["accepted_receipt"] for c in contract["claims"].values() if c["accepted_receipt"] is not None]
    resolved = state.ResolvedLedger(ledger, state.resolve_receipts(root, contract["slug"], ledger, extras))
    _lifetime(evaluate(contract, resolved, inputs, node))


def _preserve_runtime_ids(old, new, ledger):
    for event in ledger["events"]:
        node = event["target"]
        if not isinstance(node, dict) or node["kind"] == "ship":
            continue
        if node["id"] not in new[node["kind"] + "s"]:
            raise Refusal(3, "Adoption removes a runtime-referenced ID")
        if node["kind"] == "check" and old["checks"][node["id"]]["action_id"] != new["checks"][node["id"]]["action_id"]:
            raise Refusal(3, "Adoption remaps a runtime-referenced check")
        if event["kind"] == "admitted":
            before, after = _action(old, node), _action(new, node)
            if before is None or after is None or before["id"] != after["id"] or (
                    (before["command"] is None) != (after["command"] is None)):
                raise Refusal(3, "Adoption reclassifies an admitted executable/handoff")


def _adopt(root, slug, revision, review_name):
    base = ".ai/" + slug
    stem = base + "/design-history/" + revision
    w_name, p_name, l_name = base + "/workflow.json", base + "/current-design.json", base + "/evidence/ledger.json"
    candidate_w = state.safe_path(root, stem + ".workflow.json").read_bytes()
    candidate_p = state.safe_path(root, stem + ".current-design.json").read_bytes()
    contract, design = _decode(candidate_w), _decode(candidate_p)
    state.validate_contract(contract)
    state.validate_design(design)
    if contract["slug"] != slug or design["revision"] != revision or contract["design_revision"] != revision:
        raise ValueError("Candidate revision/slug mismatch")
    if candidate_w != _bytes(contract) or candidate_p != _bytes(design):
        raise ValueError("Candidate workflow/current-design must use canonical JSON bytes")
    review_raw = state.safe_path(root, review_name).read_bytes()
    review = _decode(review_raw)
    if review != design["review"]:
        raise ValueError("Review metadata differs from staged candidate")
    w_raw, p_raw, l_raw = (_read_optional(root, name) for name in (w_name, p_name, l_name))
    ledger = _decode(l_raw) if l_raw is not None else {"schema_version": 1, "slug": slug, "events": []}
    state.validate_ledger(ledger)
    if ledger["slug"] != slug:
        raise ValueError("Ledger slug mismatch")
    matches = [e for e in ledger["events"] if e["kind"] == "adopted" and e["target"] == revision]
    event = matches[0] if matches else None
    old_contract = old_design = None
    old_w = old_p = None
    old_names = []
    if event:
        prefix = dict(ledger, events=ledger["events"][:event["seq"] - 1])
        latest = [e for e in ledger["events"] if e["kind"] == "adopted"][-1]
        if latest != event:
            raise Refusal(3, "Candidate is not the latest adopted revision")
        if design["supersedes"] is not None:
            old_stem = base + "/design-history/" + design["supersedes"]
            old_names = [old_stem + ".workflow.json", old_stem + ".current-design.json"]
            old_w, old_p = (state.safe_path(root, name).read_bytes() for name in old_names)
            old_contract, old_design = _decode(old_w), _decode(old_p)
    elif ledger["events"]:
        if w_raw is None or p_raw is None:
            raise Refusal(3, "Existing ledger has lost live design authority")
        old_contract, old_design, resolved = state.load_workspace(root, slug)
        if resolved.document != ledger:
            raise Refusal(3, "Ledger changed while reading adoption basis")
        prefix, old_w, old_p = ledger, w_raw, p_raw
        old_stem = base + "/design-history/" + old_design["revision"]
        old_names = [old_stem + ".workflow.json", old_stem + ".current-design.json"]
    else:
        prefix = ledger
        for folder in ("runs", "receipts"):
            path = state.safe_path(root, base + "/evidence/" + folder)
            if path.exists() and (not path.is_dir() or any(path.iterdir())):
                raise Refusal(3, "Empty authority contradicts retained execution/receipt artifacts")
    if old_contract is not None:
        state.validate_design_binding(root, old_contract, old_design, prefix)
        _old_preflight(root, old_contract, old_design, prefix)
        if design["history"] != old_design["history"] + [
                {key: old_design[key] for key in ("revision", "document", "contract")}]:
            raise Refusal(3, "Candidate does not preserve exact previous history")
        _preserve_runtime_ids(old_contract, contract, prefix)
    elif prefix["events"] or design["history"] or design["supersedes"] is not None:
        raise Refusal(3, "Initial adoption requires empty authority and history")
    if event:
        if w_raw == candidate_w and p_raw == candidate_p:
            phase = "A3"
        elif ledger["events"][-1] != event:
            raise Refusal(3, "Partial publication has later runtime events")
        elif w_raw == old_w and p_raw == old_p:
            phase = "A1"
        elif w_raw == candidate_w and p_raw == old_p:
            phase = "A2"
        else:
            raise Refusal(3, "Conflicting or out-of-order adoption publication")
    else:
        if w_raw != old_w or p_raw != old_p:
            raise Refusal(3, "Initial adoption cannot replace existing authority")
        phase = "A0" if old_contract is not None else "B1" if l_raw is not None else "B0"
    refs = [design["document"], design["contract"], review["artifact"], *review["disposition_refs"]]
    if review["unattended_authorization"] is not None:
        refs.append(review["unattended_authorization"])
    for history in design["history"]:
        refs.extend(history[key] for key in ("document", "contract"))
    for ref in refs:
        path = state.safe_path(root, ref["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise ValueError("Adoption artifact changed: " + ref["path"])
    named = [stem + ".workflow.json", stem + ".current-design.json", review_name] + [r["path"] for r in refs]
    binding = {"binding_mode": "guarded", "adopted_contract_sha256": state.canonical_hash(contract),
               "components": design["components"], "actions": {}, "checks": {}, "claims": {}}
    expected_hashes = {ref["path"]: ref["sha256"] for ref in refs}
    for name, content in [(stem + ".workflow.json", candidate_w),
                          (stem + ".current-design.json", candidate_p), (review_name, review_raw),
                          *zip(old_names, (old_w, old_p))]:
        digest = hashlib.sha256(content).hexdigest()
        if name in expected_hashes and expected_hashes[name] != digest:
            raise ValueError("Conflicting adoption artifact references: " + name)
        expected_hashes[name] = digest

    def snapshot(include_old=True):
        scope = {"files": sorted(set(named + (old_names if include_old else []))),
                 "directories": [], "excluded_outputs": []}
        source = source_snapshot(root, scope)
        if any(source["files"][name]["sha256"] != expected_hashes[name] for name in scope["files"]):
            raise ValueError("Adoption inputs changed after parsing or review")
        return {"source": source, "contract": binding}

    if event:
        if (event["inputs"] != snapshot() or event["producer"] != review["designer"] or
                event["outcome"] != "ready" or event["receipt_refs"] or event["process"] is not None or
                event["child_exit"] is not None or event["spawned"] != "no" or event["completion_commit"] is not None):
            raise Refusal(3, "Adopted event does not bind exact candidate/review/history bytes")
        state.validate_design_binding(root, contract, design, ledger)
    else:
        preliminary = _event("adopted", revision, uuid.uuid4().hex, snapshot(False), review["designer"])
        state.validate_design_binding(root, contract, design, dict(
            ledger, events=[*ledger["events"], dict(preliminary, seq=len(ledger["events"]) + 1)]))
        for name, content in zip(old_names, (old_w, old_p)):
            _retain(state.safe_path(root, name), content)
        event = dict(preliminary, inputs=snapshot())
        state.validate_design_binding(root, contract, design, dict(
            ledger, events=[*ledger["events"], dict(event, seq=len(ledger["events"]) + 1)]))
    if (_read_optional(root, w_name), _read_optional(root, p_name), _read_optional(root, l_name)) != (
            w_raw, p_raw, l_raw) or snapshot() != event["inputs"]:
        raise Refusal(3, "Adoption basis changed before publication")
    if phase == "A3":
        state.load_workspace(root, slug)
        return {"outcome": "already-adopted", "revision": revision, "phase": phase}
    workspace = state.safe_path(root, base)
    if not matches:
        if l_raw is None:
            _exclusive(state.safe_path(root, l_name), _bytes(ledger))
        _append(workspace, ledger, event)
    if phase != "A2":
        write_json_atomic(state.safe_path(root, w_name), contract)
    write_json_atomic(state.safe_path(root, p_name), design)
    state.load_workspace(root, slug)
    return {"outcome": "adopted", "revision": revision, "phase": phase}


def _parser():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "Recover is not implemented. Unresolved lifetimes and orphan locks remain blocked. "
        "Successful metric attachment awaits the qualified producer bridge; required quality cannot close."))
    verbs = parser.add_subparsers(dest="verb", required=True)
    for name in ("status", "next", "record", "close", "adopt"):
        child = verbs.add_parser(name)
        child.add_argument("--slug", required=True)
        child.add_argument("--repo", default=".")
        if name == "status":
            child.add_argument("--target", default="ship:ship")
        elif name == "next":
            child.add_argument("--action", required=True)
        elif name == "record":
            child.add_argument("--receipt", required=True)
        elif name == "close":
            group = child.add_mutually_exclusive_group(required=True)
            group.add_argument("--increment")
            group.add_argument("--ship", action="store_true")
            child.add_argument("--commit")
        else:
            child.add_argument("--revision", required=True)
            child.add_argument("--review", required=True)
    return parser


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    if args.verb == "close" and bool(args.increment) != bool(args.commit):
        parser.error("--increment requires --commit; --ship does not accept --commit")
    try:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
            raise ValueError("Invalid slug")
        root = Path(args.repo).resolve(strict=True)
        actual_root = Path(_git(root, "rev-parse", "--show-toplevel").strip()).resolve(strict=True)
        if root != actual_root:
            raise ValueError("--repo must be the actual Git repository root")
        if args.verb == "status":
            pieces = args.target.split(":")
            if len(pieces) != 2:
                raise ValueError("Target must be KIND:ID")
            node = state.target(*pieces)
            contract, _, ledger = state.load_workspace(root, args.slug)
            readiness = _decision(root, contract, ledger, node)
            _emit(readiness)
            return 3 if any(b["code"] == "RECOVERY_UNVERIFIED" for b in readiness["blockers"]) else (
                1 if readiness["status"] == "blocked" else 0)
        workspace = state.safe_path(root, ".ai/" + args.slug)
        owner = {"token": uuid.uuid4().hex, "guard_pid": os.getpid(), "created_at": _now(),
                 "run_id": uuid.uuid4().hex, "workspace": str(workspace)}
        lock = state.safe_path(root, ".ai/%s/evidence/workflow.lock" % args.slug)
        with exclusive_lock(lock, owner):
            if args.verb == "adopt":
                if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.revision):
                    raise ValueError("Invalid revision ID")
                result = _adopt(root, args.slug, args.revision, args.review)
            elif args.verb == "next":
                code, result = _next(root, args.slug, args.action, owner["run_id"])
                _emit(result)
                return code
            elif args.verb == "record":
                path = state.safe_path(root, args.receipt)
                content = path.read_bytes()
                result = _accept(root, args.slug, _decode(content), content)
            else:
                result = _close(root, args.slug, args.increment, args.commit)
            _emit(result)
            return 0
    except Refusal as error:
        _emit({"outcome": "blocked", "reason": str(error), "details": error.details})
        return error.code
    except (FileExistsError, state.SequenceConflict) as error:
        _emit({"outcome": "conflict", "reason": str(error)})
        return 3
    except RuntimeError as error:
        _emit({"outcome": "conflict", "reason": str(error)})
        return 3
    except (ValueError, OSError, UnicodeError) as error:
        _emit({"outcome": "invalid-input", "reason": str(error)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
