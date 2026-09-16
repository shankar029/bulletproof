import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cp, mkdir, mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { generateMutants } from '../../../evals/lib/mutate.mjs';
import { runNode } from './command.mjs';

if (process.argv.length !== 2) throw new Error('Usage: node scripts/mutation.mjs');
const appRoot = join(import.meta.dirname, '..');
await mkdir(join(appRoot, '.work'), { recursive: true });
const workspace = await mkdtemp(join(appRoot, '.work', 'mutation-'));
const copy = join(workspace, 'app');
const report = {
  scope: 'Bounded backend ESM sample: up to four existing textual-engine mutants per src/*.mjs module. Browser/public code is separately browser-verified, not included in this native-suite mutation score.',
  engine: 'evals/lib/mutate.mjs generateMutants; no changes to shared engine or production files',
  results: [],
};
try {
  for (const path of ['src', 'public', 'test', 'scripts']) await cp(join(appRoot, path), join(copy, path), { recursive: true });
  const baseline = await runNode(['scripts/check.mjs', 'all'], { cwd: copy, timeout: 150000 });
  report.baseline = baseline;
  assert.equal(baseline.timedOut, false);
  assert.equal(baseline.code, 0, baseline.stdout + baseline.stderr);
  for (const file of (await readdir(join(copy, 'src'))).filter(file => file.endsWith('.mjs')).sort()) {
    const path = join(copy, 'src', file);
    const source = await readFile(path, 'utf8');
    const sourceSha256 = createHash('sha256').update(source).digest('hex');
    for (const mutant of generateMutants(source, { max: 4 })) {
      const entry = { file, sourceSha256, id: mutant.id, operator: mutant.operator, line: source.slice(0, mutant.index).split('\n').length };
      await writeFile(path, mutant.mutated);
      try {
        const syntax = await runNode(['--check', path], { cwd: copy, timeout: 15000 });
        if (syntax.timedOut) throw new Error(`Syntax check timed out: ${file}`);
        if (syntax.code !== 0) {
          report.results.push({ ...entry, result: 'INVALID_SYNTAX', evidence: syntax });
          continue;
        }
        const result = await runNode(['scripts/check.mjs', 'all'], { cwd: copy, timeout: 150000 });
        const verdict = result.timedOut || result.code === 124 ? 'TIMEOUT' :
          result.code === 0 ? 'SURVIVED' :
            /ERR_ASSERTION/.test(result.stdout) ? 'KILLED_ASSERTION' : 'ERROR_REQUIRES_REVIEW';
        report.results.push({ ...entry, result: verdict, evidence: result });
        console.log(`${file}:${entry.line} ${entry.operator}: ${verdict}`);
      } finally {
        await writeFile(path, source);
      }
    }
    assert.equal(await readFile(join(appRoot, 'src', file), 'utf8'), source, 'Released source changed during measurement');
  }
  const killed = report.results.filter(result => result.result === 'KILLED_ASSERTION').length;
  const survived = report.results.filter(result => result.result === 'SURVIVED').length;
  report.summary = {
    killed, survived,
    ungraded: report.results.length - killed - survived,
    score: killed + survived ? killed / (killed + survived) : null,
    limitation: 'Timeouts/load failures require review and are not silently counted as assertion kills.',
  };
  if (report.summary.score === null || report.summary.score < 0.6 || report.summary.ungraded > 0) process.exitCode = 1;
} finally {
  await writeFile(join(workspace, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await rm(copy, { recursive: true, force: true });
  console.log(`Evidence: ${join(workspace, 'report.json')}`);
}
