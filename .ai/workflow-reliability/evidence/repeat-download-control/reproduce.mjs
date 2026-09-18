import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createHash, randomUUID } from 'node:crypto';
import { access, mkdir, mkdtemp, readFile, readdir, writeFile } from 'node:fs/promises';
import http from 'node:http';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { pathToFileURL } from 'node:url';

const root = process.cwd();
const python = String.raw`C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe`;
const cli = String.raw`C:\Users\shbs\AppData\Local\npm-cache\_npx\6de2aa2fded2970c\node_modules\agent-browser\bin\agent-browser-win32-x64.exe`;
const output = await mkdtemp(join(import.meta.dirname, 'download-control-'));
const downloads = join(output, 'downloads');
await mkdir(downloads);
const session = `download-control-${randomUUID().slice(0, 8)}`;
const csv = Buffer.from('id,title\r\n1,Transport control\r\n');
const repeat = process.argv.includes('--repeat-blob');
let responseCount = 0, expectedCsv = csv;
const report = { session, output, commands: [], requests: [], checks: [], failure: null };
const server = http.createServer((req, res) => {
  report.requests.push({ method: req.method, url: req.url, time: new Date().toISOString() });
  if (req.url === '/control.csv') {
    if (repeat) expectedCsv = Buffer.from(`id,title\r\n${++responseCount},Transport control\r\n`);
    res.writeHead(200, { 'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="control.csv"', 'Content-Length': expectedCsv.length });
    res.end(expectedCsv);
  } else if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(repeat ? `<!doctype html><title>Repeat blob download</title><button id="download">Download CSV</button>
      <p id="notice">Ready</p><script>
      document.querySelector('#download').onclick = async () => {
        document.querySelector('#notice').textContent = 'Preparing CSV';
        try {
          const response = await fetch('/control.csv');
          const href = URL.createObjectURL(await response.blob());
          const a = document.createElement('a');
          a.href = href; a.download = 'control.csv'; document.body.append(a);
          a.click(); a.remove();
          document.querySelector('#notice').textContent = 'CSV download started.';
          setTimeout(() => URL.revokeObjectURL(href), 1000);
        } catch(error) { document.querySelector('#notice').textContent = error.message; }
      };</script>` : '<!doctype html><title>Download transport control</title><a id="download" href="/control.csv" download>Download control CSV</a>');
  } else {
    res.writeHead(204);
    res.end();
  }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const url = `http://127.0.0.1:${server.address().port}/`;

async function browser(args, expectSuccess = true) {
  const argv = ['--session', session, '--json', ...args];
  const wrapper = [join(root, 'scripts', 'run.py'), '--idle', '35', '--max', '60', '--', cli, ...argv];
  console.log(`START ${args[0]}`);
  const child = spawn(python, wrapper, { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, AGENT_BROWSER_IDLE_TIMEOUT_MS: '90000' } });
  let stdout = '', stderr = '';
  child.stdout.on('data', data => { stdout += data; });
  child.stderr.on('data', data => { stderr += data; });
  const [exitCode, signal] = await once(child, 'exit');
  await delay(20);
  child.stdout.destroy();
  child.stderr.destroy();
  report.commands.push({ executable: python, argv: wrapper, exitCode, signal, stdout, stderr });
  console.log(`DONE ${args[0]} exit=${exitCode} ${stdout.trim()} ${stderr.trim()}`);
  assert.ok(exitCode !== 124 && exitCode !== 125, 'Control command exceeded its bound');
  const result = JSON.parse(stdout);
  if (expectSuccess) {
    assert.equal(exitCode, 0);
    assert.equal(result.success, true);
  }
  return result;
}

try {
  const { chromium } = await import(pathToFileURL(join(root, 'benchmark', 'node_modules', 'playwright', 'index.mjs')));
  const executable = chromium.executablePath();
  await access(executable);
  report.browserExecutable = executable;
  await browser(['--executable-path', executable, '--download-path', downloads, 'open', url]);
  await browser(['eval', 'navigator.userAgent']);
  await browser(['click', '#download']);
  let files = [];
  const deadline = Date.now() + 12000;
  while (Date.now() < deadline) {
    files = await readdir(downloads);
    if (files.includes('control.csv')) break;
    await delay(100);
  }
  report.filesAfterClick = files;
  assert.deepEqual(await readFile(join(downloads, 'control.csv')), expectedCsv);
  report.checks.push({ name: 'Managed-launch ordinary click saves exact CSV bytes', status: 'passed',
    bytes: expectedCsv.length, sha256: createHash('sha256').update(expectedCsv).digest('hex') });
  console.log('PASS ordinary-click actual file and exact bytes');
  if (repeat) {
    await browser(['click', '#download']);
    await delay(1000);
    report.pageAfterSecondClick = await browser(['eval', 'JSON.stringify({url:location.href,notice:document.querySelector("#notice")?.textContent})']);
    report.tabsAfterSecondClick = await browser(['tab', 'list']);
    let saved = null;
    const limit = Date.now() + 12000;
    while (Date.now() < limit) {
      for (const name of await readdir(downloads)) {
        if (name.endsWith('.csv') && (await readFile(join(downloads, name))).equals(expectedCsv)) saved = name;
      }
      if (saved && responseCount === 2) break;
      await delay(100);
    }
    report.repeatedDownload = { responseCount, saved, files: await readdir(downloads) };
    assert.equal(responseCount, 2);
    assert.ok(saved, 'Second blob download must produce the changed second-response bytes');
    console.log('PASS repeated blob download actual second-response bytes');
  } else {
  const result = await browser(['download', '#download', join(downloads, 'explicit.csv')], false);
  report.explicitDownloadResult = result;
  report.filesAfterExplicitDownload = await readdir(downloads);
  if (result.success) {
    assert.deepEqual(await readFile(join(downloads, 'explicit.csv')), csv);
    report.checks.push({ name: 'Explicit download command saves exact bytes', status: 'passed' });
  } else {
    report.checks.push({ name: 'Explicit download command saves exact bytes', status: 'failed', error: result.error });
  }
  }
} catch (error) {
  report.failure = error.stack;
  process.exitCode = 1;
  console.error(error.stack);
} finally {
  try { await browser(['close']); } catch (error) {
    report.closeFailure = error.stack;
    process.exitCode = 1;
  }
  await new Promise(resolve => server.close(resolve));
  await writeFile(join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(`REPORT ${join(output, 'report.json')}`);
}
