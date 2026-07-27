import { round2 } from '../shared/round.ts';

export interface Shape { type: string; [k: string]: unknown }
export type AreaFn = (shape: any) => number;

// Areas live in a registry so new shapes are added by data (open/closed) — not by editing `area`.
const SHAPES: Record<string, AreaFn> = {
  rect: (s) => s.w * s.h,
  circle: (s) => Math.PI * s.r * s.r,
  triangle: (s) => (s.base * s.height) / 2,
};

/** Register (or override) a shape's area function without changing `area`. */
export function registerShape(type: string, fn: AreaFn): void {
  SHAPES[type] = fn;
}

export function area(shape: Shape): number {
  const fn = SHAPES[shape.type];
  if (!fn) throw new Error(`unknown shape: ${shape.type}`);
  return round2(fn(shape)); // reuse shared rounding
}
