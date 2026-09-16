import { AppError, invalid } from './errors.mjs';
import { validateGraph } from './rules.mjs';
export { AppError, invalid } from './errors.mjs';

export const statuses = ['todo', 'in_progress', 'done'];
export const priorities = ['low', 'normal', 'high'];

export function object(input, allowed, required = []) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) invalid('Expected an object');
  for (const key of Object.keys(input)) if (!allowed.includes(key)) invalid(`Unknown field: ${key}`, key);
  for (const key of required) if (!Object.hasOwn(input, key)) invalid(`Missing field: ${key}`, key);
}

export function text(value, field, max, trim = true) {
  if (typeof value !== 'string') invalid('Must be text', field);
  const result = trim ? value.trim() : value;
  if ((trim && !result) || [...result].length > max) invalid(`Must contain ${trim ? '1' : '0'}–${max} characters`, field);
  return result;
}

export function choice(value, values, field) {
  if (!values.includes(value)) invalid(`Choose ${values.join(', ')}`, field);
  return value;
}

export function safeInteger(value, minimum, field) {
  if (!Number.isSafeInteger(value) || value < minimum) invalid('Must be a safe integer', field);
}

export function emptyModel() {
  return { schemaVersion: 1, revision: 0, nextId: 1, projects: [], tasks: [] };
}

export function validate(model) {
  object(model, ['schemaVersion', 'revision', 'nextId', 'projects', 'tasks'], ['schemaVersion', 'revision', 'nextId', 'projects', 'tasks']);
  if (model.schemaVersion !== 1) invalid('Unknown schema version', 'schemaVersion');
  safeInteger(model.revision, 0, 'revision');
  safeInteger(model.nextId, 1, 'nextId');
  if (!Array.isArray(model.projects) || !Array.isArray(model.tasks)) invalid('Invalid collections');
  if (model.projects.length > 100 || model.tasks.length > 2000) throw new AppError('CAPACITY_EXCEEDED', 'Dataset capacity exceeded', 409);
  const allocated = new Set();
  const names = new Set();
  function allocation(record, prefix) {
    safeInteger(record.createdOrder, 1, 'createdOrder');
    if (record.id !== `${prefix}-${record.createdOrder}` || record.createdOrder >= model.nextId || allocated.has(record.createdOrder)) invalid('Invalid or duplicate allocation');
    allocated.add(record.createdOrder);
  }
  for (const project of model.projects) {
    object(project, ['id', 'name', 'createdOrder'], ['id', 'name', 'createdOrder']);
    allocation(project, 'p');
    if (text(project.name, 'name', 80) !== project.name || names.has(project.name.toLowerCase())) invalid('Invalid or duplicate project name', 'name');
    names.add(project.name.toLowerCase());
  }
  for (const task of model.tasks) {
    object(task, ['id', 'projectId', 'title', 'description', 'status', 'dependencyIds', 'createdOrder', 'priority'], ['id', 'projectId', 'title', 'description', 'status', 'dependencyIds', 'createdOrder', 'priority']);
    allocation(task, 't');
    if (!model.projects.some(project => project.id === task.projectId)) invalid('Missing project', 'projectId');
    if (text(task.title, 'title', 160) !== task.title) invalid('Title must be trimmed', 'title');
    text(task.description, 'description', 2000, false);
    choice(task.status, statuses, 'status');
    choice(task.priority, priorities, 'priority');
  }
  validateGraph(model);
  return model;
}

export function decode(bytes) {
  let raw;
  try { raw = JSON.parse(bytes); } catch { invalid('Invalid stored JSON'); }
  object(raw, ['schemaVersion', 'revision', 'nextId', 'projects', 'tasks'], ['schemaVersion', 'revision', 'nextId', 'projects', 'tasks']);
  if (raw.schemaVersion !== 1 || !Array.isArray(raw.tasks)) invalid('Unknown or invalid schema', 'schemaVersion');
  const tasks = raw.tasks.map(task => {
    object(task, ['id', 'projectId', 'title', 'description', 'state', 'dependencyIds', 'createdOrder'], ['id', 'projectId', 'title', 'description', 'state', 'dependencyIds', 'createdOrder']);
    const { state, ...rest } = task;
    return { ...rest, status: state, priority: 'normal' };
  });
  return validate({ ...raw, tasks });
}

export function encode(model) {
  validate(model);
  const tasks = model.tasks.map(({ status, priority, ...task }) => ({ ...task, state: status }));
  return `${JSON.stringify({ ...model, tasks }, null, 2)}\n`;
}
