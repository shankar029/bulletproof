# REVISE — narrowed R1/R2 correction review

Original return from `9a253936-ce4f-4e86-89be-a19ac9f6c7d5`.
Parent disposition follows the preserved return.

**R1 is accepted on the reviewed Windows boundary. R2 fixes the original immutable-baseline counterexample, but one reproduced policy-admission defect remains. Q2 admission: HOLD.**

This finding is confined to the newly introduced attribute gate. It does not reopen F1/F2/F3, C1, or unrelated quality work.

## Residual R2 finding — P2 / Medium / contract correctness

**Location:** `scripts/measure.py:133–150`, specifically the unconditional allowed values at **line 144**, followed by checkout at **line 160**.

### Mechanism

The materializer treats Git’s textual attribute results `"unset"` and `"unspecified"` as unambiguous state markers:

```python
allowed = {"unspecified", "unset"}
```

But these are also valid **literal external-filter names**:

```gitattributes
*.py filter=unset
```

and:

```gitattributes
*.py filter=unspecified
```

For those declarations, `git check-attr --cached -z filter -- a.py` returns respectively:

```text
a.py\0filter\0unset\0
a.py\0filter\0unspecified\0
```

Both pass the gate. **`materialize_baseline` and `validate_baseline` accept them**, instead of explicitly rejecting the declared external filter as required by the approved policy.

### Actual observations

| Versioned declaration | Materialize + validate | Sentinel during isolated materialization | Ordinary checkout with corresponding driver configured |
|---|---|---|---|
| `filter=unset` | **Accepted** | Absent | **Executed** |
| `filter=unspecified` | **Accepted** | Absent | **Executed** |

The positive controls prove these strings name real filter drivers, rather than being equivalent to `-filter` or an unspecified attribute.

**Important limit:** isolation prevented driver execution during materialization. This is an unsupported-filter admission defect, **not a demonstrated execution escape, corrupted-baseline acceptance, or overall-green report**.

### Minimal correction

Correct the Git-attribute classification before the first checkout-capable operation:

- Do not infer typed attribute state solely from these textual values.
- Use a **qualified Git-native census/distinction**, or conservatively reject ambiguous declarations.
- Git’s cached all-attributes enumeration is a candidate for that bounded qualification; do not substitute a handwritten partial attributes interpreter.
- Merely removing `"unspecified"` from this existing allowlist would also reject genuinely absent attributes, so that alone is not a sufficient correction.
- Preserve the ordinary no-filter positive, existing macro/sentinel control, and add these two literal-name regressions through the shared materializer/validator boundary.

No repair was made.

## Reproduction

Run from the repository root. This uses the actual qualified Git package and only privately owned, cleaned fixtures.

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PATH = 'C:\Users\shbs\AppData\Local\github-copilot-git-2.53.0-4\cmd;' + $env:PATH

$code = @'
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path("scripts/tests").resolve()))
from helpers import GitFixture
import measure

for name in ("unset", "unspecified"):
    fixture = GitFixture()
    try:
        with tempfile.TemporaryDirectory(prefix="q1-review-filter-") as temporary:
            owned = Path(temporary).resolve()
            fixture.write(".gitattributes", "*.py filter=" + name + "\n")
            fixture.write("a.py", "pass\n")
            revision = fixture.commit("fixture: named filter textual collision")

            sentinel = owned / "EXECUTED"
            program = owned / "driver.py"
            program.write_text(
                "import pathlib,sys\n"
                "pathlib.Path(sys.argv[1]).write_text('executed')\n"
                "sys.stdout.buffer.write(sys.stdin.buffer.read())\n",
                encoding="utf-8",
            )
            driver = '"%s" -B "%s" "%s"' % (
                Path(sys.executable).as_posix(),
                program.as_posix(),
                sentinel.as_posix(),
            )
            fixture.run("git", "config", "filter." + name + ".smudge", driver)

            print("ATTRIBUTE", repr(fixture.run(
                "git", "check-attr", "--cached", "-z", "filter", "--", "a.py"
            )[1]), flush=True)

            target = owned / "base"
            measure.materialize_baseline(fixture.root, target, revision)
            measure.validate_baseline(target, revision)
            assert not sentinel.exists()
            print("ACCEPTED", name, "sentinel absent", flush=True)

            # Prove this is a real named filter, not a disabled attribute.
            fixture.run(
                "git", "config", "filter." + name + ".smudge", driver,
                cwd=target,
            )
            fixture.run(
                "git", "checkout-index", "--all", "--force", cwd=target,
            )
            assert sentinel.read_text() == "executed"
            print("POSITIVE", name, sentinel.read_text(), flush=True)
    finally:
        fixture.close()
'@

& $py -B scripts/run.py --idle 120 --max 1200 -- $py -B -c $code
```

The diagnostic reproducer completes successfully while displaying the **incorrect acceptance**. In my execution, materialization plus validation took **7.333s** and **7.465s** respectively; these are individual fixture observations, not benchmarks.

## Correction assessment

### R1 — accepted, bounded

The actual delta addresses the original mechanism:

- Shared relative-path checks reject trailing-dot/space components.
- Existing component spelling is checked, including absolute-root ancestors.
- `"."` remains directory-only.
- Source-root validation occurs independently at both revisions.
- A genuinely absent newly introduced baseline directory remains permitted.

The preserved independent public-CLI evidence shows canonical `scripts` retaining the cycle and both alias configurations exiting **2**, without an accepted measured alias report. Native import evidence remains **canonical and dot-only**; no native-space claim is inferred.

### R2 — original corruption fixed; policy acceptance incomplete

The independent materialization and exact comparison replace status/index cleanliness as baseline authority. The reviewed implementation and pinned independent evidence support:

- Fresh assume-unchanged corruption rejection.
- Skip-worktree and altered-index controls.
- Full relevant file-set comparison, including hidden, non-code and analyzer-excluded inputs.
- Missing-file, directory-replacement and extra-file rejection.
- Exact expected bytes without normalizing supplied bytes.
- Qualified neutral/versioned EOL behavior.
- Explicit Windows mode projection.
- Common CLI-copy and supplied-Context validation policy.
- Policy implementation/controller binding and qualified Git identity checks.

**The remaining exception is the declared-filter classification above.** Thus the broad claim “declared external filters are rejected before materialization” is not yet true.

### F1/F2/F3 — retained

The prior accepted builtin/frozen precedence, physical independence and effective-frozen fingerprint corrections remain supported by the independent replay. I compared the current three modules against archived controller bytes matching the exact prior Q1 freeze hashes; this correction does not replace those mechanisms.

## Verification and operational limits

The independent freeze and handoff records reconcile to:

| Independent batch | Tests | Failures/errors/skips |
|---|---:|---:|
| Graph/inventory | 25 | 0 |
| Integration/review/boundaries | 30 | 0 |
| Legacy probe | 19 | 0 |

These are **three clean completed batches, once each: 74 distinct methods**. They remain valid execution evidence, but do not cover the newly reproduced filter-name ambiguity.

The owner’s historical 52-case passing union is **not** reclassified as a clean aggregate. The disclosed parent-state preflight reconciliation is likewise not a test retry.

I additionally ran these two existing no-shared-write controls:

- `ResumedBoundaryTests.test_shared_paths_reject_alias_components_and_preserve_directory_dot`
- `ResumedBoundaryTests.test_external_filter_macro_rejected_before_sentinel_execution`

**Both passed in 13.268s.** They are repeats, not additions to the 74-method count.

**Cleanup:** all **16 recorded temporary directories** from my focused test/probe invocation were absent afterward. Materializer-internal temporary resources are context-managed; the destination remains caller-owned, including on rejection. CLI and validator callers provide enclosing owned cleanup. No supplied source/index/configuration modification was observed in this review.

**Cost:** validation now performs a private Git clone and complete file hashing, with repeated core/DLL identity hashing. Git operations have **30-second idle / 90-second total bounds**, and attribute argv is batched without dropping paths. These are subprocess bounds—not a global materialization time, memory or repository-size guarantee. No separate performance blocker was established on the bounded fixtures.

## CHECK / AC verdicts

| Scope | Verdict |
|---|---|
| **CHECK-INVENTORY** | **VERIFIED-WITH-LIMITATIONS:** R1 canonical boundaries and complete relevant baseline file census supported. |
| **CHECK-GRAPH** | **VERIFIED-WITH-LIMITATIONS** for the reviewed Python literal-import/R1 behavior; this does not approve unsupported baseline representations. |
| **CHECK-PARTIAL-PROBE** | **VERIFIED:** all-nine required-set and incomplete/fail behavior preserved. |
| **CHECK-RECONCILE** | **NOT-VERIFIED for final Q1 acceptance:** named external filters can be accepted under a policy that requires rejection. |
| **AC01** | **VERIFIED-WITH-LIMITATIONS** for bounded Q1 inventory/native preservation; no future mixed-language mutation acceptance. |
| **AC02** | **NOT-VERIFIED for final Q1 acceptance:** missing-as-fail holds, but baseline policy qualification remains incomplete. |
| **AC09** | **NOT-VERIFIED for final Q1 acceptance:** existing regressions pass, but the reproduced correction-boundary defect remains. |

## Freshness and handoff

Before/after reconciliation matched:

- **534 frozen source/runtime/artifact inputs**
- **1,554 protected entries**
- **1,951 unique pins**, with **zero changes**
- All seven handoff-listed artifacts unchanged

Final source hashes:

```text
measure.py
753fca9e03c7961dab474fcc3536a53c1b48b55dd0382c9cf3cd4ec248e2d859

measure_graph.py
6433ce7fc09f3e6ea60fb274890970bfe3dd48b338367431ce35a849bfc01391

probe.py
668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083
```

The actual binding matched the frozen **Git 2.53.0.windows.4 core plus 69 DLLs**. Live handoff HEAD was `0b7e1a1f6fd1f807bd254886e2877d605596d96d`, on `shbs-microsoft-workflow-app-verification`, with an empty index.

This is not universal Git support or POSIX-runtime verification. The five-file controller copy is not the full executable dependency closure: actual `probe` also imports `mutate`, whose bytes and shared dependencies were pinned. No Q4 stable-controller execution is claimed.

**Parent disposition recommendation:** preserve this full return; hold Q2 admission for the narrow residual R2 correction. Final integrated C1 replay on the resulting shared dependencies and commit-composition checking remain required before combined preservation/C2. Actual complete quality remains Q2–Q5.

No persistent source, test, evidence, shared-state or session-artifact writes; no repairs, nested agents, installations, root quality/mutation, commits or publication. **Bounded handoff complete.**

---

## Parent disposition

Accept the single concrete residual attribute-classification defect. Authorize one
bounded correction of this newly introduced gate, preserving normal no-filter
behavior and explicitly rejecting ambiguous present declarations where necessary.
This is not a new broad convergence cycle. Require qualified Git-native distinction,
the two literal-name regressions, targeted independent replay and narrowed re-review.
No admission of Q2/C2 or complete quality claim follows from the earlier 74 passes.
