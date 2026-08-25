---
profile: smartdca-okf/0.4
type: research-ticket
title: "Preregister the empirical protocol and establish one canonical run"
description: "Resolved task ticket freezing the empirical protocol and establishing a reviewed deterministic three-policy canonical run before historical outcome access."
knowledge_role: operational
status: stable
original_record: true
ticket_type: task
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-25T09:15:14Z
generation_run: urn:uuid:733dc5ac-2f9c-4d46-8af5-23c136197149
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-25T09:13:48Z
    review_run: urn:uuid:8e4d4bc6-edf2-41c1-8eca-7bef42fbcb46
  - by: openai-codex/spec-review-0.1
    at: 2026-08-25T09:13:48Z
    review_run: urn:uuid:ba2f5fd9-b876-4d98-9487-eeb090be48da
  - by: openai-codex/independent-empirical-review-0.1
    at: 2026-08-25T09:13:48Z
    review_run: urn:uuid:5b34f61f-ac0c-47cf-9db5-c1cb150d864c
---
# 01 — Preregister the empirical protocol and establish one canonical run

Type: task
Status: resolved
Label: ready-for-agent
Blocked by: none
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

Can the approved empirical study be frozen before confirmatory outcomes are
inspected and executed through one deterministic end-to-end seam that preserves
the settled three-policy accounting and produces every artifact needed for
later evidence layers?

## What to build

A researcher can execute one explicitly non-confirmatory synthetic recurring-
investment episode from an immutable study configuration and receive a run
identity, input receipts, complete DCA, neutral guarded, and corrected guarded
ledgers, validation receipts, episode estimands, aggregates, and report-ready
outputs. The same checkpoint freezes the confirmatory datasets, episode rules,
coverage grid, corrected-mean configurations, cost scenarios, hypotheses,
estimands, uncertainty method, exclusions, and confirmatory-versus-exploratory
boundary before historical outcomes are read.

## Acceptance criteria

- [x] The preregistered protocol names the exact historical series or provider selection, asset semantics, retrieval and fingerprint rules, deposit cadence, horizons, evaluation convention, rolling stride, missing-data rule, coverage grid, corrected-mean primary configurations, robustness grid, transaction-cost scenarios, hypotheses, estimands, multiplicity boundary, and dependence-aware uncertainty method.
- [x] The protocol distinguishes confirmatory, secondary, robustness, and exploratory analyses and declares that confirmatory choices cannot change after outcome access.
- [x] One public experiment-runner contract accepts a validated immutable configuration plus versioned inputs and emits a deterministic run identity, manifest, complete policy ledgers, validation receipts, episode results, aggregates, tables, and figure-ready data.
- [x] DCA accounting is independent of the guarded-policy implementation, while the corrected and neutral policies share one epsilon-DCA guardrail contract and differ only through the discretionary selector.
- [x] The canonical synthetic run exercises all three policies, at least one nontrivial safety factor and the lambda-equals-one collapse, the frictionless baseline, and the declared fixed and proportional cost accounting routes.
- [x] Every ledger exposes deposits, purchases, fees, cash, units, references, scores, guardrail floors, floor activation, coverage, terminal wealth, and terminal cash/unit attribution where applicable.
- [x] Frictionless guarded ledgers verify full funding, causality, buy-only behavior, unit coverage, direct wealth accounting, and the terminal cash/unit identity; net-of-cost outputs are explicitly marked outside the current safety theorem.
- [x] The runner reproduces the existing named exact-rational regression cases relevant to two purchases, three purchases, constant prices, repeated floor activation, and the lambda-equals-one boundary.
- [x] Invalid prices, coverage values, parameters, dates, costs, or run-identity collisions fail before execution with an externally visible reason.
- [x] The protocol, canonical run, executable checks, and ticket resolution are reviewable without hidden conversation context, and no confirmatory historical outcome has been inspected.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket is the only initial frontier and establishes the shared seam used
  by every later evidence-layer ticket.
- Implementation proceeded test-first at the approved complete-run seam. The
  final module has 16 public-contract tests, including exact regression,
  cost-boundary, deterministic identity, stratum, exclusion, and CLI cases.
- Initial Standards, specification, and independent empirical reviews found
  underspecified timing/inference rules, proportional-cost overspend,
  cross-stratum pooling, a missing floor estimand, incomplete input identity,
  implicit exclusion accounting, and missing artifact-layer policy. Every
  finding was corrected and independently re-reviewed to a pass.
- The accepted version-1 protocol and input fingerprints close the explicitly
  logged, outcome-blind first-publication correction window. No SPY or BTC/USD
  provider response or derived historical policy result was retrieved.
- The canonical experiment report intentionally remains draft: the effort's
  stable-promotion gate also requires a historical-slice reproduction, which
  belongs to ticket 04 rather than this outcome-blind checkpoint.

## Answer

The outcome-blind [protocol](../../../../../experiments/protocols/safety-adaptivity-v1.json)
freezes the complete confirmatory boundary, including exact episode inclusion,
bootstrap construction, finite-run p-value, quantile, and Holm rules. Its
SHA-256 is
`a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4`;
the versioned [synthetic input](../../../../../experiments/inputs/canonical-synthetic-v1.json)
has SHA-256
`4609770766e74ee38df70e8c0b6f48412544dbba431a91a2612366dec8f6bddb`.

The public [runner](../../../../../reproducibility/empirical.py) produces the
deterministic run
`smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0`.
Its [manifest](../../../../../reports/experiments/runs/smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0/manifest.json)
joins runner, protocol, input, and six output fingerprints. The bundle contains
36 complete ledgers, 36 included comparisons, 36 strata-preserving aggregate
cells, report tables, figure data, and ten passed validation receipts. It has
zero negative-cash steps; frictionless outputs carry the epsilon-DCA scope,
while all cost-adjusted outputs are explicitly outside the current theorem.

The 16-case [executable checkpoint](../../../../../reproducibility/checks/check_empirical_protocol_canonical_run.py)
reproduces the bundle byte for byte and exposes typed pre-execution failures.
The independently replayed [experiment report](../../../../../reports/experiments/canonical-synthetic-run.md)
records all hashes, bounded mechanism observations, and limitations. The
[artifact-layer decision](../../../../../docs/adr/0008-place-empirical-protocol-input-run-layers.md)
fixes protocol, input, run, and report identity rules. Standards,
specification, and empirical-evidence re-review report no remaining finding.
