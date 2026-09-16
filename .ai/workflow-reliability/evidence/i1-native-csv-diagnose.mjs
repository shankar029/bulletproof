// Bounded real corpus diagnosis. Writes only the named evidence artifact and
// a uniquely owned temporary copy; never changes benchmark fixtures or scores.
import { mkdtempSync, cpSync, readFileSync, writeFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { generateMutants } from '../../../evals/lib/mutate.mjs';
import { parseReport, classifyResult, checkSyntax } from '../../../scripts/native_result.mjs';
import { runTestQuality, testQualityScore } from '../../../evals/lib/score.mjs';

const root = fileURLToPath(new URL('../../../', import.meta.url));
const project = path.join(root, 'benchmark/projects/csv-stats-cli');
const temp = mkdtempSync(path.join(tmpdir(), 'csv-native-diagnosis-'));
const { NODE_TEST_CONTEXT, ...env } = process.env;
const reporter = new URL('../../../scripts/native_result.mjs', import.meta.url).href;
const record = { runtime: process.version, project: 'csv-stats-cli', candidates: [] };
try {
  const arm = path.join(temp, 'arm');
  cpSync(path.join(project, 'bulletproof'), arm, { recursive: true });
  cpSync(path.join(project, 'shared'), path.join(temp, 'shared'), { recursive: true });
  const implementation = path.join(arm, 'cli.ts');
  const original = readFileSync(implementation, 'utf8');
  const files = readdirSync(arm).filter(f => f.includes('.test.'));
  const run = () => {
    const result = spawnSync(process.execPath, ['--test', `--test-reporter=${reporter}`, ...files],
      { cwd: arm, env, encoding: 'utf8', timeout: 30_000 });
    return { rc: result.status, native: parseReport(result.stdout || ''),
      stdout: result.stdout || '', stderr: result.stderr || '' };
  };
  record.baseline = run();
  if (classifyResult(record.baseline.native, record.baseline.rc) !== 'survived') {
    throw new Error('Baseline not green; diagnosis unavailable');
  }
  for (const mutant of generateMutants(original, { max: 16 })) {
    writeFileSync(implementation, mutant.mutated);
    const syntax = checkSyntax(implementation);
    const execution = syntax.status === 0 ? run() : null;
    const line = original.slice(0, mutant.index).split('\n').length;
    record.candidates.push({
      id: mutant.id, operator: mutant.operator, line,
      before: original.split('\n')[line - 1], after: mutant.mutated.split('\n')[line - 1],
      syntax, execution,
      outcome: execution ? classifyResult(execution.native, execution.rc, record.baseline.native) : 'invalid-syntax',
    });
  }
  record.counts = record.candidates.reduce((counts, item) => {
    counts[item.outcome] = (counts[item.outcome] || 0) + 1;
    return counts;
  }, {});
  // Demonstrate the exact missing assertion in the owned temp copy only.
  // No repository fixture is edited or implicitly authorized for editing.
  const gap = "import {test} from 'node:test';import assert from 'node:assert/strict';"
    + "import {parseCsv} from './cli.ts';"
    + "test('preserves trailing empty field without final newline',()=>"
    + "assert.deepEqual(parseCsv('a,b\\n1,'),[['a','b'],['1','']]));";
  writeFileSync(path.join(arm, 'gap.test.ts'), gap);
  files.push('gap.test.ts');
  writeFileSync(implementation, original);
  const gapBaseline = run();
  const survivor = record.candidates.find(c => c.outcome === 'survived');
  if (!survivor) throw new Error('Expected an observed survivor before proposing an assertion');
  writeFileSync(implementation, generateMutants(original, { max: 16 }).find(m => m.id === survivor.id).mutated);
  const gapMutant = run();
  record.proposed_assertion = { source: gap, baseline: gapBaseline, mutant: gapMutant,
    outcome: classifyResult(gapMutant.native, gapMutant.rc, gapBaseline.native) };
  if (record.proposed_assertion.outcome !== 'killed-assertion') throw new Error('Proposed assertion not proven');
  writeFileSync(implementation, original);
  record.temp_copy_quality_with_assertion = runTestQuality({ quality: { src: 'cli.ts', mutate: true } }, temp, arm);
  record.temp_copy_score_with_assertion = testQualityScore(record.temp_copy_quality_with_assertion);
  writeFileSync(new URL('i1-native-csv-diagnosis.json', import.meta.url), JSON.stringify(record, null, 2));
  console.log(JSON.stringify({ counts: record.counts, candidates: record.candidates.map(
    ({ id, line, before, after, outcome }) => ({ id, line, before, after, outcome })) }, null, 2));
} finally {
  rmSync(temp, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}
