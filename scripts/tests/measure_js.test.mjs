import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import test from "node:test";

const input = JSON.parse(fs.readFileSync(process.env.Q2_JS_TEST_INPUT, "utf8"));
const { SourceBytes, openCompiler, parseProgram } = await import(pathToFileURL(input.controller).href);
const hash = value => crypto.createHash("sha256").update(value).digest("hex");
assert.equal(hash(fs.readFileSync(input.controller)), input.controller_sha256);
const compiler = openCompiler(input.binding, input.source);
const proofs = [];

function fixture(files) {
  const root = fs.mkdtempSync(path.join(input.scratch, "native-"));
  const entries = Object.entries(files).map(([name, text]) => {
    const file = path.join(root, ...name.split("/"));
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, text);
    const bytes = fs.readFileSync(file);
    return { path: name, sha256: hash(bytes), bytes: bytes.length };
  });
  return { root, entries };
}

function parse(files) {
  const { root, entries } = fixture(files);
  const code = entries.filter(entry => !entry.path.endsWith("package.json"));
  const metadata = entries.filter(entry => entry.path.endsWith("package.json"));
  const result = parseProgram(compiler, root, code, metadata);
  proofs.push({ entries, census: result.census, diagnostics: result.diagnostics, reads: result.reads });
  return result;
}

const cases = {
  byte_boundaries() {
    const text = "\ufeffconst café = '😀';\r\nlet x = 1;\r\n";
    const unit = new SourceBytes("unicode.ts", Buffer.from(text));
    assert.equal(unit.text, text);
    assert.equal(unit.sha256, hash(Buffer.from(text)));
    const emoji = text.indexOf("😀");
    const range = unit.range(emoji, 2);
    assert.equal(range.start_byte, Buffer.byteLength(text.slice(0, emoji)));
    assert.equal(range.end_byte - range.start_byte, 4);
    assert.equal(unit.slice(emoji, emoji + 2), "😀");
    assert.throws(() => unit.range(emoji + 1, 1), /boundary/);
    assert.throws(() => unit.range(emoji, 1), /boundary/);
    for (const args of [[-1, 1], [0, -1], [0, 999], [true, 1], [0, 0.5]]) {
      assert.throws(() => unit.range(...args), /boundary/);
    }
    assert.deepEqual(unit.range(text.length, 0), {
      start_byte: Buffer.byteLength(text), end_byte: Buffer.byteLength(text), start_line: 3, end_line: 3,
    });
    assert.equal(unit.range(text.indexOf("let"), 3).start_line, 2);
    assert.throws(() => unit.span(0, 0), /nonempty/);
    assert.throws(() => new SourceBytes("bad.js", Buffer.from([0xff])), /encoded data/);
    assert.throws(() => new SourceBytes("../bad.js", Buffer.from("")), /Noncanonical/);
    const original = Buffer.from("abc");
    const isolated = new SourceBytes("a.js", original);
    original.fill(0);
    assert.equal(isolated.slice(0, 3), "abc");
    assert.equal(new SourceBytes("empty.js", Buffer.alloc(0)).range(0, 0).start_byte, 0);
  },
  six_suffixes() {
    const files = { "package.json": '{"type":"module"}' };
    for (const suffix of [".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"]) {
      const group = suffix.slice(1) + "/";
      files[group + "empty" + suffix] = "";
      files[group + "comment" + suffix] = "/** only comment */\r\n// true === false\r\n";
      files[group + "functionless" + suffix] = "export const value = 4;\n";
      files[group + "broken" + suffix] = "function ( {\n";
      files[group + "encoding" + suffix] = Buffer.from([0xff]);
    }
    const result = parse(files);
    assert.equal(result.census.length, 30);
    for (const row of result.census) {
      if (row.path.includes("broken") || row.path.includes("encoding")) {
        assert.equal(row.state, "failed", row.path);
        assert.equal(row.function_count, null);
        assert.equal(row.token_count, null);
        assert.ok(row.reason);
      } else {
        assert.equal(row.state, "processed", row.path);
        assert.equal(row.function_count, 0);
        assert.equal(row.observed_sha256, row.source_sha256);
        if (!row.path.includes("functionless")) assert.equal(row.token_count, 0, row.path);
        else assert.ok(row.token_count > 0);
      }
    }
    assert.ok(result.diagnostics.some(item => item.code === 6053 && item.location.file === null));
    assert.ok(result.reads.some(item => item.scope === "tool-resource" && item.path.endsWith("lib.esnext.full.d.ts")));
  },
  syntax_shapes() {
    const text = "export const literal = `=== text ${1 + 2}`;\r\n" +
      "export const regex = /true===false/;\r\nexport const quotient = 8 / 2;\r\n" +
      "type Fn = (arg: true) => false;\r\nexport const arrow = (x: number) => x >= 1;\r\n" +
      "export function outer() { return () => true; }\r\n";
    const result = parse({ "shape.ts": text, "view.tsx": "export const view = () => <span>{1 + 2}</span>;",
      "documented.js": "/** @param {number} x true === false */\nexport const fn = x => x;",
      "plain.js": "export const fn = x => x;" });
    const row = result.census.find(item => item.path === "shape.ts");
    assert.equal(row.state, "processed");
    assert.equal(row.function_count, 3);
    assert.equal(result.census.find(item => item.path === "view.tsx").function_count, 1);
    assert.equal(result.census.find(item => item.path === "documented.js").token_count,
      result.census.find(item => item.path === "plain.js").token_count);
    const { ts } = compiler;
    const nodes = [];
    const source = result.program.getSourceFile("/subject/shape.ts");
    function visit(node) { nodes.push(node); ts.forEachChild(node, visit); }
    visit(source);
    assert.ok(nodes.some(node => node.kind === ts.SyntaxKind.RegularExpressionLiteral));
    assert.ok(nodes.some(node => ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.SlashToken));
    assert.ok(nodes.some(node => node.kind === ts.SyntaxKind.TemplateExpression));
    for (const node of nodes.filter(node => node.kind !== ts.SyntaxKind.SourceFile &&
      node.kind !== ts.SyntaxKind.EndOfFileToken && node.getWidth(source) > 0)) {
      const unit = result.sources.get("/subject/shape.ts");
      const span = unit.span(node.getStart(source), node.end);
      assert.equal(Buffer.from(text).subarray(span.start_byte, span.end_byte).toString("utf8"), node.getText(source));
    }
  },
  diagnostics_and_symbols() {
    const result = parse({
      "package.json": '{"type":"module"}',
      "origin.ts": "export const café: number = '😀';\r\nexport const extra: boolean = 3;\r\n",
      "alias.ts": "export { café as renamed } from './origin.js';\n",
      "use.ts": "import { renamed } from './alias.js'; export const used = renamed;\n",
      "missing.ts": "import { x } from './absent.js'; import { y } from 'uninstalled'; export {x,y};\n",
      "eof.ts": "export function unfinished() {\r\n",
    });
    assert.equal(result.diagnostics.filter(item => item.code === 2322).length, 2);
    assert.equal(result.diagnostics.filter(item => item.code === 2307).length, 2);
    for (const diagnostic of result.diagnostics.filter(item => item.location.file)) {
      const location = diagnostic.location;
      const unit = result.sources.get("/subject/" + location.file.path);
      if (unit) assert.deepEqual(location.byte_range, unit.range(location.utf16_start, location.utf16_length));
    }
    assert.ok(result.diagnostics.some(item => item.location.file?.path === "eof.ts" &&
      item.location.utf16_length === 0));
    const origin = result.program.getSourceFile("/subject/origin.ts");
    const alias = result.program.getSourceFile("/subject/alias.ts");
    const declared = result.checker.getExportsOfModule(result.checker.getSymbolAtLocation(origin))
      .find(symbol => symbol.name === "café");
    const renamed = result.checker.getExportsOfModule(result.checker.getSymbolAtLocation(alias))
      .find(symbol => symbol.name === "renamed");
    assert.equal(result.checker.getAliasedSymbol(renamed), declared);
    assert.equal(result.census.find(row => row.path === "origin.ts").state, "processed");
  },
  errors_and_empty_program() {
    const { root, entries } = fixture({ "gone.ts": "export const value = 1;\n" });
    fs.unlinkSync(path.join(root, "gone.ts"));
    const missing = parseProgram(compiler, root, entries);
    assert.equal(missing.census[0].state, "failed");
    assert.equal(missing.census[0].observed_sha256, null);
    assert.ok(missing.diagnostics.some(item => item.code === 6053 && item.location.file === null));
    const empty = parseProgram(compiler, root, []);
    assert.deepEqual(empty.census, []);
    assert.deepEqual(empty.diagnostics, []);
    assert.throws(() => parseProgram({}, root, []), /openCompiler/);
    const changed = fixture({ "changed.ts": "export const value = 1;\n" });
    fs.appendFileSync(path.join(changed.root, "changed.ts"), "// changed\n");
    assert.throws(() => parseProgram(compiler, changed.root, changed.entries), /Source changed/);
    assert.throws(() => parseProgram(compiler, root, [{ ...entries[0], path: "../escape.ts" }]), /Noncanonical/);
    assert.throws(() => parseProgram(compiler, root, [entries[0], entries[0]]), /Duplicate/);
    assert.throws(() => parseProgram(compiler, root, [{ ...entries[0], path: "bad.py" }]), /Unsupported reader/);
    const metadata = fixture({ "package.json": Buffer.from([0xff]) });
    assert.throws(() => parseProgram(compiler, metadata.root, [], metadata.entries), /metadata/);
    const missingModule = structuredClone(input.source);
    missingModule.resources = missingModule.resources.filter(pin => pin.path !== input.binding.module_path);
    assert.throws(() => openCompiler(input.binding, missingModule), /Unqualified compiler resource/);
    const changedSettings = structuredClone(input.source);
    changedSettings.settings.skipLibCheck = true;
    assert.throws(() => openCompiler(input.binding, changedSettings), /settings/);
    proofs.push({ missing: missing.census, diagnostics: missing.diagnostics, empty: empty.census });
  },
  actual_root_syntax() {
    const result = parseProgram(compiler, input.root_sources.root, input.root_sources.entries);
    assert.equal(result.census.length, 2);
    assert.ok(result.census.every(row => row.state === "processed" && row.token_count > 0));
    proofs.push({ entries: input.root_sources.entries, census: result.census,
      diagnostics: result.diagnostics, reads: result.reads });
    const sentinel = path.join(input.scratch, "source-executed");
    const noExecute = parse({ "side-effect.cjs":
      "require('node:fs').writeFileSync(" + JSON.stringify(sentinel) + ", 'wrong');\n" });
    assert.equal(noExecute.census[0].state, "processed");
    assert.equal(fs.existsSync(sentinel), false);
  },
  two_revisions() {
    assert.notEqual(input.revisions[0].git, input.revisions[1].git);
    const results = input.revisions.map(revision => {
      const result = parseProgram(compiler, revision.root, revision.entries, revision.metadata);
      proofs.push({ revision: revision.name, git: revision.git, entries: revision.entries,
        metadata: revision.metadata, census: result.census, diagnostics: result.diagnostics, reads: result.reads });
      return result;
    });
    assert.deepEqual(results[0].census.map(row => row.path), ["base-only.js", "shared.ts", "view.jsx"]);
    assert.deepEqual(results[1].census.map(row => row.path), ["shared.ts", "view.jsx"]);
    assert.ok(results.every(result => result.census.every(row => row.state === "processed")));
    assert.equal(results[0].diagnostics.filter(item => item.code === 2322).length, 0);
    assert.equal(results[1].diagnostics.filter(item => item.code === 2322).length, 1);
    assert.notEqual(results[0].census.find(row => row.path === "shared.ts").source_sha256,
      results[1].census.find(row => row.path === "shared.ts").source_sha256);
  },
};

const selected = process.env.Q2_JS_TEST_CASE;
if (selected && !Object.hasOwn(cases, selected)) throw new Error("Unknown native test case");
for (const [name, body] of Object.entries(cases)) {
  if (selected && selected !== name) continue;
  test(name, () => {
    body();
    compiler.verify();
    assert.equal(hash(fs.readFileSync(input.controller)), input.controller_sha256);
    fs.writeFileSync(input.result, JSON.stringify({ case: name, proofs,
      runtime: { version: process.version, architecture: process.arch },
      controller_sha256: input.controller_sha256 }, null, 2));
  });
}
