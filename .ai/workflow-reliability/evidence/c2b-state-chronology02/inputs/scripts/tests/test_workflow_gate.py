from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from workflow_fixtures import WorkflowFixture, producer, scope
from evidence import write_json_atomic
import workflow_gate
from workflow_gate import evaluate
from workflow_state import canonical_hash, read_json, target


class WorkflowGateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = WorkflowFixture()
        self.addCleanup(self.fixture.close)

    def evaluate(self, kind="action", name="A-work"):
        contract, _, ledger = self.fixture.load()
        node = target(kind, name)
        return evaluate(contract, ledger, self.fixture.inputs(node), node)

    def test_admission_ready_without_closure_checks_and_execution_is_not_closure(self):
        result = self.evaluate()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["due"], [])
        self.assertIn("A-review", result["future"])
        self.assertEqual(result["next_command"][-2:], ["--action", "A-work"])
        self.fixture.work("A-work")
        self.assertEqual(self.evaluate()["status"], "complete")
        closure = self.evaluate("increment", "A")
        self.assertEqual(closure["status"], "blocked")
        self.assertIsNone(closure["next_command"])
        self.assertEqual({d["check_id"] for d in closure["due"]},
                         {"A-test", "A-verify", "A-review", "A-metrics"})
        self.assertTrue(all(d["outcome"] == "missing" for d in closure["due"]))

    def test_check_admission_not_gated_by_own_closure_or_result(self):
        self.assertEqual(self.evaluate("check", "A-review")["status"], "blocked")
        self.fixture.work("A-work")
        result = self.evaluate("check", "A-review")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["next_command"][-1], "A-review-run")
        self.assertEqual(result["due"], [])
        self.fixture.receipt("A-review")
        self.assertEqual(self.evaluate("check", "A-review")["status"], "complete")

    def test_all_checks_ready_for_closure_then_closed_and_ship_union(self):
        refs = self.fixture.complete_increment("A")
        result = self.evaluate("increment", "A")
        self.assertEqual(result["status"], "complete")
        self.assertEqual({r["id"] for d in result["due"] for r in d["receipt_refs"]},
                         {r["id"] for r in refs})
        self.assertTrue(all(d["outcome"] == "valid" for d in result["due"]))
        self.assertEqual(self.evaluate("ship", "ship")["status"], "blocked")
        self.fixture.complete_increment("B")
        self.assertEqual(self.evaluate("ship", "ship")["status"], "ready")

    def test_pure_gate_runs_after_materialization_without_any_file_reads(self):
        self.fixture.complete_increment("A")
        node = target("increment", "A")
        contract, _, ledger = self.fixture.load()
        inputs = self.fixture.inputs(node)
        saved = deepcopy((contract, ledger, inputs))
        with patch("builtins.open", side_effect=AssertionError("Gate performed I/O")), \
                patch.object(Path, "read_bytes", side_effect=AssertionError("Gate read bytes")), \
                patch.object(Path, "read_text", side_effect=AssertionError("Gate read text")):
            result = evaluate(contract, ledger, inputs, node)
        self.assertEqual(result["status"], "complete")
        self.assertEqual((contract, ledger, inputs), saved)

    def test_same_implementer_context_cannot_review_or_verify(self):
        for name in ("A-review", "A-verify"):
            self.fixture.contract["actions"][name + "-run"]["owner"]["context_id"] = "implementer"
        self.fixture.adopt()
        self.fixture.complete_increment("A")
        result = self.evaluate("increment", "A")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual({d["check_id"] for d in result["due"] if d["outcome"] == "blocked"},
                         {"A-review", "A-verify"})

    def test_verifier_reviewer_must_differ_even_on_same_actor_account(self):
        self.fixture.contract["actions"]["A-review-run"]["owner"]["context_id"] = "verifier"
        self.fixture.adopt()
        self.fixture.complete_increment("A")
        self.assertEqual(self.evaluate("increment", "A")["status"], "blocked")

    def test_recorder_cannot_replace_producer(self):
        self.fixture.work("A-work")
        self.fixture.receipt("A-review", mutate=lambda r: r.update(producer=producer(), recorded_by=producer("reviewer")))
        result = self.evaluate("increment", "A")
        review = next(d for d in result["due"] if d["check_id"] == "A-review")
        self.assertEqual(review["outcome"], "blocked")

    def test_missing_or_tampered_receipt_blocks_even_with_pass_event(self):
        refs = self.fixture.complete_increment("A")
        path = self.fixture.workspace / ("evidence/receipts/%s.json" % refs[0]["id"])
        path.unlink()
        result = self.evaluate("increment", "A")
        self.assertEqual(result["status"], "blocked")
        self.assertNotEqual(next(d for d in result["due"] if d["check_id"] == "A-test")["outcome"], "valid")
        self.assertIsNone(result["next_command"])

    def test_stale_source_reopens_only_affected_branch_receipt_bytes_preserved(self):
        a_refs = self.fixture.complete_increment("A")
        b_refs = self.fixture.complete_increment("B")
        b_paths = [self.fixture.workspace / ("evidence/receipts/%s.json" % r["id"]) for r in b_refs]
        before = [p.read_bytes() for p in b_paths]
        self.fixture.write("src/A.py", "VALUE = 2\n")
        a = self.evaluate("increment", "A")
        b = self.evaluate("increment", "B")
        self.assertEqual(a["status"], "blocked")
        self.assertTrue(a["reopened"])
        invalidated = {name for record in a["reopened"] for name in record["invalidated_receipts"]}
        self.assertTrue({ref["id"] for ref in a_refs} <= invalidated)
        self.assertEqual(b["status"], "complete")
        self.assertEqual([p.read_bytes() for p in b_paths], before)
        self.assertTrue(all(d["outcome"] == "valid" for d in b["due"]))

    def test_changed_component_preserves_unrelated_proof_after_adoption(self):
        self.fixture.complete_increment("A")
        self.fixture.complete_increment("B")
        self.fixture.components["a"]["signature"] = "a(x: str) -> bool"
        self.fixture.adopt()
        self.assertEqual(self.evaluate("increment", "A")["status"], "blocked")
        self.assertEqual(self.evaluate("increment", "B")["status"], "complete")

    def test_changed_check_reopens_its_consumers_not_other_checks(self):
        self.fixture.complete_increment("A")
        self.fixture.contract["checks"]["A-test"]["pass_condition"] = "Additional fixture requirement"
        self.fixture.adopt()
        result = self.evaluate("increment", "A")
        states = {d["check_id"]: d["outcome"] for d in result["due"]}
        self.assertEqual(states["A-test"], "stale")
        self.assertEqual(states["A-review"], "valid")
        self.assertEqual(result["status"], "blocked")

    def test_replacing_prerequisite_receipt_invalidates_old_dependent_chain(self):
        self.fixture.contract["actions"]["A-review-run"]["requires"].append(target("check", "A-test"))
        self.fixture.adopt()
        self.fixture.work("A-work")
        old = self.fixture.receipt("A-test")
        self.fixture.receipt("A-review", refs=[old])
        self.assertEqual(self.evaluate("check", "A-review")["status"], "complete")
        new = self.fixture.receipt("A-test")
        result = self.evaluate("increment", "A")
        self.assertNotEqual(old["id"], new["id"])
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-review")["outcome"], "stale")

    def test_inherited_increment_dependency_requires_closure_not_just_its_tests(self):
        self.fixture.contract["increments"]["A"]["requires"].append(target("increment", "B"))
        self.fixture.adopt()
        self.assertEqual(self.evaluate()["status"], "blocked")
        self.fixture.complete_increment("B")
        self.assertEqual(self.evaluate()["status"], "ready")
        self.fixture.write("src/B.py", "VALUE = 2\n")
        self.assertEqual(self.evaluate()["status"], "blocked")

    def test_metrics_unavailable_or_omitted_never_passes(self):
        self.fixture.work("A-work")
        def incomplete(receipt):
            result = receipt["result"]
            result.update(completeness="incomplete", verdict="fail", unavailable=["diff_coverage_pct"])
        self.fixture.receipt("A-metrics", mutate=incomplete)
        result = self.evaluate("increment", "A")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-metrics")["outcome"], "fail")
        def omit(receipt):
            policy = receipt["result"]["policy"]
            policy["required"].remove("diff_coverage_pct")
            policy["sha256"] = canonical_hash({k: policy[k] for k in ("required", "rules")})
        self.fixture.receipt("A-metrics", mutate=omit)
        result = self.evaluate("increment", "A")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-metrics")["outcome"], "fail")

    def test_metrics_run_source_floor_and_measurement_consistency(self):
        mutations = [
            lambda r: r["result"].update(run_id="old-run"),
            lambda r: r["result"]["metrics"]["mutation_score_pct"].update(head=59),
            lambda r: r["result"]["metrics"]["cycles"].update(head=1),
            lambda r: r["result"]["metrics"]["diff_coverage_pct"].update(command=None),
            lambda r: r["result"]["metrics"]["complexity_max"]["scope_support"].update(unsupported_paths=["python"]),
        ]
        self.fixture.work("A-work")
        for mutation in mutations:
            self.fixture.receipt("A-metrics", mutate=mutation)
            result = self.evaluate("increment", "A")
            with self.subTest(mutation=mutation):
                self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-metrics")["outcome"], "fail")

    def test_finding_limitation_does_not_waive_scenarios_blockers_or_human(self):
        self.fixture.work("A-work")
        def missing(receipt):
            receipt["result"].update(verdict="VERIFIED-WITH-LIMITATIONS", scenarios={})
        self.fixture.receipt("A-review", mutate=missing)
        result = self.evaluate("increment", "A")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-review")["outcome"], "fail")
        def blocking(receipt):
            receipt["result"]["findings"] = [{
                "id": "F1", "location": "fixture", "observation": "required proof missing",
                "blocking": True, "evidence_refs": []}]
        self.fixture.receipt("A-review", mutate=blocking)
        result = self.evaluate("increment", "A")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-review")["outcome"], "fail")

    def temporal_fixture(self, *, red=False):
        f = self.fixture
        f.write("src/legacy.py", "OLD = True\n")
        f.add_check("A-before", "A", "behavioral-red" if red else "compatibility",
                    inputs=scope("src/legacy.py", "src/A.py"), validity="before-action")
        f.contract["actions"]["A-work"]["requires"] = [target("check", "A-before")]
        if red:
            assertion_file = f.write("fixture.test.mjs", "assert.equal(1, 2);\n")
            f.contract["actions"]["A-before-run"]["inputs"]["files"].append("fixture.test.mjs")
            f.contract["checks"]["A-before"]["assertions"] = [{
                "id": "red", "test_file": "fixture.test.mjs", "test_name": "fixture property",
                "source_sha256": hashlib.sha256(assertion_file.read_bytes()).hexdigest(),
                "assertion_lines": [1], "purpose": "Fixture regression",
                "expected_red": {"operator": "strictEqual", "expected_relation": "2", "actual_relation": "1"}}]
        else:
            f.contract["actions"]["A-work"].update(kind="retire", retirement={
                "legacy_scope": scope("src/legacy.py"), "expected_legacy_presence": ["src/legacy.py"]})
        f.contract["increments"]["A"]["requires"].append(target("check", "A-before"))
        f.adopt()

    def test_earlier_consumed_compatibility_survives_retirement_then_current_checks_close(self):
        self.temporal_fixture()
        ref = self.fixture.receipt("A-before")
        self.assertEqual(self.evaluate()["status"], "ready")
        self.fixture.work("A-work", [ref], change=lambda: (self.fixture.root / "src/legacy.py").unlink())
        for suffix in ("test", "verify", "review", "metrics"):
            self.fixture.receipt("A-" + suffix, refs=[ref])
        result = self.evaluate("increment", "A")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-before")["outcome"], "valid")
        self.assertTrue(all(d["outcome"] == "valid" for d in result["due"]))

    def test_compatibility_after_legacy_disappears_cannot_admit_retirement(self):
        self.temporal_fixture()
        (self.fixture.root / "src/legacy.py").unlink()
        self.fixture.receipt("A-before")
        result = self.evaluate()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("LEGACY_ABSENT", {b["code"] for b in result["blockers"]})

    def test_backdated_timestamp_cannot_replace_receipt_acceptance_sequence(self):
        self.temporal_fixture()
        run_id, _ = self.fixture.start("A-work")
        ref = self.fixture.receipt("A-before")
        self.fixture.finish("A-work", run_id)
        # Rewrite the protocol as a malicious backfill fixture, not via append.
        path = self.fixture.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        for event in ledger["events"]:
            if event["kind"] == "admitted" and event["run_id"] == run_id:
                event["receipt_refs"] = [ref]
        write_json_atomic(path, ledger)
        result = self.evaluate("increment", "A")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-before")["outcome"], "blocked")

    def test_behavioral_red_requires_actual_matching_assertion_not_setup_or_logs(self):
        self.temporal_fixture(red=True)
        def red(receipt):
            result = receipt["result"]
            result["tests"][0].update(outcome="assertion-fail", error={
                "name": "AssertionError", "code": "ERR_TEST_FAILURE", "cause_code": "ERR_ASSERTION",
                "message": "Fixture expected failure", "assertion_stack": "at fixture.test.mjs:1:1",
                "operator": "strictEqual", "expected": "2", "actual": "1"})
        self.fixture.receipt("A-before", mutate=red, code=1)
        self.assertEqual(self.evaluate()["status"], "ready")
        def setup(receipt):
            receipt["result"]["tests"][0]["outcome"] = "setup-error"
            receipt["result"]["logs"] = [{"stream": "stdout", "text": "AssertionError ERR_ASSERTION"}]
        self.fixture.receipt("A-before", mutate=setup, code=1)
        self.assertEqual(self.evaluate()["status"], "blocked")
        def wrong(receipt):
            red(receipt)
            receipt["result"]["tests"][0]["error"]["actual"] = "wrong"
        self.fixture.receipt("A-before", mutate=wrong, code=1)
        self.assertEqual(self.evaluate()["status"], "blocked")

    def test_unresolved_launch_and_direct_exit_do_not_authorize_new_dispatch(self):
        run_id, _ = self.fixture.start("A-work")
        result = self.evaluate("action", "B-work")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("RECOVERY_UNVERIFIED", {b["code"] for b in result["blockers"]})
        item = target("action", "A-work")
        self.fixture.append(self.fixture.event("process-observed", item, run_id, self.fixture.inputs(item).target,
            process={"phase": "direct-exited", "pid": 1234, "process_group": None,
                     "start_identity": None, "identity_evidence": None, "returncode": 0,
                     "cleanup": "best-effort-attempted", "error": None}, spawned="yes"))
        self.assertEqual(self.evaluate("action", "B-work")["status"], "blocked")

    def test_external_handoff_is_awaiting_response_not_unknown_spawn(self):
        self.fixture.contract["actions"]["A-review-run"]["command"] = None
        self.fixture.contract["checks"]["A-review"]["handoff_steps"] = ["Return fixture review"]
        self.fixture.adopt()
        self.fixture.work("A-work")
        self.fixture.start("A-review-run")
        result = self.evaluate("action", "A-review-run")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("AWAITING_RESPONSE", {b["code"] for b in result["blockers"]})
        self.assertEqual(self.evaluate("check", "A-review")["status"], "blocked")
        self.assertEqual(self.evaluate("action", "B-work")["status"], "ready")

    def research_fixture(self, name="claim-one", supersedes=None):
        f = self.fixture
        section = "# %s\nA scoped fixture conclusion.\n" % name
        report_path = ".ai/demo/research-%s.md" % name
        f.write(report_path, section)
        check_id = "research-" + name
        f.add_check(check_id, "A", "research", "researcher", inputs=scope("src/A.py"))
        claim = {
            "claim_id": name, "report": report_path + "#" + name,
            "claim_sha256": hashlib.sha256(section.encode()).hexdigest(), "epistemic": "FACT",
            "scope": {"paths": ["src/A.py"], "queries": ["VALUE"], "filters": ["*.py"], "exclusions": []},
            "source_refs": [{"path": "src/A.py", "sha256": hashlib.sha256((f.root / "src/A.py").read_bytes()).hexdigest(),
                             "lines": [1], "snippet_ref": "VALUE = 1"}],
            "supersedes": supersedes or [], "correction_owner": producer("researcher"),
            "acceptance_owner": producer(), "accepted_receipt": "receipt-run-%d" % (f.serial + 1)}
        f.contract["claims"][name] = claim
        f.contract["actions"][check_id + "-run"]["claims"] = [name]
        f.contract["actions"]["A-work"]["claims"] = [name]
        f.contract["actions"]["A-work"]["requires"] = [target("check", check_id)]
        f.adopt()
        return check_id

    def test_research_requires_bound_attributed_acceptance_and_current_section(self):
        check = self.research_fixture()
        self.assertEqual(self.evaluate()["status"], "blocked")
        self.fixture.receipt(check)
        self.assertEqual(self.evaluate()["status"], "ready")
        self.fixture.write(".ai/demo/research-claim-one.md", "# claim-one\nChanged conclusion.\n")
        with self.assertRaisesRegex(ValueError, "claim section changed"):
            self.evaluate()

    def test_research_supersession_reopens_bound_consumers_preserves_unrelated(self):
        self.fixture.complete_increment("B")
        check = self.research_fixture()
        self.fixture.receipt(check)
        self.assertEqual(self.evaluate()["status"], "ready")
        replacement = self.research_fixture("claim-two", ["claim-one"])
        self.fixture.receipt(replacement)
        self.assertEqual(self.evaluate()["status"], "ready")
        self.assertIn("claim-one", self.fixture.contract["claims"])
        self.assertEqual(self.evaluate("increment", "B")["status"], "complete")
        self.fixture.contract["actions"]["A-work"]["claims"] = ["claim-one"]
        self.fixture.adopt()
        result = self.evaluate()
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("superseded" in b["reason"] for b in result["blockers"]))

    def test_research_unknown_and_wrong_acceptance_owner_block(self):
        check = self.research_fixture()
        self.fixture.receipt(check, mutate=lambda r: r.update(recorded_by=producer("human")))
        result = self.evaluate()
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("ownership mismatch" in b["reason"] for b in result["blockers"]))
        self.fixture.contract["claims"]["claim-one"]["epistemic"] = "UNKNOWN"
        self.fixture.adopt()
        self.assertEqual(self.evaluate()["status"], "blocked")

    def test_fresh_process_resumes_from_only_artifacts_and_retains_other_branch(self):
        from run import run_capture
        self.fixture.complete_increment("A")
        self.fixture.complete_increment("B")
        self.fixture.write("src/A.py", "VALUE = 7\n")
        scripts = str(Path(__file__).resolve().parents[1])
        code = (
            "import json,sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
            "from workflow_state import load_workspace,bind_inputs,target; "
            "from workflow_gate import evaluate; root=Path(sys.argv[2]); "
            "c,d,l=load_workspace(root,'demo'); "
            "print(json.dumps({n:evaluate(c,l,bind_inputs(root,c,target('increment',n)),"
            "target('increment',n))['status'] for n in ('A','B')}))"
        )
        rc, stdout, stderr = run_capture([sys.executable, "-B", "-c", code, scripts, str(self.fixture.root)],
                                         cwd=str(self.fixture.root), idle=30, max_total=90)
        self.assertEqual(rc, 0, stderr)
        self.assertEqual(json.loads(stdout), {"A": "blocked", "B": "complete"})

    def test_human_confirmation_and_completed_external_receipt(self):
        self.fixture.add_check("A-human", "A", "human", "human", inputs=scope("src/A.py"), handoff=True)
        self.fixture.contract["actions"]["A-work"]["requires"] = [target("check", "A-human")]
        self.fixture.adopt()
        self.fixture.receipt("A-human", mutate=lambda r: r["result"].update(human_confirmation="unconfirmed"))
        self.assertEqual(self.evaluate()["status"], "blocked")
        self.fixture.receipt("A-human")
        self.assertEqual(self.evaluate()["status"], "ready")

    def test_retirement_requires_post_change_proof_not_only_consumed_precheck(self):
        self.temporal_fixture()
        before = self.fixture.receipt("A-before")
        self.fixture.work("A-work", [before], change=lambda: self.fixture.write("src/A.py", "VALUE = 2\n"))
        result = self.evaluate("increment", "A")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-before")["outcome"], "valid")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-test")["outcome"], "missing")

    def test_recovered_event_alone_is_not_supported_termination_evidence(self):
        run, inputs = self.fixture.start("A-work")
        self.fixture.append(self.fixture.event("recovered", target("action", "A-work"), run, inputs,
                                               outcome="interrupted", spawned="unknown"))
        result = self.evaluate("action", "B-work")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("RECOVERY_UNVERIFIED", {b["code"] for b in result["blockers"]})

    def test_ordinary_action_cannot_backfill_current_prerequisite_chronology(self):
        self.fixture.contract["actions"]["B-work"]["requires"] = [target("check", "A-test")]
        self.fixture.adopt()
        self.fixture.work("A-work")
        run, _ = self.fixture.start("B-work")
        ref = self.fixture.receipt("A-test")
        self.fixture.finish("B-work", run)
        path = self.fixture.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        next(e for e in ledger["events"] if e["kind"] == "admitted" and e["run_id"] == run)["receipt_refs"] = [ref]
        write_json_atomic(path, ledger)
        result = self.evaluate("increment", "B")
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("before admission" in b["reason"] for b in result["blockers"]))
        # Fresh dispatch may be ready now, but the old execution is not complete.
        self.assertEqual(self.evaluate("action", "B-work")["status"], "ready")

    def test_greenfield_metric_claim_cannot_hide_new_cycles(self):
        self.fixture.work("A-work")
        def corrupt(receipt):
            receipt["result"]["baseline"] = "greenfield"
            receipt["result"]["metrics"]["cycles"].update(base=None, head=1)
        self.fixture.receipt("A-metrics", mutate=corrupt)
        result = self.evaluate("increment", "A")
        self.assertEqual(next(d for d in result["due"] if d["check_id"] == "A-metrics")["outcome"], "fail")

    def test_closure_needs_all_member_executions_before_its_sequence(self):
        self.fixture.add_action("A-extra", "A", inputs=scope("src/A.py"))
        self.fixture.adopt()
        refs = self.fixture.complete_increment("A")
        # All receipts exist before the old closure, but this additional member
        # has no check depending on it. Receipt order alone cannot prove closure.
        self.assertEqual(self.evaluate("increment", "A")["status"], "blocked")
        self.fixture.work("A-extra")
        result = self.evaluate("increment", "A")
        self.assertEqual(result["status"], "ready")
        self.assertIn("increment:A", {r["id"] for r in result["reopened"]})
        node = target("increment", "A")
        self.fixture.append(self.fixture.event("closed", node, "reclose-A", self.fixture.inputs(node).target,
                                               refs=refs, outcome="pass", commit="b" * 40))
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")

    def test_prerequisite_increment_cannot_close_after_dependent_closure(self):
        self.fixture.contract["increments"]["A"]["requires"].append(target("increment", "B"))
        self.fixture.adopt()
        b_refs = self.fixture.complete_increment("B")
        self.fixture.work("A-work", b_refs)
        a_refs = [self.fixture.receipt("A-" + suffix, refs=b_refs)
                  for suffix in ("test", "verify", "review", "metrics")]
        node = target("increment", "A")
        self.fixture.append(self.fixture.event("closed", node, "close-A", self.fixture.inputs(node).target,
                                               refs=b_refs + a_refs, outcome="pass", commit="a" * 40))
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")
        path = self.fixture.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        closure = next(e for e in ledger["events"] if e["kind"] == "closed" and e["target"] == target("increment", "B"))
        ledger["events"].remove(closure)
        ledger["events"].append(closure)
        for seq, event in enumerate(ledger["events"], 1):
            event["seq"] = seq
        write_json_atomic(path, ledger)
        self.assertEqual(self.evaluate("increment", "B")["status"], "complete")
        self.assertNotEqual(self.evaluate("increment", "A")["status"], "complete")

    def test_ship_closure_requires_increment_closures_in_its_prefix(self):
        refs = self.fixture.complete_increment("A") + self.fixture.complete_increment("B")
        node = target("ship", "ship")
        self.fixture.append(self.fixture.event("closed", node, "close-ship", self.fixture.inputs(node).target,
                                               refs=refs, outcome="pass"))
        self.assertEqual(self.evaluate("ship", "ship")["status"], "complete")
        path = self.fixture.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        ship = ledger["events"].pop()
        self.assertEqual(ledger["events"][-1]["target"], target("increment", "B"))
        ledger["events"].insert(len(ledger["events"]) - 1, ship)
        for seq, event in enumerate(ledger["events"], 1):
            event["seq"] = seq
        write_json_atomic(path, ledger)
        self.assertEqual(self.evaluate("ship", "ship")["status"], "ready")

    def test_honest_failed_launch_is_recordable_but_never_executed_work(self):
        node = target("action", "A-work")
        snapshot = self.fixture.inputs(node).target
        for index, code in enumerate((None, 127)):
            run = "failed-launch-%d" % index
            self.fixture.append(self.fixture.event("admitted", node, run, snapshot))
            self.fixture.append(self.fixture.event("launch-intent", node, run, snapshot, spawned="unknown"))
            self.fixture.append(self.fixture.event("process-observed", node, run, snapshot, spawned="no",
                process={"phase": "launch-failed", "pid": None, "process_group": None,
                         "start_identity": None, "identity_evidence": None, "returncode": code,
                         "cleanup": "not-attempted", "error": "Synthetic launch failure"}))
            for outcome, spawned in (("executed", "no"), ("pass", "no"), ("fail", "yes")):
                with self.subTest(code=code, outcome=outcome, spawned=spawned), self.assertRaises(ValueError):
                    self.fixture.append(self.fixture.event("completed", node, run, snapshot,
                        child_exit=code, outcome=outcome, spawned=spawned))
            self.fixture.append(self.fixture.event("completed", node, run, snapshot,
                                                   child_exit=code, outcome="fail", spawned="no"))
            self.assertEqual(self.evaluate()["status"], "ready")
            self.assertEqual(self.evaluate("action", "B-work")["status"], "ready")

    def test_no_spawn_cannot_supply_a_behavioral_red_receipt(self):
        self.temporal_fixture(red=True)
        def red(receipt):
            receipt["result"]["tests"][0].update(outcome="assertion-fail", error={
                "name": "AssertionError", "code": "ERR_TEST_FAILURE", "cause_code": "ERR_ASSERTION",
                "message": "Synthetic red symptom", "assertion_stack": "at fixture.test.mjs:1:1",
                "operator": "strictEqual", "expected": "2", "actual": "1"})
        self.fixture.receipt("A-before", mutate=red, code=1)
        self.assertEqual(self.evaluate()["status"], "ready")
        path = self.fixture.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        ledger["events"] = [e for e in ledger["events"] if e["kind"] != "process-observed"
                            or e["process"]["phase"] != "direct-exited"]
        for seq, event in enumerate(ledger["events"], 1):
            event["seq"] = seq
            if event["kind"] == "process-observed":
                event["spawned"] = "no"
                event["process"].update(phase="launch-failed", pid=None, returncode=1, error="Synthetic launch failure")
            if event["kind"] == "completed":
                event["spawned"] = "no"
        write_json_atomic(path, ledger)
        self.assertEqual(self.evaluate()["status"], "blocked")

    def close_with_refs(self, kind, name, refs):
        self.fixture.serial += 1
        node = target(kind, name)
        return self.fixture.append(self.fixture.event(
            "closed", node, "correction-close-%d" % self.fixture.serial, self.fixture.inputs(node).target,
            refs=refs, outcome="pass", commit="c" * 40 if kind == "increment" else None))

    def replace_closure_refs(self, kind, name, refs):
        """Corrupt only consumed refs in an owned protocol fixture, not its order."""
        path = self.fixture.workspace / "evidence/ledger.json"
        ledger = read_json(path)
        event = next(e for e in reversed(ledger["events"]) if e["kind"] == "closed"
                     and e["target"] == target(kind, name))
        event["receipt_refs"] = deepcopy(refs)
        write_json_atomic(path, ledger)

    def run_increment_checks(self, name, prerequisites):
        self.fixture.work(name + "-work", prerequisites)
        return [self.fixture.receipt(name + "-" + suffix, refs=prerequisites)
                for suffix in ("test", "verify", "review", "metrics")]

    def test_future_handoff_receipt_cannot_replace_exact_closure_proof(self):
        f = self.fixture
        f.contract["increments"]["B"]["requires"].append(target("increment", "A"))
        f.contract["actions"]["A-review-run"]["command"] = None
        f.contract["checks"]["A-review"]["handoff_steps"] = ["Return attributed review fixture"]
        f.adopt()
        original = f.complete_increment("A")
        blobs = {ref["id"]: (f.workspace / ("evidence/receipts/%s.json" % ref["id"])).read_bytes()
                 for ref in original}
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")
        self.assertEqual(self.evaluate("action", "B-work")["status"], "ready")
        replacement = f.receipt("A-review")
        latest = [replacement if ref == original[2] else ref for ref in original]
        self.assertEqual(self.evaluate("increment", "A")["status"], "ready")
        self.replace_closure_refs("increment", "A", latest)
        self.assertEqual(self.evaluate("increment", "A")["status"], "ready")
        blocked = self.evaluate("action", "B-work")
        self.assertEqual(blocked["status"], "blocked")
        self.assertIsNone(blocked["next_command"])
        self.close_with_refs("increment", "A", list(reversed(latest)))
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")
        self.assertEqual(self.evaluate("action", "B-work")["status"], "ready")
        for receipt_id, content in blobs.items():
            self.assertEqual((f.workspace / ("evidence/receipts/%s.json" % receipt_id)).read_bytes(), content)

    def test_transitive_action_proof_must_match_closure_prefix_exactly(self):
        f = self.fixture
        f.add_check("A-origin", "A", inputs=scope("src/A.py"))
        f.add_check("A-middle", "A", inputs=scope("src/A.py"), requires=[target("check", "A-origin")])
        f.contract["actions"]["A-work"]["requires"] = [target("check", "A-middle")]
        f.adopt()

        def execute_chain():
            origin = f.receipt("A-origin")
            middle = f.receipt("A-middle", refs=[origin])
            return [origin, middle, *self.run_increment_checks("A", [middle])]

        first = execute_chain()
        self.close_with_refs("increment", "A", first)
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")
        latest = execute_chain()
        self.assertEqual(self.evaluate("increment", "A")["status"], "ready")
        self.replace_closure_refs("increment", "A", latest)
        self.assertEqual(self.evaluate("increment", "A")["status"], "ready")
        self.close_with_refs("increment", "A", list(reversed(latest)))
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")
        f.write("src/A.py", "VALUE = 2\n")
        self.assertEqual(self.evaluate("increment", "A")["status"], "blocked")

    def test_inherited_increment_receipts_cannot_be_backfilled_into_closure(self):
        f = self.fixture
        f.contract["increments"]["B"]["requires"].append(target("increment", "A"))
        f.adopt()
        a_refs = f.complete_increment("A")
        original = [*a_refs, *self.run_increment_checks("B", a_refs)]
        self.close_with_refs("increment", "B", original)
        self.assertEqual(self.evaluate("increment", "B")["status"], "complete")
        replacement = f.receipt("A-test")
        latest_a = [replacement if ref == a_refs[0] else ref for ref in a_refs]
        self.close_with_refs("increment", "A", latest_a)
        latest_b = [*latest_a, *self.run_increment_checks("B", latest_a)]
        self.assertEqual(self.evaluate("increment", "B")["status"], "ready")
        self.replace_closure_refs("increment", "B", latest_b)
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")
        self.assertEqual(self.evaluate("increment", "B")["status"], "ready")
        self.close_with_refs("increment", "B", list(reversed(latest_b)))
        self.assertEqual(self.evaluate("increment", "B")["status"], "complete")

    def test_ship_cannot_substitute_receipts_from_a_later_valid_reclosure(self):
        f = self.fixture
        a_refs = f.complete_increment("A")
        b_refs = f.complete_increment("B")
        self.close_with_refs("ship", "ship", a_refs + b_refs)
        self.assertEqual(self.evaluate("ship", "ship")["status"], "complete")
        replacement = f.receipt("A-test")
        latest_a = [replacement if ref == a_refs[0] else ref for ref in a_refs]
        self.close_with_refs("increment", "A", latest_a)
        self.assertEqual(self.evaluate("ship", "ship")["status"], "ready")
        self.replace_closure_refs("ship", "ship", latest_a + b_refs)
        self.assertEqual(self.evaluate("increment", "A")["status"], "complete")
        self.assertEqual(self.evaluate("increment", "B")["status"], "complete")
        self.assertEqual(self.evaluate("ship", "ship")["status"], "ready")
        self.close_with_refs("ship", "ship", list(reversed(latest_a + b_refs)))
        self.assertEqual(self.evaluate("ship", "ship")["status"], "complete")

    def test_review_r1_required_comparisons_cannot_be_replaced_by_floors(self):
        f = self.fixture
        f.contract["actions"]["B-work"]["requires"] = [target("check", "A-metrics")]
        f.adopt()
        f.work("A-work")
        for name in sorted(workflow_gate.REQUIRED_METRICS):
            for mode in ("floor", "coverage"):
                with self.subTest(metric=name, mode=mode):
                    def substitute(receipt):
                        result = receipt["result"]
                        metric = result["metrics"][name]
                        higher = name in ("mutation_score_pct", "diff_coverage_pct")
                        metric.update(base=100 if higher else 0, head=90 if higher else 100)
                        rule = result["policy"]["rules"][name]
                        rule.update(mode=mode, threshold=60 if higher else 0)
                        policy = result["policy"]
                        policy["sha256"] = canonical_hash({k: policy[k] for k in ("required", "rules")})
                    f.receipt("A-metrics", mutate=substitute)
                    self.assertNotEqual(self.evaluate("check", "A-metrics")["status"], "complete")
                    result = self.evaluate("action", "B-work")
                    self.assertEqual(result["status"], "blocked")
                    self.assertIsNone(result["next_command"])

    def test_review_r1_tightening_adds_to_comparison_and_preserves_positive_proof(self):
        f = self.fixture
        f.contract["actions"]["B-work"]["requires"] = [target("check", "A-metrics")]
        f.adopt()
        f.work("A-work")
        for score, threshold, expected in ((96, 95, "ready"), (94, 95, "blocked"),
                                           (100, 59, "blocked"), (100, 60, "ready")):
            with self.subTest(score=score, threshold=threshold):
                def tighten(receipt):
                    result = receipt["result"]
                    result["metrics"]["mutation_score_pct"].update(base=score, head=score)
                    policy = result["policy"]
                    policy["rules"]["mutation_score_pct"].update(threshold=threshold, origin="repo-source")
                    policy["sha256"] = canonical_hash({k: policy[k] for k in ("required", "rules")})
                f.receipt("A-metrics", mutate=tighten)
                self.assertEqual(self.evaluate("action", "B-work")["status"], expected)

    def test_review_r2_failed_metric_producers_cannot_authorize_direct_consumers(self):
        f = self.fixture
        f.contract["actions"]["B-work"]["requires"] = [target("check", "A-metrics")]
        f.adopt()
        f.work("A-work")
        for code in (0, 1, 124, 125, 127, 0):
            with self.subTest(code=code):
                f.receipt("A-metrics", code=code)
                result = self.evaluate("action", "B-work")
                self.assertEqual(result["status"], "blocked" if code else "ready")
                self.assertEqual(self.evaluate("check", "A-metrics")["status"],
                                 "ready" if code else "complete")
                if code:
                    self.assertIsNone(result["next_command"])

    def test_review_r1_greenfield_and_warn_comparisons_remain_authoritative(self):
        f = self.fixture
        f.contract["actions"]["B-work"]["requires"] = [target("check", "A-metrics")]
        f.adopt()
        f.work("A-work")
        cases = [
            ("cycles", 0, 0, "greenfield", "ok", "floor", 0, "ready"),
            ("cycles", 0, 5, "greenfield", "ok", "floor", 0, "blocked"),
            ("mutation_score_pct", 100, 98, "compared", "warn", "floor", 60, "ready"),
            ("mutation_score_pct", 100, 98, "compared", "ok", "floor", 60, "blocked"),
            ("diff_coverage_pct", 100, 100, "compared", "ok", "compare", None, "blocked"),
            ("cycles", 0, 0, "compared", "ok", "compare", 5, "blocked"),
        ]
        for name, base, head, baseline, comparison, mode, threshold, expected in cases:
            with self.subTest(metric=name, head=head, baseline=baseline, comparison=comparison, mode=mode):
                def alter(receipt):
                    result = receipt["result"]
                    result.update(baseline=baseline, measurement_status=comparison, worst_status=comparison)
                    result["metrics"][name].update(base=base, head=head, comparison=comparison)
                    policy = result["policy"]
                    policy["rules"][name].update(mode=mode, threshold=threshold)
                    policy["sha256"] = canonical_hash({k: policy[k] for k in ("required", "rules")})
                f.receipt("A-metrics", mutate=alter)
                self.assertEqual(self.evaluate("action", "B-work")["status"], expected)

    def test_review_r2_exit_and_recorded_outcome_must_both_establish_success(self):
        f = self.fixture
        f.contract["actions"]["B-work"]["requires"] = [target("check", "A-metrics")]
        f.adopt()
        f.work("A-work")
        for code, outcome, expected in ((0, "fail", "blocked"), (1, "executed", "blocked"),
                                        (0, "executed", "ready")):
            with self.subTest(code=code, outcome=outcome):
                def replace_outcome(receipt):
                    path = f.workspace / "evidence/ledger.json"
                    ledger = read_json(path)
                    completed = next(e for e in reversed(ledger["events"])
                                     if e["kind"] == "completed" and e["run_id"] == receipt["run_id"])
                    completed["outcome"] = outcome
                    write_json_atomic(path, ledger)
                f.receipt("A-metrics", code=code, mutate=replace_outcome)
                self.assertEqual(self.evaluate("action", "B-work")["status"], expected)

    def test_review_r2_failed_finding_producers_and_valid_handoffs(self):
        f = self.fixture
        for kind, role in (("review", "reviewer"), ("verification", "verifier"),
                           ("research", "researcher"), ("human", "human")):
            name = "A-extra-" + kind
            f.add_check(name, "A", kind, role, inputs=scope("src/A.py"))
        f.adopt()
        for kind in ("review", "verification", "research", "human"):
            name = "A-extra-" + kind
            f.contract["actions"]["B-work"]["requires"] = [target("check", name)]
            f.adopt()
            for code in (0, 1, 124, 0):
                with self.subTest(kind=kind, code=code):
                    f.receipt(name, code=code)
                    result = self.evaluate("action", "B-work")
                    self.assertEqual(result["status"], "blocked" if code else "ready")
                    if code:
                        self.assertIsNone(result["next_command"])
            f.contract["actions"][name + "-run"]["command"] = None
            f.contract["checks"][name]["handoff_steps"] = ["Return attributed fixture findings"]
            f.adopt()
            f.receipt(name)
            self.assertEqual(self.evaluate("action", "B-work")["status"], "ready")

    def test_review_r2_red_execution_exception_requires_validated_native_proof(self):
        self.temporal_fixture(red=True)
        f = self.fixture
        f.contract["actions"]["B-work"]["requires"] = [target("action", "A-before-run")]
        f.adopt()
        self.assertEqual(f.inputs(target("action", "A-before-run")).target,
                         f.inputs(target("check", "A-before")).target)
        def red(receipt):
            receipt["result"]["tests"][0].update(outcome="assertion-fail", error={
                "name": "AssertionError", "cause_code": "ERR_ASSERTION", "code": "ERR_TEST_FAILURE",
                "message": "Declared fixture red", "assertion_stack": "at fixture.test.mjs:1:1",
                "operator": "strictEqual", "expected": "2", "actual": "1"})
        for code in (1, 124, 125, 127):
            with self.subTest(code=code):
                ref = f.receipt("A-before", code=code, mutate=red)
                self.assertEqual(self.evaluate("action", "B-work")["status"],
                                 "ready" if code == 1 else "blocked")
                if code == 1:
                    f.work("B-work", [ref])
                    self.assertEqual(self.evaluate("action", "B-work")["status"], "complete")
                    f.receipt("A-before", code=1, mutate=red)
                    self.assertEqual(self.evaluate("action", "B-work")["status"], "ready")
        f.receipt("A-before", code=1)  # Nonzero without assertion failure is not red proof.
        self.assertEqual(self.evaluate("action", "B-work")["status"], "blocked")

    def test_review_r3_prefix_work_is_shared_and_scoped_to_one_evaluation(self):
        f = self.fixture
        names = list("ABCDEFGH")
        for name in names[2:]:
            f.components[name.lower()] = {"signature": name + "()"}
            f.write("src/%s.py" % name, "VALUE = 1\n")
            f.contract["increments"][name] = {
                "id": name, "acs": ["AC-" + name], "components": [name.lower()],
                "requires": [], "implementers": [producer()]}
            f.add_action(name + "-work", name, inputs=scope("src/%s.py" % name))
            for suffix, kind, role in (("test", "test", "implementer"), ("verify", "verification", "verifier"),
                                       ("review", "review", "reviewer"), ("metrics", "metrics", "implementer")):
                f.add_check(name + "-" + suffix, name, kind, role, inputs=scope("src/%s.py" % name),
                            requires=[target("action", name + "-work")])
                f.contract["increments"][name]["requires"].append(target("check", name + "-" + suffix))
        for prior, name in zip(names, names[1:]):
            f.contract["increments"][name]["requires"].append(target("increment", prior))
        f.adopt()
        refs = []
        for size, name in enumerate(names, 1):
            refs = [*refs, *self.run_increment_checks(name, refs)]
            self.close_with_refs("increment", name, refs)
            if size not in (3, 5, 8):
                continue
            contract, _, ledger = f.load()
            node = target("increment", name)
            inputs = f.inputs(node)
            constructions, misses = [], []
            original_init, original_proof = workflow_gate._Evaluation.__init__, workflow_gate._Evaluation.proof
            def counted_init(engine, *args, **kwargs):
                constructions.append(1)
                original_init(engine, *args, **kwargs)
            def counted_proof(engine, item):
                key = item["kind"] + ":" + item["id"]
                if key not in engine.memo:
                    misses.append((len(engine.events), key))
                return original_proof(engine, item)
            with patch.object(workflow_gate._Evaluation, "__init__", counted_init), \
                    patch.object(workflow_gate._Evaluation, "proof", counted_proof):
                result = evaluate(contract, ledger, inputs, node)
            print("C1 R3 scale: increments=%d evaluators=%d proof_misses=%d unique=%d" %
                  (size, len(constructions), len(misses), len(set(misses))), flush=True)
            with self.subTest(increments=size):
                self.assertEqual(result["status"], "complete")
                self.assertLessEqual(len(constructions), size + 1)
                self.assertEqual(len(misses), len(set(misses)))
                self.assertLessEqual(len(misses), 10 * size * (size + 1))
        f.write("src/A.py", "VALUE = 2\n")
        self.assertEqual(self.evaluate("increment", names[-1])["status"], "blocked")
        f.write("src/A.py", "VALUE = 1\n")
        self.assertEqual(self.evaluate("increment", names[-1])["status"], "complete")


if __name__ == "__main__":
    unittest.main()
