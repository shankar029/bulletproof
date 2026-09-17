"""Check frozen C3 evidence and the actual staged checkout before preservation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / ".ai" / "workflow-reliability" / "evidence"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "run.py"),
         "--idle", "30", "--max", "120", "--", "git", *args],
        cwd=ROOT, capture_output=True, check=True,
    )
    if result.stderr:
        print(result.stderr.decode("utf-8", errors="replace"), end="", flush=True)
    return result.stdout.decode("utf-8").strip()


def main():
    owner = json.loads((EVIDENCE / "c3-integration-seal.json").read_text("utf-8"))
    seal_path = EVIDENCE / "c3-independent-seal.json"
    assert digest(seal_path) == (
        "80f5c69048b5098372864d46a3c9010f56da60a647db9cc9cb65777ac4926758"
    )
    seal = json.loads(seal_path.read_text("utf-8"))
    pins = dict(seal["input_pins"])
    for path, expected in seal["artifacts"].items():
        assert path not in pins or pins[path] == expected, path
        pins[path] = expected
    for path, expected in pins.items():
        assert digest(ROOT / path) == expected, f"Changed sealed input: {path}"
    print(f"Matched {len(pins)} input/evidence pins.", flush=True)

    staged = set(git("diff", "--cached", "--name-only").splitlines())
    owned = owner["owned"]
    assert set(owned) <= staged, "Stage all 16 reviewed C3 files first."
    assert "evals/report.md" not in staged
    assert not any("q2-" in path for path in staged), "Q2 is outside this commit."
    checkout = Path(tempfile.mkdtemp(prefix="bp-c3-"))
    rows = {}
    try:
        git("checkout-index", f"--prefix={checkout.as_posix()}/", "--", *owned)
        for path, expected in owned.items():
            actual = digest(checkout / path)
            assert actual == expected, f"Checkout differs from tested bytes: {path}"
            rows[path] = {"tested_sha256": expected, "checkout_sha256": actual}
        print(f"Matched {len(rows)} actual staged checkout files.", flush=True)
    finally:
        for path in owned:
            materialized = checkout / path
            if materialized.is_file():
                materialized.unlink()
        directories = {
            parent
            for path in owned
            for parent in (checkout / path).parents
            if parent != checkout and checkout in parent.parents
        }
        for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
            if directory.exists():
                directory.rmdir()
        checkout.rmdir()

    result = {
        "kind": "C3 parent preservation check, not additional runtime tests",
        "head_before_commit": git("rev-parse", "HEAD"),
        "independent_seal_sha256": digest(seal_path),
        "reconciled_input_and_artifact_count": len(pins),
        "review_sha256": digest(EVIDENCE / "c3-code-review.md"),
        "root_attributes_present": (ROOT / ".gitattributes").exists(),
        "root_attributes_sha256": (
            digest(ROOT / ".gitattributes")
            if (ROOT / ".gitattributes").exists() else None
        ),
        "staged_checkout": rows,
        "staged_paths_at_check": sorted(staged),
        "owned_checkout_removed": not checkout.exists(),
    }
    with (EVIDENCE / "c3-parent-preservation.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("Preservation evidence written.", flush=True)


if __name__ == "__main__":
    main()
