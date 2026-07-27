// Pure textual mutation engine for the test-realness dimension. Dependency-free.
// Applies one well-known mutation operator at one site per mutant, so a real test suite should
// FAIL (kill) each mutant while a shallow/fake/absent suite lets it survive. Textual (not AST) by
// design: it stays tiny and dependency-free; syntactically-invalid or equivalent mutants are
// filtered downstream (a mutant whose tests can't even load is skipped, never counted as a kill).

/** Mutation operators as [find, replace] on a single occurrence. Spacing is deliberate: matching
 *  ` + ` (spaces) avoids `++`, `+=`, and comment terminators. Each pair is applied one site
 *  at a time. Symmetric pairs are listed once per direction. */
const OPERATORS = [
  [' + ', ' - '],
  [' - ', ' + '],
  [' * ', ' / '],
  [' / ', ' * '],
  ['<=', '<'],
  ['>=', '>'],
  [' < ', ' > '],
  [' > ', ' < '],
  ['===', '!=='],
  ['!==', '==='],
  [' && ', ' || '],
  [' || ', ' && '],
  ['true', 'false'],
  ['false', 'true'],
];

/** All start indices of `needle` in `hay` (non-overlapping). */
function indicesOf(hay, needle) {
  const out = [];
  let i = hay.indexOf(needle);
  while (i !== -1) { out.push(i); i = hay.indexOf(needle, i + needle.length); }
  return out;
}

/** Replace the occurrence of `find` at `at` with `replace`. */
function replaceAt(src, at, find, replace) {
  return src.slice(0, at) + replace + src.slice(at + find.length);
}

/**
 * Generate distinct single-site mutants of `source`.
 * Returns `[{ id, operator, index, mutated }]`, deduped and excluding no-ops (mutated === source).
 * `max` bounds the count for runtime; sites are taken in source order across operators.
 */
export function generateMutants(source, { max = 16 } = {}) {
  const seen = new Set();
  const mutants = [];
  for (const [find, replace] of OPERATORS) {
    for (const at of indicesOf(source, find)) {
      const mutated = replaceAt(source, at, find, replace);
      if (mutated === source || seen.has(mutated)) continue;
      seen.add(mutated);
      mutants.push({ id: `${find.trim()}→${replace.trim()}@${at}`, operator: `${find.trim()}→${replace.trim()}`, index: at, mutated });
      if (mutants.length >= max) return mutants;
    }
  }
  return mutants;
}
