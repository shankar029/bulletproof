import { rename } from 'node:fs/promises';
import { JsonStore } from '../src/store.mjs';
import { Planner } from '../src/planner.mjs';

const [directory, checkpoint] = process.argv.slice(2);
const store = await JsonStore.open({ directory, commitFile: async (stage, target) => {
  if (checkpoint === 'before') {
    process.send({ checkpoint: 'before', stage });
    await new Promise(resolve => process.once('message', resolve));
  }
  await rename(stage, target);
} });
const result = await new Planner(store).createProject({ name: 'Crash commit' }, store.read().revision);
process.send({ checkpoint: 'after', result });
await new Promise(resolve => process.once('message', resolve));
await store.close();
