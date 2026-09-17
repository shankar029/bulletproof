# Narrowed independent design re-review

Separate read-only code-review agent, reviewing revised measurement design R1-R4.
No implementation, test execution, tool provisioning or quality pass is claimed.

Verbatim result:

> **APPROVE — no residual blocking issues in R1–R4.**
>
> - **R1:** `DirectoryRef` supports root source directories/cwd without weakening file/artifact paths.
> - **R2:** Assertion classification requires the actual raising instruction and qualified origin; ancestor assertion-line membership is explicitly insufficient.
> - **R3:** Producer-owned validation reconstructs raw evidence, completeness, all nine metric comparisons and the outer verdict; hashes or supplied summaries alone cannot establish validity.
> - **R4:** Discovery has one lower-layer owner, and `parse_files` explicitly produces the shared `ParsedInventory`, avoiding the probe import cycle.
>
> **Q1 Python inventory/graph slice is now dispatchable.** Its common validation and graph reconciliation are bounded independently of later adapters; missing metrics remain unavailable and the overall verdict fails closed.
>
> The accepted 100%/100% coverage policy preserves 60% mutation and 0.9 evaluation. External provisioning remains later Q2. This is design acceptance, not implementation verification or a Q pass.

Parent disposition: accepted for Q1 dispatch. The 100% changed executable-line and changed
decision-outcome policy is a new explicit autonomous decision for the finite coverage models
in the Q design, not a claim about an existing repository threshold. Skill-owned provisioning
is authorized only for the qualified Q2 tools; project dependencies and OS configuration are
not changed by that authorization. No missing measurement is waived.
