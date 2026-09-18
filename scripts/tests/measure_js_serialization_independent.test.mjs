import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

const input = JSON.parse(fs.readFileSync(process.env.Q2_JS_TEST_INPUT, "utf8"));
const hash = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
assert.equal(hash(fs.readFileSync(input.controller)), input.controller_sha256);
const { openCompiler, parseProgram, parserDigest, settingsDigest, serializeProgram } =
  await import(pathToFileURL(input.controller).href);

const selected = process.env.Q2_JS_TEST_CASE;
if (selected && !["review_r1", "review_r2"].includes(selected)) throw new Error("Unknown independent test case");

if (!selected) test("merged declarations, import-equals and namespace reexports share checker-backed identities", () => {
  const compiler = openCompiler(input.binding, input.source);
  const parsed = parseProgram(compiler, input.root, input.entries, input.metadata);
  const { ts } = compiler, { checker, program } = parsed;
  const configBytes = fs.readFileSync(path.join(input.root, input.config_input.path));
  const binding = { ...input.semantic, parser_sha256: parserDigest(compiler),
    settings_sha256: settingsDigest(JSON.parse(configBytes).js_entrypoints) };
  const records = serializeProgram(parsed, binding, { input: input.config_input, bytes: configBytes });
  // Save the actual serialized evidence even if a discriminating assertion fails.
  fs.writeFileSync(input.result, JSON.stringify({ records }, null, 2));
  assert.deepEqual(parsed.diagnostics, [], "Fixture must be semantically valid, not merely parseable");
  assert.deepEqual(records.symbols.files.map(row => [row.path, row.state]),
    [["barrel.ts", "processed"], ["consumer.ts", "processed"], ["origin.ts", "processed"]]);
  const origin = program.getSourceFile("/subject/origin.ts");
  const originModule = checker.getSymbolAtLocation(origin);
  const originExports = checker.getExportsOfModule(originModule);
  const symbols = records.symbols;
  const byId = new Map(symbols.symbols.map(symbol => [symbol.id, symbol]));

  function local(target) {
    assert.deepEqual(Object.keys(target).sort(), ["external", "reason", "state", "symbol_ids"]);
    assert.equal(target.state, "local");
    assert.equal(target.external, null);
    assert.equal(target.reason, "");
    assert.equal(target.symbol_ids.length, 1);
    const symbol = byId.get(target.symbol_ids[0]);
    assert.ok(symbol, "Local resolution must reference a serialized symbol");
    return symbol;
  }

  function unique(rows, predicate, label) {
    const found = rows.filter(predicate);
    assert.equal(found.length, 1, label);
    return found[0];
  }

  function actualText(site) {
    const bytes = fs.readFileSync(path.join(input.root, site.path));
    assert.ok(site.span.start_byte >= 0 && site.span.end_byte > site.span.start_byte);
    assert.ok(site.span.end_byte <= bytes.length);
    if (site.source_sha256) assert.equal(site.source_sha256, hash(bytes));
    return bytes.subarray(site.span.start_byte, site.span.end_byte).toString("utf8");
  }

  const merged = new Map();
  for (const [name, kinds] of [["Parcel", ["ClassDeclaration", "ModuleDeclaration"]],
    ["Box", ["InterfaceDeclaration", "InterfaceDeclaration"]]]) {
    const exported = unique(symbols.exports, item => item.path === "origin.ts" && item.name === name, name);
    const symbol = local(exported.target), actual = originExports.find(item => item.name === name);
    assert.ok(actual);
    assert.equal(symbol.flags, actual.flags);
    assert.equal(symbol.name, name);
    assert.equal(symbols.symbols.filter(item => item.name === name &&
      item.declarations.every(declaration => declaration.path === "origin.ts")).length, 1);
    assert.deepEqual(symbol.declarations.map(item => item.kind), kinds);
    const declarations = actual.getDeclarations();
    assert.equal(declarations.length, 2);
    symbol.declarations.forEach((declaration, index) => {
      assert.equal(declaration.path, "origin.ts");
      assert.equal(actualText(declaration), declarations[index].getText(origin));
      assert.deepEqual(declaration.lexical_scope, []);
    });

    assert.equal(exported.type_only, name === "Box");
    merged.set(name, symbol);
  }

  const moduleAlias = unique(symbols.aliases, item => item.path === "consumer.ts" && item.name === "model", "model alias");
  assert.equal(moduleAlias.kind, "import-equals");
  const moduleRecord = local(moduleAlias.target);
  assert.equal(moduleRecord.flags, originModule.flags);
  assert.deepEqual(moduleRecord.declarations.map(item => [item.path, item.kind]), [["origin.ts", "SourceFile"]]);
  const itemAlias = unique(symbols.aliases, item => item.path === "consumer.ts" && item.name === "Item", "Item alias");
  assert.equal(itemAlias.kind, "import-equals");
  assert.equal(local(itemAlias.target).id, merged.get("Parcel").id);
  const consumer = program.getSourceFile("/subject/consumer.ts");
  for (const declaration of consumer.statements.filter(ts.isImportEqualsDeclaration)) {
    const resolved = checker.getAliasedSymbol(checker.getSymbolAtLocation(declaration.name));
    assert.equal(resolved, declaration.name.text === "model" ? originModule :
      originExports.find(item => item.name === "Parcel"));
  }
  const requireEdge = unique(symbols.module_references,
    item => item.path === "consumer.ts" && item.kind === "require", "import-equals module edge");
  assert.equal(requireEdge.specifier, "./origin.js");
  assert.equal(requireEdge.resolution, "local");
  assert.deepEqual(requireEdge.targets, ["origin.ts"]);

  const namespace = unique(symbols.exports, item => item.path === "barrel.ts" && item.name === "bundle", "namespace export");
  assert.equal(namespace.kind, "reexport");
  assert.equal(namespace.type_only, false);
  assert.equal(actualText(namespace), "* as bundle");
  assert.equal(local(namespace.target).id, moduleRecord.id);
  const namespaceAlias = unique(symbols.aliases, item => item.path === "barrel.ts" && item.name === "bundle", "namespace alias");
  assert.equal(namespaceAlias.kind, "reexport");
  assert.deepEqual(namespaceAlias.target, namespace.target);
  const importedBundle = unique(symbols.aliases,
    item => item.path === "consumer.ts" && item.name === "bundle", "imported bundle");
  assert.deepEqual(importedBundle.target, namespace.target);
  const barrel = program.getSourceFile("/subject/barrel.ts");
  const bundle = checker.getExportsOfModule(checker.getSymbolAtLocation(barrel)).find(item => item.name === "bundle");
  assert.equal(checker.getAliasedSymbol(bundle), originModule);
  const reexportEdge = unique(symbols.module_references,
    item => item.path === "barrel.ts" && item.kind === "reexport", "namespace module edge");
  assert.equal(reexportEdge.specifier, "./origin.js");
  assert.equal(reexportEdge.resolution, "local");
  assert.deepEqual(reexportEdge.targets, ["origin.ts"]);

  const itemUse = unique(symbols.references, item => item.path === "consumer.ts" &&
    item.kind === "identifier" && actualText(item) === "Item", "constructor alias reference");
  assert.equal(local(itemUse.target).id, merged.get("Parcel").id);
  const boxUse = unique(symbols.references, item => item.path === "consumer.ts" &&
    actualText(item) === "Box", "merged interface type reference");
  assert.equal(local(boxUse.target).id, merged.get("Box").id);
  const parcelUses = symbols.references.filter(item => item.path === "consumer.ts" &&
    item.kind === "property" && actualText(item) === "Parcel");
  assert.equal(parcelUses.length, 2, "model.Parcel and bundle.Parcel property uses");
  assert.ok(parcelUses.every(item => local(item.target).id === merged.get("Parcel").id));
  for (const edge of [requireEdge, reexportEdge]) {
    const syntax = records.syntax.find(item => item.path === edge.path);
    assert.equal(syntax.literal_imports.filter(item => item.kind === edge.kind &&
      item.specifier === edge.specifier && JSON.stringify(item.span) === JSON.stringify(edge.span)).length, 1);
  }
  compiler.verify();
  fs.writeFileSync(input.result, JSON.stringify({
    verified: ["merged-declarations", "import-equals", "namespace-reexport"],
    runtime: { version: process.version, architecture: process.arch },
    qualified_controller_sha256: input.controller_sha256,
    merged_symbols: [...merged.values()], records,
  }, null, 2));
});

if (selected) test(selected, () => {
  const compiler = openCompiler(input.binding, input.source);
  const parsed = parseProgram(compiler, input.root, input.entries, input.metadata);
  const { ts } = compiler, { program, checker } = parsed;
  const configBytes = fs.readFileSync(path.join(input.root, input.config_input.path));
  const records = serializeProgram(parsed, {
    ...input.semantic, parser_sha256: parserDigest(compiler),
    settings_sha256: settingsDigest(JSON.parse(configBytes).js_entrypoints),
  }, { input: input.config_input, bytes: configBytes });
  const file = program.getSourceFile("/subject/use.mjs");
  const unit = parsed.sources.get(file.fileName);
  const span = node => unit.span(node.getStart(file), node.end);
  const inside = (site, range) => site.path === "use.mjs" &&
    site.span.start_byte >= range.start_byte && site.span.end_byte <= range.end_byte;
  const evidence = {
    case: selected, runtime: { version: process.version, architecture: process.arch },
    controller_sha256: input.controller_sha256,
    files: records.symbols.files, diagnostics: records.symbols.diagnostics,
    exports: records.symbols.exports, references: records.symbols.references,
    module_references: records.symbols.module_references, outside_model: records.symbols.outside_model,
    literal_imports: records.syntax.find(item => item.path === "use.mjs").literal_imports,
  };
  const preserve = () => fs.writeFileSync(input.result, JSON.stringify(evidence, null, 2));
  preserve();
  assert.deepEqual(parsed.diagnostics, [], "The real fixture must have no compiler diagnostics");
  assert.ok(records.symbols.files.every(item => item.state === "processed"));

  if (selected === "review_r1") {
    const origin = program.getSourceFile("/subject/origin.mjs");
    const actualExport = checker.getExportsOfModule(checker.getSymbolAtLocation(origin)).find(item => item.name === "value");
    const exported = records.symbols.exports.find(item => item.path === "origin.mjs" && item.name === "value");
    assert.equal(exported.target.state, "local");
    assert.equal(exported.target.symbol_ids.length, 1);
    const exportId = exported.target.symbol_ids[0];
    const declarations = file.statements.filter(ts.isVariableStatement)
      .flatMap(node => [...node.declarationList.declarations])
      .filter(node => ts.isObjectBindingPattern(node.name));
    assert.equal(declarations.length, 2);
    evidence.selections = declarations.map(declaration => {
      assert.equal(checker.getPropertyOfType(checker.getTypeAtLocation(declaration.initializer), "value"), actualExport);
      const element = declaration.name.elements[0];
      const localBinding = checker.getSymbolAtLocation(element.name);
      assert.notEqual(localBinding, actualExport, "Local binding must remain a distinct symbol");
      const localRecord = records.symbols.symbols.find(symbol =>
        symbol.declarations.some(item => item.path === "use.mjs" && item.kind === "BindingElement" &&
          item.name === element.name.text));
      assert.ok(localRecord);
      assert.notEqual(localRecord.id, exportId);
      return { selection: element.getText(file), binding_id: localRecord.id, export_id: exportId,
        checker_property_equals_export: true,
        property_target_ids: [...new Set(records.symbols.references.filter(item => inside(item, span(declaration)) &&
          item.target.symbol_ids.includes(exportId)).flatMap(item => item.target.symbol_ids))],
        outside_model: records.symbols.outside_model.filter(item => inside(item, span(declaration))),
      };
    });
    // Positive control: the ordinary namespace property read already resolves correctly.
    assert.ok(records.symbols.references.some(item => item.path === "use.mjs" &&
      item.kind === "property" && item.target.symbol_ids.includes(exportId)));
    evidence.ordinary_property_control = true;
    compiler.verify();
    preserve();
    assert.deepEqual(evidence.selections.map(item => item.property_target_ids), [[exportId], [exportId]],
      "R1: shorthand and literal-key namespace destructuring must reference the exported property, not just the local binding/module");
  } else {
    const calls = [];
    function visit(node) {
      if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) calls.push(node);
      ts.forEachChild(node, visit);
    }
    visit(file);
    assert.equal(calls.length, 3);
    evidence.calls = calls.map(node => {
      const range = span(node);
      return { text: node.getText(file), span: range,
        modules: records.symbols.module_references.filter(item => inside(item, range)),
        syntax: evidence.literal_imports.filter(item => item.span.start_byte === range.start_byte &&
          item.span.end_byte === range.end_byte),
        outside: records.symbols.outside_model.filter(item => inside(item, range)) };
    });
    const [plain, options, computed] = evidence.calls;
    assert.equal(plain.modules[0].resolution, "local");
    assert.deepEqual(plain.modules[0].targets, ["origin.mjs"]);
    assert.equal(plain.syntax[0].specifier, "./origin.mjs");
    assert.equal(computed.modules[0].resolution, "dynamic");
    assert.equal(computed.modules[0].specifier, null);
    assert.deepEqual(computed.modules[0].targets, []);
    assert.deepEqual(computed.syntax, []);
    assert.ok(computed.outside.some(item => item.kind === "computed-import"));
    evidence.literal_and_computed_controls = true;
    compiler.verify();
    preserve();
    assert.deepEqual({
      modules: options.modules.map(({ specifier, kind, resolution, targets, external, reason }) =>
        ({ specifier, kind, resolution, targets, external, reason })),
      syntax: options.syntax.map(({ specifier, kind }) => ({ specifier, kind })),
      computed_sites: options.outside.filter(item => item.kind === "computed-import").length,
    }, {
      modules: [{ specifier: "./origin.mjs", kind: "import", resolution: "local",
        targets: ["origin.mjs"], external: null, reason: "" }],
      syntax: [{ specifier: "./origin.mjs", kind: "import" }], computed_sites: 0,
    }, "R2: empty import options do not turn a literal module specifier into a computed one");
  }
});
