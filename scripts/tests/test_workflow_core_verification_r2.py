"""Independent F1 correction boundary; synthetic receipts are protocol data only.

The original verification tests and evidence remain untouched. This regression
checks exact receipt chronology, not just the presence of some valid proof in
the ledger prefix. All persistence and gate calls use the actual C1 library.
"""

import json
import unittest

from workflow_fixtures import WorkflowFixture
from evidence import write_json_atomic
from workflow_gate import evaluate
from workflow_state import read_json, target


class ClosureReferenceChronologyTests(unittest.TestCase):
    def setUp(self):
        self.fixture = WorkflowFixture()
        self.addCleanup(self.fixture.close)

    def decision(self, kind, name):
        contract, _, ledger = self.fixture.load()
        node = target(kind, name)
        return evaluate(contract, ledger, self.fixture.inputs(node), node)

    def test_closure_exact_receipt_refs_must_be_accepted_in_its_prefix(self):
        f = self.fixture
        f.contract["increments"]["B"]["requires"].append(target("increment", "A"))
        f.adopt()
        old_refs = f.complete_increment("A")
        self.assertEqual(self.decision("increment", "A")["status"], "complete")
        self.assertEqual(self.decision("action", "B-work")["status"], "ready")
        old_blobs = {ref["id"]: (f.workspace / (
            "evidence/receipts/%s.json" % ref["id"])).read_bytes() for ref in old_refs}

        replacement = f.receipt("A-test")
        # A new accepted check changes the chain: proper reclosure is needed.
        self.assertEqual(self.decision("increment", "A")["status"], "ready")
        self.assertEqual(self.decision("action", "B-work")["status"], "blocked")
        path = f.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        closure = next(event for event in ledger["events"]
                       if event["kind"] == "closed" and event["target"] == target("increment", "A"))
        accepted = next(event for event in ledger["events"]
                        if event["kind"] == "receipt-accepted" and replacement in event["receipt_refs"])
        self.assertLess(closure["seq"], accepted["seq"])
        self.assertNotEqual(old_refs[0]["id"], replacement["id"])
        # Malformed persisted history: only substitute the exact new ref, without
        # moving/reclosing the old event. Some earlier proof is not THIS proof.
        closure["receipt_refs"] = [
            replacement if ref == old_refs[0] else ref for ref in closure["receipt_refs"]]
        write_json_atomic(path, ledger)
        for ref_id, content in old_blobs.items():
            self.assertEqual((f.workspace / (
                "evidence/receipts/%s.json" % ref_id)).read_bytes(), content)
        try:
            own = self.decision("increment", "A")
            dependent = self.decision("action", "B-work")
        except ValueError:
            return  # Strict rejection of contradictory persisted proof is valid.
        diagnostic = json.dumps({
            "closure_seq": closure["seq"], "replacement_acceptance_seq": accepted["seq"],
            "old_ref": old_refs[0], "replacement_ref": replacement,
            "increment_status": own["status"], "dependent_status": dependent["status"],
        }, sort_keys=True)
        self.assertNotEqual(own["status"], "complete", diagnostic)
        self.assertEqual(dependent["status"], "blocked", diagnostic)
        self.assertIsNone(dependent["next_command"], diagnostic)


if __name__ == "__main__":
    unittest.main()
