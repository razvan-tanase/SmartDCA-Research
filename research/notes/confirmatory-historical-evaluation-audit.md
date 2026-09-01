# Audit of the confirmatory historical evaluation and robustness extension

## Audit target

This note audits the machine evidence behind the
[confirmatory historical report](../../reports/experiments/confirmatory-historical-evaluation.md).
It checks the frozen identities, outcome-access boundary, source retention,
execution grid, sample reconciliation, policy accounting, registered
dependence-aware inference, analysis-tier separation, the separately frozen
robustness extension, and scientific claim boundary.[^effort-spec]

The audited result is run
[`smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221`](../../reports/experiments/runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/manifest.json).
The separately audited robustness result is
[`smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184`](../../reports/experiments/runs/smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184/manifest.json).
[^run-evidence][^robustness-evidence]

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

After that boundary was recorded, execution plan
`historical-yahoo-registered-robustness-v1` froze the omitted registered axes
before their outcomes were executed. Its SHA-256 is
`2cc155f6c63a74a0dce7cad202d6a5870a6f59bf239733ce2ad5e117919eae14`;
the frozen robustness engine SHA-256 is
`c909f8d87bf954771da24c0313bd6e749bc050cee1177528a862f479afbcdd72`.
The outer robustness manifest records post-confirmatory execution and is
authoritative over the nested projected configuration's inherited
registration-time schema field.[^robustness-plan]

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

The robustness bundle applies the same boundary. All schedule inputs,
episode-level results, and price-bearing ledgers remain private; its public
[artifact receipt](../../reports/experiments/runs/smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184/private-artifact-receipt.json)
binds the retained bytes without exposing price or episode rows.

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

The primary run alone does not execute the protocol's separately registered
robustness coverage, 6/24/120-month horizons, or quarterly schedule. The
separately identified post-confirmatory extension executes those coverage and
horizon axes without mutating the primary run. The four alternate
corrected-mean configurations remain explicitly deferred.

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

An independent domain reviewer audited the confirmatory run's frozen protocol,
public bundle, private receipts, evaluator, and registered inference without
participating in the narrative drafting. The reviewer independently:

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
that the unexecuted robustness grids are not claimed by the primary run; they
were opened later only under the separate extension identity.

## Registered robustness extension audit

The extension reused all 1,365 sealed primary monthly episodes at the five
registered robustness coverage values and repeated \(\lambda=1\) for runner
compatibility. It separately built quarterly starts at a three-month stride
with deposits at \(0,3,\ldots,H-3\): 2, 8, and 40 deposits for 6, 24, and 120
months. All nine primary-plus-robustness coverage values were executed for the
quarterly design. Both slices used only the primary `identity-a0-b0`
configuration, all three costs, all three policies, and all three comparisons.

The extension reconciles exactly:

| Stage | Monthly | Quarterly | Total |
|---|---:|---:|---:|
| Source observations | 12,305 | 12,305 | 12,305 unique |
| Attempted schedule episodes | 1,365 | 428 | 1,793 |
| Included schedule episodes | 1,365 | 428 | 1,793 |
| Excluded schedule episodes | 0 | 0 | 0 |
| Ledgers and comparison rows | 73,710 | 34,668 | 108,378 |
| Aggregate cells | 324 | 486 | 810 |

The combined extension therefore contains 108,378 ledgers and comparison rows
without treating the two schedule-specific episode sets as one cadence.

The quarterly sample counts are BTC-USD `42/36/4` and SPY `130/124/92` for
6/24/120 months. All 20 shared-runner checks across the two slices passed. An
independent private-ledger audit also found zero transaction-path mismatches in
the \(\lambda=1\) collapse across 4,095 monthly and 1,284 quarterly scenario
groups. The public directory contains only its five derived artifacts plus the
manifest, while all 26 manifest-listed artifacts exist and match inside the
private bundle.

Among frictionless non-unit cells, corrected guarded versus DCA had 30
negative monthly medians (`-4.8134%` to `-0.0335%`) and 48 negative quarterly
medians (`-23.4841%` to `-0.0260%`). Corrected guarded versus neutral guarded
had 30 negative monthly medians (`-0.5836%` to `-0.0002%`) and, quarterly, 40
negative and eight positive medians (`-9.2164%` to `+0.0570%`). The eight
positive quarterly signal medians are exactly the eight non-unit 6-month
BTC-USD cells. These are median relative terminal-wealth gaps within each
schedule; raw wealth is not compared between cadences. In particular, the
120-month BTC-USD rows have `N=4`.

Every frictionless corrected-versus-DCA minimum respects its numerical
\(\lambda-1\) floor, and every \(\lambda=1\) aggregate is an exact tie. Negative
DCA gaps remain allowed by epsilon-DCA safety. The 156 non-unit cost-adjusted
complete-system medians were negative and did not cross the numerical floor,
but those finite rows remain outside the current theorem.

Tier separation is exact:
`analysis_tier_counts={"robustness":792,"secondary":18}`. The 18 secondary
cells are the monthly frictionless \(\lambda=1\) compatibility rows; every
quarterly row is robustness evidence. All 810 cells record
`uncertainty_status=not-run-robustness`; no row enters H1/H2, and the sealed
36-test Holm family is unchanged. The run records no deviation or protocol
violation.

An independent post-run domain reviewer recomputed the outer and nested run
identities; matched the engine, runner, protocol, plan, preparation, private,
and public artifact hashes; independently checked the schedule projections,
counts, all 36 generated table rows, tier labels, and \(\lambda=1\) transaction
paths; and found no mismatch. Result: **pass**, with no blocking scientific
error. The required interpretation is descriptive and within-schedule: it
makes no universal, causal, optimality, significance, or expected-performance
claim, and the four alternate corrected-mean configurations remain deferred.

## Reproduction and claim boundary

The exact private run is preserved at
`data/raw/smartdca-historical-confirmatory-yahoo-v1/<study-run-id>/` and the
accepted preparation at
`data/raw/smartdca-historical-preparation-yahoo-v1/<preparation-run-id>/`.
The robustness extension is preserved separately at
`data/raw/smartdca-historical-robustness-yahoo-v1/<robustness-run-id>/`.
Given those retained inputs, `python3.12 -m reproducibility.historical_study`
regenerates the primary bundle and
`python3.12 -m reproducibility.historical_robustness` regenerates the extension
under the manifests' collision/no-overwrite rule. The public checkpoint is:

```bash
python3.12 -m unittest \
  reproducibility.checks.check_historical_confirmatory_evaluation \
  reproducibility.checks.check_historical_robustness_evaluation
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
[^robustness-evidence]: Robustness-evidence join: [immutable registered robustness manifest](../../reports/experiments/runs/smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184/manifest.json).
[^robustness-plan]: Robustness-registration join: [post-confirmatory execution plan](../../experiments/inputs/historical-yahoo-registered-robustness-v1.json).
[^protocol]: Registration join: [frozen Yahoo historical protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json).
[^provider-review]: External-source and retention join: [Yahoo Finance historical-data provider review](yahoo-finance-historical-data-provider-review.md).
[^guardrail-theorem]: Safety join: [epsilon-DCA unit-coverage theorem](../theorems/epsilon-dca-safety-unit-guardrail.md).
[^performance-boundary]: Attribution join: [arbitrary-horizon terminal-inventory boundary](../theorems/arbitrary-horizon-performance-boundary.md).
[^empirical-layers]: Artifact join: [empirical protocol/input/run layer decision](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
