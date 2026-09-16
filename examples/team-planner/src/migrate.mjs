import { JsonStore } from './store.mjs';
import { options } from './main.mjs';

let store;
try {
  const config = options(process.argv.slice(2), false);
  store = await JsonStore.open({ ...config, createIfMissing: false });
  console.log(JSON.stringify(await store.migrateToV2()));
} catch (error) {
  console.error(`${error.code ?? 'MIGRATION_FAILED'}: ${error.message}`);
  process.exitCode = 1;
} finally {
  await store?.close();
}
