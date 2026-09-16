import assert from 'node:assert/strict';

export async function seedQuery(url) {
  let revision = (await (await fetch(`${url}/api/health`, { signal: AbortSignal.timeout(5000) })).json()).revision;
  const requests = [];
  async function write(path, body, method = 'POST') {
    const response = await fetch(`${url}${path}`, {
      method, headers: { 'Content-Type': 'application/json', 'If-Match': `"${revision}"` },
      body: JSON.stringify(body), signal: AbortSignal.timeout(5000),
    });
    const result = await response.json();
    requests.push({ path, method, body, status: response.status, result });
    assert.equal(response.status, method === 'POST' ? 201 : 200, JSON.stringify(result));
    revision = result.revision;
    return result;
  }
  const alpha = (await write('/api/projects', { name: 'Alpha' })).project;
  const beta = (await write('/api/projects', { name: 'Beta' })).project;
  const labels = {};
  const rows = [
    ['A', alpha, 'Archive brief', 'done'],
    ['B', alpha, 'Build outline', 'todo'],
    ['C', alpha, 'Check links', 'in_progress'],
    ['D', alpha, 'Draft launch', 'todo'],
    ['E', alpha, 'Edit launch', 'todo'],
    ['F', alpha, 'Finalize launch', 'todo'],
    ['G', beta, 'Gather launch', 'todo'],
  ];
  for (const [label, project, title, status] of rows) {
    const task = (await write('/api/tasks', { projectId: project.id, title, description: `Fixture ${label}`, ...(label === 'E' ? { dependencyIds: [labels.B] } : {}) })).task;
    labels[label] = task.id;
    if (status !== 'todo') await write(`/api/tasks/${task.id}`, { status }, 'PATCH');
  }
  return { alpha, beta, labels, revision, requests, write };
}
