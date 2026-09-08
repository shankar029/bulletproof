#!/usr/bin/env python3
"""Run a command under an *idle* timeout and recover cleanly when it hangs.

A total timeout is the wrong tool for "stuck for hours": set it low and it kills
healthy long jobs (renders, installs, test suites); set it high and a real hang
still burns that whole budget. This runner watches *progress* instead. Every
chunk of stdout/stderr resets an idle timer; the command is only killed when it
produces NO output for --idle seconds. A hung process dies in `idle` seconds no
matter how long the job would legitimately take.

On an idle kill the whole process tree is terminated (so no orphaned browser,
daemon, or child keeps a lock), a machine-readable marker is printed, and the
process exits 124 — the same code GNU `timeout` uses — so callers can branch on
"it hung" vs "it failed".

Usage:
    python run.py [--idle SECONDS] [--max SECONDS] [--label NAME] -- <command> [args...]

Options:
    --idle SECONDS   Kill if no output for this long. Default 60.
    --max SECONDS    Absolute ceiling regardless of output (0 = none). Default 0.
    --label NAME     Human label used in the markers. Default: the command.

Exit codes:
    <command's own>  Ran to completion (pass its code straight through).
    124              Killed — idle timeout (hung, no output for --idle s).
    125              Killed — max timeout (--max ceiling hit).

Markers (always on their own line, easy to grep from a transcript):
    [run] idle-timeout after Ns of silence — killed "<label>" (exit 124)
    [run] max-timeout after Ns — killed "<label>" (exit 125)
"""
import argparse
import os
import signal
import subprocess
import sys
import threading
import time


def _kill_tree(proc):
    """Kill the process and every child, cross-platform, best-effort."""
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def _popen(cmd, cwd=None, merge_stderr=True):
    kwargs = dict(
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT if merge_stderr else subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
    )
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["preexec_fn"] = os.setsid  # own process group -> kill the whole tree
    return subprocess.Popen(cmd, **kwargs)


def run_capture(cmd, cwd=None, idle=300.0, max_total=0.0):
    """Run `cmd`, capturing output, under an *idle* timeout that resets on every
    chunk of output. Kills the whole process tree on silence so no child holds a
    lock. Never raises. Returns (rc, stdout, stderr):
        rc = command's own code on completion,
             124 if killed for going silent longer than `idle`,
             125 if killed for exceeding the `max_total` ceiling,
             127 if the command was not found.
    Callers get an idle-hang as rc 124 exactly like GNU `timeout`.
    """
    try:
        proc = _popen(cmd, cwd=cwd, merge_stderr=False)
    except FileNotFoundError:
        return 127, "", "not found"
    except Exception as exc:  # noqa: BLE001
        return 125, "", str(exc)

    out_chunks, err_chunks = [], []
    last = [time.monotonic()]
    lock = threading.Lock()

    def pump(stream, sink):
        for line in stream:
            with lock:
                last[0] = time.monotonic()
            sink.append(line)

    threads = [
        threading.Thread(target=pump, args=(proc.stdout, out_chunks), daemon=True),
        threading.Thread(target=pump, args=(proc.stderr, err_chunks), daemon=True),
    ]
    for t in threads:
        t.start()

    started = time.monotonic()
    reason = None
    while proc.poll() is None:
        time.sleep(0.5)
        now = time.monotonic()
        with lock:
            idle_for = now - last[0]
        if idle > 0 and idle_for >= idle:
            reason = 124
            _kill_tree(proc)
            break
        if max_total > 0 and (now - started) >= max_total:
            reason = 125
            _kill_tree(proc)
            break

    proc.wait()
    for t in threads:
        t.join(timeout=2)

    stdout = "".join(out_chunks)
    stderr = "".join(err_chunks)
    if reason == 124:
        return 124, stdout, (stderr + "\n[idle-timeout]").strip()
    if reason == 125:
        return 125, stdout, (stderr + "\n[max-timeout]").strip()
    return proc.returncode, stdout, stderr


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--idle", type=float, default=60.0)
    parser.add_argument("--max", type=float, default=0.0)
    parser.add_argument("--label", default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    cmd = args.command
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("run.py: no command given (use: run.py --idle 60 -- <cmd>)", file=sys.stderr)
        return 2

    label = args.label or " ".join(cmd)

    popen_kwargs = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    )
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        popen_kwargs["preexec_fn"] = os.setsid  # own process group -> kill the whole tree

    proc = subprocess.Popen(cmd, **popen_kwargs)

    last_output = time.monotonic()
    started = last_output
    lock = threading.Lock()
    killed_reason = [None]  # "idle" | "max"

    def pump():
        nonlocal last_output
        assert proc.stdout is not None
        for line in proc.stdout:
            with lock:
                last_output = time.monotonic()
            sys.stdout.write(line)
            sys.stdout.flush()

    pump_thread = threading.Thread(target=pump, daemon=True)
    pump_thread.start()

    while proc.poll() is None:
        time.sleep(0.5)
        now = time.monotonic()
        with lock:
            idle_for = now - last_output
        if args.idle > 0 and idle_for >= args.idle:
            killed_reason[0] = "idle"
            _kill_tree(proc)
            break
        if args.max > 0 and (now - started) >= args.max:
            killed_reason[0] = "max"
            _kill_tree(proc)
            break

    proc.wait()
    pump_thread.join(timeout=2)

    if killed_reason[0] == "idle":
        print(
            f'\n[run] idle-timeout after {int(args.idle)}s of silence — killed "{label}" (exit 124)',
            flush=True,
        )
        return 124
    if killed_reason[0] == "max":
        print(
            f'\n[run] max-timeout after {int(args.max)}s — killed "{label}" (exit 125)',
            flush=True,
        )
        return 125
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
