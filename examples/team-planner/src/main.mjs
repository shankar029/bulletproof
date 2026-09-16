import { resolve } from 'node:path';
import { JsonStore } from './store.mjs';
import { Planner } from './planner.mjs';
import { createServer } from './server.mjs';

export function options(args, allowPort = true) {
  const result = { directory: resolve('data'), port: 4317 };
  const seen = new Set();
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i], value = args[i + 1];
    if (!['--data-dir', ...(allowPort ? ['--port'] : [])].includes(key) || !value || seen.has(key)) throw new Error('Usage: --data-dir <directory>' + (allowPort ? ' --port <0..65535>' : ''));
    seen.add(key);
    if (key === '--data-dir') result.directory = resolve(value);
    else {
      if (!/^(0|[1-9][0-9]*)$/.test(value) || Number(value) > 65535) throw new Error('Port must be 0..65535');
      result.port = Number(value);
    }
  }
  return result;
}

export async function start(config) {
  const store = await JsonStore.open(config);
  const server = createServer({ planner: new Planner(store) });
  try {
    await new Promise((resolve, reject) => {
      server.once('error', reject);
      server.listen(config.port, '127.0.0.1', resolve);
    });
  } catch (error) {
    await store.close();
    throw error;
  }
  const url = `http://127.0.0.1:${server.address().port}`;
  let closing;
  return {
    url, server, store,
    close() {
      closing ??= (async () => {
        const timer = setTimeout(() => server.closeAllConnections(), 10000);
        try {
          await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
          await store.close();
        } finally { clearTimeout(timer); }
      })();
      return closing;
    },
  };
}

if (process.argv[1] && resolve(process.argv[1]) === import.meta.filename) {
  try {
    const app = await start(options(process.argv.slice(2)));
    console.log(JSON.stringify({ url: app.url, directory: app.store.directory, pid: process.pid }));
    const health = await fetch(`${app.url}/api/health`, { signal: AbortSignal.timeout(5000) });
    if (!health.ok) { await app.close(); throw new Error('Startup health check failed'); }
    for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => {
      app.close().catch(error => { console.error(error.message); process.exitCode = 1; });
    });
  } catch (error) {
    console.error(`${error.code ?? 'STARTUP_FAILED'}: ${error.message}`);
    process.exitCode = 1;
  }
}
