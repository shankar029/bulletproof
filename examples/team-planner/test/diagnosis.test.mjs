import test from 'node:test';
import assert from 'node:assert/strict';
import { start } from '../src/main.mjs';
import { cleanup, directory } from './helpers.mjs';

test('an excluded first task cannot consume the first filtered page', async t => {
  const app = await start({ directory: await directory(t), port: 0 });
  cleanup(t, () => app.close());
  let revision = 0;
  async function write(path, body, method = 'POST') {
    const response = await fetch(`${app.url}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', 'If-Match': `"${revision}"` },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(5000),
    });
    assert.equal(response.status, method === 'POST' ? 201 : 200);
    const result = await response.json();
    revision = result.revision;
    return result;
  }
  const { project } = await write('/api/projects', { name: 'Minimum reproduction' });
  const { task: excluded } = await write('/api/tasks', { projectId: project.id, title: 'Already done' });
  await write(`/api/tasks/${excluded.id}`, { status: 'done' }, 'PATCH');
  const { task: wanted } = await write('/api/tasks', { projectId: project.id, title: 'Still todo' });
  const response = await fetch(`${app.url}/api/tasks?projectId=${project.id}&status=todo&page=1&pageSize=1`, {
    signal: AbortSignal.timeout(5000),
  });
  assert.equal(response.status, 200);
  const page = await response.json();
  assert.deepEqual(page.items.map(task => task.id), [wanted.id]);
  assert.equal(page.total, 1);
  assert.equal(page.totalPages, 1);
  assert.equal(page.pageSize, 1);
});
