# Post-verification documentation re-anchor

FACT: inspected `references/quality-metrics.md:154–157`. Its explanation of canonical
native discovery and candidate/native/result/counter reconciliation agrees with the
R1/R2 behavior independently exercised in `i1-independent-review-fixes-verification.md`.

| Input | Observed SHA-256 |
|---|---|
| Current `references/quality-metrics.md` | `cec506cd8be2fb54794eddd1b914a64cf2269b21e31d969c7dcbc9d874f6e161` |
| Same path in initial `i1-independent-before.json` | `a6f862ff1da39bac199f4b9577282de35a7a3ac5998a12508e8d39ad2c5efe2c` |
| Current `design-contracts.json` | `5b3eb1ac8f4ad0e8914965a783d97242da7ba9e8da00229b622a8360578335bf` |

FACT: independently recomputed all **98 inputs** in
`i1-independent-review-fixes-final-manifest.json`; **zero changed hashes**. The
documentation path was recorded in the initial broad snapshot, not the final 98-input
execution manifest, so this supplemental record anchors it explicitly.

Hash validation ran from the assigned worktree with the supplied Python 3.14.2 under
`-B scripts/run.py --idle 120 --max 900 --`, exit 0. It loaded both recorded manifests
and compared SHA-256 of current file bytes; it did not rely on timestamps or parent
implementation claims.

No production/test changes or further suite replay were needed for this observed
documentation clarification. The previous functional verdicts stand. This note does
not refresh the archived actual probe's scope or change its incomplete/fail result.
Separate re-review remains pending; I1.T4 stays blocked and I2 stays pending.
