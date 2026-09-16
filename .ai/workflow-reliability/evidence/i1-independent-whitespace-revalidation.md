# Artifact whitespace revalidation

Read the parent's formatting correction:

```gitattributes
* -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol
```

`.ai/workflow-reliability/.gitattributes` SHA-256:
`1fd44f434ed6352c44f6833a238f193e9a1336ad9d319622eabbcc1913a1bde9`.

The rule retains byte-exact `-text`, explicitly retains the three default whitespace
checks, and recognizes CR as part of a CRLF line ending. No command-line whitespace
override, normalization, or suppression was applied by the verifier.

Fresh ordinary checks, under the supplied bounded runner:

| Command | Exit | Result |
|---|---|---|
| `git --no-pager diff --check` | **0** | No whitespace diagnostics |
| `git --no-pager diff --check bcc971d3b64559127dfc43eb0bfd4348c42803ca` | **0** | No whitespace diagnostics |

Both emit only the separate informational warning that Git may convert `evals/report.md`
LF to CRLF when it next touches that file. Exact argv/cwd/environment/timing and raw output
are in `i1-independent-diff-check-working.{json,log}` and
`i1-independent-diff-check-attributes.{json,log}`.

All eight production/test hashes checked against the final schema-verification manifest
remain unchanged. These diff checks do not include untracked file contents; they are not
a replacement for the recorded test runs.

**F2 is resolved on this attribute configuration.** The earlier exit-2/1,601-diagnostic
record is retained unchanged as historical evidence, not silently relabeled passing.
The attribute edit changes the wider artifact snapshot, so prior probe hashes are not
claimed to bind this new metadata state. No fresh quality measurement is implied by
these whitespace checks.

Overall I1 closure remains blocked by F1's parent evidence-scope freshness defect,
required incomplete quality proof, and pending separate review. No production code,
tests, raw evidence bytes, commit, or publication were changed/performed by the verifier
in this formatting-only revalidation.
