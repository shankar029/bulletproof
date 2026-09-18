import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createHash, randomUUID } from 'node:crypto';
import { access, appendFile, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const repo = resolve(import.meta.dirname, '..', '..', '..');
const python = String.raw`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`;
const output = join(import.meta.dirname, `doc-render-${new Date().toISOString().replaceAll(/[:.]/g, '-')}`);
await mkdir(output, { recursive: true });
const report = { output, started: new Date().toISOString(), checks: [], command: process.argv };
report.runnerSha256 = createHash('sha256').update(await readFile(import.meta.filename)).digest('hex');
const profile = join(output, 'owned-browser-profile');
let cli, cdp, context;
const session = `doc-render-${randomUUID().slice(0, 8)}`;

async function command(executable, args, timeout = 35) {
  const wrapperArgs = [join(repo, 'scripts', 'run.py'), '--idle', '25', '--max', String(timeout), '--', executable, ...args];
  const child = spawn(python, wrapperArgs, { cwd: repo, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, AGENT_BROWSER_DEFAULT_TIMEOUT: '12000', AGENT_BROWSER_IDLE_TIMEOUT_MS: '60000' } });
  let stdout = '', stderr = '';
  child.stdout.on('data', data => { stdout += data; });
  child.stderr.on('data', data => { stderr += data; });
  const [exitCode] = await once(child, 'exit', { signal: AbortSignal.timeout((timeout + 10) * 1000) });
  child.stdout.destroy();
  child.stderr.destroy();
  await appendFile(join(output, 'commands.jsonl'), JSON.stringify({ executable: python, args: wrapperArgs, exitCode, stdout, stderr }) + '\n');
  assert.equal(exitCode, 0, `${args.join(' ')}\n${stdout}\n${stderr}`);
  return stdout;
}

async function discoverCli() {
  const candidates = process.env.AGENT_BROWSER_BIN ? [process.env.AGENT_BROWSER_BIN] : [];
  const cache = process.env.npm_config_cache ?? join(process.env.LOCALAPPDATA ?? join(homedir(), 'AppData', 'Local'), 'npm-cache');
  for (const dir of await readdir(join(cache, '_npx')).catch(() => [])) {
    candidates.push(join(cache, '_npx', dir, 'node_modules', 'agent-browser', 'bin', 'agent-browser-win32-x64.exe'));
  }
  for (const candidate of candidates) {
    const metadata = JSON.parse(await readFile(join(dirname(candidate), '..', 'package.json'), 'utf8').catch(() => '{}'));
    if (metadata.name === 'agent-browser' && metadata.version === '0.37.1' && await access(candidate).then(() => true, () => false)) return candidate;
  }
  throw new Error('Existing cached agent-browser@0.37.1 unavailable; no installation attempted.');
}

async function browser(...args) {
  console.log(`agent-browser ${args[0]}`);
  const result = JSON.parse(await command(cli, ['--session', session, '--cdp', cdp, '--json', ...args]));
  assert.equal(result.success, true, JSON.stringify(result));
  return result.data;
}

async function evaluate(expression) {
  return (await browser('eval', '-b', Buffer.from(expression).toString('base64'))).result;
}

function countPdfPages(buffer) {
  const pdf = buffer.toString('latin1');
  assert.ok(pdf.startsWith('%PDF-'), 'PDF header');
  assert.ok(pdf.includes('%%EOF'), 'PDF end marker');
  const objects = new Map([...pdf.matchAll(/(?:^|[\r\n])(\d+) (\d+) obj\s*([\s\S]*?)\s*endobj/g)]
    .map(match => [`${match[1]} ${match[2]}`, match[3].split(/\r?\nstream\r?\n/)[0]]));
  const catalog = [...objects.entries()].find(([, body]) => /\/Type\s*\/Catalog\b/.test(body));
  assert.ok(catalog, 'Readable PDF catalog required');
  const rootRef = catalog[1].match(/\/Pages\s+(\d+ \d+) R/)[1];
  const seen = new Set();
  const leaves = [];
  const trees = [];
  function walk(ref, parent) {
    assert.ok(!seen.has(ref), 'No duplicate/circular PDF page tree references');
    seen.add(ref);
    const body = objects.get(ref);
    assert.ok(body, `Referenced PDF object ${ref} exists`);
    if (parent) assert.ok(body.includes(`/Parent ${parent} R`), 'Page tree parent matches');
    if (/\/Type\s*\/Page\b/.test(body)) {
      leaves.push({ ref, mediaBox: body.match(/\/MediaBox\s*\[([^\]]+)\]/)?.[1] });
      return 1;
    }
    assert.ok(/\/Type\s*\/Pages\b/.test(body), 'Page tree node type');
    const kids = body.match(/\/Kids\s*\[([\s\S]*?)\]/)?.[1];
    assert.ok(kids, 'Page tree children');
    const count = [...kids.matchAll(/(\d+ \d+) R/g)].reduce((total, match) => total + walk(match[1], ref), 0);
    const declared = Number(body.match(/\/Count\s+(\d+)/)?.[1]);
    assert.equal(count, declared, 'Declared PDF page tree count equals leaf count');
    trees.push({ ref, declared, observed: count });
    return count;
  }
  const pages = walk(rootRef);
  assert.equal(leaves.length, [...objects.values()].filter(body => /\/Type\s*\/Page\b/.test(body)).length);
  return { pages, method: 'Traverse PDF catalog /Pages -> /Kids, verify /Parent and /Count against /Type /Page leaves', trees, leaves };
}

async function inspectDocument(name) {
  const file = join(repo, '.ai', 'planner-live-workflow', `${name}.html`);
  const doc = { name, url: pathToFileURL(file).href,
    sourceSha256: createHash('sha256').update(await readFile(file)).digest('hex') };
  report.documents ??= [];
  report.documents.push(doc);
  await browser('set', 'viewport', '1280', '960');
  await browser('set', 'media', 'light');
  await browser('open', doc.url);
  await browser('wait', '--fn', "document.readyState === 'complete' && !!document.querySelector('#bp-bar')");
  doc.snapshot = await browser('snapshot');
  await writeFile(join(output, `${name}-snapshot.json`), JSON.stringify(doc.snapshot, null, 2));
  const metricsExpression = `(() => {
    const rect = el => { const r=el.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height}; };
    const css = el => { const c=getComputedStyle(el); return {color:c.color,background:c.backgroundColor,font:c.font,fill:c.fill,stroke:c.stroke,display:c.display}; };
    return {title:document.title, readyState:document.readyState, viewport:innerWidth, scrollWidth:document.documentElement.scrollWidth,
      body:css(document.body), bar:css(document.querySelector('#bp-bar')),
      stylesheet:[...document.styleSheets].map(s=>({href:s.href,disabled:s.disabled})),
      diagrams:[...document.querySelectorAll('figure svg')].map(svg=>({
        label:svg.getAttribute('aria-label'),rect:rect(svg),viewBox:svg.getAttribute('viewBox'),
        boxes:[...svg.querySelectorAll('rect')].map(el=>({rect:rect(el),style:css(el)})),
        text:[...svg.querySelectorAll('text')].map(el=>({text:el.textContent,rect:rect(el),style:css(el)}))
      })),
      pre:[...document.querySelectorAll('pre')].map(el=>({text:el.textContent,rect:rect(el),scrollWidth:el.scrollWidth,clientWidth:el.clientWidth}))
    };
  })()`;
  doc.light = await evaluate(metricsExpression);
  assert.ok(doc.light.stylesheet.some(sheet => sheet.href.endsWith('/assets/artifact.css') && !sheet.disabled));
  assert.equal(doc.light.bar.display, 'flex');
  assert.equal(doc.light.diagrams.length, name === 'design' ? 2 : 0);
  for (const diagram of doc.light.diagrams) assert.ok(diagram.rect.width > 0 && diagram.rect.height > 0);
  await browser('screenshot', join(output, `${name}-light.png`), '--full');
  doc.lightErrors = await browser('errors');
  doc.lightConsole = await browser('console');
  await browser('set', 'media', 'dark');
  doc.dark = await evaluate(metricsExpression);
  assert.notEqual(doc.light.body.background, doc.dark.body.background, 'Theme changes actual computed background');
  await browser('screenshot', join(output, `${name}-dark.png`), '--full');
  doc.darkErrors = await browser('errors');
  doc.darkConsole = await browser('console');
  await browser('set', 'media', 'light');
  const pdfPath = join(output, `${name}.pdf`);
  doc.pdfCommand = await browser('pdf', pdfPath);
  doc.pdf = countPdfPages(await readFile(pdfPath));
  doc.pdf.path = pdfPath;
  doc.finalErrors = await browser('errors');
  doc.finalConsole = await browser('console');
  for (const key of ['lightErrors', 'darkErrors', 'finalErrors']) assert.deepEqual(doc[key].errors, [], `${name}: ${key}`);
  for (const key of ['lightConsole', 'darkConsole', 'finalConsole']) assert.deepEqual(doc[key].messages, [], `${name}: ${key}`);
  report.checks.push({ name: `${name} theme loaded, expected diagrams rendered, light/dark switched, console/errors empty`, status: 'VERIFIED' });
  doc.sourceUnchanged = doc.sourceSha256 === createHash('sha256').update(await readFile(file)).digest('hex');
  assert.ok(doc.sourceUnchanged, 'Verified source unchanged during render');
  report.checks.push({ name: `${name} PDF pages`, actual: doc.pdf.pages, limit: name === 'design' ? 3 : null,
    status: name === 'design' && doc.pdf.pages > 3 ? 'FAIL' : 'VERIFIED' });
  console.log(`${name}: ${doc.pdf.pages} actual PDF pages`);
}

try {
  cli = await discoverCli();
  report.cli = cli;
  report.version = await command(cli, ['--version']);
  if (process.argv.includes('--help-only')) {
    for (const args of [['--help'], ['pdf', '--help'], ['screenshot', '--help'], ['set', '--help']]) {
      const text = await command(cli, args);
      await writeFile(join(output, `${args[0].replaceAll('-', '')}-help.txt`), text);
      console.log(text);
    }
    const instructions = await readFile(join(dirname(cli), '..', 'README.md'), 'utf8');
    await writeFile(join(output, 'installed-agent-browser-README.md'), instructions);
    report.status = 'HELP_CAPTURED';
  } else {
    report.assets = {};
    for (const name of ['artifact.css', 'artifact.js']) report.assets[name] =
      createHash('sha256').update(await readFile(join(repo, '.ai', 'assets', name))).digest('hex');
    const { chromium } = await import(pathToFileURL(join(repo, 'benchmark', 'node_modules', 'playwright', 'index.mjs')));
    context = await chromium.launchPersistentContext(profile, { headless: true, args: ['--remote-debugging-port=0'], timeout: 30000 });
    const port = Number((await readFile(join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]);
    cdp = `http://127.0.0.1:${port}`;
    const response = await fetch(cdp + '/json/version', { signal: AbortSignal.timeout(5000) });
    assert.equal(response.status, 200);
    report.browser = await response.json();
    report.transport = 'Playwright launch/close only; all browser actions via agent-browser with explicit IPv4 CDP';
    await inspectDocument('design');
    await inspectDocument('ux');
    report.status = report.checks.some(check => check.status === 'FAIL') ? 'PAGE_LIMIT_FAILED' : 'RENDER_CAPTURED';
    if (report.status === 'PAGE_LIMIT_FAILED') process.exitCode = 1;
  }
} catch (error) {
  report.blocker = error.stack;
  report.status = 'BLOCKED';
  process.exitCode = 1;
} finally {
  if (context) {
    await browser('close').catch(error => { report.browserCloseError = error.message; });
    await context.close().catch(error => { report.contextCloseError = error.message; });
    report.endpointClosed = await fetch(cdp + '/json/version', { signal: AbortSignal.timeout(1500) }).then(() => false, () => true);
    await rm(profile, { recursive: true, force: true, maxRetries: 3, retryDelay: 500 }).catch(error => { report.profileCleanupError = error.message; });
    report.profileRemoved = await access(profile).then(() => false, () => true);
  }
  report.finished = new Date().toISOString();
  await writeFile(join(output, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ status: report.status, blocker: report.blocker, output, checks: report.checks,
    endpointClosed: report.endpointClosed, profileRemoved: report.profileRemoved }, null, 2));
}
