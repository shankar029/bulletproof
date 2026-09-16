import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import http from 'node:http';
import { start } from '../src/main.mjs';
import { directory } from './helpers.mjs';

async function api(t) {
  const path = await directory(t);
  const app = await start({ directory: path, port: 0 });
  t.after(() => app.close());
  let revision = 0;
  async function request(route, method = 'GET', input, headers = {}) {
    const response = await fetch(`${app.url}${route}`, {
      method, signal: AbortSignal.timeout(5000),
      headers: { ...(method !== 'GET' ? { 'Content-Type': 'application/json', 'If-Match': `"${revision}"` } : {}), ...headers },
      body: input === undefined ? undefined : JSON.stringify(input),
    });
    const value = await response.json();
    if (response.ok) {
      assert.equal(response.headers.get('etag'), `"${value.revision}"`);
      revision = value.revision;
    }
    assert.equal(response.headers.get('cache-control'), 'no-store');
    return { response, value };
  }
  return { app, request };
}

test('real HTTP commits metadata with exact revision headers', async t => {
  const { app, request } = await api(t);
  assert.deepEqual((await request('/api/health')).value, { status: 'ok', schemaVersion: 1, revision: 0 });
  const project = (await request('/api/projects', 'POST', { name: 'Launch' })).value.project;
  const created = await request('/api/tasks', 'POST', { projectId: project.id, title: 'Draft' });
  assert.equal(created.response.status, 201);
  const changed = await request(`/api/tasks/${created.value.task.id}`, 'PATCH', { title: 'Ready draft', description: '<script>alert(1)</script>' });
  assert.equal(changed.response.status, 200);
  assert.equal(changed.value.task.description, '<script>alert(1)</script>');
  assert.equal(JSON.parse(await readFile(app.store.path)).revision, 3);
  assert.equal((await request('/api/tasks')).value.items[0].title, 'Ready draft');
});

test('HTTP rejects malformed revision JSON media type and local origin', async t => {
  const { app, request } = await api(t);
  const cases = [
    [{ 'If-Match': '1' }, 400, 'INVALID_REVISION'],
    [{ 'If-Match': '"9007199254740992"' }, 400, 'INVALID_REVISION'],
    [{ 'If-Match': '"1"' }, 409, 'REVISION_CONFLICT'],
    [{ 'Content-Type': 'text/plain' }, 415, 'UNSUPPORTED_MEDIA_TYPE'],
    [{ Origin: 'http://evil.example' }, 403, 'FORBIDDEN_ORIGIN'],
  ];
  for (const [headers, status, code] of cases) {
    const { response, value } = await request('/api/projects', 'POST', { name: 'No' }, headers);
    assert.equal(response.status, status);
    assert.equal(value.error.code, code);
  }
  const hostileHost = await new Promise((resolve, reject) => {
    const req = http.get(`${app.url}/api/health`, { headers: { Host: 'evil.example' }, timeout: 5000 }, res => {
      let data = '';
      res.on('data', bytes => { data += bytes; });
      res.on('end', () => resolve({ status: res.statusCode, body: JSON.parse(data) }));
    });
    req.on('error', reject);
    req.on('timeout', () => req.destroy(new Error('HTTP timeout')));
  });
  assert.equal(hostileHost.status, 403);
  assert.equal(hostileHost.body.error.code, 'FORBIDDEN_ORIGIN');
  for (const [body, headers, status, code] of [
    ['{}', { 'Content-Type': 'application/json' }, 428, 'PRECONDITION_REQUIRED'],
    ['{', { 'Content-Type': 'application/json', 'If-Match': '"0"' }, 400, 'BAD_JSON'],
    ['"' + 'x'.repeat(65536) + '"', { 'Content-Type': 'application/json', 'If-Match': '"0"' }, 413, 'BODY_TOO_LARGE'],
  ]) {
    const res = await fetch(`${app.url}/api/projects`, { method: 'POST', headers, body, signal: AbortSignal.timeout(5000) });
    assert.equal(res.status, status);
    assert.equal((await res.json()).error.code, code);
  }
  assert.equal(app.store.read().revision, 0);
});

test('static allowlist and method boundary expose no data', async t => {
  const { app, request } = await api(t);
  for (const path of ['/data/planner.json', '/src/store.mjs', '/writer.lock', '/nope']) {
    const { response, value } = await request(path);
    assert.equal(response.status, 404);
    assert.equal(value.error.code, 'NOT_FOUND');
    assert.ok(!JSON.stringify(value).includes(app.store.directory));
  }
  const response = await fetch(app.url, { signal: AbortSignal.timeout(5000) });
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-security-policy'), /frame-ancestors 'none'/);
  assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
  const wrongMethod = await fetch(`${app.url}/api/tasks`, { method: 'DELETE', signal: AbortSignal.timeout(5000) });
  assert.equal(wrongMethod.status, 405);
  assert.equal(wrongMethod.headers.get('allow'), 'GET, POST');
});
