import { mkdir, mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { JsonStore } from '../src/store.mjs';
import { Planner } from '../src/planner.mjs';

export const root = join(import.meta.dirname, '..');
export async function directory(t) {
  await mkdir(join(root, '.work'), { recursive: true });
  const path = await mkdtemp(join(root, '.work', 'test-'));
  t.after(() => rm(path, { recursive: true, force: true }));
  return path;
}
export async function fixture(t, options = {}) {
  const path = await directory(t);
  const store = await JsonStore.open({ directory: path, ...options });
  t.after(() => store.close());
  return { store, planner: new Planner(store), directory: path };
}
export function code(expected) {
  return error => error.code === expected;
}
