import { test } from 'node:test';
import { runPair } from './helpers.mjs';

test('missing review blocks; admitted attributed review permits dependent work', async () => {
  await runPair('test_missing_review_pair_blocks_then_actual_handoff_record_unblocks');
});

test('setup failure is not behavioral red; actual matching assertion failure is', async () => {
  await runPair('test_setup_vs_red_pair_uses_real_native_assertion');
});

test('stale proof blocks; fresh public-CLI execution resumes without rewriting receipts', async () => {
  await runPair('test_stale_pair_fresh_process_reopens_only_affected_receipt');
});

test('missing metrics blocks attachment; unrelated work works (positive quality closure unavailable)', async () => {
  await runPair('test_metrics_pair_failure_capture_and_independent_work_not_fake_closure');
});

test('premature retirement blocks; prior accepted compatibility permits retirement', async () => {
  await runPair('test_compatibility_pair_requires_accepted_pre_retirement_proof');
});
