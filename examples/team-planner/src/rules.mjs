import { AppError, invalid } from './errors.mjs';

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
