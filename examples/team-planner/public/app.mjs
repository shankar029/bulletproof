const $ = selector => document.querySelector(selector);
const state = { projects: [], tasks: [], revision: 0, projectId: null, busy: false, result: null, summary: null, schemaVersion: 1 };
let loadSequence = 0;
function route() { return new URL(location.href).searchParams; }

function element(tag, text, attributes = {}) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  return node;
}
function button(text, action) {
  const node = element('button', text, { type: 'button' });
  node.addEventListener('click', action);
  return node;
}
function field(form, name, label, value = '', multiline = false) {
  const id = `${form.id || 'filter'}-${name}`;
  form.append(element('label', label, { for: id }));
  const input = element(multiline ? 'textarea' : 'input', undefined, { id, name });
  input.value = value;
  form.append(input);
  return input;
}
function select(form, name, label, values, selected) {
  const id = `${form.id || 'filter'}-${name}`;
  form.append(element('label', label, { for: id }));
  const input = element('select', undefined, { id, name });
  for (const value of values) input.append(element('option', value.replaceAll('_', ' '), { value }));
  input.value = selected;
  form.append(input);
  return input;
}
function announce(message) { $('#notice').textContent = message; }
function clearError() { $('#error').hidden = true; $('#error').textContent = ''; }
function showError(error) {
  $('#error').textContent = `${error.field ? `${error.field}: ` : ''}${error.message}`;
  $('#error').hidden = false;
  $('#error').focus();
}
async function request(path, method = 'GET', input) {
  let response;
  try {
    response = await fetch(path, {
      method, signal: AbortSignal.timeout(10000),
      headers: method === 'GET' ? {} : { 'Content-Type': 'application/json', 'If-Match': `"${state.revision}"` },
      body: input === undefined ? undefined : JSON.stringify(input),
    });
  } catch {
    throw new Error('Request failed; saving may be uncertain. Use Reload latest to read committed data before another action.');
  }
  let payload;
  try { payload = await response.json(); } catch {
    throw new Error('Invalid response. Use Reload latest to check committed data.');
  }
  if (!response.ok) {
    const error = new Error(payload.error?.message ?? 'Request failed. Reload latest to recover.');
    error.field = payload.error?.field;
    error.code = payload.error?.code;
    throw error;
  }
  return payload;
}
async function save(form, path, method, input, success) {
  if (state.busy) return;
  state.busy = true;
  clearError();
  announce('Saving…');
  const controls = [...form.querySelectorAll('button, input, textarea, select')];
  controls.forEach(control => { control.disabled = true; });
  try {
    const result = await request(path, method, input);
    state.revision = result.revision;
    if (result.project) {
      const url = new URL(location.href);
      url.search = new URLSearchParams({ projectId: result.project.id }).toString();
      history.pushState(null, '', url);
    }
    if (form.id === 'project-form') form.reset();
    await reload();
    announce(success);
  } catch (error) { announce(''); showError(error); }
  finally {
    state.busy = false;
    controls.forEach(control => { control.disabled = false; });
  }
}
function edit(task) {
  $('#editor')?.remove();
  const form = element('form', undefined, { id: 'editor', 'aria-label': task ? 'Edit task' : 'Add task' });
  form.append(element('h3', task ? 'Edit task' : 'Add task'));
  const title = field(form, 'title', 'Title', task?.title ?? '');
  field(form, 'description', 'Description', task?.description ?? '', true);
  if (task) select(form, 'status', 'Status', ['todo', 'in_progress', 'done'], task.status);
  const dependencies = element('fieldset');
  dependencies.append(element('legend', 'Dependencies'), element('p', 'Complete dependencies before starting.'));
  for (const other of state.tasks.filter(other => other.projectId === state.projectId && other.id !== task?.id)) {
    const label = element('label', undefined, { class: 'dependency' });
    const checkbox = element('input', undefined, { type: 'checkbox', name: 'dependencyIds', value: other.id });
    checkbox.checked = task?.dependencyIds.includes(other.id) ?? false;
    label.append(checkbox, document.createTextNode(other.title));
    dependencies.append(label);
  }
  form.append(dependencies);
  const actions = element('div', undefined, { class: 'actions' });
  actions.append(element('button', 'Save task', { type: 'submit' }), button('Cancel', () => {
    form.remove(); clearError(); $('#add-task').focus();
  }));
  form.append(actions);
  form.addEventListener('submit', event => {
    event.preventDefault();
    const values = new FormData(form);
    const input = { title: values.get('title'), description: values.get('description'), dependencyIds: values.getAll('dependencyIds') };
    if (task) input.status = values.get('status');
    if (!task) input.projectId = state.projectId;
    void save(form, task ? `/api/tasks/${task.id}` : '/api/tasks', task ? 'PATCH' : 'POST', input, 'Task saved');
  });
  $('#main').append(form);
  title.focus();
}
function navigate(changes) {
  if (state.busy) return;
  const url = new URL(location.href);
  for (const [key, value] of Object.entries(changes)) {
    if (value === null || value === '') url.searchParams.delete(key);
    else url.searchParams.set(key, value);
  }
  history.pushState(null, '', url);
  void reload().catch(() => {});
}
function render() {
  const projects = $('#projects');
  projects.replaceChildren();
  if (!state.projects.length) projects.append(element('li', 'No projects yet. Create your first project.'));
  for (const project of state.projects) {
    const item = element('li');
    const link = element('a', project.name, { href: `/?projectId=${encodeURIComponent(project.id)}` });
    link.addEventListener('click', event => { event.preventDefault(); navigate({ projectId: project.id, page: null }); });
    item.append(link); projects.append(item);
  }
  const main = $('#main');
  main.replaceChildren();
  main.setAttribute('aria-busy', 'false');
  const project = state.projects.find(project => project.id === state.projectId);
  if (route().get('view') === 'dashboard') {
    main.append(element('h2', project ? `${project.name} dashboard` : 'Global dashboard'));
    main.append(button('All projects', () => navigate({ projectId: null })));
    renderSummary(main);
    return;
  }
  if (!project) { main.append(element('h2', 'Choose a project'), element('p', 'Create or select a project to plan your team’s work.')); return; }
  main.append(element('h2', project.name));
  renderSummary(main);
  const filters = element('form', undefined, { class: 'filters', 'aria-label': 'Task filters' });
  field(filters, 'q', 'Search titles', route().get('q') ?? '');
  select(filters, 'status', 'Filter status', ['', 'todo', 'in_progress', 'done'], route().get('status') ?? '');
  filters.querySelector('option').textContent = 'All statuses';
  filters.append(element('button', 'Apply filters', { type: 'submit' }), button('Clear filters', () => navigate({ q: null, status: null, priority: null, page: null })));
  filters.addEventListener('submit', event => {
    event.preventDefault();
    const values = new FormData(filters);
    navigate({ q: values.get('q'), status: values.get('status'), page: null });
  });
  main.append(filters);
  const add = button('Add task', () => edit());
  add.id = 'add-task';
  main.append(add);
  const tasks = state.result.items;
  if (!tasks.length) main.append(element('p', state.tasks.length ? 'No results. Clear filters or return to the previous page.' : 'No tasks yet. Add your first task.'));
  for (const task of tasks) {
    const card = element('article', undefined, { 'aria-label': task.title, 'data-task-id': task.id });
    card.append(element('h3', task.title), element('span', task.blocked ? 'blocked (todo)' : task.status.replaceAll('_', ' '), { class: 'badge' }), element('p', task.description), button('Edit', () => edit(task)));
    main.append(card);
  }
  const pages = element('div', undefined, { class: 'actions', 'aria-label': 'Pagination' });
  const previous = button('Previous', () => navigate({ page: state.result.page - 1 }));
  previous.disabled = state.result.page <= 1;
  const next = button('Next', () => navigate({ page: state.result.page + 1 }));
  next.disabled = state.result.page >= state.result.totalPages;
  pages.append(previous, element('span', `Page ${state.result.page} of ${state.result.totalPages} · ${state.result.total} tasks`), next);
  const pageSize = select(pages, 'pageSize', 'Tasks per page', ['2', '10', '25', '50'], String(state.result.pageSize));
  pageSize.addEventListener('change', () => navigate({ pageSize: pageSize.value, page: null }));
  main.append(pages);
}
function renderSummary(main) {
  if (!state.summary) return;
  const summary = element('section', undefined, { class: 'summary', 'aria-label': 'Project totals' });
  for (const [key, label] of [['total', 'Total'], ['todo', 'Todo'], ['inProgress', 'In progress'], ['done', 'Done'], ['blocked', 'Blocked'], ['completionPercent', 'Completion %']]) {
    summary.append(element('p', `${label}: ${state.summary[key]}`));
  }
  main.append(summary);
}
async function reload() {
  const sequence = ++loadSequence;
  clearError();
  $('#main').setAttribute('aria-busy', 'true');
  announce('Loading…');
  try {
    const projects = await request('/api/projects');
    const params = route();
    const projectId = params.get('projectId');
    const query = new URLSearchParams();
    for (const key of ['projectId', 'q', 'status', 'priority', 'page', 'pageSize']) if (params.has(key)) query.set(key, params.get(key));
    const tasks = await request(`/api/tasks?${query}`);
    const summary = await request(`/api/dashboard${projectId ? `?projectId=${encodeURIComponent(projectId)}` : ''}`);
    const health = await request('/api/health');
    const allTasks = [];
    if (projectId) {
      let page = 1, totalPages;
      do {
        const batch = await request(`/api/tasks?projectId=${encodeURIComponent(projectId)}&pageSize=50&page=${page}`);
        if (batch.revision !== tasks.revision) throw new Error('Data changed while loading. Use Reload latest.');
        allTasks.push(...batch.items);
        totalPages = batch.totalPages;
        page++;
      } while (page <= totalPages);
    }
    if ([projects, summary, health].some(result => result.revision !== tasks.revision)) throw new Error('Data changed while loading. Use Reload latest.');
    if (sequence !== loadSequence) return;
    state.projects = projects.items;
    state.projectId = projectId;
    state.tasks = allTasks;
    state.result = tasks;
    state.summary = summary;
    state.schemaVersion = health.schemaVersion;
    state.revision = tasks.revision;
    render();
    announce('');
  } catch (error) {
    if (sequence === loadSequence) { $('#main').setAttribute('aria-busy', 'false'); announce(''); showError(error); }
    throw error;
  }
}
$('#project-form').addEventListener('submit', event => {
  event.preventDefault();
  void save(event.currentTarget, '/api/projects', 'POST', { name: $('#project-name').value }, 'Project created');
});
$('#reload').addEventListener('click', () => { if (!state.busy) void reload().catch(() => {}); });
$('#nav-projects').addEventListener('click', event => { event.preventDefault(); navigate({ view: null }); });
$('#nav-dashboard').addEventListener('click', event => { event.preventDefault(); navigate({ view: 'dashboard', q: null, status: null, priority: null, page: null }); });
window.addEventListener('popstate', () => { void reload().catch(() => {}); });
void reload().catch(() => {});
