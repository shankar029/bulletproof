import test from 'node:test';
import assert from 'node:assert/strict';
import { csvCell, projectCsv } from '../src/csv.mjs';
import { emptyModel } from '../src/schema.mjs';

// Independent state machine: quoted fields may contain separators and newlines.
function parse(csv) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < csv.length; i++) {
    const c = csv[i];
    if (quoted) {
      if (c === '"' && csv[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') quoted = false;
      else cell += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\r' && csv[i + 1] === '\n') {
      row.push(cell); rows.push(row); row = []; cell = ''; i++;
    } else throw new Error(`Unexpected unquoted CSV character ${c}`);
  }
  assert.equal(quoted, false);
  assert.equal(cell, '');
  assert.deepEqual(row, []);
  return rows;
}

test('CSV cells neutralize formula prefixes without changing harmless values or embedded text', () => {
  for (const prefix of ['', ' ', '\u00a0', '\ufeff', '\u0000', '\u0085', '\u200b', '\u2060', '\t', '\r\n']) {
    for (const operator of ['=', '+', '-', '@']) {
      const value = `${prefix}${operator}SUM(1,2)`;
      assert.equal(parse(csvCell(value) + '\r\n')[0][0], "'" + value);
    }
  }
  for (const value of ['\tplain', '\rplain', '\nplain']) assert.equal(parse(csvCell(value) + '\r\n')[0][0], "'" + value);
  for (const value of ['', "'=safe", 'benign + text', 'line\nnext', 'x,"y"\r\nz', '\u65e5\u672c \ud83d\ude80']) {
    assert.equal(parse(csvCell(value) + '\r\n')[0][0], value);
  }
  assert.equal(csvCell(true), '"true"');
  assert.equal(csvCell(false), '"false"');
  assert.equal(csvCell(42), '"42"');
});

test('project CSV is deterministic complete UTF8 with stable order and independently parsed fields', () => {
  const model = emptyModel();
  const project = { id: 'p-1', name: '@Team,"Unicode \u65e5"', createdOrder: 1 };
  model.projects.push(project);
  for (let i = 2; i <= 54; i++) model.tasks.push({
    id: `t-${i}`, projectId: 'p-1', title: i === 2 ? '=SUM(1,2)' : `Task ${i}`,
    description: 'Comma, quotes "test", \ud83d\ude80\nLF\rCR\r\nCRLF',
    status: 'todo', priority: i === 3 ? 'high' : 'normal', dependencyIds: i === 3 ? ['t-2'] : [], createdOrder: i,
  });
  const before = structuredClone(model);
  const csv = projectCsv(model, project);
  assert.deepEqual(model, before);
  assert.equal(Buffer.from(csv, 'utf8').toString('utf8'), csv);
  assert.equal(csv.charCodeAt(0), 34);
  const rows = parse(csv);
  assert.deepEqual(rows[0], ['projectId', 'projectName', 'id', 'title', 'description', 'status', 'priority', 'dependencyIds', 'blocked', 'createdOrder']);
  assert.equal(rows.length, 54);
  assert.deepEqual(rows[1], ['p-1', "'@Team,\"Unicode \u65e5\"", 't-2', "'=SUM(1,2)", model.tasks[0].description, 'todo', 'normal', '[]', 'false', '2']);
  assert.equal(rows[2][7], '["t-2"]');
  assert.equal(rows[2][8], 'true');
  assert.equal(rows.at(-1)[2], 't-54');
  model.tasks.reverse();
  project.archived = true;
  assert.equal(projectCsv(model, project), csv);
  assert.equal(projectCsv(model, project), csv);
  const other = { id: 'p-99', name: 'Empty', createdOrder: 99 };
  assert.deepEqual(parse(projectCsv(model, other)), [rows[0]]);
});
