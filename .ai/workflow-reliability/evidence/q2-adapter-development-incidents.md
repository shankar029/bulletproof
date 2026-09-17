# Q2 local development incidents (not acceptance)

## Initial root implementation run

Command: managed Python `-B scripts/run.py --idle 120 --max 600 --`
managed Python `-B -u -m unittest discover -s scripts/tests -p test_measure_q2.py -v`,
with qualified Git PATH prepended and `PYTHONDONTWRITEBYTECODE=1`.

Observed first run: six methods, 37.033 seconds, exit 1; three unittest failure
records (two are subtests) and two errors. Native dependency validation rejected
historical PE locator spelling `C:\WINDOWS\System32\...` as noncanonical.
No successful Q2 test/collector claim followed.

A read-only managed-Python diagnostic then resolved actual qualified DLL
locators. Windows uses `C:\Windows\System32\...`, including lowercase leaf
spellings. Most observed system DLLs have two native hardlinks (WinSxS servicing);
VCRUNTIME140 has one. The implementation now canonicalizes these *pinned PE
provenance locators*, never Artifact paths, and rehashes the actual external DLL.
Original/staged qualification files still require one link and independent
identities. No system setting, DLL, source tool or original evidence was changed.

## Second run and bounded progress correction

Same test command: six methods, 111.760 seconds, exit 1. Five methods passed;
both actual public-probe subtests timed out in `GitFixture.run` with code 124
and `[idle-timeout]`. The outer progress-visible unittest runner did not time
out. Its child's default 30-second idle budget saw no output during multiple
real validation/materialization/staging stages.

Correction: public configured probe now reports completed configuration,
materialization, staging, collection and reconciliation stages to stderr,
flushed when each actual stage completes. No periodic heartbeat, timeout
increase, helper/runner modification or guessed process cleanup.
The fixture uses the existing bounded runner's process-tree kill path; separate
PID/descendant-death proof was not captured and is not claimed.

One corrected replay of those public-probe cases is permitted. A second timeout
of either corrected case is a blocker, not authorization for repeated retries.
Full Q2 collectors, independent verification and acceptance remain pending.

## Public-probe recovery and filesystem capability

The bounded public-probe replay completed: one method / two actual Git-revision
fixtures passed in 95.524 seconds. No further timeout of those cases occurred.
The next extended root run completed ten methods in 170.009 seconds with one
error: creating an actual directory symlink raised Windows error 1314
(`A required privilege is not held by the client`). The actual junction was
created and its rejection passed before that failure. No privilege/OS change,
symlink retry, mock or skip decorator was used. The persistent symlink test is
now separately named and explicitly environment-blocked.

## Selected regression capture interrupted

`q2-adapter-root-development.py` selected ten root methods plus four existing Q1
regression methods. Thirteen methods printed successful completion, including
both real public-probe fixtures and three Q1 regressions. Their actual report/
graph files remain in `q2-adapter-root-development-records/{repository,external}.json`.
The final existing summary-forgery method performs many actual revalidations
inside subtests without default successful-subtest output. The outer runner
hit its unchanged 120-second idle limit and exited 124. This is a failed run,
not a fourteen-test pass; no completed result.json was reconstructed.

One bounded replay adds unittest.TextTestResult.addSubTest progress in the
development harness: a line is written only after an actual subtest completes.
No suite buffering, heartbeat, runner/helper modification or timeout increase.
The replay uses a new additive evidence directory. A second timeout is a blocker.
The existing runner requested process-tree termination; independent complete
descendant-death proof was not captured and is not claimed.

## Completed bounded replay and final self-review correction

The progress-visible replay completed all fourteen selected methods in
461.432 seconds, exit 0, with no failures/errors/skips. Eleven named input pins
matched before/after that run. One symlink case remains explicitly environment-
blocked and was not retried or counted as a pass. See the actual result and
fixture graph/report records in `q2-adapter-root-development-replay-records`.

Subsequent self-review found an incomplete lexical prefix check: sorting and
checking adjacent paths misses `a` versus `a/b` when `a-b` sorts between them.
The check now tests every component ancestor against the complete name set.
It also explicitly rejects non-string original-root inputs rather than relying
on downstream path/JSON failures. Two focused real methods covering these
corrections passed in 8.379 seconds, exit 0, without errors/skips. This is
fourteen pre-correction methods plus two repeated focused methods, not sixteen
distinct methods or a final-byte full-suite pass. The original fourteen-method
source pins are preserved, not rewritten to claim the later bytes.
