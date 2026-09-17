# Q1 read-only review: REVISE

Original return from `1b351703-5886-4edc-8cf8-1058ef536fb2`.
Parent disposition follows the preserved return.

**Two reproduced correctness findings block bounded Q1 acceptance and Q2 admission.** The original F1/F2/F3 corrections remain accepted on their tested boundaries. Neither new counterexample produces an overall green report: seven missing metrics still force incomplete/fail. However, individual graph comparisons are incorrectly accepted as measured/ok.

No persistent source, test, evidence, shared-state or session-artifact writes were made. Private fixtures were cleaned. No installations, agents, root mutation, publication or authentication retries occurred.

## Findings

### R1 — High / P1 / SPEC: Accepted Windows directory aliases hide local dependencies

**Locations**
- `scripts/measure_graph.py:64–75` — `input_path`
- `scripts/measure.py:235–239` — source-root validation
- `scripts/measure_graph.py:197–207` — lexical module-candidate construction

`input_path` checks containment after resolution but returns the original spelling without rejecting filesystem aliases. On this Windows host, both `scripts.` and `scripts ` resolve to the existing `scripts` directory and pass configuration validation.

The resolver subsequently constructs literal prefixes such as `scripts./`. Those do not match the canonical inventory paths under `scripts/`. Consequently, real local dependencies become “external” terminals without an unresolved diagnostic.

**Reproduced through the public configured CLI**

Source:

```python
# scripts/a.py
import b
VALUE = 1

# scripts/b.py
import a
VALUE = 2
```

A real native interpreter with `sys.path.insert(0, "scripts.")` imports both files and confirms their mutual references.

| Configured source root | Head cycles | Comparison | Resolution of both imports | Unresolved |
|---|---:|---|---|---|
| `scripts` | 1 | measured/fail | local | none |
| `scripts.` | 0 | **measured/ok** | external | none |
| `scripts ` | 0 | **measured/ok** | external | none |

All three probe invocations exit 1 with seven missing metrics. Raw reconstruction accepts the incorrect alias cases because it repeats the same resolution algorithm.

This violates the explicit canonical-path/alias rejection contract and the completeness claim for literal local imports. It can also remove edges needed by architecture reachability checks; the directly reproduced incorrect metric was cycles.

**Minimal fix:** enforce canonical, unaliased relative spellings at the shared path boundary, including directory components. Do not merely check that the resolved path stays inside the root. Preserve `"."` only for directory fields. Ensure accepted source-root spellings correspond to the canonical inventory representation, and add real Windows public-CLI regressions for the demonstrated aliases.

### R2 — High / P1 / SPEC: Clean Git status does not establish an immutable baseline

**Location:** `scripts/measure.py:373–379`, followed by inventory reconstruction at `:392–394`.

The validator verifies the base repository’s HEAD and uses `git status` to establish that its working files represent the immutable Git tree. Git status respects `assume-unchanged`, so this is insufficient.

**Reproduced using fresh, producer-generated evidence**

1. Committed baseline: no cycle.
2. Committed head: `a.py → b.py → a.py`.
3. The genuine report correctly measures base 0, head 1, with a new cycle identity and comparison fail.
4. In the privately owned **base subject only**, set:
   ```text
   git update-index --assume-unchanged a.py b.py
   ```
5. Replace its two working files with the head’s cyclic contents.
6. Recollect inventories, syntax, graph, observations and manifest through the real producers, retaining the canonical committed changed-line map.
7. Call `probe.validate_measurement_report`.

**Observed result**

- `git show <base>:a.py`: `value = 1`
- Actual base-subject `a.py`: `import b`
- Validator’s exact Git status command: exit 0, empty output.
- Public report validator: **accepts**.
- Cycle comparison changes from:
  - genuine: base 0 / head 1 / **fail**, one new ID;
  - corrupted baseline: base 1 / head 1 / **measured/ok**, no new IDs.

The outer report remains incomplete/fail because seven other metrics are missing.

This is a common validation-boundary defect for supplied Contexts, **not an observed defect in the normal CLI’s clone/copy materialization**. It is distinct from the corrected hardlink issue: these files occupy independent storage.

**Minimal fix:** establish baseline content and relevant modes against the selected immutable Git tree, using an explicit materialization/filter policy. Do not infer content identity solely from index/status cleanliness. Reject or neutralize index mechanisms that conceal worktree differences, and retain the fresh-recollection regression so stale-proof rejection cannot masquerade as the fix.

## Original correction assessment

| Correction | Review verdict | Basis |
|---|---|---|
| **F1 — builtin/frozen precedence** | **Accepted, bounded** | Runtime finders now precede filesystem candidates. Shadowable and relative-name controls remain intact. |
| **F2 — cross-root physical aliases** | **Accepted, bounded** | Actual `(st_dev, st_ino)` checks cover code, non-code, controller and artifact files across roots. Equal-content independent copies remain valid. This is an observation, not an atomic filesystem lease. |
| **F3 — effective frozen-module fingerprint** | **Accepted on managed CPython 3.14.2** | The fingerprint binds the effective complete frozen-name census and availability/package classification rather than raw environment settings. Ten actual interpreter modes passed again. Private API unavailability remains explicitly fail-closed; no general Python implementation support is inferred. |

I directly replayed **6 focused tests in 118.575 seconds: all passed**, including the ten-mode test and physical-alias controls. These six are not additional independent cases to add to the prior 61-test total.

## Structural and evidence reconciliation

- **Discovery ownership:** `measure` owns the census; `probe.code_files` is the same imported function. Tests/examples/benchmarks remain inventoried. Existing analyzer exclusions do not become blanket broad-source exclusions.
- **Actual dependencies:**
  `probe → measure, measure_graph, mutate, evidence, run`;
  `measure → measure_graph, evidence, run`;
  `measure_graph → evidence`;
  `mutate → evidence, run`.
  `evidence` and `run` have standard-library imports. No reverse measurement-to-guard import was found in the reviewed modules.
- **Controller qualification:** the five-file controller copy/hash is not the complete executable dependency closure of `probe`, which also imports `mutate`. Q1 continues executing from the original process; I do **not** treat that copy as proof of Q4 stable-controller execution or self-mutation isolation. The relevant actual dependencies were included in this review’s freshness checks.
- **Raw validation:** source reparsing and exact reconstructed-record comparisons reject ordinary receipt, graph, syntax and summary substitutions. R2 demonstrates that reconstruction still needs a trustworthy immutable baseline.
- **Graph semantics:** directed cycle identities and prohibited-relation identities are compared, not merely aggregate totals. Enumeration bounds fail closed rather than publishing a truncated passing count. Computed imports, reflection and runtime commands are not resolved runtime dependency proof.
- **Incomplete support:** JS/MJS/CJS remain visible and unsupported in Q1. No scalar, coverage or mixed-mutation success adapter was fabricated. The configured path retains all nine requirements; legacy native mutation remains a separate path.
- **Output ownership:** the normal configured CLI reserves individual output paths and retains unrelated source/evidence inputs. This does not cure R1’s input-path canonicalization defect.

## Check and AC verdicts

| Scope | Verdict |
|---|---|
| **CHECK-INVENTORY** | **NOT-VERIFIED overall:** census/receipt retention is supported, but canonical input-path acceptance fails R1. |
| **CHECK-GRAPH** | **NOT-VERIFIED:** R1 hides a real local cycle while reporting complete measured graph proof. |
| **CHECK-PARTIAL-PROBE** | **VERIFIED-WITH-LIMITATIONS:** exact required set and incomplete/fail behavior hold, including in the new counterexamples. This does not validate their graph numbers. |
| **CHECK-RECONCILE** | **NOT-VERIFIED:** R2 accepts baseline bytes inconsistent with the bound immutable Git revision. |
| **AC01** | **VERIFIED-WITH-LIMITATIONS** for scoped inventory visibility and preserved legacy/native behavior; not acceptance of future mixed-language mutation. |
| **AC02** | **NOT-VERIFIED for Q1 acceptance:** missing-as-fail works, but accepted measured comparisons can be incorrect. |
| **AC09** | **NOT-VERIFIED for Q1 acceptance:** prior regressions and original corrections remain supported; newly reproduced defects require correction and independent replay. |

**Q2 admission recommendation: HOLD.** Return R1/R2 for bounded correction, preserved regressions, independent verification and narrowed re-review. Do not require unrelated C1/C2/coverage/host functionality to close these Q1 findings.

**Actual full required quality remains blocked regardless of eventual bounded Q1 approval.**

## Freshness and execution scope

Observed HEAD remained:

```text
0b7e1a1f6fd1f807bd254886e2877d605596d96d
```

Relevant tracked and untracked source was read in full, not inferred from the tracked diff.

Before/after checks matched **325 verifier-frozen inputs**, including the **322 owner-frozen inputs**. Final checks also confirmed **382 protected historical files unchanged** and **28 recorded raw streams matching their hashes**. No `run.py` drift occurred.

| File | Final SHA-256 |
|---|---|
| `scripts/measure.py` | `44151bb17de01576687191b5e5c6872ac37f409419639265b7c9fd0ebf9290d8` |
| `scripts/measure_graph.py` | `b8ef51ae7ecb2e900808187f32766c2dd8c5948ce0db3f5681221483ca92e061` |
| `scripts/probe.py` | `bf2bf37f6a2b329e9b673cda41f6c415396e78a38e082661970350b4b54b6b6e` |
| `scripts/run.py` | `5f41967d4d541effda91adafb1fbfe8434e1e38f5234481f8a0eeb7d8564fdd6` |

The existing r3 **42 Q1 + 19 probe** result remains historical execution evidence on these matching inputs; I did not rerun the full suite. Historical `metrics.json` was not treated as current Q proof. These checks are not an OS-wide dependency closure or whole-repository freeze.

## Exact reproductions

Run from the repository root. Both use only cleaned private fixtures.

### R1: public CLI alias counterexample

```powershell
$py = 'C:\Users\shbs\AppData\Roaming\uv\python\cpython-3.14.2-windows-x86_64-none\python.exe'
$env:PYTHONDONTWRITEBYTECODE='1'
$code = @'
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('scripts/tests').resolve()))
from test_measure_inventory import Q1Fixture
from helpers import SCRIPTS
import measure,measure_graph as graph
f=Q1Fixture()
try:
 f.config['python_source_roots']=['scripts']; f.save_config()
 f.git.write('scripts/a.py','import b\nVALUE = 1\n')
 f.git.write('scripts/b.py','import a\nVALUE = 2\n')
 f.git.commit('fixture: local cycle')
 native="import sys,json; sys.path.insert(0,'scripts.'); import a,b; print(json.dumps({'a':a.__file__,'b':b.__file__,'cross_imports':a.b is b and b.a is a}))"
 rc,out,err=f.git.run(sys.executable,'-B','-S','-c',native)
 print('NATIVE',rc,out.strip())
 for root,slug in [('scripts','canonical'),('scripts.','dot-alias'),('scripts ','space-alias')]:
  f.config['python_source_roots']=[root]; f.save_config()
  measure.validate_config(f.config,f.git.root)
  args=[sys.executable,'-B',str(SCRIPTS/'probe.py'),'--repo',str(f.git.root),'--slug',slug,'--base',f.base_sha,'--skip-mutation','--measurement-config',str(f.git.root/'measurement.json')]
  rc,out,err=f.git.run(*args,expected=1,timeout=180)
  r=json.loads(out); g=r['parsed']['head']['graph']
  print(json.dumps({'source_root':root,'exit':rc,'cycles':r['metrics']['cycles'],'unresolved':g['unresolved'],'script_edges':[e for e in g['edges'] if e['from'].startswith('scripts/')],'missing':len(r['missing_required']),'verdict':r['verdict']}))
finally:
 f.close()
'@
& $py -B scripts\run.py --idle 120 --max 1200 -- $py -B -c $code
```

Observed outer exit: **0**; the three inner probe exits were **1**, with the incorrect measured/ok alias results shown above.

### R2: fresh baseline corruption masks a new cycle

```powershell
$code = @'
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('scripts/tests').resolve()))
from test_measure_inventory import Q1Fixture
from evidence import source_snapshot
import measure,measure_graph as graph,probe
f=Q1Fixture()
try:
 f.git.write('a.py','import b\n'); f.git.write('b.py','import a\n'); f.build()
 print('CONTROL',json.dumps(f.summary()['metrics']['cycles']))
 base=Path(f.context['base_root']); head=Path(f.context['head_root'])
 f.git.run('git','update-index','--assume-unchanged','a.py','b.py',cwd=base)
 for name in ['a.py','b.py']: (base/name).write_bytes((head/name).read_bytes())
 print('BASE_GIT',f.git.run('git','show',f.base_sha+':a.py',cwd=base)[1].strip())
 print('BASE_ACTUAL',(base/'a.py').read_text().strip())
 print('STATUS',repr(f.git.run('git','status','--porcelain','--untracked-files=all','--ignored=matching',cwd=base)[1]))
 raw=f.root/'fresh-review-raw'; raw.mkdir(); f.context['run_root']=str(raw)
 changes={name:sorted(lines) for name,lines in probe.changed_lines(head,f.base_sha).items()}
 f.base=graph.parse_files(f.context,measure.inventory(f.context,'base',{}),f.config)
 f.head=graph.parse_files(f.context,measure.inventory(f.context,'head',changes),f.config)
 pairs=measure.collect_pair(f.context,f.config,f.base,f.head)
 f.observations=[item for pair in pairs.values() for item in pair]
 f.manifest=measure.make_manifest(f.context,f.base,f.head)
 f.context['output_manifest']=graph.persist(f.context,'manifest.json',f.manifest)
 report=probe._configured_report(f.context,f.base,f.head,f.config,f.manifest,f.observations,'review',f.base_sha,[])
 probe.validate_measurement_report(report,f.context,f.base,f.head,f.config,f.policy,f.manifest)
 print('ACCEPTED',json.dumps({'cycles':report['metrics']['cycles'],'verdict':report['verdict'],'missing':len(report['missing_required'])}))
finally: f.close()
'@
& $py -B scripts\run.py --idle 120 --max 1200 -- $py -B -c $code
```

Observed outer exit: **0**. The validator accepted the freshly reconstructed but revision-inconsistent baseline.

### Focused original-correction replay

```powershell
$code = @'
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path('scripts/tests').resolve()))
names=[
 'test_measure_graph.GraphTests.test_runtime_precedence_preserves_shadowable_and_relative_names',
 'test_measure_graph.GraphTests.test_runtime_nonpackage_child_is_unresolved_not_a_local_namesake',
 'test_measure_graph.GraphTests.test_effective_frozen_binding_respects_startup_precedence_and_consistency',
 'test_measure_inventory.InventoryTests.test_fresh_cross_root_aliases_reject_different_names_and_noncode_inputs',
 'test_measure_inventory.InventoryTests.test_independent_equal_content_copies_survive_owned_head_write',
 'test_measure_inventory.InventoryTests.test_owned_artifacts_cannot_alias_a_source_input',
]
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
raise SystemExit(not result.wasSuccessful())
'@
& $py -B scripts\run.py --idle 120 --max 1200 -- $py -B -c $code
```

Observed: **6 passed, 118.575 seconds, exit 0**.

**Bounded handoff complete. Await parent disposition; no further reviewer work or Q2 admission is undertaken.**

---

## Parent disposition

Accept both reproduced findings. Original Q1 owner receives bounded correction
round 3 with pre-fix regressions, actual canonical-path rejection and immutable
baseline verification. Preserve the accepted original F1-F3 controls and all
historical evidence. Independent replay and narrowed re-review remain required.
The five-file controller copy is not complete Q4 controller-execution proof.
No Q2 admission or quality waiver.
