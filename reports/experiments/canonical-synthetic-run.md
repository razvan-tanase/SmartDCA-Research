# Canonical synthetic safety-adaptivity run

## Verdict

The frozen empirical protocol executes end to end through one public runner.
From exact configuration and input bytes it derives a deterministic run
identity and emits a manifest, 36 complete policy ledgers, 36 comparison
records, 36 aggregate groups, two report-ready tables, and ten passed
validation receipts. The run exercises independent DCA accounting, the shared
guarded-policy contract, a nontrivial safety factor, the
\(\lambda=1\) collapse, and frictionless, fixed-fee, and proportional-fee
routes.[^effort-spec][^guarded-rule]

This is a mechanism and infrastructure checkpoint, not an empirical
performance result. Its only input is one hand-authored, non-confirmatory path;
it estimates no sampling uncertainty and supports no claim that any policy is
superior in a population, stochastic model, or historical market.

## Frozen protocol boundary

The immutable protocol is
[`safety-adaptivity-v1.json`](../../experiments/protocols/safety-adaptivity-v1.json),
SHA-256
`a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4`.
It was registered at `2026-08-25T08:11:32Z` with
`confirmatory_outcomes_accessed=false`. Before any confirmatory outcome access,
it fixes:

- Alpha Vantage `TIME_SERIES_DAILY_ADJUSTED` for SPY adjusted close and
  `DIGITAL_CURRENCY_DAILY` for BTC/USD spot close, including exact request,
  asset, timezone, cutoff, byte-preservation, fingerprint, and versioning
  semantics;
- monthly first-eligible-observation deposits of USD 1,000, exactly \(H\)
  deposits before each \(H\)-month horizon date, every eligible first-of-month
  rolling start, exact evaluation-date mapping, asset-specific missing-data
  tolerances, and no interpolation;
- primary coverage \(\lambda\in\{1,0.9,0.75,0.5\}\), a five-value robustness
  grid, one primary corrected-mean configuration, and four robustness
  configurations;
- frictionless, 10-basis-point proportional, and USD 1 fixed-fee routes;
- two confirmatory hypotheses, one secondary comparison, primary and secondary
  estimands, exclusions, and distinct confirmatory, secondary, robustness, and
  exploratory tiers; and
- one family of 36 two-sided confirmatory tests controlled by Holm at 0.05,
  with a 10,000-replicate circular moving-block bootstrap seeded by `20260825`
  and block length equal to the episode horizon. The registration also fixes
  cell-specific seed derivation, circular remainder truncation, the percentile
  interpolation rule, the centered two-sided tail formula with its finite-run
  correction, and deterministic Holm tie order.

The protocol states that changing a confirmatory dataset, hypothesis,
estimand, grid, or inference choice after outcome access requires a new
protocol identity. Both historical datasets remain
`selected-not-retrieved`; neither price series nor a derived historical policy
outcome was inspected in this run.

The initial feature-branch artifacts were provisional until independent
review. Outcome-blind review corrections are recorded in [the originating
ticket](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/01-preregister-protocol-establish-canonical-run.md),
and Git retains their byte history. The accepted fingerprints below close that
first-publication correction window. Any later byte change requires a new
version under the empirical artifact decision.[^empirical-layers]

## Run contract and identity

The public interface is
[`reproducibility.empirical`](../../reproducibility/empirical.py):
`StudyConfig` and `VersionedInput` validate immutable exact bytes, while
`run_experiment(config, inputs, output_root)` returns the completed `RunBundle`.
The command-line interface calls the same seam:

```bash
python -m reproducibility.empirical \
  --config experiments/protocols/safety-adaptivity-v1.json \
  --input experiments/inputs/canonical-synthetic-v1.json \
  --output-root "$(mktemp -d)"
```

The run identity hashes engine version
`smartdca-empirical-runner/1`, the runner source, and the exact protocol and
input bytes. The canonical identity is
`smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0`.
The [manifest](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/manifest.json)
records runner SHA-256
`7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`
and input SHA-256
`4609770766e74ee38df70e8c0b6f48412544dbba431a91a2612366dec8f6bddb`.
It also fingerprints every emitted artifact. CPython 3.12 and the standard
library are the complete runtime dependency set. The protocol, input, bundle,
and report occupy distinct immutable or versioned layers under the repository's
empirical artifact decision.[^empirical-layers]

An existing directory with the same deterministic identity is a typed
pre-execution collision. Invalid schemas, prices, coverage, corrected-mean
parameters, dates, costs, and identities likewise expose stable typed reasons
before any policy executes.

## Canonical input and outputs

The versioned
[`canonical-synthetic-v1.json`](../../experiments/inputs/canonical-synthetic-v1.json)
contains five monthly USD 1,000 deposits at prices
\((100,150,80,130,90)\) and a common evaluation price of 120. It is marked
`confirmatory=false`, `method=hand-authored`, `seed=null`, and
`historical_observations_used=false`.

The canonical bundle contains:

| Artifact | Contents | SHA-256 |
|---|---|---|
| [`manifest.json`](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/manifest.json) | Identity, input receipts, runtime, artifact fingerprints | `cc229e251b9d79cbb50c6f0e5840fb351bbc872e84d19ac438e06f67ae4dd8d1` |
| [`ledgers.jsonl`](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/ledgers.jsonl) | 36 complete DCA, neutral, and corrected ledgers | `fc7928746bbcd53627c20816de55123e9030eadf9527e9c4a4bd477c7b00bb0b` |
| [`validation.json`](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/validation.json) | Ten validation receipts | `150bf341da9da049807a9f5aa136ccdd01242eadf7f91b8094d6624f478fd35f` |
| [`episode-results.jsonl`](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/episode-results.jsonl) | 36 pairwise episode estimands | `24133bbda44b39dff02fd4bae05e0c27a9080f2ec7b07e757e2e0a0bc82266b1` |
| [`aggregates.json`](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/aggregates.json) | 36 single-episode aggregate groups | `6e57e0ef7a9a96a4362a2bb628459f70ca20171a1783d8ba85f863206703d58c` |
| [`policy-summary.csv`](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/policy-summary.csv) | Report-ready policy table | `11745bfbd7425545b8fb5a123da0ef76450c22efbf5e70dba6e22f7d99d5fe69` |
| [`figure-ready.csv`](runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/figure-ready.csv) | Report-ready comparison data | `cb32572b7fc255c54646d0777f172a5cec3174026a4ad1a7195033b48858f5c5` |

Every ledger records deposits, selected purchases, asset notionals, fees, cash,
units, corrected references where applicable, scores, guardrail floors, floor
activation, coverage, terminal wealth, and terminal cash/unit attribution.
DCA has its own accounting path. Neutral and corrected ledgers use the same
guardrail implementation and differ only in their discretionary selector.
Each comparison also records an included/excluded status and a machine-readable
reason; a nonpositive comparator remains in raw results but contributes to no
aggregate effect, win, tie, or loss statistic.

## Validation receipts and bounded observation

All ten receipts pass: full funding, causal prefix replay, buy-only behavior,
frictionless unit coverage, direct wealth accounting, terminal cash/unit
identity, \(\lambda=1\) collapse, shared guardrail contract, independent DCA
accounting, and cost-scope separation.[^guardrail-theorem][^performance-boundary]
The 24 cost-adjusted ledgers are explicitly marked
`outside-current-safety-theorem`; only the 12 frictionless ledgers carry the
current epsilon-DCA theorem scope.

At \(\lambda=1\), all three policies coincide under every cost route. The
frictionless collapse is theorem-backed; fixed and proportional cost collapse
is a checked invariant of this accounting extension, which remains outside the
theorem. At the nontrivial \(\lambda=0.75\) frictionless seam, the
corrected selector produces nonconstant scores and repeated active floors.
On this one path its relative terminal-wealth gaps are approximately 1.87%
against DCA and 2.18% against the neutral selector, while the neutral selector
is approximately 0.31% below DCA. These values demonstrate that the selector,
floor, ledger, and estimand routes are non-degenerate. They are not estimates,
tests, or evidence of policy superiority.

## Executable regression and limits

Run the complete checkpoint with:

```bash
python -m unittest reproducibility.checks.check_empirical_protocol_canonical_run
```

The 16-test suite checks the committed bundle byte for byte, caller decimal-
context independence, typed pre-execution failures, CLI behavior, all
estimand-to-aggregate fields, and exact-rational named cases covering two
purchases, the three-purchase beta flip, constant prices, repeated floor
activation, and \(\lambda=1\).

No historical, stochastic, adversarial-family, bootstrap, or multiplicity run
has occurred. The canonical path has one episode, so its aggregate quantiles,
medians, and win/tie/loss counts merely restate that path. Later tickets must
create the declared evidence layers without editing this registration.

[^effort-spec]: [Safety-adaptivity empirical evaluation specification](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../../research/definitions/guarded-corrected-mean-smartdca-rule.md)
[^guardrail-theorem]: [Epsilon-DCA safety is exactly a causal unit-coverage guardrail](../../research/theorems/epsilon-dca-safety-unit-guardrail.md)
[^performance-boundary]: [Terminal cash and units give the exact arbitrary-horizon performance boundary](../../research/theorems/arbitrary-horizon-performance-boundary.md)
[^empirical-layers]: [Place empirical protocols, inputs, and run bundles in versioned layers](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md)
