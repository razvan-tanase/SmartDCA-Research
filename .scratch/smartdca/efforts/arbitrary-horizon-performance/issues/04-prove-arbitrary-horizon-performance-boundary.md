---
profile: smartdca-okf/0.4
type: research-ticket
title: "Prove the arbitrary-horizon performance boundary"
description: "Open research ticket proving a sharp arbitrary-horizon guarded SmartDCA performance theorem or negative boundary."
knowledge_role: operational
status: draft
original_record: true
ticket_type: research
ticket_status: open
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T20:17:00Z
generation_run: urn:uuid:ed95ae0b-06ee-4d96-a841-5724e383cc65
---
# 04 — Prove the arbitrary-horizon performance boundary

Type: research
Status: open
Label: ready-for-agent
Blocked by: 03
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Use the accounting identity, falsification evidence, and cash-path mechanism to
prove one defensible arbitrary-horizon wealth result for the guarded
corrected-mean rule. The result may be a sharp positive theorem on an
independently defined nonempty path class or a rigorous negative theorem
showing why the strongest surviving candidate class remains insufficient.

## What to build

For every finite horizon, a reader can determine the exact scope in which the
corrected discretionary allocation has a predictable relationship to DCA and
to the neutral guarded selector. All evaluation-price conditions, strictness
conditions, safety implications, and counterexamples are explicit.

## Acceptance criteria

- [ ] The theorem or negative boundary applies to every finite horizon in its declared class.
- [ ] The path class and every evaluation-price condition are stated independently of eventual relative-wealth sign.
- [ ] The result compares the corrected rule with DCA and with the neutral guarded selector wherever each comparison is claimed.
- [ ] The epsilon-DCA safety guarantee remains inherited from the guardrail and is not attributed to the corrected-mean score.
- [ ] A positive result proves a nonempty strict region and states whether its conditions are necessary, sufficient, or both.
- [ ] A sufficient-only result includes a proved obstruction to necessity and preserves visible outside-class failures.
- [ ] A negative result provides exact admissible counterexamples and identifies the strongest reusable missing structure justified by the proof.
- [ ] Constant paths, troughs at endpoints, flat troughs, ties, floor branches, and the lambda-equals-one collapse are covered or explicitly excluded.
- [ ] No stochastic, universal-dominance, parameter-superiority, or novelty claim is inferred from the theorem.
- [ ] The complete proof and exact examples are recorded as evidence suitable for independent review.

## Comments

- Created from the approved tracer-bullet decomposition of the effort specification on
  2026-08-23.
