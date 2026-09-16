import { spawn, spawnSync } from 'node:child_process';

export async function runNode(args, { cwd, timeout = 120000 } = {}) {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, args, { cwd, windowsHide: true });
    let stdout = '', stderr = '', timedOut = false;
    child.stdout.on('data', bytes => { stdout += bytes; });
    child.stderr.on('data', bytes => { stderr += bytes; });
    const timer = setTimeout(() => {
      timedOut = true;
      if (process.platform === 'win32') {
        spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true });
      } else {
        child.kill('SIGKILL');
      }
    }, timeout);
    child.once('error', error => { clearTimeout(timer); reject(error); });
    child.once('close', code => {
      clearTimeout(timer);
      resolve({ args, cwd, code, timedOut, stdout, stderr, durationMs: Date.now() - started });
    });
  });
}
