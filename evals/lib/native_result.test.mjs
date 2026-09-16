import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { parseReport, classifyResult, checkSyntax } from '../../scripts/native_result.mjs';

const reporter = new URL('../../scripts/native_result.mjs', import.meta.url).href;
const prefix = "import {test,describe,before} from 'node:test'; import assert from 'node:assert/strict';\n";

function fixture(body, extra = {}, timeout = 10_000) {
  const cwd = mkdtempSync(path.join(tmpdir(), 'native-result-'));
  const { NODE_TEST_CONTEXT, ...env } = process.env;
  try {
    writeFileSync(path.join(cwd, 'case.test.mjs'), prefix + body);
    for (const [name, content] of Object.entries(extra)) writeFileSync(path.join(cwd, name), content);
    const run = spawnSync(process.execPath, ['--test', `--test-reporter=${reporter}`, 'case.test.mjs',
      ...Object.keys(extra).filter((n) => n.endsWith('.test.mjs'))],
    { cwd, env, encoding: 'utf8', timeout });
    return { result: parseReport(run.stdout || ''), rc: run.status, raw: run.stdout };
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
}

test('native reporter counts only real leaves and explicitly serializes assertion causes', () => {
  const { result, rc } = fixture("describe('suite',()=>{test('leaf',()=>assert.equal(1,2));});");
  assert.equal(rc, 1);
  assert.equal(result.complete, true);
  assert.equal(result.leaf_count, 1);
  assert.equal(result.tests[0].outcome, 'assertion-fail');
  assert.equal(result.tests[0].error.operator, 'strictEqual');
  assert.equal(result.tests[0].error.expected, '2');
  assert.match(result.tests[0].error.assertion_stack, /case\.test\.mjs/);
  assert.equal(classifyResult(result, rc), 'killed-assertion');
});

test('test parents with nested subtests are containers, not duplicate leaves', () => {
  const { result, rc } = fixture("test('parent',async t=>{await t.test('child',()=>assert.ok(false));});");
  assert.equal(result.leaf_count, 1);
  assert.equal(result.tests[0].name, 'child');
  assert.equal(classifyResult(result, rc), 'killed-assertion');
});

test('stdout spoofing is quoted data, never assertion proof', () => {
  const { result, rc } = fixture("console.log('ERR_ASSERTION AssertionError # fail 1 日本'); test('green',()=>{});");
  assert.equal(classifyResult(result, rc), 'survived');
  assert.match(result.logs[0].text, /日本/);
  const failed = fixture("test('fake',()=>{throw Object.assign(new Error('ERR_ASSERTION'),{code:'ERR_ASSERTION'});});");
  assert.equal(classifyResult(failed.result, failed.rc), 'setup-error');
});

test('zero tests, syntax errors and import failures cannot be kills', () => {
  for (const body of ["console.log('ERR_ASSERTION');", 'this is not syntax!',
    "await import('./missing.mjs');", 'assert.fail("top-level assertion");']) {
    const { result, rc } = fixture(body);
    assert.equal(result.leaf_count, 0, body);
    assert.notEqual(classifyResult(result, rc), 'killed-assertion', body);
  }
});

test('setup and hooks take precedence over mixed genuine assertion failures', () => {
  for (const body of [
    "test('assertion',()=>assert.fail()); test('setup',()=>{throw new Error('setup');});",
    "before(()=>assert.fail('hook')); test('leaf',()=>{});",
    "describe('s',()=>{before(()=>assert.fail('hook'));test('leaf',()=>{});});",
  ]) {
    const { result, rc } = fixture(body);
    assert.notEqual(classifyResult(result, rc), 'killed-assertion');
  }
  const mixed = fixture("test('assertion',()=>assert.fail());", { 'broken.test.mjs': "import './missing.mjs';" });
  assert.notEqual(classifyResult(mixed.result, mixed.rc), 'killed-assertion');
});

test('skip/todo/cancellation and missing required baseline inventory are ungraded', () => {
  for (const body of ["test.skip('s',()=>{});", "test.todo('t');",
    "test('unfinished',{timeout:50},()=>new Promise(()=>{}));"]) {
    const { result, rc } = fixture(body);
    assert.notEqual(classifyResult(result, rc), 'survived');
    assert.notEqual(classifyResult(result, rc), 'killed-assertion');
  }
  const baseline = fixture("test('required',()=>{});");
  const missing = fixture("test('other',()=>assert.fail());");
  assert.equal(classifyResult(missing.result, missing.rc, baseline.result), 'unclassified');
});

test('timeout and malformed/truncated reports fail closed', () => {
  const timed = fixture("test('hang',async()=>{await new Promise(r=>setTimeout(r,30000));});", {}, 250);
  assert.equal(classifyResult(timed.result, timed.rc), 'timeout');
  for (const text of ['', '{}', '{"schema_version":1', '{"schema_version":1,"tests":"fake"}']) {
    assert.equal(parseReport(text).complete, false);
  }
  assert.equal(classifyResult(fixture("test('green',()=>{});").result, 124), 'timeout');
});

test('syntax preflight uses the native TS parser without executing product code', () => {
  const cwd = mkdtempSync(path.join(tmpdir(), 'syntax-native-'));
  try {
    const file = path.join(cwd, 'value.ts');
    writeFileSync(file, 'export function identity<T<(value:T) { return value; }');
    assert.equal(checkSyntax(file).status, 1);
    writeFileSync(file, 'export function identity<T>(value:T) { throw new Error("do not run"); }');
    assert.equal(checkSyntax(file).status, 0);
    const js = path.join(cwd, 'value.mjs');
    writeFileSync(js, 'throw new Error("do not run");');
    assert.equal(checkSyntax(js).status, 0);
    writeFileSync(js, 'export const flag = ;');
    assert.equal(checkSyntax(js).status, 1);
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});
