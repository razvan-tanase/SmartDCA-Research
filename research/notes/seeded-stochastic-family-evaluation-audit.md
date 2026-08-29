---
profile: smartdca-okf/0.4
type: research-note
title: "Audit of the seeded stochastic family evaluation"
description: "Generator, completeness, reconciliation, accounting, and scope audit for the controlled seeded stochastic SmartDCA study."
knowledge_role: evidence
status: draft
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-29T17:05:40Z
generation_run: urn:uuid:a06c30fa-7815-45d4-86da-84f01ac332cc
---
# Audit of the seeded stochastic family evaluation

## Audit target

This note audits the machine evidence behind the
[seeded stochastic experiment report](../../reports/experiments/seeded-stochastic-families.md).
It checks identity, generator scope, grid completeness, failure retention,
policy accounting, aggregate reconciliation, and interpretive limits. The
outcomes remain controlled synthetic sensitivity evidence, not historical
evidence and not a stochastic performance theorem.

The immutable inputs and code identities are:

- frozen protocol SHA-256
  `a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4`;
- saved stochastic-study SHA-256
  `2992939272c9d2bc2eeeea132e9c8808cb4363f33537c5ad0b54bece9aa2297d`;
- generated shared-runner input SHA-256
  `30873d39a2ded4de44143b1fcf59c879b90cfede97193b89add951bf69ea4bb6`;
- stochastic generator/source SHA-256
  `4c0ca98ee52de514b6d56a795e1ea0e35766162847d29556fcbd2fc4d5e15ffa`;
- shared empirical-runner SHA-256
  `7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`;
  and
- CPython `3.12.14`, with no third-party dependency.

Together they identify
[`smartdca-stochastic-v1-73994b28bd930d35548d60497921065f5a6320068a2f371374238587a6faf065`](../../reports/experiments/runs/smartdca-stochastic-v1-73994b28bd930d35548d60497921065f5a6320068a2f371374238587a6faf065/manifest.json).

## Generator contract

The generator uses `random.Random`'s MT19937 uniform stream and an explicit
Box--Muller transform. One configuration and seed generate a 60-month path;
the 12- and 36-month episodes are exact prefixes, including their evaluation
prices. Prices are rounded to twelve decimal places before entering the policy
runner. Every path receipt records the generator version, complete parameters,
seed, full-path and horizon-path hashes, annualized realized return and
volatility, maximum drawdown, price range, and construction-specific
diagnostics.

The five constructions are deliberately small controlled models:

1. geometric log-price diffusion with fixed annual drift and volatility;
2. a discrete log-price autoregression whose coefficient is determined by a
   declared half-life around a fixed long-run price;
3. log volatility following a stationary AR(1), with its current volatility
   driving the next diffusion return;
4. a two-state Markov bull/bear return process with declared state-specific
   drift, volatility, and stay probabilities; and
5. diffusion plus Bernoulli jump arrival and a normally distributed log-jump
   size.

These are interpretable sensitivity constructions, not calibrated structural
models of SPY or Bitcoin. The saved
[study design](../../experiments/inputs/seeded-stochastic-families-v1.json)
keeps one baseline and one exploratory sensitivity per family distinct and
uses common saved seeds `104729`, `130363`, and `155921`.

## Completeness and failures

The declared product is ten generator configurations, three seeds, and three
horizons: 90 path attempts. All 90 generated successfully. No generator,
configuration, input-validation, numerical, policy-runner, or comparison
exclusion occurred in the durable run. The
[attempt ledger](../../reports/experiments/runs/smartdca-stochastic-v1-73994b28bd930d35548d60497921065f5a6320068a2f371374238587a6faf065/path-attempts.jsonl)
still records a typed status and exclusion fields for every attempt; the
executable contract separately exercises and retains a numerical generator
failure rather than assuming the zero count.

Each generated episode executes four primary coverage levels, the one primary
corrected-mean configuration, three costs, and three policies. That produces
3,240 complete ledgers and 3,240 comparison rows covering corrected versus
DCA, corrected versus neutral guarded, and neutral guarded versus DCA. The
complete ledger artifact is deterministically gzip-compressed to 22,801,162
bytes. Its nested manifest preserves the uncompressed length `104897868` and
SHA-256
`57097fc58571bf5bbdf028ab08d140fa9c77f0e3e5768cd28f5dad84d0e06ba5`.

## Accounting and reconciliation

The shared-runner validation receipt passes full funding, all truncated causal
prefix replays, buy-only behavior, direct terminal-wealth accounting,
frictionless unit coverage, terminal cash/unit identity, transaction-level
collapse at \(\lambda=1\), shared guarded-policy floors, independent DCA
accounting, and theorem-scope separation. It checks 270 lambda-one scenario
groups. Only frictionless guarded ledgers carry the epsilon-DCA theorem scope;
the 2,160 cost-adjusted ledgers are labeled
`outside-current-safety-theorem`.

Study aggregates are recomputed from the serialized episode rows after the
shared runner has finished. The independent route reconciles 27 fields in each
of 1,080 cells against the serialized shared-runner aggregates, with zero
mismatches. It also adds the retained generator-attempt denominator,
exclusion reasons, complete relative-gap distribution, worst observed relative
shortfall, cash and unit contributions, and identity residual. The
[reconciliation receipt](../../reports/experiments/runs/smartdca-stochastic-v1-73994b28bd930d35548d60497921065f5a6320068a2f371374238587a6faf065/aggregate-reconciliation.json)
is therefore an independently implemented consistency check, not a copy of
the runner aggregate object.

## Interpretation audit

The generated results show mixed signs across families and sensitivities. At
the displayed 60-month, frictionless \(\lambda=0.75\) slice, neither the
complete corrected system nor the corrected-versus-neutral signal has one
sign across all primary families. That observation is a finite description of
three seeds per configuration. It does not estimate a market frequency,
expected advantage, causal effect, optimal parameter, or universal outcome.

Lowering coverage visibly changes floor activation and the realized downside
in the complete figure-ready grid, but the changes are not uniformly monotone
across families. The correct conclusion is sensitivity to the chosen process,
seed, horizon, and safety factor—not a stochastic optimum. Exploratory rows
remain labeled and exhaustive; they cannot replace or be pooled silently into
the primary rows.

## Reproduction

From a clean checkout with CPython 3.12, regenerate the bundle into a new empty
directory:

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

The checkpoint validates the public contract, manifest and compressed-ledger
fingerprints, report claims, and a clean replay whose substantive artifacts
are byte-identical across the declared CPython 3.12 runtime. The outer manifest
retains the installed patch version as an environment receipt. This note stays
draft until the ticket review is recorded; the experiment report also remains
draft under the effort-wide historical-slice promotion gate.
