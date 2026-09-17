"""Actual public CLI execution with owned Git/process fixtures.

Design/role metadata is explicitly synthetic protocol data, not independent
agent approval. No successful metric receipt or recovery is manufactured.
"""

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import threading
import time
import unittest

from helpers import GitFixture
from workflow_fixtures import WorkflowFixture, scope
from evidence import write_json_atomic
from test_run import ProcessWitness
import workflow_state as state


SCRIPTS = Path(__file__).resolve().parents[1]
CLI = SCRIPTS / "workflow.py"
NODE = shutil.which("node")


class CliFixture(GitFixture):
    def run(self, *argv, expected=0, **kwargs):
        result = super().run(*argv, expected=None, **kwargs)
        transcript = os.environ.get("C2_CLI_TRANSCRIPT")
        if transcript:
            with open(transcript, "a", encoding="utf-8") as stream:
                stream.write(json.dumps({"argv": argv, "cwd": str(kwargs.get("cwd") or self.root),
                                         "exit": result[0], "stdout": result[1], "stderr": result[2]}) + "\n")
        if expected is not None and result[0] != expected:
            raise AssertionError("%r returned %s\n%s\n%s" % (argv, *result))
        return result

    def __init__(self):
        super().__init__()
        self.run("git", "symbolic-ref", "HEAD", "refs/heads/fixture-feature")
        template = WorkflowFixture()
        try:
            shutil.copytree(template.root, self.root, dirs_exist_ok=True)
            self.contract = deepcopy(template.contract)
            self.design = deepcopy(template.design)
        finally:
            template.close()
        self.workspace = self.root / ".ai/demo"
        for name in ("workflow.json", "current-design.json", "evidence/ledger.json"):
            (self.workspace / name).unlink()
        for increment in ("A", "B"):
            action = self.contract["actions"][increment + "-work"]
            action["command"]["argv"] = [
                sys.executable, "-B", "-c",
                "from pathlib import Path; Path('%s.marker').write_text('executed')" % increment]
        self.stage()

    def stage(self):
        self.design["review"]["candidate_hashes"]["workflow_contract"] = state.canonical_hash(self.contract)
        revision = self.design["revision"]
        write_json_atomic(self.workspace / ("design-history/%s.workflow.json" % revision), self.contract)
        write_json_atomic(self.workspace / ("design-history/%s.current-design.json" % revision), self.design)
        write_json_atomic(self.workspace / ("evidence/review-%s.json" % revision), self.design["review"])

    def cli(self, verb, *args, expected=0, hook=None):
        argv = [sys.executable, "-B", str(CLI), verb, "--slug", "demo", "--repo", str(self.root), *args]
        if hook:
            argv = [sys.executable, "-B", "-c", hook, str(SCRIPTS), *argv[3:]]
        code, stdout, stderr = self.run(*argv, expected=expected)
        lines = stdout.splitlines()
        value = json.loads(lines[-1]) if lines and lines[-1].startswith("{") else None
        transcript = os.environ.get("C2_CLI_TRANSCRIPT")
        if transcript and verb == "next" and value and "run_id" in value:
            run_id = value["run_id"]
            ledger = self.ledger()
            events = [event for event in ledger["events"] if event["run_id"] == run_id]
            command = state.read_json(self.workspace / "workflow.json")["actions"][args[1]]["command"]
            streams = {}
            for name in ("stdout", "stderr"):
                path = self.workspace / ("evidence/runs/%s/%s.txt" % (run_id, name))
                streams[name] = path.read_text(encoding="utf-8") if path.exists() else None
            with open(transcript, "a", encoding="utf-8") as stream:
                stream.write(json.dumps({
                    "record": "actual-guarded-run", "run_id": run_id, "registered_command": command,
                    "cwd": str((self.root / command["cwd"]).resolve()) if command else None,
                    "wrapper_exit": code, "events": events, **streams}) + "\n")
        return code, value, stdout, stderr

    def adopt(self, **kwargs):
        self.stage()
        revision = self.design["revision"]
        return self.cli("adopt", "--revision", revision, "--review",
                        ".ai/demo/evidence/review-%s.json" % revision, **kwargs)

    def revision(self):
        previous = deepcopy(self.design)
        revision = "r%d" % (len(previous["history"]) + 2)
        self.contract["design_revision"] = revision
        self.design["revision"] = revision
        self.design["supersedes"] = previous["revision"]
        self.design["history"] = previous["history"] + [
            {key: previous[key] for key in ("revision", "document", "contract")}]
        for key, folder, suffix in (("document", "design-history", "html"), ("contract", "contracts", "json")):
            content = (self.root / previous[key]["path"]).read_bytes()
            name = ".ai/demo/%s/%s.%s" % (folder, revision, suffix)
            self.write(name, content)
            self.design[key] = {"path": name, "sha256": hashlib.sha256(content).hexdigest()}
        self.stage()

    def native(self, check_id="A-test", *, red=False, setup=False):
        if NODE is None:
            raise RuntimeError("Node is required for real CLI native proof")
        filename = "tests/%s.test.mjs" % check_id
        body = ("import {test} from 'node:test';\n"
                "import assert from 'node:assert/strict';\n"
                "test('actual property', () => { assert.equal(%s, 1); });\n" % ("0" if red else "1"))
        if setup:
            body = "import './missing-dependency.mjs';\n" + body
        self.write(filename, body)
        check = self.contract["checks"][check_id]
        action = self.contract["actions"][check["action_id"]]
        action["inputs"] = scope("src/%s.py" % action["increment"], filename)
        action["command"]["argv"] = [NODE, "--test", "--test-reporter=" +
                                      (SCRIPTS / "native_result.mjs").as_uri(), filename]
        action["command"]["environment"] = {"NODE_TEST_CONTEXT": None}
        if red:
            check.update(kind="behavioral-red", validity="before-action")
            action["requires"] = []
            self.contract["actions"]["A-work"]["requires"] = [state.target("check", check_id)]
            check["assertions"] = [{
                "id": "assertion", "test_file": filename, "test_name": "actual property",
                "source_sha256": hashlib.sha256(body.encode()).hexdigest(),
                "assertion_lines": [4 if setup else 3], "purpose": "actual equality counterexample",
                "expected_red": {"operator": "strictEqual", "expected_relation": "1", "actual_relation": "0"}}]
        self.stage()

    def handoff(self, check_id="A-review"):
        self.contract["actions"][check_id + "-run"]["command"] = None
        self.contract["checks"][check_id]["handoff_steps"] = ["Return independently attributed actual observations"]
        self.stage()

    def returned_finding(self, admission, check_id="A-review"):
        raw = self.write(".ai/demo/evidence/returned.txt", "Operator observed actual A.marker; synthetic actor attribution.\n")
        ref = {"path": raw.relative_to(self.root).as_posix(), "sha256": hashlib.sha256(raw.read_bytes()).hexdigest()}
        check = self.contract["checks"][check_id]
        receipt = {
            "schema_version": 1, "id": "returned-" + admission["run_id"], "check_id": check_id,
            "run_id": admission["run_id"], "producer": self.contract["actions"][check["action_id"]]["owner"],
            "recorded_by": self.design["review"]["designer"], "outcome": "pass", "inputs": admission["inputs"],
            "prerequisite_receipts": admission["receipt_refs"],
            "result": {"kind": check["kind"], "verdict": "VERIFIED",
                       "scenarios": {"AC-A": {"verdict": "VERIFIED", "evidence_refs": [ref["path"]], "reason": ""}},
                       "findings": [], "source_artifact": ref, "disposition_refs": [],
                       "human_confirmation": "not-applicable"},
            "artifacts": [dict(ref, bytes=raw.stat().st_size, media_type="text/plain")],
            "started_at": admission["time"], "finished_at": admission["time"]}
        write_json_atomic(self.root / "return.json", receipt)
        return receipt

    def ledger(self):
        return state.read_json(self.workspace / "evidence/ledger.json")


def veto_publication(destination):
    return """
import json, os, sys
sys.path.insert(0, sys.argv[1])
import workflow
def audit(event, args):
    if event == 'os.rename' and str(args[1]).replace('\\\\','/').endswith(%r):
        raise OSError('test-owned audit denied actual publication')
sys.addaudithook(audit)
raise SystemExit(workflow.main(sys.argv[2:]))
""" % destination


class WorkflowCliTests(unittest.TestCase):
    def setUp(self):
        self.f = CliFixture()
        self.addCleanup(self.f.close)

    def test_help_five_verbs_no_recovery_and_strict_options(self):
        rc, out, err = self.f.run(sys.executable, "-B", str(CLI), "--help")
        self.assertEqual(rc, 0, err)
        self.assertIn("{status,next,record,close,adopt}", out)
        self.assertIn("producer bridge", out)
        self.assertIn("Recover is not implemented", out)
        for verb in ("status", "next", "record", "close", "adopt"):
            self.assertEqual(self.f.run(sys.executable, "-B", str(CLI), verb, "--help")[0], 0)
        for args in (["recover"], ["next", "--slug", "demo", "--action", "A-work", "--bypass"],
                     ["close", "--slug", "demo", "--ship", "--commit", "a" * 40]):
            with self.subTest(args=args):
                self.assertEqual(self.f.run(sys.executable, "-B", str(CLI), *args, expected=2)[0], 2)

    def test_real_initial_adoption_and_idempotency(self):
        first = self.f.adopt()[1]
        self.assertEqual(first["phase"], "B0")
        before = self.f.ledger()
        self.assertEqual([e["kind"] for e in before["events"]], ["adopted"])
        self.assertEqual(before["events"][0]["inputs"]["contract"]["binding_mode"], "guarded")
        self.assertEqual(self.f.adopt()[1]["phase"], "A3")
        self.assertEqual(self.f.ledger(), before)
        self.assertEqual(self.f.cli("status", "--target", "action:A-work")[1]["status"], "ready")
        self.assertEqual(self.f.cli("status", expected=1)[1]["status"], "blocked")

    def test_registered_spaced_argv_cwd_and_intent_before_child(self):
        self.f.write("space dir/input.txt", "input")
        action = self.f.contract["actions"]["A-work"]
        action["command"]["cwd"] = "space dir"
        action["command"]["argv"] = [sys.executable, "-B", "-c", (
            "import json,sys; from pathlib import Path; "
            "events=json.loads(Path('../.ai/demo/evidence/ledger.json').read_text())['events']; "
            "assert any(e['kind']=='launch-intent' for e in events); "
            "Path('../witness.json').write_text(json.dumps({'arg':sys.argv[1],'cwd':Path.cwd().name})); "
            "print('actual output')"), "one spaced argument"]
        self.f.adopt()
        result = self.f.cli("next", "--action", "A-work")[1]
        self.assertEqual(result["outcome"], "executed")
        self.assertEqual(json.loads((self.f.root / "witness.json").read_text()),
                         {"arg": "one spaced argument", "cwd": "space dir"})
        self.assertEqual(Path(result["stdout"]).read_text(), "actual output\n")
        events = self.f.ledger()["events"]
        self.assertEqual([e["kind"] for e in events],
                         ["adopted", "admitted", "launch-intent", "process-observed", "process-observed", "completed"])
        self.assertEqual(self.f.cli("next", "--action", "A-work")[1]["status"], "complete")
        self.assertEqual(self.f.ledger()["events"], events)

    def test_failed_launch_and_nonzero_exit_are_not_work_completion(self):
        self.f.contract["actions"]["A-work"]["command"]["argv"] = [str(self.f.root / "absent.exe")]
        self.f.contract["actions"]["B-work"]["command"]["argv"] = [sys.executable, "-B", "-c", "raise SystemExit(23)"]
        self.f.adopt()
        result = self.f.cli("next", "--action", "A-work", expected=127)[1]
        self.assertEqual(result["spawned"], "no")
        self.assertIsNone(result["child_exit"])
        self.assertEqual(self.f.cli("next", "--action", "B-work", expected=23)[1]["child_exit"], 23)
        self.assertFalse((self.f.root / "A.marker").exists())

    def test_missing_review_pair_blocks_then_actual_handoff_record_unblocks(self):
        self.f.handoff()
        self.f.contract["actions"]["B-work"]["requires"] = [state.target("check", "A-review")]
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        self.f.cli("next", "--action", "B-work", expected=1)
        self.assertFalse((self.f.root / "B.marker").exists())
        handoff = self.f.cli("next", "--action", "A-review-run")[1]
        self.assertEqual(handoff["outcome"], "awaiting-response")
        self.assertFalse(any(e["kind"] == "launch-intent" and e["run_id"] == handoff["run_id"]
                             for e in self.f.ledger()["events"]))
        receipt = self.f.returned_finding(handoff["admission"])
        self.f.cli("record", "--receipt", "return.json")
        self.f.cli("next", "--action", "B-work")
        self.assertTrue((self.f.root / "B.marker").exists())
        saved = state.read_json(self.f.workspace / ("evidence/receipts/%s.json" % receipt["id"]))
        self.assertEqual(saved["producer"], receipt["producer"])
        self.assertNotEqual(saved["producer"], saved["recorded_by"])

    def test_setup_vs_red_pair_uses_real_native_assertion(self):
        self.f.native(red=True, setup=True)
        self.f.adopt()
        bad = self.f.cli("next", "--action", "A-test-run", expected=1)[1]
        self.assertEqual(bad["proof"], "blocked")
        self.f.cli("next", "--action", "A-work", expected=1)
        self.assertFalse((self.f.root / "A.marker").exists())
        self.f.revision()
        self.f.native(red=True, setup=False)
        self.f.adopt()
        result = self.f.cli("next", "--action", "A-test-run", expected=1)[1]
        self.assertEqual(result["proof"]["outcome"], "accepted")
        self.f.cli("next", "--action", "A-work")
        self.assertTrue((self.f.root / "A.marker").exists())

    def test_stale_pair_fresh_process_reopens_only_affected_receipt(self):
        self.f.native()
        self.f.native("B-test")
        self.f.contract["actions"]["B-test-run"]["requires"] = []
        self.f.contract["actions"]["B-work"]["requires"] = [state.target("check", "A-test")]
        self.f.adopt()
        self.f.cli("next", "--action", "B-test-run")
        self.f.cli("next", "--action", "A-work")
        self.f.cli("next", "--action", "A-test-run")
        receipts = {p.name: p.read_bytes() for p in (self.f.workspace / "evidence/receipts").glob("*.json")}
        self.f.write("src/A.py", "VALUE = 2\n")
        result = self.f.cli("status", "--target", "action:B-work", expected=1)[1]
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(self.f.cli("status", "--target", "check:B-test")[1]["status"], "complete")
        self.f.cli("next", "--action", "B-work", expected=1)
        self.assertFalse((self.f.root / "B.marker").exists())
        self.f.cli("next", "--action", "A-work")
        self.f.cli("next", "--action", "A-test-run")
        self.f.cli("next", "--action", "B-work")
        for name, content in receipts.items():
            self.assertEqual((self.f.workspace / "evidence/receipts" / name).read_bytes(), content)

    def test_metrics_pair_failure_capture_and_independent_work_not_fake_closure(self):
        self.f.contract["actions"]["A-metrics-run"]["command"]["argv"] = [
            sys.executable, "-B", "-c", "import sys; print('real collector unavailable'); sys.exit(7)"]
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        result = self.f.cli("next", "--action", "A-metrics-run", expected=7)[1]
        self.assertIn("METRIC_ATTACHMENT_UNAVAILABLE", result["reason"])
        self.assertEqual(Path(result["stdout"]).read_text(), "real collector unavailable\n")
        self.assertFalse(any(e["kind"] == "receipt-accepted" for e in self.f.ledger()["events"]))
        self.f.cli("next", "--action", "B-work")
        self.assertTrue((self.f.root / "B.marker").exists())
        self.f.cli("close", "--ship", expected=2)  # Unborn Git HEAD is not commit proof.

    def test_compatibility_pair_requires_accepted_pre_retirement_proof(self):
        self.f.native()
        check = self.f.contract["checks"]["A-test"]
        check.update(kind="compatibility", validity="before-action")
        self.f.contract["actions"]["A-test-run"]["requires"] = []
        self.f.contract["actions"]["A-test-run"]["inputs"]["files"].append("legacy.txt")
        action = self.f.contract["actions"]["A-work"]
        action.update(kind="retire", requires=[state.target("check", "A-test")],
                      retirement={"legacy_scope": scope("legacy.txt"), "expected_legacy_presence": ["legacy.txt"]})
        action["command"]["argv"] = [sys.executable, "-B", "-c",
                                    "from pathlib import Path; Path('legacy.txt').unlink(); Path('A.marker').touch()"]
        self.f.write("legacy.txt", "coexisting implementation")
        self.f.adopt()
        self.f.cli("next", "--action", "A-work", expected=1)
        self.assertTrue((self.f.root / "legacy.txt").exists())
        self.f.cli("next", "--action", "A-test-run")
        before = self.f.ledger()
        self.f.cli("next", "--action", "A-work")
        self.assertFalse((self.f.root / "legacy.txt").exists())
        events = self.f.ledger()["events"]
        accepted = next(e for e in before["events"] if e["kind"] == "receipt-accepted")
        admission = next(e for e in events if e["kind"] == "admitted" and e["target"]["id"] == "A-work")
        self.assertLess(accepted["seq"], admission["seq"])
        self.assertEqual(admission["receipt_refs"], accepted["receipt_refs"])

    def test_record_rejects_wrong_producer_and_tampered_artifact(self):
        self.f.handoff()
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        admission = self.f.cli("next", "--action", "A-review-run")[1]["admission"]
        receipt = self.f.returned_finding(admission)
        wrong = deepcopy(receipt)
        wrong["producer"]["context_id"] = "different"
        write_json_atomic(self.f.root / "wrong.json", wrong)
        self.f.cli("record", "--receipt", "wrong.json", expected=1)
        self.f.write(".ai/demo/evidence/returned.txt", "tampered")
        self.f.cli("record", "--receipt", "return.json", expected=1)
        self.assertFalse(any(e["kind"] == "receipt-accepted" for e in self.f.ledger()["events"]))

    def test_actual_finding_producer_binds_declared_observed_artifacts(self):
        script = """import hashlib,json
from pathlib import Path
assert Path('A.marker').read_text()=='executed'
path=Path('.ai/demo/evidence/observed.txt')
path.write_text('Observed actual work marker')
ref={'path':path.as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
print(json.dumps({'kind':'review','verdict':'VERIFIED',
'scenarios':{'AC-A':{'verdict':'VERIFIED','evidence_refs':[ref['path']],'reason':''}},
'findings':[],'source_artifact':ref,'disposition_refs':[],'human_confirmation':'not-applicable'}))
"""
        self.f.write("review.py", script)
        action = self.f.contract["actions"]["A-review-run"]
        action["command"]["argv"] = [sys.executable, "-B", "review.py"]
        action["inputs"]["files"].append("review.py")
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        result = self.f.cli("next", "--action", "A-review-run")[1]
        self.assertEqual(result["proof"]["outcome"], "accepted")
        self.f.cli("status", "--target", "check:A-review")
        self.f.write(".ai/demo/evidence/observed.txt", "altered after acceptance")
        reopened = self.f.cli("status", "--target", "check:A-review")[1]
        self.assertEqual(reopened["status"], "ready")
        self.assertEqual(reopened["reopened"][0]["id"], "check:A-review")
        self.assertEqual(self.f.cli("next", "--action", "A-review-run")[1]["proof"]["outcome"], "accepted")

    def test_native_shaped_stdout_from_non_native_command_is_not_proof(self):
        self.f.native()
        action = self.f.contract["actions"]["A-test-run"]
        action["command"]["argv"] = [sys.executable, "-B", "-c",
                                    "print('{\"schema_version\":1}')", *action["command"]["argv"][1:]]
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        result = self.f.cli("next", "--action", "A-test-run", expected=1)[1]
        self.assertIn("registered direct Node", result["reason"])
        self.assertFalse(any(e["kind"] == "receipt-accepted" for e in self.f.ledger()["events"]))

    def test_successful_metric_command_still_cannot_attach_quality(self):
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        result = self.f.cli("next", "--action", "A-metrics-run", expected=1)[1]
        self.assertEqual(result["child_exit"], 0)
        self.assertIn("METRIC_ATTACHMENT_UNAVAILABLE", result["reason"])
        admission = next(e for e in self.f.ledger()["events"]
                         if e["kind"] == "admitted" and e["run_id"] == result["run_id"])
        receipt = self.f.returned_finding(admission, "A-metrics")
        # Schema-valid synthetic scores are ONLY a rejected protocol input.
        # They are not collected measurements or successful quality evidence.
        receipt["result"] = WorkflowFixture.metric(
            self.f, result["run_id"], admission["inputs"], receipt["artifacts"][0])
        state.validate_receipt(receipt)
        write_json_atomic(self.f.root / "return.json", receipt)
        returned = self.f.cli("record", "--receipt", "return.json", expected=1)[1]
        self.assertIn("METRIC_ATTACHMENT_UNAVAILABLE", returned["reason"])
        commit = self.f.commit()
        result = self.f.cli("close", "--increment", "A", "--commit", commit, expected=1)[1]
        self.assertIn("Required proof", result["reason"])
        self.assertFalse(any(e["kind"] in ("receipt-accepted", "closed") for e in self.f.ledger()["events"]))

    def test_record_requires_exact_earlier_prerequisite_receipt(self):
        self.f.native()
        self.f.handoff()
        self.f.contract["actions"]["A-review-run"]["requires"] = [state.target("check", "A-test")]
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        self.f.cli("next", "--action", "A-test-run")
        admission = self.f.cli("next", "--action", "A-review-run")[1]["admission"]
        receipt = self.f.returned_finding(admission)
        wrong = deepcopy(receipt)
        wrong["id"] = "wrong"
        wrong["prerequisite_receipts"] = []
        write_json_atomic(self.f.root / "wrong.json", wrong)
        self.f.cli("record", "--receipt", "wrong.json", expected=1)
        self.f.cli("record", "--receipt", "return.json")
        self.assertEqual(len(admission["receipt_refs"]), 1)

    def test_lexical_lock_contention_never_spawns_or_steals(self):
        self.f.adopt()
        path = self.f.workspace / "evidence/workflow.lock"
        path.write_bytes(b"owned test contention")
        self.f.cli("next", "--action", "A-work", expected=3)
        self.assertEqual(path.read_bytes(), b"owned test contention")
        self.assertFalse((self.f.root / "A.marker").exists())
        self.f.cli("status", "--target", "action:A-work")

    def test_publication_failures_retry_B1_A1_A2_once_without_rewriting_event(self):
        for suffix, phase in (("/evidence/ledger.json", "B1"), ("/workflow.json", "A1"),
                              ("/current-design.json", "A2")):
            f = CliFixture()
            try:
                f.adopt(expected=2, hook=veto_publication(suffix))
                before = f.ledger()
                result = f.adopt()[1]
                self.assertEqual(result["phase"], phase)
                self.assertEqual(len(f.ledger()["events"]), 1)
                if before["events"]:
                    self.assertEqual(f.ledger(), before)
            finally:
                f.close()

    def test_revised_adoption_retains_history_and_retries_exact_old_basis(self):
        self.f.adopt()
        old_w = (self.f.workspace / "workflow.json").read_bytes()
        old_p = (self.f.workspace / "current-design.json").read_bytes()
        self.f.revision()
        self.f.adopt(expected=2, hook=veto_publication("/current-design.json"))
        before = self.f.ledger()
        self.assertEqual(self.f.adopt()[1]["phase"], "A2")
        self.assertEqual(self.f.ledger(), before)
        self.assertEqual((self.f.workspace / "design-history/r1.workflow.json").read_bytes(), old_w)
        self.assertEqual((self.f.workspace / "design-history/r1.current-design.json").read_bytes(), old_p)

    def test_each_old_input_retain_failure_unwinds_for_exact_A0_retry(self):
        for suffix in ("workflow.json", "current-design.json"):
            f = CliFixture()
            try:
                f.adopt()
                old = {name: (f.workspace / name).read_bytes()
                       for name in ("workflow.json", "current-design.json")}
                # Coherent old live v1 authority permits absent retained copies.
                for name in old:
                    (f.workspace / ("design-history/r1." + name)).unlink()
                f.revision()
                hook = """
import sys
sys.path.insert(0,sys.argv[1])
import workflow
def audit(event,args):
    if (event=='open' and 'x' in str(args[1]) and
            str(args[0]).replace('\\\\','/').endswith(%r)):
        raise OSError('test-owned audit denied actual immutable retain')
sys.addaudithook(audit)
raise SystemExit(workflow.main(sys.argv[2:]))
""" % ("/r1." + suffix)
                before = f.ledger()
                f.adopt(expected=2, hook=hook)
                self.assertEqual(f.ledger(), before)
                self.assertFalse((f.workspace / "evidence/workflow.lock").exists())
                self.assertEqual(f.adopt()[1]["phase"], "A0")
                for name, content in old.items():
                    self.assertEqual((f.workspace / ("design-history/r1." + name)).read_bytes(), content)
            finally:
                f.close()

    def test_adoption_conflicting_candidate_and_out_of_order_publication_are_not_repaired(self):
        self.f.adopt(expected=2, hook=veto_publication("/workflow.json"))
        p = (self.f.workspace / "design-history/r1.current-design.json").read_bytes()
        (self.f.workspace / "current-design.json").write_bytes(p)
        before = self.f.ledger()
        self.f.adopt(expected=3)
        self.assertEqual(self.f.ledger(), before)

    def test_adoption_missing_review_and_unconfirmed_without_authorization_reject(self):
        self.f.design["review"]["unattended_authorization"] = None
        self.f.adopt(expected=2)
        self.assertFalse((self.f.workspace / "evidence/ledger.json").exists())

    def test_partial_retained_old_copy_is_conflict_not_overwritten(self):
        self.f.adopt()
        self.f.revision()
        path = self.f.workspace / "design-history/r1.workflow.json"
        path.write_bytes(b"partial owned fixture copy")
        before = self.f.ledger()
        self.f.adopt(expected=3)
        self.assertEqual(path.read_bytes(), b"partial owned fixture copy")
        self.assertEqual(self.f.ledger(), before)

    def test_candidate_change_between_parse_and_snapshot_has_no_adoption(self):
        hook = """
import os,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import workflow
reads=0
def audit(event,args):
    global reads
    if event=='open' and str(args[0]).replace('\\\\','/').endswith('/r1.workflow.json'):
        reads+=1
        if reads==2:
            path=Path(args[0])
            content=path.read_bytes()
            path.write_bytes(b' '+content)
sys.addaudithook(audit)
raise SystemExit(workflow.main(sys.argv[2:]))
"""
        self.f.adopt(expected=2, hook=hook)
        self.assertFalse((self.f.workspace / "evidence/ledger.json").exists())

    def test_bootstrap_refuses_remaining_real_run_artifacts_after_authority_loss(self):
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        for name in ("workflow.json", "current-design.json", "evidence/ledger.json"):
            (self.f.workspace / name).unlink()
        self.f.adopt(expected=3)
        self.assertFalse((self.f.workspace / "evidence/ledger.json").exists())

    def test_adoption_preserves_pending_handoff_and_rejects_runtime_id_removal(self):
        self.f.handoff()
        self.f.adopt()
        self.f.cli("next", "--action", "A-work")
        self.f.cli("next", "--action", "A-review-run")
        before = self.f.ledger()["events"]
        self.f.revision()
        self.assertEqual(self.f.adopt()[1]["phase"], "A0")
        self.assertEqual(self.f.ledger()["events"][:-1], before)
        self.f.revision()
        self.f.contract["actions"]["A-work-renamed"] = self.f.contract["actions"].pop("A-work")
        self.f.contract["actions"]["A-work-renamed"]["id"] = "A-work-renamed"
        for action in self.f.contract["actions"].values():
            for dependency in action["requires"]:
                if dependency == state.target("action", "A-work"):
                    dependency["id"] = "A-work-renamed"
        self.f.adopt(expected=3)

    def test_transient_lock_scope_is_explicit_input_error(self):
        self.f.contract["actions"]["A-work"]["inputs"]["files"].append(".ai/demo/evidence/workflow.lock")
        self.f.adopt()
        result = self.f.cli("next", "--action", "A-work", expected=2)[1]
        self.assertIn("transient workflow lock", result["reason"])
        self.assertFalse((self.f.root / "A.marker").exists())

    def test_close_rejects_wrong_commit_dirty_source_and_protected_branch(self):
        self.f.adopt()
        commit = self.f.commit()
        self.f.cli("close", "--increment", "A", "--commit", "a" * 40, expected=1)
        self.f.write("src/A.py", "VALUE = 9\n")
        result = self.f.cli("close", "--increment", "A", "--commit", commit, expected=1)[1]
        self.assertIn("Committed bytes", result["reason"])
        self.f.run("git", "symbolic-ref", "HEAD", "refs/heads/main")
        # Give the protected ref the same real commit without resetting any files.
        self.f.run("git", "update-ref", "refs/heads/main", commit)
        self.assertIn("feature branch", self.f.cli("close", "--ship", expected=1)[1]["reason"])

    def test_close_rejects_actual_locally_known_remote_default_branch(self):
        self.f.adopt()
        commit = self.f.commit()
        self.f.run("git", "update-ref", "refs/remotes/origin/fixture-feature", commit)
        self.f.run("git", "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/fixture-feature")
        self.assertIn("feature branch", self.f.cli("close", "--ship", expected=1)[1]["reason"])

    def test_observer_persistence_denial_leaves_durable_unresolved_intent(self):
        self.f.adopt()
        hook = """
import json,sys
sys.path.insert(0,sys.argv[1])
import workflow
def audit(event,args):
    if event == 'os.rename' and str(args[1]).endswith('ledger.json'):
        with open(args[0], encoding='utf-8') as stream: doc=json.load(stream)
        if doc['events'][-1]['kind']=='process-observed':
            raise OSError('actual ledger publication denied by test audit')
sys.addaudithook(audit)
raise SystemExit(workflow.main(sys.argv[2:]))
"""
        result = self.f.cli("next", "--action", "A-work", expected=125, hook=hook)[1]
        self.assertEqual(result["outcome"], "RECOVERY_UNVERIFIED")
        self.assertIn("[observer-error]", Path(result["stderr"]).read_text())
        self.assertFalse((self.f.workspace / "evidence/workflow.lock").exists())
        self.assertFalse(any(e["kind"] == "completed" for e in self.f.ledger()["events"]))
        self.f.cli("next", "--action", "B-work", expected=3)
        self.f.revision()
        self.f.adopt(expected=3)

    def test_real_pre_popen_exit_leaves_unresolved_intent_even_without_lock(self):
        self.f.adopt()
        hook = """
import os,sys
sys.path.insert(0,sys.argv[1])
import workflow
def audit(event,args):
    if event=='subprocess.Popen' and (sys.executable in str(args[0]) or sys.executable in str(args[1])):
        os._exit(71)
sys.addaudithook(audit)
raise SystemExit(workflow.main(sys.argv[2:]))
"""
        self.f.cli("next", "--action", "A-work", expected=71, hook=hook)
        self.assertEqual(self.f.ledger()["events"][-1]["kind"], "launch-intent")
        self.assertFalse((self.f.root / "A.marker").exists())
        self.f.cli("next", "--action", "B-work", expected=3)
        # Deliberately remove this test-owned collision file to prove that its
        # absence is NOT recovery authority. No production reset API is used.
        (self.f.workspace / "evidence/workflow.lock").unlink()
        self.f.cli("next", "--action", "B-work", expected=3)
        self.f.revision()
        self.f.adopt(expected=3)
        self.assertFalse((self.f.root / "B.marker").exists())

    def test_guard_death_while_owned_child_alive_keeps_next_blocked(self):
        self.f.contract["actions"]["A-work"]["command"]["argv"] = [sys.executable, "-B", "-c", (
            "import os,time; from pathlib import Path; Path('child.pid').write_text(str(os.getpid())); "
            "deadline=time.monotonic()+18\n"
            "while not Path('release').exists() and time.monotonic()<deadline: time.sleep(.02)\n"
            "Path('child.finished').touch()\n")]
        self.f.adopt()
        result = []
        worker = threading.Thread(target=lambda: result.append(
            self.f.cli("next", "--action", "A-work", expected=None)))
        worker.start()
        child = guard = None
        try:
            deadline = time.monotonic() + 10
            while not (self.f.root / "child.pid").exists():
                self.assertLess(time.monotonic(), deadline)
                time.sleep(.02)
            pid = int((self.f.root / "child.pid").read_text())
            child = ProcessWitness(pid)
            owner = state.read_json(self.f.workspace / "evidence/workflow.lock")
            guard = ProcessWitness(owner["guard_pid"])
            self.assertTrue(child.alive())
            self.assertTrue(guard.alive())
            os.kill(owner["guard_pid"], signal.SIGTERM)
            worker.join(8)
            self.assertFalse(worker.is_alive())
            self.assertFalse(guard.alive())
            self.assertTrue(child.alive())
            self.f.cli("next", "--action", "B-work", expected=3)
            readiness = self.f.cli("status", "--target", "action:B-work", expected=3)[1]
            self.assertIn("RECOVERY_UNVERIFIED", {b["code"] for b in readiness["blockers"]})
        finally:
            self.f.write("release", "test-owned child release")
            worker.join(25)
            if child:
                deadline = time.monotonic() + 10
                while child.alive() and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertFalse(child.alive())
                child.close()
            if guard:
                guard.close()
        self.assertTrue((self.f.root / "child.finished").exists())


if __name__ == "__main__":
    unittest.main()
