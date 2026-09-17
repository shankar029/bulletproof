# AC10 independent documentation review

**Verdict: REVISE — two bounded documentation corrections.**

Reviewed 2026-09-17. This is an independent source-backed documentation review,
not runtime acceptance, a release-quality verdict, or approval of future work.
The overview is substantially improved: a clear entry point, grouped feature tables,
deep links, a practical user guide, and unusually explicit evidence limitations.

## Required corrections

### R1 — Align the per-project Copilot playbook location with the shipped launcher

- **FACT:** `install/copilot-cli.md:31-32` tells a project-only installer to put
  the playbook in, for example, `docs/bulletproof/`.
- **FACT:** `launchers/copilot/agents/bulletproof.agent.md:7-8` directs the agent
  to `bulletproof/SKILL.md` in the repository, or the global copy at
  `~/.copilot/bulletproof/`. It does not name `docs/bulletproof/SKILL.md`.
- **INFERENCE:** On a project-only installation without the global fallback,
  the documented playbook destination does not match either location explicitly
  supplied by the launcher. Discovery by an agent is not a documented resolution
  mechanism and should not be required to make the example work.
- **Correction:** Use repo-root `bulletproof/` in the per-project example, or
  explicitly instruct the user to update the copied launcher's reference to
  `docs/bulletproof/SKILL.md`. This is a pre-existing issue in a guide included in
  the requested install-example verification, not a new runtime regression.
- **Recheck:** Compare the corrected destination and copied launcher text;
  no installer execution or runtime modification is needed for this correction.

### R2 — Surface the optional `clarity` approval route, separately from code clarity

- **FACT:** README's design/review rows (`README.md:84-85`) and user-guide
  approval section (`docs/user-guide.md:63-78`) describe the shared HTML review
  layer. README also covers human-readable code at line 94.
- **FACT:** `references/ux-design.md:80-95` separately documents the optional
  `clarity` skill: structured web approval, comments/uploads, and a terminal or
  plan-document approval fallback when it is unavailable.
- **INFERENCE:** The requested feature coverage names clarity, but the new
  overview/user guide does not introduce this optional integration or distinguish
  it from the bundled HTML artifact review UI. Code clarity is covered; the
  optional approval integration is not discoverable by name from either entry point.
- **Correction:** Add a short sentence in the approval section and/or design
  feature row linking to that procedure. Say it is optional and separately
  available, not bundled or installed by the Bulletproof installers; retain
  the normal approval fallback. Do not advertise it as automatic human approval.
- **Recheck:** Verify the new relative fragment, wording, and affected preview.

## Accepted coverage and source support

These are **FACTS about inspected documentation/source**, not claims that an
agent executed these procedures successfully:

| Coverage | Inspected authority and finding |
|---|---|
| Six phases and short path | `SKILL.md` describes ordered gates and a trivial short path; README accurately presents the high-level loop without promising success. |
| Research and uncertainty | `references/research.md`, investigation steps 1–5 and operating boundaries: AC-scoped research, actual definitions/callers, reuse and evidence, independent handoff, facts versus inference. |
| Diagnosis | `references/diagnosis.md`, sections 1–4: symptom-specific reproduction, optional minimization, discriminating experiments, original and minimized rechecks. |
| Program/UX design and HTML review | `references/design-doc.md`, hard rules; `references/html-theme.md`, reader features and handoff; `references/ux-design.md`; `assets/artifact.js:365-398` supplies the named decisions and JSON controls. Optional clarity gap is R2. |
| Executable planning, compatibility and handoff | `references/planning.md:30-134`: stable tasks/checks, prerequisites, owners, evidence, expand/migrate/contract, explicit pending proof and human acceptance. |
| Test-first and real E2E | `references/testing-and-e2e.md`: behavioral red/green, independent expectations, real seams, browser/HTTP/CLI/library surfaces. Setup failure is explicitly not behavioral-red proof. |
| Code clarity and communication | `references/code-clarity.md` and `references/communication.md`: readable main flows and current rationale; outcome-first updates without suppressing complete evidence or blockers. |
| Independent roles and parallel work | `references/delegation.md`, capability ladder and rules; `references/parallel-execution.md`: mandatory independent research/verification/review, optional fallback only for other roles, isolated file-disjoint implementation and integrated verification. Host limits are stated rather than concealed. |
| Durable workspaces and final reports | `references/workspace.md`, layout/resume protocol; `references/final-report.md`, rules/structure: current state, traceability, delivered/unmet work, gates, missing proof, assumptions and publication status. |
| Quality completeness | `references/quality-metrics.md`; `scripts/probe.py:437-465,628-668`: required proof and measured status are separate; unavailable collectors remain missing; incomplete means fail; immutable run report plus display alias. |
| Native mutation and source binding | `scripts/probe.py:310-374`; `scripts/mutate.py:482-565,650-674`: current invocation, source inventory/hash and restoration checks, exact command/cwd, native-runner baseline, unsupported/ungraded status, dirty-tree refusal and no latest mutation alias. The README's restricted native-Node and unsupported-input caveats are appropriate. |
| Bounded runner | `scripts/run.py:1-100`: idle/max options, captured subprocess output, PID/process-group cleanup with best-effort error handling. The user guide correctly does not promise that a dead parent proves child cleanup. |
| App scale and production | `references/app-scale-delivery.md`, opening sections: walking skeleton and feature slices; `references/production-readiness.md`, applicability/plan rules: relevant operational and rollout checks, not a universal checklist for every change. |
| Packaging and host installation | Both installer sources and all three launcher files were read. Target names, global destinations, copied payloads, `main` default, remote ref and local source variables match the examples. R1 concerns the separate manual project-only example. |
| Evaluations and limits | `evals/README.md`, `evals/agent/README.md`, `benchmark/README.md`; direct directory count confirms ten task directories. New overview distinguishes fixed fixtures, live harness and illustrative observation; it makes no universal success or model-gain claim. |

Most features are explicitly presented as procedures; the runner, measurement
tools and HTML UI are executable support; host permissions, delegation and
approval remain host/human capabilities. No future workflow guard is advertised
as currently verified in these README claims.

Minor wording suggestion, not a separate blocker: “up to three printed pages”
would track `references/design-doc.md:25` more precisely than “Three-page HTML
overviews” at `README.md:85`.

## Checks actually executed

- Read all seven scoped Markdown files and the banner; architecture acceptance
  is limited to the changed introduction/component/launcher wording, not an
  audit of every historical architecture claim.
- Ran a read-only Python standard-library link/fragment/XML/hash check through
  the managed Python executable and `scripts/run.py --idle 30 --max 90`.
  **Exit 0.** No dependency installation or test suite execution.
- Checked **84 local link/image occurrences across seven Markdown files**:
  README 47; user guide 16; CONTRIBUTING 10; pi 1; Claude 1; Copilot 1;
  architecture 8. **Five fragment occurrences; zero missing paths/fragments.**
  This count includes repeated Markdown destinations and HTML href/src values,
  excludes fenced code and external URLs, and is not a count of unique links
  or browser clicks. Fragment checking used heading-derived IDs for these
  observed targets, not a general GitHub-renderer conformance test.
- Banner SVG parses as XML. Its source contains accessible title/description
  and the README image has descriptive alt text.
- `git diff --check` on the six tracked changed Markdown files exited 0.
  This command does not cover the untracked user guide or banner.
- Read the supplied `documentation-rendering.json`, including its diagnostic
  command records. Its four observations report marked 18.0.12, **local
  GitHub-like preview, not github.com**, at 1280/light and 390/dark; reported
  scroll widths equal viewport widths. Parent-recorded link counts are 38 and
  14 under its different counting method, not the occurrence method above.
- Independently hashed the README and user guide; **both match all corresponding
  preview records**. Inspected the narrow/dark user-guide screenshot returned
  by the image tool: visible title, links, readable prose and command block.
  The other three image requests hit the tool's image limit and were not
  visually inspected. The returned image is a viewport, not proof of the
  whole page's visual quality.

## Reviewed content hashes

SHA-256 of the scoped content at review:

```text
README.md                         608f2805659f64a9d7504b38c8f581871ac09e64156ce9cffc6b5070d0730a4f
docs/user-guide.md                50628875d6c9d8a93740126369f1794ba4d88fecc4373261e34994f23a2c6945
CONTRIBUTING.md                   f2afb5b5ac7a4c8c0f6c826011b738cbc4a2a16e22033f09ba1e9c94f77f24cf
install/pi.md                     44741c04b2af43efe350a0563e750a528d5fd9ae11a856b88d60982c32180d54
install/claude-code.md            a9ac92b017759a8167c73c3aa93b12405a6526968ece53226f538abf6a8cd5ed
install/copilot-cli.md            ba2ef48aa465b896a7987947a8dd30186bcb99faba767a6e92179853844a4abb
docs/architecture.md              c45bd3726a4415150c1da882483e62ea49d28f61f2c9e83778d3f93198953d0d
assets/bulletproof-banner.svg     d8c9cb127953f4393aef14c9cf1058c9559cbeb47ab1bf595aacd85e22958d03
```

## Limits and handoff

No browser was launched by this reviewer; parent-recorded rendering results are
not represented as independent execution. No actual GitHub rendering, remote
URL availability, host CLI compatibility matrix, installer execution, full
tests, mutation/probe execution, or production runtime acceptance was performed.
Static source checks support documentation semantics, not new runtime guarantees.

No nested agents, installs, production/code/document edits, main-checkout
operations, commits or publication. This review file is the only intended write.
Concurrent C1 `workflow_state`/gate production files were not inspected.
Future guard/operator-guide/C3 documentation remains **pending and unverified**.
The parent owns corrections, any required preview refresh and final AC10
acceptance. Stop after this bounded review.
