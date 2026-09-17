'use strict';
// Synthetic qualification only. No input JavaScript is evaluated.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const roots = JSON.parse(fs.readFileSync(path.join(__dirname, 'q2-tools-source-roots.json'), 'utf8'));
const root = path.dirname(path.dirname(roots.typescript));
const fixtureRoot = path.join(root, 'typescript fixtures with spaces');
fs.mkdirSync(fixtureRoot);
const tsRoot = roots.typescript;
const ts = require(path.join(tsRoot, 'lib', 'typescript.js'));
assert.equal(ts.version, '5.9.3');
const files = [];
const checks = [];
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const inside = (file, dir) => {
  const rel = path.relative(dir, path.resolve(file));
  return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel));
};
function write(name, text) {
  const file = path.join(fixtureRoot, name);
  fs.writeFileSync(file, text.replace(/\r?\n/g, '\r\n'), {flag: 'wx'});
  files.push({path: file, sha256: hash(fs.readFileSync(file))});
  return file;
}
const options = {
  noEmit: true, allowJs: true, checkJs: true, strict: true,
  noUnusedLocals: true, noUnusedParameters: true, allowUnreachableCode: false,
  target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.NodeNext,
  moduleResolution: ts.ModuleResolutionKind.NodeNext, jsx: ts.JsxEmit.Preserve,
  types: [], typeRoots: [],
};
const reads = new Map();
function program(input, override = {}) {
  const opts = {...options, ...override};
  const host = ts.createCompilerHost(opts);
  const read = host.readFile.bind(host);
  host.readFile = file => {
    assert(inside(file, fixtureRoot) || inside(file, tsRoot), `Unexpected compiler read: ${file}`);
    const text = read(file);
    if (text !== undefined) reads.set(path.resolve(file), hash(Buffer.from(text)));
    return text;
  };
  host.fileExists = file => (inside(file, fixtureRoot) || inside(file, tsRoot)) && ts.sys.fileExists(file);
  host.directoryExists = dir => (inside(dir, fixtureRoot) || inside(dir, tsRoot)) && ts.sys.directoryExists(dir);
  host.writeFile = () => { throw new Error('Unexpected compiler output'); };
  return ts.createProgram(input, opts, host);
}
function diagnostics(p) {
  return ts.getPreEmitDiagnostics(p).map(d => ({
    code: d.code, category: d.category, source: d.source ?? null,
    file: d.file?.fileName ?? null, start: d.start ?? null, length: d.length ?? null,
    message: ts.flattenDiagnosticMessageText(d.messageText, '\n'),
  }));
}
function nodes(sf) {
  const found = [];
  function walk(node) {
    found.push({kind: ts.SyntaxKind[node.kind], start: node.getStart(sf), end: node.end});
    ts.forEachChild(node, walk);
  }
  walk(sf);
  return found;
}
const kinds = {'.js': ts.ScriptKind.JS, '.mjs': ts.ScriptKind.JS, '.cjs': ts.ScriptKind.JS,
  '.ts': ts.ScriptKind.TS, '.tsx': ts.ScriptKind.TSX, '.jsx': ts.ScriptKind.JSX};
for (const [suffix, kind] of Object.entries(kinds)) {
  const typed = suffix === '.ts' || suffix === '.tsx';
  const signature = typed ? 'value: number' : 'value';
  const jsdoc = typed ? '' : '/** @param {number} value */\n';
  const code = `// café 😀\n${jsdoc}${suffix === '.cjs' ? '' : 'export '}function calculate(${signature}) {\n`
    + '  if (value > 0) return value + 1;\n  return value - 1;\n}\n'
    + (suffix === '.cjs' ? 'module.exports = { calculate };\n' : '');
  const clean = write('clean café' + suffix, code);
  const p = program([clean]);
  const ds = diagnostics(p);
  assert.deepEqual(ds, [], JSON.stringify(ds));
  const sf = p.getSourceFile(clean);
  assert(sf);
  const syntax = ts.createSourceFile(clean, fs.readFileSync(clean, 'utf8'), ts.ScriptTarget.Latest, true, kind);
  assert(nodes(syntax).some(n => n.kind === 'FunctionDeclaration'));
  const checker = p.getTypeChecker();
  const declaration = syntax.statements.find(ts.isFunctionDeclaration);
  const liveDecl = sf.statements.find(ts.isFunctionDeclaration);
  assert(checker.getSymbolAtLocation(liveDecl.name));
  checks.push({case: 'clean' + suffix, diagnostics: ds, file: clean, sourceStatements: syntax.statements.length,
    function: declaration.name.text, checkerSymbol: checker.getSymbolAtLocation(liveDecl.name).getName()});
  const empty = write('empty' + suffix, '');
  const comment = write('comment' + suffix, '// café 😀\n');
  const functionless = write('functionless' + suffix, suffix === '.cjs' ? 'module.exports = 17;\n' : 'export const value = 17;\n');
  const zero = program([empty, comment, functionless]);
  assert.deepEqual(diagnostics(zero), []);
  assert([empty, comment, functionless].every(f => zero.getSourceFile(f)));
  checks.push({case: 'zero-function' + suffix, census: [empty, comment, functionless], diagnostics: [],
    units: [empty, comment, functionless].map(f => nodes(zero.getSourceFile(f)).filter(n =>
      ['FunctionDeclaration', 'ArrowFunction', 'FunctionExpression'].includes(n.kind)).length)});
  const bad = write('syntax' + suffix, 'function broken( {\n');
  const badProgram = program([bad]);
  const badDiags = badProgram.getSyntacticDiagnostics().map(d => d.code);
  assert(badDiags.length > 0);
  checks.push({case: 'invalid' + suffix, file: bad, syntacticCodes: badDiags});
}
const shapeFiles = [];
for (const [suffix, kind] of Object.entries(kinds)) {
  const typed = suffix === '.ts' || suffix === '.tsx';
  let text = '// café 😀\n/* multiline\ncomment */\n'
    + (typed ? 'interface Size { value: number; }\n' : '')
    + `const outer = async (${typed ? 'value: number' : 'value'}) => {\n`
    + '  function inner(x) { return x > 1 ? x + 2 : x - 3; }\n'
    + '  const pattern = /a[b-c]+/;\n'
    + '  const message = `café 😀 ${inner(value)}`;\n'
    + '  return pattern.test(message) && value / 2 > 1 ? message : "none";\n};\n'
    + (suffix === '.tsx' || suffix === '.jsx' ? 'const view = <section>{outer(1)}</section>;\n' : '');
  const file = write('shape' + suffix, text);
  const content = fs.readFileSync(file, 'utf8');
  const sf = ts.createSourceFile(file, content, ts.ScriptTarget.Latest, true, kind);
  const p = program([file]);
  assert.equal(p.getSyntacticDiagnostics().length, 0);
  const all = nodes(sf);
  for (const required of ['ArrowFunction', 'FunctionDeclaration', 'RegularExpressionLiteral', 'TemplateExpression', 'BinaryExpression']) {
    assert(all.some(n => n.kind === required), suffix + required);
  }
  const arrow = all.find(n => n.kind === 'ArrowFunction');
  const byteStart = Buffer.byteLength(content.slice(0, arrow.start), 'utf8');
  assert(byteStart > arrow.start, 'UTF-16 offsets must not be treated as UTF-8 bytes');
  assert.equal(Buffer.from(content).subarray(byteStart, Buffer.byteLength(content.slice(0, arrow.end))).toString(),
    content.slice(arrow.start, arrow.end));
  shapeFiles.push({file, scriptKind: ts.ScriptKind[kind], syntaxKinds: [...new Set(all.map(n => n.kind))],
    arrowSpan: {utf16Start: arrow.start, utf16End: arrow.end, byteStart,
      byteEnd: Buffer.byteLength(content.slice(0, arrow.end)), line: sf.getLineAndCharacterOfPosition(arrow.start).line + 1},
    genuineStaticDiagnostics: diagnostics(p)});
}
const a = write('symbols.ts', 'export const used = 1;\nexport const unusedExport = 2;\nexport type Size = {value: number};\n');
const b = write('reexport.ts', 'export {used as alias} from "./symbols.js";\n');
const c = write('consumer.ts', 'import {alias} from "./reexport.js";\nimport type {Size} from "./symbols.js";\n'
  + 'import * as ns from "./symbols.js";\nexport const result: Size = {value: alias + ns.used};\n'
  + 'export function computed(key: keyof typeof ns) { return ns[key]; }\n');
const graph = program([a, b, c]);
assert.deepEqual(diagnostics(graph), []);
const checker = graph.getTypeChecker();
const asf = graph.getSourceFile(a);
const exported = checker.getExportsOfModule(checker.getSymbolAtLocation(asf));
const used = exported.find(s => s.getName() === 'used');
const csf = graph.getSourceFile(c);
const imports = csf.statements.filter(ts.isImportDeclaration);
const aliasNode = imports[0].importClause.namedBindings.elements[0].name;
assert.equal(checker.getAliasedSymbol(checker.getSymbolAtLocation(aliasNode)), used);
const unresolved = write('unresolved.ts', 'import {absent} from "./missing.js";\nimport unknown from "q2-uninstalled-package";\nexport {absent, unknown};\n');
const unresolvedDiagnostics = diagnostics(program([unresolved]));
assert.equal(unresolvedDiagnostics.filter(d => d.code === 2307).length, 2);
const positive = write('findings.ts', 'export {};\nconst unused = 1;\nconst value: number = "wrong";\n'
  + 'export function broken(parameter: number) { return value; console.log(value); }\n');
const positives = diagnostics(program([positive]));
for (const code of [6133, 2322, 7027]) assert(positives.some(d => d.code === code), String(code));
const sourceLess = diagnostics(program([], {checkJs: true, allowJs: false}));
assert(sourceLess.some(d => d.file === null));
const emptyProgram = program([]);
assert.deepEqual(diagnostics(emptyProgram), []);
const missing = diagnostics(program([path.join(fixtureRoot, 'does not exist.ts')]));
assert(missing.some(d => d.code === 6053 && d.file === null));
assert(files.every(f => hash(fs.readFileSync(f.path)) === f.sha256));
const loaded = Object.keys(require.cache).map(file => {
  assert(file === __filename || inside(file, tsRoot), `Unexpected required module ${file}`);
  return {path: file, sha256: hash(fs.readFileSync(file))};
});
const result = {
  version: ts.version, node: process.version, executable: process.execPath,
  options, checks, shapeFiles, files, positives, sourceLess, missing, unresolvedDiagnostics,
  symbols: {exports: exported.map(s => s.getName()), aliasResolvedToUsed: true,
    namespaceComputedAccess: 'Recorded syntax outside finite static-property-reference model; not inferred dead'},
  emptyProgram: {inputFiles: 0, diagnostics: []}, actualReadFiles: [...reads].map(([file, sha256]) => ({file, sha256})),
  loadedModules: loaded, fields: 'Diagnostic code/category/source/file/start/length/message; offsets are UTF-16, source-less path/span null',
  limits: 'No source execution, no external type downloads, no auto type acquisition; JSX parse support is not JSX runner/coverage qualification',
};
fs.writeFileSync(path.join(__dirname, 'q2-tools-source-typescript-results.json'), JSON.stringify(result, null, 2), {flag: 'wx'});
console.log(JSON.stringify({version: ts.version, suffixes: 6, cases: checks.length, shapeCases: shapeFiles.length,
  positiveDiagnosticCount: positives.length, files: files.length, aliasResolved: true, unchangedInputs: true}));
