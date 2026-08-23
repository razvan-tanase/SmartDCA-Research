---
profile: smartdca-okf/0.4
type: research-ticket
title: "Characterize the cash single-crossing mechanism"
description: "Open research ticket proving or disproving the cash single-crossing mechanism and extracting a strategy-independent path condition."
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
# 03 — Characterize the cash single-crossing mechanism

Type: research
Status: open
Label: ready-for-agent
Blocked by: 02
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Determine whether the corrected rule's cash path relative to the neutral guarded
selector changes sign at most once around a price trough in the restricted
single-valley setting. Prove the strongest valid single-crossing statement or
give an exact counterexample, then extract the narrowest economically
interpretable candidate condition that is stated without reference to eventual
terminal-wealth sign.

## What to build

The project gains a rigorous mechanism-level result connecting the
corrected-mean score, guardrail activation, and cash carried across price
movements. That result either identifies a nonempty candidate path class for
the final wealth theorem or explains precisely why cash single crossing cannot
support such a class under the initial restrictions.

## Acceptance criteria

- [ ] Cash-path differences and the meaning and location of a single crossing are defined for every finite horizon.
- [ ] The weak single-valley conjecture is proved or disproved using exact assumptions and witnesses.
- [ ] The role of repeated guardrail-floor activation is separated from the role of the discretionary score.
- [ ] Any comparative-static property of the corrected mean used by the argument is proved on the exact parameter region required.
- [ ] Every failed statement is accompanied by a minimized exact counterexample satisfying all declared assumptions.
- [ ] Any surviving condition is expressed using observable price, deposit, reference, or guardrail structure rather than terminal-wealth sign.
- [ ] The surviving class is shown to be nonempty, or the resolution proves why no useful class arises from this mechanism under the restricted family.
- [ ] The evidence and executable cases distinguish proved facts, computational observations, and unresolved questions.

## Comments

- Created from the approved tracer-bullet decomposition of the effort specification on
  2026-08-23.
