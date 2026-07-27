import { randomUUID } from 'node:crypto';

// Reuse the platform's crypto-strong UUID generator — no reinvented RNG, no dependency.
export function newId(): string {
  return randomUUID();
}
