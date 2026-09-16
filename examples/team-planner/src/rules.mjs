import { AppError, invalid } from './errors.mjs';

export const statuses = ['todo', 'in_progress', 'done'];
export const priorities = ['low', 'normal', 'high'];

export function validateDependencies(model, taskId, ids) {
  const task = model.tasks.find(task => task.id === taskId);
  if (!Array.isArray(ids) || new Set(ids).size !== ids.length) invalid('Dependencies must be unique task IDs', 'dependencyIds');
  const byId = new Map(model.tasks.map(task => [task.id, task]));
  for (const id of ids) {
    const dependency = byId.get(id);
    if (!dependency || id === taskId || dependency.projectId !== task.projectId) invalid('Choose other tasks in the same project', 'dependencyIds');
  }
}

export function validateGraph(model) {
  const byId = new Map(model.tasks.map(task => [task.id, task]));
  for (const task of model.tasks) validateDependencies(model, task.id, task.dependencyIds);
  const visited = new Set(), visiting = new Set();
  function visit(id) {
    if (visiting.has(id)) throw new AppError('DEPENDENCY_CYCLE', 'Dependencies cannot form a cycle', 409, 'dependencyIds');
    if (visited.has(id)) return;
    visiting.add(id);
    for (const dependency of byId.get(id).dependencyIds) visit(dependency);
    visiting.delete(id);
    visited.add(id);
  }
  for (const task of model.tasks) visit(task.id);
  for (const task of model.tasks) {
    if (task.status !== 'todo' && task.dependencyIds.some(id => byId.get(id).status !== 'done')) throw new AppError('DEPENDENCIES_INCOMPLETE', 'Complete dependencies before starting or completing this task', 409, 'dependencyIds');
  }
}

export function transition(model, id, oldStatus) {
  const task = model.tasks.find(task => task.id === id);
  if (task.status === oldStatus) return;
  if (oldStatus === 'done' && task.status === 'in_progress') throw new AppError('INVALID_TRANSITION', 'Reopen a completed task to todo first', 409, 'status');
  if (task.status === 'todo' && model.tasks.some(dependent => dependent.dependencyIds.includes(id) && dependent.status !== 'todo')) throw new AppError('ACTIVE_DEPENDENTS', 'Reopen active dependent tasks first', 409, 'status');
}

export function taskView(model, task) {
  return { ...task, blocked: task.status === 'todo' && task.dependencyIds.some(id => model.tasks.find(dependency => dependency.id === id).status !== 'done') };
}

export function selectTasks(model, query = {}) {
  const fail = field => { throw new AppError('INVALID_QUERY', `Invalid ${field} query`, 400, field); };
  if (!query || typeof query !== 'object' || Array.isArray(query)) fail('query');
  for (const key of Object.keys(query)) if (!['projectId', 'status', 'priority', 'q', 'page', 'pageSize'].includes(key)) fail(key);
  for (const [key, values] of [['status', statuses], ['priority', priorities]]) {
    if (Object.hasOwn(query, key) && !values.includes(query[key])) fail(key);
  }
  if (Object.hasOwn(query, 'projectId')) {
    if (typeof query.projectId !== 'string' || !/^p-[1-9][0-9]*$/.test(query.projectId) || !Number.isSafeInteger(Number(query.projectId.slice(2)))) fail('projectId');
    if (!model.projects.some(project => project.id === query.projectId)) throw new AppError('NOT_FOUND', 'Project not found', 404);
  }
  if (Object.hasOwn(query, 'q') && (typeof query.q !== 'string' || [...query.q.trim()].length > 160)) fail('q');
  const q = (query.q ?? '').trim().toLowerCase();
  function integer(key, fallback, max) {
    if (!Object.hasOwn(query, key)) return fallback;
    const value = query[key];
    if (!/^[1-9][0-9]*$/.test(String(value)) || !Number.isSafeInteger(Number(value)) || Number(value) > max) fail(key);
    return Number(value);
  }
  const page = integer('page', 1, Number.MAX_SAFE_INTEGER);
  const pageSize = integer('pageSize', 10, 50);
  if (model.schemaVersion === 1 && query.priority && query.priority !== 'normal') throw new AppError('MIGRATION_REQUIRED', 'Migrate this store before using priorities', 409);
  const matches = model.tasks.filter(task =>
    (!query.projectId || task.projectId === query.projectId) &&
    (!query.status || task.status === query.status) &&
    (!query.priority || task.priority === query.priority) &&
    (!q || task.title.toLowerCase().includes(q))
  ).sort((left, right) => left.createdOrder - right.createdOrder);
  const total = matches.length;
  const items = matches.slice((page - 1) * pageSize, page * pageSize).map(task => taskView(model, task));
  return { items, total, page, pageSize, totalPages: Math.ceil(total / pageSize), revision: model.revision };
}

export function summarize(model, projectId) {
  if (projectId !== undefined) selectTasks(model, { projectId });
  const tasks = model.tasks.filter(task => projectId === undefined || task.projectId === projectId);
  const done = tasks.filter(task => task.status === 'done').length;
  return {
    total: tasks.length,
    todo: tasks.filter(task => task.status === 'todo').length,
    inProgress: tasks.filter(task => task.status === 'in_progress').length,
    done,
    blocked: tasks.filter(task => taskView(model, task).blocked).length,
    completionPercent: tasks.length ? Math.floor(100 * done / tasks.length) : 0,
    revision: model.revision,
  };
}
