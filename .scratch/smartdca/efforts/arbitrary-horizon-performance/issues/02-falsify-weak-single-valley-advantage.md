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
  at: 2026-08-23T20:17:00Z
generation_run: urn:uuid:ed95ae0b-06ee-4d96-a841-5724e383cc65
---
# 02 — Falsify the weak single-valley advantage conjecture

Type: task
Status: open
Label: ready-for-agent
Blocked by: 01
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Using the verified arbitrary-horizon seam, determine whether weak single-valley
purchase-price paths alone are sufficient to give the guarded corrected-mean
rule a predictable terminal-wealth advantage over DCA or the neutral guarded
selector in the restricted countercyclical setting. Search deterministically
before attempting a general proof and minimize every decisive witness.

## What to build

A reproducible falsification report answers what the declared finite search
does and does not establish. If the conjecture fails, the report supplies the
smallest exact counterexample under the declared ordering. If it survives, the
report preserves the complete search domain and states explicitly that finite
non-discovery is not proof.

## Acceptance criteria

- [ ] The weak single-valley predicate is defined independently of strategy output and validated for every generated path.
- [ ] The search covers declared rational grids at horizons four through eight with equal positive deposits, declared countercyclical parameters, the identity transform, and an explicit evaluation-price grid.
- [ ] The grid, enumeration order, pruning rules, and computational limits are recorded.
- [ ] Results distinguish corrected-versus-DCA and corrected-versus-neutral comparisons.
- [ ] Guardrail-floor activation is recorded so an apparent score effect cannot be attributed silently to the floor.
- [ ] Any counterexample is minimized by horizon, price complexity, parameter complexity, and deposit complexity.
- [ ] Every reported witness is replayed as a named exact regression case.
- [ ] If no counterexample is found, the resolution reports only survival of the finite search and makes no arbitrary-horizon claim.

## Comments

- Created from the approved tracer-bullet decomposition of the effort specification on
  2026-08-23.
