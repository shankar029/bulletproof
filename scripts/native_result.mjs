// Node >=22 native custom reporter contract:
// https://nodejs.org/docs/latest-v22.x/api/test.html#custom-reporters
// Only runner events are evidence. Child stdout/stderr remains quoted log data.
// The protocol is deliberately independent of Python and the workflow ledger.
import { inspect } from 'node:util';
import path from 'node:path';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import * as nodeModule from 'node:module';
import { fileURLToPath } from 'node:url';

const OUTCOMES = new Set(['pass', 'assertion-fail', 'setup-error', 'cancelled', 'skipped', 'todo']);
const empty = () => ({ schema_version: 1, complete: false, tests: [], leaf_count: 0, logs: [] });
const identity = (t) => JSON.stringify([t.file, t.line, t.name, t.nesting]);

function errorRecord(error) {
  if (!error) return undefined;
  const cause = error.cause && typeof error.cause === 'object' ? error.cause : error;
  return {
    name: cause.name || '', code: error.code || '', cause_code: cause.code || '',
    message: String(cause.message || error.message || ''),
    assertion_stack: String(cause.stack || ''),
    operator: typeof cause.operator === 'string' ? cause.operator : null,
    expected: inspect(cause.expected), actual: inspect(cause.actual),
  };
}

function outcome(data) {
  if (data.skip) return 'skipped';
  if (data.todo) return 'todo';
  const error = data.details?.error;
  if (!error) return 'pass';
  if (error.failureType === 'cancelledByParent' || error.failureType === 'testTimeoutFailure') return 'cancelled';
  const cause = errorRecord(error);
  if (error.failureType === 'testCodeFailure' && cause.name === 'AssertionError' &&
      cause.cause_code === 'ERR_ASSERTION' && cause.operator && cause.assertion_stack) return 'assertion-fail';
  return 'setup-error';
}

export default async function* report(source) {
  const result = empty();
  const terminals = [];
  let plan = false;
  let invalid = false;
  for await (const { type, data } of source) {
    if (type === 'test:stdout' || type === 'test:stderr') {
      result.logs.push({ stream: type.slice(5), text: String(data.message) });
    } else if (type === 'test:plan' && data.nesting === 0 && !data.file) {
      plan = true;
    } else if (type === 'test:pass' || type === 'test:fail') {
      if (!data.file || !Number.isInteger(data.line) || !Number.isInteger(data.nesting) ||
          !['test', 'suite'].includes(data.details?.type)) {
        invalid = true;
        continue;
      }
      const wrapper = path.resolve(data.name) === path.resolve(data.file) && data.line === 1 && data.column === 1;
      const previous = terminals.at(-1);
      const container = data.details.type === 'suite' || wrapper ||
        (previous?.file === data.file && previous.nesting > data.nesting);
      // Container subtestsFailed only reflects its children; hook/file failures do not.
      if (container && type === 'test:fail' &&
          data.details.error?.failureType !== 'subtestsFailed') invalid = true;
      if (wrapper && type === 'test:fail') invalid = true;
      terminals.push({ file: data.file, line: data.line, name: data.name, nesting: data.nesting,
        outcome: outcome(data), ...(data.details.error ? { error: errorRecord(data.details.error) } : {}),
        container });
    }
  }
  result.tests = terminals.filter((t) => !t.container).map(({ container, ...t }) => t);
  result.leaf_count = result.tests.length;
  result.complete = plan && !invalid;
  yield JSON.stringify(result) + '\n';
}

/** Malformed/truncated output is unavailable, never a fabricated green suite. */
export function parseReport(text) {
  try {
    const value = JSON.parse(text);
    if (value?.schema_version !== 1 || typeof value.complete !== 'boolean' ||
        !Array.isArray(value.tests) || value.leaf_count !== value.tests.length ||
        !Array.isArray(value.logs) || !value.logs.every((l) =>
          ['stdout', 'stderr'].includes(l.stream) && typeof l.text === 'string') ||
        !value.tests.every((t) => typeof t.file === 'string' && t.file &&
          Number.isInteger(t.line) && t.line > 0 && typeof t.name === 'string' &&
          Number.isInteger(t.nesting) && t.nesting >= 0 && OUTCOMES.has(t.outcome) &&
          (t.outcome !== 'assertion-fail' || (t.error?.name === 'AssertionError' &&
            t.error.cause_code === 'ERR_ASSERTION' && typeof t.error.operator === 'string' &&
            typeof t.error.assertion_stack === 'string' && t.error.assertion_stack)))) return empty();
    return value;
  } catch {
    return empty();
  }
}

/** Shared grading policy; baseline inventory is required, not just a positive count. */
export function classifyResult(result, rc, baseline = null) {
  if (rc === 124 || rc === 125 || rc === null) return 'timeout';
  if (!result.complete || !result.leaf_count) return 'unclassified';
  if (result.tests.some((t) => ['setup-error', 'cancelled'].includes(t.outcome))) return 'setup-error';
  if (result.tests.some((t) => ['skipped', 'todo'].includes(t.outcome))) return 'unclassified';
  if (baseline) {
    const expected = baseline.tests.map(identity).sort();
    const actual = result.tests.map(identity).sort();
    if (JSON.stringify(expected) !== JSON.stringify(actual)) return 'unclassified';
  }
  if (rc !== 0 && result.tests.some((t) => t.outcome === 'assertion-fail')) return 'killed-assertion';
  if (rc === 0 && result.tests.every((t) => t.outcome === 'pass')) return 'survived';
  return 'unclassified';
}

/** Node 24 --check accepts malformed .ts without parsing it. Ask its native TS
 * parser too; older Node versions without that API report unsupported, not green.
 * No imports or product code execute in either syntax preflight. */
export function checkSyntax(file) {
  try {
    if (path.extname(file) === '.ts') {
      if (typeof nodeModule.stripTypeScriptTypes !== 'function') {
        return { status: 2, stdout: '', stderr: 'Native TypeScript syntax preflight unavailable' };
      }
      nodeModule.stripTypeScriptTypes(readFileSync(file, 'utf8'));
    }
    const { NODE_TEST_CONTEXT, ...env } = process.env;
    const result = spawnSync(process.execPath, ['--check', file], {
      env, encoding: 'utf8', timeout: 30_000,
    });
    return { status: result.status ?? 125, stdout: result.stdout || '', stderr: result.stderr || '' };
  } catch (error) {
    return { status: error instanceof SyntaxError ? 1 : 2, stdout: '', stderr: String(error) };
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv[2] !== '--check' || process.argv.length !== 4) {
    process.stderr.write('Use native_result.mjs --check FILE\n');
    process.exitCode = 2;
  } else {
    const result = checkSyntax(process.argv[3]);
    process.stdout.write(result.stdout);
    process.stderr.write(result.stderr);
    process.exitCode = result.status;
  }
}
