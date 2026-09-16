import { mkdir, open, readFile, rename, unlink } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import { AppError, decode, emptyModel, encode, validate } from './schema.mjs';

async function removeOwned(path) {
  try { await unlink(path); } catch (error) { if (error.code !== 'ENOENT') throw error; }
}

export class JsonStore {
  #model;
  #queue = Promise.resolve();
  #closed = false;
  #token = randomUUID();
  #commitFile;

  constructor(directory, commitFile) {
    this.directory = resolve(directory);
    this.path = join(this.directory, 'planner.json');
    this.lockPath = join(this.directory, 'writer.lock');
    this.#commitFile = commitFile ?? rename;
  }

  static async open({ directory, commitFile }) {
    const store = new JsonStore(directory, commitFile);
    await mkdir(store.directory, { recursive: true });
    let lock;
    try { lock = await open(store.lockPath, 'wx'); } catch (error) {
      if (error.code === 'EEXIST') throw new AppError('STORE_LOCKED', 'Data directory is already locked; stop its owner before recovery', 409);
      throw error;
    }
    try {
      await lock.writeFile(JSON.stringify({ token: store.#token, pid: process.pid }));
      await lock.sync();
      await lock.close();
      let bytes;
      try { bytes = await readFile(store.path, 'utf8'); } catch (error) {
        if (error.code !== 'ENOENT') throw error;
      }
      if (bytes === undefined) {
        store.#model = emptyModel();
        await store.#persist(encode(store.#model));
      } else store.#model = decode(bytes);
      return store;
    } catch (error) {
      await lock.close();
      await store.close();
      throw error;
    }
  }

  read() {
    if (this.#closed) throw new AppError('STORE_CLOSED', 'Store is closed', 503);
    return structuredClone(this.#model);
  }

  async #persist(bytes) {
    const stage = join(this.directory, `.planner-${this.#token}-${randomUUID()}.stage`);
    let file;
    try {
      file = await open(stage, 'wx');
      await file.writeFile(bytes);
      await file.sync();
      await file.close();
      await this.#commitFile(stage, this.path);
    } catch (error) {
      await file?.close();
      await removeOwned(stage);
      throw new AppError('STORAGE_UNAVAILABLE', 'Could not save. Read current state before trying again.', 503);
    }
  }

  transact(expectedRevision, change) {
    if (this.#closed) return Promise.reject(new AppError('STORE_CLOSED', 'Store is closed', 503));
    const operation = this.#queue.then(async () => {
      if (expectedRevision !== this.#model.revision) throw new AppError('REVISION_CONFLICT', 'Tasks changed. Reload before saving.', 409);
      const next = structuredClone(this.#model);
      const value = change(next);
      if (value?.then) throw new TypeError('Transaction change must be synchronous');
      if (JSON.stringify(next) === JSON.stringify(this.#model)) return { value: structuredClone(value), revision: next.revision };
      if (next.revision !== this.#model.revision || next.schemaVersion !== this.#model.schemaVersion) throw new TypeError('Command cannot change envelope revision/schema');
      if (next.revision === Number.MAX_SAFE_INTEGER) throw new AppError('CAPACITY_EXCEEDED', 'Revision capacity exceeded', 409);
      next.revision++;
      validate(next);
      const bytes = encode(next);
      const result = { value: structuredClone(value), revision: next.revision };
      await this.#persist(bytes);
      this.#model = next;
      return result;
    });
    this.#queue = operation.catch(() => {});
    return operation;
  }

  async close() {
    this.#closed = true;
    await this.#queue;
    let bytes;
    try { bytes = await readFile(this.lockPath, 'utf8'); } catch (error) {
      if (error.code === 'ENOENT') return;
      throw error;
    }
    let owner;
    try { owner = JSON.parse(bytes); } catch { return; }
    if (owner.token === this.#token) await removeOwned(this.lockPath);
  }
}
