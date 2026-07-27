/** Rounds to 2 decimals without floating-point drift. */
export const round2 = (n: number): number => Math.round((n + Number.EPSILON) * 100) / 100;
