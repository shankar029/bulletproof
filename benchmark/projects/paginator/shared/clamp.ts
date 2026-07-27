/** Clamps n to the inclusive range [min, max]. */
export const clamp = (n: number, min: number, max: number): number => Math.min(Math.max(n, min), max);
