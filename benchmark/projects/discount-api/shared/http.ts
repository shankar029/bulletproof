import type { ServerResponse } from 'node:http';

/** Writes a JSON response with the given status code. */
export function sendJson(res: ServerResponse, status: number, payload: unknown): void {
  res.writeHead(status, { 'content-type': 'application/json' });
  res.end(JSON.stringify(payload));
}
