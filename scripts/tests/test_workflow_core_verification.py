"""Independent bounded C1 verification; no runtime CLI or quality-pass claim.

Contracts: r2 design-contracts.json and c1-resolved-views. The fixture supplies
synthetic protocol receipts/identities only. Real public APIs, files, locks and
fresh Python processes are exercised. No production policy is mocked.

Additional oracles: scoped multi-hop reopening, strict UTC/schema boundaries,
increment-local context independence, closure chronology, conservative process
facts, temporal contract freshness, selective research anchors and no-I/O gate.
"""

from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from workflow_fixtures import WorkflowFixture, producer, scope
from evidence import write_json_atomic
from run import run_capture
from workflow_gate import evaluate
from workflow_state import (
    read_json, target, validate_contract, validate_design,
    validate_event, validate_ledger, validate_receipt,
)


SCRIPTS = Path(__file__).resolve().parents[1]


class CoreVerificationTests(unittest.TestCase):
    def setUp(self):
        self.f = WorkflowFixture()
        self.addCleanup(self.f.close)

    def decision(self, kind="increment", name="A"):
        contract, _, ledger = self.f.load()
        node = target(kind, name)
        return evaluate(contract, ledger, self.f.inputs(node), node)

    def receipt_bytes(self):
        return {p.name: p.read_bytes()
                for p in (self.f.workspace / "evidence/receipts").glob("*.json")}

    def fresh_decisions(self):
        code = """
import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from workflow_state import load_workspace, bind_inputs, target
from workflow_gate import evaluate
root = Path(sys.argv[2])
c, d, ledger = load_workspace(root, 'demo')
results = {}
for name in ('A', 'B'):
    node = target('increment', name)
    results[name] = evaluate(c, ledger, bind_inputs(root, c, node), node)
print(json.dumps({'pid': os.getpid(), 'revision': d['revision'], 'results': results}))
"""
        rc, out, err = run_capture(
            [sys.executable, "-B", "-c", code, str(SCRIPTS), str(self.f.root)],
            cwd=str(self.f.root), idle=30, max_total=90)
        self.assertEqual(rc, 0, (out, err))
        result = json.loads(out)
        self.assertNotEqual(result["pid"], os.getpid())
        return result

    def test_directory_membership_and_missing_path_resume_preserve_other_branch(self):
        for action in self.f.contract["actions"].values():
            if action["increment"] == "A":
                action["inputs"]["directories"] = ["inputs/A"]
                action["inputs"]["files"].append("future-A.txt")
        self.f.write("inputs/A/one.txt", "one")
        self.f.adopt()
        self.f.complete_increment("A")
        self.f.complete_increment("B")
        before = self.receipt_bytes()
        self.assertEqual(self.fresh_decisions()["results"]["A"]["status"], "complete")
        for path in ("inputs/A/two.txt", "future-A.txt"):
            with self.subTest(path=path):
                self.f.write(path, "new membership")
                result = self.fresh_decisions()["results"]
                self.assertEqual(result["A"]["status"], "blocked")
                self.assertEqual(result["B"]["status"], "complete")
                self.assertEqual(self.receipt_bytes(), before)
                self.assertFalse(result["B"]["reopened"])
                (self.f.root / path).unlink()
        self.assertEqual(self.fresh_decisions()["results"]["A"]["status"], "complete")

    def test_multihop_different_scope_receipt_replacement_and_check_change(self):
        self.f.contract["actions"]["B-review-run"]["requires"].append(target("check", "A-test"))
        self.f.adopt()
        self.f.work("A-work")
        a = self.f.receipt("A-test")
        self.f.work("B-work")
        self.f.receipt("B-test")
        self.f.receipt("B-verify")
        self.f.receipt("B-metrics")
        dependent = self.f.receipt("B-review", refs=[a])
        self.assertEqual(self.decision("check", "B-review")["status"], "complete")
        before = self.receipt_bytes()
        replacement = self.f.receipt("A-test")
        result = self.decision("increment", "B")
        due = {d["check_id"]: d["outcome"] for d in result["due"]}
        self.assertEqual(due["B-review"], "stale")
        self.assertEqual(due["B-test"], "valid")
        reopened = {r["id"]: r["invalidated_receipts"] for r in result["reopened"]}
        self.assertEqual(reopened["check:B-review"], [dependent["id"]])
        self.f.receipt("B-review", refs=[replacement])
        self.assertEqual(self.decision("check", "B-review")["status"], "complete")
        self.f.contract["checks"]["A-test"]["pass_condition"] += "; newly required assertion"
        self.f.adopt()
        self.assertEqual(self.decision("check", "B-review")["status"], "blocked")
        for name, content in before.items():
            self.assertEqual(self.receipt_bytes()[name], content)

    def test_context_independence_is_increment_local_but_includes_all_implementers(self):
        # B implementer's context can review A: B did not implement A.
        self.f.contract["increments"]["B"]["implementers"] = [producer(context="B-author")]
        for action in self.f.contract["actions"].values():
            if action["increment"] == "B" and action["owner"]["role"] == "implementer":
                action["owner"] = producer(context="B-author")
        self.f.contract["actions"]["A-review-run"]["owner"] = producer("reviewer", "B-author")
        self.f.adopt()
        self.f.complete_increment("A")
        self.assertEqual(self.decision()["status"], "complete")
        # The same context becoming a declared A co-implementer invalidates review,
        # even when the primary A-work owner remains unchanged.
        self.f.contract["increments"]["A"]["implementers"].append(producer(context="B-author"))
        self.f.adopt()
        result = self.decision()
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(next(d["outcome"] for d in result["due"]
                              if d["check_id"] == "A-review"), "blocked")

    def test_nested_unknown_fields_cannot_be_persisted_as_alternate_authority(self):
        self.f.work("A-work")
        ref = self.f.receipt("A-test")
        receipt = self.f.load()[2].receipts[ref["id"]].document
        ledger = self.f.load()[2].document
        cases = [
            (validate_contract, self.f.contract, ("increments", "A"), "due_checks"),
            (validate_contract, self.f.contract, ("actions", "A-work"), "depends_on"),
            (validate_contract, self.f.contract, ("checks", "A-test"), "gates"),
            (validate_design, self.f.design, ("review",), "waiver"),
            (validate_receipt, receipt, ("inputs",), "targets"),
            (validate_receipt, receipt, ("result", "tests", 0), "passed"),
            (validate_receipt, receipt, ("producer",), "authenticated"),
            (validate_ledger, ledger, ("events", 1), "recovery_verified"),
        ]
        for validator, original, route, key in cases:
            with self.subTest(route=route, key=key):
                value = deepcopy(original)
                node = value
                for part in route:
                    node = node[part]
                node[key] = True
                with self.assertRaises(ValueError):
                    validator(value)

    def test_date_shaped_value_with_offset_suffix_is_not_a_utc_timestamp(self):
        event = deepcopy(self.f.load()[2].document["events"][0])
        event["time"] = "2026-09-17+00:00"
        # datetime.fromisoformat accepts this as naive midnight, NOT UTC.
        with self.assertRaises(ValueError):
            validate_event(event)

    def test_closure_cannot_be_retroactively_satisfied_by_later_receipts(self):
        self.f.complete_increment("A")
        self.assertEqual(self.decision()["status"], "complete")
        path = self.f.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        closure = ledger["events"].pop()
        self.assertEqual(closure["kind"], "closed")
        # Immutable referenced blobs exist, but acceptance and execution occur
        # AFTER this forged closure. Equal timestamps deliberately cannot help.
        ledger["events"].insert(1, closure)
        for seq, event in enumerate(ledger["events"], 1):
            event["seq"] = seq
        write_json_atomic(path, ledger)
        try:
            result = self.decision()
        except ValueError:
            return  # A strict top-level rejection is also conservative.
        self.assertNotEqual(result["status"], "complete",
                            "A pre-execution closure was retroactively completed")

    def test_launch_failed_cannot_claim_successful_work_execution(self):
        item = target("action", "A-work")
        snapshot = self.f.inputs(item).target
        run = "never-spawned"
        self.f.append(self.f.event("admitted", item, run, snapshot))
        self.f.append(self.f.event("launch-intent", item, run, snapshot, spawned="unknown"))
        try:
            self.f.append(self.f.event("process-observed", item, run, snapshot,
                process={"phase": "launch-failed", "pid": None, "process_group": None,
                         "start_identity": None, "identity_evidence": None, "returncode": 0,
                         "cleanup": "not-attempted", "error": "Fixture OS spawn failure"},
                spawned="no"))
            self.f.append(self.f.event("completed", item, run, snapshot,
                                      outcome="executed", child_exit=0, spawned="no"))
            result = self.decision("action", "A-work")
        except ValueError:
            return
        self.assertNotEqual(result["status"], "complete",
                            "No child existed, yet work is reported complete")

    def test_historical_consumption_preserves_source_not_changed_contracts(self):
        self.f.write("legacy.py", "LEGACY = 1\n")
        self.f.add_check("A-before", "A", "compatibility",
                         inputs=scope("legacy.py", "src/A.py"), validity="before-action")
        self.f.contract["actions"]["A-work"].update(
            kind="retire", requires=[target("check", "A-before")],
            retirement={"legacy_scope": scope("legacy.py"), "expected_legacy_presence": ["legacy.py"]})
        self.f.contract["increments"]["A"]["requires"].append(target("check", "A-before"))
        self.f.adopt()
        old = self.f.receipt("A-before")
        self.f.work("A-work", [old], change=lambda: (self.f.root / "legacy.py").unlink())
        before = self.receipt_bytes()
        self.f.components["b"]["signature"] = "b(value) -> bool"
        self.f.adopt()
        result = self.decision()
        self.assertEqual(next(d["outcome"] for d in result["due"]
                              if d["check_id"] == "A-before"), "valid")
        self.assertEqual(result["status"], "blocked")  # Post-retirement proof still absent.
        self.f.contract["checks"]["A-before"]["pass_condition"] += "; new rollback requirement"
        self.f.adopt()
        result = self.decision()
        self.assertNotEqual(next(d["outcome"] for d in result["due"]
                                 if d["check_id"] == "A-before"), "valid")
        self.assertEqual(self.receipt_bytes(), before)
        self.assertFalse((self.f.root / "legacy.py").exists())

    def test_research_heading_is_selective_but_bound_source_is_not(self):
        section = "# inspected\nOnly src/A.py was inspected.\n"
        report = ".ai/demo/research.md"
        self.f.write(report, section + "# unrelated\nOriginal note.\n")
        self.f.add_check("research-A", "A", "research", "researcher", inputs=scope("src/A.py"))
        claim = {
            "claim_id": "claim-A", "report": report + "#inspected",
            "claim_sha256": hashlib.sha256(section.encode()).hexdigest(),
            "epistemic": "FACT", "scope": {"paths": ["src/A.py"], "query": "VALUE"},
            "source_refs": [{"path": "src/A.py", "sha256": hashlib.sha256(
                (self.f.root / "src/A.py").read_bytes()).hexdigest(),
                "lines": [1], "snippet_ref": "VALUE = 1"}],
            "supersedes": [], "correction_owner": producer("researcher"),
            "acceptance_owner": producer(), "accepted_receipt": "receipt-run-1",
        }
        self.f.contract["claims"]["claim-A"] = claim
        self.f.contract["actions"]["research-A-run"]["claims"] = ["claim-A"]
        self.f.contract["actions"]["A-work"].update(
            claims=["claim-A"], requires=[target("check", "research-A")])
        self.f.adopt()
        self.f.receipt("research-A")
        self.assertEqual(self.decision("action", "A-work")["status"], "ready")
        self.f.write(report, section + "# unrelated\nChanged unrelated note.\n")
        self.assertEqual(self.decision("action", "A-work")["status"], "ready")
        self.f.write("src/A.py", "VALUE = 2\n")
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            self.decision("action", "A-work")

    def test_materialized_gate_is_repeatable_without_files_processes_or_network(self):
        self.f.complete_increment("A")
        contract, _, ledger = self.f.load()
        node = target("increment", "A")
        inputs = self.f.inputs(node)
        frozen = deepcopy((contract, ledger, inputs))
        self.f.write("src/A.py", "VALUE = 99\n")
        with ExitStack() as stack:
            for name in ("builtins.open", "io.open", "os.open", "os.stat", "os.scandir",
                         "subprocess.Popen", "socket.socket"):
                stack.enter_context(patch(name, side_effect=AssertionError("Gate I/O: " + name)))
            first = evaluate(contract, ledger, inputs, node)
            second = evaluate(contract, ledger, inputs, node)
        self.assertEqual(first["status"], "complete")  # Materialized view, not dispatch authority.
        self.assertEqual(first, second)
        self.assertEqual((contract, ledger, inputs), frozen)
        self.assertEqual(self.decision()["status"], "blocked")  # Fresh binding sees edit.

    def test_fresh_process_append_and_stale_sequence_preserve_ledger_bytes(self):
        code = """
import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from evidence import exclusive_lock
from workflow_state import append_event, read_json, SequenceConflict
root = Path(sys.argv[2])
try:
    with exclusive_lock(root / 'child.lock', {'token': 'verification-child'}):
        result = append_event(root, read_json(root / 'candidate.json'), int(sys.argv[3]))
except SequenceConflict:
    print('sequence-conflict')
    sys.exit(3)
print(json.dumps({'pid': os.getpid(), 'event': result}))
"""
        node = target("action", "A-work")
        event = self.f.event("admitted", node, "child-admission", self.f.inputs(node).target)
        write_json_atomic(self.f.workspace / "candidate.json", event)
        path = self.f.workspace / "evidence/ledger.json"
        before = path.read_bytes()
        argv = [sys.executable, "-B", "-c", code, str(SCRIPTS), str(self.f.workspace)]
        rc, out, err = run_capture(argv + ["0"], idle=30, max_total=90)
        self.assertEqual((rc, out.strip(), err), (3, "sequence-conflict", ""))
        self.assertEqual(path.read_bytes(), before)
        rc, out, err = run_capture(argv + ["1"], idle=30, max_total=90)
        self.assertEqual(rc, 0, (out, err))
        observed = json.loads(out)
        self.assertNotEqual(observed["pid"], os.getpid())
        self.assertEqual(observed["event"]["seq"], 2)
        self.assertEqual(self.f.load()[2].document["events"][-1], observed["event"])
        self.assertFalse((self.f.workspace / "child.lock").exists())
        self.assertEqual(self.decision("action", "B-work")["status"], "blocked")


def tearDownModule():
    """Optional evidence inventory, not a product receipt or pass indicator."""
    destination = os.environ.get("C1_VERIFICATION_IMPORT_MANIFEST")
    if destination:
        files = {}
        for name, module in tuple(sys.modules.items()):
            filename = getattr(module, "__file__", None)
            if filename and Path(filename).is_file():
                path = Path(filename).resolve()
                files[name] = {"path": str(path),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        Path(destination).write_text(json.dumps(files, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
