const $ = selector => document.querySelector(selector);
const state = { projects: [], project: null, tasks: [], revision: 0, projectId: null, busy: false, loading: true, fenced: false, result: null, summary: null, schemaVersion: null };
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
function writesDisabled() {
  return state.busy || state.loading || state.fenced || state.schemaVersion !== 2;
}
function taskWritesDisabled() {
  return writesDisabled() || !state.project || state.project.archived;
}
function syncWriteControls() {
  $('#project-form').querySelectorAll('input, button').forEach(control => { control.disabled = writesDisabled(); });
  document.querySelectorAll('[data-write]').forEach(control => {
    control.disabled = control.dataset.write === 'task' ? taskWritesDisabled() : writesDisabled() || Boolean($('#editor'));
  });
  $('#editor')?.querySelectorAll('input, textarea, select').forEach(control => { control.disabled = state.busy; });
  const guidance = $('#lifecycle-guidance');
  if (guidance) guidance.hidden = !$('#editor');
  const download = $('#download-csv');
  if (download) download.disabled = state.loading || download.dataset.downloading === 'true';
}
async function request(path, method = 'GET', input, revision = state.revision) {
  let response;
  try {
    response = await fetch(path, {
      method, signal: AbortSignal.timeout(10000),
      headers: method === 'GET' ? {} : { 'Content-Type': 'application/json', 'If-Match': `"${revision}"` },
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
async function save(form, path, method, input, success, revision = state.revision) {
  if (writesDisabled() || (form.id === 'editor' && taskWritesDisabled())) return;
  state.busy = true;
  clearError();
  announce('Saving…');
  syncWriteControls();
  let focusLifecycle = false;
  try {
    const result = await request(path, method, input, revision);
    if (result.project) {
      const url = new URL(location.href);
      if (method === 'POST') url.search = new URLSearchParams({ projectId: result.project.id }).toString();
      else url.searchParams.set('archived', String(result.project.archived));
      history.pushState(null, '', url);
    }
    if (form.id === 'project-form') form.reset();
    if (await reload()) {
      announce(success);
      focusLifecycle = Boolean(result.project && method === 'PATCH');
    }
  } catch (error) {
    if (!['INVALID_INPUT', 'DUPLICATE_PROJECT', 'DEPENDENCY_CYCLE', 'DEPENDENCIES_INCOMPLETE', 'INVALID_TRANSITION', 'ACTIVE_DEPENDENTS'].includes(error.code)) state.fenced = true;
    announce(form.id === 'editor' ? 'Draft retained. Reload latest discards it and loads committed data.' : '');
    showError(error);
  }
  finally {
    state.busy = false;
    syncWriteControls();
    if (focusLifecycle) $('#project-lifecycle')?.focus();
  }
}
function edit(task) {
  if (taskWritesDisabled()) return;
  const draftRevision = state.revision;
  $('#editor')?.remove();
  const form = element('form', undefined, { id: 'editor', 'aria-label': task ? 'Edit task' : 'Add task' });
  form.append(element('h3', task ? 'Edit task' : 'Add task'));
  const title = field(form, 'title', 'Title', task?.title ?? '');
  field(form, 'description', 'Description', task?.description ?? '', true);
  if (task) select(form, 'status', 'Status', ['todo', 'in_progress', 'done'], task.status);
  select(form, 'priority', 'Priority', ['low', 'normal', 'high'], task?.priority ?? 'normal');
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
  actions.append(element('button', 'Save task', { type: 'submit', 'data-write': 'task' }), button('Cancel', () => {
    form.remove(); clearError(); syncWriteControls();
    ($('#add-task')?.disabled ? $('#project-title') : $('#add-task'))?.focus();
  }));
  form.append(actions);
  form.addEventListener('submit', event => {
    event.preventDefault();
    const values = new FormData(form);
    const input = { title: values.get('title'), description: values.get('description'), dependencyIds: values.getAll('dependencyIds'), priority: values.get('priority') };
    if (task) input.status = values.get('status');
    if (!task) input.projectId = state.projectId;
    void save(form, task ? `/api/tasks/${task.id}` : '/api/tasks', task ? 'PATCH' : 'POST', input, 'Task saved', draftRevision);
  });
  $('#main').append(form);
  syncWriteControls();
  title.focus();
}
async function downloadCsv(projectId, control) {
  control.dataset.downloading = 'true';
  control.disabled = true;
  clearError();
  announce('Preparing CSV…');
  let href;
  try {
    const response = await fetch(`/api/projects/${projectId}/tasks.csv`, { signal: AbortSignal.timeout(10000) });
    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.error?.message ?? 'CSV download failed.');
    }
    href = URL.createObjectURL(await response.blob());
    const link = element('a', undefined, { href, download: `project-${projectId}-tasks.csv` });
    document.body.append(link);
    link.click();
    link.remove();
    announce('CSV download started.');
  } catch (error) {
    announce('');
    showError(new Error(`CSV download failed: ${error.message}`));
  } finally {
    if (href) setTimeout(() => URL.revokeObjectURL(href), 1000);
    delete control.dataset.downloading;
    control.disabled = false;
  }
}
function navigate(changes) {
  if (state.busy) return;
  const url = new URL(location.href);
  for (const [key, value] of Object.entries(changes)) {
    if (value === null || value === '') url.searchParams.delete(key);
    else url.searchParams.set(key, value);
  }
  history.pushState(null, '', url);
  void reload().catch(showError);
}
function render() {
  const projects = $('#projects');
  projects.replaceChildren();
  const archivedView = route().get('archived') === 'true';
  $('#projects-title').textContent = archivedView ? 'Archived projects' : 'Projects';
  const noProjects = archivedView ? 'No archived projects.' : 'No active projects. Create a project or view Archived projects.';
  if (!state.projects.length) projects.append(element('li', noProjects));
  for (const project of state.projects) {
    const item = element('li');
    const url = new URL(location.href);
    url.searchParams.set('projectId', project.id);
    url.searchParams.delete('page');
    const link = element('a', project.name, { href: url.pathname + url.search });
    link.addEventListener('click', event => { event.preventDefault(); navigate({ projectId: project.id, page: null }); });
    item.append(link); projects.append(item);
  }
  const main = $('#main');
  main.replaceChildren();
  main.setAttribute('aria-busy', 'false');
  const legacy = state.schemaVersion === 1;
  $('#project-form').querySelectorAll('input, button').forEach(control => { control.disabled = legacy; });
  if (legacy) main.append(element('p', 'Legacy data is read-only. Stop the server and run node src\\migrate.mjs --data-dir <your directory>, then restart and Reload latest.', { role: 'status' }));
  const project = state.project;
  if (route().get('view') === 'dashboard') {
    main.append(element('h2', project ? `${project.name} dashboard` : 'Global dashboard'));
    main.append(button('All projects', () => navigate({ projectId: null })));
    renderSummary(main);
    return `${project ? project.name : 'Global'} dashboard loaded. ${state.summary.total} tasks.`;
  }
  if (!project) {
    main.append(element('h2', 'Choose a project'), element('p', 'Create or select a project to plan your team’s work.'));
    return state.projects.length ? 'Projects loaded. Choose a project.' : noProjects;
  }
  main.append(element('h2', project.name, { id: 'project-title', tabindex: '-1' }));
  if (project.archived) main.append(element('p', 'Archived — tasks are read-only. Restore this project to make changes.', { role: 'status' }));
  const actions = element('div', undefined, { class: 'actions' });
  const lifecycle = button(project.archived ? 'Restore project' : 'Archive project', () => {
    if (writesDisabled() || $('#editor')) return;
    if (!project.archived && !confirm('Archive this project? Tasks will become read-only. You can restore it later.')) return;
    void save(actions, `/api/projects/${project.id}`, 'PATCH', { archived: !project.archived },
      project.archived ? 'Project restored. Editing is available.' : 'Project archived. Tasks are read-only.');
  });
  lifecycle.id = 'project-lifecycle';
  lifecycle.dataset.write = 'project';
  lifecycle.setAttribute('aria-describedby', 'lifecycle-guidance');
  const download = button('Download CSV', () => { void downloadCsv(project.id, download); });
  download.id = 'download-csv';
  actions.append(lifecycle, download, element('span', 'Exports all tasks, not just this page.'));
  const guidance = element('p', 'Finish or cancel your draft before changing project state.', { id: 'lifecycle-guidance' });
  guidance.hidden = true;
  main.append(actions, guidance);
  renderSummary(main);
  const filters = element('form', undefined, { class: 'filters', 'aria-label': 'Task filters' });
  field(filters, 'q', 'Search titles', route().get('q') ?? '');
  select(filters, 'status', 'Filter status', ['', 'todo', 'in_progress', 'done'], route().get('status') ?? '');
  filters.querySelector('option').textContent = 'All statuses';
  const priority = select(filters, 'priority', 'Filter priority', ['', 'low', 'normal', 'high'], route().get('priority') ?? '');
  priority.querySelector('option').textContent = 'All priorities';
  filters.append(element('button', 'Apply filters', { type: 'submit' }), button('Clear filters', () => navigate({ q: null, status: null, priority: null, page: null })));
  filters.addEventListener('submit', event => {
    event.preventDefault();
    const values = new FormData(filters);
    navigate({ q: values.get('q'), status: values.get('status'), priority: values.get('priority'), page: null });
  });
  main.append(filters);
  const add = button('Add task', () => edit());
  add.id = 'add-task';
  add.dataset.write = 'task';
  main.append(add);
  const tasks = state.result.items;
  const emptyMessage = state.tasks.length ? 'No results. Clear filters or return to the previous page.' :
    project.archived ? 'No tasks in this archived project.' : 'No tasks yet. Add your first task.';
  if (!tasks.length) main.append(element('p', emptyMessage));
  for (const task of tasks) {
    const card = element('article', undefined, { 'aria-label': task.title, 'data-task-id': task.id });
    const editButton = button('Edit', () => edit(task));
    editButton.dataset.write = 'task';
    card.append(element('h3', task.title), element('span', task.blocked ? 'blocked (todo)' : task.status.replaceAll('_', ' '), { class: 'badge' }), element('p', `Priority: ${task.priority}`), element('p', task.description), editButton);
    main.append(card);
  }
  const pages = element('nav', undefined, { class: 'actions', 'aria-label': 'Pagination' });
  const previous = button('Previous', () => navigate({ page: state.result.page - 1 }));
  previous.disabled = state.result.page <= 1;
  const next = button('Next', () => navigate({ page: state.result.page + 1 }));
  next.disabled = state.result.page >= state.result.totalPages;
  pages.append(previous, element('span', `Page ${state.result.page} of ${state.result.totalPages} · ${state.result.total} tasks`), next);
  const pageSize = select(pages, 'pageSize', 'Tasks per page', ['2', '10', '25', '50'], String(state.result.pageSize));
  pageSize.addEventListener('change', () => navigate({ pageSize: pageSize.value, page: null }));
  main.append(pages);
  return tasks.length ? `${state.result.total} tasks loaded. Page ${state.result.page} of ${state.result.totalPages}.` : emptyMessage;
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
  const params = route();
  state.loading = true;
  syncWriteControls();
  clearError();
  $('#main').setAttribute('aria-busy', 'true');
  announce('Loading…');
  try {
    const projects = await request(`/api/projects?archived=${params.get('archived') ?? 'false'}`);
    const projectId = params.get('projectId');
    const detail = projectId ? await request(`/api/projects/${encodeURIComponent(projectId)}`) : null;
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
    if ([projects, summary, health, ...(detail ? [detail] : [])].some(result => result.revision !== tasks.revision)) throw new Error('Data changed while loading. Use Reload latest.');
    if (sequence !== loadSequence) return false;
    state.projects = projects.items;
    state.project = detail?.project ?? null;
    state.projectId = projectId;
    state.tasks = allTasks;
    state.result = tasks;
    state.summary = summary;
    state.schemaVersion = health.schemaVersion;
    state.revision = tasks.revision;
    state.loading = false;
    state.fenced = false;
    announce(render());
    syncWriteControls();
    return true;
  } catch (error) {
    if (sequence !== loadSequence) return false;
    state.loading = false;
    state.fenced = true;
    syncWriteControls();
    $('#main').setAttribute('aria-busy', 'false'); announce('');
    throw error;
  }
}
$('#project-form').addEventListener('submit', event => {
  event.preventDefault();
  void save(event.currentTarget, '/api/projects', 'POST', { name: $('#project-name').value }, 'Project created');
});
$('#reload').addEventListener('click', () => { if (!state.busy) void reload().catch(showError); });
$('#nav-projects').addEventListener('click', event => { event.preventDefault(); navigate({ view: null, archived: null }); });
$('#nav-archive').addEventListener('click', event => { event.preventDefault(); navigate({ view: null, archived: 'true' }); });
$('#nav-dashboard').addEventListener('click', event => { event.preventDefault(); navigate({ view: 'dashboard', q: null, status: null, priority: null, page: null }); });
window.addEventListener('popstate', () => { void reload().catch(showError); });
void reload().catch(showError);
