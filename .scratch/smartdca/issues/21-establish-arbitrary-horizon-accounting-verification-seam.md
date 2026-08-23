---
profile: smartdca-okf/0.3
type: research-ticket
title: "Establish the arbitrary-horizon accounting and verification seam"
description: "Open task ticket proving the arbitrary-horizon cash-timing identity and delivering the exact-rational three-policy verification seam."
knowledge_role: operational
status: draft
original_record: true
ticket_type: task
ticket_status: open
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T19:40:02Z
generation_run: urn:uuid:b31074e1-661f-4af8-98db-6fa1ebfc5f17
---
# 21 — Establish the arbitrary-horizon accounting and verification seam

Type: task
Status: open
Label: ready-for-agent
Blocked by: 18
Parent: [Test arbitrary-horizon guarded SmartDCA performance on single-valley paths](20-test-arbitrary-horizon-guarded-smartdca-single-valley.md)

## Question

Prove the arbitrary-horizon cash-timing identity for every fully funded strategy
in the established comparison model, derive its two-strategy form, and expose
one deterministic exact-rational scenario interface for DCA, the guarded
corrected-mean SmartDCA rule, and the neutral guarded selector. Verify that the
same interface reproduces the settled two- and three-purchase results before it
is used to investigate longer horizons.

## What to build

A researcher can submit one finite rational scenario and inspect a complete,
internally consistent ledger for all three policies: purchases, carried cash,
asset units, guardrail-floor activation, corrected references, discretionary
scores, and terminal-wealth gaps. The mathematical identity and the executable
ledger must verify each other from independent accounting routes.

## Acceptance criteria

- [ ] The cash-timing identity is proved for arbitrary finite horizons, positive prices, nonnegative deposits, and a common positive evaluation price.
- [ ] The two-strategy identity is derived using the difference between the strategies' cash paths.
- [ ] The exact-rational scenario interface exposes every externally relevant ledger quantity for DCA, the corrected rule, and the neutral selector.
- [ ] The interface reproduces the existing two-purchase win, tie, loss, and all-win cases.
- [ ] The interface reproduces the existing three-purchase beta-flip witness exactly.
- [ ] Active, inactive, and repeated guardrail-floor branches are covered by named checks.
- [ ] Constant-price behavior, zero deposits, and the lambda-equals-one DCA collapse are checked.
- [ ] The evidence record, executable check, and ticket resolution can be reviewed without hidden conversation context.

## Comments

- Created from the approved tracer-bullet decomposition of ticket 20 on
  2026-08-23.
