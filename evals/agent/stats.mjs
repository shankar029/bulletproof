// Small aggregation helpers for pass@k reporting (pure, dependency-free).

/** Population mean/stddev/min/max over a list of numbers. */
export function summarize(values) {
  const n = values.length;
  if (!n) return { n: 0, mean: 0, stddev: 0, min: 0, max: 0 };
  const mean = values.reduce((s, v) => s + v, 0) / n;
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / n;
  return { n, mean, stddev: Math.sqrt(variance), min: Math.min(...values), max: Math.max(...values) };
}

/** Fraction of runs meeting the quality bar (default: a perfect composite of 1). */
export function passRate(values, bar = 1) {
  const n = values.length;
  return n ? values.filter((v) => v >= bar - 1e-9).length / n : 0;
}
