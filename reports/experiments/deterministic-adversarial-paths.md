---
profile: smartdca-okf/0.4
type: experiment-report
title: "Deterministic synthetic and adversarial path evaluation"
description: "Reproducible three-policy evidence across deterministic boundary, stress, and deliberately hostile price paths."
knowledge_role: evidence
status: draft
original_record: false
sources:
  - id: effort-spec
    title: "Evaluate the safety-adaptivity trade-off of guarded SmartDCA"
    resource: .scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
    source_kind: internal
  - id: guardrail-theorem
    title: "Epsilon-DCA safety is exactly a causal unit-coverage guardrail"
    resource: research/theorems/epsilon-dca-safety-unit-guardrail
    source_kind: internal
  - id: performance-boundary
    title: "Terminal cash and units give the exact arbitrary-horizon performance boundary"
    resource: research/theorems/arbitrary-horizon-performance-boundary
    source_kind: internal
  - id: empirical-layers
    title: "Place empirical protocols, inputs, and run bundles in versioned layers"
    resource: docs/adr/0008-place-empirical-protocol-input-run-layers
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-25T11:10:08Z
generation_run: urn:uuid:27919a38-c8e3-4937-a663-41c2fbcb6ca6
---
# Deterministic synthetic and adversarial path evaluation

## Question

How do DCA, the neutral epsilon-DCA-guarded selector, and the
[guarded corrected-mean SmartDCA rule](../../research/definitions/guarded-corrected-mean-smartdca-rule.md)
[^guarded-rule] behave on interpretable deterministic and
deliberately hostile paths under the preregistered primary coverage,
corrected-mean, and cost grid?

## Run identity and scope

The immutable study manifest is
[`smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db`](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/manifest.json).
It binds:

- protocol SHA-256
  `a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4`;
- deterministic-study SHA-256
  `40b4ba6e22de4f34ce558be2d96239528bbd11890245ddbe4ccf68e583aae456`;
- generated runner-input SHA-256
  `1ac012f5908f81598a4f2301a29442f44111960f17637e0025aefe183ff6bc85`;
- generator-source SHA-256
  `e8e2cfcf49d7c35991c3fc5c403f023028e6f5c31b16d14d15daee291ce86a59`;
- shared-runner-source SHA-256
  `7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`;
  and
- shared runner identity
  `smartdca-run-v1-722b1c4bafd4c98698a231b67528e62355a185d94cd1a3e9db2611d3b702e879`.

The saved [study specification](../../experiments/inputs/deterministic-adversarial-v1.json)
contains 21 attempted path configurations. Predicate validation produced 18 generated paths
and 3 retained exclusions. Every generated episode was then
executed through four primary coverage values
\(\lambda\in\{1,0.9,0.75,0.5\}\), the primary
`identity-a0-b0` corrected mean, three cost scenarios, and all three policies.
The resulting [shared-runner bundle](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/runner/manifest.json)
contains 648 complete ledgers and 648 comparison rows.

This is non-confirmatory synthetic evidence. Seed: `none` (the saved paths and
finite adversarial grid are deterministic). No historical provider response or
stochastic path was used. The execution implements the outcome-blind
[effort contract](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md)
[^effort-spec] through the versioned layers fixed by
[ADR 0008](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
[^empirical-layers]

## Path construction and validation

The 14 required primary families are constant, monotone rise, monotone decline,
weak single valley, strict single valley, incomplete recovery, completed
recovery, multiple valleys, crash, sudden rebound, prolonged drawdown, flat
segments, hostile carried cash, and hostile adaptive timing. Three additional
generated episodes reconnect the runner to two-purchase, three-purchase, and
repeated-floor exact regressions. One preliminary whipsaw remains as a retained
adversarial-design iteration because its realized selector effect had the
opposite sign from the intended hostile fixture.

Path validity is independent of policy performance. The
[attempt ledger](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/path-attempts.jsonl)
records the saved price parameters, predicate, predicate diagnostics, mechanism
labels, boundary tags, status, and machine-readable exclusion reason before any
policy is run. The three retained exclusions are:

| Attempt | Reason | Meaning |
|---|---|---|
| `rejected-predicate-mismatch` | `path_predicate_failed` | A decreasing two-point path was submitted as monotone rise. |
| `rejected-nonpositive-price` | `invalid_price` | A zero purchase price violated the positive-price model. |
| `rejected-missing-evaluation` | `invalid_decimal` | The evaluation price was absent. |

The [boundary receipt](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/boundary-fixtures.json)
contains seven executable regression contracts connecting the study to the
existing constant, two-purchase, three-purchase, single-valley,
repeated-floor-activation, and arbitrary-horizon checks. Each receipt records
its prior check, expected output, observed output, and passed status; the
evidence scope remains explicitly `finite-regression-not-proof`.

The hostile adaptive-timing fixture was selected by a declared finite design
search rather than by an unrecorded favorable example. The
[search ledger](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/adversarial-search.jsonl)
retains all 729 six-purchase sequences over the fixed price grid
`{60, 100, 150}`. The policy-independent predicate admitted 42 sequences and
excluded 687; every admitted sequence was run through the same three-policy,
coverage, corrected-mean, and cost grid in a separate
[shared-runner bundle](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/adversarial-search-runner/manifest.json).
The saved objective minimizes corrected-versus-neutral terminal-wealth gap at
frictionless \(\lambda=0.75\), with a lexicographic price-sequence tie break.
It selected candidate `hostile-adaptive-timing-grid-v1-637` with prices
`[150, 100, 150, 100, 150, 60]`. This is exhaustive only for that declared
finite grid, not for all hostile paths.

## Primary deterministic observations

The table is emitted from the immutable episode results in
[`report-tables.txt`](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/report-tables.txt).
It reports the frictionless \(\lambda=0.75\) episode result for each primary
family. Each percentage uses its named comparator as denominator, so the three
columns are not arithmetically additive. Cash drag, exposure, and activation
are for the corrected guarded policy.

| Family | Complete system: corrected vs DCA | Signal only: corrected vs neutral | Safety architecture: neutral vs DCA | Corrected cash drag | Corrected asset exposure | Floor activation |
|---|---:|---:|---:|---:|---:|---:|
| Constant | 0.000% | 0.000% | 0.000% | 12.5% | 87.5% | 100.0% |
| Monotone rise | -4.712% | -0.460% | -4.271% | 16.9% | 87.8% | 100.0% |
| Monotone decline | +5.260% | -0.887% | +6.202% | 7.7% | 88.6% | 100.0% |
| Weak single valley | -1.919% | +0.077% | -1.995% | 13.5% | 88.5% | 71.4% |
| Strict single valley | -3.608% | +0.150% | -3.752% | 15.2% | 89.0% | 71.4% |
| Incomplete recovery | -1.608% | +0.292% | -1.894% | 14.6% | 87.7% | 100.0% |
| Completed recovery | -2.758% | +0.428% | -3.172% | 17.3% | 87.1% | 100.0% |
| Multiple valleys | +0.077% | +1.520% | -1.421% | 13.6% | 89.1% | 71.4% |
| Crash | +3.565% | +0.273% | +3.283% | 9.1% | 89.0% | 100.0% |
| Sudden rebound | -0.883% | +1.299% | -2.154% | 17.5% | 86.5% | 80.0% |
| Prolonged drawdown | -0.198% | -0.013% | -0.184% | 11.9% | 88.3% | 85.7% |
| Flat segments | -0.821% | +0.136% | -0.955% | 13.1% | 87.9% | 83.3% |
| Hostile carried cash | -4.978% | -0.473% | -4.526% | 16.3% | 88.6% | 100.0% |
| Hostile adaptive timing | +26.105% | -2.901% | +29.873% | 7.0% | 80.4% | 83.3% |

Several mechanisms are visible without converting the catalog into a
probability sample:

- At \(\lambda=1\), both guarded policies collapse transaction by transaction
  to DCA in every scenario. This is the registered accounting boundary.
  [^guardrail-theorem]
- On the constant frictionless path, corrected-minus-DCA terminal cash is
  `500` and the unit gap is `-5`; evaluation at `100` cancels them exactly.
  Equal wealth therefore does not imply equal inventory paths.
- The monotone rise makes carried cash costly. The complete system loses
  4.712%, with most of the gap already present in the neutral guardrail
  architecture.
- The monotone decline reverses that architecture effect: neutral guarded
  exceeds DCA by 6.202%, while the corrected signal is 0.887% below neutral.
- Weak, strict, incomplete-recovery, and completed-recovery paths all have a
  modest positive signal-only effect but a larger negative architecture
  effect. A favorable selector sign does not imply complete-system advantage.
- On multiple valleys, the +1.520% signal contribution narrowly offsets the
  -1.421% architecture result, leaving a +0.077% complete-system gap.
- The sudden rebound shows the converse mechanism: a +1.299% signal effect
  does not offset the -2.154% architecture effect caused by missed exposure.
- The hostile carried-cash path is adverse to both layers: corrected trails
  DCA by 4.978% and neutral by 0.473%.
- The hostile adaptive-timing fixture separates the layers sharply. Corrected
  trails neutral by 2.901%, even though the neutral guardrail architecture is
  29.873% above DCA and the complete system remains 26.105% above DCA. For the
  signal comparison, corrected carries `200.736` less cash and `4.556` more
  units than neutral; at evaluation price `30`, the extra-unit contribution
  `136.684` does not offset the cash contribution `-200.736`.
  [^performance-boundary]
- The retained preliminary whipsaw instead gives a +1.607% signal effect at
  the same coverage. A structural hostile-path predicate does not preordain a
  policy outcome.

The complete row-level cash, unit, purchase, exposure, fee, floor, and
activation attribution is in
[`mechanism-attribution.csv`](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/mechanism-attribution.csv).

## Coverage and downside across the fixed catalog

The next generated table is a descriptive range over all 18 paths, including
the exact regressions and retained design iteration. It is not an estimate of
any market population. Loss/tie/win counts refer to the sign of each
episode-level wealth gap.

| Coverage | Comparison | Minimum | Maximum | Loss / tie / win |
|---:|---|---:|---:|---:|
| 0.9 | Corrected vs DCA | -1.991% | +10.824% | 9 / 2 / 7 |
| 0.9 | Corrected vs neutral | -1.005% | +2.073% | 5 / 2 / 11 |
| 0.9 | Neutral vs DCA | -1.810% | +11.949% | 12 / 2 / 4 |
| 0.75 | Corrected vs DCA | -4.978% | +26.105% | 9 / 2 / 7 |
| 0.75 | Corrected vs neutral | -2.901% | +3.516% | 5 / 2 / 11 |
| 0.75 | Neutral vs DCA | -4.526% | +29.873% | 12 / 2 / 4 |
| 0.5 | Corrected vs DCA | -8.565% | +34.880% | 10 / 2 / 6 |
| 0.5 | Corrected vs neutral | -5.577% | +5.108% | 4 / 2 / 12 |
| 0.5 | Neutral vs DCA | -7.508% | +42.846% | 11 / 2 / 5 |

Lower coverage expands both adverse and favorable realized extremes in this
catalog. That is consistent with greater adaptive freedom, but these paths do
not supply frequencies or justify monotonic expected-performance claims.

## Cost-adjusted results

All cost-adjusted rows in the generated table are explicitly outside the current safety theorem. At
\(\lambda=0.75\), the descriptive ranges remain close to the frictionless
catalog under the declared 10-basis-point proportional and one-dollar fixed
fees:

| Cost | Comparison | Minimum | Maximum | Loss / tie / win |
|---|---|---:|---:|---:|
| Frictionless | Corrected vs DCA | -4.978% | +26.105% | 9 / 2 / 7 |
| Frictionless | Corrected vs neutral | -2.901% | +3.516% | 5 / 2 / 11 |
| Frictionless | Neutral vs DCA | -4.526% | +29.873% | 12 / 2 / 4 |
| Proportional 10 bps | Corrected vs DCA | -4.965% | +26.125% | 9 / 0 / 9 |
| Proportional 10 bps | Corrected vs neutral | -2.903% | +3.515% | 5 / 2 / 11 |
| Proportional 10 bps | Neutral vs DCA | -4.515% | +29.897% | 12 / 0 / 6 |
| Fixed USD 1 | Corrected vs DCA | -4.979% | +26.122% | 9 / 2 / 7 |
| Fixed USD 1 | Corrected vs neutral | -2.893% | +3.515% | 5 / 2 / 11 |
| Fixed USD 1 | Neutral vs DCA | -4.527% | +29.880% | 12 / 2 / 4 |

These are empirical net-performance calculations only. The proportional-cost
route can break zero-gap ties away from \(\lambda=1\), which is another reason
not to transfer the frictionless theorem label to cost-adjusted output.

## Accounting and reproduction

The [study validation receipt](runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/study-validation.json)
records 17 required and boundary predicates plus one retained design-iteration
predicate and seven linked boundary regression contracts as passed. The nested
shared-runner receipt verifies full funding,
causal prefixes, buy-only behavior, direct wealth accounting, frictionless unit
coverage, terminal cash/unit identity, the \(\lambda=1\) collapse, the common
guardrail contract, independent DCA accounting, and theorem-scope separation.
There were no policy-result exclusions among the 648 comparison rows.
The separate design-search runner adds 1,512 complete ledgers and 1,512
comparison rows for the 42 eligible search candidates; the 687 predicate
exclusions remain visible without being passed to a policy.
The run manifest fingerprints 22 pre-manifest artifacts, including the exact
plain-text table blocks reproduced above.

From a fresh repository checkout, regenerate the complete bundle with:

```bash
python -m reproducibility.deterministic_study \
  --config experiments/protocols/safety-adaptivity-v1.json \
  --study experiments/inputs/deterministic-adversarial-v1.json \
  --output-root /tmp/smartdca-deterministic-replay
```

Then run the executable checkpoint:

```bash
python -m unittest \
  reproducibility.checks.check_deterministic_adversarial_study
```

The checkpoint compares every regenerated artifact byte for byte with the
committed bundle.

## Limitations

This study can reveal accounting errors, guardrail activation, selector and
architecture mechanisms, exact regression drift, cash drag, exposure, and
finite counterexamples. Deterministic evidence cannot establish historical or stochastic performance,
path probabilities, expected returns, statistical
significance, market causality, parameter optimality, or universal
outperformance. The stochastic and historical evidence layers remain separate
open tickets.

[^effort-spec]: Source join: [approved empirical effort specification](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md).
[^guarded-rule]: Source join: [canonical guarded-rule definition](../../research/definitions/guarded-corrected-mean-smartdca-rule.md).
[^guardrail-theorem]: Source join: [epsilon-DCA unit-coverage theorem](../../research/theorems/epsilon-dca-safety-unit-guardrail.md).
[^performance-boundary]: Source join: [arbitrary-horizon cash-and-units boundary](../../research/theorems/arbitrary-horizon-performance-boundary.md).
[^empirical-layers]: Source join: [empirical artifact-layer decision](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
