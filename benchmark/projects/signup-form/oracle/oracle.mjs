import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

// Held-out UI acceptance suite. Serves ARM_DIR statically and drives it in a real browser.
const ARM_DIR = process.env.ARM_DIR;
if (!ARM_DIR) throw new Error('ARM_DIR env var required');

let server, browser, base;
const CONTENT_TYPE = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
before(async () => {
  server = http.createServer((req, res) => {
    const url = req.url === '/' ? '/index.html' : req.url;
    // `/shared/...` resolves to the project root so arms can reuse shared modules.
    const abs = url.startsWith('/shared/')
      ? path.join(ARM_DIR, '..', url)
      : path.join(ARM_DIR, url.slice(1));
    fs.readFile(abs, (err, data) => {
      if (err) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'content-type': CONTENT_TYPE[path.extname(abs)] || 'application/octet-stream' });
      res.end(data);
    });
  });
  await new Promise((r) => server.listen(0, r));
  base = `http://127.0.0.1:${server.address().port}/`;
  browser = await chromium.launch();
});
after(async () => { await browser?.close(); server?.close(); });

async function open() {
  const p = await browser.newPage();
  await p.goto(base);
  return p;
}
const successText = async (p) => ((await p.locator('#success').textContent()) || '').trim();
async function fillAndSubmit(p, email, password, confirm) {
  await p.fill('#email', email);
  await p.fill('#password', password);
  await p.fill('#confirm', confirm);
  if (!(await p.locator('#submit').isDisabled())) await p.locator('#submit').click();
}

test('submit is disabled until the form is valid', async () => {
  const p = await open();
  assert.equal(await p.locator('#submit').isDisabled(), true);
  await p.close();
});
test('no error or success is shown before interaction', async () => {
  const p = await open();
  assert.equal((await p.locator('#error').textContent() || '').trim(), '');
  assert.equal(await successText(p), '');
  await p.close();
});
test('rejects an invalid email', async () => {
  const p = await open();
  await fillAndSubmit(p, 'not-an-email', 'abcd1234', 'abcd1234');
  assert.equal(await successText(p), '');
  await p.close();
});
test('rejects a too-short password', async () => {
  const p = await open();
  await fillAndSubmit(p, 'user@example.com', 'ab1', 'ab1');
  assert.equal(await successText(p), '');
  await p.close();
});
test('rejects a password with no digit', async () => {
  const p = await open();
  await fillAndSubmit(p, 'user@example.com', 'abcdefgh', 'abcdefgh');
  assert.equal(await successText(p), '');
  await p.close();
});
test('rejects mismatched confirmation', async () => {
  const p = await open();
  await fillAndSubmit(p, 'user@example.com', 'abcd1234', 'abcd9999');
  assert.equal(await successText(p), '');
  await p.close();
});
test('accepts valid input and shows success with the email', async () => {
  const p = await open();
  await fillAndSubmit(p, 'user@example.com', 'abcd1234', 'abcd1234');
  assert.match(await successText(p), /Account created for user@example\.com/);
  await p.close();
});
