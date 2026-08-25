---
profile: smartdca-okf/0.4
type: research-map
title: "Safety-adaptivity empirical evaluation effort map"
description: "Approved seven-ticket route from preregistration through independent empirical publication."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-25T09:17:46Z
generation_run: urn:uuid:84d83c43-e3fa-4d94-9a48-16450f73a7c2
verified:
  - by: human:github:razvan-tanase
    at: 2026-08-25T07:38:45Z
    review_run: urn:uuid:c8afb7ab-b24c-4fd7-a244-7db644525f3c
  - by: human:github:razvan-tanase
    at: 2026-08-25T07:52:38Z
    review_run: urn:uuid:090561f8-809a-4a62-91ad-8057714a54b6
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
# Safety-adaptivity empirical evaluation effort map

## Contract

The approved problem, outcome requirements, implementation and testing
decisions, and exclusions live in the [effort specification](spec.md). The
project-wide scientific context lives in the
[SmartDCA research map](../../map.md).

## Ticket route

| Ticket | Purpose | Status | Blocked by |
|---|---|---|---|
| [01](issues/01-preregister-protocol-establish-canonical-run.md) | Freeze the protocol and establish one complete non-confirmatory empirical run. | resolved | — |
| [02](issues/02-evaluate-deterministic-adversarial-paths.md) | Evaluate deterministic synthetic and adversarial path families. | open | — |
| [03](issues/03-evaluate-seeded-stochastic-families.md) | Evaluate seeded stochastic path families. | open | — |
| [04](issues/04-establish-historical-data-episode-seam.md) | Establish fingerprinted historical inputs and rolling episodes without opening confirmatory outcomes. | open | — |
| [05](issues/05-run-confirmatory-historical-evaluation.md) | Execute the frozen rolling S&P 500 and Bitcoin evaluation. | open | 04 |
| [06](issues/06-synthesize-safety-adaptivity-tradeoff.md) | Synthesize deterministic, stochastic, and historical evidence. | open | 02, 03, 05 |
| [07](issues/07-review-publish-empirical-package.md) | Independently reproduce, review, and publish the empirical package. | open | 06 |

## Current frontier

[Preregister the empirical protocol and establish one canonical run](issues/01-preregister-protocol-establish-canonical-run.md)
is resolved after Standards, specification, and independent empirical review.
Tickets 02, 03, and 04 are open, unblocked, and unclaimed; ticket 05 still needs
the historical-data seam, while synthesis and publication remain blocked until
their full evidence dependencies resolve.
