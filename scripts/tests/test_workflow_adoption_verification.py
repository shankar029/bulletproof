"""Independent retained-basis seam proof; protocol identities are synthetic."""

from copy import deepcopy
import hashlib
import unittest

from workflow_fixtures import WorkflowFixture
from workflow_gate import evaluate
from workflow_state import (
    ResolvedLedger, bind_inputs, load_workspace, read_json, resolve_receipts,
    target, validate_design_binding,
)


class RetainedAdoptionVerificationTests(unittest.TestCase):
    def test_retained_old_basis_blocks_unresolved_run_in_both_partial_publications(self):
        fixture = WorkflowFixture()
        self.addCleanup(fixture.close)
        root, workspace = fixture.root, fixture.workspace
        action = target("action", "A-work")
        fixture.append(fixture.event(
            "admitted", action, "independent-synthetic-pending",
            fixture.inputs(action).target, spawned="unknown"))
        old_contract, old_design, old_resolved = fixture.load()
        old_prefix = deepcopy(old_resolved.document)
        # Retain the actual old authority bytes exclusively, rather than
        # inventing an alternate permissive workspace or a repaired ledger.
        retained = {}
        for name in ("workflow", "current-design"):
            content = (workspace / (name + ".json")).read_bytes()
            path = workspace / ("design-history/r1." + name + ".json")
            with path.open("xb") as stream:
                stream.write(content)
            retained[name] = path
        immutable_before = {p: p.read_bytes() for p in retained.values()}
        fixture.components["a"]["signature"] = "a(value: int) -> int"
        fixture.adopt()
        candidate_contract, candidate_design, candidate_resolved = fixture.load()
        candidate_workflow = (workspace / "workflow.json").read_bytes()
        actual_ledger = (workspace / "evidence/ledger.json").read_bytes()
        self.assertEqual(candidate_resolved.document["events"][:-1], old_prefix["events"])
        self.assertEqual(candidate_resolved.document["events"][-1]["kind"], "adopted")
        ship = target("ship", "ship")

        for phase in ("A1", "A2"):
            with self.subTest(phase=phase):
                (workspace / "workflow.json").write_bytes(
                    immutable_before[retained["workflow"]] if phase == "A1" else candidate_workflow)
                (workspace / "current-design.json").write_bytes(
                    immutable_before[retained["current-design"]])
                before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in root.rglob("*") if p.is_file()}
                with self.assertRaises(ValueError):
                    load_workspace(root, "demo")
                live_contract = read_json(workspace / "workflow.json")
                with self.assertRaises(ValueError):
                    bind_inputs(root, live_contract, ship)
                basis_contract = read_json(retained["workflow"])
                basis_design = read_json(retained["current-design"])
                self.assertEqual(basis_contract, old_contract)
                self.assertEqual(basis_design, old_design)
                # Exact persisted prefix before the final adopted event, not
                # a filtered dispatch ledger or removed pending admission.
                disk_ledger = read_json(workspace / "evidence/ledger.json")
                basis_ledger = dict(disk_ledger, events=disk_ledger["events"][:-1])
                self.assertEqual(basis_ledger, old_prefix)
                explicit = bind_inputs(root, basis_contract, ship,
                                       design=basis_design, ledger=basis_ledger)
                receipts = resolve_receipts(root, "demo", basis_ledger)
                readiness = evaluate(basis_contract, ResolvedLedger(basis_ledger, receipts),
                                     explicit, ship)
                self.assertEqual(readiness["status"], "blocked")
                self.assertIn("RECOVERY_UNVERIFIED", {b["code"] for b in readiness["blockers"]})
                self.assertIsNone(readiness["next_command"])
                self.assertEqual(validate_design_binding(
                    root, candidate_contract, candidate_design, disk_ledger), candidate_design)
                self.assertEqual((workspace / "evidence/ledger.json").read_bytes(), actual_ledger)
                self.assertEqual({p: p.read_bytes() for p in retained.values()}, immutable_before)
                self.assertEqual(
                    {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob("*") if p.is_file()}, before)


if __name__ == "__main__":
    unittest.main()
