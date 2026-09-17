from copy import deepcopy
import hashlib
import os
import sys
import unittest
from unittest.mock import patch

from workflow_fixtures import WorkflowFixture, producer, scope
from evidence import write_json_atomic
from workflow_state import (
    ResolvedInputs, ResolvedLedger, SequenceConflict, append_event, bind_inputs,
    dependency_closure, read_json, safe_path, target, resolve_receipts,
    validate_contract, validate_event, validate_ledger, validate_receipt,
)


class WorkflowStateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = WorkflowFixture()
        self.addCleanup(self.fixture.close)
        self.root = self.fixture.root

    def test_load_and_bind_use_named_unserialized_views(self):
        contract, design, ledger = self.fixture.load()
        self.assertIsInstance(ledger, ResolvedLedger)
        self.assertEqual(ledger.receipts, {})
        self.assertEqual(design["revision"], "r1")
        inputs = bind_inputs(self.root, contract, target("action", "A-work"))
        self.assertIsInstance(inputs, ResolvedInputs)
        self.assertEqual(set(inputs.targets), {"action:A-work"})
        self.assertEqual(inputs.target["source"]["files"]["src/A.py"]["sha256"],
                         hashlib.sha256(b"VALUE = 1\n").hexdigest())
        self.assertEqual(set(inputs.target), {"source", "contract"})
        self.assertEqual(set(read_json(self.fixture.workspace / "evidence/ledger.json")),
                         {"schema_version", "slug", "events"})
        self.assertNotIn("workflow", sys.modules["evidence"].__dict__)

    def test_reject_duplicate_keys_nonfinite_and_unknown_record_keys(self):
        path = self.root / "bad.json"
        for text in ('{"id":1,"id":2}', '{"a":{"k":1,"k":2}}', '{"v":NaN}', '{"v":Infinity}', '{"v":1e9999}'):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_json(path)
        for field in ("due_checks", "reverse", "receipts", "unknown"):
            value = deepcopy(self.fixture.contract)
            value[field] = []
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_contract(value)

    def test_strict_types_ids_and_normalized_paths(self):
        mutations = [
            lambda c: c.update(schema_version=True),
            lambda c: c.update(schema_version=2),
            lambda c: c.update(slug="../escape"),
            lambda c: c["actions"]["A-work"]["command"].update(idle_seconds=True),
            lambda c: c["actions"]["A-work"]["command"].update(max_seconds=float("inf")),
            lambda c: c["actions"]["A-work"]["command"].update(max_seconds=0),
            lambda c: c["actions"]["A-work"].update(id="wrong"),
            lambda c: c["actions"]["A-work"].update(inputs=scope("../outside")),
            lambda c: c["actions"]["A-work"].update(inputs=scope("src/A.py", "src\\A.py")),
            lambda c: c["actions"]["A-work"]["owner"].update(role="wizard"),
            lambda c: c["checks"]["A-test"].update(context_rule="ignore"),
            lambda c: c["checks"]["A-test"].update(action_id="absent"),
            lambda c: c["checks"]["A-review"].update(context_rule="same-allowed"),
            lambda c: c["checks"]["A-test"].update(handoff_steps=["Unexpected handoff"]),
        ]
        for mutation in mutations:
            c = deepcopy(self.fixture.contract)
            mutation(c)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_contract(c)

    def test_graph_rejects_cycles_unknown_edges_and_duplicate_check_actions(self):
        mutations = [
            lambda c: c["actions"]["A-work"]["requires"].append(target("check", "A-test")),
            lambda c: c["actions"]["A-work"]["requires"].append(target("action", "missing")),
            lambda c: c["actions"]["A-work"]["requires"].append(target("increment", "B")),
            lambda c: c["increments"]["A"]["requires"].append(target("action", "B-work")),
            lambda c: c["checks"]["A-test"].update(action_id="B-test-run"),
            lambda c: c["increments"]["A"]["requires"].append(target("increment", "A")),
        ]
        for mutation in mutations:
            c = deepcopy(self.fixture.contract)
            mutation(c)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_contract(c)

    def test_closure_requires_metrics_review_verification_and_scenarios(self):
        for kind in ("metrics", "review", "verification"):
            c = deepcopy(self.fixture.contract)
            c["increments"]["A"]["requires"] = [
                ref for ref in c["increments"]["A"]["requires"] if c["checks"][ref["id"]]["kind"] != kind]
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "mandatory closure"):
                validate_contract(c)
        c = deepcopy(self.fixture.contract)
        c["increments"]["A"]["acs"].append("AC-unproven")
        with self.assertRaisesRegex(ValueError, "scenario"):
            validate_contract(c)

    def test_action_inherits_only_prerequisite_increment_closure(self):
        c = self.fixture.contract
        before = dependency_closure(c, target("action", "A-review-run"))
        self.assertEqual(set(before), {"action:A-work", "action:A-review-run"})
        c["increments"]["A"]["requires"].append(target("increment", "B"))
        validate_contract(c)
        after = dependency_closure(c, target("action", "A-review-run"))
        self.assertIn("increment:B", after)
        self.assertIn("check:B-metrics", after)
        self.assertNotIn("check:A-metrics", after)

    def test_before_action_exactly_one_consumer_and_retirement_requirement(self):
        c = deepcopy(self.fixture.contract)
        c["checks"]["A-test"]["validity"] = "before-action"
        with self.assertRaisesRegex(ValueError, "exactly one consumer"):
            validate_contract(c)
        c = deepcopy(self.fixture.contract)
        c["actions"]["A-work"].update(kind="retire", retirement={
            "legacy_scope": scope("src/legacy.py"), "expected_legacy_presence": ["src/legacy.py"]})
        with self.assertRaisesRegex(ValueError, "earlier compatibility"):
            validate_contract(c)

    def test_history_retained_and_component_binding_selective(self):
        before = self.fixture.inputs(target("action", "B-work")).target
        old_bytes = (self.fixture.workspace / "contracts/r1.json").read_bytes()
        self.fixture.components["a"]["signature"] = "a(value: int) -> int"
        self.fixture.adopt()
        c, design, ledger = self.fixture.load()
        self.assertEqual(design["supersedes"], "r1")
        self.assertEqual(design["history"][0]["revision"], "r1")
        self.assertEqual(old_bytes, (self.fixture.workspace / "contracts/r1.json").read_bytes())
        after = self.fixture.inputs(target("action", "B-work")).target
        self.assertEqual(before["contract"]["components"], after["contract"]["components"])
        self.assertNotEqual(before["contract"]["adopted_contract_sha256"], after["contract"]["adopted_contract_sha256"])
        self.assertEqual(len(ledger.document["events"]), 2)

    def test_reject_history_hash_review_and_adoption_mismatch(self):
        original = deepcopy(self.fixture.design)
        mutations = [
            lambda d: d["document"].update(sha256="0" * 64),
            lambda d: d.update(supersedes="not-retained"),
            lambda d: d["review"].update(verdict="REJECT"),
            lambda d: d["review"].update(producer=producer("reviewer", "implementer")),
            lambda d: d["review"].update(unattended_authorization=None),
            lambda d: d["review"]["candidate_hashes"].update(workflow_contract="0" * 64),
            lambda d: d["contract"].update(path="../outside"),
        ]
        for mutation in mutations:
            d = deepcopy(original)
            mutation(d)
            write_json_atomic(self.fixture.workspace / "current-design.json", d)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.fixture.load()
        write_json_atomic(self.fixture.workspace / "current-design.json", original)
        ledger = read_json(self.fixture.workspace / "evidence/ledger.json")
        ledger["events"][0]["inputs"]["contract"]["adopted_contract_sha256"] = "0" * 64
        write_json_atomic(self.fixture.workspace / "evidence/ledger.json", ledger)
        with self.assertRaisesRegex(ValueError, "adopted contract mismatch"):
            self.fixture.load()

    def test_paths_and_directory_links_are_rejected_before_reads(self):
        for name in ("../bad", "/bad", "C:\\bad", "C:bad", "a//b", "a/./b", "a/../b", "a:stream"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_path(self.root, name)
        outside = self.root / "outside"
        outside.mkdir()
        link = self.root / "linked"
        if os.name == "nt":
            from run import run_capture
            code, out, err = run_capture(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                 "New-Item -ItemType Junction -Path '%s' -Target '%s' | Out-Null" % (link, outside)],
                idle=30, max_total=90)
            self.assertEqual(code, 0, (out, err))
        else:
            link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Linked"):
            safe_path(self.root, "linked/file.txt")

    def test_append_assigns_sequence_atomically_and_rejects_stale_writer(self):
        item = target("action", "A-work")
        value = self.fixture.event("admitted", item, "test-run", self.fixture.inputs(item).target)
        path = self.fixture.workspace / "evidence/ledger.json"
        before = path.read_bytes()
        with self.assertRaises(SequenceConflict):
            append_event(self.fixture.workspace, value, 0)
        self.assertEqual(path.read_bytes(), before)
        with patch("evidence.os.replace", side_effect=OSError("fixture write error")):
            with self.assertRaises(OSError):
                self.fixture.append(value)
        self.assertEqual(path.read_bytes(), before)
        persisted = self.fixture.append(value)
        self.assertEqual(persisted["seq"], 2)
        self.assertNotIn("seq", value)
        self.assertEqual(read_json(path)["events"][-1], persisted)
        with self.assertRaises(ValueError):
            append_event(self.fixture.workspace, persisted, 2)
        with self.assertRaises(ValueError):
            append_event(self.fixture.workspace, value, True)

    def test_duplicate_admission_invalid_seq_and_unadmitted_event(self):
        original = read_json(self.fixture.workspace / "evidence/ledger.json")
        event = self.fixture.event("completed", target("action", "A-work"), "not-admitted",
                                   self.fixture.inputs(target("action", "A-work")).target)
        with self.assertRaisesRegex(ValueError, "prior admission"):
            validate_ledger(dict(original, events=original["events"] + [dict(event, seq=2)]))
        event.update(kind="admitted")
        ledger = dict(original, events=original["events"] + [dict(event, seq=2), dict(event, seq=3)])
        with self.assertRaisesRegex(ValueError, "Duplicate admission"):
            validate_ledger(ledger)
        for seq in (True, 0, 8):
            with self.subTest(seq=seq), self.assertRaises(ValueError):
                validate_ledger(dict(original, events=[dict(original["events"][0], seq=seq)]))

    def test_receipt_and_artifact_bytes_resolved_and_tampering_blocks(self):
        self.fixture.work("A-work")
        ref = self.fixture.receipt("A-test")
        _, _, ledger = self.fixture.load()
        observation = ledger.receipts[ref["id"]]
        self.assertEqual(observation.status, "valid")
        self.assertEqual(observation.observed_sha256, ref["sha256"])
        self.assertTrue(all(a["exists"] for a in observation.artifacts.values()))
        receipt_path = self.fixture.workspace / ("evidence/receipts/%s.json" % ref["id"])
        original = receipt_path.read_bytes()
        receipt_path.write_bytes(original + b"\n")
        self.assertEqual(self.fixture.load()[2].receipts[ref["id"]].status, "stale")
        receipt_path.write_bytes(original)
        artifact = observation.document["artifacts"][0]
        (self.root / artifact["path"]).write_text("tampered")
        bad = self.fixture.load()[2].receipts[ref["id"]]
        self.assertEqual(bad.status, "stale")
        self.assertIn("artifact", bad.reason)
        self.assertFalse(all(a["expected_sha256"] == a["observed_sha256"] for a in bad.artifacts.values()))
        receipt_path.unlink()
        self.assertEqual(self.fixture.load()[2].receipts[ref["id"]].status, "missing")

    def test_malformed_receipt_is_observation_not_top_level_input_success(self):
        self.fixture.work("A-work")
        ref = self.fixture.receipt("A-test")
        path = self.fixture.workspace / ("evidence/receipts/%s.json" % ref["id"])
        path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        observation = self.fixture.load()[2].receipts[ref["id"]]
        self.assertNotEqual(observation.status, "valid")
        self.assertIsNone(observation.document)
        self.assertIn("Duplicate JSON key", observation.reason)

    def test_receipt_result_types_and_binding_hashes_are_strict(self):
        self.fixture.work("A-work")
        ref = self.fixture.receipt("A-test")
        receipt = self.fixture.load()[2].receipts[ref["id"]].document
        mutations = [
            lambda r: r.update(schema_version=True),
            lambda r: r["result"].update(leaf_count=True),
            lambda r: r["result"].update(complete=1),
            lambda r: r["result"]["tests"][0].update(line=True),
            lambda r: r["artifacts"][0].update(bytes=True),
            lambda r: r["inputs"]["source"].update(scope_sha256="F" * 64),
            lambda r: r["inputs"]["source"]["files"]["src/A.py"].update(sha256="0" * 64),
            lambda r: r["inputs"].update(receipts={}),
            lambda r: r.update(finished_at="not-a-time"),
        ]
        for mutation in mutations:
            value = deepcopy(receipt)
            mutation(value)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_receipt(value)

    def test_different_target_scopes_membership_missing_and_outputs(self):
        a = self.fixture.contract["actions"]["A-work"]
        a["inputs"] = {"files": ["missing.txt"], "directories": ["src"],
                       "excluded_outputs": [{"path": ".ai/demo/evidence/ledger.json", "reason": "Exact generated ledger"}]}
        self.fixture.adopt()
        first = self.fixture.inputs(target("increment", "A"))
        self.assertNotEqual(first.targets["action:A-work"]["source"]["scope_sha256"],
                            first.targets["check:A-test"]["source"]["scope_sha256"])
        self.assertEqual(first.targets["action:A-work"]["source"]["files"]["missing.txt"]["mode"], "missing")
        self.fixture.write("src/new.py", "NEW = True\n")
        second = self.fixture.inputs(target("increment", "A"))
        self.assertNotEqual(first.targets["action:A-work"]["source"]["scope_sha256"],
                            second.targets["action:A-work"]["source"]["scope_sha256"])
        a["inputs"]["excluded_outputs"] = [{"path": ".ai/demo/evidence", "reason": "Too broad"}]
        self.fixture.adopt()
        with self.assertRaisesRegex(ValueError, "exact owned"):
            self.fixture.inputs(target("action", "A-work"))

    def test_append_refuses_receipt_blob_not_yet_written(self):
        run_id, snapshot = self.fixture.start("A-test-run")
        event = self.fixture.event("receipt-accepted", target("check", "A-test"), run_id, snapshot,
                                   refs=[{"id": "absent", "sha256": "0" * 64}], outcome="pass")
        before = (self.fixture.workspace / "evidence/ledger.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            self.fixture.append(event)
        self.assertEqual(before, (self.fixture.workspace / "evidence/ledger.json").read_bytes())

    def test_cyclic_receipt_links_and_duplicate_reference_ids_are_rejected(self):
        self.fixture.work("A-work")
        first = self.fixture.receipt("A-test")
        second = self.fixture.receipt("A-review")
        paths = [self.fixture.workspace / ("evidence/receipts/%s.json" % r["id"]) for r in (first, second)]
        documents = [read_json(p) for p in paths]
        for document, path, ref in zip(documents, paths, (second, first)):
            document["prerequisite_receipts"] = [ref]
            write_json_atomic(path, document)
        observations = resolve_receipts(self.root, "demo", {"events": []}, [first["id"]])
        self.assertEqual(observations[first["id"]].status, "invalid")
        self.assertTrue(any("Cyclic" in o.reason for o in observations.values()))
        value = documents[0]
        value["prerequisite_receipts"] = [first, dict(first, sha256="0" * 64)]
        with self.assertRaisesRegex(ValueError, "Duplicate receipt"):
            validate_receipt(value)

    def test_missing_recursive_receipt_and_tampered_chain_never_resolve_valid(self):
        self.fixture.work("A-work")
        ref = self.fixture.receipt("A-test")
        path = self.fixture.workspace / ("evidence/receipts/%s.json" % ref["id"])
        document = read_json(path)
        document["prerequisite_receipts"] = [{"id": "absent-parent", "sha256": "0" * 64}]
        write_json_atomic(path, document)
        observations = self.fixture.load()[2].receipts
        self.assertEqual(observations["absent-parent"].status, "missing")
        self.assertEqual(observations[ref["id"]].status, "invalid")

    def test_lifecycle_requires_intent_observed_identity_and_current_adoption(self):
        run, snapshot = self.fixture.start("A-work")
        ledger = read_json(self.fixture.workspace / "evidence/ledger.json")
        for mutation in (
            lambda v: v["events"][1]["inputs"]["contract"].update(adopted_contract_sha256="0" * 64),
            lambda v: v["events"][-1]["process"].update(returncode=0),
            lambda v: v["events"][-1].update(spawned="unknown"),
            lambda v: v["events"][-1].update(target=target("action", "B-work")),
        ):
            value = deepcopy(ledger)
            mutation(value)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_ledger(value)
        self.fixture.finish("A-work", run)
        ledger = read_json(self.fixture.workspace / "evidence/ledger.json")
        ledger["events"][-2]["process"]["pid"] = 9999
        with self.assertRaisesRegex(ValueError, "identity changed"):
            validate_ledger(ledger)

    def test_previous_increment_review_does_not_replace_current_mandatory_proof(self):
        c = deepcopy(self.fixture.contract)
        c["increments"]["A"]["requires"] = [
            target("check", "B-review") if ref == target("check", "A-review") else ref
            for ref in c["increments"]["A"]["requires"]]
        with self.assertRaisesRegex(ValueError, "mandatory closure"):
            validate_contract(c)

    def test_timestamp_validation_checks_parsed_utc_awareness(self):
        event = deepcopy(self.fixture.load()[2].document["events"][0])
        for stamp in ("2026-09-17T00:00:00Z", "2026-09-17T00:00:00+00:00",
                      "2026-09-17T00:00:00.123456+00:00"):
            with self.subTest(valid=stamp):
                validate_event(dict(event, time=stamp))
        for stamp in ("2026-09-17+00:00", "20260917+00:00", "2026-09-17Z",
                      "2026-09-17T00:00:00", "2026-09-17T00:00:00+01:00"):
            with self.subTest(invalid=stamp), self.assertRaises(ValueError):
                validate_event(dict(event, time=stamp))

    def test_receipt_and_metric_dates_reject_naive_values_before_comparison(self):
        self.fixture.work("A-work")
        ref = self.fixture.receipt("A-metrics")
        receipt = self.fixture.load()[2].receipts[ref["id"]].document
        for field in ("started_at", "finished_at"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_receipt(dict(receipt, **{field: "2026-09-17+00:00"}))
        value = deepcopy(receipt)
        value["result"]["generated"] = "2026-09-17+00:00"
        with self.assertRaises(ValueError):
            validate_receipt(value)


if __name__ == "__main__":
    unittest.main()
