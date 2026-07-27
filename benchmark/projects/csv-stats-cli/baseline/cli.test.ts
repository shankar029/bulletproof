import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';

test('prints stats for a simple file', () => {
  const fix = path.join(import.meta.dirname, '../oracle/fixtures/data.csv');
  const r = spawnSync(process.execPath, [path.join(import.meta.dirname, 'cli.ts'), fix], { encoding: 'utf8' });
  assert.ok(JSON.parse(r.stdout).columns);
});
