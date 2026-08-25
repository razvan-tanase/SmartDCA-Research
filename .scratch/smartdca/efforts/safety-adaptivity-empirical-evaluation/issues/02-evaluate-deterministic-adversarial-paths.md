---
profile: smartdca-okf/0.4
type: research-ticket
title: "Evaluate deterministic synthetic and adversarial paths"
description: "Open task ticket executing the preregistered three-policy study on deterministic synthetic and adversarial price-path families."
knowledge_role: operational
status: draft
original_record: true
ticket_type: task
ticket_status: claimed
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-25T09:54:11Z
generation_run: urn:uuid:a0c58f08-1ce1-4abb-91fa-1d2e8eb43429
---
# 02 — Evaluate deterministic synthetic and adversarial paths

Type: task
Status: claimed
Label: ready-for-agent
Blocked by: 01
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

How do DCA, the neutral guarded selector, and the guarded corrected-mean
SmartDCA rule behave across interpretable deterministic and deliberately hostile
price paths when the preregistered coverage and cost configurations are applied?

## What to build

A researcher can reproduce a named deterministic study covering the mathematical
boundary cases and economically interpretable stress paths, then inspect raw
three-policy ledgers, aggregate comparisons, mechanism attribution, failures,
and a bounded experiment report generated through the shared runner.

## Acceptance criteria

- [ ] The executed families include constant prices, monotone rises, monotone declines, weak and strict single valleys, incomplete and completed recoveries, multiple valleys, crashes, sudden rebounds, prolonged drawdowns, flat segments, and paths deliberately hostile to carried cash or adaptive timing.
- [ ] Every generated path is identified by saved family parameters and satisfies its declared path predicate independently of policy performance.
- [ ] All three policies run under identical prices, deposits, dates, evaluation points, safety factors, corrected-mean configurations, and cost scenarios from the preregistered protocol.
- [ ] The results report complete-system, signal-only, and safety-architecture comparisons together with relative terminal wealth, downside, cash drag, exposure, guardrail activation, purchase activity, and terminal cash/unit attribution.
- [ ] Frictionless runs verify the epsilon-DCA unit-coverage condition and terminal cash/unit identity; cost-adjusted runs remain explicitly empirical net-performance results.
- [ ] Boundary fixtures connect the study to the existing constant, two-purchase, three-purchase, single-valley, repeated-floor-activation, and arbitrary-horizon results without presenting finite experiments as proof.
- [ ] Every attempted configuration, exclusion, validation failure, and successful result is retained rather than reporting only favorable paths or parameters.
- [ ] Raw episode results, aggregates, tables, and figure-ready data regenerate from one immutable run manifest in a fresh environment.
- [ ] The experiment report states which mechanisms appear in each path family and what deterministic evidence cannot establish about historical or stochastic performance.
- [ ] The ticket, report, checks, effort map, and repository verification gates agree at resolution.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket may proceed in parallel with tickets 03 and 04 after ticket 01
  resolves.
- Claimed on `agent/evaluate-deterministic-adversarial-paths` after confirming
  ticket 01 is resolved and no other ticket is claimed.

## Answer

_Not yet resolved._
