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
  at: 2026-08-25T08:11:32Z
generation_run: urn:uuid:d18b7494-a955-4ab1-9332-51b3f3f88d85
verified:
  - by: human:github:razvan-tanase
    at: 2026-08-25T07:38:45Z
    review_run: urn:uuid:c8afb7ab-b24c-4fd7-a244-7db644525f3c
  - by: human:github:razvan-tanase
    at: 2026-08-25T07:52:38Z
    review_run: urn:uuid:090561f8-809a-4a62-91ad-8057714a54b6
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
| [01](issues/01-preregister-protocol-establish-canonical-run.md) | Freeze the protocol and establish one complete non-confirmatory empirical run. | claimed | — |
| [02](issues/02-evaluate-deterministic-adversarial-paths.md) | Evaluate deterministic synthetic and adversarial path families. | open | 01 |
| [03](issues/03-evaluate-seeded-stochastic-families.md) | Evaluate seeded stochastic path families. | open | 01 |
| [04](issues/04-establish-historical-data-episode-seam.md) | Establish fingerprinted historical inputs and rolling episodes without opening confirmatory outcomes. | open | 01 |
| [05](issues/05-run-confirmatory-historical-evaluation.md) | Execute the frozen rolling S&P 500 and Bitcoin evaluation. | open | 04 |
| [06](issues/06-synthesize-safety-adaptivity-tradeoff.md) | Synthesize deterministic, stochastic, and historical evidence. | open | 02, 03, 05 |
| [07](issues/07-review-publish-empirical-package.md) | Independently reproduce, review, and publish the empirical package. | open | 06 |

## Current frontier

[Preregister the empirical protocol and establish one canonical run](issues/01-preregister-protocol-establish-canonical-run.md)
is claimed and in progress. Tickets 02, 03, and 04 remain blocked until it
resolves; ticket 05 needs the historical-data seam, while synthesis and
publication remain blocked until their full evidence dependencies resolve.
