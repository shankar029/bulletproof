import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createHash, randomUUID } from 'node:crypto';
import { access, appendFile, cp, mkdir, readFile, readdir, rename, writeFile } from 'node:fs/promises';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import http from 'node:http';

const root = resolve(import.meta.dirname, '..');
const repo = resolve(root, '..', '..');
const args = process.argv.slice(2);
if (args.length !== 2 || args[0] !== '--flow' || !['base', 'graph', 'query', 'migration', 'archive', 'all'].includes(args[1])) {
  throw new Error('Usage: node scripts\\e2e.mjs --flow base|graph|query|migration|archive|all');
}
const python = process.env.E2E_PYTHON;
if (!python) throw new Error('Set E2E_PYTHON to an installed Python 3 executable for the bounded command runner.');
const runId = `e2e-${new Date().toISOString().replaceAll(/[:.]/g, '-')}-${randomUUID().slice(0, 8)}`;
const output = join(root, '.work', runId);
const downloads = join(output, 'downloads');
await mkdir(output, { recursive: true });
const report = { runId, started: new Date().toISOString(), command: [process.execPath, ...process.argv.slice(1)], cwd: process.cwd(),
  output, browserTransport: 'agent-browser 0.37.1 owned Chromium launch, actions and assertions; Playwright resolves the installed executable only',
  processClose: 'Real main.mjs child; test-only IPC bridge emits installed SIGTERM handler (not native Windows Ctrl+C)',
  flows: [], findings: [], checks: [], lifecycle: [], sourceHashes: {} };
report.runnerSha256 = createHash('sha256').update(await readFile(import.meta.filename)).digest('hex');
for (const directory of ['src', 'public']) {
  for (const name of await readdir(join(root, directory))) {
    report.sourceHashes[`${directory}/${name}`] = createHash('sha256').update(await readFile(join(root, directory, name))).digest('hex');
  }
}
const active = new Set();
let cli, currentFlow, browserStarted = false;
const session = runId;
let commandNumber = 0;

async function command(executable, argv, { timeout = 30000, cwd = root, input } = {}) {
  const entry = { number: ++commandNumber, time: new Date().toISOString(), executable, args: argv, cwd, flow: currentFlow?.name };
  const wrapperArgs = [join(repo, 'scripts', 'run.py'), '--idle', '25', '--max', String(timeout / 1000), '--', executable, ...argv];
  Object.assign(entry, { wrapper: python, wrapperArgs });
  console.log(`COMMAND ${entry.number} ${currentFlow?.name ?? 'setup'} ${argv.includes('eval') ? 'eval' : argv.slice(-3).join(' ')}`);
  const child = spawn(python, wrapperArgs, { cwd, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, AGENT_BROWSER_DEFAULT_TIMEOUT: '12000', AGENT_BROWSER_IDLE_TIMEOUT_MS: '90000',
      AGENT_BROWSER_DOWNLOAD_PATH: downloads } });
  active.add(child);
  let stdout = '', stderr = '', timedOut = false;
  child.stdout.on('data', data => { stdout += data; });
  child.stderr.on('data', data => { stderr += data; });
  child.stdin.end(input);
  try {
    // The bounded runner owns the deadline and child-tree cleanup; do not race it.
    const [exitCode, signal] = await once(child, 'exit');
    timedOut = exitCode === 124 || exitCode === 125;
    await new Promise(resolve => setTimeout(resolve, 20));
    Object.assign(entry, { exitCode, signal });
    assert.equal(timedOut, false, `Command timed out: ${argv.join(' ')}`);
    assert.equal(exitCode, 0, `${argv.join(' ')}\n${stderr}\n${stdout}`);
    return stdout;
  } finally {
    Object.assign(entry, { timedOut, stdout, stderr });
    await appendFile(join(output, 'commands.jsonl'), JSON.stringify(entry) + '\n');
    child.stdout.destroy();
    child.stderr.destroy();
    if (child.exitCode !== null || child.signalCode !== null) active.delete(child);
  }
}

async function discoverCli() {
  const binaries = process.platform === 'win32' ? [...new Set([`agent-browser-win32-${process.arch}.exe`, 'agent-browser-win32-x64.exe'])] : [`agent-browser-${process.platform}-${process.arch}`];
  const candidates = process.env.AGENT_BROWSER_BIN ? [process.env.AGENT_BROWSER_BIN] : [];
  const cache = process.env.npm_config_cache ?? (process.platform === 'win32' ? join(process.env.LOCALAPPDATA, 'npm-cache') : join(homedir(), '.npm'));
  for (const dir of await readdir(join(cache, '_npx')).catch(() => [])) for (const binary of binaries) candidates.push(join(cache, '_npx', dir, 'node_modules', 'agent-browser', 'bin', binary));
  for (const candidate of candidates) {
    const metadata = JSON.parse(await readFile(join(dirname(candidate), '..', 'package.json'), 'utf8').catch(() => '{}'));
    if (metadata.name === 'agent-browser' && metadata.version === '0.37.1' && await access(candidate).then(() => true, () => false)) return candidate;
  }
  throw new Error('Missing agent-browser@0.37.1. From repository root run npm exec --yes --package=agent-browser@0.37.1 -- agent-browser --version (see README).');
}

async function browser(...argv) {
  const text = await command(cli, ['--session', session, '--json', ...argv]);
  const result = JSON.parse(text);
  assert.equal(result.success, true, JSON.stringify(result));
  return result.data;
}
async function evaluate(expression) {
  const result = await browser('eval', '-b', Buffer.from(expression).toString('base64'));
  return result.result;
}
async function ready() {
  await browser('wait', '--fn', "document.querySelector('#main')?.getAttribute('aria-busy') === 'false' && document.querySelector('#notice')?.textContent !== 'Loading…'");
}
async function open(path = '/') {
  await browser('open', currentFlow.app.url + path);
  await ready();
}
async function click(selector) {
  await browser('scrollintoview', selector);
  await browser('click', selector);
}
async function buttonNamed(name) {
  const selector = await evaluate(`(() => {
    let el = [...document.querySelectorAll('button')].find(el => el.textContent === ${JSON.stringify(name)});
    if (!el) throw new Error('Missing button');
    const path = [];
    while (el && el !== document.documentElement) {
      path.unshift(el.tagName.toLowerCase() + ':nth-child(' + ([...el.parentElement.children].indexOf(el) + 1) + ')');
      el = el.parentElement;
    }
    return 'html > ' + path.join(' > ');
  })()`);
  await browser('scrollintoview', selector);
  await browser('find', 'role', 'button', 'click', '--name', name, '--exact');
}
async function fill(selector, text) { await browser('fill', selector, text); }
async function select(selector, value) { await browser('select', selector, value); }
async function check(name, ac, actual, expected) {
  assert.deepEqual(actual, expected, name);
  report.checks.push({ flow: currentFlow.name, name, ac, status: 'VERIFIED', actual });
  console.log(`PASS ${currentFlow.name}: ${name}`);
}
async function visibleText(selector) { return evaluate(`document.querySelector(${JSON.stringify(selector)})?.textContent`); }
async function contains(selector, expected, name, ac) {
  const text = await visibleText(selector);
  assert.ok(text?.includes(expected), `${name}: expected ${JSON.stringify(expected)} in ${JSON.stringify(text)}`);
  report.checks.push({ flow: currentFlow.name, name, ac, status: 'VERIFIED', actual: text });
}
async function capture(name) {
  const prefix = `${currentFlow.name}-${name}`;
  await browser('screenshot', join(output, `${prefix}.png`), '--full');
  const snapshot = await browser('snapshot');
  await writeFile(join(output, `${prefix}-snapshot.json`), JSON.stringify(snapshot, null, 2));
}
async function saved() {
  await browser('wait', '--fn', "document.querySelector('#notice').textContent === 'Task saved' || !document.querySelector('#error').hidden");
  await check('Task save success announcement', ['AC02', 'AC07'], await visibleText('#notice'), 'Task saved');
}
async function createProject(name) {
  await fill('#project-name', name);
  await click('#project-form button');
  await browser('wait', '--text', 'Project created');
  await ready();
  return new URL(await evaluate('location.href')).searchParams.get('projectId');
}
async function keyboardUntil(expression, name, limit = 24) {
  for (let i = 0; i < limit; i++) {
    if (await evaluate(expression)) return;
    await browser('press', 'Tab');
  }
  assert.fail(`Keyboard cannot reach ${name} in ${limit} Tab presses`);
}
async function addTask(title, description = '') {
  await click('#add-task');
  await fill('#editor-title', title);
  await fill('#editor-description', description);
  await click('#editor button[type=submit]');
  await saved();
}
async function editTask(id) { await click(`article[data-task-id="${id}"] button`); }
async function setStatus(id, status, success = true) {
  await editTask(id);
  await select('#editor-status', status);
  await click('#editor button[type=submit]');
  if (success) await saved();
  else await browser('wait', '#error');
}
async function request(path, options = {}) {
  const response = await fetch(currentFlow.app.url + path, { ...options, signal: AbortSignal.timeout(5000) });
  const text = await response.text();
  let body;
  try { body = JSON.parse(text); } catch { body = text; }
  const result = { status: response.status, body, etag: response.headers.get('etag') };
  await appendFile(join(output, 'http.jsonl'), JSON.stringify({ flow: currentFlow.name, path, options, ...result }) + '\n');
  return result;
}
async function get(path) {
  const response = await request(path);
  assert.equal(response.status, 200, JSON.stringify(response));
  return response.body;
}
async function write(path, body, method = 'POST', expectedStatus = method === 'POST' ? 201 : 200, revision) {
  revision ??= (await get('/api/health')).revision;
  const result = await request(path, { method, headers: { 'Content-Type': 'application/json', 'If-Match': `"${revision}"` }, body: JSON.stringify(body) });
  assert.equal(result.status, expectedStatus, JSON.stringify(result));
  return result.body;
}
async function startApp(directory) {
  await mkdir(directory, { recursive: true });
  const child = spawn(process.execPath, ['--import', pathToFileURL(join(root, 'test', 'signal-bridge.mjs')).href,
    join(root, 'src', 'main.mjs'), '--data-dir', directory, '--port', '0'], { cwd: root, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
  active.add(child);
  const record = { flow: currentFlow.name, pid: child.pid, directory, start: new Date().toISOString(), stdout: '', stderr: '' };
  report.lifecycle.push(record);
  child.stdout.on('data', data => { record.stdout += data; });
  child.stderr.on('data', data => { record.stderr += data; });
  const app = { child, record, directory };
  currentFlow.app = app;
  const deadline = Date.now() + 12000;
  while (!record.stdout.includes('\n') && child.exitCode === null && Date.now() < deadline) await new Promise(resolve => setTimeout(resolve, 50));
  assert.ok(record.stdout.includes('\n'), `App failed startup: ${record.stderr}`);
  const address = JSON.parse(record.stdout.split('\n')[0]);
  assert.equal(address.pid, child.pid);
  app.url = address.url;
  record.url = app.url;
  const response = await fetch(app.url + '/api/health', { signal: AbortSignal.timeout(5000) });
  assert.equal(response.status, 200);
  return app;
}
async function stopApp(app = currentFlow.app) {
  if (!app || app.child.exitCode !== null) return;
  const exit = once(app.child, 'exit', { signal: AbortSignal.timeout(15000) });
  app.child.send('exercise installed graceful signal handler');
  app.child.disconnect();
  const [code] = await exit;
  active.delete(app.child);
  app.record.exitCode = code;
  app.record.stopped = new Date().toISOString();
  assert.equal(code, 0, app.record.stderr);
  assert.equal(await readFile(join(app.directory, 'writer.lock')).then(() => true, error => error.code !== 'ENOENT'), false, 'Graceful close must release owned lock');
  await assert.rejects(fetch(app.url + '/api/health', { signal: AbortSignal.timeout(1000) }), 'Old listener must really be stopped');
}
async function restart() {
  const previous = currentFlow.app;
  await stopApp(previous);
  await startApp(previous.directory);
  assert.notEqual(currentFlow.app.child.pid, previous.child.pid, 'Restart must create a different process');
}
async function audit(name) {
  const tree = await browser('snapshot');
  await writeFile(join(output, `${currentFlow.name}-${name}-landmarks.json`), JSON.stringify(tree, null, 2));
  await check(`${name} Pagination is a named navigation landmark`, ['AC07'],
    typeof tree.snapshot === 'string' && /navigation "Pagination"/.test(tree.snapshot), true);
  const result = await browser('a11y');
  await writeFile(join(output, `${currentFlow.name}-${name}-a11y.json`), JSON.stringify(result, null, 2));
  assert.equal(result.axeVersion, '4.12.1', 'Reassess audit expectations if bundled axe changes');
  assert.equal(result.counts?.violations, 0, 'Accessibility violation count must be present and zero');
  await check(`${name} axe automated violations (not full WCAG or human approval)`, ['AC07'], result.violations, []);
  for (const item of result.incomplete) report.findings.push({ id: `AXE-${item.id}`, ac: ['AC07'], flow: currentFlow.name,
    severity: 'manual-review', detail: item, evidence: `${currentFlow.name}-${name}-a11y.json` });
  assert.equal(result.counts?.incomplete, 0, 'Accessibility incomplete count must be present and zero');
  await check(`${name} axe has no unresolved incomplete checks on tested page`, ['AC07'], result.incomplete, []);
}
async function layout(width) {
  await browser('set', 'viewport', String(width), '900');
  const result = await evaluate(`(() => {
    const visible = el => !!(el.getClientRects().length);
    const controls = [...document.querySelectorAll('button,a,input,select,textarea')].filter(visible).map(el => {
      const target = el.type === 'checkbox' ? el.closest('label') : el;
      const rect = target.getBoundingClientRect();
      return {tag:el.tagName, text:el.textContent.trim().slice(0,70), id:el.id, width:rect.width, height:rect.height};
    });
    return { width:innerWidth, scrollWidth:document.documentElement.scrollWidth, controls,
      unlabeled:[...document.querySelectorAll('input,select,textarea')].filter(visible).filter(el => !el.labels?.length && !el.getAttribute('aria-label')).map(el => el.id) };
  })()`);
  await writeFile(join(output, `${currentFlow.name}-layout-${width}.json`), JSON.stringify(result, null, 2));
  await check(`${width}px no horizontal page overflow`, ['AC07'], result.scrollWidth <= width, true);
  await check(`${width}px labeled form controls`, ['AC07'], result.unlabeled, []);
  await check(`${width}px interactive targets at least 44px`, ['AC07'], result.controls.filter(control => control.width < 44 || control.height < 44), []);
  await capture(`layout-${width}`);
}
async function base() {
  async function lifecycleGuidance(name, editing) {
    await check(name, ['AC5', 'R4'], await evaluate(`(() => {
      const guidance = document.querySelector('#lifecycle-guidance');
      const lifecycle = document.querySelector('#project-lifecycle');
      return {
        editorExists: !!document.querySelector('#editor'),
        visible: !!guidance?.getClientRects().length && getComputedStyle(guidance).visibility === 'visible',
        hidden: guidance?.hidden,
        text: guidance?.textContent,
        describedBy: lifecycle?.getAttribute('aria-describedby'),
        disabled: lifecycle?.disabled
      };
    })()`), {
      editorExists: editing, visible: editing, hidden: !editing,
      text: 'Finish or cancel your draft before changing project state.',
      describedBy: 'lifecycle-guidance', disabled: editing,
    });
  }
  await check('Fresh HTTP health', ['AC01'], await get('/api/health'), { status: 'ok', schemaVersion: 2, revision: 0 });
  await open();
  await contains('#projects', 'No active projects.', 'Fresh browser empty state', ['AC01', 'AC07']);
  await check('Initial empty Projects live announcement', ['AC07'], await visibleText('#notice'), 'No active projects. Create a project or view Archived projects.');
  await check('Loading completion uses the polite status region', ['AC07'],
    await evaluate("({role:document.querySelector('#notice').getAttribute('role'),live:document.querySelector('#notice').getAttribute('aria-live')})"),
    { role: 'status', live: 'polite' });
  await capture('empty');
  await keyboardUntil("document.activeElement.id === 'project-name'", 'Project name');
  await browser('keyboard', 'type', 'Launch');
  await browser('press', 'Enter');
  await browser('wait', '--text', 'Project created');
  await ready();
  await check('Project save success overrides loaded empty status', ['AC02', 'AC07'], await visibleText('#notice'), 'Project created');
  const projectId = new URL(await evaluate('location.href')).searchParams.get('projectId');
  await browser('reload');
  await ready();
  await check('Selected empty project announces no tasks after reload', ['AC07'], await visibleText('#notice'), 'No tasks yet. Add your first task.');
  await lifecycleGuidance('Lifecycle guidance initially hidden; lifecycle enabled', false);
  await keyboardUntil("document.activeElement.id === 'add-task'", 'Add task');
  await browser('press', 'Enter');
  await check('Keyboard-only project creation and Add task navigation', ['AC07'], await evaluate('document.activeElement.id'), 'editor-title');
  await browser('keyboard', 'type', 'Draft');
  await browser('press', 'Tab');
  await browser('keyboard', 'type', 'Original description');
  await keyboardUntil("document.activeElement.textContent === 'Save task'", 'Save task');
  await browser('press', 'Enter');
  await saved();
  await addTask('Review', 'Review description');
  const tasks = (await get(`/api/tasks?projectId=${projectId}`)).items;
  const draft = tasks.find(task => task.title === 'Draft');
  const review = tasks.find(task => task.title === 'Review');
  assert.ok(draft && review);
  await editTask(draft.id);
  await lifecycleGuidance('Editing reveals associated guidance and disables lifecycle', true);
  await fill('#editor-title', 'Uncommitted guidance draft');
  await click('#editor button[type=button]');
  await lifecycleGuidance('Cancel hides guidance and re-enables lifecycle', false);
  await editTask(draft.id);
  await check('Cancel discards guidance-test draft', ['AC5', 'R4'], await evaluate("document.querySelector('#editor-title').value"), 'Draft');
  await lifecycleGuidance('Reopening editor restores guidance and lifecycle fence', true);
  await fill('#editor-title', '');
  await click('#editor button[type=submit]');
  await browser('wait', '#error');
  await check('Invalid title retains editor and blank input', ['AC02'], await evaluate("document.querySelector('#editor-title').value"), '');
  await check('Validation focuses announced alert', ['AC07', 'AC08'], await evaluate("document.activeElement.id === 'error' && document.activeElement.getAttribute('role') === 'alert'"), true);
  await capture('invalid-title');
  await fill('#editor-title', 'Draft revised');
  await fill('#editor-description', 'Edited description');
  await click('#editor button[type=submit]');
  await saved();
  await lifecycleGuidance('Save hides guidance and re-enables lifecycle', false);
  await browser('reload');
  await ready();
  await contains(`article[data-task-id="${draft.id}"]`, 'Draft revised', 'Title survives browser refresh', ['AC02', 'AC07']);
  await restart();
  await open(`/?projectId=${projectId}`);
  await contains(`article[data-task-id="${draft.id}"]`, 'Edited description', 'Description survives full process restart', ['AC02', 'AC07']);
  await check('HTTP full restart title/description', ['AC02'], (await get(`/api/tasks?projectId=${projectId}`)).items.map(t => [t.title, t.description]), [['Draft revised', 'Edited description'], ['Review', 'Review description']]);
  await editTask(draft.id);
  await fill('#editor-title', 'Retained conflict draft');
  await write(`/api/tasks/${review.id}`, { description: 'Concurrent owner write' }, 'PATCH');
  const beforeConflict = await readFile(join(currentFlow.directory, 'planner.json'), 'utf8');
  await click('#editor button[type=submit]');
  await browser('wait', '#error');
  await contains('#error', 'Reload', 'Conflict offers explicit reload', ['AC03', 'AC08']);
  await check('Conflict retains draft', ['AC08'], await evaluate("document.querySelector('#editor-title').value"), 'Retained conflict draft');
  await check('Rejected conflict preserves bytes', ['AC03'], await readFile(join(currentFlow.directory, 'planner.json'), 'utf8'), beforeConflict);
  await capture('conflict');
  await click('#reload');
  await ready();
  await check('Explicit reload discards draft', ['AC08'], await evaluate("document.querySelector('#editor') === null"), true);
  await contains(`article[data-task-id="${draft.id}"]`, 'Draft revised', 'Explicit reload restores committed text', ['AC08']);
  const scriptTitle = '<script>window.__plannerInjected = true</script>';
  await addTask(scriptTitle);
  await check('Script-like title is text, never executable', ['AC08'], await evaluate("({injected:window.__plannerInjected === true, scripts:[...document.querySelectorAll('article script')].length, text:[...document.querySelectorAll('article h3')].map(el=>el.textContent)})"),
    { injected: false, scripts: 0, text: ['Draft revised', 'Review', scriptTitle] });
  await click('#add-task');
  await check('Editor receives keyboard focus', ['AC07'], await evaluate('document.activeElement.id'), 'editor-title');
  await browser('keyboard', 'type', 'Keyboard cancelled draft');
  await browser('press', 'Tab');
  await check('Tab reaches labeled description', ['AC07'], await evaluate('document.activeElement.id'), 'editor-description');
  const focus = await evaluate("({style:getComputedStyle(document.activeElement).outlineStyle,width:getComputedStyle(document.activeElement).outlineWidth})");
  assert.notEqual(focus.style, 'none');
  assert.ok(parseFloat(focus.width) >= 2);
  for (let i = 0; i < 6; i++) {
    if (await evaluate("document.activeElement.textContent === 'Cancel'")) break;
    await browser('press', 'Tab');
  }
  await check('Keyboard reaches Cancel', ['AC07'], await evaluate('document.activeElement.textContent'), 'Cancel');
  await browser('press', 'Enter');
  await check('Keyboard cancel restores Add task focus', ['AC07'], await evaluate('document.activeElement.id'), 'add-task');
  await check('Cancelled draft never persisted', ['AC02', 'AC07'], (await get('/api/tasks')).total, 3);
  await click('#add-task');
  await layout(390);
  await layout(1280);
  await audit('editor');
  await click('#editor button[type=button]');
  await boundaries(projectId);
  await capture('complete');
  currentFlow.successfulJourneyConsole = await browser('console');
  currentFlow.successfulJourneyErrors = await browser('errors');
  await check('Successful base journey has no uncaught browser exceptions', ['AC07'], currentFlow.successfulJourneyErrors.errors, []);
  await check('Successful base journey CLI console is clean', ['AC07'], currentFlow.successfulJourneyConsole.messages, []);
  await browser('set', 'offline', 'on');
  try {
    await click('#reload');
    await browser('wait', '#error');
    await contains('#error', 'Reload latest', 'Network failure offers read recovery', ['AC08']);
    await check('Network failure is not success-shaped', ['AC08'], await visibleText('#notice'), '');
    await capture('network-failure');
  } finally { await browser('set', 'offline', 'off'); }
  await click('#reload');
  await ready();
  await contains('#main', 'Draft revised', 'UI recovers after network failure', ['AC08']);
}

async function boundaries(projectId) {
  const revision = (await get('/api/health')).revision;
  const before = await readFile(join(currentFlow.directory, 'planner.json'), 'utf8');
  const normal = { 'Content-Type': 'application/json', 'If-Match': `"${revision}"` };
  for (const [name, path, options, status, code] of [
    ['missing revision', '/api/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }, 428, 'PRECONDITION_REQUIRED'],
    ['malformed revision', '/api/projects', { method: 'POST', headers: { ...normal, 'If-Match': '1' }, body: '{}' }, 400, 'INVALID_REVISION'],
    ['malformed JSON', '/api/projects', { method: 'POST', headers: normal, body: '{' }, 400, 'BAD_JSON'],
    ['wrong media type', '/api/projects', { method: 'POST', headers: { ...normal, 'Content-Type': 'text/plain' }, body: '{}' }, 415, 'UNSUPPORTED_MEDIA_TYPE'],
    ['oversized body', '/api/projects', { method: 'POST', headers: normal, body: JSON.stringify({ name: 'x'.repeat(66000) }) }, 413, 'BODY_TOO_LARGE'],
    ['duplicate project', '/api/projects', { method: 'POST', headers: normal, body: '{"name":"Launch"}' }, 409, 'DUPLICATE_PROJECT'],
    ['blank name', '/api/projects', { method: 'POST', headers: normal, body: '{"name":" "}' }, 400, 'INVALID_INPUT'],
    ['oversize title', '/api/tasks', { method: 'POST', headers: normal, body: JSON.stringify({ projectId, title: 'x'.repeat(161) }) }, 400, 'INVALID_INPUT'],
    ['wrong title type', '/api/tasks', { method: 'POST', headers: normal, body: JSON.stringify({ projectId, title: 42 }) }, 400, 'INVALID_INPUT'],
    ['unknown field', '/api/tasks', { method: 'POST', headers: normal, body: JSON.stringify({ projectId, title: 'Wrong', unexpected: true }) }, 400, 'INVALID_INPUT'],
    ['unknown task', '/api/tasks/t-999', { method: 'PATCH', headers: normal, body: '{"title":"Missing"}' }, 404, 'NOT_FOUND'],
    ['unknown route', '/api/missing', {}, 404, 'NOT_FOUND'],
    ['wrong method', '/api/health', { method: 'DELETE' }, 405, 'METHOD_NOT_ALLOWED'],
    ['foreign Origin', '/api/health', { headers: { Origin: 'https://example.invalid' } }, 403, 'FORBIDDEN_ORIGIN'],
    ['non-allowlisted data path', '/planner.json', {}, 404, 'NOT_FOUND'],
    ['encoded traversal', '/%2e%2e%2fplanner.json', {}, 404, 'NOT_FOUND'],
  ]) {
    const response = await request(path, options);
    await check(`HTTP ${name}`, ['AC02', 'AC08'], [response.status, response.body.error?.code], [status, code]);
    assert.ok(!JSON.stringify(response.body).includes(currentFlow.directory), 'Errors must not disclose the data directory');
  }
  const badHost = await new Promise((resolveResult, reject) => {
    const req = http.get(currentFlow.app.url + '/api/health', { headers: { Host: 'example.invalid' }, timeout: 5000 }, res => {
      let text = ''; res.on('data', data => { text += data; }); res.on('end', () => resolveResult({ status: res.statusCode, body: JSON.parse(text) }));
    });
    req.on('error', reject); req.on('timeout', () => req.destroy(new Error('Host check timeout')));
  });
  await check('Foreign Host is rejected', ['AC08'], [badHost.status, badHost.body.error.code], [403, 'FORBIDDEN_ORIGIN']);
  await check('All invalid HTTP writes leave exact bytes unchanged', ['AC02', 'AC03', 'AC08'], await readFile(join(currentFlow.directory, 'planner.json'), 'utf8'), before);
  const concurrent = await Promise.all(['Concurrent A', 'Concurrent B'].map(title => request('/api/tasks', { method: 'POST', headers: normal, body: JSON.stringify({ projectId, title }) })));
  await check('Same-revision concurrent writes yield one success and one conflict', ['AC03'], concurrent.map(r => r.status).sort(), [201, 409]);
  await check('Concurrent write conflict is explicit', ['AC03'], concurrent.find(r => r.status === 409).body.error.code, 'REVISION_CONFLICT');
}

async function graph() {
  await open();
  const projectId = await createProject('Launch');
  await addTask('Draft');
  await addTask('Review');
  const [draft, review] = (await get('/api/tasks')).items;
  await editTask(review.id);
  await browser('check', `#editor input[value="${draft.id}"]`);
  await click('#editor button[type=submit]');
  await saved();
  await contains(`article[data-task-id="${review.id}"]`, 'blocked (todo)', 'Dependency renders blocked status', ['AC04', 'AC07']);
  await setStatus(review.id, 'in_progress', false);
  await contains('#error', 'Complete dependencies', 'Blocked transition explains required action', ['AC04', 'AC07']);
  await check('Rejected transition retains status draft', ['AC04'], await evaluate("document.querySelector('#editor-status').value"), 'in_progress');
  await capture('blocked-transition');
  await click('#editor button[type=button]');
  await setStatus(draft.id, 'done');
  await setStatus(review.id, 'in_progress');
  await setStatus(review.id, 'done');
  await contains('.summary', 'Completion %: 100', 'Completed dependency chain updates dashboard', ['AC04', 'AC06']);
  await setStatus(draft.id, 'todo', false);
  await contains('#error', 'Reopen', 'Reopen predecessor rejected with actionable error', ['AC04']);
  await capture('reopen-conflict');
  await click('#editor button[type=button]');
  await setStatus(review.id, 'todo');
  await setStatus(draft.id, 'todo');
  const revision = (await get('/api/health')).revision;
  const other = (await write('/api/projects', { name: 'Other' })).project;
  const otherTask = (await write('/api/tasks', { projectId: other.id, title: 'Other project task' })).task;
  for (const [dependencyIds, code, status] of [
    [[draft.id], 'INVALID_INPUT', 400], [['t-999'], 'INVALID_INPUT', 400],
    [[review.id, review.id], 'INVALID_INPUT', 400], [[otherTask.id], 'INVALID_INPUT', 400], [[review.id], 'DEPENDENCY_CYCLE', 409],
  ]) {
    const result = await write(`/api/tasks/${draft.id}`, { dependencyIds }, 'PATCH', status);
    await check(`Rejected dependency ${JSON.stringify(dependencyIds)}`, ['AC04'], result.error.code, code);
  }
  await restart();
  await open(`/?projectId=${projectId}`);
  await contains(`article[data-task-id="${review.id}"]`, 'blocked (todo)', 'Dependency survives restart', ['AC04']);
  await check('Graph no illegal transition committed', ['AC04'], (await get(`/api/tasks?projectId=${projectId}`)).items.map(t => [t.title, t.status, t.dependencyIds]), [['Draft', 'todo', []], ['Review', 'todo', [draft.id]]]);
  assert.ok(revision > 0);
  await capture('complete');
}

async function query() {
  const alpha = (await write('/api/projects', { name: 'Alpha' })).project;
  const beta = (await write('/api/projects', { name: 'Beta' })).project;
  const emptySummary = await get(`/api/dashboard?projectId=${alpha.id}`);
  delete emptySummary.revision;
  await check('Empty project dashboard is independently all zero', ['AC06'], emptySummary,
    { total: 0, todo: 0, inProgress: 0, done: 0, blocked: 0, completionPercent: 0 });
  const titles = ['Archive brief', 'Build outline', 'Check links', 'Draft launch', 'Edit launch', 'Finalize launch'];
  const tasks = [];
  for (const title of titles) tasks.push((await write('/api/tasks', { projectId: alpha.id, title, dependencyIds: title === 'Edit launch' ? [tasks[1].id] : [] })).task);
  await write(`/api/tasks/${tasks[0].id}`, { status: 'done' }, 'PATCH');
  await write(`/api/tasks/${tasks[2].id}`, { status: 'in_progress' }, 'PATCH');
  await write('/api/tasks', { projectId: beta.id, title: 'Gather launch' });
  const expected = { total: 6, todo: 4, inProgress: 1, done: 1, blocked: 1, completionPercent: 16 };
  const summary = await get(`/api/dashboard?projectId=${alpha.id}`);
  delete summary.revision;
  await check('Independent F-query Alpha dashboard', ['AC06'], summary, expected);
  for (const [suffix, ids, total, pages] of [
    ['status=todo&page=1&pageSize=2', [tasks[1].id, tasks[3].id], 4, 2],
    ['status=todo&page=2&pageSize=2', [tasks[4].id, tasks[5].id], 4, 2],
    ['status=todo&q=%20LAUNCH%20&page=1&pageSize=2', [tasks[3].id, tasks[4].id], 3, 2],
    ['status=todo&q=launch&page=2&pageSize=2', [tasks[5].id], 3, 2],
    ['status=todo&page=3&pageSize=2', [], 4, 2],
    ['q=unmatched', [], 0, 0],
  ]) {
    const result = await get(`/api/tasks?projectId=${alpha.id}&${suffix}`);
    await check(`Independent HTTP query ${suffix}`, ['AC05'], [result.items.map(t => t.id), result.total, result.totalPages], [ids, total, pages]);
  }
  await open(`/?projectId=${alpha.id}`);
  await select('#filter-pageSize', '2');
  await ready();
  await select('#filter-status', 'todo');
  await click('.filters button[type=submit]');
  await ready();
  const ids = () => evaluate("[...document.querySelectorAll('article')].map(el=>el.dataset.taskId)");
  await check('Browser filtered first page B,D', ['AC05', 'AC07'], await ids(), [tasks[1].id, tasks[3].id]);
  await buttonNamed('Next');
  await ready();
  await check('Browser filtered second page E,F', ['AC05', 'AC07'], await ids(), [tasks[4].id, tasks[5].id]);
  await contains('.summary', 'Total: 6', 'Page change does not affect totals', ['AC06']);
  const deepLink = await evaluate('location.pathname + location.search');
  await capture('filtered-page2');
  await fill('#filter-q', 'launch');
  await click('.filters button[type=submit]');
  await ready();
  await check('Applying filters resets page to 1', ['AC05'], await evaluate("new URL(location.href).searchParams.get('page')"), null);
  await check('Browser AND-filter first page D,E', ['AC05'], await ids(), [tasks[3].id, tasks[4].id]);
  await browser('back');
  await ready();
  await check('Browser Back restores filtered second page', ['AC05', 'AC07'], await ids(), [tasks[4].id, tasks[5].id]);
  await browser('reload');
  await ready();
  await check('Reload preserves actual deep link state', ['AC05'], await ids(), [tasks[4].id, tasks[5].id]);
  await click('#nav-dashboard');
  await ready();
  await check('Dashboard project summary ignores filters/pages', ['AC06'], await evaluate("[...document.querySelectorAll('.summary p')].map(el=>el.textContent)"),
    ['Total: 6', 'Todo: 4', 'In progress: 1', 'Done: 1', 'Blocked: 1', 'Completion %: 16']);
  await check('Dashboard loaded status is announced', ['AC07'], await visibleText('#notice'), 'Alpha dashboard loaded. 6 tasks.');
  await buttonNamed('All projects');
  await ready();
  await contains('.summary', 'Total: 7', 'Global dashboard includes other project', ['AC06']);
  await open(deepLink);
  await fill('#filter-q', 'nothing matches');
  await click('.filters button[type=submit]');
  await ready();
  await contains('#main', 'No results.', 'No-result state rendered', ['AC05']);
  await check('Unmatched filter announces no results with recovery action', ['AC05', 'AC07'], await visibleText('#notice'), 'No results. Clear filters or return to the previous page.');
  await buttonNamed('Clear filters');
  await ready();
  await check('Clear filters restores first two records', ['AC05'], await ids(), [tasks[0].id, tasks[1].id]);
  await check('Clear filters announces loaded count and current page', ['AC07'], await visibleText('#notice'), '6 tasks loaded. Page 1 of 3.');
  for (let index = 1; index <= 7; index++) await write('/api/tasks', { projectId: alpha.id, title: `Extra ${index}` });
  await open(`/?projectId=${alpha.id}`);
  const first = await ids();
  await check('Default pageSize=10 really paginates thirteen tasks', ['AC05'], first.length, 10);
  await buttonNamed('Next');
  await ready();
  const second = await ids();
  await check('Next page contains remaining three tasks', ['AC05'], second.length, 3);
  await check('No duplicates or omissions across default-size pages', ['AC05'], new Set([...first, ...second]).size, 13);
  await capture('default-page2');
  await restart();
  await open(`/?projectId=${alpha.id}&page=2`);
  await check('Deep linked second page survives process restart', ['AC05'], await ids(), second);
  await contains('.summary', 'Total: 13', 'Restart dashboard persists all thirteen tasks', ['AC06']);
  await audit('query');
}

async function migration() {
  await open('/?projectId=p-1');
  await contains('#main', 'Legacy data is read-only.', 'Actual v1 fixture loads in browser read-only', ['AC09']);
  await check('Legacy browser disables edits', ['AC09'], await evaluate("document.querySelector('#add-task').disabled && document.querySelector('#project-name').disabled"), true);
  const original = await readFile(join(currentFlow.directory, 'planner.json'));
  await check('Genuine I3 fixture SHA-256', ['AC09'], createHash('sha256').update(original).digest('hex'), 'ad7845486864bb4fef3f938eac02ef4ba213f8d3e20da4e4fa1b1c8b61df4450');
  const rejected = await write('/api/tasks/t-7', { priority: 'high' }, 'PATCH', 409);
  await check('Legacy API refuses writes', ['AC09'], rejected.error.code, 'MIGRATION_REQUIRED');
  await scenario('legacy-download', async () => {
    const legacyCsv = await download('legacy', 'p-1');
    await check('Legacy CSV contains all six original task IDs', ['AC4', 'AC5'],
      parseCsv(legacyCsv.toString('utf8')).slice(1).map(row => row[2]), JSON.parse(original).tasks.filter(task => task.projectId === 'p-1').map(task => task.id));
    await check('Legacy download leaves original bytes unchanged', ['AC4', 'AC5'],
      (await readFile(join(currentFlow.directory, 'planner.json'))).equals(original), true);
  });
  await capture('legacy');
  await stopApp();
  const migrationArgs = [join(root, 'src', 'migrate.mjs'), '--data-dir', currentFlow.directory];
  const first = JSON.parse(await command(process.execPath, migrationArgs));
  await check('Offline migration increments revision exactly once', ['AC09'], first, { schemaVersion: 2, revision: 12, changed: true });
  const migrated = await readFile(join(currentFlow.directory, 'planner.json'));
  const legacy = JSON.parse(original);
  const independent = { ...legacy, schemaVersion: 2, revision: 12, tasks: legacy.tasks.map(({ state, ...task }) => ({ ...task, status: state, priority: 'normal' })) };
  await check('Migration preserves exact IDs/text/edges/order/nextId/status', ['AC09'], JSON.parse(migrated), independent);
  await check('Migration exact-byte original backup', ['AC09'], (await readFile(join(currentFlow.directory, 'planner.v1-backup.json'))).equals(original), true);
  await check('Repeated offline migration no-op', ['AC09'], JSON.parse(await command(process.execPath, migrationArgs)), { schemaVersion: 2, revision: 12, changed: false });
  await check('Repeated migration preserves exact bytes', ['AC09'], (await readFile(join(currentFlow.directory, 'planner.json'))).equals(migrated), true);
  await startApp(currentFlow.directory);
  await open('/?projectId=p-1');
  await editTask('t-7');
  await select('#editor-priority', 'high');
  await click('#editor button[type=submit]');
  await saved();
  await select('#filter-priority', 'high');
  await click('.filters button[type=submit]');
  await ready();
  await check('Browser high priority filter after real edit', ['AC09', 'AC05'], await evaluate("[...document.querySelectorAll('article')].map(el=>el.dataset.taskId)"), ['t-7']);
  await fill('#filter-q', ' LAUNCH ');
  await select('#filter-status', 'todo');
  await click('.filters button[type=submit]');
  await ready();
  await check('Browser project/status/normalized title/priority all combine with AND', ['AC05', 'AC09'],
    await evaluate("[...document.querySelectorAll('article')].map(el=>el.dataset.taskId)"), ['t-7']);
  await restart();
  await open('/?projectId=p-1&priority=high');
  await check('High priority filter survives full process restart', ['AC09'], await evaluate("[...document.querySelectorAll('article')].map(el=>el.dataset.taskId)"), ['t-7']);
  await contains('article[data-task-id="t-7"]', 'Priority: high', 'Migrated browser priority survives restart', ['AC09']);
  await contains('.summary', 'Completion %: 16', 'Migrated dashboard preserves independent counts', ['AC06', 'AC09']);
  await capture('priority-restart');
}

function parseCsv(csv) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < csv.length; i++) {
    const c = csv[i];
    if (quoted) {
      if (c === '"' && csv[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') quoted = false;
      else cell += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\r' && csv[i + 1] === '\n') {
      row.push(cell); rows.push(row); row = []; cell = ''; i++;
    } else assert.fail(`Invalid unquoted CSV character at ${i}`);
  }
  assert.equal(quoted, false);
  assert.equal(cell, '');
  assert.deepEqual(row, []);
  return rows;
}

async function download(label, projectId) {
  if (report.downloadBlocker) throw new Error(`Download transport BLOCKED earlier in this run: ${report.downloadBlocker}`);
  const path = join(output, `${currentFlow.name}-${label}.csv`);
  const before = new Set(await readdir(downloads));
  await browser('scrollintoview', '#download-csv');
  let result, browserPath;
  try {
    result = await browser('click', '#download-csv');
    const deadline = Date.now() + 12000;
    let created = [];
    do {
      created = (await readdir(downloads)).filter(name => !before.has(name));
      if (created.length === 1 && created[0].endsWith('.csv')) {
        browserPath = join(downloads, created[0]);
        break;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    } while (Date.now() < deadline);
    assert.ok(browserPath, `Expected one completed browser CSV; new download entries: ${JSON.stringify(created)}`);
    // Managed Chrome overwrites repeated filenames; retain the completed file
    // outside its inbox so the next download cannot reuse stale bytes.
    await rename(browserPath, path);
  } catch (error) {
    report.downloadBlocker = error.message;
    throw error;
  }
  const bytes = await readFile(path);
  await check(`${label} completed download retains its success notice`, ['AC4'],
    await visibleText('#notice'), 'CSV download started.');
  const response = await fetch(`${currentFlow.app.url}/api/projects/${projectId}/tasks.csv`, { signal: AbortSignal.timeout(5000) });
  assert.equal(response.status, 200);
  const serverBytes = Buffer.from(await response.arrayBuffer());
  await writeFile(join(output, `${currentFlow.name}-${label}-server.csv`), serverBytes);
  await check(`${label} actual browser download equals server bytes`, ['AC4'], bytes.equals(serverBytes), true);
  await check(`${label} CSV download metadata`, ['AC4'],
    [response.headers.get('content-type'), response.headers.get('content-disposition'), response.headers.get('cache-control')],
    ['text/csv; charset=utf-8', `attachment; filename="project-${projectId}-tasks.csv"`, 'no-store']);
  await check(`${label} UTF8 no BOM with final CRLF`, ['AC4'],
    bytes.toString('utf8').startsWith('"projectId"') && bytes.subarray(-2).equals(Buffer.from('\r\n')) &&
      Buffer.from(bytes.toString('utf8')).equals(bytes), true);
  report.downloads ??= [];
  report.downloads.push({ flow: currentFlow.name, label, path, downloadedFrom: browserPath,
    retention: 'moved completed browser file', result, bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex'), headers: Object.fromEntries(response.headers) });
  return bytes;
}

async function scenario(name, action) {
  try { return await action(); }
  catch (error) {
    currentFlow.failedScenarios ??= [];
    currentFlow.failedScenarios.push({ name, error: error.stack });
    console.error(`FAILED SCENARIO ${name}: ${error.message}`);
    await capture(`failed-${name}`);
  }
}

async function archiveDialog(accept) {
  await click('#project-lifecycle');
  const dialog = await browser('dialog', 'status');
  await writeFile(join(output, `archive-dialog-${commandNumber}.json`), JSON.stringify(dialog, null, 2));
  assert.ok(JSON.stringify(dialog).includes('Archive this project? Tasks will become read-only. You can restore it later.'), 'Actual native confirm text');
  await browser('dialog', accept ? 'accept' : 'dismiss');
  if (accept) {
    await browser('wait', '--text', 'Project archived. Tasks are read-only.');
    await ready();
  }
  await check(`Archive confirm ${accept ? 'accepted' : 'dismissed'} updates lifecycle control`, ['AC1', 'AC5'],
    await visibleText('#project-lifecycle'), accept ? 'Restore project' : 'Archive project');
}

async function archive() {
  await open();
  const neighbor = await createProject('Still active');
  const projectId = await createProject('@Team,"Unicode \u65e5"');
  await addTask('=SUM(1,2)', 'Comma, "quotes" \ud83d\ude80\nsecond line');
  const first = (await get(`/api/tasks?projectId=${projectId}`)).items[0];
  const tasks = [first];
  for (const [title, status, dependencyIds, priority, description] of [
    ['Launch todo', 'todo', [], 'low', '\tplain'],
    ['Launch blocked', 'todo', [first.id], 'high', '\u200b@SUM(1,2)'],
    ['Launch later', 'todo', [], 'normal', ''],
    ['Running', 'in_progress', [], 'normal', 'safe'],
    ['Finished', 'done', [], 'high', 'line\rreturn\r\npair'],
  ]) {
    const task = (await write('/api/tasks', { projectId, title, dependencyIds, priority, description })).task;
    tasks.push(status === 'todo' ? task : (await write(`/api/tasks/${task.id}`, { status }, 'PATCH')).task);
  }
  await click('#reload');
  await ready();
  const disk = () => readFile(join(currentFlow.directory, 'planner.json'), 'utf8');
  const before = JSON.parse(await disk());
  let activeCsv;
  await scenario('active-download', async () => {
    activeCsv = await download('active', projectId);
    const rows = parseCsv(activeCsv.toString('utf8'));
  await check('Independent CSV fixed columns and all six task IDs', ['AC4'],
    [rows[0], rows.slice(1).map(row => row[2])],
    [['projectId', 'projectName', 'id', 'title', 'description', 'status', 'priority', 'dependencyIds', 'blocked', 'createdOrder'], tasks.map(task => task.id)]);
  await check('Independent CSV unsafe name/title and multiline Unicode', ['AC4'], rows[1],
    [projectId, "'@Team,\"Unicode \u65e5\"", first.id, "'=SUM(1,2)", 'Comma, "quotes" \ud83d\ude80\nsecond line', 'todo', 'normal', '[]', 'false', String(first.createdOrder)]);
  await check('Independent CSV formula descriptions, dependencies and blocked data', ['AC4'],
    [rows[2][4], rows[3][4], rows[3][6], rows[3][7], rows[3][8], rows[6][4]],
    ["'\tplain", "'\u200b@SUM(1,2)", 'high', JSON.stringify([first.id]), 'true', 'line\rreturn\r\npair']);
  });
  await check('Export does not modify stored data or revision', ['AC4'], JSON.parse(await disk()), before);
  await archiveDialog(false);
  await check('Cancelled archive leaves exact model intact', ['AC1', 'AC5'], JSON.parse(await disk()), before);
  await select('#filter-pageSize', '2');
  await ready();
  await fill('#filter-q', 'Launch');
  await select('#filter-status', 'todo');
  await click('.filters button[type=submit]');
  await ready();
  await buttonNamed('Next');
  await ready();
  const ids = () => evaluate("[...document.querySelectorAll('article')].map(el=>el.dataset.taskId)");
  await check('Pre-archive filtered second page', ['AC5'], await ids(), [tasks[3].id]);
  await browser('focus', '#project-lifecycle');
  await check('Archive control receives keyboard focus', ['AC5'], await evaluate('document.activeElement.id'), 'project-lifecycle');
  await archiveDialog(true);
  await check('Archive focuses replacement lifecycle control', ['AC5'], await evaluate('document.activeElement.id'), 'project-lifecycle');
  await check('Archive preserves selected filter and page', ['AC2', 'AC5'],
    await evaluate("Object.fromEntries(new URL(location.href).searchParams)"),
    { projectId, pageSize: '2', q: 'Launch', status: 'todo', page: '2', archived: 'true' });
  await check('Archive filtered results unchanged', ['AC5'], await ids(), [tasks[3].id]);
  await check('Archive sidebar includes only archived project', ['AC2'],
    await evaluate("[...document.querySelectorAll('#projects a')].map(a=>new URL(a.href).searchParams.get('projectId'))"), [projectId]);
  await check('Every visible task write control disabled; restore/download enabled', ['AC3'],
    await evaluate("({disabled:[...document.querySelectorAll('[data-write=task]')].every(el=>el.disabled),restore:document.querySelector('#project-lifecycle').disabled,download:document.querySelector('#download-csv').disabled})"),
    { disabled: true, restore: false, download: false });
  const archivedModel = JSON.parse(await disk());
  await check('Any-status lifecycle preserves all task fields, IDs and allocation', ['AC1'],
    [archivedModel.tasks, archivedModel.nextId, archivedModel.revision], [before.tasks, before.nextId, before.revision + 1]);
  await check('Only target project archive flag changes', ['AC1'], archivedModel.projects,
    before.projects.map(project => project.id === projectId ? { ...project, archived: true } : project));
  await scenario('archived-download', async () => {
    const archivedCsv = await download('archived-filtered-page2', projectId);
    assert.ok(activeCsv, 'Active browser download must exist for active/archive equality');
    await check('Archived filtered download is identical full-project snapshot', ['AC4'], archivedCsv.equals(activeCsv), true);
  });
  await click('#nav-projects');
  await ready();
  await check('Active sidebar excludes archive while deep detail remains readable', ['AC2'],
    await evaluate("({ids:[...document.querySelectorAll('#projects a')].map(a=>new URL(a.href).searchParams.get('projectId')),title:document.querySelector('#project-title').textContent})"),
    { ids: [neighbor], title: '@Team,"Unicode \u65e5"' });
  await browser('back');
  await ready();
  await check('Back restores archive selector and filtered page', ['AC2', 'AC5'],
    [await evaluate("new URL(location.href).searchParams.get('archived')"), await ids()], ['true', [tasks[3].id]]);
  await capture('filtered-archive');
  await restart();
  await check('Restart preserves exact archived model', ['AC1'], JSON.parse(await disk()), archivedModel);
  await open(`/?projectId=${projectId}`);
  await contains('#main', 'Archived — tasks are read-only.', 'Archived direct link works without archive navigation', ['AC2']);
  await check('Deep link shows all mixed-status tasks and blocked dependency', ['AC1', 'AC2'],
    await evaluate("[...document.querySelectorAll('article .badge')].map(el=>el.textContent)"),
    ['todo', 'todo', 'blocked (todo)', 'todo', 'in progress', 'done']);
  await layout(390);
  await layout(1280);
  await audit('archived');
  await browser('focus', '#project-lifecycle');
  await browser('press', 'Tab');
  await check('Keyboard reaches archived download', ['AC5'], await evaluate('document.activeElement.id'), 'download-csv');
  const focus = await evaluate("({style:getComputedStyle(document.activeElement).outlineStyle,width:getComputedStyle(document.activeElement).outlineWidth})");
  await check('Archived download has visible focus outline', ['AC5'], focus.style !== 'none' && parseFloat(focus.width) >= 2, true);
  const guardBytes = await disk();
  for (const input of [{ title: 'no' }, { description: 'no' }, { status: 'done' }, { priority: 'high' },
    { dependencyIds: [] }, { title: first.title }, { title: 'no', description: 'no', priority: 'low' }]) {
    const response = await write(`/api/tasks/${first.id}`, input, 'PATCH', 409);
    await check(`Archived API rejects ${JSON.stringify(input)}`, ['AC3'], response.error.code, 'PROJECT_ARCHIVED');
  }
  const rejectedCreate = await write('/api/tasks', { projectId, title: 'Forbidden creation' }, 'POST', 409);
  await check('Archived API rejects creation', ['AC3'], rejectedCreate.error.code, 'PROJECT_ARCHIVED');
  await check('Rejected archived writes preserve exact disk bytes', ['AC3'], await disk(), guardBytes);
  await browser('focus', '#project-lifecycle');
  await browser('press', 'Enter');
  await browser('wait', '--text', 'Project restored. Editing is available.');
  await ready();
  await check('Restore enables Add/Edit and focuses lifecycle', ['AC3', 'AC5'],
    await evaluate("[document.querySelector('#add-task').disabled,document.querySelector('article button').disabled,document.activeElement.id]"), [false, false, 'project-lifecycle']);
  await editTask(first.id);
  await fill('#editor-description', 'Restored edit');
  await click('#editor button[type=submit]');
  await saved();
  await check('Restored real UI edit persisted', ['AC3'], (await get(`/api/tasks?projectId=${projectId}`)).items[0].description, 'Restored edit');
  await setStatus(tasks[2].id, 'in_progress', false);
  await contains('#error', 'Complete dependencies', 'Restore retains dependency transition rules', ['AC3']);
  await click('#editor button[type=button]');
  await editTask(first.id);
  await fill('#editor-title', 'Draft from client one');
  await check('Lifecycle disabled while draft open', ['AC3'], await evaluate("document.querySelector('#project-lifecycle').disabled"), true);
  const tabs = await browser('tab', 'list');
  await writeFile(join(output, 'archive-tabs.json'), JSON.stringify(tabs, null, 2));
  const originalTab = tabs.tabs.find(tab => tab.active).targetId;
  const secondTab = await browser('tab', 'new', '--label', 'archiver', `${currentFlow.app.url}/?projectId=${projectId}`);
  currentFlow.secondClient = secondTab;
  await ready();
  await archiveDialog(true);
  await browser('tab', String(originalTab));
  const staleBytes = await disk();
  await scenario('stale-client-download', () => download('stale-client-after-archive', projectId));
  await click('#editor button[type=submit]');
  await browser('wait', '#error');
  await check('Two real browser clients retain stale draft and fence retry', ['AC3'],
    await evaluate("[document.querySelector('#editor-title').value,document.querySelector('#editor button[type=submit]').disabled,document.activeElement.id]"),
    ['Draft from client one', true, 'error']);
  await contains('#notice', 'Draft retained', 'Stale draft recovery announced', ['AC3']);
  await check('Rejected stale write leaves disk unchanged', ['AC3'], await disk(), staleBytes);
  await capture('stale-draft');
  await click('#editor button[type=button]');
  await check('Fenced draft Cancel focuses project heading', ['AC3', 'AC5'], await evaluate('document.activeElement.id'), 'project-title');
  await click('#reload');
  await ready();
  await check('Explicit reload discards draft and adopts archived state', ['AC3'],
    await evaluate("document.querySelector('#editor') === null && document.querySelector('#add-task').disabled"), true);
  await browser('tab', String(originalTab));
  await click('#project-lifecycle');
  await browser('wait', '--text', 'Project restored. Editing is available.');
  await ready();
  await archiveFailures(projectId, first.id);
  await restart();
  await open(`/?projectId=${projectId}`);
  await contains(`article[data-task-id="${first.id}"]`, 'Committed before failed refresh', 'Restore and edited text survive second restart', ['AC1', 'AC3']);
  const empty = await createProject('Empty lifecycle');
  await archiveDialog(true);
  await contains('#main', 'No tasks in this archived project.', 'Empty archive is readable', ['AC1', 'AC2']);
  await scenario('empty-download', async () => {
    await check('Empty archived download is header only', ['AC4'], parseCsv((await download('empty', empty)).toString('utf8')).length, 1);
  });
  await capture('complete');
}

async function archiveFailures(projectId, taskId) {
  const csvUrl = `${currentFlow.app.url}/api/projects/${projectId}/tasks.csv`;
  const filesBefore = (await readdir(downloads)).sort();
  await browser('network', 'route', csvUrl, '--abort');
  try {
    await click('#download-csv');
    await browser('wait', '#error');
    await contains('#error', 'CSV download failed:', 'Download transport failure is actionable', ['AC4']);
    await check('Failed export leaves no file and no success announcement', ['AC4'],
      [(await readdir(downloads)).sort(), await visibleText('#notice'), await evaluate('document.activeElement.id')], [filesBefore, '', 'error']);
  } finally { await browser('network', 'unroute', csvUrl); }
  const projectsUrl = `${currentFlow.app.url}/api/projects?archived=false`;
  const staleProjects = await get('/api/projects?archived=false');
  await write(`/api/tasks/${taskId}`, { description: 'Changed between read batches' }, 'PATCH');
  await browser('network', 'route', projectsUrl, '--body', JSON.stringify(staleProjects));
  try {
    await click('#reload');
    await browser('wait', '#error');
    await contains('#error', 'Data changed while loading.', 'Mismatched real snapshot response prevents publication', ['AC5']);
    await check('Revision mismatch fences writes and retains prior rendered data', ['AC5'],
      await evaluate("document.querySelector('#add-task').disabled && document.querySelector('article p:nth-of-type(2)').textContent === 'Restored edit'"), true);
    await capture('coherence-failure');
  } finally { await browser('network', 'unroute', projectsUrl); }
  await click('#reload');
  await ready();
  await editTask(taskId);
  await fill('#editor-description', 'Committed before failed refresh');
  const healthUrl = `${currentFlow.app.url}/api/health`;
  await browser('network', 'route', healthUrl, '--abort');
  try {
    await click('#editor button[type=submit]');
    await browser('wait', '#error');
    await check('Post-save refresh failure retains draft, fences save, focuses alert', ['AC3', 'AC5'],
      await evaluate("[document.querySelector('#editor-description').value,document.querySelector('#editor button[type=submit]').disabled,document.activeElement.id]"),
      ['Committed before failed refresh', true, 'error']);
    await check('Post-save failure does not announce successful save', ['AC5'],
      await visibleText('#notice'), 'Draft retained. Reload latest discards it and loads committed data.');
    await check('Actual save committed despite refresh fault', ['AC5'],
      (await get(`/api/tasks?projectId=${projectId}`)).items.find(task => task.id === taskId).description, 'Committed before failed refresh');
    await capture('post-save-refresh-failure');
  } finally { await browser('network', 'unroute', healthUrl); }
  await click('#reload');
  await ready();
  await check('Explicit reload after uncertain save restores writable committed state', ['AC5'],
    await evaluate("!document.querySelector('#editor') && !document.querySelector('#add-task').disabled"), true);
}

try {
  cli = await discoverCli();
  report.agentBrowser = await command(cli, ['--version']);
  const { chromium } = await import(pathToFileURL(join(repo, 'benchmark', 'node_modules', 'playwright', 'index.mjs')));
  await mkdir(downloads, { recursive: true });
  const executable = chromium.executablePath();
  await access(executable);
  browserStarted = true;
  report.launch = await browser('--executable-path', executable, '--download-path', downloads, 'open', 'about:blank');
  report.browser = { executable, userAgent: await evaluate('navigator.userAgent') };
  for (const name of args[1] === 'all' ? ['base', 'graph', 'query', 'migration', 'archive'] : [args[1]]) {
    currentFlow = { name, directory: join(output, `data-${name}`), started: new Date().toISOString(), status: 'RUNNING' };
    report.flows.push(currentFlow);
    console.log(`START ${name} ${currentFlow.directory}`);
    try {
      await mkdir(currentFlow.directory, { recursive: true });
      if (name === 'migration') await writeFile(join(currentFlow.directory, 'planner.json'), await readFile(join(root, 'test', 'fixtures', 'planner-v1.json')));
      await startApp(currentFlow.directory);
      if (report.flows.length === 1) {
        const warmup = await command(cli, ['--session', session, '--json', 'open', currentFlow.app.url], { timeout: 60000 });
        assert.equal(JSON.parse(warmup).success, true);
        await ready();
      }
      await browser('console', '--clear');
      await browser('errors', '--clear');
      await ({ base, graph, query, migration, archive })[name]();
      currentFlow.status = currentFlow.failedScenarios?.length ? 'FAILED' : 'VERIFIED';
    } catch (error) {
      currentFlow.status = 'FAILED';
      currentFlow.error = error.stack;
      console.error(`FAIL ${name}: ${error.message}`);
      await capture('failure').catch(captureError => { currentFlow.captureError = captureError.message; });
    } finally {
      currentFlow.console = await browser('console').catch(error => ({ unavailable: error.message }));
      currentFlow.errors = await browser('errors').catch(error => ({ unavailable: error.message }));
      if (!Array.isArray(currentFlow.errors.errors) || currentFlow.errors.errors.length) {
        currentFlow.status = 'FAILED';
        currentFlow.browserErrorFailure = 'Uncaught errors found or browser error collection unavailable';
      }
      if (!Array.isArray(currentFlow.console.messages) || currentFlow.console.messages.length) {
        report.findings.push({ id: 'BROWSER-CONSOLE', flow: name, ac: ['AC07'], detail: currentFlow.console });
      }
      const expectedNegative = message => ['base', 'graph', 'archive'].includes(name) &&
        (/Failed to load resource: the server responded with a status of (400|409)\b/.test(JSON.stringify(message)) ||
          (['base', 'archive'].includes(name) && /Failed to load resource: net::ERR_(INTERNET_DISCONNECTED|FAILED)\b/.test(JSON.stringify(message))));
      currentFlow.expectedNegativeConsole = Array.isArray(currentFlow.console.messages) ? currentFlow.console.messages.filter(expectedNegative) : null;
      currentFlow.unexpectedConsole = Array.isArray(currentFlow.console.messages) ? currentFlow.console.messages.filter(message => !expectedNegative(message)) : null;
      if (!Array.isArray(currentFlow.unexpectedConsole) || currentFlow.unexpectedConsole.length) {
        currentFlow.status = 'FAILED';
        currentFlow.consoleFailure = 'Unexpected browser console messages found or console collection unavailable';
      }
      await stopApp().catch(error => { currentFlow.cleanupError = error.message; currentFlow.status = 'FAILED'; });
      delete currentFlow.app;
      currentFlow.finished = new Date().toISOString();
      console.log(`END ${name} ${currentFlow.status}`);
      await writeFile(join(output, 'report.json'), JSON.stringify(report, null, 2));
    }
  }
} catch (error) {
  report.blocker = error.stack;
  console.error(error.stack);
} finally {
  if (browserStarted) await browser('close').catch(error => { report.browserCloseError = error.message; });
  for (const child of active) if (child.exitCode === null) child.kill('SIGKILL');
  report.changedSources = [];
  for (const [path, hash] of Object.entries(report.sourceHashes)) {
    if (createHash('sha256').update(await readFile(join(root, ...path.split('/')))).digest('hex') !== hash) report.changedSources.push(path);
  }
  report.finished = new Date().toISOString();
  report.status = !report.blocker && !report.browserCloseError && !report.changedSources.length && report.flows.length && report.flows.every(flow => flow.status === 'VERIFIED') ? 'VERIFIED_WITH_LIMITATIONS' : 'FAILED';
  await writeFile(join(output, 'report.json'), JSON.stringify(report, null, 2));
  if (process.env.E2E_EVIDENCE_DIR) await cp(output, join(resolve(process.env.E2E_EVIDENCE_DIR), runId),
    { recursive: true, filter: path => !path.includes('owned-browser-profile') });
  console.log(`Evidence: ${join(output, 'report.json')}`);
  process.exitCode = report.status === 'FAILED' ? 1 : 0;
}
