"""Pure decisions over validated, materialized workflow records.

No filesystem reads, process execution, callbacks or global receipt cache. A
Readiness is a derived view, not permission to bypass locked revalidation.
"""

from datetime import datetime
import re

from probe import default_policy, judge
from workflow_state import (
    BlockedInput, ResolvedLedger, canonical_hash, dependencies, dependency_closure, target as make_target,
    target_key, validate_contract, validate_ledger, validate_snapshot, validate_target,
)


LIMITATIONS = [
    "Producer/context IDs are self-declared, not authenticated independence.",
    "Only declared input scopes are observed; this is not a sandbox.",
    "Read-only readiness is not permission to dispatch without locked revalidation.",
    "Design human approval and publication require their own attributed evidence.",
]
REQUIRED_METRICS = frozenset(default_policy()["required"])
MUTATION_FLOOR = default_policy()["rules"]["mutation_score_pct"]["threshold"]


def _bindings_equal(left, right):
    # Global adopted hash is provenance, not a blanket invalidator on adoption.
    return all(left[key] == right[key] for key in ("components", "actions", "checks", "claims"))


def _fresh(left, right, *, historical=False):
    return (_bindings_equal(left["contract"], right["contract"]) and
            (historical or left["source"]["scope_sha256"] == right["source"]["scope_sha256"]))


def _refs_equal(left, right):
    return sorted((r["id"], r["sha256"]) for r in left) == sorted((r["id"], r["sha256"]) for r in right)


def _merge_refs(results):
    refs = {}
    for _, _, group in results:
        for ref in group:
            refs[ref["id"]] = ref
    return list(refs.values())


def _command_succeeded(completion):
    return completion["child_exit"] == 0 and completion["outcome"] == "executed"


def _good_finding(result, check):
    if result.get("kind") != check["kind"] or result["verdict"] not in ("VERIFIED", "VERIFIED-WITH-LIMITATIONS"):
        return "Independent finding does not verify this check"
    if any(f["blocking"] for f in result["findings"]):
        return "Unresolved blocking finding"
    for ac in check["acs"]:
        scenario = result["scenarios"].get(ac)
        if not scenario or scenario["verdict"] not in ("VERIFIED", "VERIFIED-WITH-LIMITATIONS") or not scenario["evidence_refs"]:
            return "Missing verified scenario evidence: " + ac
    if check["kind"] == "human" and result["human_confirmation"] != "confirmed":
        return "Human acceptance is unconfirmed"
    return ""


def _native_result(result, check, receipt, exit_code):
    if result.get("schema_version") != 1 or "tests" not in result:
        return "Expected native test evidence"
    if not result["complete"] or not result["leaf_count"]:
        return "Missing complete positive test inventory"
    tests = result["tests"]
    if any(t["outcome"] in ("setup-error", "cancelled", "skipped", "todo") for t in tests):
        return "Setup, cancelled, skipped or todo tests do not establish proof"
    if check["kind"] != "behavioral-red":
        if exit_code != 0 or any(t["outcome"] != "pass" for t in tests):
            return "Current test proof is not green"
    elif exit_code in (None, 0, 124, 125, 127) or not any(t["outcome"] == "assertion-fail" for t in tests):
        return "Behavioral red needs a relevant assertion failure, not an exit code alone"
    for assertion in check["assertions"]:
        name = assertion["test_file"].replace("\\", "/")
        if receipt["inputs"]["source"]["files"].get(name, {}).get("sha256") != assertion["source_sha256"]:
            return "Assertion source is not bound to receipt inputs"
        matches = [t for t in tests if t["file"].replace("\\", "/") == name
                   and t["name"] == assertion["test_name"]]
        if len(matches) != 1:
            return "Missing or ambiguous declared assertion test"
        test = matches[0]
        if check["kind"] != "behavioral-red":
            if test["outcome"] != "pass":
                return "Required assertion did not pass"
            continue
        error = test.get("error", {})
        expected = assertion["expected_red"]
        stack = error.get("assertion_stack", "").replace("\\", "/")
        if (test["outcome"] != "assertion-fail" or error.get("name") != "AssertionError" or
                error.get("cause_code") != "ERR_ASSERTION" or error.get("operator") != expected["operator"] or
                error.get("expected") != expected["expected_relation"] or
                error.get("actual") != expected["actual_relation"] or not any(
                    re.search(r"(?:^|[/\s(])" + re.escape(name) + ":" + str(line) + r":\d+(?:\)|\s|$)", stack)
                    for line in assertion["assertion_lines"])):
            return "Assertion failure does not match the declared red symptom/line"
    return ""


def _metric_result(result, receipt, action):
    if result.get("schema_version") != 2 or "metrics" not in result:
        return "Expected metric verdict"
    if (result["run_id"] != receipt["run_id"] or
            result["source"]["scope_sha256"] != receipt["inputs"]["source"]["scope_sha256"]):
        return "Metrics are not from the admitted run/source"
    policy = result["policy"]
    if not REQUIRED_METRICS <= set(policy["required"]):
        return "Metric policy omits required measurements"
    if (result["baseline"] == "unknown" or result["verdict"] != "pass" or
            result["completeness"] != "complete" or result["missing_required"] or result["unavailable"]):
        return "Required metrics remain unavailable or failed"
    for name in policy["required"]:
        metric, rule = result["metrics"].get(name), policy["rules"].get(name)
        if not metric or not rule or metric["name"] != name:
            return "Missing required metric or rule: " + name
        if (metric["state"] != "measured" or metric["comparison"] not in ("ok", "warn") or
                metric["head"] is None or metric["run_id"] != receipt["run_id"] or
                metric["source"]["scope_sha256"] != result["source"]["scope_sha256"] or
                metric["command"] is None or not metric["artifacts"]):
            return "Incomplete measured proof: " + name
        if result["baseline"] == "compared" and metric["base"] is None:
            return "Missing brownfield baseline"
        support = metric["scope_support"]
        if (not isinstance(support.get("measured_paths"), list) or not support["measured_paths"] or
                support.get("unsupported_paths") != []):
            return "Metric scope is unsupported or lacks a measured inventory"
        # Receipt policy hashes bind supplied bytes, not policy authority.
        # Numeric floors can tighten, but never replace, built-in comparison.
        _, comparison = judge(name, metric["base"], metric["head"], result["baseline"] == "greenfield")
        if comparison not in ("ok", "warn") or metric["comparison"] != comparison:
            return "Measured regression contradicts claimed comparison"
        if rule["mode"] in ("floor", "coverage"):
            if rule["threshold"] is None or metric["head"] < rule["threshold"]:
                return "Required numeric floor not met"
        elif rule["threshold"] is not None:
            return "Additional numeric bars require an explicit floor/coverage rule"
        if name == "diff_coverage_pct" and rule["mode"] not in ("floor", "coverage"):
            return "Required coverage bar is unavailable"
        if name == "mutation_score_pct" and (metric["head"] < MUTATION_FLOOR or
                rule["threshold"] is None or rule["threshold"] < MUTATION_FLOOR):
            return "Mutation policy or measured score is below the existing floor"
    statuses = [m["comparison"] for m in result["metrics"].values() if m["state"] == "measured"]
    expected = "fail" if "fail" in statuses else "warn" if "warn" in statuses else "ok"
    if result["measurement_status"] != expected or result["worst_status"] != expected or expected == "fail":
        return "Metric summary contradicts measurements"
    # Each collector may have its own argv; admission identity comes from the
    # receipt's action hash and run ID, not an invented duplicate command field.
    if action["command"] is None:
        return "Metrics must execute an admitted producer command"
    return ""


class _Evaluation:
    def __init__(self, contract, ledger, inputs, *, prefixes=None):
        self.contract = contract
        self.ledger = ledger
        self.inputs = inputs
        self.events = ledger.document["events"]
        self.memo = {}
        self.active = set()
        # One evaluator/memo per prefix, owned by this public evaluation only.
        # Keeping current and historical memos separate also keeps reopened
        # diagnostics limited to current proof, without losing prefix reuse.
        self.prefixes = {} if prefixes is None else prefixes
        self.prefixes[len(self.events)] = self
        self.admissions = {e["run_id"]: e for e in self.events if e["kind"] == "admitted"}

    def snapshot(self, item):
        key = target_key(item)
        if key not in self.inputs.targets and item["kind"] == "check":
            # _snapshot_for(check) and _snapshot_for(its action) bind exactly
            # the same scope/components/action/check/claims. A direct action
            # dependency materializes only the latter; reuse that exact view.
            action = self.action_for(item)
            if action:
                key = target_key(make_target("action", action["id"]))
        return self.inputs.targets.get(key, BlockedInput("Target snapshot missing"))

    def action_for(self, item):
        if item["kind"] == "check":
            check = self.contract["checks"].get(item["id"])
            return self.contract["actions"].get(check["action_id"]) if check else None
        if item["kind"] == "action":
            return self.contract["actions"].get(item["id"])
        return None

    def matches(self, event, item):
        if event["target"] == item:
            return True
        action = self.action_for(item)
        return action is not None and event["target"] == make_target("action", action["id"])

    def latest(self, kind, item):
        return next((e for e in reversed(self.events) if e["kind"] == kind and self.matches(e, item)), None)

    def earlier_refs(self, refs, seq):
        return all(any(e["kind"] == "receipt-accepted" and ref in e["receipt_refs"] and e["seq"] < seq
                       for e in self.events) for ref in refs)

    def completed(self, item):
        event = self.latest("completed", item)
        action = self.action_for(item)
        if action and action["command"] is None:
            event = self.latest("receipt-accepted", make_target("check", next(
                c["id"] for c in self.contract["checks"].values() if c["action_id"] == action["id"])))
        if event is None:
            return None
        if action and action["command"] is not None and event["spawned"] != "yes":
            return None
        admission = self.admissions.get(event["run_id"])
        if not admission or not self.matches(admission, item):
            return None
        if any(e["run_id"] == event["run_id"] and e["kind"] in ("interrupted", "recovered") for e in self.events):
            return None
        return event

    def _execution(self, item, refs):
        event = self.completed(item)
        if event is None:
            return "missing", "Action has no completed admitted execution", refs
        action = self.action_for(item)
        execution_refs = refs
        if action["command"] is not None and not _command_succeeded(event):
            # Even a direct action consumer needs validated red proof, not just
            # a registered red kind or a nonzero command exit.
            check = next((c for c in self.contract["checks"].values() if c["action_id"] == action["id"]), None)
            red = self.proof(make_target("check", check["id"])) if check and check["kind"] == "behavioral-red" else None
            if red is None or red[0] != "valid":
                return "fail", "Action execution failed", refs
            execution_refs = _merge_refs([("valid", "", refs), red])
        current = self.snapshot(item)
        if isinstance(current, BlockedInput):
            return "blocked", current.reason, refs
        if not _fresh(event["inputs"], current):
            check = next((c for c in self.contract["checks"].values()
                          if c["action_id"] == action["id"] and c["validity"] == "before-action"), None)
            if check and self.proof(make_target("check", check["id"]))[0] == "valid":
                # Its receipt separately proves earlier consumption. The old
                # executed check is historical, not a demand to restore old code.
                return "valid", "", execution_refs
            return "stale", "Action post-execution inputs changed", refs
        admission = self.admissions[event["run_id"]]
        if not _refs_equal(admission["receipt_refs"], refs):
            return "stale", "Action prerequisite receipt chain changed", refs
        if not self.earlier_refs(refs, admission["seq"]):
            return "blocked", "Action prerequisites were not accepted before admission", refs
        return "valid", "", execution_refs

    def historical_consumption(self, check, ref):
        if check["validity"] != "before-action":
            return None
        consumer = next(a for a in self.contract["actions"].values()
                        if a["kind"] in ("work", "retire") and make_target("check", check["id"]) in a["requires"])
        node = make_target("action", consumer["id"])
        event = self.completed(node)
        if not event:
            return None
        current = self.snapshot(node)
        if isinstance(current, BlockedInput) or not _fresh(event["inputs"], current):
            return None
        admission = self.admissions[event["run_id"]]
        return admission if ref in admission["receipt_refs"] else None

    def _identity(self, check, receipt):
        action = self.contract["actions"][check["action_id"]]
        producer = receipt["producer"]
        if producer != action["owner"] or producer["role"] != check["owner_role"]:
            return "Receipt producer does not match registered check owner"
        increment = self.contract["increments"][action["increment"]]
        if check["context_rule"] == "independent":
            contexts = {p["context_id"] for p in increment["implementers"]}
            if producer["context_id"] in contexts:
                return "Check context is not independent of implementers"
        if check["kind"] in ("review", "verification"):
            opposite = "review" if check["kind"] == "verification" else "verification"
            others = [self.contract["actions"][c["action_id"]]["owner"]["context_id"]
                      for c in self.contract["checks"].values() if c["kind"] == opposite
                      and self.contract["actions"][c["action_id"]]["increment"] == action["increment"]]
            if producer["context_id"] in others:
                return "Reviewer and verifier contexts are not distinct"
        return ""

    def _receipt(self, check, event, ref, prerequisite_refs):
        observation = self.ledger.receipts.get(ref["id"])
        if observation is None or observation.status == "missing":
            return "missing", "Accepted receipt is missing"
        if observation.status != "valid" or observation.observed_sha256 != ref["sha256"]:
            return "stale", observation.reason or "Receipt/artifact bytes changed"
        receipt = observation.document
        if receipt is None or receipt["check_id"] != check["id"] or receipt["run_id"] != event["run_id"]:
            return "blocked", "Receipt/check/admission identity mismatch"
        if receipt["outcome"] != "pass":
            return receipt["outcome"], "Receipt outcome is " + receipt["outcome"]
        action = self.contract["actions"][check["action_id"]]
        node = make_target("check", check["id"])
        admission = self.admissions.get(receipt["run_id"])
        if not admission or not self.matches(admission, node) or admission["seq"] >= event["seq"]:
            return "blocked", "Receipt lacks an earlier matching admission"
        if (datetime.fromisoformat(receipt["started_at"]) < datetime.fromisoformat(admission["time"]) or
                datetime.fromisoformat(receipt["finished_at"]) > datetime.fromisoformat(event["time"])):
            return "blocked", "Receipt timestamps contradict admission/acceptance"
        identity_error = self._identity(check, receipt)
        if identity_error:
            return "blocked", identity_error
        if not _refs_equal(receipt["prerequisite_receipts"], admission["receipt_refs"]) or not _refs_equal(
                receipt["prerequisite_receipts"], prerequisite_refs):
            return "stale", "Receipt prerequisite chain changed"
        if not _fresh(receipt["inputs"], admission["inputs"]) or not _fresh(receipt["inputs"], event["inputs"]):
            return "stale", "Receipt differs from admitted/accepted inputs"
        if not self.earlier_refs(prerequisite_refs, admission["seq"]):
            return "blocked", "Prerequisite receipt was not accepted before admission"
        consumption = self.historical_consumption(check, ref)
        if consumption and event["seq"] >= consumption["seq"]:
            return "blocked", "Temporal proof was accepted after consuming admission"
        if consumption and check["kind"] == "compatibility":
            consumer = self.action_for(consumption["target"])
            retirement = consumer["retirement"] if consumer else None
            if retirement:
                before = receipt["inputs"]["source"]["files"]
                admitted = consumption["inputs"]["source"]["files"]
                if any(before.get(p, {}).get("mode", "missing") == "missing" or
                       before.get(p) != admitted.get(p) for p in retirement["expected_legacy_presence"]):
                    return "blocked", "Consumed compatibility did not observe legacy coexistence at admission"
        current = self.snapshot(node)
        if isinstance(current, BlockedInput):
            return "blocked", current.reason
        if not _fresh(receipt["inputs"], current, historical=consumption is not None):
            return "stale", "Relevant source/component/action/check/claim binding changed"
        completion = self.completed(make_target("action", action["id"]))
        if completion is None or completion["run_id"] != receipt["run_id"]:
            return "blocked", "Receipt has no matching completed execution/handoff"
        if completion["seq"] > event["seq"] or not _fresh(completion["inputs"], receipt["inputs"]):
            return "blocked", "Completion must precede acceptance on unchanged check inputs"
        if action["command"] is not None:
            if check["kind"] == "behavioral-red":
                if completion["outcome"] != "fail":
                    return "fail", "Behavioral red requires a recorded failed command and validated assertion"
            elif not _command_succeeded(completion):
                return "fail", "Receipt producer command did not complete successfully"
        result = receipt["result"]
        if check["kind"] in ("verification", "review", "research", "human"):
            error = _good_finding(result, check)
        elif check["kind"] == "metrics":
            error = _metric_result(result, receipt, action)
        else:
            error = _native_result(result, check, receipt, completion["child_exit"])
        return ("fail", error) if error else ("valid", "")

    def check(self, check_id):
        check = self.contract["checks"][check_id]
        item = make_target("check", check_id)
        action = self.contract["actions"][check["action_id"]]
        prerequisites = [self.proof(dep) for dep in dependencies(self.contract, make_target("action", action["id"]))]
        refs = _merge_refs(prerequisites)
        if any(state != "valid" for state, _, _ in prerequisites):
            return "blocked", "Check prerequisite is not complete/current", refs
        event = self.latest("receipt-accepted", item)
        if event is None:
            return "missing", "No accepted receipt for check", refs
        if len(event["receipt_refs"]) != 1:
            return "blocked", "Check acceptance must reference exactly one receipt", refs
        ref = event["receipt_refs"][0]
        state, reason = self._receipt(check, event, ref, refs)
        return state, reason, [ref]

    def claims(self, action):
        superseded = {name for c in self.contract["claims"].values() for name in c["supersedes"]}
        for name in action["claims"]:
            claim = self.contract["claims"][name]
            if name in superseded:
                return "Bound research claim was superseded: " + name
            if claim["epistemic"] not in ("FACT", "INFERENCE"):
                return "Bound research claim is unverified: " + name
            if claim["accepted_receipt"] is None:
                return "Research claim lacks attributed acceptance: " + name
            observation = self.ledger.receipts.get(claim["accepted_receipt"])
            if not observation or observation.status != "valid" or not observation.document:
                return "Research acceptance receipt unavailable"
            receipt = observation.document
            check = self.contract["checks"].get(receipt["check_id"])
            if not check or check["kind"] != "research":
                return "Research acceptance references a non-research check"
            if (receipt["producer"] != claim["correction_owner"] or
                    receipt["recorded_by"] != claim["acceptance_owner"]):
                return "Research correction/acceptance ownership mismatch"
            if receipt["inputs"]["contract"]["claims"].get(name) != canonical_hash(claim):
                return "Research acceptance does not bind this exact claim"
            accepted = self.proof(make_target("check", check["id"]))
            if accepted[0] != "valid":
                return "Research recheck is not current: " + accepted[1]
        return ""

    def closure_proven_before(self, item, event):
        """A closure is a fact supported by its prefix, not by later events.

        Re-evaluate the same derived graph against only earlier ledger facts.
        This includes member executions, null-command check acceptances and
        prerequisite increment/ship closures, not just the referenced blobs.
        The prefix must establish the closure's exact consumed ID/hash set;
        different earlier valid receipts cannot substitute for later proof.
        Current snapshots still govern freshness; this does not revive stale
        proof or manufacture an old source snapshot.
        """
        boundary = event["seq"] - 1
        prior = self.prefixes.get(boundary)
        if prior is None:
            prefix = dict(self.ledger.document, events=self.events[:boundary])
            prior = _Evaluation(self.contract, ResolvedLedger(prefix, self.ledger.receipts), self.inputs,
                                prefixes=self.prefixes)
        proofs = [prior.proof(dep) for dep in dependencies(self.contract, item)]
        return (all(state == "valid" for state, _, _ in proofs)
                and _refs_equal(event["receipt_refs"], _merge_refs(proofs)))

    def proof(self, item):
        key = target_key(item)
        if key in self.memo:
            return self.memo[key]
        if key in self.active:
            return "blocked", "Cyclic proof/claim reference", []
        self.active.add(key)
        current = self.snapshot(item)
        if isinstance(current, BlockedInput):
            result = ("blocked", current.reason, [])
        elif item["kind"] == "check":
            result = self.check(item["id"])
        else:
            prerequisites = [self.proof(dep) for dep in dependencies(self.contract, item)]
            refs = _merge_refs(prerequisites)
            if any(state != "valid" for state, _, _ in prerequisites):
                result = ("blocked", "Required dependency is not complete/current", refs)
            elif item["kind"] == "action":
                claim_error = self.claims(self.action_for(item))
                result = ("blocked", claim_error, refs) if claim_error else self._execution(item, refs)
            else:
                event = self.latest("closed", item)
                if event is None:
                    result = ("missing", "Closure has not been recorded", refs)
                elif not _fresh(event["inputs"], current) or not _refs_equal(event["receipt_refs"], refs):
                    result = ("stale", "Closure inputs/prerequisite receipts changed", refs)
                elif event["outcome"] != "pass" or (item["kind"] == "increment" and not event["completion_commit"]):
                    result = ("blocked", "Closure lacks successful commit-bound proof", refs)
                elif not self.closure_proven_before(item, event):
                    result = ("blocked", "Closure prerequisites were not established before closure", refs)
                else:
                    result = ("valid", "", refs)
        self.active.remove(key)
        self.memo[key] = result
        return result

    def unresolved(self):
        for run_id, admission in self.admissions.items():
            node = admission["target"]
            if not isinstance(node, dict):
                continue
            action = self.action_for(node)
            events = [e for e in self.events if e["run_id"] == run_id]
            if action and action["command"] is None:
                if not any(e["kind"] == "receipt-accepted" for e in events):
                    yield "AWAITING_RESPONSE", node, "Admitted external check is awaiting attributed proof"
            elif not any(e["kind"] == "completed" for e in events):
                yield "RECOVERY_UNVERIFIED", node, "Unresolved admission; direct exit or missing lock is not tree-termination proof"

    def admission(self, item):
        action = self.action_for(item)
        node = make_target("action", action["id"]) if action else item
        required = [self.proof(dep) for dep in dependencies(self.contract, node)]
        errors = []
        for dep, result in zip(dependencies(self.contract, node), required):
            if result[0] != "valid":
                errors.append((result[0].upper(), dep, result[1]))
        if action:
            error = self.claims(action)
            if error:
                errors.append(("RESEARCH_UNVERIFIED", node, error))
            if action["retirement"] and self.completed(node) is None:
                files = self.snapshot(node)["source"]["files"]
                if any(files.get(p, {}).get("mode", "missing") == "missing"
                       for p in action["retirement"]["expected_legacy_presence"]):
                    errors.append(("LEGACY_ABSENT", node, "Legacy paths must coexist before retirement admission"))
        return errors


def evaluate(contract, ledger, inputs, target):
    """Return authoritative readiness from materialized values only."""
    validate_contract(contract)
    validate_ledger(ledger.document)
    validate_target(target)
    validate_snapshot(inputs.target)
    if target_key(target) not in inputs.targets or inputs.targets[target_key(target)] != inputs.target:
        raise ValueError("Resolved inputs do not match requested target")
    for snapshot in inputs.targets.values():
        if not isinstance(snapshot, BlockedInput):
            validate_snapshot(snapshot)
    engine = _Evaluation(contract, ledger, inputs)
    errors = engine.admission(target)
    action = engine.action_for(target)
    for error in engine.unresolved():
        # An unrelated pending human handoff does not block independent work;
        # unknown process lifetime does block all further dispatch.
        if (error[0] == "RECOVERY_UNVERIFIED" or error[1] == target or
                (action is not None and engine.action_for(error[1]) == action)):
            errors.append(error)
    own = engine.proof(target) if target["kind"] != "action" or not action or action["kind"] != "check" else (
        engine.proof(make_target("check", next(c["id"] for c in contract["checks"].values()
                                             if c["action_id"] == action["id"]))))
    status = "blocked" if errors else "complete" if own[0] == "valid" else "ready"
    due_ids = set()
    root = make_target("action", action["id"]) if action else target
    for dep in dependencies(contract, root):
        due_ids.update(node["id"] for node in dependency_closure(contract, dep).values() if node["kind"] == "check")
    due = []
    for name in sorted(due_ids):
        state, reason, refs = engine.proof(make_target("check", name))
        check_action = contract["actions"][contract["checks"][name]["action_id"]]
        due.append({"check_id": name, "owner": check_action["owner"], "outcome": state, "receipt_refs": refs})
    blockers = []
    for code, node, reason in errors:
        owner_action = engine.action_for(node)
        blockers.append({"code": code, "target": node, "reason": reason,
                         "owner": owner_action["owner"] if owner_action else None,
                         "command_or_handoff_ref": "action:" + owner_action["id"] if owner_action else None})
    reopened = []
    for key, (state, reason, refs) in engine.memo.items():
        if state not in ("valid", "missing"):
            node = dict(zip(("kind", "id"), key.split(":", 1)))
            if any(engine.matches(e, node) and e["kind"] in ("completed", "receipt-accepted", "closed") for e in engine.events):
                prior = engine.latest("receipt-accepted" if node["kind"] == "check" else
                                      "closed" if node["kind"] in ("increment", "ship") else "completed", node)
                invalidated = prior["receipt_refs"] if prior else refs
                reopened.append({"id": key, "changed_prerequisites": [reason],
                                 "invalidated_receipts": [r["id"] for r in invalidated]})
    command = None
    if status == "ready" and action:
        command = ["python", "scripts/workflow.py", "next", "--slug", contract["slug"], "--action", action["id"]]
    return {"target": target, "status": status, "due": due,
            "future": sorted(set(contract["checks"]) - due_ids -
                             ({target["id"]} if target["kind"] == "check" else set())),
            "reopened": reopened, "blockers": blockers, "next_command": command,
            "ledger_seq": len(ledger.document["events"]), "inputs": inputs.target,
            "limitations": list(LIMITATIONS)}
