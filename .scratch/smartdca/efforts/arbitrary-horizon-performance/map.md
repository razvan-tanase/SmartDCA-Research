---
profile: smartdca-okf/0.4
type: research-map
title: "Arbitrary-horizon performance effort map"
description: "Operational map of the approved arbitrary-horizon guarded SmartDCA performance effort and its blocking frontier."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T21:32:47Z
generation_run: urn:uuid:ff59c0f2-6dfc-4e4e-8604-62961e607c7f
verified:
  - by: openai-codex/writing-for-agents-0.1
    at: 2026-08-23T21:32:48Z
    review_run: urn:uuid:d87a04a7-92ae-43c4-a446-998b6f1a8d14
---
# Arbitrary-horizon performance effort map

## Contract

The approved scope, completion boundary, testing decisions, and exclusions live
in the [effort specification](spec.md). The project-wide scientific context
lives in the [SmartDCA research map](../../map.md). Follow the
[Wayfinder ticket workflow](../../../../docs/agents/wayfinder-ticket-workflow.md)
whenever claiming, executing, resolving, or advancing a ticket in this route.

## Ticket route

| Ticket | Purpose | Status | Blocked by |
|---|---|---|---|
| [01](issues/01-establish-accounting-verification-seam.md) | Prove the cash-timing identity and build the exact-rational verification seam. | open | `.scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect` |
| [02](issues/02-falsify-weak-single-valley-advantage.md) | Search for and minimize counterexamples to the weak single-valley conjecture. | open | 01 |
| [03](issues/03-characterize-cash-single-crossing-mechanism.md) | Prove or disprove the proposed cash-path mechanism. | open | 02 |
| [04](issues/04-prove-arbitrary-horizon-performance-boundary.md) | State and prove the strongest surviving arbitrary-horizon boundary. | open | 03 |
| [05](issues/05-review-publish-research-package.md) | Independently review and publish the accepted result. | open | 04 |

## Active frontier

Only ticket 01 may be claimed. Its external dependency is resolved; tickets
02–05 remain blocked in the order shown above. Local ticket numbers are
meaningful only inside this effort; blockers outside the effort use their full
Concept ID.
