# Ordinary CLI: bounded metric-producer identity question

**Stopped before production edits at the requested producer-interface check.**
This is an implementation-role finding, not a design review, independent
verification, regression result or overall C2 completion.

Accepted HEAD observed: `ee6e0e34e78b70fcb672074af0a76f51fe937e1a`.
State is the accepted `fe30290e...b57a6e`; r2 contract is
`80442414...0b949d`. The state-seam recovery of prior test capture is accepted;
neither historical timeout nor long-TEMP failure is reopened.

## Exact source conflict

FACT at the bounded observed `probe.py` SHA-256
`668042417c42b7aa457a695ffa8782845d18b9834c1937f17e277190cc0bb083`:

- `scripts/probe.py:515` (`_execute_configured`) and `:628` (`main` ordinary
  path) independently allocate `run_id = uuid.uuid4().hex`.
- Its argument definitions at `:586-595` expose no `--run-id`; these paths
  do not consume an externally supplied admission ID.
- `scripts/workflow_gate.py:106-111`, `_metric_result`, requires
  `result["run_id"] == receipt["run_id"]`. The receipt's run must match an
  earlier admission (`_receipt:296-305`), persisted before executing the
  producer. Source equality and the remaining numeric/artifact checks are
  additional requirements, not substitutes for this ID equality.
- Original `design-contracts.json` requires a metrics check to rerun the
  producer after admission with the same run ID. R2 preserves that existing
  guarded receipt policy, all schemas, registered-command boundary and
  no historical import. It does not define a producer-ID/admission-ID mapping.

INFERENCE: the present probe entry point cannot emit a matching admitted
MetricVerdict on either path through a supported invocation. Learning its UUID
after execution and assigning it to a new admission would backfill admission;
replacing the report ID would rewrite producer provenance. Intercepting uuid,
patching producer internals or loosening the gate is not an acceptable adapter.

This is **not** a claim that status, work, nonmetric checks, finite adoption or
missing-metric denial are impossible. Nor is it a reason to cancel the Q2
owner. It is a separate limitation of successful strict metric attachment,
even after collectors become available. The existing unavailable-quality
closure limitation does not by itself specify whether that producer attachment
is also intentionally deferred in ordinary-v1.

## Executed API evidence

Two actual parser invocations, under managed Python with `-B`,
`PYTHONDONTWRITEBYTECODE=1`, outer `scripts/run.py --idle 120 --max 600`,
streamed immediately through PowerShell Tee-Object:

1. `probe.py --help`: exit **0**, no run-ID option.
2. `probe.py --slug c2-cli-interface --run-id c2-cli-admission`: exit **2**,
   `probe.py: error: unrecognized arguments: --run-id`.

The second exits during argument parsing. No root metric collection, mutation,
Git fixture, producer report or CLI proof was attempted.

Artifacts:

- `c2-cli-probe-help01.txt`: help output.
- `c2-cli-probe-runid01.txt`: parser rejection.
- `c2-cli-probe-api01.json`: literal complete argv/cwd, exits, managed runtime
  path, timestamps and four before/after hashes (all matched during these
  invocations).

There was no buffered capturer, timeout, retry, process kill, install, agent,
production/test edit, commit or push. **CLI/native test passes: zero, not run.**
Q2 is authorized to change its disjoint files; these limited pins are not a
claim that all imports or future Q2 bytes remain unchanged.

## Narrow decision needed

Recommended bounded direction: explicitly classify **successful guarded probe
attachment** as an additional unavailable producer prerequisite for ordinary-v1,
while implementing actual probe failure capture and fail-closed metric/close
denial. Then independently authorize its producer-owner follow-up to support a
pre-admitted identity, source binding and raw-output validation contract before
any successful metric attachment is claimed.

Alternatively authorize that small producer seam now through its existing
owner. CLI must not unilaterally modify `probe.py`, replace its UUID, infer
admission from completion, or accept summary-score JSON as producer validation.
An optional producer run-ID input alone is necessary for this approach but does
not settle source/projection/raw-validator integration; those checks stay due.

No broader recovery/platform/design round is requested. The five-verb parser,
finite adoption table, receipt execution, native failures and guide remain
unimplemented in this return. The parent can resolve this exact support-boundary
question without changing the accepted state/gate seams or reducing quality bars.
