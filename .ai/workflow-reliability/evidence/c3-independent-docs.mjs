// Independent replay of the inspected, frozen owner flow, with output isolation.
// Also prove links against an actual disposable installed-layout bundle.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { pathToFileURL } from 'node:url';
import { stageSkillBundle } from '../../../evals/agent/workspace.mjs';

const output = resolve('.ai/workflow-reliability/evidence');
const helper = join(output, 'c3-integration-docs.mjs');
const original = await readFile(helper, 'utf8');
const ownerHash = createHash('sha256').update(await readFile(helper)).digest('hex');
assert.equal(ownerHash, '56e4df111c29845fc918678706e624b6e0047b3893abd88bb813362ef76973b1');
assert.ok(!(await readdir(output)).some(n => /^c3-independent-(?:docs\.json|.*\.png|bundle\.json|browser-help\.json)$/.test(n)),
  'Independent outputs already exist; preserve them, use a new owned tag for a retry');
const python = process.env.BULLETPROOF_PYTHON;
assert.ok(python);
const cli = process.env.C3_AGENT_BROWSER ??
  'C:/Users/shbs/AppData/Local/npm-cache/_npx/6de2aa2fded2970c/node_modules/agent-browser/bin/agent-browser-win32-x64.exe';
const helperRoot = process.env.C3_DOC_HELPERS ??
  'C:/Users/shbs/.copilot/session-state/c154cbfc-3b1d-4163-b8dd-5f0b43af3095/files/workflow-reliability';
const { marked } = await import(pathToFileURL(join(helperRoot, 'doc-tools/node_modules/marked/lib/marked.esm.js')));
const help = [];
for (const args of [['--help'], ['set', '--help'], ['screenshot', '--help']]) {
  const argv = ['-B', resolve('scripts/run.py'), '--idle', '30', '--max', '60', '--', cli, ...args];
  const child = spawn(python, argv, { stdio: ['ignore', 'pipe', 'pipe'] });
  let stdout = '', stderr = '';
  child.stdout.on('data', value => { stdout += value; });
  child.stderr.on('data', value => { stderr += value; });
  const code = await new Promise((done, reject) => {
    child.once('error', reject); child.once('close', done);
  });
  help.push({ argv, code, stdout, stderr });
  console.log(`Inspected agent-browser ${args.join(' ')} (${code})`);
  assert.equal(code, 0, stdout + stderr);
}
await writeFile(join(output, 'c3-independent-browser-help.json'),
  JSON.stringify(help, null, 2) + '\n', { flag: 'wx' });

const scratch = await mkdtemp(join(tmpdir(), 'c3i-b-'));
const bundleRecord = { owner_helper_sha256: ownerHash, files: [], links: [],
  limitation: 'Disposable existing stageSkillBundle invocation; no host installation or download.' };
try {
  const bundle = stageSkillBundle(process.cwd(), scratch);
  const seal = JSON.parse(await readFile(join(output, 'c3-integration-seal.json'), 'utf8'));
  const scoped = Object.keys(seal.owned).filter(name => name === 'SKILL.md' || name.startsWith('references/'));
  const slug = text => text.toLowerCase().replace(/<[^>]*>/g, '')
    .replace(/[^\p{L}\p{N}_\-\s]/gu, '').replace(/\s/g, '-');
  for (const relative of scoped) {
    const file = join(bundle, relative), bytes = await readFile(file), links = [];
    const sha256 = createHash('sha256').update(bytes).digest('hex');
    assert.equal(sha256, seal.owned[relative]);
    bundleRecord.files.push({ relative, sha256 });
    marked.walkTokens(marked.lexer(bytes.toString('utf8')), token => {
      if (token.type === 'link' || token.type === 'image') links.push(token.href);
      if (token.type === 'html') {
        for (const match of token.text.matchAll(/(?:href|src)="([^"]+)"/g)) links.push(match[1]);
      }
    });
    for (const link of new Set(links)) {
      if (/^[a-z]+:/i.test(link)) continue;
      const [part, anchor] = link.split('#');
      const target = part ? resolve(dirname(file), decodeURIComponent(part)) : file;
      assert.ok(target.startsWith(bundle), `Unbundled link: ${relative}: ${link}`);
      const info = await stat(target);
      if (anchor && info.isFile() && target.endsWith('.md')) {
        const headings = marked.lexer(await readFile(target, 'utf8'))
          .filter(t => t.type === 'heading').map(t => slug(t.text));
        assert.ok(headings.includes(decodeURIComponent(anchor)), `${relative}: ${link}`);
      }
      bundleRecord.links.push({ relative, link, target });
    }
    console.log(`Checked installed-bundle links: ${relative}`);
  }
  // Verify real payload dependencies, beyond just Markdown link existence.
  for (const part of ['scripts/workflow.py', 'scripts/workflow_state.py',
    'scripts/workflow_gate.py', 'scripts/evidence.py', 'scripts/mutate.py',
    'scripts/run.py', 'scripts/native_result.mjs', 'assets/artifact.css', 'assets/artifact.js']) {
    assert.deepEqual(await readFile(join(bundle, part)), await readFile(resolve(part)));
    bundleRecord.files.push({ relative: part, sha256: createHash('sha256')
      .update(await readFile(join(bundle, part))).digest('hex') });
  }
  bundleRecord.passed = true;
} catch (error) {
  bundleRecord.passed = false;
  bundleRecord.failure = String(error.stack ?? error);
  throw error;
} finally {
  await rm(scratch, { recursive: true, force: true });
  bundleRecord.cleanup = 'Only newly owned staged bundle removed; old trees untouched';
  await writeFile(join(output, 'c3-independent-bundle.json'),
    JSON.stringify(bundleRecord, null, 2) + '\n', { flag: 'wx' });
}
// Reuse every owner assertion unchanged. These exact substitutions only isolate
// output/session/temp identity and honor this invocation's timeout bounds.
const substitutions = [
  ['const prefix = `c3-integration${tag}`;', 'const prefix = `c3-independent${tag}`;'],
  ["'c3-doc-'", "'c3i-doc-'"],
  ['`c3-doc-${randomUUID()}`', '`c3i-doc-${randomUUID()}`'],
  ["'--idle', '30', '--max', '60'", "'--idle', '120', '--max', '1800'"],
];
let source = original;
for (const [from, to] of substitutions) {
  assert.equal(source.split(from).length, 2, `Expected one inspected replacement: ${from}`);
  source = source.replace(from, to);
}
await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
