import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { start } from '../src/main.mjs';
import { directory, cleanup } from './helpers.mjs';

async function api(t) {
  const path = await directory(t);
  const app = await start({ directory: path, port: 0 });
  cleanup(t, () => app.close());
  async function request(route, method = 'GET', input, headers = {}) {
    return fetch(app.url + route, {
      method, signal: AbortSignal.timeout(5000),
      headers: { 'Content-Type': 'application/json', 'If-Match': `"${app.store.read().revision}"`, ...headers },
      body: input === undefined ? undefined : JSON.stringify(input),
    });
  }
  return { app, request };
}

test('archive lifecycle PATCH succeeds for mixed-status project', async t => {
  const { app, request } = await api(t);
  const { project } = await (await request('/api/projects', 'POST', { name: 'Release' })).json();
  for (const status of ['todo', 'in_progress', 'done']) {
    const { task } = await (await request('/api/tasks', 'POST', { projectId: project.id, title: status })).json();
    if (status !== 'todo') assert.equal((await request(`/api/tasks/${task.id}`, 'PATCH', { status })).status, 200);
  }
  const tasks = app.store.read().tasks;
  const response = await request(`/api/projects/${project.id}`, 'PATCH', { archived: true });
  assert.equal(response.status, 200);
  const archived = await response.json();
  assert.equal(archived.project.archived, true);
  assert.deepEqual(app.store.read().tasks, tasks);
  assert.equal(response.headers.get('etag'), `"${archived.revision}"`);
  assert.deepEqual((await (await request('/api/projects')).json()).items, []);
  assert.equal((await (await request('/api/projects?archived=true')).json()).items[0].id, project.id);
  assert.deepEqual((await (await request(`/api/projects/${project.id}`)).json()), archived);
  assert.equal((await (await request(`/api/tasks?projectId=${project.id}&pageSize=2`)).json()).total, 3);
  assert.equal((await (await request('/api/dashboard')).json()).total, 3);
  assert.equal((await request(`/api/projects/${project.id}`, 'PATCH', { archived: false })).status, 200);
  assert.equal((await (await request('/api/projects')).json()).items.length, 1);
});

test('archive HTTP boundaries reject malformed writes and queries without data changes', async t => {
  const { app, request } = await api(t);
  const { project } = await (await request('/api/projects', 'POST', { name: 'Strict' })).json();
  const path = `/api/projects/${project.id}`;
  const before = await readFile(app.store.path, 'utf8');
  for (const input of [{}, { archived: 'true' }, { archived: null }, { archived: 1 }, { archived: [] }, { archived: true, name: 'bad' }]) {
    assert.equal((await request(path, 'PATCH', input)).status, 400);
  }
  for (const route of ['/api/projects?archived=1', '/api/projects?archived=true&archived=false', `${path}?q=a`, `${path}/tasks.csv?page=1`, '/?archived=1']) {
    assert.equal((await request(route)).status, 400, route);
  }
  assert.equal((await request(path, 'PATCH', { archived: true }, { 'If-Match': '"0"' })).status, 409);
  assert.equal((await request(path, 'PATCH', { archived: true }, { Origin: 'https://evil.example' })).status, 403);
  assert.equal((await request(path, 'PATCH', { archived: true }, { 'Content-Type': 'text/plain' })).status, 415);
  const noRevision = await fetch(app.url + path, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: '{"archived":true}' });
  assert.equal(noRevision.status, 428);
  for (const [route, allow] of [[path, 'GET, PATCH'], [`${path}/tasks.csv`, 'GET']]) {
    const response = await request(route, 'DELETE');
    assert.equal(response.status, 405);
    assert.equal(response.headers.get('allow'), allow);
  }
  for (const route of ['/api/projects/p-999', '/api/projects/p-999/tasks.csv', '/api/projects/p-01', '/api/projects/p-9007199254740992']) {
    assert.equal((await request(route)).status, 404);
  }
  assert.equal(await readFile(app.store.path, 'utf8'), before);
});

test('CSV HTTP exports all rows with safe download headers before and after archive', async t => {
  const { app, request } = await api(t);
  const { project } = await (await request('/api/projects', 'POST', { name: '=Launch' })).json();
  const route = `/api/projects/${project.id}/tasks.csv`;
  const empty = await request(route);
  assert.equal(empty.status, 200);
  const header = await empty.text();
  assert.equal(header, '"projectId","projectName","id","title","description","status","priority","dependencyIds","blocked","createdOrder"\r\n');
  for (let i = 0; i < 51; i++) {
    assert.equal((await request('/api/tasks', 'POST', { projectId: project.id, title: `Task ${i}`, description: 'Unicode \u65e5\u672c \ud83d\ude80,\n"quoted"' })).status, 201);
  }
  let csv;
  for (const archived of [false, true]) {
    if (archived) await request(`/api/projects/${project.id}`, 'PATCH', { archived: true });
    const before = await readFile(app.store.path, 'utf8');
    const response = await request(route);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('content-type'), 'text/csv; charset=utf-8');
    assert.equal(response.headers.get('content-disposition'), `attachment; filename="project-${project.id}-tasks.csv"`);
    assert.equal(response.headers.get('cache-control'), 'no-store');
    assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
    assert.equal(response.headers.get('etag'), `"${app.store.read().revision}"`);
    const text = await response.text();
    assert.equal(text.startsWith(header), true);
    assert.equal(text.includes('"Task 50"'), true);
    assert.equal(text.includes("\"'=Launch\""), true);
    assert.equal(text.includes('Unicode \u65e5\u672c \ud83d\ude80,\n""quoted""'), true);
    if (csv) assert.equal(text, csv);
    csv = text;
    assert.equal(await readFile(app.store.path, 'utf8'), before);
  }
});
