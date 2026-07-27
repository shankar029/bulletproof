# SPEC — Expression Evaluator (gnarly)

`evaluate(src: string): number` evaluates an arithmetic expression.

## Requirements
- Binary operators `+ - * /` with correct **precedence** (`*`/`/` bind tighter than `+`/`-`) and
  **left-associativity** (`10-4-3 === 3`).
- **Parentheses**, including nesting, override precedence.
- **Unary minus/plus**, including after an operator (`3*-2 === -6`).
- Decimals and arbitrary whitespace.
- Throw on **division by zero**, malformed input (`2+`), and invalid characters (`2#3`).

## Project context (reuse these)
`shared/tokenize.ts` exports `tokenize(src)`. Reuse it; don't hand-roll a second lexer.

## Guardrail
Parse it for real — **no `eval()` / `new Function()`**.

## Acceptance (held-out oracle)
Precedence, (nested) parentheses, unary minus after an operator, left-associativity, decimals,
whitespace, and the three throwing cases.
