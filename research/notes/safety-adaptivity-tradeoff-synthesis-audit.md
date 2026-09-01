# Audit of the safety-adaptivity trade-off synthesis

## Audit target

This note records the detailed evidence and claim reconstruction behind the
[cross-layer synthesis report](../../reports/experiments/safety-adaptivity-tradeoff-synthesis.md).
The machine target is immutable run
[`smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26`](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/manifest.json),
generated from the versioned [synthesis
manifest](../../experiments/inputs/safety-adaptivity-synthesis-v1.json).

The audit asks four questions:

1. Did the synthesis admit only reviewed source runs and exact accepted bytes?
2. Can every reported value be reconstructed from episode-reconciled source
   aggregates without pooling incompatible units?
3. Are the complete system, corrected-mean signal, and safety architecture
   kept distinct across evidence layers, costs, and analysis tiers?
4. Does the conclusion preserve the mathematical and empirical claim
   boundaries?

## Reviewed source gate

The input manifest names four accepted source identities:

| Layer | Reviewed run | Aggregate cells | Episode-level reconciliation |
|---|---|---:|---|
| Deterministic | `smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db` | 648 | Public episode rows and all generated artifacts were independently replayed. |
| Stochastic | `smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25` | 1,080 | Public episode rows were independently regrouped across all declared fields. |
| Historical primary | `smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221` | 216 | Private episode rows are retained by receipt and were independently reconciled to the public aggregates. |
| Historical robustness | `smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184` | 810 | Private monthly and quarterly rows are retained by receipt and were independently reconciled to the public aggregates. |

For each source, the synthesis validates the exact outer manifest, run ID,
manifest schema, selected aggregate artifact and count, review record, and
required pass markers. It also verifies source-bound deposit evidence and the
declared aggregate-reconciliation artifact for all four sources; the primary
historical source additionally verifies its registered uncertainty artifact.
The selected aggregate, reconciliation, and uncertainty hashes must be bound
by the source manifest, and the deposit-evidence hash must match its declared
source-manifest field. `review_status` must equal `pass`; a pending status
fails before an output root is created.

The [source-validation
receipt](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/source-validation.json)
records four accepted sources, zero rejected sources, and 2,754 normalized
aggregate rows. It also fingerprints the canonical theorem, evidence note, and
executable check for universal dominance impossibility, the epsilon-DCA
guardrail, and the terminal-inventory boundary. This makes the empirical and
mathematical inputs to the thesis conclusion explicit.

## Normalization and non-pooling rule

The generated [normalized
evidence](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/normalized-evidence.csv)
retains source ID, run ID, evidence layer, analysis and design tier, schedule,
dataset or family, generator configuration, horizon, coverage, cost and theorem
scope, comparison and comparison role, sample counts, relative wealth and
downside, cash drag, exposure, floor-activation frequency, raw mean guardrail
floor, guardrail floor per reviewed deposit, purchases, and cash/unit
attribution. No row is relabeled into a different comparison.

The synthesis summarizes source aggregate cells, not a pooled collection of
episodes. A deterministic family, a stochastic family median over three
seeds, and a historical dataset-horizon cell are not exchangeable sampling
units. The safety-factor output therefore reports a descriptive median across
source cell medians plus cell ranges. It carries minimum and maximum source
sample counts rather than adding overlapping or otherwise incomparable sample
counts. Every generated table states that its ranges are not independent-
sample intervals.

## Numerical reconstruction

The [cross-layer
summary](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/cross-layer-summary.csv)
contains 15 rows: the three policy comparisons for each of five declared
evidence slices. Its central receipts are:

- deterministic primary catalog at frictionless \(\lambda=0.75\): complete
  system `9/1/4`, signal `5/1/8`, and architecture `10/1/3` negative/zero/
  positive median signs across 14 fixed paths;
- stochastic primary 60-month baselines at frictionless \(\lambda=0.75\):
  complete system `3/0/2`, signal `1/0/4`, and architecture `3/0/2` signs
  across five family cells, each based on three saved seeds;
- historical primary non-unit frictionless cells: complete system `18/0/0`,
  signal `17/0/1`, and architecture `18/0/0` signs; and
- registered historical robustness: 30 negative monthly complete-system and
  signal medians, 48 negative quarterly complete-system medians, and 40
  negative plus eight positive quarterly signal medians.

The primary historical ranges reconstruct to `-4.593%` through `-0.335%` for
H1, `-0.545%` through `+0.052%` for H2, and `-4.365%` through `-0.340%` for the
secondary architecture comparison. The uncertainty join contains exactly 36
registered cells. Nine H1 and zero H2 cells have Holm-adjusted p-values below
0.05. Architecture and robustness cells receive no synthetic p-value or
interval.

The [safety-factor
curve](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/safety-factor-curve.csv)
contains 81 rows across five non-pooled slices and all three comparisons. Each
row carries relative wealth, 5% downside, worst observed shortfall, cash drag,
asset exposure, guardrail-activation frequency, mean guardrail floor divided by
the reviewed per-period deposit, purchase count, and cash and unit-value
contributions divided by the cell's total contributed capital. Raw dollar and
terminal-unit components remain only in normalized source-cell rows. The
generated SVGs read only the dimensionless summary rows. A separate [cost-scope
summary](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/cost-scope-summary.csv)
contains 48 tier-separated non-unit net-cost rows and never receives the frictionless theorem
label.

Within each source aggregate cell, `mean_left_guardrail_floor` averages every
scheduled purchase step, including zero floors. Dividing it by the constant
reviewed per-period deposit gives that cell's unconditional average mandatory
floor per contribution event, equivalently its total guardrail floors divided
by its total contributed capital. The plotted point is the unweighted median
of the retained cell ratios rather than a pooled slice-level ratio. It is
deliberately not a conditional size given activation; the separate activation-
frequency series reports how often the floor binds.

The [summary-reconciliation
receipt](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/summary-reconciliation.json)
matches the 2,754 input cells to 2,754 normalized rows, 15 cross-layer rows, 81
safety-factor rows, and 48 cost rows. At source-cell grain, cash plus
evaluation-price unit contribution reconstructs the mean wealth gap with
maximum absolute residual `6.88e-54`; the dimensionless contributions satisfy
the same identity after division by total contributed capital. Generated
tables set `manual_numeric_transcription=false`.

## Safety and attribution audit

All 594 source aggregate cells at \(\lambda=1\) have zero mean and median gap.
The source validations behind them independently check transaction-level
collapse rather than terminal equality alone. Across 612 frictionless cells
for corrected-versus-DCA or neutral-versus-DCA, no observed minimum relative
gap is below \(\lambda-1\). This is a finite regression audit of the proved
[epsilon-DCA unit guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md),
not a substitute for its proof.[^guardrail]

Cash/unit attribution follows the accepted
\(W^c-W^T=H_T+P U_T\) identity. Positive carried cash does not determine the
sign because the evaluation-price unit component can dominate. Every primary
historical H1 cell has a positive mean cash component and a negative mean unit
component, with a negative total. Deterministic and stochastic cells include
both total signs. This supports a ledger-conditioned timing interpretation and
rules out describing cash drag, guardrail activation, or the corrected score as
a standalone causal performance explanation.[^inventory]

## Analysis tiers and dependence

Only primary historical H1 and H2 are confirmatory. The circular moving-block
bootstrap samples ordered monthly episode starts in horizon-length blocks and
therefore carries the preregistered overlapping-window dependence into the
interpretation. Its cellwise percentile intervals are not multiplicity
adjusted; the centered two-sided tests enter one 36-cell Holm family. H2's zero
rejections do not establish equivalence.

Neutral-versus-DCA, \(\lambda=1\), mechanisms, downside, exposure, purchases,
and attribution are secondary. The post-confirmatory coverage and quarterly
extensions are registered robustness with `uncertainty_status=not-run-
robustness`. Stochastic exploratory configurations and the deterministic
design iteration retain their labels. The historical bundle contains no
post-hoc regime analysis. Net-of-cost rows are robustness evidence outside the
current safety theorem. In particular, each BTC-USD 120-month quarterly cell
contains only four eligible episodes; these sparse cells support descriptive
sensitivity checks only.

## Cross-layer interpretation

The layers agree on mechanism and disagree on realized sign. Deterministic
paths prove neither frequency nor expectation, but show both favorable and
adverse complete-system, architecture, and signal outcomes. Controlled
stochastic baselines and sensitivities likewise change signs with process,
seed, horizon, and coverage. The uniformly negative historical primary result
is therefore compatible with both layers without being predicted by either.
It is also compatible with epsilon-DCA safety because a relative floor permits
losses against DCA above the floor.

The defensible thesis chain is:

1. in the project's causal, long-only, buy-only, fully funded, same-deposit,
   cash-inclusive comparison model over every finite positive price path,
   universal dominance forces transaction-level DCA;[^impossibility]
2. the sharp epsilon-DCA guardrail weakens dominance to a chosen frictionless
   relative-wealth floor and assigns only the residual funded interval to the
   score;[^guardrail]
3. the arbitrary-horizon terminal-inventory boundary explains each realized
   gap from terminal cash and units without supplying its sign;[^inventory]
4. the empirical evidence verifies the floor and accounting across the frozen
   grid, but finds path-sensitive synthetic behavior, uniformly negative
   primary historical complete-system medians, and no multiplicity-adjusted H2
   evidence of incremental corrected-mean value.

This conclusion does not claim universal inferiority, stochastic optimality,
parameter ranking, expected return, or causal market effect. It describes an
experimentally evaluated architecture with a proved floor in the frictionless
theorem model whose selected adaptive score has not earned a return-improvement
claim in this study.

## Limitations and future boundary

The synthesis inherits every source limitation: one primary corrected-mean
configuration; finite deterministic and stochastic catalogs; three seeds per
stochastic configuration; two historical proxy series from the reviewed Yahoo
Finance seam; overlapping windows; private source-bearing historical rows;
six horizons across two deposit cadences; and two simple fee models.[^provider]
Robustness rows have no dependence-aware interval, and the four registered
alternate corrected-mean configurations remain unexecuted. The BTC-USD
120-month quarterly cells have only four eligible episodes each, so their
values are especially sample-limited even within the descriptive robustness
boundary.

Future empirical questions may test a separately specified selector, new
point-in-time sources, non-overlapping holdout periods, or the deferred
parameter grid. A dynamic guardrail, restricted-price theorem, or cost-aware
safety guarantee changes the mathematical model or policy and must be proposed
and reviewed in a separate effort. The synthesis does not promote a
deterministic or stochastic pattern into such a regime.

## Pre-acceptance artifact history

Six earlier bundles remain preserved under the versioned-artifact policy.
They are not accepted evidence targets:

| Run | Why superseded before acceptance |
|---|---|
| [`090c3fd…`](../../reports/experiments/runs/smartdca-synthesis-v1-090c3fdaf0c14f9b0b26e8d00c83bf0de9b42fe2d39681af961d6343d4c5e139/manifest.json) | Pooled cost tiers and allowed \(\lambda=1\) rows into non-unit cost summaries. |
| [`008df6c…`](../../reports/experiments/runs/smartdca-synthesis-v1-008df6c68b700cd8018db3bb39f883b7a71b150e0b7f4898dfdf49c8bbc2f12b/manifest.json) | Split cost tiers, but still allowed \(\lambda=1\) rows into non-unit selection. |
| [`1c91131…`](../../reports/experiments/runs/smartdca-synthesis-v1-1c91131f95c892a4a9fc0f7bb40981e52e51bce9fce0c1e1dfac2f6a00a97aba/manifest.json) | Fixed non-unit selection, but did not yet require every source's reconciliation evidence. |
| [`925e43d…`](../../reports/experiments/runs/smartdca-synthesis-v1-925e43d48057dfc62627b34c950fbe5688faac05be7ca047a548a18bd7bddf39/manifest.json) | Pre-review candidate with raw-attribution pooling, analysis-tier, and claim-wording defects. |
| [`ec3d271…`](../../reports/experiments/runs/smartdca-synthesis-v1-ec3d271c5ad0e7ff3abea196cec598b9f3fed24d3eaa1ddc955ba12170dd070a/manifest.json) | Pre-acceptance candidate superseded by the final complete-system and architecture claim-precision edit. |
| [`7fec8cf…`](../../reports/experiments/runs/smartdca-synthesis-v1-7fec8cfa6ed5691fe01e168927a67b55e1ea81d02313716184d334d31178b568/manifest.json) | Domain-reviewed candidate superseded after Standards review found patch-version-dependent manifest bytes and specification review found omitted guardrail floor size. |

Run `smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26`
is the only candidate submitted for acceptance. Preserving the earlier bytes
records the correction path without treating any superseded result as current.

## Independent domain review

An independent domain reviewer who did not participate in drafting or
implementation re-audited exact candidate
`smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26`.
The reviewer independently reconstructed the specification hash, generator
hash, CPython 3.12 runtime identity, run ID, artifact inventory, and all
artifact hashes, and reproduced all 13 bundle files byte for byte.

The reviewer matched all 2,754 raw guardrail-floor values to their reviewed
source aggregates, verified every deposit-normalized ratio and its
\(0\le m/d\le\lambda\) bound, and independently reconstructed all 81 curve
medians. The normalized metric is an unconditional mean over scheduled
contribution events, including inactive zero-floor steps; within each cell it
equals total floors divided by total contributed capital, while plotted points
remain unweighted medians of cell ratios rather than pooled schedule totals.

The reviewer also confirmed that the prior claims, cross-layer counts,
uncertainty family, theorem boundary, tier separation, cost scope, cash/unit
reconciliation, sparse-cell disclosure, SVG semantics, and six superseded
bundle identities remain unchanged and accurate. Runtime checks cover patch-
metadata normalization and bind both implementation and major/minor version to
identity.

Result: **pass**, with no blocking scientific issue. No nonblocking issue
remains.

## Reproduction

Run:

```bash
python3.12 -m reproducibility.safety_adaptivity_synthesis \
  --manifest experiments/inputs/safety-adaptivity-synthesis-v1.json \
  --output-root /tmp/smartdca-synthesis-replay
python3.12 -m unittest \
  reproducibility.checks.check_safety_adaptivity_synthesis
```

The public checkpoint compares two clean executions byte for byte, validates
the manifest inventory and all artifact fingerprints, checks the exact
cross-layer receipts above, rejects non-pass review status, and confirms the
no-overwrite identity rule.

[^impossibility]: Theory join: [causal DCA dominance impossibility](../theorems/causal-dca-dominance-impossibility.md) and [detailed evidence](pathwise-dca-dominance-under-causal-budget.md).
[^guardrail]: Safety join: [epsilon-DCA unit-coverage theorem](../theorems/epsilon-dca-safety-unit-guardrail.md) and [detailed evidence](sharp-epsilon-dca-safety-guardrail.md).
[^inventory]: Attribution join: [arbitrary-horizon performance boundary](../theorems/arbitrary-horizon-performance-boundary.md) and [detailed evidence](arbitrary-horizon-performance-boundary.md).
[^provider]: External-source boundary: [Yahoo Finance provider review](yahoo-finance-historical-data-provider-review.md).
