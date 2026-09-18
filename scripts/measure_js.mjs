/**
 * Native shared-parser core. This module does not publish measurement artifacts
 * or implement the JSRequestV1 command; accepting execution belongs to measure.
 */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const compilers = new WeakMap();
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
  function verify() {
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
  compilers.set(handle, { ts, read, verify, resourceNames: Object.freeze([...pins.keys()].sort(compare)) });
  return handle;
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
  return { program, checker, census, diagnostics,
    sources: new Map([...sources].filter(([name]) => name.startsWith("/subject/"))),
    reads: [...reads.values()].sort((a, b) => compare(a.scope + "/" + a.path, b.scope + "/" + b.path)) };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  throw new Error("measure_js is a native parser library; no measurement command is exposed");
}
