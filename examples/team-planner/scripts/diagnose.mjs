import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { runNode } from './command.mjs';

const appRoot = join(import.meta.dirname, '..');
if (process.argv.length !== 2) throw new Error('Usage: node scripts/diagnose.mjs');
await mkdir(join(appRoot, '.work'), { recursive: true });
const workspace = await mkdtemp(join(appRoot, '.work', 'diagnosis-'));
const copy = join(workspace, 'app');
const report = {
  scenario: 'Controlled filter-after-pagination defect; cause disclosed, not blind diagnosis',
  original: 'Existing seven-task HTTP query regression, expected second todo page E/F and total 4',
  minimized: 'Two-task HTTP regression: done then todo; filtered page 1 must contain todo and total 1',
  hypothesis: 'Taking a page before filtering lets excluded tasks consume the requested page.',
  comparison: 'Identical public HTTP inputs and regression commands against good, faulted and exact-restored source.',
  results: [],
};
const hash = text => createHash('sha256').update(text).digest('hex');
try {
  for (const path of ['src', 'public', 'test']) await cp(join(appRoot, path), join(copy, path), { recursive: true });
  await mkdir(join(copy, 'scripts'), { recursive: true });
  for (const file of ['command.mjs', 'diagnosis-probes.mjs']) await cp(join(import.meta.dirname, file), join(copy, 'scripts', file));
  const rulesPath = join(copy, 'src', 'rules.mjs');
  const source = await readFile(rulesPath, 'utf8');
  const filter = 'const matches = model.tasks.filter(task =>';
  const page = 'const items = matches.slice((page - 1) * pageSize, page * pageSize).map(task => taskView(model, task));';
  assert.equal(source.split(filter).length, 2, 'Filter injection site changed; revalidate the experiment');
  assert.equal(source.split(page).length, 2, 'Page injection site changed; revalidate the experiment');
  const faulty = source.replace(filter, 'const matches = model.tasks.slice((page - 1) * pageSize, page * pageSize).filter(task =>')
    .replace(page, 'const items = matches.map(task => taskView(model, task));');
  report.sourceSha256 = hash(source);
  report.faultSha256 = hash(faulty);
  report.injection = { filter, page, change: 'Move only pagination ahead of the existing filters; no parser or fixture changes.' };
  for (const [phase, code] of [['baseline', source], ['controlled-fault', faulty], ['restored', source]]) {
    await writeFile(rulesPath, code);
    const probe = await runNode(['scripts/diagnosis-probes.mjs'], { cwd: copy, timeout: 45000 });
    assert.equal(probe.timedOut, false, 'Probe setup timeout is not diagnosis evidence');
    assert.equal(probe.code, 0, probe.stdout + probe.stderr);
    const observations = JSON.parse(probe.stdout);
    assert.equal(observations.length, 10);
    for (const observation of observations) {
      const faulted = phase === 'controlled-fault' && observation.label !== 'same two tasks, page size two control';
      let expected = observation.expected;
      if (faulted) {
        expected = { ids: [], total: 0 };
        if (observation.label === 'original second page') expected = { ids: ['t-6'], total: 1 };
        else if (observation.label === 'same seven tasks, first page') expected = { ids: ['t-4'], total: 1 };
      }
      assert.deepEqual(observation.http, expected, `${phase}: ${observation.label}`);
      assert.deepEqual(observation.direct, expected, `${phase}: rules versus HTTP comparison`);
    }
    report.results.push({ phase, scenario: 'one-factor reduction and parsing discriminator', observations, ...probe });
    console.log(`${phase}/probes: ten observed cases; HTTP and direct rules agree, same-data page-size control verified`);
    for (const [scenario, file] of [['original', 'query.test.mjs'], ['minimized', 'diagnosis.test.mjs']]) {
      const result = await runNode(['--test', '--test-timeout=15000', '--test-reporter=tap', join('test', file)], { cwd: copy, timeout: 45000 });
      report.results.push({ phase, scenario, ...result });
      assert.equal(result.timedOut, false, `${phase}/${scenario} timed out; not behavioral proof`);
      if (phase === 'controlled-fault') {
        assert.equal(result.code, 1, `${scenario} must fail with the injected defect`);
        assert.match(result.stdout, /ERR_ASSERTION/);
        assert.match(result.stdout, /deepStrictEqual/);
        assert.doesNotMatch(result.stdout + result.stderr, /SyntaxError|ERR_MODULE_NOT_FOUND/);
      } else {
        assert.equal(result.code, 0, result.stdout + result.stderr);
        assert.match(result.stdout, /# fail 0/);
        assert.match(result.stdout, /# skipped 0/);
      }
      console.log(`${phase}/${scenario}: expected ${phase === 'controlled-fault' ? 'behavioral failure' : 'pass'}, observed exit ${result.code}`);
    }
  }
  assert.equal(hash(await readFile(rulesPath, 'utf8')), hash(source));
  assert.equal(hash(await readFile(join(appRoot, 'src', 'rules.mjs'), 'utf8')), hash(source), 'Released source changed during replay');
  report.result = 'PASS';
} catch (error) {
  report.result = 'FAIL';
  report.error = error.stack;
  throw error;
} finally {
  await writeFile(join(workspace, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await rm(copy, { recursive: true, force: true });
  console.log(`Evidence: ${join(workspace, 'report.json')}`);
}
