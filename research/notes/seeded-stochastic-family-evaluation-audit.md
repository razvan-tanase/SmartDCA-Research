# Audit of the seeded stochastic family evaluation

## Audit target

This note audits the machine evidence behind the
[seeded stochastic experiment report](../../reports/experiments/seeded-stochastic-families.md).
It checks identity, generator scope, grid completeness, failure retention,
policy accounting, aggregate reconciliation, and interpretive limits. The
outcomes remain controlled synthetic sensitivity evidence, not historical
evidence and not a stochastic performance theorem.
[^effort-spec]

The immutable inputs and code identities are: [^run-evidence]

- frozen protocol SHA-256
  `a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4`;
- saved stochastic-study SHA-256
  `2992939272c9d2bc2eeeea132e9c8808cb4363f33537c5ad0b54bece9aa2297d`;
- generated shared-runner input SHA-256
  `30873d39a2ded4de44143b1fcf59c879b90cfede97193b89add951bf69ea4bb6`;
- stochastic generator/source SHA-256
  `af4484cd2774a7e31394a4f17aaf533f9e9d759037f788d59ce84d0c2412d41e`;
- shared empirical-runner SHA-256
  `7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`;
  and
- CPython `3.12.14`, with no third-party dependency.

Together they identify
[`smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25`](../../reports/experiments/runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/manifest.json).

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
[attempt ledger](../../reports/experiments/runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/path-attempts.jsonl)
records a typed status and exclusion fields for every attempt. Focused contract
checks separately force and retain a numerical generator failure, an invalid
saved configuration, and a runner-boundary failure rather than assuming the
durable run's zero counts. Pre-execution and runner failures leave immutable
failure receipts with declared, attempted, generated, included, and excluded
sample counts; generated path attempts are retained when available.

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
shared runner has finished. A second route independently regroups those rows
and the attempt ledger, then reconciles every one of the 46 study fields in
all 1,080 cells and all 39 fields in the corresponding shared-runner cells.
That covers 49,684 study values and 42,124 runner values after their four
respective top-level counts, including attempted/generated/excluded counts,
exclusion reasons, complete relative-gap distributions, downside and worst
shortfall, cash and unit contributions, and identity residual. The
[reconciliation receipt](../../reports/experiments/runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/aggregate-reconciliation.json)
records zero mismatches. Focused corruption probes cover each previously
omitted category, so the receipt is an independently implemented consistency
check rather than a copy of either aggregate object.

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
retains the installed patch version as an environment receipt. The ticket
review and effort-wide historical-slice promotion gate are now satisfied by
the reviewed [historical-data
seam](../../reports/experiments/historical-data-episode-seam.md). This note and
its experiment report are stable controlled-simulation evidence for later
synthesis, without changing their scientific claim boundary.

[^effort-spec]: Source join: [approved empirical effort specification](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md).
[^run-evidence]: Source join: the [saved stochastic study](../../experiments/inputs/seeded-stochastic-families-v1.json), [generator and orchestration source](../../reproducibility/stochastic_study.py), and [immutable run manifest](../../reports/experiments/runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/manifest.json).
