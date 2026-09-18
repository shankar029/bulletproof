# Decisions and authorization

User explicitly requested autonomous execution without waiting for design/UX approval.
Human approval remains **unconfirmed**, not received.

Execution-mode decision, 2026-09-18: coordinator explicitly authorizes unadopted procedural
implementation after verifying no live authority/admissions. Use ordinary apply_patch edits
and bounded test commands; all results are unbound procedural evidence, not receipts.
Unsupported guarded candidates are parked. This authorizes no runtime changes and does not
waive independent verification/review or claim a passed G6 metrics gate.

- CSV exports every task in the project, independent of active UI filters/pagination. Stable ascending createdOrder; fixed headers; UTF-8 without BOM; CRLF record separators; quote every cell and double embedded quotes. Dependencies use JSON array text. Include projectId, projectName, id, title, description, status, priority, dependencyIds, blocked, createdOrder. Prefix text cells with an apostrophe when the first non-whitespace/control character is =, +, -, or @, or when the cell begins with tab/CR/LF. No mutation of stored data.
- Archive means project lifecycle, not snapshot backup. No task-status prerequisite. Repeated archive/restore with the current revision is an idempotent no-op.
- Default project navigation is active-only; explicit archive navigation is separate. Global task queries/dashboard retain existing inclusive semantics; document that choice.
- Preserve v1 read-only migration behavior. Prefer an optional, strictly boolean archived field on v2 projects; absent means active. Do not automatically rewrite existing snapshots on read. Existing older binaries need not read newly archived snapshots; old snapshots must remain usable by the updated app.
- Archive/restore uses existing global revision checks. Stale revision errors retain precedence. Authoritative archived check occurs inside the serialized store transaction before task mutation/allocation, including no-op writes.
- No deployment or framework change. Do not push or create a PR; publication is already policy-blocked per user.
