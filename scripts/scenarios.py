#!/usr/bin/env python3
"""Reconcile `.ai/<slug>/scenarios.md` against the evidence it claims.

Phase 3 enumerates the end-to-end scenarios and declares, per row, the artifact
that will prove it. Phase 5 executes them. Phase 6 reconciles. Every one of
those steps is a prompt rule an agent must choose to follow, and the failure
this script exists for is the quiet one: a scenario that was never run, or one
whose "evidence" is a zero-byte file, a stale screenshot from three commits
ago, or a transcript of the failure it was supposed to disprove.

Judgement does not catch that reliably. A file check does.

What it enforces, per scenario row:

    MISSING    no artifact at the declared path
    EMPTY      artifact exists but is zero bytes
    STALE      artifact mtime predates --since (the commit it claims to prove)
    DROPPED    a row carries no evidence path and no BLOCKED reason
    UNPROVEN   --strict only: no backticked literal from `Expected observable`
               appears in a text artifact

BLOCKED rows are exempt from artifact checks but must carry a reason: an
environment blocker is an honest outcome, an empty Status cell is not.

--coverage is the Gate 3 mode, run when nothing has been executed yet. It
ignores evidence entirely and asks whether the *enumeration* is complete:

    UNCOVERED      an AC has no scenario and no N/A row for some class
    VAGUE          expected observable has no literal or number to assert
    NO-DESTINATION no evidence path declared, and not N/A or BLOCKED
    NO-AC          row names no acceptance criterion
    NO-CLASS       row's class matches none of the seven
    UNREASONED-NA  N/A without a stated reason

What neither mode can do is judge whether a scenario is *worth running*. A row
reading "expect `ok`" satisfies every check here. This raises the floor on
shape; the design review and the Phase 6 reviewer remain the only judges of
substance.

Usage:
    python scenarios.py --slug <slug> [--root DIR] [--since REF]
                        [--ac AC1,AC2] [--strict] [--coverage] [--json]

Options:
    --slug NAME   Workspace slug under <root>/.ai/. Required.
    --root DIR    Repository root. Default: cwd.
    --since REF   Git ref whose commit time artifacts must not predate.
                  Default: HEAD. Pass --since '' to skip the staleness check.
    --ac LIST     Only check rows whose AC is in this comma-separated list
                  (an increment gate checks its due scope, not the whole plan).
    --strict      Also require a backticked literal from the expected
                  observable to appear in text artifacts. Advisory by design:
                  it cannot read a screenshot, so it never claims to.
    --coverage    Gate 3 mode: check enumeration completeness and specificity
                  instead of evidence. ACs come from traceability.md unless
                  --ac is given.
    --json        Emit a machine-readable report on stdout instead of text.

Exit codes:
    0   every checked row is proven or honestly blocked
    1   one or more rows failed a check
    2   usage error, or scenarios.md is missing or unparseable
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath

# Header cells are matched by these aliases so the table can be written for a
# human without the checker pinning one exact wording.
COLUMNS = {
    "id": ("id", "s-id", "sid", "scenario"),
    "ac": ("ac", "acs", "criterion", "criteria"),
    "cls": ("class", "type", "category"),
    "expected": ("expected observable", "expected", "observable", "pass condition"),
    "evidence": ("evidence", "artifact", "evidence artifact", "evidence path"),
    "status": ("status", "result", "verdict", "outcome"),
}

ID_RE = re.compile(r"^S\d+[a-z]?$", re.IGNORECASE)
AC_RE = re.compile(r"\bAC\s*0*(\d+)\b", re.IGNORECASE)
NA_RE = re.compile(r"\bN/?A\b", re.IGNORECASE)
# The seven classes Phase 5 must cover, each mapped to the substrings a row
# might actually use — the table is written for a human, so "negative/rejection"
# and "failure/fault" are both normal ways to name their class.
CLASSES = {
    "positive": ("positive", "primary", "happy"),
    "negative": ("negative", "rejection", "invalid"),
    "boundary": ("boundary", "edge", "limit"),
    "failure": ("failure", "fault", "degrade", "outage"),
    "authorization": ("authorization", "authz", "auth", "permission"),
    "idempotency": ("idempotency", "idempotent", "repeat", "retry", "concurrent"),
    "regression": ("regression", "invariant", "preserved"),
}
BACKTICKED_RE = re.compile(r"`([^`]+)`")
BLOCKED_RE = re.compile(r"\bBLOCKED\b", re.IGNORECASE)
# Only these are read as text for --strict; anything else (png, pdf, bin) is
# reported as unreadable rather than silently passed.
TEXT_SUFFIXES = {
    ".txt",
    ".log",
    ".json",
    ".jsonl",
    ".md",
    ".csv",
    ".xml",
    ".yaml",
    ".yml",
    ".html",
    ".har",
    ".out",
    ".err",
}


@dataclass
class Row:
    ident: str
    ac: str
    cls: str
    expected: str
    evidence: str
    status: str
    line: int


@dataclass
class Failure:
    ident: str
    kind: str
    detail: str


@dataclass
class Report:
    checked: int = 0
    blocked: list = field(default_factory=list)
    failures: list = field(default_factory=list)
    skipped: int = 0

    @property
    def ok(self) -> bool:
        return not self.failures


def _split_row(line: str) -> list[str]:
    body = line.strip()
    body = body.removeprefix("|")
    body = body.removesuffix("|")
    return [cell.strip() for cell in body.split("|")]


def _is_delimiter(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _map_header(cells: list[str]) -> dict[str, int] | None:
    """Return column-key -> index, or None when this is not the scenario table."""
    found: dict[str, int] = {}
    for index, cell in enumerate(cells):
        name = cell.strip().strip("*").lower()
        for key, aliases in COLUMNS.items():
            if key in found:
                continue
            if name in aliases or any(name.startswith(a + " ") for a in aliases):
                found[key] = index
                break
    # The table is identified by the two columns this tool cannot work without.
    if "id" in found and "evidence" in found:
        return found
    return None


def _cell(cells: list[str], header: dict[str, int], key: str) -> str:
    index = header.get(key)
    return cells[index] if index is not None and index < len(cells) else ""


def parse_scenarios(text: str) -> list[Row]:
    """Extract scenario rows from the first markdown table that has Id + Evidence."""
    rows: list[Row] = []
    header: dict[str, int] | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        if "|" not in line:
            if header and rows:
                break  # table ended
            continue
        cells = _split_row(line)
        if header is None:
            header = _map_header(cells)
            continue
        if _is_delimiter(cells):
            continue

        ident = _cell(cells, header, "id").strip().strip("*").strip("`")
        if not ID_RE.match(ident):
            continue  # not a scenario row (a note, a spanning cell, an example)
        rows.append(
            Row(
                ident=ident.upper(),
                ac=_cell(cells, header, "ac"),
                cls=_cell(cells, header, "cls"),
                expected=_cell(cells, header, "expected"),
                evidence=_cell(cells, header, "evidence"),
                status=_cell(cells, header, "status"),
                line=number,
            )
        )
    return rows


def commit_time(root: Path, ref: str) -> int | None:
    try:
        out = subprocess.run(  # fixed argv, no shell
            ["git", "-C", str(root), "log", "-1", "--format=%ct", ref],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    value = out.stdout.strip()
    return int(value) if value.isdigit() else None


def _artifact_path(slug_dir: Path, declared: str) -> Path | None:
    cleaned = declared.strip().strip("`").strip()
    # Tolerate a markdown link: [S1 transcript](evidence/S1.json)
    link = re.search(r"\]\(([^)]+)\)", cleaned)
    if link:
        cleaned = link.group(1).strip()
    if not cleaned or cleaned in {"-", "—", "n/a", "N/A"}:
        return None
    # Normalize separators FIRST: a backslash path must face the same rules as a
    # forward-slash one on every platform. Splitting only on "/" lets
    # `..\..\etc\passwd` through as one innocuous-looking component.
    cleaned = cleaned.replace("\\", "/")
    # A trailing slash is a legitimate way to write a directory artifact; strip
    # it before splitting so it is not read as an empty final component.
    cleaned = cleaned.rstrip("/")
    if not cleaned:
        return None
    if cleaned.startswith((".ai/", "/")) or PureWindowsPath(cleaned).drive:
        return None
    if any(part in ("", ".", "..") for part in cleaned.split("/")):
        return None
    candidate = slug_dir / cleaned
    # Containment is re-checked on the resolved path, so a symlink planted
    # inside the workspace cannot redirect the checker outside it.
    try:
        if not candidate.resolve().is_relative_to(slug_dir.resolve()):
            return None
    except OSError:
        return None
    return candidate


def _row_acs(row: Row) -> set[str]:
    return {f"AC{int(n)}" for n in AC_RE.findall(row.ac)}


def _row_classes(row: Row) -> set[str]:
    text = row.cls.lower()
    return {key for key, aliases in CLASSES.items() if any(a in text for a in aliases)}


def _is_specific(expected: str) -> bool:
    """A pass condition a machine could later sample, not a hope.

    Backticked literal or a bare number. "Works correctly" fails; so does an
    empty cell. This is shape, not substance — see the docstring caveat.
    """
    body = expected.strip()
    if not body or NA_RE.fullmatch(body):
        return False
    return bool(BACKTICKED_RE.search(body)) or bool(re.search(r"\d", body))


def read_acs(slug_dir: Path) -> set[str]:
    """Acceptance-criterion ids from traceability.md, seeded in Phase 1."""
    source = slug_dir / "traceability.md"
    if not source.is_file():
        return set()
    found: set[str] = set()
    for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        first = _split_row(line)[0].strip().strip("*`")
        match = AC_RE.fullmatch(first)
        if match:
            found.add(f"AC{int(match.group(1))}")
    return found


def coverage(
    root: Path, slug: str, acs: set[str] | None, classes: set[str] | None = None
) -> Report:
    """Gate 3: is the enumeration complete and specific, before any evidence exists?

    Deliberately does not touch the filesystem beyond the two documents: at
    Gate 3 nothing has been run yet, so an evidence check would fail by design.
    """
    slug_dir = root / ".ai" / slug
    source = slug_dir / "scenarios.md"
    if not source.is_file():
        raise FileNotFoundError(source)

    rows = parse_scenarios(source.read_text(encoding="utf-8", errors="replace"))
    if not rows:
        raise ValueError(
            f"no scenario rows found in {source} — expected a markdown table with at "
            "least 'Id' and 'Evidence' columns and S-prefixed ids"
        )

    report = Report()
    wanted = acs if acs is not None else read_acs(slug_dir)
    if not wanted:
        raise ValueError(
            "no acceptance criteria found: seed traceability.md in Phase 1, or pass --ac"
        )
    want_classes = classes or set(CLASSES)

    covered: dict[tuple[str, str], list[str]] = {}
    for row in rows:
        report.checked += 1
        row_acs, row_classes = _row_acs(row), _row_classes(row)
        if not row_acs:
            report.failures.append(
                Failure(row.ident, "NO-AC", "row names no acceptance criterion")
            )
        if not row_classes:
            report.failures.append(
                Failure(
                    row.ident,
                    "NO-CLASS",
                    f"class {row.cls!r} matches none of {', '.join(sorted(CLASSES))}",
                )
            )
        excused = NA_RE.search(row.status) or BLOCKED_RE.search(row.status)
        if not _is_specific(row.expected) and not excused:
            report.failures.append(
                Failure(
                    row.ident,
                    "VAGUE",
                    "expected observable has no literal or number to assert: "
                    f"{row.expected.strip() or '(empty)'!r}",
                )
            )
        if not excused and _artifact_path(slug_dir, row.evidence) is None:
            report.failures.append(
                Failure(row.ident, "NO-DESTINATION", "no evidence path declared")
            )
        if NA_RE.search(row.status) and not NA_RE.sub("", row.status).strip(" :.-—"):
            report.failures.append(
                Failure(row.ident, "UNREASONED-NA", "N/A without a stated reason")
            )
        for ac in row_acs:
            for cls in row_classes:
                covered.setdefault((ac, cls), []).append(row.ident)

    for ac in sorted(wanted, key=lambda x: int(x[2:])):
        missing = sorted(c for c in want_classes if (ac, c) not in covered)
        if missing:
            report.failures.append(
                Failure(ac, "UNCOVERED", "no scenario or N/A row for: " + ", ".join(missing))
            )
    return report


def check(
    root: Path, slug: str, since: str | None, acs: set[str] | None, strict: bool
) -> Report:
    slug_dir = root / ".ai" / slug
    source = slug_dir / "scenarios.md"
    if not source.is_file():
        raise FileNotFoundError(source)

    rows = parse_scenarios(source.read_text(encoding="utf-8", errors="replace"))
    if not rows:
        raise ValueError(
            f"no scenario rows found in {source} — expected a markdown table with at "
            "least 'Id' and 'Evidence' columns and S-prefixed ids"
        )

    report = Report()
    cutoff = commit_time(root, since) if since else None
    seen: dict[str, int] = {}

    for row in rows:
        if row.ident in seen:
            report.failures.append(
                Failure(
                    row.ident, "DUPLICATE", f"id reused (also line {seen[row.ident]})"
                )
            )
            continue
        seen[row.ident] = row.line

        if acs is not None and not (
            {a.strip().upper() for a in row.ac.replace(",", " ").split()} & acs
        ):
            report.skipped += 1
            continue

        if BLOCKED_RE.search(row.status):
            reason = BLOCKED_RE.sub("", row.status).strip(" :.-—")
            if not reason:
                report.failures.append(
                    Failure(row.ident, "DROPPED", "BLOCKED without a named blocker")
                )
            else:
                report.blocked.append({"id": row.ident, "reason": reason})
            continue

        report.checked += 1
        path = _artifact_path(slug_dir, row.evidence)
        if path is None:
            report.failures.append(
                Failure(row.ident, "DROPPED", "no evidence path and not BLOCKED")
            )
            continue
        if not path.exists():
            report.failures.append(
                Failure(row.ident, "MISSING", path.relative_to(slug_dir).as_posix())
            )
            continue
        if path.is_dir():
            if not any(p.is_file() and p.stat().st_size > 0 for p in path.rglob("*")):
                report.failures.append(
                    Failure(row.ident, "EMPTY", "directory holds no non-empty file")
                )
                continue
            newest = max(p.stat().st_mtime for p in path.rglob("*") if p.is_file())
        else:
            if path.stat().st_size == 0:
                report.failures.append(
                    Failure(row.ident, "EMPTY", path.relative_to(slug_dir).as_posix())
                )
                continue
            newest = path.stat().st_mtime

        if cutoff is not None and newest < cutoff:
            report.failures.append(
                Failure(
                    row.ident,
                    "STALE",
                    f"artifact predates {since} by {int(cutoff - newest)}s",
                )
            )
            continue

        if strict and path.is_file():
            literals = BACKTICKED_RE.findall(row.expected)
            if literals:
                if path.suffix.lower() not in TEXT_SUFFIXES:
                    report.failures.append(
                        Failure(
                            row.ident,
                            "UNPROVEN",
                            "--strict cannot read {}; a human or the reviewer must "
                            "confirm it shows: {}".format(
                                path.suffix or "this file", ", ".join(literals)
                            ),
                        )
                    )
                    continue
                body = path.read_text(encoding="utf-8", errors="replace")
                if not any(literal in body for literal in literals):
                    report.failures.append(
                        Failure(
                            row.ident,
                            "UNPROVEN",
                            "none of {} appears in {}".format(
                                ", ".join(repr(x) for x in literals),
                                path.relative_to(slug_dir).as_posix(),
                            ),
                        )
                    )
    return report


def render(report: Report, slug: str, strict: bool, mode: str = "evidence") -> str:
    skipped = f" · skipped {report.skipped} (out of scope)" if report.skipped else ""
    lines = [
        f"scenarios ({mode}): {slug}",
        (
            f"  checked {report.checked} · blocked {len(report.blocked)}"
            f" · failed {len(report.failures)}{skipped}"
        ),
    ]
    for item in report.blocked:
        lines.append(f"  BLOCKED  {item['id']:<6} {item['reason']}")
    for failure in report.failures:
        lines.append(f"  {failure.kind:<14} {failure.ident:<6} {failure.detail}")
    if report.ok and mode == "coverage":
        lines.append(
            "  OK — every AC × class is enumerated with a specific expected observable. "
            "Shape only: a scenario can still be shallow."
        )
    elif report.ok:
        lines.append(
            "  OK — every checked row is proven or honestly blocked."
            + ("" if strict else " (run --strict to sample artifact contents)")
        )
    elif mode == "coverage":
        lines.append(
            "  FAIL — the enumeration is incomplete. Add the scenario, or record "
            "N/A with a reason; do not leave the cell silent."
        )
    else:
        lines.append(
            "  FAIL — a scenario without proof is not verified. "
            "Re-run it, or mark it BLOCKED with a named blocker."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scenarios.py",
        description="Reconcile .ai/<slug>/scenarios.md against captured evidence.",
    )
    parser.add_argument("--slug", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--since",
        default="HEAD",
        help="git ref artifacts must not predate ('' to skip)",
    )
    parser.add_argument(
        "--ac", default=None, help="comma-separated ACs to limit the check to"
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Gate 3 mode: check the enumeration is complete and specific, "
        "without touching evidence (nothing has run yet)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    acs = (
        {a.strip().upper() for a in args.ac.split(",") if a.strip()}
        if args.ac
        else None
    )

    try:
        if args.coverage:
            report = coverage(root, args.slug, acs)
        else:
            report = check(root, args.slug, args.since or None, acs, args.strict)
    except FileNotFoundError as error:
        print(f"scenarios.py: not found: {error}", file=sys.stderr)
        print(
            "Phase 3 writes this file; see references/planning.md §4b.", file=sys.stderr
        )
        return 2
    except ValueError as error:
        print(f"scenarios.py: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "slug": args.slug,
                    "mode": "coverage" if args.coverage else "evidence",
                    "checked": report.checked,
                    "skipped": report.skipped,
                    "blocked": report.blocked,
                    "failures": [vars(f) for f in report.failures],
                    "ok": report.ok,
                },
                indent=2,
            )
        )
    else:
        print(
            render(
                report,
                args.slug,
                args.strict,
                "coverage" if args.coverage else "evidence",
            )
        )
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
