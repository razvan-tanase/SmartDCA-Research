# Confirmatory historical safety-adaptivity evaluation

## Question

What realized performance did DCA, the neutral epsilon-DCA-guarded selector,
and the [guarded corrected-mean SmartDCA rule](../../research/definitions/guarded-corrected-mean-smartdca-rule.md)
produce across the frozen rolling SPY adjusted-close and BTC-USD episodes?
[^guarded-rule]

## Result

The primary historical finding is negative. Across all 18 non-unit primary
frictionless cells, the median complete-system gap for corrected guarded versus
DCA was below zero, ranging from `-4.593%` to `-0.335%`. All 18 cellwise 95%
block-bootstrap percentile intervals were below zero, and nine cells rejected
the two-sided zero null after Holm adjustment over the full 36-cell H1/H2
family. Every rejection was in the negative direction.

The registered signal-only comparison does not isolate a favorable
corrected-mean effect. Corrected guarded versus neutral guarded had a negative
median in 17 of 18 cells, ranging from `-0.545%` to `+0.052%`; no H2 cell was
Holm-significant. This does not establish that the signal is zero or equivalent
to the neutral selector. It says only that this run found no multiplicity-
adjusted H2 evidence against zero under the registered test.

These are realized associations among overlapping historical windows. They do
not establish universal, causal, optimal, or expected superiority or
inferiority for either policy.

## Run identity and scope

The immutable public manifest is
[`smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221`](runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/manifest.json).
It binds:

- replacement protocol SHA-256
  `a5194248f7b55073e60b357c01c4993c1e50ed20c9c9672daf4780db1127f2be`;
- accepted preparation-manifest SHA-256
  `f86691e21acb8f1f70d9d9124c020f126014aae5aa631c90a0f82165814e5894`;
- canonical runner-input SHA-256
  `d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`;
- historical-study source SHA-256
  `bb9ffa3014ec19bfa22440f1a90e126cd64b2a9713420ce55b163e6796b9d14a`;
- shared-runner source SHA-256
  `7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`;
  and
- CPython 3.12 with no third-party evaluation dependency.

The [frozen Yahoo replacement protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json)
declared the hypotheses, primary grid, estimands, overlapping-window bootstrap,
and multiplicity correction before outcomes were accessed.[^protocol] Its
registration-time `confirmatory_outcomes_accessed=false` field remains
immutable; the tracked ticket and audit note record that outcomes were
subsequently opened by this run on 2026-08-31.

Yahoo Finance source observations, normalized prices, episode schedules, raw
episode results, and price-bearing ledgers remain in the ignored private
bundle. The committed bundle contains only derived aggregates, uncertainty,
validation, generated tables, figure-ready data, and cryptographic receipts,
following the conservative redistribution boundary in the reviewed provider
note and the repository's empirical-layer decision.[^provider-review]
[^empirical-layers]

## Execution completeness

Outcome-blind preparation contributed 8,287 SPY observations and 4,018 BTC-USD
observations through 2025-12-31. The accepted monthly-first-eligible schedule
produced the following overlapping episode counts; each count is the sample
size of every corresponding coverage/comparison cell.

| Dataset | 12 months | 36 months | 60 months | Total |
|---|---:|---:|---:|---:|
| SPY adjusted daily | 383 | 359 | 335 | 1,077 |
| BTC-USD daily | 120 | 96 | 72 | 288 |
| **Total** | **503** | **455** | **407** | **1,365** |

All 1,365 declared episodes were attempted and included; there were zero
exclusions, failures, deviations, or protocol violations. Crossing the
episodes with four primary coverage values, three cost routes, and three
policies produced 49,140 complete ledgers and 49,140 comparison rows. These
reconcile independently to 216 aggregate cells. The complete machine-readable
[validation](runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/study-validation.json)
and [aggregate reconciliation](runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/aggregate-reconciliation.json)
retain the count and invariant receipts.

## Confirmatory outcomes

The registered H1 comparison is corrected guarded versus DCA; H2 is corrected
guarded versus neutral guarded. The table reports the range of the three
coverage-specific medians at \(\lambda\in\{0.5,0.75,0.9\}\). `N` is the number
of episodes in each individual cell. The significance columns use Holm-
adjusted two-sided p-values below 0.05.

| Dataset | Horizon | N | H1 median range | H1 significant λ | H2 median range | H2 significant λ |
|---|---:|---:|---:|---|---:|---|
| BTC-USD | 12 months | 120 | -4.337% to -1.640% | none | -0.241% to -0.100% | none |
| BTC-USD | 36 months | 96 | -3.707% to -3.172% | 0.9 | -0.545% to -0.391% | none |
| BTC-USD | 60 months | 72 | -4.593% to -2.511% | 0.5, 0.9 | -0.252% to +0.052% | none |
| SPY | 12 months | 383 | -0.875% to -0.335% | 0.5, 0.75, 0.9 | -0.009% to -0.002% | none |
| SPY | 36 months | 359 | -0.924% to -0.717% | 0.5, 0.75, 0.9 | -0.045% to -0.039% | none |
| SPY | 60 months | 335 | -0.938% to -0.832% | none | -0.072% to -0.068% | none |

The generated [exact confirmatory table](runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/report-tables.md)
retains every observed median, cellwise interval, and adjusted p-value without
manual transcription. Seven H2 cellwise percentile intervals were wholly
negative, but none survived the registered Holm family. Percentile intervals
are cellwise and not multiplicity-adjusted; they must not be read as the same
decision rule as the Holm-adjusted tests.

The circular moving-block bootstrap used 10,000 replicates per cell, base seed
`20260825`, deterministic order-independent cell seeds, monthly episode starts
as sampling units, and block length equal to the 12-, 36-, or 60-month horizon.
The full [uncertainty artifact](runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/uncertainty.json)
records each seed, block construction, replicate digest, interval, centered
tail count, unadjusted p-value, Holm rank, and adjusted p-value.

## Secondary safety and mechanism observations

The neutral-guarded-versus-DCA safety-architecture comparison is descriptive.
Its median was negative in all 18 non-unit primary frictionless cells, ranging
from `-4.365%` to `-0.340%`. This does not causally attribute the H1 result to
the guardrail: it describes the neutral policy as configured under the same
realized windows.

At \(\lambda=1\), both guarded policies collapsed transaction by transaction to
DCA in every episode and cost route. All 54 corresponding aggregate rows are
exact ties. At non-unit frictionless coverage, the largest observed corrected-
versus-DCA shortfall was `18.961%`, and the lowest 5% quantile was `-15.292%`;
both occurred in the BTC-USD 12-month, \(\lambda=0.5\) cell. These negative gaps
are compatible with [epsilon-DCA safety](../../research/theorems/epsilon-dca-safety-unit-guardrail.md):
the theorem supplies a \(\lambda\) relative-wealth floor, not DCA dominance.
[^guardrail-theorem]

Across the 18 non-unit frictionless cells, mean corrected-policy cash drag
ranged from `2.126%` to `11.482%` of deposits and mean terminal asset exposure
from `91.698%` to `98.909%`. The corresponding neutral-policy ranges were
`1.667%` to `8.329%` cash drag and `92.041%` to `99.563%` exposure. Mean floor
activation ranged from `3.990%` to `100%` for corrected and `3.900%` to `100%`
for neutral. Both policies made one positive purchase per scheduled deposit in
these frictionless cells.

In every H1 aggregate, mean carried-cash contribution was positive and mean
evaluation-price unit contribution was negative. Their sum reconciles to the
mean terminal-wealth gap episode by episode under the accepted
[terminal-inventory identity](../../research/theorems/arbitrary-horizon-performance-boundary.md).
This is ledger-conditioned attribution, not a causal explanation or a claim
about future prices.[^performance-boundary]

## Robustness observations and costs

The two preregistered cost scenarios are robustness rows, not confirmatory
tests and not covered by the current safety theorem.

| Cost route | Non-unit H1 cells | Median range | Largest observed shortfall |
|---|---:|---:|---:|
| Proportional 10 bps | 18 | -4.592% to -0.330% | 18.957% |
| Fixed USD 1 per purchase | 18 | -4.598% to -0.335% | 18.979% |

All 36 net-of-cost complete-system medians were negative. No observed net row
fell below its numerical \(\lambda\) gap floor, but that finite observation does
not extend the frictionless theorem to fees. No confirmatory interval or
multiplicity-adjusted test was registered for these rows.

This run did not execute the protocol's separate robustness coverage values,
four alternate corrected-mean configurations, 6/24/120-month horizons, or
quarterly schedule. It therefore makes no claim about those grids. They cannot
be silently pooled with or substituted for the primary analysis.

## Exploratory analyses

No post-hoc regime labels, calendar subperiods, extra parameters, or path
diagnostics were executed or selected. There is no exploratory result in this
bundle.

## Accounting and reproduction

The shared validation replayed every causal prefix and passed full funding,
buy-only behavior, nonnegative cash, frictionless unit coverage, independent
DCA accounting, direct terminal-wealth accounting, terminal cash/unit
attribution, common guarded-policy floors, transaction-level \(\lambda=1\)
collapse, and theorem/cost-scope separation for all 49,140 ledgers.

Reproduction requires the access-controlled accepted preparation directory.
With CPython 3.12 and two new empty roots, run:

```bash
python3.12 -m reproducibility.historical_study \
  --config experiments/protocols/safety-adaptivity-yahoo-v2.json \
  --accepted-preparation-manifest \
    experiments/inputs/historical-yahoo-preparation-manifest-v5.json \
  --preparation-directory \
    data/raw/smartdca-historical-preparation-yahoo-v1/smartdca-historical-input-v1-4da2c9a1982b48cc821969e802118270d7a95e44cc03107e8d2846729df0e14f \
  --output-root "$(mktemp -d)" \
  --publication-root "$(mktemp -d)"
```

Then run the public checkpoint:

```bash
python3.12 -m unittest \
  reproducibility.checks.check_historical_confirmatory_evaluation
```

The evaluator fails before outcome creation on any accepted-manifest, protocol,
artifact, count, or run-identity mismatch. Existing run identities are
collision targets and are never overwritten.

## Limitations and publication state

The evidence covers one fixed corrected-mean configuration, primary monthly
episodes for two Yahoo Finance series, three horizons, three non-unit coverage
levels, and two simple fee models. SPY adjusted close is a declared proxy and
BTC-USD is a spot proxy with limited venue/aggregation semantics; source and
adjustment boundaries are documented in the provider review.[^provider-review]
Windows overlap heavily, and the registered block bootstrap addresses that
dependence only within the declared design.

The finding is not individualized investment advice and does not establish a
causal market effect, stochastic optimum, parameter ranking, expected return,
or universal rule. The linked [audit note](../../research/notes/confirmatory-historical-evaluation-audit.md)
records the independent domain review.[^historical-audit] This report is the
reviewed historical input to ticket 06's cross-layer synthesis, not the final
publication package; the independent package review remains ticket 07.

[^protocol]: Source join: [frozen Yahoo historical protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json).
[^provider-review]: External-source and retention join: [Yahoo Finance historical-data provider review](../../research/notes/yahoo-finance-historical-data-provider-review.md).
[^guarded-rule]: Model join: [guarded corrected-mean SmartDCA definition](../../research/definitions/guarded-corrected-mean-smartdca-rule.md).
[^guardrail-theorem]: Safety join: [epsilon-DCA unit-coverage theorem](../../research/theorems/epsilon-dca-safety-unit-guardrail.md).
[^performance-boundary]: Attribution join: [arbitrary-horizon terminal-inventory boundary](../../research/theorems/arbitrary-horizon-performance-boundary.md).
[^empirical-layers]: Artifact join: [empirical protocol/input/run layer decision](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
[^historical-audit]: Evidence join: [confirmatory historical evaluation audit](../../research/notes/confirmatory-historical-evaluation-audit.md).
