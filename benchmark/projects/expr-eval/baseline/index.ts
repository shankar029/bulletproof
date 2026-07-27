// Naive evaluator: splits into tokens and folds strictly left-to-right. No operator precedence,
// no parentheses, no unary minus, and no error handling for malformed input or division by zero.
export function evaluate(src: string): number {
  const tokens = src.replace(/\s+/g, '').match(/(\d+\.?\d*|[-+*/])/g) ?? [];
  let acc = Number(tokens[0]);
  for (let i = 1; i < tokens.length; i += 2) {
    const op = tokens[i];
    const n = Number(tokens[i + 1]);
    if (op === '+') acc += n;
    else if (op === '-') acc -= n;
    else if (op === '*') acc *= n;
    else if (op === '/') acc /= n;
  }
  return acc;
}
