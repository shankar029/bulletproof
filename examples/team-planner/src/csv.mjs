import { taskView } from './rules.mjs';

export function csvCell(value) {
  const text = typeof value === 'string' && (/^[\t\r\n]/u.test(value) || /^[\s\p{Cc}\p{Cf}]*[=+\-@]/u.test(value)) ? "'" + value : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

export function projectCsv(model, project) {
  const rows = [['projectId', 'projectName', 'id', 'title', 'description', 'status', 'priority', 'dependencyIds', 'blocked', 'createdOrder']];
  const tasks = model.tasks.filter(task => task.projectId === project.id).sort((a, b) => a.createdOrder - b.createdOrder);
  for (const task of tasks) rows.push([
    project.id, project.name, task.id, task.title, task.description, task.status, task.priority,
    JSON.stringify(task.dependencyIds), taskView(model, task).blocked, task.createdOrder,
  ]);
  return rows.map(row => row.map(csvCell).join(',')).join('\r\n') + '\r\n';
}
