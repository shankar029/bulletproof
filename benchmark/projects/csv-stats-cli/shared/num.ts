/** Rounds a number to `dp` decimal places without floating-point drift. */
export const roundTo = (n: number, dp: number): number => {
  const f = 10 ** dp;
  return Math.round((n + Number.EPSILON) * f) / f;
};
