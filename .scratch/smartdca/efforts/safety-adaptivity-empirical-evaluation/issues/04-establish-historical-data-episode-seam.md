# 04 — Establish the historical-data and rolling-episode seam

Type: task
Status: claimed
Blocked by: 01
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

Can the preregistered S&P 500 and Bitcoin series be acquired, fingerprinted,
normalized, and converted into point-in-time-valid recurring-investment
episodes without exposing or analyzing confirmatory outcomes prematurely?

## What to build

A researcher can reproduce the exact historical inputs or their retrieval
receipts, audit series and calendar semantics, generate the declared rolling
episodes, inspect every exclusion, and run one explicitly non-confirmatory
validation episode through all three policies to prove that data becomes a
complete study input without opening the confirmatory result set.

## Acceptance criteria

- [ ] The selected S&P 500 investable or total-return proxy and Bitcoin/USD spot series match the preregistered provider, series identifier, currency, timezone, adjustment semantics, retrieval rule, and licensing or redistribution decision.
- [x] Each retained input has a retrieval timestamp, content fingerprint, source receipt, schema description, date coverage, and an immutable identity used by experiment manifests.
- [x] Market-calendar alignment, timezone normalization, deposit-date mapping, evaluation-date mapping, and missing-observation handling implement the preregistered rules without silent interpolation.
- [x] Rolling episodes use only information available through each purchase date and expose their deposit schedule, purchase timestamps, horizon, evaluation timestamp, input rows, and exclusion reason where invalid.
- [x] Hand-checkable fixtures verify splits or adjusted-price semantics where applicable, weekend and holiday behavior, missing endpoints, boundary dates, and overlapping-window construction.
- [x] Prefix checks confirm that extending the dataset with future rows does not change earlier policy decisions.
- [x] One explicitly non-confirmatory validation episode for each asset runs end to end through DCA, neutral guarded, and corrected guarded policies and emits the standard manifest, ledgers, validations, and estimands.
- [x] Confirmatory aggregate outcomes remain unopened and unreported; validation output is labeled as infrastructure evidence rather than a study conclusion.
- [x] Every unavailable, malformed, incomplete, or excluded episode is retained with a machine-readable reason and reconciles with dataset and episode counts.
- [ ] The data receipts, episode builder, validation runs, checks, and ticket resolution are reproducible without hidden manual steps.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket may proceed in parallel with tickets 02 and 03 after ticket 01
  resolves; ticket 05 cannot begin until this data boundary passes review.
- Claimed on `main` after confirming ticket 01 is resolved and no other ticket
  is claimed. The frozen protocol and its complete-run seam govern the work.
- The provider and license review is recorded in
  [`alpha-vantage-historical-data-provider-review.md`](../../../../../research/notes/alpha-vantage-historical-data-provider-review.md).
  No licensed Alpha Vantage key was available. Both locked requests made with
  the provider's demo credential returned a typed `Information` envelope; no
  market price row or derived confirmatory outcome was opened.
- The complete fictional-fixture checkpoint is
  `smartdca-historical-validation-v1-bee2ccc740eeaa7b0c6be4aa300934c993f525dfce4a0125e2d0044895a2cddd`.
  Twenty-two public-contract tests replay it byte for byte and cover acquisition,
  receipts, schema rejection, calendar mapping, exclusions, prefix stability,
  the full-grid handoff, and the three-policy validation slice.
- Initial Standards review found missing domain-review evidence and duplicated
  artifact staging; specification review found relabelable fixture provenance,
  dropped dataset-failure attempts, truncated excluded schedules, and a pinned
  Python patch release. The implementation now binds confirmatory source sets
  to the protocol and live acquisition receipt, persists complete rejected
  grids, shares artifact staging, and records the registered `3.12` runtime.
  Independent domain re-review passed both glossary entries after clarifying
  that a source receipt covers declared provider or fixture sources without
  conflating source identity with experiment-input identity.
- The remaining acceptance gate is an authorized provider retrieval whose
  exact headers, semantics, date coverage, and sanitized receipt pass the new
  seam. Raw and normalized provider observations must remain outside Git under
  the recorded conservative redistribution decision.

## Answer

_Not yet resolved._
