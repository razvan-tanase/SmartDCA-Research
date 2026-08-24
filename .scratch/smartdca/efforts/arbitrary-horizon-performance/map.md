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
  at: 2026-08-24T20:11:40Z
generation_run: urn:uuid:6a0602e3-5197-442d-bfc1-256ac8a382ba
verified:
  - by: openai-codex/writing-for-agents-0.1
    at: 2026-08-23T21:32:48Z
    review_run: urn:uuid:d87a04a7-92ae-43c4-a446-998b6f1a8d14
  - by: openai-codex/spec-review-0.1
    at: 2026-08-23T22:36:39Z
    review_run: urn:uuid:7d7be1a1-3482-44ae-be16-e07cd8bc3010
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T08:32:57Z
    review_run: urn:uuid:8e47900a-b265-4440-819f-2a5326ed440f
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T08:32:57Z
    review_run: urn:uuid:a7c4c38d-001a-494a-a8de-cd2211240855
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T08:38:49Z
    review_run: urn:uuid:8a97bf17-69e6-4d16-bcc0-5755d83d8785
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T08:38:49Z
    review_run: urn:uuid:96546068-7247-4999-906a-ef18ccb9a474
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T11:10:20Z
    review_run: urn:uuid:a85e3b86-c811-468c-a420-88980df31ea6
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T11:10:20Z
    review_run: urn:uuid:70aff5a0-c58b-47c8-a8ea-7d4016beba2c
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:2d41dd92-0f83-4940-9eff-8eba11d4196d
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:c830b658-ad37-43ba-b537-690dda4f5455
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
| [01](issues/01-establish-accounting-verification-seam.md) | Prove the cash-timing identity and build the exact-rational verification seam. | resolved | `.scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect` |
| [02](issues/02-falsify-weak-single-valley-advantage.md) | Search for and minimize counterexamples to the weak single-valley conjecture. | resolved | 01 |
| [03](issues/03-characterize-cash-single-crossing-mechanism.md) | Prove or disprove the proposed cash-path mechanism. | resolved | 02 |
| [04](issues/04-prove-arbitrary-horizon-performance-boundary.md) | State and prove the strongest surviving arbitrary-horizon boundary. | resolved | 03 |
| [05](issues/05-review-publish-research-package.md) | Independently review and publish the accepted result. | open, unclaimed | 04 (resolved) |

## Active frontier

Ticket 04 is resolved. Its reviewed
[theorem](../../../../research/theorems/arbitrary-horizon-performance-boundary.md)
gives the exact affine evaluation-price boundary from terminal cash and units,
while its [evidence](../../../../research/notes/arbitrary-horizon-performance-boundary.md)
specializes the result to a reciprocal-exposure balance on single-valley paths
and proves that reference-aligned cash crossing alone remains insufficient.
Ticket 05 is open, unblocked, and unclaimed pending the user significance
gate. Local ticket numbers are meaningful only inside this effort; blockers
outside the effort use their full Concept ID.
