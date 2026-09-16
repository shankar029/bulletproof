import { mkdir, mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { JsonStore } from '../src/store.mjs';
import { Planner } from '../src/planner.mjs';

export const root = join(import.meta.dirname, '..');
const cleanups = new WeakMap();
export function cleanup(t, dispose) {
  if (!cleanups.has(t)) {
    const stack = [];
    cleanups.set(t, stack);
    t.after(async () => {
      const errors = [];
      while (stack.length) {
        try { await stack.pop()(); } catch (error) { errors.push(error); }
      }
      if (errors.length) throw new AggregateError(errors, 'Owned test cleanup failed');
    });
  }
  cleanups.get(t).push(dispose);
}
export async function directory(t) {
  await mkdir(join(root, '.work'), { recursive: true });
  const path = await mkdtemp(join(root, '.work', 'test-'));
  cleanup(t, () => rm(path, { recursive: true, force: true }));
  return path;
}
export async function fixture(t, options = {}) {
  const path = await directory(t);
  const store = await JsonStore.open({ directory: path, ...options });
  cleanup(t, () => store.close());
  return { store, planner: new Planner(store), directory: path };
}
export function code(expected) {
  return error => error.code === expected;
}
