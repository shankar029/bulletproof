# Narrow baseline-materialization review

Original return from `1b351703-5886-4edc-8cf8-1058ef536fb2`.
Reviewed proposal SHA-256:
`6a3e9976a799753462eb7f88c58d3b726f3364611f8d2831e6e23d8cb58ef5ee`.

## APPROVE — narrow baseline-materialization policy

The selected **`isolated-versioned-attribute-checkout-v1`** policy is a sufficient and feasible clarification of R2. No required design revision or new Context field is identified.

I read:
- `evidence/q1-review-correction-boundary.md`
- `baseline-materialization-contract.json`, revision 1

### Why this closes the design gap

- **The baseline authority becomes the selected immutable Git tree**, independently materialized—not the supplied index, Git status, or freshly fingerprinted working files. Thus `assume-unchanged`, `skip-worktree`, and altered index contents cannot legitimize R2’s corrupted baseline.
- **The byte representation is now explicit.** Neutral LF defaults plus qualified, versioned built-in attributes support legitimate checkout representations without requiring raw-blob equality.
- **Byte identity is not weakened:** the supplied baseline must match the independently expected bytes exactly. Normalizing the supplied files, running clean filters over them, or comparing only normalized hashes would not satisfy this policy.
- **Source coverage remains intact.** “Complete relevant path set” must retain the existing subject/source scope, including applicable non-code contracts and analyzer-excluded inputs. This amendment does not authorize new exclusions or a code-only comparison.
- **Platform mode limits are honest.** Recording immutable tree modes and the explicit Windows projection is appropriate; it does not pretend ordinary Windows worktree bits establish POSIX executable identity or Q4 execution proof.

### Feasibility and implementation preconditions

Git can supply tree/index-based attribute interpretation without first executing a checkout transformation. Therefore, rejecting external filters before materialization does not require a handwritten attributes parser. **The concrete commands and installed-Git behavior remain unqualified by this review** and must be demonstrated before implementation relies on them.

The implementation must preserve these requirements already present in the contract:

1. Resolve the selected tree without replacement semantics; derive attributes from that tree in the isolated environment.
2. Reject applicable external filters **before the first operation capable of invoking them**. The sentinel control must establish nonexecution, not merely eventual rejection.
3. Qualify supported built-in transformations—including their attribute precedence and neutral defaults—or reject them explicitly. Do not silently ignore an unsupported transformation.
4. Compare expected and supplied path sets, bytes, regular-file types and representable modes independently of caller index flags. Apply the same materialization policy in CLI creation and common validation.
5. Bind the actual policy implementation and qualified Git identity into the existing controller/tool evidence and its validation. An unvalidated policy-name field is insufficient. If implementation introduces another module, its real dependency must not disappear from the controller binding.
6. Keep all derivation resources privately owned and cleaned; do not modify the supplied repository, index or configuration.

These are implementation/qualification obligations, **not additional design revisions**.

The owner’s distinction concerning R1 is also correct: the native demonstration established the **dot alias**; it did not establish equivalent native behavior for the space alias. Both accepted configuration aliases still require correction.

**Disposition:** parent may authorize the bounded R1/R2 correction under this policy. Human approval remains unconfirmed. This approval is **not** acceptance of the eventual implementation, Q1 code approval, Q2 admission, or a quality pass. No persistent writes or command qualification were performed in this adjudication.

---

## Parent disposition

Accept the independent boundary review and authorize the existing Q1 owner to
qualify the actual installed Git operations, then implement R1/R2 without weakening
the stated conditions. Policy semantics remain unchanged; only approval metadata
in the proposal is updated. The previous proposal hash above identifies what was
reviewed. Preserve all pre-fix failures, require independent execution verification
and separate correction review, and keep Q2/release blocked until their due gates.
