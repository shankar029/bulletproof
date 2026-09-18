import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import test from "node:test";

const input = JSON.parse(fs.readFileSync(process.env.Q2_JS_TEST_INPUT, "utf8"));
const { SourceBytes, openCompiler, parseProgram, parserDigest, settingsDigest,
  serializeProgram, candidatesForProgram } = await import(pathToFileURL(input.controller).href);
const hash = value => crypto.createHash("sha256").update(value).digest("hex");
const canonical = value => Array.isArray(value) ? value.map(canonical) :
  value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])])) : value;
const digest = value => hash(JSON.stringify(canonical(value)) + "\n");
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

function serialize(revision) {
  const result = parseProgram(compiler, revision.root, revision.entries, revision.metadata);
  const config = { input: input.semantic.config_input,
    bytes: fs.readFileSync(path.join(input.semantic.config_root, input.semantic.config_input.path)) };
  const value = JSON.parse(config.bytes);
  const binding = { semantic_version: "typescript-shared-v1", run_id: input.semantic.run_id,
    revision: revision.name, git_revision: revision.git, inventory_sha256: revision.inventory.digest,
    source_sha256: revision.inventory.source_sha256, parser_sha256: parserDigest(compiler),
    settings_sha256: settingsDigest(value.js_entrypoints), policy_sha256: input.semantic.policy_sha256,
    toolset_sha256: input.semantic.toolset_sha256 };
  const records = serializeProgram(result, binding, config);
  proofs.push({ revision: revision.name, git: revision.git, binding,
    records_sha256: digest(records), census: records.symbols.files,
    symbols: records.symbols.symbols.map(item => ({ id: item.id, name: item.name })),
    counts: Object.fromEntries(["exports", "aliases", "references", "module_references", "outside_model", "diagnostics"]
      .map(key => [key, records.symbols[key].length])) });
  return { result, config, binding, ...records };
}

function checkRanges(revision, records) {
  const bytes = new Map(revision.entries.map(entry => [entry.path, fs.readFileSync(path.join(revision.root, entry.path))]));
  for (const item of [...records.symbols.references, ...records.symbols.aliases, ...records.symbols.exports,
    ...records.symbols.module_references, ...records.symbols.symbols.flatMap(symbol => symbol.declarations)]) {
    const data = bytes.get(item.path);
    assert.ok(data && item.span.start_byte >= 0 && item.span.end_byte <= data.length);
    assert.ok(item.span.end_byte > item.span.start_byte);
    const text = data.subarray(item.span.start_byte, item.span.end_byte);
    assert.equal(Buffer.from(new TextDecoder("utf-8", { fatal: true }).decode(text)).equals(text), true);
    if (item.source_sha256) assert.equal(item.source_sha256, hash(data));
  }
  const local = new Set(records.symbols.symbols.map(symbol => symbol.id));
  for (const item of [...records.symbols.references, ...records.symbols.aliases, ...records.symbols.exports]) {
    if (item.target.state === "local") {
      assert.ok(item.target.symbol_ids.length > 0);
      assert.ok(item.target.symbol_ids.every(id => local.has(id)));
      assert.equal(item.target.external, null);
    } else {
      assert.deepEqual(item.target.symbol_ids, []);
      if (item.target.state === "external") assert.ok(item.target.external);
      else assert.ok(item.target.reason);
    }
  }
}

const cases = {
  review_corrections() {
    const revision = input.revisions[1], records = serialize(revision);
    checkRanges(revision, records);
    const source = fs.readFileSync(path.join(revision.root, "selections.ts"));
    const text = item => source.subarray(item.span.start_byte, item.span.end_byte).toString("utf8");
    const expected = records.symbols.exports.find(item => item.path === "origin.ts" && item.name === "café").target;
    const reads = records.symbols.references.filter(item => item.path === "selections.ts" && item.kind === "property");
    const known = reads.filter(item => ["café", '"café"', '["café"]'].includes(text(item)));
    assert.equal(known.length, 4);
    for (const item of known) assert.deepEqual(item.target, expected);
    for (const [selection, state] of [["[key]", "dynamic"], ["rest", "dynamic"], ["unresolved", "unresolved"]]) {
      const matches = reads.filter(item => text(item) === selection);
      assert.equal(matches.length, 1);
      assert.equal(matches[0].target.state, state);
      assert.deepEqual(matches[0].target.symbol_ids, []);
      assert.ok(matches[0].target.reason);
      assert.ok(records.symbols.outside_model.some(item => item.path === "selections.ts" &&
        item.kind === "reflection" && digest(item.span) === digest(matches[0].span)));
      assert.ok(records.syntax.find(item => item.path === "selections.ts").outside_model.some(item =>
        digest(item.span) === digest(matches[0].span)));
    }
    for (const name of ["café", "quoted", "renamed", "literal"]) {
      const local = records.symbols.exports.find(item => item.path === "selections.ts" && item.name === name);
      assert.equal(local.target.state, "local");
      assert.notDeepEqual(local.target.symbol_ids, expected.symbol_ids);
    }
    const imports = records.symbols.module_references.filter(item => item.path === "selections.ts" &&
      text(item).startsWith("import("));
    assert.equal(imports.length, 3);
    for (const item of imports.slice(0, 2)) {
      assert.equal(item.specifier, "./origin.js");
      assert.equal(item.resolution, "local");
      assert.deepEqual(item.targets, ["origin.ts"]);
      assert.ok(records.syntax.find(entry => entry.path === "selections.ts").literal_imports.some(entry =>
        digest(entry.span) === digest(item.span) && entry.specifier === item.specifier));
      assert.equal(records.symbols.outside_model.some(entry => entry.path === item.path &&
        entry.kind === "computed-import" && digest(entry.span) === digest(item.span)), false);
    }
    assert.equal(imports[2].resolution, "dynamic");
    assert.equal(imports[2].specifier, null);
    const requires = records.symbols.module_references.filter(item => item.path === "require-arity.cjs");
    assert.equal(requires.length, 2);
    assert.ok(requires.every(item => item.kind === "require"));
    assert.equal(requires[0].resolution, "local");
    assert.deepEqual(requires[0].targets, ["consumer.mjs"]);
    assert.equal(requires[1].resolution, "dynamic");
    assert.equal(requires[1].specifier, null);
    proofs.push({ property_reads: reads, dynamic_imports: imports, require_controls: requires });
  },
  serialized_records() {
    const revision = input.revisions[1], records = serialize(revision), { symbols, syntax } = records;
    assert.deepEqual(Object.keys(symbols).sort(), ["schema_version", "binding", "inputs", "files", "symbols",
      "exports", "aliases", "references", "module_references", "entrypoints", "outside_model", "directives", "diagnostics"].sort());
    assert.deepEqual(symbols.files.map(item => item.path), revision.entries.map(item => item.path));
    assert.deepEqual(syntax.map(item => item.path),
      symbols.files.filter(item => item.state === "processed").map(item => item.path));
    for (const item of syntax) {
      assert.deepEqual(Object.keys(item).sort(), ["schema_version", "revision", "inventory_sha256", "path",
        "source_sha256", "parser_sha256", "semantic_version", "nodes", "literal_imports", "outside_model", "diagnostics"].sort());
      assert.ok(item.nodes.every(node => !["SourceFile", "EndOfFileToken"].includes(node.kind)));
      for (const imported of item.literal_imports) {
        assert.equal(symbols.module_references.filter(edge => edge.path === item.path &&
          edge.specifier === imported.specifier && edge.kind === imported.kind &&
          JSON.stringify(edge.span) === JSON.stringify(imported.span)).length, 1);
      }
    }
    checkRanges(revision, records);
    const declared = symbols.exports.find(item => item.path === "origin.ts" && item.name === "café");
    const renamed = symbols.exports.find(item => item.path === "barrel.ts" && item.name === "renamed");
    assert.equal(declared.target.state, "local");
    assert.deepEqual(renamed.target, declared.target);
    assert.ok(symbols.aliases.some(item => item.name === "value" &&
      item.target.symbol_ids[0] === declared.target.symbol_ids[0]));
    assert.ok(symbols.references.some(item => item.kind === "shorthand" &&
      item.target.symbol_ids[0] === declared.target.symbol_ids[0]));
    assert.ok(symbols.references.some(item => item.kind === "namespace-element" &&
      item.target.symbol_ids[0] === declared.target.symbol_ids[0]));
    assert.ok(symbols.references.some(item => item.kind === "namespace-element" && item.target.state === "dynamic"));
    assert.ok(symbols.module_references.some(item => item.path === "barrel.ts" && item.targets.includes("cycle.ts")));
    assert.ok(symbols.module_references.some(item => item.path === "cycle.ts" && item.targets.includes("barrel.ts")));
    assert.ok(symbols.module_references.some(item => item.specifier === "./absent.js" &&
      item.kind === "type-import" && item.resolution === "unresolved"));
    assert.ok(symbols.module_references.some(item => item.specifier === "node:child_process" && item.resolution === "external"));
    assert.equal(symbols.module_references.some(item => item.specifier === "./not-an-import.js"), false);
    assert.ok(symbols.module_references.some(item => item.path === "calls.cjs" && item.resolution === "dynamic"));
    assert.ok(symbols.outside_model.some(item => item.kind === "runtime-command"));
    assert.equal(symbols.outside_model.filter(item => item.path === "runtime.mjs" && item.kind === "runtime-command").length, 1);
    assert.equal(symbols.outside_model.some(item => item.path === "runtime.mjs" && item.kind === "reflection"), false);
    assert.ok(symbols.exports.some(item => item.path === "calls.cjs" && item.name === "local" && item.kind === "commonjs"));
    assert.ok(symbols.outside_model.some(item => item.path === "package.json" && item.reason.includes("/exports/")));
    const root = symbols.entrypoints.find(item => item.path === "origin.ts");
    assert.deepEqual(root.public_exports, ["café", "extra", "identity"]);
    assert.ok(root.origins.some(origin => origin.kind === "package" && origin.pointer === "/exports/."));
    assert.ok(root.origins.some(origin => origin.kind === "config" && origin.origin_ref === "fixture-explicit"));
    assert.ok(symbols.entrypoints.some(item => item.path === "case.test.mjs" &&
      item.origins.some(origin => origin.kind === "suite")));
    for (const origin of symbols.entrypoints.flatMap(item => item.origins)) {
      const root = origin.input.scope === "head-contract" ? input.semantic.config_root : revision.root;
      const content = fs.readFileSync(path.join(root, origin.input.path));
      assert.equal(hash(content), origin.input.sha256);
      let value = JSON.parse(content);
      for (const part of origin.pointer.slice(1).split("/")) value = value[part.replaceAll("~1", "/").replaceAll("~0", "~")];
      assert.notEqual(value, undefined);
    }
    assert.deepEqual(symbols.directives.map(item => item.kind), ["ts-check", "ts-nocheck", "ts-expect-error", "ts-ignore"]);
    assert.equal(symbols.files.find(item => item.path === "empty.js").token_count, 0);
    assert.deepEqual(syntax.find(item => item.path === "empty.js").nodes, []);
    assert.equal(symbols.files.find(item => item.path === "invalid.ts").state, "failed");
    assert.equal(symbols.files.find(item => item.path === "bad-utf8.js").state, "failed");
    assert.deepEqual(symbols.diagnostics, records.result.diagnostics);
    for (const key of ["exports", "aliases", "references", "module_references", "outside_model", "directives"]) {
      assert.equal(new Set(symbols[key].map(digest)).size, symbols[key].length, key);
    }
    for (const item of symbols.symbols) {
      const descriptors = item.declarations.map(({ source_sha256, span, ...descriptor }) => descriptor);
      descriptors.sort((a, b) => Buffer.compare(Buffer.from(JSON.stringify(canonical(a))), Buffer.from(JSON.stringify(canonical(b)))));
      assert.equal(item.id, digest(["js-symbol-v1", descriptors]));
    }
  },
  candidate_records() {
    const revision = input.revisions[1], records = serialize(revision);
    console.log("Completed candidate source serialization");
    const population = candidatesForProgram(records.result, revision.inventory, records.syntax);
    console.log("Completed candidate population generation");
    const shape = population.eligible.filter(item => item.path === "shapes.ts");
    assert.ok(shape.some(item => item.line === 5 && item.before_text === "+" && item.after_text === "-"));
    assert.ok(shape.some(item => item.line === 6 && item.before_text === ">="));
    assert.ok(shape.some(item => item.line === 7 && item.before_text === "==="));
    assert.ok(shape.some(item => item.line === 11 && item.before_text === "return 7;" && item.after_text === ";"));
    assert.ok(shape.some(item => item.line === 13 && item.before_text === "console.log('😀');"));
    assert.ok(shape.some(item => item.line === 14 && item.before_text === "true"));
    for (const line of [1, 2, 3, 4, 8, 9, 15, 16]) assert.equal(shape.some(item => item.line === line), false, String(line));
    assert.ok(population.eligible.some(item => item.path === "widget.jsx" && item.before_text === "+"));
    assert.ok(population.eligible.some(item => item.path === "view.tsx" && item.before_text === ">="));
    assert.equal(population.eligible.some(item => item.path === "types.d.ts"), false);
    assert.ok(records.syntax.find(item => item.path === "types.d.ts").nodes.length > 0);
    assert.deepEqual(population.unsupported_scope.map(item => item.path), ["bad-utf8.js", "invalid.ts"]);
    assert.ok(population.no_operator.some(item => item.path === "shapes.ts" && item.line === 2));
    for (const candidate of population.eligible) {
      assert.deepEqual(Object.keys(candidate).sort(), ["id", "path", "language", "line", "span", "operator",
        "before_text", "after_text", "before_sha256", "after_sha256"].sort());
      const original = fs.readFileSync(path.join(revision.root, candidate.path));
      assert.equal(hash(original), candidate.before_sha256);
      assert.equal(original.subarray(candidate.span.start_byte, candidate.span.end_byte).toString("utf8"), candidate.before_text);
      const edited = Buffer.concat([original.subarray(0, candidate.span.start_byte), Buffer.from(candidate.after_text),
        original.subarray(candidate.span.end_byte)]);
      assert.equal(hash(edited), candidate.after_sha256);
      assert.deepEqual(edited.subarray(0, candidate.span.start_byte), original.subarray(0, candidate.span.start_byte));
      assert.deepEqual(edited.subarray(candidate.span.start_byte + Buffer.byteLength(candidate.after_text)),
        original.subarray(candidate.span.end_byte));
      assert.equal(candidate.id, digest({ path: candidate.path, span: candidate.span, operator: candidate.operator,
        before_sha256: candidate.before_sha256, after_sha256: candidate.after_sha256 }));
      if (candidate.path === "shapes.ts" && [7, 11, 13].includes(candidate.line)) {
        const copy = fixture({ "shapes.ts": edited });
        const parsed = parseProgram(compiler, copy.root, copy.entries);
        assert.equal(parsed.census[0].state, "processed");
        console.log(`Completed candidate syntax assertion: ${candidate.path}:${candidate.line} ${candidate.operator}`);
      }
    }
    console.log("Completed candidate byte and syntax assertions");
    proofs.push({ population });
    const forged = structuredClone(records.syntax);
    forged[0].nodes.push({ kind: "Fake", span: { start_byte: 0, end_byte: 1, start_line: 1, end_line: 1 } });
    assert.throws(() => candidatesForProgram(records.result, revision.inventory, forged), /Mismatched/);
    console.log("Completed candidate forged-syntax rejection");
    const legacy = input.semantic.legacy_inventory;
    const wrong = { ...records.binding, inventory_sha256: legacy.digest };
    const wrongMode = serializeProgram(records.result, wrong, records.config);
    assert.throws(() => candidatesForProgram(records.result, legacy, wrongMode.syntax), /inputs\/mode/);
    console.log("Completed candidate legacy-inventory rejection");
    const unknown = structuredClone(revision.inventory);
    unknown.changed_production["ghost.js"] = [1];
    delete unknown.digest;
    unknown.digest = digest(unknown);
    const unknownSyntax = serializeProgram(records.result, { ...records.binding, inventory_sha256: unknown.digest }, records.config);
    assert.throws(() => candidatesForProgram(records.result, unknown, unknownSyntax.syntax), /not an inventoried/);
    console.log("Completed candidate unknown-source rejection");
  },
  serialized_freshness() {
    const base = serialize(input.revisions[0]);
    console.log("Completed base syntax/symbol serialization");
    const head = serialize(input.revisions[1]);
    console.log("Completed head syntax/symbol serialization");
    for (const name of ["café", "identity"]) {
      const left = base.symbols.exports.find(item => item.path === "origin.ts" && item.name === name);
      const right = head.symbols.exports.find(item => item.path === "origin.ts" && item.name === name);
      assert.deepEqual(left.target.symbol_ids, right.target.symbol_ids);
      assert.notDeepEqual(left.span, right.span);
    }
    assert.equal(base.symbols.entrypoints.find(item => item.path === "head-only.ts").state, "absent-at-revision");
    assert.equal(head.symbols.entrypoints.find(item => item.path === "head-only.ts").state, "active");
    assert.ok(base.symbols.files.some(item => item.path === "base-only.cjs"));
    assert.equal(head.symbols.files.some(item => item.path === "base-only.cjs"), false);
    const expected = digest({ syntax: head.syntax, symbols: head.symbols });
    head.result.census.length = 0;
    head.result.diagnostics.length = 0;
    assert.equal(digest(serializeProgram(head.result, head.binding, head.config)), expected);
    const badBinding = { ...head.binding, parser_sha256: hash("foreign parser") };
    assert.throws(() => serializeProgram(head.result, badBinding, head.config), /binding/);
    assert.throws(() => serializeProgram(head.result, head.binding, {
      ...head.config, bytes: Buffer.concat([head.config.bytes, Buffer.from(" ")]) }), /configuration bytes/);
    const modified = JSON.parse(head.config.bytes);
    modified.js_entrypoints[0].public_exports = ["notAnExport"];
    const bytes = Buffer.from(JSON.stringify(modified));
    const config = { input: { ...head.config.input, sha256: hash(bytes), bytes: bytes.length }, bytes };
    assert.throws(() => serializeProgram(head.result, { ...head.binding,
      settings_sha256: settingsDigest(modified.js_entrypoints) }, config), /public exports/);
    const file = path.join(input.revisions[1].root, "origin.ts");
    fs.appendFileSync(file, "// actual stale input\n");
    assert.throws(() => serializeProgram(head.result, head.binding, head.config), /Source changed/);
    assert.throws(() => candidatesForProgram(head.result, input.revisions[1].inventory, head.syntax), /Source changed/);
  },
  async parser_copy_binding() {
    const controllerCopy = path.join(input.scratch, "independent-controller.mjs");
    fs.copyFileSync(input.controller, controllerCopy);
    const independent = await import(pathToFileURL(controllerCopy).href);
    const otherCompiler = independent.openCompiler(input.binding, input.source);
    console.log("Opened byte-identical independently located controller");
    assert.equal(independent.parserDigest(otherCompiler), parserDigest(compiler));
    fs.appendFileSync(controllerCopy, "\n// actual controller change\n");
    assert.throws(() => independent.parserDigest(otherCompiler), /controller changed/);
    proofs.push({ copied_controller_parser_digest: parserDigest(compiler), changed_copy_rejected: true });
  },
  actual_source_candidates() {
    const revision = input.revisions[1], records = serialize(revision);
    const population = candidatesForProgram(records.result, revision.inventory, records.syntax);
    for (const name of ["evals/lib/score.mjs", "scripts/native_result.mjs"]) {
      assert.equal(records.symbols.files.find(item => item.path === name).state, "processed");
      const candidates = population.eligible.filter(item => item.path === name);
      assert.ok(candidates.length > 0, name);
      const bytes = fs.readFileSync(path.join(revision.root, name));
      assert.ok(candidates.every(item => item.before_sha256 === hash(bytes)));
      proofs.push({ path: name, sha256: hash(bytes), candidates: candidates.length,
        population_sha256: digest(candidates) });
    }
  },
  serialized_empty() {
    const records = serialize(input.revisions[1]);
    assert.deepEqual(records.syntax, []);
    for (const key of ["files", "symbols", "exports", "aliases", "references", "module_references",
      "entrypoints", "outside_model", "directives", "diagnostics"]) assert.deepEqual(records.symbols[key], [], key);
    assert.deepEqual(candidatesForProgram(records.result, input.revisions[1].inventory, records.syntax),
      { eligible: [], no_operator: [], unsupported_scope: [] });
  },
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
  test(name, async () => {
    await body();
    compiler.verify();
    assert.equal(hash(fs.readFileSync(input.controller)), input.controller_sha256);
    fs.writeFileSync(input.result, JSON.stringify({ case: name, proofs,
      runtime: { version: process.version, architecture: process.arch },
      controller_sha256: input.controller_sha256 }, null, 2));
  });
}
