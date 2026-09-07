# Task for delegate

Working directory is /tmp/shopcart (a git repo, branch feat/loyalty-tiers). Read the skill reference at C:/code/projects/bulletproof/references/research.md FIRST and follow it exactly.

Then produce /tmp/shopcart/.ai/promo-stacking/research.md describing what exists today that bears on this requirement:

  "Allow multiple promo codes to be stacked on one cart, with a configurable cap on combined discount."

Rules that matter most:
- Every claim about the codebase carries path:line AND the snippet it rests on. No citation, no claim.
- Every "not implemented" carries the actual search command you ran that came up empty, with its scope.
- Head the file with the current commit sha.
- Cover only what the requirement touches or is constrained by. Aim for two pages.
- Do NOT propose a solution, approach or file layout. Do NOT edit any source file.

Reply with a five-line summary and the path.

## Acceptance Contract
Acceptance level: attested
Completion is not accepted from prose alone. End with a structured acceptance report.

Criteria:
- criterion-1: Return concrete findings with file paths and severity when applicable

Required evidence: review-findings, residual-risks

Finish with a fenced JSON block tagged `acceptance-report` in this shape:
Use empty arrays when no items apply; array fields contain strings unless object entries are shown.
`criteriaSatisfied[].status` must be exactly one of: satisfied, not-satisfied, not-applicable.
`commandsRun[].result` must be exactly one of: passed, failed, not-run.
`manualNotes` and `notes` are optional strings; an empty string means no note and does not satisfy `manual-notes` evidence.
```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "specific proof"
    }
  ],
  "changedFiles": [
    "src/file.ts"
  ],
  "testsAddedOrUpdated": [
    "test/file.test.ts"
  ],
  "commandsRun": [
    {
      "command": "command",
      "result": "passed",
      "summary": "short result"
    }
  ],
  "validationOutput": [
    "validation output or concise summary"
  ],
  "residualRisks": [
    "none"
  ],
  "noStagedFiles": true,
  "diffSummary": "short description of the diff",
  "reviewFindings": [
    "blocker: file.ts:12 - issue found, or no blockers"
  ],
  "manualNotes": "anything else the parent should know"
}
```