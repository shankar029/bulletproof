import { tokenize, type Token } from '../shared/tokenize.ts';

// Recursive-descent parser with correct precedence, parentheses, and unary operators.
//   expr   := term  (('+' | '-') term)*
//   term   := factor (('*' | '/') factor)*
//   factor := ('+' | '-') factor | '(' expr ')' | number
export function evaluate(src: string): number {
  const tokens = tokenize(src);
  let pos = 0;
  const peek = (): Token | undefined => tokens[pos];
  const next = (): Token => tokens[pos++];

  function parseExpr(): number {
    let value = parseTerm();
    for (let t = peek(); t?.type === 'op' && (t.value === '+' || t.value === '-'); t = peek()) {
      next();
      const rhs = parseTerm();
      value = t.value === '+' ? value + rhs : value - rhs;
    }
    return value;
  }

  function parseTerm(): number {
    let value = parseFactor();
    for (let t = peek(); t?.type === 'op' && (t.value === '*' || t.value === '/'); t = peek()) {
      next();
      const rhs = parseFactor();
      if (t.value === '/') {
        if (rhs === 0) throw new Error('division by zero');
        value /= rhs;
      } else {
        value *= rhs;
      }
    }
    return value;
  }

  function parseFactor(): number {
    const t = peek();
    if (!t) throw new Error('unexpected end of input');
    if (t.type === 'op' && (t.value === '-' || t.value === '+')) {
      next();
      const operand = parseFactor();
      return t.value === '-' ? -operand : operand;
    }
    if (t.type === 'lparen') {
      next();
      const value = parseExpr();
      if (peek()?.type !== 'rparen') throw new Error('missing closing parenthesis');
      next();
      return value;
    }
    if (t.type === 'num') {
      next();
      return t.value;
    }
    throw new Error('unexpected token');
  }

  const result = parseExpr();
  if (pos !== tokens.length) throw new Error('unexpected trailing input');
  return result;
}
