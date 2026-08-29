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
  at: 2026-08-29T15:49:48Z
generation_run: urn:uuid:36b6508d-0191-4797-a242-cd905f5f91a1
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
  - by: openai-codex/standards-review-0.1
    at: 2026-08-25T11:16:26Z
    review_run: urn:uuid:34df7016-c817-4ad7-b05a-36773412a89c
  - by: openai-codex/spec-review-0.1
    at: 2026-08-25T11:12:41Z
    review_run: urn:uuid:3423b393-7949-4da7-999c-dcfc0747fc29
  - by: openai-codex/independent-empirical-review-0.1
    at: 2026-08-25T11:15:20Z
    review_run: urn:uuid:8a76cee8-e9c9-4ade-9e4d-b08f61a6046c
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
| [02](issues/02-evaluate-deterministic-adversarial-paths.md) | Evaluate deterministic synthetic and adversarial path families. | resolved | — |
| [03](issues/03-evaluate-seeded-stochastic-families.md) | Evaluate seeded stochastic path families. | claimed | — |
| [04](issues/04-establish-historical-data-episode-seam.md) | Establish fingerprinted historical inputs and rolling episodes without opening confirmatory outcomes. | open | — |
| [05](issues/05-run-confirmatory-historical-evaluation.md) | Execute the frozen rolling S&P 500 and Bitcoin evaluation. | open | 04 |
| [06](issues/06-synthesize-safety-adaptivity-tradeoff.md) | Synthesize deterministic, stochastic, and historical evidence. | open | 02, 03, 05 |
| [07](issues/07-review-publish-empirical-package.md) | Independently reproduce, review, and publish the empirical package. | open | 06 |

## Current frontier

[Preregister the empirical protocol and establish one canonical run](issues/01-preregister-protocol-establish-canonical-run.md)
is resolved after Standards, specification, and independent empirical review.
[Evaluate deterministic synthetic and adversarial paths](issues/02-evaluate-deterministic-adversarial-paths.md)
is also resolved after byte-identical clean-room replay of its 18 generated
paths, retained exclusions, and exhaustive finite adversarial search.
[Evaluate seeded stochastic path families](issues/03-evaluate-seeded-stochastic-families.md)
is claimed on `main`; ticket 04 remains open and unclaimed. Ticket 05 still
needs the historical-data seam, while synthesis and publication remain blocked
until their full evidence dependencies resolve.
