import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const input = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const { openCompiler, parseProgram } = await import(pathToFileURL(input.controller).href);
const compiler = openCompiler(input.binding, input.source);
const sha = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const root = fs.mkdtempSync(path.join(input.scratch, "s-"));
const write = (name, content) => {
  const bytes = Buffer.from(content);
  fs.writeFileSync(path.join(root, name), bytes);
  return { path: name, sha256: sha(bytes), bytes: bytes.length };
};
const observations = {};
const metadata = write("package.json", '{"type":"module"}');
fs.unlinkSync(path.join(root, metadata.path));
assert.throws(() => parseProgram(compiler, root, [], [metadata]), error => {
  assert.match(error.message, /Unreadable admitted metadata: package.json/);
  assert.equal(error.cause.code, "ENOENT");
  observations.missing_metadata = { message: error.message, cause: error.cause.code };
  return true;
});

const source = write("use.ts", "import { value } from './unadmitted.js'; export const used = value;\n");
write("unadmitted.js", "export const value = 7;\n");
const parsed = parseProgram(compiler, root, [source]);
assert.equal(parsed.census.length, 1);
assert.equal(parsed.census[0].state, "processed");
assert.equal(parsed.program.getSourceFile("/subject/unadmitted.js"), undefined);
assert.ok(!parsed.reads.some(item => item.path === "unadmitted.js"));
observations.unadmitted_source = parsed.diagnostics.map(item => item.code);
assert.deepEqual(observations.unadmitted_source, [2307]);

let callbackCalled = false;
const callback = () => { callbackCalled = true; throw new Error("Must not call this"); };
assert.throws(() => parseProgram({ ts: compiler.ts, read: callback, verify: callback }, root, []),
  /Expected a compiler opened by openCompiler/);
assert.equal(callbackCalled, false);
observations.forged_handle = { callback_called: callbackCalled };

const linked = write("linked.ts", "export const value = 1;\n");
fs.linkSync(path.join(root, linked.path), path.join(root, "alias.ts"));
assert.throws(() => parseProgram(compiler, root, [linked]), error => {
  assert.match(error.message, /Input is not an independent regular file/);
  observations.hardlinked_source = error.message;
  return true;
});
compiler.verify();
console.log(JSON.stringify(observations));
