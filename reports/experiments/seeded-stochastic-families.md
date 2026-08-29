---
profile: smartdca-okf/0.4
type: experiment-report
title: "Seeded stochastic path-family evaluation"
description: "Reproducible three-policy sensitivity evidence across controlled trend, mean-reversion, volatility, regime-switching, and jump constructions."
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
  - id: stochastic-audit
    title: "Audit of the seeded stochastic family evaluation"
    resource: research/notes/seeded-stochastic-family-evaluation-audit
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-29T18:35:34Z
generation_run: urn:uuid:ac795fdc-b96d-4dae-9f8f-5974ed34f822
---
# Seeded stochastic path-family evaluation

## Question

How do DCA, the neutral epsilon-DCA-guarded selector, and the
[guarded corrected-mean SmartDCA rule](../../research/definitions/guarded-corrected-mean-smartdca-rule.md)
[^guarded-rule] behave under reproducible controlled trend, mean-reversion,
volatility, regime-switching, and jump constructions?

## Run identity and scope

The immutable study manifest is
[`smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25`](runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/manifest.json).
It binds the frozen protocol (`a508b4f0…d6e4`), saved stochastic study
(`29929392…297d`), generated runner input (`30873d39…bb6`), generator source
(`af4484cd…d41e`), shared runner (`7fd480fd…fee`), and CPython `3.12.14`.
The detailed identity and fingerprint audit is recorded in the linked
[research note](../../research/notes/seeded-stochastic-family-evaluation-audit.md).
[^stochastic-audit]

The [saved design](../../experiments/inputs/seeded-stochastic-families-v1.json)
contains one primary baseline and one separately labeled exploratory
sensitivity for each family. Three common saved seeds and the preregistered
12-, 36-, and 60-month horizons produce 90 attempted paths. All 90 generated;
there were zero exclusions or configuration, numerical, generator, input, or
runner failures. Each path executes the frozen
[effort contract](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md)
[^effort-spec] grid: four primary coverage levels, primary
`identity-a0-b0`, three cost scenarios, and all three policies.

The resulting bundle contains 3,240 complete policy ledgers, 3,240 comparison
rows, 1,080 aggregate cells, exhaustive
[figure-ready data](runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/stochastic-figure-ready.csv),
and generated [report tables](runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/report-tables.txt).
The empirical layers and immutable identity rules follow
[ADR 0008](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
[^empirical-layers]

## Controlled constructions

| Family | Primary configuration | Exploratory sensitivity |
|---|---|---|
| Trend | +6% annual drift, 15% annual volatility | -6% annual drift |
| Mean reversion | 12-month log-price half-life around 100, 15% stationary dispersion | 3-month half-life |
| Stochastic volatility | 15% long-run annual volatility, 0.9 monthly persistence | 35% long-run annual volatility |
| Regime switching | bull +10%/12% volatility and bear -12%/25%, stay probabilities 96%/85% | stay probabilities 85%/95% |
| Jump diffusion | 4% monthly negative-jump probability, mean log jump -12% | 12% monthly jump probability |

These values are economically interpretable stress controls, not estimates
fitted to a historical asset. The
[attempt ledger](runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/path-attempts.jsonl)
retains every parameter, seed, horizon, path fingerprint, realized return,
volatility, drawdown, and regime/volatility/jump diagnostic before policy
performance is summarized.

## Primary 60-month observations

The table is the generated frictionless \(\lambda=0.75\) distribution slice.
Each cell has only three paths, so the median and interpolated 5% downside are
descriptive. Percentages use the named comparator as denominator. “Worst” is
the largest observed relative shortfall magnitude; zero means all three
observations were nonnegative.

| Family | Corrected vs DCA median | 5% downside | Worst | Corrected vs neutral median | 5% downside | Worst | Neutral vs DCA median |
|---|---:|---:|---:|---:|---:|---:|---:|
| Trend | -0.269% | -0.273% | 0.273% | +0.043% | +0.037% | 0.000% | -0.316% |
| Mean reversion | +0.111% | +0.097% | 0.000% | +0.071% | +0.037% | 0.000% | +0.040% |
| Stochastic volatility | -0.491% | -0.580% | 0.590% | +0.022% | +0.009% | 0.000% | -0.498% |
| Regime switching | -0.773% | -0.883% | 0.895% | -0.029% | -0.060% | 0.064% | -0.745% |
| Jump diffusion | +0.115% | -0.103% | 0.128% | +0.020% | +0.017% | 0.000% | +0.095% |

The complete system has mixed signs: median corrected-versus-DCA gaps are
positive for baseline mean reversion and jump diffusion, and negative for
trend, stochastic volatility, and regime switching. The signal-only comparison
is also not uniformly positive because the baseline regime construction has a
negative median and downside tail. Three seeds do not support a population
win rate or an expected-return claim.

Terminal attribution explains why the same carried cash can help or hurt. For
the primary trend corrected-versus-DCA cell, the mean cash contribution is
`+1015.595` while the evaluation-price value of the unit gap is `-1143.872`,
leaving a negative effect. For mean reversion the corresponding values are
`+894.404` and `-782.925`, leaving a positive effect. This is exactly the
ledger-conditioned cash/unit decomposition, not evidence that either process
will occur in a market. [^performance-boundary]

## Safety and coverage

At \(\lambda=1\), both guarded policies collapse transaction by transaction
to DCA on all 90 paths and three costs. [^guardrail-theorem] On the 60-month
primary frictionless paths, mean corrected-policy floor activation is roughly
30–32% at \(\lambda=0.9\), 10–11% at \(\lambda=0.75\), and 3.9% at
\(\lambda=0.5\). Lower coverage therefore leaves the selector unconstrained
more often in this grid. It does not produce a uniformly monotone performance
effect: for example, downside expands as coverage falls in the volatility and
regime baselines, while other families have different realized shapes.

At \(\lambda=0.75\), primary corrected-policy terminal cash drag averages
about 1.5–1.9% of deposits across families and terminal asset exposure is
about 98.3–98.4% of wealth. The complete
[aggregate data](runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/stochastic-aggregates.json)
retains mean and median relative gaps, downside quantiles, worst shortfall,
cash drag, exposure, activation, mean floor, purchase counts, fees, terminal
cash and units, cash/unit contributions, win/tie/loss counts, and every
episode-level effect-size value for all three comparisons.

## Exploratory sensitivity

The exploratory configurations remain separate and exhaustive. The same
60-month frictionless \(\lambda=0.75\) slice is:

| Family sensitivity | Corrected vs DCA median | 5% downside | Worst | Corrected vs neutral median | 5% downside | Worst | Neutral vs DCA median |
|---|---:|---:|---:|---:|---:|---:|---:|
| Negative trend | +0.659% | +0.633% | 0.000% | -0.037% | -0.085% | 0.090% | +0.674% |
| Faster mean reversion | +0.365% | +0.242% | 0.000% | +0.275% | +0.227% | 0.000% | +0.090% |
| Higher volatility | -0.021% | -0.159% | 0.174% | +0.252% | -0.065% | 0.100% | -0.272% |
| Persistent bear regime | +0.711% | -0.348% | 0.466% | +0.063% | -0.030% | 0.040% | +0.577% |
| More frequent jumps | +0.080% | -0.021% | 0.033% | -0.009% | -0.131% | 0.145% | +0.045% |

Sensitivity changes both signs and downside tails. These rows show dependence
on controlled process characteristics; they do not rank parameters, and none
replaces the primary baseline after outcome access.

## Accounting, costs, and failures

All 1,080 aggregate cells independently reconcile with the serialized episode
rows across every one of the 46 study fields and all 39 shared-runner fields:
49,684 study values and 42,124 runner values, including top-level counts, with
zero mismatches. The nested validation replays every causal prefix and passes
full funding, buy-only accounting, frictionless unit coverage, direct wealth,
terminal cash/unit identity, shared floors, and independent DCA accounting.
The complete compressed ledger keeps the original 104,897,868-byte SHA-256 in
its manifest.

Frictionless guarded results are the only rows labeled with the current
epsilon-DCA theorem. The 2,160 proportional- or fixed-cost ledgers are separate
net empirical results labeled `outside-current-safety-theorem`; they do not
inherit the guarantee. The completed run has zero failures and exclusions.
Focused executable checks also force invalid-configuration and runner-boundary
failures and verify that each leaves an immutable machine-readable receipt,
retained path attempts where available, and explicit declared, attempted,
included, and excluded counts.

## Reproduction

With CPython 3.12 and a fresh output directory:

```bash
python -m reproducibility.stochastic_study \
  --config experiments/protocols/safety-adaptivity-v1.json \
  --study experiments/inputs/seeded-stochastic-families-v1.json \
  --output-root /tmp/smartdca-stochastic-replay
```

Then run:

```bash
python -m unittest reproducibility.checks.check_stochastic_family_study
```

The checkpoint verifies all fingerprints and regenerates every substantive
artifact byte for byte under CPython 3.12; the outer manifest separately
records the installed interpreter patch version.

## Limitations

This study has three seeds per configuration, five deliberately simple process
families, one primary corrected-mean parameterization, and no calibration to a
historical asset. It supplies controlled sensitivity, implementation stress,
and mechanism attribution. It does not establish historical relevance,
stochastic optimality, statistical significance, causal superiority,
parameter superiority, expected outperformance, or universal performance.
The report stays draft until the effort's registered historical-slice review
gate is satisfied.

[^effort-spec]: Source join: [approved empirical effort specification](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md).
[^guarded-rule]: Source join: [canonical guarded-rule definition](../../research/definitions/guarded-corrected-mean-smartdca-rule.md).
[^guardrail-theorem]: Source join: [epsilon-DCA unit-coverage theorem](../../research/theorems/epsilon-dca-safety-unit-guardrail.md).
[^performance-boundary]: Source join: [arbitrary-horizon cash-and-units boundary](../../research/theorems/arbitrary-horizon-performance-boundary.md).
[^empirical-layers]: Source join: [empirical artifact-layer decision](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
[^stochastic-audit]: Source join: [stochastic study audit note](../../research/notes/seeded-stochastic-family-evaluation-audit.md).
