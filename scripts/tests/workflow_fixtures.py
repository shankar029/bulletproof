"""Synthetic protocol fixtures, never claims of actual independent/quality proof.

All hashes, artifact bytes, directories and persistence calls are real. Producer
identities and passing native/metric records are explicitly test data.
"""

from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import exclusive_lock, source_snapshot, write_json_atomic
from workflow_state import (
    append_event, bind_inputs, canonical_hash, load_workspace, read_json, target,
)


TIME = "2026-09-17T00:00:00+00:00"


def producer(role="implementer", context=None):
    return {"actor_id": "fixture-account", "context_id": context or role,
            "role": role, "host": "fixture-host", "model": "fixture-model"}


def scope(*files):
    return {"files": list(files), "directories": [], "excluded_outputs": []}


def command():
    return {"argv": [sys.executable, "-B", "-c", "print('fixture invocation')"],
            "cwd": ".", "runtime": {"executable": sys.executable, "observed_version": sys.version.split()[0]},
            "idle_seconds": 30, "max_seconds": 90, "environment": {}}


class WorkflowFixture:
    def __init__(self):
        self.directory = tempfile.TemporaryDirectory(prefix="bulletproof-workflow-fixture-")
        self.root = Path(self.directory.name)
        self.workspace = self.root / ".ai/demo"
        self.workspace.mkdir(parents=True)
        self.serial = 0
        self.contract = {"schema_version": 1, "slug": "demo", "design_revision": "r1",
                         "increments": {}, "actions": {}, "checks": {}, "claims": {},
                         "revision_reason": "Synthetic protocol fixture"}
        self.components = {"a": {"signature": "a() -> int"}, "b": {"signature": "b() -> int"}}
        for name in ("A", "B"):
            self.write("src/%s.py" % name, "VALUE = 1\n")
            self.contract["increments"][name] = {
                "id": name, "acs": ["AC-" + name], "components": [name.lower()],
                "requires": [], "implementers": [producer()]}
            self.add_action(name + "-work", name, inputs=scope("src/%s.py" % name))
            for suffix, kind, role in (("test", "test", "implementer"), ("verify", "verification", "verifier"),
                                       ("review", "review", "reviewer"), ("metrics", "metrics", "implementer")):
                check_id = name + "-" + suffix
                self.add_check(check_id, name, kind, role, inputs=scope("src/%s.py" % name),
                               requires=[target("action", name + "-work")])
                self.contract["increments"][name]["requires"].append(target("check", check_id))
        write_json_atomic(self.workspace / "evidence/ledger.json", {"schema_version": 1, "slug": "demo", "events": []})
        self.design = None
        self.adopt()

    def close(self):
        self.directory.cleanup()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return path

    def artifact(self, name, content="Synthetic protocol evidence\n", *, full=False):
        path = self.write(name, content)
        value = {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        if full:
            value.update(bytes=path.stat().st_size, media_type="text/plain")
        return value

    def add_action(self, name, increment, *, kind="work", inputs=None, requires=None, owner=None, retirement=None):
        self.contract["actions"][name] = {
            "id": name, "increment": increment, "kind": kind, "requires": requires or [],
            "command": command(), "owner": owner or producer(), "inputs": inputs or scope(),
            "components": [increment.lower()], "claims": [], "declared_changes": [],
            "retirement": retirement}

    def add_check(self, name, increment, kind="test", role="implementer", *, inputs=None,
                  requires=None, validity="current", handoff=False):
        self.add_action(name + "-run", increment, kind="check", inputs=inputs,
                        requires=requires, owner=producer(role))
        if handoff:
            self.contract["actions"][name + "-run"]["command"] = None
        self.contract["checks"][name] = {
            "id": name, "action_id": name + "-run", "acs": ["AC-" + increment], "kind": kind,
            "owner_role": role, "context_rule": "independent" if role in ("verifier", "reviewer") else "same-allowed",
            "validity": validity, "assertions": [], "pass_condition": "Fixture scenario is verified",
            "handoff_steps": ["Return attributed fixture evidence"] if handoff else []}

    def event(self, kind, item, run_id, inputs, *, refs=None, outcome="ready", spawned="no",
              child_exit=None, process=None, commit=None):
        return {"kind": kind, "target": item, "run_id": run_id, "inputs": deepcopy(inputs),
                "receipt_refs": deepcopy(refs or []), "producer": producer(),
                "outcome": outcome, "process": process, "child_exit": child_exit,
                "spawned": spawned, "completion_commit": commit, "time": TIME, "reason": "Fixture event"}

    def append(self, event):
        ledger = read_json(self.workspace / "evidence/ledger.json")
        with exclusive_lock(self.workspace / "fixture.lock", {"token": "fixture"}):
            return append_event(self.workspace, event, len(ledger["events"]))

    def adopt(self):
        previous = self.design
        revision = self.contract["design_revision"]
        if previous and previous["revision"] == revision:
            revision = "r%d" % (len(previous["history"]) + 2)
            self.contract["design_revision"] = revision
        document = self.artifact(".ai/demo/design-history/%s.html" % revision, "<h1>Fixture %s</h1>" % revision)
        normative_path = self.workspace / ("contracts/%s.json" % revision)
        write_json_atomic(normative_path, self.components)
        normative = {"path": normative_path.relative_to(self.root).as_posix(),
                     "sha256": hashlib.sha256(normative_path.read_bytes()).hexdigest()}
        review_artifact = self.artifact(".ai/demo/evidence/design-%s.txt" % revision, "Fixture APPROVE, not actual review\n")
        authorization = self.artifact(".ai/demo/evidence/authorization.txt", "Fixture unattended authorization\n")
        hashes = {key: canonical_hash(value) for key, value in self.components.items()}
        self.design = {
            "schema_version": 1, "revision": revision, "document": document, "contract": normative,
            "components": hashes, "supersedes": previous["revision"] if previous else None,
            "review": {"producer": producer("reviewer", "design-reviewer"), "designer": producer(),
                       "candidate_hashes": {"document": document["sha256"], "components": hashes,
                                            "workflow_contract": canonical_hash(self.contract)},
                       "verdict": "APPROVE", "artifact": review_artifact, "disposition_refs": [],
                       "human_approval": "unconfirmed", "unattended_authorization": authorization},
            "history": previous["history"] + [{key: previous[key] for key in ("revision", "document", "contract")}]
                       if previous else [],
            "reason": "Synthetic adoption"}
        write_json_atomic(self.workspace / "workflow.json", self.contract)
        write_json_atomic(self.workspace / "current-design.json", self.design)
        inputs = {"source": source_snapshot(self.root, scope(document["path"], normative["path"])),
                  "contract": {"binding_mode": "guarded", "adopted_contract_sha256": canonical_hash(self.contract),
                               "components": hashes, "actions": {}, "checks": {}, "claims": {}}}
        self.append(self.event("adopted", revision, "adopt-" + revision, inputs))

    def inputs(self, item):
        return bind_inputs(self.root, self.contract, item)

    def load(self):
        return load_workspace(self.root, "demo")

    def start(self, action_id, refs=None):
        self.serial += 1
        run_id = "run-%d" % self.serial
        item = target("action", action_id)
        snapshot = self.inputs(item).target
        handoff = self.contract["actions"][action_id]["command"] is None
        self.append(self.event("admitted", item, run_id, snapshot, refs=refs,
                               outcome="awaiting-response" if handoff else "ready"))
        if not handoff:
            self.append(self.event("launch-intent", item, run_id, snapshot, spawned="unknown"))
            self.append(self.event("process-observed", item, run_id, snapshot, spawned="yes",
                                   process={"phase": "spawned", "pid": 1234, "process_group": None,
                                            "start_identity": None, "identity_evidence": None,
                                            "returncode": None, "cleanup": "not-attempted", "error": None}))
        return run_id, snapshot

    def finish(self, action_id, run_id, *, code=0):
        item = target("action", action_id)
        snapshot = self.inputs(item).target
        self.append(self.event("process-observed", item, run_id, snapshot, spawned="yes",
                               process={"phase": "direct-exited", "pid": 1234, "process_group": None,
                                        "start_identity": None, "identity_evidence": None,
                                        "returncode": code, "cleanup": "not-attempted", "error": None}))
        return self.append(self.event("completed", item, run_id, snapshot, outcome="executed" if code == 0 else "fail",
                                      child_exit=code, spawned="yes"))

    def work(self, action_id, refs=None, change=None):
        run_id, _ = self.start(action_id, refs)
        if change:
            change()
        self.finish(action_id, run_id)
        return run_id

    def native(self, outcome="pass"):
        return {"schema_version": 1, "complete": True, "leaf_count": 1,
                "tests": [{"file": "fixture.test.mjs", "line": 1, "name": "fixture property",
                           "nesting": 0, "outcome": outcome}], "logs": []}

    def metric(self, run_id, inputs, artifact):
        names = ["duplication_pct", "complexity_max", "complexity_avg", "cycles", "dead_exports",
                 "static_findings", "mutation_score_pct", "diff_coverage_pct", "architecture_rules"]
        rules, metrics = {}, {}
        for name in names:
            floor = name in ("mutation_score_pct", "diff_coverage_pct")
            rules[name] = {"mode": "floor" if floor else "compare",
                           "threshold": 60 if name == "mutation_score_pct" else 80 if floor else None,
                           "origin": "built-in", "origin_ref": "Synthetic fixture"}
            metrics[name] = {"name": name, "state": "measured", "base": 100 if floor else 0,
                             "head": 100 if floor else 0, "comparison": "ok", "reason": "",
                             "run_id": run_id, "source": inputs["source"], "command": command(),
                             "artifacts": [{k: artifact[k] for k in ("path", "sha256", "bytes")}],
                             "scope_support": {"measured_paths": list(inputs["source"]["files"]),
                                               "unsupported_paths": []}}
        policy = {"schema_version": 1, "required": names, "rules": rules,
                  "sha256": canonical_hash({"required": names, "rules": rules})}
        return {"schema_version": 2, "run_id": run_id, "source": inputs["source"], "baseline": "compared",
                "measurement_status": "ok", "completeness": "complete", "missing_required": [],
                "verdict": "pass", "metrics": metrics, "unavailable": [], "worst_status": "ok",
                "policy": policy, "generated": TIME}

    def receipt(self, check_id, *, refs=None, mutate=None, code=0):
        check = self.contract["checks"][check_id]
        action_id = check["action_id"]
        run_id, snapshot = self.start(action_id, refs)
        if self.contract["actions"][action_id]["command"] is not None:
            self.finish(action_id, run_id, code=code)
        receipt_id = "receipt-" + run_id
        artifact = self.artifact(".ai/demo/evidence/runs/%s/result.txt" % run_id, full=True)
        if check["kind"] in ("verification", "review", "research", "human"):
            result = {"kind": check["kind"], "verdict": "VERIFIED",
                      "scenarios": {ac: {"verdict": "VERIFIED", "evidence_refs": [artifact["path"]], "reason": ""}
                                    for ac in check["acs"]},
                      "findings": [], "source_artifact": {k: artifact[k] for k in ("path", "sha256")},
                      "disposition_refs": [], "human_confirmation": "confirmed" if check["kind"] == "human" else "not-applicable"}
        elif check["kind"] == "metrics":
            result = self.metric(run_id, snapshot, artifact)
        else:
            result = self.native()
        value = {"schema_version": 1, "id": receipt_id, "check_id": check_id, "run_id": run_id,
                 "producer": self.contract["actions"][action_id]["owner"], "recorded_by": producer(),
                 "outcome": "pass", "inputs": snapshot, "prerequisite_receipts": refs or [],
                 "result": result, "artifacts": [artifact], "started_at": TIME, "finished_at": TIME}
        if mutate:
            mutate(value)
        path = self.workspace / ("evidence/receipts/%s.json" % receipt_id)
        write_json_atomic(path, value)
        ref = {"id": receipt_id, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.append(self.event("receipt-accepted", target("check", check_id), run_id, snapshot,
                               refs=[ref], outcome="pass"))
        return ref

    def complete_increment(self, name):
        self.work(name + "-work")
        refs = [self.receipt(name + "-" + suffix) for suffix in ("test", "verify", "review", "metrics")]
        item = target("increment", name)
        self.append(self.event("closed", item, "close-" + name, self.inputs(item).target,
                               refs=refs, outcome="pass", commit="a" * 40))
        return refs
