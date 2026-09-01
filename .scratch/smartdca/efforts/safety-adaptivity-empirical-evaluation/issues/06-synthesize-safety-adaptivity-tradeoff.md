# 06 — Synthesize the empirical safety-adaptivity trade-off

Type: research
Status: resolved
Blocked by: 02, 03, 05
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

What defensible conclusion about guarded SmartDCA's safety-adaptivity trade-off
is supported jointly by the deterministic, stochastic, and confirmatory
historical evidence, and how much observed behavior belongs to the guardrail
versus the corrected-mean signal?

## What to build

A thesis author can regenerate one integrated evidence package containing the
approved primary tables, figures, terminal cash/unit attribution, cross-layer
comparisons, limitations, and concise conclusions for the complete system,
safety architecture, and corrected-mean signal without manually transcribing
results or promoting exploratory patterns to confirmed claims.

## Acceptance criteria

- [x] The synthesis consumes only reviewed run manifests and reconciles every cited number with deterministic, stochastic, or historical episode-level evidence.
- [x] Complete-system performance, signal contribution, and safety-architecture behavior remain separate throughout tables, figures, and prose.
- [x] The safety-factor curve reports relative wealth, downside, cash drag, exposure, guardrail activation frequency and mean floor size, purchase activity, and terminal cash/unit attribution across the declared evidence layers.
- [x] Gross frictionless safety findings and net-of-cost empirical findings remain visually and verbally distinct.
- [x] Confirmatory hypotheses, secondary analyses, robustness checks, and exploratory regime observations are labeled consistently and respect the preregistered multiplicity boundary.
- [x] Historical uncertainty and overlapping-window dependence are carried into the integrated interpretation rather than replaced by naive independent-sample claims.
- [x] All primary tables and figure-ready data are generated from one versioned synthesis manifest using the same reviewed aggregates as the prose.
- [x] The synthesis explains where deterministic mechanisms agree or disagree with stochastic and historical observations, including null, negative, or parameter-sensitive results.
- [x] The central thesis conclusion connects impossible universal dominance, the sharp epsilon-DCA guardrail, the arbitrary-horizon terminal-inventory boundary, and measured adaptive behavior without claiming optimality or universal superiority.
- [x] Limitations and empirically motivated future questions are stated beside the findings, and any proposed new mathematical regime is left for a separately specified effort.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This is the first ticket that requires all three empirical evidence layers.
- Claimed on `main` on 2026-09-01 after confirming tickets 02, 03, and 05 are
  resolved and no other effort ticket is claimed.
- Pre-acceptance generation first preserved five superseded run identities:
  `090c3fd…` corrected cost-tier pooling and \(\lambda=1\) leakage;
  `008df6c…` corrected the remaining \(\lambda=1\) leakage; `1c91131…`
  added all-source reconciliation gates; `925e43d…` corrected raw-attribution
  pooling, tier labels, and claim wording; and `ec3d271…` preceded the final
  complete-system and architecture claim-precision edit. The linked synthesis
  audit records their full identities and preserves every bundle as
  pre-acceptance history rather than accepted evidence.
- Initial independent domain review audited candidate
  `smartdca-synthesis-v1-7fec8cfa6ed5691fe01e168927a67b55e1ea81d02313716184d334d31178b568`,
  its source gates, generated tables and figures, tier and cost boundaries,
  theorem joins, sparse-cell disclosure, and artifact history. It passed with
  no blocking scientific issue after one audit-only wording correction made
  clear that deposit and reconciliation evidence is required for all four
  sources while registered uncertainty is primary-historical-specific.
- Parallel Standards and specification review then superseded `7fec8cf…`:
  Standards found patch-version-dependent runtime metadata outside the run
  identity, while specification review found that the synthesis omitted
  guardrail floor size. Candidate `394aa4d…` binds the normalized runtime
  family into its identity and reports mean floor size per deposit throughout
  normalized data, curve summaries, generated tables, the mechanism SVG, and
  the public checkpoint.
- Final independent domain re-review accepted exact candidate
  `smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26`
  with no blocking or nonblocking scientific issue. It reconstructed the run
  identity and all 12 artifact hashes, reproduced all 13 files byte for byte,
  matched all 2,754 guardrail floors and deposit-normalized ratios to reviewed
  source aggregates, and independently recomputed all 81 curve medians. The
  audit note records the full review and all six superseded identities.

## Answer

Resolved. One versioned [synthesis
manifest](../../../../../experiments/inputs/safety-adaptivity-synthesis-v1.json)
now regenerates immutable run
[`smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26`](../../../../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/manifest.json).
It accepts only the four exact reviewed source runs, reconciles all 2,754
aggregate cells, and generates 15 cross-layer rows, 81 safety-factor rows, 48
tier-separated net-cost rows, four SVGs, primary tables, and machine-readable
claim receipts without manual numerical transcription. The mechanism outputs
include both guardrail activation frequency and mean floor size per deposit.

The integrated result supports safety without empirical superiority. The
proved guardrail supplies the frictionless floor and collapses to DCA at
`lambda=1`; realized complete-system, signal, and architecture signs remain
path-sensitive in deterministic and stochastic evidence. All 18 historical
primary complete-system medians were negative, while the corrected-mean
signal had no Holm-significant H2 cell in the sealed 36-test family. Robustness
and cost rows remain descriptive, historical dependence is retained, and the
BTC-USD 120-month quarterly cells are explicitly limited by `N=4`.

The independently reviewed [report](../../../../../reports/experiments/safety-adaptivity-tradeoff-synthesis.md),
[audit note](../../../../../research/notes/safety-adaptivity-tradeoff-synthesis-audit.md),
and seven-case [public
checkpoint](../../../../../reproducibility/checks/check_safety_adaptivity_synthesis.py)
preserve the reconstruction and claim boundaries. The domain review passed
without a blocking scientific issue. Ticket 07 is unblocked for independent
reproduction, package review, and publication.
