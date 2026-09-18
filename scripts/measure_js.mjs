/**
 * Shared-parser core and fixed JSRequestV1 producer. Measurement admission,
 * manifest publication and accepting replay belong to the Python controller.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const compilers = new WeakMap();
const analyses = new WeakMap();
const hash = data => crypto.createHash("sha256").update(data).digest("hex");
const compare = (a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b));
const decoder = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true });
const SETTINGS = Object.freeze({
  noEmit: true, allowJs: true, checkJs: true, strict: true,
  noUnusedLocals: true, noUnusedParameters: true, allowUnreachableCode: false,
  target: 99, module: 199, moduleResolution: 99, jsx: 1, types: [], typeRoots: [],
});

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort(compare).map(key => [key, canonical(value[key])]));
  }
  if (typeof value === "number" && !Number.isFinite(value)) throw new Error("Non-finite JSON");
  if (typeof value === "string" && Buffer.from(value).toString("utf8") !== value) {
    throw new Error("Unpaired Unicode surrogate");
  }
  if (value === undefined) throw new Error("Undefined JSON value");
  return value;
}

function digest(value) {
  return hash(Buffer.from(JSON.stringify(canonical(value)) + "\n"));
}

function exactKeys(value, keys, label) {
  if (!value || typeof value !== "object" || Array.isArray(value) ||
      Object.keys(value).sort().join() !== [...keys].sort().join()) {
    throw new Error("Invalid " + label + " fields");
  }
}

function pinnedBytes(root, ref) {
  exactKeys(ref, ["path", "sha256", "bytes"], "Artifact");
  relative(ref.path);
  if (typeof ref.sha256 !== "string" || !/^[0-9a-f]{64}$/u.test(ref.sha256) ||
      !Number.isSafeInteger(ref.bytes) || ref.bytes < 0) throw new Error("Invalid artifact pin");
  const bytes = readRegular(path.join(root, ...ref.path.split("/")));
  if (bytes.length !== ref.bytes || hash(bytes) !== ref.sha256) {
    throw new Error("Artifact changed: " + ref.path);
  }
  return bytes;
}

function relative(name) {
  if (typeof name !== "string" || !name || /[\\:\x00-\x1f]/u.test(name) ||
      name.split("/").some(part => !part || part === "." || part === ".." || /[. ]$/u.test(part)) ||
      Buffer.from(name).toString("utf8") !== name) {
    throw new Error("Noncanonical source path: " + name);
  }
  return name;
}

function absolute(name) {
  if (typeof name !== "string" || !path.isAbsolute(name) || path.resolve(name) !== name) {
    throw new Error("Noncanonical absolute input: " + name);
  }
  for (let current = name; ; current = path.dirname(current)) {
    const info = fs.lstatSync(current);
    if (info.isSymbolicLink() || fs.realpathSync.native(current) !== current) {
      throw new Error("Linked or aliased input: " + current);
    }
    if (path.dirname(current) === current) break;
  }
  return name;
}

function readRegular(name) {
  absolute(name);
  const before = fs.statSync(name, { bigint: true });
  if (!before.isFile() || before.nlink !== 1n || before.ino === 0n) {
    throw new Error("Input is not an independent regular file: " + name);
  }
  const bytes = fs.readFileSync(name);
  const after = fs.statSync(name, { bigint: true });
  for (const key of ["dev", "ino", "size", "mtimeNs", "nlink", "mode"]) {
    if (before[key] !== after[key]) throw new Error("Input changed during read: " + name);
  }
  return bytes;
}

export class SourceBytes {
  #bytes;
  #offsets;
  #lines;

  constructor(name, bytes) {
    relative(name);
    if (!Buffer.isBuffer(bytes)) throw new TypeError("Source bytes must be a Buffer");
    this.#bytes = Buffer.from(bytes);
    this.path = name;
    this.sha256 = hash(bytes);
    this.bytes = bytes.length;
    this.text = decoder.decode(bytes);
    this.#offsets = new Array(this.text.length + 1);
    this.#lines = [0];
    let offset = 0, index = 0;
    for (const character of this.text) {
      this.#offsets[index] = offset;
      index += character.length;
      offset += Buffer.byteLength(character);
      this.#offsets[index] = offset;
    }
    this.#offsets[0] = 0;
    for (let i = 0; i < this.text.length; i++) {
      const character = this.text[i];
      if (character === "\r" && this.text[i + 1] === "\n") i++;
      if (character === "\r" || character === "\n" || character === "\u2028" || character === "\u2029") {
        this.#lines.push(i + 1);
      }
    }
    Object.freeze(this);
  }

  #line(position) {
    let low = 0, high = this.#lines.length;
    while (low + 1 < high) {
      const middle = (low + high) >>> 1;
      if (this.#lines[middle] <= position) low = middle;
      else high = middle;
    }
    return low + 1;
  }

  range(start, length) {
    const end = start + length;
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(length) || start < 0 || length < 0 ||
        this.#offsets[start] === undefined || this.#offsets[end] === undefined) {
      throw new RangeError("Invalid UTF-16 source boundary: " + this.path);
    }
    return { start_byte: this.#offsets[start], end_byte: this.#offsets[end],
      start_line: this.#line(start), end_line: this.#line(length ? end - 1 : start) };
  }

  span(start, end) {
    if (end <= start) throw new RangeError("Syntax Span must be nonempty");
    return this.range(start, end - start);
  }

  slice(start, end) {
    const span = this.range(start, end - start);
    return this.#bytes.subarray(span.start_byte, span.end_byte).toString("utf8");
  }
}

/** Inputs are the existing Python-qualified binding and source description. */
export function openCompiler(binding, source) {
  if (binding.qualified_api !== "typescript-compiler-5-9-3-v1" ||
      binding.observed_version !== "5.9.3" || process.version !== "v24.11.1" ||
      process.arch !== "arm64" || process.execArgv.length !== 0 ||
      digest(source.settings) !== digest(SETTINGS) ||
      process.env.NODE_OPTIONS || process.env.NODE_PATH ||
      Object.keys(process.env).some(name => /^(TS_NODE_|VSCODE_INSPECTOR_OPTIONS$)/iu.test(name))) {
    throw new Error("Unqualified compiler/runtime/settings or preload environment");
  }
  const root = absolute(source.roots.typescript);
  if (binding.module_path !== path.join(root, "lib", "typescript.js") ||
      absolute(binding.executable) !== fs.realpathSync.native(process.execPath) ||
      hash(readRegular(binding.executable)) !== binding.sha256) {
    throw new Error("Compiler module/runtime binding mismatch");
  }
  const pins = new Map();
  for (const pin of source.resources) {
    const name = relative(path.relative(root, pin.path).split(path.sep).join("/"));
    if (pins.has(name)) throw new Error("Duplicate compiler resource: " + name);
    pins.set(name, Object.freeze({ ...pin }));
  }
  function read(name) {
    const pin = pins.get(name);
    if (!pin) throw new Error("Unqualified compiler resource: " + name);
    const bytes = readRegular(pin.path);
    if (bytes.length !== pin.bytes || hash(bytes) !== pin.sha256) {
      throw new Error("Changed compiler resource: " + name);
    }
    return bytes;
  }
  const adapterPath = fileURLToPath(import.meta.url), adapterHash = hash(readRegular(adapterPath));
  function verify() {
    if (hash(readRegular(adapterPath)) !== adapterHash) throw new Error("Parser controller changed");
    for (const name of pins.keys()) read(name);
    if (hash(readRegular(binding.executable)) !== binding.sha256) throw new Error("Runtime changed");
    for (const file of Object.keys(require.cache)) {
      const name = relative(path.relative(root, file).split(path.sep).join("/"));
      read(name);
    }
  }
  verify();
  read("lib/typescript.js");
  const ts = require(binding.module_path);
  if (ts.version !== "5.9.3") throw new Error("Unexpected loaded compiler");
  verify();
  const handle = Object.freeze({ ts, verify });
  const parser = digest({ semantic_version: "typescript-shared-v1",
    adapter_sha256: adapterHash,
    compiler_version: ts.version, module_path: binding.module_path, resources: [...pins].map(([name, pin]) => ({
      path: name, qualified_path: pin.path, sha256: pin.sha256, bytes: pin.bytes,
    })).sort((a, b) => compare(a.path, b.path)),
    runtime: { executable: binding.executable, sha256: binding.sha256,
      version: process.version, architecture: process.arch }, options: SETTINGS });
  compilers.set(handle, { ts, read, verify, parser, binding: structuredClone(binding),
    resourceNames: Object.freeze([...pins.keys()].sort(compare)) });
  return handle;
}

export function parserDigest(compiler) {
  const state = compilers.get(compiler);
  if (!state) throw new TypeError("Expected an opened compiler");
  state.verify();
  return state.parser;
}

export function settingsDigest(jsEntrypoints) {
  if (!Array.isArray(jsEntrypoints)) throw new TypeError("Explicit entrypoint declarations required");
  return digest({ compiler_options: SETTINGS, semantic_version: "typescript-shared-v1",
    js_entrypoints: jsEntrypoints });
}

/**
 * Build one closed-host Program from explicit source entries. Returned AST and
 * checker objects are native-only; this is not a JSResultV1 or ParsedInventory.
 */
export function parseProgram(compiler, root, entries, metadata = []) {
  compiler = compilers.get(compiler);
  if (!compiler) throw new TypeError("Expected a compiler opened by openCompiler");
  absolute(root);
  compiler.verify();
  const { ts } = compiler;
  const scriptKinds = { ".js": ts.ScriptKind.JS, ".mjs": ts.ScriptKind.JS,
    ".cjs": ts.ScriptKind.JS, ".jsx": ts.ScriptKind.JSX, ".ts": ts.ScriptKind.TS,
    ".tsx": ts.ScriptKind.TSX };
  const sources = new Map(), failures = new Map(), refs = new Map(), reads = new Map();
  const sourceFiles = new Map(), folded = new Set();
  const roots = [];
  for (const entry of [...entries, ...metadata]) {
    relative(entry.path);
    if (folded.has(entry.path.toLowerCase())) throw new Error("Duplicate/aliased source: " + entry.path);
    folded.add(entry.path.toLowerCase());
    const isCode = entries.includes(entry);
    const suffix = path.posix.extname(entry.path).toLowerCase();
    if (isCode && !Object.hasOwn(scriptKinds, suffix)) throw new Error("Unsupported reader: " + suffix);
    if (!isCode && path.posix.basename(entry.path) !== "package.json") {
      throw new Error("Undeclared metadata kind: " + entry.path);
    }
    if (!/^[0-9a-f]{64}$/u.test(entry.sha256) || !Number.isSafeInteger(entry.bytes) || entry.bytes < 0) {
      throw new Error("Invalid source pin: " + entry.path);
    }
    const virtual = "/subject/" + entry.path;
    refs.set(virtual, { scope: "subject", path: entry.path, sha256: entry.sha256, bytes: entry.bytes });
    if (isCode) roots.push(virtual);
    let bytes;
    try {
      bytes = readRegular(path.join(root, ...entry.path.split("/")));
    } catch (error) {
      if (!["ENOENT", "EACCES", "EPERM"].includes(error.code)) throw error;
      if (!isCode) throw new Error("Unreadable admitted metadata: " + entry.path, { cause: error });
      failures.set(virtual, { reason: error.code + ": " + entry.path, observed: null, code: error.code });
      continue;
    }
    if (hash(bytes) !== entry.sha256 || bytes.length !== entry.bytes) {
      throw new Error("Source changed since inventory: " + entry.path);
    }
    try {
      sources.set(virtual, new SourceBytes(entry.path, bytes));
    } catch (error) {
      if (!(error instanceof TypeError) || error.code !== "ERR_ENCODING_INVALID_ENCODED_DATA") throw error;
      if (!isCode) throw new Error("Invalid UTF-8 metadata: " + entry.path, { cause: error });
      failures.set(virtual, { reason: "Invalid UTF-8: " + entry.path, observed: hash(bytes) });
    }
  }
  for (const name of compiler.resourceNames) {
    const bytes = compiler.read(name);
    const virtual = "/tool-resource/" + name;
    refs.set(virtual, { scope: "tool-resource", path: name, sha256: hash(bytes), bytes: bytes.length });
  }
  function source(name) {
    if (!refs.has(name) || failures.has(name)) return undefined;
    if (!sources.has(name)) {
      const ref = refs.get(name);
      sources.set(name, new SourceBytes(ref.path, compiler.read(ref.path)));
    }
    reads.set(name, refs.get(name));
    return sources.get(name);
  }
  const knownDirectories = new Set(["/", "/subject", "/tool-resource"]);
  for (const name of refs.keys()) {
    for (let dir = path.posix.dirname(name); dir !== "/"; dir = path.posix.dirname(dir)) {
      knownDirectories.add(dir);
    }
  }
  const host = {
    getSourceFile(name, version) {
      const unit = source(name);
      if (!unit) return undefined;
      if (!sourceFiles.has(name)) {
        const kind = scriptKinds[path.posix.extname(name).toLowerCase()] ?? ts.ScriptKind.JSON;
        sourceFiles.set(name, ts.createSourceFile(name, unit.text, version, true, kind));
      }
      return sourceFiles.get(name);
    },
    getDefaultLibFileName: options => "/tool-resource/lib/" + ts.getDefaultLibFileName(options),
    getDefaultLibLocation: () => "/tool-resource/lib",
    getCurrentDirectory: () => "/subject",
    getCanonicalFileName: name => name,
    useCaseSensitiveFileNames: () => true,
    getNewLine: () => "\n",
    fileExists: name => refs.has(name) && !failures.has(name),
    readFile: name => source(name)?.text,
    directoryExists: name => knownDirectories.has(name),
    getDirectories: name => [...knownDirectories].filter(dir => dir !== name && path.posix.dirname(dir) === name),
    realpath: name => name,
    writeFile() { throw new Error("Unexpected TypeScript output"); },
  };
  const program = ts.createProgram(roots, { ...SETTINGS, types: [], typeRoots: [] }, host);
  const checker = program.getTypeChecker();
  function message(value, category, code) {
    if (typeof value === "string") return { text: value, category, code, next: [] };
    return { text: value.messageText, category: value.category, code: value.code,
      next: (value.next ?? []).map(item => message(item, item.category, item.code)) };
  }
  function location(item) {
    if (!item.file) {
      if (item.start !== undefined || item.length !== undefined) throw new Error("Unpaired diagnostic location");
      return { file: null, utf16_start: null, utf16_length: null, byte_range: null };
    }
    const unit = source(item.file.fileName);
    if (!unit) throw new Error("Diagnostic refers to unread source");
    return { file: refs.get(item.file.fileName), utf16_start: item.start, utf16_length: item.length,
      byte_range: unit.range(item.start, item.length) };
  }
  const diagnostics = ts.getPreEmitDiagnostics(program).map(item => {
    const record = { code: item.code, category: item.category, source: item.source ?? null,
      message: message(item.messageText, item.category, item.code), location: location(item),
      related: (item.relatedInformation ?? []).map(related => ({ code: related.code,
        category: related.category, message: message(related.messageText, related.category, related.code),
        location: location(related) })) };
    return { id: digest(record), ...record };
  }).sort((a, b) => compare(a.id, b.id));
  const census = entries.map(entry => {
    const virtual = "/subject/" + entry.path;
    const failure = failures.get(virtual);
    const file = program.getSourceFile(virtual);
    const badSyntax = file ? program.getSyntacticDiagnostics(file) : [];
    const ok = !failure && file && badSyntax.length === 0;
    let tokens = 0, functions = 0;
    if (ok) {
      const stack = [file];
      while (stack.length) {
        const node = stack.pop();
        if (node.kind === ts.SyntaxKind.JSDoc) continue;
        if (ts.isFunctionLike(node) && node.body) functions++;
        const children = node.getChildren(file);
        if (ts.isToken(node) && node.kind !== ts.SyntaxKind.EndOfFileToken && node.getWidth(file) > 0) tokens++;
        stack.push(...children);
      }
    }
    return { path: entry.path, source_sha256: entry.sha256,
      observed_sha256: failure ? failure.observed : sources.get(virtual).sha256,
      suffix: path.posix.extname(entry.path).toLowerCase(), state: ok ? "processed" : "failed",
      reason: ok ? "" : failure?.reason ?? (badSyntax.length ? "Invalid syntax" : "Missing compiler source"),
      token_count: ok ? tokens : null, function_count: ok ? functions : null,
      diagnostic_ids: diagnostics.filter(item => item.location.file?.scope === "subject" &&
        item.location.file.path === entry.path).map(item => item.id) };
  }).sort((a, b) => compare(a.path, b.path));
  function verify() {
    compiler.verify();
    for (const ref of refs.values()) {
      if (ref.scope !== "subject") continue;
      const failure = failures.get("/subject/" + ref.path);
      let bytes;
      try {
        bytes = readRegular(path.join(root, ...ref.path.split("/")));
      } catch (error) {
        if (failure?.code && error.code === failure.code) continue;
        throw error;
      }
      if (failure?.observed === null) throw new Error("Failed source became readable during parsing");
      if (hash(bytes) !== ref.sha256 || bytes.length !== ref.bytes) throw new Error("Source changed during parsing");
    }
  }
  verify();
  const result = { program, checker, census, diagnostics,
    sources: new Map([...sources].filter(([name]) => name.startsWith("/subject/"))),
    reads: [...reads.values()].sort((a, b) => compare(a.scope + "/" + a.path, b.scope + "/" + b.path)) };
  analyses.set(result, { compiler, root, program, checker, sources, refs, host, verify,
    entries: structuredClone(entries), census: structuredClone(census), diagnostics: structuredClone(diagnostics) });
  return result;
}

function analysis(result) {
  const state = analyses.get(result);
  if (!state) throw new TypeError("Expected a parsed Program");
  state.verify();
  return state;
}

function ordered(records) {
  return records.sort((a, b) => compare(a.path ?? "", b.path ?? "") ||
    (a.span?.start_byte ?? 0) - (b.span?.start_byte ?? 0) ||
    (a.span?.end_byte ?? 0) - (b.span?.end_byte ?? 0) ||
    compare(JSON.stringify(canonical(a)), JSON.stringify(canonical(b))));
}

function tokens(ts, node, file) {
  const result = [], stack = [node];
  while (stack.length) {
    const current = stack.pop();
    if (current.kind === ts.SyntaxKind.JSDoc) continue;
    if (ts.isToken(current) && current.kind !== ts.SyntaxKind.EndOfFileToken && current.getWidth(file)) {
      result.push({ kind: ts.SyntaxKind[current.kind], text: current.getText(file) });
    } else {
      stack.push(...[...current.getChildren(file)].reverse());
    }
  }
  return result;
}

function checkedJSON(ts, name, text) {
  const value = JSON.parse(text);
  const file = ts.createSourceFile(name, text, ts.ScriptTarget.JSON, true, ts.ScriptKind.JSON);
  function visit(node) {
    if (ts.isObjectLiteralExpression(node)) {
      const seen = new Set();
      for (const property of node.properties) {
        const key = JSON.parse(property.name.getText(file));
        if (seen.has(key)) throw new Error("Duplicate JSON key: " + key);
        seen.add(key);
      }
    }
    ts.forEachChild(node, visit);
  }
  visit(file);
  return value;
}

function checkBinding(state, binding, config) {
  const fields = ["semantic_version", "run_id", "revision", "git_revision", "inventory_sha256",
    "source_sha256", "parser_sha256", "toolset_sha256", "settings_sha256", "policy_sha256"];
  if (Object.keys(binding).sort().join() !== fields.sort().join() ||
      binding.semantic_version !== "typescript-shared-v1" ||
      !["base", "head"].includes(binding.revision) || typeof binding.run_id !== "string" || !/^[!-~]+$/u.test(binding.run_id) ||
      typeof binding.git_revision !== "string" || !/^(?:[0-9a-f]{40}|[0-9a-f]{64})$/u.test(binding.git_revision) ||
      fields.filter(key => key.endsWith("_sha256")).some(key => typeof binding[key] !== "string" || !/^[0-9a-f]{64}$/u.test(binding[key])) ||
      binding.parser_sha256 !== state.compiler.parser ||
      binding.settings_sha256 !== settingsDigest(config.js_entrypoints)) {
    throw new Error("Invalid or mismatched JS binding");
  }
}

/** Serialize the existing Program, never execute source or construct ParsedInventory. */
export function serializeProgram(result, binding, configInput) {
  const state = analysis(result), { program, checker } = state, { ts } = state.compiler;
  const configRef = configInput.input;
  relative(configRef.path);
  if (Object.keys(configRef).sort().join() !== "bytes,path,scope,sha256" ||
      configRef.scope !== "head-contract" || !Buffer.isBuffer(configInput.bytes) ||
      hash(configInput.bytes) !== configRef.sha256 || configInput.bytes.length !== configRef.bytes) {
    throw new Error("Source-bound configuration bytes required");
  }
  const config = checkedJSON(ts, configRef.path, decoder.decode(configInput.bytes));
  if (config.schema_version !== 1 || config.semantic_profile !== "workflow-reliability-q-v1" ||
      !Array.isArray(config.js_entrypoints) || !Array.isArray(config.suites) ||
      !config.tools?.typescript || digest(config.tools.typescript) !== digest(state.compiler.binding)) {
    throw new Error("Expected source-bound MeasurementConfig");
  }
  checkBinding(state, binding, config);
  const byFile = new Map(state.census.filter(row => row.state === "processed").map(row => {
    const file = program.getSourceFile("/subject/" + row.path);
    return [file, { row, unit: state.sources.get(file.fileName) }];
  }));
  const declarationData = new Map(), scopes = new Map(), declarations = new Set();
  const symbolRecords = new Map(), symbolIds = new Map();
  const exports = [], aliases = [], references = [], modules = [], outside = [], directives = [], syntax = [];
  function site(node) {
    const data = byFile.get(node.getSourceFile());
    if (!data) throw new Error("Site is not a successfully parsed inventory input");
    return { path: data.row.path, span: data.unit.span(node.getStart(), node.end) };
  }
  function scopeNode(node) {
    return ts.isFunctionLike(node) || ts.isClassLike(node) || ts.isModuleDeclaration(node) ||
      ts.isBlock(node) || ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node);
  }
  function discover(symbol, seen = new Set()) {
    if (!symbol || seen.has(symbol)) return;
    seen.add(symbol);
    if (symbol.flags & ts.SymbolFlags.Alias) discover(checker.getAliasedSymbol(symbol), seen);
    for (const declaration of symbol.getDeclarations() ?? []) {
      if (byFile.has(declaration.getSourceFile()) && declaration.getWidth() > 0) declarations.add(declaration);
    }
  }
  function bindingProperty(node) {
    if (!ts.isBindingElement(node) || !ts.isObjectBindingPattern(node.parent)) return null;
    const selection = node.propertyName ?? node.name;
    const key = ts.isComputedPropertyName(selection) ? selection.expression : selection;
    const literal = !node.dotDotDotToken && (ts.isIdentifier(selection) ||
      ts.isStringLiteralLike(key) || ts.isNumericLiteral(key));
    return { selection, dynamic: !literal,
      symbol: literal ? checker.getPropertyOfType(checker.getTypeAtLocation(node.parent), key.text) : undefined };
  }
  for (const [file] of byFile) {
    const counts = new Map();
    function visit(node, scope) {
      scopes.set(node, scope);
      discover(checker.getSymbolAtLocation(node));
      if (node.name) discover(checker.getSymbolAtLocation(node.name));
      if (ts.isShorthandPropertyAssignment(node)) discover(checker.getShorthandAssignmentValueSymbol(node));
      discover(bindingProperty(node)?.symbol);
      let next = scope;
      if (scopeNode(node)) {
        const name = node.name?.getText(file) ?? "<anonymous>";
        const label = ts.SyntaxKind[node.kind] + ":" + name;
        const key = JSON.stringify([...scope, label]);
        const occurrence = counts.get(key) ?? 0;
        counts.set(key, occurrence + 1);
        next = [...scope, name === "<anonymous>" ? label + "#" + occurrence : label];
      }
      ts.forEachChild(node, child => visit(child, next));
    }
    visit(file, []);
    const symbol = checker.getSymbolAtLocation(file);
    discover(symbol);
    if (symbol) for (const exported of checker.getExportsOfModule(symbol)) discover(exported);
  }
  const occurrences = new Map();
  for (const node of [...declarations].sort((a, b) =>
    compare(a.getSourceFile().fileName, b.getSourceFile().fileName) || a.pos - b.pos || a.end - b.end)) {
    const file = node.getSourceFile(), data = byFile.get(file);
    const descriptor = { path: data.row.path, kind: ts.SyntaxKind[node.kind],
      lexical_scope: scopes.get(node) ?? [], name: node.name?.getText(file) ?? (node === file ? data.row.path : "<anonymous>"),
      token_context: tokens(ts, node, file) };
    const key = digest(descriptor), occurrence = occurrences.get(key) ?? 0;
    occurrences.set(key, occurrence + 1);
    declarationData.set(node, { ...descriptor, occurrence, source_sha256: data.row.source_sha256,
      span: data.unit.span(node.getStart(file), node.end) });
  }
  function unresolved(reason) {
    return { state: "unresolved", symbol_ids: [], external: null, reason };
  }
  function external(name) {
    return { state: "external", symbol_ids: [], external: name, reason: "" };
  }
  function importOrigin(node) {
    for (let current = node; current; current = current.parent) {
      if ((ts.isImportDeclaration(current) || ts.isExportDeclaration(current)) && current.moduleSpecifier) {
        return current.moduleSpecifier.text;
      }
      if (ts.isImportEqualsDeclaration(current) && ts.isExternalModuleReference(current.moduleReference)) {
        return current.moduleReference.expression.text;
      }
    }
    return null;
  }
  function resolution(symbol) {
    if (!symbol) return unresolved("No statically resolved symbol");
    const original = symbol;
    if (symbol.flags & ts.SymbolFlags.Alias) symbol = checker.getAliasedSymbol(symbol);
    const originalDeclarations = symbol.getDeclarations() ?? [];
    const named = originalDeclarations.find(node => node.name);
    const declaredSymbol = named && checker.getSymbolAtLocation(named.name);
    if (declaredSymbol && !(declaredSymbol.flags & ts.SymbolFlags.Alias)) {
      const declared = declaredSymbol.getDeclarations() ?? [];
      if (declared.length === originalDeclarations.length && declared.every(node => originalDeclarations.includes(node))) {
        symbol = declaredSymbol;
      }
    }
    const found = (symbol.getDeclarations() ?? []).map(node => declarationData.get(node)).filter(Boolean);
    if (found.length) {
      if (!symbolIds.has(symbol)) {
        found.sort((a, b) => compare(a.path, b.path) || a.span.start_byte - b.span.start_byte ||
          a.span.end_byte - b.span.end_byte || compare(a.kind, b.kind));
        const descriptors = found.map(({ source_sha256, span, ...descriptor }) => descriptor);
        descriptors.sort((a, b) => compare(JSON.stringify(canonical(a)), JSON.stringify(canonical(b))));
        const id = digest(["js-symbol-v1", descriptors]);
        if (symbolRecords.has(id) && (symbolRecords.get(id).name !== symbol.getName() ||
            symbolRecords.get(id).flags !== symbol.flags)) throw new Error("Colliding source symbol identities");
        symbolIds.set(symbol, id);
        symbolRecords.set(id, { id, name: symbol.getName(), flags: symbol.flags, declarations: found });
      }
      return { state: "local", symbol_ids: [symbolIds.get(symbol)], external: null, reason: "" };
    }
    const library = (symbol.getDeclarations() ?? []).find(node => node.getSourceFile().fileName.startsWith("/tool-resource/"));
    if (library) return external(library.getSourceFile().fileName.slice(1) + ":" + symbol.getName());
    for (const node of original.getDeclarations() ?? []) {
      const origin = importOrigin(node);
      if (origin && !origin.startsWith(".") && !origin.startsWith("/") && !origin.startsWith("#")) {
        return external(origin + ":" + original.getName());
      }
    }
    return unresolved("Symbol has no nonempty declaration in the successfully parsed inventory");
  }
  function moduleTarget(literal, file) {
    const specifier = literal.text;
    const mode = program.getModeForUsageLocation(file, literal);
    const resolved = ts.resolveModuleName(specifier, file.fileName, program.getCompilerOptions(), state.host,
      undefined, undefined, mode).resolvedModule;
    if (resolved?.resolvedFileName.startsWith("/subject/")) {
      const target = resolved.resolvedFileName.slice("/subject/".length);
      if (state.entries.some(entry => entry.path === target)) {
        return { resolution: "local", targets: [target], external: null, reason: "" };
      }
      return { resolution: "unresolved", targets: [], external: null, reason: "Resolved source is outside inventory" };
    }
    if (!specifier.startsWith(".") && !specifier.startsWith("/") && !specifier.startsWith("#") && !/^[a-z]:/iu.test(specifier)) {
      return { resolution: "external", targets: [], external: specifier, reason: "" };
    }
    return { resolution: "unresolved", targets: [], external: null, reason: "Literal local module did not resolve" };
  }
  function isGlobal(node, name) {
    if (!ts.isIdentifier(node) || node.text !== name) return false;
    const declarations = checker.getSymbolAtLocation(node)?.getDeclarations() ?? [];
    return !declarations.some(declaration => declaration.getSourceFile().fileName.startsWith("/subject/"));
  }
  function callOrigin(node, seen = new Set()) {
    if (seen.has(node)) return null;
    seen.add(node);
    if (ts.isPropertyAccessExpression(node) || ts.isElementAccessExpression(node)) return callOrigin(node.expression, seen);
    if (ts.isCallExpression(node) && isGlobal(node.expression, "require") &&
        node.arguments.length === 1 && ts.isStringLiteralLike(node.arguments[0])) return node.arguments[0].text;
    for (const declaration of checker.getSymbolAtLocation(node)?.getDeclarations() ?? []) {
      const imported = importOrigin(declaration);
      if (imported) return imported;
      if (ts.isVariableDeclaration(declaration) && declaration.initializer) {
        const origin = callOrigin(declaration.initializer, seen);
        if (origin) return origin;
      }
      if (ts.isBindingElement(declaration) && ts.isVariableDeclaration(declaration.parent.parent) &&
          declaration.parent.parent.initializer) {
        const origin = callOrigin(declaration.parent.parent.initializer, seen);
        if (origin) return origin;
      }
    }
    return null;
  }
  for (const [file, data] of byFile) {
    const nodes = [], imports = [], sites = [], notes = [];
    function outsideSite(node, kind, reason) {
      const value = { ...site(node), kind, reason };
      outside.push(value);
      sites.push({ kind, span: value.span, reason });
    }
    function moduleReference(node, argument, kind) {
      const location = site(node);
      if (argument && ts.isStringLiteralLike(argument)) {
        const target = moduleTarget(argument, file);
        modules.push({ ...location, specifier: argument.text, kind, ...target });
        imports.push({ specifier: argument.text, kind, span: location.span });
      } else {
        modules.push({ ...location, specifier: null, kind, resolution: "dynamic", targets: [], external: null,
          reason: "Computed module specifier" });
        outsideSite(node, "computed-import", "Computed module specifier");
      }
    }
    function visit(node) {
      if (node.kind === ts.SyntaxKind.JSDoc) return;
      if (node !== file && node.kind !== ts.SyntaxKind.EndOfFileToken && node.getWidth(file) > 0) {
        nodes.push({ kind: ts.SyntaxKind[node.kind], span: site(node).span });
      }
      if (ts.isImportDeclaration(node)) {
        const allTypeOnly = node.importClause?.isTypeOnly ||
          (!node.importClause?.name && node.importClause?.namedBindings && ts.isNamedImports(node.importClause.namedBindings) &&
            node.importClause.namedBindings.elements.length > 0 &&
            node.importClause.namedBindings.elements.every(element => element.isTypeOnly));
        moduleReference(node, node.moduleSpecifier, allTypeOnly ? "type-import" : "import");
      } else if (ts.isExportDeclaration(node) && node.moduleSpecifier) {
        const allTypeOnly = node.isTypeOnly || (node.exportClause && ts.isNamedExports(node.exportClause) &&
          node.exportClause.elements.length > 0 && node.exportClause.elements.every(element => element.isTypeOnly));
        moduleReference(node, node.moduleSpecifier, allTypeOnly ? "type-import" : "reexport");
      } else if (ts.isImportTypeNode(node)) {
        moduleReference(node, ts.isLiteralTypeNode(node.argument) ? node.argument.literal : null, "type-import");
      } else if (ts.isImportEqualsDeclaration(node) && ts.isExternalModuleReference(node.moduleReference)) {
        moduleReference(node, node.moduleReference.expression, "require");
      } else if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) {
        moduleReference(node, node.arguments[0], "import");
      } else if (ts.isCallExpression(node) && isGlobal(node.expression, "require")) {
        moduleReference(node, node.arguments.length === 1 ? node.arguments[0] : null, "require");
      }
      if ((ts.isCallExpression(node) || ts.isNewExpression(node)) &&
          (isGlobal(node.expression, "eval") || isGlobal(node.expression, "Function"))) {
        outsideSite(node, "reflection", "Runtime code construction is outside the static model");
      }
      if (ts.isCallExpression(node)) {
        const origin = callOrigin(node.expression);
        if (origin === "node:child_process" || origin === "child_process") {
          outsideSite(node, "runtime-command", "Child-process launch target is not an import edge");
        }
      }
      if (ts.isImportSpecifier(node) || ts.isNamespaceImport(node) ||
          ts.isImportEqualsDeclaration(node) || (ts.isImportClause(node) && node.name)) {
        aliases.push({ ...site(node.name), name: node.name.text,
          kind: ts.isNamespaceImport(node) ? "namespace" : ts.isImportEqualsDeclaration(node) ? "import-equals" : "import",
          target: resolution(checker.getSymbolAtLocation(node.name)) });
      }
      if (ts.isExportSpecifier(node)) {
        const target = resolution(checker.getExportSpecifierLocalTargetSymbol(node));
        exports.push({ ...site(node), name: node.name.text, kind: "reexport", type_only: !!node.isTypeOnly || !!node.parent.parent.isTypeOnly, target });
        aliases.push({ ...site(node), name: node.name.text, kind: "reexport", target });
      } else if (ts.isExportDeclaration(node) && !node.exportClause) {
        exports.push({ ...site(node), name: "*", kind: "star", type_only: !!node.isTypeOnly,
          target: resolution(checker.getSymbolAtLocation(node.moduleSpecifier)) });
      } else if (ts.isNamespaceExport(node)) {
        const target = resolution(checker.getSymbolAtLocation(node.name));
        exports.push({ ...site(node), name: node.name.text, kind: "reexport", type_only: !!node.parent.isTypeOnly, target });
        aliases.push({ ...site(node), name: node.name.text, kind: "reexport", target });
      }
      if (ts.isElementAccessExpression(node)) {
        const argument = node.argumentExpression;
        const literal = argument && (ts.isStringLiteralLike(argument) || ts.isNumericLiteral(argument));
        const target = literal ? resolution(checker.getPropertyOfType(checker.getTypeAtLocation(node.expression), argument.text)) :
          { state: "dynamic", symbol_ids: [], external: null, reason: "Computed property access" };
        references.push({ ...site(node), kind: "namespace-element", target });
        if (!literal) outsideSite(node, "reflection", "Computed property access prevents complete static absence-of-reference proof");
      }
      const binding = bindingProperty(node);
      if (binding) {
        const target = binding.dynamic ?
          { state: "dynamic", symbol_ids: [], external: null, reason: "Computed or rest object binding selection" } :
          resolution(binding.symbol);
        references.push({ ...site(binding.selection), kind: "property", target });
        if (target.state === "dynamic" || target.state === "unresolved") {
          outsideSite(binding.selection, "reflection", target.reason + "; no complete static absence-of-reference proof");
        }
      }
      if (ts.isIdentifier(node) || ts.isPrivateIdentifier(node)) {
        const parent = node.parent;
        const shorthand = ts.isShorthandPropertyAssignment(parent);
        const declarationName = parent.name === node && !shorthand &&
          !ts.isPropertyAccessExpression(parent) && !ts.isExportSpecifier(parent);
        const bindingKey = ts.isBindingElement(parent) && ts.isObjectBindingPattern(parent.parent) &&
          parent.propertyName === node;
        if (!declarationName && !bindingKey) {
          references.push({ ...site(node),
            kind: shorthand ? "shorthand" : ts.isPartOfTypeNode(node) ? "type" :
              ts.isExportSpecifier(parent) ? "export" : ts.isPropertyAccessExpression(parent) && parent.name === node ? "property" : "identifier",
            target: resolution(shorthand ? checker.getShorthandAssignmentValueSymbol(parent) : checker.getSymbolAtLocation(node)) });
        }
      }
      ts.forEachChild(node, visit);
    }
    visit(file);
    const module = checker.getSymbolAtLocation(file);
    if (module) {
      for (const symbol of checker.getExportsOfModule(module)) {
        if (exports.some(item => item.path === data.row.path && item.name === symbol.name)) continue;
        const declaration = (symbol.getDeclarations() ?? []).find(node => node.getSourceFile() === file);
        if (!declaration || !declaration.getWidth(file)) continue;
        exports.push({ ...site(declaration), name: symbol.getName(),
          kind: symbol.name === "default" ? "default" : ts.isBinaryExpression(declaration) ||
            ts.isPropertyAccessExpression(declaration) ? "commonjs" : "declaration",
          type_only: (symbol.flags & ts.SymbolFlags.Value) === 0, target: resolution(symbol) });
      }
    }
    // These are the pinned 5.9.3 parser's own directive ranges, not a comment lexer.
    for (const item of file.commentDirectives ?? []) {
      if (![0, 1].includes(item.type)) throw new Error("Unknown qualified comment directive");
      directives.push({ path: data.row.path, span: data.unit.span(item.range.pos, item.range.end),
        kind: item.type === 0 ? "ts-expect-error" : "ts-ignore",
        text: data.unit.slice(item.range.pos, item.range.end) });
    }
    if (!(file.pragmas instanceof Map)) throw new Error("Missing qualified parser pragma map");
    for (const kind of ["ts-check", "ts-nocheck"]) {
      const value = file.pragmas.get(kind);
      for (const item of value ? Array.isArray(value) ? value : [value] : []) {
        directives.push({ path: data.row.path, span: data.unit.span(item.range.pos, item.range.end),
          kind, text: data.unit.slice(item.range.pos, item.range.end) });
      }
    }
    for (const item of directives.filter(item => item.path === data.row.path)) notes.push(item.kind + ": " + item.text);
    syntax.push({ schema_version: 1, revision: binding.revision, inventory_sha256: binding.inventory_sha256,
      path: data.row.path, source_sha256: data.row.source_sha256, parser_sha256: binding.parser_sha256,
      semantic_version: binding.semantic_version, nodes: ordered(nodes), literal_imports: ordered(imports),
      outside_model: ordered(sites), diagnostics: notes });
  }
  const entrypoints = deriveEntrypoints(state, binding.revision, config, configRef, outside);
  for (const symbol of declarations) resolution(checker.getSymbolAtLocation(symbol.name ?? symbol));
  const artifact = { schema_version: 1, binding: structuredClone(binding),
    inputs: [...state.refs.values(), structuredClone(configRef)].sort((a, b) => compare(a.scope + "/" + a.path, b.scope + "/" + b.path)),
    files: structuredClone(state.census), symbols: [...symbolRecords.values()].sort((a, b) => compare(a.id, b.id)),
    exports: ordered(exports), aliases: ordered(aliases), references: ordered(references),
    module_references: ordered(modules), entrypoints, outside_model: ordered(outside),
    directives: ordered(directives), diagnostics: structuredClone(state.diagnostics) };
  syntax.sort((a, b) => compare(a.path, b.path));
  state.verify();
  state.serialized = { binding: structuredClone(binding), syntax: structuredClone(syntax) };
  return { syntax, symbols: artifact };
}

function deriveEntrypoints(state, revision, config, configRef, outside) {
  const { ts } = state.compiler, roots = new Map();
  const rows = new Map(state.census.map(row => [row.path, row]));
  const isJS = name => [".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"].includes(path.posix.extname(name).toLowerCase());
  function add(name, requested, origin) {
    relative(name);
    const row = rows.get(name);
    if (!row && (revision !== "base" || origin.kind === "package")) {
      throw new Error("Entrypoint is outside the JS inventory: " + name);
    }
    const file = state.program.getSourceFile("/subject/" + name);
    const module = file && state.checker.getSymbolAtLocation(file);
    const available = row?.state === "processed" && module ?
      state.checker.getExportsOfModule(module).map(symbol => symbol.getName()).sort(compare) : [];
    if (requested !== null && (!Array.isArray(requested) || requested.some(value => typeof value !== "string" || !value) ||
        new Set(requested).size !== requested.length || (row && requested.some(value => !available.includes(value))))) {
      throw new Error("Entrypoint public exports do not match source: " + name);
    }
    const publicExports = requested ?? available;
    if (!roots.has(name)) roots.set(name, { path: name, source_sha256: row?.source_sha256 ?? null,
      state: row ? "active" : "absent-at-revision", public_exports: [], origins: [] });
    const root = roots.get(name);
    root.public_exports = [...new Set([...root.public_exports, ...publicExports])].sort(compare);
    root.origins.push(origin);
  }
  config.js_entrypoints.forEach((entry, index) => {
    if (!entry || Object.keys(entry).sort().join() !== "origin_ref,path,public_exports" ||
        typeof entry.origin_ref !== "string" || !entry.origin_ref || !isJS(entry.path)) {
      throw new Error("Invalid JS entrypoint declaration");
    }
    if (config.js_entrypoints.slice(0, index).some(previous => previous.path === entry.path)) {
      throw new Error("Duplicate JS entrypoint declaration");
    }
    add(entry.path, entry.public_exports, { kind: "config", input: structuredClone(configRef),
      pointer: "/js_entrypoints/" + index, origin_ref: entry.origin_ref });
  });
  config.suites.forEach((suite, index) => {
    if (suite.runner !== "node-native") return;
    if (typeof suite.id !== "string" || !suite.id || !Array.isArray(suite.test_files)) {
      throw new Error("Invalid native suite entrypoint");
    }
    suite.test_files.forEach((name, fileIndex) => {
      relative(name);
      if (isJS(name)) add(name, null, { kind: "suite", input: structuredClone(configRef),
        pointer: "/suites/" + index + "/test_files/" + fileIndex, origin_ref: "suite:" + suite.id });
    });
  });
  const escape = value => value.replaceAll("~", "~0").replaceAll("/", "~1");
  for (const [virtual, ref] of state.refs) {
    if (ref.scope !== "subject" || path.posix.basename(ref.path) !== "package.json") continue;
    const unit = state.sources.get(virtual), value = checkedJSON(ts, ref.path, unit.text);
    const file = ts.createSourceFile(virtual, unit.text, ts.ScriptTarget.JSON, true, ts.ScriptKind.JSON);
    const pointers = new Map();
    function locate(node, pointer) {
      pointers.set(pointer, node);
      if (ts.isObjectLiteralExpression(node)) {
        for (const property of node.properties) locate(property.initializer, pointer + "/" + escape(JSON.parse(property.name.getText(file))));
      } else if (ts.isArrayLiteralExpression(node)) {
        node.elements.forEach((element, index) => locate(element, pointer + "/" + index));
      }
    }
    if (file.statements.length !== 1 || !ts.isExpressionStatement(file.statements[0])) throw new Error("Invalid package object");
    locate(file.statements[0].expression, "");
    function unsupported(pointer) {
      const node = pointers.get(pointer);
      outside.push({ path: ref.path, span: unit.span(node.getStart(file), node.end), kind: "reflection",
        reason: "Unsupported package entrypoint value at " + pointer + "; no complete dead-symbol claim" });
    }
    function target(value, pointer) {
      if (value === null) return;
      if (typeof value !== "string" || !value || value.includes("*") ||
          (pointer.startsWith("/exports") && !value.startsWith("./"))) {
        unsupported(pointer);
        return;
      }
      const declared = value.startsWith("./") ? value.slice(2) : value;
      relative(declared);
      const name = path.posix.join(path.posix.dirname(ref.path), declared);
      if (!isJS(name)) {
        unsupported(pointer);
        return;
      }
      add(name, null, { kind: "package", input: structuredClone(ref), pointer,
        origin_ref: "package:" + ref.path + "#" + pointer });
    }
    if (Object.hasOwn(value, "exports")) {
      if (value.exports && typeof value.exports === "object" && !Array.isArray(value.exports) &&
          Object.keys(value.exports).every(key => key === "." || key.startsWith("./"))) {
        for (const [key, declared] of Object.entries(value.exports)) target(declared, "/exports/" + escape(key));
      } else target(value.exports, "/exports");
    }
    if (Object.hasOwn(value, "bin")) {
      if (value.bin && typeof value.bin === "object" && !Array.isArray(value.bin)) {
        for (const [key, declared] of Object.entries(value.bin)) target(declared, "/bin/" + escape(key));
      } else target(value.bin, "/bin");
    }
  }
  return [...roots.values()].sort((a, b) => compare(a.path, b.path)).map(root => ({
    ...root, origins: root.origins.sort((a, b) => compare(JSON.stringify(canonical(a)), JSON.stringify(canonical(b)))),
  }));
}

/** Enumerate the unsampled eligible population; this never writes or runs mutants. */
export function candidatesForProgram(result, inventory, syntaxEvidence) {
  const state = analysis(result), { ts } = state.compiler;
  if (!state.serialized) throw new Error("Serialize source-bound syntax before requesting candidates");
  const { binding, syntax } = state.serialized;
  const { digest: inventoryHash, ...payload } = inventory;
  if (inventory.schema_version !== 1 || inventory.revision !== "head" ||
      inventory.enumeration_state !== "complete" || inventory.enumeration_errors.length ||
      !Array.isArray(inventory.entries)) throw new Error("Candidates require a complete head Inventory");
  if (inventoryHash !== digest(payload) || inventoryHash !== binding.inventory_sha256 ||
      inventory.source_sha256 !== binding.source_sha256 || inventory.revision !== binding.revision ||
      digest(syntaxEvidence) !== digest(syntax)) throw new Error("Mismatched inventory or syntax evidence");
  const jsEntries = inventory.entries.filter(entry => [".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"].includes(entry.suffix));
  if (jsEntries.length !== state.entries.length || jsEntries.some(entry =>
    !state.entries.some(input => input.path === entry.path && input.sha256 === entry.sha256 && input.bytes === entry.bytes) ||
    entry.language !== ([".ts", ".tsx"].includes(entry.suffix) ? "typescript" : "javascript") ||
    entry.parse_state !== "pending" || entry.parser !== null || entry.reason !== "")) {
    throw new Error("Candidate inventory differs from shared parser inputs/mode");
  }
  const operators = [
    ["===", "!==", "equality === -> !=="], ["!==", "===", "equality !== -> ==="],
    [">=", "<", "boundary >= -> <"], ["<=", ">", "boundary <= -> >"],
    ["!=", "==", "equality != -> =="], ["==", "!=", "equality == -> !="],
    ["&&", "||", "logic && -> ||"], ["||", "&&", "logic || -> &&"],
    [">", "<", "comparison > -> <"], ["<", ">", "comparison < -> >"],
    ["+", "-", "arithmetic + -> -"], ["-", "+", "arithmetic - -> +"],
    ["true", "false", "literal true -> false"], ["false", "true", "literal false -> true"],
  ];
  const eligible = [], noOperator = [], unsupported = [];
  for (const [name, changedLines] of Object.entries(inventory.changed_production)) {
    if (!inventory.entries.some(entry => entry.path === name && entry.role === "production")) {
      throw new Error("Changed-production path is not an inventoried production file");
    }
    const entry = jsEntries.find(item => item.path === name);
    if (!entry) continue;
    if (!Array.isArray(changedLines) || changedLines.some((line, index) =>
      !Number.isSafeInteger(line) || line < 1 || (index && line <= changedLines[index - 1]))) {
      throw new Error("Invalid changed-production line set");
    }
    const row = state.census.find(item => item.path === name);
    if (row.state !== "processed") {
      unsupported.push({ path: name, reason: row.reason });
      continue;
    }
    const file = state.program.getSourceFile("/subject/" + name), unit = state.sources.get(file.fileName);
    const edits = [];
    function add(node, after, operator, rank) {
      const start = node.getStart(file), end = node.end;
      if (end > start) edits.push({ span: unit.span(start, end), before: unit.slice(start, end), after, operator, rank });
    }
    function visit(node) {
      if (node.kind === ts.SyntaxKind.JSDoc || ts.isTypeNode(node) ||
          ts.isImportDeclaration(node) || ts.isImportEqualsDeclaration(node) ||
          ts.isExportDeclaration(node) || ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node) ||
          (ts.canHaveModifiers(node) && ts.getModifiers(node)?.some(item => item.kind === ts.SyntaxKind.DeclareKeyword))) return;
      if (ts.isBinaryExpression(node)) {
        const text = node.operatorToken.getText(file), rank = operators.findIndex(item => item[0] === text);
        if (rank >= 0) add(node.operatorToken, operators[rank][1], operators[rank][2], rank);
      } else if (node.kind === ts.SyntaxKind.TrueKeyword || node.kind === ts.SyntaxKind.FalseKeyword) {
        const rank = operators.findIndex(item => item[0] === node.getText(file));
        add(node, operators[rank][1], operators[rank][2], rank);
      }
      if (ts.isReturnStatement(node) || (ts.isExpressionStatement(node) && !ts.isStringLiteral(node.expression))) {
        add(node, ";", "statement deletion", operators.length);
      }
      ts.forEachChild(node, visit);
    }
    if (!file.isDeclarationFile) visit(file);
    edits.sort((a, b) => a.rank - b.rank || a.span.start_byte - b.span.start_byte || a.span.end_byte - b.span.end_byte);
    const original = Buffer.from(unit.text);
    for (const line of changedLines) {
      const edit = edits.find(item => item.span.start_line === line);
      if (!edit) {
        noOperator.push({ path: name, line });
        continue;
      }
      const replacement = Buffer.from(edit.after);
      const after = Buffer.concat([original.subarray(0, edit.span.start_byte), replacement, original.subarray(edit.span.end_byte)]);
      const identity = { path: name, span: edit.span, operator: edit.operator,
        before_sha256: unit.sha256, after_sha256: hash(after) };
      eligible.push({ id: digest(identity), path: name, language: entry.language, line, span: edit.span,
        operator: edit.operator, before_text: edit.before, after_text: edit.after,
        before_sha256: unit.sha256, after_sha256: identity.after_sha256 });
    }
  }
  state.verify();
  return { eligible: eligible.sort((a, b) => a.line - b.line || compare(a.path, b.path) ||
      a.span.start_byte - b.span.start_byte || a.span.end_byte - b.span.end_byte),
    no_operator: noOperator.sort((a, b) => a.line - b.line || compare(a.path, b.path)),
    unsupported_scope: unsupported.sort((a, b) => compare(a.path, b.path)) };
}

function selectedQualifications(config) {
  const refs = new Map();
  for (const binding of Object.values(config.tools)) {
    exactKeys(binding, ["executable", "module_path", "observed_version", "sha256",
      "qualified_api", "help", "configuration", "qualification"], "ToolBinding");
    if (!Array.isArray(binding.qualification) || !binding.qualification.length) {
      throw new Error("Missing tool qualification");
    }
    for (const ref of [binding.help, binding.configuration, ...binding.qualification]) {
      if (refs.has(ref.path) && digest(refs.get(ref.path)) !== digest(ref)) {
        throw new Error("Conflicting qualification artifact");
      }
      refs.set(ref.path, ref);
    }
  }
  return [...refs.values()].sort((a, b) => compare(a.path, b.path));
}

function commandCompiler(config, runRoot, refs, contextRoots) {
  const binding = config.tools.typescript;
  if (!binding) throw new Error("Qualified TypeScript binding required");
  const documents = new Map(refs.map(ref => [ref.sha256, pinnedBytes(runRoot, ref)]));
  function qualified(sha) {
    if (!binding.qualification.some(ref => ref.sha256 === sha) || !documents.has(sha)) {
      throw new Error("Missing original compiler qualification: " + sha);
    }
    return JSON.parse(decoder.decode(documents.get(sha)));
  }
  const originalRoots = qualified("7b096834fba95bef4984701376be69f72f37b2549777b5b2eb03715d1f141bde");
  const files = qualified("23c3bfa261c02c797d847c134c0131ccebae9ff704cb419d3b0d07c861b4a5af");
  const result = qualified("c162d0ce8e34c343442fdb646f40db4674c1fa51098e5af5302222986b5d2b86");
  const runtime = qualified("1f38647736643a54273217524f452724f4daf5437c7fa8cb8c6a78c4479ce91b");
  if (binding.help.sha256 !== "f2e3e3a9ad5608d2818b0356c935a3c45458958d2d70ec3ed715eefc3af5f256" ||
      binding.sha256 !== runtime.executors.node.sha256 || digest(result.options) !== digest(SETTINGS)) {
    throw new Error("Compiler qualification mismatch");
  }
  const rootsBytes = pinnedBytes(runRoot, binding.configuration);
  const roots = JSON.parse(decoder.decode(rootsBytes));
  exactKeys(roots, ["typescript", "lizard", "vulture", "pygments", "pathspec"], "qualified roots");
  absolute(roots.typescript);
  for (const root of contextRoots) {
    const name = path.relative(root, roots.typescript);
    const reverse = path.relative(roots.typescript, root);
    if ((!path.isAbsolute(name) && name.split(path.sep)[0] !== "..") ||
        (!path.isAbsolute(reverse) && reverse.split(path.sep)[0] !== "..")) {
      throw new Error("Compiler resources overlap Context");
    }
  }
  const resources = files.filter(ref => {
    const name = path.relative(originalRoots.typescript, ref.path);
    return name && !path.isAbsolute(name) && name.split(path.sep)[0] !== "..";
  }).map(ref => ({ ...ref, path: path.join(roots.typescript, path.relative(originalRoots.typescript, ref.path)) }));
  const source = { roots: { typescript: roots.typescript }, resources, runtime_imports: [], settings: SETTINGS };
  const compiler = openCompiler(binding, source);
  checkedJSON(compiler.ts, binding.configuration.path, decoder.decode(rootsBytes));
  return { compiler, source };
}

function produceRequest(requestPath) {
  absolute(requestPath);
  const requestBytes = readRegular(requestPath);
  const request = JSON.parse(decoder.decode(requestBytes));
  exactKeys(request, ["schema_version", "binding", "execution_id", "purpose", "context",
    "inventory", "config", "pre_manifest", "inputs", "outputs"], "JSRequestV1");
  if (request.schema_version !== 1 || !["produce", "validate"].includes(request.purpose) ||
      typeof request.execution_id !== "string" || !/^[0-9a-f]{32}$/u.test(request.execution_id)) {
    throw new Error("Invalid JS request version, purpose or execution ID");
  }
  const { context, inventory, config, binding } = request;
  exactKeys(config, ["schema_version", "semantic_profile", "tools", "python_source_roots",
    "js_entrypoints", "suites", "coverage_policy", "architecture_rules", "mutation_cap",
    "mutation_max_seconds", "approval_artifact", "tool_artifact_root"], "MeasurementConfig");
  exactKeys(context, ["schema_version", "run_id", "source", "base_root", "head_root",
    "controller_root", "run_root", "controller_sha256", "policy_sha256", "toolset_sha256",
    "contract_artifacts", "output_manifest"], "Context");
  exactKeys(inventory, ["schema_version", "revision", "source_sha256", "entries",
    "changed_production", "scope_exclusions", "enumeration_state", "enumeration_errors", "digest"], "Inventory");
  const { digest: inventoryDigest, ...inventoryBody } = inventory;
  if (context.schema_version !== 1 || inventory.schema_version !== 1 ||
      !["base", "head"].includes(inventory.revision) || digest(inventoryBody) !== inventoryDigest ||
      binding.run_id !== context.run_id || binding.revision !== inventory.revision ||
      binding.git_revision !== context.source[inventory.revision] ||
      binding.inventory_sha256 !== inventoryDigest || binding.source_sha256 !== inventory.source_sha256 ||
      binding.toolset_sha256 !== context.toolset_sha256 || binding.policy_sha256 !== context.policy_sha256) {
    throw new Error("Mismatched request/context/inventory binding");
  }
  const roots = ["base_root", "head_root", "controller_root", "run_root"].map(key => absolute(context[key]));
  for (const left of roots) {
    if (!fs.statSync(left).isDirectory()) throw new Error("Context root is not a directory");
    for (const right of roots) {
      if (left === right) continue;
      const name = path.relative(left, right);
      if (!path.isAbsolute(name) && name.split(path.sep)[0] !== "..") {
        throw new Error("Overlapping Context roots");
      }
    }
  }
  if (new Set(roots).size !== roots.length) throw new Error("Duplicate Context roots");
  const subjectRoot = context[inventory.revision + "_root"];
  const prefix = inventory.revision + "/js/";
  if (requestPath !== path.join(context.run_root, prefix, "request.json") ||
      fileURLToPath(import.meta.url) !== path.join(context.controller_root, "measure_js.mjs")) {
    throw new Error("Request/controller must use fixed locators");
  }
  exactKeys(request.outputs, ["result", "symbols"], "JS output");
  for (const name of ["result", "symbols"]) {
    if (request.outputs[name] !== prefix + name + ".json") throw new Error("Invalid fixed JS output path");
    try {
      fs.lstatSync(path.join(context.run_root, request.outputs[name]));
      throw new Error("Refusing to overwrite JS output: " + name);
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  if (request.pre_manifest.path !== "js-preflight.json" ||
      digest(request.pre_manifest) !== digest(context.output_manifest)) {
    throw new Error("Expected active JS preflight manifest");
  }
  const manifestBytes = pinnedBytes(context.run_root, request.pre_manifest);
  const manifest = JSON.parse(decoder.decode(manifestBytes));
  exactKeys(manifest, ["run_id", "root", "inputs", "reserved_outputs"], "preflight manifest");
  const qualifications = selectedQualifications(config);
  const expectedRows = qualifications.map(artifact => ({ artifact, role: "qualification", revision: null }));
  if (manifest.run_id !== context.run_id || manifest.root !== context.run_root ||
      digest(manifest.inputs) !== digest(expectedRows) || !Array.isArray(manifest.reserved_outputs)) {
    throw new Error("Invalid preflight ownership");
  }
  const reservations = manifest.reserved_outputs.map(relative);
  if (digest(reservations) !== digest([...reservations].sort(compare)) ||
      new Set(reservations.map(name => name.toLowerCase())).size !== reservations.length) {
    throw new Error("Noncanonical preflight reservations");
  }
  for (const name of reservations) {
    if (reservations.some(other => other !== name && other.toLowerCase().startsWith(name.toLowerCase() + "/"))) {
      throw new Error("Overlapping preflight reservations");
    }
  }
  for (const name of [...qualifications.map(ref => ref.path), "js-preflight.json", "js-produced.json",
    "manifest.json", ...["base", "head"].flatMap(side =>
      ["request", "command", "result", "symbols"].map(slot => `${side}/js/${slot}.json`))]) {
    if (!reservations.includes(name)) throw new Error("Unreserved JS artifact: " + name);
  }
  if (qualifications.some(ref => ["base", "head", "manifest.json", "js-preflight.json", "js-produced.json"]
    .includes(ref.path.split("/")[0].toLowerCase()))) throw new Error("Qualification overlaps generated output");

  const controllerNames = ["measure.py", "measure_graph.py", "probe.py", "evidence.py", "run.py", "measure_js.mjs"];
  const controllerFiles = controllerNames.map(name => {
    const bytes = readRegular(path.join(context.controller_root, name));
    return { path: name, sha256: hash(bytes), bytes: bytes.length };
  }).sort((a, b) => compare(a.path, b.path));
  if (digest(Object.fromEntries(controllerFiles.map(ref => [ref.path, ref.sha256]))) !== context.controller_sha256) {
    throw new Error("Controller bytes changed");
  }
  const { compiler, source } = commandCompiler(config, context.run_root, qualifications, roots);
  checkedJSON(compiler.ts, "request.json", decoder.decode(requestBytes));
  checkedJSON(compiler.ts, request.pre_manifest.path, decoder.decode(manifestBytes));
  const contracts = context.contract_artifacts.map(ref => ({
    input: { scope: "head-contract", ...ref }, bytes: pinnedBytes(context.head_root, ref),
  }));
  const configurations = contracts.filter(item => {
    try { return JSON.parse(decoder.decode(item.bytes))?.semantic_profile === "workflow-reliability-q-v1"; }
    catch (error) {
      if (!(error instanceof SyntaxError) && error.code !== "ERR_ENCODING_INVALID_ENCODED_DATA") throw error;
      return false; // Other bound contracts can be opaque approval documents.
    }
  });
  if (configurations.length !== 1 || digest(JSON.parse(decoder.decode(configurations[0].bytes))) !== digest(config)) {
    throw new Error("Request configuration differs from source contract");
  }
  const jsSuffixes = new Set([".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"]);
  const entries = inventory.entries.filter(entry => jsSuffixes.has(path.posix.extname(entry.path).toLowerCase()));
  for (const entry of entries) {
    const suffix = path.posix.extname(entry.path).toLowerCase();
    if (entry.suffix !== suffix || entry.parse_state !== "pending" ||
        entry.language !== ([".ts", ".tsx"].includes(suffix) ? "typescript" : "javascript")) {
      throw new Error("JS inventory classification mismatch");
    }
  }
  const metadataNames = new Set();
  for (const name of [...entries.map(entry => entry.path), ...config.js_entrypoints.map(entry => entry.path)]) {
    relative(name);
    for (let directory = path.posix.dirname(name); ; directory = path.posix.dirname(directory)) {
      metadataNames.add(directory === "." ? "package.json" : directory + "/package.json");
      if (directory === ".") break;
    }
  }
  const metadata = [], absentMetadata = [];
  for (const name of [...metadataNames].sort(compare)) {
    try {
      const bytes = readRegular(path.join(subjectRoot, name));
      metadata.push({ path: name, sha256: hash(bytes), bytes: bytes.length });
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
      absentMetadata.push(name);
    }
  }
  const resources = source.resources.map(ref => ({ ...ref,
    path: path.relative(source.roots.typescript, ref.path).split(path.sep).join("/") }));
  const expectedInputs = [
    ...[...entries, ...metadata].map(({ path, sha256, bytes }) => ({ scope: "subject", path, sha256, bytes })),
    ...contracts.map(item => item.input),
    ...resources.map(ref => ({ scope: "tool-resource", ...ref })),
  ].sort((a, b) => compare(a.scope + "/" + a.path, b.scope + "/" + b.path));
  if (new Set(expectedInputs.map(ref => ref.scope + "/" + ref.path)).size !== expectedInputs.length ||
      digest(request.inputs) !== digest(expectedInputs)) throw new Error("Incomplete or unexpected admitted JS inputs");
  const inputRoots = { subject: subjectRoot, "head-contract": context.head_root, "tool-resource": source.roots.typescript };
  function verify() {
    if (!readRegular(requestPath).equals(requestBytes)) throw new Error("Request changed during production");
    pinnedBytes(context.run_root, request.pre_manifest);
    for (const ref of qualifications) pinnedBytes(context.run_root, ref);
    for (const ref of controllerFiles) pinnedBytes(context.controller_root, ref);
    for (const { scope, ...ref } of expectedInputs) pinnedBytes(inputRoots[scope], ref);
    for (const name of absentMetadata) {
      try {
        fs.lstatSync(path.join(subjectRoot, name));
        throw new Error("Metadata appeared during production: " + name);
      } catch (error) {
        if (error.code !== "ENOENT") throw error;
      }
    }
    compiler.verify();
  }
  verify();
  const parsed = parseProgram(compiler, subjectRoot, entries, metadata);
  console.log("Completed JS source census: " + parsed.census.length);
  const records = serializeProgram(parsed, binding, configurations[0]);
  console.log("Completed JS syntax and symbol serialization");
  const provenance = {
    runtime: { executable: fs.realpathSync.native(process.execPath), version: process.version,
      architecture: process.arch, typescript_version: compiler.ts.version, exec_argv: [...process.execArgv] },
    adapter_sha256: hash(readRegular(fileURLToPath(import.meta.url))), controller_files: controllerFiles,
    loaded_modules: Object.keys(require.cache).map(name => {
      const ref = resources.find(item => path.join(source.roots.typescript, item.path) === name);
      if (!ref) throw new Error("Unqualified loaded module: " + name);
      return { scope: "tool-resource", ...ref };
    }).sort((a, b) => compare(a.path, b.path)),
    reads: expectedInputs,
  };
  verify();
  const symbolsBytes = Buffer.from(JSON.stringify(canonical(records.symbols)) + "\n");
  const symbols = { path: request.outputs.symbols, sha256: hash(symbolsBytes), bytes: symbolsBytes.length };
  const result = { schema_version: 1, binding, execution_id: request.execution_id,
    request: { path: prefix + "request.json", sha256: hash(requestBytes), bytes: requestBytes.length },
    state: "produced", symbols, provenance, syntax: records.syntax, reasons: [] };
  absolute(path.join(context.run_root, inventory.revision, "js"));
  fs.writeFileSync(path.join(context.run_root, symbols.path), symbolsBytes, { flag: "wx" });
  verify();
  const resultBytes = Buffer.from(JSON.stringify(canonical(result)) + "\n");
  fs.writeFileSync(path.join(context.run_root, request.outputs.result), resultBytes, { flag: "wx" });
  pinnedBytes(context.run_root, symbols);
  pinnedBytes(context.run_root, { path: request.outputs.result, sha256: hash(resultBytes), bytes: resultBytes.length });
  verify();
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 3) throw new Error("Expected one absolute JSRequestV1 path");
    produceRequest(process.argv[2]);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 2;
  }
}
