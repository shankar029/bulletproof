// Local documentation proof adapted from the existing preview-docs.mjs helper.
// Uses existing marked/Chromium; all page operations are agent-browser commands.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { pathToFileURL } from 'node:url';

const root = process.cwd();
const output = resolve('.ai/workflow-reliability/evidence');
const tag = process.env.C3_EVIDENCE_TAG ?? '';
assert.match(tag, /^(?:-r[0-9]+)?$/);
const prefix = `c3-integration${tag}`;
const helperRoot = process.env.C3_DOC_HELPERS ??
  'C:/Users/shbs/.copilot/session-state/c154cbfc-3b1d-4163-b8dd-5f0b43af3095/files/workflow-reliability';
const { marked } = await import(pathToFileURL(join(helperRoot, 'doc-tools/node_modules/marked/lib/marked.esm.js')));
const { chromium } = await import(pathToFileURL(resolve('benchmark/node_modules/playwright/index.mjs')));
const python = process.env.BULLETPROOF_PYTHON;
assert.ok(python, 'Set BULLETPROOF_PYTHON to the verified interpreter');
const cli = process.env.C3_AGENT_BROWSER ??
  'C:/Users/shbs/AppData/Local/npm-cache/_npx/6de2aa2fded2970c/node_modules/agent-browser/bin/agent-browser-win32-x64.exe';
const scratch = await mkdtemp(join(tmpdir(), 'c3-doc-'));
const session = `c3-doc-${randomUUID()}`;
const commands = [], links = [], results = [], navigation = [];
const docs = [
  'SKILL.md', 'README.md', 'CONTRIBUTING.md', 'docs/user-guide.md', 'docs/architecture.md',
  ...['workspace', 'planning', 'design-doc', 'delegation', 'testing-and-e2e', 'research',
    'communication', 'review-and-pr', 'final-report', 'workflow-gates'].map(n => `references/${n}.md`),
];
const previews = new Map([
  ['README.md', join(scratch, 'readme.html')],
  ['docs/user-guide.md', join(scratch, 'user-guide.html')],
  ['references/workflow-gates.md', join(scratch, 'operator-guide.html')],
]);
const slug = text => text.toLowerCase().replace(/<[^>]*>/g, '')
  .replace(/[^\p{L}\p{N}_\-\s]/gu, '').replace(/\s/g, '-');
let context, cdp, failure;

async function browser(...args) {
  const argv = ['--session', session, '--cdp', cdp, '--json', ...args];
  const managed = ['-B', resolve('scripts/run.py'), '--idle', '30', '--max', '60', '--', cli, ...argv];
  const child = spawn(python, managed, {
    windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  let stdout = '', stderr = '';
  child.stdout.on('data', value => { stdout += value; });
  child.stderr.on('data', value => { stderr += value; });
  const code = await new Promise((done, reject) => {
    child.once('error', reject);
    child.once('close', done);
  });
  commands.push({ executable: python, argv: managed, code, stdout, stderr });
  console.log(`Completed agent-browser ${args[0]} (${code})`);
  assert.equal(code, 0, stdout + stderr);
  const result = JSON.parse(stdout);
  assert.equal(result.success, true, stdout);
  return result.data;
}

async function checkLinks(file, text) {
  const found = [];
  marked.walkTokens(marked.lexer(text), token => {
    if (token.type === 'link' || token.type === 'image') found.push(token.href);
    if (token.type === 'html') {
      for (const match of token.text.matchAll(/(?:href|src)="([^"]+)"/g)) found.push(match[1]);
    }
  });
  for (const link of new Set(found)) {
    if (/^[a-z]+:/i.test(link)) continue;
    const [relative, anchor] = link.split('#');
    const target = relative ? resolve(dirname(file), decodeURIComponent(relative)) : file;
    const info = await stat(target);
    if (anchor && info.isFile() && target.endsWith('.md')) {
      const headings = marked.lexer(await readFile(target, 'utf8'))
        .filter(token => token.type === 'heading').map(token => slug(token.text));
      assert.ok(headings.includes(decodeURIComponent(anchor)), `${file}: unresolved anchor ${link}`);
    }
  }
  return [...new Set(found)];
}

try {
  for (const relative of docs) {
    const file = resolve(relative), bytes = await readFile(file), text = bytes.toString('utf8');
    links.push({ file: relative, sha256: createHash('sha256').update(bytes).digest('hex'),
      checked: await checkLinks(file, text) });
    console.log(`Checked local links: ${relative}`);
  }
  const renderer = new marked.Renderer();
  renderer.heading = function(token) {
    return `<h${token.depth} id="${slug(token.text)}">${this.parser.parseInline(token.tokens)}</h${token.depth}>\n`;
  };
  for (const [relative, page] of previews) {
    let content = await marked.parse(await readFile(resolve(relative), 'utf8'), { renderer });
    content = content.replace(/(href|src)="([^"]+)"/g, (whole, attr, link) => {
      if (/^[a-z]+:/i.test(link) || link.startsWith('#')) return whole;
      const [file, anchor] = link.split('#');
      const target = resolve(dirname(resolve(relative)), file);
      const preview = [...previews].find(([source]) => resolve(source) === target)?.[1];
      return `${attr}="${pathToFileURL(preview ?? target).href}${anchor ? '#' + anchor : ''}"`;
    });
    // Existing local GitHub-like preview theme; no README/banner layout replacement.
    await writeFile(page, `<!doctype html><html lang="en"><meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1"><title>${relative} preview</title><style>
      :root{color-scheme:light dark;--bg:#fff;--fg:#1f2328;--line:#d1d9e0;--code:#f6f8fa;--link:#0969da}
      @media(prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--line:#30363d;--code:#161b22;--link:#79c0ff}}
      *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 system-ui,sans-serif}
      main{max-width:980px;margin:auto;padding:32px 28px;overflow-wrap:break-word}a{color:var(--link)}img{max-width:100%;height:auto}
      h1,h2{line-height:1.3;border-bottom:1px solid var(--line);padding-bottom:.3em}h2{margin-top:1.8em}h3{margin-top:1.5em}
      pre{padding:16px;background:var(--code);overflow:auto;border-radius:8px}code{font-size:.88em;background:var(--code)}
      table{display:block;max-width:100%;overflow:auto;border-collapse:collapse}th,td{border:1px solid var(--line);padding:8px 12px}
      th{text-align:left}tr:nth-child(even){background:var(--code)}blockquote{border-left:4px solid var(--line);margin:0;padding-left:18px}
      hr{border:0;border-top:1px solid var(--line);margin:28px 0}@media(max-width:600px){main{padding:20px 16px}}
      </style><main>${content}</main></html>`);
  }
  // Launch/close only through this existing library; no Playwright page operations.
  context = await chromium.launchPersistentContext(join(scratch, 'profile'), {
    headless: true, args: ['--remote-debugging-port=0'], timeout: 30000,
  });
  const port = Number((await readFile(join(scratch, 'profile/DevToolsActivePort'), 'utf8')).split('\n')[0]);
  cdp = `http://127.0.0.1:${port}`;
  for (const [relative, page] of previews) {
    for (const width of [1280, 390]) {
      for (const theme of ['light', 'dark']) {
        await browser('set', 'viewport', String(width), '900');
        await browser('set', 'media', theme);
        await browser('open', pathToFileURL(page).href);
        const snapshot = await browser('snapshot', '-i');
        const view = JSON.parse((await browser('eval', `JSON.stringify({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,headings:document.querySelectorAll("h1,h2,h3").length,images:[...document.images].map(i=>({loaded:i.complete&&i.naturalWidth>0,alt:i.alt})),text:document.body.innerText.length,background:getComputedStyle(document.body).backgroundColor})`)).result);
        assert.equal(view.width, width);
        assert.ok(view.scrollWidth <= width, `${relative}: horizontal overflow`);
        assert.ok(view.headings >= 7 && view.text > 3000);
        assert.ok(view.images.every(image => image.loaded && image.alt.length > 0));
        assert.equal(view.background, theme === 'light' ? 'rgb(255, 255, 255)' : 'rgb(13, 17, 23)');
        const errors = await browser('errors'), consoleLog = await browser('console');
        assert.deepEqual(errors.errors, []);
        assert.deepEqual(consoleLog.messages, []);
        const name = page.split(/[\\/]/).at(-1).replace('.html', '');
        const image = `${prefix}-${name}-${width}-${theme}.png`;
        await browser('screenshot', join(output, image));
        results.push({ file: relative, width, theme, view, snapshot, errors, consoleLog, image });
      }
    }
  }
  await browser('open', pathToFileURL(previews.get('README.md')).href);
  await browser('snapshot', '-i');
  await browser('click', 'a[href="#features-at-a-glance"]');
  assert.equal((await browser('get', 'url')).url.split('#')[1], 'features-at-a-glance');
  await browser('screenshot', join(output, `${prefix}-readme-feature-navigation.png`));
  navigation.push('README feature overview anchor');
  await browser('snapshot', '-i');
  await browser('click', 'a[href="#build-deliberately-in-increments-that-survive-a-handoff"]');
  assert.equal((await browser('get', 'url')).url.split('#')[1], 'build-deliberately-in-increments-that-survive-a-handoff');
  navigation.push('README build/resume subnavigation');
  const snapshot = await browser('snapshot', '-i');
  const operator = Object.entries(snapshot.refs).find(([, value]) => value.role === 'link' && value.name === 'Operator guide');
  assert.ok(operator, 'Operator link is visible in accessibility snapshot');
  await browser('click', `@${operator[0]}`);
  assert.equal((await browser('get', 'url')).url, pathToFileURL(previews.get('references/workflow-gates.md')).href);
  navigation.push('README operator guide link');
  assert.deepEqual((await browser('errors')).errors, []);
  assert.deepEqual((await browser('console')).messages, []);
} catch (error) {
  failure = String(error.stack ?? error);
  throw error;
} finally {
  try {
    if (cdp) await browser('close');
  } finally {
    await context?.close();
    await rm(scratch, { recursive: true, force: true });
    await writeFile(join(output, `${prefix}-docs.json`), JSON.stringify({
      renderer: 'Existing marked 18.0.12/local GitHub-like preview; not github.com',
      helperRoot, cli, session, links, results, navigation, commands, failure: failure ?? null,
      cleanup: 'Owned browser context closed and scratch removed; no old process cleanup claim',
    }, null, 2) + '\n', { flag: 'wx' });
  }
}
console.log(`Local documentation proof: ${links.length} files, ${results.length} views, ${navigation.length} navigation checks`);
