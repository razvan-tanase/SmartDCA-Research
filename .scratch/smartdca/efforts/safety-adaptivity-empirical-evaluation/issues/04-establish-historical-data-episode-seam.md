---
profile: smartdca-okf/0.5
type: research-ticket
title: "Establish the historical-data and rolling-episode seam"
description: "Open task ticket delivering fingerprinted S&P 500 and Bitcoin inputs, point-in-time episode construction, and a non-confirmatory validation run."
knowledge_role: operational
status: draft
original_record: true
ticket_type: task
ticket_status: open
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-25T07:52:38Z
generation_run: urn:uuid:a5d8aafb-5c01-48a5-8177-23ed524a00a7
---
# 04 — Establish the historical-data and rolling-episode seam

Type: task
Status: open
Label: ready-for-agent
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
- [ ] Each retained input has a retrieval timestamp, content fingerprint, source receipt, schema description, date coverage, and an immutable identity used by experiment manifests.
- [ ] Market-calendar alignment, timezone normalization, deposit-date mapping, evaluation-date mapping, and missing-observation handling implement the preregistered rules without silent interpolation.
- [ ] Rolling episodes use only information available through each purchase date and expose their deposit schedule, purchase timestamps, horizon, evaluation timestamp, input rows, and exclusion reason where invalid.
- [ ] Hand-checkable fixtures verify splits or adjusted-price semantics where applicable, weekend and holiday behavior, missing endpoints, boundary dates, and overlapping-window construction.
- [ ] Prefix checks confirm that extending the dataset with future rows does not change earlier policy decisions.
- [ ] One explicitly non-confirmatory validation episode for each asset runs end to end through DCA, neutral guarded, and corrected guarded policies and emits the standard manifest, ledgers, validations, and estimands.
- [ ] Confirmatory aggregate outcomes remain unopened and unreported; validation output is labeled as infrastructure evidence rather than a study conclusion.
- [ ] Every unavailable, malformed, incomplete, or excluded episode is retained with a machine-readable reason and reconciles with dataset and episode counts.
- [ ] The data receipts, episode builder, validation runs, checks, and ticket resolution are reproducible without hidden manual steps.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket may proceed in parallel with tickets 02 and 03 after ticket 01
  resolves; ticket 05 cannot begin until this data boundary passes review.

## Answer

_Not yet resolved._
