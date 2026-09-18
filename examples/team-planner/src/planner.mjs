import { AppError, invalid, object, text, choice, statuses, priorities } from './schema.mjs';
import { taskView, transition, validateDependencies, validateGraph, selectTasks, summarize } from './rules.mjs';
import { projectCsv } from './csv.mjs';

export function findTask(model, id) {
  const task = model.tasks.find(task => task.id === id);
  if (!task) throw new AppError('NOT_FOUND', 'Task not found', 404);
  return task;
}

export function findProject(model, id) {
  const project = model.projects.find(project => project.id === id);
  if (!project) throw new AppError('NOT_FOUND', 'Project not found', 404);
  return project;
}

function allocate(model, prefix) {
  if (model.nextId === Number.MAX_SAFE_INTEGER) throw new AppError('CAPACITY_EXCEEDED', 'Identifier capacity exceeded', 409);
  const createdOrder = model.nextId++;
  return { id: `${prefix}-${createdOrder}`, createdOrder };
}

function projectView(project) {
  return { ...project, archived: project.archived === true };
}

function assertProjectWritable(model, projectId) {
  const project = findProject(model, projectId);
  if (project.archived === true) throw new AppError('PROJECT_ARCHIVED', 'Project is archived; restore it before editing tasks', 409);
  return project;
}

export class Planner {
  constructor(store) { this.store = store; }
  health() {
    const { schemaVersion, revision } = this.store.read();
    return { status: 'ok', schemaVersion, revision };
  }
  listProjects(query = {}) {
    if (!query || typeof query !== 'object' || Array.isArray(query)) throw new AppError('INVALID_QUERY', 'Invalid project query', 400);
    for (const key of Object.keys(query)) {
      if (key !== 'archived' || !['true', 'false'].includes(query[key])) throw new AppError('INVALID_QUERY', `Invalid ${key} query`, 400, key);
    }
    const { projects, revision } = this.store.read();
    return { items: projects.filter(project => (project.archived === true) === (query.archived === 'true')).map(projectView), revision };
  }
  getProject(id) {
    const model = this.store.read();
    return { project: projectView(findProject(model, id)), revision: model.revision };
  }
  exportProjectCsv(id) {
    const model = this.store.read();
    return { csv: projectCsv(model, findProject(model, id)), revision: model.revision };
  }
  async setProjectArchived(id, input, revision) {
    const result = await this.store.transact(revision, model => {
      object(input, ['archived'], ['archived']);
      if (typeof input.archived !== 'boolean') invalid('Archived must be a boolean', 'archived');
      const project = findProject(model, id);
      if ((project.archived === true) !== input.archived) project.archived = input.archived;
      return projectView(project);
    });
    return { project: result.value, revision: result.revision };
  }
  listTasks(query) { return selectTasks(this.store.read(), query); }
  dashboard(projectId) { return summarize(this.store.read(), projectId); }
  async createProject(input, revision) {
    const result = await this.store.transact(revision, model => {
      object(input, ['name'], ['name']);
      const name = text(input.name, 'name', 80);
      if (model.projects.some(project => project.name.toLowerCase() === name.toLowerCase())) throw new AppError('DUPLICATE_PROJECT', 'A project with this name already exists', 409, 'name');
      if (model.projects.length >= 100) throw new AppError('CAPACITY_EXCEEDED', 'Project limit reached', 409);
      const project = { ...allocate(model, 'p'), name };
      model.projects.push(project);
      return projectView(project);
    });
    return { project: result.value, revision: result.revision };
  }
  async createTask(input, revision) {
    const result = await this.store.transact(revision, model => {
      object(input, ['projectId', 'title', 'description', 'dependencyIds', 'priority'], ['projectId', 'title']);
      if (typeof input.projectId !== 'string') invalid('Project ID must be text', 'projectId');
      assertProjectWritable(model, input.projectId);
      const title = text(input.title, 'title', 160);
      const description = text(Object.hasOwn(input, 'description') ? input.description : '', 'description', 2000, false);
      if (model.tasks.length >= 2000) throw new AppError('CAPACITY_EXCEEDED', 'Task limit reached', 409);
      const priority = Object.hasOwn(input, 'priority') ? choice(input.priority, priorities, 'priority') : 'normal';
      const task = { ...allocate(model, 't'), projectId: input.projectId, title, description, status: 'todo', dependencyIds: Object.hasOwn(input, 'dependencyIds') ? structuredClone(input.dependencyIds) : [], priority };
      model.tasks.push(task);
      validateGraph(model);
      return taskView(model, task);
    });
    return { task: result.value, revision: result.revision };
  }
  async updateTask(id, input, revision) {
    const result = await this.store.transact(revision, model => {
      object(input, ['title', 'description', 'status', 'dependencyIds', 'priority']);
      if (!Object.keys(input).length) throw new AppError('INVALID_INPUT', 'Supply at least one change');
      const task = findTask(model, id);
      assertProjectWritable(model, task.projectId);
      const oldStatus = task.status;
      if (Object.hasOwn(input, 'title')) task.title = text(input.title, 'title', 160);
      if (Object.hasOwn(input, 'description')) task.description = text(input.description, 'description', 2000, false);
      if (Object.hasOwn(input, 'status')) task.status = choice(input.status, statuses, 'status');
      if (Object.hasOwn(input, 'priority')) task.priority = choice(input.priority, priorities, 'priority');
      if (Object.hasOwn(input, 'dependencyIds')) task.dependencyIds = structuredClone(input.dependencyIds);
      validateDependencies(model, id, task.dependencyIds);
      transition(model, id, oldStatus);
      validateGraph(model);
      return taskView(model, task);
    });
    return { task: result.value, revision: result.revision };
  }
}
