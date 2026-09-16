const $ = selector => document.querySelector(selector);
const state = { projects: [], tasks: [], revision: 0, projectId: new URL(location.href).searchParams.get('projectId'), busy: false };

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
  const id = `task-${name}`;
  form.append(element('label', label, { for: id }));
  const input = element(multiline ? 'textarea' : 'input', undefined, { id, name });
  input.value = value;
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
    if (result.project) state.projectId = result.project.id;
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
  const actions = element('div', undefined, { class: 'actions' });
  actions.append(element('button', 'Save task', { type: 'submit' }), button('Cancel', () => {
    form.remove(); clearError(); $('#add-task').focus();
  }));
  form.append(actions);
  form.addEventListener('submit', event => {
    event.preventDefault();
    const values = new FormData(form);
    const input = { title: values.get('title'), description: values.get('description') };
    if (!task) input.projectId = state.projectId;
    void save(form, task ? `/api/tasks/${task.id}` : '/api/tasks', task ? 'PATCH' : 'POST', input, 'Task saved');
  });
  $('#main').append(form);
  title.focus();
}
function navigate(projectId) {
  state.projectId = projectId;
  const url = new URL(location.href);
  url.searchParams.set('projectId', projectId);
  history.pushState(null, '', url);
  render();
}
function render() {
  const projects = $('#projects');
  projects.replaceChildren();
  if (!state.projects.length) projects.append(element('li', 'No projects yet. Create your first project.'));
  for (const project of state.projects) {
    const item = element('li');
    const link = element('a', project.name, { href: `/?projectId=${encodeURIComponent(project.id)}` });
    link.addEventListener('click', event => { event.preventDefault(); navigate(project.id); });
    item.append(link); projects.append(item);
  }
  const main = $('#main');
  main.replaceChildren();
  main.setAttribute('aria-busy', 'false');
  const project = state.projects.find(project => project.id === state.projectId);
  if (!project) { main.append(element('h2', 'Choose a project'), element('p', 'Create or select a project to plan your team’s work.')); return; }
  main.append(element('h2', project.name));
  const add = button('Add task', () => edit());
  add.id = 'add-task';
  main.append(add);
  const tasks = state.tasks.filter(task => task.projectId === project.id);
  if (!tasks.length) main.append(element('p', 'No tasks yet. Add your first task.'));
  for (const task of tasks) {
    const card = element('article', undefined, { 'aria-label': task.title, 'data-task-id': task.id });
    card.append(element('h3', task.title), element('span', task.status, { class: 'badge' }), element('p', task.description), button('Edit', () => edit(task)));
    main.append(card);
  }
}
async function reload() {
  clearError();
  $('#main').setAttribute('aria-busy', 'true');
  announce('Loading…');
  try {
    const projects = await request('/api/projects');
    const tasks = await request('/api/tasks');
    if (projects.revision !== tasks.revision) throw new Error('Data changed while loading. Use Reload latest.');
    state.projects = projects.items;
    state.tasks = tasks.items;
    state.revision = tasks.revision;
    if (!state.projectId && projects.items.length) state.projectId = projects.items[0].id;
    render();
    announce('');
  } catch (error) { $('#main').setAttribute('aria-busy', 'false'); announce(''); showError(error); throw error; }
}
$('#project-form').addEventListener('submit', event => {
  event.preventDefault();
  void save(event.currentTarget, '/api/projects', 'POST', { name: $('#project-name').value }, 'Project created');
});
$('#reload').addEventListener('click', () => { if (!state.busy) void reload().catch(() => {}); });
window.addEventListener('popstate', () => { state.projectId = new URL(location.href).searchParams.get('projectId'); render(); });
void reload().catch(() => {});
