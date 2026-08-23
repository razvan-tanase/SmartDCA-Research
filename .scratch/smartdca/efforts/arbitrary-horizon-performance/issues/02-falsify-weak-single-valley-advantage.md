---
profile: smartdca-okf/0.4
type: research-ticket
title: "Falsify the weak single-valley advantage conjecture"
description: "Open task ticket falsifying the weak single-valley advantage conjecture with deterministic exact-rational search."
knowledge_role: operational
status: draft
original_record: true
ticket_type: task
ticket_status: open
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T21:32:47Z
generation_run: urn:uuid:ff59c0f2-6dfc-4e4e-8604-62961e607c7f
verified:
  - by: openai-codex/writing-for-agents-0.1
    at: 2026-08-23T21:32:48Z
    review_run: urn:uuid:d87a04a7-92ae-43c4-a446-998b6f1a8d14
---
# 02 — Falsify the weak single-valley advantage conjecture

Type: task
Status: open
Blocked by: 01
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Using the verified arbitrary-horizon seam, determine whether weak single-valley
purchase-price paths alone are sufficient to give the guarded corrected-mean
rule a predictable terminal-wealth advantage over DCA or the neutral guarded
selector in the restricted countercyclical setting. Search deterministically
before attempting a general proof and minimize every decisive witness.

## What to build

A reproducible falsification report states the scope and limits of the declared
finite search. If the conjecture fails, the report supplies the
smallest exact counterexample under the declared ordering. If it survives, the
report preserves the complete search domain and states explicitly that finite
non-discovery is not proof.

## Acceptance criteria

- [ ] The weak single-valley predicate is defined independently of strategy output and validated for every generated path.
- [ ] The search covers declared rational grids at horizons four through eight with equal positive deposits, declared countercyclical parameters, the identity transform, and an explicit evaluation-price grid.
- [ ] The grid, enumeration order, pruning rules, and computational limits are recorded.
- [ ] Results distinguish corrected-versus-DCA and corrected-versus-neutral comparisons.
- [ ] Guardrail-floor activation is recorded, and every reported score effect identifies whether floor activation contributed.
- [ ] Any counterexample is minimized by horizon, price complexity, parameter complexity, and deposit complexity.
- [ ] Every reported witness is replayed as a named exact regression case.
- [ ] If no counterexample is found, the resolution limits its claim to survival of the declared finite search.

## Comments

- Created from the approved tracer-bullet decomposition of the effort specification on
  2026-08-23.
