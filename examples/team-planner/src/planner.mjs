import { AppError, object, text } from './schema.mjs';

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

export class Planner {
  constructor(store) { this.store = store; }
  health() {
    const { schemaVersion, revision } = this.store.read();
    return { status: 'ok', schemaVersion, revision };
  }
  listProjects() {
    const { projects, revision } = this.store.read();
    return { items: projects, revision };
  }
  listTasks() {
    const { tasks, revision } = this.store.read();
    return { items: tasks.map(task => ({ ...task, blocked: false })), total: tasks.length, page: 1, pageSize: 10, totalPages: Math.ceil(tasks.length / 10), revision };
  }
  async createProject(input, revision) {
    const result = await this.store.transact(revision, model => {
      object(input, ['name'], ['name']);
      const name = text(input.name, 'name', 80);
      if (model.projects.some(project => project.name.toLowerCase() === name.toLowerCase())) throw new AppError('DUPLICATE_PROJECT', 'A project with this name already exists', 409, 'name');
      if (model.projects.length >= 100) throw new AppError('CAPACITY_EXCEEDED', 'Project limit reached', 409);
      const project = { ...allocate(model, 'p'), name };
      model.projects.push(project);
      return project;
    });
    return { project: result.value, revision: result.revision };
  }
  async createTask(input, revision) {
    const result = await this.store.transact(revision, model => {
      object(input, ['projectId', 'title', 'description'], ['projectId', 'title']);
      findProject(model, input.projectId);
      const title = text(input.title, 'title', 160);
      const description = text(Object.hasOwn(input, 'description') ? input.description : '', 'description', 2000, false);
      if (model.tasks.length >= 2000) throw new AppError('CAPACITY_EXCEEDED', 'Task limit reached', 409);
      const task = { ...allocate(model, 't'), projectId: input.projectId, title, description, status: 'todo', dependencyIds: [], priority: 'normal' };
      model.tasks.push(task);
      return { ...task, blocked: false };
    });
    return { task: result.value, revision: result.revision };
  }
  async updateTask(id, input, revision) {
    const result = await this.store.transact(revision, model => {
      object(input, ['title', 'description']);
      if (!Object.keys(input).length) throw new AppError('INVALID_INPUT', 'Supply at least one change');
      const task = findTask(model, id);
      if (Object.hasOwn(input, 'title')) task.title = text(input.title, 'title', 160);
      if (Object.hasOwn(input, 'description')) task.description = text(input.description, 'description', 2000, false);
      return { ...task, blocked: false };
    });
    return { task: result.value, revision: result.revision };
  }
}
