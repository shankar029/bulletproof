export type Token =
  | { type: 'num'; value: number }
  | { type: 'op'; value: '+' | '-' | '*' | '/' }
  | { type: 'lparen' }
  | { type: 'rparen' };

/** Lexes an arithmetic expression into tokens. Throws on invalid characters or numbers. */
export function tokenize(src: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < src.length) {
    const c = src[i];
    if (c === ' ' || c === '\t' || c === '\n') { i++; continue; }
    if (c === '(') { tokens.push({ type: 'lparen' }); i++; continue; }
    if (c === ')') { tokens.push({ type: 'rparen' }); i++; continue; }
    if (c === '+' || c === '-' || c === '*' || c === '/') { tokens.push({ type: 'op', value: c }); i++; continue; }
    if ((c >= '0' && c <= '9') || c === '.') {
      let j = i;
      while (j < src.length && ((src[j] >= '0' && src[j] <= '9') || src[j] === '.')) j++;
      const slice = src.slice(i, j);
      const value = Number(slice);
      if (Number.isNaN(value)) throw new Error(`invalid number: ${slice}`);
      tokens.push({ type: 'num', value });
      i = j;
      continue;
    }
    throw new Error(`unexpected character: ${c}`);
  }
  return tokens;
}
