import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { start } from '../src/main.mjs';
import { selectTasks } from '../src/rules.mjs';

const root = join(import.meta.dirname, '..');
const snapshot = JSON.parse(await readFile(join(root, 'test', 'fixtures', 'planner-v1.json')));
await mkdir(join(root, '.work'), { recursive: true });
const results = [];
async function observe(label, query, expectedIds, expectedTotal) {
  const directory = await mkdtemp(join(root, '.work', 'probe-'));
  let app;
  try {
    await writeFile(join(directory, 'planner.json'), JSON.stringify(snapshot));
    app = await start({ directory, port: 0 });
    const response = await fetch(`${app.url}/api/tasks?${new URLSearchParams(query)}`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) throw new Error(`Probe HTTP failure ${response.status}: ${await response.text()}`);
    const http = await response.json();
    const direct = selectTasks(app.store.read(), query);
    const summarize = result => ({ ids: result.items.map(task => task.id), total: result.total });
    results.push({
      label, tasks: snapshot.tasks.map(task => task.id), projects: snapshot.projects.map(project => project.id),
      query, expected: { ids: expectedIds, total: expectedTotal },
      http: summarize(http), direct: summarize(direct),
    });
  } finally {
    await app?.close();
    await rm(directory, { recursive: true, force: true });
  }
}
const query = { projectId: 'p-1', status: 'todo', page: '1', pageSize: '1' };
await observe('original second page', { ...query, page: '2', pageSize: '2' }, ['t-7', 't-8'], 4);
await observe('same seven tasks, first page', { ...query, pageSize: '2' }, ['t-4', 't-6'], 4);
await observe('seven tasks', query, ['t-4'], 4);
for (const [id, label, total] of [
  ['t-9', 'remove other-project task G', 4],
  ['t-7', 'remove dependent task E', 3],
  ['t-6', 'remove unrelated todo D', 2],
  ['t-5', 'remove in-progress task C', 2],
  ['t-8', 'remove unrelated todo F', 1],
]) {
  snapshot.tasks = snapshot.tasks.filter(task => task.id !== id);
  await observe(label, query, ['t-4'], total);
}
snapshot.projects = snapshot.projects.filter(project => project.id !== 'p-2');
await observe('remove now-empty project Beta', query, ['t-4'], 1);
await observe('same two tasks, page size two control', { ...query, pageSize: '2' }, ['t-4'], 1);
console.log(JSON.stringify(results));
