# Audit of the confirmatory historical evaluation

## Audit target

This note audits the machine evidence behind the
[confirmatory historical report](../../reports/experiments/confirmatory-historical-evaluation.md).
It checks the frozen identities, outcome-access boundary, source retention,
execution grid, sample reconciliation, policy accounting, registered
dependence-aware inference, analysis-tier separation, and scientific claim
boundary.[^effort-spec]

The audited result is run
[`smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221`](../../reports/experiments/runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/manifest.json).
[^run-evidence]

## Identity and outcome access

The public manifest and retained private bundle bind the following exact
identities:

- frozen Yahoo replacement protocol SHA-256
  `a5194248f7b55073e60b357c01c4993c1e50ed20c9c9672daf4780db1127f2be`;
- accepted preparation-manifest SHA-256
  `f86691e21acb8f1f70d9d9124c020f126014aae5aa631c90a0f82165814e5894`;
- accepted preparation run
  `smartdca-historical-input-v1-4da2c9a1982b48cc821969e802118270d7a95e44cc03107e8d2846729df0e14f`;
- canonical runner-input SHA-256
  `d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`;
- historical-study source SHA-256
  `bb9ffa3014ec19bfa22440f1a90e126cd64b2a9713420ce55b163e6796b9d14a`;
- shared empirical-runner SHA-256
  `7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`;
  and
- nested shared-runner run
  `smartdca-run-v1-22733a3f5cc4d73932e2c7da97aaca0f1bcd7adb79244688e6045b2972cd3657`.

The study run ID independently recomputes from the registered engine identity,
study source, shared runner, protocol bytes, and accepted input bytes. All
seven public-derived artifact fingerprints match the manifest, and the public
directory contains no source-bearing `runner/` subtree.

The protocol's `confirmatory_outcomes_accessed=false` value is retained as the
immutable registration-time state. It must not be rewritten after execution.
The confirmatory evaluator was frozen at commit `9c15cf3`, and the accepted
pre-outcome checkpoint was recorded at `63fa1ea`. Outcomes were subsequently
accessed when the exact accepted run completed on 2026-08-31. No confirmatory
dataset, policy, parameter, episode rule, estimand, uncertainty method, or
exclusion rule changed after access; the run records `deviations=[]` and
`protocol_violations=[]`.

## Source and retention boundary

The reviewed Yahoo source seam accepted 8,287 SPY adjusted-close rows and
4,018 BTC-USD close rows, with the declared date, currency, timezone, and field
semantics. The source review distinguishes Yahoo Finance as provider from the
unaffiliated pinned yfinance acquisition client and bounds the BTC-USD series
as a spot proxy.[^provider-review]

Exact canonical exports, normalized observations, rolling schedules,
episode-level outcomes, and price-bearing ledgers remain under ignored
`data/raw/`. The public bundle exposes derived aggregates, uncertainty,
reconciliation, generated tables, figure-ready data, and a
[private-artifact receipt](../../reports/experiments/runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/private-artifact-receipt.json).
The receipt binds every private artifact by path, byte length, encoding where
applicable, and SHA-256 without redistributing observations. This separation
implements [ADR 0008](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
[^provider-review][^empirical-layers]

## Completeness and reconciliation

The source and episode flow is exact:

| Stage | Count |
|---|---:|
| Source observations | 12,305 |
| Attempted rolling episodes | 1,365 |
| Included rolling episodes | 1,365 |
| Excluded rolling episodes | 0 |
| Complete policy ledgers | 49,140 |
| Three-way comparison rows | 49,140 |
| Aggregate cells | 216 |
| Confirmatory uncertainty cells | 36 |

The 1,365 episodes comprise 1,077 SPY episodes and 288 BTC-USD episodes across
the frozen 12-, 36-, and 60-month monthly-start designs. Each episode executes
four primary coverage values, one primary `identity-a0-b0` corrected-mean
configuration, three cost scenarios, and all three policies. The resulting
216 cells cover all three comparisons. An independent regrouping route
recomputed 27 declared aggregate fields for every cell with no mismatch.

The run does not execute the protocol's separately registered robustness
coverage values, alternate corrected-mean configurations, 6/24/120-month
horizons, or quarterly schedule. Only proportional and fixed-cost rows from
the robustness tier appear. The report states this explicitly and makes no
claim about the unexecuted grids.

## Accounting and safety audit

The shared runner validated all 49,140 ledgers and comparison rows. Every
declared check passed:

- full funding, nonnegative cash, long-only buy-only units, and direct terminal
  wealth accounting;
- replay of every truncated policy prefix to rule out future observation use;
- frictionless epsilon-DCA unit coverage after each purchase;
- transaction-level \(\lambda=1\) collapse for both guarded policies;
- common guarded-policy floors with selectors as the only policy difference;
- DCA accounting through an independent route;
- exact terminal cash/unit attribution for all three comparisons; and
- separation of frictionless theorem scope from proportional and fixed costs.

All 54 \(\lambda=1\) aggregate rows are exact ties across comparisons and cost
routes. For the 18 non-unit frictionless H1 cells, the worst observed relative
shortfall is `18.961%`, below the cell's allowed `50%` shortfall at
\(\lambda=0.5\). Gross negative gaps therefore do not contradict the
[epsilon-DCA unit guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md):
the theorem is a relative-wealth floor, not a DCA-dominance result.
[^guardrail-theorem]

The two fee routes contain 36 non-unit corrected-versus-DCA aggregates. Their
medians are all negative, and none of their observed minimum gaps crosses its
numerical \(\lambda-1\) boundary. Those are finite empirical observations only.
All 32,760 cost-adjusted ledgers are labeled
`outside-current-safety-theorem`; no safety theorem is inferred for fees.

## Registered inference audit

The confirmatory family has exactly 36 tests:

\[
2\ \text{datasets}\times3\ \text{horizons}\times3\ \text{non-unit coverage
values}\times2\ \text{comparisons}.
\]

Each cell orders monthly episode starts, uses a circular moving-block bootstrap
whose block length equals its horizon, draws 10,000 replicates with CPython
3.12 `random.Random`, and derives an order-independent cell seed from the
registered base seed `20260825` and complete cell identity. The artifact
retains the seed, blocks per replicate, sample bounds, replicate digest,
percentile interval, centered two-sided tail count, finite-sample p-value, Holm
rank, and adjusted p-value.[^protocol]

Independent recomputation found no mismatch in any of the 36 cell seeds,
observed statistics, registered block constructions, or full-family Holm
adjustments. The retained machine artifact separately records the replicate
digests, intervals, centered tail counts, finite-sample p-values, Holm order,
and adjusted p-values. The Holm family combines H1 and H2 exactly as
registered.

The audited outcomes are:

- H1 complete system: all 18 medians are negative, between `-4.593%` and
  `-0.335%`; all 18 cellwise percentile intervals are negative; nine
  Holm-adjusted p-values are below 0.05;
- H2 signal only: 17 medians are negative and one is positive, between
  `-0.545%` and `+0.052%`; seven cellwise percentile intervals are negative;
  no Holm-adjusted p-value is below 0.05; and
- secondary safety architecture: all 18 non-unit frictionless medians are
  negative, between `-4.365%` and `-0.340%`.

The nine H1 rejections are SPY at all three coverage values for 12 and 36
months; BTC-USD at \(\lambda=0.9\) for 36 months; and BTC-USD at
\(\lambda=0.5\) and \(0.9\) for 60 months. The sole positive H2 median is
BTC-USD, 60 months, \(\lambda=0.9\), at `+0.052%`; it is not significant.

Cellwise percentile intervals are not multiplicity-adjusted and are not the
same decision rule as the centered-bootstrap Holm tests. H2's absence of a
rejection does not prove zero effect or equivalence. The neutral-versus-DCA
architecture rows are descriptive and cannot be used as a causal
decomposition of H1.

## Independent domain review

An independent domain reviewer audited the frozen protocol, public run,
private receipts, evaluator, and registered inference without participating in
the narrative drafting. The reviewer independently:

- matched the protocol, input, shared-runner, and historical-study hashes and
  recomputed the study run ID;
- reconciled 12,305 observations, 1,365 attempts/inclusions, zero exclusions,
  49,140 ledgers and comparisons, 216 aggregates, and 36 uncertainty cells;
- recomputed every bootstrap seed, statistic, block construction, and Holm
  adjustment; and
- checked H1, H2, architecture, net-cost, and \(\lambda=1\) statements against
  the machine artifacts.

Result: **pass**, with no blocking scientific error. The review required the
final prose to preserve six boundaries: name the 18 cells as non-unit primary
frictionless cells; identify the full 36-cell Holm family; distinguish
cellwise intervals from multiplicity-adjusted tests; avoid interpreting H2
non-significance as equivalence; keep architecture descriptive rather than
causal; and separate realized gross safety from net cost rows outside the
theorem. The report incorporates each requirement. The reviewer also confirmed
that the unexecuted robustness grids are not claimed.

## Reproduction and claim boundary

The exact private run is preserved at
`data/raw/smartdca-historical-confirmatory-yahoo-v1/<study-run-id>/` and the
accepted preparation at
`data/raw/smartdca-historical-preparation-yahoo-v1/<preparation-run-id>/`.
Given those retained inputs, `python3.12 -m reproducibility.historical_study`
regenerates the private and public bundles under the manifest's collision/no-
overwrite rule. The public checkpoint is:

```bash
python3.12 -m unittest \
  reproducibility.checks.check_historical_confirmatory_evaluation
```

This evidence describes overlapping-window associations for the declared SPY
adjusted-close and BTC-USD proxy series. It does not establish universal,
causal, stochastic, optimal, expected, or future market performance. The
[terminal-inventory boundary](../theorems/arbitrary-horizon-performance-boundary.md)
validates ledger-conditioned attribution but does not supply a performance
sign.[^performance-boundary] Ticket 06 may synthesize this bounded historical
result with the separately labeled deterministic and stochastic evidence;
ticket 07 remains the independent publication-package gate.

[^effort-spec]: Contract join: [approved safety-adaptivity empirical specification](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md).
[^run-evidence]: Machine-evidence join: [immutable historical study manifest](../../reports/experiments/runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/manifest.json).
[^protocol]: Registration join: [frozen Yahoo historical protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json).
[^provider-review]: External-source and retention join: [Yahoo Finance historical-data provider review](yahoo-finance-historical-data-provider-review.md).
[^guardrail-theorem]: Safety join: [epsilon-DCA unit-coverage theorem](../theorems/epsilon-dca-safety-unit-guardrail.md).
[^performance-boundary]: Attribution join: [arbitrary-horizon terminal-inventory boundary](../theorems/arbitrary-horizon-performance-boundary.md).
[^empirical-layers]: Artifact join: [empirical protocol/input/run layer decision](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
