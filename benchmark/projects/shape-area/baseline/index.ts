// Naive refactor: still an if/else chain (not extensible), inline rounding (duplication),
// and it kept the 3.14 approximation instead of Math.PI (a behavior regression).
export function area(shape: any): number {
  let a: number;
  if (shape.type === 'rect') a = shape.w * shape.h;
  else if (shape.type === 'circle') a = 3.14 * shape.r * shape.r; // BUG: not Math.PI
  else if (shape.type === 'triangle') a = (shape.base * shape.height) / 2;
  else throw new Error('unknown shape');
  return Math.round((a + Number.EPSILON) * 100) / 100; // inline rounding (duplication)
}
