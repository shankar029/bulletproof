import { test } from 'node:test';
import assert from 'node:assert/strict';
import { newId } from './index.ts';

test('newId returns unique, non-empty strings', () => {
  const ids = new Set<string>();
  for (let i = 0; i < 5000; i++) {
    const id = newId();
    assert.ok(typeof id === 'string' && id.length > 0);
    ids.add(id);
  }
  assert.equal(ids.size, 5000);
});
