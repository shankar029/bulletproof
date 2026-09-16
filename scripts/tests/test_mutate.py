import json
import os
from pathlib import Path
import sys
import unittest
import uuid

from helpers import GitFixture, SCRIPTS
from mutate import build_mutants, changed_lines, detect_test_cmd, select_test_run
from evidence import exclusive_lock, source_snapshot, write_json_atomic


class MutationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = GitFixture()
        self.addCleanup(self.fixture.close)
        self.root = self.fixture.root
        # Ignore output for Git cleanliness, but source_snapshot still observes every
        # file except the exact current report and administrative .git metadata.
        self.fixture.write(".gitignore", ".ai/*/evidence/\n")

    def prepare(self, extension="mjs", folder="", body=None, source=None):
        name = (folder + "/" if folder else "") + "value." + extension
        test_name = (folder + "/" if folder else "") + "math case.test." + extension
        if extension == "cjs":
            old = "exports.flag = false;\r\nexports.unused = false;\r\n"
            new = "exports.flag = true;\r\nexports.unused = true;\r\n"
            imports = "const {test}=require('node:test');const assert=require('node:assert/strict');const {flag}=require('./value.cjs');\n"
        else:
            old = "export const flag = false;\r\nexport const unused = false;\r\n"
            new = "export const flag = true;\r\nexport const unused = true;\r\n"
            imports = "import {test} from 'node:test';import assert from 'node:assert/strict';import {flag} from './value.mjs';\n"
        if source is not None:
            old, new = source
        self.fixture.write(name, old)
        self.fixture.write(test_name, imports + (body or "test('required with spaces',()=>assert.equal(flag,true));"))
        self.base = self.fixture.commit("fixture: baseline")
        self.fixture.write(name, new)
        self.fixture.commit("fixture: change")
        return name, test_name, new.encode("utf8")

    def cli(self, *extra, expected=0, repo=None, run_id=None):
        run_id = run_id or uuid.uuid4().hex
        argv = [sys.executable, str(SCRIPTS / "mutate.py"), "--repo", str(repo or self.root),
                "--slug", "fixture", "--base", self.base, "--run-id", run_id, "--timeout", "5", *extra]
        result = self.fixture.run(*argv, expected=expected, timeout=90)
        report_path = self.root / ".ai/fixture/evidence/runs" / run_id / "mutation.json"
        report = json.loads(report_path.read_text(encoding="utf8")) if report_path.exists() else None
        return report, result, report_path

    def test_real_esm_and_cjs_kill_survivor_byte_restoration_and_nonce(self):
        # Both module systems use the real public CLI and native reporter.
        for extension in ("mjs", "cjs"):
            with self.subTest(extension=extension):
                name, _, original = self.prepare(extension)
                report, _, output = self.cli("--max-mutants", "2")
                self.assertEqual(report["schema_version"], 2)
                self.assertTrue(report["complete"], report["reason"])
                self.assertEqual((report["killed"], report["survived"], report["total"]), (1, 1, 2))
                self.assertEqual(report["score_pct"], 50.0)  # threshold is probe policy, not execution
                self.assertEqual(report["source"]["scope_sha256"], report["restored_sha256"])
                self.assertEqual((self.root / name).read_bytes(), original)
                self.assertEqual(report["source"]["base"], self.base)
                self.assertEqual(len(report["source"]["head"]), 40)
                self.assertEqual(report["test_run"]["command"]["environment"], {"NODE_TEST_CONTEXT": None})
                saved = output.read_bytes()
                _, result, _ = self.cli(run_id=report["run_id"], expected=2)
                self.assertEqual(output.read_bytes(), saved)
                self.assertIn("exists", result[2].lower())

    def test_nested_package_and_spaced_argv_preserve_test_cwd_and_parameters(self):
        folder = "packages/space name"
        _, test_file, _ = self.prepare(folder=folder)
        self.fixture.write(folder + "/package.json", '{"type":"module"}')
        self.fixture.commit("fixture: nested manifest")
        report, _, _ = self.cli("--test-cwd", str(self.root / folder), "--max-mutants", "1",
                                "--", "node", "--test", "--test-name-pattern", "required.*spaces",
                                Path(test_file).name)
        self.assertEqual(report["test_run"]["command"]["cwd"], folder)
        argv = report["test_run"]["command"]["argv"]
        self.assertEqual(argv[-3:], ["--test-name-pattern", "required.*spaces", "math case.test.mjs"])
        # Default --repo nested directory is preserved as cwd before Git normalization.
        report, _, _ = self.cli("--max-mutants", "1", repo=self.root / folder)
        self.assertEqual(report["test_run"]["command"]["cwd"], folder)
        self.assertEqual(report["killed"], 1)

    def test_setup_log_spoof_zero_missing_and_skipped_mutants_are_not_kills(self):
        bodies = [
            "test('required',()=>{if(!flag) throw new Error('setup');assert.ok(flag);});",
            "test('required',()=>{if(!flag) throw new Error('ERR_ASSERTION');});",
            "if(flag)test('required',()=>{});else console.log('ERR_ASSERTION # fail 1');",
            "test('required',{skip:!flag},()=>{});",
            "if(flag)test('required',()=>{});else test('different',()=>assert.fail());",
        ]
        for body in bodies:
            with self.subTest(body=body):
                name, _, original = self.prepare(body=body)
                report, _, _ = self.cli("--max-mutants", "1", expected=2)
                self.assertFalse(report["complete"])
                self.assertEqual(report["killed"], 0)
                self.assertEqual(report["ungraded"], 1)
                self.assertEqual((self.root / name).read_bytes(), original)

    def test_baseline_zero_import_syntax_and_skips_fail_before_mutation(self):
        for body in ["console.log('ERR_ASSERTION');", "await import('./missing.mjs');",
                     "not valid syntax!", "test.skip('required',()=>{});", "test.todo('required');"]:
            with self.subTest(body=body):
                name, _, original = self.prepare(body=body)
                report, _, _ = self.cli("--max-mutants", "1", expected=2)
                self.assertFalse(report["complete"])
                self.assertEqual(report["killed"], 0)
                self.assertIn("Baseline", report["reason"])
                self.assertEqual((self.root / name).read_bytes(), original)

    def test_timeout_is_ungraded_and_restores_bytes(self):
        name, _, original = self.prepare(body=
            "test('required',async()=>{if(!flag)await new Promise(r=>setTimeout(r,30000));});")
        report, _, _ = self.cli("--max-mutants", "1", "--timeout", "1", expected=2)
        self.assertEqual(report["results"][0]["outcome"], "timeout")
        self.assertEqual((report["killed"], report["ungraded"]), (0, 1))
        self.assertEqual((self.root / name).read_bytes(), original)

    def test_inherited_node_context_is_removed_and_bom_is_restored(self):
        name, _, original = self.prepare(source=(
            "\ufeffexport const flag = false;\r\n", "\ufeffexport const flag = true;\r\n"))
        previous = os.environ.get("NODE_TEST_CONTEXT")
        os.environ["NODE_TEST_CONTEXT"] = "child-v8"
        try:
            report, _, _ = self.cli("--max-mutants", "1")
        finally:
            if previous is None:
                os.environ.pop("NODE_TEST_CONTEXT", None)
            else:
                os.environ["NODE_TEST_CONTEXT"] = previous
        self.assertEqual(report["killed"], 1)
        self.assertEqual((self.root / name).read_bytes(), original)

    def test_exclusive_lock_blocks_a_second_measurement(self):
        self.prepare()
        lock = self.root / ".git/bulletproof-mutation.lock"
        with exclusive_lock(lock, {"token": uuid.uuid4().hex}):
            report, _, _ = self.cli(expected=2)
            self.assertFalse(report["complete"])
            self.assertIsNone(report["source"])
            self.assertTrue(lock.exists())

    def test_syntax_preflight_rejects_generated_typescript_generic_mutant(self):
        self.fixture.write("value.ts", "export function identity(value) { return value; }\n")
        self.fixture.write("case.test.mjs",
                           "import {test} from 'node:test';import assert from 'node:assert/strict';"
                           "import {identity} from './value.ts';test('value',()=>assert.equal(identity(1),1));")
        self.base = self.fixture.commit()
        original = b"export function identity<T>(value:T) { return value; }\r\n"
        self.fixture.write("value.ts", original)
        self.fixture.commit()
        report, _, _ = self.cli(expected=2)
        self.assertEqual(report["results"][0]["outcome"], "invalid-syntax")
        self.assertEqual(report["killed"], 0)
        self.assertNotIn("execution", report["results"][0]["artifacts"])
        self.assertEqual((self.root / "value.ts").read_bytes(), original)

    def test_competing_edit_preserved_with_recovery_bytes(self):
        name, _, original = self.prepare(body=
            "import {writeFileSync} from 'node:fs';"
            "test('required',()=>{if(!flag)writeFileSync(new URL('./value.mjs',import.meta.url),"
            "\"export const flag = 'competitor';\\n\");assert.ok(flag);});")
        report, _, _ = self.cli("--max-mutants", "1", expected=2)
        self.assertIn("Competing edit preserved", report["reason"])
        self.assertIn(b"competitor", (self.root / name).read_bytes())
        import base64
        self.assertEqual(base64.b64decode(report["results"][0]["artifacts"]["original_base64"]), original)
        self.assertNotEqual(report["source"]["scope_sha256"], report["restored_sha256"])

    def test_dirty_untracked_contract_rejected_but_owned_output_is_not(self):
        self.prepare()
        self.fixture.write(".ai/fixture/current-design.json", "{}")
        report, _, _ = self.cli(expected=2)
        self.assertIn("dirty", report["reason"])
        self.assertIsNone(report["source"])

    def test_legacy_quoted_commands_fail_and_custom_runner_is_unclassified(self):
        self.prepare()
        report, _, _ = self.cli("--test-cmd", 'node --test "math case.test.mjs"', expected=2)
        self.assertIn("Ambiguous legacy", report["reason"])
        report, _, _ = self.cli("--", sys.executable, "-c", "print('ERR_ASSERTION')", expected=2)
        self.assertEqual(report["test_run"]["runner"], "process")
        self.assertEqual(report["killed"], 0)
        self.assertIn("Unsupported custom", report["reason"])

    def test_changed_python_cannot_be_hidden_by_candidate_selection(self):
        self.prepare()
        for source in ["value = 1\n", "value = True\n"]:
            with self.subTest(source=source):
                self.fixture.write("zzz_uncovered.py", source)
                self.fixture.commit("fixture: unsupported changed Python")
                report, _, _ = self.cli("--max-mutants", "1", expected=2)
                self.assertEqual(report["killed"], 1)
                self.assertEqual(report["ungraded"], 0)
                self.assertFalse(report["complete"])
                self.assertTrue(any(item["file"] == "zzz_uncovered.py"
                                    for item in report["unsupported_scope"]))

    def test_probe_can_preallocate_shared_run_directory(self):
        self.prepare()
        parent_file = self.fixture.write(".ai/fixture/evidence/runs/shared-run/probe.json",
                                         '{"parent":"allocated"}')
        report, _, _ = self.cli("--max-mutants", "1", run_id="shared-run")
        self.assertTrue(report["complete"])
        self.assertEqual(report["run_id"], "shared-run")
        self.assertEqual(parent_file.read_text(), '{"parent":"allocated"}')
        self.assertIn(parent_file.relative_to(self.root).as_posix(), report["source"]["files"])

    def test_shared_metrics_publication_preserves_freshness_but_contracts_do_not(self):
        self.prepare()
        contract = self.fixture.write(".ai/fixture/current-design.json", '{"revision":1}')
        self.fixture.commit("fixture: source contract")
        note = self.fixture.write(".ai/fixture/evidence/contract-note.json", '{"required":true}')
        report, _, output = self.cli("--max-mutants", "1", run_id="shared-run")
        original = report["source"]["scope_sha256"]
        scope = report["source"]["scope"]
        exclusions = {item["path"] for item in scope["excluded_outputs"]}
        self.assertEqual(exclusions, {
            ".git", ".ai/fixture/evidence/runs/shared-run/mutation.json",
            ".ai/fixture/evidence/runs/shared-run/metrics.json", ".ai/fixture/metrics.json",
        })
        write_json_atomic(output.with_name("metrics.json"), {"run_id": "shared-run"})
        write_json_atomic(self.root / ".ai/fixture/metrics.json", {"run_id": "shared-run"})
        self.assertEqual(source_snapshot(self.root, scope)["scope_sha256"], original)
        self.assertEqual(report["restored_sha256"], original)
        # Existing untracked generated display output is allowed by the same exact
        # ownership policy; a subsequent invocation still measures its own scope.
        second, _, _ = self.cli("--max-mutants", "1")
        self.assertTrue(second["complete"])
        # The second run is new observed evidence, not part of the first run's
        # output family. Restore that membership before testing source edits.
        second_path = self.root / ".ai/fixture/evidence/runs" / second["run_id"] / "mutation.json"
        second_path.unlink()
        self.assertEqual(source_snapshot(self.root, scope)["scope_sha256"], original)
        for path, replacement in [(contract, '{"revision":2}'), (note, '{"required":false}')]:
            before = path.read_bytes()
            path.write_text(replacement, encoding="utf8")
            self.assertNotEqual(source_snapshot(self.root, scope)["scope_sha256"], original)
            path.write_bytes(before)
        legacy_alias = self.root / ".ai/fixture/mutation.json"
        self.assertFalse(legacy_alias.exists())  # producer writes no mutation latest alias
        legacy_alias.write_text('{"foreign":"legacy"}', encoding="utf8")
        self.assertNotEqual(source_snapshot(self.root, scope)["scope_sha256"], original)

    def test_competing_report_write_is_not_overwritten(self):
        self.prepare(body=
            "import {writeFileSync} from 'node:fs';"
            "test('required',()=>{if(!flag)writeFileSync("
            "'.ai/fixture/evidence/runs/shared-run/mutation.json','{\"foreign\":true}');assert.ok(flag);});")
        report, result, _ = self.cli("--max-mutants", "1", run_id="shared-run", expected=2)
        self.assertEqual(report, {"foreign": True})
        self.assertIn("report ownership changed", result[2])

    def test_discovery_diffs_safe_operators_and_ambiguous_scope(self):
        self.prepare()
        self.assertIn("value.mjs", changed_lines(str(self.root), self.base))
        self.assertEqual(detect_test_cmd(str(self.root)), ["node", "--test", "math case.test.mjs"])
        self.fixture.write("operators.cjs",
                           "exports.arrow = x => x;\nexports.strict = x === 3;\n"
                           "exports.not = x !== 3;\nexports.shift = x >> 3;\n"
                           "exports.regex = /true/.test(x);\n")
        unsupported = []
        mutants = build_mutants(str(self.root), {"operators.cjs": {1, 2, 3, 4, 5}}, 20,
                                unsupported=unsupported)
        self.assertEqual([m["line"] for m in mutants], [2, 3])
        self.assertIn("!==", mutants[0]["_text"])
        self.assertIn("===", mutants[1]["_text"])
        self.assertEqual(unsupported[0]["line"], 5)
        self.fixture.write("nested/package.json", "{}")
        self.fixture.write("nested/hidden.test.mjs", "")
        self.assertNotIn("nested/hidden.test.mjs", detect_test_cmd(str(self.root)))
        with self.assertRaisesRegex(ValueError, "Conflicting reporter"):
            select_test_run(self.root, self.root, ["node", "--test", "--test-reporter=tap"])


if __name__ == "__main__":
    unittest.main()
