import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { AppError } from './schema.mjs';

const assets = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/app.mjs', ['app.mjs', 'text/javascript; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']],
]);
const securityHeaders = {
  'X-Content-Type-Options': 'nosniff',
  'Content-Security-Policy': "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
};

function send(res, status, body, headers = {}) {
  res.writeHead(status, { ...securityHeaders, ...headers });
  res.end(body);
}
function json(res, status, body, headers = {}) {
  send(res, status, JSON.stringify(body), {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    ...(Number.isSafeInteger(body.revision) ? { ETag: `"${body.revision}"` } : {}),
    ...headers,
  });
}
function expectedRevision(req) {
  const value = req.headers['if-match'];
  if (value === undefined) throw new AppError('PRECONDITION_REQUIRED', 'If-Match revision required', 428);
  if (!/^"(0|[1-9][0-9]*)"$/.test(value) || !Number.isSafeInteger(Number(value.slice(1, -1)))) throw new AppError('INVALID_REVISION', 'Use a quoted nonnegative safe integer revision');
  return Number(value.slice(1, -1));
}
async function body(req) {
  if (!/^application\/json(?:\s*;\s*charset=utf-8)?$/i.test(req.headers['content-type'] ?? '')) throw new AppError('UNSUPPORTED_MEDIA_TYPE', 'Use application/json', 415);
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 65536) throw new AppError('BODY_TOO_LARGE', 'Body exceeds 64 KiB', 413);
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { throw new AppError('BAD_JSON', 'Invalid JSON body'); }
}

export function parseQuery(params, allowed = []) {
  const query = {};
  for (const [key, value] of params) {
    if (!allowed.includes(key) || Object.hasOwn(query, key)) throw new AppError('INVALID_QUERY', `Unknown or duplicate query: ${key}`, 400, key);
    query[key] = value;
  }
  return query;
}

export function createServer({ planner, onError = error => console.error(error) }) {
  return http.createServer({ requestTimeout: 10000, headersTimeout: 10000 }, async (req, res) => {
    try {
      const port = req.socket.localPort;
      const hosts = [`127.0.0.1:${port}`, `localhost:${port}`];
      if (!hosts.includes(req.headers.host) || (req.headers.origin !== undefined && !hosts.map(host => `http://${host}`).includes(req.headers.origin))) throw new AppError('FORBIDDEN_ORIGIN', 'Only same-site local requests are allowed', 403);
      const url = new URL(req.url, `http://${req.headers.host}`);
      const taskMatch = /^\/api\/tasks\/(t-[1-9][0-9]*)$/.exec(url.pathname);
      let methods;
      if (assets.has(url.pathname) || ['/api/health', '/api/dashboard'].includes(url.pathname)) methods = ['GET'];
      if (url.pathname === '/api/projects' || url.pathname === '/api/tasks') methods = ['GET', 'POST'];
      if (taskMatch) methods = ['PATCH'];
      if (!methods) throw new AppError('NOT_FOUND', 'Route not found', 404);
      if (!methods.includes(req.method)) {
        json(res, 405, { error: { code: 'METHOD_NOT_ALLOWED', message: 'Method not allowed' } }, { Allow: methods.join(', ') });
        return;
      }
      if (assets.has(url.pathname)) {
        parseQuery(url.searchParams);
        const [name, type] = assets.get(url.pathname);
        send(res, 200, await readFile(new URL(`../public/${name}`, import.meta.url)), { 'Content-Type': type });
        return;
      }
      parseQuery(url.searchParams);
      if (req.method === 'GET') {
        if (url.pathname === '/api/health') json(res, 200, planner.health());
        else if (url.pathname === '/api/projects') json(res, 200, planner.listProjects());
        else if (url.pathname === '/api/tasks') json(res, 200, planner.listTasks());
        else throw new AppError('NOT_FOUND', 'Route not found', 404);
        return;
      }
      const revision = expectedRevision(req);
      const input = await body(req);
      if (taskMatch) json(res, 200, await planner.updateTask(taskMatch[1], input, revision));
      else if (url.pathname === '/api/projects') json(res, 201, await planner.createProject(input, revision));
      else json(res, 201, await planner.createTask(input, revision));
    } catch (error) {
      const known = error instanceof AppError;
      if (!known) onError(error);
      if (!res.headersSent && !res.destroyed) json(res, known ? error.status : 500, {
        error: { code: known ? error.code : 'INTERNAL_ERROR', message: known ? error.message : 'Unexpected server error', ...(known && error.field ? { field: error.field } : {}) },
      });
    }
  });
}
