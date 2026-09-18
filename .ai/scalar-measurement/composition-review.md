# Narrow composition design review

Fresh read-only reviewer `scalar-composition-design-review` reviewed
composition-amendment.md against the actual imported JS checkpoint,
interfaces.md, native request contract and accepted scalar contracts.

Verdict: **APPROVE - design only.**

> No significant issues found in the reviewed changes. Parent must explicitly
> release ownership before wiring; this result does not authorize code changes.
> Native measure_js.mjs must remain byte-immutable. Implementation and executable
> proof remain pending; no tests were run.

Parent ownership release is still required. This review is not acceptance of
collect/validate_evidence, raw reconciliation or integrated scalar measurements.

## Narrow location addendum and release

Parent explicitly authorized a different fresh read-only context because the
original synchronous reviewer cannot be resumed. Reviewer
`77ac2243-615c-4464-bb8b-e782bcd90f5d` returned **APPROVE - narrow
location-projection amendment only**. This does not replace the original review.
The reviewer confirmed native SourceBytes.range permits zero width while span
does not, and required projection/round-trip, independent location-identity
mutations, no permissive null fallback, Unicode/CRLF/EOF fidelity, exact counts,
and unchanged syntax/mutation nonempty-span constraints. These tests are pending.

Parent's conditional wiring release is now satisfied: implement the reviewed
composition and location delta without another permission loop. Native producer
bytes and six-file native controller boundary remain immutable.
