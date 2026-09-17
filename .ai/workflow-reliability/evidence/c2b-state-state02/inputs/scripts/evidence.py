"""Standalone file evidence primitives; no workflow policy or ledger dependency."""

from contextlib import contextmanager
import errno
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _name(value, *, allow_root=False):
    if not isinstance(value, str) or not value or "\0" in value:
        raise ValueError("Expected a nonempty repository-relative path")
    name = value.replace("\\", "/")
    if allow_root and name == ".":
        return name
    if name.startswith("/") or PureWindowsPath(name).drive or any(
            part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("Unsafe repository-relative path: %r" % value)
    return name


def _input_path(root, name):
    path = root / name
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Input escapes repository root: %s" % name)
    # Materialized inputs avoid unrecorded link-target changes and directory loops.
    if os.path.normcase(str(resolved)) != os.path.normcase(os.path.abspath(path)):
        raise ValueError("Linked inputs are unsupported; materialize the scope: %s" % name)
    return path


def source_snapshot(root: Path, scope: dict) -> dict:
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Snapshot root must be a directory")
    if not isinstance(scope, dict) or set(scope) - {"files", "directories", "excluded_outputs"}:
        raise ValueError("Invalid FileScope fields")
    normalized = {}
    for key in ("files", "directories"):
        values = scope.get(key, [])
        if not isinstance(values, list):
            raise ValueError("FileScope %s must be a list" % key)
        normalized[key] = sorted({_name(value, allow_root=key == "directories") for value in values})
    exclusions = scope.get("excluded_outputs", [])
    if not isinstance(exclusions, list):
        raise ValueError("FileScope excluded_outputs must be a list")
    excluded = {}
    for item in exclusions:
        if not isinstance(item, dict) or set(item) != {"path", "reason"}:
            raise ValueError("Each exclusion needs a path and reason")
        name = _name(item["path"])
        reason = item["reason"]
        if not isinstance(reason, str) or not reason.strip() or name in excluded:
            raise ValueError("Exclusions need unique paths and nonempty reasons")
        excluded[name] = reason
    normalized["excluded_outputs"] = [{"path": name, "reason": excluded[name]} for name in sorted(excluded)]

    def is_excluded(name):
        return any(name == prefix or name.startswith(prefix + "/") for prefix in excluded)

    files = {}

    def add_file(name):
        if is_excluded(name):
            raise ValueError("Declared input is excluded: %s" % name)
        path = _input_path(root, name)
        if not path.exists():
            files[name] = {"sha256": None, "mode": "missing"}
            return
        if not path.is_file():
            raise ValueError("Input is not a regular file: %s" % name)
        files[name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mode": "executable" if path.stat().st_mode & 0o111 else "file",
        }

    for name in normalized["files"]:
        add_file(name)
    for name in normalized["directories"]:
        if is_excluded(name):
            raise ValueError("Declared directory is excluded: %s" % name)
        directory = _input_path(root, name)
        if not directory.exists():
            files[name] = {"sha256": None, "mode": "missing"}
            continue
        if not directory.is_dir():
            raise ValueError("Input is not a directory: %s" % name)

        def walk_error(error):
            raise error

        for base, dirs, names in os.walk(directory, onerror=walk_error, followlinks=False):
            kept = []
            for entry in sorted(dirs):
                relative = (Path(base) / entry).relative_to(root).as_posix()
                if not is_excluded(relative):
                    _input_path(root, relative)
                    kept.append(entry)
            dirs[:] = kept
            for entry in sorted(names):
                relative = (Path(base) / entry).relative_to(root).as_posix()
                if not is_excluded(relative):
                    add_file(relative)
    files = dict(sorted(files.items()))
    digest = hashlib.sha256(_json_bytes({"scope": normalized, "files": files})).hexdigest()
    return {"binding_mode": "standalone-source", "base": None, "head": None,
            "scope": normalized, "files": files, "scope_sha256": digest}


def _sync_directory(path):
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        try:
            os.fsync(descriptor)
        except OSError as error:
            if error.errno not in (errno.EINVAL, errno.ENOTSUP):
                raise
    finally:
        os.close(descriptor)


def write_json_atomic(path: Path, value: dict) -> None:
    content = _json_bytes(value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, staged = tempfile.mkstemp(prefix=".%s-" % path.name, suffix=".stage", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staged, path)
        _sync_directory(path.parent)
    finally:
        if os.path.exists(staged):
            os.unlink(staged)


@contextmanager
def exclusive_lock(path: Path, owner: dict):
    """Hold an exclusive owner record; callers provide a unique run token."""
    if not isinstance(owner, dict) or not isinstance(owner.get("token"), str) or not owner["token"]:
        raise ValueError("Lock owner requires a unique nonempty token")
    content = _json_bytes(owner)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    identity = os.fstat(descriptor)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        try:
            current = path.stat()
        except FileNotFoundError as error:
            raise RuntimeError("Lock ownership changed; refusing cleanup") from error
        if (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino) or path.read_bytes() != content:
            raise RuntimeError("Lock ownership changed; refusing cleanup")
        path.unlink()
